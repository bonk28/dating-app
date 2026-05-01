// Demander la position et l'envoyer au serveur
function updateLocation() {
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                fetch('/api/update-location', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    })
                }).then(function(r) { return r.json(); }).then(function(d) {
                    if (d.success) console.log('📍 Position mise à jour');
                });
            },
            function(error) {
                console.log('📍 Géolocalisation refusée');
            },
            { enableHighAccuracy: true }
        );
    }
}

// Mettre à jour au chargement et toutes les 5 minutes
updateLocation();
setInterval(updateLocation, 300000);
