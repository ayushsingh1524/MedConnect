import React, { useState, useRef, useEffect } from 'react';
import './ChatWindow.css';

const ChatWindow = ({ messages, isTyping, onSendMessage }) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="chat-title">
          <span className="ai-icon">✨</span>
          <h3>MedConnect Assistant</h3>
        </div>
        <button className="chat-minimize-btn">−</button>
      </div>
      
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <span className="chat-empty-icon">👋</span>
            <p>I'm your AI CRM Assistant.</p>
            <p className="chat-empty-sub">
              Try saying: "Log a meeting with Dr. Smith today where we discussed cardio products. Sentiment was positive."
            </p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`message-bubble ${msg.role}`}>
              {!msg.data && (
                <div className="message-content">
                  {msg.content}
                </div>
              )}
              {msg.data && (
                <div className="message-structured-data-card">
                  <div className={`status-indicator ${msg.data.status}`}>
                    {msg.data.status === 'success' ? '✅ Action Successful' : '⚠️ Action Needed'}
                  </div>
                  <div className="data-action">
                    <strong>Action:</strong> <span className="code-badge">{msg.data.action}</span>
                  </div>
                  {msg.data.message && msg.data.message !== "Interaction logged successfully" && (
                    <div className="data-suggestion">
                      {msg.data.message}
                    </div>
                  )}
                  {msg.data.follow_up_suggestion && (
                    <div className="data-suggestion">
                      <strong>Suggestion:</strong> {msg.data.follow_up_suggestion}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
        
        {isTyping && (
          <div className="message-bubble assistant typing">
            <span className="dot"></span>
            <span className="dot"></span>
            <span className="dot"></span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <form className="chat-input-area" onSubmit={handleSubmit}>
        <input 
          type="text" 
          className="chat-input" 
          placeholder="Ask me to log a visit or analyze history..." 
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={isTyping}
        />
        <button type="submit" className="chat-send-btn" disabled={!inputValue.trim() || isTyping}>
          <span className="icon">↑</span>
        </button>
      </form>
    </div>
  );
};

export default ChatWindow;
