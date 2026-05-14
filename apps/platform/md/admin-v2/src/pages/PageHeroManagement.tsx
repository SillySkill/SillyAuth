import React, { useEffect, useState, useCallback } from 'react';
import {
  Tabs,
  Form,
  Input,
  Button,
  Card,
  Row,
  Col,
  message,
  Spin,
  Typography,
  Space,
  Collapse,
  Empty,
  Popconfirm,
  Select,
} from 'antd';
import {
  SaveOutlined,
  ReloadOutlined,
  PlusOutlined,
  DeleteOutlined,
  DownloadOutlined,
  BookOutlined,
  ShopOutlined,
  InfoCircleOutlined,
  TeamOutlined,
  MailOutlined,
  QuestionCircleOutlined,
  DollarOutlined,
  FileTextOutlined,
  EditOutlined,
  SafetyOutlined,
  SolutionOutlined,
  HomeOutlined,
  PictureOutlined,
  VideoCameraOutlined,
} from '@ant-design/icons';
import {
  getDownloadsHero, saveDownloadsHero,
  getTutorialsHero, saveTutorialsHero,
  getMarketplaceHero, saveMarketplaceHero,
  getAboutHero, saveAboutHero,
  getCommunityHero, saveCommunityHero,
  getContactHero, saveContactHero,
  getHelpHero, saveHelpHero,
  getPricingHero, savePricingHero,
  getDocsHero, saveDocsHero,
  getCreationHero, saveCreationHero,
  getPolicyHero, savePolicyHero,
  getVendorApplyHero, saveVendorApplyHero,
  getIndexHero, saveIndexHero,
} from '../api/pageHeroes';
import type { PageHeroData, PageHeroSlide } from '../api/pageHeroes';

const { TextArea } = Input;
const { Title, Text } = Typography;
const { Panel } = Collapse;

// ---------------------------------------------------------------------------
// Page hero tab definitions
// ---------------------------------------------------------------------------

interface HeroPageDef {
  key: string;
  label: string;
  icon: React.ReactNode;
  getter: () => Promise<PageHeroData>;
  setter: (data: PageHeroData) => Promise<void>;
}

const HERO_PAGES: HeroPageDef[] = [
  { key: 'index',       label: '首页',         icon: <HomeOutlined />,
    getter: getIndexHero,        setter: saveIndexHero },
  { key: 'downloads',    label: '下载中心',     icon: <DownloadOutlined />,
    getter: getDownloadsHero,    setter: saveDownloadsHero },
  { key: 'tutorials',    label: '教程中心',     icon: <BookOutlined />,
    getter: getTutorialsHero,    setter: saveTutorialsHero },
  { key: 'marketplace',  label: '供应商市场',   icon: <ShopOutlined />,
    getter: getMarketplaceHero,  setter: saveMarketplaceHero },
  { key: 'about',        label: '关于我们',     icon: <InfoCircleOutlined />,
    getter: getAboutHero,        setter: saveAboutHero },
  { key: 'community',    label: '社区论坛',     icon: <TeamOutlined />,
    getter: getCommunityHero,    setter: saveCommunityHero },
  { key: 'contact',      label: '联系我们',     icon: <MailOutlined />,
    getter: getContactHero,      setter: saveContactHero },
  { key: 'help',         label: '帮助中心',     icon: <QuestionCircleOutlined />,
    getter: getHelpHero,         setter: saveHelpHero },
  { key: 'pricing',      label: '定价方案',     icon: <DollarOutlined />,
    getter: getPricingHero,      setter: savePricingHero },
  { key: 'docs',         label: '文档中心',     icon: <FileTextOutlined />,
    getter: getDocsHero,         setter: saveDocsHero },
  { key: 'creation',     label: '精选好文',     icon: <EditOutlined />,
    getter: getCreationHero,     setter: saveCreationHero },
  { key: 'policy',       label: '政策声明',     icon: <SafetyOutlined />,
    getter: getPolicyHero,       setter: savePolicyHero },
  { key: 'vendor_apply', label: '供应商申请',   icon: <SolutionOutlined />,
    getter: getVendorApplyHero,  setter: saveVendorApplyHero },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function createEmptySlide(): PageHeroSlide {
  return { title: '', subtitle: '', description: '', badge: '', background_image: '', type: 'image' };
}

/** Convert legacy flat data to slides array */
function ensureSlides(data: PageHeroData): PageHeroSlide[] {
  if (data.slides && data.slides.length > 0) {
    return data.slides.map((s) => ({ ...createEmptySlide(), ...s }));
  }
  // Migrate: flat fields → first slide
  if (data.title || data.subtitle || data.badge || data.background_image) {
    return [{ ...createEmptySlide(), title: data.title, subtitle: data.subtitle, description: data.description, badge: data.badge, background_image: data.background_image }];
  }
  // No data → start with one empty slide
  return [createEmptySlide()];
}

/** Collapse slides back to storage format (preserve flat fields for compat) */
function slidesToData(slides: PageHeroSlide[]): PageHeroData {
  const data: PageHeroData = { slides };
  // Only set flat fields if single slide, for backward compat
  if (slides.length === 1) {
    data.title = slides[0].title;
    data.subtitle = slides[0].subtitle;
    data.description = slides[0].description;
    data.badge = slides[0].badge;
    data.background_image = slides[0].background_image;
  }
  return data;
}

// ---------------------------------------------------------------------------
// Slide editor card
// ---------------------------------------------------------------------------

const SlideEditor: React.FC<{
  slide: PageHeroSlide;
  index: number;
  onChange: (index: number, slide: PageHeroSlide) => void;
  onDelete: (index: number) => void;
  canDelete: boolean;
}> = ({ slide, index, onChange, onDelete, canDelete }) => {
  const update = (field: keyof PageHeroSlide, value: string | undefined) => {
    onChange(index, { ...slide, [field]: value || undefined });
  };

  return (
    <Card
      size="small"
      title={
        <Space>
          {index === 0 ? <PictureOutlined /> : <PictureOutlined />}
          <span>轮播 {index + 1}{slide.title ? `：${slide.title}` : ''}</span>
        </Space>
      }
      extra={
        canDelete ? (
          <Popconfirm title="确定删除此轮播？" onConfirm={() => onDelete(index)}>
            <Button type="text" danger icon={<DeleteOutlined />} size="small" />
          </Popconfirm>
        ) : null
      }
      style={{ marginBottom: 12 }}
    >
      <Row gutter={12}>
        <Col span={12}>
          <Form.Item label="标题 (H1)" style={{ marginBottom: 8 }}>
            <Input
              value={slide.title || ''}
              onChange={(e) => update('title', e.target.value)}
              placeholder="轮播主标题"
            />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item label="徽章" style={{ marginBottom: 8 }}>
            <Input
              value={slide.badge || ''}
              onChange={(e) => update('badge', e.target.value)}
              placeholder="如：新品上线"
            />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item label="媒体类型" style={{ marginBottom: 8 }}>
            <Select
              value={slide.type || 'image'}
              onChange={(v) => update('type', v)}
              options={[
                { value: 'image', label: '图片' },
                { value: 'video', label: '视频' },
              ]}
            />
          </Form.Item>
        </Col>
      </Row>
      <Form.Item label="副标题" style={{ marginBottom: 8 }}>
        <Input
          value={slide.subtitle || ''}
          onChange={(e) => update('subtitle', e.target.value)}
          placeholder="副标题文字"
        />
      </Form.Item>
      <Form.Item label="描述文字" style={{ marginBottom: 8 }}>
        <TextArea
          rows={2}
          value={slide.description || ''}
          onChange={(e) => update('description', e.target.value)}
          placeholder="显示在标题下方的描述"
        />
      </Form.Item>
      <Row gutter={12}>
        <Col span={12}>
          <Form.Item label="背景图片 URL" style={{ marginBottom: 0 }}>
            <Input
              value={slide.background_image || ''}
              onChange={(e) => update('background_image', e.target.value)}
              placeholder={slide.type === 'video' ? '视频封面图 URL' : '图片/背景 URL'}
            />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item label={slide.type === 'video' ? '视频 URL' : '图片 URL'} style={{ marginBottom: 0 }}>
            <Input
              value={slide.src || ''}
              onChange={(e) => update('src', e.target.value)}
              placeholder={slide.type === 'video' ? '视频 MP4 地址' : '图片地址（覆盖背景）'}
            />
          </Form.Item>
        </Col>
      </Row>
    </Card>
  );
};

// ---------------------------------------------------------------------------
// Main Page Component
// ---------------------------------------------------------------------------

const PageHeroManagement: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeKey, setActiveKey] = useState(HERO_PAGES[0].key);
  const [refreshKey, setRefreshKey] = useState(0);
  const [slides, setSlides] = useState<PageHeroSlide[]>([]);

  // ---- Load slides for current tab ----
  const loadTabData = useCallback(async (key: string) => {
    setLoading(true);
    try {
      const def = HERO_PAGES.find((p) => p.key === key);
      if (!def) return;
      const data = await def.getter();
      setSlides(ensureSlides(data));
    } catch {
      message.error('加载 Hero 配置失败');
      setSlides([createEmptySlide()]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTabData(activeKey);
  }, [activeKey, loadTabData, refreshKey]);

  // ---- Slide mutations ----
  const handleSlideChange = (index: number, slide: PageHeroSlide) => {
    setSlides((prev) => {
      const next = [...prev];
      next[index] = slide;
      return next;
    });
  };

  const handleAddSlide = () => {
    setSlides((prev) => [...prev, createEmptySlide()]);
  };

  const handleDeleteSlide = (index: number) => {
    setSlides((prev) => prev.filter((_, i) => i !== index));
  };

  // ---- Save ----
  const handleSave = async () => {
    const def = HERO_PAGES.find((p) => p.key === activeKey);
    if (!def) return;

    // Validate: at least one slide with title
    const nonEmpty = slides.filter((s) => s.title?.trim());
    if (nonEmpty.length === 0) {
      message.warning('请至少填写一个轮播的标题');
      return;
    }

    setSaving(true);
    try {
      // Clean empty slides (no title)
      const cleanSlides = slides
        .filter((s) => s.title?.trim())
        .map((s) => {
          const clean: PageHeroSlide = { ...s };
          // Remove empty strings
          Object.keys(clean).forEach((k) => {
            const key = k as keyof PageHeroSlide;
            if (clean[key] === '' || clean[key] === undefined) {
              delete clean[key];
            }
          });
          return clean;
        });

      const data = slidesToData(cleanSlides);
      await def.setter(data);
      message.success(`${def.label} Hero 配置已保存（${cleanSlides.length} 张轮播）`);
    } catch {
      message.error('保存失败');
    } finally {
      setSaving(false);
    }
  };

  // ---- Render ----
  const renderSlideEditor = () => {
    const def = HERO_PAGES.find((p) => p.key === activeKey);
    if (!def) return null;

    return (
      <Card
        title={
          <Space>
            {def.icon}
            <span>{def.label} - Hero 轮播配置</span>
          </Space>
        }
        extra={
          <Space>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
              loading={saving}
            >
              保存
            </Button>
          </Space>
        }
      >
        <Text type="secondary" style={{ marginBottom: 16, display: 'block' }}>
          编辑该页面的 Hero 轮播内容。每个轮播可独立设置标题、描述和背景。
          设置 1 张为静态横幅，2 张及以上自动切换为轮播模式。留空的轮播将被忽略。
        </Text>

        {slides.map((slide, i) => (
          <SlideEditor
            key={i}
            slide={slide}
            index={i}
            onChange={handleSlideChange}
            onDelete={handleDeleteSlide}
            canDelete={slides.length > 1}
          />
        ))}

        <Button
          type="dashed"
          icon={<PlusOutlined />}
          onClick={handleAddSlide}
          block
          style={{ marginTop: 8 }}
        >
          添加轮播
        </Button>
      </Card>
    );
  };

  // ---- Tabs ----
  const tabItems = HERO_PAGES.map((def) => ({
    key: def.key,
    label: (
      <span>
        {def.icon}
        <span style={{ marginLeft: 8 }}>{def.label}</span>
      </span>
    ),
    children: null,
  }));

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Title level={2} style={{ margin: 0 }}>
            页面 Hero 管理
          </Title>
        </Col>
        <Col>
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={() => setRefreshKey((k) => k + 1)}
            >
              刷新数据
            </Button>
          </Space>
        </Col>
      </Row>
      <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
        管理各页面的 Hero 轮播横幅。保存后刷新前端页面即可看到效果。
        首页默认使用后台配置的轮播；其他页面未配置时使用默认文案。
      </Text>

      <Row gutter={24}>
        <Col span={5}>
          <Tabs
            activeKey={activeKey}
            onChange={setActiveKey}
            tabPosition="left"
            items={tabItems}
          />
        </Col>
        <Col span={19}>
          <Spin spinning={loading}>
            {renderSlideEditor()}
          </Spin>
        </Col>
      </Row>
    </div>
  );
};

export default PageHeroManagement;
