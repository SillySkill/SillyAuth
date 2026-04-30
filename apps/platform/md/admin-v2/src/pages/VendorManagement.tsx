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
      message.error('Failed to load vendors');
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
      message.success(`Vendor ${checked ? 'activated' : 'deactivated'}`);
      fetchVendors();
    } catch (error) {
      message.error('Failed to update vendor');
    }
  };

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: 'Confirm Delete',
      content: 'Are you sure you want to delete this vendor? All related data will be affected.',
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await deleteVendor(id);
          message.success('Vendor deleted successfully');
          fetchVendors();
        } catch (error) {
          message.error('Failed to delete vendor');
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
        message.success('Vendor updated successfully');
      } else {
        await createVendor(values);
        message.success('Vendor created successfully');
      }
      setModalVisible(false);
      fetchVendors();
    } catch (error: unknown) {
      if (error && typeof error === 'object' && 'errorFields' in error) return;
      message.error('Operation failed');
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
      title: 'Name',
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
      title: 'Contact',
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
      title: 'Website',
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
      title: 'Status',
      key: 'status',
      width: 140,
      render: (_: unknown, record: Vendor) => (
        <Space size={8}>
          {record.is_verified ? (
            <Tag color="green">Verified</Tag>
          ) : (
            <Tag color="orange">Pending</Tag>
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
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 140,
      render: (category: string) =>
        category ? <Tag color="cyan">{category}</Tag> : <span style={{ color: '#ccc' }}>-</span>,
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => formatDate(date),
    },
    {
      title: 'Actions',
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
            Edit
          </Button>
          <Popconfirm
            title="Delete this vendor?"
            onConfirm={() => handleDelete(record.id)}
            okText="Delete"
            cancelText="Cancel"
            okType="danger"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        Vendor Management
      </Title>

      <Card style={{ marginBottom: 16 }}>
        <Form layout="inline" onFinish={handleSearch}>
          <Form.Item name="search">
            <Input placeholder="Search by name..." prefix={<SearchOutlined />} style={{ width: 260 }} allowClear />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
                Search
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => {
                  setFilters({});
                  setPagination({ current: 1, pageSize: 10, total: 0 });
                }}
              >
                Reset
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Card
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            Create Vendor
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
            showTotal: (total) => `Total ${total} vendors`,
            onChange: (page, pageSize) => handleTableChange(page, pageSize),
          }}
          locale={{ emptyText: 'No vendors found' }}
        />
      </Card>

      <Modal
        title={editingVendor ? 'Edit Vendor' : 'Create Vendor'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={700}
        confirmLoading={submitting}
        okText={editingVendor ? 'Update' : 'Create'}
        cancelText="Cancel"
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            label="Name"
            name="name"
            rules={[{ required: true, message: 'Please enter the vendor name' }]}
          >
            <Input placeholder="Vendor company name" />
          </Form.Item>

          <Form.Item
            label="Description"
            name="description"
            rules={[{ required: true, message: 'Please enter a description' }]}
          >
            <TextArea rows={3} placeholder="Brief description" showCount maxLength={500} />
          </Form.Item>

          <Form.Item label="Contact Email" name="contact_email" rules={[{ type: 'email', message: 'Invalid email' }]}>
            <Input placeholder="contact@company.com" />
          </Form.Item>

          <Form.Item label="Contact Phone" name="contact_phone">
            <Input placeholder="+86 138-0000-0000" />
          </Form.Item>

          <Form.Item label="Website" name="website" rules={[{ type: 'url', message: 'Invalid URL', warningOnly: true }]}>
            <Input placeholder="https://www.example.com" />
          </Form.Item>

          <Form.Item label="Category" name="category">
            <Select placeholder="Select a category" allowClear>
              <Option value="Development Tools">Development Tools</Option>
              <Option value="Cloud Services">Cloud Services</Option>
              <Option value="AI Services">AI Services</Option>
              <Option value="Design Tools">Design Tools</Option>
              <Option value="Education">Education</Option>
              <Option value="Other">Other</Option>
            </Select>
          </Form.Item>

          <Form.Item label="Logo URL" name="logo" rules={[{ type: 'url', message: 'Invalid URL', warningOnly: true }]}>
            <Input placeholder="https://example.com/logo.png" />
          </Form.Item>

          <Form.Item label="Sort Order" name="sort_order">
            <Input type="number" placeholder="0" />
          </Form.Item>

          <Space size="large">
            <Form.Item label="Verified" name="is_verified" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item label="Active" name="is_active" valuePropName="checked">
              <Switch />
            </Form.Item>
          </Space>
        </Form>
      </Modal>
    </div>
  );
};

export default VendorManagement;
