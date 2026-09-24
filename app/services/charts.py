"""Advanced charting module for candlestick charts and visualizations."""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import mplfinance as mpf
from pathlib import Path
import json


class CandlestickChart:
    """Generate interactive candlestick charts with technical indicators."""
    
    def __init__(self, symbol: str, data: pd.DataFrame):
        """
        Initialize chart generator.
        
        Args:
            symbol: Asset symbol
            data: DataFrame with OHLC data (columns: open, high, low, close, volume)
        """
        self.symbol = symbol
        self.data = data.copy()
        self._validate_data()
    
    def _validate_data(self):
        """Validate data has required columns."""
        required_cols = ['open', 'high', 'low', 'close']
        for col in required_cols:
            if col not in self.data.columns:
                raise ValueError(f"Missing required column: {col}")
    
    def create_candlestick_chart(self, indicators: List[str] = None) -> go.Figure:
        """
        Create interactive candlestick chart with Plotly.
        
        Args:
            indicators: List of indicators to add (ma, ema, bollinger, volume)
        
        Returns:
            Plotly Figure object
        """
        if indicators is None:
            indicators = ['ma']
        
        fig = make_subplots(
            rows=2 if 'volume' in indicators else 1,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3] if 'volume' in indicators else [1.0],
            subplot_titles=('Price', 'Volume') if 'volume' in indicators else ('Price',)
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=self.data.index,
                open=self.data['open'],
                high=self.data['high'],
                low=self.data['low'],
                close=self.data['close'],
                name='OHLC',
                increasing_line_color='#10B981',
                decreasing_line_color='#EF4444'
            ),
            row=1, col=1
        )
        
        # Add moving averages
        if 'ma' in indicators:
            ma20 = self.data['close'].rolling(window=20).mean()
            ma50 = self.data['close'].rolling(window=50).mean()
            
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=ma20,
                    mode='lines',
                    name='MA20',
                    line=dict(color='#FBBF24', width=1)
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=ma50,
                    mode='lines',
                    name='MA50',
                    line=dict(color='#60A5FA', width=1)
                ),
                row=1, col=1
            )
        
        # Add Bollinger Bands
        if 'bollinger' in indicators:
            ma20 = self.data['close'].rolling(window=20).mean()
            std20 = self.data['close'].rolling(window=20).std()
            upper = ma20 + (std20 * 2)
            lower = ma20 - (std20 * 2)
            
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=upper,
                    mode='lines',
                    name='Upper BB',
                    line=dict(color='#10B981', width=1, dash='dash')
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=lower,
                    mode='lines',
                    name='Lower BB',
                    line=dict(color='#EF4444', width=1, dash='dash'),
                    fill='tonexty',
                    fillcolor='rgba(16, 185, 129, 0.1)'
                ),
                row=1, col=1
            )
        
        # Add volume
        if 'volume' in indicators and 'volume' in self.data.columns:
            colors = np.where(self.data['close'] >= self.data['open'], '#10B981', '#EF4444')
            
            fig.add_trace(
                go.Bar(
                    x=self.data.index,
                    y=self.data['volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.7
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            title=f'{self.symbol} - Candlestick Chart',
            xaxis_rangeslider_visible=False,
            template='plotly_dark',
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_xaxes(
            title_text="Date",
            gridcolor='#2D3748',
            gridwidth=1
        )
        
        fig.update_yaxes(
            title_text="Price",
            gridcolor='#2D3748',
            gridwidth=1
        )
        
        return fig
    
    def to_html(self, indicators: List[str] = None) -> str:
        """Convert chart to HTML string."""
        fig = self.create_candlestick_chart(indicators)
        return fig.to_html(include_plotlyjs=True, full_html=False)
    
    def to_json(self, indicators: List[str] = None) -> str:
        """Convert chart to JSON."""
        fig = self.create_candlestick_chart(indicators)
        return fig.to_json()
    
    def save_chart(self, filepath: str, indicators: List[str] = None):
        """Save chart as HTML file."""
        fig = self.create_candlestick_chart(indicators)
        fig.write_html(filepath)


class TechnicalIndicators:
    """Calculate and visualize technical indicators."""
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator."""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD indicator."""
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands."""
        ma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        
        return {
            'upper': ma + (std * std_dev),
            'middle': ma,
            'lower': ma - (std * std_dev)
        }
    
    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        high = data['high']
        low = data['low']
        close = data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()


def generate_chart_data(symbol: str, ohlc_data: pd.DataFrame, patterns: List[Dict] = None) -> Dict:
    """
    Generate chart data for frontend consumption.
    
    Args:
        symbol: Asset symbol
        ohlc_data: OHLC data DataFrame
        patterns: List of detected candlestick patterns
    
    Returns:
        Dictionary with chart data
    """
    # Ensure data has proper index
    if not isinstance(ohlc_data.index, pd.DatetimeIndex):
        ohlc_data.index = pd.to_datetime(ohlc_data.index)
    
    # Create chart object
    chart = CandlestickChart(symbol, ohlc_data)
    
    # Generate Plotly chart JSON
    chart_json = chart.to_json(indicators=['ma', 'bollinger'])
    
    # Calculate indicators
    indicators = {
        'rsi': TechnicalIndicators.calculate_rsi(ohlc_data['close']).iloc[-1],
        'macd': TechnicalIndicators.calculate_macd(ohlc_data['close']),
        'bollinger': TechnicalIndicators.calculate_bollinger_bands(ohlc_data['close']),
        'atr': TechnicalIndicators.calculate_atr(ohlc_data).iloc[-1]
    }
    
    # Format data for frontend
    ohlc_array = []
    for idx, row in ohlc_data.tail(60).iterrows():
        ohlc_array.append({
            'date': idx.strftime('%Y-%m-%d'),
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close']),
            'volume': float(row.get('volume', 0))
        })
    
    # Format patterns
    formatted_patterns = []
    if patterns:
        for pattern in patterns[-10:]:  # Last 10 patterns
            formatted_patterns.append({
                'date': pattern.get('date'),
                'pattern': pattern.get('pattern'),
                'bias': pattern.get('bias'),
                'meaning': pattern.get('meaning')
            })
    
    return {
        'symbol': symbol,
        'chart_json': chart_json,
        'ohlc_data': ohlc_array,
        'patterns': formatted_patterns,
        'indicators': {
            'rsi': float(indicators['rsi']),
            'macd': {
                'value': float(indicators['macd']['macd'].iloc[-1]),
                'signal': float(indicators['macd']['signal'].iloc[-1]),
                'histogram': float(indicators['macd']['histogram'].iloc[-1])
            },
            'bollinger': {
                'upper': float(indicators['bollinger']['upper'].iloc[-1]),
                'middle': float(indicators['bollinger']['middle'].iloc[-1]),
                'lower': float(indicators['bollinger']['lower'].iloc[-1])
            },
            'atr': float(indicators['atr'])
        }
    }