import React, { useState } from 'react';
import { signUp } from '../api/api'; 
import 'bootstrap/dist/css/bootstrap.min.css';

const WebsiteSignupPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [signupError, setSignupError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false); // State to track form submission

  const handleSignup = async (e : any) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setSignupError('Passwords do not match.');
      return;
    }

    // Disable submit button to prevent multiple submissions
    setIsSubmitting(true);

    try {
      const response = await signUp({ email, password });
      console.log(response);
      // Handle successful sign-up
      setSignupError('');
    } catch (error) {
      console.error('Error signing up:', error);
      setSignupError('Error signing up. Please try again.');
    } finally {
      // Enable submit button after form submission completes
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <form onSubmit={handleSignup} className="mt-5">
            <h2>Sign Up</h2>
            {signupError && <div className="alert alert-danger">{signupError}</div>}
            <div className="form-group">
              <label htmlFor="signup-email">Email</label>
              <input
                type="text"
                className="form-control"
                id="signup-email"
                placeholder="Enter Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="signup-password">Password</label>
              <input
                type="password"
                className="form-control"
                id="signup-password"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="signup-confirm-password">Confirm Password</label>
              <input
                type="password"
                className="form-control"
                id="signup-confirm-password"
                placeholder="Confirm password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Signing Up...' : 'Sign Up'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default WebsiteSignupPage;
