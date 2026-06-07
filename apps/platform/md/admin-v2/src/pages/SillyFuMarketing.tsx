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
  Divider,
} from 'antd';
import type { FormListFieldData } from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  SaveOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import {
  getSillyFuProduct,
  saveSillyFuProduct,
  getSillyFuVariants,
  saveSillyFuVariants,
  getSillyFuOpenClaw,
  saveSillyFuOpenClaw,
} from '../api/sillyfuMarketing';
import type {
  SillyFuProductData,
  SillyFuOpenClawData,
  VariantItem,
} from '../api/sillyfuMarketing';

const { TextArea } = Input;
const { Title, Text } = Typography;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function ensureArray<T>(val: T[] | undefined | null): T[] {
  return Array.isArray(val) ? val : [];
}

const FIELD_STYLE: React.CSSProperties = { width: '100%' };

// ---------------------------------------------------------------------------
// Generic array-editor row (label/value pair)
// ---------------------------------------------------------------------------

interface LabelValueRowProps {
  name: number;
  restField: Record<string, unknown>;
  remove: () => void;
  labelPlaceholder?: string;
  valuePlaceholder?: string;
  labelName?: string;
  valueName?: string;
}

const LabelValueRow: React.FC<LabelValueRowProps> = ({
  name,
  restField,
  remove,
  labelPlaceholder = '标签',
  valuePlaceholder = '值',
  labelName = 'label',
  valueName = 'value',
}) => (
  <Card
    size="small"
    style={{ marginBottom: 8 }}
    extra={
      <Button
        danger
        size="small"
        icon={<DeleteOutlined />}
        onClick={remove}
      />
    }
  >
    <Row gutter={12}>
      <Col span={10}>
        <Form.Item
          {...restField}
          name={[name, labelName]}
          rules={[{ required: true, message: '必填' }]}
          style={{ marginBottom: 0 }}
        >
          <Input placeholder={labelPlaceholder} />
        </Form.Item>
      </Col>
      <Col span={14}>
        <Form.Item
          {...restField}
          name={[name, valueName]}
          style={{ marginBottom: 0 }}
        >
          <Input placeholder={valuePlaceholder} />
        </Form.Item>
      </Col>
    </Row>
  </Card>
);

// ---------------------------------------------------------------------------
// Array-editor section wrapper
// ---------------------------------------------------------------------------

type FieldWithRest = FormListFieldData & { restField: Record<string, unknown> };

interface ArraySectionProps {
  name: string;
  children: (field: FieldWithRest, remove: (index: number) => void) => React.ReactNode;
  addLabel?: string;
}

const ArraySection: React.FC<ArraySectionProps> = ({
  name,
  children,
  addLabel = '添加',
}) => (
  <Form.List name={name}>
    {(fields, { add, remove }) => (
      <>
        {fields.map((field) => {
          const { key, name, ...restField } = field;
          return children({ ...field, restField } as FieldWithRest, remove);
        })}
        <Button
          type="dashed"
          onClick={() => add()}
          block
          icon={<PlusOutlined />}
          style={{ marginTop: 4 }}
        >
          {addLabel}
        </Button>
      </>
    )}
  </Form.List>
);

// ---------------------------------------------------------------------------
// Main Page Component
// ---------------------------------------------------------------------------

const SillyFuMarketing: React.FC = () => {
  // ---- State ----
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);
  const [productKey, setProductKey] = useState(0);  // force Form remount on load

  const [productForm] = Form.useForm();
  const [variantsForm] = Form.useForm();
  const [openclawForm] = Form.useForm();

  // ---- Load data ----

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [product, variants, openclaw] = await Promise.all([
        getSillyFuProduct().catch(() => ({} as SillyFuProductData)),
        getSillyFuVariants().catch(() => [] as VariantItem[]),
        getSillyFuOpenClaw().catch(() => ({} as SillyFuOpenClawData)),
      ]);

      loadedProductRef.current = product;
      loadedOpenClawRef.current = openclaw;

      // Flatten nested agents for the form
      const flatProduct: Record<string, unknown> = { ...product };
      if (product.agents) {
        flatProduct.agent_openclaw_name = product.agents.openclaw?.name || '';
        flatProduct.agent_openclaw_color = product.agents.openclaw?.color || '';
        flatProduct.agent_openclaw_color_hex = product.agents.openclaw?.color_hex || '';
        flatProduct.agent_openclaw_version = product.agents.openclaw?.version || '';
        flatProduct.agent_openclaw_tech_stack = product.agents.openclaw?.tech_stack || '';
        flatProduct.agent_openclaw_strength = product.agents.openclaw?.strength || '';
        flatProduct.agent_openclaw_good_at = product.agents.openclaw?.good_at || '';
        flatProduct.agent_hermes_name = product.agents.hermes?.name || '';
        flatProduct.agent_hermes_color = product.agents.hermes?.color || '';
        flatProduct.agent_hermes_color_hex = product.agents.hermes?.color_hex || '';
        flatProduct.agent_hermes_version = product.agents.hermes?.version || '';
        flatProduct.agent_hermes_tech_stack = product.agents.hermes?.tech_stack || '';
        flatProduct.agent_hermes_strength = product.agents.hermes?.strength || '';
        flatProduct.agent_hermes_good_at = product.agents.hermes?.good_at || '';
      }
      // Flatten showcase
      if (product.showcase) {
        flatProduct.showcase_title = product.showcase.title || '';
        flatProduct.showcase_desc = product.showcase.desc || '';
        flatProduct.showcase_image = product.showcase.image || '';
        flatProduct.showcase_features = ensureArray(product.showcase.features);
      } else {
        flatProduct.showcase_title = '';
        flatProduct.showcase_desc = '';
        flatProduct.showcase_image = '';
        flatProduct.showcase_features = [];
      }

      productForm.setFieldsValue(flatProduct);
      variantsForm.setFieldsValue({ items: ensureArray(variants) });
      openclawForm.setFieldsValue({
        ...openclaw,
        ai_features: ensureArray(openclaw.ai_features),
      });

      setProductKey((k) => k + 1);
    } catch {
      message.error('加载 SillyFu 配置数据失败');
    } finally {
      setLoading(false);
    }
  }, [productForm, variantsForm, openclawForm]);

  useEffect(() => {
    loadData();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // ---- Save helpers ----

  // Keep reference to loaded data so saves can merge partial form values
  const loadedProductRef = React.useRef<SillyFuProductData>({});
  const loadedOpenClawRef = React.useRef<SillyFuOpenClawData>({});

  const saveProductSection = async () => {
    setSaving('product');
    try {
      const values = await productForm.validateFields();
      // Start from currently loaded DB data (preserves fields not in form state)
      const data: SillyFuProductData = { ...loadedProductRef.current };
      // Overlay form values (skip empty arrays that signal un-rendered Form.List)
      for (const [k, v] of Object.entries(values)) {
        if (v === undefined) continue;
        if (Array.isArray(v) && v.length === 0 && Array.isArray((data as Record<string, unknown>)[k]) && ((data as Record<string, unknown>)[k] as unknown[]).length > 0) continue;
        (data as Record<string, unknown>)[k] = v;
      }
      // Rebuild agents from flat fields
      data.agents = {
        openclaw: {
          name: values.agent_openclaw_name || (data.agents?.openclaw?.name || ''),
          color: values.agent_openclaw_color || (data.agents?.openclaw?.color || ''),
          color_hex: values.agent_openclaw_color_hex || (data.agents?.openclaw?.color_hex || ''),
          version: values.agent_openclaw_version || (data.agents?.openclaw?.version || ''),
          tech_stack: values.agent_openclaw_tech_stack || (data.agents?.openclaw?.tech_stack || ''),
          strength: values.agent_openclaw_strength || (data.agents?.openclaw?.strength || ''),
          good_at: values.agent_openclaw_good_at || (data.agents?.openclaw?.good_at || ''),
        },
        hermes: {
          name: values.agent_hermes_name || (data.agents?.hermes?.name || ''),
          color: values.agent_hermes_color || (data.agents?.hermes?.color || ''),
          color_hex: values.agent_hermes_color_hex || (data.agents?.hermes?.color_hex || ''),
          version: values.agent_hermes_version || (data.agents?.hermes?.version || ''),
          tech_stack: values.agent_hermes_tech_stack || (data.agents?.hermes?.tech_stack || ''),
          strength: values.agent_hermes_strength || (data.agents?.hermes?.strength || ''),
          good_at: values.agent_hermes_good_at || (data.agents?.hermes?.good_at || ''),
        },
      };
      // Rebuild showcase
      data.showcase = {
        title: values.showcase_title || (data.showcase?.title || ''),
        desc: values.showcase_desc || (data.showcase?.desc || ''),
        image: values.showcase_image || (data.showcase?.image || ''),
        features: ensureArray(values.showcase_features).length > 0 ? ensureArray(values.showcase_features) : ensureArray(data.showcase?.features),
      };
      // Clean up flat fields from data
      const flatKeys = Object.keys(data).filter(
        (k) =>
          k.startsWith('agent_openclaw_') ||
          k.startsWith('agent_hermes_') ||
          k.startsWith('showcase_')
      );
      flatKeys.forEach((k) => delete (data as Record<string, unknown>)[k]);

      await saveSillyFuProduct(data);
      message.success('产品信息已保存');
    } catch (err: unknown) {
      if (
        err &&
        typeof err === 'object' &&
        'errorFields' in (err as Record<string, unknown>)
      ) {
        message.error('请检查必填字段');
        return;
      }
      message.error('保存失败');
    } finally {
      setSaving(null);
    }
  };

  const saveVariantsSection = async () => {
    setSaving('variants');
    try {
      const values = await variantsForm.validateFields();
      await saveSillyFuVariants(ensureArray(values.items));
      message.success('规格变体已保存');
    } catch {
      message.error('保存失败');
    } finally {
      setSaving(null);
    }
  };

  const saveOpenClawSection = async () => {
    setSaving('openclaw');
    try {
      const values = await openclawForm.validateFields();
      // Merge with loaded data to preserve fields not in form (e.g. badges)
      const data: SillyFuOpenClawData = { ...loadedOpenClawRef.current };
      for (const [k, v] of Object.entries(values)) {
        if (v === undefined) continue;
        if (Array.isArray(v) && v.length === 0 && Array.isArray((data as Record<string, unknown>)[k]) && ((data as Record<string, unknown>)[k] as unknown[]).length > 0) continue;
        (data as Record<string, unknown>)[k] = v;
      }
      await saveSillyFuOpenClaw(data);
      message.success('Hero 配置已保存');
    } catch {
      message.error('保存失败');
    } finally {
      setSaving(null);
    }
  };

  // ---- Section card wrapper ----

  const SectionCard: React.FC<{
    title: string;
    onSave: () => void;
    saving?: boolean;
    children: React.ReactNode;
  }> = ({ title, onSave, saving: cardSaving, children }) => (
    <Card
      title={title}
      extra={
        <Button
          type="primary"
          icon={<SaveOutlined />}
          onClick={onSave}
          loading={cardSaving}
        >
          保存
        </Button>
      }
    >
      {children}
    </Card>
  );

  // ---- Loading / error states ----

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <Spin size="large" tip="加载 SillyFu 配置..." />
      </div>
    );
  }

  // ---- Tab items ----

  const tabItems = [
    // ================================================================
    // Tab 0: Hero / 顶部 (openclaw — 页面头部配置)
    // ================================================================
    {
      key: 'hero',
      label: 'Hero / 顶部',
      children: (
        <SectionCard
          title="Hero 顶部区域配置"
          onSave={saveOpenClawSection}
          saving={saving === 'openclaw'}
        >
          <Text type="secondary" style={{ marginBottom: 16, display: 'block' }}>
            编辑页面头部的视频、封面图、标题和 AI 能力卡片
          </Text>
          <Form form={openclawForm} layout="vertical" key={`oc_${productKey}`}>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="store_name"
                  label="商城名称"
                  rules={[{ required: true }]}
                >
                  <Input placeholder="OpenClaw 商城" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="subtitle" label="副标题">
                  <Input placeholder="官方授权线上销售渠道" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="hero_video" label="Hero 视频 URL">
                  <Input placeholder="/assets/hero/hero.mp4" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="hero_poster" label="Hero 封面图 URL（移动端显示）">
                  <Input placeholder="/static/img/hero-poster.png" />
                </Form.Item>
              </Col>
            </Row>
            <Divider>AI 能力卡片</Divider>
            <Text type="secondary" style={{ marginBottom: 8, display: 'block' }}>
              AI 智能能力展示卡片（Hero 下方横向排列）
            </Text>
            <ArraySection name="ai_features" addLabel="添加 AI 能力">
              {(field, remove) => (
                <Card
                  key={field.key}
                  size="small"
                  style={{ marginBottom: 8 }}
                  extra={
                    <Button
                      danger
                      size="small"
                      icon={<DeleteOutlined />}
                      onClick={() => remove(field.name)}
                    />
                  }
                >
                  <Row gutter={12}>
                    <Col span={6}>
                      <Form.Item
                        {...field.restField}
                        name={[field.name, 'icon']}
                        label="图标"
                        rules={[{ required: true }]}
                        style={{ marginBottom: 8 }}
                      >
                        <Input placeholder="fa-brain" />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item
                        {...field.restField}
                        name={[field.name, 'title']}
                        label="标题"
                        rules={[{ required: true }]}
                        style={{ marginBottom: 8 }}
                      >
                        <Input placeholder="智能对话" />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        {...field.restField}
                        name={[field.name, 'desc']}
                        label="描述"
                        style={{ marginBottom: 8 }}
                      >
                        <Input placeholder="自然语言交互，理解复杂需求" />
                      </Form.Item>
                    </Col>
                  </Row>
                </Card>
              )}
            </ArraySection>
          </Form>
        </SectionCard>
      ),
    },
    // ================================================================
    // Tab 1: 基本信息 (product)
    // ================================================================
    {
      key: 'basic',
      label: '基本信息',
      children: (
        <SectionCard
          title="产品基本信息"
          onSave={saveProductSection}
          saving={saving === 'product'}
        >
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="name"
                label="产品名称"
                rules={[{ required: true }]}
              >
                <Input placeholder="傻福虾盘" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="subtitle" label="副标题">
                <Input placeholder="AI USB 智能U盘" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="ai_system" label="AI 系统">
                <Input placeholder="OpenClaw GPT" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="description" label="产品描述">
            <TextArea rows={3} placeholder="产品详细描述" />
          </Form.Item>
          <Row gutter={16}>
            <Col span={6}>
              <Form.Item name="capacity_range" label="容量范围">
                <Input placeholder="128G - 1TB" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="speed" label="读取速度">
                <Input placeholder="500MB/s" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="interface" label="接口">
                <Input placeholder="USB-A + USB-C" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="dimensions" label="尺寸">
                <Input placeholder="65 x 18 x 8 mm" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={6}>
              <Form.Item name="material" label="外壳材质">
                <Input placeholder="铝合金" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="colors" label="颜色选项">
                <Input placeholder="太空灰 / 银色" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="warranty" label="质保期限">
                <Input placeholder="2年" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="compatible" label="系统兼容">
                <Input placeholder="Windows / macOS / Linux / Android" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="serial" label="序列号">
                <Input placeholder="OC-2024-001" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="production_count" label="产量">
                <Input placeholder="10,000+" />
              </Form.Item>
            </Col>
          </Row>
        </SectionCard>
      ),
    },
    // ================================================================
    // Tab 2: 技术参数 (product)
    // ================================================================
    {
      key: 'tech_specs',
      label: '技术参数',
      children: (
        <SectionCard
          title="技术参数"
          onSave={saveProductSection}
          saving={saving === 'product'}
        >
          <Text type="secondary" style={{ marginBottom: 16, display: 'block' }}>
            技术规格表，每项包含标签和值
          </Text>
          <ArraySection name="tech_specs" addLabel="添加规格项">
            {(field, remove) => (
              <LabelValueRow
                key={field.key}
                name={field.name}
                restField={field.restField}
                remove={() => remove(field.name)}
                labelPlaceholder="产品名称"
                valuePlaceholder="傻福虾盘"
              />
            )}
          </ArraySection>
        </SectionCard>
      ),
    },
    // ================================================================
    // Tab 3: 图库 (product)
    // ================================================================
    {
      key: 'gallery',
      label: '图库',
      children: (
        <SectionCard
          title="产品图库"
          onSave={saveProductSection}
          saving={saving === 'product'}
        >
          <Text type="secondary" style={{ marginBottom: 16, display: 'block' }}>
            产品图库轮播图片，每张图片包含 URL 和描述
          </Text>
          <ArraySection name="images" addLabel="添加图片">
            {(field, remove) => (
              <Card
                key={field.key}
                size="small"
                style={{ marginBottom: 8 }}
                extra={
                  <Button
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={() => remove(field.name)}
                  />
                }
              >
                <Row gutter={12}>
                  <Col span={18}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'src']}
                      label="图片URL"
                      rules={[{ required: true, message: '请输入图片URL' }]}
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="/static/img/sillyclaw/product.png" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'alt']}
                      label="替代文字"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="正面" />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            )}
          </ArraySection>
        </SectionCard>
      ),
    },
    // ================================================================
    // Tab 4: 产品展示 (product)
    // ================================================================
    {
      key: 'showcase',
      label: '产品展示',
      children: (
        <SectionCard
          title="产品展示区"
          onSave={saveProductSection}
          saving={saving === 'product'}
        >
          <Row gutter={16}>
            <Col span={16}>
              <Form.Item name="showcase_title" label="标题">
                <Input placeholder="双接口设计" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="showcase_image" label="展示图片URL">
                <Input placeholder="/static/img/showcase.png" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="showcase_desc" label="描述">
            <TextArea rows={2} placeholder="USB-A 和 USB-C 双接口..." />
          </Form.Item>
          <Divider>特性列表</Divider>
          <ArraySection name="showcase_features" addLabel="添加特性">
            {(field, remove) => (
              <Row
                key={field.key}
                gutter={8}
                align="middle"
                style={{ marginBottom: 8 }}
              >
                <Col flex="auto">
                  <Form.Item
                    {...field.restField}
                    name={[field.name]}
                    style={{ marginBottom: 0 }}
                  >
                    <Input placeholder="支持Windows和Mac无缝切换" />
                  </Form.Item>
                </Col>
                <Col>
                  <Button
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={() => remove(field.name)}
                  />
                </Col>
              </Row>
            )}
          </ArraySection>
        </SectionCard>
      ),
    },
    // ================================================================
    // Tab 5: 双Agent系统 (product)
    // ================================================================
    {
      key: 'agents',
      label: '双Agent',
      children: (
        <SectionCard
          title="双 Agent 系统"
          onSave={saveProductSection}
          saving={saving === 'product'}
        >
          <Title level={5} style={{ color: '#E53935' }}>
            OpenClaw (红色系)
          </Title>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="agent_openclaw_name"
                label="名称"
                rules={[{ required: true }]}
              >
                <Input placeholder="OpenClaw" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="agent_openclaw_color" label="色系名称">
                <Input placeholder="红色系" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="agent_openclaw_color_hex" label="色值">
                <Input placeholder="#E53935" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="agent_openclaw_version" label="版本">
                <Input placeholder="v2.0" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="agent_openclaw_tech_stack" label="技术栈">
                <Input placeholder="GPT-4 + Claude" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="agent_openclaw_strength" label="优势">
                <Input placeholder="代码生成" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="agent_openclaw_good_at" label="擅长">
            <Input placeholder="代码编写、架构设计、调试" />
          </Form.Item>

          <Divider />
          <Title level={5} style={{ color: '#00ACC1' }}>
            Hermes (蓝色系)
          </Title>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="agent_hermes_name"
                label="名称"
                rules={[{ required: true }]}
              >
                <Input placeholder="Hermes" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="agent_hermes_color" label="色系名称">
                <Input placeholder="蓝色系" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="agent_hermes_color_hex" label="色值">
                <Input placeholder="#00ACC1" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="agent_hermes_version" label="版本">
                <Input placeholder="v2.0" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="agent_hermes_tech_stack" label="技术栈">
                <Input placeholder="GPT-4 + Claude" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="agent_hermes_strength" label="优势">
                <Input placeholder="文案审核" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="agent_hermes_good_at" label="擅长">
            <Input placeholder="内容审查、安全审计、风格优化" />
          </Form.Item>
        </SectionCard>
      ),
    },
    // ================================================================
    // Tab 6: 运行模式 (product)
    // ================================================================
    {
      key: 'modes',
      label: '运行模式',
      children: (
        <SectionCard
          title="三种运行模式"
          onSave={saveProductSection}
          saving={saving === 'product'}
        >
          <ArraySection name="modes" addLabel="添加模式">
            {(field, remove) => (
              <Card
                key={field.key}
                size="small"
                style={{ marginBottom: 8 }}
                extra={
                  <Button
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={() => remove(field.name)}
                  />
                }
              >
                <Row gutter={12}>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'name']}
                      label="名称"
                      rules={[{ required: true }]}
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="独立模式" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'icon']}
                      label="图标"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="fa-user" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'color']}
                      label="颜色"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="#E53935" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'desc']}
                      label="描述"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="单一Agent独立工作" />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            )}
          </ArraySection>
        </SectionCard>
      ),
    },
    // ================================================================
    // Tab 7: 质量体系 (product)
    // ================================================================
    {
      key: 'quality',
      label: '质量体系',
      children: (
        <SectionCard
          title="质量保障体系"
          onSave={saveProductSection}
          saving={saving === 'product'}
        >
          <Title level={5}>协作缺陷</Title>
          <Text type="secondary" style={{ marginBottom: 8, display: 'block' }}>
            展示为什么需要协作模式的四个关键缺陷
          </Text>
          <ArraySection name="why_collab" addLabel="添加缺陷">
            {(field, remove) => (
              <Card
                key={field.key}
                size="small"
                style={{ marginBottom: 8 }}
                extra={
                  <Button
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={() => remove(field.name)}
                  />
                }
              >
                <Row gutter={12}>
                  <Col span={8}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'icon']}
                      label="图标"
                      rules={[{ required: true }]}
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="fa-exclamation-triangle" />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'issue']}
                      label="问题"
                      rules={[{ required: true }]}
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="幻觉问题" />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'desc']}
                      label="描述"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="单一Agent可能产生不准确输出" />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            )}
          </ArraySection>

          <Divider />
          <Title level={5}>六维质量指标</Title>
          <Text type="secondary" style={{ marginBottom: 8, display: 'block' }}>
            质量保障体系的六个维度
          </Text>
          <ArraySection name="quality_dimensions" addLabel="添加维度">
            {(field, remove) => (
              <Card
                key={field.key}
                size="small"
                style={{ marginBottom: 8 }}
                extra={
                  <Button
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={() => remove(field.name)}
                  />
                }
              >
                <Row gutter={12}>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'icon']}
                      label="图标"
                      rules={[{ required: true }]}
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="fa-check" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'title']}
                      label="标题"
                      rules={[{ required: true }]}
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="正确性" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'desc']}
                      label="描述"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="交叉验证输出" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'effect']}
                      label="效果"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="准确率提升30%" />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            )}
          </ArraySection>
        </SectionCard>
      ),
    },
    // ================================================================
    // Tab 8: 安全保障 (product)
    // ================================================================
    {
      key: 'security',
      label: '安全保障',
      children: (
        <SectionCard
          title="安全保障体系"
          onSave={saveProductSection}
          saving={saving === 'product'}
        >
          <Title level={5}>四维安全保障</Title>
          <Text type="secondary" style={{ marginBottom: 8, display: 'block' }}>
            四个安全保障维度
          </Text>
          <ArraySection name="security_dimensions" addLabel="添加安全维度">
            {(field, remove) => (
              <Card
                key={field.key}
                size="small"
                style={{ marginBottom: 8 }}
                extra={
                  <Button
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={() => remove(field.name)}
                  />
                }
              >
                <Row gutter={12}>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'icon']}
                      label="图标"
                      rules={[{ required: true }]}
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="fa-shield-alt" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'title']}
                      label="标题"
                      rules={[{ required: true }]}
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="沙盒执行" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'desc']}
                      label="描述"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="隔离代码运行" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'effect']}
                      label="效果"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="防止系统级影响" />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            )}
          </ArraySection>

          <Divider />
          <Title level={5}>安全审计细则</Title>
          <Text type="secondary" style={{ marginBottom: 8, display: 'block' }}>
            详细安全审计条目
          </Text>
          <ArraySection name="security_items" addLabel="添加审计项">
            {(field, remove) => (
              <Card
                key={field.key}
                size="small"
                style={{ marginBottom: 8 }}
                extra={
                  <Button
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={() => remove(field.name)}
                  />
                }
              >
                <Row gutter={12}>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'type']}
                      label="类型"
                      rules={[{ required: true }]}
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="文件操作" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'desc']}
                      label="描述"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="读写文件时需要用户确认" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'action']}
                      label="动作"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="需要确认" />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            )}
          </ArraySection>
        </SectionCard>
      ),
    },
    // ================================================================
    // Tab 9: 色彩系统 (product)
    // ================================================================
    {
      key: 'colors',
      label: '色彩系统',
      children: (
        <SectionCard
          title="四色视觉系统"
          onSave={saveProductSection}
          saving={saving === 'product'}
        >
          <Text type="secondary" style={{ marginBottom: 16, display: 'block' }}>
            四种颜色对应不同运行状态，用于Visual Feedback
          </Text>
          <ArraySection name="color_system" addLabel="添加颜色模式">
            {(field, remove) => (
              <Card
                key={field.key}
                size="small"
                style={{ marginBottom: 8 }}
                extra={
                  <Button
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={() => remove(field.name)}
                  />
                }
              >
                <Row gutter={12}>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'mode']}
                      label="模式"
                      rules={[{ required: true }]}
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="协作模式" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'color']}
                      label="颜色"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="#E53935" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'border']}
                      label="边框颜色"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="#E53935" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'indicator']}
                      label="指示器"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="红色边框" />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            )}
          </ArraySection>
        </SectionCard>
      ),
    },
    // ================================================================
    // Tab 10: 使用场景 (product)
    // ================================================================
    {
      key: 'use_cases',
      label: '使用场景',
      children: (
        <SectionCard
          title="适用场景"
          onSave={saveProductSection}
          saving={saving === 'product'}
        >
          <Text type="secondary" style={{ marginBottom: 16, display: 'block' }}>
            不同场景推荐不同运行模式
          </Text>
          <ArraySection name="use_cases" addLabel="添加场景">
            {(field, remove) => (
              <Card
                key={field.key}
                size="small"
                style={{ marginBottom: 8 }}
                extra={
                  <Button
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={() => remove(field.name)}
                  />
                }
              >
                <Row gutter={12}>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'scene']}
                      label="场景"
                      rules={[{ required: true }]}
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="代码开发" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'mode']}
                      label="推荐模式"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="协作模式" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'mode_icon']}
                      label="模式图标"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="fa-code" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'desc']}
                      label="描述"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="OpenClaw编写，Hermes审查" />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            )}
          </ArraySection>
        </SectionCard>
      ),
    },
    // ================================================================
    // Tab 11: 产品实拍 (product)
    // ================================================================
    {
      key: 'photos',
      label: '产品实拍',
      children: (
        <SectionCard
          title="产品实拍照"
          onSave={saveProductSection}
          saving={saving === 'product'}
        >
          <Text type="secondary" style={{ marginBottom: 16, display: 'block' }}>
            产品实物照片墙，每张照片包含 URL、描述和标题
          </Text>
          <ArraySection name="photos" addLabel="添加照片">
            {(field, remove) => (
              <Card
                key={field.key}
                size="small"
                style={{ marginBottom: 8 }}
                extra={
                  <Button
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                    onClick={() => remove(field.name)}
                  />
                }
              >
                <Row gutter={12}>
                  <Col span={12}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'src']}
                      label="图片URL"
                      rules={[{ required: true }]}
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="/static/img/photo1.jpg" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'alt']}
                      label="替代文字"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="正面视图" />
                    </Form.Item>
                  </Col>
                  <Col span={6}>
                    <Form.Item
                      {...field.restField}
                      name={[field.name, 'caption']}
                      label="标题"
                      style={{ marginBottom: 8 }}
                    >
                      <Input placeholder="精致工艺" />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
            )}
          </ArraySection>
        </SectionCard>
      ),
    },
    // ================================================================
    // Tab 12: 规格变体 (variants — separate config item)
    // ================================================================
    {
      key: 'variants',
      label: '规格变体',
      children: (
        <SectionCard
          title="规格变体展示"
          onSave={saveVariantsSection}
          saving={saving === 'variants'}
        >
          <Text type="secondary" style={{ marginBottom: 16, display: 'block' }}>
            展示用规格信息（注意：实际价格由「商城管理→商品管理」控制）
          </Text>
          <Form form={variantsForm} layout="vertical" key={`variants_${productKey}`}>
            <ArraySection name="items" addLabel="添加变体">
              {(field, remove) => (
                <Card
                  key={field.key}
                  size="small"
                  style={{ marginBottom: 8 }}
                  extra={
                    <Button
                      danger
                      size="small"
                      icon={<DeleteOutlined />}
                      onClick={() => remove(field.name)}
                    />
                  }
                >
                  <Row gutter={12}>
                    <Col span={6}>
                      <Form.Item
                        {...field.restField}
                        name={[field.name, 'capacity']}
                        label="容量"
                        rules={[{ required: true }]}
                        style={{ marginBottom: 8 }}
                      >
                        <Input placeholder="128G" />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item
                        {...field.restField}
                        name={[field.name, 'color']}
                        label="颜色"
                        style={{ marginBottom: 8 }}
                      >
                        <Input placeholder="太空灰" />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item
                        {...field.restField}
                        name={[field.name, 'price']}
                        label="价格标签"
                        style={{ marginBottom: 8 }}
                      >
                        <Input placeholder="¥ 479" />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item
                        {...field.restField}
                        name={[field.name, 'badge']}
                        label="徽章"
                        style={{ marginBottom: 8 }}
                      >
                        <Input placeholder="热卖" />
                      </Form.Item>
                    </Col>
                  </Row>
                  <Form.Item
                    {...field.restField}
                    name={[field.name, 'tags']}
                    label="标签 (逗号分隔)"
                    style={{ marginBottom: 8 }}
                    getValueFromEvent={(e) =>
                      e.target.value
                        ? e.target.value.split(',').map((s: string) => s.trim())
                        : []
                    }
                    getValueProps={(v: string[]) => ({
                      value: Array.isArray(v) ? v.join(', ') : '',
                    })}
                  >
                    <Input placeholder="USB-A, USB-C, 高速" />
                  </Form.Item>
                </Card>
              )}
            </ArraySection>
          </Form>
        </SectionCard>
      ),
    },
  ];

  // ---- Render ----

  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 24,
        }}
      >
        <Title level={2} style={{ margin: 0 }}>
          SillyFu 营销管理
        </Title>
        <Button icon={<ReloadOutlined />} onClick={loadData}>
          刷新数据
        </Button>
      </div>
      <Text
        type="secondary"
        style={{ display: 'block', marginBottom: 24 }}
      >
        编辑产品页营销内容。每个标签页对应公开页面上的一个分区，修改后请点击「保存」按钮。
        价格和库存请前往「商城管理→商品管理」编辑。
      </Text>

      <Form
        form={productForm}
        layout="vertical"
        key={`product_${productKey}`}
      >
        <Tabs
          defaultActiveKey="hero"
          tabPosition="left"
          style={{ minHeight: 500 }}
          items={tabItems}
        />
      </Form>
    </div>
  );
};

export default SillyFuMarketing;
