import React, { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Breadcrumb } from 'antd';
import {
  DashboardOutlined,
  FileTextOutlined,
  MenuOutlined,
  PictureOutlined,
  ToolOutlined,
  TeamOutlined,
  SettingOutlined,
  GlobalOutlined,
  UserOutlined,
  LogoutOutlined,
  PlayCircleOutlined,
  DownloadOutlined,
  DollarOutlined,
  TrophyOutlined,
  BankOutlined,
  FundOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import type { MenuProps } from 'antd';

const { Header, Sider, Content } = Layout;

const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const user = useAuthStore((state) => state.user);
  const clearAuth = useAuthStore((state) => state.clearAuth);

  const menuItems: MenuProps['items'] = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/content',
      icon: <FileTextOutlined />,
      label: '内容管理',
    },
    {
      key: '/navigation',
      icon: <MenuOutlined />,
      label: '导航管理',
    },
    {
      key: '/carousel',
      icon: <PictureOutlined />,
      label: '轮播图管理',
    },
    {
      key: '/skills',
      icon: <ToolOutlined />,
      label: '技能管理',
    },
    {
      key: '/vendors',
      icon: <TeamOutlined />,
      label: '供应商管理',
    },
    {
      key: '/seo',
      icon: <SettingOutlined />,
      label: 'SEO 设置',
    },
    {
      key: '/i18n',
      icon: <GlobalOutlined />,
      label: '多语言管理',
    },
    {
      key: '/users',
      icon: <UserOutlined />,
      label: '用户管理',
    },
    {
      key: '/tutorials',
      icon: <PlayCircleOutlined />,
      label: '教程管理',
    },
    {
      key: '/downloads',
      icon: <DownloadOutlined />,
      label: '下载资源管理',
    },
    {
      key: '/commission',
      icon: <DollarOutlined />,
      label: '佣金配置',
    },
    {
      key: '/points',
      icon: <TrophyOutlined />,
      label: '积分管理',
    },
    {
      key: '/payment-accounts',
      icon: <BankOutlined />,
      label: '收款账户',
    },
    {
      key: '/creator-earnings',
      icon: <FundOutlined />,
      label: '创作者收益',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ];

  const getBreadcrumb = () => {
    const pathMap: Record<string, string> = {
      '/dashboard': '仪表盘',
      '/content': '内容管理',
      '/navigation': '导航管理',
      '/carousel': '轮播图管理',
      '/skills': '技能管理',
      '/vendors': '供应商管理',
      '/seo': 'SEO 设置',
      '/i18n': '多语言管理',
      '/users': '用户管理',
      '/tutorials': '教程管理',
      '/downloads': '下载资源管理',
      '/commission': '佣金配置',
      '/points': '积分管理',
      '/payment-accounts': '收款账户',
      '/creator-earnings': '创作者收益',
    };

    return pathMap[location.pathname] || '首页';
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="dark"
      >
        <div style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontSize: collapsed ? 16 : 20,
          fontWeight: 'bold',
        }}>
          {collapsed ? 'CMS' : 'SillyMD CMS'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header style={{
          background: '#fff',
          padding: '0 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: '0 1px 4px rgba(0,21,41,.08)',
        }}>
          <Breadcrumb style={{ fontSize: 16 }}>
            <Breadcrumb.Item>{getBreadcrumb()}</Breadcrumb.Item>
          </Breadcrumb>
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Avatar icon={<UserOutlined />} />
              <span>{user?.username || '用户'}</span>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ margin: '24px', background: '#fff', padding: 24, borderRadius: 8 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
