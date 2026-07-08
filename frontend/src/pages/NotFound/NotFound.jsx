import React from 'react';
import { Link } from 'react-router-dom';
import './NotFound.css';

const NotFound = () => {
  return (
    <div className="notfound-container">
      <div className="notfound-content">
        <h1 className="notfound-title">404</h1>
        <h2 className="notfound-subtitle">Page Not Found</h2>
        <p className="notfound-text">The page you are looking for doesn't exist or has been moved.</p>
        <Link to="/" className="notfound-btn">
          Return to Dashboard
        </Link>
      </div>
    </div>
  );
};

export default NotFound;
