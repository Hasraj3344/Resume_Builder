import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Card } from '../components/Shared';

const SubscriptionCancel = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
      <Card className="max-w-md text-center">
        <div className="w-16 h-16 bg-warning-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-neutral-900 mb-2">
          Subscription Cancelled
        </h2>
        <p className="text-neutral-600 mb-6">
          You cancelled the subscription process. No charges were made to your account.
        </p>
        <p className="text-sm text-neutral-500 mb-6">
          You can upgrade to Pro anytime from your subscription page.
        </p>
        <div className="flex gap-4">
          <Button variant="outline" fullWidth onClick={() => navigate('/dashboard')}>
            Go to Dashboard
          </Button>
          <Button variant="primary" fullWidth onClick={() => navigate('/subscription')}>
            Try Again
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default SubscriptionCancel;
