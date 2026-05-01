from flask_socketio import emit, join_room
from flask_login import current_user
from app import socketio

# Stocker les appels en cours
active_calls = {}

@socketio.on('join_chat')
def handle_join(data):
    join_room(f'user_{current_user.id}')

@socketio.on('start_call')
def handle_start_call(data):
    """Un utilisateur lance un appel"""
    target = data['to_user']
    call_type = data['type']  # 'video' ou 'voice'
    
    # Créer un ID d'appel unique
    import time
    call_id = f"call_{current_user.id}_{target}_{int(time.time())}"
    
    active_calls[call_id] = {
        'caller': current_user.id,
        'target': target,
        'type': call_type,
        'status': 'ringing'
    }
    
    # Notifier le destinataire
    emit('incoming_call', {
        'call_id': call_id,
        'from': current_user.username,
        'type': call_type
    }, room=f'user_{target}')
    
    # Dire à l'appelant que ça sonne
    emit('call_ringing', {'call_id': call_id})

@socketio.on('accept_call')
def handle_accept(data):
    """Destinataire accepte l'appel"""
    call_id = data['call_id']
    if call_id in active_calls:
        active_calls[call_id]['status'] = 'active'
        emit('call_accepted', {'call_id': call_id, 'type': active_calls[call_id]['type']}, room=f'user_{active_calls[call_id]["caller"]}')

@socketio.on('reject_call')
def handle_reject(data):
    """Destinataire refuse"""
    call_id = data['call_id']
    if call_id in active_calls:
        emit('call_rejected', {}, room=f'user_{active_calls[call_id]["caller"]}')
        del active_calls[call_id]

@socketio.on('end_call')
def handle_end(data):
    call_id = data['call_id']
    if call_id in active_calls:
        target = active_calls[call_id]['target'] if current_user.id == active_calls[call_id]['caller'] else active_calls[call_id]['caller']
        emit('call_ended', {}, room=f'user_{target}')
        del active_calls[call_id]
