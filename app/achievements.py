from app import db
from app.models import Achievement, UserAchievement
from datetime import datetime

ACHIEVEMENTS = [
    {'name': 'Premier Pas', 'description': 'Compléter son profil', 'icon': '🚀', 'condition': 'profile_started'},
    {'name': 'Perfect Profile', 'description': 'Ajouter photo, bio et intérêts', 'icon': '✨', 'condition': 'perfect_profile'},
    {'name': 'Social Butterfly', 'description': 'Envoyer 10 messages', 'icon': '🦋', 'condition': 'messages_10'},
    {'name': 'Chat King', 'description': 'Envoyer 100 messages', 'icon': '👑', 'condition': 'messages_100'},
    {'name': 'Match Maker', 'description': 'Obtenir 5 matches', 'icon': '💑', 'condition': 'matches_5'},
    {'name': 'Match Master', 'description': 'Obtenir 20 matches', 'icon': '💝', 'condition': 'matches_20'},
    {'name': 'Super Swiper', 'description': 'Faire 100 swipes', 'icon': '⭐', 'condition': 'swipes_100'},
    {'name': 'Early Bird', 'description': 'Se connecter avant 8h', 'icon': '🌅', 'condition': 'early_login'},
    {'name': 'Night Owl', 'description': 'Se connecter après minuit', 'icon': '🦉', 'condition': 'late_login'},
    {'name': 'Globe Trotter', 'description': 'Matcher avec 3 pays différents', 'icon': '🌍', 'condition': 'international'},
    {'name': 'Story Teller', 'description': 'Publier 5 stories', 'icon': '📸', 'condition': 'stories_5'},
    {'name': 'Ice Breaker', 'description': 'Utiliser 10 brise-glaces', 'icon': '🧊', 'condition': 'icebreakers_10'},
]

def create_default_achievements():
    for achievement_data in ACHIEVEMENTS:
        if not Achievement.query.filter_by(condition=achievement_data['condition']).first():
            achievement = Achievement(**achievement_data)
            db.session.add(achievement)
    db.session.commit()

def unlock_achievement(user, condition):
    achievement = Achievement.query.filter_by(condition=condition).first()
    if achievement:
        existing = UserAchievement.query.filter_by(
            user_id=user.id, achievement_id=achievement.id
        ).first()
        if not existing:
            ua = UserAchievement(user_id=user.id, achievement_id=achievement.id)
            db.session.add(ua)
            db.session.commit()
            return achievement.name
    return None
