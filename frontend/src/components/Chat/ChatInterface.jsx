import React, { useState, useRef, useEffect } from 'react';
import MessageDisplay from './MessageDisplay';
import { sendChatMessage } from '../../services/api';

/**
 * Main ChatInterface component
 * Handles user input, message history, and communication with the AI backend
 */
const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
    };

    // Prepare updated history to include the just-typed message
    const updatedHistory = [...messages, userMessage];

    // Add user message to chat UI
    setMessages(updatedHistory);
    setInputValue('');
    setError(null);
    setIsLoading(true);

    try {
      // Send to backend with latest history
      const response = await sendChatMessage(userMessage.content, updatedHistory);

      // Add AI response to chat
      const aiMessage = {
        role: 'assistant',
        content: response.content,
        formatType: response.format_type,
        metadata: response.metadata,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to get response. Please try again.');
      
      // Add error message to chat
      const errorMessage = {
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please try again.',
        formatType: 'error',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleClearChat = () => {
    if (window.confirm('Clear all messages?')) {
      setMessages([]);
      setError(null);
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>AI Chat Assistant</h2>
        <button 
          onClick={handleClearChat}
          className="btn-clear"
          disabled={messages.length === 0}
        >
          Clear Chat
        </button>
      </div>

      {error && (
        <div className="chat-error">
          <span className="error-icon">??</span>
          {error}
        </div>
      )}

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty-state">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" className="empty-icon">
              <path 
                d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              />
            </svg>
            <h3>Start a conversation</h3>
            <p>Ask me anything! I can help with:</p>
            <ul>
              <li>Technical questions and code examples</li>
              <li>General knowledge and explanations</li>
              <li>Problem-solving and brainstorming</li>
            </ul>
          </div>
        ) : (
          messages.map((msg, index) => (
            <MessageDisplay
              key={index}
              message={msg.content}
              isUser={msg.role === 'user'}
              formatType={msg.formatType}
              timestamp={msg.timestamp}
            />
          ))
        )}
        
        {isLoading && (
          <div className="message-container message-assistant loading">
            <div className="loading-indicator">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message... (Shift+Enter for new line)"
          className="chat-input"
          rows={1}
          disabled={isLoading}
        />
        <button
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || isLoading}
          className="btn-send"
        >
          {isLoading ? (
            <span className="loading-spinner" />
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path 
                d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              />
          )}
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
