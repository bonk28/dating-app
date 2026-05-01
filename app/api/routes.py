from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from app import db
from app.api import bp
from app.models import User, Like, Match, Message
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

@bp.route('/swipe/<int:user_id>', methods=['POST'])
@login_required
def swipe(user_id):
    data = request.get_json()
    direction = data.get('direction', 'like')
    
    if direction == 'unlike':
        like = Like.query.filter_by(liker_id=current_user.id, liked_id=user_id).first()
        if like:
            db.session.delete(like)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'error': 'Pas de like'})
    
    if direction not in ['like', 'pass', 'super_like']:
        return jsonify({'error': 'Direction invalide'})
    
    like = Like.query.filter_by(liker_id=current_user.id, liked_id=user_id).first()
    if like:
        like.direction = direction
    else:
        like = Like(liker_id=current_user.id, liked_id=user_id, direction=direction)
        db.session.add(like)
    
    is_match = False
    match_id = None
    
    if direction in ['like', 'super_like']:
        reciprocal = Like.query.filter_by(liker_id=user_id, liked_id=current_user.id).filter(Like.direction.in_(['like', 'super_like'])).first()
        if reciprocal:
            other_user = User.query.get(user_id)
            compatibility = current_user.get_compatibility(other_user)
            match = Match(user1_id=min(current_user.id, user_id), user2_id=max(current_user.id, user_id), compatibility=compatibility)
            db.session.add(match)
            db.session.flush()
            match_id = match.id
            is_match = True
    
    db.session.commit()
    return jsonify({'success': True, 'is_match': is_match, 'match_id': match_id})

@bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    matches = Match.query.filter((Match.user1_id == current_user.id) | (Match.user2_id == current_user.id)).count()
    likes = Like.query.filter_by(liked_id=current_user.id).count()
    messages = Message.query.filter_by(sender_id=current_user.id).count()
    return jsonify({'matches': matches, 'likes_received': likes, 'messages_sent': messages})

@bp.route('/messages/<int:match_id>', methods=['GET'])
@login_required
def get_messages(match_id):
    match = Match.query.get_or_404(match_id)
    if current_user.id not in [match.user1_id, match.user2_id]:
        return jsonify({'error': 'Non autorisé'}), 403
    messages = Message.query.filter_by(match_id=match_id).order_by(Message.created_at).all()
    for msg in messages:
        if msg.sender_id != current_user.id:
            msg.is_read = True
    db.session.commit()
    return jsonify([{'id': m.id, 'sender_id': m.sender_id, 'content': m.content, 'message_type': m.message_type, 'is_read': m.is_read, 'is_edited': m.is_edited, 'is_deleted': m.is_deleted, 'created_at': m.created_at.isoformat()} for m in messages])

@bp.route('/messages/<int:match_id>', methods=['POST'])
@login_required
def send_message(match_id):
    data = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Message vide'}), 400
    match = Match.query.get_or_404(match_id)
    if current_user.id not in [match.user1_id, match.user2_id]:
        return jsonify({'error': 'Non autorisé'}), 403
    msg = Message(match_id=match_id, sender_id=current_user.id, content=content)
    db.session.add(msg)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/messages/edit/<int:message_id>', methods=['POST'])
@login_required
def edit_message(message_id):
    msg = Message.query.get_or_404(message_id)
    if msg.sender_id != current_user.id:
        return jsonify({'error': 'Non autorisé'}), 403
    msg.content = request.get_json().get('content', '')
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
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/messages/media/<int:match_id>', methods=['POST'])
@login_required
def send_media_message(match_id):
    if 'media' not in request.files:
        return jsonify({'error': 'Fichier requis'}), 400
    file = request.files['media']
    media_type = request.form.get('type', 'image')
    if file and file.filename:
        filename = secure_filename(f"chat_{match_id}_{datetime.now().timestamp()}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        msg = Message(match_id=match_id, sender_id=current_user.id, content=filename, message_type=media_type)
        db.session.add(msg)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Fichier invalide'}), 400

@bp.route('/messages/voice/<int:match_id>', methods=['POST'])
@login_required
def send_voice_message(match_id):
    if 'audio' not in request.files:
        return jsonify({'error': 'Audio requis'}), 400
    file = request.files['audio']
    if file and file.filename:
        filename = secure_filename(f"voice_{match_id}_{datetime.now().timestamp()}.webm")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        msg = Message(match_id=match_id, sender_id=current_user.id, content=filename, message_type='voice')
        db.session.add(msg)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Fichier invalide'}), 400

@bp.route('/update-location', methods=['POST'])
@login_required
def update_location():
    data = request.get_json()
    if data.get('latitude') and data.get('longitude'):
        current_user.latitude = data['latitude']
        current_user.longitude = data['longitude']
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Coordonnées manquantes'}), 400
