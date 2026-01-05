import React from 'react';
import HeroSection from './HeroSection';
import FeaturesSection from './FeaturesSection';
import HowItWorksSection from './HowItWorksSection';
import AboutUsSection from './AboutUsSection';

const HomePage = ({ user }) => {
  return (
    <div className="min-h-screen">
      <HeroSection user={user} />
      <FeaturesSection />
      <HowItWorksSection />
      <AboutUsSection />
    </div>
  );
};

export default HomePage;
