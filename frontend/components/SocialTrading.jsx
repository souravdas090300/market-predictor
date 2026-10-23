import React, { useState, useEffect } from 'react';
import { Users, TrendingUp, Star, Share2, Heart, Loader2, Plus } from 'lucide-react';
import axios from 'axios';

const SocialTrading = () => {
  const [activeTab, setActiveTab] = useState('leaderboard');
  const [leaderboard, setLeaderboard] = useState([]);
  const [strategies, setStrategies] = useState([]);
  const [myStrategies, setMyStrategies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newStrategy, setNewStrategy] = useState({
    name: '',
    description: '',
    rules: {}
  });

  const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' && window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://market-predictor-production-0f87.up.railway.app');

  useEffect(() => {
    loadLeaderboard();
    loadStrategies();
  }, []);

  const loadLeaderboard = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/v2/social/leaderboard?period=1m&limit=10`);
      setLeaderboard(response.data.leaderboard || []);
    } catch (error) {
      console.error('Failed to load leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStrategies = async () => {
    try {
      // Mock data for now
      setStrategies([
        {
          id: 'strat_1',
          name: 'Bull Run Strategy',
          author: 'trader1',
          description: 'Momentum-based strategy for bullish markets',
          followers: 450,
          rating: 4.5,
          return: 0.35
        },
        {
          id: 'strat_2',
          name: 'Value Hunters',
          author: 'trader2',
          description: 'Value investing with focus on undervalued stocks',
          followers: 320,
          rating: 4.2,
          return: 0.28
        }
      ]);
    } catch (error) {
      console.error('Failed to load strategies:', error);
    }
  };

  const followStrategy = async (strategyId, allocation) => {
    try {
      await axios.post(`${API_URL}/api/v2/social/follow`, {
        strategy_id: strategyId,
        allocation: allocation
      });
      alert('Strategy followed successfully!');
    } catch (error) {
      console.error('Failed to follow strategy:', error);
      alert('Failed to follow strategy');
    }
  };

  const rateStrategy = async (strategyId, rating) => {
    try {
      await axios.post(`${API_URL}/api/v2/social/rate`, {
        strategy_id: strategyId,
        rating: rating
      });
      alert('Rating submitted!');
      loadLeaderboard();
    } catch (error) {
      console.error('Failed to rate strategy:', error);
      alert('Failed to submit rating');
    }
  };

  const createStrategy = async () => {
    try {
      await axios.post(`${API_URL}/api/v2/social/strategies`, {
        strategy_name: newStrategy.name,
        description: newStrategy.description,
        rules: newStrategy.rules
      });
      alert('Strategy created successfully!');
      setShowCreateModal(false);
      setNewStrategy({ name: '', description: '', rules: {} });
      loadStrategies();
    } catch (error) {
      console.error('Failed to create strategy:', error);
      alert('Failed to create strategy');
    }
  };

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${i < Math.floor(rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ));
  };

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="flex gap-2 border-b">
        <button
          onClick={() => setActiveTab('leaderboard')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'leaderboard'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <TrendingUp className="w-4 h-4 inline mr-2" />
          Leaderboard
        </button>
        <button
          onClick={() => setActiveTab('strategies')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'strategies'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Users className="w-4 h-4 inline mr-2" />
          Strategies
        </button>
        <button
          onClick={() => setActiveTab('my-strategies')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'my-strategies'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Share2 className="w-4 h-4 inline mr-2" />
          My Strategies
        </button>
      </div>

      {/* Leaderboard Tab */}
      {activeTab === 'leaderboard' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Top Traders</h2>
            <button
              onClick={loadLeaderboard}
              disabled={loading}
              className="px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Refresh'}
            </button>
          </div>

          <div className="bg-white border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Rank</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Strategy</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Author</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">Return</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">Followers</th>
                  <th className="px-4 py-3 text-center text-sm font-medium text-gray-500">Rating</th>
                  <th className="px-4 py-3 text-center text-sm font-medium text-gray-500">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {leaderboard.map((item, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <span className={`font-bold ${
                        item.rank === 1 ? 'text-yellow-500' :
                        item.rank === 2 ? 'text-gray-400' :
                        item.rank === 3 ? 'text-amber-600' : 'text-gray-600'
                      }`}>
                        #{item.rank}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-medium">{item.strategy_name}</td>
                    <td className="px-4 py-3 text-gray-600">{item.author}</td>
                    <td className="px-4 py-3 text-right font-semibold text-green-600">
                      {(item.return * 100).toFixed(1)}%
                    </td>
                    <td className="px-4 py-3 text-right text-gray-600">{item.followers}</td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex justify-center gap-0.5">
                        {renderStars(item.rating || 4)}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => followStrategy(item.strategy_id, 0.1)}
                        className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                      >
                        Follow
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Strategies Tab */}
      {activeTab === 'strategies' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Browse Strategies</h2>

          <div className="grid gap-4">
            {strategies.map((strategy) => (
              <div key={strategy.id} className="bg-white border rounded-lg p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-semibold text-lg">{strategy.name}</h3>
                    <p className="text-sm text-gray-500">by {strategy.author}</p>
                  </div>
                  <div className="flex items-center gap-1">
                    {renderStars(strategy.rating)}
                  </div>
                </div>

                <p className="text-gray-700 mb-4">{strategy.description}</p>

                <div className="flex gap-6 text-sm text-gray-600 mb-4">
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    <span>{strategy.followers} followers</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" />
                    <span className="text-green-600 font-semibold">
                      {(strategy.return * 100).toFixed(1)}% return
                    </span>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => followStrategy(strategy.id, 0.1)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                  >
                    <Heart className="w-4 h-4" />
                    Follow (10%)
                  </button>
                  <button
                    onClick={() => rateStrategy(strategy.id, 5)}
                    className="px-4 py-2 border rounded-lg hover:bg-gray-50 flex items-center gap-2"
                  >
                    <Star className="w-4 h-4" />
                    Rate
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* My Strategies Tab */}
      {activeTab === 'my-strategies' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">My Strategies</h2>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Create Strategy
            </button>
          </div>

          {myStrategies.length === 0 ? (
            <div className="bg-gray-50 border rounded-lg p-8 text-center">
              <Share2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">You haven't created any strategies yet.</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create Your First Strategy
              </button>
            </div>
          ) : (
            <div className="grid gap-4">
              {myStrategies.map((strategy) => (
                <div key={strategy.id} className="bg-white border rounded-lg p-6">
                  <h3 className="font-semibold text-lg">{strategy.name}</h3>
                  <p className="text-gray-700 mt-2">{strategy.description}</p>
                  <div className="flex gap-4 mt-4 text-sm text-gray-600">
                    <span>{strategy.followers} followers</span>
                    <span>Rating: {strategy.rating.toFixed(1)}/5</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Create Strategy Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg">
            <h3 className="text-xl font-semibold mb-4">Create New Strategy</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Strategy Name
                </label>
                <input
                  type="text"
                  value={newStrategy.name}
                  onChange={(e) => setNewStrategy({ ...newStrategy, name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="My Awesome Strategy"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={newStrategy.description}
                  onChange={(e) => setNewStrategy({ ...newStrategy, description: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  rows={4}
                  placeholder="Describe your strategy..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rules (JSON)
                </label>
                <textarea
                  value={JSON.stringify(newStrategy.rules, null, 2)}
                  onChange={(e) => {
                    try {
                      setNewStrategy({ ...newStrategy, rules: JSON.parse(e.target.value) });
                    } catch {
                      // Invalid JSON, ignore
                    }
                  }}
                  className="w-full px-3 py-2 border rounded-lg font-mono text-sm"
                  rows={4}
                  placeholder='{"entry_condition": "...", "exit_condition": "..."}'
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={createStrategy}
                disabled={!newStrategy.name || !newStrategy.description}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Create Strategy
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SocialTrading;
