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
      const msg = error instanceof Error ? error.message : 'Failed to load SEO config';
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
      message.success('SEO settings saved successfully');
    } catch (error: unknown) {
      if (error instanceof Error && error.message?.includes('Validation')) return;
      const msg = error instanceof Error ? error.message : 'Failed to save SEO settings';
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
          <GlobalOutlined /> Global SEO
        </span>
      ),
      children: (
        <Row gutter={24}>
          <Col span={24}>
            <Form.Item
              name="site_title"
              label="Site Title"
              rules={[{ required: true, message: 'Please enter the site title' }]}
            >
              <Input placeholder="e.g. SillyMD - Medical Knowledge Platform" />
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item
              name="meta_description"
              label="Meta Description"
              rules={[{ required: true, message: 'Please enter meta description' }]}
            >
              <TextArea rows={3} placeholder="Brief description for search engines (150-160 chars recommended)" />
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item name="meta_keywords" label="Meta Keywords">
              <Input placeholder="Comma-separated keywords: medical, health, education" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="google_analytics_id" label="Google Analytics ID">
              <Input placeholder="UA-XXXXX-Y or G-XXXXXXXX" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="baidu_analytics_id" label="Baidu Analytics ID">
              <Input placeholder="Baidu Tongji ID" />
            </Form.Item>
          </Col>
        </Row>
      ),
    },
    {
      key: 'og',
      label: (
        <span>
          <ShareAltOutlined /> OG Meta (Open Graph)
        </span>
      ),
      children: (
        <Row gutter={24}>
          <Col span={24}>
            <Form.Item name="og_title" label="OG Title">
              <Input placeholder="Open Graph title for social sharing" />
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item name="og_description" label="OG Description">
              <TextArea rows={3} placeholder="Open Graph description for social sharing" />
            </Form.Item>
          </Col>
          <Col span={24}>
            <Form.Item name="og_image" label="OG Image URL">
              <Input placeholder="https://example.com/og-image.png (1200x630 recommended)" />
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
          <ApartmentOutlined /> Sitemap
        </span>
      ),
      children: (
        <Row gutter={24}>
          <Col span={24}>
            <Form.Item
              name="auto_generate_sitemap"
              label="Auto-Generate Sitemap"
              valuePropName="checked"
              extra="Automatically generate and update sitemap.xml"
            >
              <Switch checkedChildren="On" unCheckedChildren="Off" />
            </Form.Item>
          </Col>
        </Row>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>SEO Settings</Title>
        <p style={{ color: '#888' }}>
          Configure global SEO metadata, Open Graph tags, robots.txt, and sitemap settings.
        </p>
      </div>

      <Spin spinning={loading}>
        <Card
          extra={
            <Space>
              <Button icon={<ReloadOutlined />} onClick={loadConfig}>
                Reload
              </Button>
              <Button
                type="primary"
                icon={<SaveOutlined />}
                onClick={handleSave}
                loading={saving}
              >
                Save Settings
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
