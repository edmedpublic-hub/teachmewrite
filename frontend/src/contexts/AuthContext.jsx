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

  // Cache the user for instant render on reload.
  // `tier` is kept as a Navbar-facing alias for `current_tier`.
  const _cacheUser = (u) => {
    if (u?.username) localStorage.setItem('username', u.username);
    const tierValue = u?.current_tier || u?.tier || 'BASIC';
    localStorage.setItem('user_tier', tierValue);
    setUser({ ...u, tier: tierValue });
  };

  // Fetch the real user state from /api/v1/users/me/.
  // Handles 401 gracefully: clears token, returns null.
  const _fetchCurrentUser = async () => {
    try {
      const data = await authAPI.getCurrentUser();
      _cacheUser(data);
      return data;
    } catch (err) {
      if (err?.response?.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('username');
        localStorage.removeItem('user_tier');
        setUser(null);
      }
      return null;
    }
  };

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }

    // Optimistic render from cache while /me/ is in flight
    const cachedUsername = localStorage.getItem('username');
    if (cachedUsername) {
      const cachedTier = localStorage.getItem('user_tier') || 'BASIC';
      setUser({ username: cachedUsername, current_tier: cachedTier, tier: cachedTier });
    }

    await _fetchCurrentUser();
    setLoading(false);
  };

  const login = async (username, password) => {
    setError(null);
    try {
      console.log('AuthContext: Attempting login');
      await authAPI.login(username, password);
      console.log('AuthContext: Token received, fetching user state');

      const u = await _fetchCurrentUser();
      if (!u) {
        // Auth succeeded but /me/ failed; fall back to cached defaults
        _cacheUser({ username, current_tier: 'BASIC' });
      }
      return { success: true, user: u || { username, current_tier: 'BASIC', tier: 'BASIC' } };
    } catch (err) {
      console.error('AuthContext: Login failed:', err);
      const handledError = handleApiError(err);
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
    // Still mocked: /users/profile/ not wired into AuthContext yet.
    // Separate Day 107 item (see book/day_106.md).
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
