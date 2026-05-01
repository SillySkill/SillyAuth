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
  message,
  Card,
  Row,
  Col,
  Typography,
  Popconfirm,
  Divider,
  List,
  InputNumber,
  Empty,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  LikeOutlined,
  BookOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  getTutorials,
  createTutorial,
  updateTutorial,
  deleteTutorial,
  getChapters,
  createChapter,
  updateChapter,
  deleteChapter,
} from '../api/tutorials';
import type { Tutorial } from '../types';
import type { TutorialChapter } from '../api/tutorials';
import { formatDate } from '../utils';

const { Option } = Select;
const { TextArea } = Input;
const { Title } = Typography;

interface TutorialFormValues {
  title: string;
  description: string;
  content: string;
  skill_id?: number;
  difficulty_level?: string;
  video_url?: string;
  cover_image?: string;
  status?: string;
  sort_order?: number;
}

interface ChapterFormValues {
  title: string;
  content: string;
  order: number;
  video_url?: string;
  duration?: number;
}

const difficultyOptions = [
  { label: '初级', value: 'beginner', color: 'green' },
  { label: '中级', value: 'intermediate', color: 'orange' },
  { label: '高级', value: 'advanced', color: 'red' },
];

const TutorialManagement: React.FC = () => {
  const [tutorials, setTutorials] = useState<Tutorial[]>([]);
  const [loading, setLoading] = useState(false);

  // Main tutorial modal
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTutorial, setEditingTutorial] = useState<Tutorial | null>(null);
  const [form] = Form.useForm<TutorialFormValues>();
  const [submitting, setSubmitting] = useState(false);

  // Chapter management
  const [chaptersModalVisible, setChaptersModalVisible] = useState(false);
  const [selectedTutorialId, setSelectedTutorialId] = useState<number | null>(null);
  const [chapters, setChapters] = useState<TutorialChapter[]>([]);
  const [chaptersLoading, setChaptersLoading] = useState(false);

  // Chapter edit modal
  const [chapterModalVisible, setChapterModalVisible] = useState(false);
  const [editingChapter, setEditingChapter] = useState<TutorialChapter | null>(null);
  const [chapterForm] = Form.useForm<ChapterFormValues>();
  const [chapterSubmitting, setChapterSubmitting] = useState(false);

  // Pagination and filters
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [filters, setFilters] = useState<{ search?: string; difficulty_level?: string; status?: string }>({});

  const fetchTutorials = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {
        page: pagination.current,
        page_size: pagination.pageSize,
      };
      if (filters.search) params.search = filters.search;
      if (filters.difficulty_level) params.difficulty_level = filters.difficulty_level;
      if (filters.status) params.status = filters.status;

      const response = await getTutorials(params as Parameters<typeof getTutorials>[0]);
      if (response.success) {
        setTutorials(response.data.items);
        setPagination((prev) => ({ ...prev, total: response.data.total }));
      }
    } catch (error) {
      message.error('加载教程失败');
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, filters]);

  useEffect(() => {
    fetchTutorials();
  }, [fetchTutorials]);

  // ---- Main Tutorial CRUD ----

  const handleSearch = (values: { search?: string; difficulty_level?: string; status?: string }) => {
    setFilters((prev) => ({ ...prev, ...values }));
    setPagination((prev) => ({ ...prev, current: 1 }));
  };

  const handleAdd = () => {
    setEditingTutorial(null);
    form.resetFields();
    form.setFieldsValue({ status: 'draft', difficulty_level: 'beginner', sort_order: 0 });
    setModalVisible(true);
  };

  const handleEdit = (record: Tutorial) => {
    setEditingTutorial(record);
    form.setFieldsValue({
      title: record.title,
      description: record.description,
      content: record.content,
      skill_id: record.skill_id,
      difficulty_level: record.difficulty_level,
      video_url: record.video_url,
      cover_image: record.cover_image,
      status: record.status,
      sort_order: record.sort_order,
    });
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除此教程吗？所有章节也将被删除。',
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteTutorial(id);
          message.success('教程已删除');
          fetchTutorials();
        } catch (error) {
          message.error('删除教程失败');
        }
      },
    });
  };

  const handleToggleFeatured = async (id: number, status: string) => {
    try {
      const newStatus = status === 'published' ? 'draft' : 'published';
      await updateTutorial(id, { status: newStatus });
      message.success(`教程${newStatus === 'published' ? '已发布' : '已取消发布'}`);
      fetchTutorials();
    } catch (error) {
      message.error('更新教程失败');
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const values = await form.validateFields();
      if (editingTutorial) {
        await updateTutorial(editingTutorial.id, values);
        message.success('教程更新成功');
      } else {
        await createTutorial(values);
        message.success('教程创建成功');
      }
      setModalVisible(false);
      fetchTutorials();
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

  // ---- Chapter Management ----

  const openChapterManager = async (tutorialId: number) => {
    setSelectedTutorialId(tutorialId);
    setChaptersModalVisible(true);
    setChaptersLoading(true);
    try {
      const response = await getChapters(tutorialId);
      if (response.success) {
        setChapters(response.data);
      }
    } catch (error) {
      message.error('加载章节失败');
    } finally {
      setChaptersLoading(false);
    }
  };

  const handleAddChapter = () => {
    setEditingChapter(null);
    chapterForm.resetFields();
    chapterForm.setFieldsValue({ order: chapters.length + 1, duration: 0 });
    setChapterModalVisible(true);
  };

  const handleEditChapter = (chapter: TutorialChapter) => {
    setEditingChapter(chapter);
    chapterForm.setFieldsValue({
      title: chapter.title,
      content: chapter.content,
      order: chapter.order,
      video_url: chapter.video_url,
      duration: chapter.duration,
    });
    setChapterModalVisible(true);
  };

  const handleDeleteChapter = async (chapterId: number) => {
    if (!selectedTutorialId) return;
    Modal.confirm({
      title: '删除章节',
      content: '确定要删除此章节吗？',
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteChapter(selectedTutorialId, chapterId);
          message.success('章节已删除');
          openChapterManager(selectedTutorialId);
        } catch (error) {
          message.error('删除章节失败');
        }
      },
    });
  };

  const handleChapterSubmit = async () => {
    if (!selectedTutorialId) return;
    setChapterSubmitting(true);
    try {
      const values = await chapterForm.validateFields();
      if (editingChapter) {
        await updateChapter(selectedTutorialId, editingChapter.id, values);
        message.success('章节更新成功');
      } else {
        await createChapter(selectedTutorialId, values);
        message.success('章节创建成功');
      }
      setChapterModalVisible(false);
      openChapterManager(selectedTutorialId);
    } catch (error: unknown) {
      if (error && typeof error === 'object' && 'errorFields' in error) return;
      message.error('操作失败');
    } finally {
      setChapterSubmitting(false);
    }
  };

  // ---- Table Columns ----

  const columns: ColumnsType<Tutorial> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: 260,
      ellipsis: true,
      render: (title: string, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>{title}</div>
          {record.description && (
            <div style={{ fontSize: 12, color: '#999', marginTop: 2 }}>
              {record.description.length > 60
                ? record.description.substring(0, 60) + '...'
                : record.description}
            </div>
          )}
        </div>
      ),
    },
    {
      title: '难度',
      dataIndex: 'difficulty_level',
      key: 'difficulty_level',
      width: 110,
      render: (level: string) => {
        const opt = difficultyOptions.find((d) => d.value === level);
        return <Tag color={opt?.color}>{opt?.label || level}</Tag>;
      },
    },
    {
      title: '精选',
      key: 'featured',
      width: 90,
      render: (_: unknown, record: Tutorial) => (
        <Switch
          checked={record.status === 'published'}
          size="small"
          checkedChildren="是"
          unCheckedChildren="否"
          onChange={() => handleToggleFeatured(record.id, record.status)}
        />
      ),
    },
    {
      title: '浏览',
      dataIndex: 'view_count',
      key: 'view_count',
      width: 80,
      render: (count: number) => (
        <span>
          <EyeOutlined style={{ marginRight: 4 }} />
          {count.toLocaleString()}
        </span>
      ),
    },
    {
      title: '点赞',
      key: 'likes',
      width: 80,
      render: () => (
        <span>
          <LikeOutlined style={{ marginRight: 4 }} />
        </span>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const config: Record<string, { color: string; label: string }> = {
          published: { color: 'green', label: '已发布' },
          draft: { color: 'orange', label: '草稿' },
          archived: { color: 'default', label: '已归档' },
        };
        const cfg = config[status] || { color: 'default', label: status };
        return <Tag color={cfg.color}>{cfg.label}</Tag>;
      },
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
      width: 240,
      fixed: 'right',
      render: (_: unknown, record: Tutorial) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<BookOutlined />}
            onClick={() => openChapterManager(record.id)}
          >
            章节
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此教程？"
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
        教程管理
      </Title>

      {/* Search/Filter */}
      <Card style={{ marginBottom: 16 }}>
        <Form layout="inline" onFinish={handleSearch}>
          <Form.Item name="search">
            <Input placeholder="按标题搜索..." prefix={<SearchOutlined />} style={{ width: 220 }} allowClear />
          </Form.Item>
          <Form.Item name="difficulty_level">
            <Select placeholder="难度" style={{ width: 150 }} allowClear>
              {difficultyOptions.map((opt) => (
                <Option key={opt.value} value={opt.value}>{opt.label}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="status">
            <Select placeholder="状态" style={{ width: 140 }} allowClear>
              <Option value="published">已发布</Option>
              <Option value="draft">草稿</Option>
              <Option value="archived">已归档</Option>
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

      {/* Main Table */}
      <Card
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            创建教程
          </Button>
        }
      >
        <Table<Tutorial>
          columns={columns}
          dataSource={tutorials}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1300 }}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 个教程`,
            onChange: (page, pageSize) => handleTableChange(page, pageSize),
          }}
          locale={{ emptyText: '暂无教程' }}
        />
      </Card>

      {/* Create/Edit Tutorial Modal */}
      <Modal
        title={editingTutorial ? '编辑教程' : '创建教程'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={800}
        confirmLoading={submitting}
        okText={editingTutorial ? '更新' : '创建'}
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            label="标题（中文）"
            name="title"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder="教程标题" />
          </Form.Item>

          <Form.Item
            label="描述"
            name="description"
            rules={[{ required: true, message: '请输入描述' }]}
          >
            <TextArea rows={3} placeholder="简要描述" showCount maxLength={500} />
          </Form.Item>

          <Form.Item
            label="内容"
            name="content"
            rules={[{ required: true, message: '请输入教程内容' }]}
          >
            <TextArea rows={6} placeholder="教程内容（Markdown 或 HTML）" showCount maxLength={100000} />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="难度" name="difficulty_level">
                <Select placeholder="选择难度">
                  {difficultyOptions.map((opt) => (
                    <Option key={opt.value} value={opt.value}>{opt.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="状态" name="status">
                <Select>
                  <Option value="published">已发布</Option>
                  <Option value="draft">草稿</Option>
                  <Option value="archived">已归档</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item label="视频 URL" name="video_url" rules={[{ type: 'url', message: 'URL 格式无效', warningOnly: true }]}>
            <Input placeholder="https://example.com/video.mp4" />
          </Form.Item>

          <Form.Item label="封面图片 URL" name="cover_image" rules={[{ type: 'url', message: 'URL 格式无效', warningOnly: true }]}>
            <Input placeholder="https://example.com/cover.jpg" />
          </Form.Item>

          <Form.Item label="排序" name="sort_order">
            <InputNumber min={0} max={9999} style={{ width: '100%' }} placeholder="显示顺序" />
          </Form.Item>

          <Form.Item label="技能 ID（可选）" name="skill_id">
            <InputNumber min={1} style={{ width: '100%' }} placeholder="关联技能" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Chapter Management Modal */}
      <Modal
        title="章节管理"
        open={chaptersModalVisible}
        onCancel={() => {
          setChaptersModalVisible(false);
          setSelectedTutorialId(null);
        }}
        footer={null}
        width={700}
      >
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'flex-end' }}>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAddChapter}>
            添加章节
          </Button>
        </div>

        {chaptersLoading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>加载章节中...</div>
        ) : chapters.length === 0 ? (
          <Empty description="暂无章节" />
        ) : (
          <List
            dataSource={chapters.sort((a, b) => a.order - b.order)}
            renderItem={(chapter) => (
              <List.Item
                actions={[
                  <Button
                    type="link"
                    size="small"
                    icon={<EditOutlined />}
                    onClick={() => handleEditChapter(chapter)}
                  >
                    编辑
                  </Button>,
                  <Popconfirm
                    title="确定删除此章节？"
                    onConfirm={() => handleDeleteChapter(chapter.id)}
                    okText="删除"
                    cancelText="取消"
                    okType="danger"
                  >
                    <Button type="link" size="small" danger icon={<DeleteOutlined />}>
                      删除
                    </Button>
                  </Popconfirm>,
                ]}
              >
                <List.Item.Meta
                  avatar={
                    <Tag color="blue" style={{ marginRight: 0 }}>#{chapter.order}</Tag>
                  }
                  title={chapter.title}
                  description={
                    <span>
                      {chapter.duration ? `${chapter.duration} 分钟` : ''}
                      {chapter.video_url ? ' | 有视频' : ''}
                    </span>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Modal>

      {/* Chapter Edit Modal */}
      <Modal
        title={editingChapter ? '编辑章节' : '添加章节'}
        open={chapterModalVisible}
        onOk={handleChapterSubmit}
        onCancel={() => setChapterModalVisible(false)}
        width={640}
        confirmLoading={chapterSubmitting}
        okText={editingChapter ? '更新' : '创建'}
        cancelText="取消"
        destroyOnClose
      >
        <Form form={chapterForm} layout="vertical" preserve={false}>
          <Form.Item
            label="章节标题"
            name="title"
            rules={[{ required: true, message: '请输入章节标题' }]}
          >
            <Input placeholder="例如：入门指南" />
          </Form.Item>

          <Form.Item
            label="内容"
            name="content"
            rules={[{ required: true, message: '请输入章节内容' }]}
          >
            <TextArea rows={5} placeholder="章节内容" showCount maxLength={50000} />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="排序" name="order">
                <InputNumber min={1} max={999} style={{ width: '100%' }} placeholder="1" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="时长（分钟）" name="duration">
                <InputNumber min={0} style={{ width: '100%' }} placeholder="30" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item label="视频 URL" name="video_url">
            <Input placeholder="https://example.com/video.mp4" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TutorialManagement;
