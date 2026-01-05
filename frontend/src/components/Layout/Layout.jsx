import React from 'react';
import Navbar from './Navbar';
import Footer from './Footer';

const Layout = ({ children, user, onLogout }) => {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar user={user} onLogout={onLogout} />
      <main className="flex-grow">
        {children}
      </main>
      <Footer />
    </div>
  );
};

export default Layout;
