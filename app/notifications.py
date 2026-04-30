from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from app import db
from app.models import Message, Match, Like

socketio = SocketIO()

def init_socketio(app):
    socketio.init_app(app, cors_allowed_origins="*")
    
    @socketio.on('connect')
    def handle_connect():
        if current_user.is_authenticated:
            join_room(f'user_{current_user.id}')
            emit('status', {'msg': f'{current_user.username} en ligne'}, broadcast=True)
    
    @socketio.on('join_chat')
    def handle_join_chat(data):
        room = f'chat_{data["match_id"]}'
        join_room(room)
    
    @socketio.on('typing')
    def handle_typing(data):
        room = f'chat_{data["match_id"]}'
        emit('typing', {'user': current_user.username, 'match_id': data['match_id']}, room=room, include_self=False)
    
    @socketio.on('new_match')
    def handle_match(data):
        emit('match_alert', {'from': current_user.username, 'to': data['user_id']}, room=f'user_{data["user_id"]}')
    
    return socketio
