import React, { useState, useEffect, useCallback } from 'react';
import { Card, Row, Col, Statistic, Spin, message, Typography } from 'antd';
import {
  ShoppingCartOutlined,
  DollarOutlined,
  DatabaseOutlined,
  AppstoreOutlined,
} from '@ant-design/icons';
import { getStoreStats } from '../api/store';
import type { StoreStats as StoreStatsType } from '../api/store';
import { formatCurrency } from '../utils';

const { Title } = Typography;

interface StatCard {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  suffix?: React.ReactNode;
  formatter?: (value: number | string) => string;
}

const StoreStats: React.FC = () => {
  const [stats, setStats] = useState<StoreStatsType | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getStoreStats();
      if (response.success) {
        setStats(response.data);
      } else {
        message.error('加载商城统计数据失败');
      }
    } catch {
      message.error('加载商城统计数据失败');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  if (loading) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: 400,
        }}
      >
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  const statCards: StatCard[] = [
    {
      title: '产品线',
      value: stats?.total_collections ?? 0,
      icon: <AppstoreOutlined />,
      color: '#1890ff',
      suffix: (
        <span style={{ fontSize: 14, color: '#8c8c8c' }}>
          / {stats?.active_collections ?? 0} 活跃
        </span>
      ),
    },
    {
      title: '商品',
      value: stats?.total_products ?? 0,
      icon: <DatabaseOutlined />,
      color: '#52c41a',
      suffix: (
        <span style={{ fontSize: 14, color: '#8c8c8c' }}>
          / {stats?.active_products ?? 0} 活跃
        </span>
      ),
    },
    {
      title: '订单',
      value: stats?.total_orders ?? 0,
      icon: <ShoppingCartOutlined />,
      color: '#faad14',
      suffix: (
        <span style={{ fontSize: 14, color: '#8c8c8c' }}>
          / {stats?.pending_orders ?? 0} 待处理
        </span>
      ),
    },
    {
      title: '总营收',
      value: stats?.total_revenue ?? 0,
      icon: <DollarOutlined />,
      color: '#cf1322',
      formatter: (val: number | string) => formatCurrency(Number(val)),
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        商城数据概览
      </Title>

      <Row gutter={[16, 16]}>
        {statCards.map((card) => (
          <Col xs={24} sm={12} lg={6} key={card.title}>
            <Card hoverable>
              <Statistic
                title={card.title}
                value={card.value}
                prefix={card.icon}
                suffix={card.suffix}
                valueStyle={{ color: card.color }}
                formatter={card.formatter}
              />
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default StoreStats;
