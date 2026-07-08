import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Layout & Core
import Layout from './components/Layout/Layout';
import ErrorBoundary from './components/ErrorBoundary/ErrorBoundary';
import { ToastProvider } from './components/Toast/ToastContext';

// Pages
import Dashboard from './pages/Dashboard/Dashboard';
import DoctorList from './pages/DoctorList/DoctorList';
import DoctorDetails from './pages/DoctorDetails/DoctorDetails';
import LogInteraction from './pages/LogInteraction/LogInteraction';
import AIChatPanel from './pages/AIChatPanel/AIChatPanel';
import NotFound from './pages/NotFound/NotFound';

// CSS Reset / Global Variables
import './index.css';

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <Router>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="hcps" element={<DoctorList />} />
              <Route path="hcps/:id" element={<DoctorDetails />} />
              <Route path="interactions" element={<LogInteraction />} />
              <Route path="chat" element={<AIChatPanel />} />
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </Router>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;
