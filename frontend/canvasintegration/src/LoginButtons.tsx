import React from 'react';

const LoginButtons: React.FC = () => {
  const loginMicrosoft = () => {
    window.location.href = "https://localhost:5000/login/microsoft";
  };

  const loginGoogle = () => {
    window.location.href = "https://localhost:5000/login/google";
  };

  return (
    <div>
      <button onClick={loginMicrosoft}>Login with Microsoft</button>
      <button onClick={loginGoogle}>Login with Google</button>
    </div>
  );
};

export default LoginButtons;
