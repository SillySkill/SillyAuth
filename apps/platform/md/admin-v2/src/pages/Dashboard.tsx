import React, { useEffect, useState, useCallback } from 'react';
import { Row, Col, Card, Statistic, Table, Button, Space, Tag, Typography, Spin, Empty } from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  DollarOutlined,
  RiseOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getOverview, getRecentActivity } from '../api/dashboard';
import type { DashboardOverview, RecentActivity } from '../types';
import { formatDate } from '../utils';

const { Title } = Typography;

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 0,
  }).format(value);
};

const DashboardPage: React.FC = () => {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [activities, setActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [activityLoading, setActivityLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const ovResponse = await getOverview();
      if (ovResponse.success) {
        setOverview(ovResponse.data);
      }
    } catch (error) {
      console.error('Failed to load dashboard overview:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchActivities = useCallback(async () => {
    setActivityLoading(true);
    try {
      const actResponse = await getRecentActivity(10);
      if (actResponse.success) {
        setActivities(actResponse.data);
      }
    } catch (error) {
      console.error('Failed to load recent activities:', error);
    } finally {
      setActivityLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    fetchActivities();
  }, [fetchData, fetchActivities]);

  const statCards = [
    {
      title: '用户总数',
      value: overview?.stats?.total_users ?? 0,
      icon: <TeamOutlined />,
      color: '#1890ff',
    },
    {
      title: '活跃用户',
      value: overview?.stats?.active_users_today ?? 0,
      icon: <UserOutlined />,
      color: '#52c41a',
    },
    {
      title: '收入',
      value: overview?.stats?.total_revenue ?? 0,
      icon: <DollarOutlined />,
      color: '#faad14',
      formatter: formatCurrency,
    },
    {
      title: '转化率',
      value: overview?.stats?.active_users_today && overview?.stats?.total_users
        ? ((overview.stats.active_users_today / overview.stats.total_users) * 100).toFixed(1)
        : '0',
      suffix: '%',
      icon: <RiseOutlined />,
      color: '#722ed1',
    },
  ] as const;

  const actionButtons = [
    { key: 'content', label: '内容管理', path: '/content', icon: <ThunderboltOutlined />, color: '#1890ff' },
    { key: 'users', label: '用户管理', path: '/users', icon: <UserOutlined />, color: '#52c41a' },
    { key: 'tutorials', label: '教程管理', path: '/tutorials', icon: <ThunderboltOutlined />, color: '#faad14' },
    { key: 'downloads', label: '下载管理', path: '/downloads', icon: <ThunderboltOutlined />, color: '#722ed1' },
  ] as const;

  const activityColumns: ColumnsType<RecentActivity> = [
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      width: 160,
      render: (action: string) => {
        const colorMap: Record<string, string> = {
          USER_LOGIN: 'green',
          CONTENT_CREATED: 'blue',
          CONTENT_UPDATED: 'geekblue',
          CONTENT_DELETED: 'red',
          USER_REGISTERED: 'cyan',
          ORDER_PAID: 'gold',
          DOWNLOAD: 'purple',
        };
        return <Tag color={colorMap[action] || 'default'}>{action}</Tag>;
      },
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '用户',
      dataIndex: 'user',
      key: 'user',
      width: 120,
      render: (user: RecentActivity['user']) => user?.username || '-',
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => formatDate(date),
    },
  ];

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        控制面板
      </Title>

      {/* Stat Cards */}
      <Row gutter={[16, 16]}>
        {statCards.map((card) => (
          <Col xs={24} sm={12} lg={6} key={card.title}>
            <Card hoverable>
              <Statistic
                title={card.title}
                value={card.value}
                prefix={card.icon}
                suffix={card.suffix || undefined}
                valueStyle={{ color: card.color }}
                formatter={'formatter' in card ? card.formatter : undefined}
                precision={card.title === '转化率' ? 1 : 0}
              />
            </Card>
          </Col>
        ))}
      </Row>

      {/* Quick Actions */}
      <Card
        title="快捷操作"
        style={{ marginTop: 24 }}
        styles={{ body: { padding: '16px 24px' } }}
      >
        <Space wrap size="middle">
          {actionButtons.map((btn) => (
            <Button
              key={btn.key}
              type="default"
              icon={btn.icon}
              style={{ borderColor: btn.color, color: btn.color }}
            >
              {btn.label}
            </Button>
          ))}
        </Space>
      </Card>

      {/* Recent Activity Table */}
      <Card title="最近活动" style={{ marginTop: 24 }}>
        {activities.length === 0 && !activityLoading ? (
          <Empty description="暂无活动" />
        ) : (
          <Table<RecentActivity>
            columns={activityColumns}
            dataSource={activities}
            rowKey="id"
            loading={activityLoading}
            pagination={false}
            size="middle"
          />
        )}
      </Card>
    </div>
  );
};

export default DashboardPage;
