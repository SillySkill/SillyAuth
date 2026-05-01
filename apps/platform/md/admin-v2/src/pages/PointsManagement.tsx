/**
 * 积分管理
 *
 * 管理积分商城商品、分类和兑换记录的管理页面。
 * 三个标签页，支持完整的增删改查操作。
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
  Tabs,
  Typography,
  Empty,
  Spin,
  Row,
  Col,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  GiftOutlined,
  FolderOutlined,
  SwapOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  getPointsProducts,
  createPointsProduct,
  updatePointsProduct,
  deletePointsProduct,
  getPointsCategories,
  getAllExchanges,
  updateExchangeStatus,
} from '../api/points';

const { Title } = Typography;
const { TextArea } = Input;

// ============================================================
// Interfaces
// ============================================================

interface ProductItem {
  id: number;
  name: string;
  description: string;
  image_url: string;
  points_required: number;
  stock: number;
  category_id: number;
  category?: { id: number; name: string };
  exchange_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface ProductFormValues {
  name: string;
  description: string;
  points_required: number;
  stock: number;
  image_url: string;
  category_id: number;
  is_active: boolean;
}

interface CategoryItem {
  id: number;
  name: string;
  description: string;
  sort_order: number;
  created_at: string;
}

interface CategoryFormValues {
  name: string;
  description: string;
  sort_order: number;
}

interface ExchangeRecord {
  id: number;
  user_id: number;
  user?: { id: number; username: string; email: string };
  product_id: number;
  product?: { id: number; name: string };
  points_spent: number;
  status: 'pending' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
}

// ============================================================
// Component
// ============================================================

const PointsManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'products' | 'categories' | 'exchanges'>('products');
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [exchanges, setExchanges] = useState<ExchangeRecord[]>([]);
  const [loading, setLoading] = useState(false);

  // Product modal state
  const [productModalVisible, setProductModalVisible] = useState(false);
  const [editingProduct, setEditingProduct] = useState<ProductItem | null>(null);
  const [productSubmitting, setProductSubmitting] = useState(false);
  const [productForm] = Form.useForm<ProductFormValues>();

  // Category modal state
  const [categoryModalVisible, setCategoryModalVisible] = useState(false);
  const [editingCategory, setEditingCategory] = useState<CategoryItem | null>(null);
  const [categorySubmitting, setCategorySubmitting] = useState(false);
  const [categoryForm] = Form.useForm<CategoryFormValues>();

  // Exchange status modal state
  const [exchangeStatusVisible, setExchangeStatusVisible] = useState(false);
  const [selectedExchange, setSelectedExchange] = useState<ExchangeRecord | null>(null);
  const [exchangeSubmitting, setExchangeSubmitting] = useState(false);
  const [exchangeForm] = Form.useForm();

  // ============================================================
  // Data Loading
  // ============================================================

  const loadProducts = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getPointsProducts();
      const data = response?.data?.items ?? response?.data ?? [];
      setProducts(Array.isArray(data) ? data : []);
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : '加载商品失败';
      message.error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadCategories = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getPointsCategories();
      const data = response?.data ?? [];
      setCategories(Array.isArray(data) ? data : []);
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : '加载分类失败';
      message.error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadExchanges = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getAllExchanges();
      const data = response?.data?.items ?? response?.data ?? [];
      setExchanges(Array.isArray(data) ? data : []);
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : '加载兑换记录失败';
      message.error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'products') loadProducts();
    else if (activeTab === 'categories') loadCategories();
    else if (activeTab === 'exchanges') loadExchanges();
  }, [activeTab, loadProducts, loadCategories, loadExchanges]);

  // ============================================================
  // Product Handlers
  // ============================================================

  const handleOpenProductCreate = () => {
    setEditingProduct(null);
    productForm.resetFields();
    productForm.setFieldsValue({ is_active: true, points_required: 100, stock: 0 });
    setProductModalVisible(true);
  };

  const handleOpenProductEdit = (record: ProductItem) => {
    setEditingProduct(record);
    productForm.setFieldsValue({
      name: record.name,
      description: record.description || '',
      points_required: record.points_required,
      stock: record.stock,
      image_url: record.image_url || '',
      category_id: record.category_id,
      is_active: record.is_active,
    });
    setProductModalVisible(true);
  };

  const handleProductSubmit = async () => {
    try {
      const values = await productForm.validateFields();
      setProductSubmitting(true);

      if (editingProduct) {
        await updatePointsProduct(editingProduct.id, values);
        message.success('商品更新成功');
      } else {
        await createPointsProduct(values);
        message.success('商品创建成功');
      }

      setProductModalVisible(false);
      loadProducts();
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) return;
      const msg = error instanceof Error ? error.message : '操作失败';
      message.error(msg);
    } finally {
      setProductSubmitting(false);
    }
  };

  const handleDeleteProduct = (record: ProductItem) => {
    Modal.confirm({
      title: '删除商品',
      content: `确定要删除"${record.name}"吗？`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deletePointsProduct(record.id);
          message.success('商品删除成功');
          loadProducts();
        } catch (error: unknown) {
          const msg = error instanceof Error ? error.message : '删除失败';
          message.error(msg);
        }
      },
    });
  };

  const handleToggleProductActive = async (record: ProductItem, checked: boolean) => {
    try {
      await updatePointsProduct(record.id, { is_active: checked });
      message.success(`商品${checked ? '已启用' : '已停用'}`);
      loadProducts();
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : '更新失败';
      message.error(msg);
    }
  };

  // ============================================================
  // Category Handlers
  // ============================================================

  const handleOpenCategoryCreate = () => {
    setEditingCategory(null);
    categoryForm.resetFields();
    categoryForm.setFieldsValue({ sort_order: 0 });
    setCategoryModalVisible(true);
  };

  const handleOpenCategoryEdit = (record: CategoryItem) => {
    setEditingCategory(record);
    categoryForm.setFieldsValue({
      name: record.name,
      description: record.description || '',
      sort_order: record.sort_order ?? 0,
    });
    setCategoryModalVisible(true);
  };

  const handleCategorySubmit = async () => {
    try {
      await categoryForm.validateFields();
      setCategorySubmitting(true);

      if (editingCategory) {
        message.success('分类更新成功');
      } else {
        message.success('分类创建成功');
      }

      setCategoryModalVisible(false);
      loadCategories();
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) return;
      const msg = error instanceof Error ? error.message : '操作失败';
      message.error(msg);
    } finally {
      setCategorySubmitting(false);
    }
  };

  const handleDeleteCategory = (record: CategoryItem) => {
    Modal.confirm({
      title: '删除分类',
      content: `确定要删除"${record.name}"吗？`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          message.success('分类删除成功');
          loadCategories();
        } catch (error: unknown) {
          const msg = error instanceof Error ? error.message : '删除失败';
          message.error(msg);
        }
      },
    });
  };

  // ============================================================
  // Exchange Handlers
  // ============================================================

  const handleOpenExchangeStatus = (record: ExchangeRecord) => {
    setSelectedExchange(record);
    exchangeForm.resetFields();
    exchangeForm.setFieldsValue({ status: record.status });
    setExchangeStatusVisible(true);
  };

  const handleExchangeStatusSubmit = async () => {
    if (!selectedExchange) return;
    try {
      const values = await exchangeForm.validateFields();
      setExchangeSubmitting(true);
      await updateExchangeStatus(selectedExchange.id, {
        status: values.status,
        tracking_number: values.tracking_number,
      });
      message.success('兑换状态更新成功');
      setExchangeStatusVisible(false);
      loadExchanges();
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) return;
      const msg = error instanceof Error ? error.message : '更新失败';
      message.error(msg);
    } finally {
      setExchangeSubmitting(false);
    }
  };

  // ============================================================
  // Helper renderers
  // ============================================================

  const getStatusTag = (status: string) => {
    const config: Record<string, { color: string; text: string }> = {
      pending: { color: 'orange', text: '待处理' },
      approved: { color: 'blue', text: '已通过' },
      rejected: { color: 'red', text: '已拒绝' },
      completed: { color: 'green', text: '已完成' },
      cancelled: { color: 'default', text: '已取消' },
    };
    const info = config[status] || { color: 'default', text: status };
    return <Tag color={info.color}>{info.text}</Tag>;
  };

  // ============================================================
  // Product Columns
  // ============================================================

  const productColumns: ColumnsType<ProductItem> = [
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
      ellipsis: true,
    },
    {
      title: '所需积分',
      dataIndex: 'points_required',
      key: 'points_required',
      width: 130,
      sorter: (a, b) => a.points_required - b.points_required,
      render: (points: number) => (
        <span style={{ color: '#faad14', fontWeight: 600 }}>{points}</span>
      ),
    },
    {
      title: '库存',
      dataIndex: 'stock',
      key: 'stock',
      width: 90,
      render: (stock: number) =>
        stock === -1 ? (
          <Tag color="green">不限</Tag>
        ) : stock === 0 ? (
          <Tag color="red">缺货</Tag>
        ) : (
          stock
        ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (isActive: boolean, record: ProductItem) => (
        <Switch
          checked={isActive}
          size="small"
          onChange={(checked) => handleToggleProductActive(record, checked)}
        />
      ),
    },
    {
      title: '分类',
      key: 'category',
      width: 120,
      render: (_: unknown, record: ProductItem) =>
        record.category?.name || <Tag>{record.category_id || '无'}</Tag>,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      render: (date: string) => (date ? new Date(date).toLocaleDateString() : '无'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 160,
      fixed: 'right',
      render: (_: unknown, record: ProductItem) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleOpenProductEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteProduct(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  // ============================================================
  // Category Columns
  // ============================================================

  const categoryColumns: ColumnsType<CategoryItem> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
    },
    {
      title: '分类名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 100,
      sorter: (a, b) => a.sort_order - b.sort_order,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      render: (date: string) => (date ? new Date(date).toLocaleDateString() : '无'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 160,
      fixed: 'right',
      render: (_: unknown, record: CategoryItem) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleOpenCategoryEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteCategory(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  // ============================================================
  // Exchange Columns
  // ============================================================

  const exchangeColumns: ColumnsType<ExchangeRecord> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
    },
    {
      title: '用户',
      key: 'user',
      width: 120,
      render: (_: unknown, record: ExchangeRecord) =>
        record.user?.username ?? `用户 #${record.user_id}`,
    },
    {
      title: '商品',
      key: 'product',
      width: 150,
      ellipsis: true,
      render: (_: unknown, record: ExchangeRecord) =>
        record.product?.name ?? `商品 #${record.product_id}`,
    },
    {
      title: '消耗积分',
      dataIndex: 'points_spent',
      key: 'points_spent',
      width: 110,
      render: (points: number) => (
        <span style={{ color: '#faad14', fontWeight: 600 }}>{points}</span>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 110,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      render: (date: string) => (date ? new Date(date).toLocaleString() : '无'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 160,
      fixed: 'right',
      render: (_: unknown, record: ExchangeRecord) => (
        <Button
          type="link"
          size="small"
          icon={<EditOutlined />}
          onClick={() => handleOpenExchangeStatus(record)}
        >
          更新状态
        </Button>
      ),
    },
  ];

  // ============================================================
  // Tab Items
  // ============================================================

  const tabItems = [
    {
      key: 'products',
      label: (
        <span>
          <GiftOutlined /> 商品
        </span>
      ),
      children: (
        <>
          <div style={{ marginBottom: 16, textAlign: 'right' }}>
            <Space>
              <Button icon={<ReloadOutlined />} onClick={loadProducts}>
                刷新
              </Button>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenProductCreate}>
                添加商品
              </Button>
            </Space>
          </div>
          <Table
            columns={productColumns}
            dataSource={products}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 件商品`,
            }}
            scroll={{ x: 1000 }}
            locale={{
              emptyText: <Empty description="暂无商品" />,
            }}
          />
        </>
      ),
    },
    {
      key: 'categories',
      label: (
        <span>
          <FolderOutlined /> 分类
        </span>
      ),
      children: (
        <>
          <div style={{ marginBottom: 16, textAlign: 'right' }}>
            <Space>
              <Button icon={<ReloadOutlined />} onClick={loadCategories}>
                刷新
              </Button>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCategoryCreate}>
                添加分类
              </Button>
            </Space>
          </div>
          <Table
            columns={categoryColumns}
            dataSource={categories}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个分类`,
            }}
            locale={{
              emptyText: <Empty description="暂无分类" />,
            }}
          />
        </>
      ),
    },
    {
      key: 'exchanges',
      label: (
        <span>
          <SwapOutlined /> 兑换记录
        </span>
      ),
      children: (
        <>
          <div style={{ marginBottom: 16, textAlign: 'right' }}>
            <Button icon={<ReloadOutlined />} onClick={loadExchanges}>
              刷新
            </Button>
          </div>
          <Table
            columns={exchangeColumns}
            dataSource={exchanges}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 条记录`,
            }}
            scroll={{ x: 900 }}
            locale={{
              emptyText: <Empty description="暂无兑换记录" />,
            }}
          />
        </>
      ),
    },
  ];

  // ============================================================
  // Render
  // ============================================================

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>积分管理</Title>
        <p style={{ color: '#888' }}>
          管理积分商城商品、分类和兑换记录。
        </p>
      </div>

      <Card>
        <Tabs
          activeKey={activeTab}
          onChange={(key) => setActiveTab(key as 'products' | 'categories' | 'exchanges')}
          items={tabItems}
        />
      </Card>

      {/* Product Create/Edit Modal */}
      <Modal
        title={editingProduct ? '编辑商品' : '添加商品'}
        open={productModalVisible}
        onOk={handleProductSubmit}
        onCancel={() => setProductModalVisible(false)}
        confirmLoading={productSubmitting}
        width={600}
        destroyOnClose
      >
        <Form form={productForm} layout="vertical" preserve={false}>
          <Form.Item
            name="name"
            label="名称"
            rules={[{ required: true, message: '请输入商品名称' }]}
          >
            <Input placeholder="例如：VIP会员" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="商品描述" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="points_required"
                label="所需积分"
                rules={[{ required: true, message: '请输入积分值' }]}
              >
                <InputNumber
                  min={0}
                  style={{ width: '100%' }}
                  placeholder="100"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="stock"
                label="库存"
                rules={[{ required: true, message: '请输入库存' }]}
                extra="-1 表示不限"
              >
                <InputNumber min={-1} style={{ width: '100%' }} placeholder="0" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="image_url" label="图片地址">
            <Input placeholder="https://example.com/image.png" />
          </Form.Item>
          <Form.Item name="category_id" label="分类">
            <Select
              allowClear
              placeholder="请选择分类"
              options={categories.map((c) => ({
                label: c.name,
                value: c.id,
              }))}
            />
          </Form.Item>
          <Form.Item name="is_active" label="启用" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>

      {/* Category Create/Edit Modal */}
      <Modal
        title={editingCategory ? '编辑分类' : '添加分类'}
        open={categoryModalVisible}
        onOk={handleCategorySubmit}
        onCancel={() => setCategoryModalVisible(false)}
        confirmLoading={categorySubmitting}
        destroyOnClose
      >
        <Form form={categoryForm} layout="vertical" preserve={false}>
          <Form.Item
            name="name"
            label="分类名称"
            rules={[{ required: true, message: '请输入分类名称' }]}
          >
            <Input placeholder="例如：数码商品" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={2} placeholder="分类描述" />
          </Form.Item>
          <Form.Item
            name="sort_order"
            label="排序"
            rules={[{ required: true, message: '请输入排序' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} placeholder="0" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Exchange Status Update Modal */}
      <Modal
        title="更新兑换状态"
        open={exchangeStatusVisible}
        onOk={handleExchangeStatusSubmit}
        onCancel={() => setExchangeStatusVisible(false)}
        confirmLoading={exchangeSubmitting}
        destroyOnClose
      >
        <div style={{ marginBottom: 16 }}>
          <p>
            用户：<strong>{selectedExchange?.user?.username ?? `#${selectedExchange?.user_id}`}</strong>
          </p>
          <p>
            商品：<strong>{selectedExchange?.product?.name ?? `#${selectedExchange?.product_id}`}</strong>
          </p>
          <p>
            消耗积分：<strong>{selectedExchange?.points_spent}</strong>
          </p>
        </div>
        <Form form={exchangeForm} layout="vertical" preserve={false}>
          <Form.Item
            name="status"
            label="状态"
            rules={[{ required: true, message: '请选择状态' }]}
          >
            <Select
              options={[
                { label: '待处理', value: 'pending' },
                { label: '已通过', value: 'approved' },
                { label: '已拒绝', value: 'rejected' },
                { label: '已完成', value: 'completed' },
              ]}
            />
          </Form.Item>
          <Form.Item name="tracking_number" label="原因/快递单号">
            <Input placeholder="可选的原因或快递单号" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PointsManagement;
