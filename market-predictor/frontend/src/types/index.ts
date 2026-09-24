// Core types for the Market Predictor application

export interface Signal {
  symbol: string;
  name: string;
  class: 'stock' | 'crypto' | 'forex' | 'commodity';
  signal: 'bullish' | 'bearish' | 'neutral';
  probability_up: number;
  conviction: number;
  model_probability_up: number;
  sentiment: {
    score: number;
    headline_count: number;
    headlines: Array<{
      title: string;
      link: string;
      source: string;
      score: number;
    }>;
  };
  backtest?: {
    accuracy: number;
    baseline_accuracy: number;
    samples: number;
  };
  indicators: {
    rsi_14: number;
    vs_sma_50_pct: number;
    volatility_20d_pct: number;
  };
  candles: Array<{
    d: string;
    o: number;
    h: number;
    l: number;
    c: number;
  }>;
  candle_patterns: Array<{
    pattern: string;
    bias: string;
    meaning: string;
  }>;
  as_of: string;
  note?: string;
  live?: {
    price: number;
    change_pct: number;
  };
}

export interface WatchlistItem {
  symbol: string;
  name: string;
  class: 'stock' | 'crypto' | 'forex' | 'commodity';
}

export interface Quote {
  price: number;
  change_pct: number;
}

export interface MaterialAnalysis {
  label: 'bullish' | 'bearish' | 'neutral';
  score: number;
  conviction: number;
  key_phrases: string[];
}

export interface RiskAnalysis {
  symbol: string;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  position_size: number;
  risk_amount: number;
  risk_percent: number;
  potential_profit: number;
  potential_loss: number;
  risk_reward_ratio: number;
  recommended_position_size: number;
  max_position_size: number;
}

export interface StrategyOptimization {
  symbol: string;
  strategy_type: string;
  best_parameters: {
    lookback_period: number;
    holding_period: number;
    threshold: number;
  };
  performance: {
    total_return: number;
    win_rate: number;
    max_drawdown: number;
    sharpe_ratio: number;
  };
  backtest_results: Array<{
    date: string;
    signal: string;
    entry_price: number;
    exit_price: number;
    return: number;
  }>;
}

export interface CorrelationData {
  symbols: string[];
  correlation_matrix: number[][];
  heatmap_data: Array<{
    symbol1: string;
    symbol2: string;
    correlation: number;
  }>;
  timestamp: string;
}

export interface NewsItem {
  title: string;
  link: string;
  source: string;
  published_date: string;
  sentiment: number;
  summary?: string;
}

export interface User {
  user_id: string;
  username: string;
  email: string;
  email_verified: boolean;
  created_at: string;
  last_login?: string;
  roles: string[];
  preferences: UserPreferences;
  profile: UserProfile;
  subscription: Subscription;
  oauth_providers: string[];
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
  notifications: {
    email: boolean;
    push: boolean;
    price_alerts: boolean;
    signal_alerts: boolean;
  };
  default_market: string;
  watchlist: string[];
}

export interface UserProfile {
  first_name?: string;
  last_name?: string;
  bio?: string;
  location?: string;
  website?: string;
  avatar_url?: string;
}

export interface Subscription {
  plan: 'free' | 'basic' | 'pro' | 'enterprise';
  status: 'active' | 'past_due' | 'canceled' | 'expired';
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  features: string[];
}

export interface ModelTrainingConfig {
  symbol: string;
  lookback_days: number;
  features: string[];
  model_type: 'xgboost' | 'lightgbm' | 'random_forest';
  validation_method: 'walk_forward' | 'time_series_split';
  test_size: number;
  hyperparameters: Record<string, any>;
}

export interface ModelTrainingResult {
  model_id: string;
  symbol: string;
  training_status: 'completed' | 'failed' | 'in_progress';
  accuracy: number;
  feature_importance: Array<{
    feature: string;
    importance: number;
  }>;
  training_time: number;
  trained_at: string;
  model_path: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface APIKey {
  key_id: string;
  name: string;
  scopes: string[];
  created_at: string;
  last_used?: string;
  is_active: boolean;
}
