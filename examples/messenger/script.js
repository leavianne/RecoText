// Messenger Beispiele von GitHub, mit KI erweitert und händig angepasst

const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const typingIndicator = document.getElementById('typing-indicator');
const currentTimeElement = document.getElementById('current-time');
const micIcon = document.querySelector('.fa-microphone-lines');

const annaResponses = [
    "Hallo! Mir geht es gut, danke",
    "Ja, ich habe Zeit. Was ist los?",
    "Das klingt interessant",
    "Klar, ich kann helfen",
    "Treffen klingt gut",
    "Wow, das sieht toll aus",
    "Da stimme ich dir zu",
    "Super, freut mich",
    "Bin gespannt",
    "Ruf gerne an",
    "Gern geschehen",
    "Ja, das Wetter ist perfekt",
    "Haha, das ist lustig",
    "Ja, ich erinnere mich",
    "Noch wach, aber müde",
];

// ===== FUNKTIONEN =====
// Uhrzeit aktualisieren
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('de-DE', { 
        hour: '2-digit', minute: '2-digit' 
    });
    currentTimeElement.textContent = timeString;
}
setInterval(updateTime, 60000);
updateTime();

// Nachricht hinzufügen
function addMessage(text, isOutgoing = false) {
    addNewMessage(text, isOutgoing);
}

function addNewMessage(text, isOutgoing) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isOutgoing ? 'outgoing' : 'incoming'}`;
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    bubbleDiv.textContent = text;
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    const now = new Date();
    timeDiv.textContent = now.toLocaleTimeString('de-DE', { 
        hour: '2-digit', minute: '2-digit' 
    });
    
    messageDiv.appendChild(bubbleDiv);
    messageDiv.appendChild(timeDiv);
    messagesContainer.appendChild(messageDiv);
    setTimeout(scrollToBottom, 0);
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Tippen von Anna
let isTyping = false;
let typingTimeout = null;

// Simuliert das Tippen
function simulateTyping(duration = 1500) {
    const statusElement = document.querySelector('.contact-status');
    if (isTyping) clearTimeout(typingTimeout);
    if (!isTyping) statusElement.dataset.originalStatus = statusElement.textContent;
    isTyping = true;
    statusElement.textContent = "schreibt...";
    typingIndicator.classList.add('active');
    typingTimeout = setTimeout(() => {
        resetTypingStatus();
    }, duration);
    return duration;
}

function resetTypingStatus() {
    const statusElement = document.querySelector('.contact-status');
    const originalStatus = statusElement.dataset.originalStatus || "Online";
    statusElement.textContent = originalStatus;
    typingIndicator.classList.remove('active');
    isTyping = false;
}

// Zufällige Antwort von Anna
function getRandomAnnaResponse() {
    const randomIndex = Math.floor(Math.random() * annaResponses.length);
    return annaResponses[randomIndex];
}

// Anna antwortet
function respondAsAnna() {
    const typingDuration = 2000;
    simulateTyping(typingDuration);
    setTimeout(() => {
        const response = getRandomAnnaResponse();
        addMessage(response, false);
    }, typingDuration);
}

function sendAnnaFirstMessage() {
    setTimeout(() => {
        const firstMessage = "Hallo! Wie geht es dir?";
        simulateTyping(1200);
        setTimeout(() => {
            addMessage(firstMessage, false);
            setTimeout(() => {
                messageInput.focus();
            }, 300);
        }, 1200);
    }, 800);
}

// ===== SPRACHERKENNUNG =====
let isRecording = false;

async function startVoiceRecognition() {
    if (isRecording) return;
    isRecording = true;
    micIcon.classList.remove('fa-microphone-lines');
    micIcon.classList.add('fa-microphone');
    micIcon.style.color = '#f56565';
    micIcon.style.animation = 'pulse 1.5s infinite';
    
    console.log('Starte Spracherkennung...');
    
    try {
        const typingElement = document.querySelector('.contact-status');
        const originalStatus = typingElement.textContent;

        setTimeout(() => {
            if (isRecording) typingElement.textContent = "Warte auf Sprache...";
        }, 1000);
        
        const response = await fetch("/voice-transcribe", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        const data = await response.json();
        
        typingElement.textContent = originalStatus;
        
        if (data.status === "success") {
            console.log("Spracherkennung erfolgreich:", data.text);
            
            if (data.text && data.text.trim()) {
                messageInput.value = data.text;
                messageInput.focus();
            }
        } else {
            console.error("Fehler bei Spracherkennung:", data.message);
            alert("Sprache nicht verstanden. Bitte nochmal sprechen.");
        }
    } catch (error) {
        console.error("Netzwerkfehler:", error);
        alert("Verbindungsfehler bei Spracherkennung");
    } finally {
        isRecording = false;
    }
    setTimeout(() => {
        resetMicButton();
    }, 1500);
}

// ===== INITIALISIERUNG =====
// Anna schickt erste Nachricht
sendAnnaFirstMessage();

// ===== EVENT LISTENERS =====
// Senden-Button
sendBtn.addEventListener('click', () => {
    const message = messageInput.value.trim();
    if (message) {
        addMessage(message, true);
        messageInput.value = '';
        setTimeout(() => {
            respondAsAnna();
        }, 500);
    }
});

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendBtn.click();
    }
});

if (micIcon) {
    micIcon.addEventListener('click', startVoiceRecognition);
}

function resetMicButton() {
    micIcon.classList.remove('fa-microphone');
    micIcon.classList.add('fa-microphone-lines');
    micIcon.style.color = '';
    micIcon.style.animation = '';
}

// ===== EMOJI-ERKENNUNG (Hand) =====
let isEmojiRecognitionRunning = false;

async function startEmojiRecognition() {
    if (isEmojiRecognitionRunning) return;
    isEmojiRecognitionRunning = true;
    const emojiIcon = document.querySelector('.fa-hand');
    if (emojiIcon) {
        emojiIcon.style.color = '#f56565';
        emojiIcon.style.animation = 'pulse 1.5s infinite';
    }
    
    console.log('Starte Emoji-Erkennung...');
    
    try {
        const typingElement = document.querySelector('.contact-status');
        const originalStatus = typingElement.textContent;
        typingElement.textContent = "Kamera wird geöffnet...";
        
        const response = await fetch("/recognize-emoji", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        const data = await response.json();
        
        typingElement.textContent = originalStatus;
        
        if (data.status === "success") {
            console.log("Emoji erkannt:", data.emoji);
            
            if (data.emoji) {
                messageInput.value += data.emoji + " ";
                messageInput.focus();
                messageInput.selectionStart = messageInput.selectionEnd = messageInput.value.length;
            }
        } else {
            console.error("Fehler bei Emoji-Erkennung:", data.message);
            alert("Emoji-Erkennung fehlgeschlagen: " + data.message);
        }

    } catch (error) {
        console.error("Netzwerkfehler:", error);
        alert("Verbindungsfehler bei Emoji-Erkennung");
    } finally {
        isEmojiRecognitionRunning = false;
    }
    setTimeout(() => {
        resetCamButton();
    }, 1500);
}

const emojiIcon = document.querySelector('.fa-hand');
if (emojiIcon) {
    emojiIcon.addEventListener('click', startEmojiRecognition);
}

function resetCamButton() {
    emojiIcon.classList.remove('fa-camera');
    emojiIcon.classList.add('fa-hand');
    emojiIcon.style.color = '';
    emojiIcon.style.animation = '';    
}

// ===== EMOJI-ERKENNUNG (Gesicht) =====
let isFaceRecognitionRunning = false;

async function startFaceRecognition() {
    if (isFaceRecognitionRunning) return;
    isFaceRecognitionRunning = true;
    const FaceIcon = document.querySelector('.fa-smile');
    if (FaceIcon) {
        FaceIcon.style.color = '#f56565';
        FaceIcon.style.animation = 'pulse 1.5s infinite';
    }
    
    console.log('Starte Emoji-Erkennung...');
    
    try {
        const typingElement = document.querySelector('.contact-status');
        const originalStatus = typingElement.textContent;
        typingElement.textContent = "Kamera wird geöffnet...";
        
        const response = await fetch("/recognize-face", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        const data = await response.json();
        
        typingElement.textContent = originalStatus;
        
        if (data.status === "success") {
            console.log("Emoji erkannt:", data.emoji);
            
            if (data.emoji) {
                messageInput.value += data.emoji + " ";
                messageInput.focus();
                messageInput.selectionStart = messageInput.selectionEnd = messageInput.value.length;
            }
        } else {
            console.error("Fehler bei Emoji-Erkennung:", data.message);
            alert("Emoji-Erkennung fehlgeschlagen: " + data.message);
        }

    } catch (error) {
        console.error("Netzwerkfehler:", error);
        alert("Verbindungsfehler bei Emoji-Erkennung");
    } finally {
        isFaceRecognitionRunning = false;
    }
    setTimeout(() => {
        resetCamButtonFace();
    }, 1500);
}

const FaceIcon = document.querySelector('.fa-smile');
if (FaceIcon) {
    FaceIcon.addEventListener('click', startFaceRecognition);
}

function resetCamButtonFace() {
    const faceIcon = document.querySelector('.fa-smile');
    if (faceIcon) {
        faceIcon.style.color = '';
        faceIcon.style.animation = '';
    }
}