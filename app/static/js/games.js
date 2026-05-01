// ============ JEUX SYNCHRONISÉS ============
function openGames() {
  document.getElementById('gamesPanel').style.display = 'block';
  socket.emit('join_game', { match_id: mid });
}

function closeGames() {
  document.getElementById('gamesPanel').style.display = 'none';
  document.getElementById('gameArea').innerHTML = '';
}

// Pierre Feuille Ciseaux
function startRPS() {
  const area = document.getElementById('gameArea');
  area.innerHTML = `
    <h4 style="text-align:center;">✊ ✋ ✌️</h4>
    <p style="text-align:center;color:#aaa;">Choisis et confirme. L'adversaire ne verra rien avant d'avoir choisi !</p>
    <div style="display:flex;justify-content:center;gap:15px;margin:15px 0;">
      <button onclick="chooseRPS('rock')" id="btn-rock" style="font-size:3em;padding:15px;border-radius:15px;background:#1a1a2e;border:2px solid #333;cursor:pointer;">✊</button>
      <button onclick="chooseRPS('paper')" id="btn-paper" style="font-size:3em;padding:15px;border-radius:15px;background:#1a1a2e;border:2px solid #333;cursor:pointer;">✋</button>
      <button onclick="chooseRPS('scissors')" id="btn-scissors" style="font-size:3em;padding:15px;border-radius:15px;background:#1a1a2e;border:2px solid #333;cursor:pointer;">✌️</button>
    </div>
    <button id="rpsConfirm" onclick="confirmRPS()" style="display:block;margin:10px auto;padding:12px 30px;background:#e91e63;color:white;border:none;border-radius:25px;cursor:pointer;opacity:0.5;" disabled>✅ Confirmer</button>
    <p id="rpsStatus" style="text-align:center;color:#aaa;margin:10px;"></p>
    <div id="rpsResult" style="text-align:center;font-size:1.3em;margin:10px;"></div>
  `;
  window.rpsChoice = null;
}

function chooseRPS(choice) {
  window.rpsChoice = choice;
  document.querySelectorAll('#gameArea button[id^="btn-"]').forEach(b => b.style.border = '2px solid #333');
  document.getElementById('btn-' + choice).style.border = '3px solid #e91e63';
  document.getElementById('rpsConfirm').disabled = false;
  document.getElementById('rpsConfirm').style.opacity = '1';
}

function confirmRPS() {
  if (!window.rpsChoice) return;
  document.getElementById('rpsStatus').textContent = '✅ Choix envoyé ! En attente de l\'autre joueur...';
  document.getElementById('rpsConfirm').disabled = true;
  socket.emit('rps_choice', { match_id: mid, choice: window.rpsChoice });
}

socket.on('rps_reveal', (data) => {
  const emojis = { rock: '✊', paper: '✋', scissors: '✌️' };
  document.getElementById('rpsResult').innerHTML = 
    `Toi: ${emojis[data.your_choice]} | Lui: ${emojis[data.their_choice]}<br>` +
    (data.winner === 'draw' ? '🤝 Égalité !' : 
     data.winner === 'you' ? '🎉 Tu gagnes !' : '😢 Tu perds...');
  document.getElementById('rpsStatus').textContent = '';
});

// Action ou Vérité
function startAV() {
  document.getElementById('gameArea').innerHTML = `
    <h4 style="text-align:center;">🎯 Action ou Vérité</h4>
    <div style="display:flex;gap:10px;justify-content:center;margin:15px 0;">
      <button onclick="chooseAV('classic')" style="padding:12px 25px;background:#4CAF50;color:white;border:none;border-radius:10px;">🎯 Classique</button>
      <button onclick="chooseAV('adult')" style="padding:12px 25px;background:#f44336;color:white;border:none;border-radius:10px;">🔞 Adulte</button>
    </div>
    <div id="avChoices"></div>
    <div id="avResult" style="text-align:center;padding:15px;"></div>
  `;
}

const avData = {
  classic: {
    actions: ["Fais 10 pompes","Imite une célébrité","Danse 30 secondes","Chante","Fais le cri d'un animal"],
    verites: ["Ton plus grand rêve ?","Ta plus grande peur ?","Ton pire date ?","Premier crush ?","Talent caché ?"]
  },
  adult: {
    actions: ["Envoie un selfie sexy","Mords tes lèvres","Clin d'œil","Passe ta main dans tes cheveux","Chuchote un message"],
    verites: ["Ton plus gros turn-on ?","Fantasme le plus fou ?","Premier baiser ?","Date le plus gênant ?","Ce qui t'excite ?"]
  }
};

function chooseAV(version) {
  document.getElementById('avChoices').innerHTML = `
    <button onclick="pickAV('${version}','action')" style="padding:12px 25px;background:#ff9800;color:white;border:none;border-radius:10px;margin:5px;">⚡ Action</button>
    <button onclick="pickAV('${version}','verite')" style="padding:12px 25px;background:#2196F3;color:white;border:none;border-radius:10px;margin:5px;">💬 Vérité</button>
  `;
}

function pickAV(version, type) {
  const list = avData[version][type + 's'];
  const challenge = list[Math.floor(Math.random() * list.length)];
  document.getElementById('avResult').innerHTML = `
    <div style="background:#1a1a2e;padding:20px;border-radius:15px;border:2px solid ${type==='action'?'#ff9800':'#2196F3'};">
      <b>${type==='action'?'⚡ ACTION':'💬 VÉRITÉ'}</b><br>${challenge}
    </div>
    <button onclick="sendAV('${version}','${type}','${challenge.replace(/'/g, "\\'")}')" style="padding:10px 20px;background:#e91e63;color:white;border:none;border-radius:20px;margin-top:10px;cursor:pointer;">📤 Envoyer à l'autre</button>
  `;
}

function sendAV(version, type, challenge) {
  socket.emit('av_send', { match_id: mid, to_user: oid, version, type, challenge });
  alert('✅ Défi envoyé !');
}

socket.on('av_receive', (data) => {
  document.getElementById('avResult').innerHTML = `
    <div style="background:#1a1a2e;padding:20px;border-radius:15px;border:2px solid ${data.type==='action'?'#ff9800':'#2196F3'};">
      📩 <b>${data.type==='action'?'⚡ ACTION':'💬 VÉRITÉ'} reçu !</b><br>${data.challenge}
    </div>`;
});
