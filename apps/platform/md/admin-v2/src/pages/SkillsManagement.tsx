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
    { label: '初级', value: 'beginner' },
    { label: '中级', value: 'intermediate' },
    { label: '高级', value: 'advanced' },
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
      message.error('加载技能失败');
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
      message.success(`技能${checked ? '已启用' : '已禁用'}`);
      fetchSkills();
    } catch (error) {
      message.error('更新状态失败');
    }
  };

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除此技能吗？此操作不可撤销。',
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteSkill(id);
          message.success('技能删除成功');
          fetchSkills();
        } catch (error) {
          message.error('删除技能失败');
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
        message.success('技能更新成功');
      } else {
        await createSkill(values);
        message.success('技能创建成功');
      }
      setModalVisible(false);
      fetchSkills();
    } catch (error: unknown) {
      if (error && typeof error === 'object' && 'errorFields' in error) return;
      message.error('操作失败');
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
      title: '名称',
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
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 130,
      render: (category: string) =>
        category ? <Tag color="purple">{category}</Tag> : <Tag color="default">-</Tag>,
    },
    {
      title: '难度',
      dataIndex: 'difficulty_level',
      key: 'difficulty_level',
      width: 110,
      render: (level: string) => {
        const config: Record<string, { color: string; label: string }> = {
          beginner: { color: 'green', label: '初级' },
          intermediate: { color: 'orange', label: '中级' },
          advanced: { color: 'red', label: '高级' },
        };
        const cfg = config[level] || { color: 'default', label: level };
        return <Tag color={cfg.color}>{cfg.label}</Tag>;
      },
    },
    {
      title: '排序',
      dataIndex: 'sort_order',
      key: 'sort_order',
      width: 100,
    },
    {
      title: '状态',
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
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => formatDate(date),
    },
    {
      title: '操作',
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
            编辑
          </Button>
          <Popconfirm
            title="删除此技能？"
            onConfirm={() => handleDelete(record.id)}
            okText="删除"
            cancelText="取消"
            okType="danger"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        技能管理
      </Title>

      <Card style={{ marginBottom: 16 }}>
        <Form layout="inline" onFinish={handleSearch}>
          <Form.Item name="search">
            <Input placeholder="按名称搜索..." prefix={<SearchOutlined />} style={{ width: 220 }} allowClear />
          </Form.Item>
          <Form.Item name="difficulty_level">
            <Select placeholder="难度" style={{ width: 160 }} allowClear>
              {difficultyOptions.map((opt) => (
                <Option key={opt.value} value={opt.value}>{opt.label}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
                搜索
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => {
                  setFilters({});
                  setPagination({ current: 1, pageSize: 10, total: 0 });
                }}
              >
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Card
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            创建技能
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
            showTotal: (total) => `共 ${total} 个技能`,
            onChange: (page, pageSize) => handleTableChange(page, pageSize),
          }}
          locale={{ emptyText: '暂无技能' }}
        />
      </Card>

      <Modal
        title={editingSkill ? '编辑技能' : '创建技能'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={640}
        confirmLoading={submitting}
        okText={editingSkill ? '更新' : '创建'}
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            label="名称"
            name="name"
            rules={[{ required: true, message: '请输入技能名称' }]}
          >
            <Input placeholder="例如：React、Python、Docker" />
          </Form.Item>

          <Form.Item
            label="描述"
            name="description"
            rules={[{ required: true, message: '请输入描述' }]}
          >
            <TextArea rows={3} placeholder="简要描述该技能" showCount maxLength={500} />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="分类" name="category">
                <Input placeholder="例如：前端、后端、DevOps" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="难度级别" name="difficulty_level">
                <Select placeholder="选择级别">
                  {difficultyOptions.map((lvl) => (
                    <Option key={lvl.value} value={lvl.value}>{lvl.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="排序" name="sort_order">
                <InputNumber min={0} max={9999} style={{ width: '100%' }} placeholder="显示顺序" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="启用" name="is_active" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item label="图标" name="icon">
            <Input placeholder="Emoji 或图标类名" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default SkillsManagement;
