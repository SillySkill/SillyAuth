import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, App as AntdApp } from 'antd';
import Login from './pages/Login';
import MainLayout from './components/MainLayout';
import Dashboard from './pages/Dashboard';
import ContentManagement from './pages/ContentManagement';
import NavigationEdit from './pages/NavigationEdit';
import CarouselEdit from './pages/CarouselEdit';
import SkillsManagement from './pages/SkillsManagement';
import VendorManagement from './pages/VendorManagement';
import SEOSettings from './pages/SEOSettings';
import I18nManagement from './pages/I18nManagement';
import UserManagement from './pages/UserManagement';
import TutorialManagement from './pages/TutorialManagement';
import DownloadManagement from './pages/DownloadManagement';
import CommissionManagement from './pages/CommissionManagement';
import PointsManagement from './pages/PointsManagement';
import PaymentAccountsManagement from './pages/PaymentAccountsManagement';
import CreatorEarnings from './pages/CreatorEarnings';
import { useAuthStore } from './stores/authStore';

// 私有路由组件
const PrivateRoute: React.FC<{ children: React.ReactElement }> = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

function App() {
  return (
    <AntdApp>
      <ConfigProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <MainLayout />
              </PrivateRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="content" element={<ContentManagement />} />
            <Route path="navigation" element={<NavigationEdit />} />
            <Route path="carousel" element={<CarouselEdit />} />
            <Route path="skills" element={<SkillsManagement />} />
            <Route path="vendors" element={<VendorManagement />} />
            <Route path="seo" element={<SEOSettings />} />
            <Route path="i18n" element={<I18nManagement />} />
            <Route path="users" element={<UserManagement />} />
            <Route path="tutorials" element={<TutorialManagement />} />
            <Route path="downloads" element={<DownloadManagement />} />
            <Route path="commission" element={<CommissionManagement />} />
            <Route path="points" element={<PointsManagement />} />
            <Route path="payment-accounts" element={<PaymentAccountsManagement />} />
            <Route path="creator-earnings" element={<CreatorEarnings />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </ConfigProvider>
    </AntdApp>
  );
}

export default App;
