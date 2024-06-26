import React from 'react';
import { useNavigate } from 'react-router-dom';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const handleLoginClick = () => {
    navigate('/login');
  };

  return (
    <div className="jumbotron">
      <div className="container">
        <h1 className="display-4">Welcome to Canvas Integration</h1>
        <p className="lead">Our website helps sync your canvas assignments across multiple calender and to do services.</p>
        <hr className="my-4" />
        <button onClick={handleLoginClick}>Log in to account</button>
      </div>
    </div>
  );
};

export default HomePage;