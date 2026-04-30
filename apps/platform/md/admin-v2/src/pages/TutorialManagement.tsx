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
  { label: 'Beginner', value: 'beginner', color: 'green' },
  { label: 'Intermediate', value: 'intermediate', color: 'orange' },
  { label: 'Advanced', value: 'advanced', color: 'red' },
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
      message.error('Failed to load tutorials');
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
      title: 'Confirm Delete',
      content: 'Are you sure you want to delete this tutorial? All chapters will also be deleted.',
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await deleteTutorial(id);
          message.success('Tutorial deleted successfully');
          fetchTutorials();
        } catch (error) {
          message.error('Failed to delete tutorial');
        }
      },
    });
  };

  const handleToggleFeatured = async (id: number, status: string) => {
    try {
      const newStatus = status === 'published' ? 'draft' : 'published';
      await updateTutorial(id, { status: newStatus });
      message.success(`Tutorial ${newStatus === 'published' ? 'published' : 'unpublished'}`);
      fetchTutorials();
    } catch (error) {
      message.error('Failed to update tutorial');
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const values = await form.validateFields();
      if (editingTutorial) {
        await updateTutorial(editingTutorial.id, values);
        message.success('Tutorial updated successfully');
      } else {
        await createTutorial(values);
        message.success('Tutorial created successfully');
      }
      setModalVisible(false);
      fetchTutorials();
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
      message.error('Failed to load chapters');
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
      title: 'Delete Chapter',
      content: 'Are you sure you want to delete this chapter?',
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await deleteChapter(selectedTutorialId, chapterId);
          message.success('Chapter deleted');
          openChapterManager(selectedTutorialId);
        } catch (error) {
          message.error('Failed to delete chapter');
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
        message.success('Chapter updated');
      } else {
        await createChapter(selectedTutorialId, values);
        message.success('Chapter created');
      }
      setChapterModalVisible(false);
      openChapterManager(selectedTutorialId);
    } catch (error: unknown) {
      if (error && typeof error === 'object' && 'errorFields' in error) return;
      message.error('Operation failed');
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
      title: 'Title',
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
      title: 'Difficulty',
      dataIndex: 'difficulty_level',
      key: 'difficulty_level',
      width: 110,
      render: (level: string) => {
        const opt = difficultyOptions.find((d) => d.value === level);
        return <Tag color={opt?.color}>{opt?.label || level}</Tag>;
      },
    },
    {
      title: 'Featured',
      key: 'featured',
      width: 90,
      render: (_: unknown, record: Tutorial) => (
        <Switch
          checked={record.status === 'published'}
          size="small"
          checkedChildren="Yes"
          unCheckedChildren="No"
          onChange={() => handleToggleFeatured(record.id, record.status)}
        />
      ),
    },
    {
      title: 'Views',
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
      title: 'Likes',
      key: 'likes',
      width: 80,
      render: () => (
        <span>
          <LikeOutlined style={{ marginRight: 4 }} />
        </span>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const config: Record<string, { color: string; label: string }> = {
          published: { color: 'green', label: 'Published' },
          draft: { color: 'orange', label: 'Draft' },
          archived: { color: 'default', label: 'Archived' },
        };
        const cfg = config[status] || { color: 'default', label: status };
        return <Tag color={cfg.color}>{cfg.label}</Tag>;
      },
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      render: (date: string) => formatDate(date),
    },
    {
      title: 'Actions',
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
            Chapters
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Delete this tutorial?"
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
        Tutorial Management
      </Title>

      {/* Search/Filter */}
      <Card style={{ marginBottom: 16 }}>
        <Form layout="inline" onFinish={handleSearch}>
          <Form.Item name="search">
            <Input placeholder="Search by title..." prefix={<SearchOutlined />} style={{ width: 220 }} allowClear />
          </Form.Item>
          <Form.Item name="difficulty_level">
            <Select placeholder="Difficulty" style={{ width: 150 }} allowClear>
              {difficultyOptions.map((opt) => (
                <Option key={opt.value} value={opt.value}>{opt.label}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="status">
            <Select placeholder="Status" style={{ width: 140 }} allowClear>
              <Option value="published">Published</Option>
              <Option value="draft">Draft</Option>
              <Option value="archived">Archived</Option>
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

      {/* Main Table */}
      <Card
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            Create Tutorial
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
            showTotal: (total) => `Total ${total} tutorials`,
            onChange: (page, pageSize) => handleTableChange(page, pageSize),
          }}
          locale={{ emptyText: 'No tutorials found' }}
        />
      </Card>

      {/* Create/Edit Tutorial Modal */}
      <Modal
        title={editingTutorial ? 'Edit Tutorial' : 'Create Tutorial'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={800}
        confirmLoading={submitting}
        okText={editingTutorial ? 'Update' : 'Create'}
        cancelText="Cancel"
        destroyOnClose
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            label="Title (zh_CN)"
            name="title"
            rules={[{ required: true, message: 'Please enter the title' }]}
          >
            <Input placeholder="Tutorial title" />
          </Form.Item>

          <Form.Item
            label="Description"
            name="description"
            rules={[{ required: true, message: 'Please enter a description' }]}
          >
            <TextArea rows={3} placeholder="Brief description" showCount maxLength={500} />
          </Form.Item>

          <Form.Item
            label="Content"
            name="content"
            rules={[{ required: true, message: 'Please enter tutorial content' }]}
          >
            <TextArea rows={6} placeholder="Tutorial content in markdown or HTML" showCount maxLength={100000} />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="Difficulty" name="difficulty_level">
                <Select placeholder="Select difficulty">
                  {difficultyOptions.map((opt) => (
                    <Option key={opt.value} value={opt.value}>{opt.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="Status" name="status">
                <Select>
                  <Option value="published">Published</Option>
                  <Option value="draft">Draft</Option>
                  <Option value="archived">Archived</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item label="Video URL" name="video_url" rules={[{ type: 'url', message: 'Invalid URL', warningOnly: true }]}>
            <Input placeholder="https://example.com/video.mp4" />
          </Form.Item>

          <Form.Item label="Cover Image URL" name="cover_image" rules={[{ type: 'url', message: 'Invalid URL', warningOnly: true }]}>
            <Input placeholder="https://example.com/cover.jpg" />
          </Form.Item>

          <Form.Item label="Sort Order" name="sort_order">
            <InputNumber min={0} max={9999} style={{ width: '100%' }} placeholder="Display order" />
          </Form.Item>

          <Form.Item label="Skill ID (Optional)" name="skill_id">
            <InputNumber min={1} style={{ width: '100%' }} placeholder="Link to a skill" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Chapter Management Modal */}
      <Modal
        title="Chapter Management"
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
            Add Chapter
          </Button>
        </div>

        {chaptersLoading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>Loading chapters...</div>
        ) : chapters.length === 0 ? (
          <Empty description="No chapters yet" />
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
                    Edit
                  </Button>,
                  <Popconfirm
                    title="Delete this chapter?"
                    onConfirm={() => handleDeleteChapter(chapter.id)}
                    okText="Delete"
                    cancelText="Cancel"
                    okType="danger"
                  >
                    <Button type="link" size="small" danger icon={<DeleteOutlined />}>
                      Delete
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
                      {chapter.duration ? `${chapter.duration} min` : ''}
                      {chapter.video_url ? ' | Has video' : ''}
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
        title={editingChapter ? 'Edit Chapter' : 'Add Chapter'}
        open={chapterModalVisible}
        onOk={handleChapterSubmit}
        onCancel={() => setChapterModalVisible(false)}
        width={640}
        confirmLoading={chapterSubmitting}
        okText={editingChapter ? 'Update' : 'Create'}
        cancelText="Cancel"
        destroyOnClose
      >
        <Form form={chapterForm} layout="vertical" preserve={false}>
          <Form.Item
            label="Chapter Title"
            name="title"
            rules={[{ required: true, message: 'Please enter chapter title' }]}
          >
            <Input placeholder="e.g. Getting Started" />
          </Form.Item>

          <Form.Item
            label="Content"
            name="content"
            rules={[{ required: true, message: 'Please enter chapter content' }]}
          >
            <TextArea rows={5} placeholder="Chapter content" showCount maxLength={50000} />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="Order" name="order">
                <InputNumber min={1} max={999} style={{ width: '100%' }} placeholder="1" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="Duration (min)" name="duration">
                <InputNumber min={0} style={{ width: '100%' }} placeholder="30" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item label="Video URL" name="video_url">
            <Input placeholder="https://example.com/video.mp4" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TutorialManagement;
