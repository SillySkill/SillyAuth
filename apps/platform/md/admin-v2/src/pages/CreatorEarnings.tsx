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
      const msg = error instanceof Error ? error.message : 'Failed to load pending settlements';
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
      const msg = error instanceof Error ? error.message : 'Failed to load revenue stats';
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
      message.success(`Successfully settled creator "${selectedCreator.username}"`);
      setSettleModalVisible(false);
      setSelectedCreator(null);
      loadPendingSettlements();
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) return;
      const msg = error instanceof Error ? error.message : 'Settlement failed';
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
      title: 'User ID',
      dataIndex: 'user_id',
      key: 'user_id',
      width: 80,
    },
    {
      title: 'Username',
      dataIndex: 'username',
      key: 'username',
      ellipsis: true,
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      ellipsis: true,
    },
    {
      title: 'Settlement Method',
      dataIndex: 'settlement_method',
      key: 'settlement_method',
      width: 150,
      render: (method: string) => (
        <Tag color={getStatusColor(method)}>{method.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Pending Count',
      dataIndex: 'pending_count',
      key: 'pending_count',
      width: 130,
      sorter: (a, b) => a.pending_count - b.pending_count,
    },
    {
      title: 'Total Pending Amount',
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
      title: 'Oldest Earning Date',
      dataIndex: 'oldest_earning_date',
      key: 'oldest_earning_date',
      width: 170,
      render: (date: string) => (date ? new Date(date).toLocaleDateString() : 'N/A'),
    },
    {
      title: 'Action',
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
          Settle
        </Button>
      ),
    },
  ];

  // ============================================================
  // Columns - Revenue Stats
  // ============================================================

  const revenueColumns: ColumnsType<RevenueStat> = [
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
    },
    {
      title: 'Paid Orders',
      dataIndex: 'paid_orders',
      key: 'paid_orders',
      sorter: (a, b) => a.paid_orders - b.paid_orders,
    },
    {
      title: 'Total Revenue',
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
          <DollarOutlined /> Pending Settlements
        </span>
      ),
      children: (
        <>
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={8}>
              <Card>
                <Statistic
                  title="Creators Pending"
                  value={settlements.length}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Statistic
                  title="Total Pending Amount"
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
                  title="Pending Settlements Count"
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
              showTotal: (total) => `Total ${total} creators`,
            }}
            scroll={{ x: 1100 }}
            locale={{
              emptyText: <Empty description="No pending settlements" />,
            }}
          />
        </>
      ),
    },
    {
      key: 'stats',
      label: (
        <span>
          <BarChartOutlined /> Revenue Stats
        </span>
      ),
      children: (
        <>
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={6}>
              <Card>
                <Statistic
                  title="Total Paid Orders"
                  value={totalPaidOrders}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="Total Revenue"
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
                  title="Avg. Daily Revenue"
                  value={revenueStats.length > 0 ? totalRevenue / revenueStats.length : 0}
                  precision={2}
                  prefix="¥"
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col span={6}>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ marginBottom: 4, fontSize: 13, color: '#888' }}>Period</span>
                <Select
                  value={revenueDays}
                  onChange={handleRevenueDaysChange}
                  style={{ width: '100%' }}
                  options={[
                    { label: 'Last 7 Days', value: 7 },
                    { label: 'Last 14 Days', value: 14 },
                    { label: 'Last 30 Days', value: 30 },
                    { label: 'Last 90 Days', value: 90 },
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
              showTotal: (total) => `Total ${total} records`,
            }}
            locale={{
              emptyText: <Empty description="No revenue data available" />,
            }}
          />
        </>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>Creator Earnings</Title>
        <p style={{ color: '#888' }}>
          Manage creator settlements and view revenue statistics.
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
            Refresh
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
        title="Settle Creator Earnings"
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
            Creator: <strong>{selectedCreator?.username}</strong>
          </p>
          <p>
            Pending Amount:{' '}
            <strong style={{ color: '#faad14' }}>
              ¥
              {selectedCreator?.total_pending_amount != null
                ? Number(selectedCreator.total_pending_amount).toFixed(2)
                : '0.00'}
            </strong>
          </p>
          <p>
            Pending Count: <strong>{selectedCreator?.pending_count}</strong>
          </p>
        </div>
        <Form form={settleForm} layout="vertical">
          <Form.Item
            name="payment_account_id"
            label="Payment Account"
            rules={[{ required: true, message: 'Please select a payment account' }]}
          >
            <Select
              placeholder="Select payment account"
              options={[
                { label: 'WeChat Main Account', value: 1 },
                { label: 'Alipay Main Account', value: 2 },
                { label: 'PayPal Account', value: 3 },
              ]}
            />
          </Form.Item>
          <Form.Item name="notes" label="Notes">
            <Input placeholder="Settlement notes (optional)" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default CreatorEarnings;
