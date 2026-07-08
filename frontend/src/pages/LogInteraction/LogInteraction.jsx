import React, { useState, useEffect } from 'react';
import HistoryTable from '../../components/HistoryTable/HistoryTable';
import { useToast } from '../../components/Toast/ToastContext';
import './LogInteraction.css';

const LogInteraction = () => {
  const [formData, setFormData] = useState({
    doctorId: '',
    type: 'in-person',
    date: new Date().toISOString().split('T')[0],
    notes: ''
  });
  
  const [doctors, setDoctors] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);
  
  const { showToast } = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [docsRes, histRes] = await Promise.all([
          fetch('/api/v1/hcps'),
          fetch('/api/v1/interactions?limit=10')
        ]);
        
        if (docsRes.ok) {
          const docsData = await docsRes.json();
          setDoctors(docsData.doctors || docsData);
        }
        if (histRes.ok) {
          const histData = await histRes.json();
          setHistory(histData.interactions || histData);
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
      const payload = {
        doctor_id: parseInt(formData.doctorId, 10),
        interaction_type: formData.type,
        interaction_date: formData.date,
        notes: formData.notes
      };
      
      const res = await fetch('/api/v1/interactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (res.ok) {
        const newInteraction = await res.json();
        showToast('Interaction logged successfully! AI has generated a summary.', 'success');
        setHistory([newInteraction, ...history].slice(0, 10)); // keep top 10
        // reset form
        setFormData({
          ...formData,
          doctorId: '',
          notes: ''
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

  return (
    <div className="log-interaction-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Interactions</h1>
          <p className="page-subtitle">Log new visits and review interaction history.</p>
        </div>
      </div>

      <div className="interaction-content-grid">
        <div className="form-column">
          <div className="form-card">
            <h2>Log New Interaction</h2>
            <form onSubmit={handleSubmit} className="interaction-form">
              
              <div className="form-group">
                <label htmlFor="doctorId">Healthcare Professional</label>
                <select 
                  id="doctorId" 
                  name="doctorId" 
                  value={formData.doctorId} 
                  onChange={handleChange}
                  required
                >
                  <option value="" disabled>Select HCP...</option>
                  {doctors.map(doc => (
                    <option key={doc.id} value={doc.id}>
                      Dr. {doc.name} ({doc.specialty})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-row">
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
              </div>

              <div className="form-group">
                <label htmlFor="notes">Meeting Notes (AI will analyze this)</label>
                <textarea 
                  id="notes" 
                  name="notes" 
                  rows="6" 
                  placeholder="Summarize the discussion, products mentioned, sentiment, and any follow-up actions required..."
                  value={formData.notes}
                  onChange={handleChange}
                  required
                ></textarea>
              </div>

              <div className="form-actions">
                <button type="button" className="secondary-btn" onClick={() => setFormData({...formData, doctorId: '', notes: ''})}>Cancel</button>
                <button type="submit" className="primary-btn" disabled={loading}>
                  {loading ? (
                    <span className="spinner"></span>
                  ) : (
                    "Save & Analyze"
                  )}
                </button>
              </div>
            </form>
          </div>
          
          <div className="ai-tip-card">
            <span className="ai-icon">✨</span>
            <div className="tip-content">
              <h4>Pro Tip</h4>
              <p>You can also use the AI Assistant in the sidebar to log interactions conversationally! Just type or dictate your notes.</p>
            </div>
          </div>
        </div>

        <div className="history-column">
          <div className="section-header">
            <h2>Recent History</h2>
          </div>
          {pageLoading ? (
            <div className="skeleton" style={{height: '400px', width: '100%', borderRadius: 'var(--border-radius-lg)'}}></div>
          ) : history.length > 0 ? (
            <HistoryTable interactions={history} />
          ) : (
            <div className="empty-state">
              <span className="empty-icon">📝</span>
              <h3>No interactions yet</h3>
              <p>Your logged interactions will appear here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LogInteraction;
