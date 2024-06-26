import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../api/api'; 
import 'bootstrap/dist/css/bootstrap.min.css';

const WebsiteLoginPage = () => {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loginError, setLoginError] = useState('');

    const handleLogin = async (e : any) => {
        e.preventDefault();

        try {
            const response = await login({ email, password });  
            console.log(response);
            setLoginError('');
            navigate('/dashboard');
        } catch (error) {
            console.error('Error logging in:', error);
            setLoginError('Invalid credentials. Please try again.');
        }
    };

    return (
        <div className="container">
            <div className="row justify-content-center">
                <div className="col-md-6">
                    <form onSubmit={handleLogin} className="mt-5">
                        <h2>Login</h2>
                        {loginError && <div className="alert alert-danger">{loginError}</div>}
                        <div className="form-group">
                            <label htmlFor="email">Email</label>
                            <input
                                type="text"
                                className="form-control"
                                id="email"
                                placeholder="Enter Email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="password">Password</label>
                            <input
                                type="password"
                                className="form-control"
                                id="password"
                                placeholder="Enter password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        <button type="submit" className="btn btn-primary">Login</button>
                        <button type="button" className="btn btn-secondary ml-2" onClick={() => navigate('/signup')}>Sign Up</button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default WebsiteLoginPage;
