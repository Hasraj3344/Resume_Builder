import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Button, Card, LoadingSpinner } from '../Shared';
import api from '../../services/api';

const DashboardPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [usageStats, setUsageStats] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Get usage stats
      const statsResponse = await api.get('/api/subscription/usage');
      setUsageStats(statsResponse.data);

      // Get subscription info
      const subResponse = await api.get('/api/subscription/status');
      setSubscription(subResponse.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const workflows = [
    {
      id: 'manual',
      title: 'Manual Job Description',
      description: 'Paste a job description and optimize your resume to match specific requirements',
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      features: [
        'Paste any job description',
        'AI-powered keyword matching',
        'Semantic similarity analysis',
        'Instant resume optimization',
      ],
      buttonText: 'Start Manual Workflow',
      buttonVariant: 'primary',
      path: '/dashboard/manual',
    },
    {
      id: 'adzuna',
      title: 'Adzuna Job Search',
      description: 'Search real-time job postings and get your resume optimized for specific opportunities',
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      ),
      features: [
        'Search live job postings',
        'Filter by location & salary',
        'View match scores instantly',
        'One-click optimization',
      ],
      buttonText: 'Search Jobs on Adzuna',
      buttonVariant: 'success',
      path: '/dashboard/adzuna',
    },
  ];

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  const isPro = subscription?.plan === 'pro' && subscription?.status === 'active';
  const usageText = isPro
    ? 'Unlimited'
    : `${usageStats?.used || 0}/${usageStats?.limit || 3} used`;
  const remainingText = isPro
    ? 'Pro Member'
    : `${usageStats?.remaining || 3} remaining this month`;

  return (
    <div className="min-h-screen bg-neutral-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Welcome Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-neutral-900 mb-4">
            Welcome back, {user?.full_name?.split(' ')[0] || 'User'}! 👋
          </h1>
          <p className="text-xl text-neutral-600 max-w-2xl mx-auto">
            Choose how you'd like to optimize your resume today
          </p>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Card hover={false}>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary mb-2">{usageText}</div>
              <div className="text-sm text-neutral-600">Resumes Generated</div>
              <div className="text-xs text-neutral-500 mt-1">{remainingText}</div>
            </div>
          </Card>
          <Card hover={false}>
            <div className="text-center">
              <div className="text-3xl font-bold text-success mb-2 uppercase">
                {usageStats?.plan || 'Free'}
              </div>
              <div className="text-sm text-neutral-600">Current Plan</div>
              {!isPro && (
                <div
                  className="text-xs text-primary mt-1 cursor-pointer hover:underline font-semibold"
                  onClick={() => navigate('/subscription')}
                >
                  Upgrade to Pro →
                </div>
              )}
              {isPro && (
                <div
                  className="text-xs text-success mt-1 cursor-pointer hover:underline"
                  onClick={() => navigate('/subscription')}
                >
                  Manage Subscription
                </div>
              )}
            </div>
          </Card>
          <Card hover={false}>
            <div className="text-center">
              <div className="text-3xl font-bold text-neutral-700 mb-2">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : 'N/A'}
              </div>
              <div className="text-sm text-neutral-600">Member Since</div>
            </div>
          </Card>
        </div>

        {/* Workflow Selection */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {workflows.map((workflow) => (
            <Card key={workflow.id} className="flex flex-col">
              <div className="flex items-start gap-4 mb-4">
                <div className="flex-shrink-0 w-16 h-16 rounded-xl bg-primary-50 text-primary flex items-center justify-center">
                  {workflow.icon}
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-neutral-900 mb-2">
                    {workflow.title}
                  </h3>
                  <p className="text-neutral-600">{workflow.description}</p>
                </div>
              </div>

              {/* Features List */}
              <div className="flex-1 mb-6">
                <ul className="space-y-2">
                  {workflow.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-sm text-neutral-700">
                      <svg className="w-5 h-5 text-success flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>

              <Button
                variant={workflow.buttonVariant}
                fullWidth
                onClick={() => navigate(workflow.path)}
              >
                {workflow.buttonText} →
              </Button>
            </Card>
          ))}
        </div>

        {/* Quick Tips Section */}
        <div className="mt-12">
          <Card className="bg-primary-50 border-primary-200">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <svg className="w-6 h-6 text-primary" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-semibold text-primary-900 mb-2">Pro Tip</h4>
                <p className="text-sm text-primary-800">
                  For best results, use the Adzuna workflow to find real job postings that match your profile.
                  Our AI will optimize your resume specifically for those opportunities, increasing your chances of getting interviews.
                </p>
              </div>
            </div>
          </Card>
        </div>

        {/* Recent Activity (Placeholder) */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-neutral-900 mb-6">Recent Activity</h2>
          <Card>
            <div className="text-center py-12">
              <svg className="w-16 h-16 mx-auto text-neutral-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-neutral-600 mb-2">No recent activity</p>
              <p className="text-sm text-neutral-500">
                Start by selecting a workflow above to generate your first optimized resume
              </p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
