// import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './components/GoogleLoginButton.js';
import DashboardPage from './components/Dashboard.jsx';
import Category from './components/CategoryDashboard.jsx'


const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/Category" element={<Category/>}/>
      </Routes>
    </Router>
  );
};

export default App;
