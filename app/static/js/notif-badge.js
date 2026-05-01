(function() {
    var badge = document.createElement('div');
    badge.id = 'notifBadge';
    badge.style.cssText = 'position:fixed;bottom:140px;left:20px;width:50px;height:50px;border-radius:50%;background:#f44336;color:white;font-size:1em;cursor:pointer;z-index:9998;box-shadow:0 5px 20px rgba(244,67,54,0.4);display:none;align-items:center;justify-content:center;font-weight:bold;';
    badge.textContent = '0';
    badge.onclick = function(){
        var p = document.getElementById('notifPanel');
        p.style.display = p.style.display === 'block' ? 'none' : 'block';
        showNotifs();
    };
    document.body.appendChild(badge);
    
    var panel = document.createElement('div');
    panel.id = 'notifPanel';
    panel.style.cssText = 'display:none;position:fixed;top:0;right:0;width:320px;height:100vh;background:white;z-index:10000;box-shadow:-5px 0 20px rgba(0,0,0,0.3);overflow-y:auto;padding:20px;';
    panel.innerHTML = '<h3>🔔 Notifications</h3><button onclick="document.getElementById(\'notifPanel\').style.display=\'none\'" style="position:absolute;top:20px;right:20px;background:none;border:none;font-size:1.5em;cursor:pointer;">✕</button><div id="notifList"></div><button onclick="clearNotifs()" style="width:100%;padding:10px;background:#f44336;color:white;border:none;border-radius:8px;cursor:pointer;margin-top:15px;">🗑️ Tout effacer</button>';
    document.body.appendChild(panel);
    
    var notifications = JSON.parse(localStorage.getItem('notifs') || '[]');
    
    function playSound() {
        try { new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CA').play(); } catch(e) {}
    }
    
    window.addNotif = function(icon, title, body) {
        notifications.unshift({icon:icon, title:title, body:body, time:new Date().toLocaleTimeString()});
        localStorage.setItem('notifs', JSON.stringify(notifications));
        badge.textContent = notifications.length;
        badge.style.display = 'flex';
        playSound();
    };
    
    function showNotifs() {
        var list = document.getElementById('notifList');
        list.innerHTML = notifications.length === 0 ? '<p style="color:#999;padding:30px;">Aucune notification</p>' :
            notifications.map(function(n, i){ return '<div style="padding:12px;background:#f5f5f5;border-radius:8px;margin:5px 0;display:flex;gap:10px;"><span style="font-size:1.5em;">'+n.icon+'</span><div style="flex:1;"><b>'+n.title+'</b><br><small>'+n.body+'</small><br><small style="color:#999;">'+n.time+'</small></div></div>'; }).join('');
    }
    
    window.clearNotifs = function() { notifications = []; localStorage.setItem('notifs', JSON.stringify(notifications)); badge.style.display = 'none'; showNotifs(); };
    
    var oldMatches = 0;
    setInterval(function() {
        fetch('/api/stats').then(function(r){ return r.json(); }).then(function(s){
            if (s.matches > oldMatches && oldMatches > 0) { addNotif('💕', 'Nouveau match !', 'Quelqu\'un t\'a liké !'); }
            oldMatches = s.matches;
        }).catch(function(){});
    }, 10000);
})();
