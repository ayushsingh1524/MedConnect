import React from 'react';
import './Navbar.css';

const Navbar = ({ toggleSidebar }) => {
  return (
    <header className="navbar">
      <div className="navbar-search">
        <button 
          className="hamburger-btn" 
          onClick={toggleSidebar}
          aria-label="Toggle menu"
        >
          ☰
        </button>
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input 
            type="text" 
            placeholder="Search doctors, interactions..." 
            className="search-input"
          />
        </div>
      </div>
      
      <div className="navbar-actions">
        <button className="icon-btn notification-btn">
          <span className="icon">🔔</span>
          <span className="badge">3</span>
        </button>
        
        <div className="user-profile">
          <div className="avatar">SR</div>
          <div className="user-info">
            <span className="user-name">Sarah Rep</span>
            <span className="user-role">Field Sales Manager</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
