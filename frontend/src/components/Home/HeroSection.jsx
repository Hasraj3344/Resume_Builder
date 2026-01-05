import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Transition } from '../Shared';

const HeroSection = ({ user }) => {
  const navigate = useNavigate();

  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-primary-50 via-white to-primary-100 py-20 md:py-32">
      {/* Background Decoration */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary rounded-full mix-blend-multiply filter blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-20 right-10 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className="container-custom relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Text Content */}
          <Transition type="slideInLeft" className="text-center lg:text-left">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-neutral-900 mb-6 leading-tight">
              AI-Powered Resume Optimization for Your{' '}
              <span className="text-gradient">Dream Job</span>
            </h1>
            <p className="text-lg md:text-xl text-neutral-600 mb-8 max-w-2xl">
              Match your resume with real-time job postings, optimize with AI, and land more interviews.
              Get ATS-friendly resumes tailored to each job in minutes.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Button
                variant="primary"
                size="lg"
                onClick={() => navigate(user ? '/dashboard' : '/register')}
                rightIcon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                }
              >
                {user ? 'Go to Dashboard' : 'Get Started Free'}
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
              >
                Learn More
              </Button>
            </div>
            {/* Stats */}
            <div className="flex flex-wrap gap-8 mt-12 justify-center lg:justify-start">
              <div>
                <div className="text-3xl font-bold text-primary">85%</div>
                <div className="text-sm text-neutral-600">Match Accuracy</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-primary">10K+</div>
                <div className="text-sm text-neutral-600">Resumes Generated</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-primary">5min</div>
                <div className="text-sm text-neutral-600">Average Time</div>
              </div>
            </div>
          </Transition>

          {/* Illustration/Image */}
          <Transition type="slideInRight" className="hidden lg:block">
            <div className="relative">
              {/* Resume Preview Card */}
              <div className="card p-8 transform hover:scale-105 transition-transform duration-500">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center">
                    <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <div>
                    <div className="h-3 w-32 bg-neutral-200 rounded mb-2"></div>
                    <div className="h-2 w-24 bg-neutral-100 rounded"></div>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="h-2 bg-neutral-100 rounded"></div>
                  <div className="h-2 bg-neutral-100 rounded w-5/6"></div>
                  <div className="h-2 bg-neutral-100 rounded w-4/6"></div>
                </div>
                <div className="mt-6 pt-6 border-t border-neutral-200">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-success">Match Score</span>
                    <span className="text-2xl font-bold text-success">85%</span>
                  </div>
                  <div className="mt-2 h-2 bg-neutral-100 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-success to-success-light rounded-full" style={{ width: '85%' }}></div>
                  </div>
                </div>
              </div>
              {/* Floating Badge */}
              <div className="absolute -top-4 -right-4 bg-white shadow-lg rounded-lg px-4 py-2 animate-bounce">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-success" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm font-medium text-neutral-900">ATS Optimized</span>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
