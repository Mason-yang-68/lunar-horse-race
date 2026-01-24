import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import random
from threading import Lock
import os
from themes import get_theme, get_questions, get_all_themes, DEFAULT_THEME

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_horse_year'
socketio = SocketIO(app, async_mode='eventlet')

# State
PLAYERS = {} # { sid: { name: "Name", score: 0, avatar: "horse1", finished: False } }
BOT_PLAYERS = []  # List of bot player IDs
GAME_STATE = {
    'status': 'WAITING', # WAITING, RACING, FINISHED
    'total_prize': 0,
    'theme': DEFAULT_THEME  # Current theme ID
}
ITEMS = {} # { item_id: { type: 'food'|'hardware', position: {x, y}, active: True } }
ACTIVE_EFFECTS = {} # { sid: { type: 'food'|'hardware', end_time: timestamp } }

HOST_CONTROL = {
    'controller_sid': None,  # Session ID of the controlling HOST
    'disconnect_time': None,  # Timestamp when controller disconnected
    'viewers': []  # List of viewer HOST session IDs
}
HOST_TAKEOVER_TIMEOUT = 30  # Seconds before viewers can take over

# Background task control - for cancellation on reset
TASK_FLAGS = {
    'quiz_running': False,
    'race_timer_running': False,
    'bot_running': False
}

# Rate limiting for shake events
RATE_LIMIT = {
    # sid: last_shake_time
}
RATE_LIMIT_INTERVAL = 0.05  # Minimum 50ms between shakes (20 per second max)

# Slot machine lock
SLOT_LOCK = Lock()

# Player timeout tracking for memory cleanup
PLAYER_LAST_ACTIVE = {
    # sid: last_active_timestamp
}
CLEANUP_TIMEOUT = 3600  # 1 hour in seconds

# Bot player auto-shake runner
def bot_runner():
    import time
    BOT_NAMES = ['小明', '阿華', '小美', '阿寶', '小強', '小花', '阿傑', '小玉', '阿龍']
    TASK_FLAGS['bot_running'] = True
    while GAME_STATE['status'] == 'RACING' and TASK_FLAGS['bot_running']:
        eventlet.sleep(random.uniform(0.1, 0.3))  # Faster shake interval for testing
        for bot_id in BOT_PLAYERS:
            if bot_id in PLAYERS and not PLAYERS[bot_id].get('finished'):
                player = PLAYERS[bot_id]
                current_time = time.time()
                
                # Check countdown
                race_start_time = GAME_STATE.get('race_start_time', 0)
                if current_time < race_start_time:
                    continue
                
                # Check if frozen or answering
                if player.get('freeze_until', 0) > current_time:
                    continue
                if player.get('answering_until', 0) > current_time:
                    # Bot auto-answers randomly
                    if random.random() < random.uniform(0.5, 0.9):  # Random 50%-90% chance correct
                        player['progress'] = min(100, player['progress'] + 3)
                        player['quiz_cooldown_until'] = current_time + 6
                    else:
                        player['freeze_until'] = current_time + 5
                        player['quiz_cooldown_until'] = current_time + 6
                    player['answering_until'] = 0
                    continue
                
                # Simulate shake - faster for testing
                intensity = random.randint(30, 60)
                base_move = 0.05  # Much faster for testing (was 0.0165)
                bonus = (intensity / 600.0)
                move_amount = base_move + bonus
                
                player['progress'] = min(100, player['progress'] + move_amount)
                
                # Check finish
                if player['progress'] >= 100 and not player.get('finished'):
                    player['finished'] = True
                    finished_count = sum(1 for p in PLAYERS.values() if p.get('finished'))
                    player['finish_order'] = finished_count
                    
                    # Emit player_finished event for leaderboard
                    socketio.emit('player_finished', {
                        'player_id': bot_id,
                        'player_name': player['name'],
                        'rank': finished_count
                    })
                    
                    if finished_count >= len(PLAYERS):
                        # All finished
                        print(f"BOT: All {len(PLAYERS)} players finished - calculating results!")
                        from server_render import on_calculate_results
                        socketio.start_background_task(on_calculate_results)
                
                # Broadcast update
                socketio.emit('player_update', {
                    'id': bot_id,
                    'progress': player['progress']
                })

@app.route('/')
def index():
    return render_template('host.html')

@app.route('/play')
def play():
    return render_template('client.html')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/path-editor')
def path_editor():
    """Tool for editing track path"""
    return render_template('path_editor.html')

@app.route('/api/themes')
def api_themes():
    """Get list of available themes"""
    return jsonify(get_all_themes())

# --- Socket Events ---

@socketio.on('set_theme')
def on_set_theme(data):
    """Set the current theme"""
    theme_id = data.get('theme_id', DEFAULT_THEME)
    theme = get_theme(theme_id)
    GAME_STATE['theme'] = theme_id
    print(f"[THEME] Theme set to: {theme['name']} ({theme_id})")
    print(f"[THEME] GAME_STATE['theme'] is now: {GAME_STATE['theme']}")
    
    # Broadcast theme change to all clients
    emit('theme_changed', {
        'theme_id': theme_id,
        'name': theme['name'],
        'track_background': theme.get('track_background'),
        'avatar_folder': theme.get('avatar_folder'),
        'avatar_prefix': theme.get('avatar_prefix', 'horse')
    }, broadcast=True)

@socketio.on('get_theme')
def on_get_theme():
    """Get current theme info"""
    theme = get_theme(GAME_STATE['theme'])
    emit('current_theme', {
        'theme_id': theme['id'],
        'name': theme['name'],
        'track_background': theme.get('track_background'),
        'avatar_folder': theme.get('avatar_folder'),
        'avatar_prefix': theme.get('avatar_prefix', 'horse')
    })

@socketio.on('connect')
def on_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def on_disconnect():
    import time
    
    # Handle HOST disconnection
    if HOST_CONTROL['controller_sid'] == request.sid:
        HOST_CONTROL['disconnect_time'] = time.time()
        print(f"HOST controller disconnected: {request.sid[:8]}...")
        # Notify all viewers that controller is offline
        socketio.emit('host_controller_offline', {
            'timeout': HOST_TAKEOVER_TIMEOUT
        }, namespace='/')
    elif request.sid in HOST_CONTROL['viewers']:
        HOST_CONTROL['viewers'].remove(request.sid)
        print(f"HOST viewer disconnected: {request.sid[:8]}...")
    
    # Handle player disconnection
    if request.sid in PLAYERS:
        player = PLAYERS[request.sid]
        # Keep ALL players during racing OR waiting (iOS may disconnect when screen locks)
        if GAME_STATE['status'] in ['RACING', 'WAITING']:
            print(f"Client disconnected but keeping player for rejoin: {player['name']}")
            # Mark as disconnected but don't remove - they can rejoin!
            player['disconnected'] = True
            # Notify host about disconnection
            emit('player_disconnected', {
                'player_id': request.sid,
                'player_name': player['name']
            }, broadcast=True)
        else:
            del PLAYERS[request.sid]
            emit('update_player_list', list(PLAYERS.values()), broadcast=True)
    print(f"Client disconnected: {request.sid}")

@socketio.on('host_register')
def on_host_register():
    """Register a HOST connection - first one becomes controller, others are viewers"""
    import time
    
    sid = request.sid
    
    # Check if old controller is still valid
    old_controller = HOST_CONTROL['controller_sid']
    
    # Case 1: No controller yet, or old controller has disconnected
    # (disconnect_time is set when controller disconnects)
    should_become_controller = False
    
    if old_controller is None:
        # No controller exists
        should_become_controller = True
        print(f"No controller exists, new HOST will be controller")
    elif old_controller == sid:
        # Same sid reconnected (unlikely but handle it)
        should_become_controller = True
        print(f"Same HOST controller reconnected")
    elif HOST_CONTROL['disconnect_time'] is not None:
        # Old controller has disconnected - allow immediate takeover
        # (This happens when user refreshes page - old sid disconnects, new sid connects)
        should_become_controller = True
        print(f"Old controller disconnected, new HOST takes over immediately")
        # Clear old viewers since they might be stale too
        HOST_CONTROL['viewers'] = []
    
    if should_become_controller:
        # Become the controller
        HOST_CONTROL['controller_sid'] = sid
        HOST_CONTROL['disconnect_time'] = None
        HOST_CONTROL['viewers'] = [v for v in HOST_CONTROL['viewers'] if v != sid]
        print(f"HOST controller registered: {sid[:8]}...")
        emit('host_status', {
            'is_controller': True,
            'message': '您是主控制者'
        })
    else:
        # Controller is still connected - become a viewer
        if sid not in HOST_CONTROL['viewers']:
            HOST_CONTROL['viewers'].append(sid)
        print(f"HOST viewer registered: {sid[:8]}... (controller: {old_controller[:8]}...)")
        
        emit('host_status', {
            'is_controller': False,
            'can_takeover': False,
            'takeover_remaining': 0,
            'message': '控制者已存在，您目前為觀看者'
        })
        
        # Send current game state to viewer so they see the same screen
        emit('update_player_list', list(PLAYERS.values()))
        emit('game_state_sync', {
            'status': GAME_STATE['status'],
            'total_prize': GAME_STATE.get('total_prize', 0),
            'players': [{'id': p['id'], 'name': p['name'], 'progress': p.get('progress', 0), 
                'avatar_id': p.get('avatar_id', 'horse1'), 'finished': p.get('finished', False)}
                       for p in PLAYERS.values()]
        })

@socketio.on('host_takeover')
def on_host_takeover(data=None):
    """
    Allow a viewer to forcefully take over as the main controller.
    Requires password verification.
    """
    global HOST_CONTROL
    
    # Check password
    password = data.get('password', '') if data else ''
    correct_password = os.environ.get('HOST_PASSWORD', '8888')
    
    # Simple check - if password provided, must match. 
    # If no password provided (legacy/dev), we might default to fail or existing behavior?
    # Let's enforce password if data is sent.
    
    if password != correct_password:
        emit('takeover_failed', {'reason': '密碼錯誤'}, to=request.sid)
        return
    
    sid = request.sid
    
    old_controller = HOST_CONTROL['controller_sid']
    HOST_CONTROL['controller_sid'] = sid
    HOST_CONTROL['disconnect_time'] = None
    
    # Remove from viewers if present
    if sid in HOST_CONTROL['viewers']:
        HOST_CONTROL['viewers'].remove(sid)
    
    print(f"HOST takeover: {old_controller[:8] if old_controller else 'None'}... -> {sid[:8]}...")
    
    emit('host_status', {
        'is_controller': True,
        'message': '已成功接管控制權'
    })
    
    # Notify all that new controller is active
    socketio.emit('host_controller_online', {}, namespace='/')


@socketio.on('rejoin_waiting')
def on_rejoin_waiting(data):
    """Handle player reconnection during waiting phase"""
    if GAME_STATE['status'] != 'WAITING':
        emit('rejoin_waiting_failed', {'message': '遊戲已開始'})
        return
    
    name = data.get('name', '')
    if not name:
        emit('rejoin_waiting_failed', {'message': '名稱錯誤'})
        return
    
    # Find existing player by name
    old_player = None
    old_id = None
    for pid, player in list(PLAYERS.items()):
        if player['name'] == name:
            old_player = player
            old_id = pid
            break
    
    if not old_player:
        emit('rejoin_waiting_failed', {'message': '找不到玩家'})
        return
    
    # Transfer player data to new session
    new_id = request.sid
    old_player['id'] = new_id
    old_player['disconnected'] = False
    
    # Move player to new session ID
    if old_id != new_id:
        PLAYERS[new_id] = old_player
        del PLAYERS[old_id]
        print(f"Player {name} rejoined waiting: {old_id[:8]}... -> {new_id[:8]}...")
    
    emit('rejoin_waiting_success', {'id': new_id, 'avatar_id': old_player.get('avatar_id', 'horse1')}, room=new_id)
    # Notify host about reconnection - send old_id so host can find the element
    emit('player_reconnected', {
        'player_id': new_id,
        'old_player_id': old_id,
        'player_name': name
    }, broadcast=True)
    emit('update_player_list', list(PLAYERS.values()), broadcast=True)

@socketio.on('join_game')
def on_join(data):
    if GAME_STATE['status'] != 'WAITING':
        emit('error', {'message': 'Game already started!'})
        return

    name = data.get('name', 'Unknown').strip()
    avatar_id = data.get('avatar_id', 'horse1')
    device_id = data.get('device_id', '')
    
    # Name validation: limit length to 10 characters
    if len(name) > 10:
        name = name[:10]
    
    # Check for empty name
    if not name:
        emit('error', {'message': '請輸入名字'})
        return
    
    # Check for duplicate names
    existing_player = None
    existing_pid = None
    for pid, player in list(PLAYERS.items()):
        if player['name'] == name:
            existing_player = player
            existing_pid = pid
            break
    
    if existing_player:
        # Same name exists - check device_id
        if device_id and existing_player.get('device_id') == device_id:
            # Same device! This is a reconnection, take over the slot
            print(f"Player {name} reconnecting with same device_id, taking over slot")
            new_id = request.sid
            existing_player['id'] = new_id
            existing_player['disconnected'] = False
            existing_player['avatar_id'] = avatar_id  # Update avatar if changed
            
            # Move player to new session ID
            if existing_pid != new_id:
                PLAYERS[new_id] = existing_player
                del PLAYERS[existing_pid]
            
            emit('join_success', {'id': new_id, 'name': name}, room=new_id)
            # Notify host about reconnection
            emit('player_reconnected', {
                'player_id': new_id,
                'old_player_id': existing_pid,
                'player_name': name
            }, broadcast=True)
            emit('update_player_list', list(PLAYERS.values()), broadcast=True)
            return
        else:
            # Different device, add suffix
            suffix = 2
            new_name = f"{name}{suffix}"
            existing_names = [p['name'] for p in PLAYERS.values()]
            while new_name in existing_names:
                suffix += 1
                new_name = f"{name}{suffix}"
            name = new_name
            # Notify player about name change
            emit('name_changed', {'original': data.get('name'), 'new': name})
    
    PLAYERS[request.sid] = {
        'id': request.sid,
        'name': name,
        'avatar_id': avatar_id,
        'device_id': device_id,  # Store device ID
        'progress': 0,
        'speed': 0,
        'finished': False,
        'dodge_until': 0  # Timestamp when dodge expires
    }
    emit('join_success', {'id': request.sid, 'name': name}, room=request.sid)
    emit('update_player_list', list(PLAYERS.values()), broadcast=True)

@socketio.on('rejoin_game')
def on_rejoin(data):
    """Handle player reconnection during racing"""
    if GAME_STATE['status'] != 'RACING':
        emit('rejoin_failed', {'message': '遊戲未進行中'})
        return
    
    name = data.get('name', '')
    device_id = data.get('device_id', '')
    if not name:
        emit('rejoin_failed', {'message': '名稱錯誤'})
        return
    
    # Find existing player by name
    old_player = None
    old_id = None
    for pid, player in list(PLAYERS.items()):
        if player['name'] == name:
            old_player = player
            old_id = pid
            break
    
    if not old_player:
        emit('rejoin_failed', {'message': '找不到玩家'})
        return
    
    # Optional: verify device_id matches (log warning if mismatch but allow)
    if device_id and old_player.get('device_id') and device_id != old_player.get('device_id'):
        print(f"WARNING: Player {name} rejoining with different device_id!")
    
    # Transfer player data to new session
    new_id = request.sid
    old_player['id'] = new_id
    old_player['disconnected'] = False
    
    # IMPORTANT: Clear any blocking states so player can move immediately
    old_player['freeze_until'] = 0
    old_player['answering_until'] = 0
    old_player['quiz_cooldown_until'] = 0
    
    # Move player to new session ID
    if old_id != new_id:
        PLAYERS[new_id] = old_player
        del PLAYERS[old_id]
        print(f"Player {name} rejoined: {old_id[:8]}... -> {new_id[:8]}... (states cleared)")
    
    emit('rejoin_success', {'id': new_id, 'progress': old_player['progress']}, room=new_id)
    # Notify host about reconnection - IMPORTANT: send old_id so host can find the element
    emit('player_reconnected', {
        'player_id': new_id,
        'old_player_id': old_id,  # Add old ID so host can find the disconnected horse element
        'player_name': name
    }, broadcast=True)
    emit('update_player_list', list(PLAYERS.values()), broadcast=True)

@socketio.on('add_bots')
def on_add_bots(data):
    """Add bot players for testing"""
    if GAME_STATE['status'] != 'WAITING':
        return
    
    count = min(int(data.get('count', 1)), 1)  # Add 1 bot at a time
    BOT_NAMES = ['小明', '阿華', '小美', '阿寶', '小強', '小花', '阿傑', '小玉', '阿龍']
    
    import uuid
    for i in range(count):
        if len(BOT_PLAYERS) >= 9:
            break
        bot_id = f"bot_{uuid.uuid4().hex[:8]}"
        name = BOT_NAMES[len(BOT_PLAYERS) % len(BOT_NAMES)]
        avatar_id = f"horse{random.randint(1, 10)}"
        
        PLAYERS[bot_id] = {
            'id': bot_id,
            'name': name,
            'avatar_id': avatar_id,
            'progress': 0,
            'speed': 0,
            'finished': False,
            'is_bot': True
        }
        BOT_PLAYERS.append(bot_id)
        print(f"Bot added: {name} ({bot_id})")
    
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
        
        # Lucky prize settings
        GAME_STATE['lucky_prize'] = int(data.get('lucky_prize', 500))
        GAME_STATE['lucky_winners_count'] = 0
        GAME_STATE['lucky_max_winners'] = 3
    except:
        GAME_STATE['total_prize'] = 0
        GAME_STATE['manual_prizes'] = None
        GAME_STATE['top3_prizes'] = None
        GAME_STATE['lucky_prize'] = 500
        GAME_STATE['lucky_winners_count'] = 0
        GAME_STATE['lucky_max_winners'] = 3
        
    GAME_STATE['status'] = 'RACING'
    # Set race start time (after 4 second countdown)
    import time
    GAME_STATE['race_start_time'] = time.time() + 4  # 4 seconds countdown
    
    # Reset progress and items
    ITEMS.clear()
    ACTIVE_EFFECTS.clear()
    for pid in PLAYERS:
        PLAYERS[pid]['progress'] = 0
        PLAYERS[pid]['speed'] = 0
        PLAYERS[pid]['finished'] = False
        PLAYERS[pid]['finish_order'] = 0
    
    # Start quiz spawning (will wait for countdown to finish)
    socketio.start_background_task(quiz_spawner)
    print("Quiz spawner started!")
    
    # Start bot runner if there are bots
    if BOT_PLAYERS:
        socketio.start_background_task(bot_runner)
        print(f"Bot runner started for {len(BOT_PLAYERS)} bots!")
    
    # Check if we need to emit prizes to client? No, only results.
    emit('race_started', {'total_prize': GAME_STATE['total_prize']}, broadcast=True)
    
    # Start race timer for auto-end and progress sync
    socketio.start_background_task(race_timer)
    print("Race timer started!")

# Maximum race time in seconds (10 minutes)
MAX_RACE_TIME = 600

def race_timer():
    """Background task to handle max race time and progress sync"""
    import time
    
    TASK_FLAGS['race_timer_running'] = True
    race_start = GAME_STATE.get('race_start_time', time.time())
    last_sync = 0
    SYNC_INTERVAL = 5  # Sync progress every 5 seconds
    
    while GAME_STATE['status'] == 'RACING' and TASK_FLAGS['race_timer_running']:
        eventlet.sleep(1)  # Check every second
        
        if GAME_STATE['status'] != 'RACING':
            break
        
        current_time = time.time()
        elapsed = current_time - race_start
        
        # Progress sync every 5 seconds
        if current_time - last_sync >= SYNC_INTERVAL:
            last_sync = current_time
            # Send full progress update to all clients
            progress_data = {
                'players': [{'id': p['id'], 'progress': p['progress'], 'finished': p.get('finished', False)} 
                           for p in PLAYERS.values()],
                'elapsed': int(elapsed),
                'remaining': max(0, int(MAX_RACE_TIME - elapsed))
            }
            socketio.emit('progress_sync', progress_data, namespace='/')
        
        # Check if all players finished
        active_players = [p for p in PLAYERS.values() if not p.get('is_bot', False)]
        all_finished = all(p.get('finished', False) for p in active_players) if active_players else False
        
        if all_finished:
            print("All players finished! Auto-calculating results...")
            socketio.emit('race_auto_end', {'reason': 'all_finished'}, namespace='/')
            # Wait a moment for clients to process
            eventlet.sleep(2)
            calculate_and_emit_results()
            break
        
        # Check max time
        if elapsed >= MAX_RACE_TIME:
            print(f"Max race time ({MAX_RACE_TIME}s) reached! Auto-ending race...")
            socketio.emit('race_auto_end', {'reason': 'timeout', 'elapsed': int(elapsed)}, namespace='/')
            # Wait a moment for clients to process
            eventlet.sleep(2)
            calculate_and_emit_results()
            break
    
    print("Race timer ended.")

# Question bank is now managed in themes.py

# Track which questions each player has seen
PLAYER_QUESTIONS = {}

def quiz_spawner():
    """Background task to send quiz questions to random players during race"""
    import time
    
    TASK_FLAGS['quiz_running'] = True
    
    # Wait 5 seconds after race starts before sending any questions
    # This gives players time to settle in
    QUIZ_DELAY_AFTER_START = 5
    race_start = GAME_STATE.get('race_start_time', time.time())
    initial_wait = race_start + QUIZ_DELAY_AFTER_START - time.time()
    if initial_wait > 0:
        print(f"Quiz spawner waiting {initial_wait:.1f}s before starting...")
        eventlet.sleep(initial_wait)
    
    # Notify host that quizzes are about to start
    socketio.emit('quiz_starting', {}, namespace='/')
    print("Quiz spawner: Questions are now active!")
    
    while GAME_STATE['status'] == 'RACING' and TASK_FLAGS['quiz_running']:
        # Dynamic interval based on player count: more players = faster questions
        # With 1-2 players: 2-3s (was 4-6s), with 10 players: ~0.6-1s
        player_count = max(1, len(PLAYERS))
        base_interval = 2.0 / (player_count ** 0.5)  # Scale with sqrt of players, faster base
        interval = random.uniform(base_interval, base_interval * 1.5)
        eventlet.sleep(max(1.0, interval))  # Minimum 1 second between questions
        if GAME_STATE['status'] != 'RACING':
            break
        
        current_time = time.time()
        
        # Get eligible players (not finished, not frozen, not answering, not in cooldown)
        eligible_players = []
        for p in PLAYERS.values():
            if p.get('finished'):
                continue
                
            # Check blocking conditions with logging
            if p.get('freeze_until', 0) >= current_time:
                # print(f"Skip {p['name']}: Frozen")
                continue
            
            # Check if answering (and fix stuck state if timeout passed)
            if p.get('answering_until', 0) > 0:
                if p.get('answering_until', 0) < current_time:
                    # Auto-clear stuck state
                    print(f"Server auto-clearing stuck answering state for {p['name']}")
                    p['answering_until'] = 0
                    p['current_question_id'] = None
                else:
                    # Still answering
                    # print(f"Skip {p['name']}: Answering")
                    continue
            
            if p.get('quiz_cooldown_until', 0) >= current_time:
                # print(f"Skip {p['name']}: Cooldown")
                continue
                
            eligible_players.append(p)
        if not eligible_players:
            continue
            
        # Pick a random player
        target_player = random.choice(eligible_players)
        player_id = target_player['id']
        
        # Initialize player's question history if needed
        if player_id not in PLAYER_QUESTIONS:
            PLAYER_QUESTIONS[player_id] = []
        
        # Get questions based on current theme
        current_theme = GAME_STATE.get('theme', DEFAULT_THEME)
        theme_questions = get_questions(current_theme)
        print(f"[QUIZ] Using theme: {current_theme}, total questions: {len(theme_questions)}")
        
        # Pick a question they haven't seen (or random if all seen)
        available_qs = [i for i, q in enumerate(theme_questions) if i not in PLAYER_QUESTIONS[player_id]]
        if not available_qs:
            available_qs = list(range(len(theme_questions)))  # Reset if all used
            PLAYER_QUESTIONS[player_id] = []
        
        q_index = random.choice(available_qs)
        question = theme_questions[q_index]
        PLAYER_QUESTIONS[player_id].append(q_index)
        
        # Randomize answer order
        original_options = question['options']
        correct_answer_text = original_options[question['answer']]
        
        # Create shuffled options
        shuffled_indices = list(range(len(original_options)))
        random.shuffle(shuffled_indices)
        shuffled_options = [original_options[i] for i in shuffled_indices]
        
        # Find new position of correct answer
        new_correct_index = shuffled_options.index(correct_answer_text)
        
        # Set answering state (15 seconds to answer, blocks shaking)
        target_player['answering_until'] = current_time + 15
        target_player['current_question_id'] = q_index  # Use index instead of 'id'
        target_player['shuffled_answer'] = new_correct_index  # Store shuffled answer
        
        print(f"Quiz sent to {target_player['name']}: Q#{q_index} (15s to answer)")
        
        # Send question to specific player only (with shuffled options)
        # Handle both 'question' and 'q' key formats for backwards compatibility
        question_text = question.get('question') or question.get('q', '')
        socketio.emit('quiz_question', {
            'question_id': q_index,
            'question': question_text,
            'options': shuffled_options,  # Shuffled!
            'timeout': 15  # Tell client about timeout (15 seconds)
        }, room=player_id)
        
        # Notify host that a question was sent (include player index for color)
        player_ids = list(PLAYERS.keys())
        player_index = player_ids.index(player_id) if player_id in player_ids else 0
        socketio.emit('quiz_sent', {
            'player_id': player_id,
            'player_name': target_player['name'],
            'player_index': player_index,
            'question': question_text
        }, namespace='/')

def check_item_collision(player_id, player_progress, is_dodging=False):
    """Check if player collides with any items"""
    import time
    collected_items = []
    
    for item_id, item in list(ITEMS.items()):
        if not item.get('active'):
            continue
            
        # Collision detection (within 8% progress for easier collection)
        if abs(player_progress - item['position']) < 8:
            # If dodging and it's hardware (bad item), skip it!
            if is_dodging and item['type'] == 'hardware':
                print(f"Player {player_id[:8]}... DODGED hardware at {item['position']:.1f}%!")
                item['active'] = False
                del ITEMS[item_id]
                socketio.emit('item_dodged', {
                    'item_id': item_id,
                    'player_id': player_id
                }, namespace='/')
                continue
            
            item['active'] = False
            collected_items.append(item)
            
            # Apply effect
            effect_duration = 3 if item['type'] == 'food' else 2
            ACTIVE_EFFECTS[player_id] = {
                'type': item['type'],
                'end_time': time.time() + effect_duration
            }
            
            print(f"Player {player_id[:8]}... collected {item['type']} at {item['position']:.1f}%!")
            print(f"Broadcasting item_collected event to all clients...")
            
            # Remove item and broadcast to ALL clients (including host)
            del ITEMS[item_id]
            socketio.emit('item_collected', {
                'item_id': item_id,
                'player_id': player_id,
                'effect': item['type']
            }, namespace='/')
            
    return collected_items

def get_speed_multiplier(player_id):
    """Get current speed multiplier based on active effects"""
    import time
    if player_id not in ACTIVE_EFFECTS:
        return 1.0
        
    effect = ACTIVE_EFFECTS[player_id]
    if time.time() > effect['end_time']:
        del ACTIVE_EFFECTS[player_id]
        print(f"Effect expired for player {player_id[:8]}...")
        return 1.0
        
    if effect['type'] == 'food':
        print(f"Player {player_id[:8]}... has SPEED BOOST (2x)!")
        return 2.0  # 2x speed boost - very noticeable!
    elif effect['type'] == 'hardware':
        print(f"Player {player_id[:8]}... is SLOWED (0.3x)!")
        return 0.3  # 70% speed reduction - very slow!
    return 1.0


@socketio.on('quiz_answer')
def on_quiz_answer(data):
    """Handle player's answer to a quiz question"""
    import time
    if GAME_STATE['status'] != 'RACING':
        return
    
    player_id = request.sid
    if player_id not in PLAYERS:
        return
    
    question_id = data.get('question_id')
    answer_index = data.get('answer')
    
    # Get questions based on current theme
    current_theme = GAME_STATE.get('theme', DEFAULT_THEME)
    theme_questions = get_questions(current_theme)
    
    # Find the question (question_id is actually the index in the list)
    question = None
    try:
        q_idx = int(question_id)
        if 0 <= q_idx < len(theme_questions):
            question = theme_questions[q_idx]
    except (ValueError, TypeError):
        pass
        
    if not question:
        # Provide fallback/cleanup if question not found to avoid player getting stuck
        if player_id in PLAYERS:
            PLAYERS[player_id]['answering_until'] = 0
            PLAYERS[player_id]['current_question_id'] = None
        return
    
    player = PLAYERS[player_id]
    current_time = time.time()
    
    # Clear answering state
    player['answering_until'] = 0
    player['current_question_id'] = None
    
    # Check against shuffled answer (stored when question was sent)
    shuffled_answer = player.get('shuffled_answer', question['answer'])
    is_correct = (answer_index == shuffled_answer)
    player['shuffled_answer'] = None  # Clear after use
    
    if is_correct:
        # Correct: Move forward 3% instantly + 6 second cooldown
        player['progress'] = min(100, player['progress'] + 3)
        player['quiz_cooldown_until'] = current_time + 6
        print(f"{player['name']} answered CORRECTLY! (+3%, cooldown 6s)")
    else:
        # Wrong: Freeze for 5 seconds + 6 second cooldown before next question
        player['freeze_until'] = current_time + 5
        player['quiz_cooldown_until'] = current_time + 6
        print(f"{player['name']} answered WRONG! (frozen 5s, cooldown 6s)")
    
    # Send result to the player
    socketio.emit('quiz_result', {
        'correct': is_correct,
        'correct_answer': question['answer']
    }, room=player_id)
    
    # Broadcast to host
    socketio.emit('quiz_answered', {
        'player_id': player_id,
        'player_name': player['name'],
        'question': question.get('question') or question.get('q', ''),
        'correct': is_correct
    }, namespace='/')


@socketio.on('quiz_timeout')
def on_quiz_timeout(data):
    """Handle when player didn't answer in time"""
    import time
    if GAME_STATE['status'] != 'RACING':
        return
    
    player_id = request.sid
    if player_id not in PLAYERS:
        return
    
    player = PLAYERS[player_id]
    current_time = time.time()
    
    # Clear answering state
    player['answering_until'] = 0
    player['current_question_id'] = None
    
    # No freeze penalty for timeout - just cooldown
    # player['freeze_until'] = current_time + 2  # Removed
    
    # Set 6 second cooldown before next question
    player['quiz_cooldown_until'] = current_time + 6
    
    print(f"{player['name']} quiz TIMEOUT! (no penalty, cooldown 6s)")
    
    # Notify host
    socketio.emit('quiz_timeout_notify', {
        'player_id': player_id,
        'player_name': player['name']
    }, namespace='/')


@socketio.on('slot_spin_start')
def on_slot_spin_start(data):
    """
    Handle slot machine spin request.
    Determine the result server-side with locking to prevent over-awarding lucky prizes.
    """
    sid = request.sid
    if sid not in PLAYERS:
        return

    player = PLAYERS[sid]
    
    # Simple probability for winning
    # 30% chance to win IF spots are available
    WIN_CHANCE = 0.3
    lucky_prize = GAME_STATE.get('lucky_prize', 0)
    max_winners = GAME_STATE.get('lucky_max_winners', 3)
    
    result_type = 'lose'
    win_amount = 200 # Consolation prize
    
    with SLOT_LOCK:
        winners_count = GAME_STATE.get('lucky_winners_count', 0)
        
        # Check if they can win
        if winners_count < max_winners:
            # Roll the dice
            if random.random() < WIN_CHANCE:
                result_type = 'win'
                win_amount = lucky_prize
                GAME_STATE['lucky_winners_count'] = winners_count + 1
            else:
                # 30% chance of "Near Miss" if they lost but spots were open
                if random.random() < 0.3:
                    result_type = 'near-miss'
                    
        # Store result in player temporarily
        PLAYERS[sid]['pending_slot_result'] = {
            'type': result_type,
            'amount': win_amount
        }
        
    # Generate stop indices for the client animation
    # 0=Horse (Win), 1=Coin, 2=Bag
    # Win: [0, 0, 0]
    # Near Miss: [0, 0, 1] (or similar)
    # Lose: [0, 1, 2] (random mismatch)
    
    stops = [0, 0, 0]
    if result_type == 'win':
        stops = [0, 0, 0]
    elif result_type == 'near-miss':
        stops = [0, 0, 1] 
    else:
        # Random loser combo
        stops = [random.choice([0,1,2]), random.choice([0,1,2]), random.choice([0,1,2])]
        # Ensure it's not a winner [0,0,0]
        while stops == [0, 0, 0]:
             stops = [random.choice([0,1,2]), random.choice([0,1,2]), random.choice([0,1,2])]

    emit('slot_spin_result', {
        'result_type': result_type,
        'stops': stops,
        'amount': win_amount
    })

@socketio.on('slot_animation_complete')
def on_slot_animation_complete(data):
    """
    Client confirms animation is done. 
    Finalize the prize and broadcast result if needed.
    """
    sid = request.sid
    if sid not in PLAYERS:
        return
        
    player = PLAYERS[sid]
    pending = player.get('pending_slot_result')
    
    if not pending:
        # Should not happen ideally
        return
        
    # Commit the prize
    player['slot_prize'] = pending['amount']
    
    # Send result back to player to show popup
    emit('slot_result_final', {
        'isWin': pending['type'] == 'win',
        'amount': pending['amount']
    })

    # Broadcast to host if they won big
    if pending['type'] == 'win':
         emit('host_slot_winner', {
            'player_name': player['name'],
            'amount': pending['amount'],
            'winners_count': GAME_STATE.get('lucky_winners_count', 0),
            'max_winners': GAME_STATE.get('lucky_max_winners', 3)
        }, broadcast=True)
         
    # Update global results immediately so leaderboard refreshes
    calculate_and_emit_results()


@socketio.on('shake_event')
def on_shake(data):
    if GAME_STATE['status'] != 'RACING':
        return
    
    intensity = data.get('intensity', 10)
    
    # Check if player exists
    if request.sid not in PLAYERS:
        # DEBUG: Player not found - log all current player IDs
        print(f"SHAKE from UNKNOWN sid: {request.sid[:8]}...")
        print(f"Current PLAYERS keys: {[k[:8] + '...' for k in PLAYERS.keys()]}")
        return
    
    if PLAYERS[request.sid].get('finished'):
        return  # Already finished
    
    import time
    current_time = time.time()
    
    # Rate limiting: max 20 shakes per second (50ms interval)
    last_shake = RATE_LIMIT.get(request.sid, 0)
    if current_time - last_shake < RATE_LIMIT_INTERVAL:
        return  # Too fast, ignore this shake
    RATE_LIMIT[request.sid] = current_time
    
    # Update last active time for memory cleanup tracking
    PLAYER_LAST_ACTIVE[request.sid] = current_time
    
    player = PLAYERS[request.sid]
    
    # Check if countdown is still in progress
    race_start_time = GAME_STATE.get('race_start_time', 0)
    if current_time < race_start_time:
        return  # Countdown not finished, cannot move yet
    
    # Check if player is answering a question (cannot shake)
    if player.get('answering_until', 0) > current_time:
        return  # Player is answering, cannot move
    
    # Check if player is frozen (answered wrong)
    if player.get('freeze_until', 0) > current_time:
        return  # Player is frozen, cannot move
    
    # Move horse
    base_move = 0.0165
    bonus = (intensity / 600.0)
    move_amount = base_move + bonus
    
    # Apply speed multiplier from items
    speed_multiplier = get_speed_multiplier(request.sid)
    move_amount *= speed_multiplier
    
    PLAYERS[request.sid]['progress'] += move_amount
    
    if PLAYERS[request.sid]['progress'] >= 100:
        PLAYERS[request.sid]['progress'] = 100
        PLAYERS[request.sid]['finished'] = True
        
        # Calculate rank based on how many finished
        finished_count = sum(1 for p in PLAYERS.values() if p.get('finished'))
        PLAYERS[request.sid]['finish_order'] = finished_count
        
        # Broadcast player finished event with rank
        emit('player_finished', {
            'player_id': request.sid,
            'player_name': PLAYERS[request.sid]['name'],
            'rank': finished_count
        }, broadcast=True)
        
        # Trigger slot machine for players finishing 4th or later
        if finished_count > 3:
            current_theme = GAME_STATE.get('theme', 'hashimae')
            theme = get_theme(current_theme)
            emit('slot_machine_trigger', {
                'rank': finished_count,
                'lucky_prize': GAME_STATE.get('lucky_prize', 500),
                'lucky_slots_remaining': GAME_STATE.get('lucky_max_winners', 3) - GAME_STATE.get('lucky_winners_count', 0),
                'avatar_folder': theme.get('avatar_folder', ''),
                'avatar_prefix': theme.get('avatar_prefix', 'horse')
            }, room=request.sid)
        
        # Check if ALL finished
        total_players = len(PLAYERS)
        print(f"Player {PLAYERS[request.sid]['name']} finished! Count: {finished_count}/{total_players}")
        if finished_count >= total_players:
            print(f"All {total_players} players finished - calculating results!")
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

def calculate_and_emit_results():
    """Calculate final results and emit to all clients - can be called from timer or socket event"""
    # Sort by finish order if available, else progress
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
                    amounts.append(600)  # Fixed amount for non-top-3
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
            
            # If player won a slot prize (lucky prize or consolation), override the default prize
            # Only for rank > 3 (since top 3 get special prizes)
            if i >= 3:
                if player.get('slot_prize'):
                    prize = player['slot_prize']
                else:
                    # Player hasn't played slots yet (or is playing), send special value
                    # We use -1 to indicate "Pending"
                    prize = -1
                
            results.append({
                'name': player['name'],
                'rank': i + 1,
                'prize': prize,
                'avatar_id': player.get('avatar_id', 'horse1')
            })
            
    socketio.emit('game_results', results, namespace='/')
    GAME_STATE['status'] = 'FINISHED'
    print(f"Game results emitted for {n} players")

@socketio.on('calculate_results')
def on_calculate_results():
    calculate_and_emit_results()

@socketio.on('reset_game')
def on_reset():
    # Stop all background tasks
    TASK_FLAGS['quiz_running'] = False
    TASK_FLAGS['race_timer_running'] = False
    TASK_FLAGS['bot_running'] = False
    
    # Reset game state
    GAME_STATE['status'] = 'WAITING'
    PLAYERS.clear()
    BOT_PLAYERS.clear()
    
    # Clear tracking data to prevent memory leaks
    RATE_LIMIT.clear()
    PLAYER_LAST_ACTIVE.clear()
    PLAYER_QUESTIONS.clear()
    
    print("Game reset: All tasks stopped, data cleared")
    emit('reset_game_client', broadcast=True)

if __name__ == '__main__':
    # Render會提供PORT環境變數
    port = int(os.environ.get('PORT', 5000))
    
    import socket
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = '127.0.0.1'
        
    print(f"Server running at http://{local_ip}:{port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
