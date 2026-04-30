/**
 * 教程管理页面
 * Tutorial Management Page
 */
import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Image,
  Tooltip,
  Modal,
  Form,
  Input,
  Select,
  message,
  Popconfirm,
  Switch
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { tutorialApi } from '@/api/tutorials';

const { TextArea } = Input;
const { Option } = Select;

interface Tutorial {
  id: number;
  tutorial_key: string;
  slug: string;
  title_zh_CN: string;
  title_en: string;
  description_zh_CN: string;
  category: string;
  subcategory: string;
  difficulty: string;
  thumbnail: string;
  video_url: string;
  video_type: string;
  video_duration: number;
  view_count: number;
  like_count: number;
  featured: boolean;
  is_published: boolean;
  created_at: string;
}

/**
 * 教程管理组件
 */
const TutorialManagement: React.FC = () => {
  const [tutorials, setTutorials] = useState<Tutorial[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [currentTutorial, setCurrentTutorial] = useState<Tutorial | null>(null);
  const [form] = Form.useForm();

  /**
   * 分类选项
   */
  const categoryOptions = [
    { value: 'claude-code', label: 'Claude Code', icon: '🤖' },
    { value: 'openclaw', label: 'OpenClaw', icon: '🦞' },
    { value: 'cursor', label: 'Cursor', icon: '⚡' },
    { value: 'windsurf', label: 'Windsurf', icon: '🌊' },
    { value: 'copilot', label: 'GitHub Copilot', icon: '✈️' },
    { value: 'bolt', label: 'Bolt.new', icon: '⚡' },
    { value: 'new', label: 'v0.dev', icon: '🆕' },
    { value: 'codeium', label: 'Codeium', icon: '💎' },
    { value: 'tabnine', label: 'Tabnine', icon: '9️⃣' },
    { value: 'continue', label: 'Continue', icon: '▶️' }
  ];

  const subcategoryOptions = [
    { value: 'installation', label: '安装教程' },
    { value: 'usage', label: '使用教程' },
    { value: 'tips', label: '使用技巧' },
    { value: 'advanced', label: '高级教程' },
    { value: 'troubleshooting', label: '故障排除' }
  ];

  const difficultyOptions = [
    { value: 'beginner', label: '入门', color: 'green' },
    { value: 'intermediate', label: '中级', color: 'orange' },
    { value: 'advanced', label: '高级', color: 'red' }
  ];

  /**
   * 加载教程列表
   */
  const loadTutorials = async () => {
    setLoading(true);
    try {
      const response = await tutorialApi.list();
      if (response.data) {
        setTutorials(response.data);
      }
    } catch (error) {
      message.error('加载教程列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTutorials();
  }, []);

  /**
   * 打开新增/编辑对话框
   */
  const openModal = (tutorial?: Tutorial) => {
    if (tutorial) {
      setCurrentTutorial(tutorial);
      form.setFieldsValue(tutorial);
    } else {
      setCurrentTutorial(null);
      form.resetFields();
    }
    setModalVisible(true);
  };

  /**
   * 保存教程
   */
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      if (currentTutorial) {
        await tutorialApi.update(currentTutorial.id, values);
        message.success('更新成功');
      } else {
        await tutorialApi.create(values);
        message.success('创建成功');
      }
      setModalVisible(false);
      loadTutorials();
    } catch (error) {
      message.error('保存失败');
    }
  };

  /**
   * 删除教程
   */
  const handleDelete = async (id: number) => {
    try {
      await tutorialApi.delete(id);
      message.success('删除成功');
      loadTutorials();
    } catch (error) {
      message.error('删除失败');
    }
  };

  /**
   * 切换精选状态
   */
  const handleToggleFeatured = async (id: number, featured: boolean) => {
    try {
      await tutorialApi.update(id, { featured: !featured });
      message.success('更新成功');
      loadTutorials();
    } catch (error) {
      message.error('更新失败');
    }
  };

  /**
   * 切换发布状态
   */
  const handleTogglePublished = async (id: number, is_published: boolean) => {
    try {
      await tutorialApi.update(id, { is_published: !is_published });
      message.success('更新成功');
      loadTutorials();
    } catch (error) {
      message.error('更新失败');
    }
  };

  /**
   * 表格列定义
   */
  const columns: ColumnsType<Tutorial> = [
    {
      title: '缩略图',
      dataIndex: 'thumbnail',
      key: 'thumbnail',
      width: 120,
      render: (url: string) => (
        <Image src={url} width={100} height={60} style={{ objectFit: 'cover' }} />
      )
    },
    {
      title: '标题',
      dataIndex: 'title_zh_CN',
      key: 'title_zh_CN',
      width: 250,
      render: (title: string, record: Tutorial) => (
        <div>
          <div>{title}</div>
          <div style={{ fontSize: 12, color: '#999' }}>{record.title_en}</div>
        </div>
      )
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 150,
      render: (category: string, record: Tutorial) => (
        <Space direction="vertical" size={4}>
          <Tag color="blue">{categoryOptions.find(c => c.value === category)?.label || category}</Tag>
          <Tag>{subcategoryOptions.find(s => s.value === record.subcategory)?.label || record.subcategory}</Tag>
        </Space>
      )
    },
    {
      title: '难度',
      dataIndex: 'difficulty',
      key: 'difficulty',
      width: 100,
      render: (difficulty: string) => {
        const option = difficultyOptions.find(d => d.value === difficulty);
        return <Tag color={option?.color}>{option?.label || difficulty}</Tag>;
      }
    },
    {
      title: '视频',
      key: 'video',
      width: 120,
      render: (_, record: Tutorial) => (
        <Space>
          <Tooltip title="视频类型">
            <Tag>{record.video_type}</Tag>
          </Tooltip>
          <Tooltip title="视频时长">
            <span>{Math.floor(record.video_duration / 60)}:{(record.video_duration % 60).toString().padStart(2, '0')}</span>
          </Tooltip>
        </Space>
      )
    },
    {
      title: '统计',
      key: 'stats',
      width: 150,
      render: (_, record: Tutorial) => (
        <Space direction="vertical" size={4}>
          <span><EyeOutlined /> {record.view_count.toLocaleString()}</span>
          <span>❤️ {record.like_count}</span>
        </Space>
      )
    },
    {
      title: '状态',
      key: 'status',
      width: 120,
      render: (_, record: Tutorial) => (
        <Space direction="vertical" size={4}>
          <Switch
            size="small"
            checkedChildren="精选"
            unCheckedChildren="普通"
            checked={record.featured}
            onChange={() => handleToggleFeatured(record.id, record.featured)}
          />
          <Switch
            size="small"
            checkedChildren="已发布"
            unCheckedChildren="草稿"
            checked={record.is_published}
            onChange={() => handleTogglePublished(record.id, record.is_published)}
          />
        </Space>
      )
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (_, record: Tutorial) => (
        <Space>
          <Tooltip title="预览">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => window.open(`/tutorials/${record.slug}.html`, '_blank')}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => openModal(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个教程吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          <h2>教程管理</h2>
          <Tag color="blue">共 {tutorials.length} 个教程</Tag>
        </Space>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => openModal()}
        >
          新增教程
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={tutorials}
        rowKey="id"
        loading={loading}
        scroll={{ x: 1400 }}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 个教程`
        }}
      />

      {/* 新增/编辑对话框 */}
      <Modal
        title={currentTutorial ? '编辑教程' : '新增教程'}
        open={modalVisible}
        onOk={handleSave}
        onCancel={() => setModalVisible(false)}
        width={800}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="教程标识"
            name="tutorial_key"
            rules={[{ required: true, message: '请输入教程唯一标识' }]}
          >
            <Input placeholder="例如: claude-code-getting-started" />
          </Form.Item>

          <Form.Item
            label="URL 标识"
            name="slug"
            rules={[{ required: true, message: '请输入 URL 标识' }]}
          >
            <Input placeholder="例如: claude-code-getting-started" />
          </Form.Item>

          <Form.Item
            label="中文标题"
            name="title_zh_CN"
            rules={[{ required: true, message: '请输入中文标题' }]}
          >
            <Input placeholder="教程标题" />
          </Form.Item>

          <Form.Item
            label="英文标题"
            name="title_en"
          >
            <Input placeholder="Tutorial Title" />
          </Form.Item>

          <Form.Item
            label="中文描述"
            name="description_zh_CN"
            rules={[{ required: true, message: '请输入中文描述' }]}
          >
            <TextArea rows={3} placeholder="教程简介" />
          </Form.Item>

          <Form.Item
            label="英文描述"
            name="description_en"
          >
            <TextArea rows={3} placeholder="Tutorial Description" />
          </Form.Item>

          <Form.Item
            label="工具分类"
            name="category"
            rules={[{ required: true, message: '请选择工具分类' }]}
          >
            <Select placeholder="选择工具">
              {categoryOptions.map(opt => (
                <Option key={opt.value} value={opt.value}>
                  {opt.icon} {opt.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="教程子分类"
            name="subcategory"
            rules={[{ required: true, message: '请选择子分类' }]}
          >
            <Select placeholder="选择子分类">
              {subcategoryOptions.map(opt => (
                <Option key={opt.value} value={opt.value}>{opt.label}</Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="难度级别"
            name="difficulty"
            rules={[{ required: true, message: '请选择难度级别' }]}
          >
            <Select placeholder="选择难度">
              {difficultyOptions.map(opt => (
                <Option key={opt.value} value={opt.value}>{opt.label}</Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="缩略图"
            name="thumbnail"
          >
            <Input placeholder="图片 URL" />
          </Form.Item>

          <Form.Item
            label="视频链接"
            name="video_url"
            rules={[{ required: true, message: '请输入视频链接' }]}
          >
            <Input placeholder="视频 URL" />
          </Form.Item>

          <Form.Item
            label="视频类型"
            name="video_type"
            rules={[{ required: true, message: '请选择视频类型' }]}
          >
            <Select>
              <Option value="upload">上传视频</Option>
              <Option value="youtube">YouTube</Option>
              <Option value="bilibili">Bilibili</Option>
              <Option value="vimeo">Vimeo</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="视频时长（秒）"
            name="video_duration"
            rules={[{ required: true, message: '请输入视频时长' }]}
          >
            <Input type="number" placeholder="例如: 1800" />
          </Form.Item>

          <Form.Item
            label="GitHub 链接"
            name="github_url"
          >
            <Input placeholder="https://github.com/..." />
          </Form.Item>

          <Form.Item
            label="文档链接"
            name="documentation_url"
          >
            <Input placeholder="文档 URL" />
          </Form.Item>

          <Form.Item
            label="是否精选"
            name="featured"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            label="是否发布"
            name="is_published"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TutorialManagement;
