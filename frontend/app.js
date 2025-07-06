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
const agentSelect = document.getElementById('agent-select');

// State
let conversation = [];
let selectedAgent = null;

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
        // If the response is wrapped (like {success, data, ...})
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

// Load available agents
async function loadAgents() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const health = await response.json();
        
        // Clear existing options
        agentSelect.innerHTML = '<option value="">Auto-select agent</option>';
        
        // Add agent options based on health check
        if (health.components) {
            Object.keys(health.components).forEach(agentName => {
                if (agentName.endsWith('_agent') && health.components[agentName].status === 'healthy') {
                    const option = document.createElement('option');
                    option.value = agentName;
                    option.textContent = agentName.replace('_agent', ' ').replace(/\b\w/g, l => l.toUpperCase());
                    agentSelect.appendChild(option);
                }
            });
        }
    } catch (error) {
        console.error('Failed to load agents:', error);
    }
}

// Send message to backend using /main_query endpoint
async function sendMessage(text) {
    addMessage({ text }, 'user');
    setStatus('Sending message...');
    
    try {
        const requestBody = { query: text };
        
        // If specific agent is selected, use the enhanced pipeline
        if (selectedAgent) {
            const response = await fetch(`${API_BASE}/ask`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    user_query: text,
                    topic: selectedAgent
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            addMessage(data, 'agent');
        } else {
            // Use main_query endpoint for auto-routing
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
        }
        
        setStatus('Ready');
    } catch (error) {
        console.error('API error:', error);
        const errorMsg = `API error: ${error.message}. Please try again.`;
        addMessage({ error: errorMsg }, 'agent');
        setStatus('Error occurred');
    }
}

// Handle agent selection
agentSelect.addEventListener('change', (e) => {
    selectedAgent = e.target.value || null;
    if (selectedAgent) {
        setStatus(`Selected agent: ${selectedAgent}`);
    } else {
        setStatus('Auto-selecting agent');
    }
});

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
    setStatus('Loading agents...');
    await loadAgents();
    setStatus('Ready');
};

// Export for testing
window._chat = { sendMessage, addMessage, setStatus, loadAgents };
