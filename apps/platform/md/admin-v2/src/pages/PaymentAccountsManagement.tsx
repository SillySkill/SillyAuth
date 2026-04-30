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
      const msg = error instanceof Error ? error.message : 'Failed to load payment accounts';
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
          message.error('Credentials must be valid JSON');
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
        message.success('Payment account updated successfully');
      } else {
        await createPaymentAccount(payload);
        message.success('Payment account created successfully');
      }

      handleCloseModal();
      loadAccounts(pagination.current, pagination.pageSize);
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) {
        return; // Form validation error
      }
      const msg = error instanceof Error ? error.message : 'Operation failed';
      message.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = (record: PaymentAccount) => {
    Modal.confirm({
      title: 'Delete Payment Account',
      content: `Are you sure you want to delete "${record.account_name}"? This action cannot be undone.`,
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await deletePaymentAccount(record.id);
          message.success('Payment account deleted successfully');
          loadAccounts(pagination.current, pagination.pageSize);
        } catch (error: unknown) {
          const msg = error instanceof Error ? error.message : 'Delete failed';
          message.error(msg);
        }
      },
    });
  };

  const handleSwitchChange = async (record: PaymentAccount, checked: boolean) => {
    try {
      await updatePaymentAccount(record.id, { is_active: checked });
      message.success(`Account ${checked ? 'activated' : 'deactivated'}`);
      loadAccounts(pagination.current, pagination.pageSize);
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : 'Update failed';
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
      wechat: { color: 'green', icon: <WechatOutlined />, label: 'WeChat' },
      alipay: { color: 'blue', icon: <AlipayOutlined />, label: 'Alipay' },
      paypal: { color: 'geekblue', icon: <PayCircleOutlined />, label: 'PayPal' },
      bank: { color: 'purple', icon: <CreditCardOutlined />, label: 'Bank' },
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
      title: 'Account Type',
      dataIndex: 'account_type',
      key: 'account_type',
      width: 130,
      render: (type: string) => getAccountTypeTag(type),
      filters: [
        { text: 'WeChat', value: 'wechat' },
        { text: 'Alipay', value: 'alipay' },
        { text: 'PayPal', value: 'paypal' },
        { text: 'Bank', value: 'bank' },
      ],
      onFilter: (value, record) => record.account_type === value,
    },
    {
      title: 'Account Name',
      dataIndex: 'account_name',
      key: 'account_name',
      ellipsis: true,
    },
    {
      title: 'Account ID',
      dataIndex: 'account_id',
      key: 'account_id',
      ellipsis: true,
    },
    {
      title: 'Is Active',
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
      title: 'Is Primary',
      dataIndex: 'is_primary',
      key: 'is_primary',
      width: 110,
      render: (isPrimary: boolean) =>
        isPrimary ? <Tag color="gold">Primary</Tag> : <Tag>Secondary</Tag>,
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 90,
      sorter: true,
    },
    {
      title: 'Currency',
      dataIndex: 'currency',
      key: 'currency',
      width: 90,
      render: (currency: string) => <Tag>{currency}</Tag>,
    },
    {
      title: 'Actions',
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
            Edit
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
          >
            Delete
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
        <Title level={2}>Payment Accounts Management</Title>
        <p style={{ color: '#888' }}>
          Manage platform payment accounts for WeChat, Alipay, PayPal, and bank transfers.
        </p>
      </div>

      <Card
        extra={
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={() => loadAccounts(pagination.current, pagination.pageSize)}
            >
              Refresh
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreate}>
              Add Account
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
              showTotal: (total) => `Total ${total} accounts`,
            }}
            scroll={{ x: 1100 }}
            locale={{
              emptyText: <Empty description="No payment accounts found" />,
            }}
          />
        </Spin>
      </Card>

      {/* Create / Edit Modal */}
      <Modal
        title={editingAccount ? 'Edit Payment Account' : 'Add Payment Account'}
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
            label="Account Type"
            rules={[{ required: true, message: 'Please select an account type' }]}
          >
            <Select
              placeholder="Select account type"
              options={[
                { label: 'WeChat Pay', value: 'wechat' },
                { label: 'Alipay', value: 'alipay' },
                { label: 'PayPal', value: 'paypal' },
                { label: 'Bank Transfer', value: 'bank' },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="account_name"
            label="Account Name"
            rules={[{ required: true, message: 'Please enter account name' }]}
          >
            <Input placeholder="e.g. WeChat Main Account" />
          </Form.Item>

          <Form.Item
            name="account_id"
            label="Account ID"
            rules={[{ required: true, message: 'Please enter account ID' }]}
          >
            <Input placeholder="Unique account identifier" />
          </Form.Item>

          <Form.Item
            name="credentials"
            label="Credentials (JSON)"
            rules={[{ required: true, message: 'Please enter credentials' }]}
          >
            <TextArea
              rows={6}
              placeholder='{"mch_id": "123", "api_key": "xxx"}'
            />
          </Form.Item>

          <Form.Item
            name="currency"
            label="Currency"
            rules={[{ required: true, message: 'Please select a currency' }]}
          >
            <Select
              options={[
                { label: 'CNY (Chinese Yuan)', value: 'CNY' },
                { label: 'USD (US Dollar)', value: 'USD' },
                { label: 'EUR (Euro)', value: 'EUR' },
              ]}
            />
          </Form.Item>

          <Form.Item name="description" label="Description">
            <TextArea rows={3} placeholder="Optional description" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PaymentAccountsManagement;
