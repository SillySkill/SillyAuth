import React, { useEffect, useState, useCallback } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Drawer,
  Form,
  Input,
  InputNumber,
  Select,
  DatePicker,
  message,
  Popconfirm,
  Typography,
  Spin,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  getEvents,
  createEvent,
  updateEvent,
  deleteEvent,
  getEventRegistrations,
} from '@/api/yicuiyuan';
import type {
  YicuiyuanEvent,
  YicuiyuanEventCreateRequest,
  YicuiyuanEventUpdateRequest,
  YicuiyuanEventRegistration,
} from '@/api/yicuiyuan';

const { Title } = Typography;
const { TextArea } = Input;

const STATUS_COLORS: Record<string, string> = {
  upcoming: 'blue',
  ongoing: 'green',
  completed: 'default',
  cancelled: 'red',
};

const STATUS_LABELS: Record<string, string> = {
  upcoming: '即将开始',
  ongoing: '进行中',
  completed: '已结束',
  cancelled: '已取消',
};

const YicuiyuanEventManagement: React.FC = () => {
  const [items, setItems] = useState<YicuiyuanEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [searchText, setSearchText] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<YicuiyuanEvent | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();

  // Registration drawer state
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [registrations, setRegistrations] = useState<YicuiyuanEventRegistration[]>([]);
  const [registrationsLoading, setRegistrationsLoading] = useState(false);
  const [selectedEventTitle, setSelectedEventTitle] = useState('');

  const fetchItems = useCallback(async () => {
    setLoading(true);
    try {
      const result = await getEvents({
        page,
        page_size: pageSize,
        search: searchText || undefined,
      });
      if (result.success) {
        setItems(result.data?.items || []);
        setTotal(result.data?.total || 0);
      }
    } catch {
      message.error('加载活动列表失败');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, searchText]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const handleAdd = () => {
    setEditingItem(null);
    form.resetFields();
    form.setFieldsValue({
      status: 'upcoming',
      max_participants: 100,
      sort_order: 0,
    });
    setModalVisible(true);
  };

  const handleEdit = (record: YicuiyuanEvent) => {
    setEditingItem(record);
    form.setFieldsValue({
      title: record.title,
      description: record.description,
      event_date: record.event_date ? undefined : undefined,
      _event_date_str: record.event_date,
      event_time: record.event_time,
      location: record.location,
      max_participants: record.max_participants,
      status: record.status,
      sort_order: record.sort_order,
    });
    setModalVisible(true);
  };

  const handleDelete = async (record: YicuiyuanEvent) => {
    try {
      const result = await deleteEvent(record.id);
      if (result.success) {
        message.success('活动已删除');
        fetchItems();
      } else {
        message.error(result.message || '删除失败');
      }
    } catch {
      message.error('删除失败');
    }
  };

  const handleShowRegistrations = async (record: YicuiyuanEvent) => {
    setSelectedEventTitle(record.title);
    setDrawerVisible(true);
    setRegistrationsLoading(true);
    try {
      const result = await getEventRegistrations(record.id);
      if (result.success) {
        setRegistrations(result.data || []);
      } else {
        message.error(result.message || '加载报名列表失败');
      }
    } catch {
      message.error('加载报名列表失败');
    } finally {
      setRegistrationsLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setSubmitting(true);

      const eventDate = values.event_date
        ? values.event_date.format('YYYY-MM-DD')
        : values._event_date_str || '';

      if (editingItem) {
        const updateData: YicuiyuanEventUpdateRequest = {};
        for (const key of Object.keys(values)) {
          if (values[key] !== undefined && key !== '_event_date_str') {
            (updateData as Record<string, unknown>)[key] = values[key];
          }
        }
        updateData.event_date = eventDate;
        const result = await updateEvent(editingItem.id, updateData);
        if (result.success) {
          message.success('活动已更新');
        } else {
          message.error(result.message || '更新失败');
          return;
        }
      } else {
        const createData: YicuiyuanEventCreateRequest = {
          title: values.title,
          description: values.description || '',
          event_date: eventDate,
          event_time: values.event_time || '',
          location: values.location || '',
          max_participants: values.max_participants || 100,
          status: values.status || 'upcoming',
          sort_order: values.sort_order || 0,
        };
        const result = await createEvent(createData);
        if (result.success) {
          message.success('活动已创建');
        } else {
          message.error(result.message || '创建失败');
          return;
        }
      }

      setModalVisible(false);
      fetchItems();
    } catch {
      // Validation failed - do nothing
    } finally {
      setSubmitting(false);
    }
  };

  const columns: ColumnsType<YicuiyuanEvent> = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: 250,
      ellipsis: true,
    },
    {
      title: '活动日期',
      dataIndex: 'event_date',
      key: 'event_date',
      width: 120,
      render: (val: string) => (val || '-'),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={STATUS_COLORS[status] || 'default'}>
          {STATUS_LABELS[status] || status}
        </Tag>
      ),
    },
    {
      title: '报名数',
      dataIndex: 'registration_count',
      key: 'registration_count',
      width: 80,
      align: 'center',
      render: (count: number | undefined, record: YicuiyuanEvent) => (
        <Button
          type="link"
          icon={<TeamOutlined />}
          onClick={() => handleShowRegistrations(record)}
        >
          {count ?? 0}
        </Button>
      ),
    },
    {
      title: '地点',
      dataIndex: 'location',
      key: 'location',
      width: 150,
      ellipsis: true,
      render: (val: string | undefined) => val || '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (val: string) => (val ? new Date(val).toLocaleString('zh-CN') : '-'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_: unknown, record: YicuiyuanEvent) => (
        <Space size="small">
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm title="确定删除此活动？" onConfirm={() => handleDelete(record)}>
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const registrationColumns: ColumnsType<YicuiyuanEventRegistration> = [
    {
      title: '报名人',
      dataIndex: 'registrant_name',
      key: 'registrant_name',
      width: 120,
    },
    {
      title: '联系方式',
      dataIndex: 'contact_info',
      key: 'contact_info',
      width: 160,
      render: (val: string | undefined) => val || '-',
    },
    {
      title: '参与人数',
      dataIndex: 'num_participants',
      key: 'num_participants',
      width: 100,
      align: 'center',
    },
    {
      title: '备注',
      dataIndex: 'note',
      key: 'note',
      width: 200,
      ellipsis: true,
      render: (val: string | undefined) => val || '-',
    },
    {
      title: '报名时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (val: string) => (val ? new Date(val).toLocaleString('zh-CN') : '-'),
    },
  ];

  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 16,
        }}
      >
        <Title level={3} style={{ margin: 0 }}>
          活动管理
        </Title>
        <Space>
          <Input.Search
            placeholder="搜索标题..."
            allowClear
            onSearch={(value) => {
              setSearchText(value);
              setPage(1);
            }}
            style={{ width: 240 }}
          />
          <Button icon={<ReloadOutlined />} onClick={fetchItems}>
            刷新
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新建活动
          </Button>
        </Space>
      </div>

      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={items}
          rowKey="id"
          pagination={{
            current: page,
            pageSize,
            total,
            showSizeChanger: true,
            showTotal: (t) => `共 ${t} 条`,
            onChange: (p, ps) => {
              setPage(p);
              setPageSize(ps);
            },
          }}
          scroll={{ x: 1000 }}
        />
      </Spin>

      <Modal
        title={editingItem ? '编辑活动' : '新建活动'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        confirmLoading={submitting}
        width={640}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="标题"
            name="title"
            rules={[{ required: true, message: '请输入活动标题' }]}
          >
            <Input placeholder="活动标题" />
          </Form.Item>

          <Form.Item label="描述" name="description">
            <TextArea rows={4} placeholder="活动描述（可选）" />
          </Form.Item>

          <Form.Item
            label="活动日期"
            name="event_date"
            rules={[{ required: true, message: '请选择活动日期' }]}
          >
            <DatePicker style={{ width: '100%' }} placeholder="选择日期" />
          </Form.Item>

          <Form.Item label="活动时间" name="event_time">
            <Input placeholder="例如：14:00-17:00（可选）" />
          </Form.Item>

          <Form.Item label="地点" name="location">
            <Input placeholder="活动地点（可选）" />
          </Form.Item>

          <Form.Item label="最大参与人数" name="max_participants">
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label="状态" name="status">
            <Select>
              <Select.Option value="upcoming">即将开始</Select.Option>
              <Select.Option value="ongoing">进行中</Select.Option>
              <Select.Option value="completed">已结束</Select.Option>
              <Select.Option value="cancelled">已取消</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item label="排序权重" name="sort_order">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>

      <Drawer
        title={`报名管理 - ${selectedEventTitle}`}
        placement="right"
        width={640}
        open={drawerVisible}
        onClose={() => setDrawerVisible(false)}
      >
        <Spin spinning={registrationsLoading}>
          <Table
            columns={registrationColumns}
            dataSource={registrations}
            rowKey="id"
            pagination={false}
            scroll={{ x: 600 }}
          />
        </Spin>
      </Drawer>
    </div>
  );
};

export default YicuiyuanEventManagement;
