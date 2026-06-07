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
  InputNumber,
  message,
  Popconfirm,
  Typography,
  Spin,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getPages, createPage, updatePage, deletePage } from '@/api/pages';
import type { Page, PageCreateRequest, PageUpdateRequest } from '@/api/pages';

const { Title } = Typography;
const { TextArea } = Input;

const PageManagement: React.FC = () => {
  const [items, setItems] = useState<Page[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [searchText, setSearchText] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [editingPage, setEditingPage] = useState<Page | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();

  const fetchItems = useCallback(async () => {
    setLoading(true);
    try {
      const result = await getPages({
        page,
        page_size: pageSize,
        search: searchText || undefined,
      });
      if (result.success) {
        setItems(result.data?.items || []);
        setTotal(result.data?.total || 0);
      }
    } catch {
      message.error('加载页面列表失败');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, searchText]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const handleAdd = () => {
    setEditingPage(null);
    form.resetFields();
    form.setFieldsValue({ status: 'draft', sort_order: 0 });
    setModalVisible(true);
  };

  const handleEdit = (record: Page) => {
    setEditingPage(record);
    form.setFieldsValue({
      slug: record.slug,
      title: record.title,
      content: record.content,
      status: record.status,
      meta_title: record.meta_title,
      meta_description: record.meta_description,
      sort_order: record.sort_order,
    });
    setModalVisible(true);
  };

  const handleDelete = async (record: Page) => {
    try {
      const result = await deletePage(record.id);
      if (result.success) {
        message.success('页面已删除');
        fetchItems();
      } else {
        message.error(result.message || '删除失败');
      }
    } catch {
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setSubmitting(true);

      if (editingPage) {
        const updateData: PageUpdateRequest = {};
        for (const key of Object.keys(values)) {
          if (values[key] !== undefined) {
            (updateData as Record<string, unknown>)[key] = values[key];
          }
        }
        const result = await updatePage(editingPage.id, updateData);
        if (result.success) {
          message.success('页面已更新');
        } else {
          message.error(result.message || '更新失败');
          return;
        }
      } else {
        const createData: PageCreateRequest = {
          slug: values.slug,
          title: values.title,
          content: values.content || '',
          status: values.status || 'draft',
          meta_title: values.meta_title,
          meta_description: values.meta_description,
          sort_order: values.sort_order || 0,
        };
        const result = await createPage(createData);
        if (result.success) {
          message.success('页面已创建');
        } else {
          message.error(result.message || '创建失败');
          return;
        }
      }

      setModalVisible(false);
      fetchItems();
    } catch {
      // Validation failed - do nothing
    } finally {
      setSubmitting(false);
    }
  };

  const columns: ColumnsType<Page> = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: 200,
      ellipsis: true,
    },
    {
      title: 'Slug',
      dataIndex: 'slug',
      key: 'slug',
      width: 150,
      render: (slug: string) => <code>/{slug}</code>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) =>
        status === 'published' ? (
          <Tag color="green">已发布</Tag>
        ) : (
          <Tag color="default">草稿</Tag>
        ),
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 80,
      align: 'center',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (val: string) => (val ? new Date(val).toLocaleString('zh-CN') : '-'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_: unknown, record: Page) => (
        <Space size="small">
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm title="确定删除此页面？" onConfirm={() => handleDelete(record)}>
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 16,
        }}
      >
        <Title level={3} style={{ margin: 0 }}>
          页面管理
        </Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchItems}>
            刷新
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新建页面
          </Button>
        </Space>
      </div>

      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={items}
          rowKey="id"
          pagination={{
            current: page,
            pageSize,
            total,
            showSizeChanger: true,
            showTotal: (t) => `共 ${t} 条`,
            onChange: (p, ps) => {
              setPage(p);
              setPageSize(ps);
            },
          }}
          scroll={{ x: 900 }}
        />
      </Spin>

      <Modal
        title={editingPage ? '编辑页面' : '新建页面'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        confirmLoading={submitting}
        width={720}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="Slug"
            name="slug"
            rules={[
              { required: true, message: '请输入 slug' },
              { pattern: /^[a-z0-9-]+$/, message: '只允许小写字母、数字和连字符' },
              { min: 2, message: '至少 2 个字符' },
              { max: 200, message: '最多 200 个字符' },
            ]}
          >
            <Input
              placeholder="my-integration-page"
              disabled={!!editingPage}
              addonBefore="/page/"
            />
          </Form.Item>

          <Form.Item
            label="标题"
            name="title"
            rules={[{ required: true, message: '请输入页面标题' }]}
          >
            <Input placeholder="页面标题" />
          </Form.Item>

          <Form.Item label="内容 (HTML)" name="content">
            <TextArea rows={10} placeholder="输入 HTML 内容..." />
          </Form.Item>

          <Form.Item label="状态" name="status">
            <Select>
              <Select.Option value="draft">草稿</Select.Option>
              <Select.Option value="published">已发布</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item label="SEO 标题" name="meta_title">
            <Input placeholder="SEO 标题（可选）" />
          </Form.Item>

          <Form.Item label="SEO 描述" name="meta_description">
            <TextArea rows={3} placeholder="SEO 描述（可选）" />
          </Form.Item>

          <Form.Item label="排序权重" name="sort_order">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PageManagement;
