import React from 'react';

const OAuthLoginButtons: React.FC = () => {
  const loginMicrosoft = () => {
    window.location.href = "https://localhost:5000/login/microsoft";
  };

  const loginGoogle = () => {
    window.location.href = "https://localhost:5000/login/google";
  };

  return (
    <div className="btn-group" role="group" aria-label="Login Buttons">
      <button type="button" className="btn btn-primary" onClick={loginMicrosoft}>Login with Microsoft</button>
      <button type="button" className="btn btn-dark" onClick={loginGoogle}>Login with Google</button>
    </div>
  );
};

export default OAuthLoginButtons;
