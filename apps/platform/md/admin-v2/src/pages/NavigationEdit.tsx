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
      const msg = error instanceof Error ? error.message : 'Failed to load navigation';
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
      message.success('Navigation saved successfully');
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : 'Failed to save navigation';
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
        message.success('Item updated');
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
        message.success('Item added');
      }

      setModalVisible(false);
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) return;
    }
  };

  const handleDelete = (record: NavItem) => {
    setItems((prev) => prev.filter((item) => item.id !== record.id));
    message.success('Item deleted');
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
      title: 'Sort',
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
      title: 'Label (ZH)',
      dataIndex: 'label_zh',
      key: 'label_zh',
      width: 150,
    },
    {
      title: 'Label (EN)',
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
      title: 'Icon',
      dataIndex: 'icon',
      key: 'icon',
      width: 120,
      render: (icon: string) => icon || <Tag>none</Tag>,
    },
    {
      title: 'Visible',
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
      title: 'Sort Order',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 100,
    },
    {
      title: 'Actions',
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
            Edit
          </Button>
          <Popconfirm
            title="Delete this navigation item?"
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
        <Title level={2}>Navigation Editor</Title>
        <p style={{ color: '#888' }}>
          Manage the site navigation menu using drag-and-drop or move buttons. Click Save to persist changes.
        </p>
      </div>

      <Card
        extra={
          <Space>
            <Button icon={<ReloadOutlined />} onClick={loadNavigation}>
              Reload
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              Add Item
            </Button>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSaveAll}
              loading={saving}
            >
              Save Changes
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
              emptyText: <Empty description="No navigation items. Add one to get started." />,
            }}
          />
        </Spin>
      </Card>

      {/* Add/Edit Modal */}
      <Modal
        title={editingItem ? 'Edit Navigation Item' : 'Add Navigation Item'}
        open={modalVisible}
        onOk={handleModalSubmit}
        onCancel={() => setModalVisible(false)}
        width={560}
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            name="label_zh"
            label="Label (Chinese)"
            rules={[{ required: true, message: 'Please enter the Chinese label' }]}
          >
            <Input placeholder="e.g. 首页" />
          </Form.Item>
          <Form.Item
            name="label_en"
            label="Label (English)"
            rules={[{ required: true, message: 'Please enter the English label' }]}
          >
            <Input placeholder="e.g. Home" />
          </Form.Item>
          <Form.Item
            name="url"
            label="URL"
            rules={[{ required: true, message: 'Please enter the URL' }]}
          >
            <Input placeholder="e.g. /home or https://..." />
          </Form.Item>
          <Form.Item name="icon" label="Icon (text/class name)">
            <Input placeholder="e.g. HomeOutlined" />
          </Form.Item>
          <Form.Item
            name="sort_order"
            label="Sort Order"
            rules={[{ required: true, message: 'Please enter sort order' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="is_visible" label="Visible" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default NavigationEdit;
