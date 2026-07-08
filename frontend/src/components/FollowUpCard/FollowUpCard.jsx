import React from 'react';
import './FollowUpCard.css';

const FollowUpCard = ({ followUp, onComplete }) => {
  if (!followUp) return null;

  const isUrgent = followUp.priority === 'urgent' || followUp.priority === 'high';
  const isOverdue = new Date(followUp.due_date) < new Date(new Date().setHours(0,0,0,0));

  return (
    <div className={`follow-up-card ${isUrgent ? 'urgent' : ''} ${isOverdue ? 'overdue' : ''}`}>
      <div className="follow-up-header">
        <div className="priority-badge">{followUp.priority.toUpperCase()}</div>
        <div className="due-date">
          {isOverdue && <span className="overdue-warning">⚠️</span>}
          {new Date(followUp.due_date).toLocaleDateString('en-US', { 
            month: 'short', day: 'numeric' 
          })}
        </div>
      </div>
      
      <div className="follow-up-body">
        <h4 className="doctor-name">Dr. {followUp.doctor_name || 'Unknown'}</h4>
        <p className="description">{followUp.description}</p>
      </div>
      
      <div className="follow-up-footer">
        <button 
          className="complete-btn" 
          onClick={() => onComplete && onComplete(followUp.id)}
        >
          <span className="icon">✓</span> Mark Done
        </button>
      </div>
    </div>
  );
};

export default FollowUpCard;
