import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI } from '@/services/api';
import type { User } from '@/services/mockData';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, name: string, password: string) => Promise<void>;
  logout: () => void;
  completeOnboarding: (data: { platform: string; zone: string; workingHours: string }) => Promise<void>;
  updateUser: (updates: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem('gigsurance_user');
    if (stored) {
      try { setUser(JSON.parse(stored)); } catch {}
    }
    setIsLoading(false);
  }, []);

  const persistUser = (u: User | null) => {
    setUser(u);
    if (u) localStorage.setItem('gigsurance_user', JSON.stringify(u));
    else localStorage.removeItem('gigsurance_user');
  };

  const login = async (email: string, password: string) => {
    const u = await authAPI.login(email, password);
    persistUser(u);
  };

  const register = async (email: string, name: string, password: string) => {
    const u = await authAPI.register(email, name, password);
    persistUser(u);
  };

  const logout = useCallback(() => {
    persistUser(null);
  }, []);

  const completeOnboarding = async (data: { platform: string; zone: string; workingHours: string }) => {
    if (!user) return;
    const result = await authAPI.completeOnboarding(user.id, data);
    const updated = { ...user, ...data, ...result, onboarded: true };
    persistUser(updated);
  };

  const updateUser = (updates: Partial<User>) => {
    if (!user) return;
    persistUser({ ...user, ...updates });
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout, completeOnboarding, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
};
