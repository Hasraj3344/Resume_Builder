import React from 'react';
import { Transition } from '../Shared';

const HowItWorksSection = () => {
  const steps = [
    {
      number: '01',
      title: 'Upload Your Resume',
      description: 'Register and upload your existing resume in PDF or DOCX format. Our AI will parse and understand your experience.',
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      ),
    },
    {
      number: '02',
      title: 'Search or Paste Jobs',
      description: 'Choose between searching real-time job postings from Adzuna or pasting a job description manually.',
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      ),
    },
    {
      number: '03',
      title: 'AI Optimizes Resume',
      description: 'Our AI analyzes the job requirements and rewrites your resume bullets with relevant keywords and metrics.',
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
    },
    {
      number: '04',
      title: 'Download & Apply',
      description: 'Download your ATS-friendly resume in DOCX format and apply with confidence. Track your applications and success.',
      icon: (
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
      ),
    },
  ];

  return (
    <section id="how-it-works" className="section bg-neutral-50">
      <div className="container-custom">
        <Transition type="fadeIn">
          <h2 className="section-title">How It Works</h2>
          <p className="section-subtitle">
            Get your optimized resume in 4 simple steps
          </p>
        </Transition>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mt-12">
          {steps.map((step, index) => (
            <Transition key={index} type="slideUp" delay={index * 100}>
              <div className="relative">
                {/* Connector Line (Desktop only) */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-16 left-1/2 w-full h-0.5 bg-gradient-to-r from-primary/50 to-primary/20"></div>
                )}

                {/* Step Card */}
                <div className="relative bg-white rounded-card shadow-card p-6 hover-lift text-center">
                  {/* Step Number */}
                  <div className="absolute -top-6 left-1/2 transform -translate-x-1/2">
                    <div className="w-12 h-12 bg-gradient-to-br from-primary to-primary-dark text-white rounded-full flex items-center justify-center font-bold text-lg shadow-lg">
                      {step.number}
                    </div>
                  </div>

                  {/* Icon */}
                  <div className="text-primary mb-4 mt-6 flex justify-center">
                    {step.icon}
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-semibold text-neutral-900 mb-3">{step.title}</h3>
                  <p className="text-neutral-600 text-sm leading-relaxed">{step.description}</p>
                </div>
              </div>
            </Transition>
          ))}
        </div>

        {/* CTA */}
        <Transition type="fadeIn" className="mt-16 text-center">
          <div className="inline-flex items-center gap-2 bg-primary-100 text-primary px-6 py-3 rounded-full">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">Average completion time: 5 minutes</span>
          </div>
        </Transition>
      </div>
    </section>
  );
};

export default HowItWorksSection;
