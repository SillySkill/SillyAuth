import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Typography } from 'antd';
import {
  FileTextOutlined,
  MenuOutlined,
  PictureOutlined,
  ToolOutlined,
  TeamOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { getDashboardStats, getActivityLogs } from '@/api/dashboard';
import type { DashboardStats } from '@/api/dashboard';
import { formatDate } from '@/utils';

const { Title } = Typography;

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, logsRes] = await Promise.all([
        getDashboardStats(),
        getActivityLogs({ page: 1, limit: 10 }),
      ]);
      setStats(statsRes.data);
      setLogs(logsRes.data);
    } catch (error) {
      console.error('获取仪表盘数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      render: (action: string) => {
        const actionMap: Record<string, { text: string; color: string }> = {
          USER_LOGIN: { text: '用户登录', color: 'green' },
          CONTENT_CREATED: { text: '创建内容', color: 'blue' },
          CONTENT_UPDATED: { text: '更新内容', color: 'blue' },
          CONTENT_DELETED: { text: '删除内容', color: 'red' },
          NAVIGATION_CREATED: { text: '创建导航', color: 'purple' },
          CAROUSEL_CREATED: { text: '创建轮播图', color: 'orange' },
        };
        const info = actionMap[action] || { text: action, color: 'default' };
        return <Tag color={info.color}>{info.text}</Tag>;
      },
    },
    {
      title: '用户',
      dataIndex: 'user',
      key: 'user',
      render: (user: any) => user?.username || '-',
    },
    {
      title: '时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (date: string) => formatDate(date),
    },
  ];

  const statCards = [
    {
      title: '内容总数',
      value: stats?.content.total || 0,
      prefix: <FileTextOutlined />,
      color: '#1890ff',
    },
    {
      title: '已发布',
      value: stats?.content.published || 0,
      prefix: <FileTextOutlined />,
      color: '#52c41a',
    },
    {
      title: '草稿',
      value: stats?.content.draft || 0,
      prefix: <FileTextOutlined />,
      color: '#faad14',
    },
    {
      title: '导航菜单',
      value: stats?.navigation.total || 0,
      prefix: <MenuOutlined />,
      color: '#722ed1',
    },
    {
      title: '轮播图',
      value: stats?.carousel.total || 0,
      prefix: <PictureOutlined />,
      color: '#eb2f96',
    },
    {
      title: '技能',
      value: stats?.skill.total || 0,
      prefix: <ToolOutlined />,
      color: '#fa8c16',
    },
    {
      title: '供应商',
      value: stats?.vendor.total || 0,
      prefix: <TeamOutlined />,
      color: '#13c2c2',
    },
    {
      title: '用户',
      value: stats?.user.total || 0,
      prefix: <UserOutlined />,
      color: '#2f54eb',
    },
  ];

  return (
    <div>
      <Title level={2}>仪表盘</Title>
      <Row gutter={16} style={{ marginTop: 24 }}>
        {statCards.map((card, index) => (
          <Col span={6} key={index} style={{ marginBottom: 16 }}>
            <Card>
              <Statistic
                title={card.title}
                value={card.value}
                prefix={card.prefix}
                valueStyle={{ color: card.color }}
              />
            </Card>
          </Col>
        ))}
      </Row>

      <Card title="最近操作" style={{ marginTop: 24 }}>
        <Table
          columns={columns}
          dataSource={logs}
          rowKey="id"
          loading={loading}
          pagination={false}
        />
      </Card>
    </div>
  );
};

export default Dashboard;
