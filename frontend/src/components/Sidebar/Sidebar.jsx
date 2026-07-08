import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = ({ isOpen, closeSidebar }) => {
  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <h1 className="brand-title">MedConnect</h1>
        <p className="brand-subtitle">AI Healthcare CRM</p>
      </div>
      
      <nav className="sidebar-nav">
        <NavLink 
          to="/" 
          onClick={closeSidebar} 
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          <span className="nav-icon">📊</span>
          Dashboard
        </NavLink>
        
        <NavLink 
          to="/hcps" 
          onClick={closeSidebar}
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          <span className="nav-icon">👨‍⚕️</span>
          HCP Directory
        </NavLink>
        
        <NavLink 
          to="/interactions" 
          onClick={closeSidebar}
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          <span className="nav-icon">🗓️</span>
          Interactions
        </NavLink>
        
        <NavLink 
          to="/follow-ups" 
          onClick={closeSidebar}
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          <span className="nav-icon">✅</span>
          Follow-ups
        </NavLink>

        <NavLink 
          to="/chat" 
          onClick={closeSidebar}
          className={({ isActive }) => (isActive ? 'nav-item ai-assistant active' : 'nav-item ai-assistant')}
        >
          <span className="nav-icon">✨</span>
          AI Assistant
        </NavLink>
      </nav>
    </aside>
  );
};

export default Sidebar;
