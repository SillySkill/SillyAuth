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
  Typography,
  Popconfirm,
  Drawer,
  Descriptions,
  Divider,
  List,
  Spin,
  Empty,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  ShoppingCartOutlined,
  GiftOutlined,
  HistoryOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getUsers, getUser, updateUser } from '../api/users';
import type { User } from '../types';
import { formatDate, formatCurrency } from '../utils';

const { Option } = Select;
const { Title } = Typography;

interface UserFormValues {
  username: string;
  email: string;
  role: string;
  is_active: boolean;
}

interface UserDrawerData {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  avatar?: string;
  created_at: string;
  updated_at: string;
  orders?: Array<{
    id: number;
    product_name: string;
    amount: number;
    status: string;
    created_at: string;
  }>;
  points?: Array<{
    id: number;
    points: number;
    type: string;
    description: string;
    created_at: string;
  }>;
  activities?: Array<{
    id: number;
    action: string;
    detail: string;
    created_at: string;
  }>;
}

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [filters, setFilters] = useState<{ search?: string; role?: string }>({});
  const [form] = Form.useForm<UserFormValues>();
  const [submitting, setSubmitting] = useState(false);

  // Drawer state for user detail view
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [drawerUser, setDrawerUser] = useState<UserDrawerData | null>(null);
  const [drawerLoading, setDrawerLoading] = useState(false);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {
        page: pagination.current,
        page_size: pagination.pageSize,
      };
      if (filters.search) params.search = filters.search;
      if (filters.role) params.role = filters.role;

      const response = await getUsers(params as Parameters<typeof getUsers>[0]);
      if (response.success) {
        setUsers(response.data.items);
        setPagination((prev) => ({ ...prev, total: response.data.total }));
      }
    } catch (error) {
      message.error('加载用户列表失败');
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, filters]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleSearch = (values: { search?: string; role?: string }) => {
    setFilters((prev) => ({ ...prev, ...values }));
    setPagination((prev) => ({ ...prev, current: 1 }));
  };

  const handleEdit = (record: User) => {
    setEditingUser(record);
    form.setFieldsValue({
      username: record.username,
      email: record.email,
      role: record.role,
      is_active: record.is_active,
    });
    setModalVisible(true);
  };

  const handleViewDetail = async (record: User) => {
    setDrawerVisible(true);
    setDrawerLoading(true);
    try {
      const response = await getUser(record.id);
      if (response.success) {
        setDrawerUser(response.data as unknown as UserDrawerData);
      }
    } catch (error) {
      message.error('加载用户详情失败');
    } finally {
      setDrawerLoading(false);
    }
  };

  const handleToggleActive = async (id: number, checked: boolean) => {
    try {
      await updateUser(id, { is_active: checked });
      message.success(`用户${checked ? '已启用' : '已禁用'}`);
      fetchUsers();
    } catch (error) {
      message.error('更新用户状态失败');
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const values = await form.validateFields();
      if (editingUser) {
        await updateUser(editingUser.id, values);
        message.success('用户更新成功');
      }
      setModalVisible(false);
      fetchUsers();
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

  const roleLabelMap: Record<string, string> = {
    admin: '管理员',
    creator: '创作者',
    user: '用户',
    editor: '编辑',
  };

  const roleColorMap: Record<string, string> = {
    admin: 'red',
    creator: 'blue',
    user: 'green',
    editor: 'orange',
  };

  const columns: ColumnsType<User> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 150,
      render: (username: string) => <span style={{ fontWeight: 500 }}>{username}</span>,
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 220,
      ellipsis: true,
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      width: 110,
      render: (role: string) => (
        <Tag color={roleColorMap[role] || 'default'}>
          {roleLabelMap[role] || role}
        </Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (isActive: boolean, record: User) => (
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
      width: 170,
      render: (date: string) => formatDate(date),
    },
    {
      title: '操作',
      key: 'actions',
      width: 220,
      fixed: 'right',
      render: (_: unknown, record: User) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
        </Space>
      ),
    },
  ];

  const statusColorMap: Record<string, string> = {
    paid: 'green',
    completed: 'blue',
    pending: 'orange',
    cancelled: 'red',
    refunded: 'default',
  };

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        用户管理
      </Title>

      <Card style={{ marginBottom: 16 }}>
        <Form layout="inline" onFinish={handleSearch}>
          <Form.Item name="search">
            <Input
              placeholder="搜索用户名/邮箱..."
              prefix={<SearchOutlined />}
              style={{ width: 260 }}
              allowClear
            />
          </Form.Item>
          <Form.Item name="role">
            <Select placeholder="角色" style={{ width: 140 }} allowClear>
              <Option value="admin">管理员</Option>
              <Option value="creator">创作者</Option>
              <Option value="user">用户</Option>
              <Option value="editor">编辑</Option>
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

      <Card>
        <Table<User>
          columns={columns}
          dataSource={users}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1100 }}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 位用户`,
            onChange: (page, pageSize) => handleTableChange(page, pageSize),
          }}
          locale={{ emptyText: '暂无用户' }}
        />
      </Card>

      {/* Edit User Modal */}
      <Modal
        title="编辑用户"
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={520}
        confirmLoading={submitting}
        okText="更新"
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            label="用户名"
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '至少 3 个字符' },
            ]}
          >
            <Input placeholder="用户名" />
          </Form.Item>

          <Form.Item
            label="邮箱"
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '邮箱格式无效' },
            ]}
          >
            <Input placeholder="请输入邮箱" />
          </Form.Item>

          <Form.Item
            label="角色"
            name="role"
            rules={[{ required: true, message: '请选择角色' }]}
          >
            <Select placeholder="请选择角色">
              <Option value="admin">管理员</Option>
              <Option value="creator">创作者</Option>
              <Option value="user">用户</Option>
              <Option value="editor">编辑</Option>
            </Select>
          </Form.Item>

          <Form.Item label="启用" name="is_active" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>

      {/* User Detail Drawer */}
      <Drawer
        title={drawerUser ? `用户详情: ${drawerUser.username}` : '用户详情'}
        placement="right"
        width={600}
        onClose={() => {
          setDrawerVisible(false);
          setDrawerUser(null);
        }}
        open={drawerVisible}
      >
        {drawerLoading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}>
            <Spin size="large" />
          </div>
        ) : drawerUser ? (
          <>
            {/* Profile Info */}
            <Descriptions title="基本信息" column={2} bordered size="small">
              <Descriptions.Item label="用户名">{drawerUser.username}</Descriptions.Item>
              <Descriptions.Item label="邮箱">{drawerUser.email}</Descriptions.Item>
              <Descriptions.Item label="角色">
                <Tag color={roleColorMap[drawerUser.role]}>
                  {roleLabelMap[drawerUser.role] || drawerUser.role}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={drawerUser.is_active ? 'green' : 'red'}>
                  {drawerUser.is_active ? '启用' : '禁用'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">{formatDate(drawerUser.created_at)}</Descriptions.Item>
              <Descriptions.Item label="更新时间">{formatDate(drawerUser.updated_at)}</Descriptions.Item>
            </Descriptions>

            <Divider />

            {/* Order History */}
            <Title level={5}>
              <ShoppingCartOutlined /> 订单历史
            </Title>
            {drawerUser.orders && drawerUser.orders.length > 0 ? (
              <List
                size="small"
                dataSource={drawerUser.orders}
                renderItem={(order) => (
                  <List.Item
                    extra={
                      <Tag color={statusColorMap[order.status] || 'default'}>{order.status}</Tag>
                    }
                  >
                    <List.Item.Meta
                      title={order.product_name}
                      description={formatDate(order.created_at)}
                    />
                    <div>{formatCurrency(order.amount)}</div>
                  </List.Item>
                )}
              />
            ) : (
              <Empty description="暂无订单" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            )}

            <Divider />

            {/* Points History */}
            <Title level={5}>
              <GiftOutlined /> 积分记录
            </Title>
            {drawerUser.points && drawerUser.points.length > 0 ? (
              <List
                size="small"
                dataSource={drawerUser.points}
                renderItem={(point) => (
                  <List.Item>
                    <List.Item.Meta
                      title={`${point.points > 0 ? '+' : ''}${point.points} 积分`}
                      description={point.description}
                    />
                    <div style={{ fontSize: 12, color: '#999' }}>{formatDate(point.created_at)}</div>
                  </List.Item>
                )}
              />
            ) : (
              <Empty description="暂无积分记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            )}

            <Divider />

            {/* Activity Log */}
            <Title level={5}>
              <HistoryOutlined /> 操作日志
            </Title>
            {drawerUser.activities && drawerUser.activities.length > 0 ? (
              <List
                size="small"
                dataSource={drawerUser.activities}
                renderItem={(activity) => (
                  <List.Item>
                    <List.Item.Meta
                      title={<Tag>{activity.action}</Tag>}
                      description={activity.detail}
                    />
                    <div style={{ fontSize: 12, color: '#999' }}>{formatDate(activity.created_at)}</div>
                  </List.Item>
                )}
              />
            ) : (
              <Empty description="暂无操作日志" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            )}
          </>
        ) : (
          <Empty description="暂无用户数据" />
        )}
      </Drawer>
    </div>
  );
};

export default UserManagement;
