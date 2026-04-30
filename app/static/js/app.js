// ============ GÉOLOCALISATION ============
function updateLocation() {
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                fetch('/api/update-location', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    })
                });
            },
            (error) => console.log('Géolocalisation refusée')
        );
    }
}

// Mettre à jour la position toutes les 5 minutes
updateLocation();
setInterval(updateLocation, 300000);

// ============ SWIPE TACTILE ============
let startX, startY, currentX, currentY;
let isDragging = false;

function initSwipe() {
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('touchstart', handleStart);
        card.addEventListener('touchmove', handleMove);
        card.addEventListener('touchend', handleEnd);
        
        card.addEventListener('mousedown', handleStart);
        card.addEventListener('mousemove', handleMove);
        card.addEventListener('mouseup', handleEnd);
    });
}

function handleStart(e) {
    const point = e.touches ? e.touches[0] : e;
    startX = point.clientX;
    startY = point.clientY;
    isDragging = true;
    e.target.closest('.card').style.transition = 'none';
}

function handleMove(e) {
    if (!isDragging) return;
    e.preventDefault();
    
    const point = e.touches ? e.touches[0] : e;
    currentX = point.clientX;
    currentY = point.clientY;
    
    const diffX = currentX - startX;
    const diffY = currentY - startY;
    const card = e.target.closest('.card');
    
    card.style.transform = `translate(${diffX}px, ${diffY}px) rotate(${diffX * 0.05}deg)`;
    
    // Afficher les badges
    const likeBadge = card.querySelector('.like-badge');
    const nopeBadge = card.querySelector('.nope-badge');
    const superBadge = card.querySelector('.super-like-badge');
    
    if (diffX > 50) {
        if (likeBadge) likeBadge.style.display = 'block';
        if (nopeBadge) nopeBadge.style.display = 'none';
    } else if (diffX < -50) {
        if (nopeBadge) nopeBadge.style.display = 'block';
        if (likeBadge) likeBadge.style.display = 'none';
    }
    
    if (diffY < -50) {
        if (superBadge) superBadge.style.display = 'block';
    }
}

function handleEnd(e) {
    if (!isDragging) return;
    isDragging = false;
    
    const diffX = currentX - startX;
    const diffY = currentY - startY;
    const card = e.target.closest('.card');
    const userId = card.dataset.userId;
    
    card.style.transition = 'transform 0.3s, opacity 0.3s';
    
    if (Math.abs(diffX) > 100 || Math.abs(diffY) > 100) {
        let direction;
        if (diffY < -100) direction = 'super_like';
        else if (diffX > 100) direction = 'like';
        else direction = 'pass';
        
        // Animation de sortie
        if (direction === 'super_like') {
            card.style.transform = 'translateY(-150%) scale(0.8)';
        } else {
            card.style.transform = `translateX(${diffX > 0 ? 150 : -150}%) rotate(${diffX > 0 ? 15 : -15}deg)`;
        }
        card.style.opacity = '0';
        
        setTimeout(() => {
            swipeUser(userId, direction);
            card.remove();
        }, 300);
    } else {
        // Retour à la position initiale
        card.style.transform = '';
        document.querySelectorAll('.like-badge, .nope-badge, .super-like-badge')
            .forEach(b => b.style.display = 'none');
    }
}

// ============ FONCTIONS DE SWIPE ============
function swipeUser(userId, direction) {
    fetch(`/api/swipe/${userId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({direction: direction})
    })
    .then(r => r.json())
    .then(data => {
        if (data.is_match) {
            showMatchNotification(data.compatibility);
        }
        updateStats();
    });
}

function showMatchNotification(compatibility) {
    const notification = document.createElement('div');
    notification.className = 'match-notification';
    notification.innerHTML = `
        <div class="match-content">
            <h1>🎉 C'est un Match !</h1>
            <p>Compatibilité : ${compatibility}%</p>
            <button onclick="this.parentElement.parentElement.remove()">Continuer</button>
            <a href="/matches">Voir mes matches</a>
        </div>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.remove(), 5000);
}

// ============ PWA INSTALLATION ============
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    const installBtn = document.getElementById('install-btn');
    if (installBtn) {
        installBtn.style.display = 'block';
        installBtn.addEventListener('click', () => {
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((result) => {
                if (result.outcome === 'accepted') {
                    console.log('PWA installée');
                }
                deferredPrompt = null;
            });
        });
    }
});

// ============ NOTIFICATIONS ============
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

function showNotification(title, body) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
            body: body,
            icon: '/static/icons/icon-192.png'
        });
    }
}

// ============ STATISTIQUES ============
function updateStats() {
    fetch('/api/stats')
        .then(r => r.json())
        .then(stats => {
            const statsEl = document.getElementById('user-stats');
            if (statsEl) {
                statsEl.innerHTML = `
                    💕 ${stats.matches} matches | 
                    ❤️ ${stats.likes_received} likes | 
                    💬 ${stats.messages_sent} messages
                `;
            }
        });
}

// ============ INITIALISATION ============
document.addEventListener('DOMContentLoaded', () => {
    initSwipe();
    updateStats();
    requestNotificationPermission();
    
    // Rafraîchir les stats toutes les 30 secondes
    setInterval(updateStats, 30000);
});
