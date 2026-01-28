// Slot Machine Logic Module
// Handles the "Lucky Slot Machine" mini-game on the client side

window.initSlotMachine = function (socket) {
    console.log('Slot Machine module initialized');

    // Listener for slot machine trigger
    socket.on('slot_machine_trigger', (data) => {
        console.log('Slot machine triggered!', data);
        showSlotMachine(socket, data);
    });

    // Listener for slot spin result (Server Authoritative)
    socket.on('slot_spin_result', (data) => {
        console.log('Received slot spin result:', data);

        // If we are currently spinning (we should be if we requested it),
        // we need to pass this data to the spin animation logic.
        // We can store it in a global or trigger the resolve if it was a promise.
        // But since spinReels is running, let's look at how to inject it.

        // Easier way: call a function that `spinReels` is polling or just set a global
        window.currentSlotResult = data;

        // If this is just a re-broadcast/late join, we might need to show message directly?
        // But for the active player, `spinReels` loop deals with it.

        // Handle message display "immediately" (or better, after animation?)
        // Let's let animate completion handle the text update to build suspense.

        // Result screen logic - Wait for animation to finish!
        // The animation function `spinReels` will check `window.currentSlotResult`.
    });

    // Old listener for final result (Keep slightly for compat or remove? Remove, replaced by above)
    // socket.on('slot_result_final', ... ); REMOVED


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
const slotSpinSound = new Audio('/static/audio/slot_spin.mp3'); // We need these files or use tones
const slotWinSound = new Audio('/static/audio/slot_win.mp3');

function spinReels(socket, data) {
    // 1. Reset State
    window.currentSlotResult = null;
    const msgEl = document.getElementById('slot-message');
    if (msgEl) msgEl.innerHTML = "🎰 轉動中... 祝你好運!";

    // Play spin sound logic
    slotSpinSound.pause();
    slotSpinSound.currentTime = 0;
    slotWinSound.pause();
    slotWinSound.currentTime = 0;

    slotSpinSound.loop = true;
    slotSpinSound.play().catch(e => console.log('Slot spin audio failed:', e));
    if (navigator.vibrate) navigator.vibrate(100);

    // 2. Request Result from Server (Request-Response)
    console.log("[SLOT] Requesting Spin from Server...");
    socket.emit('request_slot_spin');

    // 3. Start "Infinite" Animation Loop until result arrives
    const reels = [1, 2, 3];
    const reelElements = reels.map(r => document.getElementById('reel' + r));
    let spinning = true;
    let frameId = null;
    let pos = [0, 0, 0];
    const speeds = [15, 20, 25]; // Different speeds

    const animateLoop = () => {
        if (!spinning) return;

        for (let i = 0; i < 3; i++) {
            pos[i] += speeds[i];
            reelElements[i].style.transform = `translateY(-${pos[i] % 800}px)`;
        }
        frameId = requestAnimationFrame(animateLoop);
    };
    frameId = requestAnimationFrame(animateLoop);

    // 4. Poll for Result (or wait for event)
    const checkResultInterval = setInterval(() => {
        if (window.currentSlotResult) {
            clearInterval(checkResultInterval);
            cancelAnimationFrame(frameId);
            spinning = false;

            finishAnimation(window.currentSlotResult);
        }
    }, 100);

    // Safety timeout (if server dies)
    setTimeout(() => {
        if (spinning) {
            clearInterval(checkResultInterval);
            cancelAnimationFrame(frameId);
            spinning = false;
            alert("Connection error. Please check your prizes locally.");
            location.reload();
        }
    }, 10000);

    function finishAnimation(resultData) {
        console.log("[SLOT] Result received, stopping reels:", resultData);
        const won = resultData.won;

        // Generate visual targets based on SERVER result
        const results = [];
        if (won) {
            const match = 7; // Lucky 7
            results.push(match, match, match);
        } else {
            // Random non-matching
            let r1 = Math.floor(Math.random() * 10) + 1;
            let r2 = Math.floor(Math.random() * 10) + 1;
            let r3 = Math.floor(Math.random() * 10) + 1;
            // Ensure not matching
            if (r1 === r2 && r2 === r3) r3 = (r3 % 10) + 1;
            results.push(r1, r2, r3);
        }

        // Final Snap Animation
        const durations = [1000, 1500, 2000];

        for (let r = 0; r < 3; r++) {
            animateReelStop(r + 1, results[r], durations[r]);
        }

        // Show Final Message & Sound
        setTimeout(() => {
            slotSpinSound.pause();

            if (msgEl) {
                if (won) {
                    msgEl.innerHTML = `<div style="color:#00FF00;font-size:28px;">🎉 恭喜中獎！</div><div style="font-size:36px;color:gold;margin-top:10px;">💰 $${resultData.prize}</div>`;
                    slotWinSound.play().catch(e => { });
                    if (navigator.vibrate) navigator.vibrate([200, 100, 200, 100, 400]);
                } else {
                    let failText = "💰 獎金";
                    if (resultData.result_type == 'slots_full') failText = "😅 名額已滿";
                    msgEl.innerHTML = `<div style="color:#FFA500;font-size:24px;">${failText}</div><div style="font-size:32px;color:white;margin-top:10px;">$${resultData.prize}</div>`;
                    if (navigator.vibrate) navigator.vibrate([100]);
                }
            }

            // Go to Result Screen
            setTimeout(() => {
                const overlay = document.getElementById('slot-overlay');
                if (overlay) overlay.remove();
                const resultScreen = document.getElementById('result-screen');
                const raceScreen = document.getElementById('race-screen');
                if (resultScreen && raceScreen) {
                    raceScreen.style.display = 'none';
                    resultScreen.style.display = 'block';
                }
            }, 4000);

        }, 2500); // Wait for last reel
    }
}

function animateReelStop(reelNum, finalValue, duration) {
    const reel = document.getElementById('reel' + reelNum);
    // Use CSS transition for smooth stop
    // We were 'modding' the position, so we need to find the NEXT occurrence of finalValue
    // Current transform is roughly known. Let's just snap for simplicity or do a clean spin-to-stop.

    // Simpler: Just spin a specific distance from 0
    // Reset transform to allow clean transition? No, might jump.
    // Let's just do a simple transition from "current visual" (hard to track) 
    // OR just spin X more times and land.

    const finalPos = (finalValue - 1) * 80;
    // Add extra spins
    const totalDist = (800 * 2) + finalPos; // Spin 2 full times then land

    // We need to re-apply the animation approach but targeted.
    // Since we interrupted the infinite loop, we can just start a new transition
    reel.style.transition = 'none';
    reel.style.transform = 'translateY(0px)'; // Reset to start (might jump, but fast)

    // Force reflow
    void reel.offsetWidth;

    reel.style.transition = `transform ${duration / 1000}s cubic-bezier(0.25, 0.1, 0.25, 1)`;
    reel.style.transform = `translateY(-${totalDist}px)`;

    // Wait for transition end to reset to 'canonical' position (0..800) so image stays
    setTimeout(() => {
        reel.style.transition = 'none';
        reel.style.transform = `translateY(-${finalPos}px)`;
    }, duration);
}
