import React from 'react';
import './HistoryTable.css';

const getSentimentColor = (sentiment) => {
  switch (sentiment) {
    case 'positive': return 'sentiment-pos';
    case 'negative': return 'sentiment-neg';
    default: return 'sentiment-neu';
  }
};

const HistoryTable = ({ interactions }) => {
  if (!interactions || interactions.length === 0) {
    return <div className="table-empty">No interaction history found.</div>;
  }

  return (
    <div className="table-container">
      <table className="history-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Doctor</th>
            <th>Products Discussed</th>
            <th>Sentiment</th>
            <th>Notes Summary</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {interactions.map((interaction, index) => (
            <tr key={interaction.id || index}>
              <td className="col-date">
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span>{new Date(interaction.interaction_date).toLocaleDateString('en-US')}</span>
                  <span style={{ fontSize: '0.85em', color: 'var(--gray-500)', marginTop: '2px' }}>
                    {new Date(interaction.interaction_date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </td>
              <td className="col-type">
                <span className="type-badge">{interaction.interaction_type}</span>
              </td>
              <td className="col-doctor">
                {interaction.doctor_name || 'Unknown'}
              </td>
              <td className="col-products">
                {interaction.products_discussed && interaction.products_discussed.length > 0
                  ? interaction.products_discussed.join(', ')
                  : '-'}
              </td>
              <td className="col-sentiment">
                <span className={`status-dot ${getSentimentColor(interaction.sentiment)}`}></span>
                {interaction.sentiment.charAt(0).toUpperCase() + interaction.sentiment.slice(1)}
              </td>
              <td className="col-notes">
                <div className="notes-truncate">
                  {interaction.ai_summary || interaction.raw_notes || '-'}
                </div>
              </td>
              <td className="col-status">
                <span className={`status-badge ${interaction.status}`}>
                  {interaction.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default HistoryTable;
