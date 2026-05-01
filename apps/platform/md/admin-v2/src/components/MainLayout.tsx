import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Avatar, Dropdown, theme } from 'antd';
import type { MenuProps } from 'antd';
import {
  DashboardOutlined,
  FileTextOutlined,
  CodeOutlined,
  ShopOutlined,
  TeamOutlined,
  BookOutlined,
  DownloadOutlined,
  CreditCardOutlined,
  DollarOutlined,
  PercentageOutlined,
  GiftOutlined,
  MenuOutlined,
  SearchOutlined,
  GlobalOutlined,
  AppstoreOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DatabaseOutlined,
  ShoppingCartOutlined,
  CheckSquareOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '@/stores/authStore';

const { Header, Sider, Content } = Layout;

const menuItems: MenuProps['items'] = [
  {
    key: '/dashboard',
    icon: <DashboardOutlined />,
    label: '控制面板',
  },
  {
    key: '/content',
    icon: <FileTextOutlined />,
    label: '内容管理',
  },
  {
    key: '/skills',
    icon: <CodeOutlined />,
    label: '技能管理',
  },
  {
    key: '/vendors',
    icon: <ShopOutlined />,
    label: '供应商',
  },
  {
    key: '/users',
    icon: <TeamOutlined />,
    label: '用户管理',
  },
  {
    key: '/tutorials',
    icon: <BookOutlined />,
    label: '教程管理',
  },
  {
    key: '/downloads',
    icon: <DownloadOutlined />,
    label: '下载管理',
  },
  {
    key: '/payment-accounts',
    icon: <CreditCardOutlined />,
    label: '支付账户',
  },
  {
    key: '/creator-earnings',
    icon: <DollarOutlined />,
    label: '创作者收益',
  },
  {
    key: '/commission',
    icon: <PercentageOutlined />,
    label: '佣金管理',
  },
  {
    key: '/points',
    icon: <GiftOutlined />,
    label: '积分商城',
  },
  {
    key: '/navigation',
    icon: <MenuOutlined />,
    label: '导航管理',
  },
  {
    key: '/seo',
    icon: <SearchOutlined />,
    label: 'SEO设置',
  },
  {
    key: '/i18n',
    icon: <GlobalOutlined />,
    label: '多语言',
  },
  {
    key: '/modules',
    icon: <AppstoreOutlined />,
    label: '模块管理',
  },
  {
    key: '/config-data',
    icon: <DatabaseOutlined />,
    label: '配置数据',
  },
  {
    key: '/store',
    icon: <ShoppingCartOutlined />,
    label: '商城管理',
  },
  {
    key: '/tasks',
    icon: <CheckSquareOutlined />,
    label: '任务管理',
  },
];

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    navigate(key);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: user?.username || '个人资料',
      disabled: true,
    },
    { type: 'divider' },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ];

  const handleUserMenuClick: MenuProps['onClick'] = ({ key }) => {
    if (key === 'logout') {
      handleLogout();
    }
  };

  // Determine selected keys from current path
  const selectedKeys = [location.pathname];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        theme="dark"
        width={220}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 10,
        }}
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: collapsed ? 16 : 18,
            fontWeight: 'bold',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          {collapsed ? 'SM' : 'SillyMD 管理后台'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={selectedKeys}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>

      <Layout style={{ marginLeft: collapsed ? 80 : 220, transition: 'margin-left 0.2s' }}>
        <Header
          style={{
            padding: '0 24px',
            background: colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid #f0f0f0',
            position: 'sticky',
            top: 0,
            zIndex: 9,
          }}
        >
          <div
            style={{ fontSize: 18, cursor: 'pointer' }}
            onClick={() => setCollapsed(!collapsed)}
          >
            {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          </div>

          <Dropdown
            menu={{ items: userMenuItems, onClick: handleUserMenuClick }}
            placement="bottomRight"
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                cursor: 'pointer',
              }}
            >
              <Avatar icon={<UserOutlined />} />
              <span>{user?.username || 'Admin'}</span>
            </div>
          </Dropdown>
        </Header>

        <Content
          style={{
            margin: 24,
            padding: 24,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
            minHeight: 280,
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
