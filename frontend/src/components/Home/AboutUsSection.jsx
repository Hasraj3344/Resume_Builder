import React from 'react';
import { Transition } from '../Shared';

const AboutUsSection = () => {
  const stats = [
    { label: 'Users', value: '10,000+', icon: '👥' },
    { label: 'Resumes Generated', value: '50,000+', icon: '📄' },
    { label: 'Success Rate', value: '85%', icon: '🎯' },
    { label: 'Avg Match Score', value: '82%', icon: '✨' },
  ];

  const techStack = [
    { name: 'React 19', category: 'Frontend' },
    { name: 'FastAPI', category: 'Backend' },
    { name: 'OpenAI GPT', category: 'AI' },
    { name: 'FAISS', category: 'Vector Search' },
    { name: 'Adzuna API', category: 'Jobs Data' },
    { name: 'PostgreSQL', category: 'Database' },
  ];

  return (
    <section id="about" className="section bg-white">
      <div className="container-custom">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Text Content */}
          <Transition type="slideInLeft">
            <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 mb-6">
              About <span className="text-gradient">ResumeAI</span>
            </h2>
            <p className="text-lg text-neutral-600 mb-6 leading-relaxed">
              ResumeAI is an AI-powered platform that helps job seekers optimize their resumes
              for specific job descriptions. We combine advanced machine learning, natural language
              processing, and real-time job data to give you the competitive edge in your job search.
            </p>
            <p className="text-lg text-neutral-600 mb-6 leading-relaxed">
              Our mission is to democratize access to professional resume optimization, making it
              affordable and accessible for everyone. Whether you're a recent graduate or a seasoned
              professional, ResumeAI helps you land more interviews.
            </p>

            {/* Mission Points */}
            <div className="space-y-4 mb-8">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-success/20 flex items-center justify-center flex-shrink-0 mt-1">
                  <svg className="w-4 h-4 text-success" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <p className="text-neutral-700"><span className="font-semibold">AI-Powered Optimization:</span> Using GPT-3.5 and semantic matching algorithms</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-success/20 flex items-center justify-center flex-shrink-0 mt-1">
                  <svg className="w-4 h-4 text-success" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <p className="text-neutral-700"><span className="font-semibold">Real-Time Job Data:</span> Access to thousands of live job postings from Adzuna</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-success/20 flex items-center justify-center flex-shrink-0 mt-1">
                  <svg className="w-4 h-4 text-success" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <p className="text-neutral-700"><span className="font-semibold">ATS Compatibility:</span> Optimized for all major Applicant Tracking Systems</p>
              </div>
            </div>

            {/* Tech Stack */}
            <div>
              <h3 className="text-xl font-semibold text-neutral-900 mb-4">Built With Modern Technology</h3>
              <div className="flex flex-wrap gap-2">
                {techStack.map((tech, index) => (
                  <span
                    key={index}
                    className="badge badge-primary"
                  >
                    {tech.name}
                  </span>
                ))}
              </div>
            </div>
          </Transition>

          {/* Stats Grid */}
          <Transition type="slideInRight">
            <div className="grid grid-cols-2 gap-6">
              {stats.map((stat, index) => (
                <div
                  key={index}
                  className="card text-center hover-lift"
                >
                  <div className="text-4xl mb-3">{stat.icon}</div>
                  <div className="text-3xl font-bold text-primary mb-2">{stat.value}</div>
                  <div className="text-sm text-neutral-600">{stat.label}</div>
                </div>
              ))}
            </div>

            {/* Team Image Placeholder */}
            <div className="mt-8 card bg-gradient-to-br from-primary-50 to-primary-100 p-8">
              <div className="text-center">
                <div className="flex justify-center -space-x-4 mb-4">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className="w-12 h-12 rounded-full bg-white border-2 border-white shadow-md flex items-center justify-center"
                    >
                      <svg className="w-6 h-6 text-primary" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                      </svg>
                    </div>
                  ))}
                </div>
                <h4 className="font-semibold text-neutral-900 mb-2">Built by Job Seekers, for Job Seekers</h4>
                <p className="text-sm text-neutral-600">
                  Our team understands the challenges of modern job hunting because we've been there too.
                </p>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </section>
  );
};

export default AboutUsSection;
