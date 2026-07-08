import React from 'react';
import './RecommendationPanel.css';

const RecommendationPanel = ({ recommendations }) => {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="recommendation-panel empty">
        <div className="sparkle-icon">✨</div>
        <p>No AI recommendations available for this HCP yet.</p>
        <button className="generate-btn">Generate Insights</button>
      </div>
    );
  }

  return (
    <div className="recommendation-panel">
      <div className="panel-header">
        <h3>✨ AI Strategic Insights</h3>
        <button className="refresh-btn">↻</button>
      </div>
      
      <div className="recommendations-list">
        {recommendations.map((rec, index) => (
          <div key={rec.id || index} className="recommendation-item">
            <div className="rec-confidence">
              {rec.metadata_data?.confidence_score ? 
                `${Math.round(rec.metadata_data.confidence_score * 100)}% Match` : 
                'High Priority'
              }
            </div>
            <h4 className="rec-title">{rec.title}</h4>
            <p className="rec-description">{rec.description}</p>
            
            <div className="rec-actions">
              <button className="rec-action-btn primary">Add to Plan</button>
              <button className="rec-action-btn secondary">Dismiss</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecommendationPanel;
