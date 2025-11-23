/**
 * Authentication Context
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '../services/api';
import type { UserInfo, OTPRequest, OTPVerifyRequest } from '../types';

interface AuthContextType {
  user: UserInfo | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  requestOTP: (data: OTPRequest) => Promise<void>;
  verifyOTP: (data: OTPVerifyRequest) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user is already authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (apiClient.isAuthenticated()) {
        try {
          const userData = await apiClient.getCurrentUser();
          setUser(userData);
        } catch (err) {
          console.error('Failed to get current user:', err);
          // Token might be expired, clear it
          await apiClient.logout();
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const requestOTP = async (data: OTPRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.requestOTP(data);
      return response;
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || 'Failed to request OTP. Please try again.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const verifyOTP = async (data: OTPVerifyRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      await apiClient.verifyOTP(data);

      // Fetch user info
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || 'Failed to verify OTP. Please try again.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);

    try {
      await apiClient.logout();
      setUser(null);
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const clearError = () => {
    setError(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: user !== null,
    isLoading,
    error,
    requestOTP,
    verifyOTP,
    logout,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
