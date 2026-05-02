export interface User {
  id: string;
  email: string;
  name: string;
  mobile: string;
  pan: string;
  role: 'user' | 'admin';
  platform: string;
  city?: string;
  zone: string;
  workingHours: string;
  riskScore: number;
  weeklyPremium: number;
  onboarded: boolean;
  avatar?: string;
}

export interface TriggerEvent {
  id: string;
  type: 'heat' | 'rain' | 'disruption';
  zone: string;
  severity: 'low' | 'medium' | 'high';
  timestamp: string;
  value: number;
  threshold: number;
  status: 'safe' | 'warning' | 'breached';
  payoutTriggered: boolean;
  payoutAmount?: number;
}

export interface Transaction {
  id: string;
  type: 'payout' | 'premium' | 'refund';
  amount: number;
  date: string;
  description: string;
  status: 'completed' | 'pending' | 'failed';
  triggerType?: string;
}

export interface PolicyData {
  weekly_cap: number;
  id: string;
  status: 'active' | 'paused' | 'expired';
  coverageAmount: number;
  weeklyPremium: number;
  riskScore: number;
  startDate: string;
  zone: string;
  triggers: string[];
}

export interface WeatherData {
  temperature: number;
  humidity: number;
  rainfall: number;
  aqi: number;
  zone: string;
  updatedAt: string;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'trigger' | 'payout' | 'system' | 'info';
  read: boolean;
  timestamp: string;
}

export const mockUsers: User[] = [
  {
    id: '1', email: 'rider@gigsurance.com', name: 'Vikram Singh', mobile: '9876543210', pan: 'ABCDE1234F', role: 'user',
    platform: 'Uber', zone: 'Mumbai - Zone A', workingHours: '8AM - 8PM',
    riskScore: 72, weeklyPremium: 49, onboarded: true,
  },
  {
    id: '2', email: 'admin@gigsurance.com', name: 'Admin User', mobile: '9123456780', pan: 'ADMIN1234Z', role: 'admin',
    platform: '', zone: '', workingHours: '',
    riskScore: 0, weeklyPremium: 0, onboarded: true,
  },
];

export const mockTriggerEvents: TriggerEvent[] = [
  { id: 't1', type: 'heat', zone: 'Mumbai - Zone A', severity: 'high', timestamp: '2026-04-03T14:30:00', value: 44, threshold: 42, status: 'breached', payoutTriggered: true, payoutAmount: 200 },
  { id: 't2', type: 'rain', zone: 'Mumbai - Zone A', severity: 'medium', timestamp: '2026-04-02T09:15:00', value: 85, threshold: 100, status: 'warning', payoutTriggered: false },
  { id: 't3', type: 'disruption', zone: 'Mumbai - Zone B', severity: 'high', timestamp: '2026-04-01T11:00:00', value: 1, threshold: 1, status: 'breached', payoutTriggered: true, payoutAmount: 350 },
  { id: 't4', type: 'heat', zone: 'Mumbai - Zone A', severity: 'low', timestamp: '2026-03-30T13:00:00', value: 38, threshold: 42, status: 'safe', payoutTriggered: false },
  { id: 't5', type: 'rain', zone: 'Delhi - Zone C', severity: 'high', timestamp: '2026-03-28T07:00:00', value: 120, threshold: 100, status: 'breached', payoutTriggered: true, payoutAmount: 150 },
  { id: 't6', type: 'heat', zone: 'Mumbai - Zone A', severity: 'medium', timestamp: '2026-03-25T15:00:00', value: 41, threshold: 42, status: 'warning', payoutTriggered: false },
];

export const mockTransactions: Transaction[] = [
  { id: 'tx1', type: 'payout', amount: 200, date: '2026-04-03', description: 'Heat trigger payout - Zone A', status: 'completed', triggerType: 'heat' },
  { id: 'tx2', type: 'premium', amount: -49, date: '2026-04-01', description: 'Weekly premium deduction', status: 'completed' },
  { id: 'tx3', type: 'payout', amount: 350, date: '2026-04-01', description: 'Civil disruption payout', status: 'completed', triggerType: 'disruption' },
  { id: 'tx4', type: 'premium', amount: -49, date: '2026-03-25', description: 'Weekly premium deduction', status: 'completed' },
  { id: 'tx5', type: 'payout', amount: 150, date: '2026-03-28', description: 'Heavy rain payout - Zone C', status: 'completed', triggerType: 'rain' },
  { id: 'tx6', type: 'premium', amount: -49, date: '2026-03-18', description: 'Weekly premium deduction', status: 'completed' },
  { id: 'tx7', type: 'payout', amount: 180, date: '2026-03-15', description: 'Heat trigger payout', status: 'completed', triggerType: 'heat' },
];

export const mockPolicy: PolicyData = {
  id: 'pol-001', status: 'active', coverageAmount: 5000, weeklyPremium: 49,
  riskScore: 72, startDate: '2026-01-15', zone: 'Mumbai - Zone A',
  triggers: ['Extreme Heat (>42°C)', 'Heavy Rainfall (>100mm)', 'Civil Disruption'],
};

export const mockWeather: WeatherData = {
  temperature: 38, humidity: 65, rainfall: 12, aqi: 142,
  zone: 'Mumbai - Zone A', updatedAt: '2026-04-03T14:30:00',
};

export const mockNotifications: Notification[] = [
  { id: 'n1', title: 'Heat Trigger Detected', message: 'Temperature exceeded 42°C in your zone. Payout of ₹200 initiated.', type: 'trigger', read: false, timestamp: '2026-04-03T14:30:00' },
  { id: 'n2', title: 'Payout Processed', message: '₹200 has been credited to your account.', type: 'payout', read: false, timestamp: '2026-04-03T14:35:00' },
  { id: 'n3', title: 'Weekly Premium Deducted', message: '₹49 deducted for week of April 1-7.', type: 'system', read: true, timestamp: '2026-04-01T00:00:00' },
  { id: 'n4', title: 'Coverage Active', message: 'Your parametric insurance coverage is active.', type: 'info', read: true, timestamp: '2026-03-25T10:00:00' },
];

export const mockAnalyticsData = {
  earningsSaved: [
    { month: 'Oct', amount: 320 }, { month: 'Nov', amount: 180 }, { month: 'Dec', amount: 450 },
    { month: 'Jan', amount: 280 }, { month: 'Feb', amount: 520 }, { month: 'Mar', amount: 700 },
  ],
  triggerFrequency: [
    { month: 'Oct', heat: 3, rain: 1, disruption: 0 }, { month: 'Nov', heat: 1, rain: 4, disruption: 1 },
    { month: 'Dec', heat: 0, rain: 2, disruption: 0 }, { month: 'Jan', heat: 2, rain: 1, disruption: 1 },
    { month: 'Feb', heat: 4, rain: 0, disruption: 0 }, { month: 'Mar', heat: 5, rain: 2, disruption: 1 },
  ],
  seasonalTrends: [
    { season: 'Summer', risk: 85, avgPayout: 280 }, { season: 'Monsoon', risk: 70, avgPayout: 220 },
    { season: 'Winter', risk: 30, avgPayout: 80 }, { season: 'Spring', risk: 55, avgPayout: 150 },
  ],
};

export const mockAdminKPIs = {
  activeUsers: 12847,
  totalPayouts: 2340000,
  triggerFrequency: 1823,
  avgPremium: 52,
  riskPoolBalance: 4500000,
  claimsRatio: 0.68,
};
