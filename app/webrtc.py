from flask_socketio import emit, join_room
from flask_login import current_user
from flask import request
from app import socketio
import time
import random

# ========== STOCKAGE ÉTAT SERVEUR ==========
games = {}  # {room: {players: {}, choices: {}, scores: {}, config: {}}}

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')
        print(f"🟢 {current_user.username} connecté (user_{current_user.id})")

@socketio.on('join_chat')
def handle_join(data):
    room = f'chat_{data["match_id"]}'
    join_room(room)
    print(f"💬 {current_user.username} → {room}")

# ========== PIERRE FEUILLE CISEAUX ==========

@socketio.on('rps_invite')
def handle_rps_invite(data):
    """Joueur A invite Joueur B"""
    target = data['to_user']
    config = {
        'manches': data.get('manches', 3),
        'gage': data.get('gage', 'Gage surprise'),
        'inviter': current_user.id,
        'invited': target,
        'timestamp': time.time()
    }
    
    print(f"📤 RPS: {current_user.username} → user_{target} | {config['manches']} manches | {config['gage']}")
    
    emit('rps_invite_received', {
        'manches': config['manches'],
        'gage': config['gage'],
        'from': current_user.username
    }, room=f'user_{target}')

@socketio.on('rps_accept')
def handle_rps_accept(data):
    """Joueur B accepte"""
    match_id = data['match_id']
    room = f'chat_{match_id}'
    
    games[match_id] = {
        'players': {},
        'choices': {},
        'scores': {current_user.id: 0},
        'config': {
            'manches': data.get('manches', 3),
            'gage': data.get('gage', 'Gage'),
            'current_manche': 0
        }
    }
    
    print(f"✅ RPS accepté! Match {match_id}")
    
    emit('rps_accepted', {
        'manches': data.get('manches', 3),
        'gage': data.get('gage', '')
    }, room=f'user_{data["to_user"]}')

@socketio.on('rps_decline')
def handle_rps_decline(data):
    print(f"❌ RPS refusé")
    emit('rps_declined', {}, room=f'user_{data["to_user"]}')

@socketio.on('rps_round_choice')
def handle_rps_choice(data):
    """Un joueur a fait son choix"""
    match_id = data['match_id']
    choice = data['choice']
    
    if match_id not in games:
        games[match_id] = {'choices': {}, 'players': {}}
    
    games[match_id]['choices'][current_user.id] = choice
    games[match_id]['players'][current_user.id] = current_user.username
    
    print(f"🎮 {current_user.username} → {choice} (match {match_id}) | {len(games[match_id]['choices'])}/2")
    
    # Attendre les 2 joueurs
    if len(games[match_id]['choices']) >= 2:
        players = list(games[match_id]['choices'].keys())[:2]
        p1, p2 = players[0], players[1]
        c1, c2 = games[match_id]['choices'][p1], games[match_id]['choices'][p2]
        
        # Déterminer le gagnant
        if c1 == c2:
            winner = 'draw'
        elif (c1 == 'rock' and c2 == 'scissors') or \
             (c1 == 'paper' and c2 == 'rock') or \
             (c1 == 'scissors' and c2 == 'paper'):
            winner = p1
        else:
            winner = p2
        
        print(f"🏆 RPS: {c1} vs {c2} → {winner}")
        
        # Envoyer le résultat aux DEUX joueurs
        emit('rps_round_result', {
            'opponent_choice': c2,
            'winner': winner,
            'players': {p1: c1, p2: c2}
        }, room=f'user_{p1}')
        
        emit('rps_round_result', {
            'opponent_choice': c1,
            'winner': winner,
            'players': {p1: c1, p2: c2}
        }, room=f'user_{p2}')
        
        # Réinitialiser pour la prochaine manche
        games[match_id]['choices'] = {}

# ========== ACTION OU VÉRITÉ ==========

@socketio.on('av_invite')
def handle_av_invite(data):
    print(f"📤 AV: {current_user.username} → user_{data['to_user']}")
    emit('av_invite_received', {
        'version': data['version'],
        'from': current_user.username
    }, room=f'user_{data["to_user"]}')

@socketio.on('av_accept')
def handle_av_accept(data):
    print(f"✅ AV accepté")
    emit('av_accepted', {
        'version': data.get('version', 'classic')
    }, room=f'user_{data["to_user"]}')

@socketio.on('av_decline')
def handle_av_decline(data):
    emit('av_declined', {}, room=f'user_{data["to_user"]}')

@socketio.on('av_send')
def handle_av_send(data):
    emit('av_receive', {
        'type': data['type'],
        'challenge': data['challenge']
    }, room=f'user_{data["to_user"]}')

# ========== APPELS ==========

@socketio.on('invite_call')
def handle_invite_call(data):
    print(f"📞 Appel: {current_user.username} → user_{data['to_user']}")
    emit('incoming_call', {
        'from': current_user.username,
        'from_id': current_user.id,
        'call_type': data['call_type']
    }, room=f'user_{data["to_user"]}')
