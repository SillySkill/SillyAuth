import React, { useEffect, useState, useCallback } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Switch,
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
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
import { getSkills, createSkill, updateSkill, deleteSkill } from '../api/skills';
import type { Skill } from '../types';
import { formatDate } from '../utils';

const { Option } = Select;
const { TextArea } = Input;
const { Title } = Typography;

interface SkillFormValues {
  name: string;
  description: string;
  category?: string;
  difficulty_level?: string;
  sort_order?: number;
  is_active?: boolean;
  icon?: string;
}

const SkillsManagement: React.FC = () => {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingSkill, setEditingSkill] = useState<Skill | null>(null);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [filters, setFilters] = useState<{ search?: string; difficulty_level?: string; is_active?: boolean }>({});
  const [form] = Form.useForm<SkillFormValues>();
  const [submitting, setSubmitting] = useState(false);

  const difficultyOptions = [
    { label: 'Beginner', value: 'beginner' },
    { label: 'Intermediate', value: 'intermediate' },
    { label: 'Advanced', value: 'advanced' },
  ];

  const fetchSkills = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {
        page: pagination.current,
        page_size: pagination.pageSize,
      };
      if (filters.search) params.search = filters.search;
      if (filters.difficulty_level) params.difficulty_level = filters.difficulty_level;

      const response = await getSkills(params as Parameters<typeof getSkills>[0]);
      if (response.success) {
        setSkills(response.data.items);
        setPagination((prev) => ({ ...prev, total: response.data.total }));
      }
    } catch (error) {
      message.error('Failed to load skills');
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, filters]);

  useEffect(() => {
    fetchSkills();
  }, [fetchSkills]);

  const handleSearch = (values: { search?: string; difficulty_level?: string }) => {
    setFilters((prev) => ({ ...prev, ...values }));
    setPagination((prev) => ({ ...prev, current: 1 }));
  };

  const handleAdd = () => {
    setEditingSkill(null);
    form.resetFields();
    form.setFieldsValue({ is_active: true, sort_order: 0, difficulty_level: 'beginner' });
    setModalVisible(true);
  };

  const handleEdit = (record: Skill) => {
    setEditingSkill(record);
    form.setFieldsValue({
      name: record.name,
      description: record.description,
      category: record.category,
      difficulty_level: record.difficulty_level,
      sort_order: record.sort_order,
      is_active: record.is_active,
      icon: record.icon,
    });
    setModalVisible(true);
  };

  const handleToggleActive = async (id: number, checked: boolean) => {
    try {
      await updateSkill(id, { is_active: checked });
      message.success(`Skill ${checked ? 'activated' : 'deactivated'}`);
      fetchSkills();
    } catch (error) {
      message.error('Failed to update status');
    }
  };

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: 'Confirm Delete',
      content: 'Are you sure you want to delete this skill? This cannot be undone.',
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await deleteSkill(id);
          message.success('Skill deleted successfully');
          fetchSkills();
        } catch (error) {
          message.error('Failed to delete skill');
        }
      },
    });
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const values = await form.validateFields();
      if (editingSkill) {
        await updateSkill(editingSkill.id, values);
        message.success('Skill updated successfully');
      } else {
        await createSkill(values);
        message.success('Skill created successfully');
      }
      setModalVisible(false);
      fetchSkills();
    } catch (error: unknown) {
      if (error && typeof error === 'object' && 'errorFields' in error) return;
      message.error('Operation failed');
    } finally {
      setSubmitting(false);
    }
  };

  const handleTableChange = (page: number, pageSize: number) => {
    setPagination({ current: page, pageSize, total: pagination.total });
  };

  const columns: ColumnsType<Skill> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 180,
      render: (name: string, record) => (
        <Space>
          {record.icon && <span>{record.icon}</span>}
          <span style={{ fontWeight: 500 }}>{name}</span>
        </Space>
      ),
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 130,
      render: (category: string) =>
        category ? <Tag color="purple">{category}</Tag> : <Tag color="default">-</Tag>,
    },
    {
      title: 'Difficulty',
      dataIndex: 'difficulty_level',
      key: 'difficulty_level',
      width: 110,
      render: (level: string) => {
        const config: Record<string, { color: string; label: string }> = {
          beginner: { color: 'green', label: 'Beginner' },
          intermediate: { color: 'orange', label: 'Intermediate' },
          advanced: { color: 'red', label: 'Advanced' },
        };
        const cfg = config[level] || { color: 'default', label: level };
        return <Tag color={cfg.color}>{cfg.label}</Tag>;
      },
    },
    {
      title: 'Sort Order',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 100,
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 90,
      render: (isActive: boolean, record: Skill) => (
        <Switch
          checked={isActive}
          size="small"
          onChange={(checked) => handleToggleActive(record.id, checked)}
        />
      ),
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => formatDate(date),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 180,
      fixed: 'right',
      render: (_: unknown, record: Skill) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Delete this skill?"
            onConfirm={() => handleDelete(record.id)}
            okText="Delete"
            cancelText="Cancel"
            okType="danger"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        Skills Management
      </Title>

      <Card style={{ marginBottom: 16 }}>
        <Form layout="inline" onFinish={handleSearch}>
          <Form.Item name="search">
            <Input placeholder="Search by name..." prefix={<SearchOutlined />} style={{ width: 220 }} allowClear />
          </Form.Item>
          <Form.Item name="difficulty_level">
            <Select placeholder="Difficulty" style={{ width: 160 }} allowClear>
              {difficultyOptions.map((opt) => (
                <Option key={opt.value} value={opt.value}>{opt.label}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
                Search
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => {
                  setFilters({});
                  setPagination({ current: 1, pageSize: 10, total: 0 });
                }}
              >
                Reset
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Card
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            Create Skill
          </Button>
        }
      >
        <Table<Skill>
          columns={columns}
          dataSource={skills}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1100 }}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} skills`,
            onChange: (page, pageSize) => handleTableChange(page, pageSize),
          }}
          locale={{ emptyText: 'No skills found' }}
        />
      </Card>

      <Modal
        title={editingSkill ? 'Edit Skill' : 'Create Skill'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={640}
        confirmLoading={submitting}
        okText={editingSkill ? 'Update' : 'Create'}
        cancelText="Cancel"
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            label="Name"
            name="name"
            rules={[{ required: true, message: 'Please enter the skill name' }]}
          >
            <Input placeholder="e.g. React, Python, Docker" />
          </Form.Item>

          <Form.Item
            label="Description"
            name="description"
            rules={[{ required: true, message: 'Please enter a description' }]}
          >
            <TextArea rows={3} placeholder="Brief description of this skill" showCount maxLength={500} />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="Category" name="category">
                <Input placeholder="e.g. Frontend, Backend, DevOps" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="Difficulty Level" name="difficulty_level">
                <Select placeholder="Select level">
                  {difficultyOptions.map((lvl) => (
                    <Option key={lvl.value} value={lvl.value}>{lvl.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="Sort Order" name="sort_order">
                <InputNumber min={0} max={9999} style={{ width: '100%' }} placeholder="Display order" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="Active" name="is_active" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item label="Icon" name="icon">
            <Input placeholder="Emoji or icon class name" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default SkillsManagement;
