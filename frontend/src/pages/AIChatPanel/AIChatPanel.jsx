import React, { useState, useEffect } from 'react';
import ChatWindow from '../../components/ChatWindow/ChatWindow';
import { useToast } from '../../components/Toast/ToastContext';
import './AIChatPanel.css';

const AIChatPanel = () => {
  const [formData, setFormData] = useState({
    doctorId: '',
    type: 'in-person',
    date: new Date().toISOString().split('T')[0],
    time: new Date().toTimeString().split(' ')[0].substring(0,5),
    notes: '',
    sentiment: '',
    outcomes: '',
    followUpActions: '',
    products: ''
  });
  
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);
  
  // Chat State
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  const { showToast } = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const docsRes = await fetch('/api/v1/hcps');
        if (docsRes.ok) {
          const docsData = await docsRes.json();
          setDoctors(docsData.doctors || docsData);
        }
      } catch (err) {
        console.error(err);
        showToast('Failed to load data', 'error');
      } finally {
        setPageLoading(false);
      }
    };
    
    fetchData();
  }, [showToast]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.doctorId) {
      showToast('Please select a healthcare professional', 'error');
      return;
    }
    
    setLoading(true);
    try {
      let combinedNotes = formData.notes;
      if (formData.outcomes) combinedNotes += `\n\nOutcomes: ${formData.outcomes}`;
      if (formData.followUpActions) combinedNotes += `\n\nFollow-up Actions: ${formData.followUpActions}`;
      
      const payload = {
        doctor_id: formData.doctorId,
        interaction_type: formData.type,
        interaction_date: new Date(`${formData.date}T${formData.time}`).toISOString(),
        raw_notes: combinedNotes,
        sentiment: formData.sentiment || 'neutral',
        products_discussed: formData.products ? formData.products.split(',').map(p => p.trim()) : []
      };
      
      const res = await fetch('/api/v1/interactions/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (res.ok) {
        showToast('Interaction logged successfully!', 'success');
        // reset form
        setFormData({
          ...formData,
          doctorId: '',
          notes: '',
          sentiment: '',
          outcomes: '',
          followUpActions: '',
          products: '',
          time: new Date().toTimeString().split(' ')[0].substring(0,5)
        });
      } else {
        const err = await res.json();
        showToast(err.detail || 'Failed to log interaction', 'error');
      }
    } catch(err) {
      console.error(err);
      showToast('Network error occurred', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSendMessage = async (text) => {
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);

    let systemParts = [];
    let responseParts = [];
    let structuredData = null;

    const updateAssistantMessage = () => {
      const content = [...systemParts, ...responseParts].join('');
      setMessages(prev => {
        const newMessages = [...prev];
        const lastIdx = newMessages.length - 1;
        if (lastIdx >= 0 && newMessages[lastIdx].role === 'assistant') {
          newMessages[lastIdx] = { role: 'assistant', content, data: structuredData };
        } else {
          newMessages.push({ role: 'assistant', content, data: structuredData });
        }
        return newMessages;
      });
    };

    setMessages(prev => [...prev, { role: 'assistant', content: '', data: null }]);

    try {
      // Append instructions to the LLM to use dry_run to fill the form without saving
      const requestText = text + "\n(Note: I am on the manual Log Interaction page. Please set dry_run=true when calling log_interaction so I can review it before saving.)";
      
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: requestText })
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
        buffer = lines.pop() || '';
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            try {
              const eventObj = JSON.parse(dataStr);

              if (eventObj.event === 'token') {
                responseParts.push(eventObj.data);
                updateAssistantMessage();

              } else if (eventObj.event === 'tool_start') {
                systemParts.push(`\n🔧 Calling ${eventObj.data.name}...\n`);
                updateAssistantMessage();
                
                // AUTO-FILL THE FORM!
                if (eventObj.data.name === 'log_interaction' && eventObj.data.args) {
                  const args = eventObj.data.args;
                  setFormData(prev => ({
                    ...prev,
                    doctorId: args.doctor_id || prev.doctorId,
                    type: args.interaction_type || prev.type,
                    date: args.interaction_date || prev.date,
                    notes: args.raw_notes || prev.notes,
                    sentiment: args.sentiment || prev.sentiment,
                    outcomes: args.outcomes || prev.outcomes,
                    followUpActions: args.follow_up_actions || prev.followUpActions,
                    products: (args.products_discussed && args.products_discussed.length > 0) ? args.products_discussed.join(', ') : prev.products
                  }));
                  showToast("Form auto-filled by AI Assistant!", "success");
                }

              } else if (eventObj.event === 'tool_end') {
                systemParts.push(`✅ ${eventObj.data.name} completed.\n\n`);
                updateAssistantMessage();

              } else if (eventObj.event === 'final_json') {
                structuredData = eventObj.data;
                updateAssistantMessage();

              } else if (eventObj.event === 'error') {
                responseParts.push(`\n⚠️ Error: ${eventObj.data}`);
                updateAssistantMessage();
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
    <div className="log-interaction-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Log HCP Interaction</h1>
          <p className="page-subtitle">Log new visits manually or use the AI Assistant to extract details automatically.</p>
        </div>
      </div>

      <div className="interaction-content-grid">
        <div className="form-column">
          <div className="form-card">
            <h2>Interaction Details</h2>
            <form onSubmit={handleSubmit} className="interaction-form">
              
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="doctorId">HCP Name</label>
                  <select 
                    id="doctorId" 
                    name="doctorId" 
                    value={formData.doctorId} 
                    onChange={handleChange}
                    required
                  >
                    <option value="" disabled>Search or select HCP...</option>
                    {doctors.map(doc => (
                      <option key={doc.id} value={doc.id}>
                        {doc.name} ({doc.specialty})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="type">Interaction Type</label>
                  <select 
                    id="type" 
                    name="type" 
                    value={formData.type} 
                    onChange={handleChange}
                  >
                    <option value="in-person">In-Person Visit</option>
                    <option value="video">Video Call</option>
                    <option value="phone">Phone Call</option>
                    <option value="email">Email</option>
                    <option value="conference">Conference / Event</option>
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="date">Date</label>
                  <input 
                    type="date" 
                    id="date" 
                    name="date" 
                    value={formData.date} 
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="time">Time</label>
                  <input 
                    type="time" 
                    id="time" 
                    name="time" 
                    value={formData.time} 
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="notes">Topics Discussed (Extracted automatically)</label>
                <textarea 
                  id="notes" 
                  name="notes" 
                  rows="4" 
                  placeholder="Enter key discussion points or use the AI Assistant..."
                  value={formData.notes}
                  onChange={handleChange}
                  required
                ></textarea>
                <button type="button" className="text-btn voice-btn">
                  🎙️ Summarize from Voice Note (Requires Consent)
                </button>
              </div>

              <div className="form-section-divider"></div>
              
              <h3>Materials Shared / Samples Distributed</h3>
              
              <div className="form-group">
                <label htmlFor="products">Materials Shared / Products Discussed</label>
                <div className="flex-row">
                  <input 
                    type="text" 
                    id="products"
                    name="products"
                    placeholder="Enter products (comma separated)" 
                    className="flex-1"
                    value={formData.products}
                    onChange={handleChange}
                  />
                  <button type="button" className="secondary-btn">🔍 Search/Add</button>
                </div>
              </div>

              <div className="form-group">
                <label>Samples Distributed</label>
                <div className="flex-row">
                  <input type="text" placeholder="No samples added." readOnly className="flex-1" />
                  <button type="button" className="secondary-btn">➕ Add Sample</button>
                </div>
              </div>

              <div className="form-section-divider"></div>

              <div className="form-group">
                <label>Observed/Inferred HCP Sentiment</label>
                <div className="radio-group">
                  <label className="radio-label">
                    <input 
                      type="radio" 
                      name="sentiment" 
                      value="positive" 
                      checked={formData.sentiment === 'positive'} 
                      onChange={handleChange} 
                    />
                    <span>😀 Positive</span>
                  </label>
                  <label className="radio-label">
                    <input 
                      type="radio" 
                      name="sentiment" 
                      value="neutral" 
                      checked={formData.sentiment === 'neutral'} 
                      onChange={handleChange} 
                    />
                    <span>😐 Neutral</span>
                  </label>
                  <label className="radio-label">
                    <input 
                      type="radio" 
                      name="sentiment" 
                      value="negative" 
                      checked={formData.sentiment === 'negative'} 
                      onChange={handleChange} 
                    />
                    <span>😟 Negative</span>
                  </label>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="outcomes">Outcomes</label>
                <textarea 
                  id="outcomes" 
                  name="outcomes" 
                  rows="3" 
                  placeholder="Key outcomes or agreements..."
                  value={formData.outcomes}
                  onChange={handleChange}
                ></textarea>
              </div>

              <div className="form-group">
                <label htmlFor="followUpActions">Follow-up Actions</label>
                <textarea 
                  id="followUpActions" 
                  name="followUpActions" 
                  rows="2" 
                  placeholder="Any required follow-ups..."
                  value={formData.followUpActions}
                  onChange={handleChange}
                ></textarea>
              </div>

              <div className="form-actions">
                <button type="button" className="secondary-btn" onClick={() => setFormData({...formData, doctorId: '', notes: '', sentiment: '', outcomes: '', followUpActions: ''})}>Clear Form</button>
                <button type="submit" className="primary-btn" disabled={loading}>
                  {loading ? (
                    <span className="spinner"></span>
                  ) : (
                    "Save Interaction"
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* AI Assistant on the right */}
        <div className="chat-column">
          <div className="chat-section" style={{ height: '100%', minHeight: '600px' }}>
            <ChatWindow 
              messages={messages} 
              isTyping={isTyping} 
              onSendMessage={handleSendMessage} 
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIChatPanel;
