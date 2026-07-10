import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import AnalyticsCard from '../../components/AnalyticsCard/AnalyticsCard';
import InteractionTimeline from '../../components/InteractionTimeline/InteractionTimeline';
import FollowUpCard from '../../components/FollowUpCard/FollowUpCard';
import Modal from '../../components/Modal/Modal';
import { useToast } from '../../components/Toast/ToastContext';
import './Dashboard.css';

// Mock data until Redux integration
const MOCK_STATS = {
  total_doctors: 124,
  total_interactions: 856,
  pending_follow_ups: 12,
  positive_sentiment_pct: 78.5
};

const MOCK_TIMELINE = [
  {
    id: 1,
    doctor_name: 'Sarah Jenkins',
    interaction_type: 'in-person',
    interaction_date: new Date().toISOString(),
    sentiment: 'positive',
    products_discussed: ['CardioMax', 'VascularPlus'],
    ai_summary: 'Dr. Jenkins was very receptive to the new clinical data for CardioMax. She intends to start prescribing it for her high-risk patients.'
  },
  {
    id: 2,
    doctor_name: 'Michael Chen',
    interaction_type: 'email',
    interaction_date: new Date(Date.now() - 86400000).toISOString(),
    sentiment: 'neutral',
    products_discussed: ['NeuroShield'],
    ai_summary: 'Sent requested literature on NeuroShield drug interactions.'
  }
];

const MOCK_TASKS = [
  {
    id: 1,
    doctor_name: 'Robert Smith',
    due_date: new Date(Date.now() - 86400000).toISOString(), // overdue
    priority: 'high',
    description: 'Drop off requested samples for new diabetes medication.'
  },
  {
    id: 2,
    doctor_name: 'Emily Davis',
    due_date: new Date(Date.now() + 86400000).toISOString(),
    priority: 'medium',
    description: 'Follow up call regarding patient enrollment in phase 3 trial.'
  }
];


const Dashboard = () => {
  const [stats, setStats] = useState(MOCK_STATS);
  const [timeline, setTimeline] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [taskToComplete, setTaskToComplete] = useState(null);
  
  const { showToast } = useToast();

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await fetch('/api/v1/dashboard/summary');
        if (res.ok) {
          const data = await res.json();
          setStats(data.stats || MOCK_STATS);
          setTimeline(data.recent_interactions || MOCK_TIMELINE);
          setTasks(data.upcoming_follow_ups || MOCK_TASKS);
        }
      } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  const confirmCompleteTask = (id) => {
    setTaskToComplete(id);
  };

  const handleCompleteTask = async () => {
    if (!taskToComplete) return;
    try {
      const res = await fetch(`/api/v1/interactions/follow-ups/${taskToComplete}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'completed' })
      });
      if (res.ok) {
        setTasks(tasks.filter(t => t.id !== taskToComplete));
        showToast('Task marked as completed', 'success');
      } else {
        showToast('Failed to complete task', 'error');
      }
    } catch(err) {
      console.error(err);
      showToast('Network error occurred', 'error');
    } finally {
      setTaskToComplete(null);
    }
  };

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Overview</h1>
          <p className="page-subtitle">Welcome back, Sarah. Here's what's happening today.</p>
        </div>
        <Link to="/chat" className="primary-btn">
          <span className="icon">+</span> Log Interaction
        </Link>
      </div>

      <div className="analytics-grid">
        <AnalyticsCard 
          title="Total HCPs in Territory" 
          value={stats.total_doctors} 
          icon="👨‍⚕️" 
          trend="4" 
          trendDirection="up" 
        />
        <AnalyticsCard 
          title="YTD Interactions" 
          value={stats.total_interactions} 
          icon="🗓️" 
          trend="12%" 
          trendDirection="up" 
        />
        <AnalyticsCard 
          title="Pending Follow-ups" 
          value={stats.pending_follow_ups} 
          icon="✅" 
          trend="3 Overdue" 
          trendDirection="down" 
        />
        <AnalyticsCard 
          title="Positive Sentiment" 
          value={`${stats.positive_sentiment_pct}%`} 
          icon="😊" 
          trend="2.4%" 
          trendDirection="up" 
        />
      </div>

      <div className="dashboard-content-grid">
        <div className="dashboard-main-col">
          <div className="section-header">
            <h2>Recent Activity</h2>
            <Link to="/interactions" className="text-btn">View All</Link>
          </div>
          <div className="card-container timeline-wrapper">
            {loading ? (
              <div style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
                <div className="skeleton" style={{height: '80px', width: '100%'}}></div>
                <div className="skeleton" style={{height: '80px', width: '100%'}}></div>
                <div className="skeleton" style={{height: '80px', width: '100%'}}></div>
              </div>
            ) : timeline.length > 0 ? (
              <InteractionTimeline interactions={timeline} />
            ) : (
              <div className="empty-state">
                <span className="empty-icon">🗓️</span>
                <h3>No recent activity</h3>
                <p>Log a new interaction to get started.</p>
              </div>
            )}
          </div>
        </div>
        
        <div className="dashboard-side-col">
          <div className="section-header">
            <h2>Action Items</h2>
          </div>
          <div className="tasks-wrapper">
            <div className="tasks-list">
              {loading ? (
                <div style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
                  <div className="skeleton" style={{height: '100px', width: '100%'}}></div>
                  <div className="skeleton" style={{height: '100px', width: '100%'}}></div>
                </div>
              ) : tasks.length > 0 ? (
                tasks.map(task => (
                  <FollowUpCard 
                    key={task.id} 
                    followUp={task} 
                    onComplete={() => confirmCompleteTask(task.id)} 
                  />
                ))
              ) : (
                <div className="empty-state">
                  <span className="empty-icon">✅</span>
                  <h3>All caught up!</h3>
                  <p>You have no pending follow-ups.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <Modal
        isOpen={!!taskToComplete}
        onClose={() => setTaskToComplete(null)}
        title="Complete Follow-up"
        footer={
          <>
            <button className="secondary-btn" onClick={() => setTaskToComplete(null)}>Cancel</button>
            <button className="primary-btn" onClick={handleCompleteTask}>Confirm</button>
          </>
        }
      >
        <p>Are you sure you want to mark this task as completed? This action cannot be undone.</p>
      </Modal>
    </div>
  );
};

export default Dashboard;
