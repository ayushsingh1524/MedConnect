import React from 'react';
import { NavLink } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  return (
    <header className="navbar glass-nav">
      <div className="navbar-brand">
        <h1 className="brand-title">MedConnect</h1>
      </div>
      
      <nav className="navbar-nav">
        <NavLink 
          to="/" 
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          Dashboard
        </NavLink>
        
        <NavLink 
          to="/hcps" 
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          HCP Directory
        </NavLink>
        
        <NavLink 
          to="/interactions" 
          className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
        >
          Interactions
        </NavLink>

        <NavLink 
          to="/chat" 
          className={({ isActive }) => (isActive ? 'nav-item ai-assistant active' : 'nav-item ai-assistant')}
        >
          ✨ AI Assistant
        </NavLink>
      </nav>

      <div className="navbar-actions">
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input 
            type="text" 
            placeholder="Search..." 
            className="search-input"
          />
        </div>
        
        <button className="icon-btn notification-btn">
          <span className="icon">🔔</span>
          <span className="badge">3</span>
        </button>
        
        <div className="user-profile">
          <div className="avatar">SR</div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
