(function(){
    var badge = document.createElement('div');
    badge.id = 'uniBadge';
    badge.style.cssText = 'position:fixed;bottom:90px;right:15px;width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#ff2d78,#ff6b9d);color:white;cursor:grab;z-index:9998;box-shadow:0 5px 25px rgba(255,45,120,.5);display:flex;align-items:center;justify-content:center;font-size:1.2em;touch-action:none;user-select:none;font-weight:bold;';
    badge.innerHTML = '🔔';
    document.body.appendChild(badge);
    
    var notifCount = document.createElement('span');
    notifCount.style.cssText = 'position:absolute;top:-6px;right:-6px;background:#ff1744;color:white;border-radius:50%;width:22px;height:22px;font-size:.55em;display:none;align-items:center;justify-content:center;font-weight:bold;';
    notifCount.textContent = '0';
    badge.appendChild(notifCount);
    
    var panel = document.createElement('div');
    panel.id = 'uniPanel';
    panel.style.cssText = 'display:none;position:fixed;bottom:150px;right:15px;width:300px;background:#1a1a2e;border-radius:20px;z-index:9997;box-shadow:0 10px 40px rgba(0,0,0,.8);overflow:hidden;';
    panel.innerHTML = '<div style="display:flex;gap:5px;padding:10px;"><button onclick="showNotifsTab()" style="flex:1;padding:12px;background:#ff2d78;color:white;border:none;border-radius:12px;cursor:pointer;font-weight:bold;">🔔 Notifs</button><button onclick="showMusicTab()" style="flex:1;padding:12px;background:#1DB954;color:white;border:none;border-radius:12px;cursor:pointer;font-weight:bold;">🎵 Musique</button></div><div id="uniContent" style="padding:10px;max-height:350px;overflow-y:auto;color:white;"></div>';
    document.body.appendChild(panel);
    
    // DRAG
    var isDragging = false, startX, startY, startLeft, startTop;
    badge.onmousedown = badge.ontouchstart = function(e) {
        isDragging = false;
        var t = e.touches ? e.touches[0] : e;
        startX = t.clientX; startY = t.clientY;
        var rect = badge.getBoundingClientRect();
        startLeft = rect.left; startTop = rect.top;
        document.onmousemove = document.ontouchmove = function(e) {
            var t = e.touches ? e.touches[0] : e;
            if (Math.abs(t.clientX-startX) > 3 || Math.abs(t.clientY-startY) > 3) isDragging = true;
            if (!isDragging) return;
            badge.style.left = Math.max(0, Math.min(window.innerWidth-52, startLeft+t.clientX-startX)) + 'px';
            badge.style.top = Math.max(60, Math.min(window.innerHeight-52, startTop+t.clientY-startY)) + 'px';
            badge.style.right = 'auto'; badge.style.bottom = 'auto';
        };
        document.onmouseup = document.ontouchend = function() {
            document.onmousemove = document.ontouchmove = null;
        };
    };
    
    badge.onclick = function() {
        if (!isDragging) {
            panel.style.display = panel.style.display === 'block' ? 'none' : 'block';
            if (panel.style.display === 'block') showNotifsTab();
        }
    };
    
    // NOTIFICATIONS
    var notifs = JSON.parse(localStorage.getItem('notifs') || '[]');
    updateBadge();
    
    window.addNotif = function(icon, title, body) {
        notifs.unshift({icon:icon, title:title, body:body, time:new Date().toLocaleTimeString()});
        localStorage.setItem('notifs', JSON.stringify(notifs));
        updateBadge();
        try { new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CA').play(); } catch(e) {}
        if (navigator.vibrate) navigator.vibrate([200,100,200]);
    };
    
    function updateBadge() {
        notifCount.textContent = notifs.length;
        notifCount.style.display = notifs.length > 0 ? 'flex' : 'none';
    }
    
    window.showNotifsTab = function() {
        var c = document.getElementById('uniContent');
        c.innerHTML = '<h4 style="margin-bottom:10px;">🔔 Notifications</h4>' + 
            (notifs.length === 0 ? '<p style="color:#888;text-align:center;padding:20px;">Aucune notification</p>' :
            notifs.map(function(n) { return '<div style="padding:10px;background:rgba(255,255,255,.03);border-radius:8px;margin:5px 0;font-size:.85em;">'+n.icon+' <b>'+n.title+'</b><br>'+n.body+'<br><small style="opacity:.4;">'+n.time+'</small></div>'; }).join('')) +
            '<button onclick="notifs=[];localStorage.setItem(\'notifs\',\'[]\');updateBadge();showNotifsTab();" style="width:100%;padding:8px;background:#ff1744;color:white;border:none;border-radius:8px;margin-top:10px;cursor:pointer;">🗑️ Tout effacer</button>';
    };
    
    // MUSIQUE
    var playlist = JSON.parse(localStorage.getItem('globalPlaylist') || '[]');
    var currentTrack = parseInt(localStorage.getItem('globalTrackIndex') || '-1');
    var audio = document.getElementById('globalAudio') || new Audio();
    if (!document.getElementById('globalAudio')) { audio.id = 'globalAudio'; document.body.appendChild(audio); }
    audio.volume = 0.8;
    
    if (currentTrack >= 0 && playlist[currentTrack]) {
        audio.src = playlist[currentTrack].dataUrl;
        audio.currentTime = parseFloat(localStorage.getItem('globalTrackTime') || '0');
    }
    
    audio.ontimeupdate = function() { localStorage.setItem('globalTrackTime', audio.currentTime); };
    audio.onended = function() { if (playlist.length > 0) { currentTrack = (currentTrack + 1) % playlist.length; playTrack(currentTrack); } };
    
    function saveState() {
        localStorage.setItem('globalPlaylist', JSON.stringify(playlist));
        localStorage.setItem('globalTrackIndex', currentTrack);
        localStorage.setItem('globalTrackTime', audio.currentTime);
    }
    
    function playTrack(index) {
        if (index < 0 || index >= playlist.length) return;
        currentTrack = index;
        audio.src = playlist[index].dataUrl;
        audio.play().catch(function(){});
        saveState();
    }
    
    window.showMusicTab = function() {
        var c = document.getElementById('uniContent');
        c.innerHTML = '<h4 style="margin-bottom:10px;">🎵 Musique</h4>' +
            '<input id="ms" placeholder="🔍 Rechercher..." style="width:100%;padding:12px;border-radius:25px;border:none;background:#333;color:white;margin-bottom:10px;" onkeypress="if(event.key==\'Enter\')searchM()">' +
            '<button onclick="searchM()" style="width:100%;padding:10px;background:#1DB954;color:white;border:none;border-radius:25px;cursor:pointer;font-weight:bold;">🔍 Rechercher</button>' +
            '<div id="mr" style="margin-top:10px;max-height:200px;overflow-y:auto;"></div>' +
            (playlist.length > 0 ? '<hr style="border-color:rgba(255,255,255,.1);margin:10px 0;"><h5>Ma playlist</h5>' + playlist.map(function(t,i){ return '<div style="padding:8px;cursor:pointer;border-radius:5px;color:white;font-size:.85em;" onclick="playTrack('+i+')">'+(i===currentTrack?'🔊 ':'🎵 ')+t.title+'</div>'; }).join('') : '');
    };
    
    window.searchM = async function() {
        var q = document.getElementById('ms').value.trim();
        if (!q) return;
        var res = document.getElementById('mr');
        res.innerHTML = '<p style="color:white;text-align:center;">🔍 Recherche...</p>';
        try {
            var r = await fetch('https://itunes.apple.com/search?term='+encodeURIComponent(q)+'&media=music&limit=20');
            var d = await r.json();
            if (d.results && d.results.length > 0) {
                res.innerHTML = d.results.map(function(t){
                    return '<div onclick="addTrack(\''+(t.previewUrl||'')+'\',\''+(t.trackName||'').replace(/'/g,'')+'\',\''+(t.artistName||'').replace(/'/g,'')+'\')" style="display:flex;align-items:center;gap:8px;padding:8px;cursor:pointer;border-radius:5px;color:white;font-size:.85em;"><img src="'+t.artworkUrl100+'" style="width:35px;height:35px;border-radius:5px;" onerror="this.style.display=\'none\'"><div style="flex:1;overflow:hidden;"><div>'+t.trackName+'</div><div style="font-size:.7em;opacity:.6;">'+t.artistName+'</div></div><span style="color:#1DB954;">'+(t.previewUrl?'▶️':'❌')+'</span></div>';
                }).join('');
            } else { res.innerHTML = '<p style="color:#888;text-align:center;padding:20px;">Aucun résultat</p>'; }
        } catch(e) { res.innerHTML = '<p style="color:#f44336;text-align:center;padding:20px;">Erreur</p>'; }
    };
    
    window.addTrack = function(url, title, artist) {
        if (!url) { alert('Aperçu non disponible'); return; }
        playlist.push({title:title, artist:artist, dataUrl:url});
        saveState();
        if (currentTrack < 0) playTrack(playlist.length-1);
        showMusicTab();
    };
    
    window.playTrack = playTrack;
    
    var oldMatches = 0;
    setInterval(function() {
        fetch('/api/stats').then(function(r){return r.json()}).then(function(s){
            if (s.matches > oldMatches && oldMatches > 0) addNotif('💕', 'Nouveau match!', 'Quelqu\'un t\'a liké');
            oldMatches = s.matches;
        }).catch(function(){});
    }, 15000);
})();
