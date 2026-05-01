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
      const msg = error instanceof Error ? error.message : '加载翻译失败';
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
        message.success('翻译更新成功');
      } else {
        await api.post('/i18n/translations', values);
        message.success('翻译创建成功');
      }

      setModalVisible(false);
      loadTranslations(pagination.current, pagination.pageSize);
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) return;
      const msg = error instanceof Error ? error.message : '操作失败';
      message.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = (record: Translation) => {
    Modal.confirm({
      title: '删除翻译',
      content: `确定要删除 "${record.key}" 吗？`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await api.delete(`/i18n/translations/${record.id}`);
          message.success('翻译删除成功');
          loadTranslations(pagination.current, pagination.pageSize);
        } catch (error: unknown) {
          const msg = error instanceof Error ? error.message : '删除失败';
          message.error(msg);
        }
      },
    });
  };

  const handleImport = () => {
    message.info('导入功能已就绪，上传JSON文件导入翻译。');
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
      message.success('翻译导出成功');
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : '导出失败';
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
      title: '键名',
      dataIndex: 'key',
      key: 'key',
      width: 220,
      ellipsis: true,
    },
    {
      title: '中文',
      dataIndex: 'zh_CN',
      key: 'zh_CN',
      ellipsis: true,
    },
    {
      title: '英文',
      dataIndex: 'en',
      key: 'en',
      ellipsis: true,
    },
    {
      title: '模块',
      dataIndex: 'module',
      key: 'module',
      width: 120,
      render: (mod: string) => <Tag color={getModuleColor(mod)}>{mod}</Tag>,
      filters: [
        { text: '通用', value: 'common' },
        { text: 'CMS', value: 'cms' },
        { text: '技能', value: 'skills' },
        { text: '商城', value: 'store' },
        { text: '支付', value: 'payment' },
        { text: '积分', value: 'points' },
        { text: '管理', value: 'admin' },
      ],
      onFilter: (value, record) => record.module === value,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      sorter: true,
      render: (date: string) => (date ? new Date(date).toLocaleDateString() : '无'),
    },
    {
      title: '操作',
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
            编辑
          </Button>
          <Popconfirm
            title="确定删除此翻译？"
            onConfirm={() => handleDelete(record)}
            okText="是"
            cancelText="否"
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              删除
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
        <Title level={2}>国际化管理</Title>
        <p style={{ color: '#888' }}>
          管理所有模块的翻译字符串。支持搜索、增删改查、导入和导出。
        </p>
      </div>

      <Card>
        {/* Toolbar */}
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap' }}>
          <Space wrap>
            <Input.Search
              placeholder="搜索键名"
              value={searchKey}
              onChange={(e) => setSearchKey(e.target.value)}
              onSearch={handleSearch}
              style={{ width: 220 }}
              allowClear
            />
            <Select
              allowClear
              placeholder="按模块筛选"
              value={searchModule || undefined}
              onChange={(value) => setSearchModule(value || '')}
              style={{ width: 160 }}
              options={[
                { label: '通用', value: 'common' },
                { label: 'CMS', value: 'cms' },
                { label: '技能', value: 'skills' },
                { label: '商城', value: 'store' },
                { label: '支付', value: 'payment' },
                { label: '积分', value: 'points' },
                { label: '管理', value: 'admin' },
              ]}
            />
            <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
              搜索
            </Button>
            {(searchKey || searchModule) && (
              <Button onClick={handleResetSearch}>重置</Button>
            )}
          </Space>

          <Space wrap>
            <Button icon={<DownloadOutlined />} onClick={handleExport}>
              导出JSON
            </Button>
            <Button icon={<UploadOutlined />} onClick={handleImport}>
              导入JSON
            </Button>
            <Button icon={<ReloadOutlined />} onClick={() => loadTranslations(pagination.current, pagination.pageSize)}>
              刷新
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreate}>
              添加翻译
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
              showTotal: (total) => `共 ${total} 条翻译`,
            }}
            scroll={{ x: 1000 }}
            locale={{
              emptyText: <Empty description="暂无翻译" />,
            }}
          />
        </Spin>
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        title={editingTranslation ? '编辑翻译' : '添加翻译'}
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
            label="键名"
            rules={[{ required: true, message: '请输入翻译键名' }]}
          >
            <Input
              placeholder="示例: nav.home"
              disabled={editingTranslation !== null}
            />
          </Form.Item>
          <Form.Item
            name="zh_CN"
            label="中文"
            rules={[{ required: true, message: '请输入中文翻译' }]}
          >
            <TextArea rows={2} placeholder="示例: 首页" />
          </Form.Item>
          <Form.Item
            name="en"
            label="英文"
            rules={[{ required: true, message: '请输入英文翻译' }]}
          >
            <TextArea rows={2} placeholder="示例: Home" />
          </Form.Item>
          <Form.Item
            name="module"
            label="模块"
            rules={[{ required: true, message: '请选择模块' }]}
          >
            <Select
              options={[
                { label: '通用', value: 'common' },
                { label: 'CMS', value: 'cms' },
                { label: '技能', value: 'skills' },
                { label: '商城', value: 'store' },
                { label: '支付', value: 'payment' },
                { label: '积分', value: 'points' },
                { label: '管理', value: 'admin' },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default I18nManagement;
