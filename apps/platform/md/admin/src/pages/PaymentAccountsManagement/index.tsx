/**
 * 收款账户管理页面
 * Payment Accounts Management
 *
 * 管理平台的收款账户配置（微信、支付宝、PayPal等）
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
  Popconfirm,
  Tabs
} from 'antd';
import {
  BankOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  WechatOutlined,
  AlipayOutlined,
  PayCircleOutlined,
  CreditCardOutlined,
  EyeInvisibleOutlined,
  EyeOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { TabPane } = Tabs;
const { TextArea } = Input;

interface PaymentAccount {
  id: number;
  account_type: string;
  account_name: string;
  account_id: string;
  credentials: Record<string, any>;
  is_active: boolean;
  is_primary: boolean;
  priority: number;
  currency: string;
  description: string;
  created_at: string;
  updated_at: string;
}

interface CreatorSettlement {
  user_id: number;
  username: string;
  email: string;
  settlement_method: string;
  payment_account_type: string;
  payment_account_id: string;
  min_settlement_amount: number;
  pending_count: number;
  total_pending_amount: number;
  oldest_earning_date: string;
  latest_earning_date: string;
}

const PaymentAccountsManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'accounts' | 'settlements'>('accounts');
  const [accounts, setAccounts] = useState<PaymentAccount[]>([]);
  const [pendingSettlements, setPendingSettlements] = useState<CreatorSettlement[]>([]);
  const [loading, setLoading] = useState(false);

  // Modal states
  const [accountModalVisible, setAccountModalVisible] = useState(false);
  const [editingAccount, setEditingAccount] = useState<PaymentAccount | null>(null);
  const [showCredentials, setShowCredentials] = useState<Record<number, boolean>>({});

  useEffect(() => {
    if (activeTab === 'accounts') loadAccounts();
    if (activeTab === 'settlements') loadPendingSettlements();
  }, [activeTab]);

  const loadAccounts = async () => {
    setLoading(true);
    try {
      // TODO: 调用 API
      // const response = await paymentAccountsApi.list();
      // setAccounts(response.data);
      setAccounts([
        {
          id: 1,
          account_type: 'wechat',
          account_name: '微信支付-主账户',
          account_id: 'default_wechat',
          credentials: { mch_id: '1234567890', api_key: '***' },
          is_active: true,
          is_primary: true,
          priority: 100,
          currency: 'CNY',
          description: '微信支付主要收款账户',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 2,
          account_type: 'alipay',
          account_name: '支付宝-主账户',
          account_id: 'default_alipay',
          credentials: { app_id: '2021001234567890', private_key: '***' },
          is_active: true,
          is_primary: true,
          priority: 100,
          currency: 'CNY',
          description: '支付宝主要收款账户',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 3,
          account_type: 'paypal',
          account_name: 'PayPal-Sandbox',
          account_id: 'default_paypal_sandbox',
          credentials: { client_id: 'ATxxxxxxxx', client_secret: '***', mode: 'sandbox' },
          is_active: true,
          is_primary: true,
          priority: 100,
          currency: 'USD',
          description: 'PayPal 沙盒环境测试账户',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ]);
    } catch (error) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const loadPendingSettlements = async () => {
    setLoading(true);
    try {
      // TODO: 调用 API
      // const response = await paymentAccountsApi.getPendingSettlements();
      // setPendingSettlements(response.data);
      setPendingSettlements([]);
    } catch (error) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAddAccount = () => {
    setEditingAccount(null);
    setAccountModalVisible(true);
  };

  const handleEditAccount = (account: PaymentAccount) => {
    setEditingAccount(account);
    setAccountModalVisible(true);
  };

  const handleDeleteAccount = async (id: number) => {
    try {
      // TODO: 调用 API
      // await paymentAccountsApi.delete(id);
      message.success('删除成功');
      loadAccounts();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSettleCreator = async (userId: number, username: string) => {
    Modal.confirm({
      title: '结算创作者收益',
      content: `确认为创作者 "${username}" 结算所有待结算收益吗？`,
      onOk: async () => {
        try {
          // TODO: 调用 API
          // await paymentAccountsApi.adminSettle(userId, { ... });
          message.success('结算成功');
          loadPendingSettlements();
        } catch (error) {
          message.error('结算失败');
        }
      }
    });
  };

  const getAccountIcon = (type: string) => {
    const icons: any = {
      wechat: <WechatOutlined style={{ fontSize: 24, color: '#09BB07' }} />,
      alipay: <AlipayOutlined style={{ fontSize: 24, color: '#1677FF' }} />,
      paypal: <PayCircleOutlined style={{ fontSize: 24, color: '#003087' }} />,
      bank: <CreditCardOutlined style={{ fontSize: 24, color: '#722ED1' }} />
    };
    return icons[type] || <BankOutlined style={{ fontSize: 24 }} />;
  };

  const accountColumns: ColumnsType<PaymentAccount> = [
    {
      title: '类型',
      dataIndex: 'account_type',
      key: 'account_type',
      width: 100,
      render: (type: string) => (
        <Space>
          {getAccountIcon(type)}
          <span style={{ textTransform: 'uppercase' }}>{type}</span>
        </Space>
      ),
      filters: [
        { text: '微信支付', value: 'wechat' },
        { text: '支付宝', value: 'alipay' },
        { text: 'PayPal', value: 'paypal' },
        { text: '银行账户', value: 'bank' }
      ],
      onFilter: (value, record) => record.account_type === value
    },
    {
      title: '账户名称',
      dataIndex: 'account_name',
      key: 'account_name',
      ellipsis: true
    },
    {
      title: '账户标识',
      dataIndex: 'account_id',
      key: 'account_id',
      ellipsis: true
    },
    {
      title: '凭证信息',
      dataIndex: 'credentials',
      key: 'credentials',
      width: 250,
      render: (credentials: Record<string, any>, record: PaymentAccount) => {
        const show = showCredentials[record.id];
        return (
          <div style={{ fontSize: 12 }}>
            {show ? (
              Object.entries(credentials).map(([key, value]) => (
                <div key={key}>
                  <strong>{key}:</strong> {String(value)}
                </div>
              ))
            ) : (
              <span>
                {Object.keys(credentials).length} 个字段
                <Tag color="blue" style={{ marginLeft: 8 }}>
                  已配置
                </Tag>
              </span>
            )}
            <Button
              type="link"
              size="small"
              icon={show ? <EyeInvisibleOutlined /> : <EyeOutlined />}
              onClick={() => setShowCredentials({ ...showCredentials, [record.id]: !show })}
            >
              {show ? '隐藏' : '显示'}
            </Button>
          </div>
        );
      }
    },
    {
      title: '货币',
      dataIndex: 'currency',
      key: 'currency',
      width: 80,
      render: (currency: string) => <Tag>{currency}</Tag>
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      sorter: (a, b) => a.priority - b.priority
    },
    {
      title: '状态',
      key: 'status',
      width: 120,
      render: (_, record: PaymentAccount) => (
        <Space direction="vertical" size={4}>
          {record.is_active ? (
            <Tag color="green">启用</Tag>
          ) : (
            <Tag color="red">禁用</Tag>
          )}
          {record.is_primary && <Tag color="blue">主账户</Tag>}
        </Space>
      )
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      fixed: 'right',
      render: (_, record: PaymentAccount) => (
        <Space>
          <Button
            type="text"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditAccount(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确认删除？"
            description="删除后无法恢复"
            onConfirm={() => handleDeleteAccount(record.id)}
            okText="确认"
            cancelText="取消"
          >
            <Button type="text" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  const settlementColumns: ColumnsType<CreatorSettlement> = [
    {
      title: '创作者',
      dataIndex: 'username',
      key: 'username',
      render: (text: string, record: CreatorSettlement) => (
        <div>
          <div>{text}</div>
          <div style={{ fontSize: 12, color: '#999' }}>{record.email}</div>
        </div>
      )
    },
    {
      title: '结算方式',
      dataIndex: 'settlement_method',
      key: 'settlement_method',
      width: 120,
      render: (method: string) => {
        const map: any = {
          'direct': { text: '直接分佣', color: 'blue' },
          'points': { text: '积分转换', color: 'green' }
        };
        const config = map[method] || { text: method, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '收款账户',
      key: 'payment_account',
      width: 200,
      render: (_, record: CreatorSettlement) => (
        <div>
          <div>{record.payment_account_type || '未设置'}</div>
          <div style={{ fontSize: 12, color: '#999' }}>{record.payment_account_id || ''}</div>
        </div>
      )
    },
    {
      title: '待结算笔数',
      dataIndex: 'pending_count',
      key: 'pending_count',
      width: 100,
      sorter: (a, b) => a.pending_count - b.pending_count
    },
    {
      title: '待结算金额',
      dataIndex: 'total_pending_amount',
      key: 'total_pending_amount',
      width: 120,
      render: (amount: number) => (
        <span style={{ color: '#faad14', fontWeight: 600 }}>
          ¥{amount.toFixed(2)}
        </span>
      ),
      sorter: (a, b) => a.total_pending_amount - b.total_pending_amount
    },
    {
      title: '最早收益日期',
      dataIndex: 'oldest_earning_date',
      key: 'oldest_earning_date',
      width: 120
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      fixed: 'right',
      render: (_, record: CreatorSettlement) => (
        <Space>
          <Button
            type="primary"
            size="small"
            onClick={() => handleSettleCreator(record.user_id, record.username)}
          >
            结算
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h2>收款与结算管理</h2>
        <p style={{ color: 'var(--text-light)' }}>
          管理平台收款账户配置和创作者收益结算
        </p>
      </div>

      <Card>
        <Tabs activeKey={activeTab} onChange={(key) => setActiveTab(key as any)}>
          <TabPane tab="收款账户" key="accounts">
            <div style={{ marginBottom: 16, textAlign: 'right' }}>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleAddAccount}
              >
                新增收款账户
              </Button>
            </div>
            <Table
              columns={accountColumns}
              dataSource={accounts}
              rowKey="id"
              loading={loading}
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 个账户`
              }}
              scroll={{ x: 1200 }}
            />
          </TabPane>

          <TabPane tab="待结算列表" key="settlements">
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="待结算创作者"
                    value={pendingSettlements.length}
                    prefix={<BankOutlined />}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="待结算总额"
                    value={pendingSettlements.reduce((sum, s) => sum + s.total_pending_amount, 0)}
                    precision={2}
                    prefix="¥"
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="待结算笔数"
                    value={pendingSettlements.reduce((sum, s) => sum + s.pending_count, 0)}
                  />
                </Card>
              </Col>
            </Row>

            <Table
              columns={settlementColumns}
              dataSource={pendingSettlements}
              rowKey="user_id"
              loading={loading}
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 位创作者`
              }}
              scroll={{ x: 1200 }}
            />
          </TabPane>
        </Tabs>
      </Card>

      {/* 账户编辑弹窗 */}
      <Modal
        title={editingAccount ? '编辑收款账户' : '新增收款账户'}
        open={accountModalVisible}
        onCancel={() => setAccountModalVisible(false)}
        onOk={() => {
          // TODO: 保存逻辑
          setAccountModalVisible(false);
          loadAccounts();
        }}
        width={600}
      >
        <Form layout="vertical">
          <Form.Item label="账户类型" required>
            <Select
              placeholder="选择账户类型"
              options={[
                { label: '微信支付', value: 'wechat' },
                { label: '支付宝', value: 'alipay' },
                { label: 'PayPal', value: 'paypal' },
                { label: '银行账户', value: 'bank' }
              ]}
              defaultValue={editingAccount?.account_type}
            />
          </Form.Item>

          <Form.Item label="账户名称" required>
            <Input
              placeholder="例如：微信支付-主账户"
              defaultValue={editingAccount?.account_name}
            />
          </Form.Item>

          <Form.Item label="账户标识" required>
            <Input
              placeholder="唯一标识符"
              defaultValue={editingAccount?.account_id}
            />
          </Form.Item>

          <Form.Item label="凭证信息" required>
            <TextArea
              rows={6}
              placeholder='JSON 格式，例如：{"mch_id": "123", "api_key": "xxx"}'
              defaultValue={editingAccount ? JSON.stringify(editingAccount.credentials, null, 2) : ''}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="货币">
                <Select
                  defaultValue={editingAccount?.currency || 'CNY'}
                  options={[
                    { label: 'CNY (人民币)', value: 'CNY' },
                    { label: 'USD (美元)', value: 'USD' },
                    { label: 'EUR (欧元)', value: 'EUR' }
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="优先级">
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  max={999}
                  defaultValue={editingAccount?.priority || 0}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="启用状态">
                <Switch
                  defaultChecked={editingAccount?.is_active ?? true}
                  checkedChildren="启用"
                  unCheckedChildren="禁用"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="设为主账户">
                <Switch
                  defaultChecked={editingAccount?.is_primary ?? false}
                  checkedChildren="是"
                  unCheckedChildren="否"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item label="描述">
            <TextArea
              rows={3}
              placeholder="账户描述"
              defaultValue={editingAccount?.description || ''}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PaymentAccountsManagement;
