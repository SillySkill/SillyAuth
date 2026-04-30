/**
 * 创作者收益页面
 * Creator Earnings
 *
 * 创作者查看收益、设置结算偏好、申请结算
 */
import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  InputNumber,
  message,
  Card,
  Row,
  Col,
  Statistic,
  Tabs,
  Descriptions,
  Alert
} from 'antd';
import {
  DollarOutlined,
  TrophyOutlined,
  GiftOutlined,
  WalletOutlined,
  SettingOutlined,
  HistoryOutlined,
  PayCircleOutlined,
  WechatOutlined,
  AlipayOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { TabPane } = Tabs;

interface EarningRecord {
  id: number;
  order_id: number;
  content_type: string;
  content_id: number;
  gross_amount: number;
  platform_commission: number;
  creator_share: number;
  settlement_status: string;
  settlement_method: string;
  settlement_amount: number;
  points_awarded: number;
  settled_at: string;
  created_at: string;
}

interface SettlementRecord {
  id: number;
  batch_number: string;
  total_orders: number;
  total_amount: number;
  total_commission: number;
  total_earnings: number;
  settlement_method: string;
  status: string;
  transaction_id: string;
  period_start: string;
  period_end: string;
  created_at: string;
  processed_at: string;
}

interface EarningsSummary {
  settlement_method: string;
  auto_settle: boolean;
  total_earnings_count: number;
  pending_earnings: number;
  settled_amount: number;
  points_earned: number;
  total_orders_count: number;
  total_gross_amount: number;
  total_platform_commission: number;
}

const CreatorEarnings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'earnings' | 'settlements' | 'settings'>('overview');
  const [earnings, setEarnings] = useState<EarningRecord[]>([]);
  const [settlements, setSettlements] = useState<SettlementRecord[]>([]);
  const [summary, setSummary] = useState<EarningsSummary | null>(null);
  const [loading, setLoading] = useState(false);

  // Settings modal
  const [settingsVisible, setSettingsVisible] = useState(false);

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    if (activeTab === 'overview' || activeTab === 'earnings') loadEarnings();
    if (activeTab === 'overview' || activeTab === 'settlements') loadSettlements();
    if (activeTab === 'overview') loadSummary();
  };

  const loadSummary = async () => {
    setLoading(true);
    try {
      // TODO: 调用 API
      // const response = await paymentAccountsApi.getEarningsSummary();
      // setSummary(response.data);
      setSummary({
        settlement_method: 'direct',
        auto_settle: false,
        total_earnings_count: 150,
        pending_earnings: 2580.50,
        settled_amount: 12450.00,
        points_earned: 5200,
        total_orders_count: 150,
        total_gross_amount: 17800.00,
        total_platform_commission: 2769.50
      });
    } catch (error) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const loadEarnings = async () => {
    setLoading(true);
    try {
      // TODO: 调用 API
      // const response = await paymentAccountsApi.getEarnings();
      // setEarnings(response.data);
      setEarnings([]);
    } catch (error) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const loadSettlements = async () => {
    setLoading(true);
    try {
      // TODO: 调用 API
      // const response = await paymentAccountsApi.getSettlements();
      // setSettlements(response.data);
      setSettlements([
        {
          id: 1,
          batch_number: 'STL20240201123456789001',
          total_orders: 45,
          total_amount: 6800.00,
          total_commission: 2040.00,
          total_earnings: 4760.00,
          settlement_method: 'direct',
          status: 'completed',
          transaction_id: 'TXN2024020112345',
          period_start: '2024-01-01',
          period_end: '2024-01-31',
          created_at: '2024-02-01T10:00:00Z',
          processed_at: '2024-02-01T14:30:00Z'
        }
      ]);
    } catch (error) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSettle = async () => {
    if (!summary || summary.pending_earnings < 100) {
      message.warning('待结算金额不足 100 元');
      return;
    }

    Modal.confirm({
      title: '申请结算',
      content: `确认结算待结算金额 ¥${summary.pending_earnings.toFixed(2)} 吗？`,
      onOk: async () => {
        try {
          // TODO: 调用 API
          // await paymentAccountsApi.settle({ ... });
          message.success('结算申请已提交');
          loadData();
        } catch (error) {
          message.error('结算失败');
        }
      }
    });
  };

  const handleSaveSettings = async (values: any) => {
    try {
      // TODO: 调用 API
      // await paymentAccountsApi.updatePreference(values);
      message.success('设置保存成功');
      setSettingsVisible(false);
      loadData();
    } catch (error) {
      message.error('保存失败');
    }
  };

  const earningColumns: ColumnsType<EarningRecord> = [
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString()
    },
    {
      title: '订单',
      dataIndex: 'order_id',
      key: 'order_id',
      width: 100
    },
    {
      title: '内容',
      key: 'content',
      width: 150,
      render: (_, record: EarningRecord) => (
        <div>
          <Tag>{record.content_type}</Tag>
          <span style={{ fontSize: 12 }}>ID: {record.content_id}</span>
        </div>
      )
    },
    {
      title: '总金额',
      dataIndex: 'gross_amount',
      key: 'gross_amount',
      render: (amount: number) => `¥${amount.toFixed(2)}`
    },
    {
      title: '平台佣金',
      dataIndex: 'platform_commission',
      key: 'platform_commission',
      render: (amount: number) => <span style={{ color: '#ff4d4f' }}>-¥{amount.toFixed(2)}</span>
    },
    {
      title: '创作者分成',
      dataIndex: 'creator_share',
      key: 'creator_share',
      render: (amount: number) => <span style={{ color: '#52c41a', fontWeight: 600 }}>+¥{amount.toFixed(2)}</span>
    },
    {
      title: '结算状态',
      dataIndex: 'settlement_status',
      key: 'settlement_status',
      width: 120,
      render: (status: string) => {
        const map = {
          'pending': { text: '待结算', color: 'orange' },
          'settled': { text: '已结算', color: 'green' },
          'points_converted': { text: '已转积分', color: 'blue' },
          'failed': { text: '失败', color: 'red' }
        };
        const config = map[status] || { text: status, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '结算方式',
      dataIndex: 'settlement_method',
      key: 'settlement_method',
      width: 100,
      render: (method: string) => {
        const map = {
          'direct': { text: '直接分佣', color: 'blue' },
          'points': { text: '积分转换', color: 'green' }
        };
        const config = map[method] || { text: method, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    }
  ];

  const settlementColumns: ColumnsType<SettlementRecord> = [
    {
      title: '批次号',
      dataIndex: 'batch_number',
      key: 'batch_number',
      width: 200,
      render: (text: string) => <code>{text}</code>
    },
    {
      title: '订单数',
      dataIndex: 'total_orders',
      key: 'total_orders',
      width: 100
    },
    {
      title: '总金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (amount: number) => `¥${amount.toFixed(2)}`
    },
    {
      title: '创作者收益',
      dataIndex: 'total_earnings',
      key: 'total_earnings',
      render: (amount: number) => <span style={{ color: '#52c41a', fontWeight: 600 }}>¥{amount.toFixed(2)}</span>
    },
    {
      title: '结算方式',
      dataIndex: 'settlement_method',
      key: 'settlement_method',
      width: 100,
      render: (method: string) => {
        const map = {
          'direct': { text: '直接分佣', color: 'blue' },
          'points': { text: '积分转换', color: 'green' }
        };
        const config = map[method] || { text: method, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const map = {
          'processing': { text: '处理中', color: 'blue' },
          'completed': { text: '已完成', color: 'green' },
          'failed': { text: '失败', color: 'red' },
          'cancelled': { text: '已取消', color: 'default' }
        };
        const config = map[status] || { text: status, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '结算周期',
      key: 'period',
      width: 180,
      render: (_, record: SettlementRecord) => (
        <div style={{ fontSize: 12 }}>
          {record.period_start} ~ {record.period_end}
        </div>
      )
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString()
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h2>创作者收益</h2>
        <p style={{ color: 'var(--text-light)' }}>
          查看收益、设置结算偏好、申请提现
        </p>
      </div>

      <Card>
        <Tabs activeKey={activeTab} onChange={(key) => setActiveTab(key as any)}>
          {/* 收益概览 */}
          <TabPane tab={<span><TrophyOutlined /> 收益概览</span>} key="overview">
            {summary && (
              <>
                <Row gutter={16} style={{ marginBottom: 24 }}>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="待结算金额"
                        value={summary.pending_earnings}
                        precision={2}
                        prefix="¥"
                        valueStyle={{ color: '#faad14' }}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="已结算金额"
                        value={summary.settled_amount}
                        precision={2}
                        prefix="¥"
                        valueStyle={{ color: '#52c41a' }}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="积分收益"
                        value={summary.points_earned}
                        prefix={<GiftOutlined />}
                        valueStyle={{ color: '#1890ff' }}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card>
                      <Statistic
                        title="总订单数"
                        value={summary.total_orders_count}
                        suffix="笔"
                      />
                    </Card>
                  </Col>
                </Row>

                <Descriptions title="收益详情" bordered column={2}>
                  <Descriptions.Item label="结算方式">
                    {summary.settlement_method === 'direct' ? '直接分佣' : '积分转换'}
                  </Descriptions.Item>
                  <Descriptions.Item label="自动结算">
                    {summary.auto_settle ? <Tag color="green">是</Tag> : <Tag>否</Tag>}
                  </Descriptions.Item>
                  <Descriptions.Item label="总销售额">
                    ¥{summary.total_gross_amount.toFixed(2)}
                  </Descriptions.Item>
                  <Descriptions.Item label="平台佣金">
                    ¥{summary.total_platform_commission.toFixed(2)}
                  </Descriptions.Item>
                  <Descriptions.Item label="创作者分成">
                    ¥{(summary.total_gross_amount - summary.total_platform_commission).toFixed(2)}
                  </Descriptions.Item>
                  <Descriptions.Item label="分成比例">
                    {((1 - summary.total_platform_commission / summary.total_gross_amount) * 100).toFixed(1)}%
                  </Descriptions.Item>
                </Descriptions>

                {summary.pending_earnings >= 100 && (
                  <Alert
                    message="您可以申请结算"
                    description={`当前待结算金额 ¥${summary.pending_earnings.toFixed(2)} 已达到最低结算标准`}
                    type="success"
                    showIcon
                    action={
                      <Button type="primary" size="small" onClick={handleSettle}>
                        立即结算
                      </Button>
                    }
                    style={{ marginTop: 16 }}
                  />
                )}
              </>
            )}
          </TabPane>

          {/* 收益明细 */}
          <TabPane tab={<span><DollarOutlined /> 收益明细</span>} key="earnings">
            <Table
              columns={earningColumns}
              dataSource={earnings}
              rowKey="id"
              loading={loading}
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 条记录`
              }}
            />
          </TabPane>

          {/* 结算记录 */}
          <TabPane tab={<span><HistoryOutlined /> 结算记录</span>} key="settlements">
            <Table
              columns={settlementColumns}
              dataSource={settlements}
              rowKey="id"
              loading={loading}
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 条记录`
              }}
            />
          </TabPane>

          {/* 结算设置 */}
          <TabPane tab={<span><SettingOutlined /> 结算设置</span>} key="settings">
            <Card title="结算偏好设置">
              <Form
                layout="vertical"
                onFinish={handleSaveSettings}
                initialValues={{
                  settlement_method: summary?.settlement_method || 'direct',
                  auto_settle: summary?.auto_settle || false,
                  min_settlement_amount: 100,
                  settlement_period: 'monthly'
                }}
              >
                <Form.Item
                  label="结算方式"
                  name="settlement_method"
                  extra="直接分佣：收益结算到收款账户；积分转换：收益转换为平台积分"
                >
                  <Select>
                    <Select.Option value="direct">
                      <Space>
                        <WalletOutlined />
                        直接分佣（结算到收款账户）
                      </Space>
                    </Select.Option>
                    <Select.Option value="points">
                      <Space>
                        <GiftOutlined />
                        积分转换（自动转换为平台积分）
                      </Space>
                    </Select.Option>
                  </Select>
                </Form.Item>

                <Form.Item
                  label="收款方式"
                  name="payment_account_type"
                >
                  <Select placeholder="选择收款方式">
                    <Select.Option value="alipay">
                      <Space>
                        <AlipayOutlined />
                        支付宝
                      </Space>
                    </Select.Option>
                    <Select.Option value="wechat">
                      <Space>
                        <WechatOutlined />
                        微信支付
                      </Space>
                    </Select.Option>
                    <Select.Option value="paypal">
                      <Space>
                        <PayCircleOutlined />
                        PayPal
                      </Space>
                    </Select.Option>
                    <Select.Option value="bank">银行账户</Select.Option>
                  </Select>
                </Form.Item>

                <Form.Item
                  label="收款账号"
                  name="payment_account_id"
                >
                  <Input placeholder="输入您的收款账号" />
                </Form.Item>

                <Form.Item
                  label="自动结算"
                  name="auto_settle"
                  valuePropName="checked"
                  extra="达到最低结算金额后自动结算，无需手动申请"
                >
                  <Switch checkedChildren="开启" unCheckedChildren="关闭" />
                </Form.Item>

                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      label="最低结算金额"
                      name="min_settlement_amount"
                      extra="待结算金额达到此数值后方可申请结算"
                    >
                      <InputNumber
                        style={{ width: '100%' }}
                        min={10}
                        max={100000}
                        addonAfter="元"
                      />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      label="结算周期"
                      name="settlement_period"
                    >
                      <Select>
                        <Select.Option value="weekly">每周结算</Select.Option>
                        <Select.Option value="monthly">每月结算</Select.Option>
                        <Select.Option value="quarterly">每季度结算</Select.Option>
                      </Select>
                    </Form.Item>
                  </Col>
                </Row>

                <Form.Item>
                  <Button type="primary" htmlType="submit" size="large">
                    保存设置
                  </Button>
                </Form.Item>
              </Form>
            </Card>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default CreatorEarnings;
