// HomePage.tsx
import React from 'react';
import LoginButtons from './LoginButtons';

const HomePage: React.FC = () => {
  return (
    <div className="jumbotron">
      <div className="container">
        <h1 className="display-4">Welcome to OAuth2 Integration</h1>
        <p className="lead">This is a sample application demonstrating OAuth2 integration with Microsoft and Google.</p>
        <hr className="my-4" />
        <LoginButtons />
      </div>
    </div>
  );
};

export default HomePage;
