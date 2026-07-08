import React from 'react';
import './AnalyticsCard.css';

const AnalyticsCard = ({ title, value, icon, trend, trendDirection }) => {
  const isPositive = trendDirection === 'up';
  
  return (
    <div className="analytics-card">
      <div className="analytics-icon-wrapper">
        <span className="analytics-icon">{icon}</span>
      </div>
      
      <div className="analytics-content">
        <h3 className="analytics-title">{title}</h3>
        <div className="analytics-data">
          <span className="analytics-value">{value}</span>
          
          {trend && (
            <span className={`analytics-trend ${isPositive ? 'trend-up' : 'trend-down'}`}>
              {isPositive ? '↑' : '↓'} {trend}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsCard;
