import React from 'react';
import './InteractionTimeline.css';

const getSentimentEmoji = (sentiment) => {
  switch (sentiment) {
    case 'positive': return '😊';
    case 'negative': return '😟';
    default: return '😐';
  }
};

const getTypeIcon = (type) => {
  switch (type) {
    case 'in-person': return '🤝';
    case 'phone': return '📞';
    case 'email': return '✉️';
    case 'video': return '💻';
    case 'conference': return '🎤';
    default: return '📝';
  }
};

const InteractionTimeline = ({ interactions }) => {
  if (!interactions || interactions.length === 0) {
    return <div className="empty-state">No interactions found.</div>;
  }

  return (
    <div className="timeline-container">
      {interactions.map((interaction, index) => (
        <div key={interaction.id || index} className="timeline-item">
          <div className="timeline-marker">
            <span className="type-icon">{getTypeIcon(interaction.interaction_type)}</span>
          </div>
          
          <div className="timeline-content">
            <div className="timeline-header">
              <span className="timeline-date">
                {new Date(interaction.interaction_date).toLocaleDateString('en-US', {
                  month: 'short', day: 'numeric', year: 'numeric'
                })}
              </span>
              <span className={`sentiment-badge ${interaction.sentiment}`}>
                {getSentimentEmoji(interaction.sentiment)} {interaction.sentiment}
              </span>
            </div>
            
            <h4 className="timeline-title">
              {interaction.interaction_type.charAt(0).toUpperCase() + interaction.interaction_type.slice(1)} Interaction
              {interaction.doctor_name ? ` with Dr. ${interaction.doctor_name}` : ''}
            </h4>
            
            {interaction.products_discussed && interaction.products_discussed.length > 0 && (
              <div className="products-list">
                {interaction.products_discussed.map((prod, i) => (
                  <span key={i} className="product-tag">{prod}</span>
                ))}
              </div>
            )}
            
            <p className="timeline-notes">
              {interaction.ai_summary || interaction.raw_notes || "No notes provided."}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default InteractionTimeline;
