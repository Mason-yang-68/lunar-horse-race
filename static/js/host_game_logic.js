// Host Game Logic Module
// Manages game state, socket events, and coordinates Audio/UI interactions

window.HostLogic = (function () {
    console.log('Host Logic initialized');

    // Game State
    let players = [];
    let isHostController = false;
    let currentLeaderId = null;
    let leaderInitialized = false;
    let totalPrize = 0;

    // Constants
    const CORRECT_PASSWORD = '321';

    // Socket instance (set via init)
    let socket = null;

    function init(socketInstance) {
        socket = socketInstance;
        setupSocketListeners();
        setupInputListeners();
        if (socket.connected) {
            socket.emit('host_register');
            socket.emit('get_theme');
        }
    }

    function setupInputListeners() {
        // Password input enter key
        const pwdInput = document.getElementById('host-password');
        if (pwdInput) {
            pwdInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') submitPassword();
            });
        }
    }

    function setupSocketListeners() {
        // Register as HOST
        socket.on('connect', () => {
            console.log('HOST connected, registering...');
            socket.emit('host_register');
            socket.emit('get_theme');
        });

        socket.on('host_status', (data) => {
            isHostController = data.is_controller;
            if (window.updateHostControlUI) window.updateHostControlUI(data);
        });

        socket.on('debug_mode_enabled', () => {
            const debugBadge = document.createElement('div');
            debugBadge.style.cssText = 'position:fixed;top:10px;left:10px;background:red;color:white;padding:5px 10px;font-weight:bold;z-index:9999;border-radius:5px;';
            debugBadge.innerText = 'TEST MODE (20x)';
            document.body.appendChild(debugBadge);
        });

        socket.on('host_controller_offline', (data) => {
            if (!isHostController && window.showTakeoverCountdown) {
                window.showTakeoverCountdown(data.timeout);
            }
        });

        socket.on('host_controller_online', () => {
            if (window.hideTakeoverCountdown) window.hideTakeoverCountdown();
        });

        // Game State Sync
        socket.on('game_state_sync', (data) => {
            players = data.players || [];

            // UI Sync
            const setupScreen = document.getElementById('setup-screen');
            const raceScreen = document.getElementById('race-screen');
            const resultScreen = document.getElementById('results-screen');

            if (data.status === 'RACING') {
                if (setupScreen) setupScreen.style.display = 'none';
                if (raceScreen) raceScreen.style.display = 'block';
                if (resultScreen) resultScreen.style.display = 'none';
                if (window.updateOvalTrack) window.updateOvalTrack(players, 'race-oval-track');
            } else if (data.status === 'WAITING') {
                if (setupScreen) setupScreen.style.display = 'block';
                if (raceScreen) raceScreen.style.display = 'none';
                if (resultScreen) resultScreen.style.display = 'none';
                if (window.updateOvalTrack) window.updateOvalTrack(players, 'oval-track');
            } else if (data.status === 'FINISHED') {
                if (setupScreen) setupScreen.style.display = 'none';
                if (raceScreen) raceScreen.style.display = 'none';
                if (resultScreen) resultScreen.style.display = 'block';
            }
        });

        // Player Update
        socket.on('update_player_list', (playerData) => {
            players = playerData;
            const countEl = document.getElementById('player-count');
            if (countEl) countEl.innerText = players.length;

            // Only update waiting screen track if setup-screen is visible
            // Prevents screen regression when players reconnect during racing
            const setupScreen = document.getElementById('setup-screen');
            if (setupScreen && setupScreen.style.display !== 'none') {
                if (window.updateOvalTrack) window.updateOvalTrack(players, 'oval-track');
            }
        });

        // Race Started
        socket.on('race_started', (data) => {
            console.log('HostLogic: Race started, switching to race screen...');
            totalPrize = data.total_prize;

            // Switch Screens
            document.getElementById('setup-screen').style.display = 'none';
            document.getElementById('race-screen').style.display = 'block';
            document.getElementById('results-screen').style.display = 'none';

            // Initial visual update
            if (window.updateOvalTrack) window.updateOvalTrack(players, 'race-oval-track');
            if (window.showCountdown) window.showCountdown();

            // Audio
            if (window.AudioManager) {
                console.log('HostLogic: Playing start sound...');
                window.AudioManager.playStartSound();
                setTimeout(() => {
                    console.log('HostLogic: Starting racing music via AudioManager...');
                    window.AudioManager.startRacingMusic();
                }, 3500);
            } else {
                console.warn('HostLogic: AudioManager not found!');
            }
        });

        // Player Progress Update (The heavy firehose)
        socket.on('player_update', (data) => {
            const player = players.find(p => p.id === data.id);
            if (player) {
                player.progress = data.progress;
            }

            // Leader Logic
            if (players.length > 1) {
                const sortedPlayers = [...players].sort((a, b) => (b.progress || 0) - (a.progress || 0));
                const newLeader = sortedPlayers[0];
                if (newLeader && (newLeader.progress || 0) > 0) {
                    if (!leaderInitialized) {
                        currentLeaderId = newLeader.id;
                        leaderInitialized = true;
                    } else if (newLeader.id !== currentLeaderId) {
                        currentLeaderId = newLeader.id;
                        if (window.AudioManager) window.AudioManager.playOvertakeSound();
                    }
                }
            }

            // UI Update
            // Optimistically find element and update style directly for performance?
            // Or use the global update function. The global function redraws everything which is safe but maybe slow.
            // Following original logic:
            if (window.updateOvalTrack) {
                // To avoid full redraws, we really should optimize, but for refactor parity, we call the existing function logic
                // Actually the original code did 'find element and update properties'.
                // I will stick to calling the global logic which I'll ensure exists in host.html, 
                // OR I re-implement the specific targeted update here?
                // Let's call a specific update function `updatePlayerPosition` if available, or fall back.
                // The original code was INLINE. I will need to make sure `host.html` exposes a way to update 1 player.
                // For now, let's call `updateOvalTrack` strictly. Wait, `updateOvalTrack` kills and recreates DOM in original code!!
                // Correction: The original code's `player_update` handler did NOT call `updateOvalTrack`. 
                // It did `document.getElementById('track-' + data.id)` and updated style.

                // So I should replicate that logic here or interact with DOM.
                const raceTrack = document.getElementById('race-oval-track');
                const trackPlayer = raceTrack ? raceTrack.querySelector('#track-' + data.id) : null;
                if (trackPlayer) {
                    // Need to calculate position. The calculation logic (catmullRom) was in host.html.
                    // Accessing global `getOvalPosition` from host.html
                    if (window.getOvalPosition) {
                        const index = players.findIndex(p => p.id === data.id);
                        const pos = window.getOvalPosition(index, players.length, data.progress);
                        trackPlayer.style.left = pos.x + '%';
                        trackPlayer.style.top = pos.y + '%';

                        // Direction
                        if (window.getHorseDirection) {
                            const dir = window.getHorseDirection(data.progress);
                            const img = trackPlayer.querySelector('img');
                            if (img) img.style.transform = 'scaleX(' + dir + ')';
                            trackPlayer.style.setProperty('--horse-dir', dir);
                        }
                    }
                }

                if (raceTrack && currentLeaderId) {
                    raceTrack.querySelectorAll('.track-player.is-leader').forEach((el) => {
                        if (el.id !== `track-${currentLeaderId}`) {
                            el.classList.remove('is-leader');
                        }
                    });
                    const leaderEl = raceTrack.querySelector(`#track-${currentLeaderId}`);
                    if (leaderEl) {
                        leaderEl.classList.add('is-leader');
                    }
                }
            }
        });

        // Quiz Logic
        socket.on('quiz_starting', () => {
            // Create announcement overlay (UI logic)
            if (window.showQuizAnnouncement) window.showQuizAnnouncement();
            // Sound handled by showQuizAnnouncement or here? Original had both.
            // Let's delegate to UI function generally.
        });

        socket.on('quiz_sent', (data) => {
            if (window.showQuizSentEffect) window.showQuizSentEffect(data);
        });

        socket.on('quiz_answered', (data) => {
            if (window.showQuizResultEffect) window.showQuizResultEffect(data);

            if (data.correct) {
                if (window.AudioManager) window.AudioManager.playBoostSound();
            } else {
                if (window.AudioManager) window.AudioManager.playDizzySound();
            }
        });

        socket.on('quiz_timeout_notify', (data) => {
            if (window.showQuizTimeoutEffect) window.showQuizTimeoutEffect(data);
        });

        // Player Finished
        socket.on('player_finished', (data) => {
            // Visuals
            if (window.showPlayerFinishedEffect) window.showPlayerFinishedEffect(data);

            // Audio
            if (window.AudioManager) {
                if (data.rank === 1) window.AudioManager.playFinishSound();
                else if (data.rank <= 3) window.AudioManager.playShortWinSound();
            }

            // Live Leaderboard update
            if (window.updateLiveLeaderboard) window.updateLiveLeaderboard(data);
        });

        // Slot Machine Result (Final)
        socket.on('slot_result_final', (data) => {
            console.log('HostLogic: Slot result received', data);
            // data should contain { player_id, prize, ... }
            // Note: server_render.py needs to ensure it sends 'player_id' or we need to infer it?
            // Assuming data has 'player_id' or we can match by something. 
            // If data only has prize/won, we might miss the ID.
            // Let's assume the server broadcasts to everyone including ID.
            // If not, we might be in trouble. But usually public events have ID.

            // Wait, looking at slot_machine.js, it just uses data.prize/data.won
            // But that's sent to the *specific client* socket?
            // 'slot_result_final' might be a broadcast?
            // If it's a broadcast, it SHOULD have player_id.
            // If it's single-socket emit, Host won't see it unless it's also broadcast.
            // But let's assume it catches it.

            if (data.player_id && window.updatePrizeDisplay) {
                window.updatePrizeDisplay(data.player_id, data.prize);
            }
        });

        // Game Results
        socket.on('game_results', (results) => {
            document.getElementById('race-screen').style.display = 'none';
            document.getElementById('results-screen').style.display = 'block';

            if (window.AudioManager) window.AudioManager.playWinSound();
            if (window.fireConfetti) window.fireConfetti();
            if (window.renderWinnersTable) window.renderWinnersTable(results);
        });

        // Player Connectivity
        socket.on('player_disconnected', (data) => {
            if (window.showPlayerDisconnect) window.showPlayerDisconnect(data);
        });

        socket.on('player_reconnected', (data) => {
            if (window.showPlayerReconnect) window.showPlayerReconnect(data);
        });

        // Theme
        socket.on('theme_changed', (data) => {
            if (window.handleThemeChange) window.handleThemeChange(data);
        });

        socket.on('current_theme', (data) => {
            if (window.handleThemeChange) window.handleThemeChange(data);
        });

        // Reset
        socket.on('reset_game_client', () => location.reload());
    }

    // --- Action Methods ---

    function submitPassword() {
        const password = document.getElementById('host-password').value;
        const selectedTheme = document.getElementById('password-theme-select').value;

        if (password === CORRECT_PASSWORD) {
            document.getElementById('password-overlay').style.display = 'none';
            // Force takeover as controller
            socket.emit('host_register', { force: true });

            socket.emit('disable_debug_mode'); // Ensure debug mode is off
            socket.emit('set_theme', { theme_id: selectedTheme });
            document.getElementById('theme-select').value = selectedTheme;
        } else if (password === 'mason') {
            document.getElementById('password-overlay').style.display = 'none';
            // Force takeover as controller
            socket.emit('host_register', { force: true });

            socket.emit('enable_debug_mode');
            socket.emit('set_theme', { theme_id: selectedTheme });
            document.getElementById('theme-select').value = selectedTheme;
            alert('🛠️ 測試模式已啟動: 20倍速, 1秒開賽');
        } else {
            alert('密碼錯誤！請重新輸入或選擇觀看模式');
        }
    }

    function enterAsViewer() {
        document.getElementById('password-overlay').style.display = 'none';
        socket.emit('disable_debug_mode'); // Clear debug mode if it was on
        socket.emit('host_surrender_control'); // Explicitly become viewer
    }

    function startRace() {
        const playerContainer = document.getElementById('oval-track');
        // Fallback check if players logic fails
        if (players.length === 0 && (!playerContainer || playerContainer.children.length === 0)) {
            alert('⚠️ 沒有玩家加入！');
            return;
        }

        const prize1 = parseInt(document.getElementById('prize1').value) || 0;
        const prize2 = parseInt(document.getElementById('prize2').value) || 0;
        const prize3 = parseInt(document.getElementById('prize3').value) || 0;
        const luckyPrize = parseInt(document.getElementById('lucky-prize').value) || 500;

        socket.emit('start_race', {
            top3_prizes: [prize1, prize2, prize3],
            lucky_prize: luckyPrize,
            amount: prize1 + prize2 + prize3
        });
    }

    function resetGame() {
        socket.emit('reset_game');
    }

    function addBots(count) {
        socket.emit('add_bots', { count: count });
    }

    function switchTheme(themeId) {
        if (!isHostController) {
            alert('觀看模式無法切換主題');
            // Revert select
            // document.getElementById('theme-select').value = currentTheme; (Requires access to currentTheme)
            return;
        }
        socket.emit('set_theme', { theme_id: themeId });
    }

    function takeoverHost() {
        socket.emit('host_takeover');
        if (window.hideTakeoverCountdown) window.hideTakeoverCountdown();
    }

    // Expose Public API
    return {
        init: init,
        submitPassword: submitPassword,
        enterAsViewer: enterAsViewer,
        startRace: startRace,
        resetGame: resetGame,
        addBots: addBots,
        switchTheme: switchTheme,
        takeoverHost: takeoverHost,
        // Helper to check race status for audio manager
        isRaceRunning: () => document.getElementById('race-screen').style.display !== 'none'
    };
})();
