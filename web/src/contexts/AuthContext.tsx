'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  forgotPassword: (email: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in from localStorage or cookie
    const storedUser = localStorage.getItem('cleudocode_user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error('Failed to parse user from localStorage', e);
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      // Simulate API call to backend
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // In a real app, this would be an API call to your backend
      // const response = await fetch('/api/login', { ... });
      // const userData = await response.json();
      
      // Mock user data
      const mockUser: User = {
        id: '1',
        name: 'John Doe',
        email: email,
        avatar: 'https://via.placeholder.com/40x40'
      };
      
      setUser(mockUser);
      localStorage.setItem('cleudocode_user', JSON.stringify(mockUser));
    } catch (error) {
      throw new Error('Login failed');
    } finally {
      setLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string) => {
    setLoading(true);
    try {
      // Simulate API call to backend
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock user data
      const mockUser: User = {
        id: '1',
        name: name,
        email: email,
        avatar: 'https://via.placeholder.com/40x40'
      };
      
      setUser(mockUser);
      localStorage.setItem('cleudocode_user', JSON.stringify(mockUser));
    } catch (error) {
      throw new Error('Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('cleudocode_user');
  };

  const forgotPassword = async (email: string) => {
    // Simulate API call to backend
    await new Promise(resolve => setTimeout(resolve, 1000));
    // In a real app, this would send a reset link to the user's email
  };

  const value = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    register,
    logout,
    forgotPassword
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}