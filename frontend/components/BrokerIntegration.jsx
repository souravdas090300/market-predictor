import React, { useState, useEffect } from 'react';
import { Link, RefreshCw, Wallet, ArrowUpRight, ArrowDownRight, Loader2, Plus, X } from 'lucide-react';
import axios from 'axios';

const BrokerIntegration = () => {
  const [connectedBrokers, setConnectedBrokers] = useState([]);
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showConnectModal, setShowConnectModal] = useState(false);
  const [newBroker, setNewBroker] = useState({
    name: '',
    api_key: '',
    api_secret: ''
  });
  const [selectedBroker, setSelectedBroker] = useState(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' && window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://market-predictor-production-0f87.up.railway.app');

  useEffect(() => {
    loadConnectedBrokers();
  }, []);

  const loadConnectedBrokers = () => {
    // Mock data - in production, this would come from API
    setConnectedBrokers([
      { id: 'acc_1', name: 'Interactive Brokers', status: 'connected', account_id: 'acc_12345' }
    ]);
  };

  const connectBroker = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/v2/brokers/connect`, {
        broker_name: newBroker.name,
        api_key: newBroker.api_key,
        api_secret: newBroker.api_secret
      });

      if (response.data.success) {
        setConnectedBrokers([
          ...connectedBrokers,
          {
            id: response.data.account_id,
            name: newBroker.name,
            status: 'connected',
            account_id: response.data.account_id
          }
        ]);
        setShowConnectModal(false);
        setNewBroker({ name: '', api_key: '', api_secret: '' });
        alert('Broker connected successfully!');
      }
    } catch (error) {
      console.error('Failed to connect broker:', error);
      alert('Failed to connect broker');
    } finally {
      setLoading(false);
    }
  };

  const syncBrokerData = async (brokerName) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/v2/brokers/sync`, {
        broker_name: brokerName
      });

      if (response.data.success) {
        alert('Data synced successfully!');
        loadPositions(brokerName);
      }
    } catch (error) {
      console.error('Failed to sync broker data:', error);
      alert('Failed to sync data');
    } finally {
      setLoading(false);
    }
  };

  const loadPositions = async (brokerName) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/v2/brokers/positions/${brokerName}`);
      setPositions(response.data.positions || []);
      setSelectedBroker(brokerName);
    } catch (error) {
      console.error('Failed to load positions:', error);
    } finally {
      setLoading(false);
    }
  };

  const executeOrder = async (brokerName, symbol, side, quantity) => {
    try {
      await axios.post(`${API_URL}/api/v2/brokers/orders`, {
        broker_name: brokerName,
        symbol,
        side,
        quantity
      });
      alert('Order submitted successfully!');
      loadPositions(brokerName);
    } catch (error) {
      console.error('Failed to execute order:', error);
      alert('Failed to submit order');
    }
  };

  return (
    <div className="space-y-6">
      {/* Connected Brokers */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Connected Brokers</h2>
        <button
          onClick={() => setShowConnectModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Connect Broker
        </button>
      </div>

      {connectedBrokers.length === 0 ? (
        <div className="bg-gray-50 border rounded-lg p-8 text-center">
          <Link className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No brokers connected yet.</p>
          <button
            onClick={() => setShowConnectModal(true)}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Connect Your First Broker
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {connectedBrokers.map((broker) => (
            <div key={broker.id} className="bg-white border rounded-lg p-6">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-semibold text-lg">{broker.name}</h3>
                  <p className="text-sm text-gray-500">Account: {broker.account_id}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    {broker.status}
                  </span>
                  <button
                    onClick={() => syncBrokerData(broker.name)}
                    disabled={loading}
                    className="p-2 hover:bg-gray-100 rounded-lg"
                    title="Sync Data"
                  >
                    {loading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <RefreshCw className="w-4 h-4" />
                    )}
                  </button>
                  <button
                    onClick={() => loadPositions(broker.name)}
                    disabled={loading}
                    className="px-3 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 text-sm"
                  >
                    View Positions
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Positions */}
      {selectedBroker && positions.length > 0 && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Positions - {selectedBroker}</h2>
            <div className="flex gap-2">
              <span className="px-3 py-1 bg-blue-50 text-blue-700 rounded-lg text-sm">
                <Wallet className="w-4 h-4 inline mr-1" />
                Cash: $25,000
              </span>
              <span className="px-3 py-1 bg-green-50 text-green-700 rounded-lg text-sm">
                Buying Power: $30,000
              </span>
            </div>
          </div>

          <div className="bg-white border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Symbol</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">Quantity</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">Current Price</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">Value</th>
                  <th className="px-4 py-3 text-center text-sm font-medium text-gray-500">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {positions.map((position, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{position.symbol}</td>
                    <td className="px-4 py-3 text-right">{position.quantity}</td>
                    <td className="px-4 py-3 text-right">${position.current_price.toFixed(2)}</td>
                    <td className="px-4 py-3 text-right font-semibold">
                      ${position.value.toFixed(2)}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex justify-center gap-2">
                        <button
                          onClick={() => executeOrder(selectedBroker, position.symbol, 'buy', 1)}
                          className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 flex items-center gap-1"
                        >
                          <ArrowUpRight className="w-3 h-3" />
                          Buy
                        </button>
                        <button
                          onClick={() => executeOrder(selectedBroker, position.symbol, 'sell', 1)}
                          className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 flex items-center gap-1"
                        >
                          <ArrowDownRight className="w-3 h-3" />
                          Sell
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Connect Broker Modal */}
      {showConnectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold">Connect Broker</h3>
              <button
                onClick={() => setShowConnectModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Broker Name
                </label>
                <select
                  value={newBroker.name}
                  onChange={(e) => setNewBroker({ ...newBroker, name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  <option value="">Select a broker...</option>
                  <option value="interactive_brokers">Interactive Brokers</option>
                  <option value="alpaca">Alpaca</option>
                  <option value="td_ameritrade">TD Ameritrade</option>
                  <option value="robinhood">Robinhood</option>
                  <option value="webull">Webull</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Key
                </label>
                <input
                  type="password"
                  value={newBroker.api_key}
                  onChange={(e) => setNewBroker({ ...newBroker, api_key: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="Enter your API key"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Secret
                </label>
                <input
                  type="password"
                  value={newBroker.api_secret}
                  onChange={(e) => setNewBroker({ ...newBroker, api_secret: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="Enter your API secret"
                />
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <p className="text-sm text-yellow-800">
                  <strong>Security Note:</strong> Your API credentials are encrypted and stored securely.
                  Never share your API keys with others.
                </p>
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-6">
              <button
                onClick={() => setShowConnectModal(false)}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={connectBroker}
                disabled={loading || !newBroker.name || !newBroker.api_key || !newBroker.api_secret}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Connect'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BrokerIntegration;
