const videoElement = document.getElementById('video');

// WebRTC configuration
const config = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' } // Use a public STUN server
  ]
};

// Initialize WebRTC connection
const peerConnection = new RTCPeerConnection(config);

// Handle incoming video stream
peerConnection.ontrack = (event) => {
  videoElement.srcObject = event.streams[0];
};

// Connect to the WebRTC signaling server
const socket = new WebSocket('ws://51.154.64.248:8889/cam1');

// Handle signaling messages
socket.onmessage = async (message) => {
  const data = JSON.parse(message.data);

  if (data.type === 'offer') {
    await peerConnection.setRemoteDescription(new RTCSessionDescription(data));
    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    socket.send(JSON.stringify(peerConnection.localDescription));
  }
};

// Add a dummy media stream to kickstart negotiation
navigator.mediaDevices
  .getUserMedia({ video: false, audio: false })
  .then((stream) => {
    stream.getTracks().forEach((track) => peerConnection.addTrack(track, stream));
  })
  .catch((error) => {
    console.error('Error adding dummy media stream:', error);
  });