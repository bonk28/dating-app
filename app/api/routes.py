from flask import jsonify, request
from flask_login import login_required, current_user
from app import db
from app.api import bp
from app.models import User, Like, Match, Message, Defi, DefiParticipant, DefiVote, Report
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance entre deux points GPS en km"""
    R = 6371  # Rayon de la Terre
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

@bp.route('/swipe/<int:user_id>', methods=['POST'])
@login_required
def swipe(user_id):
    data = request.get_json()
    direction = data.get('direction', 'like')
    
    if direction not in ['like', 'pass', 'super_like']:
        return jsonify({'success': False, 'error': 'Direction invalide'}), 400
    
    like = Like.query.filter_by(
        liker_id=current_user.id,
        liked_id=user_id
    ).first()
    
    if like:
        like.direction = direction
    else:
        like = Like(liker_id=current_user.id, liked_id=user_id, direction=direction)
        db.session.add(like)
    
    is_match = False
    match_id = None
    compatibility = 0
    
    if direction in ['like', 'super_like']:
        reciprocal = Like.query.filter_by(
            liker_id=user_id,
            liked_id=current_user.id
        ).filter(Like.direction.in_(['like', 'super_like'])).first()
        
        if reciprocal:
            # Calculer la compatibilité
            other_user = User.query.get(user_id)
            compatibility = current_user.get_compatibility(other_user)
            
            match = Match(
                user1_id=min(current_user.id, user_id),
                user2_id=max(current_user.id, user_id),
                compatibility=compatibility
            )
            db.session.add(match)
            db.session.flush()
            match_id = match.id
            is_match = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_match': is_match,
        'match_id': match_id,
        'compatibility': compatibility
    })

@bp.route('/update-location', methods=['POST'])
@login_required
def update_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if latitude and longitude:
        current_user.latitude = latitude
        current_user.longitude = longitude
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Coordonnées manquantes'}), 400

@bp.route('/discover', methods=['GET'])
@login_required
def discover():
    # Récupérer les IDs déjà swipés
    swiped_ids = [s.swiped_id for s in current_user.likes_sent.all()]
    swiped_ids.append(current_user.id)
    
    # Requête de base
    query = User.query.filter(
        ~User.id.in_(swiped_ids),
        User.is_active == True
    )
    
    # Filtrer par genre recherché
    if current_user.looking_for:
        query = query.filter(User.gender == current_user.looking_for)
    
    # Filtrer par âge si configuré
    if request.args.get('min_age'):
        query = query.filter(User.age >= int(request.args.get('min_age')))
    if request.args.get('max_age'):
        query = query.filter(User.age <= int(request.args.get('max_age')))
    
    users = query.all()
    
    # Filtrer par distance si la géolocalisation est activée
    if current_user.latitude and current_user.longitude:
        max_dist = current_user.max_distance
        nearby_users = []
        for user in users:
            if user.latitude and user.longitude:
                dist = calculate_distance(
                    current_user.latitude, current_user.longitude,
                    user.latitude, user.longitude
                )
                if dist <= max_dist:
                    user.distance = int(dist)
                    user.compatibility = current_user.get_compatibility(user)
                    nearby_users.append(user)
        users = nearby_users
    
    # Trier par compatibilité
    users.sort(key=lambda u: getattr(u, 'compatibility', 0), reverse=True)
    
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'age': u.age,
        'gender': u.gender,
        'bio': u.bio,
        'interests': u.interests,
        'location': u.location,
        'photo': u.photo,
        'distance': getattr(u, 'distance', None),
        'compatibility': getattr(u, 'compatibility', 50)
    } for u in users[:20]])

@bp.route('/messages/<int:match_id>', methods=['GET'])
@login_required
def get_messages(match_id):
    match = Match.query.get_or_404(match_id)
    
    if current_user.id not in [match.user1_id, match.user2_id]:
        return jsonify({'error': 'Non autorisé'}), 403
    
    messages = Message.query.filter_by(match_id=match_id)\
                .order_by(Message.created_at).all()
    
    # Marquer comme lu
    for msg in messages:
        if msg.sender_id != current_user.id and not msg.is_read:
            msg.is_read = True
    
    db.session.commit()
    
    return jsonify([{
        'id': msg.id,
        'sender_id': msg.sender_id,
        'content': msg.content,
        'message_type': msg.message_type,
        'is_read': msg.is_read,
        'created_at': msg.created_at.isoformat()
    } for msg in messages])

@bp.route('/messages/<int:match_id>', methods=['POST'])
@login_required
def send_message(match_id):
    data = request.get_json()
    content = data.get('content', '').strip()
    message_type = data.get('type', 'text')
    
    if not content:
        return jsonify({'error': 'Message vide'}), 400
    
    match = Match.query.get_or_404(match_id)
    
    if current_user.id not in [match.user1_id, match.user2_id]:
        return jsonify({'error': 'Non autorisé'}), 403
    
    message = Message(
        match_id=match_id,
        sender_id=current_user.id,
        content=content,
        message_type=message_type
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': {
            'id': message.id,
            'sender_id': message.sender_id,
            'content': message.content,
            'message_type': message.message_type,
            'created_at': message.created_at.isoformat()
        }
    })

@bp.route('/report/<int:user_id>', methods=['POST'])
@login_required
def report_user(user_id):
    data = request.get_json()
    reason = data.get('reason', '')
    
    report = Report(
        reporter_id=current_user.id,
        reported_id=user_id,
        reason=reason
    )
    db.session.add(report)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Utilisateur signalé'})

@bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    matches_count = Match.query.filter(
        ((Match.user1_id == current_user.id) | (Match.user2_id == current_user.id)),
        Match.is_active == True
    ).count()
    
    likes_received = Like.query.filter_by(
        liked_id=current_user.id
    ).filter(Like.direction.in_(['like', 'super_like'])).count()
    
    messages_sent = Message.query.filter_by(sender_id=current_user.id).count()
    
    return jsonify({
        'matches': matches_count,
        'likes_received': likes_received,
        'messages_sent': messages_sent,
        'profile_views': 0  # À implémenter avec Redis
    })

@bp.route('/messages/media/<int:match_id>', methods=['POST'])
@login_required
def send_media_message(match_id):
    """Envoyer une image ou vidéo dans le chat"""
    if 'media' not in request.files:
        return jsonify({'error': 'Fichier requis'}), 400
    
    file = request.files['media']
    media_type = request.form.get('type', 'image')
    
    if file and file.filename:
        from werkzeug.utils import secure_filename
        import os
        filename = secure_filename(f"chat_{match_id}_{datetime.now().timestamp()}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        msg = Message(
            match_id=match_id,
            sender_id=current_user.id,
            content=filename,
            message_type=media_type
        )
        db.session.add(msg)
        db.session.commit()
        
        return jsonify({'success': True, 'message_id': msg.id})
    
    return jsonify({'error': 'Fichier invalide'}), 400

@bp.route('/defis', methods=['GET'])
@login_required
def get_defis():
    defis = Defi.query.filter(Defi.is_active==True, Defi.expires_at > datetime.utcnow()).order_by(Defi.created_at.desc()).all()
    return jsonify([{
        'id': d.id,
        'creator': User.query.get(d.creator_id).username,
        'title': d.title,
        'description': d.description,
        'defi_type': d.defi_type,
        'reward': d.reward,
        'participants': d.participants.count(),
        'votes': d.votes.count(),
        'expires': d.expires_at.isoformat()
    } for d in defis])

@bp.route('/defis/create', methods=['POST'])
@login_required
def create_defi():
    data = request.get_json()
    defi = Defi(
        creator_id=current_user.id,
        title=data.get('title'),
        description=data.get('description'),
        defi_type=data.get('defi_type', 'general'),
        reward=data.get('reward', '⭐'),
        expires_at=datetime.utcnow() + timedelta(hours=data.get('duration', 24))
    )
    db.session.add(defi)
    db.session.commit()
    return jsonify({'success': True, 'defi_id': defi.id})

@bp.route('/defis/<int:defi_id>/join', methods=['POST'])
@login_required
def join_defi(defi_id):
    data = request.get_json()
    participant = DefiParticipant(
        defi_id=defi_id,
        user_id=current_user.id,
        content=data.get('content', '')
    )
    db.session.add(participant)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/defis/<int:defi_id>/vote/<int:participant_id>', methods=['POST'])
@login_required
def vote_defi(defi_id, participant_id):
    existing = DefiVote.query.filter_by(defi_id=defi_id, voter_id=current_user.id).first()
    if existing:
        return jsonify({'error': 'Déjà voté'}), 400
    vote = DefiVote(defi_id=defi_id, voter_id=current_user.id, participant_id=participant_id)
    db.session.add(vote)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/messages/edit/<int:message_id>', methods=['POST'])
@login_required
def edit_message(message_id):
    msg = Message.query.get_or_404(message_id)
    if msg.sender_id != current_user.id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    data = request.get_json()
    new_content = data.get('content', '').strip()
    if not new_content:
        return jsonify({'error': 'Message vide'}), 400
    
    msg.content = new_content
    msg.is_edited = True
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/messages/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    msg = Message.query.get_or_404(message_id)
    if msg.sender_id != current_user.id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    msg.is_deleted = True
    msg.content = 'Message supprimé'
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/unlike/<int:user_id>', methods=['POST'])
@login_required
def unlike_user(user_id):
    like = Like.query.filter_by(liker_id=current_user.id, liked_id=user_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Pas de like trouvé'}), 404
