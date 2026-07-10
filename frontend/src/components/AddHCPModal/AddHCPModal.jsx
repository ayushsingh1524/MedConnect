import React, { useState } from 'react';
import './AddHCPModal.css';

const SPECIALTIES = [
  'All',
  'Cardiology',
  'Endocrinology',
  'Neurology',
  'Oncology',
  'Pediatrics',
  'Internal Medicine'
].filter(s => s !== 'All');

const AddHCPModal = ({ isOpen, onClose, onAdd }) => {
  const [formData, setFormData] = useState({
    name: '',
    specialty: 'Cardiology',
    hospital: '',
    city: '',
    email: '',
    phone: ''
  });

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onAdd(formData);
    // Reset form
    setFormData({
      name: '',
      specialty: 'Cardiology',
      hospital: '',
      city: '',
      email: '',
      phone: ''
    });
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Add New Healthcare Professional</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>
        
        <form onSubmit={handleSubmit} className="add-hcp-form">
          <div className="form-group">
            <label htmlFor="name">Full Name (with Title) *</label>
            <input 
              type="text" 
              id="name" 
              name="name" 
              placeholder="e.g. Dr. Jane Smith"
              value={formData.name} 
              onChange={handleChange} 
              required 
            />
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="specialty">Specialty *</label>
              <select 
                id="specialty" 
                name="specialty" 
                value={formData.specialty} 
                onChange={handleChange}
                required
              >
                {SPECIALTIES.map(spec => (
                  <option key={spec} value={spec}>{spec}</option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="hospital">Hospital / Clinic *</label>
              <input 
                type="text" 
                id="hospital" 
                name="hospital" 
                value={formData.hospital} 
                onChange={handleChange} 
                required 
              />
            </div>
          </div>
          
          <div className="form-group">
            <label htmlFor="city">City *</label>
            <input 
              type="text" 
              id="city" 
              name="city" 
              value={formData.city} 
              onChange={handleChange} 
              required 
            />
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input 
                type="email" 
                id="email" 
                name="email" 
                value={formData.email} 
                onChange={handleChange} 
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="phone">Phone</label>
              <input 
                type="text" 
                id="phone" 
                name="phone" 
                value={formData.phone} 
                onChange={handleChange} 
              />
            </div>
          </div>
          
          <div className="modal-actions">
            <button type="button" className="secondary-btn" onClick={onClose}>Cancel</button>
            <button type="submit" className="primary-btn">Save HCP</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddHCPModal;
