// ============ BADGE NOTIFICATION ============
(function() {
    // Créer le badge
    var badge = document.createElement('div');
    badge.id = 'notifBadge';
    badge.innerHTML = '🔔';
    badge.style.cssText = 'position:fixed;top:20px;right:20px;width:55px;height:55px;border-radius:50%;background:#f44336;color:white;font-size:1.3em;cursor:pointer;z-index:9999;box-shadow:0 5px 25px rgba(244,67,54,0.6);display:flex;align-items:center;justify-content:center;font-weight:bold;';
    badge.onclick = function() {
        var p = document.getElementById('notifPanel');
        if (p.style.display === 'block') {
            p.style.display = 'none';
        } else {
            p.style.display = 'block';
            showNotifs();
        }
    };
    document.body.appendChild(badge);
    
    // Créer le panneau
    var panel = document.createElement('div');
    panel.id = 'notifPanel';
    panel.style.cssText = 'display:none;position:fixed;top:0;right:0;width:300px;height:100vh;background:white;z-index:10000;box-shadow:-5px 0 30px rgba(0,0,0,0.3);overflow-y:auto;padding:20px;';
    panel.innerHTML = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;"><h3>🔔 Notifications</h3><button onclick="document.getElementById(\'notifPanel\').style.display=\'none\'" style="background:none;border:none;font-size:1.5em;cursor:pointer;">✕</button></div><div id="notifList"></div><button onclick="clearNotifs()" style="width:100%;padding:10px;background:#f44336;color:white;border:none;border-radius:8px;cursor:pointer;margin-top:15px;">🗑️ Tout effacer</button>';
    document.body.appendChild(panel);
    
    var notifications = JSON.parse(localStorage.getItem('notifs') || '[]');
    
    function playSound() {
        try { 
            var a = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CA');
            a.play(); 
        } catch(e) {}
    }
    
    window.addNotif = function(icon, title, body) {
        notifications.unshift({icon:icon, title:title, body:body, time:new Date().toLocaleTimeString()});
        localStorage.setItem('notifs', JSON.stringify(notifications));
        var badge = document.getElementById('notifBadge');
        if (badge) {
            badge.innerHTML = '🔔<sup style="font-size:0.5em;">'+notifications.length+'</sup>';
            badge.style.animation = 'pulse 0.5s';
            setTimeout(function(){ badge.style.animation = ''; }, 500);
        }
        playSound();
    };
    
    function showNotifs() {
        var list = document.getElementById('notifList');
        if (notifications.length === 0) {
            list.innerHTML = '<p style="color:#999;text-align:center;padding:30px;">Aucune notification</p>';
        } else {
            list.innerHTML = notifications.map(function(n, i) {
                return '<div style="padding:12px;background:#f5f5f5;border-radius:8px;margin:5px 0;display:flex;gap:10px;"><span style="font-size:1.5em;">'+n.icon+'</span><div style="flex:1;"><b>'+n.title+'</b><br><small>'+n.body+'</small><br><small style="color:#999;">'+n.time+'</small></div></div>';
            }).join('');
        }
    }
    
    window.clearNotifs = function() {
        notifications = [];
        localStorage.setItem('notifs', JSON.stringify(notifications));
        var badge = document.getElementById('notifBadge');
        if (badge) badge.innerHTML = '🔔';
        showNotifs();
    };
    
    // Animation pulse
    var style = document.createElement('style');
    style.textContent = '@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.3)}}';
    document.head.appendChild(style);
    
    // Tester avec une notif de démo après 3 secondes (à enlever en prod)
    // setTimeout(function(){ addNotif('💕', 'Bienvenue !', 'Les notifications fonctionnent !'); }, 3000);
    
    var oldMatches = 0;
    setInterval(function() {
        fetch('/api/stats').then(function(r){ return r.json(); }).then(function(s){
            if (s.matches > oldMatches && oldMatches > 0) {
                addNotif('💕', 'Nouveau match !', 'Quelqu\'un t\'a liké !');
            }
            oldMatches = s.matches;
        }).catch(function(){});
    }, 15000);
    
})();
