import React from 'react';
import MarkdownRenderer from '../Markdown/MarkdownRenderer';

/**
 * MessageDisplay component for rendering individual chat messages
 * Supports different message types and formatting
 */
const MessageDisplay = ({ 
  message, 
  isUser = false, 
  formatType = 'balanced',
  timestamp,
  className = ''
}) => {
  const messageClass = isUser ? 'message-user' : 'message-assistant';
  const formatClass = `format-${formatType}`;

  return (
    <div className={`message-container ${messageClass} ${formatClass} ${className}`}>
      <div className="message-header">
        <div className="message-avatar">
          {isUser ? (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="8" r="4" fill="currentColor" />
              <path 
                d="M4 20c0-3.314 3.134-6 7-6h2c3.866 0 7 2.686 7 6v1H4v-1z" 
                fill="currentColor"
              />
            </svg>
          ) : (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path 
                d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              />
            </svg>
          )}
        </div>
        <div className="message-meta">
          <span className="message-sender">
            {isUser ? 'You' : 'AI Assistant'}
          </span>
          {timestamp && (
            <span className="message-timestamp">
              {new Date(timestamp).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </span>
          )}
          {!isUser && formatType && (
            <span className="message-format-badge" title={`Format: ${formatType}`}>
              {formatType}
            </span>
          )}
        </div>
      </div>
      
      <div className="message-content">
        {isUser ? (
          <p className="user-message-text">{message}</p>
        ) : (
          <MarkdownRenderer content={message} />
        )}
      </div>
    </div>
  );
};

export default MessageDisplay;
