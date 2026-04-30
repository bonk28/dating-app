// ============ LECTURE AUDIO PERSISTANTE ============
(function() {
    // Utiliser un audio global stocké dans window
    if (!window._globalPlayer) {
        window._globalPlayer = {
            audio: new Audio(),
            playlist: [],
            currentIndex: -1,
            isPlaying: false
        };
        
        const gp = window._globalPlayer;
        
        // Restaurer depuis localStorage
        const saved = JSON.parse(localStorage.getItem('_playerState') || '{}');
        if (saved.playlist) gp.playlist = saved.playlist;
        if (saved.currentIndex >= 0) gp.currentIndex = saved.currentIndex;
        
        gp.audio.volume = 0.8;
        
        // Sauvegarder l'état régulièrement
        setInterval(() => {
            localStorage.setItem('_playerState', JSON.stringify({
                playlist: gp.playlist,
                currentIndex: gp.currentIndex,
                isPlaying: !gp.audio.paused,
                currentTime: gp.audio.currentTime
            }));
        }, 3000);
        
        // Créer le mini-player flottant
        function createMiniPlayer() {
            if (document.getElementById('_miniPlayer')) return;
            const div = document.createElement('div');
            div.id = '_miniPlayer';
            div.style.cssText = 'position:fixed;bottom:0;left:0;right:0;background:#1a1a2e;padding:8px 12px;display:none;align-items:center;gap:10px;border-top:2px solid #1DB954;z-index:9999;box-shadow:0 -5px 20px rgba(0,0,0,0.5);';
            div.innerHTML = `
                <span style="font-size:1.5em;" id="_mpIcon">🎵</span>
                <div style="flex:1;overflow:hidden;">
                    <div style="font-weight:600;font-size:0.8em;color:white;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" id="_mpTitle">---</div>
                    <div style="font-size:0.7em;color:#888;" id="_mpArtist">---</div>
                </div>
                <button id="_mpPrev" style="background:none;border:none;color:white;font-size:1em;cursor:pointer;">⏮</button>
                <button id="_mpPlay" style="background:none;border:none;color:white;font-size:1.3em;cursor:pointer;">▶️</button>
                <button id="_mpNext" style="background:none;border:none;color:white;font-size:1em;cursor:pointer;">⏭</button>
                <button id="_mpClose" style="background:none;border:none;color:#f44336;font-size:1em;cursor:pointer;">✕</button>
            `;
            document.body.appendChild(div);
            
            document.getElementById('_mpPlay').onclick = () => {
                if (gp.audio.paused) { gp.audio.play(); document.getElementById('_mpPlay').textContent = '⏸️'; }
                else { gp.audio.pause(); document.getElementById('_mpPlay').textContent = '▶️'; }
            };
            document.getElementById('_mpPrev').onclick = () => {
                if (gp.playlist.length > 0) {
                    gp.currentIndex = (gp.currentIndex - 1 + gp.playlist.length) % gp.playlist.length;
                    playCurrent();
                }
            };
            document.getElementById('_mpNext').onclick = () => {
                if (gp.playlist.length > 0) {
                    gp.currentIndex = (gp.currentIndex + 1) % gp.playlist.length;
                    playCurrent();
                }
            };
            document.getElementById('_mpClose').onclick = () => {
                gp.audio.pause();
                gp.audio.src = '';
                div.style.display = 'none';
                localStorage.removeItem('_playerState');
            };
        }
        
        function playCurrent() {
            if (gp.currentIndex < 0 || gp.currentIndex >= gp.playlist.length) return;
            const t = gp.playlist[gp.currentIndex];
            gp.audio.src = t.dataUrl;
            gp.audio.play();
            document.getElementById('_mpTitle').textContent = t.title;
            document.getElementById('_mpArtist').textContent = t.artist;
            document.getElementById('_mpPlay').textContent = '⏸️';
            document.getElementById('_miniPlayer').style.display = 'flex';
        }
        
        gp.audio.addEventListener('play', () => {
            if (gp.currentIndex >= 0) {
                document.getElementById('_miniPlayer').style.display = 'flex';
            }
        });
        
        gp.audio.addEventListener('ended', () => {
            if (gp.playlist.length > 0) {
                gp.currentIndex = (gp.currentIndex + 1) % gp.playlist.length;
                playCurrent();
            }
        });
        
        // Exposer les fonctions globalement
        window.addToGlobalPlaylist = function(track) {
            gp.playlist.push(track);
            if (gp.currentIndex < 0) {
                gp.currentIndex = gp.playlist.length - 1;
                createMiniPlayer();
                setTimeout(playCurrent, 500);
            }
        };
        
        window.playGlobalTrack = function(index) {
            gp.currentIndex = index;
            createMiniPlayer();
            setTimeout(playCurrent, 500);
        };
        
        window.getGlobalPlaylist = function() { return gp.playlist; };
        window.getCurrentTrackIndex = function() { return gp.currentIndex; };
        window.isGlobalPlaying = function() { return !gp.audio.paused; };
        
        createMiniPlayer();
    }
})();
