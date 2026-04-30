import React, { useEffect, useState } from 'react';
import { Table, Button, Space, Modal, Form, Input, Switch, Slider, message, Popconfirm, Card, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import api from '@/api';

const SkillsManagement: React.FC = () => {
  const [skills, setSkills] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingSkill, setEditingSkill] = useState<any>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchSkills();
  }, []);

  const fetchSkills = async () => {
    setLoading(true);
    try {
      const res = await api.get('/skills/all');
      setSkills(res.data || []);
    } catch (error) {
      message.error('获取技能列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingSkill(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: any) => {
    setEditingSkill(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/skills/${id}`);
      message.success('删除成功');
      fetchSkills();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingSkill) {
        await api.put(`/skills/${editingSkill.id}`, values);
        message.success('更新成功');
      } else {
        await api.post('/skills', values);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchSkills();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const columns = [
    { title: '技能名称', dataIndex: 'name', key: 'name' },
    { title: '分类', dataIndex: 'category', key: 'category' },
    {
      title: '熟练度',
      dataIndex: 'level',
      key: 'level',
      render: (level: number) => (
        <div style={{ width: 100 }}>
          <div style={{ marginBottom: 4 }}>{level}%</div>
          <div style={{ height: 4, background: '#f0f0f0', borderRadius: 2 }}>
            <div
              style={{
                height: '100%',
                width: `${level}%`,
                background: '#1890ff',
                borderRadius: 2,
              }}
            />
          </div>
        </div>
      ),
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
        title="技能管理"
        extra={<Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>新建技能</Button>}
      >
        <Table columns={columns} dataSource={skills} rowKey="id" loading={loading} />
      </Card>

      <Modal
        title={editingSkill ? '编辑技能' : '新建技能'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="技能名称" name="name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="分类" name="category" rules={[{ required: true }]} initialValue="前端">
            <Input />
          </Form.Item>
          <Form.Item label="熟练度" name="level" rules={[{ required: true }]} initialValue={80}>
            <Slider marks={{ 0: '0%', 50: '50%', 100: '100%' }} />
          </Form.Item>
          <Form.Item label="图标" name="icon">
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

export default SkillsManagement;
