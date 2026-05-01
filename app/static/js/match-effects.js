function showMatchEffect(compatibility) {
    // Son de match
    try {
        var audio = new Audio('data:audio/wav;base64,UklGRl5IAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YTpIAACAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CAf39/f4B/f3+AgH9/f3+Af39/gIB/f39/gH9/f4CA');
        audio.play();
    } catch(e) {}
    
    // Confettis
    for (var i = 0; i < 50; i++) {
        setTimeout(function() {
            var confetti = document.createElement('div');
            var colors = ['#ff2d78','#00e5ff','#ffd700','#00c853','#ff6b9d','#aeea00'];
            confetti.style.cssText = 'position:fixed;top:-10px;left:'+Math.random()*100+'%;width:10px;height:10px;background:'+colors[Math.floor(Math.random()*colors.length)]+';border-radius:50%;z-index:9999;animation:confettiFall '+ (Math.random()*2+2) +'s linear forwards;pointer-events:none;';
            document.body.appendChild(confetti);
            setTimeout(function() { confetti.remove(); }, 3000);
        }, i * 30);
    }
    
    // Animation CSS
    if (!document.getElementById('confettiStyle')) {
        var style = document.createElement('style');
        style.id = 'confettiStyle';
        style.textContent = '@keyframes confettiFall{0%{transform:translateY(0)rotate(0deg);opacity:1}100%{transform:translateY(100vh)rotate(720deg);opacity:0}}';
        document.head.appendChild(style);
    }
}

// Overlay de match
function showMatchOverlay(username, compatibility) {
    var overlay = document.createElement('div');
    overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.9);z-index:10000;display:flex;flex-direction:column;align-items:center;justify-content:center;animation:fadeIn .5s';
    overlay.innerHTML = '<div style="font-size:6em;animation:bounceIn 1s">💕</div><h2 style="color:white;font-size:2em;margin:20px;">IT\'S A MATCH!</h2><p style="color:#ffd700;font-size:1.2em;">Avec <b>'+username+'</b></p><p style="color:#00c853;">'+compatibility+'% compatible</p><button onclick="this.parentElement.remove()" style="margin-top:30px;padding:15px 40px;background:linear-gradient(135deg,#ff2d78,#00e5ff);color:white;border:none;border-radius:30px;font-size:1.1em;cursor:pointer;">💬 ENVOYER UN MESSAGE</button><button onclick="this.parentElement.remove()" style="margin-top:10px;padding:10px 30px;background:transparent;color:white;border:1px solid rgba(255,255,255,.3);border-radius:30px;cursor:pointer;">Continuer à swiper</button>';
    document.body.appendChild(overlay);
    showMatchEffect(compatibility);
}
