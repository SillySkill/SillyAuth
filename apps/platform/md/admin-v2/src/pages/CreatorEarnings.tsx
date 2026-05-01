/**
 * Creator Earnings Admin Page
 *
 * Two tabs:
 *   1. "Pending Settlements" - View and settle creators' pending earnings.
 *   2. "Revenue Stats" - Revenue statistics filtered by time period.
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  message,
  Card,
  Tabs,
  Typography,
  Empty,
  Spin,
  Statistic,
  Row,
  Col,
} from 'antd';
import {
  DollarOutlined,
  BarChartOutlined,
  ReloadOutlined,
  PayCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';
import type { SorterResult } from 'antd/es/table/interface';
import {
  getPendingSettlements,
  settleCreator,
  getRevenueStats,
} from '../api/payment';

const { Title } = Typography;

// ============================================================
// Interfaces
// ============================================================

interface CreatorPendingSettlement {
  user_id: number;
  username: string;
  email: string;
  settlement_method: string;
  pending_count: number;
  total_pending_amount: number;
  oldest_earning_date: string;
}

interface RevenueStat {
  date: string;
  paid_orders: number;
  total_revenue: number;
}

// ============================================================
// Component
// ============================================================

const CreatorEarnings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'pending' | 'stats'>('pending');
  const [settlements, setSettlements] = useState<CreatorPendingSettlement[]>([]);
  const [revenueStats, setRevenueStats] = useState<RevenueStat[]>([]);
  const [loading, setLoading] = useState(false);
  const [settleModalVisible, setSettleModalVisible] = useState(false);
  const [selectedCreator, setSelectedCreator] = useState<CreatorPendingSettlement | null>(null);
  const [revenueDays, setRevenueDays] = useState(30);
  const [submitting, setSubmitting] = useState(false);

  const [settleForm] = Form.useForm();

  // ============================================================
  // Data Loading
  // ============================================================

  const loadPendingSettlements = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getPendingSettlements();
      const data = response?.data?.items ?? response?.data ?? [];
      setSettlements(Array.isArray(data) ? data : []);
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : '加载待结算列表失败';
      message.error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadRevenueStats = useCallback(async (days: number) => {
    setLoading(true);
    try {
      const response = await getRevenueStats(days);
      const data = Array.isArray(response?.data)
        ? response.data
        : response?.data?.items ?? [];
      setRevenueStats(Array.isArray(data) ? data : []);
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : '加载收入统计失败';
      message.error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'pending') {
      loadPendingSettlements();
    } else {
      loadRevenueStats(revenueDays);
    }
  }, [activeTab, revenueDays, loadPendingSettlements, loadRevenueStats]);

  // ============================================================
  // Handlers
  // ============================================================

  const handleSettleClick = (record: CreatorPendingSettlement) => {
    setSelectedCreator(record);
    settleForm.resetFields();
    setSettleModalVisible(true);
  };

  const handleSettleConfirm = async () => {
    if (!selectedCreator) return;
    try {
      const values = await settleForm.validateFields();
      setSubmitting(true);
      await settleCreator(selectedCreator.user_id, {
        payment_account_id: values.payment_account_id,
        notes: values.notes,
      });
      message.success(`已成功结算创作者 "${selectedCreator.username}"`);
      setSettleModalVisible(false);
      setSelectedCreator(null);
      loadPendingSettlements();
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) return;
      const msg = error instanceof Error ? error.message : '结算失败';
      message.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRevenueDaysChange = (value: number) => {
    setRevenueDays(value);
  };

  const getStatusColor = (method: string) => {
    const map: Record<string, string> = {
      direct: 'blue',
      points: 'green',
      wechat: 'green',
      alipay: 'blue',
      paypal: 'geekblue',
      bank: 'purple',
    };
    return map[method] || 'default';
  };

  // ============================================================
  // Columns - Pending Settlements
  // ============================================================

  const settlementColumns: ColumnsType<CreatorPendingSettlement> = [
    {
      title: '用户ID',
      dataIndex: 'user_id',
      key: 'user_id',
      width: 80,
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      ellipsis: true,
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      ellipsis: true,
    },
    {
      title: '结算方式',
      dataIndex: 'settlement_method',
      key: 'settlement_method',
      width: 150,
      render: (method: string) => (
        <Tag color={getStatusColor(method)}>{method.toUpperCase()}</Tag>
      ),
    },
    {
      title: '待结笔数',
      dataIndex: 'pending_count',
      key: 'pending_count',
      width: 130,
      sorter: (a, b) => a.pending_count - b.pending_count,
    },
    {
      title: '待结算金额',
      dataIndex: 'total_pending_amount',
      key: 'total_pending_amount',
      width: 180,
      sorter: (a, b) => a.total_pending_amount - b.total_pending_amount,
      render: (amount: number) => (
        <span style={{ color: '#faad14', fontWeight: 600 }}>
          {amount != null ? `¥${Number(amount).toFixed(2)}` : '¥0.00'}
        </span>
      ),
    },
    {
      title: '最早收入日期',
      dataIndex: 'oldest_earning_date',
      key: 'oldest_earning_date',
      width: 170,
      render: (date: string) => (date ? new Date(date).toLocaleDateString() : '无'),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      fixed: 'right',
      render: (_: unknown, record: CreatorPendingSettlement) => (
        <Button
          type="primary"
          size="small"
          icon={<PayCircleOutlined />}
          onClick={() => handleSettleClick(record)}
        >
          结算
        </Button>
      ),
    },
  ];

  // ============================================================
  // Columns - Revenue Stats
  // ============================================================

  const revenueColumns: ColumnsType<RevenueStat> = [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
    },
    {
      title: '已支付订单',
      dataIndex: 'paid_orders',
      key: 'paid_orders',
      sorter: (a, b) => a.paid_orders - b.paid_orders,
    },
    {
      title: '总收入',
      dataIndex: 'total_revenue',
      key: 'total_revenue',
      sorter: (a, b) => a.total_revenue - b.total_revenue,
      render: (amount: number) => (
        <span style={{ color: '#52c41a', fontWeight: 600 }}>
          {amount != null ? `¥${Number(amount).toFixed(2)}` : '¥0.00'}
        </span>
      ),
    },
  ];

  // ============================================================
  // Summary stats
  // ============================================================

  const totalPending = settlements.reduce(
    (sum, s) => sum + (Number(s.total_pending_amount) || 0),
    0
  );
  const totalPendingCount = settlements.reduce(
    (sum, s) => sum + (s.pending_count || 0),
    0
  );
  const totalRevenue = revenueStats.reduce(
    (sum, s) => sum + (Number(s.total_revenue) || 0),
    0
  );
  const totalPaidOrders = revenueStats.reduce(
    (sum, s) => sum + (s.paid_orders || 0),
    0
  );

  // ============================================================
  // Render
  // ============================================================

  const tabItems = [
    {
      key: 'pending',
      label: (
        <span>
          <DollarOutlined /> 待结算
        </span>
      ),
      children: (
        <>
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={8}>
              <Card>
                <Statistic
                  title="待结算创作者"
                  value={settlements.length}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Statistic
                  title="待结算总额"
                  value={totalPending}
                  precision={2}
                  prefix="¥"
                  valueStyle={{ color: '#faad14' }}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Statistic
                  title="待结算笔数"
                  value={totalPendingCount}
                />
              </Card>
            </Col>
          </Row>
          <Table
            columns={settlementColumns}
            dataSource={settlements}
            rowKey="user_id"
            loading={loading}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 位创作者`,
            }}
            scroll={{ x: 1100 }}
            locale={{
              emptyText: <Empty description="暂无待结算记录" />,
            }}
          />
        </>
      ),
    },
    {
      key: 'stats',
      label: (
        <span>
          <BarChartOutlined /> 收入统计
        </span>
      ),
      children: (
        <>
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={6}>
              <Card>
                <Statistic
                  title="总支付订单"
                  value={totalPaidOrders}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="总收入"
                  value={totalRevenue}
                  precision={2}
                  prefix="¥"
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="日均收入"
                  value={revenueStats.length > 0 ? totalRevenue / revenueStats.length : 0}
                  precision={2}
                  prefix="¥"
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col span={6}>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ marginBottom: 4, fontSize: 13, color: '#888' }}>时间范围</span>
                <Select
                  value={revenueDays}
                  onChange={handleRevenueDaysChange}
                  style={{ width: '100%' }}
                  options={[
                    { label: '最近7天', value: 7 },
                    { label: '最近14天', value: 14 },
                    { label: '最近30天', value: 30 },
                    { label: '最近90天', value: 90 },
                  ]}
                />
              </div>
            </Col>
          </Row>
          <Table
            columns={revenueColumns}
            dataSource={revenueStats}
            rowKey="date"
            loading={loading}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 条记录`,
            }}
            locale={{
              emptyText: <Empty description="暂无收入数据" />,
            }}
          />
        </>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>创作者收益</Title>
        <p style={{ color: '#888' }}>
          管理创作者结算并查看收入统计数据。
        </p>
      </div>

      <Card
        extra={
          <Button
            icon={<ReloadOutlined />}
            onClick={() => {
              if (activeTab === 'pending') loadPendingSettlements();
              else loadRevenueStats(revenueDays);
            }}
          >
            刷新
          </Button>
        }
      >
        <Tabs
          activeKey={activeTab}
          onChange={(key) => setActiveTab(key as 'pending' | 'stats')}
          items={tabItems}
        />
      </Card>

      {/* Settle Modal */}
      <Modal
        title="结算创作者收益"
        open={settleModalVisible}
        onOk={handleSettleConfirm}
        onCancel={() => {
          setSettleModalVisible(false);
          setSelectedCreator(null);
        }}
        confirmLoading={submitting}
        destroyOnClose
      >
        <div style={{ marginBottom: 16 }}>
          <p>
            创作者：<strong>{selectedCreator?.username}</strong>
          </p>
          <p>
            待结金额：{' '}
            <strong style={{ color: '#faad14' }}>
              ¥
              {selectedCreator?.total_pending_amount != null
                ? Number(selectedCreator.total_pending_amount).toFixed(2)
                : '0.00'}
            </strong>
          </p>
          <p>
            待结笔数：<strong>{selectedCreator?.pending_count}</strong>
          </p>
        </div>
        <Form form={settleForm} layout="vertical">
          <Form.Item
            name="payment_account_id"
            label="支付账户"
            rules={[{ required: true, message: '请选择支付账户' }]}
          >
            <Select
              placeholder="选择支付账户"
              options={[
                { label: '微信主账户', value: 1 },
                { label: '支付宝主账户', value: 2 },
                { label: 'PayPal 账户', value: 3 },
              ]}
            />
          </Form.Item>
          <Form.Item name="notes" label="备注">
            <Input placeholder="结算备注（选填）" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default CreatorEarnings;
