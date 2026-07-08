import React, { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { fetchHCPById, clearCurrentHCP } from '../../store/slices/hcpSlice';
import InteractionTimeline from '../../components/InteractionTimeline/InteractionTimeline';
import RecommendationPanel from '../../components/RecommendationPanel/RecommendationPanel';
import './DoctorDetails.css';

const DoctorDetails = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const { currentHCP: profile, loading, error } = useSelector((state) => state.hcps);

  useEffect(() => {
    dispatch(fetchHCPById(id));
    return () => dispatch(clearCurrentHCP());
  }, [dispatch, id]);

  if (loading) return <div className="doctor-details-page"><div className="skeleton" style={{height: '200px'}}></div></div>;
  if (error || !profile) return <div className="doctor-details-page">Error loading HCP details.</div>;

  const doctor = profile.doctor;
  const interactions = profile.interactions || [];
  const recommendations = profile.recommendations || [];

  return (
    <div className="doctor-details-page">
      <div className="breadcrumb">
        <Link to="/hcps">← Back to Directory</Link>
      </div>

      <div className="profile-header-card">
        <div className="profile-avatar-large">
          {doctor.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()}
        </div>
        
        <div className="profile-info-main">
          <div className="profile-title-row">
            <h1 className="profile-name">Dr. {doctor.name}</h1>
            <span className="priority-tag">High Priority</span>
          </div>
          <p className="profile-specialty">{doctor.specialty}</p>
          
          <div className="profile-contact-details">
            <div className="contact-item">
              <span className="icon">🏥</span> {doctor.hospital}, {doctor.city}
            </div>
            <div className="contact-item">
              <span className="icon">✉️</span> {doctor.email}
            </div>
            <div className="contact-item">
              <span className="icon">📞</span> {doctor.phone}
            </div>
          </div>
        </div>
        
        <div className="profile-actions">
          <Link to="/interactions" className="primary-btn" style={{textDecoration: 'none'}}>Log Interaction</Link>
        </div>
      </div>

      <div className="details-content-grid">
        <div className="details-main-col">
          <div className="section-header">
            <h2>Interaction History</h2>
          </div>
          <div className="card-container timeline-container-large">
            {interactions.length > 0 ? (
              <InteractionTimeline interactions={interactions} />
            ) : (
              <div className="empty-state">
                <span className="empty-icon">🗓️</span>
                <h3>No interactions</h3>
                <p>Log a new interaction with Dr. {doctor.name} to see their timeline.</p>
              </div>
            )}
          </div>
        </div>
        
        <div className="details-side-col">
          <RecommendationPanel recommendations={recommendations} />
          
          <div className="quick-stats-card">
            <h3>HCP Stats</h3>
            <div className="stat-row">
              <span>YTD Visits</span>
              <strong>{interactions.length}</strong>
            </div>
            <div className="stat-row">
              <span>Preferred Channel</span>
              <strong>In-person</strong>
            </div>
            <div className="stat-row">
              <span>Status</span>
              <strong>Active</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DoctorDetails;
