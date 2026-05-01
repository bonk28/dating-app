// ============ BOUTON FLOTTANT NOTIFICATIONS ============
(function() {
    // Créer le bouton flottant
    const badge = document.createElement('div');
    badge.id = 'notifBadge';
    badge.style.cssText = `
        position: fixed; bottom: 90px; left: 20px;
        width: 50px; height: 50px; border-radius: 50%;
        background: #f44336; color: white; border: none;
        font-size: 1em; cursor: pointer; z-index: 9998;
        box-shadow: 0 5px 20px rgba(244,67,54,0.4);
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; transition: all 0.3s;
    `;
    badge.textContent = '0';
    badge.style.display = 'none';
    badge.onclick = showNotifications;
    document.body.appendChild(badge);
    
    // Créer le panneau de notifications
    const panel = document.createElement('div');
    panel.id = 'notifPanel';
    panel.style.cssText = `
        display: none; position: fixed; top: 0; right: 0;
        width: 320px; height: 100vh; background: white;
        z-index: 10000; box-shadow: -5px 0 20px rgba(0,0,0,0.3);
        overflow-y: auto; padding: 20px; transition: transform 0.3s;
    `;
    panel.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
            <h3>🔔 Notifications</h3>
            <button onclick="document.getElementById('notifPanel').style.display='none'" style="background:none;border:none;font-size:1.5em;cursor:pointer;">✕</button>
        </div>
        <div id="notifList"><p style="color:#999;">Aucune notification</p></div>
        <button onclick="clearNotifs()" style="width:100%;padding:10px;background:#f44336;color:white;border:none;border-radius:8px;cursor:pointer;margin-top:15px;">🗑️ Tout effacer</button>
    `;
    document.body.appendChild(panel);
    
    // Stocker les notifications
    let notifications = JSON.parse(localStorage.getItem('notifications') || '[]');
    let count = notifications.length;
    updateBadge();
    
    function updateBadge() {
        count = notifications.length;
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
        if (count > 0) {
            badge.style.animation = 'pulse 0.5s';
            setTimeout(() => badge.style.animation = '', 500);
        }
    }
    
    function showNotifications() {
        const list = document.getElementById('notifList');
        if (notifications.length === 0) {
            list.innerHTML = '<p style="color:#999;text-align:center;padding:30px;">Aucune notification</p>';
        } else {
            list.innerHTML = notifications.map((n, i) => `
                <div style="padding:12px;background:#f5f5f5;border-radius:8px;margin:5px 0;display:flex;align-items:center;gap:10px;">
                    <span style="font-size:1.5em;">${n.icon}</span>
                    <div style="flex:1;">
                        <div style="font-weight:500;">${n.title}</div>
                        <div style="font-size:0.8em;color:#666;">${n.body}</div>
                        <div style="font-size:0.7em;color:#999;">${n.time}</div>
                    </div>
                    <button onclick="removeNotif(${i})" style="background:none;border:none;color:#f44336;cursor:pointer;">✕</button>
                </div>
            `).join('');
        }
        panel.style.display = 'block';
        // Réinitialiser le compteur
        updateBadge();
    }
    
    // Fonction pour ajouter une notification
    window.addNotif = function(icon, title, body) {
        notifications.unshift({
            icon: icon,
            title: title,
            body: body,
            time: new Date().toLocaleTimeString()
        });
        localStorage.setItem('notifications', JSON.stringify(notifications));
        updateBadge();
        
        // Son
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CA');
            audio.play();
        } catch(e) {}
    };
    
    window.removeNotif = function(i) {
        notifications.splice(i, 1);
        localStorage.setItem('notifications', JSON.stringify(notifications));
        showNotifications();
        updateBadge();
    };
    
    window.clearNotifs = function() {
        notifications = [];
        localStorage.setItem('notifications', JSON.stringify(notifications));
        showNotifications();
        updateBadge();
    };
    
    // CSS pulse
    const style = document.createElement('style');
    style.textContent = '@keyframes pulse{0%,100%{transform:scale(1);}50%{transform:scale(1.2);}}';
    document.head.appendChild(style);
    
    // Vérifier nouveaux messages/likes toutes les 10s
    let oldMatches = 0, oldMessages = 0;
    setInterval(() => {
        fetch('/api/stats').then(r => r.json()).then(stats => {
            if (stats.matches > oldMatches && oldMatches > 0) {
                addNotif('💕', 'Nouveau match !', 'Quelqu\'un t\'a liké !');
            }
            oldMatches = stats.matches;
        }).catch(() => {});
    }, 10000);
})();
