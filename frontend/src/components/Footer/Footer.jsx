import React from 'react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="app-footer">
      <div className="footer-content">
        <p>Built by <strong>Ayush Singh</strong> | Avion Assignment</p>
        <div className="footer-links">
          <a href="#" className="footer-link">GitHub</a>
          <a href="#" className="footer-link">LinkedIn</a>
          <a href="#" className="footer-link">Portfolio</a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
