import React from 'react';
import OAuthLoginButtons from './OAuthLoginButtons';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleCanvasLoginClick = () => {
    navigate('/login-canvas');
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Dashboard</h1>
      </header>
      <main className="dashboard-main">
        <h2>Welcome to the Dashboard</h2>
        <button onClick={handleLogout} className="btn btn-danger">Logout</button>
        <button type="button" className="btn btn-secondary" onClick={handleCanvasLoginClick}>Log in to canvas</button>
        <OAuthLoginButtons />
      </main>
    </div>
  );
};

export default Dashboard;
