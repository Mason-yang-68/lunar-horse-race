import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_horse_year'
socketio = SocketIO(app, async_mode='eventlet')

# State
PLAYERS = {} # { sid: { name: "Name", score: 0, avatar: "horse1", finished: False } }
GAME_STATE = {
    'status': 'WAITING', # WAITING, RACING, FINISHED
    'total_prize': 0
}

@app.route('/')
def index():
    return render_template('host.html')

@app.route('/play')
def play():
    return render_template('client.html')

# --- Socket Events ---

@socketio.on('connect')
def on_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def on_disconnect():
    if request.sid in PLAYERS:
        del PLAYERS[request.sid]
        emit('update_player_list', list(PLAYERS.values()), broadcast=True)
    print(f"Client disconnected: {request.sid}")

@socketio.on('join_game')
def on_join(data):
    if GAME_STATE['status'] != 'WAITING':
        emit('error', {'message': 'Game already started!'})
        return

    name = data.get('name', 'Unknown')
    avatar_id = data.get('avatar_id', 'horse1') 
    
    PLAYERS[request.sid] = {
        'id': request.sid,
        'name': name,
        'avatar_id': avatar_id,
        'progress': 0,
        'speed': 0,
        'finished': False
    }
    emit('join_success', {'id': request.sid}, room=request.sid)
    emit('update_player_list', list(PLAYERS.values()), broadcast=True)

@socketio.on('start_race')
def on_start_race(data):
    try:
        # Check if top3 prizes are provided
        top3_prizes = data.get('top3_prizes')
        if top3_prizes and isinstance(top3_prizes, list) and len(top3_prizes) >= 3:
            # Use custom top 3 prizes
            GAME_STATE['top3_prizes'] = [int(p) for p in top3_prizes[:3]]
            GAME_STATE['total_prize'] = sum(GAME_STATE['top3_prizes'])
            GAME_STATE['manual_prizes'] = None
        # Check if manual prize list is provided (legacy support)
        elif data.get('manual_prizes') and isinstance(data.get('manual_prizes'), list):
            # Use manual prizes
            GAME_STATE['manual_prizes'] = [int(p) for p in data.get('manual_prizes')]
            GAME_STATE['total_prize'] = sum(GAME_STATE['manual_prizes'])
            GAME_STATE['top3_prizes'] = None
        else:
            GAME_STATE['manual_prizes'] = None
            GAME_STATE['top3_prizes'] = None
            GAME_STATE['total_prize'] = int(data.get('amount', 0))
    except:
        GAME_STATE['total_prize'] = 0
        GAME_STATE['manual_prizes'] = None
        GAME_STATE['top3_prizes'] = None
        
    GAME_STATE['status'] = 'RACING'
    # Reset progress
    for pid in PLAYERS:
        PLAYERS[pid]['progress'] = 0
        PLAYERS[pid]['speed'] = 0
        PLAYERS[pid]['finished'] = False
        PLAYERS[pid]['finish_order'] = 0
    
    # Check if we need to emit prizes to client? No, only results.
    emit('race_started', {'total_prize': GAME_STATE['total_prize']}, broadcast=True)

@socketio.on('shake_event')
def on_shake(data):
    if GAME_STATE['status'] != 'RACING':
        return
    
    # User requested LONGER RACE (~2 mins)
    # Assumed shake rate: 2-3 shakes/sec ~ 150-180 shakes/min
    # 2 mins ~ 300-360 shakes
    # Progress 100 max.
    # Move amount ~ 100 / 300 ~ 0.33 per shake.
    
    intensity = data.get('intensity', 10)
    
    if request.sid in PLAYERS and not PLAYERS[request.sid].get('finished'):
        # Move horse
        # Intensity usually 15-50.
        # Old formula: 1 + (intensity/5) ~ 4-11 per shake -> 10-20 shakes to finish.
        # New Target: ~0.3 per shake.
        # Let's scale intensity.
        
        base_move = 0.1
        bonus = (intensity / 100.0) # If intensity 30 -> 0.3. Total 0.4. 
        # 100 / 0.4 = 250 shakes. Sounds about right.
        
        move_amount = base_move + bonus
        
        PLAYERS[request.sid]['progress'] += move_amount
        
        if PLAYERS[request.sid]['progress'] >= 100:
             PLAYERS[request.sid]['progress'] = 100
             PLAYERS[request.sid]['finished'] = True
             
             # Calculate rank based on how many finished
             finished_count = sum(1 for p in PLAYERS.values() if p.get('finished'))
             PLAYERS[request.sid]['finish_order'] = finished_count
             
             # Check if ALL finished
             total_players = len(PLAYERS)
             if finished_count >= total_players:
                 # Auto-Finish Logic
                 on_calculate_results()
        
        emit('player_update', {
            'id': request.sid, 
            'progress': PLAYERS[request.sid]['progress']
        }, broadcast=True)

@socketio.on('game_completed')
def on_game_completed(data):
    pass

def has_four(n):
    return '4' in str(n)

def solve_prizes(total, n_players):
    if n_players <= 0: return []
    # Ensure minimum 100 per player
    if total < n_players * 100:
        total = n_players * 100 

    prizes = [100] * n_players
    remainder = total - (100 * n_players)
    
    weights = []
    for i in range(n_players):
        if i == 0: w = 50
        elif i == 1: w = 30
        elif i == 2: w = 10
        else: w = 2
        weights.append(w)
        
    weight_sum = sum(weights)
    current_distributed = 0
    surplus_prizes = [0] * n_players
    
    for i in range(n_players):
        if weight_sum > 0:
            share = int((weights[i] / weight_sum) * remainder)
            share = (share // 100) * 100 
            surplus_prizes[i] = share
            current_distributed += share
        
    leftover = remainder - current_distributed
    idx = 0
    while leftover > 0:
        surplus_prizes[idx] += 100
        leftover -= 100
        idx = (idx + 1) % n_players
        
    final_prizes = [p + s for p, s in zip(prizes, surplus_prizes)]
    final_prizes.sort(reverse=True)
    
    # Fix "4"s
    attempts = 0
    while attempts < 1000:
        bad_indices = [i for i, x in enumerate(final_prizes) if has_four(x)]
        if not bad_indices:
            break
            
        for i in bad_indices:
            amount_to_move = 100
            if i > 0:
                final_prizes[i] -= amount_to_move
                final_prizes[i-1] += amount_to_move
                if not has_four(final_prizes[i]) and not has_four(final_prizes[i-1]) and final_prizes[i-1] >= final_prizes[i]:
                    break 
                final_prizes[i] += amount_to_move
                final_prizes[i-1] -= amount_to_move
            if i < n_players - 1:
                final_prizes[i] -= amount_to_move
                final_prizes[i+1] += amount_to_move
                if not has_four(final_prizes[i]) and not has_four(final_prizes[i+1]) and final_prizes[i] >= final_prizes[i+1]:
                    break
                final_prizes[i] += amount_to_move
                final_prizes[i+1] -= amount_to_move
            target = (i + 1) % n_players
            final_prizes[i] -= 100
            final_prizes[target] += 100
            final_prizes.sort(reverse=True)
        attempts += 1
        
    return final_prizes
    
@socketio.on('preview_prizes')
def on_preview_prizes(data):
    # Only calculate and return, don't save
    try:
        amount = int(data.get('amount', 0))
        n = int(data.get('count', 1))
        prizes = solve_prizes(amount, n)
        emit('prize_preview', prizes)
    except:
        emit('prize_preview', [])

@socketio.on('calculate_results')
def on_calculate_results():
    # Sort by finish order if available, else progress
    sorted_players = sorted(PLAYERS.values(), key=lambda x: (x.get('finished', False), x.get('finish_order', 999), x['progress']), reverse=True)
    # The sort logic:
    # We want finished=True first.
    # Inside finished=True, we want finish_order smallest (1, 2, 3...)
    # Inside finished=False, we want progress largest.
    # Simplify:
    # key: (is_finished, -finish_order, progress)
    # True > False.
    # finish_order: 1 is better than 2. So -1 > -2.
    
    sorted_players = sorted(PLAYERS.values(), key=lambda x: (
        1 if x.get('finished') else 0,
        -x.get('finish_order', 999) if x.get('finished') else 0,
        x['progress']
    ), reverse=True)
    
    total = GAME_STATE['total_prize']
    n = len(sorted_players)
    results = []
    
    if n > 0:
        if GAME_STATE.get('top3_prizes'):
            # Use custom top 3 prizes, rest get 100 each
            top3 = GAME_STATE['top3_prizes']
            amounts = []
            for i in range(n):
                if i == 0:
                    amounts.append(top3[0])
                elif i == 1:
                    amounts.append(top3[1])
                elif i == 2:
                    amounts.append(top3[2])
                else:
                    amounts.append(100)  # Fixed amount for non-top-3
        elif GAME_STATE.get('manual_prizes'):
             amounts = GAME_STATE['manual_prizes']
             # Ensure length matches or fill 0 / truncate
             if len(amounts) < n:
                 amounts.extend([0] * (n - len(amounts)))
             elif len(amounts) > n:
                 amounts = amounts[:n]
             amounts.sort(reverse=True)
        else:
             amounts = solve_prizes(total, n)
        
        for i, player in enumerate(sorted_players):
            prize = amounts[i] if i < len(amounts) else 0
            results.append({
                'name': player['name'],
                'rank': i + 1,
                'prize': prize,
                'avatar_id': player.get('avatar_id', 'horse1')
            })
            
    emit('game_results', results, broadcast=True)
    GAME_STATE['status'] = 'FINISHED'

@socketio.on('reset_game')
def on_reset():
    GAME_STATE['status'] = 'WAITING'
    PLAYERS.clear()
    emit('reset_game_client', broadcast=True)

if __name__ == '__main__':
    # Get local IP
    import socket
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = '127.0.0.1'
        
    print(f"Server running at http://{local_ip}:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
