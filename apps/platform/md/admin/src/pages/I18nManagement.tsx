import React, { useEffect, useState } from 'react';
import { Table, Button, Space, Modal, Form, Input, Select, message, Card, Tag } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import api from '@/api';

const { Option } = Select;
const { TextArea } = Input;

const I18nManagement: React.FC = () => {
  const [translations, setTranslations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTranslation, setEditingTranslation] = useState<any>(null);
  const [form] = Form.useForm();
  const [language, setLanguage] = useState('zh');

  useEffect(() => {
    fetchTranslations();
  }, [language]);

  const fetchTranslations = async () => {
    setLoading(true);
    try {
      const res = await api.get('/translations', { params: { language } });
      const data = res.data || {};
      const list = Object.entries(data).map(([key, value]) => ({ key, value }));
      setTranslations(list);
    } catch (error) {
      message.error('获取翻译失败');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (record: any) => {
    setEditingTranslation(record);
    form.setFieldsValue({ key: record.key, value: record.value });
    setModalVisible(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      await api.put(`/translations/${editingTranslation.key}/${language}`, values);
      message.success('更新成功');
      setModalVisible(false);
      fetchTranslations();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const columns = [
    { title: '键', dataIndex: 'key', key: 'key', width: 300 },
    { title: '值', dataIndex: 'value', key: 'value', ellipsis: true },
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
      <Card
        title="多语言管理"
        extra={
          <Select style={{ width: 120 }} value={language} onChange={setLanguage}>
            <Option value="zh">中文</Option>
            <Option value="en">English</Option>
          </Select>
        }
      >
        <Table columns={columns} dataSource={translations} rowKey="key" loading={loading} />
      </Card>

      <Modal
        title="编辑翻译"
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="键" name="key">
            <Input disabled />
          </Form.Item>
          <Form.Item label="值" name="value" rules={[{ required: true }]}>
            <TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default I18nManagement;
