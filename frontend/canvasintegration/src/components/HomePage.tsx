import React, { useState } from 'react';
import CanvasLoginForm from './CanvasLoginForm';
import LoginButtons from './LoginButtons';

const HomePage: React.FC = () => {
  const [isLoggedInToCanvas, setIsLoggedInToCanvas] = useState(false);

  // Function to handle successful Canvas login
  const handleCanvasLogin = (credentials: { username: string, password: string }) => {
    // Assuming a simple validation for demonstration
    if (credentials.username === 'demo' && credentials.password === 'password') {
      setIsLoggedInToCanvas(true);
    } else {
      alert('Invalid credentials. Please try again.');
    }
  };

  return (
    <div className="container mt-4">
      <h1>Welcome to OAuth2 Integration</h1>
      {!isLoggedInToCanvas ? (
        <CanvasLoginForm onLogin={handleCanvasLogin} />
      ) : (
        <>
          <p>You are logged in to Canvas.</p>
          <LoginButtons />
        </>
      )}
    </div>
  );
};

export default HomePage;
