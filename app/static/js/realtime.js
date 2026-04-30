// ============ TEMPS RÉEL ============
const socket = io();

let localStream = null;
let pc = null;
let currentCallRoom = null;

// ============ STATUT EN LIGNE ============
socket.on('connect', () => {
    console.log('🟢 Connecté au serveur');
});

socket.on('user_online', (data) => {
    updateUserStatus(data.user_id, true);
    showNotification(`${data.username} est en ligne 🟢`);
});

socket.on('user_offline', (data) => {
    updateUserStatus(data.user_id, false, data.last_seen);
});

socket.on('online_users', (users) => {
    users.forEach(u => updateUserStatus(u.user_id, true));
});

function updateUserStatus(userId, online, lastSeen = null) {
    const els = document.querySelectorAll(`[data-user-status="${userId}"]`);
    els.forEach(el => {
        if (online) {
            el.innerHTML = '<span style="color:#4CAF50;">●</span> En ligne';
        } else {
            el.innerHTML = `<span style="color:#999;">●</span> Vu à ${lastSeen || '...'}`;
        }
    });
}

// ============ APPELS ============
function startCall(userId, callType) {
    socket.emit('call_user', { to_user: userId, call_type: callType });
    showCallingUI(userId, callType);
}

function showCallingUI(userId, callType) {
    const overlay = document.createElement('div');
    overlay.id = 'callOverlay';
    overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.9);z-index:10000;display:flex;flex-direction:column;align-items:center;justify-content:center;color:white;';
    overlay.innerHTML = `
        <div style="font-size:5em;animation:pulse 1.5s infinite;">${callType === 'video' ? '📹' : '📞'}</div>
        <h2 style="margin:20px;">Appel en cours...</h2>
        <button onclick="cancelCall()" style="padding:15px 40px;background:#f44336;color:white;border:none;border-radius:25px;font-size:1.2em;cursor:pointer;">Raccrocher</button>
    `;
    document.body.appendChild(overlay);
}

socket.on('incoming_call', async (data) => {
    if (confirm(`${data.from} vous appelle en ${data.call_type === 'video' ? 'vidéo' : 'vocal'} ! Accepter ?`)) {
        currentCallRoom = data.room;
        socket.emit('accept_call', { room: data.room });
        await setupCall(data.call_type, data.room);
    } else {
        socket.emit('reject_call', { room: data.room });
    }
});

socket.on('call_accepted', async (data) => {
    currentCallRoom = data.room;
    await setupCall('video', data.room);
});

async function setupCall(callType, room) {
    try {
        const constraints = {
            audio: true,
            video: callType === 'video'
        };
        
        localStream = await navigator.mediaDevices.getUserMedia(constraints);
        
        // Afficher le flux local
        const localVideo = document.getElementById('localVideo');
        if (localVideo) localVideo.srcObject = localStream;
        
        // Créer connexion peer-to-peer
        const config = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };
        pc = new RTCPeerConnection(config);
        
        localStream.getTracks().forEach(track => pc.addTrack(track, localStream));
        
        pc.ontrack = (event) => {
            const remoteVideo = document.getElementById('remoteVideo');
            if (remoteVideo) remoteVideo.srcObject = event.streams[0];
        };
        
        pc.onicecandidate = (event) => {
            if (event.candidate) {
                socket.emit('signal', {
                    room: room,
                    type: 'ice-candidate',
                    candidate: event.candidate
                });
            }
        };
        
        // Créer offre
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        socket.emit('signal', {
            room: room,
            type: 'offer',
            sdp: pc.localDescription
        });
        
    } catch(e) {
        alert('Erreur caméra/micro : ' + e.message);
    }
}

socket.on('signal', async (data) => {
    if (!pc) return;
    
    if (data.type === 'offer') {
        await pc.setRemoteDescription(new RTCSessionDescription(data.sdp));
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        socket.emit('signal', {
            room: currentCallRoom,
            type: 'answer',
            sdp: pc.localDescription
        });
    } else if (data.type === 'answer') {
        await pc.setRemoteDescription(new RTCSessionDescription(data.sdp));
    } else if (data.type === 'ice-candidate') {
        await pc.addIceCandidate(new RTCIceCandidate(data.candidate));
    }
});

socket.on('call_ended', () => {
    endCall();
});

function cancelCall() {
    if (currentCallRoom) {
        socket.emit('end_call', { room: currentCallRoom });
    }
    endCall();
}

function endCall() {
    if (pc) { pc.close(); pc = null; }
    if (localStream) { localStream.getTracks().forEach(t => t.stop()); localStream = null; }
    currentCallRoom = null;
    const overlay = document.getElementById('callOverlay');
    if (overlay) overlay.remove();
}
