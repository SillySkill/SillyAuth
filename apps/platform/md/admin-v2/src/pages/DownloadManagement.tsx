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
  InputNumber,
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
  CloudDownloadOutlined,
  WindowsOutlined,
  AppleOutlined,
  LinuxOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getDownloads, createDownload, updateDownload, deleteDownload } from '../api/downloads';
import type { Download } from '../types';
import { formatDate, formatFileSize } from '../utils';

const { Option } = Select;
const { TextArea } = Input;
const { Title } = Typography;

interface DownloadFormValues {
  title: string;
  description: string;
  file_url: string;
  file_size?: number;
  file_type?: string;
  version?: string;
  category?: string;
  platform?: string;
  is_active?: boolean;
}

const DownloadManagement: React.FC = () => {
  const [downloads, setDownloads] = useState<Download[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingDownload, setEditingDownload] = useState<Download | null>(null);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [filters, setFilters] = useState<{ search?: string; platform?: string; is_active?: boolean }>({});
  const [form] = Form.useForm<DownloadFormValues>();
  const [submitting, setSubmitting] = useState(false);

  const platformOptions = [
    { label: 'Windows', value: 'windows', icon: <WindowsOutlined /> },
    { label: 'macOS', value: 'macos', icon: <AppleOutlined /> },
    { label: 'Linux', value: 'linux', icon: <LinuxOutlined /> },
    { label: 'Cross-platform', value: 'all', icon: null },
  ];

  const categoryOptions = [
    'IDE & Editors',
    'Dev Tools',
    'Runtime',
    'Database',
    'Container',
    'Version Control',
    'Utility',
    'Other',
  ];

  const fetchDownloads = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {
        page: pagination.current,
        page_size: pagination.pageSize,
      };
      if (filters.search) params.search = filters.search;
      if (filters.platform) params.platform = filters.platform;

      const response = await getDownloads(params as Parameters<typeof getDownloads>[0]);
      if (response.success) {
        setDownloads(response.data.items);
        setPagination((prev) => ({ ...prev, total: response.data.total }));
      }
    } catch (error) {
      message.error('Failed to load downloads');
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, filters]);

  useEffect(() => {
    fetchDownloads();
  }, [fetchDownloads]);

  const handleSearch = (values: { search?: string; platform?: string }) => {
    setFilters((prev) => ({ ...prev, ...values }));
    setPagination((prev) => ({ ...prev, current: 1 }));
  };

  const handleAdd = () => {
    setEditingDownload(null);
    form.resetFields();
    form.setFieldsValue({ is_active: true, file_size: 0 });
    setModalVisible(true);
  };

  const handleEdit = (record: Download) => {
    setEditingDownload(record);
    form.setFieldsValue({
      title: record.title,
      description: record.description,
      file_url: record.file_url,
      file_size: record.file_size,
      file_type: record.file_type,
      version: record.version,
      category: record.category,
      platform: record.platform,
      is_active: record.is_active,
    });
    setModalVisible(true);
  };

  const handleToggleActive = async (id: number, checked: boolean) => {
    try {
      await updateDownload(id, { is_active: checked });
      message.success(`Download ${checked ? 'activated' : 'deactivated'}`);
      fetchDownloads();
    } catch (error) {
      message.error('Failed to update download');
    }
  };

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: 'Confirm Delete',
      content: 'Are you sure you want to delete this download?',
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await deleteDownload(id);
          message.success('Download deleted successfully');
          fetchDownloads();
        } catch (error) {
          message.error('Failed to delete download');
        }
      },
    });
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const values = await form.validateFields();
      if (editingDownload) {
        await updateDownload(editingDownload.id, values);
        message.success('Download updated successfully');
      } else {
        await createDownload(values);
        message.success('Download created successfully');
      }
      setModalVisible(false);
      fetchDownloads();
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

  const getPlatformIcon = (platform: string) => {
    const opt = platformOptions.find((p) => p.value === platform);
    return opt?.icon || null;
  };

  const getPlatformColor = (platform: string): string => {
    const map: Record<string, string> = {
      windows: 'blue',
      macos: 'default',
      linux: 'orange',
      all: 'purple',
    };
    return map[platform] || 'default';
  };

  const columns: ColumnsType<Download> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      width: 220,
      ellipsis: true,
      render: (title: string) => <span style={{ fontWeight: 500 }}>{title}</span>,
    },
    {
      title: 'Version',
      dataIndex: 'version',
      key: 'version',
      width: 100,
      render: (version: string) =>
        version ? <Tag color="blue">{version}</Tag> : <Tag color="default">-</Tag>,
    },
    {
      title: 'Platform',
      dataIndex: 'platform',
      key: 'platform',
      width: 130,
      render: (platform: string) => {
        const icon = getPlatformIcon(platform);
        const label = platformOptions.find((p) => p.value === platform)?.label || platform;
        return (
          <Tag color={getPlatformColor(platform)} icon={icon}>
            {label}
          </Tag>
        );
      },
    },
    {
      title: 'File Size',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      render: (size: number) => formatFileSize(size),
    },
    {
      title: 'Downloads',
      dataIndex: 'download_count',
      key: 'download_count',
      width: 100,
      render: (count: number) => (
        <span>
          <CloudDownloadOutlined style={{ marginRight: 4 }} />
          {count.toLocaleString()}
        </span>
      ),
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category: string) =>
        category ? <Tag color="cyan">{category}</Tag> : <span style={{ color: '#ccc' }}>-</span>,
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (isActive: boolean, record: Download) => (
        <Switch
          checked={isActive}
          size="small"
          onChange={(checked) => handleToggleActive(record.id, checked)}
        />
      ),
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      render: (date: string) => formatDate(date),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 180,
      fixed: 'right',
      render: (_: unknown, record: Download) => (
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
            title="Delete this download?"
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
        Download Management
      </Title>

      {/* Search/Filter */}
      <Card style={{ marginBottom: 16 }}>
        <Form layout="inline" onFinish={handleSearch}>
          <Form.Item name="search">
            <Input placeholder="Search by title..." prefix={<SearchOutlined />} style={{ width: 220 }} allowClear />
          </Form.Item>
          <Form.Item name="platform">
            <Select placeholder="Platform" style={{ width: 150 }} allowClear>
              {platformOptions.map((opt) => (
                <Option key={opt.value} value={opt.value}>
                  {opt.icon} {opt.label}
                </Option>
              ))}
            </Select>
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

      {/* Table */}
      <Card
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            Create Download
          </Button>
        }
      >
        <Table<Download>
          columns={columns}
          dataSource={downloads}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1300 }}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} downloads`,
            onChange: (page, pageSize) => handleTableChange(page, pageSize),
          }}
          locale={{ emptyText: 'No downloads found' }}
        />
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        title={editingDownload ? 'Edit Download' : 'Create Download'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={700}
        confirmLoading={submitting}
        okText={editingDownload ? 'Update' : 'Create'}
        cancelText="Cancel"
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            label="Title (zh_CN)"
            name="title"
            rules={[{ required: true, message: 'Please enter the title' }]}
          >
            <Input placeholder="Download title" />
          </Form.Item>

          <Form.Item
            label="Description"
            name="description"
            rules={[{ required: true, message: 'Please enter a description' }]}
          >
            <TextArea rows={3} placeholder="Brief description" showCount maxLength={500} />
          </Form.Item>

          <Form.Item
            label="File URL"
            name="file_url"
            rules={[
              { required: true, message: 'Please enter the file URL' },
              { type: 'url', message: 'Invalid URL' },
            ]}
          >
            <Input placeholder="https://example.com/downloads/file.zip" />
          </Form.Item>

          <Form.Item label="Version" name="version">
            <Input placeholder="e.g. 3.12.1" />
          </Form.Item>

          <Form.Item label="Platform" name="platform">
            <Select placeholder="Select platform" allowClear>
              {platformOptions.map((opt) => (
                <Option key={opt.value} value={opt.value}>
                  {opt.icon} {opt.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item label="File Size (bytes)" name="file_size">
            <InputNumber min={0} style={{ width: '100%' }} placeholder="0" />
          </Form.Item>

          <Form.Item label="File Type" name="file_type">
            <Select placeholder="Select file type" allowClear>
              <Option value="exe">exe</Option>
              <Option value="msi">msi</Option>
              <Option value="dmg">dmg</Option>
              <Option value="zip">zip</Option>
              <Option value="tar.gz">tar.gz</Option>
              <Option value="deb">deb</Option>
              <Option value="rpm">rpm</Option>
              <Option value="other">Other</Option>
            </Select>
          </Form.Item>

          <Form.Item label="Category" name="category">
            <Select placeholder="Select category" allowClear>
              {categoryOptions.map((cat) => (
                <Option key={cat} value={cat}>{cat}</Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item label="Active" name="is_active" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default DownloadManagement;
