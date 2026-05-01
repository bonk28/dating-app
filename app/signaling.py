"""
Serveur de signalisation WebRTC
Gère les rooms d'appel, échange SDP/ICE
"""
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app import socketio
import time

# Rooms actives
active_rooms = {}

@socketio.on('join_room')
def handle_join_room(data):
    """Rejoindre une room d'appel"""
    room = data['room']
    join_room(room)
    
    if room not in active_rooms:
        active_rooms[room] = {
            'users': {},
            'created_at': time.time()
        }
    
    active_rooms[room]['users'][current_user.id] = {
        'username': current_user.username,
        'joined_at': time.time()
    }
    
    # Notifier les autres dans la room
    emit('user_joined', {
        'user_id': current_user.id,
        'username': current_user.username,
        'users': list(active_rooms[room]['users'].keys())
    }, room=room, include_self=False)

@socketio.on('leave_room')
def handle_leave_room(data):
    """Quitter une room d'appel"""
    room = data['room']
    leave_room(room)
    
    if room in active_rooms:
        if current_user.id in active_rooms[room]['users']:
            del active_rooms[room]['users'][current_user.id]
        
        emit('user_left', {
            'user_id': current_user.id,
            'username': current_user.username
        }, room=room)
        
        # Nettoyer room vide
        if len(active_rooms[room]['users']) == 0:
            del active_rooms[room]

# ============ SIGNALING WEBRTC ============

@socketio.on('call_offer')
def handle_offer(data):
    """Relayer l'offre SDP au destinataire"""
    room = data['room']
    emit('call_offer', {
        'offer': data['offer'],
        'from': current_user.id,
        'from_name': current_user.username
    }, room=room, include_self=False)

@socketio.on('call_answer')
def handle_answer(data):
    """Relayer la réponse SDP"""
    room = data['room']
    emit('call_answer', {
        'answer': data['answer'],
        'from': current_user.id
    }, room=room, include_self=False)

@socketio.on('ice_candidate')
def handle_ice(data):
    """Relayer les candidats ICE"""
    room = data['room']
    emit('ice_candidate', {
        'candidate': data['candidate'],
        'from': current_user.id
    }, room=room, include_self=False)

@socketio.on('call_end')
def handle_call_end(data):
    """Fin d'appel"""
    room = data['room']
    emit('call_ended', {
        'from': current_user.id,
        'from_name': current_user.username
    }, room=room, include_self=False)

# ============ INVITATION APPEL ============

@socketio.on('invite_call')
def handle_invite_call(data):
    """Envoyer une invitation d'appel"""
    target_room = f"user_{data['to_user']}"
    call_room = f"call_{min(current_user.id, data['to_user'])}_{max(current_user.id, data['to_user'])}_{int(time.time())}"
    
    emit('incoming_call', {
        'from': current_user.username,
        'from_id': current_user.id,
        'call_type': data['call_type'],  # 'video' ou 'audio'
        'room': call_room
    }, room=target_room)
    
    return call_room

@socketio.on('accept_call')
def handle_accept_call(data):
    """Accepter un appel"""
    emit('call_accepted', {
        'room': data['room'],
        'from': current_user.id,
        'from_name': current_user.username
    }, room=data['room'])

@socketio.on('reject_call')
def handle_reject_call(data):
    """Refuser un appel"""
    emit('call_rejected', {
        'from': current_user.id,
        'from_name': current_user.username
    }, room=f"user_{data['to_user']}")
