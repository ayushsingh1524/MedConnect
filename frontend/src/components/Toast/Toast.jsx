import React from 'react';
import './Toast.css';

const Toast = ({ message, type, onClose }) => {
  const icons = {
    success: '✅',
    error: '⚠️',
    warning: '⚡',
    info: 'ℹ️'
  };

  return (
    <div className={`toast toast-${type}`} role="alert">
      <span className="toast-icon">{icons[type]}</span>
      <p className="toast-message">{message}</p>
      <button className="toast-close" onClick={onClose} aria-label="Close notification">×</button>
    </div>
  );
};

export default Toast;
