import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, message, Card } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import api from '@/api';

const { TextArea } = Input;

const SEOSettings: React.FC = () => {
  const [seoSettings, setSeoSettings] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingSEO, setEditingSEO] = useState<any>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchSEOSettings();
  }, []);

  const fetchSEOSettings = async () => {
    setLoading(true);
    try {
      const res = await api.get('/seo');
      setSeoSettings(res.data || []);
    } catch (error) {
      message.error('获取SEO配置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (record: any) => {
    setEditingSEO(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      await api.put(`/seo/${editingSEO.page}`, values);
      message.success('更新成功');
      setModalVisible(false);
      fetchSEOSettings();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const columns = [
    { title: '页面', dataIndex: 'page', key: 'page' },
    { title: '标题', dataIndex: 'title', key: 'title', ellipsis: true },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
    { title: '关键词', dataIndex: 'keywords', key: 'keywords', ellipsis: true },
    { title: '语言', dataIndex: 'language', key: 'language' },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
      ),
    },
  ];

  return (
    <div>
      <Card title="SEO 设置">
        <Table columns={columns} dataSource={seoSettings} rowKey="id" loading={loading} />
      </Card>

      <Modal
        title="编辑 SEO 配置"
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={700}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="页面" name="page">
            <Input disabled />
          </Form.Item>
          <Form.Item label="标题" name="title" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="描述" name="description">
            <TextArea rows={3} />
          </Form.Item>
          <Form.Item label="关键词" name="keywords">
            <Input placeholder="用逗号分隔" />
          </Form.Item>
          <Form.Item label="OG 图片" name="ogImage">
            <Input />
          </Form.Item>
          <Form.Item label="Canonical URL" name="canonical">
            <Input />
          </Form.Item>
          <Form.Item label="Robots" name="robots">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default SEOSettings;
