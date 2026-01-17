import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import random
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_horse_year'
socketio = SocketIO(app, async_mode='eventlet')

# State
PLAYERS = {} # { sid: { name: "Name", score: 0, avatar: "horse1", finished: False } }
BOT_PLAYERS = []  # List of bot player IDs
GAME_STATE = {
    'status': 'WAITING', # WAITING, RACING, FINISHED
    'total_prize': 0
}
ITEMS = {} # { item_id: { type: 'food'|'hardware', position: {x, y}, active: True } }
ACTIVE_EFFECTS = {} # { sid: { type: 'food'|'hardware', end_time: timestamp } }

# Bot player auto-shake runner
def bot_runner():
    import time
    BOT_NAMES = ['🤖小明', '🤖小華', '🤖阿寶', '🤖大雄', '🤖小新', '🤖小丸', '🤖阿呆', '🤖小智', '🤖喵喵']
    while GAME_STATE['status'] == 'RACING':
        eventlet.sleep(random.uniform(0.3, 0.8))  # Random shake interval
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
                    if random.random() < 0.5:  # 50% chance correct
                        player['progress'] = min(100, player['progress'] + 5)
                        player['quiz_cooldown_until'] = current_time + 2
                    else:
                        player['freeze_until'] = current_time + 2
                        player['quiz_cooldown_until'] = current_time + 7
                    player['answering_until'] = 0
                    continue
                
                # Simulate shake
                intensity = random.randint(20, 50)
                base_move = 0.0165  # Match player shake speed (5x faster)
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

# --- Socket Events ---

@socketio.on('connect')
def on_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def on_disconnect():
    if request.sid in PLAYERS:
        player = PLAYERS[request.sid]
        # Keep ALL players during racing (iOS may disconnect when screen locks)
        if GAME_STATE['status'] == 'RACING':
            print(f"Client disconnected but keeping player for rejoin: {player['name']}")
            # Mark as disconnected but don't remove - they can rejoin!
            player['disconnected'] = True
        else:
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
        'finished': False,
        'dodge_until': 0  # Timestamp when dodge expires
    }
    emit('join_success', {'id': request.sid}, room=request.sid)
    emit('update_player_list', list(PLAYERS.values()), broadcast=True)

@socketio.on('rejoin_game')
def on_rejoin(data):
    """Handle player reconnection during racing"""
    if GAME_STATE['status'] != 'RACING':
        emit('rejoin_failed', {'message': '遊戲未進行中'})
        return
    
    name = data.get('name', '')
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
    emit('update_player_list', list(PLAYERS.values()), broadcast=True)

@socketio.on('add_bots')
def on_add_bots(data):
    """Add bot players for testing"""
    if GAME_STATE['status'] != 'WAITING':
        return
    
    count = min(int(data.get('count', 1)), 9)  # Max 9 bots
    BOT_NAMES = ['🤖小明', '🤖小華', '🤖阿寶', '🤖大雄', '🤖小新', '🤖小丸', '🤖阿呆', '🤖小智', '🤖喵喵']
    
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
    except:
        GAME_STATE['total_prize'] = 0
        GAME_STATE['manual_prizes'] = None
        GAME_STATE['top3_prizes'] = None
        
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

# Question bank (20 questions) - 橋前駅店內問題
QUESTIONS = [
    # 第一組：內場細節
    {"id": 1, "q": "在橋前駅店裡...招牌鬆餅咬開是？", "options": ["湯圓", "麻糬", "棉花糖"], "answer": 1},
    {"id": 2, "q": "在橋前駅店裡...那杯特殊的拿鐵叫？", "options": ["命運拿鐵", "直覺拿鐵", "覺醒拿鐵"], "answer": 1},
    {"id": 3, "q": "在橋前駅店裡...盤子上的手繪動物？", "options": ["貓咪", "狗狗", "兔子"], "answer": 0},
    # 第二組：環境與裝潢
    {"id": 4, "q": "在橋前駅店裡...外牆那隻貓去哪？", "options": ["釣魚", "太空", "飆車"], "answer": 1},
    {"id": 5, "q": "在橋前駅店裡...草皮上停什麼車？", "options": ["跑車", "老機車", "戰車"], "answer": 1},
    {"id": 6, "q": "在橋前駅店裡...廁所牆壁滿滿是？", "options": ["鏡子", "畫作塗鴉", "磁磚"], "answer": 1},
    # 第三組：店規與地理
    {"id": 7, "q": "在橋前駅店裡...店門口這條橋叫？", "options": ["關廟橋", "許縣溪橋", "新化橋"], "answer": 1},
    {"id": 8, "q": "在橋前駅店裡...帶寵物進室內要？", "options": ["綁繩子", "不落地", "穿衣服"], "answer": 1},
    {"id": 9, "q": "在橋前駅店裡...用餐限時幾分鐘？", "options": ["90分", "120分", "無限時"], "answer": 1},
    {"id": 10, "q": "在橋前駅店裡...每週哪一天公休？", "options": ["週一", "週二", "週三"], "answer": 1},
    # 第四組：菜單細節篇
    {"id": 11, "q": "在橋前駅店裡...招牌鬆餅形狀是？", "options": ["圓形", "方形", "愛心"], "answer": 2},
    {"id": 12, "q": "在橋前駅店裡...口袋麵包夾什麼？", "options": ["打拋豬", "咖哩雞", "牛肉片"], "answer": 0},
    {"id": 13, "q": "在橋前駅店裡...招牌義大利麵醬？", "options": ["青醬", "南瓜堅果", "墨魚汁"], "answer": 1},
    {"id": 14, "q": "在橋前駅店裡...燻雞可頌搭配？", "options": ["薯泥", "生菜沙拉", "白飯"], "answer": 1},
    # 第五組：店規與設施
    {"id": 15, "q": "在橋前駅店裡...每人低消要點？", "options": ["一杯飲料", "一份鬆餅", "200元"], "answer": 0},
    {"id": 16, "q": "在橋前駅店裡...WiFi 密碼通常是？", "options": ["老闆生日", "店裡電話", "12345678"], "answer": 1},
    {"id": 17, "q": "在橋前駅店裡...點餐結帳要去？", "options": ["廚房", "櫃台", "等店員來"], "answer": 1},
    # 第六組：地理與風格
    {"id": 18, "q": "在橋前駅店裡...店在南雄路幾段？", "options": ["一段", "二段", "三段"], "answer": 1},
    {"id": 19, "q": "在橋前駅店裡...戶外用餐區鋪？", "options": ["紅磚", "綠草皮", "水泥"], "answer": 1},
    {"id": 20, "q": "在橋前駅店裡...整間店走什麼風？", "options": ["日式風", "工業風", "宮廷風"], "answer": 1},
    # 第七組：點餐規則與自助服務
    {"id": 22, "q": "在橋前駅店裡...畫完單要去？", "options": ["櫃台結帳", "廚房大叫", "丟在桌上"], "answer": 0},
    {"id": 23, "q": "在橋前駅店裡...水和餐具要？", "options": ["自己拿", "大喊店員", "變魔術"], "answer": 0},
    {"id": 24, "q": "在橋前駅店裡...絕對不能帶？", "options": ["外食", "錢包", "手機"], "answer": 0},
    {"id": 25, "q": "在橋前駅店裡...鬆餅現烤要？", "options": ["等一下", "馬上有", "昨天做"], "answer": 0},
    {"id": 26, "q": "在橋前駅店裡...櫃台收什麼？", "options": ["現金", "支票", "欠條"], "answer": 0},
    # 第八組：飲料與餐點細節
    {"id": 29, "q": "在橋前駅店裡...冰沙上面有？", "options": ["薄荷葉/裝飾", "鹹菜", "荷包蛋"], "answer": 0},
    {"id": 30, "q": "在橋前駅店裡...熱拿鐵表面？", "options": ["有拉花", "黑黑的", "有蒼蠅"], "answer": 0},
    {"id": 31, "q": "在橋前駅店裡...鬆餅旁那是？", "options": ["鮮奶油/冰淇淋", "哇沙米", "醬油膏"], "answer": 0},
    {"id": 33, "q": "在橋前駅店裡...這裡披薩是？", "options": ["薄脆皮", "芝心厚片", "發糕皮"], "answer": 0},
    # 第九組：氛圍與視覺
    {"id": 37, "q": "在橋前駅店裡...店內燈光是？", "options": ["溫馨黃光", "手術燈白", "七彩霓虹"], "answer": 0},
    {"id": 39, "q": "在橋前駅店裡...二樓看出去？", "options": ["許縣溪/風景", "垃圾場", "火山爆發"], "answer": 0},
]

# Track which questions each player has seen
PLAYER_QUESTIONS = {}

def quiz_spawner():
    """Background task to send quiz questions to random players during race"""
    import time
    while GAME_STATE['status'] == 'RACING':
        # Dynamic interval based on player count: more players = faster questions
        # With 1-2 players: 4-6s, with 10 players: ~1.2-2s
        player_count = max(1, len(PLAYERS))
        base_interval = 4.0 / (player_count ** 0.5)  # Scale with sqrt of players
        interval = random.uniform(base_interval, base_interval * 1.5)
        eventlet.sleep(max(1.0, interval))  # Minimum 1 second between questions
        if GAME_STATE['status'] != 'RACING':
            break
        
        current_time = time.time()
        
        # Get eligible players (not finished, not frozen, not answering, not in cooldown)
        eligible_players = [
            p for p in PLAYERS.values() 
            if not p.get('finished') 
            and p.get('freeze_until', 0) < current_time
            and p.get('answering_until', 0) < current_time
            and p.get('quiz_cooldown_until', 0) < current_time
        ]
        if not eligible_players:
            continue
            
        # Pick a random player
        target_player = random.choice(eligible_players)
        player_id = target_player['id']
        
        # Initialize player's question history if needed
        if player_id not in PLAYER_QUESTIONS:
            PLAYER_QUESTIONS[player_id] = []
        
        # Pick a question they haven't seen (or random if all seen)
        available_qs = [q for q in QUESTIONS if q['id'] not in PLAYER_QUESTIONS[player_id]]
        if not available_qs:
            available_qs = QUESTIONS  # Reset if all used
            PLAYER_QUESTIONS[player_id] = []
        
        question = random.choice(available_qs)
        PLAYER_QUESTIONS[player_id].append(question['id'])
        
        # Randomize answer order
        original_options = question['options']
        correct_answer_text = original_options[question['answer']]
        
        # Create shuffled options
        shuffled_indices = list(range(len(original_options)))
        random.shuffle(shuffled_indices)
        shuffled_options = [original_options[i] for i in shuffled_indices]
        
        # Find new position of correct answer
        new_correct_index = shuffled_options.index(correct_answer_text)
        
        # Set answering state (10 seconds to answer, blocks shaking)
        target_player['answering_until'] = current_time + 10
        target_player['current_question_id'] = question['id']
        target_player['shuffled_answer'] = new_correct_index  # Store shuffled answer
        
        print(f"Quiz sent to {target_player['name']}: Q{question['id']} (10s to answer)")
        
        # Send question to specific player only (with shuffled options)
        socketio.emit('quiz_question', {
            'question_id': question['id'],
            'question': question['q'],
            'options': shuffled_options,  # Shuffled!
            'timeout': 10  # Tell client about timeout
        }, room=player_id)
        
        # Notify host that a question was sent (include player index for color)
        player_ids = list(PLAYERS.keys())
        player_index = player_ids.index(player_id) if player_id in player_ids else 0
        socketio.emit('quiz_sent', {
            'player_id': player_id,
            'player_name': target_player['name'],
            'player_index': player_index,
            'question': question['q']
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
    
    # Find the question
    question = next((q for q in QUESTIONS if q['id'] == question_id), None)
    if not question:
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
        # Correct: Move forward 5% instantly + 3 second cooldown
        player['progress'] = min(100, player['progress'] + 5)
        player['quiz_cooldown_until'] = current_time + 3  # Changed to 3s
        print(f"{player['name']} answered CORRECTLY! (+5%, cooldown 3s)")
    else:
        # Wrong: Freeze for 5 seconds + 7 second cooldown before next question
        player['freeze_until'] = current_time + 5  # Changed to 5 seconds
        player['quiz_cooldown_until'] = current_time + 7
        print(f"{player['name']} answered WRONG! (frozen 5s, cooldown 7s)")
    
    # Send result to the player
    socketio.emit('quiz_result', {
        'correct': is_correct,
        'correct_answer': question['answer']
    }, room=player_id)
    
    # Broadcast to host
    socketio.emit('quiz_answered', {
        'player_id': player_id,
        'player_name': player['name'],
        'question': question['q'],
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
    
    # Set 7 second cooldown before next question (was 10)
    player['quiz_cooldown_until'] = current_time + 7
    
    print(f"{player['name']} quiz TIMEOUT! (cooldown 7s)")
    
    # Notify host
    socketio.emit('quiz_timeout_notify', {
        'player_id': player_id,
        'player_name': player['name']
    }, namespace='/')


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
    player = PLAYERS[request.sid]
    current_time = time.time()
    
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
        
        # Check if ALL finished
        total_players = len(PLAYERS)
        if finished_count >= total_players:
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
    BOT_PLAYERS.clear()  # Clear bots on reset
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
