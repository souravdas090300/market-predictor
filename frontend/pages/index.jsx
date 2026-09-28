/**
 * Market Predictor Pro - Landing Page
 * Stunning, professional homepage for unauthenticated users
 */

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

export default function LandingPage() {
  const router = useRouter();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('auth-token');
    if (token) {
      setIsAuthenticated(true);
      router.push('/dashboard');
    }

    // Handle scroll effect
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [router]);

  return (
    <div style={{ backgroundColor: '#0F172A', color: '#F9FAFB', minHeight: '100vh', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      {/* Navigation */}
      <nav
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 1000,
          backgroundColor: isScrolled ? 'rgba(15, 23, 42, 0.95)' : 'transparent',
          backdropFilter: 'blur(10px)',
          borderBottom: isScrolled ? '1px solid #2D3748' : 'none',
          padding: '1rem 2rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          transition: 'all 0.3s ease'
        }}
      >
        <div style={{ fontSize: '24px', fontWeight: 'bold', background: 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          📈 Market Predictor Pro
        </div>

        <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
          <a href="#features" style={{ color: '#D1D5DB', textDecoration: 'none', cursor: 'pointer' }}>Features</a>
          <a href="#pricing" style={{ color: '#D1D5DB', textDecoration: 'none', cursor: 'pointer' }}>Pricing</a>
          <Link href="/auth/login">
            <button style={{
              padding: '0.5rem 1.5rem',
              backgroundColor: '#3B82F6',
              color: '#F9FAFB',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => e.target.style.backgroundColor = '#2563EB'}
            onMouseLeave={(e) => e.target.style.backgroundColor = '#3B82F6'}
            >
              Sign In
            </button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{
        background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)',
        padding: '6rem 2rem',
        textAlign: 'center',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <h1 style={{
          fontSize: '3.5rem',
          fontWeight: '800',
          marginBottom: '1rem',
          background: 'linear-gradient(135deg, #10B981 0%, #3B82F6 50%, #FBBF24 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          lineHeight: '1.2'
        }}>
          Trade Smarter, Not Harder
        </h1>

        <p style={{
          fontSize: '1.25rem',
          color: '#D1D5DB',
          maxWidth: '600px',
          marginBottom: '2rem',
          lineHeight: '1.6'
        }}>
          AI-powered market predictions, sentiment analysis, and automated trading. Make data-driven decisions in real-time.
        </p>

        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginBottom: '3rem' }}>
          <Link href="/auth/signup">
            <button style={{
              padding: '1rem 2.5rem',
              fontSize: '1.1rem',
              backgroundColor: '#10B981',
              color: '#0F172A',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '700',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = '#059669';
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 10px 25px rgba(16, 185, 129, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = '#10B981';
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = 'none';
            }}
            >
              Start Free Trial
            </button>
          </Link>
          <Link href="/auth/login">
            <button style={{
              padding: '1rem 2.5rem',
              fontSize: '1.1rem',
              backgroundColor: 'transparent',
              color: '#3B82F6',
              border: '2px solid #3B82F6',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '700',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
              e.target.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = 'transparent';
              e.target.style.transform = 'translateY(0)';
            }}
            >
              Sign In
            </button>
          </Link>
        </div>

        {/* Feature Pills */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', maxWidth: '800px', marginTop: '3rem' }}>
          <FeaturePill icon="📊" title="Live Trading" desc="Real-time market data & signals" />
          <FeaturePill icon="🤖" title="AI Predictions" desc="ML-powered price forecasts" />
          <FeaturePill icon="📈" title="Advanced Analytics" desc="Professional backtesting tools" />
          <FeaturePill icon="🔔" title="Smart Alerts" desc="Price & sentiment notifications" />
        </div>
      </section>

      {/* Features Section */}
      <section id="features" style={{ padding: '5rem 2rem', maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{
          fontSize: '2.5rem',
          fontWeight: '700',
          textAlign: 'center',
          marginBottom: '3rem',
          color: '#F9FAFB'
        }}>
          Powerful Features
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
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
      <section style={{
        background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%)',
        padding: '4rem 2rem',
        margin: '3rem 0'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem', textAlign: 'center' }}>
          <StatCard number="50K+" label="Active Traders" />
          <StatCard number="$2.3B+" label="Volume Analyzed" />
          <StatCard number="98.5%" label="Prediction Accuracy" />
          <StatCard number="24/7" label="Real-time Monitoring" />
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" style={{ padding: '5rem 2rem', maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{
          fontSize: '2.5rem',
          fontWeight: '700',
          textAlign: 'center',
          marginBottom: '3rem',
          color: '#F9FAFB'
        }}>
          Pricing Plans
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
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
      <section style={{
        background: 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
        padding: '4rem 2rem',
        textAlign: 'center',
        borderRadius: '12px',
        margin: '4rem 2rem'
      }}>
        <h2 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '1rem', color: '#0F172A' }}>
          Ready to Start Trading Smarter?
        </h2>
        <p style={{ fontSize: '1.1rem', marginBottom: '2rem', color: 'rgba(15, 23, 42, 0.9)' }}>
          Join thousands of traders using Market Predictor Pro
        </p>
        <Link href="/auth/signup">
          <button style={{
            padding: '1rem 2.5rem',
            fontSize: '1.1rem',
            backgroundColor: '#0F172A',
            color: '#10B981',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: '700',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = 'scale(1.05)';
            e.target.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.3)';
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = 'scale(1)';
            e.target.style.boxShadow = 'none';
          }}
          >
            Get Started Free
          </button>
        </Link>
      </section>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid #2D3748',
        padding: '2rem',
        textAlign: 'center',
        color: '#D1D5DB'
      }}>
        <p>&copy; 2024 Market Predictor Pro. All rights reserved.</p>
      </footer>
    </div>
  );
}

function FeaturePill({ icon, title, desc }) {
  return (
    <div style={{
      padding: '1.5rem',
      backgroundColor: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '8px',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(10px)',
      transition: 'all 0.3s ease'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.backgroundColor = 'rgba(16, 185, 129, 0.1)';
      e.currentTarget.style.border = '1px solid #10B981';
      e.currentTarget.style.transform = 'translateY(-5px)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
      e.currentTarget.style.border = '1px solid rgba(255, 255, 255, 0.1)';
      e.currentTarget.style.transform = 'translateY(0)';
    }}
    >
      <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{icon}</div>
      <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>{title}</div>
      <div style={{ fontSize: '0.9rem', color: '#D1D5DB' }}>{desc}</div>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div style={{
      padding: '2rem',
      backgroundColor: 'rgba(45, 55, 72, 0.5)',
      borderRadius: '12px',
      border: '1px solid #2D3748',
      transition: 'all 0.3s ease'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.backgroundColor = 'rgba(45, 55, 72, 0.8)';
      e.currentTarget.style.borderColor = '#3B82F6';
      e.currentTarget.style.transform = 'translateY(-10px)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.backgroundColor = 'rgba(45, 55, 72, 0.5)';
      e.currentTarget.style.borderColor = '#2D3748';
      e.currentTarget.style.transform = 'translateY(0)';
    }}
    >
      <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>{icon}</div>
      <h3 style={{ fontSize: '1.3rem', fontWeight: '600', marginBottom: '0.5rem', color: '#F9FAFB' }}>
        {title}
      </h3>
      <p style={{ color: '#D1D5DB', lineHeight: '1.6' }}>{description}</p>
    </div>
  );
}

function StatCard({ number, label }) {
  return (
    <div>
      <div style={{ fontSize: '2.5rem', fontWeight: '700', color: '#10B981', marginBottom: '0.5rem' }}>
        {number}
      </div>
      <div style={{ color: '#D1D5DB' }}>{label}</div>
    </div>
  );
}

function PricingCard({ name, price, period, features, highlighted }) {
  return (
    <div style={{
      padding: '2rem',
      backgroundColor: highlighted ? 'rgba(16, 185, 129, 0.15)' : 'rgba(45, 55, 72, 0.5)',
      borderRadius: '12px',
      border: highlighted ? '2px solid #10B981' : '1px solid #2D3748',
      transition: 'all 0.3s ease',
      position: 'relative'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-10px)';
      e.currentTarget.style.boxShadow = highlighted ? '0 20px 40px rgba(16, 185, 129, 0.2)' : '0 20px 40px rgba(59, 130, 246, 0.2)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = 'none';
    }}
    >
      {highlighted && (
        <div style={{
          position: 'absolute',
          top: '-12px',
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: '#10B981',
          color: '#0F172A',
          padding: '0.25rem 1rem',
          borderRadius: '20px',
          fontSize: '0.85rem',
          fontWeight: '600'
        }}>
          MOST POPULAR
        </div>
      )}

      <h3 style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '0.5rem', marginTop: highlighted ? '1rem' : 0 }}>
        {name}
      </h3>
      <div style={{ marginBottom: '1.5rem' }}>
        <span style={{ fontSize: '2.5rem', fontWeight: '700', color: '#10B981' }}>{price}</span>
        <span style={{ color: '#D1D5DB' }}>{period}</span>
      </div>

      <ul style={{ marginBottom: '2rem', listStyle: 'none', padding: 0 }}>
        {features.map((feature, i) => (
          <li key={i} style={{ padding: '0.5rem 0', color: '#D1D5DB', display: 'flex', alignItems: 'center' }}>
            <span style={{ color: '#10B981', marginRight: '0.5rem' }}>✓</span>
            {feature}
          </li>
        ))}
      </ul>

      <Link href="/auth/signup">
        <button style={{
          width: '100%',
          padding: '0.75rem',
          backgroundColor: highlighted ? '#10B981' : 'rgba(59, 130, 246, 0.2)',
          color: highlighted ? '#0F172A' : '#3B82F6',
          border: highlighted ? 'none' : '1px solid #3B82F6',
          borderRadius: '6px',
          cursor: 'pointer',
          fontWeight: '600',
          transition: 'all 0.3s ease'
        }}
        onMouseEnter={(e) => {
          if (highlighted) {
            e.target.style.backgroundColor = '#059669';
          } else {
            e.target.style.backgroundColor = 'rgba(59, 130, 246, 0.3)';
          }
        }}
        onMouseLeave={(e) => {
          if (highlighted) {
            e.target.style.backgroundColor = '#10B981';
          } else {
            e.target.style.backgroundColor = 'rgba(59, 130, 246, 0.2)';
          }
        }}
        >
          Get Started
        </button>
      </Link>
    </div>
  );
}
