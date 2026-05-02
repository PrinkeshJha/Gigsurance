import React, { createContext, useState, useEffect, useCallback } from 'react';
import type { User } from '@/services/api';
import { authAPI, onboardingAPI } from '@/services/api';

export interface AuthContextType {
user: User | null;
isLoading: boolean;
login: (pan: string, password: string) => Promise<void>;
register: (email: string, name: string, mobile: string, pan: string, password: string) => Promise<void>;
logout: () => void;
completeOnboarding: (data: {
platform: string;
city: string;
zone: string;
workingHours: string;
riskScore: number;
weeklyPremium: number;
}) => Promise<void>;
updateUser: (updates: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);
export { AuthContext };

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
const [user, setUser] = useState<User | null>(null);
const [isLoading, setIsLoading] = useState(true);

// -------------------------------
// Persist user + token
// -------------------------------
const persistUser = (u: User | null, token?: string | null) => {
if (token !== undefined) {
if (token) {
localStorage.setItem('gigsurance_token', token);
} else {
localStorage.removeItem('gigsurance_token');
}
}


setUser(u);

if (u) {
  localStorage.setItem('gigsurance_user', JSON.stringify(u));
} else {
  localStorage.removeItem('gigsurance_user');
}


};

// -------------------------------
// Load user on app start
// -------------------------------
useEffect(() => {
const loadUser = async () => {
const savedToken = localStorage.getItem('gigsurance_token');


  if (savedToken) {
    try {
      const userData = await authAPI.getMe();
      persistUser(userData as User, savedToken);
    } catch {
      persistUser(null, null);
    }
  }

  setIsLoading(false);
};

loadUser();


}, []);

// -------------------------------
// LOGIN (FIXED 🔥)
// -------------------------------
const login = async (pan: string, password: string) => {
try {
const res = await authAPI.login(
pan.trim().toUpperCase(),
password
);


  const token = res.access_token;

  // Save token
  localStorage.setItem('gigsurance_token', token);

  const userData = await authAPI.getMe();
  persistUser(userData as User, token);

} catch (err: any) {
  throw new Error(err.message || 'Login failed');
}


};

// -------------------------------
// REGISTER (FIXED 🔥)
// -------------------------------
const register = async (
email: string,
name: string,
mobile: string,
pan: string,
password: string
) => {
await authAPI.register({
email,
name,
mobile,
pan: pan.trim().toUpperCase(),
password,
});


// Auto login after register
await login(pan, password);


};

// -------------------------------
// LOGOUT
// -------------------------------
const logout = useCallback(() => {
persistUser(null, null);
window.location.href = "/login"; // ✅ ensure redirect
}, []);

// -------------------------------
// COMPLETE ONBOARDING (FIXED 🔥)
// -------------------------------
const completeOnboarding = async (data: {
platform: string;
city: string;
zone: string;
workingHours: string;
riskScore: number;
weeklyPremium: number;
}) => {
if (!user) throw new Error('Auth required');


await onboardingAPI.complete({
  platform: data.platform,
  city: data.city,
  zone: data.zone,
  working_hours: data.workingHours,
  riskScore: data.riskScore,
  weeklyPremium: data.weeklyPremium,
});

const updatedUser = await authAPI.getMe();
persistUser(updatedUser as User);


};

// -------------------------------
// UPDATE PROFILE
// -------------------------------
const updateUser = async (updates: Partial<User>) => {
if (!user) throw new Error('Auth required');


const updatedUser = await authAPI.updateProfile(updates);
persistUser(updatedUser as User);


};

return (
<AuthContext.Provider
value={{
user,
isLoading,
login,
register,
logout,
completeOnboarding,
updateUser,
}}
>
{children}
</AuthContext.Provider>
);
};
