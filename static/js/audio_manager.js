// Audio Manager Module for Host Screen
// Handles background music, sound effects, and audio context

window.AudioManager = (function () {
    console.log('Audio Manager initialized');

    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

    // Audio elements for music
    // Audio elements for music
    // Use encodeURIComponent for filenames with special chars/spaces, but keep path structure
    const waitingMusic = new Audio('/static/audio/' + encodeURIComponent('等待入場的音樂.mp3'));
    waitingMusic.loop = true;
    waitingMusic.volume = 0.5;

    const racingMusic = new Audio('/static/audio/' + encodeURIComponent('競賽的音樂Galloping Gags at 160.mp3'));
    racingMusic.loop = true;
    racingMusic.volume = 0.6;

    // Sound effects
    const correctSound = new Audio('/static/audio/correct.mp3');
    correctSound.volume = 0.6;

    const wrongSound = new Audio('/static/audio/wrong.mp3');
    wrongSound.volume = 0.6;

    const fireworksSound = new Audio('/static/audio/new-years-eve-in-peru-fireworks-fire-crackers-and-rockets-to-celebrate-the-new-year-pisco-peru-2012-17692.mp3');
    fireworksSound.volume = 0.7;

    function playTone(freq, type, duration, volume = 0.3) {
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.frequency.value = freq;
        osc.type = type;
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        gain.gain.setValueAtTime(volume, audioCtx.currentTime);
        osc.start();
        gain.gain.exponentialRampToValueAtTime(0.00001, audioCtx.currentTime + duration);
        osc.stop(audioCtx.currentTime + duration);
        return osc;
    }

    function stopAllMusic() {
        waitingMusic.pause();
        racingMusic.pause();
    }

    return {
        // Expose necessary methods
        init: function () {
            // Document click listener is usually handled in the main script or here
            // We can expose a method to attempt processing user gesture
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
        },

        startWaitingMusic: function () {
            console.log('AM: Starting waiting music...');
            stopAllMusic();
            waitingMusic.currentTime = 0;
            waitingMusic.play()
                .then(() => console.log('AM: Waiting music playing'))
                .catch(e => console.error('AM: Waiting music blocked:', e));
        },

        startRacingMusic: function () {
            console.log('AM: Starting racing music...');
            stopAllMusic();
            racingMusic.currentTime = 0;
            racingMusic.play()
                .then(() => console.log('AM: Racing music playing'))
                .catch(e => console.error('AM: Racing music blocked:', e));
        },

        stopAllMusic: stopAllMusic,

        playStartSound: function () {
            // Countdown beeps: 3-2-1-GO! (synthesized tones)
            setTimeout(() => playTone(440, 'square', 0.1, 0.3), 0);
            setTimeout(() => playTone(440, 'square', 0.1, 0.3), 1000);
            setTimeout(() => playTone(440, 'square', 0.1, 0.3), 2000);
            setTimeout(() => playTone(880, 'sawtooth', 0.5, 0.4), 3000);
        },

        playCheerSound: function () {
            if (audioCtx.state === 'suspended') audioCtx.resume();

            const duration = 0.8;
            const sampleRate = audioCtx.sampleRate;
            const buffer = audioCtx.createBuffer(1, sampleRate * duration, sampleRate);
            const data = buffer.getChannelData(0);
            for (let i = 0; i < data.length; i++) {
                data[i] = (Math.random() * 2 - 1) * 0.6;
            }

            const source = audioCtx.createBufferSource();
            source.buffer = buffer;

            const filter = audioCtx.createBiquadFilter();
            filter.type = 'bandpass';
            filter.frequency.value = 900;
            filter.Q.value = 0.6;

            const gain = audioCtx.createGain();
            gain.gain.setValueAtTime(0.0001, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.5, audioCtx.currentTime + 0.08);
            gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);

            source.connect(filter);
            filter.connect(gain);
            gain.connect(audioCtx.destination);
            source.start();
            source.stop(audioCtx.currentTime + duration);
        },

        playWinSound: function () {
            stopAllMusic();
            fireworksSound.currentTime = 0;
            fireworksSound.play().catch(e => { });
        },

        playCorrectSound: function () {
            correctSound.currentTime = 0;
            correctSound.play().catch(e => { });
        },

        playWrongSound: function () {
            wrongSound.currentTime = 0;
            wrongSound.play().catch(e => { });
        },

        playShortWinSound: function () {
            const freqs = [523.25, 659.25, 783.99, 1046.50];
            freqs.forEach((freq, i) => {
                setTimeout(() => playTone(freq, 'sine', 0.1, 0.4), i * 80);
            });
        },

        playVictoryInterlude: function () {
            stopAllMusic();
            fireworksSound.currentTime = 0;
            fireworksSound.play().catch(e => { });

            // Resume racing music after 5 seconds if still racing check is passed in or handled nicely
            // For now, we return a promise or setup a timeout callback? 
            // The original code checked DOM which is bad for a logic module.
            // We'll expose a resume function or let the caller handle logic.
            // BETTER: Expose method to resume racing music, caller decides when.

            // To be safe and identical to old behavior, we will use a callback
            setTimeout(() => {
                // The caller should check if race is still on.
                // But here we can't see the DOM.
                // We will trigger a custom event or callback if provided.
                if (window.isRaceStillRunning && window.isRaceStillRunning()) {
                    fireworksSound.pause();
                    racingMusic.play().catch(e => console.log('Resume failed'));
                }
            }, 5000);
        },

        playItemSound: function (type) {
            if (type === 'boost') {
                playTone(523.25, 'sine', 0.1, 0.2);
                setTimeout(() => playTone(659.25, 'sine', 0.1, 0.2), 100);
            } else {
                playTone(392, 'sawtooth', 0.15, 0.2);
                setTimeout(() => playTone(329.63, 'sawtooth', 0.15, 0.2), 120);
            }
        },

        playTone: playTone // Expose generic tone player if needed
    };
})();
