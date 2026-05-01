/**
 * Payment Accounts Management
 *
 * Admin page for managing payment accounts (WeChat, Alipay, PayPal, Bank).
 * Full CRUD with table, modal forms, and delete confirmation.
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
  Switch,
  InputNumber,
  message,
  Card,
  Typography,
  Empty,
  Spin,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  WechatOutlined,
  AlipayOutlined,
  PayCircleOutlined,
  CreditCardOutlined,
} from '@ant-design/icons';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';
import type { SorterResult } from 'antd/es/table/interface';
import {
  getPaymentAccounts,
  createPaymentAccount,
  updatePaymentAccount,
  deletePaymentAccount,
} from '../api/payment';

const { TextArea } = Input;
const { Title } = Typography;

// ============================================================
// Interfaces
// ============================================================

interface PaymentAccount {
  id: number;
  account_type: 'wechat' | 'alipay' | 'paypal' | 'bank';
  account_name: string;
  account_id: string;
  credentials: Record<string, unknown>;
  is_active: boolean;
  is_primary: boolean;
  priority: number;
  currency: string;
  description: string;
  created_at: string;
  updated_at: string;
}

interface PaymentAccountFormValues {
  account_type: string;
  account_name: string;
  account_id: string;
  credentials: string;
  currency: string;
  description: string;
}

// ============================================================
// Component
// ============================================================

const PaymentAccountsManagement: React.FC = () => {
  const [accounts, setAccounts] = useState<PaymentAccount[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingAccount, setEditingAccount] = useState<PaymentAccount | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });

  const [form] = Form.useForm<PaymentAccountFormValues>();

  // ============================================================
  // Data Loading
  // ============================================================

  const loadAccounts = useCallback(async (page = 1, pageSize = 20) => {
    setLoading(true);
    try {
      const response = await getPaymentAccounts();
      const data = response?.data ?? [];
      setAccounts(Array.isArray(data) ? data : []);
      setPagination({ current: page, pageSize, total: data.length });
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : '加载支付账户失败';
      message.error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAccounts();
  }, [loadAccounts]);

  // ============================================================
  // Handlers
  // ============================================================

  const handleOpenCreate = () => {
    setEditingAccount(null);
    form.resetFields();
    form.setFieldsValue({
      currency: 'CNY',
      account_type: 'wechat',
    });
    setModalVisible(true);
  };

  const handleOpenEdit = (record: PaymentAccount) => {
    setEditingAccount(record);
    form.setFieldsValue({
      account_type: record.account_type,
      account_name: record.account_name,
      account_id: record.account_id,
      credentials: JSON.stringify(record.credentials, null, 2),
      currency: record.currency,
      description: record.description || '',
    });
    setModalVisible(true);
  };

  const handleCloseModal = () => {
    setModalVisible(false);
    setEditingAccount(null);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setSubmitting(true);

      let parsedCredentials: Record<string, unknown> = {};
      if (values.credentials) {
        try {
          parsedCredentials = JSON.parse(values.credentials);
        } catch {
          message.error('凭证必须是有效的JSON格式');
          setSubmitting(false);
          return;
        }
      }

      const payload = {
        account_type: values.account_type,
        account_name: values.account_name,
        account_id: values.account_id,
        credentials: parsedCredentials,
        currency: values.currency,
        description: values.description,
      };

      if (editingAccount) {
        await updatePaymentAccount(editingAccount.id, payload);
        message.success('支付账户更新成功');
      } else {
        await createPaymentAccount(payload);
        message.success('支付账户创建成功');
      }

      handleCloseModal();
      loadAccounts(pagination.current, pagination.pageSize);
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) {
        return; // Form validation error
      }
      const msg = error instanceof Error ? error.message : '操作失败';
      message.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = (record: PaymentAccount) => {
    Modal.confirm({
      title: '删除支付账户',
      content: `确定要删除 "${record.account_name}" 吗？此操作不可撤销。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deletePaymentAccount(record.id);
          message.success('支付账户删除成功');
          loadAccounts(pagination.current, pagination.pageSize);
        } catch (error: unknown) {
          const msg = error instanceof Error ? error.message : '删除失败';
          message.error(msg);
        }
      },
    });
  };

  const handleSwitchChange = async (record: PaymentAccount, checked: boolean) => {
    try {
      await updatePaymentAccount(record.id, { is_active: checked });
      message.success(`账户${checked ? '已启用' : '已停用'}`);
      loadAccounts(pagination.current, pagination.pageSize);
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : '更新失败';
      message.error(msg);
    }
  };

  const handleTableChange = (
    pag: TablePaginationConfig,
    _filters: Record<string, unknown>,
    _sorter: SorterResult<PaymentAccount> | SorterResult<PaymentAccount>[]
  ) => {
    loadAccounts(pag.current ?? 1, pag.pageSize ?? 20);
  };

  // ============================================================
  // Helper renderers
  // ============================================================

  const getAccountTypeTag = (type: string) => {
    const config: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
      wechat: { color: 'green', icon: <WechatOutlined />, label: '微信' },
      alipay: { color: 'blue', icon: <AlipayOutlined />, label: '支付宝' },
      paypal: { color: 'geekblue', icon: <PayCircleOutlined />, label: 'PayPal' },
      bank: { color: 'purple', icon: <CreditCardOutlined />, label: '银行' },
    };
    const info = config[type] || { color: 'default', icon: null, label: type };
    return (
      <Tag color={info.color} icon={info.icon}>
        {info.label}
      </Tag>
    );
  };

  // ============================================================
  // Columns
  // ============================================================

  const columns: ColumnsType<PaymentAccount> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
      sorter: true,
    },
    {
      title: '账户类型',
      dataIndex: 'account_type',
      key: 'account_type',
      width: 130,
      render: (type: string) => getAccountTypeTag(type),
      filters: [
        { text: '微信', value: 'wechat' },
        { text: '支付宝', value: 'alipay' },
        { text: 'PayPal', value: 'paypal' },
        { text: '银行', value: 'bank' },
      ],
      onFilter: (value, record) => record.account_type === value,
    },
    {
      title: '账户名称',
      dataIndex: 'account_name',
      key: 'account_name',
      ellipsis: true,
    },
    {
      title: '账户ID',
      dataIndex: 'account_id',
      key: 'account_id',
      ellipsis: true,
    },
    {
      title: '是否激活',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean, record: PaymentAccount) => (
        <Switch
          checked={isActive}
          size="small"
          onChange={(checked) => handleSwitchChange(record, checked)}
        />
      ),
    },
    {
      title: '是否主要',
      dataIndex: 'is_primary',
      key: 'is_primary',
      width: 110,
      render: (isPrimary: boolean) =>
        isPrimary ? <Tag color="gold">主要</Tag> : <Tag>次要</Tag>,
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 90,
      sorter: true,
    },
    {
      title: '货币',
      dataIndex: 'currency',
      key: 'currency',
      width: 90,
      render: (currency: string) => <Tag>{currency}</Tag>,
    },
    {
      title: '操作',
      key: 'actions',
      width: 160,
      fixed: 'right',
      render: (_: unknown, record: PaymentAccount) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleOpenEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  // ============================================================
  // Render
  // ============================================================

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>支付账户管理</Title>
        <p style={{ color: '#888' }}>
          管理平台的微信、支付宝、PayPal 和银行转账支付账户。
        </p>
      </div>

      <Card
        extra={
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={() => loadAccounts(pagination.current, pagination.pageSize)}
            >
              刷新
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreate}>
              添加账户
            </Button>
          </Space>
        }
      >
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={accounts}
            rowKey="id"
            loading={loading}
            onChange={handleTableChange}
            pagination={{
              ...pagination,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个账户`,
            }}
            scroll={{ x: 1100 }}
            locale={{
              emptyText: <Empty description="暂无支付账户" />,
            }}
          />
        </Spin>
      </Card>

      {/* Create / Edit Modal */}
      <Modal
        title={editingAccount ? '编辑支付账户' : '添加支付账户'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={handleCloseModal}
        confirmLoading={submitting}
        width={640}
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            name="account_type"
            label="账户类型"
            rules={[{ required: true, message: '请选择账户类型' }]}
          >
            <Select
              placeholder="请选择账户类型"
              options={[
                { label: '微信支付', value: 'wechat' },
                { label: '支付宝', value: 'alipay' },
                { label: 'PayPal', value: 'paypal' },
                { label: '银行转账', value: 'bank' },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="account_name"
            label="账户名称"
            rules={[{ required: true, message: '请输入账户名称' }]}
          >
            <Input placeholder="例如：微信主账户" />
          </Form.Item>

          <Form.Item
            name="account_id"
            label="账户ID"
            rules={[{ required: true, message: '请输入账户ID' }]}
          >
            <Input placeholder="唯一账户标识符" />
          </Form.Item>

          <Form.Item
            name="credentials"
            label="凭证 (JSON)"
            rules={[{ required: true, message: '请输入凭证' }]}
          >
            <TextArea
              rows={6}
              placeholder='{"mch_id": "123", "api_key": "xxx"}'
            />
          </Form.Item>

          <Form.Item
            name="currency"
            label="货币"
            rules={[{ required: true, message: '请选择货币' }]}
          >
            <Select
              options={[
                { label: 'CNY（人民币）', value: 'CNY' },
                { label: 'USD（美元）', value: 'USD' },
                { label: 'EUR（欧元）', value: 'EUR' },
              ]}
            />
          </Form.Item>

          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="可选描述" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PaymentAccountsManagement;
