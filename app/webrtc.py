from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app import socketio

# Gestion des appels WebRTC
active_calls = {}

@socketio.on('call_user')
def handle_call(data):
    to_user = data['to_user']
    call_type = data['call_type']  # 'video' ou 'voice'
    from_user = current_user.username
    
    # Créer une room pour l'appel
    room = f"call_{current_user.id}_{to_user}_{int(time.time())}"
    
    emit('incoming_call', {
        'from': from_user,
        'from_id': current_user.id,
        'call_type': call_type,
        'room': room
    }, room=f'user_{to_user}')
    
    active_calls[room] = {
        'caller': current_user.id,
        'callee': to_user,
        'type': call_type,
        'status': 'ringing'
    }

@socketio.on('accept_call')
def handle_accept(data):
    room = data['room']
    join_room(room)
    if room in active_calls:
        active_calls[room]['status'] = 'active'
        emit('call_accepted', {'room': room}, room=f'user_{active_calls[room]["caller"]}')

@socketio.on('reject_call')
def handle_reject(data):
    room = data['room']
    if room in active_calls:
        emit('call_rejected', {'room': room}, 
             room=f'user_{active_calls[room]["caller"]}')
        del active_calls[room]

@socketio.on('signal')
def handle_signal(data):
    """Relayer les signaux WebRTC (SDP, ICE candidates)"""
    room = data['room']
    emit('signal', {
        'type': data['type'],
        'sdp': data.get('sdp'),
        'candidate': data.get('candidate')
    }, room=room, include_self=False)

@socketio.on('end_call')
def handle_end(data):
    room = data['room']
    if room in active_calls:
        emit('call_ended', {'room': room}, room=room)
        del active_calls[room]

# ============ JEUX TEMPS RÉEL ============
rps_games = {}

@socketio.on('game_ready')
def handle_game_ready(data):
    match_id = data['match_id']
    game = data['game']
    room = f'chat_{match_id}'
    
    if game == 'rps':
        if match_id not in rps_games:
            rps_games[match_id] = {}
        rps_games[match_id][current_user.id] = None
        
        emit('rps_opponent_ready', {}, room=room, include_self=False)

@socketio.on('rps_choice_confirmed')
def handle_rps_confirmed(data):
    match_id = data['match_id']
    choice = data['choice']
    room = f'chat_{match_id}'
    
    if match_id not in rps_games:
        rps_games[match_id] = {}
    
    rps_games[match_id][current_user.id] = choice
    
    # Vérifier si les deux ont confirmé
    players = list(rps_games[match_id].keys())
    if len(players) >= 2:
        p1, p2 = players[0], players[1]
        c1 = rps_games[match_id].get(p1)
        c2 = rps_games[match_id].get(p2)
        
        if c1 and c2:
            # Déterminer le gagnant
            if c1 == c2:
                winner = 'draw'
            elif (c1 == 'rock' and c2 == 'scissors') or \
                 (c1 == 'paper' and c2 == 'rock') or \
                 (c1 == 'scissors' and c2 == 'paper'):
                winner = p1
            else:
                winner = p2
            
            # Envoyer le résultat
            emit('rps_result', {
                'players': {p1: c1, p2: c2},
                'winner': winner
            }, room=room)
            
            # Réinitialiser
            rps_games[match_id] = {}

@socketio.on('av_challenge')
def handle_av_challenge(data):
    """Relayer le défi à l'autre joueur"""
    emit('av_challenge_received', {
        'version': data['version'],
        'type': data['type'],
        'challenge': data['challenge']
    }, room=f'user_{data["to_user"]}')

@socketio.on('av_send')
def handle_av_send(data):
    """Transmettre le défi action/vérité à l'autre joueur"""
    emit('av_receive', {
        'version': data.get('version', 'classic'),
        'type': data['type'],
        'challenge': data['challenge']
    }, room=f'user_{data["to_user"]}')

# ============ RPS AVEC INVITATION ============
rps_games = {}

@socketio.on('rps_invite')
def handle_rps_invite(data):
    emit('rps_invite_received', {
        'manches': data['manches'],
        'gage': data['gage']
    }, room=f'user_{data["to_user"]}')

@socketio.on('rps_accept')
def handle_rps_accept(data):
    match_id = data['match_id']
    rps_games[match_id] = {
        'manches': data['manches'],
        'gage': data['gage'],
        'scores': {current_user.id: 0},
        'choices': {},
        'current_manche': 0
    }
    emit('rps_accepted', {'manches': data['manches'], 'gage': data['gage']}, room=f'user_{data["to_user"]}')

@socketio.on('rps_decline')
def handle_rps_decline(data):
    emit('rps_declined', {}, room=f'user_{data["to_user"]}')

@socketio.on('rps_round_choice')
def handle_rps_choice(data):
    match_id = data['match_id']
    choice = data['choice']
    
    if match_id not in rps_games:
        rps_games[match_id] = {'choices': {}}
    
    rps_games[match_id]['choices'][current_user.id] = choice
    
    if len(rps_games[match_id]['choices']) >= 2:
        p1, p2 = list(rps_games[match_id]['choices'].keys())[:2]
        c1, c2 = rps_games[match_id]['choices'][p1], rps_games[match_id]['choices'][p2]
        
        if c1 == c2: winner = 'draw'
        elif (c1=='rock' and c2=='scissors') or (c1=='paper' and c2=='rock') or (c1=='scissors' and c2=='paper'): winner = p1
        else: winner = p2
        
        # Envoyer résultat à chaque joueur
        emit('rps_round_result', {'opponent_choice': c2, 'winner': winner}, room=f'user_{p1}')
        emit('rps_round_result', {'opponent_choice': c1, 'winner': winner}, room=f'user_{p2}')
        
        rps_games[match_id]['choices'] = {}
