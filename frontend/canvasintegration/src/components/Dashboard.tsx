import React from 'react';
import OAuthLoginButtons from './OAuthLoginButtons';

const Dashboard: React.FC = () => {
  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Dashboard</h1>
      </header>
      <main className="dashboard-main">
        <h2>Welcome to the Dashboard</h2>
        <OAuthLoginButtons />
      </main>
    </div>
  );
};

export default Dashboard;
