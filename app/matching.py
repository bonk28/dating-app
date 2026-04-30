from app.models import User, Like, Match
from app import db
from datetime import datetime, timedelta

class SmartMatching:
    def __init__(self, user):
        self.user = user
    
    def get_potential_matches(self, limit=20):
        """Algorithme intelligent de matching"""
        # Récupérer les IDs déjà swipés
        swiped = [l.liked_id for l in self.user.likes_sent.all()]
        swiped.append(self.user.id)
        
        # Base query
        query = User.query.filter(
            ~User.id.in_(swiped),
            User.is_active == True
        )
        
        # Filtres de préférence
        if self.user.looking_for:
            query = query.filter(User.gender == self.user.looking_for)
        
        users = query.all()
        scored_users = []
        
        for u in users:
            score = 0
            
            # Compatibilité intérêts (0-30 points)
            if self.user.interests and u.interests:
                my_int = set(i.strip().lower() for i in self.user.interests.split(','))
                their_int = set(i.strip().lower() for i in u.interests.split(','))
                common = my_int & their_int
                score += min(len(common) * 10, 30)
            
            # Proximité d'âge (0-20 points)
            if self.user.age and u.age:
                diff = abs(self.user.age - u.age)
                if diff <= 2: score += 20
                elif diff <= 5: score += 15
                elif diff <= 10: score += 10
            
            # Proximité géographique (0-25 points)
            if self.user.latitude and u.latitude:
                dist = self._calculate_distance(
                    self.user.latitude, self.user.longitude,
                    u.latitude, u.longitude
                )
                if dist <= 5: score += 25
                elif dist <= 20: score += 20
                elif dist <= 50: score += 15
            
            # Bonus activité récente (0-15 points)
            if u.last_seen and (datetime.utcnow() - u.last_seen).days < 1:
                score += 15
            elif u.last_seen and (datetime.utcnow() - u.last_seen).days < 7:
                score += 10
            
            # Bonus photo (0-10 points)
            if u.photo: score += 5
            if u.photos.count() > 1: score += 5
            
            u.match_score = score
            u.distance = dist if u.latitude else None
            scored_users.append(u)
        
        scored_users.sort(key=lambda x: x.match_score, reverse=True)
        return scored_users[:limit]
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        from math import radians, sin, cos, sqrt, atan2
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return int(6371 * c)
