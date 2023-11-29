let isRecording = false;
let mediaRecorder;
let audioChunks = [];

document.getElementById('recordButton').addEventListener('click', () => {
    const recordButton = document.getElementById('recordButton');

    if (!isRecording) {
        startRecording();
        recordButton.classList.add('flashing');
        recordButton.textContent = "Stop Recording";
    } else {
        stopRecording();
        recordButton.classList.remove('flashing');
        recordButton.textContent = "Start Recording";
    }

    isRecording = !isRecording;
});


function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            mediaRecorder.start();
        })
        .catch(e => console.error(e));
}

function stopRecording() {
    mediaRecorder.stop();
    mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        sendAudioToServer(audioBlob);
        audioChunks = []; // Reset the audio chunks for the next recording
    };
}

function sendAudioToServer(audioBlob) {
    console.log("Audio Blob size:", audioBlob.size);
    console.log("Audio Blob type:", audioBlob.type);
    let formData = new FormData();
    formData.append('audioFile', audioBlob, 'recording.wav');

    fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('transcription').value = data.transcription;
        document.getElementById('chatGptResponse').value = data.chatGptResponse;
    })
    .catch(error => console.error('Error:', error));
}

document.getElementById('sendToChatGPTButton').addEventListener('click', function() {
    const transcribedText = document.getElementById('transcription').value;
    console.log('Transcribed Text:', transcribedText); // Log transcribedText
    sendToChatGPT(transcribedText);
});

function sendToChatGPT(transcribedText) {
    const sessionId = getSessionId();
    console.log('Session ID:', sessionId); // Log sessionId

    fetch('http://localhost:5000/chatgpt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: sessionId,
            message: transcribedText
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('ChatGpt Response:', data.chatGptResponse); // Log chatGptResponse
        console.log('Command Output:', data.commandOutput); // Log commandOutput
        document.getElementById('chatGptResponse').value = data.chatGptResponse;
        document.getElementById('commandOutput').value = data.commandOutput;
    })
    .catch(error => {
        console.error('Error:', error); // Log errors
    });
}


function getSessionId() {
    // Retrieve the existing session ID from local storage or create a new one
    let sessionId = localStorage.getItem('sessionId');
    if (!sessionId) {
        sessionId = 'session-' + Date.now(); // Implement this to generate a unique ID
        localStorage.setItem('sessionId', sessionId);
    }
    return sessionId;
}

