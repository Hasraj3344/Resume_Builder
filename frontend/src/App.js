import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/Layout';
import { HomePage } from './components/Home';
import { LoadingSpinner } from './components/Shared';

// Lazy load components for code splitting
const LoginPage = React.lazy(() => import('./components/Auth/LoginPage'));
const RegisterPage = React.lazy(() => import('./components/Auth/RegisterPage'));
const DashboardPage = React.lazy(() => import('./components/Dashboard/DashboardPage'));
const ManualWorkflowPage = React.lazy(() => import('./components/Workflow/ManualWorkflowPage'));
const AdzunaWorkflowPage = React.lazy(() => import('./components/Workflow/AdzunaWorkflowPage'));
const ProfilePage = React.lazy(() => import('./components/Profile/ProfilePage'));
const SubscriptionPage = React.lazy(() => import('./pages/SubscriptionPage'));
const SubscriptionSuccess = React.lazy(() => import('./pages/SubscriptionSuccess'));
const SubscriptionCancel = React.lazy(() => import('./pages/SubscriptionCancel'));

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// App Routes Component
const AppRoutes = () => {
  const { user, logout } = useAuth();

  return (
    <Layout user={user} onLogout={logout}>
      <React.Suspense fallback={<LoadingSpinner fullScreen />}>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<HomePage user={user} />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/manual"
            element={
              <ProtectedRoute>
                <ManualWorkflowPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/adzuna"
            element={
              <ProtectedRoute>
                <AdzunaWorkflowPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/subscription"
            element={
              <ProtectedRoute>
                <SubscriptionPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/subscription/success"
            element={
              <ProtectedRoute>
                <SubscriptionSuccess />
              </ProtectedRoute>
            }
          />
          <Route
            path="/subscription/cancel"
            element={
              <ProtectedRoute>
                <SubscriptionCancel />
              </ProtectedRoute>
            }
          />

          {/* Catch-all route - 404 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </React.Suspense>
    </Layout>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#fff',
              color: '#111827',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            },
            success: {
              iconTheme: {
                primary: '#10B981',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: '#EF4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </Router>
    </AuthProvider>
  );
}

export default App;
