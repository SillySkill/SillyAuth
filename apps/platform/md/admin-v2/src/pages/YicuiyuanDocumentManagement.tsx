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
  Switch,
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
import { getDocuments, createDocument, updateDocument, deleteDocument } from '@/api/yicuiyuan';
import type { YicuiyuanDocument, YicuiyuanDocumentCreateRequest, YicuiyuanDocumentUpdateRequest } from '@/api/yicuiyuan';

const { Title } = Typography;
const { TextArea } = Input;

const CATEGORY_OPTIONS = [
  { value: 'overview', label: '小区概况' },
  { value: 'notice', label: '通知公告' },
  { value: 'finance', label: '财务公开' },
  { value: 'maintenance_fund', label: '维修基金' },
  { value: 'contract', label: '合同公示' },
  { value: 'rules', label: '规章制度' },
  { value: 'policy', label: '政策法规' },
  { value: 'minutes', label: '会议纪要' },
  { value: 'members', label: '业主信息' },
];

const CATEGORY_COLORS: Record<string, string> = {
  overview: 'blue',
  notice: 'red',
  finance: 'green',
  maintenance_fund: 'orange',
  contract: 'purple',
  rules: 'cyan',
  policy: 'geekblue',
  minutes: 'gold',
  members: 'magenta',
};

const YicuiyuanDocumentManagement: React.FC = () => {
  const [items, setItems] = useState<YicuiyuanDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [searchText, setSearchText] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<YicuiyuanDocument | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();

  const fetchItems = useCallback(async () => {
    setLoading(true);
    try {
      const result = await getDocuments({
        page,
        page_size: pageSize,
        search: searchText || undefined,
      });
      if (result.success) {
        setItems(result.data?.items || []);
        setTotal(result.data?.total || 0);
      }
    } catch {
      message.error('加载文档列表失败');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, searchText]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const handleAdd = () => {
    setEditingItem(null);
    form.resetFields();
    form.setFieldsValue({ category: 'notice', sort_order: 0, is_published: true });
    setModalVisible(true);
  };

  const handleEdit = (record: YicuiyuanDocument) => {
    setEditingItem(record);
    form.setFieldsValue({
      category: record.category,
      title: record.title,
      summary: record.summary,
      content: record.content,
      file_url: record.file_url,
      sort_order: record.sort_order,
      is_published: record.is_published,
    });
    setModalVisible(true);
  };

  const handleDelete = async (record: YicuiyuanDocument) => {
    try {
      const result = await deleteDocument(record.id);
      if (result.success) {
        message.success('文档已删除');
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

      if (editingItem) {
        const updateData: YicuiyuanDocumentUpdateRequest = {};
        for (const key of Object.keys(values)) {
          if (values[key] !== undefined) {
            (updateData as Record<string, unknown>)[key] = values[key];
          }
        }
        const result = await updateDocument(editingItem.id, updateData);
        if (result.success) {
          message.success('文档已更新');
        } else {
          message.error(result.message || '更新失败');
          return;
        }
      } else {
        const createData: YicuiyuanDocumentCreateRequest = {
          category: values.category,
          title: values.title,
          summary: values.summary || '',
          content: values.content || '',
          file_url: values.file_url,
          sort_order: values.sort_order || 0,
          is_published: values.is_published,
        };
        const result = await createDocument(createData);
        if (result.success) {
          message.success('文档已创建');
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

  const columns: ColumnsType<YicuiyuanDocument> = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: 250,
      ellipsis: true,
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (cat: string) => {
        const label = CATEGORY_OPTIONS.find((o) => o.value === cat)?.label || cat;
        return <Tag color={CATEGORY_COLORS[cat] || 'default'}>{label}</Tag>;
      },
    },
    {
      title: '发布状态',
      dataIndex: 'is_published',
      key: 'is_published',
      width: 100,
      align: 'center',
      render: (val: boolean) =>
        val ? <Tag color="green">已发布</Tag> : <Tag color="red">未发布</Tag>,
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
      render: (_: unknown, record: YicuiyuanDocument) => (
        <Space size="small">
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm title="确定删除此文档？" onConfirm={() => handleDelete(record)}>
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
          文档管理
        </Title>
        <Space>
          <Input.Search
            placeholder="搜索标题..."
            allowClear
            onSearch={(value) => {
              setSearchText(value);
              setPage(1);
            }}
            style={{ width: 240 }}
          />
          <Button icon={<ReloadOutlined />} onClick={fetchItems}>
            刷新
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新建文档
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
        title={editingItem ? '编辑文档' : '新建文档'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        confirmLoading={submitting}
        width={720}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="标题"
            name="title"
            rules={[{ required: true, message: '请输入文档标题' }]}
          >
            <Input placeholder="文档标题" />
          </Form.Item>

          <Form.Item
            label="分类"
            name="category"
            rules={[{ required: true, message: '请选择分类' }]}
          >
            <Select placeholder="请选择分类">
              {CATEGORY_OPTIONS.map((opt) => (
                <Select.Option key={opt.value} value={opt.value}>
                  {opt.label}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item label="摘要" name="summary">
            <TextArea rows={3} placeholder="文档摘要（可选）" />
          </Form.Item>

          <Form.Item label="内容" name="content">
            <TextArea rows={10} placeholder="输入文档内容..." />
          </Form.Item>

          <Form.Item label="文件链接" name="file_url">
            <Input placeholder="附件文件 URL（可选）" />
          </Form.Item>

          <Form.Item label="排序权重" name="sort_order">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label="发布" name="is_published" valuePropName="checked">
            <Switch checkedChildren="已发布" unCheckedChildren="未发布" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default YicuiyuanDocumentManagement;
