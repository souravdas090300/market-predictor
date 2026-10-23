/**
 * Custom hook for WebSocket connections
 * Supports both single symbol and watchlist subscriptions
 */

import { useState, useEffect, useRef, useCallback } from 'react';

export function useWebSocket(url, options = {}) {
  const {
    onMessage = null,
    onError = null,
    onClose = null,
    onOpen = null,
    reconnect = true,
    reconnectInterval = 3000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const shouldReconnectRef = useRef(reconnect);

  useEffect(() => {
    shouldReconnectRef.current = reconnect;
  }, [reconnect]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        if (onOpen) onOpen();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          if (onMessage) onMessage(data);
        } catch (e) {
          console.error('Error parsing WebSocket message:', e);
        }
      };

      ws.onerror = (event) => {
        const errorMessage = 'WebSocket error occurred';
        setError(errorMessage);
        if (onError) onError(event);
      };

      ws.onclose = () => {
        setIsConnected(false);
        if (onClose) onClose();

        // Attempt reconnection if enabled
        if (shouldReconnectRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };
    } catch (e) {
      setError(e.message);
      if (onError) onError(e);
    }
  }, [url, onMessage, onError, onClose, onOpen, reconnectInterval]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const sendMessage = useCallback((message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    error,
    sendMessage,
    connect,
    disconnect,
  };
}

/**
 * Hook for watchlist WebSocket (multiple symbols)
 */
export function useWatchlistWebSocket(apiUrl, symbols = []) {
  const [priceUpdates, setPriceUpdates] = useState({});
  const [lastUpdateTime, setLastUpdateTime] = useState(null);
  const wsUrl = `${apiUrl}/api/v2/assets/ws/watchlist`.replace('http', 'ws');

  const handleMessage = useCallback((data) => {
    if (data.type === 'watchlist_update' && data.updates) {
      const updatesMap = {};
      data.updates.forEach(update => {
        updatesMap[update.symbol] = update;
      });
      setPriceUpdates(prev => ({ ...prev, ...updatesMap }));
      setLastUpdateTime(new Date());
    }
  }, []);

  const { isConnected, sendMessage, connect, disconnect } = useWebSocket(wsUrl, {
    onMessage: handleMessage,
  });

  // Subscribe to symbols when connection is open
  useEffect(() => {
    if (isConnected && symbols.length > 0) {
      sendMessage({
        action: 'subscribe',
        symbols: symbols,
      });
    }
  }, [isConnected, symbols, sendMessage]);

  // Update subscription when symbols change
  useEffect(() => {
    if (isConnected) {
      sendMessage({
        action: 'subscribe',
        symbols: symbols,
      });
    }
  }, [symbols, sendMessage, isConnected]);

  return {
    isConnected,
    priceUpdates,
    lastUpdateTime,
    sendMessage,
    connect,
    disconnect,
  };
}

/**
 * Hook for single symbol WebSocket
 */
export function useSymbolWebSocket(apiUrl, symbol) {
  const [priceData, setPriceData] = useState(null);
  const [lastUpdateTime, setLastUpdateTime] = useState(null);
  const wsUrl = `${apiUrl}/api/v2/assets/ws/price/${symbol}`.replace('http', 'ws');

  const handleMessage = useCallback((data) => {
    if (data.type === 'price_update') {
      setPriceData(data);
      setLastUpdateTime(new Date());
    }
  }, []);

  const { isConnected, connect, disconnect } = useWebSocket(wsUrl, {
    onMessage: handleMessage,
  });

  useEffect(() => {
    if (symbol) {
      connect();
    } else {
      disconnect();
    }
    return () => disconnect();
  }, [symbol, connect, disconnect]);

  return {
    isConnected,
    priceData,
    lastUpdateTime,
  };
}
