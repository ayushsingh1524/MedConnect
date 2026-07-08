import React from 'react';
import { Link } from 'react-router-dom';
import './DoctorCard.css';

const DoctorCard = ({ doctor }) => {
  if (!doctor) return null;

  return (
    <div className="doctor-card">
      <div className="doctor-card-header">
        <div className="doctor-avatar">
          {doctor.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()}
        </div>
        <div className="doctor-info-basic">
          <h3 className="doctor-name">{doctor.name}</h3>
          <span className="doctor-specialty">{doctor.specialty}</span>
        </div>
      </div>
      
      <div className="doctor-card-body">
        <div className="info-row">
          <span className="icon">🏥</span>
          <span className="text">{doctor.hospital}</span>
        </div>
        <div className="info-row">
          <span className="icon">📍</span>
          <span className="text">{doctor.city}</span>
        </div>
      </div>
      
      <div className="doctor-card-footer">
        <Link to={`/hcps/${doctor.id}`} className="view-profile-btn">
          View Profile
        </Link>
        <button className="action-btn icon-btn" title="Log Interaction">
          <span className="icon">✏️</span>
        </button>
      </div>
    </div>
  );
};

export default DoctorCard;
