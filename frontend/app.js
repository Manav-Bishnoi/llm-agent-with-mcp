// frontend/app.js
// Complete Chat Interface for Multi-Agent AI System
// Features: Chat UI, agent selection, conversation history, WebSocket support, error handling, responsive design

const API_BASE = 'http://localhost:5000';

// DOM Elements
const chatContainer = document.getElementById('chat-container');
const messageList = document.getElementById('message-list');
const inputForm = document.getElementById('input-form');
const userInput = document.getElementById('user-input');
const agentSelect = document.getElementById('agent-select');
const statusBar = document.getElementById('status-bar');

// State
let conversation = [];
let ws;

// Initialize WebSocket for real-time updates
function initWebSocket() {
    ws = new WebSocket('ws://localhost:5000/ws');
    ws.onopen = () => setStatus('Connected');
    ws.onclose = () => setStatus('Disconnected');
    ws.onerror = () => setStatus('WebSocket Error');
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        addMessage(data, 'agent');
    };
}

// Set status bar
function setStatus(msg) {
    statusBar.textContent = msg;
}

// Add message to chat
function addMessage(msg, sender) {
    const li = document.createElement('li');
    li.className = sender;
    li.textContent = `${sender === 'user' ? 'You' : msg.agent || 'Agent'}: ${msg.data || msg.text || msg.error || msg}`;
    messageList.appendChild(li);
    messageList.scrollTop = messageList.scrollHeight;
}

// Send message to backend
async function sendMessage(text, agent) {
    addMessage({ text }, 'user');
    try {
        const res = await fetch(`${API_BASE}/tools/${agent}/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: 'suggest_advice', params: { symptom: text } })
        });
        const data = await res.json();
        addMessage(data, 'agent');
    } catch (e) {
        addMessage({ error: 'API error. Please try again.' }, 'agent');
    }
}

// Handle form submit
inputForm.onsubmit = (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    const agent = agentSelect.value;
    if (!text) return;
    sendMessage(text, agent);
    userInput.value = '';
};

// Populate agent select
async function loadAgents() {
    // For demo, hardcoded. In production, fetch from /health or /agents endpoint
    const agents = [
        { value: 'healthcare_agent', label: 'Healthcare' },
        { value: 'fitness_agent', label: 'Fitness' },
        { value: 'education_agent', label: 'Education' },
        { value: 'finance_agent', label: 'Finance' },
        { value: 'law_agent', label: 'Law' },
        { value: 'travel_agent', label: 'Travel' }
    ];
    agents.forEach(a => {
        const opt = document.createElement('option');
        opt.value = a.value;
        opt.textContent = a.label;
        agentSelect.appendChild(opt);
    });
}

// Responsive design
window.onload = () => {
    loadAgents();
    initWebSocket();
    setStatus('Ready');
};

// Export for testing
window._chat = { sendMessage, addMessage, setStatus, loadAgents };
