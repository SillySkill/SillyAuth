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
      message.error('加载文章列表失败');
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, filters]);

  const fetchCategories = useCallback(async () => {
    try {
      const response = await getCategories();
      if (response.success) {
        // Handle both flat array and paginated {items, total} responses
        setCategories(response.data.items || response.data);
      }
    } catch (error) {
      console.error('加载分类失败');
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
      title: '确认删除',
      content: '确定要删除此文章吗？此操作不可撤销。',
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteArticle(id);
          message.success('文章已删除');
          fetchArticles();
        } catch (error) {
          message.error('删除文章失败');
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
          message.success('文章已更新');
        }
      } else {
        const result = await createArticle(values);
        if (result.success) {
          message.success('文章已创建');
        }
      }
      setModalVisible(false);
      fetchArticles();
    } catch (error: any) {
      if (error?.errorFields) {
        // Form validation error, ignore
        return;
      }
      message.error('操作失败');
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
      title: '标题（中文）',
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
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category: Article['category']) =>
        category ? <Tag color="blue">{category.name}</Tag> : <Tag color="default">未分类</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 110,
      render: (status: string) => {
        const config: Record<string, { color: string; label: string }> = {
          published: { color: 'green', label: '已发布' },
          draft: { color: 'orange', label: '草稿' },
          archived: { color: 'default', label: '已归档' },
        };
        const cfg = config[status] || { color: 'default', label: status };
        return <Tag color={cfg.color}>{cfg.label}</Tag>;
      },
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      width: 130,
      render: (author: Article['author']) => author?.username || '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => formatDate(date),
    },
    {
      title: '操作',
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
            编辑
          </Button>
          <Popconfirm
            title="删除此文章？"
            description="此操作不可撤销。"
            onConfirm={() => handleDelete(record.id)}
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
        内容管理
      </Title>

      {/* Search/Filter Bar */}
      <Card style={{ marginBottom: 16 }}>
        <Form layout="inline" onFinish={handleSearch}>
          <Form.Item name="title">
            <Input placeholder="搜索标题..." prefix={<SearchOutlined />} style={{ width: 220 }} allowClear />
          </Form.Item>
          <Form.Item name="category_id">
            <Select placeholder="分类" style={{ width: 180 }} allowClear>
              {categories.map((cat) => (
                <Option key={cat.id} value={cat.id}>
                  {cat.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="status">
            <Select placeholder="状态" style={{ width: 140 }} allowClear>
              <Option value="published">已发布</Option>
              <Option value="draft">草稿</Option>
              <Option value="archived">已归档</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
                搜索
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => {
                  setFilters({});
                  setPagination({ current: 1, pageSize: 10, total: 0 });
                }}
              >
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      {/* Table */}
      <Card
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            创建文章
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
            showTotal: (total) => `共 ${total} 篇文章`,
            onChange: (page, pageSize) => handleTableChange(page, pageSize),
          }}
          locale={{ emptyText: '暂无文章' }}
        />
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        title={editingArticle ? '编辑文章' : '创建文章'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={800}
        confirmLoading={submitting}
        okText={editingArticle ? '更新' : '创建'}
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            label="标题（中文）"
            name="title"
            rules={[{ required: true, message: '请输入中文标题' }]}
          >
            <Input placeholder="请输入中文标题" />
          </Form.Item>

          <Form.Item
            label="内容（中文）"
            name="content"
            rules={[{ required: true, message: '请输入中文内容' }]}
          >
            <TextArea rows={6} placeholder="请输入中文内容" showCount maxLength={50000} />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="分类" name="category_id">
                <Select placeholder="选择分类" allowClear>
                  {categories.map((cat) => (
                    <Option key={cat.id} value={cat.id}>
                      {cat.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="状态" name="status" rules={[{ required: true }]}>
                <Select>
                  <Option value="published">已发布</Option>
                  <Option value="draft">草稿</Option>
                  <Option value="archived">已归档</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item label="摘要" name="excerpt">
            <TextArea rows={2} placeholder="简短描述" maxLength={300} />
          </Form.Item>

          <Form.Item label="标签" name="tags">
            <Select mode="tags" placeholder="输入标签后按回车" style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label="封面图片URL" name="cover_image">
            <Input placeholder="https://example.com/image.jpg" />
          </Form.Item>

          <Form.Item label="推荐" name="is_featured" valuePropName="checked">
            <Select>
              <Option value={true}>是</Option>
              <Option value={false}>否</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ContentManagement;
