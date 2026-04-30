import React, { useEffect, useState } from 'react';
import { Table, Button, Space, Modal, Form, Input, Switch, message, Popconfirm, Card, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { formatDate } from '@/utils';
import api from '@/api';

const NavigationEdit: React.FC = () => {
  const [navigations, setNavigations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingNav, setEditingNav] = useState<any>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchNavigations();
  }, []);

  const fetchNavigations = async () => {
    setLoading(true);
    try {
      const res = await api.get('/navigation');
      setNavigations(res.data || []);
    } catch (error) {
      message.error('获取导航列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingNav(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: any) => {
    setEditingNav(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/navigation/${id}`);
      message.success('删除成功');
      fetchNavigations();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingNav) {
        await api.put(`/navigation/${editingNav.id}`, values);
        message.success('更新成功');
      } else {
        await api.post('/navigation', values);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchNavigations();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const columns = [
    { title: '标题', dataIndex: 'title', key: 'title' },
    { title: '键', dataIndex: 'key', key: 'key' },
    { title: 'URL', dataIndex: 'url', key: 'url' },
    { title: '图标', dataIndex: 'icon', key: 'icon' },
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
        title="导航管理"
        extra={<Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>新建导航</Button>}
      >
        <Table columns={columns} dataSource={navigations} rowKey="id" loading={loading} />
      </Card>

      <Modal
        title={editingNav ? '编辑导航' : '新建导航'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="标题" name="title" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="键" name="key" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="URL" name="url" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="图标" name="icon">
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

export default NavigationEdit;
