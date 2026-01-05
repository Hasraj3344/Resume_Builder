import React from 'react';
import { Button, Card } from './index';

const SubscriptionModal = ({ isOpen, onClose, usageInfo }) => {
  if (!isOpen) return null;

  const { plan, limit, used, remaining, reset_date } = usageInfo || {};

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="max-w-2xl w-full animate-fadeIn">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-warning-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-neutral-900 mb-2">
            Monthly Limit Reached
          </h2>
          <p className="text-neutral-600">
            You've used all {limit} resume generations this month
          </p>
        </div>

        {/* Current Usage Stats */}
        <div className="bg-neutral-50 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-neutral-600">Current Plan</span>
            <span className="font-semibold text-neutral-900 uppercase">{plan || 'Free'}</span>
          </div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-neutral-600">Resumes Generated</span>
            <span className="font-semibold text-neutral-900">{used} / {limit}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-neutral-600">Resets On</span>
            <span className="font-semibold text-neutral-900">
              {reset_date ? new Date(reset_date).toLocaleDateString() : 'Next month'}
            </span>
          </div>
        </div>

        {/* Pro Plan Benefits */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Upgrade to Pro</h3>

          <div className="bg-gradient-to-br from-primary-50 to-success-50 rounded-lg p-6 border-2 border-primary-200 mb-4">
            <div className="flex items-baseline mb-4">
              <span className="text-4xl font-bold text-neutral-900">$9.99</span>
              <span className="text-neutral-600 ml-2">/month</span>
            </div>

            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="font-medium text-neutral-900">Unlimited Resume Generation</p>
                  <p className="text-sm text-neutral-600">Generate as many optimized resumes as you need</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="font-medium text-neutral-900">Adzuna Job Search</p>
                  <p className="text-sm text-neutral-600">Search & match with real-time job postings</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="font-medium text-neutral-900">AI-Powered Optimization</p>
                  <p className="text-sm text-neutral-600">Smart resume tailoring for each job</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="font-medium text-neutral-900">Priority Support</p>
                  <p className="text-sm text-neutral-600">Get help when you need it</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="font-medium text-neutral-900">Cancel Anytime</p>
                  <p className="text-sm text-neutral-600">No long-term commitment required</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <Button variant="outline" fullWidth onClick={onClose}>
            Maybe Later
          </Button>
          <Button variant="success" fullWidth onClick={() => {
            // Navigate to subscription page
            window.location.href = '/subscription';
          }}>
            Upgrade to Pro →
          </Button>
        </div>

        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-neutral-400 hover:text-neutral-600 transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </Card>
    </div>
  );
};

export default SubscriptionModal;
