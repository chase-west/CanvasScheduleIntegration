import React from 'react';
import LoginButtons from './LoginButtons';

const HomePage: React.FC = () => {
  return (
    <div className="jumbotron">
      <div className="container">
        <h1 className="display-4">Welcome to Canvas Integration</h1>
        <p className="lead">Our website helps you sync your canvas assignments across multiple calender services and to do services.</p>
        <hr className="my-4" />
        <LoginButtons />
      </div>
    </div>
  );
};

export default HomePage;
