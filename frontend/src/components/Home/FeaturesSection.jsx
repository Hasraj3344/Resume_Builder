import React from 'react';
import { Card, Transition } from '../Shared';

const FeaturesSection = () => {
  const features = [
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      title: 'Smart Matching',
      description: 'Advanced AI algorithms match your resume with job descriptions using semantic similarity and keyword analysis.',
      color: 'text-primary',
      bgColor: 'bg-primary-100',
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      title: 'AI Rewriting',
      description: 'GPT-powered resume optimization that rewrites your experience bullets with STAR/WHR format and quantifiable metrics.',
      color: 'text-success',
      bgColor: 'bg-success/10',
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
      title: 'Real-Time Jobs',
      description: 'Search thousands of live job postings from Adzuna API with advanced filters and instant matching.',
      color: 'text-info',
      bgColor: 'bg-info/10',
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      title: 'ATS-Friendly',
      description: 'Generate professional DOCX resumes optimized for Applicant Tracking Systems with proper formatting.',
      color: 'text-warning',
      bgColor: 'bg-warning/10',
    },
  ];

  return (
    <section id="features" className="section bg-white">
      <div className="container-custom">
        <Transition type="fadeIn">
          <h2 className="section-title">Powerful Features</h2>
          <p className="section-subtitle">
            Everything you need to create winning resumes that get you hired
          </p>
        </Transition>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mt-12">
          {features.map((feature, index) => (
            <Transition key={index} type="slideUp" delay={index * 100}>
              <Card hoverable className="h-full">
                <div className={`w-16 h-16 ${feature.bgColor} ${feature.color} rounded-lg flex items-center justify-center mb-4`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-neutral-900 mb-3">{feature.title}</h3>
                <p className="text-neutral-600 text-sm leading-relaxed">{feature.description}</p>
              </Card>
            </Transition>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
