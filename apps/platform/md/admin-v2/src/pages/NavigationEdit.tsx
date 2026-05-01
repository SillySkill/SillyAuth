/**
 * Navigation Editor
 *
 * Admin page for editing the site navigation tree.
 * Uses a list-based approach with move up/down buttons.
 * Since there is no dedicated API module, uses direct api import for calls.
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Button,
  Space,
  message,
  Card,
  Typography,
  Empty,
  Spin,
  Table,
  Switch,
  Input,
  InputNumber,
  Modal,
  Form,
  Tag,
  Popconfirm,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SaveOutlined,
  ReloadOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import api from '../api/index';

const { Title } = Typography;

// ============================================================
// Interfaces
// ============================================================

interface NavItem {
  id: string | number;
  label_zh: string;
  label_en: string;
  url: string;
  icon: string;
  sort_order: number;
  is_visible: boolean;
  children?: NavItem[];
  __isNew?: boolean;
}

interface NavFormValues {
  label_zh: string;
  label_en: string;
  url: string;
  icon: string;
  sort_order: number;
  is_visible: boolean;
}

// ============================================================
// Component
// ============================================================

const NavigationEdit: React.FC = () => {
  const [items, setItems] = useState<NavItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // Modal state
  const [modalVisible, setModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<NavItem | null>(null);
  const [form] = Form.useForm<NavFormValues>();

  // ============================================================
  // Data Loading
  // ============================================================

  const loadNavigation = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('/cms/navigation');
      const data = response?.data?.items ?? response?.items ?? response ?? [];
      setItems(Array.isArray(data) ? data : []);
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : '加载导航失败';
      message.error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadNavigation();
  }, [loadNavigation]);

  // ============================================================
  // Handlers
  // ============================================================

  const handleSaveAll = async () => {
    setSaving(true);
    try {
      await api.put('/cms/navigation', { items });
      message.success('导航保存成功');
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : '保存导航失败';
      message.error(msg);
    } finally {
      setSaving(false);
    }
  };

  const handleAdd = () => {
    setEditingItem(null);
    form.resetFields();
    form.setFieldsValue({
      label_zh: '',
      label_en: '',
      url: '',
      icon: '',
      sort_order: items.length,
      is_visible: true,
    });
    setModalVisible(true);
  };

  const handleEdit = (record: NavItem) => {
    setEditingItem(record);
    form.setFieldsValue({
      label_zh: record.label_zh,
      label_en: record.label_en,
      url: record.url,
      icon: record.icon || '',
      sort_order: record.sort_order,
      is_visible: record.is_visible,
    });
    setModalVisible(true);
  };

  const handleModalSubmit = async () => {
    try {
      const values = await form.validateFields();

      if (editingItem) {
        // Update existing item
        setItems((prev) =>
          prev.map((item) =>
            item.id === editingItem.id
              ? { ...item, ...values }
              : item
          )
        );
        message.success('项目已更新');
      } else {
        // Add new item
        const newItem: NavItem = {
          id: `new_${Date.now()}`,
          label_zh: values.label_zh,
          label_en: values.label_en,
          url: values.url,
          icon: values.icon || '',
          sort_order: values.sort_order,
          is_visible: values.is_visible,
          children: [],
          __isNew: true,
        };
        setItems((prev) => [...prev, newItem]);
        message.success('项目已添加');
      }

      setModalVisible(false);
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) return;
    }
  };

  const handleDelete = (record: NavItem) => {
    setItems((prev) => prev.filter((item) => item.id !== record.id));
    message.success('项目已删除');
  };

  const handleMoveUp = (index: number) => {
    if (index === 0) return;
    setItems((prev) => {
      const newItems = [...prev];
      [newItems[index - 1], newItems[index]] = [newItems[index], newItems[index - 1]];
      return newItems.map((item, i) => ({ ...item, sort_order: i }));
    });
  };

  const handleMoveDown = (index: number) => {
    setItems((prev) => {
      if (index === prev.length - 1) return prev;
      const newItems = [...prev];
      [newItems[index], newItems[index + 1]] = [newItems[index + 1], newItems[index]];
      return newItems.map((item, i) => ({ ...item, sort_order: i }));
    });
  };

  const handleToggleVisible = (record: NavItem, checked: boolean) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === record.id ? { ...item, is_visible: checked } : item
      )
    );
  };

  // ============================================================
  // Columns
  // ============================================================

  const columns: ColumnsType<NavItem> = [
    {
      title: '排序',
      key: 'sort_actions',
      width: 80,
      render: (_: unknown, _record: NavItem, index: number) => (
        <Space size={4}>
          <Button
            type="text"
            size="small"
            icon={<ArrowUpOutlined />}
            disabled={index === 0}
            onClick={() => handleMoveUp(index)}
          />
          <Button
            type="text"
            size="small"
            icon={<ArrowDownOutlined />}
            disabled={index === items.length - 1}
            onClick={() => handleMoveDown(index)}
          />
        </Space>
      ),
    },
    {
      title: '中文标签',
      dataIndex: 'label_zh',
      key: 'label_zh',
      width: 150,
    },
    {
      title: '英文标签',
      dataIndex: 'label_en',
      key: 'label_en',
      width: 150,
    },
    {
      title: 'URL',
      dataIndex: 'url',
      key: 'url',
      width: 200,
      ellipsis: true,
    },
    {
      title: '图标',
      dataIndex: 'icon',
      key: 'icon',
      width: 120,
      render: (icon: string) => icon || <Tag>无</Tag>,
    },
    {
      title: '可见',
      dataIndex: 'is_visible',
      key: 'is_visible',
      width: 80,
      render: (isVisible: boolean, record: NavItem) => (
        <Switch
          checked={isVisible}
          size="small"
          onChange={(checked) => handleToggleVisible(record, checked)}
        />
      ),
    },
    {
      title: '排序值',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 100,
    },
    {
      title: '操作',
      key: 'actions',
      width: 160,
      fixed: 'right',
      render: (_: unknown, record: NavItem) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此导航项？"
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
        <Title level={2}>导航编辑</Title>
        <p style={{ color: '#888' }}>
          通过拖拽或移动按钮管理站点导航菜单，点击保存以持久化更改。
        </p>
      </div>

      <Card
        extra={
          <Space>
            <Button icon={<ReloadOutlined />} onClick={loadNavigation}>
              重新加载
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              添加项
            </Button>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSaveAll}
              loading={saving}
            >
              保存修改
            </Button>
          </Space>
        }
      >
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={items}
            rowKey="id"
            loading={loading}
            pagination={false}
            scroll={{ x: 1000 }}
            locale={{
              emptyText: <Empty description="暂无导航项，点击添加开始使用。" />,
            }}
          />
        </Spin>
      </Card>

      {/* Add/Edit Modal */}
      <Modal
        title={editingItem ? '编辑导航项' : '添加导航项'}
        open={modalVisible}
        onOk={handleModalSubmit}
        onCancel={() => setModalVisible(false)}
        width={560}
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            name="label_zh"
            label="中文标签"
            rules={[{ required: true, message: '请输入中文标签' }]}
          >
            <Input placeholder="e.g. 首页" />
          </Form.Item>
          <Form.Item
            name="label_en"
            label="英文标签"
            rules={[{ required: true, message: '请输入英文标签' }]}
          >
            <Input placeholder="e.g. Home" />
          </Form.Item>
          <Form.Item
            name="url"
            label="URL"
            rules={[{ required: true, message: '请输入 URL' }]}
          >
            <Input placeholder="e.g. /home or https://..." />
          </Form.Item>
          <Form.Item name="icon" label="图标（文本/类名）">
            <Input placeholder="e.g. HomeOutlined" />
          </Form.Item>
          <Form.Item
            name="sort_order"
            label="排序值"
            rules={[{ required: true, message: '请输入排序值' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="is_visible" label="可见" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default NavigationEdit;
