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
  InputNumber,
  Select,
  message,
  Card,
  Row,
  Col,
  Typography,
  Popconfirm,
  Tabs,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  getCollections,
  createCollection,
  updateCollection,
  deleteCollection,
  getProducts,
  createProduct,
  updateProduct,
  deleteProduct,
} from '../api/store';
import type {
  Collection,
  CollectionCreateRequest,
  Product,
  ProductCreateRequest,
} from '../api/store';
import { formatDate, formatCurrency } from '../utils';

const { TextArea } = Input;
const { Title } = Typography;

interface CollectionFormValues {
  name: string;
  slug?: string;
  description?: string;
  image_url?: string;
  sort_order?: number;
  is_active?: boolean;
}

interface ProductFormValues {
  name: string;
  slug?: string;
  description: string;
  price: number;
  currency?: string;
  images?: string;
  collection_id?: number;
  stock?: number;
  is_active?: boolean;
  sort_order?: number;
}

const StoreManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'collections' | 'products'>(
    'collections'
  );

  // ===== Collections State =====
  const [collections, setCollections] = useState<Collection[]>([]);
  const [collectionsLoading, setCollectionsLoading] = useState(false);
  const [collectionModalVisible, setCollectionModalVisible] = useState(false);
  const [editingCollection, setEditingCollection] = useState<Collection | null>(null);
  const [collectionPagination, setCollectionPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });
  const [collectionForm] = Form.useForm<CollectionFormValues>();
  const [collectionSubmitting, setCollectionSubmitting] = useState(false);

  // ===== Products State =====
  const [products, setProducts] = useState<Product[]>([]);
  const [productsLoading, setProductsLoading] = useState(false);
  const [productModalVisible, setProductModalVisible] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [productPagination, setProductPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });
  const [productForm] = Form.useForm<ProductFormValues>();
  const [productSubmitting, setProductSubmitting] = useState(false);

  // ============================================================
  // Collections Data
  // ============================================================

  const fetchCollections = useCallback(async () => {
    setCollectionsLoading(true);
    try {
      const response = await getCollections({
        page: collectionPagination.current,
        page_size: collectionPagination.pageSize,
      });
      if (response.success) {
        setCollections(response.data.items);
        setCollectionPagination((prev) => ({
          ...prev,
          total: response.data.total,
        }));
      }
    } catch (error) {
      message.error('加载商品集合失败');
    } finally {
      setCollectionsLoading(false);
    }
  }, [collectionPagination.current, collectionPagination.pageSize]);

  useEffect(() => {
    if (activeTab === 'collections') {
      fetchCollections();
    }
  }, [activeTab, fetchCollections]);

  // ============================================================
  // Products Data
  // ============================================================

  const fetchProducts = useCallback(async () => {
    setProductsLoading(true);
    try {
      const response = await getProducts({
        page: productPagination.current,
        page_size: productPagination.pageSize,
      });
      if (response.success) {
        setProducts(response.data.items);
        setProductPagination((prev) => ({
          ...prev,
          total: response.data.total,
        }));
      }
    } catch (error) {
      message.error('加载商品失败');
    } finally {
      setProductsLoading(false);
    }
  }, [productPagination.current, productPagination.pageSize]);

  useEffect(() => {
    if (activeTab === 'products') {
      fetchProducts();
    }
  }, [activeTab, fetchProducts]);

  // Also fetch collections for product form dropdown when products tab is active
  useEffect(() => {
    if (activeTab === 'products') {
      const load = async () => {
        try {
          const response = await getCollections({ page_size: 200 });
          if (response.success) {
            setCollections(response.data.items);
          }
        } catch {
          // non-critical
        }
      };
      load();
    }
  }, [activeTab]);

  // ============================================================
  // Collection Handlers
  // ============================================================

  const handleAddCollection = () => {
    setEditingCollection(null);
    collectionForm.resetFields();
    collectionForm.setFieldsValue({
      name: '',
      slug: '',
      description: '',
      image_url: '',
      sort_order: 0,
      is_active: true,
    });
    setCollectionModalVisible(true);
  };

  const handleEditCollection = (record: Collection) => {
    setEditingCollection(record);
    collectionForm.setFieldsValue({
      name: record.name,
      slug: record.slug,
      description: record.description,
      image_url: record.image_url,
      sort_order: record.sort_order,
      is_active: record.is_active,
    });
    setCollectionModalVisible(true);
  };

  const handleDeleteCollection = async (id: number) => {
    try {
      await deleteCollection(id);
      message.success('商品集合已删除');
      fetchCollections();
    } catch (error) {
      message.error('删除商品集合失败');
    }
  };

  const handleCollectionSubmit = async () => {
    setCollectionSubmitting(true);
    try {
      const values = await collectionForm.validateFields();
      const data: CollectionCreateRequest = { ...values };

      if (editingCollection) {
        await updateCollection(editingCollection.id, data);
        message.success('商品集合已更新');
      } else {
        await createCollection(data);
        message.success('商品集合已创建');
      }
      setCollectionModalVisible(false);
      fetchCollections();
    } catch (error: any) {
      if (error?.errorFields) return;
      message.error('操作失败');
    } finally {
      setCollectionSubmitting(false);
    }
  };

  // ============================================================
  // Product Handlers
  // ============================================================

  const handleAddProduct = () => {
    setEditingProduct(null);
    productForm.resetFields();
    productForm.setFieldsValue({
      name: '',
      slug: '',
      description: '',
      price: 0,
      currency: 'CNY',
      images: '',
      collection_id: undefined,
      stock: 0,
      is_active: true,
      sort_order: 0,
    });
    setProductModalVisible(true);
  };

  const handleEditProduct = (record: Product) => {
    setEditingProduct(record);
    productForm.setFieldsValue({
      name: record.name,
      slug: record.slug,
      description: record.description,
      price: record.price,
      currency: record.currency || 'CNY',
      images: record.images ? record.images.join(', ') : '',
      collection_id: record.collection_id,
      stock: record.stock,
      is_active: record.is_active,
      sort_order: record.sort_order,
    });
    setProductModalVisible(true);
  };

  const handleDeleteProduct = async (id: number) => {
    try {
      await deleteProduct(id);
      message.success('商品已删除');
      fetchProducts();
    } catch (error) {
      message.error('删除商品失败');
    }
  };

  const handleProductSubmit = async () => {
    setProductSubmitting(true);
    try {
      const values = await productForm.validateFields();
      const data: ProductCreateRequest = {
        ...values,
        images: values.images
          ? values.images.split(',').map((s) => s.trim()).filter(Boolean)
          : undefined,
      };

      if (editingProduct) {
        await updateProduct(editingProduct.id, data);
        message.success('商品已更新');
      } else {
        await createProduct(data);
        message.success('商品已创建');
      }
      setProductModalVisible(false);
      fetchProducts();
    } catch (error: any) {
      if (error?.errorFields) return;
      message.error('操作失败');
    } finally {
      setProductSubmitting(false);
    }
  };

  // ============================================================
  // Collection Columns
  // ============================================================

  const collectionColumns: ColumnsType<Collection> = [
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
      ellipsis: true,
    },
    {
      title: '标识键',
      dataIndex: 'slug',
      key: 'slug',
      width: 160,
      render: (slug: string) => (
        <Tag color="blue" style={{ fontFamily: 'monospace' }}>
          {slug}
        </Tag>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (desc: string) => desc || '-',
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean) =>
        isActive ? (
          <Tag color="green">启用</Tag>
        ) : (
          <Tag color="default">禁用</Tag>
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
      render: (_: unknown, record: Collection) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditCollection(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="删除此集合？"
            description="此操作不可撤销。"
            onConfirm={() => handleDeleteCollection(record.id)}
            okText="删除"
            cancelText="取消"
            okType="danger"
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
  // Product Columns
  // ============================================================

  const productColumns: ColumnsType<Product> = [
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
      width: 220,
      ellipsis: true,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 130,
      render: (price: number, record: Product) => (
        <span style={{ fontWeight: 600, color: '#cf1322' }}>
          {formatCurrency(price, record.currency || 'CNY')}
        </span>
      ),
    },
    {
      title: '商品集合',
      dataIndex: 'collection',
      key: 'collection',
      width: 150,
      render: (collection: Collection) =>
        collection ? (
          <Tag color="blue">{collection.name}</Tag>
        ) : (
          <Tag color="default">未分类</Tag>
        ),
    },
    {
      title: '库存',
      dataIndex: 'stock',
      key: 'stock',
      width: 90,
      render: (stock: number) => (
        <span style={{ color: stock === 0 ? '#ff4d4f' : 'inherit' }}>
          {stock ?? '-'}
        </span>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 90,
      render: (isActive: boolean) =>
        isActive ? (
          <Tag color="green">启用</Tag>
        ) : (
          <Tag color="default">禁用</Tag>
        ),
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
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
      render: (_: unknown, record: Product) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditProduct(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="删除此商品？"
            description="此操作不可撤销。"
            onConfirm={() => handleDeleteProduct(record.id)}
            okText="删除"
            cancelText="取消"
            okType="danger"
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
  // Tab Configuration
  // ============================================================

  const tabItems = [
    {
      key: 'collections',
      label: '商品集合',
      children: (
        <Card
          extra={
            <Space>
              <Button
                icon={<ReloadOutlined />}
                onClick={fetchCollections}
              >
                刷新
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleAddCollection}
              >
                新建集合
              </Button>
            </Space>
          }
        >
          <Table<Collection>
            columns={collectionColumns}
            dataSource={collections}
            rowKey="id"
            loading={collectionsLoading}
            scroll={{ x: 1100 }}
            pagination={{
              current: collectionPagination.current,
              pageSize: collectionPagination.pageSize,
              total: collectionPagination.total,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个集合`,
              onChange: (page, pageSize) =>
                setCollectionPagination({
                  current: page,
                  pageSize,
                  total: collectionPagination.total,
                }),
            }}
            locale={{ emptyText: '暂无商品集合' }}
          />
        </Card>
      ),
    },
    {
      key: 'products',
      label: '商品',
      children: (
        <Card
          extra={
            <Space>
              <Button icon={<ReloadOutlined />} onClick={fetchProducts}>
                刷新
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleAddProduct}
              >
                新建商品
              </Button>
            </Space>
          }
        >
          <Table<Product>
            columns={productColumns}
            dataSource={products}
            rowKey="id"
            loading={productsLoading}
            scroll={{ x: 1200 }}
            pagination={{
              current: productPagination.current,
              pageSize: productPagination.pageSize,
              total: productPagination.total,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个商品`,
              onChange: (page, pageSize) =>
                setProductPagination({
                  current: page,
                  pageSize,
                  total: productPagination.total,
                }),
            }}
            locale={{ emptyText: '暂无商品' }}
          />
        </Card>
      ),
    },
  ];

  // ============================================================
  // Render
  // ============================================================

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        商城管理
      </Title>

      <Tabs
        activeKey={activeTab}
        onChange={(key) => setActiveTab(key as 'collections' | 'products')}
        items={tabItems}
      />

      {/* Collection Create/Edit Modal */}
      <Modal
        title={editingCollection ? '编辑商品集合' : '创建商品集合'}
        open={collectionModalVisible}
        onOk={handleCollectionSubmit}
        onCancel={() => setCollectionModalVisible(false)}
        width={640}
        confirmLoading={collectionSubmitting}
        okText={editingCollection ? '更新' : '创建'}
        cancelText="取消"
        destroyOnClose
      >
        <Form
          form={collectionForm}
          layout="vertical"
          preserve={false}
        >
          <Form.Item
            label="名称"
            name="name"
            rules={[{ required: true, message: '请输入集合名称' }]}
          >
            <Input placeholder="e.g. 热门推荐" />
          </Form.Item>
          <Form.Item label="标识键 (Slug)" name="slug">
            <Input placeholder="e.g. hot-picks" />
          </Form.Item>
          <Form.Item label="描述" name="description">
            <TextArea rows={3} placeholder="简短描述此集合" />
          </Form.Item>
          <Form.Item label="图片URL" name="image_url">
            <Input placeholder="https://example.com/image.jpg" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="排序值" name="sort_order">
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="启用"
                name="is_active"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* Product Create/Edit Modal */}
      <Modal
        title={editingProduct ? '编辑商品' : '创建商品'}
        open={productModalVisible}
        onOk={handleProductSubmit}
        onCancel={() => setProductModalVisible(false)}
        width={700}
        confirmLoading={productSubmitting}
        okText={editingProduct ? '更新' : '创建'}
        cancelText="取消"
        destroyOnClose
      >
        <Form
          form={productForm}
          layout="vertical"
          preserve={false}
        >
          <Row gutter={16}>
            <Col span={16}>
              <Form.Item
                label="商品名称"
                name="name"
                rules={[{ required: true, message: '请输入商品名称' }]}
              >
                <Input placeholder="e.g. SillyMD Pro 会员" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="标识键 (Slug)"
                name="slug"
              >
                <Input placeholder="e.g. sillymd-pro" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item
            label="描述"
            name="description"
            rules={[{ required: true, message: '请输入商品描述' }]}
          >
            <TextArea rows={3} placeholder="商品详细描述" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="价格"
                name="price"
                rules={[{ required: true, message: '请输入价格' }]}
              >
                <InputNumber
                  min={0}
                  precision={2}
                  style={{ width: '100%' }}
                  addonAfter="CNY"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="所属集合" name="collection_id">
                <Select placeholder="选择集合" allowClear>
                  {collections.map((col) => (
                    <Select.Option key={col.id} value={col.id}>
                      {col.name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="库存" name="stock">
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item
            label="图片列表"
            name="images"
            tooltip="多个URL用英文逗号分隔"
          >
            <Input placeholder="https://img1.jpg, https://img2.jpg" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="排序值" name="sort_order">
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="启用"
                name="is_active"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default StoreManagement;
