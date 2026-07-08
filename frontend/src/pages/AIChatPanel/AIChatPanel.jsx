import React, { useState } from 'react';
import ChatWindow from '../../components/ChatWindow/ChatWindow';
import './AIChatPanel.css';

const AIChatPanel = () => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  const handleSendMessage = async (text) => {
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMsg = { role: 'assistant', content: '', data: null };

      setMessages(prev => [...prev, assistantMsg]);

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '');
            try {
              const eventObj = JSON.parse(dataStr);
              if (eventObj.event === 'token') {
                assistantMsg.content += eventObj.data;
              } else if (eventObj.event === 'tool_start') {
                assistantMsg.content += `\n[System: Calling tool ${eventObj.data.name}...]\n`;
              } else if (eventObj.event === 'tool_end') {
                assistantMsg.content += `[System: Tool finished]\n`;
              } else if (eventObj.event === 'final_json') {
                assistantMsg.data = eventObj.data;
              } else if (eventObj.event === 'end') {
                break;
              }
              
              // Update state with new message content
              setMessages(prev => {
                const newMessages = [...prev];
                newMessages[newMessages.length - 1] = { ...assistantMsg };
                return newMessages;
              });
            } catch (e) {
              console.error('Error parsing SSE:', e, dataStr);
            }
          }
        }
      }
    } catch (err) {
      console.error('Chat error:', err);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error connecting to the server.' }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="ai-chat-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">AI Assistant</h1>
          <p className="page-subtitle">Your intelligent copilot for CRM data entry and insights.</p>
        </div>
      </div>
      
      <div className="ai-layout-container">
        <div className="chat-section">
          <ChatWindow 
            messages={messages} 
            isTyping={isTyping} 
            onSendMessage={handleSendMessage} 
          />
        </div>
        
        <div className="capabilities-section">
          <div className="capability-card">
            <div className="icon">🎤</div>
            <h3>Conversational Logging</h3>
            <p>Don't fill out forms. Just tell me how the meeting went, and I'll extract the products discussed, sentiment, and automatically schedule any follow-ups.</p>
            <div className="example-prompt">
              "I just met with Dr. Chen. He loves the new trial data for NeuroShield but wants a sample pack delivered next week."
            </div>
          </div>
          
          <div className="capability-card">
            <div className="icon">🧠</div>
            <h3>Strategic Insights</h3>
            <p>Ask me to analyze past interactions to suggest the best approach for your upcoming visits.</p>
            <div className="example-prompt">
              "What's the best way to pitch CardioMax to Dr. Jenkins based on our history?"
            </div>
          </div>

          <div className="capability-card">
            <div className="icon">📊</div>
            <h3>Data Retrieval</h3>
            <p>Quickly pull up territory stats or specific doctor information without navigating through menus.</p>
            <div className="example-prompt">
              "Who are the high priority cardiologists in San Francisco?"
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIChatPanel;
