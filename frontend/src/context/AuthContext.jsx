import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('library_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check initial auth state from backend
    authApi.me()
      .then((res) => {
        if (res.authenticated && res.user) {
          setUser(res.user);
          localStorage.setItem('library_user', JSON.stringify(res.user));
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const login = async (username, password) => {
    const res = await authApi.login(username, password);
    if (res.success && res.user) {
      setUser(res.user);
      localStorage.setItem('library_user', JSON.stringify(res.user));
    }
    return res;
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch {}
    setUser(null);
    localStorage.removeItem('library_user');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, isAuthenticated: !!user, isAdmin: user?.is_admin }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
