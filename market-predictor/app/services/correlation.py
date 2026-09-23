"""Correlation analysis and visualization module."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px


class CorrelationAnalyzer:
    """Analyze correlations between multiple assets."""
    
    def __init__(self, data: Dict[str, pd.DataFrame]):
        """
        Initialize correlation analyzer.
        
        Args:
            data: Dictionary mapping symbols to price DataFrames
        """
        self.data = data
        self.prices = self._align_data()
    
    def _align_data(self) -> pd.DataFrame:
        """Align price data by date."""
        # Extract close prices for each symbol
        close_data = {}
        
        for symbol, df in self.data.items():
            if 'close' in df.columns:
                close_data[symbol] = df['close']
            elif 'c' in df.columns:
                close_data[symbol] = df['c']
        
        # Create DataFrame and align by index
        prices_df = pd.DataFrame(close_data)
        return prices_df.dropna()
    
    def calculate_correlation_matrix(self, method: str = 'pearson') -> pd.DataFrame:
        """
        Calculate correlation matrix.
        
        Args:
            method: Correlation method ('pearson', 'spearman', 'kendall')
        
        Returns:
            Correlation matrix DataFrame
        """
        if len(self.prices.columns) < 2:
            raise ValueError("Need at least 2 assets to calculate correlation")
        
        # Calculate daily returns
        returns = self.prices.pct_change().dropna()
        
        # Calculate correlation
        correlation_matrix = returns.corr(method=method)
        
        return correlation_matrix
    
    def get_correlation_heatmap(self, method: str = 'pearson') -> go.Figure:
        """
        Create interactive correlation heatmap.
        
        Args:
            method: Correlation method
        
        Returns:
            Plotly Figure object
        """
        corr_matrix = self.calculate_correlation_matrix(method)
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            colorbar=dict(title="Correlation Coefficient")
        ))
        
        fig.update_layout(
            title='Asset Correlation Matrix',
            xaxis_title='Assets',
            yaxis_title='Assets',
            template='plotly_dark',
            height=600
        )
        
        return fig
    
    def find_highly_correlated_pairs(self, threshold: float = 0.7) -> List[Dict]:
        """
        Find pairs with correlation above threshold.
        
        Args:
            threshold: Correlation threshold
        
        Returns:
            List of correlated pairs with their correlation values
        """
        corr_matrix = self.calculate_correlation_matrix()
        
        correlated_pairs = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                correlation = corr_matrix.iloc[i, j]
                
                if abs(correlation) >= threshold:
                    correlated_pairs.append({
                        'asset1': corr_matrix.columns[i],
                        'asset2': corr_matrix.columns[j],
                        'correlation': correlation,
                        'type': 'positive' if correlation > 0 else 'negative'
                    })
        
        # Sort by absolute correlation
        correlated_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        return correlated_pairs
    
    def calculate_portfolio_diversification(self, weights: Optional[Dict[str, float]] = None) -> Dict:
        """
        Calculate portfolio diversification metrics.
        
        Args:
            weights: Dictionary of asset weights (sum should be 1.0)
        
        Returns:
            Dictionary with diversification metrics
        """
        corr_matrix = self.calculate_correlation_matrix()
        
        if weights is None:
            # Equal weight portfolio
            n_assets = len(corr_matrix.columns)
            weights = {symbol: 1.0 / n_assets for symbol in corr_matrix.columns}
        
        # Convert weights to array
        weight_array = np.array([weights.get(col, 0) for col in corr_matrix.columns])
        
        # Calculate portfolio variance
        portfolio_variance = np.dot(weight_array, np.dot(corr_matrix, weight_array))
        
        # Calculate diversification ratio (vs equal weight portfolio)
        equal_weight_variance = np.sum(corr_matrix.values) / (len(corr_matrix) ** 2)
        diversification_ratio = equal_weight_variance / portfolio_variance if portfolio_variance > 0 else 0
        
        # Calculate concentration (Herfindahl-Hirschman Index)
        hhi = sum(w ** 2 for w in weight_array)
        
        return {
            'portfolio_variance': portfolio_variance,
            'portfolio_std': np.sqrt(portfolio_variance),
            'diversification_ratio': diversification_ratio,
            'concentration_index': hhi,
            'diversification_score': 1 - hhi,
            'average_correlation': corr_matrix.values[np.triu_indices_from(len(corr_matrix), k=1)].mean()
        }


def generate_correlation_data(symbols: List[str], data: Dict[str, pd.DataFrame]) -> Dict:
    """
    Generate correlation data for frontend consumption.
    
    Args:
        symbols: List of asset symbols
        data: Dictionary mapping symbols to price DataFrames
    
    Returns:
        Dictionary with correlation data and visualization
    """
    analyzer = CorrelationAnalyzer(data)
    
    # Calculate correlation matrix
    corr_matrix = analyzer.calculate_correlation_matrix()
    
    # Get heatmap figure
    heatmap_fig = analyzer.get_correlation_heatmap()
    
    # Find highly correlated pairs
    correlated_pairs = analyzer.find_highly_correlated_pairs(threshold=0.5)
    
    # Calculate diversification metrics (equal weights)
    div_metrics = analyzer.calculate_portfolio_diversification()
    
    # Format matrix for frontend
    matrix_data = []
    for i, row_label in enumerate(corr_matrix.index):
        row_data = []
        for j, col_label in enumerate(corr_matrix.columns):
            row_data.append({
                'asset_x': row_label,
                'asset_y': col_label,
                'correlation': float(corr_matrix.iloc[i, j])
            })
        matrix_data.append(row_data)
    
    return {
        'symbols': symbols,
        'correlation_matrix': matrix_data,
        'heatmap_json': heatmap_fig.to_json(),
        'correlated_pairs': correlated_pairs,
        'diversification_metrics': div_metrics,
        'generated_at': pd.Timestamp.now().isoformat()
    }