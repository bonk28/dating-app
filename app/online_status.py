from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from flask import request
from app import db, socketio
from datetime import datetime
import time

# Stocker les utilisateurs en ligne
online_users = {}

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        user_id = current_user.id
        online_users[user_id] = {
            'username': current_user.username,
            'last_seen': datetime.utcnow(),
            'sid': request.sid
        }
        current_user.last_seen = datetime.utcnow()
        current_user.is_online = True
        db.session.commit()
        
        # Notifier tout le monde
        emit('user_online', {
            'user_id': user_id,
            'username': current_user.username
        }, broadcast=True)
        
        # Envoyer la liste des en ligne
        emit('online_users', get_online_list(), broadcast=False)

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        user_id = current_user.id
        if user_id in online_users:
            del online_users[user_id]
        current_user.is_online = False
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        
        emit('user_offline', {
            'user_id': user_id,
            'username': current_user.username,
            'last_seen': datetime.utcnow().strftime('%H:%M')
        }, broadcast=True)

@socketio.on('check_online')
def handle_check_online(data):
    user_id = data.get('user_id')
    is_online = user_id in online_users
    emit('online_status', {
        'user_id': user_id,
        'online': is_online,
        'last_seen': get_last_seen(user_id)
    })

def get_online_list():
    return [{'user_id': uid, 'username': info['username']} 
            for uid, info in online_users.items()]

def get_last_seen(user_id):
    from app.models import User
    user = User.query.get(user_id)
    if user and user.last_seen:
        return user.last_seen.strftime('%H:%M')
    return None
