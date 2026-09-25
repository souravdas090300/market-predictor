'use client';

import { useState } from 'react';
import { Grid3x3, Plus, X } from 'lucide-react';

export default function CorrelationPage() {
  const [symbols, setSymbols] = useState(['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']);
  const [newSymbol, setNewSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [correlationData, setCorrelationData] = useState<any>(null);

  const handleAddSymbol = () => {
    if (newSymbol.trim() && !symbols.includes(newSymbol.toUpperCase())) {
      setSymbols([...symbols, newSymbol.toUpperCase()]);
      setNewSymbol('');
    }
  };

  const handleRemoveSymbol = (symbol: string) => {
    setSymbols(symbols.filter(s => s !== symbol));
  };

  const handleAnalyze = async () => {
    setLoading(true);
    
    // Simulate correlation analysis
    setTimeout(() => {
      const matrix = symbols.map(() => 
        symbols.map(() => (Math.random() * 2 - 1))
      );
      
      // Make diagonal 1.0 and matrix symmetric
      for (let i = 0; i < matrix.length; i++) {
        matrix[i][i] = 1.0;
        for (let j = i + 1; j < matrix.length; j++) {
          matrix[j][i] = matrix[i][j];
        }
      }

      const heatmapData = [];
      for (let i = 0; i < symbols.length; i++) {
        for (let j = i + 1; j < symbols.length; j++) {
          heatmapData.push({
            symbol1: symbols[i],
            symbol2: symbols[j],
            correlation: matrix[i][j],
          });
        }
      }

      setCorrelationData({
        symbols,
        correlation_matrix: matrix,
        heatmap_data: heatmapData,
        timestamp: new Date().toISOString(),
      });
      setLoading(false);
    }, 1500);
  };

  const getCorrelationColor = (value: number) => {
    const absValue = Math.abs(value);
    if (value > 0) {
      return `rgba(16, 185, 129, ${absValue})`; // Green for positive
    } else {
      return `rgba(239, 68, 68, ${absValue})`; // Red for negative
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Correlation Analysis</h1>
        <p className="text-slate-400">Analyze correlations between multiple assets</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Symbol Selection */}
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-6">
            <Grid3x3 className="w-5 h-5 text-slate-400" />
            <h2 className="text-xl font-semibold text-white">Select Assets</h2>
          </div>

          <div className="space-y-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={newSymbol}
                onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
                onKeyPress={(e) => e.key === 'Enter' && handleAddSymbol()}
                placeholder="Add symbol (e.g., AAPL)"
                className="flex-1 px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              />
              <button
                onClick={handleAddSymbol}
                className="px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
              >
                <Plus className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-2">
              {symbols.map((symbol) => (
                <div key={symbol} className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
                  <span className="text-white font-medium">{symbol}</span>
                  <button
                    onClick={() => handleRemoveSymbol(symbol)}
                    className="p-1 hover:bg-red-600/20 rounded transition-colors"
                  >
                    <X className="w-4 h-4 text-red-400" />
                  </button>
                </div>
              ))}
            </div>

            <button
              onClick={handleAnalyze}
              disabled={loading || symbols.length < 2}
              className="w-full px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              {loading ? 'Analyzing...' : 'Analyze Correlations'}
            </button>
          </div>
        </div>

        {/* Correlation Heatmap */}
        <div className="lg:col-span-2 bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white">Correlation Matrix</h2>
            {correlationData && (
              <span className="text-slate-400 text-sm">
                Updated: {new Date(correlationData.timestamp).toLocaleTimeString()}
              </span>
            )}
          </div>

          {correlationData ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr>
                    <th className="p-2 text-left text-slate-400 text-sm"></th>
                    {correlationData.symbols.map((symbol: string) => (
                      <th key={symbol} className="p-2 text-center text-white text-sm font-medium">
                        {symbol}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {correlationData.correlation_matrix.map((row: number[], rowIndex: number) => (
                    <tr key={rowIndex}>
                      <td className="p-2 text-white text-sm font-medium">
                        {correlationData.symbols[rowIndex]}
                      </td>
                      {row.map((value: number, colIndex: number) => (
                        <td key={colIndex} className="p-2">
                          <div
                            className="w-12 h-12 flex items-center justify-center rounded text-sm font-medium"
                            style={{
                              backgroundColor: getCorrelationColor(value),
                              color: Math.abs(value) > 0.5 ? 'white' : 'black',
                            }}
                          >
                            {value.toFixed(2)}
                          </div>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <Grid3x3 className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400">Select at least 2 assets to analyze correlations</p>
            </div>
          )}
        </div>
      </div>

      {/* High Correlations */}
      {correlationData && (
        <div className="mt-6 bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <h2 className="text-xl font-semibold text-white mb-4">High Correlations (|r| &gt; 0.7)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {correlationData.heatmap_data
              .filter((item: any) => Math.abs(item.correlation) > 0.7)
              .map((item: any, index: number) => (
                <div key={index} className="bg-slate-900/50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">{item.symbol1}</span>
                    <span className="text-slate-400">vs</span>
                    <span className="text-white font-medium">{item.symbol2}</span>
                  </div>
                  <div className="text-2xl font-bold" style={{ color: item.correlation > 0 ? '#10B981' : '#EF4444' }}>
                    {item.correlation.toFixed(3)}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
