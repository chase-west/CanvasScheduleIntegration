import React from 'react';
import OAuthLoginButtons from './OAuthLoginButtons';
import { useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const handleCanvasLoginClick = () => {
    navigate('/login-canvas');
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Dashboard</h1>
      </header>
      <main className="dashboard-main">
        <h2>Welcome to the Dashboard</h2>
        <button type="button" className="btn btn-secondary" onClick={handleCanvasLoginClick}>Log in to canvas</button>
        <OAuthLoginButtons />
      </main>
    </div>
  );
};

export default Dashboard;
