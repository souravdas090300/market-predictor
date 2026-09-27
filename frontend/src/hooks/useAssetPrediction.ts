import { useState, useEffect } from 'react';

// Types for asset predictions
export interface Asset {
  symbol: string;
  name: string;
  class: 'stock' | 'crypto' | 'forex' | 'commodity';
  price: number;
  change_pct: number;
  volume: number;
  market_cap?: number;
  high_24h: number;
  low_24h: number;
}

export interface AssetPrediction {
  symbol: string;
  timeframe: string;
  current_price: number;
  predicted_price: number;
  predicted_change_pct: number;
  confidence: number;
  confidence_interval: {
    low: number;
    high: number;
  };
  expected_high: number;
  expected_low: number;
  expected_average: number;
  trend: 'bullish' | 'bearish' | 'neutral';
  timestamp: string;
}

export interface AssetHistoricalData {
  symbol: string;
  timeframe: string;
  data: Array<{
    timestamp: string;
    price: number;
    volume: number;
  }>;
}

export interface AssetComparison {
  symbol: string;
  name: string;
  current_price: number;
  predictions: {
    timeframe: string;
    predicted_price: number;
    change_pct: number;
  }[];
}

// Mock data for development
const MOCK_ASSETS: Asset[] = [
  // Stocks
  { symbol: 'AAPL', name: 'Apple Inc.', class: 'stock', price: 178.35, change_pct: 2.34, volume: 52340000, market_cap: 2800000000000, high_24h: 180.12, low_24h: 175.23 },
  { symbol: 'MSFT', name: 'Microsoft Corporation', class: 'stock', price: 378.91, change_pct: 1.87, volume: 22340000, market_cap: 2810000000000, high_24h: 382.45, low_24h: 374.12 },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', class: 'stock', price: 141.80, change_pct: -0.45, volume: 18450000, market_cap: 1780000000000, high_24h: 143.23, low_24h: 140.56 },
  { symbol: 'NVDA', name: 'NVIDIA Corporation', class: 'stock', price: 495.22, change_pct: 3.56, volume: 45670000, market_cap: 1220000000000, high_24h: 501.34, low_24h: 488.90 },
  { symbol: 'TSLA', name: 'Tesla Inc.', class: 'stock', price: 245.67, change_pct: -1.23, volume: 98760000, market_cap: 780000000000, high_24h: 251.23, low_24h: 242.34 },
  
  // Crypto
  { symbol: 'BTC-USD', name: 'Bitcoin', class: 'crypto', price: 43567.89, change_pct: 2.45, volume: 28500000000, market_cap: 850000000000, high_24h: 44123.45, low_24h: 42890.12 },
  { symbol: 'ETH-USD', name: 'Ethereum', class: 'crypto', price: 2345.67, change_pct: 1.89, volume: 15400000000, market_cap: 280000000000, high_24h: 2389.45, low_24h: 2312.34 },
  { symbol: 'BNB-USD', name: 'Binance Coin', class: 'crypto', price: 312.45, change_pct: -0.67, volume: 890000000, market_cap: 48000000000, high_24h: 318.90, low_24h: 308.23 },
  { symbol: 'SOL-USD', name: 'Solana', class: 'crypto', price: 98.76, change_pct: 4.23, volume: 1230000000, market_cap: 42000000000, high_24h: 102.34, low_24h: 94.56 },
  { symbol: 'XRP-USD', name: 'Ripple', class: 'crypto', price: 0.6234, change_pct: 1.12, volume: 1560000000, market_cap: 34000000000, high_24h: 0.6345, low_24h: 0.6123 },
  
  // Forex
  { symbol: 'EURUSD=X', name: 'EUR/USD', class: 'forex', price: 1.0876, change_pct: 0.12, volume: 45000000000, high_24h: 1.0898, low_24h: 1.0854 },
  { symbol: 'GBPUSD=X', name: 'GBP/USD', class: 'forex', price: 1.2634, change_pct: -0.08, volume: 32000000000, high_24h: 1.2678, low_24h: 1.2601 },
  
  // Commodities
  { symbol: 'GC=F', name: 'Gold', class: 'commodity', price: 1945.67, change_pct: 0.34, volume: 89000000, high_24h: 1952.34, low_24h: 1938.90 },
  { symbol: 'CL=F', name: 'Crude Oil', class: 'commodity', price: 85.23, change_pct: -1.45, volume: 234000000, high_24h: 87.45, low_24h: 84.12 },
  { symbol: 'NG=F', name: 'Natural Gas', class: 'commodity', price: 2.87, change_pct: 2.67, volume: 67000000, high_24h: 2.94, low_24h: 2.78 },
];

const TIMEFRAMES = ['1h', '4h', '1d', '1w', '1m', '3m'];

// Generate mock prediction data
const generateMockPrediction = (symbol: string, timeframe: string): AssetPrediction => {
  const asset = MOCK_ASSETS.find(a => a.symbol === symbol) || MOCK_ASSETS[0];
  const currentPrice = asset.price;
  
  // Generate prediction based on timeframe
  const timeframeMultiplier = {
    '1h': 0.001,
    '4h': 0.003,
    '1d': 0.01,
    '1w': 0.03,
    '1m': 0.08,
    '3m': 0.15
  }[timeframe] || 0.01;
  
  const randomChange = (Math.random() - 0.4) * timeframeMultiplier; // Slightly bullish bias
  const predictedPrice = currentPrice * (1 + randomChange);
  const confidence = 75 + Math.random() * 20; // 75-95% confidence
  
  const predictedChangePct = ((predictedPrice - currentPrice) / currentPrice) * 100;
  const trend = predictedChangePct > 0.5 ? 'bullish' : predictedChangePct < -0.5 ? 'bearish' : 'neutral';
  
  const confidenceRange = currentPrice * timeframeMultiplier * 0.5;
  
  return {
    symbol,
    timeframe,
    current_price: currentPrice,
    predicted_price: predictedPrice,
    predicted_change_pct: predictedChangePct,
    confidence: Math.round(confidence),
    confidence_interval: {
      low: predictedPrice - confidenceRange,
      high: predictedPrice + confidenceRange
    },
    expected_high: predictedPrice + confidenceRange * 0.7,
    expected_low: predictedPrice - confidenceRange * 0.7,
    expected_average: predictedPrice,
    trend,
    timestamp: new Date().toISOString()
  };
};

// Generate mock historical data
const generateMockHistoricalData = (symbol: string, timeframe: string): AssetHistoricalData => {
  const asset = MOCK_ASSETS.find(a => a.symbol === symbol) || MOCK_ASSETS[0];
  const basePrice = asset.price;
  const points = 30; // 30 data points
  
  const data = Array.from({ length: points }, (_, i) => {
    const randomChange = (Math.random() - 0.5) * 0.02;
    const price = basePrice * (1 + randomChange * (i / points));
    const timestamp = new Date(Date.now() - (points - i) * 24 * 60 * 60 * 1000).toISOString();
    
    return {
      timestamp,
      price,
      volume: Math.floor(Math.random() * 100000000)
    };
  });
  
  return {
    symbol,
    timeframe,
    data
  };
};

// Hook: Get all assets
export const useAssetsList = () => {
  const [data, setData] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadAssets = async () => {
      try {
        setLoading(true);
        // In production, this would be an API call
        // const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/assets`);
        // const data = await response.json();
        
        // Mock data for development
        await new Promise(resolve => setTimeout(resolve, 500));
        setData(MOCK_ASSETS);
        setError(null);
      } catch (err) {
        setError('Failed to load assets');
        console.error('Error loading assets:', err);
      } finally {
        setLoading(false);
      }
    };

    loadAssets();
  }, []);

  return { data, loading, error, refetch: () => loadAssets() };
};

// Hook: Get asset details
export const useAssetDetails = (symbol: string) => {
  const [data, setData] = useState<Asset | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!symbol) return;

    const loadAssetDetails = async () => {
      try {
        setLoading(true);
        // In production, this would be an API call
        // const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/assets/${symbol}`);
        // const data = await response.json();
        
        // Mock data for development
        await new Promise(resolve => setTimeout(resolve, 300));
        const asset = MOCK_ASSETS.find(a => a.symbol === symbol);
        setData(asset || null);
        setError(null);
      } catch (err) {
        setError('Failed to load asset details');
        console.error('Error loading asset details:', err);
      } finally {
        setLoading(false);
      }
    };

    loadAssetDetails();
  }, [symbol]);

  return { data, loading, error, refetch: () => loadAssetDetails() };
};

// Hook: Get asset price prediction
export const useAssetPricePrediction = (symbol: string, timeframe: string = '1d') => {
  const [data, setData] = useState<AssetPrediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!symbol) return;

    const loadPrediction = async () => {
      try {
        setLoading(true);
        // In production, this would be an API call
        // const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/assets/${symbol}/predictions?timeframe=${timeframe}`);
        // const data = await response.json();
        
        // Mock data for development
        await new Promise(resolve => setTimeout(resolve, 400));
        const prediction = generateMockPrediction(symbol, timeframe);
        setData(prediction);
        setError(null);
      } catch (err) {
        setError('Failed to load prediction');
        console.error('Error loading prediction:', err);
      } finally {
        setLoading(false);
      }
    };

    loadPrediction();
  }, [symbol, timeframe]);

  return { data, loading, error, refetch: () => loadPrediction() };
};

// Hook: Get all timeframes for an asset
export const useAssetAllPredictions = (symbol: string) => {
  const [data, setData] = useState<AssetPrediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!symbol) return;

    const loadAllPredictions = async () => {
      try {
        setLoading(true);
        // In production, this would be an API call
        // const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/assets/${symbol}/predictions`);
        // const data = await response.json();
        
        // Mock data for development
        await new Promise(resolve => setTimeout(resolve, 600));
        const predictions = TIMEFRAMES.map(timeframe => 
          generateMockPrediction(symbol, timeframe)
        );
        setData(predictions);
        setError(null);
      } catch (err) {
        setError('Failed to load predictions');
        console.error('Error loading predictions:', err);
      } finally {
        setLoading(false);
      }
    };

    loadAllPredictions();
  }, [symbol]);

  return { data, loading, error, refetch: () => loadAllPredictions() };
};

// Hook: Compare multiple assets
export const useAssetComparison = (symbols: string[]) => {
  const [data, setData] = useState<AssetComparison[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (symbols.length === 0) return;

    const loadComparison = async () => {
      try {
        setLoading(true);
        // In production, this would be an API call
        // const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/assets/compare?symbols=${symbols.join(',')}`);
        // const data = await response.json();
        
        // Mock data for development
        await new Promise(resolve => setTimeout(resolve, 500));
        const comparison = symbols.map(symbol => {
          const asset = MOCK_ASSETS.find(a => a.symbol === symbol);
          if (!asset) return null;
          
          return {
            symbol: asset.symbol,
            name: asset.name,
            current_price: asset.price,
            predictions: TIMEFRAMES.map(timeframe => {
              const pred = generateMockPrediction(symbol, timeframe);
              return {
                timeframe: pred.timeframe,
                predicted_price: pred.predicted_price,
                change_pct: pred.predicted_change_pct
              };
            })
          };
        }).filter((item): item is AssetComparison => item !== null);
        
        setData(comparison);
        setError(null);
      } catch (err) {
        setError('Failed to load comparison');
        console.error('Error loading comparison:', err);
      } finally {
        setLoading(false);
      }
    };

    loadComparison();
  }, [symbols]);

  return { data, loading, error, refetch: () => loadComparison() };
};

// Hook: Get historical data
export const useAssetHistoricalData = (symbol: string, timeframe: string = '1d') => {
  const [data, setData] = useState<AssetHistoricalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!symbol) return;

    const loadHistoricalData = async () => {
      try {
        setLoading(true);
        // In production, this would be an API call
        // const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/assets/${symbol}/historical?timeframe=${timeframe}`);
        // const data = await response.json();
        
        // Mock data for development
        await new Promise(resolve => setTimeout(resolve, 400));
        const historical = generateMockHistoricalData(symbol, timeframe);
        setData(historical);
        setError(null);
      } catch (err) {
        setError('Failed to load historical data');
        console.error('Error loading historical data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadHistoricalData();
  }, [symbol, timeframe]);

  return { data, loading, error, refetch: () => loadHistoricalData() };
};

// Helper function to format price
export const formatPrice = (price: number, symbol: string): string => {
  if (symbol.includes('USD') && !symbol.includes('USD=X')) {
    // Crypto - show more decimal places for lower values
    if (price < 1) return `$${price.toFixed(4)}`;
    if (price < 10) return `$${price.toFixed(2)}`;
    return `$${price.toFixed(2)}`;
  }
  if (symbol.includes('USD=X')) {
    // Forex - show 4 decimal places
    return price.toFixed(4);
  }
  // Stocks and commodities
  return `$${price.toFixed(2)}`;
};

// Helper function to format percentage
export const formatPercentage = (pct: number): string => {
  const sign = pct >= 0 ? '+' : '';
  return `${sign}${pct.toFixed(2)}%`;
};

// Helper function to get trend color
export const getTrendColor = (trend: string): string => {
  switch (trend) {
    case 'bullish': return 'text-green-400';
    case 'bearish': return 'text-red-400';
    default: return 'text-yellow-400';
  }
};

// Helper function to get trend icon
export const getTrendIcon = (trend: string) => {
  switch (trend) {
    case 'bullish': return '📈';
    case 'bearish': return '📉';
    default: return '➡️';
  }
};