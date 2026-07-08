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

    // We'll build the assistant message progressively
    let systemParts = [];   // Tool call system messages
    let responseParts = []; // AI text content
    let structuredData = null;

    const updateAssistantMessage = () => {
      const content = [
        ...systemParts,
        ...responseParts
      ].join('');

      setMessages(prev => {
        const newMessages = [...prev];
        // Find or create the assistant message
        const lastIdx = newMessages.length - 1;
        if (lastIdx >= 0 && newMessages[lastIdx].role === 'assistant') {
          newMessages[lastIdx] = { role: 'assistant', content, data: structuredData };
        } else {
          newMessages.push({ role: 'assistant', content, data: structuredData });
        }
        return newMessages;
      });
    };

    // Add an empty assistant message
    setMessages(prev => [...prev, { role: 'assistant', content: '', data: null }]);

    try {
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        // Keep the last potentially incomplete chunk in the buffer
        buffer = lines.pop() || '';
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6); // More reliable than replace
            try {
              const eventObj = JSON.parse(dataStr);

              if (eventObj.event === 'token') {
                responseParts.push(eventObj.data);
                updateAssistantMessage();

              } else if (eventObj.event === 'tool_start') {
                systemParts.push(`\n🔧 Calling ${eventObj.data.name}...\n`);
                updateAssistantMessage();

              } else if (eventObj.event === 'tool_end') {
                systemParts.push(`✅ ${eventObj.data.name} completed.\n\n`);
                // Clear system parts so the final response appears clean
                // but keep them visible briefly
                updateAssistantMessage();

              } else if (eventObj.event === 'final_json') {
                structuredData = eventObj.data;
                updateAssistantMessage();

              } else if (eventObj.event === 'error') {
                responseParts.push(`\n⚠️ Error: ${eventObj.data}`);
                updateAssistantMessage();

              } else if (eventObj.event === 'end') {
                // Stream complete
              }
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
