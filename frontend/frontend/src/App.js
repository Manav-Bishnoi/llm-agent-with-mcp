import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function ChatApp() {
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [status, setStatus] = useState('Ready');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);
    
    const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';
    
    // Auto-scroll to bottom
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };
    
    useEffect(() => {
        scrollToBottom();
    }, [messages]);
    
    // Add message to chat
    const addMessage = (content, sender) => {
        let displayText = '';
        if (typeof content === 'string') {
            displayText = content;
        } else if (content && typeof content === 'object') {
            if (content.data && typeof content.data === 'object' && content.data.data) {
                displayText = content.data.data;
            } else if (content.data && typeof content.data === 'string') {
                displayText = content.data;
            } else if (content.response && typeof content.response === 'object' && content.response.data) {
                displayText = content.response.data;
            } else if (content.error) {
                displayText = `Error: ${content.error}`;
            } else {
                displayText = JSON.stringify(content, null, 2);
            }
        }
        
        const newMessage = {
            id: Date.now() + Math.random(),
            text: displayText,
            sender: sender,
            timestamp: new Date().toLocaleTimeString()
        };
        
        setMessages(prev => [...prev, newMessage]);
    };
    
    // Send message to backend
    const sendMessage = async (text) => {
        if (!text.trim()) return;
        
        setIsLoading(true);
        setInputText('');
        
        // Add user message
        addMessage(text, 'user');
        setStatus('Sending message...');
        
        // Add checkpoint 1
        // addMessage('🔄 CHECKPOINT 1: Starting API request...', 'agent');
        
        try {
            const requestBody = { query: text };
            setStatus('responding...');
            
            // Add checkpoint 2
            // addMessage('📤 CHECKPOINT 2: Request body prepared', 'agent');
            
            const response = await fetch(`${API_BASE}/main_query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });
            
            // Add checkpoint 3
            // addMessage(`📥 CHECKPOINT 3: Response received (Status: ${response.status})`, 'agent');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            // Add checkpoint 4
            // addMessage('🔍 CHECKPOINT 4: Parsing JSON response...', 'agent');
            
            const data = await response.json();
            
            // Add checkpoint 5
            // addMessage('📋 CHECKPOINT 5: Response data received', 'agent');
            
            // Add checkpoint 6
            // addMessage('💬 CHECKPOINT 6: Processing agent response...', 'agent');
            
            addMessage(data, 'agent');
            
            // Add checkpoint 7
            // addMessage('✅ CHECKPOINT 7: Request completed successfully!', 'agent');
            setStatus('Ready');
            
        } catch (error) {
            console.error('API error:', error);
            
            // Add error checkpoint
            addMessage('❌ CHECKPOINT ERROR: API request failed', 'agent');
            addMessage(`📍 Error details: ${error.message}`, 'agent');
            
            const errorMsg = `API error: ${error.message}. Please try again.`;
            addMessage({ error: errorMsg }, 'agent');
            setStatus('Error occurred');
        } finally {
            setIsLoading(false);
        }
    };
    
    // Handle form submission
    const handleSubmit = (e) => {
        e.preventDefault();
        if (inputText.trim() && !isLoading) {
            sendMessage(inputText);
        }
    };
    
    // Handle Enter key
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (inputText.trim() && !isLoading) {
                sendMessage(inputText);
            }
        }
    };
    
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
            {/* Header */}
            <header className="bg-white shadow-lg border-b border-gray-200">
                <div className="max-w-4xl mx-auto px-4 py-6">
                    <h1 className="text-3xl font-bold text-gray-800 text-center">
                        Multi-Agent AI Chat
                    </h1>
                    <div className="text-center mt-2">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                            status === 'Ready' ? 'bg-green-100 text-green-800' :
                            status === 'Error occurred' ? 'bg-red-100 text-red-800' :
                            'bg-blue-100 text-blue-800'
                        }`}>
                            {status}
                        </span>
                    </div>
                </div>
            </header>
            
            {/* Chat Container */}
            <div className="flex-1 max-w-4xl mx-auto w-full px-4 py-6">
                <div className="bg-white rounded-lg shadow-xl h-[600px] flex flex-col">
                    {/* Messages Area */}
                    <div className="flex-1 overflow-y-auto p-6 space-y-4">
                        {messages.length === 0 ? (
                            <div className="text-center text-gray-500 mt-8">
                                <div className="text-6xl mb-4">💬</div>
                                <p className="text-lg">Start a conversation with the AI agent</p>
                                <p className="text-sm mt-2">Ask about health, finance, education, or any topic!</p>
                            </div>
                        ) : (
                            messages.map((message) => (
                                <div
                                    key={message.id}
                                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-[80%] rounded-lg px-4 py-3 shadow-sm ${
                                            message.sender === 'user'
                                                ? 'bg-blue-500 text-white'
                                                : 'bg-gray-100 text-gray-800'
                                        }`}
                                    >
                                        <div className="text-sm font-medium mb-1">
                                            {message.sender === 'user' ? 'You' : 'Agent'}
                                        </div>
                                        <div className="whitespace-pre-wrap break-words">
                                            {message.text}
                                        </div>
                                        <div className={`text-xs mt-2 ${
                                            message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                                        }`}>
                                            {message.timestamp}
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                    
                    {/* Input Area */}
                    <div className="border-t border-gray-200 p-4">
                        <form onSubmit={handleSubmit} className="flex space-x-3">
                            <input
                                type="text"
                                value={inputText}
                                onChange={(e) => setInputText(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Type your message..."
                                disabled={isLoading}
                                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                            />
                            <button
                                type="submit"
                                disabled={isLoading || !inputText.trim()}
                                className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-200"
                            >
                                {isLoading ? (
                                    <div className="flex items-center space-x-2">
                                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                        <span>Sending...</span>
                                    </div>
                                ) : (
                                    'Send'
                                )}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ChatApp;
