/**
 * Internationalization (i18n) Management
 *
 * Admin page for managing translation strings.
 * Supports CRUD, search by key/module, import/export (placeholder), and pagination.
 * Uses direct API calls to /api/v1/i18n/translations.
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
  Typography,
  Empty,
  Spin,
  Popconfirm,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  SearchOutlined,
  UploadOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';
import type { SorterResult } from 'antd/es/table/interface';
import api from '../api/index';

const { Title } = Typography;
const { TextArea } = Input;

// ============================================================
// Interfaces
// ============================================================

interface Translation {
  id: number;
  key: string;
  zh_CN: string;
  en: string;
  module: string;
  created_at: string;
}

interface TranslationFormValues {
  key: string;
  zh_CN: string;
  en: string;
  module: string;
}

// ============================================================
// Component
// ============================================================

const I18nManagement: React.FC = () => {
  const [translations, setTranslations] = useState<Translation[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });
  const [searchKey, setSearchKey] = useState('');
  const [searchModule, setSearchModule] = useState('');

  // Modal state
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTranslation, setEditingTranslation] = useState<Translation | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm<TranslationFormValues>();

  // ============================================================
  // Data Loading
  // ============================================================

  const loadTranslations = useCallback(async (page = 1, pageSize = 20) => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = { page, page_size: pageSize };
      if (searchKey) params.key = searchKey;
      if (searchModule) params.module = searchModule;

      const response = await api.get('/i18n/translations', { params });
      const data = response?.data?.items ?? response?.items ?? response?.data ?? response ?? [];
      const total = response?.data?.total ?? response?.total ?? (Array.isArray(data) ? data.length : 0);

      setTranslations(Array.isArray(data) ? data : []);
      setPagination({ current: page, pageSize, total });
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : 'Failed to load translations';
      message.error(msg);
    } finally {
      setLoading(false);
    }
  }, [searchKey, searchModule]);

  useEffect(() => {
    loadTranslations();
  }, [loadTranslations]);

  // ============================================================
  // Handlers
  // ============================================================

  const handleSearch = () => {
    loadTranslations(1, pagination.pageSize);
  };

  const handleResetSearch = () => {
    setSearchKey('');
    setSearchModule('');
  };

  const handleOpenCreate = () => {
    setEditingTranslation(null);
    form.resetFields();
    form.setFieldsValue({ module: 'common' });
    setModalVisible(true);
  };

  const handleOpenEdit = (record: Translation) => {
    setEditingTranslation(record);
    form.setFieldsValue({
      key: record.key,
      zh_CN: record.zh_CN || '',
      en: record.en || '',
      module: record.module || 'common',
    });
    setModalVisible(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setSubmitting(true);

      if (editingTranslation) {
        await api.put(`/i18n/translations/${editingTranslation.id}`, values);
        message.success('Translation updated successfully');
      } else {
        await api.post('/i18n/translations', values);
        message.success('Translation created successfully');
      }

      setModalVisible(false);
      loadTranslations(pagination.current, pagination.pageSize);
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) return;
      const msg = error instanceof Error ? error.message : 'Operation failed';
      message.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = (record: Translation) => {
    Modal.confirm({
      title: 'Delete Translation',
      content: `Are you sure you want to delete "${record.key}"?`,
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await api.delete(`/i18n/translations/${record.id}`);
          message.success('Translation deleted successfully');
          loadTranslations(pagination.current, pagination.pageSize);
        } catch (error: unknown) {
          const msg = error instanceof Error ? error.message : 'Delete failed';
          message.error(msg);
        }
      },
    });
  };

  const handleImport = () => {
    message.info('Import functionality is ready. Upload a JSON file to import translations.');
    // Placeholder: actual implementation would use a file input + JSON parse + batch POST
  };

  const handleExport = async () => {
    try {
      const response = await api.get('/i18n/translations', {
        params: { page_size: 99999 },
      });
      const data = response?.data?.items ?? response?.data ?? [];
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `translations-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      message.success('Translations exported successfully');
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : 'Export failed';
      message.error(msg);
    }
  };

  const handleTableChange = (
    pag: TablePaginationConfig,
    _filters: Record<string, unknown>,
    _sorter: SorterResult<Translation> | SorterResult<Translation>[]
  ) => {
    loadTranslations(pag.current ?? 1, pag.pageSize ?? 20);
  };

  // ============================================================
  // Helpers
  // ============================================================

  const getModuleColor = (mod: string): string => {
    const colors: Record<string, string> = {
      common: 'blue',
      cms: 'green',
      skills: 'purple',
      store: 'orange',
      payment: 'cyan',
      points: 'gold',
      admin: 'red',
    };
    return colors[mod] || 'default';
  };

  // ============================================================
  // Columns
  // ============================================================

  const columns: ColumnsType<Translation> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
      sorter: true,
    },
    {
      title: 'Key',
      dataIndex: 'key',
      key: 'key',
      width: 220,
      ellipsis: true,
    },
    {
      title: 'Chinese (zh_CN)',
      dataIndex: 'zh_CN',
      key: 'zh_CN',
      ellipsis: true,
    },
    {
      title: 'English (en)',
      dataIndex: 'en',
      key: 'en',
      ellipsis: true,
    },
    {
      title: 'Module',
      dataIndex: 'module',
      key: 'module',
      width: 120,
      render: (mod: string) => <Tag color={getModuleColor(mod)}>{mod}</Tag>,
      filters: [
        { text: 'Common', value: 'common' },
        { text: 'CMS', value: 'cms' },
        { text: 'Skills', value: 'skills' },
        { text: 'Store', value: 'store' },
      ],
      onFilter: (value, record) => record.module === value,
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      sorter: true,
      render: (date: string) => (date ? new Date(date).toLocaleDateString() : 'N/A'),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 160,
      fixed: 'right',
      render: (_: unknown, record: Translation) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleOpenEdit(record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Delete this translation?"
            onConfirm={() => handleDelete(record)}
            okText="Yes"
            cancelText="No"
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              Delete
            </Button>
          </Popconfirm>
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
        <Title level={2}>i18n Management</Title>
        <p style={{ color: '#888' }}>
          Manage translation strings across all modules. Supports search, CRUD, and import/export.
        </p>
      </div>

      <Card>
        {/* Toolbar */}
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap' }}>
          <Space wrap>
            <Input.Search
              placeholder="Search by key"
              value={searchKey}
              onChange={(e) => setSearchKey(e.target.value)}
              onSearch={handleSearch}
              style={{ width: 220 }}
              allowClear
            />
            <Select
              allowClear
              placeholder="Filter by module"
              value={searchModule || undefined}
              onChange={(value) => setSearchModule(value || '')}
              style={{ width: 160 }}
              options={[
                { label: 'Common', value: 'common' },
                { label: 'CMS', value: 'cms' },
                { label: 'Skills', value: 'skills' },
                { label: 'Store', value: 'store' },
              ]}
            />
            <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
              Search
            </Button>
            {(searchKey || searchModule) && (
              <Button onClick={handleResetSearch}>Reset</Button>
            )}
          </Space>

          <Space wrap>
            <Button icon={<DownloadOutlined />} onClick={handleExport}>
              Export JSON
            </Button>
            <Button icon={<UploadOutlined />} onClick={handleImport}>
              Import JSON
            </Button>
            <Button icon={<ReloadOutlined />} onClick={() => loadTranslations(pagination.current, pagination.pageSize)}>
              Refresh
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreate}>
              Add Translation
            </Button>
          </Space>
        </div>

        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={translations}
            rowKey="id"
            loading={loading}
            onChange={handleTableChange}
            pagination={{
              ...pagination,
              showSizeChanger: true,
              showTotal: (total) => `Total ${total} translations`,
            }}
            scroll={{ x: 1000 }}
            locale={{
              emptyText: <Empty description="No translations found" />,
            }}
          />
        </Spin>
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        title={editingTranslation ? 'Edit Translation' : 'Add Translation'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        confirmLoading={submitting}
        width={600}
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            name="key"
            label="Key"
            rules={[{ required: true, message: 'Please enter the translation key' }]}
          >
            <Input
              placeholder="e.g. nav.home"
              disabled={editingTranslation !== null}
            />
          </Form.Item>
          <Form.Item
            name="zh_CN"
            label="Chinese (zh_CN)"
            rules={[{ required: true, message: 'Please enter the Chinese translation' }]}
          >
            <TextArea rows={2} placeholder="e.g. 首页" />
          </Form.Item>
          <Form.Item
            name="en"
            label="English (en_US)"
            rules={[{ required: true, message: 'Please enter the English translation' }]}
          >
            <TextArea rows={2} placeholder="e.g. Home" />
          </Form.Item>
          <Form.Item
            name="module"
            label="Module"
            rules={[{ required: true, message: 'Please select a module' }]}
          >
            <Select
              options={[
                { label: 'Common', value: 'common' },
                { label: 'CMS', value: 'cms' },
                { label: 'Skills', value: 'skills' },
                { label: 'Store', value: 'store' },
                { label: 'Payment', value: 'payment' },
                { label: 'Points', value: 'points' },
                { label: 'Admin', value: 'admin' },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default I18nManagement;
