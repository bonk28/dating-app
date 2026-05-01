from flask_socketio import emit, join_room
from flask_login import current_user
from app import socketio

@socketio.on('join_chat')
def handle_join(data):
    room = f'chat_{data["match_id"]}'
    join_room(room)
    # Rejoindre aussi la room utilisateur pour les appels
    join_room(f'user_{current_user.id}')

@socketio.on('call_user')
def handle_call(data):
    """Envoyer une notification d'appel à l'autre utilisateur"""
    emit('incoming_call', {
        'from': data.get('from_user', 'Quelqu\'un'),
        'from_id': current_user.id,
        'type': data['type'],
        'match_id': data['match_id']
    }, room=f'user_{data["to_user"]}')

@socketio.on('call_rejected')
def handle_reject(data):
    emit('call_rejected', {}, room=f'user_{data["to"]}')

@socketio.on('signal')
def handle_signal(data):
    """Relayer les signaux WebRTC"""
    room = f'chat_{data["match_id"]}'
    emit('signal', {
        'sdp': data.get('sdp'),
        'candidate': data.get('candidate')
    }, room=room, include_self=False)

# RPS Game
rps_games = {}
@socketio.on('rps_invite')
def handle_rps_invite(data):
    emit('rps_invite_received', {'manches': data['manches'], 'gage': data['gage']}, room=f'user_{data["to_user"]}')
@socketio.on('rps_accept')
def handle_rps_accept(data):
    rps_games[data['match_id']] = {'manches': data['manches'], 'gage': data['gage'], 'choices': {}}
    emit('rps_accepted', {'manches': data['manches'], 'gage': data['gage']}, room=f'user_{data["to_user"]}')
@socketio.on('rps_decline')
def handle_rps_decline(data):
    emit('rps_declined', {}, room=f'user_{data["to_user"]}')
@socketio.on('rps_round_choice')
def handle_rps_choice(data):
    mid = data['match_id']
    if mid not in rps_games: rps_games[mid] = {'choices': {}}
    rps_games[mid]['choices'][current_user.id] = data['choice']
    if len(rps_games[mid]['choices']) >= 2:
        p1, p2 = list(rps_games[mid]['choices'].keys())[:2]
        c1, c2 = rps_games[mid]['choices'][p1], rps_games[mid]['choices'][p2]
        winner = 'draw' if c1==c2 else (p1 if (c1=='rock' and c2=='scissors') or (c1=='paper' and c2=='rock') or (c1=='scissors' and c2=='paper') else p2)
        emit('rps_round_result', {'opponent_choice': c2, 'winner': winner}, room=f'user_{p1}')
        emit('rps_round_result', {'opponent_choice': c1, 'winner': winner}, room=f'user_{p2}')
        rps_games[mid]['choices'] = {}

# AV Game
@socketio.on('av_invite')
def handle_av_invite(data): emit('av_invite_received', {'version': data['version']}, room=f'user_{data["to_user"]}')
@socketio.on('av_accept')
def handle_av_accept(data): emit('av_accepted', {'version': data['version']}, room=f'user_{data["to_user"]}')
@socketio.on('av_decline')
def handle_av_decline(data): emit('av_declined', {}, room=f'user_{data["to_user"]}')
@socketio.on('av_send')
def handle_av_send(data): emit('av_receive', {'type': data['type'], 'challenge': data['challenge']}, room=f'user_{data["to_user"]}')
