import React, { useEffect, useState, useCallback } from 'react';
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
  Row,
  Col,
  Typography,
  Popconfirm,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  getArticles,
  createArticle,
  updateArticle,
  deleteArticle,
  getCategories,
} from '../api/content';
import type { Article, Category } from '../types';
import { formatDate } from '../utils';

const { Option } = Select;
const { TextArea } = Input;
const { Title } = Typography;

interface ArticleFormValues {
  title: string;
  content: string;
  excerpt?: string;
  category_id?: number;
  tags?: string[];
  cover_image?: string;
  status: 'draft' | 'published' | 'archived';
  is_featured?: boolean;
}

const ContentManagement: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingArticle, setEditingArticle] = useState<Article | null>(null);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [filters, setFilters] = useState<{ title?: string; category_id?: number; status?: string }>({});
  const [form] = Form.useForm<ArticleFormValues>();
  const [submitting, setSubmitting] = useState(false);

  const fetchArticles = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getArticles({
        page: pagination.current,
        page_size: pagination.pageSize,
        ...filters,
      });
      if (response.success) {
        setArticles(response.data.items);
        setPagination((prev) => ({ ...prev, total: response.data.total }));
      }
    } catch (error) {
      message.error('Failed to load articles');
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, filters]);

  const fetchCategories = useCallback(async () => {
    try {
      const response = await getCategories();
      if (response.success) {
        setCategories(response.data);
      }
    } catch (error) {
      console.error('Failed to load categories');
    }
  }, []);

  useEffect(() => {
    fetchArticles();
    fetchCategories();
  }, [fetchArticles, fetchCategories]);

  const handleSearch = (values: { title?: string; category_id?: number; status?: string }) => {
    setFilters(values);
    setPagination((prev) => ({ ...prev, current: 1 }));
  };

  const handleAdd = () => {
    setEditingArticle(null);
    form.resetFields();
    form.setFieldsValue({ status: 'draft', is_featured: false });
    setModalVisible(true);
  };

  const handleEdit = (record: Article) => {
    setEditingArticle(record);
    form.setFieldsValue({
      title: record.title,
      content: record.content,
      excerpt: record.excerpt,
      category_id: record.category_id,
      tags: record.tags,
      cover_image: record.cover_image,
      status: record.status,
      is_featured: record.is_featured,
    });
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: 'Confirm Delete',
      content: 'Are you sure you want to delete this article? This action cannot be undone.',
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await deleteArticle(id);
          message.success('Article deleted successfully');
          fetchArticles();
        } catch (error) {
          message.error('Failed to delete article');
        }
      },
    });
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const values = await form.validateFields();
      if (editingArticle) {
        const result = await updateArticle(editingArticle.id, values);
        if (result.success) {
          message.success('Article updated successfully');
        }
      } else {
        const result = await createArticle(values);
        if (result.success) {
          message.success('Article created successfully');
        }
      }
      setModalVisible(false);
      fetchArticles();
    } catch (error: any) {
      if (error?.errorFields) {
        // Form validation error, ignore
        return;
      }
      message.error('Operation failed');
    } finally {
      setSubmitting(false);
    }
  };

  const handleTableChange = (page: number, pageSize: number) => {
    setPagination({ current: page, pageSize, total: pagination.total });
  };

  const columns: ColumnsType<Article> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
    },
    {
      title: 'Title (zh_CN)',
      dataIndex: 'title',
      key: 'title',
      width: 260,
      ellipsis: true,
      render: (title: string, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>{title}</div>
          {record.excerpt && (
            <div style={{ fontSize: 12, color: '#999', marginTop: 2 }}>{record.excerpt}</div>
          )}
        </div>
      ),
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category: Article['category']) =>
        category ? <Tag color="blue">{category.name}</Tag> : <Tag color="default">Uncategorized</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 110,
      render: (status: string) => {
        const config: Record<string, { color: string; label: string }> = {
          published: { color: 'green', label: 'Published' },
          draft: { color: 'orange', label: 'Draft' },
          archived: { color: 'default', label: 'Archived' },
        };
        const cfg = config[status] || { color: 'default', label: status };
        return <Tag color={cfg.color}>{cfg.label}</Tag>;
      },
    },
    {
      title: 'Author',
      dataIndex: 'author',
      key: 'author',
      width: 130,
      render: (author: Article['author']) => author?.username || '-',
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
      render: (_: unknown, record: Article) => (
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
            title="Delete this article?"
            description="This action cannot be undone."
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
        Content Management
      </Title>

      {/* Search/Filter Bar */}
      <Card style={{ marginBottom: 16 }}>
        <Form layout="inline" onFinish={handleSearch}>
          <Form.Item name="title">
            <Input placeholder="Search by title..." prefix={<SearchOutlined />} style={{ width: 220 }} allowClear />
          </Form.Item>
          <Form.Item name="category_id">
            <Select placeholder="Category" style={{ width: 180 }} allowClear>
              {categories.map((cat) => (
                <Option key={cat.id} value={cat.id}>
                  {cat.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="status">
            <Select placeholder="Status" style={{ width: 140 }} allowClear>
              <Option value="published">Published</Option>
              <Option value="draft">Draft</Option>
              <Option value="archived">Archived</Option>
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
            Create Article
          </Button>
        }
      >
        <Table<Article>
          columns={columns}
          dataSource={articles}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} articles`,
            onChange: (page, pageSize) => handleTableChange(page, pageSize),
          }}
          locale={{ emptyText: 'No articles found' }}
        />
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        title={editingArticle ? 'Edit Article' : 'Create Article'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={800}
        confirmLoading={submitting}
        okText={editingArticle ? 'Update' : 'Create'}
        cancelText="Cancel"
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            label="Title (zh_CN)"
            name="title"
            rules={[{ required: true, message: 'Please enter the Chinese title' }]}
          >
            <Input placeholder="Enter Chinese title" />
          </Form.Item>

          <Form.Item
            label="Content (zh_CN)"
            name="content"
            rules={[{ required: true, message: 'Please enter the Chinese content' }]}
          >
            <TextArea rows={6} placeholder="Enter Chinese content" showCount maxLength={50000} />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="Category" name="category_id">
                <Select placeholder="Select category" allowClear>
                  {categories.map((cat) => (
                    <Option key={cat.id} value={cat.id}>
                      {cat.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="Status" name="status" rules={[{ required: true }]}>
                <Select>
                  <Option value="published">Published</Option>
                  <Option value="draft">Draft</Option>
                  <Option value="archived">Archived</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item label="Excerpt" name="excerpt">
            <TextArea rows={2} placeholder="Short description" maxLength={300} />
          </Form.Item>

          <Form.Item label="Tags" name="tags">
            <Select mode="tags" placeholder="Type tag and press Enter" style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label="Cover Image URL" name="cover_image">
            <Input placeholder="https://example.com/image.jpg" />
          </Form.Item>

          <Form.Item label="Featured" name="is_featured" valuePropName="checked">
            <Select>
              <Option value={true}>Yes</Option>
              <Option value={false}>No</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ContentManagement;
