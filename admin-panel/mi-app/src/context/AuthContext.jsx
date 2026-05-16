// src/context/AuthContext.jsx
import { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // On initial mount, check if a session exists on the server
    const checkUserSession = async () => {
      try {
        // Assuming authAPI.me() calls the /auth/me endpoint
        const data = await authAPI.me(); 
        if (data.usuario && data.usuario.rol !== 'cliente') {
          setUser(data.usuario);
        } else {
          // If the user is a customer or data is invalid, clear the session
          setUser(null);
        }
      } catch (error) {
        // If the /me endpoint fails (e.g., 401), it means no valid session exists
        console.error('No active session found:', error.message);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkUserSession();
  }, []);

  const login = async (email, password) => {
    try {
      setLoading(true);
      const data = await authAPI.login(email, password);

      // Security check: only admin or superadmin can log into the panel
      if (data.usuario.rol === 'cliente') {
        throw new Error('Access to the admin panel is denied for this user role.');
      }

      setUser(data.usuario);
      return { success: true };
    } catch (error) {
      // Ensure user state is null on a failed login attempt
      setUser(null);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      // This function is likely for the public site, but we keep it for completeness
      setLoading(true);
      await authAPI.register(userData);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Error logging out:', error);
    } finally {
      setUser(null);
    }
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};