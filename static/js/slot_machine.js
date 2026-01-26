// Slot Machine Logic Module
// Handles the "Lucky Slot Machine" mini-game on the client side

window.initSlotMachine = function (socket) {
    console.log('Slot Machine module initialized');

    // Listener for slot machine trigger
    socket.on('slot_machine_trigger', (data) => {
        console.log('Slot machine triggered!', data);
        showSlotMachine(socket, data);
    });

    // Listener for final result
    socket.on('slot_result_final', (data) => {
        const msgEl = document.getElementById('slot-message');
        if (msgEl) {
            if (data.won) {
                msgEl.innerHTML = `<div style="color:#00FF00;font-size:28px;">🎉 恭喜中獎！</div><div style="font-size:36px;color:gold;margin-top:10px;">💰 $${data.prize}</div>`;
                if (navigator.vibrate) navigator.vibrate([200, 100, 200, 100, 400]);

                // Update the result screen prize text as well (so it shows correct amount when screens switch)
                const resultPrizeEl = document.getElementById('my-prize');
                if (resultPrizeEl) {
                    resultPrizeEl.innerText = "獎金: $" + data.prize;
                    // Highlight it
                    resultPrizeEl.style.color = "#00FF00";
                    resultPrizeEl.style.textShadow = "0 0 10px #0f0";
                }
            } else {
                msgEl.innerHTML = `<div style="color:#FFA500;font-size:24px;">💰 獎金</div><div style="font-size:32px;color:white;margin-top:10px;">$${data.prize}</div>`;
                if (navigator.vibrate) navigator.vibrate([100]);
            }
        }

        // Result screen logic - ONLY for the player involved
        // Use loose equality (==) to handle string/number ID mismatches
        if (typeof myId !== 'undefined' && data.player_id == myId) {
            setTimeout(() => {
                const overlay = document.getElementById('slot-overlay');
                if (overlay) overlay.remove();

                // Show result screen ONLY if game is actually defined as over (race screen hidden)
                // Or if we want to force it. BUT, if game is still running (others racing), 
                // we should stick to race screen (which might show 'Finished' status)
                // However, client.html hides race-screen on game_results.
                // So if race-screen is already hidden, we ensure result-screen is shown.
                // If race-screen is VISIBLE, it means game is not over. We just remove overlay.
                const raceScreen = document.getElementById('race-screen');
                const resultScreen = document.getElementById('result-screen');

                if (raceScreen && raceScreen.style.display === 'none') {
                    if (resultScreen) resultScreen.style.display = 'block';
                }
            }, 5000);
        } else {
            // For others, just ensure overlay is removed if it somehow got stuck (unlikely)
            // But do NOT switch to result screen
        }
    });

    // Listener for prizes exhausted (too slow!)
    socket.on('slot_prizes_exhausted', (data) => {
        console.log('Slot prizes exhausted!', data);

        // IMPORTANT: Only show overlay if this player is the one who missed
        // Check if we have myId defined (from client.html global scope)
        if (typeof myId !== 'undefined' && data.player_id !== myId) {
            console.log('Slot exhausted event not for this player, ignoring');
            return;
        }

        // Also check if we had a slot overlay open (meaning we were eligible for slots)
        // If we never had one, we weren't in the slot phase
        const existingOverlay = document.getElementById('slot-overlay');
        if (!existingOverlay && typeof myId !== 'undefined' && data.player_id !== myId) {
            // Not our event and we don't have overlay, ignore
            return;
        }

        // Remove existing overlay if any
        if (existingOverlay) {
            existingOverlay.remove();
        }

        // Create new notification overlay
        const overlay = document.createElement('div');
        overlay.id = 'slot-overlay';
        overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.95);z-index:99999;display:flex;flex-direction:column;align-items:center;justify-content:center;';

        overlay.innerHTML = `
            <div style="text-align:center;color:gold;font-size:24px;margin-bottom:20px;">🎰 吃角子老虎 🎰</div>
            <div style="color:#FF6B6B;font-size:28px;margin-bottom:15px;">😅 慢了一步！</div>
            <div style="font-size:18px;color:#aaa;margin-bottom:20px;">所有幸運名額已被搶光</div>
            <div style="font-size:40px;color:white;margin-bottom:20px;">💰 $${data.prize}</div>
            <div style="font-size:14px;color:#666;">參加獎</div>
        `;
        document.body.appendChild(overlay);

        if (navigator.vibrate) navigator.vibrate([50, 50, 50]);

        // Auto-close after 4 seconds and show result screen
        setTimeout(() => {
            const el = document.getElementById('slot-overlay');
            if (el) el.remove();

            // Show result screen after slot closes
            const resultScreen = document.getElementById('result-screen');
            const raceScreen = document.getElementById('race-screen');
            if (resultScreen && raceScreen) {
                raceScreen.style.display = 'none';
                resultScreen.style.display = 'block';
            }
        }, 4000);
    });
};

function showSlotMachine(socket, data) {
    const overlay = document.createElement('div');
    overlay.id = 'slot-overlay';
    overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.95);z-index:99999;display:flex;flex-direction:column;align-items:center;justify-content:center;';

    const folder = data.avatar_folder || '';
    const prefix = data.avatar_prefix || 'horse';
    const basePath = folder ? `/static/images/${folder}/` : '/static/images/';

    overlay.innerHTML = `
        <div style="text-align:center;color:gold;font-size:24px;margin-bottom:20px;">🎰 幸運吃角子老虎 🎰</div>
        <div style="text-align:center;color:#aaa;font-size:14px;margin-bottom:20px;">
            第 ${data.rank} 名 <br>
            <span style="color:#00FF00">剩餘 ${data.lucky_slots_remaining} 個幸運名額</span>
        </div>
        <div id="slot-reels" style="display:flex;gap:10px;background:#222;padding:20px;border-radius:15px;border:3px solid gold;">
            <div style="width:80px;height:80px;overflow:hidden;border:2px solid #444;border-radius:10px;background:#111;"><div id="reel1"></div></div>
            <div style="width:80px;height:80px;overflow:hidden;border:2px solid #444;border-radius:10px;background:#111;"><div id="reel2"></div></div>
            <div style="width:80px;height:80px;overflow:hidden;border:2px solid #444;border-radius:10px;background:#111;"><div id="reel3"></div></div>
        </div>
        <div id="slot-message" style="margin-top:30px;font-size:20px;color:white;text-align:center;"></div>
        <button id="spin-btn" style="margin-top:20px;padding:15px 40px;font-size:20px;background:linear-gradient(145deg,#FFD700,#FFA500);color:#000;border:none;border-radius:10px;cursor:pointer;font-weight:bold;">🍀 試試你的運氣吧！</button>
    `;
    document.body.appendChild(overlay);

    // Build reel images
    for (let r = 1; r <= 3; r++) {
        const reel = document.getElementById('reel' + r);
        let html = '';
        // Duplicate images for infinite scrolling loop effect
        for (let i = 1; i <= 10; i++) {
            html += `<img src="${basePath}${prefix}${i}.png" style="width:80px;height:80px;object-fit:contain;">`;
        }
        for (let i = 1; i <= 10; i++) {
            html += `<img src="${basePath}${prefix}${i}.png" style="width:80px;height:80px;object-fit:contain;">`;
        }
        reel.innerHTML = html;
    }

    document.getElementById('spin-btn').onclick = () => {
        document.getElementById('spin-btn').disabled = true;
        document.getElementById('spin-btn').style.opacity = '0.5';
        spinReels(socket, data);
    };
}

// Slot Machine Audio
// Slot Machine Audio using Web Audio API (No external files needed)
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playSlotSound(type) {
    if (audioCtx.state === 'suspended') audioCtx.resume();

    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();

    osc.connect(gain);
    gain.connect(audioCtx.destination);

    if (type === 'spin') {
        // Mechanical reeling sound (low frequency ticks)
        osc.type = 'square';
        osc.frequency.setValueAtTime(100, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(60, audioCtx.currentTime + 0.1);
        gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.1);
    } else if (type === 'win') {
        // Victory fanfare
        const now = audioCtx.currentTime;
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(523.25, now); // C5
        osc.frequency.setValueAtTime(659.25, now + 0.1); // E5
        osc.frequency.setValueAtTime(783.99, now + 0.2); // G5
        osc.frequency.setValueAtTime(1046.50, now + 0.4); // C6

        gain.gain.setValueAtTime(0.2, now);
        gain.gain.linearRampToValueAtTime(0, now + 0.8);

        osc.start(now);
        osc.stop(now + 0.8);
    }
}

let spinInterval = null;

function spinReels(socket, data) {
    const canWin = data.lucky_slots_remaining > 0;

    // Start spin sound loop
    if (spinInterval) clearInterval(spinInterval);
    spinInterval = setInterval(() => playSlotSound('spin'), 100);

    if (navigator.vibrate) navigator.vibrate(100);

    if (navigator.vibrate) navigator.vibrate(100);

    // --- RESULT LOGIC ---
    // Use server provided probability
    const winProb = (data.win_probability !== undefined) ? data.win_probability : (canWin ? 0.5 : 0);
    console.log(`[SLOT] Win Probability: ${winProb} (Can Win: ${canWin})`);

    let won = false;
    if (canWin && Math.random() < winProb) {
        won = true;
    }

    // Generate visual targets
    const results = [];
    if (won) {
        const match = 7; // Lucky 7
        results.push(match, match, match);
    } else {
        // Random non-matching
        let r1 = Math.floor(Math.random() * 10) + 1;
        let r2 = Math.floor(Math.random() * 10) + 1;
        let r3 = Math.floor(Math.random() * 10) + 1;

        // Ensure not matching by accident (simple check)
        if (r1 === r2 && r2 === r3) {
            r3 = (r3 % 10) + 1;
        }
        results.push(r1, r2, r3);
    }

    // Animate Reels
    const durations = [2000, 2500, 3000];
    for (let r = 0; r < 3; r++) {
        // Ensure animateReel is available (defined below)
        if (typeof animateReel === 'function') {
            animateReel(r + 1, results[r], durations[r]);
        }
    }

    // Stop after longest duration + suspense delay
    setTimeout(() => {
        // Stop spin sound
        if (spinInterval) {
            clearInterval(spinInterval);
            spinInterval = null;
        }

        // Play result sound if won
        if (won) {
            playSlotSound('win');
            if (navigator.vibrate) navigator.vibrate([200, 100, 200, 100, 400]);
        } else {
            if (navigator.vibrate) navigator.vibrate([100]);
        }

        // Send result to server
        socket.emit('slot_result', { won: won });

    }, 3800); // 3800ms matches visual end (3000ms) + 800ms suspense
}

function animateReel(reelNum, finalValue, duration) {
    const reel = document.getElementById('reel' + reelNum);
    let pos = 0;
    const speed = 15;
    const startTime = Date.now();

    const animate = () => {
        const elapsed = Date.now() - startTime;
        if (elapsed < duration - 500) {
            pos += speed;
            reel.style.transform = `translateY(-${pos % 800}px)`; // 800 is height of 10 items * 80px
            requestAnimationFrame(animate);
        } else {
            const finalPos = (finalValue - 1) * 80;
            reel.style.transition = 'transform 0.5s ease-out';
            reel.style.transform = `translateY(-${finalPos}px)`;
        }
    };
    animate();
}
