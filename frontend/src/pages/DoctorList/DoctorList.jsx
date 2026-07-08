import React, { useState, useEffect, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchHCPs } from '../../store/slices/hcpSlice';
import DoctorCard from '../../components/DoctorCard/DoctorCard';
import './DoctorList.css';


const SPECIALTIES = ['All', 'Cardiology', 'Neurology', 'Endocrinology', 'Internal Medicine', 'Oncology'];

const DoctorList = () => {
  const dispatch = useDispatch();
  const { list: doctors, loading, error } = useSelector((state) => state.hcps);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [activeSpecialty, setActiveSpecialty] = useState('All');

  useEffect(() => {
    dispatch(fetchHCPs());
  }, [dispatch]);

  const filteredDoctors = useMemo(() => {
    if (!doctors) return [];
    return doctors.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          doc.hospital.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSpecialty = activeSpecialty === 'All' || doc.specialty === activeSpecialty;
    
    return matchesSearch && matchesSpecialty;
  });
  }, [doctors, searchTerm, activeSpecialty]);

  return (
    <div className="doctor-list-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">HCP Directory</h1>
          <p className="page-subtitle">Manage your territory's healthcare professionals.</p>
        </div>
        <button className="primary-btn">
          <span className="icon">+</span> Add HCP
        </button>
      </div>

      <div className="directory-controls">
        <div className="search-bar">
          <span className="search-icon">🔍</span>
          <input 
            type="text" 
            placeholder="Search by name or hospital..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="directory-search-input"
          />
        </div>
        
        <div className="filter-chips">
          {SPECIALTIES.map(specialty => (
            <button 
              key={specialty}
              className={`filter-chip ${activeSpecialty === specialty ? 'active' : ''}`}
              onClick={() => setActiveSpecialty(specialty)}
            >
              {specialty}
            </button>
          ))}
        </div>
      </div>

      <div className="doctor-grid">
        {loading ? (
          <>
            <div className="skeleton" style={{height: '250px', width: '100%', borderRadius: 'var(--border-radius-lg)'}}></div>
            <div className="skeleton" style={{height: '250px', width: '100%', borderRadius: 'var(--border-radius-lg)'}}></div>
            <div className="skeleton" style={{height: '250px', width: '100%', borderRadius: 'var(--border-radius-lg)'}}></div>
            <div className="skeleton" style={{height: '250px', width: '100%', borderRadius: 'var(--border-radius-lg)'}}></div>
          </>
        ) : error ? (
          <div className="empty-state">
            <span className="empty-icon">⚠️</span>
            <h3>Failed to load HCPs</h3>
            <p className="error-text">{error}</p>
          </div>
        ) : filteredDoctors.length > 0 ? (
          filteredDoctors.map(doctor => (
            <DoctorCard key={doctor.id} doctor={doctor} />
          ))
        ) : (
          <div className="empty-state" style={{gridColumn: '1 / -1'}}>
            <span className="empty-icon">🔍</span>
            <h3>No HCPs found</h3>
            <p>We couldn't find any HCPs matching your search criteria.</p>
            <button className="secondary-btn" style={{marginTop: '1rem'}} onClick={() => {
              setSearchTerm('');
              setActiveSpecialty('All');
            }}>Clear Filters</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DoctorList;
