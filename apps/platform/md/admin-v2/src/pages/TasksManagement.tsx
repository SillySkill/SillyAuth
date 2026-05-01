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
  InputNumber,
  message,
  Card,
  Row,
  Col,
  Typography,
  Popconfirm,
  Tabs,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  getTaskDefinitions,
  createTaskDefinition,
  updateTaskDefinition,
  deleteTaskDefinition,
  getAchievements,
  createAchievement,
  updateAchievement,
  deleteAchievement,
} from '../api/tasks';
import type {
  TaskDefinition,
  TaskDefinitionCreateRequest,
  Achievement,
  AchievementCreateRequest,
} from '../api/tasks';
import { formatDate } from '../utils';

const { TextArea } = Input;
const { Title, Text } = Typography;

// ============================================================
// Task Definition Form Values
// ============================================================

interface TaskFormValues {
  name: string;
  description: string;
  points_reward: number;
  action_type: string;
  action_config?: string;
  is_active?: boolean;
}

// ============================================================
// Achievement Form Values
// ============================================================

interface AchievementFormValues {
  name: string;
  description: string;
  icon?: string;
  badge_image?: string;
  criteria_type: string;
  criteria_value: number;
  points_reward: number;
  is_active?: boolean;
}

// ============================================================
// Component
// ============================================================

const TasksManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'tasks' | 'achievements'>(
    'tasks'
  );

  // ===== Task Definitions State =====
  const [tasks, setTasks] = useState<TaskDefinition[]>([]);
  const [tasksLoading, setTasksLoading] = useState(false);
  const [taskModalVisible, setTaskModalVisible] = useState(false);
  const [editingTask, setEditingTask] = useState<TaskDefinition | null>(null);
  const [taskPagination, setTaskPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });
  const [taskForm] = Form.useForm<TaskFormValues>();
  const [taskSubmitting, setTaskSubmitting] = useState(false);

  // ===== Achievements State =====
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [achievementsLoading, setAchievementsLoading] = useState(false);
  const [achievementModalVisible, setAchievementModalVisible] = useState(false);
  const [editingAchievement, setEditingAchievement] =
    useState<Achievement | null>(null);
  const [achievementPagination, setAchievementPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });
  const [achievementForm] = Form.useForm<AchievementFormValues>();
  const [achievementSubmitting, setAchievementSubmitting] = useState(false);

  // ============================================================
  // Task Definitions Data
  // ============================================================

  const fetchTasks = useCallback(async () => {
    setTasksLoading(true);
    try {
      const response = await getTaskDefinitions({
        page: taskPagination.current,
        page_size: taskPagination.pageSize,
      });
      if (response.success) {
        setTasks(response.data.items);
        setTaskPagination((prev) => ({
          ...prev,
          total: response.data.total,
        }));
      }
    } catch (error) {
      message.error('加载任务定义失败');
    } finally {
      setTasksLoading(false);
    }
  }, [taskPagination.current, taskPagination.pageSize]);

  useEffect(() => {
    if (activeTab === 'tasks') {
      fetchTasks();
    }
  }, [activeTab, fetchTasks]);

  // ============================================================
  // Achievements Data
  // ============================================================

  const fetchAchievements = useCallback(async () => {
    setAchievementsLoading(true);
    try {
      const response = await getAchievements({
        page: achievementPagination.current,
        page_size: achievementPagination.pageSize,
      });
      if (response.success) {
        setAchievements(response.data.items);
        setAchievementPagination((prev) => ({
          ...prev,
          total: response.data.total,
        }));
      }
    } catch (error) {
      message.error('加载成就定义失败');
    } finally {
      setAchievementsLoading(false);
    }
  }, [achievementPagination.current, achievementPagination.pageSize]);

  useEffect(() => {
    if (activeTab === 'achievements') {
      fetchAchievements();
    }
  }, [activeTab, fetchAchievements]);

  // ============================================================
  // Task Definition Handlers
  // ============================================================

  const handleAddTask = () => {
    setEditingTask(null);
    taskForm.resetFields();
    taskForm.setFieldsValue({
      name: '',
      description: '',
      points_reward: 0,
      action_type: '',
      action_config: '{}',
      is_active: true,
    });
    setTaskModalVisible(true);
  };

  const handleEditTask = (record: TaskDefinition) => {
    setEditingTask(record);
    taskForm.setFieldsValue({
      name: record.name,
      description: record.description,
      points_reward: record.points_reward,
      action_type: record.action_type,
      action_config: record.action_config
        ? JSON.stringify(record.action_config, null, 2)
        : '{}',
      is_active: record.is_active,
    });
    setTaskModalVisible(true);
  };

  const handleDeleteTask = async (id: number) => {
    try {
      await deleteTaskDefinition(id);
      message.success('任务定义已删除');
      fetchTasks();
    } catch (error) {
      message.error('删除任务定义失败');
    }
  };

  const handleTaskSubmit = async () => {
    setTaskSubmitting(true);
    try {
      const values = await taskForm.validateFields();
      const data: TaskDefinitionCreateRequest = {
        name: values.name,
        description: values.description,
        points_reward: values.points_reward,
        action_type: values.action_type,
        action_config: values.action_config
          ? (() => {
              try {
                return JSON.parse(values.action_config);
              } catch {
                return {};
              }
            })()
          : undefined,
        is_active: values.is_active,
      };

      if (editingTask) {
        await updateTaskDefinition(editingTask.id, data);
        message.success('任务定义已更新');
      } else {
        await createTaskDefinition(data);
        message.success('任务定义已创建');
      }
      setTaskModalVisible(false);
      fetchTasks();
    } catch (error: any) {
      if (error?.errorFields) return;
      if (error instanceof SyntaxError) {
        message.error('action_config JSON 格式无效');
        return;
      }
      message.error('操作失败');
    } finally {
      setTaskSubmitting(false);
    }
  };

  // ============================================================
  // Achievement Handlers
  // ============================================================

  const handleAddAchievement = () => {
    setEditingAchievement(null);
    achievementForm.resetFields();
    achievementForm.setFieldsValue({
      name: '',
      description: '',
      icon: '',
      badge_image: '',
      criteria_type: '',
      criteria_value: 1,
      points_reward: 0,
      is_active: true,
    });
    setAchievementModalVisible(true);
  };

  const handleEditAchievement = (record: Achievement) => {
    setEditingAchievement(record);
    achievementForm.setFieldsValue({
      name: record.name,
      description: record.description,
      icon: record.icon || '',
      badge_image: record.badge_image || '',
      criteria_type: record.criteria_type,
      criteria_value: record.criteria_value,
      points_reward: record.points_reward,
      is_active: record.is_active,
    });
    setAchievementModalVisible(true);
  };

  const handleDeleteAchievement = async (id: number) => {
    try {
      await deleteAchievement(id);
      message.success('成就定义已删除');
      fetchAchievements();
    } catch (error) {
      message.error('删除成就定义失败');
    }
  };

  const handleAchievementSubmit = async () => {
    setAchievementSubmitting(true);
    try {
      const values = await achievementForm.validateFields();
      const data: AchievementCreateRequest = {
        name: values.name,
        description: values.description,
        icon: values.icon || undefined,
        badge_image: values.badge_image || undefined,
        criteria_type: values.criteria_type,
        criteria_value: values.criteria_value,
        points_reward: values.points_reward,
        is_active: values.is_active,
      };

      if (editingAchievement) {
        await updateAchievement(editingAchievement.id, data);
        message.success('成就定义已更新');
      } else {
        await createAchievement(data);
        message.success('成就定义已创建');
      }
      setAchievementModalVisible(false);
      fetchAchievements();
    } catch (error: any) {
      if (error?.errorFields) return;
      message.error('操作失败');
    } finally {
      setAchievementSubmitting(false);
    }
  };

  // ============================================================
  // Task Definition Columns
  // ============================================================

  const taskColumns: ColumnsType<TaskDefinition> = [
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
      width: 200,
      ellipsis: true,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (desc: string) => desc || '-',
    },
    {
      title: '积分奖励',
      dataIndex: 'points_reward',
      key: 'points_reward',
      width: 110,
      render: (points: number) => (
        <Tag color="gold" style={{ fontWeight: 600 }}>
          +{points} 积分
        </Tag>
      ),
    },
    {
      title: '类型',
      dataIndex: 'action_type',
      key: 'action_type',
      width: 140,
      render: (type: string) => {
        const typeLabels: Record<string, { color: string; label: string }> = {
          login: { color: 'blue', label: '登录' },
          post_article: { color: 'green', label: '发文' },
          comment: { color: 'cyan', label: '评论' },
          like: { color: 'red', label: '点赞' },
          share: { color: 'purple', label: '分享' },
          download: { color: 'orange', label: '下载' },
          purchase: { color: 'gold', label: '购买' },
          daily_visit: { color: 'geekblue', label: '每日访问' },
        };
        const cfg = typeLabels[type] || { color: 'default', label: type };
        return <Tag color={cfg.color}>{cfg.label}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 90,
      render: (isActive: boolean) =>
        isActive ? (
          <Tag color="green">启用</Tag>
        ) : (
          <Tag color="default">禁用</Tag>
        ),
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (date: string) => formatDate(date),
    },
    {
      title: '操作',
      key: 'actions',
      width: 180,
      fixed: 'right',
      render: (_: unknown, record: TaskDefinition) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditTask(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="删除此任务定义？"
            description="此操作不可撤销。"
            onConfirm={() => handleDeleteTask(record.id)}
            okText="删除"
            cancelText="取消"
            okType="danger"
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // ============================================================
  // Achievement Columns
  // ============================================================

  const achievementColumns: ColumnsType<Achievement> = [
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
      width: 200,
      ellipsis: true,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (desc: string) => desc || '-',
    },
    {
      title: '图标',
      dataIndex: 'icon',
      key: 'icon',
      width: 100,
      render: (icon: string) =>
        icon ? (
          <Text style={{ fontSize: 20 }}>{icon}</Text>
        ) : (
          <Tag color="default">无图标</Tag>
        ),
    },
    {
      title: '积分奖励',
      dataIndex: 'points_reward',
      key: 'points_reward',
      width: 110,
      render: (points: number) => (
        <Tag color="gold" style={{ fontWeight: 600 }}>
          +{points} 积分
        </Tag>
      ),
    },
    {
      title: '条件类型',
      dataIndex: 'criteria_type',
      key: 'criteria_type',
      width: 140,
      render: (type: string) => {
        const typeLabels: Record<string, { color: string; label: string }> = {
          article_count: { color: 'blue', label: '文章数量' },
          comment_count: { color: 'cyan', label: '评论数量' },
          like_count: { color: 'red', label: '点赞数量' },
          download_count: { color: 'orange', label: '下载数量' },
          purchase_count: { color: 'gold', label: '购买数量' },
          points_earned: { color: 'purple', label: '积分累计' },
          login_days: { color: 'geekblue', label: '登录天数' },
        };
        const cfg = typeLabels[type] || { color: 'default', label: type };
        return <Tag color={cfg.color}>{cfg.label}</Tag>;
      },
    },
    {
      title: '条件值',
      dataIndex: 'criteria_value',
      key: 'criteria_value',
      width: 90,
      render: (value: number) => (
        <Text strong>{value}</Text>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 90,
      render: (isActive: boolean) =>
        isActive ? (
          <Tag color="green">启用</Tag>
        ) : (
          <Tag color="default">禁用</Tag>
        ),
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (date: string) => formatDate(date),
    },
    {
      title: '操作',
      key: 'actions',
      width: 180,
      fixed: 'right',
      render: (_: unknown, record: Achievement) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditAchievement(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="删除此成就定义？"
            description="此操作不可撤销。"
            onConfirm={() => handleDeleteAchievement(record.id)}
            okText="删除"
            cancelText="取消"
            okType="danger"
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // ============================================================
  // Tab Configuration
  // ============================================================

  const tabItems = [
    {
      key: 'tasks',
      label: '每日任务',
      children: (
        <Card
          extra={
            <Space>
              <Button icon={<ReloadOutlined />} onClick={fetchTasks}>
                刷新
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleAddTask}
              >
                新建任务
              </Button>
            </Space>
          }
        >
          <Table<TaskDefinition>
            columns={taskColumns}
            dataSource={tasks}
            rowKey="id"
            loading={tasksLoading}
            scroll={{ x: 1100 }}
            pagination={{
              current: taskPagination.current,
              pageSize: taskPagination.pageSize,
              total: taskPagination.total,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个任务`,
              onChange: (page, pageSize) =>
                setTaskPagination({
                  current: page,
                  pageSize,
                  total: taskPagination.total,
                }),
            }}
            locale={{ emptyText: '暂无任务定义' }}
          />
        </Card>
      ),
    },
    {
      key: 'achievements',
      label: '成就',
      children: (
        <Card
          extra={
            <Space>
              <Button
                icon={<ReloadOutlined />}
                onClick={fetchAchievements}
              >
                刷新
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleAddAchievement}
              >
                新建成就
              </Button>
            </Space>
          }
        >
          <Table<Achievement>
            columns={achievementColumns}
            dataSource={achievements}
            rowKey="id"
            loading={achievementsLoading}
            scroll={{ x: 1250 }}
            pagination={{
              current: achievementPagination.current,
              pageSize: achievementPagination.pageSize,
              total: achievementPagination.total,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个成就`,
              onChange: (page, pageSize) =>
                setAchievementPagination({
                  current: page,
                  pageSize,
                  total: achievementPagination.total,
                }),
            }}
            locale={{ emptyText: '暂无成就定义' }}
          />
        </Card>
      ),
    },
  ];

  // ============================================================
  // Render
  // ============================================================

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        任务管理
      </Title>

      <Tabs
        activeKey={activeTab}
        onChange={(key) =>
          setActiveTab(key as 'tasks' | 'achievements')
        }
        items={tabItems}
      />

      {/* Task Definition Create/Edit Modal */}
      <Modal
        title={editingTask ? '编辑任务定义' : '创建任务定义'}
        open={taskModalVisible}
        onOk={handleTaskSubmit}
        onCancel={() => setTaskModalVisible(false)}
        width={700}
        confirmLoading={taskSubmitting}
        okText={editingTask ? '更新' : '创建'}
        cancelText="取消"
        destroyOnClose
      >
        <Form form={taskForm} layout="vertical" preserve={false}>
          <Row gutter={16}>
            <Col span={16}>
              <Form.Item
                label="任务名称"
                name="name"
                rules={[{ required: true, message: '请输入任务名称' }]}
              >
                <Input placeholder="e.g. 每日签到" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="积分奖励"
                name="points_reward"
                rules={[{ required: true, message: '请输入积分奖励' }]}
              >
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item
            label="任务描述"
            name="description"
            rules={[{ required: true, message: '请输入任务描述' }]}
          >
            <TextArea rows={2} placeholder="描述此任务的完成条件" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="动作类型"
                name="action_type"
                rules={[{ required: true, message: '请选择动作类型' }]}
              >
                <Input placeholder="e.g. login, post_article" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="启用"
                name="is_active"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item
            label="动作配置 (JSON)"
            name="action_config"
            tooltip="以 JSON 格式定义动作的附加参数"
          >
            <TextArea
              rows={5}
              placeholder='{"key": "value"}'
              style={{ fontFamily: 'monospace', fontSize: 13 }}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* Achievement Create/Edit Modal */}
      <Modal
        title={editingAchievement ? '编辑成就定义' : '创建成就定义'}
        open={achievementModalVisible}
        onOk={handleAchievementSubmit}
        onCancel={() => setAchievementModalVisible(false)}
        width={700}
        confirmLoading={achievementSubmitting}
        okText={editingAchievement ? '更新' : '创建'}
        cancelText="取消"
        destroyOnClose
      >
        <Form
          form={achievementForm}
          layout="vertical"
          preserve={false}
        >
          <Row gutter={16}>
            <Col span={16}>
              <Form.Item
                label="成就名称"
                name="name"
                rules={[{ required: true, message: '请输入成就名称' }]}
              >
                <Input placeholder="e.g. 百篇文章" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="积分奖励"
                name="points_reward"
                rules={[{ required: true, message: '请输入积分奖励' }]}
              >
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item
            label="成就描述"
            name="description"
            rules={[{ required: true, message: '请输入成就描述' }]}
          >
            <TextArea rows={2} placeholder="描述此成就的达成条件" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="条件类型"
                name="criteria_type"
                rules={[{ required: true, message: '请输入条件类型' }]}
              >
                <Input placeholder="e.g. article_count" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="条件值"
                name="criteria_value"
                rules={[{ required: true, message: '请输入条件值' }]}
              >
                <InputNumber min={1} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="启用"
                name="is_active"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="图标" name="icon">
                <Input placeholder="e.g. 🏆 或 trophy" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="徽章图片URL" name="badge_image">
                <Input placeholder="https://example.com/badge.png" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default TasksManagement;
