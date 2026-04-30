/**
 * 资源下载管理页面
 * Download Management Page
 */
import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Image,
  Input,
  Modal,
  Form,
  Select,
  message,
  Popconfirm,
  Switch,
  Tooltip
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  CloudDownloadOutlined,
  LinkOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { downloadApi } from '@/api/downloads';

const { TextArea } = Input;
const { Option } = Select;

interface Download {
  id: number;
  download_key: string;
  slug: string;
  title_zh_CN: string;
  title_en: string;
  description_zh_CN: string;
  category: string;
  subcategory: string;
  version: string;
  platform: string;
  file_name: string;
  file_url: string;
  file_size: number;
  file_type: string;
  file_checksum: string;
  mirror_url_1: string;
  mirror_url_2: string;
  mirror_url_3: string;
  mirror_url_names: string;
  github_url: string;
  official_url: string;
  download_count: number;
  view_count: number;
  featured: boolean;
  is_official: boolean;
  is_published: boolean;
  created_at: string;
}

/**
 * 资源下载管理组件
 */
const DownloadManagement: React.FC = () => {
  const [downloads, setDownloads] = useState<Download[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [currentDownload, setCurrentDownload] = useState<Download | null>(null);
  const [form] = Form.useForm();

  /**
   * 分类选项
   */
  const categoryOptions = [
    { value: 'wsl', label: 'WSL', icon: '🐧' },
    { value: 'python', label: 'Python', icon: '🐍' },
    { value: 'nodejs', label: 'Node.js', icon: '💚' },
    { value: 'git', label: 'Git', icon: '📂' },
    { value: 'github-desktop', label: 'GitHub Desktop', icon: '🐙' },
    { value: 'vscode', label: 'VS Code', icon: '💻' },
    { value: 'docker', label: 'Docker', icon: '🐳' },
    { value: 'postgresql', label: 'PostgreSQL', icon: '🐘' },
    { value: 'redis', label: 'Redis', icon: '🔴' },
    { value: 'mongodb', label: 'MongoDB', icon: '🍃' },
    { value: 'tools', label: '其他工具', icon: '🛠️' }
  ];

  const subcategoryOptions = [
    { value: 'installer', label: '安装包' },
    { value: 'source-code', label: '源代码' },
    { value: 'extension', label: '扩展/插件' },
    { value: 'plugin', label: '插件' }
  ];

  const platformOptions = [
    { value: 'windows', label: 'Windows', icon: '🪟' },
    { value: 'macos', label: 'macOS', icon: '🍎' },
    { value: 'linux', label: 'Linux', icon: '🐧' },
    { value: 'all', label: '全平台', icon: '🌐' }
  ];

  /**
   * 加载资源列表
   */
  const loadDownloads = async () => {
    setLoading(true);
    try {
      const response = await downloadApi.list();
      if (response.success) {
        setDownloads(response.data);
      }
    } catch (error) {
      message.error('加载资源列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDownloads();
  }, []);

  /**
   * 打开新增/编辑对话框
   */
  const openModal = (download?: Download) => {
    if (download) {
      setCurrentDownload(download);
      // 解析镜像名称
      let mirrorNames = {};
      try {
        mirrorNames = JSON.parse(download.mirror_url_names || '{}');
      } catch (e) {
        mirrorNames = {};
      }
      form.setFieldsValue({
        ...download,
        mirror_name_1: mirrorNames.mirror_url_1 || '',
        mirror_name_2: mirrorNames.mirror_url_2 || '',
        mirror_name_3: mirrorNames.mirror_url_3 || ''
      });
    } else {
      setCurrentDownload(null);
      form.resetFields();
    }
    setModalVisible(true);
  };

  /**
   * 保存资源
   */
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      // 组装镜像名称 JSON
      const mirrorNames = {};
      if (values.mirror_url_1 && values.mirror_name_1) {
        mirrorNames.mirror_url_1 = values.mirror_name_1;
      }
      if (values.mirror_url_2 && values.mirror_name_2) {
        mirrorNames.mirror_url_2 = values.mirror_name_2;
      }
      if (values.mirror_url_3 && values.mirror_name_3) {
        mirrorNames.mirror_url_3 = values.mirror_name_3;
      }
      values.mirror_url_names = JSON.stringify(mirrorNames);

      if (currentDownload) {
        await downloadApi.update(currentDownload.id, values);
        message.success('更新成功');
      } else {
        await downloadApi.create(values);
        message.success('创建成功');
      }
      setModalVisible(false);
      loadDownloads();
    } catch (error) {
      message.error('保存失败');
    }
  };

  /**
   * 删除资源
   */
  const handleDelete = async (id: number) => {
    try {
      await downloadApi.delete(id);
      message.success('删除成功');
      loadDownloads();
    } catch (error) {
      message.error('删除失败');
    }
  };

  /**
   * 切换精选状态
   */
  const handleToggleFeatured = async (id: number, featured: boolean) => {
    try {
      await downloadApi.update(id, { featured: !featured });
      message.success('更新成功');
      loadDownloads();
    } catch (error) {
      message.error('更新失败');
    }
  };

  /**
   * 切换官方标识
   */
  const handleToggleOfficial = async (id: number, is_official: boolean) => {
    try {
      await downloadApi.update(id, { is_official: !is_official });
      message.success('更新成功');
      loadDownloads();
    } catch (error) {
      message.error('更新失败');
    }
  };

  /**
   * 格式化文件大小
   */
  const formatFileSize = (bytes: number): string => {
    if (bytes >= 1073741824) {
      return (bytes / 1073741824).toFixed(2) + ' GB';
    } else if (bytes >= 1048576) {
      return (bytes / 1048576).toFixed(2) + ' MB';
    } else if (bytes >= 1024) {
      return (bytes / 1024).toFixed(2) + ' KB';
    }
    return bytes + ' B';
  };

  /**
   * 表格列定义
   */
  const columns: ColumnsType<Download> = [
    {
      title: '资源名称',
      dataIndex: 'title_zh_CN',
      key: 'title_zh_CN',
      width: 250,
      fixed: 'left',
      render: (title: string, record: Download) => (
        <div>
          <div style={{ fontWeight: 500 }}>
            {categoryOptions.find(c => c.value === record.category)?.icon} {title}
            {record.is_official && <Tag color="green" style={{ marginLeft: 8 }}>官方</Tag>}
          </div>
          <div style={{ fontSize: 12, color: '#999' }}>{record.title_en}</div>
        </div>
      )
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
      width: 100,
      render: (version: string) => <Tag color="blue">{version}</Tag>
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 150,
      render: (category: string, record: Download) => (
        <Space direction="vertical" size={4}>
          <Tag color="purple">{categoryOptions.find(c => c.value === category)?.label || category}</Tag>
          <Tag>{subcategoryOptions.find(s => s.value === record.subcategory)?.label || record.subcategory}</Tag>
        </Space>
      )
    },
    {
      title: '平台',
      dataIndex: 'platform',
      key: 'platform',
      width: 100,
      render: (platform: string) => {
        const option = platformOptions.find(p => p.value === platform);
        return (
          <span>
            {option?.icon} {option?.label || platform}
          </span>
        );
      }
    },
    {
      title: '文件信息',
      key: 'file',
      width: 200,
      render: (_, record: Download) => (
        <Space direction="vertical" size={4}>
          <div style={{ fontSize: 12 }}>
            <span style={{ color: '#999' }}>类型:</span> {record.file_type}
          </div>
          <div style={{ fontSize: 12 }}>
            <span style={{ color: '#999' }}>大小:</span> {formatFileSize(record.file_size)}
          </div>
          <Tooltip title={record.file_checksum}>
            <div style={{ fontSize: 12, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              <span style={{ color: '#999' }}>校验:</span> {record.file_checksum?.substring(0, 16)}...
            </div>
          </Tooltip>
        </Space>
      )
    },
    {
      title: '链接',
      key: 'links',
      width: 150,
      render: (_, record: Download) => (
        <Space direction="vertical" size={4}>
          {record.file_url && (
            <Tooltip title="主链接">
              <Tag color="blue" icon={<LinkOutlined />}>主链接</Tag>
            </Tooltip>
          )}
          {record.mirror_url_1 && (
            <Tooltip title="镜像1">
              <Tag color="orange" icon={<CloudDownloadOutlined />}>镜像1</Tag>
            </Tooltip>
          )}
          {record.github_url && (
            <Tooltip title={record.github_url}>
              <Tag icon={<LinkOutlined />}>GitHub</Tag>
            </Tooltip>
          )}
        </Space>
      )
    },
    {
      title: '统计',
      key: 'stats',
      width: 120,
      render: (_, record: Download) => (
        <Space direction="vertical" size={4}>
          <span><CloudDownloadOutlined /> {record.download_count.toLocaleString()}</span>
          <span><EyeOutlined /> {record.view_count.toLocaleString()}</span>
        </Space>
      )
    },
    {
      title: '状态',
      key: 'status',
      width: 120,
      render: (_, record: Download) => (
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
            checkedChildren="官方"
            unCheckedChildren="非官方"
            checked={record.is_official}
            onChange={() => handleToggleOfficial(record.id, record.is_official)}
          />
          <Switch
            size="small"
            checkedChildren="发布"
            unCheckedChildren="草稿"
            checked={record.is_published}
            onChange={(checked) => {
              downloadApi.update(record.id, { is_published: !checked })
                .then(() => {
                  message.success('更新成功');
                  loadDownloads();
                })
                .catch(() => message.error('更新失败'));
            }}
          />
        </Space>
      )
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (_, record: Download) => (
        <Space>
          <Tooltip title="预览">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => window.open(`/downloads/${record.slug}.html`, '_blank')}
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
            title="确定要删除这个资源吗？"
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
          <h2>资源下载管理</h2>
          <Tag color="blue">共 {downloads.length} 个资源</Tag>
        </Space>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => openModal()}
        >
          新增资源
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={downloads}
        rowKey="id"
        loading={loading}
        scroll={{ x: 1600 }}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 个资源`
        }}
      />

      {/* 新增/编辑对话框 */}
      <Modal
        title={currentDownload ? '编辑资源' : '新增资源'}
        open={modalVisible}
        onOk={handleSave}
        onCancel={() => setModalVisible(false)}
        width={800}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="资源标识"
            name="download_key"
            rules={[{ required: true, message: '请输入资源唯一标识' }]}
          >
            <Input placeholder="例如: wsl2-windows" />
          </Form.Item>

          <Form.Item
            label="URL 标识"
            name="slug"
            rules={[{ required: true, message: '请输入 URL 标识' }]}
          >
            <Input placeholder="例如: wsl2-windows" />
          </Form.Item>

          <Form.Item
            label="中文标题"
            name="title_zh_CN"
            rules={[{ required: true, message: '请输入中文标题' }]}
          >
            <Input placeholder="资源标题" />
          </Form.Item>

          <Form.Item
            label="英文标题"
            name="title_en"
          >
            <Input placeholder="Resource Title" />
          </Form.Item>

          <Form.Item
            label="中文描述"
            name="description_zh_CN"
            rules={[{ required: true, message: '请输入中文描述' }]}
          >
            <TextArea rows={3} placeholder="资源简介" />
          </Form.Item>

          <Form.Item
            label="资源分类"
            name="category"
            rules={[{ required: true, message: '请选择资源分类' }]}
          >
            <Select placeholder="选择分类">
              {categoryOptions.map(opt => (
                <Option key={opt.value} value={opt.value}>
                  {opt.icon} {opt.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="子分类"
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
            label="版本号"
            name="version"
            rules={[{ required: true, message: '请输入版本号' }]}
          >
            <Input placeholder="例如: 3.12.1" />
          </Form.Item>

          <Form.Item
            label="支持平台"
            name="platform"
            rules={[{ required: true, message: '请选择平台' }]}
          >
            <Select placeholder="选择平台">
              {platformOptions.map(opt => (
                <Option key={opt.value} value={opt.value}>
                  {opt.icon} {opt.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="文件名"
            name="file_name"
            rules={[{ required: true, message: '请输入文件名' }]}
          >
            <Input placeholder="例如: python-3.12.1-amd64.exe" />
          </Form.Item>

          <Form.Item
            label="文件下载链接"
            name="file_url"
            rules={[{ required: true, message: '请输入文件下载链接' }]}
          >
            <Input placeholder="https://..." />
          </Form.Item>

          <Form.Item
            label="文件大小（字节）"
            name="file_size"
            rules={[{ required: true, message: '请输入文件大小' }]}
          >
            <Input type="number" placeholder="例如: 25600000" />
          </Form.Item>

          <Form.Item
            label="文件类型"
            name="file_type"
            rules={[{ required: true, message: '请输入文件类型' }]}
          >
            <Select>
              <Option value="exe">exe</Option>
              <Option value="msi">msi</Option>
              <Option value="zip">zip</Option>
              <Option value="tar.gz">tar.gz</Option>
              <Option value="dmg">dmg</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="文件校验和"
            name="file_checksum"
          >
            <Input placeholder="MD5 或 SHA256" />
          </Form.Item>

          <Form.Item label="国内镜像链接1">
            <Input.Group compact>
              <Form.Item name="mirror_url_1" noStyle>
                <Input style={{ width: '70%' }} placeholder="镜像 URL" />
              </Form.Item>
              <Form.Item name="mirror_name_1" noStyle>
                <Input style={{ width: '30%' }} placeholder="名称（如：阿里云）" />
              </Form.Item>
            </Input.Group>
          </Form.Item>

          <Form.Item label="国内镜像链接2">
            <Input.Group compact>
              <Form.Item name="mirror_url_2" noStyle>
                <Input style={{ width: '70%' }} placeholder="镜像 URL" />
              </Form.Item>
              <Form.Item name="mirror_name_2" noStyle>
                <Input style={{ width: '30%' }} placeholder="名称" />
              </Form.Item>
            </Input.Group>
          </Form.Item>

          <Form.Item label="国内镜像链接3">
            <Input.Group compact>
              <Form.Item name="mirror_url_3" noStyle>
                <Input style={{ width: '70%' }} placeholder="镜像 URL" />
              </Form.Item>
              <Form.Item name="mirror_name_3" noStyle>
                <Input style={{ width: '30%' }} placeholder="名称" />
              </Form.Item>
            </Input.Group>
          </Form.Item>

          <Form.Item
            label="GitHub 仓库"
            name="github_url"
          >
            <Input placeholder="https://github.com/..." />
          </Form.Item>

          <Form.Item
            label="官方网站"
            name="official_url"
          >
            <Input placeholder="https://..." />
          </Form.Item>

          <Form.Item
            label="是否官方资源"
            name="is_official"
            valuePropName="checked"
          >
            <Switch />
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

export default DownloadManagement;
