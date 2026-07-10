import React, { useState, useEffect } from 'react';
import HistoryTable from '../../components/HistoryTable/HistoryTable';
import { useToast } from '../../components/Toast/ToastContext';
import './LogInteraction.css';

const LogInteraction = () => {
  const [history, setHistory] = useState([]);
  const [pageLoading, setPageLoading] = useState(true);
  
  const { showToast } = useToast();

  const fetchHistory = async () => {
    try {
      const histRes = await fetch('/api/v1/interactions/?limit=50');
      if (histRes.ok) {
        const histData = await histRes.json();
        setHistory(histData.interactions || histData);
      }
    } catch (err) {
      console.error('Failed to fetch history', err);
      showToast('Failed to load interactions history', 'error');
    } finally {
      setPageLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div className="log-interaction-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Recent Logged Interactions</h1>
          <p className="page-subtitle">View your past interactions with Healthcare Professionals.</p>
        </div>
      </div>

      <div className="history-section" style={{marginTop: '1rem'}}>
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
  );
};

export default LogInteraction;
