// Demander permission notification
function requestNotif() {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
  }
}

function notify(title, body, icon) {
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(title, { body, icon: icon || '/static/icons/icon-192.png' });
  }
}

// Vérifier nouveaux messages/likes toutes les 10s
setInterval(() => {
  fetch('/api/stats').then(r => r.json()).then(stats => {
    const old = parseInt(localStorage.getItem('lastMatches') || '0');
    if (stats.matches > old) {
      notify('💕 Nouveau match !', 'Quelqu\'un t\'a liké !');
    }
    localStorage.setItem('lastMatches', stats.matches);
  });
}, 10000);

requestNotif();
