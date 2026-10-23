import React, { useState, useEffect } from 'react';
import { Brain, TrendingUp, Shield, Loader2, AlertCircle } from 'lucide-react';
import axios from 'axios';

const GeminiAI = ({ symbol }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('sentiment');
  const [sentiment, setSentiment] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [strategy, setStrategy] = useState(null);
  const [riskTolerance, setRiskTolerance] = useState('moderate');
  const [investmentHorizon, setInvestmentHorizon] = useState('medium-term');
  const [timeHorizon, setTimeHorizon] = useState('24h');

  const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' && window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://market-predictor-production-0f87.up.railway.app');

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v2/gemini/status`);
      setStatus(response.data);
    } catch (error) {
      console.error('Failed to check Gemini status:', error);
      setStatus({ available: false, enabled: false });
    }
  };

  const analyzeSentiment = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/v2/gemini/sentiment`, {
        symbol,
        news_headlines: [],
        additional_context: ''
      });
      setSentiment(response.data);
    } catch (error) {
      console.error('Sentiment analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPrediction = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/v2/gemini/prediction`, {
        symbol,
        time_horizon: timeHorizon
      });
      setPrediction(response.data);
    } catch (error) {
      console.error('Prediction failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateStrategy = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/v2/gemini/strategy`, {
        symbol,
        risk_tolerance: riskTolerance,
        investment_horizon: investmentHorizon
      });
      setStrategy(response.data);
    } catch (error) {
      console.error('Strategy generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment) => {
    if (sentiment === 'bullish') return 'text-green-500';
    if (sentiment === 'bearish') return 'text-red-500';
    return 'text-gray-500';
  };

  const getRiskColor = (risk) => {
    if (risk === 'low') return 'text-green-500';
    if (risk === 'high') return 'text-red-500';
    return 'text-yellow-500';
  };

  if (!status) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!status.available) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-6 h-6 text-yellow-600 mt-1" />
          <div>
            <h3 className="font-semibold text-yellow-800">Gemini AI Not Available</h3>
            <p className="text-sm text-yellow-700 mt-1">
              Gemini AI service is not configured. Add GEMINI_API_KEY to your environment variables to enable AI features.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Status Badge */}
      <div className="flex items-center gap-2">
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
          status.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
        }`}>
          {status.enabled ? 'Gemini AI Active' : 'Gemini AI Inactive'}
        </span>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        <button
          onClick={() => setActiveTab('sentiment')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'sentiment'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Brain className="w-4 h-4 inline mr-2" />
          Sentiment
        </button>
        <button
          onClick={() => setActiveTab('prediction')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'prediction'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <TrendingUp className="w-4 h-4 inline mr-2" />
          Prediction
        </button>
        <button
          onClick={() => setActiveTab('strategy')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'strategy'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Shield className="w-4 h-4 inline mr-2" />
          Strategy
        </button>
      </div>

      {/* Sentiment Tab */}
      {activeTab === 'sentiment' && (
        <div className="space-y-4">
          <button
            onClick={analyzeSentiment}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Brain className="w-4 h-4" />}
            Analyze Sentiment
          </button>

          {sentiment && (
            <div className="bg-white border rounded-lg p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-lg">Market Sentiment</h3>
                <span className={`font-semibold ${getSentimentColor(sentiment.overall_sentiment)}`}>
                  {sentiment.overall_sentiment?.toUpperCase()}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Sentiment Score</p>
                  <p className="text-2xl font-bold">{(sentiment.sentiment_score * 100).toFixed(0)}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Confidence</p>
                  <p className="text-2xl font-bold">{(sentiment.confidence * 100).toFixed(0)}%</p>
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-2">Risk Level</p>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(sentiment.risk_level)}`}>
                  {sentiment.risk_level?.toUpperCase()}
                </span>
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-2">Key Factors</p>
                <div className="flex flex-wrap gap-2">
                  {sentiment.key_factors?.map((factor, idx) => (
                    <span key={idx} className="px-2 py-1 bg-gray-100 rounded text-sm">
                      {factor}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-2">Summary</p>
                <p className="text-gray-700">{sentiment.summary}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Prediction Tab */}
      {activeTab === 'prediction' && (
        <div className="space-y-4">
          <div className="flex gap-4 items-center">
            <select
              value={timeHorizon}
              onChange={(e) => setTimeHorizon(e.target.value)}
              className="px-3 py-2 border rounded-lg"
            >
              <option value="1h">1 Hour</option>
              <option value="4h">4 Hours</option>
              <option value="24h">24 Hours</option>
              <option value="7d">7 Days</option>
              <option value="30d">30 Days</option>
            </select>
            <button
              onClick={getPrediction}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <TrendingUp className="w-4 h-4" />}
              Get Prediction
            </button>
          </div>

          {prediction && (
            <div className="bg-white border rounded-lg p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-lg">Price Prediction</h3>
                <span className={`font-semibold ${
                  prediction.direction === 'up' ? 'text-green-500' :
                  prediction.direction === 'down' ? 'text-red-500' : 'text-gray-500'
                }`}>
                  {prediction.direction?.toUpperCase()}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Predicted Change</p>
                  <p className={`text-2xl font-bold ${
                    prediction.predicted_change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {prediction.predicted_change_percent >= 0 ? '+' : ''}
                    {prediction.predicted_change_percent?.toFixed(2)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Confidence</p>
                  <p className="text-2xl font-bold">{(prediction.confidence * 100).toFixed(0)}%</p>
                </div>
              </div>

              {prediction.support_level && (
                <div>
                  <p className="text-sm text-gray-500">Support Level</p>
                  <p className="text-lg font-semibold text-green-600">${prediction.support_level?.toFixed(2)}</p>
                </div>
              )}

              {prediction.resistance_level && (
                <div>
                  <p className="text-sm text-gray-500">Resistance Level</p>
                  <p className="text-lg font-semibold text-red-600">${prediction.resistance_level?.toFixed(2)}</p>
                </div>
              )}

              <div>
                <p className="text-sm text-gray-500 mb-2">Key Indicators</p>
                <div className="flex flex-wrap gap-2">
                  {prediction.key_indicators?.map((indicator, idx) => (
                    <span key={idx} className="px-2 py-1 bg-gray-100 rounded text-sm">
                      {indicator}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-2">Reasoning</p>
                <p className="text-gray-700">{prediction.reasoning}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Strategy Tab */}
      {activeTab === 'strategy' && (
        <div className="space-y-4">
          <div className="flex gap-4 items-center">
            <select
              value={riskTolerance}
              onChange={(e) => setRiskTolerance(e.target.value)}
              className="px-3 py-2 border rounded-lg"
            >
              <option value="low">Low Risk</option>
              <option value="moderate">Moderate Risk</option>
              <option value="high">High Risk</option>
            </select>
            <select
              value={investmentHorizon}
              onChange={(e) => setInvestmentHorizon(e.target.value)}
              className="px-3 py-2 border rounded-lg"
            >
              <option value="short-term">Short-term</option>
              <option value="medium-term">Medium-term</option>
              <option value="long-term">Long-term</option>
            </select>
            <button
              onClick={generateStrategy}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
              Generate Strategy
            </button>
          </div>

          {strategy && (
            <div className="bg-white border rounded-lg p-6 space-y-4">
              <h3 className="font-semibold text-lg">{strategy.strategy_name}</h3>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Position Size</p>
                  <p className="text-xl font-bold">{strategy.position_size_percent}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Stop Loss</p>
                  <p className="text-xl font-bold text-red-600">{strategy.stop_loss_percent}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Take Profit</p>
                  <p className="text-xl font-bold text-green-600">{strategy.take_profit_percent}%</p>
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-500">Risk/Reward Ratio</p>
                <p className="text-lg font-semibold">{strategy.risk_reward_ratio?.toFixed(2)}</p>
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-2">Entry Conditions</p>
                <ul className="list-disc list-inside space-y-1">
                  {strategy.entry_conditions?.map((condition, idx) => (
                    <li key={idx} className="text-sm text-gray-700">{condition}</li>
                  ))}
                </ul>
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-2">Exit Conditions</p>
                <ul className="list-disc list-inside space-y-1">
                  {strategy.exit_conditions?.map((condition, idx) => (
                    <li key={idx} className="text-sm text-gray-700">{condition}</li>
                  ))}
                </ul>
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-2">Notes</p>
                <p className="text-gray-700">{strategy.notes}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default GeminiAI;
