import React, { useEffect, useState } from 'react';
import { Table, Button, Space, Modal, Form, Input, Switch, message, Popconfirm, Card, Tag, Image } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import api from '@/api';

const VendorManagement: React.FC = () => {
  const [vendors, setVendors] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingVendor, setEditingVendor] = useState<any>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchVendors();
  }, []);

  const fetchVendors = async () => {
    setLoading(true);
    try {
      const res = await api.get('/vendors');
      setVendors(res.data || []);
    } catch (error) {
      message.error('获取供应商列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingVendor(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: any) => {
    setEditingVendor(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/vendors/${id}`);
      message.success('删除成功');
      fetchVendors();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingVendor) {
        await api.put(`/vendors/${editingVendor.id}`, values);
        message.success('更新成功');
      } else {
        await api.post('/vendors', values);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchVendors();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const columns = [
    { title: '名称', dataIndex: 'name', key: 'name' },
    {
      title: 'Logo',
      dataIndex: 'logo',
      key: 'logo',
      render: (logo: string) => logo ? <Image src={logo} width={50} height={50} /> : '-',
    },
    { title: '网站', dataIndex: 'website', key: 'website' },
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
        title="供应商管理"
        extra={<Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>新建供应商</Button>}
      >
        <Table columns={columns} dataSource={vendors} rowKey="id" loading={loading} />
      </Card>

      <Modal
        title={editingVendor ? '编辑供应商' : '新建供应商'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="名称" name="name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Logo URL" name="logo">
            <Input />
          </Form.Item>
          <Form.Item label="网站" name="website">
            <Input />
          </Form.Item>
          <Form.Item label="描述" name="description">
            <Input.TextArea rows={3} />
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

export default VendorManagement;
