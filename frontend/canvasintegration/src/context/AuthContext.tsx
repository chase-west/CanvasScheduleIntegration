import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { login as apiLogin, signUp as apiSignUp, loginToCanvas as apiLoginToCanvas, checkUserState, logout as apiLogout } from '../api/api'; 

interface AuthContextType {
  isAuthenticated: boolean;
  hasLoggedIntoCanvas: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  loginToCanvas: (credentials: { username: string; password: string }) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [hasLoggedIntoCanvas, setHasLoggedIntoCanvas] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true); // Loading state

  useEffect(() => {
    const fetchUserState = async () => {
      try {
        const response = await checkUserState();
        setIsAuthenticated(response.isAuthenticated);
        setHasLoggedIntoCanvas(response.hasLoggedIntoCanvas); 
      } catch (error) {
        setIsAuthenticated(false);
        setHasLoggedIntoCanvas(false);
      } finally {
        setLoading(false); // Set loading to false once authentication check is complete
      }
    };

    fetchUserState();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      await apiLogin({ email, password });
      const response = await checkUserState();
      setIsAuthenticated(response.isAuthenticated); // Update isAuthenticated based on backend response
    } catch (error) {
      console.error("Login failed:", error);
      setIsAuthenticated(false); // Ensure isAuthenticated is false on login failure
      throw error; // Rethrow the error to handle in the login component
    }
  };

  const logout = async () => {
    try {
      await apiLogout(); // Backend logout
      setIsAuthenticated(false); // Update isAuthenticated on successful logout
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  const signUp = async (email: string, password: string) => {
    try {
      await apiSignUp({ email, password });
    } catch (error) {
      console.error("Sign up failed:", error);
    }
  };

  const loginToCanvas = async (credentials: { username: string; password: string }) => {
    try {
      await apiLoginToCanvas(credentials);
    } catch (error) {
      console.error("Canvas login failed:", error);
    }
  };

  // Show loading indicator or login page based on authentication status
  if (loading) {
    return <div>Loading...</div>; // Optional: Replace with a loading spinner or indicator
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, hasLoggedIntoCanvas, login, logout, signUp, loginToCanvas }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
  