from flask_socketio import emit, join_room
from flask_login import current_user
from app import socketio

# Stockage des games
rps_games = {}

@socketio.on('join_chat')
def handle_join(data):
    room = f'chat_{data["match_id"]}'
    join_room(room)
    join_room(f'user_{current_user.id}')
    print(f"✅ {current_user.username} a rejoint user_{current_user.id}")

# ========== RPS ==========
@socketio.on('rps_invite')
def handle_rps_invite(data):
    print(f"📤 RPS invite de {current_user.username} à user_{data['to_user']}")
    emit('rps_invite_received', {
        'manches': data['manches'],
        'gage': data['gage']
    }, room=f'user_{data["to_user"]}')

@socketio.on('rps_accept')
def handle_rps_accept(data):
    match_id = data['match_id']
    rps_games[match_id] = {'choices': {}, 'manches': data.get('manches', 3), 'gage': data.get('gage', '')}
    print(f"✅ RPS accepté pour match {match_id}")
    emit('rps_accepted', {'manches': data.get('manches', 3), 'gage': data.get('gage', '')}, room=f'user_{data["to_user"]}')

@socketio.on('rps_decline')
def handle_rps_decline(data):
    print(f"❌ RPS refusé")
    emit('rps_declined', {}, room=f'user_{data["to_user"]}')

@socketio.on('rps_round_choice')
def handle_rps_choice(data):
    match_id = data['match_id']
    choice = data['choice']
    
    if match_id not in rps_games:
        rps_games[match_id] = {'choices': {}}
    
    rps_games[match_id]['choices'][current_user.id] = choice
    print(f"🎮 {current_user.username} a choisi {choice} (match {match_id})")
    
    if len(rps_games[match_id]['choices']) >= 2:
        players = list(rps_games[match_id]['choices'].keys())[:2]
        p1, p2 = players[0], players[1]
        c1, c2 = rps_games[match_id]['choices'][p1], rps_games[match_id]['choices'][p2]
        
        if c1 == c2:
            winner = 'draw'
        elif (c1 == 'rock' and c2 == 'scissors') or (c1 == 'paper' and c2 == 'rock') or (c1 == 'scissors' and c2 == 'paper'):
            winner = p1
        else:
            winner = p2
        
        print(f"🏆 Résultat RPS: {c1} vs {c2} -> winner: {winner}")
        
        emit('rps_round_result', {'opponent_choice': c2, 'winner': winner}, room=f'user_{p1}')
        emit('rps_round_result', {'opponent_choice': c1, 'winner': winner}, room=f'user_{p2}')
        
        rps_games[match_id]['choices'] = {}

# ========== AV ==========
@socketio.on('av_invite')
def handle_av_invite(data):
    print(f"📤 AV invite de {current_user.username} à user_{data['to_user']}")
    emit('av_invite_received', {'version': data['version']}, room=f'user_{data["to_user"]}')

@socketio.on('av_accept')
def handle_av_accept(data):
    print(f"✅ AV accepté")
    emit('av_accepted', {'version': data.get('version', 'classic')}, room=f'user_{data["to_user"]}')

@socketio.on('av_decline')
def handle_av_decline(data):
    emit('av_declined', {}, room=f'user_{data["to_user"]}')

@socketio.on('av_send')
def handle_av_send(data):
    print(f"📩 AV défi envoyé")
    emit('av_receive', {'type': data['type'], 'challenge': data['challenge']}, room=f'user_{data["to_user"]}')

# ========== APPELS ==========
@socketio.on('invite_call')
def handle_invite_call(data):
    print(f"📞 Appel de {current_user.username} à user_{data['to_user']}")
    emit('incoming_call', {
        'from': current_user.username,
        'from_id': current_user.id,
        'call_type': data['call_type']
    }, room=f'user_{data["to_user"]}')
