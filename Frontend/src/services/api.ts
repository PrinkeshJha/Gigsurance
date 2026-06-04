import axios from 'axios';

/* ================= CONFIG ================= */

const API_BASE =
import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const api = axios.create({
baseURL: API_BASE,
headers: {
'Content-Type': 'application/json',
},
withCredentials: true, // ✅ IMPORTANT FOR CORS
});

/* ================= INTERCEPTORS ================= */

// ✅ REQUEST
api.interceptors.request.use((config) => {
const token = localStorage.getItem('gigsurance_token');

if (token && config.headers) {
config.headers.Authorization = `Bearer ${token}`;
}

return config;
});

// ✅ RESPONSE
api.interceptors.response.use(
(response) => response,
(error) => {
if (error.response?.status === 401) {
localStorage.removeItem('gigsurance_token');
localStorage.removeItem('gigsurance_user');

  window.location.href = '/login';
}

const message =
  error.response?.data?.detail ||
  error.message ||
  'Request failed';

return Promise.reject(new Error(message));


}
);

/* ================= TYPES ================= */

export type AuthResponse = {
access_token: string;
token_type: string;
};

export type User = {
id?: string;
name: string;
email: string;
mobile: string;
pan: string;
platform?: string;
city?: string;
zone?: string;
working_hours?: string;
role?: string;
is_onboarded?: boolean;
risk_score?: number;
weekly_premium?: number;
};

export type Transaction = {
id: string;
amount: number;
type: 'payout' | 'premium';
status: string;
createdAt: string;
};

export type Policy = {
  id: string;
  status: string;
  coverageAmount: number;
  weeklyPremium: number;
  riskScore: number;
};

export type Notification = {
  id: string;
  type: 'trigger' | 'payout' | 'system' | 'info';
  title: string;
  message: string;
  read: boolean;
  timestamp: string;
};

export type WeatherData = {
  temperature?: number;
  condition?: string;
  zone?: string;
  risk_level?: 'low' | 'medium' | 'high';
  humidity?: number;
  rainfall?: number;
  aqi?: number;
  updatedAt?: string;
};

export type TriggerEvent = {
  id: string;
  type: string;
  zone: string;
  severity: 'low' | 'medium' | 'high';
  timestamp: string;
  value?: number;
  threshold?: number;
  status?: 'safe' | 'warning' | 'breached';
  payoutTriggered?: boolean;
  payoutAmount?: number;
};

/* ================= AUTH ================= */

export const authAPI = {
login: async (pan: string, password: string): Promise<AuthResponse> => {
const res = await api.post('/auth/login', { pan, password });


// ✅ SAVE TOKEN HERE (CRITICAL FIX)
localStorage.setItem('gigsurance_token', res.data.access_token);

return res.data;


},

register: async (data: {
email: string;
name: string;
mobile: string;
pan: string;
password: string;
}) => {
const res = await api.post('/auth/register', data);
return res.data;
},

getMe: async (): Promise<User> => {
const res = await api.get('/auth/me');
return res.data;
},

updateProfile: async (updates: Partial<User>) => {
const res = await api.patch('/auth/profile', updates);
return res.data;
},
};

/* ================= META ================= */

export const metaAPI = {
getPlatforms: async () => (await api.get('/meta/platforms')).data,
getCities: async () => (await api.get('/meta/cities')).data,
getZones: async (city: string) =>
(await api.get(`/meta/zones/${encodeURIComponent(city)}`)).data,
};

/* ================= ONBOARDING ================= */

export const onboardingAPI = {
calculate: async (data: any) => {
const res = await api.post('/onboarding/calculate', data);

return {
  riskScore: res.data.risk_score,
  weeklyPremium: res.data.weekly_premium,
  weeklyCap: res.data.weekly_cap,
  perDeliveryDeduction: res.data.per_delivery_deduction,
};


},

complete: async (data: any) => {
const res = await api.post('/onboarding/complete', {
...data,
risk_score: data.riskScore,
weekly_premium: data.weeklyPremium,
});


return res.data;


},
};

/* ================= POLICY ================= */

export const policyAPI = {
get: async () => {
const res = await api.get('/policy/me');

return {
  id: res.data.id,
  status: res.data.status,
  coverageAmount: res.data.coverage_amount,
  weeklyPremium: res.data.weekly_premium,
  riskScore: res.data.risk_score,
};


},

toggleCoverage: async (active: boolean) => {
const res = await api.post('/policy/toggle', { active });

return {
  id: res.data.id,
  status: res.data.status,
  coverageAmount: res.data.coverage_amount,
  weeklyPremium: res.data.weekly_premium,
  riskScore: res.data.risk_score,
};


},
};

/* ================= TRANSACTIONS ================= */

export const transactionAPI = {
getAll: async (): Promise<Transaction[]> => {
const res = await api.get('/transactions');


return (res.data || []).map((t: any) => ({
  id: t.id,
  amount: Number(t.amount || 0),
  type: t.type === 'credit' ? 'payout' : 'premium',
  status: t.status,
  createdAt: t.created_at,
}));


},
};

/* ================= ANALYTICS ================= */

export const analyticsAPI = {
getData: async () => {
const res = await api.get('/analytics');


return {
  totalUsers: res.data.total_users,
  activePolicies: res.data.active_policies,
  totalPayouts: res.data.total_payouts,
  riskDistribution: res.data.risk_distribution,
};


},
};

/* ================= TRIGGERS ================= */

export const triggerAPI = {
getAll: async () => {
const res = await api.get('/triggers/all');
return res.data;
},

getLive: async () => {
const res = await api.get('/triggers/live');
return res.data;
},
};

/* ================= WEATHER ================= */

export const weatherAPI = {
getCurrent: async (zone: string) => {
if (!zone) throw new Error('Zone is required');


const res = await api.get(`/weather/${encodeURIComponent(zone)}`);
return res.data;


},
};

/* ================= NOTIFICATIONS ================= */

export const notificationsAPI = {
getAll: async () => {
const res = await api.get('/notifications');


return {
  notifications: res.data.notifications || [],
  unread_count: res.data.unread_count || 0,
};


},

markAsRead: async () => {
const res = await api.post('/notifications/mark-read');
return res.data;
},
};

/* ================= ADMIN ================= */

export const adminAPI = {
  getKPIs: async () => {
    try {
      const res = await api.get('/admin/kpis');
      return {
        activeUsers: res.data.active_users || 0,
        totalPayouts: res.data.revenue || 0, 
        triggerFrequency: 42, // Mocked as backend doesn't return
        avgPremium: 49, // Mocked
        riskPoolBalance: 4500000,
        claimsRatio: res.data.growth_rate || 0.12,
      };
    } catch (e) {
      return {
        activeUsers: 0,
        totalPayouts: 0,
        triggerFrequency: 0,
        avgPremium: 0,
        riskPoolBalance: 0,
        claimsRatio: 0,
      };
    }
  },
};

/* ================= PAYMENTS ================= */

export const razorpayAPI = {
createOrder: async (data: { amount: number }) => {
const res = await api.post('/payments/create-order', data);


return {
  order_id: res.data.order_id,
  amount: res.data.amount,
  currency: res.data.currency,
  key: res.data.key,
};


},

verifyPayment: async (data: {
razorpay_order_id: string;
razorpay_payment_id: string;
razorpay_signature: string;
}) => {
const res = await api.post('/payments/verify', data);
return res.data;
},
};

/* ================= WALLET ================= */

export const walletAPI = {
  getWallet: async () => {
    const res = await api.get('/wallet/me');
    return res.data;
  },
  getTransactions: async () => {
    const res = await api.get('/wallet/me/transactions');
    return res.data;
  },
  withdraw: async (data: { amount: number; destination_details: any }) => {
    const res = await api.post('/wallet/withdraw', data);
    return res.data;
  },
  getWithdrawals: async () => {
    const res = await api.get('/wallet/me/withdrawals');
    return res.data;
  },
  getAdminWallets: async () => {
    const res = await api.get('/admin/wallets');
    return res.data;
  },
  getAdminWithdrawals: async () => {
    const res = await api.get('/admin/withdrawals');
    return res.data;
  },
  approveWithdrawal: async (id: string) => {
    const res = await api.patch(`/admin/withdrawals/${id}/approve`);
    return res.data;
  },
  rejectWithdrawal: async (id: string, reason: string) => {
    const res = await api.patch(`/admin/withdrawals/${id}/reject`, { reason });
    return res.data;
  },
  freezeWallet: async (workerId: string, freeze: boolean) => {
    const res = await api.post(`/admin/wallets/${workerId}/freeze`, { freeze });
    return res.data;
  },
  getWalletAnalytics: async () => {
    const res = await api.get('/admin/analytics');
    return res.data;
  }
};

/* ================= TRACKING ================= */

export const trackingAPI = {
  getLiveWorkers: async () => {
    const res = await api.get('/admin/workers/live');
    return res.data;
  },
  getWorkerHistory: async (id: string) => {
    const res = await api.get(`/workers/${id}/location/history`);
    return res.data;
  },
  getWorkerSessions: async (id: string) => {
    const res = await api.get(`/workers/${id}/location/sessions`);
    return res.data;
  },
  getOfflineWorkers: async (minutes: number) => {
    const res = await api.get(`/admin/workers/offline-since/${minutes}`);
    return res.data;
  }
};

/* ================= GEOSPATIAL ANALYTICS ================= */

export const geoAPI = {
  getWorkerHeatmap: async () => {
    const res = await api.get('/analytics/heatmap/workers');
    return res.data;
  },
  getFraudHeatmap: async () => {
    const res = await api.get('/analytics/heatmap/fraud');
    return res.data;
  },
  getTriggerHeatmap: async () => {
    const res = await api.get('/analytics/heatmap/triggers');
    return res.data;
  },
  getPayoutHeatmap: async () => {
    const res = await api.get('/analytics/heatmap/payouts');
    return res.data;
  },
  getZoneStats: async (id: string) => {
    const res = await api.get(`/analytics/geo-zones/${id}/stats`);
    return res.data;
  },
  getWorkerClusters: async () => {
    const res = await api.get('/analytics/workers/clusters');
    return res.data;
  },
  getAllZones: async () => {
    const res = await api.get('/api/zones');
    return res.data;
  }
};

