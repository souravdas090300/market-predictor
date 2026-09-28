'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function LandingPage() {
  const router = useRouter();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
      router.push('/');
    }

    // Handle scroll effect
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [router]);

  return (
    <div className="bg-slate-950 text-white min-h-screen font-sans">
      {/* Navigation */}
      <nav
        className={`sticky top-0 z-50 transition-all duration-300 ${
          isScrolled ? 'bg-slate-950/95 backdrop-blur-lg border-b border-slate-800' : 'bg-transparent'
        }`}
        style={{ padding: '1rem 2rem' }}
      >
        <div className="flex justify-between items-center">
          <div className="text-2xl font-bold bg-gradient-to-r from-green-500 to-blue-500 bg-clip-text text-transparent">
            📈 Market Predictor Pro
          </div>

          <div className="flex gap-8 items-center">
            <a href="#features" className="text-slate-300 hover:text-white transition-colors cursor-pointer">Features</a>
            <a href="#pricing" className="text-slate-300 hover:text-white transition-colors cursor-pointer">Pricing</a>
            <Link href="/auth/login">
              <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all duration-300 font-semibold">
                Sign In
              </button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section
        className="py-24 text-center min-h-screen flex flex-col justify-center items-center"
        style={{
          background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)',
          padding: '6rem 2rem'
        }}
      >
        <h1
          className="text-5xl md:text-6xl font-extrabold mb-4 leading-tight"
          style={{
            background: 'linear-gradient(135deg, #10B981 0%, #3B82F6 50%, #FBBF24 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}
        >
          Trade Smarter, Not Harder
        </h1>

        <p className="text-xl text-slate-300 max-w-2xl mb-8 leading-relaxed">
          AI-powered market predictions, sentiment analysis, and automated trading. Make data-driven decisions in real-time.
        </p>

        <div className="flex gap-4 justify-center mb-12">
          <Link href="/auth/register">
            <button className="px-10 py-4 text-lg bg-green-600 hover:bg-green-700 text-slate-950 rounded-lg transition-all duration-300 font-bold hover:-translate-y-0.5 hover:shadow-lg hover:shadow-green-500/30">
              Start Free Trial
            </button>
          </Link>
          <Link href="/auth/login">
            <button className="px-10 py-4 text-lg bg-transparent text-blue-500 border-2 border-blue-500 rounded-lg transition-all duration-300 font-bold hover:bg-blue-500/10 hover:-translate-y-0.5">
              Sign In
            </button>
          </Link>
        </div>

        {/* Feature Pills */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-4xl mt-12">
          <FeaturePill icon="📊" title="Live Trading" desc="Real-time market data & signals" />
          <FeaturePill icon="🤖" title="AI Predictions" desc="ML-powered price forecasts" />
          <FeaturePill icon="📈" title="Advanced Analytics" desc="Professional backtesting tools" />
          <FeaturePill icon="🔔" title="Smart Alerts" desc="Price & sentiment notifications" />
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 max-w-6xl mx-auto px-4">
        <h2 className="text-4xl font-bold text-center mb-12 text-white">
          Powerful Features
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <FeatureCard
            icon="⚡"
            title="Advanced Backtesting"
            description="Test your strategies on historical data with comprehensive metrics including Sharpe ratio, max drawdown, and win rate."
          />
          <FeatureCard
            icon="😊"
            title="Sentiment Analysis"
            description="Analyze news, social media, and fear & greed index to gauge market sentiment in real-time."
          />
          <FeatureCard
            icon="🎯"
            title="Smart Alerts"
            description="Get instant notifications for price alerts, sentiment shifts, and technical signals via email or SMS."
          />
          <FeatureCard
            icon="💼"
            title="Portfolio Optimization"
            description="Automatic rebalancing recommendations, tax-loss harvesting, and risk analysis."
          />
          <FeatureCard
            icon="🤖"
            title="ML Predictions"
            description="Ensemble of LSTM, ARIMA, XGBoost, and Prophet models for accurate price predictions."
          />
          <FeatureCard
            icon="🏦"
            title="Broker Integration"
            description="Connect to Alpaca, Interactive Brokers, and more for live trading execution."
          />
        </div>
      </section>

      {/* Stats Section */}
      <section
        className="py-16 mx-4"
        style={{
          background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%)',
          margin: '3rem 0'
        }}
      >
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 text-center">
          <StatCard number="50K+" label="Active Traders" />
          <StatCard number="$2.3B+" label="Volume Analyzed" />
          <StatCard number="98.5%" label="Prediction Accuracy" />
          <StatCard number="24/7" label="Real-time Monitoring" />
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 max-w-6xl mx-auto px-4">
        <h2 className="text-4xl font-bold text-center mb-12 text-white">
          Pricing Plans
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <PricingCard
            name="Starter"
            price="$0"
            period="/month"
            features={['Up to 5 watchlists', 'Basic signals', 'Email alerts', 'Community access']}
            highlighted={false}
          />
          <PricingCard
            name="Professional"
            price="$49"
            period="/month"
            features={['Unlimited watchlists', 'Advanced analytics', 'SMS & Email alerts', 'Sentiment analysis', 'ML predictions']}
            highlighted={true}
          />
          <PricingCard
            name="Enterprise"
            price="Custom"
            period="pricing"
            features={['API access', 'Broker integration', 'Custom strategies', 'Dedicated support', 'White-label option']}
            highlighted={false}
          />
        </div>
      </section>

      {/* CTA Section */}
      <section
        className="py-16 mx-4 text-center rounded-xl"
        style={{
          background: 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
          margin: '4rem 2rem'
        }}
      >
        <h2 className="text-3xl font-bold mb-4 text-slate-950">
          Ready to Start Trading Smarter?
        </h2>
        <p className="text-lg mb-8 text-slate-900/90">
          Join thousands of traders using Market Predictor Pro
        </p>
        <Link href="/auth/register">
          <button className="px-10 py-4 text-lg bg-slate-950 text-green-500 rounded-lg transition-all duration-300 font-bold hover:scale-105 hover:shadow-xl">
            Get Started Free
          </button>
        </Link>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 text-center text-slate-400">
        <p>&copy; 2024 Market Predictor Pro. All rights reserved.</p>
      </footer>
    </div>
  );
}

function FeaturePill({ icon, title, desc }: { icon: string; title: string; desc: string }) {
  return (
    <div
      className="p-6 bg-white/5 rounded-lg border border-white/10 backdrop-blur-lg transition-all duration-300 hover:bg-green-500/10 hover:border-green-500 hover:-translate-y-1"
    >
      <div className="text-4xl mb-2">{icon}</div>
      <div className="font-semibold mb-1">{title}</div>
      <div className="text-sm text-slate-400">{desc}</div>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div
      className="p-8 bg-slate-800/50 rounded-xl border border-slate-700 transition-all duration-300 hover:bg-slate-800 hover:border-blue-500 hover:-translate-y-2"
    >
      <div className="text-5xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2 text-white">
        {title}
      </h3>
      <p className="text-slate-400 leading-relaxed">{description}</p>
    </div>
  );
}

function StatCard({ number, label }: { number: string; label: string }) {
  return (
    <div>
      <div className="text-4xl font-bold text-green-500 mb-2">
        {number}
      </div>
      <div className="text-slate-400">{label}</div>
    </div>
  );
}

function PricingCard({ name, price, period, features, highlighted }: { name: string; price: string; period: string; features: string[]; highlighted: boolean }) {
  return (
    <div
      className={`p-8 rounded-xl border transition-all duration-300 relative hover:-translate-y-2 ${
        highlighted
          ? 'bg-green-500/15 border-2 border-green-500 hover:shadow-xl hover:shadow-green-500/20'
          : 'bg-slate-800/50 border border-slate-700 hover:shadow-xl hover:shadow-blue-500/20'
      }`}
    >
      {highlighted && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-green-500 text-slate-950 px-4 py-1 rounded-full text-sm font-semibold">
          MOST POPULAR
        </div>
      )}

      <h3 className={`text-2xl font-bold mb-1 ${highlighted ? 'mt-4' : ''}`}>
        {name}
      </h3>
      <div className="mb-6">
        <span className="text-4xl font-bold text-green-500">{price}</span>
        <span className="text-slate-400">{period}</span>
      </div>

      <ul className="mb-8 space-y-3">
        {features.map((feature, i) => (
          <li key={i} className="text-slate-400 flex items-center">
            <span className="text-green-500 mr-2">✓</span>
            {feature}
          </li>
        ))}
      </ul>

      <button
        className={`w-full py-3 rounded-lg font-semibold transition-all duration-300 ${
          highlighted
            ? 'bg-green-500 text-slate-950 hover:bg-green-600'
            : 'bg-blue-500/20 text-blue-500 border border-blue-500 hover:bg-blue-500/30'
        }`}
      >
        Get Started
      </button>
    </div>
  );
}
