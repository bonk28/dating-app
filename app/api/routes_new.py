from flask import jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import *
from app.achievements import unlock_achievement
from app.icebreakers import get_random_icebreaker, get_all_categories
from app.quiz import QUIZ_QUESTIONS, calculate_compatibility
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

def init_new_routes(bp):
    
    # ===== STORIES =====
    @bp.route('/stories', methods=['GET'])
    @login_required
    def get_stories():
        stories = Story.query.filter(
            Story.expires_at > datetime.utcnow()
        ).order_by(Story.created_at.desc()).all()
        
        return jsonify([{
            'id': s.id,
            'user_id': s.user_id,
            'username': s.user.username,
            'filename': s.filename,
            'caption': s.caption,
            'created_at': s.created_at.isoformat(),
            'views': s.views
        } for s in stories])
    
    @bp.route('/stories', methods=['POST'])
    @login_required
    def create_story():
        if 'file' not in request.files:
            return jsonify({'error': 'Fichier requis'}), 400
        
        file = request.files['file']
        if file.filename:
            filename = secure_filename(f"story_{current_user.id}_{datetime.now().timestamp()}.jpg")
            filepath = os.path.join('/opt/dating-app/app/static/uploads', filename)
            file.save(filepath)
            
            story = Story(
                user_id=current_user.id,
                filename=filename,
                caption=request.form.get('caption', ''),
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            db.session.add(story)
            db.session.commit()
            
            # Achievement
            story_count = Story.query.filter_by(user_id=current_user.id).count()
            if story_count >= 5:
                unlock_achievement(current_user, 'stories_5')
            
            return jsonify({'success': True, 'story_id': story.id})
        
        return jsonify({'error': 'Fichier invalide'}), 400
    
    # ===== ICE BREAKERS =====
    @bp.route('/icebreakers', methods=['GET'])
    @login_required
    def get_icebreakers():
        category = request.args.get('category')
        icebreaker = get_random_icebreaker(category)
        categories = get_all_categories()
        return jsonify({'icebreaker': icebreaker, 'categories': categories})
    
    @bp.route('/icebreakers/send', methods=['POST'])
    @login_required
    def send_icebreaker():
        data = request.get_json()
        match_id = data.get('match_id')
        message = data.get('message')
        
        msg = Message(
            match_id=match_id,
            sender_id=current_user.id,
            content=message,
            message_type='icebreaker'
        )
        db.session.add(msg)
        db.session.commit()
        
        # Achievement
        ice_count = Message.query.filter_by(
            sender_id=current_user.id, 
            message_type='icebreaker'
        ).count()
        if ice_count >= 10:
            unlock_achievement(current_user, 'icebreakers_10')
        
        return jsonify({'success': True})
    
    # ===== QUIZ =====
    @bp.route('/quiz/questions', methods=['GET'])
    @login_required
    def get_quiz():
        return jsonify(QUIZ_QUESTIONS)
    
    @bp.route('/quiz/submit', methods=['POST'])
    @login_required
    def submit_quiz():
        answers = request.get_json().get('answers', [])
        # Stocker les réponses dans la session ou la DB
        return jsonify({'success': True})
    
    @bp.route('/quiz/compatibility/<int:user_id>', methods=['GET'])
    @login_required
    def quiz_compatibility(user_id):
        # Récupérer les réponses des deux utilisateurs
        # Calculer la compatibilité
        return jsonify({'compatibility': 75})
    
    # ===== EVENTS =====
    @bp.route('/events', methods=['GET'])
    @login_required
    def get_events():
        events = VirtualEvent.query.filter(
            VirtualEvent.date > datetime.utcnow(),
            VirtualEvent.is_active == True
        ).all()
        
        return jsonify([{
            'id': e.id,
            'title': e.title,
            'description': e.description,
            'event_type': e.event_type,
            'date': e.date.isoformat(),
            'participants': EventParticipant.query.filter_by(event_id=e.id).count(),
            'max_participants': e.max_participants
        } for e in events])
    
    @bp.route('/events/<int:event_id>/join', methods=['POST'])
    @login_required
    def join_event(event_id):
        event = VirtualEvent.query.get_or_404(event_id)
        
        existing = EventParticipant.query.filter_by(
            event_id=event_id, user_id=current_user.id
        ).first()
        
        if existing:
            return jsonify({'error': 'Déjà inscrit'}), 400
        
        if EventParticipant.query.filter_by(event_id=event_id).count() >= event.max_participants:
            return jsonify({'error': 'Complet'}), 400
        
        participant = EventParticipant(event_id=event_id, user_id=current_user.id)
        db.session.add(participant)
        db.session.commit()
        
        return jsonify({'success': True})
    
    # ===== DND (Do Not Disturb) =====
    @bp.route('/dnd/toggle', methods=['POST'])
    @login_required
    def toggle_dnd():
        current_user.is_dnd = not current_user.is_dnd
        db.session.commit()
        return jsonify({'dnd_active': current_user.is_dnd})
    
    # ===== LOCATION SHARING =====
    @bp.route('/share-location', methods=['POST'])
    @login_required
    def share_location():
        data = request.get_json()
        match_id = data.get('match_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        # Désactiver les anciens partages
        LocationShare.query.filter_by(
            user_id=current_user.id, is_active=True
        ).update({'is_active': False})
        
        share = LocationShare(
            match_id=match_id,
            user_id=current_user.id,
            latitude=latitude,
            longitude=longitude
        )
        db.session.add(share)
        db.session.commit()
        
        return jsonify({'success': True})
    
    @bp.route('/location/<int:match_id>', methods=['GET'])
    @login_required
    def get_shared_location(match_id):
        share = LocationShare.query.filter_by(
            match_id=match_id, is_active=True
        ).filter(
            LocationShare.user_id != current_user.id
        ).order_by(LocationShare.shared_at.desc()).first()
        
        if share:
            return jsonify({
                'latitude': share.latitude,
                'longitude': share.longitude,
                'shared_at': share.shared_at.isoformat()
            })
        return jsonify({'error': 'Aucune position partagée'}), 404
    
    # ===== ACHIEVEMENTS =====
    @bp.route('/achievements', methods=['GET'])
    @login_required
    def get_achievements():
        all_achievements = Achievement.query.all()
        user_achievements = {ua.achievement_id: ua.unlocked_at 
                           for ua in current_user.achievements}
        
        return jsonify([{
            'id': a.id,
            'name': a.name,
            'description': a.description,
            'icon': a.icon,
            'unlocked': a.id in user_achievements,
            'unlocked_at': user_achievements.get(a.id, '').isoformat() if a.id in user_achievements else None
        } for a in all_achievements])
    
    # ===== DAILY QUESTION =====
    @bp.route('/daily-question', methods=['GET'])
    @login_required
    def get_daily_question():
        today = datetime.now().date()
        question = DailyQuestion.query.filter_by(date=today).first()
        
        if not question:
            # Créer une question du jour
            import random
            questions = [
                ("Café ou thé ?", "☕ Café", "🍵 Thé"),
                ("Chien ou chat ?", "🐶 Chien", "🐱 Chat"),
                ("Netflix ou sortie ?", "📺 Netflix", "🎉 Sortie"),
                ("Sucré ou salé ?", "🍰 Sucré", "🍕 Salé"),
            ]
            q = random.choice(questions)
            question = DailyQuestion(
                question=q[0], option_a=q[1], option_b=q[2], date=today
            )
            db.session.add(question)
            db.session.commit()
        
        user_answer = UserAnswer.query.filter_by(
            user_id=current_user.id, question_id=question.id
        ).first()
        
        return jsonify({
            'id': question.id,
            'question': question.question,
            'option_a': question.option_a,
            'option_b': question.option_b,
            'user_answer': user_answer.answer if user_answer else None
        })
    
    @bp.route('/daily-question/<int:question_id>', methods=['POST'])
    @login_required
    def answer_daily_question(question_id):
        answer = request.get_json().get('answer')
        
        existing = UserAnswer.query.filter_by(
            user_id=current_user.id, question_id=question_id
        ).first()
        
        if existing:
            existing.answer = answer
        else:
            ua = UserAnswer(
                user_id=current_user.id,
                question_id=question_id,
                answer=answer
            )
            db.session.add(ua)
        
        db.session.commit()
        return jsonify({'success': True})
    
    # ===== AUDIO MESSAGE =====
    @bp.route('/messages/voice/<int:match_id>', methods=['POST'])
    @login_required
    def send_voice_message(match_id):
        if 'audio' not in request.files:
            return jsonify({'error': 'Fichier audio requis'}), 400
        
        file = request.files['audio']
        if file.filename:
            filename = secure_filename(f"voice_{match_id}_{datetime.now().timestamp()}.webm")
            filepath = os.path.join('/opt/dating-app/app/static/uploads', filename)
            file.save(filepath)
            
            msg = Message(
                match_id=match_id,
                sender_id=current_user.id,
                content=filename,
                message_type='voice'
            )
            db.session.add(msg)
            db.session.commit()
            
            return jsonify({'success': True, 'message_id': msg.id})
        
        return jsonify({'error': 'Fichier invalide'}), 400
