import {
  mockUsers, mockTriggerEvents, mockTransactions, mockPolicy,
  mockWeather, mockNotifications, mockAnalyticsData, mockAdminKPIs,
  type User, type TriggerEvent, type Transaction, type PolicyData,
  type WeatherData, type Notification,
} from './mockData';

const delay = (ms: number) => new Promise(r => setTimeout(r, ms));

const simulateError = (rate = 0.05) => {
  if (Math.random() < rate) throw new Error('API request failed. Please try again.');
};

export const authAPI = {
  login: async (email: string, _password: string): Promise<User> => {
    await delay(800);
    const user = mockUsers.find(u => u.email === email);
    if (!user) throw new Error('Invalid credentials');
    return user;
  },
  register: async (email: string, name: string, _password: string): Promise<User> => {
    await delay(1000);
    if (mockUsers.find(u => u.email === email)) throw new Error('Email already exists');
    return { id: '3', email, name, role: 'user', platform: '', zone: '', workingHours: '', riskScore: 0, weeklyPremium: 0, onboarded: false };
  },
  completeOnboarding: async (userId: string, data: { platform: string; zone: string; workingHours: string }): Promise<{ riskScore: number; weeklyPremium: number }> => {
    await delay(1500);
    const riskScore = Math.floor(Math.random() * 40) + 50;
    const weeklyPremium = Math.floor(riskScore * 0.7) + 10;
    return { riskScore, weeklyPremium };
  },
};

export const weatherAPI = {
  getCurrent: async (zone: string): Promise<WeatherData> => {
    await delay(500);
    simulateError();
    return { ...mockWeather, zone };
  },
};

export const triggerAPI = {
  getAll: async (): Promise<TriggerEvent[]> => {
    await delay(600);
    simulateError();
    return mockTriggerEvents;
  },
  getByZone: async (zone: string): Promise<TriggerEvent[]> => {
    await delay(500);
    return mockTriggerEvents.filter(t => t.zone === zone);
  },
};

export const transactionAPI = {
  getAll: async (): Promise<Transaction[]> => {
    await delay(600);
    simulateError();
    return mockTransactions;
  },
};

export const policyAPI = {
  get: async (): Promise<PolicyData> => {
    await delay(500);
    return mockPolicy;
  },
  toggleCoverage: async (active: boolean): Promise<PolicyData> => {
    await delay(800);
    return { ...mockPolicy, status: active ? 'active' : 'paused' };
  },
};

export const notificationAPI = {
  getAll: async (): Promise<Notification[]> => {
    await delay(400);
    return mockNotifications;
  },
  markRead: async (id: string): Promise<void> => {
    await delay(300);
  },
};

export const analyticsAPI = {
  getData: async () => {
    await delay(700);
    simulateError();
    return mockAnalyticsData;
  },
};

export const adminAPI = {
  getKPIs: async () => {
    await delay(600);
    return mockAdminKPIs;
  },
};
