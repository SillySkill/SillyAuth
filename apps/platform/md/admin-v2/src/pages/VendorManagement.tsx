import React, { useEffect, useState, useCallback } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Switch,
  Modal,
  Form,
  Input,
  Select,
  message,
  Card,
  Typography,
  Popconfirm,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  LinkOutlined,
  MailOutlined,
  PhoneOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getVendors, createVendor, updateVendor, deleteVendor } from '../api/vendors';
import type { Vendor } from '../types';
import { formatDate } from '../utils';

const { Option } = Select;
const { TextArea } = Input;
const { Title } = Typography;

interface VendorFormValues {
  name: string;
  description: string;
  logo?: string;
  website?: string;
  category?: string;
  contact_email?: string;
  contact_phone?: string;
  is_active?: boolean;
  is_verified?: boolean;
  sort_order?: number;
}

const VendorManagement: React.FC = () => {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingVendor, setEditingVendor] = useState<Vendor | null>(null);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [filters, setFilters] = useState<{ search?: string; is_verified?: boolean; is_active?: boolean }>({});
  const [form] = Form.useForm<VendorFormValues>();
  const [submitting, setSubmitting] = useState(false);

  const fetchVendors = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {
        page: pagination.current,
        page_size: pagination.pageSize,
      };
      if (filters.search) params.search = filters.search;

      const response = await getVendors(params as Parameters<typeof getVendors>[0]);
      if (response.success) {
        setVendors(response.data.items);
        setPagination((prev) => ({ ...prev, total: response.data.total }));
      }
    } catch (error) {
      message.error('加载供应商失败');
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, filters]);

  useEffect(() => {
    fetchVendors();
  }, [fetchVendors]);

  const handleSearch = (values: { search?: string }) => {
    setFilters((prev) => ({ ...prev, ...values }));
    setPagination((prev) => ({ ...prev, current: 1 }));
  };

  const handleAdd = () => {
    setEditingVendor(null);
    form.resetFields();
    form.setFieldsValue({ is_active: true, is_verified: false, sort_order: 0 });
    setModalVisible(true);
  };

  const handleEdit = (record: Vendor) => {
    setEditingVendor(record);
    form.setFieldsValue({
      name: record.name,
      description: record.description,
      logo: record.logo,
      website: record.website,
      category: record.category,
      contact_email: record.contact_email,
      contact_phone: record.contact_phone,
      is_active: record.is_active,
      is_verified: record.is_verified,
      sort_order: record.sort_order,
    });
    setModalVisible(true);
  };

  const handleToggleActive = async (id: number, checked: boolean) => {
    try {
      await updateVendor(id, { is_active: checked });
      message.success(`供应商${checked ? '已启用' : '已禁用'}`);
      fetchVendors();
    } catch (error) {
      message.error('更新供应商失败');
    }
  };

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除此供应商吗？所有相关数据将受影响。',
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteVendor(id);
          message.success('供应商删除成功');
          fetchVendors();
        } catch (error) {
          message.error('删除供应商失败');
        }
      },
    });
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const values = await form.validateFields();
      if (editingVendor) {
        await updateVendor(editingVendor.id, values);
        message.success('供应商更新成功');
      } else {
        await createVendor(values);
        message.success('供应商创建成功');
      }
      setModalVisible(false);
      fetchVendors();
    } catch (error: unknown) {
      if (error && typeof error === 'object' && 'errorFields' in error) return;
      message.error('操作失败');
    } finally {
      setSubmitting(false);
    }
  };

  const handleTableChange = (page: number, pageSize: number) => {
    setPagination({ current: page, pageSize, total: pagination.total });
  };

  const columns: ColumnsType<Vendor> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (name: string, record) => (
        <Space>
          {record.logo && (
            <img src={record.logo} alt={name} style={{ width: 28, height: 28, borderRadius: 4, objectFit: 'cover' }} />
          )}
          <span style={{ fontWeight: 500 }}>{name}</span>
        </Space>
      ),
    },
    {
      title: '联系方式',
      key: 'contact',
      width: 200,
      render: (_: unknown, record: Vendor) => (
        <Space direction="vertical" size={2}>
          {record.contact_email && (
            <span style={{ fontSize: 13 }}>
              <MailOutlined style={{ marginRight: 4 }} />
              {record.contact_email}
            </span>
          )}
          {record.contact_phone && (
            <span style={{ fontSize: 13, color: '#666' }}>
              <PhoneOutlined style={{ marginRight: 4 }} />
              {record.contact_phone}
            </span>
          )}
        </Space>
      ),
    },
    {
      title: '网站',
      dataIndex: 'website',
      key: 'website',
      width: 150,
      render: (website: string) =>
        website ? (
          <a href={website} target="_blank" rel="noopener noreferrer">
            <LinkOutlined style={{ marginRight: 4 }} />
            {website.replace(/^https?:\/\//, '')}
          </a>
        ) : (
          <span style={{ color: '#ccc' }}>-</span>
        ),
    },
    {
      title: '状态',
      key: 'status',
      width: 140,
      render: (_: unknown, record: Vendor) => (
        <Space size={8}>
          {record.is_verified ? (
            <Tag color="green">已验证</Tag>
          ) : (
            <Tag color="orange">待审核</Tag>
          )}
          <Switch
            checked={record.is_active}
            size="small"
            onChange={(checked) => handleToggleActive(record.id, checked)}
          />
        </Space>
      ),
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 140,
      render: (category: string) =>
        category ? <Tag color="cyan">{category}</Tag> : <span style={{ color: '#ccc' }}>-</span>,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => formatDate(date),
    },
    {
      title: '操作',
      key: 'actions',
      width: 180,
      fixed: 'right',
      render: (_: unknown, record: Vendor) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此供应商？"
            onConfirm={() => handleDelete(record.id)}
            okText="删除"
            cancelText="取消"
            okType="danger"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        供应商管理
      </Title>

      <Card style={{ marginBottom: 16 }}>
        <Form layout="inline" onFinish={handleSearch}>
          <Form.Item name="search">
            <Input placeholder="按名称搜索..." prefix={<SearchOutlined />} style={{ width: 260 }} allowClear />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
                搜索
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => {
                  setFilters({});
                  setPagination({ current: 1, pageSize: 10, total: 0 });
                }}
              >
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Card
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            创建供应商
          </Button>
        }
      >
        <Table<Vendor>
          columns={columns}
          dataSource={vendors}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1350 }}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 家供应商`,
            onChange: (page, pageSize) => handleTableChange(page, pageSize),
          }}
          locale={{ emptyText: '暂无供应商' }}
        />
      </Card>

      <Modal
        title={editingVendor ? '编辑供应商' : '创建供应商'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={700}
        confirmLoading={submitting}
        okText={editingVendor ? '更新' : '创建'}
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            label="名称"
            name="name"
            rules={[{ required: true, message: '请输入供应商名称' }]}
          >
            <Input placeholder="供应商公司名称" />
          </Form.Item>

          <Form.Item
            label="描述"
            name="description"
            rules={[{ required: true, message: '请输入描述' }]}
          >
            <TextArea rows={3} placeholder="简要描述" showCount maxLength={500} />
          </Form.Item>

          <Form.Item label="联系邮箱" name="contact_email" rules={[{ type: 'email', message: '邮箱格式无效' }]}>
            <Input placeholder="contact@company.com" />
          </Form.Item>

          <Form.Item label="联系电话" name="contact_phone">
            <Input placeholder="+86 138-0000-0000" />
          </Form.Item>

          <Form.Item label="网站" name="website" rules={[{ type: 'url', message: 'URL格式无效', warningOnly: true }]}>
            <Input placeholder="https://www.example.com" />
          </Form.Item>

          <Form.Item label="分类" name="category">
            <Select placeholder="请选择分类" allowClear>
              <Option value="Development Tools">开发工具</Option>
              <Option value="Cloud Services">云服务</Option>
              <Option value="AI Services">AI服务</Option>
              <Option value="Design Tools">设计工具</Option>
              <Option value="Education">教育</Option>
              <Option value="Other">其他</Option>
            </Select>
          </Form.Item>

          <Form.Item label="Logo地址" name="logo" rules={[{ type: 'url', message: 'URL格式无效', warningOnly: true }]}>
            <Input placeholder="https://example.com/logo.png" />
          </Form.Item>

          <Form.Item label="排序" name="sort_order">
            <Input type="number" placeholder="0" />
          </Form.Item>

          <Space size="large">
            <Form.Item label="已验证" name="is_verified" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item label="启用" name="is_active" valuePropName="checked">
              <Switch />
            </Form.Item>
          </Space>
        </Form>
      </Modal>
    </div>
  );
};

export default VendorManagement;
