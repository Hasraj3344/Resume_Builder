import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Button, Card, LoadingSpinner } from '../components/Shared';
import api from '../services/api';

const SubscriptionSuccess = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    activateSubscription();
  }, []);

  const activateSubscription = async () => {
    try {
      // Get subscription_id from URL params
      const subscriptionId = searchParams.get('subscription_id');

      if (!subscriptionId) {
        setError('No subscription ID found');
        setLoading(false);
        return;
      }

      // Activate subscription in backend
      await api.post('/api/subscription/activate', {
        subscription_id: subscriptionId
      });

      setLoading(false);
      toast.success('Subscription activated successfully!');

      // Redirect to subscription page after 2 seconds
      setTimeout(() => {
        navigate('/subscription');
      }, 2000);

    } catch (err) {
      console.error('Activation error:', err);
      setError(err.response?.data?.detail || 'Failed to activate subscription');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <Card className="max-w-md text-center">
          <LoadingSpinner />
          <p className="mt-4 text-neutral-600">Activating your subscription...</p>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
        <Card className="max-w-md text-center">
          <div className="w-16 h-16 bg-error-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-neutral-900 mb-2">Activation Failed</h2>
          <p className="text-neutral-600 mb-6">{error}</p>
          <Button variant="primary" fullWidth onClick={() => navigate('/subscription')}>
            Go to Subscription Page
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
      <Card className="max-w-md text-center">
        <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-success" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-neutral-900 mb-2">
          Welcome to Pro! 🎉
        </h2>
        <p className="text-neutral-600 mb-6">
          Your subscription has been activated successfully. You now have unlimited resume generation!
        </p>
        <p className="text-sm text-neutral-500 mb-6">
          Redirecting to subscription page...
        </p>
      </Card>
    </div>
  );
};

export default SubscriptionSuccess;
