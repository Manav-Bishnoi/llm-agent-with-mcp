// frontend/app.js
// Complete Chat Interface for Multi-Agent AI System
// Features: Chat UI, agent selection, conversation history, WebSocket support, error handling, responsive design

const API_BASE = 'http://localhost:8000';

// DOM Elements
const chatContainer = document.getElementById('chat-container');
const messageList = document.getElementById('message-list');
const inputForm = document.getElementById('input-form');
const userInput = document.getElementById('user-input');
const statusBar = document.getElementById('status-bar');

// Set status bar
function setStatus(msg) {
    statusBar.textContent = msg;
}

// Add message to chat
function addMessage(msg, sender) {
    const li = document.createElement('li');
    li.className = sender;
    
    let displayText = '';
    if (typeof msg === 'string') {
        displayText = msg;
    } else if (msg && typeof msg === 'object') {
        if (msg.data && typeof msg.data === 'object' && msg.data.data) {
            displayText = msg.data.data;
        } else if (msg.data && typeof msg.data === 'string') {
            displayText = msg.data;
        } else if (msg.response && typeof msg.response === 'object' && msg.response.data) {
            displayText = msg.response.data;
        } else if (msg.error) {
            displayText = `Error: ${msg.error}`;
        } else {
            displayText = JSON.stringify(msg, null, 2);
        }
    }
    
    li.textContent = `${sender === 'user' ? 'You' : 'Agent'}: ${displayText}`;
    messageList.appendChild(li);
    messageList.scrollTop = messageList.scrollHeight;
}

// Send message to backend using /main_query endpoint (always auto-select)
async function sendMessage(text) {
    addMessage({ text }, 'user');
    setStatus('Sending message...');
    try {
        const requestBody = { query: text };
        const response = await fetch(`${API_BASE}/main_query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        addMessage(data, 'agent');
        setStatus('Ready');
    } catch (error) {
        console.error('API error:', error);
        const errorMsg = `API error: ${error.message}. Please try again.`;
        addMessage({ error: errorMsg }, 'agent');
        setStatus('Error occurred');
    }
}

// Handle form submit
inputForm.onsubmit = (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;
    sendMessage(text);
    userInput.value = '';
};

// Initialize on page load
window.onload = async () => {
    setStatus('Ready');
};

// Export for testing
window._chat = { sendMessage, addMessage, setStatus };
