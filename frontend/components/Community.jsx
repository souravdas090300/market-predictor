import React, { useState, useEffect } from 'react';
import { MessageSquare, Users, BookOpen, Send, Bell, Search, Plus, Loader2 } from 'lucide-react';
import axios from 'axios';

const Community = () => {
  const [activeTab, setActiveTab] = useState('forums');
  const [forums, setForums] = useState([]);
  const [discussions, setDiscussions] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newMessage, setNewMessage] = useState('');
  const [newDiscussion, setNewDiscussion] = useState({ title: '', content: '', forum_id: '' });
  const [showNewDiscussionModal, setShowNewDiscussionModal] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' && window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://market-predictor-production-0f87.up.railway.app');

  useEffect(() => {
    loadForums();
    loadDiscussions();
  }, []);

  const loadForums = () => {
    // Mock data
    setForums([
      { id: 1, name: 'General Discussion', topics: 1245, posts: 8542 },
      { id: 2, name: 'Trading Strategies', topics: 856, posts: 5234 },
      { id: 3, name: 'Market Analysis', topics: 634, posts: 3891 },
      { id: 4, name: 'Technical Analysis', topics: 445, posts: 2678 },
      { id: 5, name: 'Cryptocurrency', topics: 892, posts: 6123 }
    ]);
  };

  const loadDiscussions = () => {
    // Mock data
    setDiscussions([
      {
        id: 1,
        title: 'Best strategies for volatile markets?',
        author: 'trader_joe',
        forum: 'Trading Strategies',
        replies: 23,
        views: 456,
        last_activity: '2 hours ago',
        tags: ['strategy', 'volatility']
      },
      {
        id: 2,
        title: 'AAPL earnings analysis - Q4 2024',
        author: 'market_watcher',
        forum: 'Market Analysis',
        replies: 45,
        views: 892,
        last_activity: '5 hours ago',
        tags: ['earnings', 'AAPL']
      },
      {
        id: 3,
        title: 'Bitcoin halving predictions',
        author: 'crypto_king',
        forum: 'Cryptocurrency',
        replies: 67,
        views: 1234,
        last_activity: '1 day ago',
        tags: ['bitcoin', 'halving']
      }
    ]);
  };

  const loadMessages = (discussionId) => {
    // Mock data
    setMessages([
      { id: 1, author: 'trader_joe', content: 'I think moving average crossovers work well in volatile markets.', timestamp: '2 hours ago' },
      { id: 2, author: 'market_pro', content: 'Agreed. Also consider using Bollinger Bands for volatility signals.', timestamp: '1 hour ago' },
      { id: 3, author: 'newbie_trader', content: 'What timeframes do you recommend?', timestamp: '30 minutes ago' }
    ]);
  };

  const sendMessage = async () => {
    if (!newMessage.trim()) return;

    try {
      // Mock API call
      setMessages([
        ...messages,
        {
          id: messages.length + 1,
          author: 'you',
          content: newMessage,
          timestamp: 'Just now'
        }
      ]);
      setNewMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const createDiscussion = async () => {
    try {
      // Mock API call
      setDiscussions([
        {
          id: discussions.length + 1,
          title: newDiscussion.title,
          author: 'you',
          forum: forums.find(f => f.id === parseInt(newDiscussion.forum_id))?.name || 'General',
          replies: 0,
          views: 0,
          last_activity: 'Just now',
          tags: []
        },
        ...discussions
      ]);
      setShowNewDiscussionModal(false);
      setNewDiscussion({ title: '', content: '', forum_id: '' });
    } catch (error) {
      console.error('Failed to create discussion:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="flex gap-2 border-b">
        <button
          onClick={() => setActiveTab('forums')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'forums'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <BookOpen className="w-4 h-4 inline mr-2" />
          Forums
        </button>
        <button
          onClick={() => setActiveTab('discussions')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'discussions'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <MessageSquare className="w-4 h-4 inline mr-2" />
          Discussions
        </button>
        <button
          onClick={() => setActiveTab('messages')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'messages'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Send className="w-4 h-4 inline mr-2" />
          Messages
        </button>
        <button
          onClick={() => setActiveTab('notifications')}
          className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
            activeTab === 'notifications'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Bell className="w-4 h-4 inline mr-2" />
          Notifications
        </button>
      </div>

      {/* Forums Tab */}
      {activeTab === 'forums' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Community Forums</h2>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search forums..."
                  className="pl-10 pr-4 py-2 border rounded-lg"
                />
              </div>
            </div>
          </div>

          <div className="grid gap-3">
            {forums.map((forum) => (
              <div
                key={forum.id}
                className="bg-white border rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => {
                  setActiveTab('discussions');
                }}
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold text-lg">{forum.name}</h3>
                    <div className="flex gap-4 mt-2 text-sm text-gray-600">
                      <span>{forum.topics} topics</span>
                      <span>{forum.posts} posts</span>
                    </div>
                  </div>
                  <Users className="w-6 h-6 text-gray-400" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Discussions Tab */}
      {activeTab === 'discussions' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Recent Discussions</h2>
            <button
              onClick={() => setShowNewDiscussionModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              New Discussion
            </button>
          </div>

          <div className="space-y-3">
            {discussions.map((discussion) => (
              <div
                key={discussion.id}
                className="bg-white border rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => {
                  loadMessages(discussion.id);
                  setActiveTab('messages');
                }}
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-lg">{discussion.title}</h3>
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                    {discussion.forum}
                  </span>
                </div>

                <div className="flex gap-4 text-sm text-gray-600 mb-2">
                  <span>by {discussion.author}</span>
                  <span>{discussion.replies} replies</span>
                  <span>{discussion.views} views</span>
                </div>

                <div className="flex justify-between items-center">
                  <div className="flex gap-2">
                    {discussion.tags.map((tag, idx) => (
                      <span key={idx} className="px-2 py-1 bg-gray-100 rounded text-xs">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <span className="text-sm text-gray-500">{discussion.last_activity}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Messages Tab */}
      {activeTab === 'messages' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Discussion Thread</h2>

          <div className="bg-white border rounded-lg p-6 space-y-4">
            {messages.map((message) => (
              <div key={message.id} className="border-b pb-4 last:border-0">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold">{message.author}</span>
                  <span className="text-sm text-gray-500">{message.timestamp}</span>
                </div>
                <p className="text-gray-700">{message.content}</p>
              </div>
            ))}

            <div className="flex gap-2 pt-4">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 border rounded-lg"
              />
              <button
                onClick={sendMessage}
                disabled={!newMessage.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                Send
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Notifications</h2>

          <div className="space-y-3">
            {[
              { type: 'reply', message: 'trader_joe replied to your discussion', time: '2 hours ago' },
              { type: 'mention', message: 'market_pro mentioned you in a post', time: '5 hours ago' },
              { type: 'like', message: 'Your post received 10 likes', time: '1 day ago' },
              { type: 'follow', message: 'newbie_trader started following you', time: '2 days ago' }
            ].map((notification, idx) => (
              <div key={idx} className="bg-white border rounded-lg p-4 flex items-center gap-4">
                <div className={`p-2 rounded-full ${
                  notification.type === 'reply' ? 'bg-blue-100 text-blue-600' :
                  notification.type === 'mention' ? 'bg-purple-100 text-purple-600' :
                  notification.type === 'like' ? 'bg-pink-100 text-pink-600' :
                  'bg-green-100 text-green-600'
                }`}>
                  <Bell className="w-4 h-4" />
                </div>
                <div className="flex-1">
                  <p className="text-gray-700">{notification.message}</p>
                  <p className="text-sm text-gray-500">{notification.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* New Discussion Modal */}
      {showNewDiscussionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg">
            <h3 className="text-xl font-semibold mb-4">Create New Discussion</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Forum
                </label>
                <select
                  value={newDiscussion.forum_id}
                  onChange={(e) => setNewDiscussion({ ...newDiscussion, forum_id: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  <option value="">Select a forum...</option>
                  {forums.map(forum => (
                    <option key={forum.id} value={forum.id}>{forum.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  value={newDiscussion.title}
                  onChange={(e) => setNewDiscussion({ ...newDiscussion, title: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="Discussion title..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Content
                </label>
                <textarea
                  value={newDiscussion.content}
                  onChange={(e) => setNewDiscussion({ ...newDiscussion, content: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  rows={6}
                  placeholder="Write your discussion content..."
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-6">
              <button
                onClick={() => setShowNewDiscussionModal(false)}
                className="px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={createDiscussion}
                disabled={!newDiscussion.title || !newDiscussion.content}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Create Discussion
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Community;
