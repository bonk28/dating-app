(function(){
    var badge = document.createElement('div');
    badge.id = 'uniBadge';
    badge.style.cssText = 'position:fixed;bottom:80px;right:15px;width:50px;height:50px;border-radius:50%;background:#e91e63;color:white;cursor:pointer;z-index:9998;box-shadow:0 5px 20px rgba(233,30,99,.4);display:flex;align-items:center;justify-content:center;font-size:1.2em;';
    badge.textContent = '🔔';
    document.body.appendChild(badge);
    
    var panel = document.createElement('div');
    panel.id = 'uniPanel';
    panel.style.cssText = 'display:none;position:fixed;bottom:140px;right:15px;width:300px;background:#1a1a2e;border-radius:15px;z-index:9997;box-shadow:0 10px 40px rgba(0,0,0,.6);overflow:hidden;';
    panel.innerHTML = '<div style="display:flex;gap:5px;padding:8px;"><button onclick="showNotifs()" style="flex:1;padding:12px;background:#e91e63;color:white;border:none;border-radius:8px;cursor:pointer;font-weight:bold;">🔔 Notifications</button><button onclick="showMusic()" style="flex:1;padding:12px;background:#1DB954;color:white;border:none;border-radius:8px;cursor:pointer;font-weight:bold;">🎵 Musique</button></div><div id="uniContent" style="padding:10px;max-height:350px;overflow-y:auto;color:white;"></div>';
    document.body.appendChild(panel);
    
    badge.onclick = function(){
        if (panel.style.display === 'block') { panel.style.display = 'none'; }
        else { panel.style.display = 'block'; showNotifs(); }
    };
    
    var notifs = JSON.parse(localStorage.getItem('notifs') || '[]');
    var oldMatches = 0;
    
    window.addNotif = function(icon, title, body) {
        notifs.unshift({icon:icon, title:title, body:body, time:new Date().toLocaleTimeString()});
        localStorage.setItem('notifs', JSON.stringify(notifs));
        badge.innerHTML = '🔔<sup style="background:white;color:#e91e63;border-radius:10px;padding:1px 5px;font-size:.5em;position:absolute;top:-5px;right:-5px;">'+notifs.length+'</sup>';
        try { new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CA').play(); } catch(e) {}
        if (navigator.vibrate) navigator.vibrate([200,100,200]);
    };
    
    window.showNotifs = function() {
        var c = document.getElementById('uniContent');
        c.innerHTML = '<h4 style="margin-bottom:10px;">🔔 Notifications</h4>' + 
            (notifs.length === 0 ? '<p style="color:#888;text-align:center;padding:20px;">Aucune notification</p>' :
            notifs.map(function(n) {
                return '<div style="padding:10px;background:rgba(255,255,255,.05);border-radius:8px;margin:5px 0;font-size:.85em;">'+n.icon+' <b>'+n.title+'</b><br>'+n.body+'<br><small style="opacity:.5;">'+n.time+'</small></div>';
            }).join('')) +
            '<button onclick="notifs=[];localStorage.setItem(\'notifs\',\'[]\');showNotifs();badge.innerHTML=\'🔔\';" style="width:100%;padding:8px;background:#f44336;color:white;border:none;border-radius:5px;margin-top:10px;cursor:pointer;">🗑️ Tout effacer</button>';
    };
    
    window.showMusic = function() {
        var c = document.getElementById('uniContent');
        c.innerHTML = '<h4 style="margin-bottom:10px;">🎵 Musique</h4>' +
            '<input id="ms" placeholder="🔍 Rechercher..." style="width:100%;padding:12px;border-radius:25px;border:none;background:#333;color:white;margin-bottom:10px;font-size:.9em;" onkeypress="if(event.key==\'Enter\')searchM()">' +
            '<button onclick="searchM()" style="width:100%;padding:10px;background:#1DB954;color:white;border:none;border-radius:25px;cursor:pointer;font-weight:bold;">🔍 Rechercher</button>' +
            '<div id="mr" style="margin-top:10px;max-height:200px;overflow-y:auto;"></div>';
    };
    
    window.searchM = function() {
        var q = document.getElementById('ms').value.trim();
        if (!q) return;
        document.getElementById('mr').innerHTML = '<p style="text-align:center;color:#888;padding:10px;">🔍 Recherche...</p>';
        fetch('https://itunes.apple.com/search?term='+encodeURIComponent(q)+'&media=music&limit=15')
        .then(function(r) { return r.json(); })
        .then(function(d) {
            if (d.results && d.results.length > 0) {
                document.getElementById('mr').innerHTML = d.results.map(function(t) {
                    return '<div onclick="playM(\''+(t.previewUrl||'')+'\',\''+(t.trackName||'').replace(/\'/g,"")+'\',\''+(t.artistName||'').replace(/\'/g,"")+'\')" style="display:flex;align-items:center;gap:8px;padding:8px;cursor:pointer;border-radius:5px;margin:2px 0;font-size:.85em;">' +
                        '<img src="'+t.artworkUrl100+'" style="width:40px;height:40px;border-radius:5px;" onerror="this.style.display=\'none\'">' +
                        '<div style="flex:1;"><div>'+t.trackName+'</div><div style="font-size:.7em;opacity:.7;">'+t.artistName+'</div></div>' +
                        '<span style="color:#1DB954;">'+(t.previewUrl?'▶️':'❌')+'</span></div>';
                }).join('');
            } else {
                document.getElementById('mr').innerHTML = '<p style="text-align:center;color:#888;padding:20px;">Aucun résultat</p>';
            }
        }).catch(function() {
            document.getElementById('mr').innerHTML = '<p style="text-align:center;color:#f44336;padding:20px;">Erreur réseau</p>';
        });
    };
    
    window.playM = function(url, title, artist) {
        if (!url) { alert('Aperçu non disponible pour ce titre'); return; }
        if (!window._ga) window._ga = new Audio();
        window._ga.src = url;
        window._ga.play().catch(function() { alert('Lecture bloquée, réessaie'); });
        if (typeof addNotif !== 'undefined') addNotif('🎵', title, artist);
    };
    
    setInterval(function() {
        fetch('/api/stats').then(function(r) { return r.json(); }).then(function(s) {
            if (s.matches > oldMatches && oldMatches > 0) { addNotif('💕', 'Nouveau match !', 'Quelqu\'un t\'a liké !'); }
            oldMatches = s.matches;
        }).catch(function() {});
    }, 15000);
})();
