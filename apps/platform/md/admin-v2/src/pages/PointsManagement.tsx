/**
 * Points Management
 *
 * Admin page for managing points mall: Products, Categories, and Exchange Records.
 * Three tabs with full CRUD operations.
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
      const msg = error instanceof Error ? error.message : 'Failed to load products';
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
      const msg = error instanceof Error ? error.message : 'Failed to load categories';
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
      const msg = error instanceof Error ? error.message : 'Failed to load exchange records';
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
        message.success('Product updated successfully');
      } else {
        await createPointsProduct(values);
        message.success('Product created successfully');
      }

      setProductModalVisible(false);
      loadProducts();
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) return;
      const msg = error instanceof Error ? error.message : 'Operation failed';
      message.error(msg);
    } finally {
      setProductSubmitting(false);
    }
  };

  const handleDeleteProduct = (record: ProductItem) => {
    Modal.confirm({
      title: 'Delete Product',
      content: `Are you sure you want to delete "${record.name}"?`,
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await deletePointsProduct(record.id);
          message.success('Product deleted successfully');
          loadProducts();
        } catch (error: unknown) {
          const msg = error instanceof Error ? error.message : 'Delete failed';
          message.error(msg);
        }
      },
    });
  };

  const handleToggleProductActive = async (record: ProductItem, checked: boolean) => {
    try {
      await updatePointsProduct(record.id, { is_active: checked });
      message.success(`Product ${checked ? 'activated' : 'deactivated'}`);
      loadProducts();
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : 'Update failed';
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
        message.success('Category updated successfully');
      } else {
        message.success('Category created successfully');
      }

      setCategoryModalVisible(false);
      loadCategories();
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) return;
      const msg = error instanceof Error ? error.message : 'Operation failed';
      message.error(msg);
    } finally {
      setCategorySubmitting(false);
    }
  };

  const handleDeleteCategory = (record: CategoryItem) => {
    Modal.confirm({
      title: 'Delete Category',
      content: `Are you sure you want to delete "${record.name}"?`,
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          message.success('Category deleted successfully');
          loadCategories();
        } catch (error: unknown) {
          const msg = error instanceof Error ? error.message : 'Delete failed';
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
      message.success('Exchange status updated successfully');
      setExchangeStatusVisible(false);
      loadExchanges();
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) return;
      const msg = error instanceof Error ? error.message : 'Update failed';
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
      pending: { color: 'orange', text: 'Pending' },
      approved: { color: 'blue', text: 'Approved' },
      rejected: { color: 'red', text: 'Rejected' },
      completed: { color: 'green', text: 'Completed' },
      cancelled: { color: 'default', text: 'Cancelled' },
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
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: 'Points Required',
      dataIndex: 'points_required',
      key: 'points_required',
      width: 130,
      sorter: (a, b) => a.points_required - b.points_required,
      render: (points: number) => (
        <span style={{ color: '#faad14', fontWeight: 600 }}>{points}</span>
      ),
    },
    {
      title: 'Stock',
      dataIndex: 'stock',
      key: 'stock',
      width: 90,
      render: (stock: number) =>
        stock === -1 ? (
          <Tag color="green">Unlimited</Tag>
        ) : stock === 0 ? (
          <Tag color="red">Out of Stock</Tag>
        ) : (
          stock
        ),
    },
    {
      title: 'Status',
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
      title: 'Category',
      key: 'category',
      width: 120,
      render: (_: unknown, record: ProductItem) =>
        record.category?.name || <Tag>{record.category_id || 'N/A'}</Tag>,
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      render: (date: string) => (date ? new Date(date).toLocaleDateString() : 'N/A'),
    },
    {
      title: 'Actions',
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
            Edit
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteProduct(record)}
          >
            Delete
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
      title: 'Category Name',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Sort Order',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 100,
      sorter: (a, b) => a.sort_order - b.sort_order,
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      render: (date: string) => (date ? new Date(date).toLocaleDateString() : 'N/A'),
    },
    {
      title: 'Actions',
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
            Edit
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteCategory(record)}
          >
            Delete
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
      title: 'User',
      key: 'user',
      width: 120,
      render: (_: unknown, record: ExchangeRecord) =>
        record.user?.username ?? `User #${record.user_id}`,
    },
    {
      title: 'Product',
      key: 'product',
      width: 150,
      ellipsis: true,
      render: (_: unknown, record: ExchangeRecord) =>
        record.product?.name ?? `Product #${record.product_id}`,
    },
    {
      title: 'Points Used',
      dataIndex: 'points_spent',
      key: 'points_spent',
      width: 110,
      render: (points: number) => (
        <span style={{ color: '#faad14', fontWeight: 600 }}>{points}</span>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 110,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      render: (date: string) => (date ? new Date(date).toLocaleString() : 'N/A'),
    },
    {
      title: 'Actions',
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
          Update Status
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
          <GiftOutlined /> Products
        </span>
      ),
      children: (
        <>
          <div style={{ marginBottom: 16, textAlign: 'right' }}>
            <Space>
              <Button icon={<ReloadOutlined />} onClick={loadProducts}>
                Refresh
              </Button>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenProductCreate}>
                Add Product
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
              showTotal: (total) => `Total ${total} products`,
            }}
            scroll={{ x: 1000 }}
            locale={{
              emptyText: <Empty description="No products found" />,
            }}
          />
        </>
      ),
    },
    {
      key: 'categories',
      label: (
        <span>
          <FolderOutlined /> Categories
        </span>
      ),
      children: (
        <>
          <div style={{ marginBottom: 16, textAlign: 'right' }}>
            <Space>
              <Button icon={<ReloadOutlined />} onClick={loadCategories}>
                Refresh
              </Button>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCategoryCreate}>
                Add Category
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
              showTotal: (total) => `Total ${total} categories`,
            }}
            locale={{
              emptyText: <Empty description="No categories found" />,
            }}
          />
        </>
      ),
    },
    {
      key: 'exchanges',
      label: (
        <span>
          <SwapOutlined /> Exchange Records
        </span>
      ),
      children: (
        <>
          <div style={{ marginBottom: 16, textAlign: 'right' }}>
            <Button icon={<ReloadOutlined />} onClick={loadExchanges}>
              Refresh
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
              showTotal: (total) => `Total ${total} records`,
            }}
            scroll={{ x: 900 }}
            locale={{
              emptyText: <Empty description="No exchange records found" />,
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
        <Title level={2}>Points Management</Title>
        <p style={{ color: '#888' }}>
          Manage points mall products, categories, and exchange records.
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
        title={editingProduct ? 'Edit Product' : 'Add Product'}
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
            label="Name"
            rules={[{ required: true, message: 'Please enter product name' }]}
          >
            <Input placeholder="e.g. VIP Membership" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <TextArea rows={3} placeholder="Product description" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="points_required"
                label="Points Required"
                rules={[{ required: true, message: 'Please enter points' }]}
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
                label="Stock"
                rules={[{ required: true, message: 'Please enter stock' }]}
                extra="Use -1 for unlimited"
              >
                <InputNumber min={-1} style={{ width: '100%' }} placeholder="0" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="image_url" label="Image URL">
            <Input placeholder="https://example.com/image.png" />
          </Form.Item>
          <Form.Item name="category_id" label="Category">
            <Select
              allowClear
              placeholder="Select category"
              options={categories.map((c) => ({
                label: c.name,
                value: c.id,
              }))}
            />
          </Form.Item>
          <Form.Item name="is_active" label="Active" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>

      {/* Category Create/Edit Modal */}
      <Modal
        title={editingCategory ? 'Edit Category' : 'Add Category'}
        open={categoryModalVisible}
        onOk={handleCategorySubmit}
        onCancel={() => setCategoryModalVisible(false)}
        confirmLoading={categorySubmitting}
        destroyOnClose
      >
        <Form form={categoryForm} layout="vertical" preserve={false}>
          <Form.Item
            name="name"
            label="Category Name"
            rules={[{ required: true, message: 'Please enter category name' }]}
          >
            <Input placeholder="e.g. Digital Goods" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <TextArea rows={2} placeholder="Category description" />
          </Form.Item>
          <Form.Item
            name="sort_order"
            label="Sort Order"
            rules={[{ required: true, message: 'Please enter sort order' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} placeholder="0" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Exchange Status Update Modal */}
      <Modal
        title="Update Exchange Status"
        open={exchangeStatusVisible}
        onOk={handleExchangeStatusSubmit}
        onCancel={() => setExchangeStatusVisible(false)}
        confirmLoading={exchangeSubmitting}
        destroyOnClose
      >
        <div style={{ marginBottom: 16 }}>
          <p>
            User: <strong>{selectedExchange?.user?.username ?? `#${selectedExchange?.user_id}`}</strong>
          </p>
          <p>
            Product: <strong>{selectedExchange?.product?.name ?? `#${selectedExchange?.product_id}`}</strong>
          </p>
          <p>
            Points Used: <strong>{selectedExchange?.points_spent}</strong>
          </p>
        </div>
        <Form form={exchangeForm} layout="vertical" preserve={false}>
          <Form.Item
            name="status"
            label="Status"
            rules={[{ required: true, message: 'Please select a status' }]}
          >
            <Select
              options={[
                { label: 'Pending', value: 'pending' },
                { label: 'Approved', value: 'approved' },
                { label: 'Rejected', value: 'rejected' },
                { label: 'Completed', value: 'completed' },
              ]}
            />
          </Form.Item>
          <Form.Item name="tracking_number" label="Reason / Tracking Number">
            <Input placeholder="Optional reason or tracking number" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PointsManagement;
