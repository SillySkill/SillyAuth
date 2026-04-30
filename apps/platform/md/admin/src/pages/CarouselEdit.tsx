import React, { useEffect, useState } from 'react';
import { Table, Button, Space, Modal, Form, Input, Select, Switch, message, Popconfirm, Card, Tag, Image } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { formatDate } from '@/utils';
import api from '@/api';

const { Option } = Select;

const CarouselEdit: React.FC = () => {
  const [carousels, setCarousels] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingCarousel, setEditingCarousel] = useState<any>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchCarousels();
  }, []);

  const fetchCarousels = async () => {
    setLoading(true);
    try {
      const res = await api.get('/carousel');
      setCarousels(res.data || []);
    } catch (error) {
      message.error('获取轮播图列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingCarousel(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: any) => {
    setEditingCarousel(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/carousel/${id}`);
      message.success('删除成功');
      fetchCarousels();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingCarousel) {
        await api.put(`/carousel/${editingCarousel.id}`, values);
        message.success('更新成功');
      } else {
        await api.post('/carousel', values);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchCarousels();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const columns = [
    { title: '标题', dataIndex: 'title', key: 'title' },
    {
      title: '媒体',
      dataIndex: 'mediaUrl',
      key: 'mediaUrl',
      render: (url: string) => <Image src={url} width={100} height={60} />,
    },
    {
      title: '类型',
      dataIndex: 'mediaType',
      key: 'mediaType',
      render: (type: string) => <Tag>{type}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'isActive',
      key: 'isActive',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>{isActive ? '启用' : '禁用'}</Tag>
      ),
    },
    { title: '排序', dataIndex: 'order', key: 'order' },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
          <Popconfirm title="确定删除?" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card
        title="轮播图管理"
        extra={<Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>新建轮播图</Button>}
      >
        <Table columns={columns} dataSource={carousels} rowKey="id" loading={loading} />
      </Card>

      <Modal
        title={editingCarousel ? '编辑轮播图' : '新建轮播图'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="标题" name="title" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="描述" name="description">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item label="媒体类型" name="mediaType" rules={[{ required: true }]} initialValue="IMAGE">
            <Select>
              <Option value="IMAGE">图片</Option>
              <Option value="VIDEO">视频</Option>
            </Select>
          </Form.Item>
          <Form.Item label="媒体URL" name="mediaUrl" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="链接URL" name="linkUrl">
            <Input />
          </Form.Item>
          <Form.Item label="链接标题" name="linkTitle">
            <Input />
          </Form.Item>
          <Form.Item label="排序" name="order" initialValue={0}>
            <Input type="number" />
          </Form.Item>
          <Form.Item label="是否启用" name="isActive" valuePropName="checked" initialValue={true}>
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default CarouselEdit;
