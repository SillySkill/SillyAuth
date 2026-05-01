/**
 * SEO Settings
 *
 * Admin page for configuring global SEO metadata, OG tags, robots.txt, and sitemap.
 * Uses antd Card + Collapse sections and loads/saves via direct API calls.
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Button,
  Space,
  Input,
  Switch,
  message,
  Card,
  Typography,
  Collapse,
  Form,
  Row,
  Col,
  Spin,
} from 'antd';
import {
  SaveOutlined,
  ReloadOutlined,
  GlobalOutlined,
  ShareAltOutlined,
  RobotOutlined,
  ApartmentOutlined,
} from '@ant-design/icons';
import api from '../api/index';

const { Title } = Typography;
const { TextArea } = Input;

// ============================================================
// Interfaces
// ============================================================

interface SEOFormValues {
  site_title: string;
  meta_description: string;
  meta_keywords: string;
  google_analytics_id: string;
  baidu_analytics_id: string;
  og_title: string;
  og_description: string;
  og_image: string;
  robots_txt: string;
  auto_generate_sitemap: boolean;
}

// ============================================================
// Component
// ============================================================

const SEOSettings: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form] = Form.useForm<SEOFormValues>();

  // ============================================================
  // Data Loading
  // ============================================================

  const loadConfig = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('/cms/seo');
      const data = response?.data ?? response ?? {};
      form.setFieldsValue({
        site_title: data.site_title || '',
        meta_description: data.meta_description || '',
        meta_keywords: data.meta_keywords || '',
        google_analytics_id: data.google_analytics_id || '',
        baidu_analytics_id: data.baidu_analytics_id || '',
        og_title: data.og_title || '',
        og_description: data.og_description || '',
        og_image: data.og_image || '',
        robots_txt: data.robots_txt || '',
        auto_generate_sitemap: data.auto_generate_sitemap ?? false,
      });
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : '加载SEO配置失败';
      message.error(msg);
    } finally {
      setLoading(false);
    }
  }, [form]);

  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  // ============================================================
  // Handlers
  // ============================================================

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setSaving(true);
      await api.put('/cms/seo', values);
      message.success('SEO设置保存成功');
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) return;
      const msg = error instanceof Error ? error.message : '保存SEO设置失败';
      message.error(msg);
    } finally {
      setSaving(false);
    }
  };

  // ============================================================
  // Render
  // ============================================================

  const collapseItems = [
    {
      key: 'global',
      label: (
        <span>
          <GlobalOutlined /> 全局SEO
        </span>
      ),
      children: (
        <Row gutter={24}>
          <Col span={24}>
            <Form.Item
              name="site_title"
              label="站点标题"
              rules={[{ required: true, message: '请输入站点标题' }]}
            >
              <Input placeholder="例如：SillyMD - 医学知识平台" />
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item
              name="meta_description"
              label="元描述"
              rules={[{ required: true, message: '请输入元描述' }]}
            >
              <TextArea rows={3} placeholder="搜索引擎的简短描述（建议150-160个字符）" />
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item name="meta_keywords" label="元关键词">
              <Input placeholder="逗号分隔的关键词：医学，健康，教育" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="google_analytics_id" label="Google Analytics ID">
              <Input placeholder="UA-XXXXX-Y 或 G-XXXXXXXX" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="baidu_analytics_id" label="百度统计ID">
              <Input placeholder="百度统计ID" />
            </Form.Item>
          </Col>
        </Row>
      ),
    },
    {
      key: 'og',
      label: (
        <span>
          <ShareAltOutlined /> OG元数据（Open Graph）
        </span>
      ),
      children: (
        <Row gutter={24}>
          <Col span={24}>
            <Form.Item name="og_title" label="OG标题">
              <Input placeholder="社交分享的Open Graph标题" />
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item name="og_description" label="OG描述">
              <TextArea rows={3} placeholder="社交分享的Open Graph描述" />
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item name="og_image" label="OG图片URL">
              <Input placeholder="https://example.com/og-image.png（建议1200x630）" />
            </Form.Item>
          </Col>
        </Row>
      ),
    },
    {
      key: 'robots',
      label: (
        <span>
          <RobotOutlined /> Robots.txt
        </span>
      ),
      children: (
        <Form.Item name="robots_txt">
          <TextArea
            rows={10}
            placeholder={`User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: https://example.com/sitemap.xml`}
          />
        </Form.Item>
      ),
    },
    {
      key: 'sitemap',
      label: (
        <span>
          <ApartmentOutlined /> 站点地图
        </span>
      ),
      children: (
        <Row gutter={24}>
          <Col span={24}>
            <Form.Item
              name="auto_generate_sitemap"
              label="自动生成站点地图"
              valuePropName="checked"
              extra="自动生成并更新 sitemap.xml"
            >
              <Switch checkedChildren="开" unCheckedChildren="关" />
            </Form.Item>
          </Col>
        </Row>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>SEO设置</Title>
        <p style={{ color: '#888' }}>
          配置全局SEO元数据、Open Graph标签、robots.txt和站点地图设置。
        </p>
      </div>

      <Spin spinning={loading}>
        <Card
          extra={
            <Space>
              <Button icon={<ReloadOutlined />} onClick={loadConfig}>
                重新加载
              </Button>
              <Button
                type="primary"
                icon={<SaveOutlined />}
                onClick={handleSave}
                loading={saving}
              >
                保存设置
              </Button>
            </Space>
          }
        >
          <Form form={form} layout="vertical">
            <Collapse
              defaultActiveKey={['global', 'og', 'robots', 'sitemap']}
              items={collapseItems}
            />
          </Form>
        </Card>
      </Spin>
    </div>
  );
};

export default SEOSettings;
