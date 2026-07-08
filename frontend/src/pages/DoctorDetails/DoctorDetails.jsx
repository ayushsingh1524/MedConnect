import React, { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { fetchHCPById, clearCurrentHCP } from '../../store/slices/hcpSlice';
import InteractionTimeline from '../../components/InteractionTimeline/InteractionTimeline';
import RecommendationPanel from '../../components/RecommendationPanel/RecommendationPanel';
import './DoctorDetails.css';

// Mock data
const MOCK_DOCTOR = {
  id: '1',
  name: 'Sarah Jenkins',
  specialty: 'Cardiology',
  hospital: 'Mercy General',
  city: 'San Francisco',
  email: 's.jenkins@mercy.org',
  phone: '(555) 123-4567',
  status: 'High Priority'
};

const MOCK_RECOMMENDATIONS = [
  {
    id: '1',
    title: 'Discuss CardioMax Trial Data',
    description: 'Dr. Jenkins has shown high interest in recent vascular trials. Present the Q3 CardioMax outcomes to address her previous concerns regarding efficacy in elderly patients.',
    metadata_data: { confidence_score: 0.92 }
  },
  {
    id: '2',
    title: 'Invite to Upcoming Symposium',
    description: 'There is a regional cardiology symposium next month. She attended last year and provided positive feedback.',
    metadata_data: { confidence_score: 0.78 }
  }
];

const MOCK_TIMELINE = [
  {
    id: '1',
    interaction_type: 'in-person',
    interaction_date: new Date().toISOString(),
    sentiment: 'positive',
    products_discussed: ['CardioMax'],
    ai_summary: 'Great lunch meeting. She is very interested in the new efficacy data and asked for sample packs.'
  }
];

const DoctorDetails = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const { currentHCP: doctor, loading, error } = useSelector((state) => state.hcps);

  useEffect(() => {
    dispatch(fetchHCPById(id));
    return () => dispatch(clearCurrentHCP());
  }, [dispatch, id]);

  if (loading) return <div className="doctor-details-page"><div className="skeleton" style={{height: '200px'}}></div></div>;
  if (error || !doctor) return <div className="doctor-details-page">Error loading HCP details.</div>;

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
            <span className="priority-tag">{doctor.status}</span>
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
          <button className="primary-btn">Log Interaction</button>
          <button className="secondary-btn">Schedule Task</button>
        </div>
      </div>

      <div className="details-content-grid">
        <div className="details-main-col">
          <div className="section-header">
            <h2>Interaction History</h2>
          </div>
          <div className="card-container timeline-container-large">
            <InteractionTimeline interactions={MOCK_TIMELINE} />
          </div>
        </div>
        
        <div className="details-side-col">
          <RecommendationPanel recommendations={MOCK_RECOMMENDATIONS} />
          
          <div className="quick-stats-card">
            <h3>HCP Stats</h3>
            <div className="stat-row">
              <span>YTD Visits</span>
              <strong>12</strong>
            </div>
            <div className="stat-row">
              <span>Preferred Channel</span>
              <strong>In-person</strong>
            </div>
            <div className="stat-row">
              <span>Average Sentiment</span>
              <strong>Positive</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DoctorDetails;
