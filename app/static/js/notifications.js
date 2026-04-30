// ============ NOTIFICATIONS LIVE ============
let audioCtx = null;

function playNotificationSound() {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    gainNode.gain.value = 0.3;
    oscillator.start();
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);
    oscillator.stop(audioCtx.currentTime + 0.5);
}

function vibrate(pattern = [200, 100, 200]) {
    if (navigator.vibrate) navigator.vibrate(pattern);
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    const colors = { info: '#667eea', success: '#4CAF50', love: '#f44336', match: '#ff6b6b' };
    toast.style.cssText = `
        position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
        background: ${colors[type] || colors.info}; color: white;
        padding: 15px 25px; border-radius: 25px; z-index: 9999;
        font-weight: bold; box-shadow: 0 5px 20px rgba(0,0,0,0.3);
        animation: slideDown 0.3s ease-out;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    playNotificationSound();
    vibrate();
    setTimeout(() => { toast.style.animation = 'slideUp 0.3s ease-in'; setTimeout(() => toast.remove(), 300); }, 3000);
}

// Ajouter le CSS d'animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown { from { transform: translateX(-50%) translateY(-100px); opacity: 0; } to { transform: translateX(-50%) translateY(0); opacity: 1; } }
    @keyframes slideUp { from { transform: translateX(-50%) translateY(0); opacity: 1; } to { transform: translateX(-50%) translateY(-100px); opacity: 0; } }
`;
document.head.appendChild(style);

// ============ POLLING MATCHES ============
let lastMatchCount = 0;
function checkNewMatches() {
    fetch('/api/stats')
        .then(r => r.json())
        .then(stats => {
            if (stats.matches > lastMatchCount) {
                showToast('🎉 Nouveau match ! Quelqu\'un t\'a liké !', 'match');
                vibrate([300, 100, 300, 100, 500]);
            }
            lastMatchCount = stats.matches;
        });
}
setInterval(checkNewMatches, 10000);
