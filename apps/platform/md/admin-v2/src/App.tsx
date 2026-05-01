import React, { useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuthStore } from '@/stores/authStore';

import MainLayout from '@/components/MainLayout';
import LoginPage from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import ContentManagement from '@/pages/ContentManagement';
import SkillsManagement from '@/pages/SkillsManagement';
import VendorManagement from '@/pages/VendorManagement';
import UserManagement from '@/pages/UserManagement';
import TutorialManagement from '@/pages/TutorialManagement';
import DownloadManagement from '@/pages/DownloadManagement';
import PaymentAccountsManagement from '@/pages/PaymentAccountsManagement';
import CreatorEarnings from '@/pages/CreatorEarnings';
import CommissionManagement from '@/pages/CommissionManagement';
import PointsManagement from '@/pages/PointsManagement';
import NavigationEdit from '@/pages/NavigationEdit';
import SEOSettings from '@/pages/SEOSettings';
import I18nManagement from '@/pages/I18nManagement';
import ModuleManagement from '@/pages/ModuleManagement';
import ConfigDataManagement from '@/pages/ConfigDataManagement';
import StoreManagement from '@/pages/StoreManagement';
import TasksManagement from '@/pages/TasksManagement';

// Protected route wrapper – redirects to /login if not authenticated
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { isAuthenticated, isLoading } = useAuthStore();
  const location = useLocation();

  if (isLoading) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
        <Spin size="large" tip="Loading..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

const App: React.FC = () => {
  const { checkAuth, isAuthenticated } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <Routes>
      {/* Public route */}
      <Route
        path="/login"
        element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />
        }
      />

      {/* Protected routes – wrapped in MainLayout */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="content" element={<ContentManagement />} />
        <Route path="skills" element={<SkillsManagement />} />
        <Route path="vendors" element={<VendorManagement />} />
        <Route path="users" element={<UserManagement />} />
        <Route path="tutorials" element={<TutorialManagement />} />
        <Route path="downloads" element={<DownloadManagement />} />
        <Route path="payment-accounts" element={<PaymentAccountsManagement />} />
        <Route path="creator-earnings" element={<CreatorEarnings />} />
        <Route path="commission" element={<CommissionManagement />} />
        <Route path="points" element={<PointsManagement />} />
        <Route path="navigation" element={<NavigationEdit />} />
        <Route path="seo" element={<SEOSettings />} />
        <Route path="i18n" element={<I18nManagement />} />
        <Route path="modules" element={<ModuleManagement />} />
        <Route path="config-data" element={<ConfigDataManagement />} />
        <Route path="store" element={<StoreManagement />} />
        <Route path="tasks" element={<TasksManagement />} />
      </Route>

      {/* Catch-all: redirect unknown paths to dashboard */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

export default App;
