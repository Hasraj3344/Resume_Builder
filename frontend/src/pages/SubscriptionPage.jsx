import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Button, Card, LoadingSpinner } from '../components/Shared';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const SubscriptionPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [usageStats, setUsageStats] = useState(null);
  const [subscription, setSubscription] = useState(null);

  useEffect(() => {
    loadSubscriptionData();
  }, []);

  const loadSubscriptionData = async () => {
    try {
      // Get usage stats
      const statsResponse = await api.get('/api/subscription/usage');
      setUsageStats(statsResponse.data);

      // Get subscription info
      const subResponse = await api.get('/api/subscription/status');
      setSubscription(subResponse.data);
    } catch (error) {
      console.error('Failed to load subscription data:', error);
    }
  };

  const handleUpgradeToPro = async () => {
    setLoading(true);
    try {
      const response = await api.post('/api/subscription/create-pro', {
        return_url: `${window.location.origin}/subscription/success`,
        cancel_url: `${window.location.origin}/subscription/cancel`
      });

      // Redirect to PayPal approval URL
      if (response.data.approval_url) {
        window.location.href = response.data.approval_url;
      } else {
        throw new Error('No approval URL received');
      }
    } catch (error) {
      console.error('Upgrade error:', error);
      const errorDetail = error.response?.data?.detail;
      let errorMsg = 'Failed to start subscription';

      if (typeof errorDetail === 'string') {
        errorMsg = errorDetail;
      } else if (Array.isArray(errorDetail)) {
        errorMsg = errorDetail.map(err => err.msg || JSON.stringify(err)).join(', ');
      } else if (errorDetail?.message) {
        errorMsg = errorDetail.message;
      }

      toast.error(errorMsg);
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!window.confirm('Are you sure you want to cancel your Pro subscription?')) {
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/subscription/cancel');
      toast.success('Subscription cancelled successfully');
      loadSubscriptionData();
    } catch (error) {
      console.error('Cancel error:', error);
      toast.error(error.response?.data?.detail || 'Failed to cancel subscription');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !usageStats) {
    return <LoadingSpinner fullScreen />;
  }

  const isPro = subscription?.plan === 'pro' && subscription?.status === 'active';

  return (
    <div className="min-h-screen bg-neutral-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-primary hover:text-primary-dark flex items-center gap-2 mb-4"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Dashboard
          </button>
          <h1 className="text-4xl font-bold text-neutral-900 mb-2">Subscription Plans</h1>
          <p className="text-lg text-neutral-600">
            Choose the plan that works best for you
          </p>
        </div>

        {/* Current Usage Stats */}
        {usageStats && (
          <Card className="mb-8 bg-gradient-to-r from-primary-50 to-success-50">
            <h2 className="text-xl font-bold text-neutral-900 mb-4">Current Usage</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-neutral-600 mb-1">Current Plan</p>
                <p className="text-2xl font-bold text-neutral-900 uppercase">{usageStats.plan || 'Free'}</p>
              </div>
              <div>
                <p className="text-sm text-neutral-600 mb-1">Resumes Generated</p>
                <p className="text-2xl font-bold text-neutral-900">
                  {usageStats.used} / {usageStats.limit || '∞'}
                </p>
              </div>
              <div>
                <p className="text-sm text-neutral-600 mb-1">Next Reset</p>
                <p className="text-2xl font-bold text-neutral-900">
                  {usageStats.reset_date ? new Date(usageStats.reset_date).toLocaleDateString() : 'N/A'}
                </p>
              </div>
            </div>
          </Card>
        )}

        {/* Pricing Plans */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Free Plan */}
          <Card className={`relative ${!isPro ? 'ring-2 ring-primary' : ''}`}>
            {!isPro && (
              <div className="absolute top-4 right-4 bg-primary text-white px-3 py-1 rounded-full text-sm font-semibold">
                Current Plan
              </div>
            )}
            <div className="mb-6">
              <h3 className="text-2xl font-bold text-neutral-900 mb-2">Free</h3>
              <div className="flex items-baseline mb-4">
                <span className="text-4xl font-bold text-neutral-900">$0</span>
                <span className="text-neutral-600 ml-2">/month</span>
              </div>
            </div>

            <div className="space-y-3 mb-6">
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-neutral-700">3 resume generations per month</span>
              </div>
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-neutral-700">AI-powered optimization</span>
              </div>
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-neutral-700">DOCX export</span>
              </div>
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-neutral-300 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="text-neutral-400">Adzuna job search</span>
              </div>
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-neutral-300 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="text-neutral-400">Priority support</span>
              </div>
            </div>

            <Button variant="outline" fullWidth disabled={!isPro}>
              {isPro ? 'Downgrade to Free' : 'Current Plan'}
            </Button>
          </Card>

          {/* Pro Plan */}
          <Card className={`relative bg-gradient-to-br from-primary-50 to-success-50 ${isPro ? 'ring-2 ring-success' : ''}`}>
            {isPro && (
              <div className="absolute top-4 right-4 bg-success text-white px-3 py-1 rounded-full text-sm font-semibold">
                Current Plan
              </div>
            )}
            <div className="mb-6">
              <h3 className="text-2xl font-bold text-neutral-900 mb-2">Pro</h3>
              <div className="flex items-baseline mb-4">
                <span className="text-4xl font-bold text-neutral-900">$9.99</span>
                <span className="text-neutral-600 ml-2">/month</span>
              </div>
            </div>

            <div className="space-y-3 mb-6">
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-neutral-900 font-semibold">Unlimited resume generations</span>
              </div>
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-neutral-700">AI-powered optimization</span>
              </div>
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-neutral-700">DOCX export</span>
              </div>
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-neutral-900 font-semibold">Adzuna job search & matching</span>
              </div>
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-neutral-900 font-semibold">Priority support</span>
              </div>
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-neutral-700">Cancel anytime</span>
              </div>
            </div>

            {isPro ? (
              <Button variant="error" fullWidth onClick={handleCancelSubscription} disabled={loading}>
                Cancel Subscription
              </Button>
            ) : (
              <Button variant="success" fullWidth onClick={handleUpgradeToPro} disabled={loading}>
                {loading ? 'Processing...' : 'Upgrade to Pro →'}
              </Button>
            )}
          </Card>
        </div>

        {/* FAQ Section */}
        <Card className="mt-8">
          <h2 className="text-2xl font-bold text-neutral-900 mb-6">Frequently Asked Questions</h2>
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-neutral-900 mb-2">How does billing work?</h3>
              <p className="text-neutral-600">
                Pro subscriptions are billed monthly via PayPal. You can cancel anytime, and you'll retain access until the end of your current billing period.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-neutral-900 mb-2">Can I switch plans?</h3>
              <p className="text-neutral-600">
                Yes! You can upgrade from Free to Pro at any time. If you cancel Pro, you'll be downgraded to Free at the end of your billing cycle.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-neutral-900 mb-2">What payment methods do you accept?</h3>
              <p className="text-neutral-600">
                We accept all major payment methods through PayPal, including credit cards, debit cards, and PayPal balance.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default SubscriptionPage;
