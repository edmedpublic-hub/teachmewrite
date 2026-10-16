// src/contexts/AuthContext.jsx
import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI, handleApiError } from '../services/api';

export const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }

    // Set a basic user object without fetching from backend
    // Since /api/v1/users/me/ doesn't exist
    setUser({ 
      username: localStorage.getItem('username') || 'Student',
      tier: localStorage.getItem('user_tier') || 'BASIC'
    });
    setLoading(false);
  };

  const login = async (username, password) => {
    setError(null);
    try {
      console.log('AuthContext: Attempting login');
      const data = await authAPI.login(username, password);
      console.log('AuthContext: Login successful, token received');
      
      // Store user info in localStorage
      localStorage.setItem('username', username);
      localStorage.setItem('user_tier', 'BASIC'); // Default tier
      
      // Set basic user object
      setUser({ username, tier: 'BASIC' });
      
      return { success: true, user: { username } };
    } catch (error) {
      console.error('AuthContext: Login failed:', error);
      const handledError = handleApiError(error);
      setError(handledError.message);
      return { success: false, error: handledError.message };
    }
  };

  const logout = () => {
    authAPI.logout();
    localStorage.removeItem('username');
    localStorage.removeItem('user_tier');
    setUser(null);
  };

  const updateProfile = async (profileData) => {
    // Mock profile update since endpoint doesn't exist
    setUser({ ...user, ...profileData });
    return { success: true, user: { ...user, ...profileData } };
  };

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    updateProfile,
    isAuthenticated: !!localStorage.getItem('access_token'),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};