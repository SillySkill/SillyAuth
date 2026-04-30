import React, { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  Tag,
  message,
  Popconfirm,
  Card,
  Row,
  Col,
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SendOutlined } from '@ant-design/icons';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import {
  getContents,
  createContent,
  updateContent,
  deleteContent,
  publishContent,
} from '@/api/content';
import { formatDate } from '@/utils';

const { Option } = Select;
const { TextArea } = Input;

const ContentManagement: React.FC = () => {
  const [contents, setContents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingContent, setEditingContent] = useState<any>(null);
  const [pagination, setPagination] = useState({ page: 1, limit: 10, total: 0 });
  const [form] = Form.useForm();

  useEffect(() => {
    fetchContents();
  }, [pagination.page, pagination.limit]);

  const fetchContents = async () => {
    setLoading(true);
    try {
      const res = await getContents({
        page: pagination.page,
        limit: pagination.limit,
      });
      setContents(res.data || []);
      setPagination((prev) => ({
        ...prev,
        total: res.meta?.total || 0,
      }));
    } catch (error) {
      message.error('获取内容列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingContent(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: any) => {
    setEditingContent(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteContent(id);
      message.success('删除成功');
      fetchContents();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handlePublish = async (id: string) => {
    try {
      await publishContent(id);
      message.success('发布成功');
      fetchContents();
    } catch (error) {
      message.error('发布失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingContent) {
        await updateContent(editingContent.id, values);
        message.success('更新成功');
      } else {
        await createContent(values);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchContents();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: 200,
    },
    {
      title: '键',
      dataIndex: 'key',
      key: 'key',
      width: 150,
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => {
        const colorMap: Record<string, string> = {
          PAGE: 'blue',
          SECTION: 'green',
          COMPONENT: 'purple',
        };
        return <Tag color={colorMap[type]}>{type}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const colorMap: Record<string, string> = {
          PUBLISHED: 'green',
          DRAFT: 'orange',
          ARCHIVED: 'red',
        };
        return <Tag color={colorMap[status]}>{status}</Tag>;
      },
    },
    {
      title: '语言',
      dataIndex: 'language',
      key: 'language',
      width: 80,
    },
    {
      title: '更新时间',
      dataIndex: 'updatedAt',
      key: 'updatedAt',
      width: 180,
      render: (date: string) => formatDate(date),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right' as const,
      render: (_: any, record: any) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          {record.status !== 'PUBLISHED' && (
            <Button
              type="link"
              icon={<SendOutlined />}
              onClick={() => handlePublish(record.id)}
            >
              发布
            </Button>
          )}
          <Popconfirm
            title="确定要删除吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
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
      <Card
        title="内容管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新建内容
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={contents}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            current: pagination.page,
            pageSize: pagination.limit,
            total: pagination.total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, limit) =>
              setPagination((prev) => ({ ...prev, page, limit: limit || 10 })),
          }}
        />
      </Card>

      <Modal
        title={editingContent ? '编辑内容' : '新建内容'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={1000}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="内容键"
                name="key"
                rules={[{ required: true, message: '请输入内容键' }]}
              >
                <Input placeholder="如: home, about 等" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="类型"
                name="type"
                rules={[{ required: true, message: '请选择类型' }]}
              >
                <Select placeholder="请选择类型">
                  <Option value="PAGE">页面</Option>
                  <Option value="SECTION">区块</Option>
                  <Option value="COMPONENT">组件</Option>
                  <Option value="TEXT">文本</Option>
                  <Option value="HTML">HTML</Option>
                  <Option value="MARKDOWN">Markdown</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="标题"
            name="title"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder="请输入标题" />
          </Form.Item>

          <Form.Item label="内容" name="content">
            <ReactQuill
              theme="snow"
              placeholder="请输入内容..."
              style={{ minHeight: 300 }}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="语言" name="language" initialValue="zh">
                <Select>
                  <Option value="zh">中文</Option>
                  <Option value="en">English</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="状态" name="status" initialValue="DRAFT">
                <Select>
                  <Option value="DRAFT">草稿</Option>
                  <Option value="PUBLISHED">已发布</Option>
                  <Option value="ARCHIVED">归档</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item label="元数据 (JSON)" name="metadata">
            <TextArea rows={4} placeholder='{"key": "value"}' />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ContentManagement;
