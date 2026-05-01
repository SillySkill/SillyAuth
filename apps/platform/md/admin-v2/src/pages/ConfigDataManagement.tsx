import React, { useEffect, useState, useCallback } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  message,
  Card,
  Row,
  Col,
  Typography,
  Popconfirm,
  Empty,
  Spin,
  List,
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  getConfigList,
  createConfig,
  updateConfig,
  deleteConfig,
} from '../api/configData';
import type { ConfigDataItem } from '../api/configData';
import { formatDate } from '../utils';

const { TextArea } = Input;
const { Title, Text } = Typography;

// Predefined categories available in the system
const DEFAULT_CATEGORIES = [
  'hero_slides',
  'market_stats',
  'vendor_tiers',
  'platform_features',
  'pricing',
  'about',
  'privacy',
  'terms',
  'contact',
  'footer',
  'system',
  'sillyclaw',
  'navigation',
  'tasks',
];

interface ConfigFormValues {
  category: string;
  name: string;
  dataJson: string;
}

const ConfigDataManagement: React.FC = () => {
  const [items, setItems] = useState<ConfigDataItem[]>([]);
  const [categories, setCategories] = useState<string[]>(DEFAULT_CATEGORIES);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<ConfigDataItem | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm<ConfigFormValues>();

  const fetchItems = useCallback(async () => {
    if (!activeCategory) return;
    setLoading(true);
    try {
      const response = await getConfigList(activeCategory);
      if (response.success && response.data) {
        setItems(response.data.items || (Array.isArray(response.data) ? response.data : []));
      }
    } catch (error) {
      message.error(`加载 "${activeCategory}" 分类配置失败`);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [activeCategory]);

  useEffect(() => {
    if (activeCategory) {
      fetchItems();
    }
  }, [activeCategory, fetchItems]);

  // Try to discover categories from active items (in a real app you'd have an endpoint)
  const handleAdd = () => {
    setEditingItem(null);
    form.resetFields();
    form.setFieldsValue({
      category: activeCategory || '',
      name: '',
      dataJson: '{}',
    });
    setModalVisible(true);
  };

  const handleEdit = (record: ConfigDataItem) => {
    setEditingItem(record);
    form.setFieldsValue({
      category: record.category,
      name: record.name,
      dataJson: JSON.stringify(record.data, null, 2),
    });
    setModalVisible(true);
  };

  const handleDelete = async (record: ConfigDataItem) => {
    try {
      await deleteConfig(record.category, record.name);
      message.success('配置项已删除');
      fetchItems();
    } catch (error) {
      message.error('删除配置项失败');
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const values = await form.validateFields();

      // Validate JSON
      let parsedData: Record<string, unknown>;
      try {
        parsedData = JSON.parse(values.dataJson);
      } catch {
        message.error('JSON 格式无效，请检查后重试');
        return;
      }

      if (editingItem) {
        await updateConfig(editingItem.category, editingItem.name, {
          data: parsedData,
        });
        message.success('配置项已更新');
      } else {
        await createConfig({
          category: values.category,
          name: values.name,
          data: parsedData,
        });
        message.success('配置项已创建');
        // Add category to list if new
        if (!categories.includes(values.category)) {
          setCategories((prev) => [...prev, values.category]);
        }
        if (values.category !== activeCategory) {
          setActiveCategory(values.category);
        }
      }
      setModalVisible(false);
      fetchItems();
    } catch (error: any) {
      if (error?.errorFields) return;
      message.error('操作失败');
    } finally {
      setSubmitting(false);
    }
  };

  const columns: ColumnsType<ConfigDataItem> = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 220,
      render: (name: string) => (
        <Text strong style={{ fontFamily: 'monospace' }}>
          {name}
        </Text>
      ),
    },
    {
      title: '数据预览',
      dataIndex: 'data',
      key: 'data',
      ellipsis: true,
      render: (data: Record<string, unknown>) => {
        const json = JSON.stringify(data);
        const preview = json.length > 120 ? json.substring(0, 120) + '...' : json;
        return (
          <Tooltip title={<pre style={{ maxWidth: 400, maxHeight: 300, overflow: 'auto', fontSize: 12, margin: 0 }}>{json}</pre>}>
            <Text
              style={{
                fontFamily: 'monospace',
                fontSize: 12,
                color: '#666',
              }}
            >
              {preview}
            </Text>
          </Tooltip>
        );
      },
    },
    {
      title: '数据键数量',
      dataIndex: 'data',
      key: 'keyCount',
      width: 110,
      render: (data: Record<string, unknown>) => (
        <Tag color="blue">{Object.keys(data || {}).length} 个字段</Tag>
      ),
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (date: string) => formatDate(date),
    },
    {
      title: '操作',
      key: 'actions',
      width: 180,
      fixed: 'right',
      render: (_: unknown, record: ConfigDataItem) => (
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
            title="删除此配置项？"
            description="此操作不可撤销。"
            onConfirm={() => handleDelete(record)}
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
        配置数据管理
      </Title>

      <Row gutter={16}>
        {/* Left Panel: Category List */}
        <Col xs={24} sm={8} md={6} lg={5}>
          <Card
            title="配置分类"
            size="small"
            style={{ height: '100%' }}
            extra={
              <Button
                type="text"
                size="small"
                icon={<ReloadOutlined />}
                onClick={() => {
                  if (activeCategory) fetchItems();
                }}
              />
            }
          >
            <List
              size="small"
              dataSource={categories}
              renderItem={(category) => (
                <List.Item
                  key={category}
                  onClick={() => setActiveCategory(category)}
                  style={{
                    cursor: 'pointer',
                    padding: '8px 12px',
                    borderRadius: 6,
                    backgroundColor:
                      activeCategory === category ? '#e6f4ff' : 'transparent',
                    borderLeft:
                      activeCategory === category
                        ? '3px solid #1677ff'
                        : '3px solid transparent',
                    marginBottom: 2,
                  }}
                >
                  <Space>
                    <SettingOutlined
                      style={{
                        color: activeCategory === category ? '#1677ff' : '#999',
                      }}
                    />
                    <Text
                      strong={activeCategory === category}
                      style={{
                        color:
                          activeCategory === category ? '#1677ff' : 'inherit',
                      }}
                    >
                      {category}
                    </Text>
                  </Space>
                </List.Item>
              )}
              locale={{ emptyText: '暂无分类' }}
            />
          </Card>
        </Col>

        {/* Right Panel: Data Table */}
        <Col xs={24} sm={16} md={18} lg={19}>
          {!activeCategory ? (
            <Card>
              <Empty description="请从左侧选择一个配置分类以查看条目" />
            </Card>
          ) : (
            <Card
              title={
                <Space>
                  <SettingOutlined />
                  <span>{activeCategory}</span>
                  <Tag color="blue">{items.length} 个条目</Tag>
                </Space>
              }
              extra={
                <Space>
                  <Button icon={<ReloadOutlined />} onClick={fetchItems}>
                    刷新
                  </Button>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={handleAdd}
                  >
                    新建配置项
                  </Button>
                </Space>
              }
            >
              <Spin spinning={loading}>
                <Table<ConfigDataItem>
                  columns={columns}
                  dataSource={items}
                  rowKey="name"
                  pagination={false}
                  scroll={{ x: 900 }}
                  locale={{
                    emptyText: (
                      <Empty description={`"${activeCategory}" 分类下暂无配置项`} />
                    ),
                  }}
                />
              </Spin>
            </Card>
          )}
        </Col>
      </Row>

      {/* Create/Edit Modal */}
      <Modal
        title={editingItem ? '编辑配置项' : '创建配置项'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={800}
        confirmLoading={submitting}
        okText={editingItem ? '更新' : '创建'}
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="分类 (Category)"
                name="category"
                rules={[{ required: true, message: '请输入分类名称' }]}
              >
                <Input
                  placeholder="e.g. hero_slides"
                  disabled={!!editingItem}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="名称 (Name)"
                name="name"
                rules={[{ required: true, message: '请输入配置名称' }]}
              >
                <Input
                  placeholder="e.g. homepage_slides"
                  disabled={!!editingItem}
                />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item
            label="JSON 数据"
            name="dataJson"
            rules={[
              { required: true, message: '请输入 JSON 数据' },
              {
                validator: (_, value) => {
                  if (!value) return Promise.resolve();
                  try {
                    JSON.parse(value);
                    return Promise.resolve();
                  } catch {
                    return Promise.reject(new Error('JSON 格式无效'));
                  }
                },
              },
            ]}
          >
            <TextArea
              rows={16}
              placeholder='{"key": "value"}'
              style={{ fontFamily: 'monospace', fontSize: 13 }}
              showCount
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ConfigDataManagement;
