import React from 'react';
import './index.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './components/HomePage';
import CanvasLoginForm from './components/CanvasLoginPage';
import Dashboard from './components/Dashboard';
import WebsiteLoginPage from './components/WebsiteLoginPage'
import WebsiteSignupPage from './components/WebsiteSignupPage';

const App: React.FC = () => {
  return (
    <Router>
      <div className="app-container">
        <Header />
        <main className="container mt-4">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login-canvas" element={<CanvasLoginForm />} />
            <Route path="/login" element={<WebsiteLoginPage />} />
            <Route path="/signup" element={<WebsiteSignupPage />} />
            <Route path="/dashboard" element={<Dashboard />} /> 
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
};

export default App;
