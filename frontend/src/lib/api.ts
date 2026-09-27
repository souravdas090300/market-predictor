import axios from 'axios';
import type { 
  Signal, 
  WatchlistItem, 
  Quote, 
  MaterialAnalysis, 
  RiskAnalysis,
  StrategyOptimization,
  CorrelationData,
  NewsItem,
  User,
  AuthTokens,
  APIKey
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
          refresh_token: refreshToken,
        });
        
        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// Signal endpoints
export const signalAPI = {
  getSignal: async (symbol: string, news: boolean = true, refresh: boolean = false): Promise<Signal> => {
    const response = await api.get(`/api/signal/${symbol}`, {
      params: { news, refresh }
    });
    return response.data;
  },

  getWatchlist: async (): Promise<WatchlistItem[]> => {
    const response = await api.get('/api/watchlist');
    return response.data;
  },

  getSignalHistory: async (symbol: string, days: number = 90): Promise<any> => {
    const response = await api.get(`/api/signal/${symbol}/history`, {
      params: { days }
    });
    return response.data;
  },

  getBulkSignals: async (symbols: string[]): Promise<Signal[]> => {
    const response = await api.post('/api/bulk', { symbols });
    return response.data;
  },

  exportSignals: async (symbol: string, format: 'csv' | 'json' = 'csv'): Promise<any> => {
    const response = await api.get(`/api/export/${symbol}`, {
      params: { format }
    });
    return response.data;
  },
};

// Quote endpoints
export const quoteAPI = {
  getQuote: async (symbol: string): Promise<Quote> => {
    const response = await api.get(`/api/quote/${symbol}`);
    return response.data;
  },

  getQuotes: async (symbols: string[]): Promise<Record<string, Quote>> => {
    const response = await api.get('/api/quotes', {
      params: { symbols: symbols.join(',') }
    });
    return response.data;
  },

  getLiveQuotes: (symbols: string[]): EventSource => {
    const url = `${API_BASE_URL}/api/live/quotes?symbols=${encodeURIComponent(symbols.join(','))}`;
    return new EventSource(url);
  },
};

// Material endpoints
export const materialAPI = {
  analyzeMaterial: async (symbol: string, text: string, combine: boolean = true): Promise<any> => {
    const response = await api.post('/api/material', {
      symbol,
      text,
      combine
    });
    return response.data;
  },

  analyzeFromURL: async (symbol: string, url: string, combine: boolean = true): Promise<any> => {
    const response = await api.post('/api/material-from-url', {
      symbol,
      text: url,
      combine
    });
    return response.data;
  },

  analyzeFromFile: async (symbol: string, file: File, combine: boolean = true): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('symbol', symbol);
    formData.append('combine', combine.toString());

    const response = await api.post('/api/material-from-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Risk analysis endpoints
export const riskAPI = {
  calculateRisk: async (params: {
    symbol: string;
    entry_price: number;
    stop_loss: number;
    take_profit: number;
    account_balance?: number;
    max_risk_percent?: number;
  }): Promise<RiskAnalysis> => {
    const response = await api.post('/api/risk/calculate', params);
    return response.data;
  },
};

// Strategy optimization endpoints
export const strategyAPI = {
  optimizeStrategy: async (params: {
    symbol: string;
    strategy_type?: string;
    lookback_min?: number;
    lookback_max?: number;
    holding_min?: number;
    holding_max?: number;
  }): Promise<StrategyOptimization> => {
    const response = await api.post('/api/strategy/optimize', params);
    return response.data;
  },
};

// Correlation analysis endpoints
export const correlationAPI = {
  analyzeCorrelation: async (symbols: string[]): Promise<CorrelationData> => {
    const response = await api.post('/api/correlation/analyze', { symbols });
    return response.data;
  },
};

// News endpoints
export const newsAPI = {
  getNews: async (symbol: string, assetClass: string = 'stock', maxArticles: number = 20): Promise<{ news: NewsItem[] }> => {
    const response = await api.get(`/api/news/${symbol}`, {
      params: { asset_class: assetClass, max_articles: maxArticles }
    });
    return response.data;
  },
};

// Authentication endpoints
export const authAPI = {
  register: async (username: string, email: string, password: string): Promise<any> => {
    const response = await api.post('/api/auth/register', {
      username,
      email,
      password
    });
    return response.data;
  },

  login: async (username: string, password: string): Promise<AuthTokens & { user: any }> => {
    const response = await api.post('/api/auth/login', {
      username,
      password
    });
    return response.data;
  },

  refreshToken: async (refreshToken: string): Promise<AuthTokens> => {
    const response = await api.post('/api/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  updateProfile: async (profileData: Partial<User['profile']>): Promise<any> => {
    const response = await api.put('/api/user/profile', profileData);
    return response.data;
  },

  getSubscription: async (): Promise<User['subscription']> => {
    const response = await api.get('/api/user/subscription');
    return response.data;
  },

  updateSubscription: async (plan: string, durationDays: number = 30): Promise<any> => {
    const response = await api.put('/api/user/subscription', {
      plan,
      duration_days: durationDays
    });
    return response.data;
  },

  createAPIKey: async (name: string, scopes: string[] = ['read', 'write']): Promise<APIKey> => {
    const response = await api.post('/api/auth/api-key', { name, scopes });
    return response.data;
  },

  listAPIKeys: async (): Promise<{ api_keys: APIKey[]; count: number }> => {
    const response = await api.get('/api/auth/api-keys');
    return response.data;
  },

  revokeAPIKey: async (keyId: string): Promise<any> => {
    const response = await api.delete(`/api/auth/api-key/${keyId}`);
    return response.data;
  },

  googleOAuthRedirect: async (): Promise<any> => {
    const response = await api.get('/api/auth/oauth/google');
    return response.data;
  },

  oauthCallback: async (provider: string, code: string, redirectUri: string): Promise<any> => {
    const response = await api.post('/api/auth/oauth/callback', {
      provider,
      code,
      redirect_uri: redirectUri
    });
    return response.data;
  },
};

// Admin endpoints
export const adminAPI = {
  getConfig: async (): Promise<any> => {
    const response = await api.get("/api/admin/config");
    return response.data;
  },

  updateConfig: async (config: any): Promise<any> => {
    const response = await api.put("/api/admin/config", config);
    return response.data;
  },

  getUsers: async (): Promise<any> => {
    const response = await api.get("/api/admin/users");
    return response.data;
  },

  updateUser: async (userId: string, userData: any): Promise<any> => {
    const response = await api.put(`/api/admin/users/${userId}`, userData);
    return response.data;
  },

  getSystemStatus: async (): Promise<any> => {
    const response = await api.get("/api/admin/status");
    return response.data;
  },
};

// Alerts endpoints
export const alertsAPI = {
  getAlerts: async (): Promise<any[]> => {
    const response = await api.get('/api/alerts');
    return response.data;
  },

  createAlert: async (alert: {
    symbol: string;
    type: 'price' | 'signal';
    condition: 'above' | 'below' | 'equals';
    value: number;
  }): Promise<any> => {
    const response = await api.post('/api/alerts', alert);
    return response.data;
  },

  deleteAlert: async (alertId: string): Promise<any> => {
    const response = await api.delete(`/api/alerts/${alertId}`);
    return response.data;
  },

  toggleAlert: async (alertId: string): Promise<any> => {
    const response = await api.put(`/api/alerts/${alertId}/toggle`);
    return response.data;
  },
};

// Backtest endpoints
export const backtestAPI = {
  runBacktest: async (config: {
    symbol: string;
    strategy: string;
    start_date: string;
    end_date: string;
    initial_capital: number;
    position_size: number;
    stop_loss: number;
    take_profit: number;
  }): Promise<any> => {
    const response = await api.post('/api/backtest', config);
    return response.data;
  },

  getBacktestResults: async (backtestId: string): Promise<any> => {
    const response = await api.get(`/api/backtest/${backtestId}`);
    return response.data;
  },
};

// Portfolio endpoints
export const portfolioAPI = {
  getPortfolio: async (): Promise<any> => {
    const response = await api.get('/api/portfolio');
    return response.data;
  },

  addHolding: async (holding: {
    symbol: string;
    quantity: number;
    average_cost: number;
  }): Promise<any> => {
    const response = await api.post('/api/portfolio/holdings', holding);
    return response.data;
  },

  removeHolding: async (symbol: string): Promise<any> => {
    const response = await api.delete(`/api/portfolio/holdings/${symbol}`);
    return response.data;
  },

  updateHolding: async (symbol: string, updates: any): Promise<any> => {
    const response = await api.put(`/api/portfolio/holdings/${symbol}`, updates);
    return response.data;
  },
};

// Rate limits endpoints
export const rateLimitsAPI = {
  getRateLimits: async (): Promise<any[]> => {
    const response = await api.get('/api/rate-limits');
    return response.data;
  },

  getUsageStats: async (): Promise<any> => {
    const response = await api.get('/api/rate-limits/stats');
    return response.data;
  },
};
