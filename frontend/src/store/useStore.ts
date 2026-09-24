import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, Signal, WatchlistItem } from '@/types';

interface AppState {
  // Auth state
  user: User | null;
  isAuthenticated: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  
  // UI state
  theme: 'light' | 'dark' | 'auto';
  sidebarOpen: boolean;
  currentSymbol: string | null;
  
  // Data state
  watchlist: WatchlistItem[];
  currentSignal: Signal | null;
  quotes: Record<string, { price: number; change_pct: number }>;
  
  // Actions
  setUser: (user: User | null) => void;
  setAuthTokens: (accessToken: string, refreshToken: string) => void;
  logout: () => void;
  setTheme: (theme: 'light' | 'dark' | 'auto') => void;
  setSidebarOpen: (open: boolean) => void;
  setCurrentSymbol: (symbol: string | null) => void;
  setWatchlist: (watchlist: WatchlistItem[]) => void;
  setCurrentSignal: (signal: Signal | null) => void;
  updateQuote: (symbol: string, quote: { price: number; change_pct: number }) => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial state
      user: null,
      isAuthenticated: false,
      accessToken: null,
      refreshToken: null,
      theme: 'dark',
      sidebarOpen: true,
      currentSymbol: null,
      watchlist: [],
      currentSignal: null,
      quotes: {},
      
      // Actions
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setAuthTokens: (accessToken, refreshToken) => set({ accessToken, refreshToken }),
      logout: () => set({ 
        user: null, 
        isAuthenticated: false, 
        accessToken: null, 
        refreshToken: null,
        currentSignal: null,
        currentSymbol: null
      }),
      setTheme: (theme) => set({ theme }),
      setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
      setCurrentSymbol: (currentSymbol) => set({ currentSymbol }),
      setWatchlist: (watchlist) => set({ watchlist }),
      setCurrentSignal: (currentSignal) => set({ currentSignal }),
      updateQuote: (symbol, quote) => set((state) => ({
        quotes: { ...state.quotes, [symbol]: quote }
      })),
    }),
    {
      name: 'market-predictor-storage',
      partialize: (state) => ({
        theme: state.theme,
        sidebarOpen: state.sidebarOpen,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
    }
  )
);
