/**
 * 佣金配置管理页面
 * Commission Configuration Management
 */
import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  InputNumber,
  Input,
  Select,
  Switch,
  message,
  Popconfirm,
  Card,
  Statistic,
  Row,
  Col,
  Tooltip,
  Divider
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SaveOutlined,
  PercentageOutlined,
  DollarOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  SettingOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { commissionApi } from '@/api/commission';
import { paymentApi } from '@/api/payment';

interface CommissionSetting {
  id: number;
  scope: string;
  scope_id: number | null;
  commission_rate: number;
  min_commission_rate: number;
  max_commission_rate: number;
  creator_share_rate: number;
  is_custom: boolean;
  is_active: boolean;
  valid_from: string | null;
  valid_until: string | null;
  description: string;
  created_at: string;
}

const CommissionManagement: React.FC = () => {
  const [settings, setSettings] = useState<CommissionSetting[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [currentSetting, setCurrentSetting] = useState<CommissionSetting | null>(null);
  const [form] = Form.useForm();

  // 统计数据
  const [stats, setStats] = useState({
    totalOrders: 0,
    totalRevenue: 0,
    platformRevenue: 0,
    creatorRevenue: 0
  });

  useEffect(() => {
    loadSettings();
    loadStats();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const response = await commissionApi.list();
      if (response.success) {
        setSettings(response.data);
      }
    } catch (error) {
      message.error('加载配置失败');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await paymentApi.getRevenueStats({ days: 30 });
      if (response.success) {
        setStats({
          totalOrders: response.data.total_orders,
          totalRevenue: response.data.total_revenue,
          platformRevenue: response.data.total_revenue * 0.3,  // 粗略计算
          creatorRevenue: response.data.total_revenue * 0.7
        });
      }
    } catch (error) {
      console.error('加载统计失败', error);
    }
  };

  const openModal = (setting?: CommissionSetting) => {
    if (setting) {
      setCurrentSetting(setting);
      form.setFieldsValue(setting);
    } else {
      setCurrentSetting(null);
      form.resetFields();
    }
    setModalVisible(true);
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();

      // 验证佣金比例
      if (values.commission_rate < values.min_commission_rate ||
          values.commission_rate > values.max_commission_rate) {
        message.error('佣金比例必须在最小值和最大值之间');
        return;
      }

      if (currentSetting) {
        await commissionApi.update(currentSetting.id, values);
        message.success('更新成功');
      } else {
        await commissionApi.create(values);
        message.success('创建成功');
      }

      setModalVisible(false);
      loadSettings();
    } catch (error) {
      message.error('保存失败');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await commissionApi.delete(id);
      message.success('删除成功');
      loadSettings();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleToggleActive = async (id: number, isActive: boolean) => {
    try {
      await commissionApi.update(id, { is_active: !isActive });
      message.success('更新成功');
      loadSettings();
    } catch (error) {
      message.error('更新失败');
    }
  };

  const getScopeText = (scope: string) => {
    const map = {
      'global': '全局',
      'category': '分类',
      'user': '用户',
      'product': '产品',
      'top_creators': '优质创作者'
    };
    return map[scope] || scope;
  };

  const columns: ColumnsType<CommissionSetting> = [
    {
      title: '配置范围',
      dataIndex: 'scope',
      key: 'scope',
      width: 150,
      render: (scope: string, record: CommissionSetting) => (
        <div>
          <div style={{ fontWeight: 500 }}>{getScopeText(scope)}</div>
          {record.scope_id && <div style={{ fontSize: 12, color: '#999' }}>ID: {record.scope_id}</div>}
        </div>
      )
    },
    {
      title: '平台佣金',
      dataIndex: 'commission_rate',
      key: 'commission_rate',
      width: 150,
      render: (rate: number) => (
        <Statistic
          title=""
          value={rate}
          suffix="%"
          precision={2}
          valueStyle={{
            color: rate === 0 ? '#52c41a' : rate > 50 ? '#ff4d4f' : '#1890ff'
          }}
        />
      )
    },
    {
      title: '创作者分成',
      dataIndex: 'creator_share_rate',
      key: 'creator_share_rate',
      width: 150,
      render: (rate: number) => (
        <Statistic
          title=""
          value={rate}
          suffix="%"
          precision={2}
          valueStyle={{ color: '#52c41a' }}
        />
      )
    },
    {
      title: '范围',
      key: 'range',
      width: 150,
      render: (_, record: CommissionSetting) => (
        <Space direction="vertical" size={4}>
          <div style={{ fontSize: 12 }}>
            最小: <span style={{ color: '#52c41a' }}>{record.min_commission_rate}%</span>
          </div>
          <div style={{ fontSize: 12 }}>
            最大: <span style={{ color: '#ff4d4f' }}>{record.max_commission_rate}%</span>
          </div>
        </Space>
      )
    },
    {
      title: '类型',
      dataIndex: 'is_custom',
      key: 'is_custom',
      width: 100,
      render: (isCustom: boolean) => (
        <Tag color={isCustom ? 'purple' : 'blue'}>
          {isCustom ? '自定义' : '默认'}
        </Tag>
      )
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean, record: CommissionSetting) => (
        <Switch
          size="small"
          checkedChildren="启用"
          unCheckedChildren="禁用"
          checked={isActive}
          onChange={() => handleToggleActive(record.id, isActive)}
          disabled={record.scope === 'global'}  // 全局配置不允许禁用
        />
      )
    },
    {
      title: '有效期',
      key: 'validity',
      width: 200,
      render: (_, record: CommissionSetting) => (
        <Space direction="vertical" size={4}>
          {record.valid_from && (
            <div style={{ fontSize: 12 }}>
              从: {new Date(record.valid_from).toLocaleDateString()}
            </div>
          )}
          {record.valid_until && (
            <div style={{ fontSize: 12 }}>
              到: {new Date(record.valid_until).toLocaleDateString()}
            </div>
          )}
          {!record.valid_from && !record.valid_until && (
            <div style={{ fontSize: 12, color: '#999' }}>永久有效</div>
          )}
        </Space>
      )
    },
    {
      title: '说明',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      fixed: 'right',
      render: (_, record: CommissionSetting) => (
        <Space>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => openModal(record)}
            />
          </Tooltip>
          {record.is_custom && (
            <Popconfirm
              title="确定要删除这个配置吗？"
              onConfirm={() => handleDelete(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          )}
        </Space>
      )
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h2>平台佣金配置</h2>
        <p style={{ color: 'var(--text-light)'}}>
          设置平台佣金比例，支持全局、分类、用户等不同层级的配置
        </p>
      </div>

      {/* 收入统计 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总订单数"
              value={stats.totalOrders}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总收入"
              value={stats.totalRevenue}
              prefix="¥"
              precision={2}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平台收入"
              value={stats.platformRevenue}
              prefix="¥"
              precision={2}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="创作者收入"
              value={stats.creatorRevenue}
              prefix="¥"
              precision={2}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 配置列表 */}
      <Card
        title="佣金配置列表"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => openModal()}
          >
            新增配置
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={settings}
          rowKey="id"
          loading={loading}
          pagination={false}
          scroll={{ x: 1400 }}
        />
      </Card>

      {/* 配置说明 */}
      <Card
        title={<span><InfoCircleOutlined /> 配置说明</span>}
        style={{ marginTop: 24 }}
      >
        <Row gutter={16}>
          <Col span={12}>
            <h4>优先级规则</h4>
            <ol style={{ paddingLeft: 16, lineHeight: '1.8' }}>
              <li>产品自定义配置（最高优先级）</li>
              <li>用户自定义配置</li>
              <li>优质创作者配置（月销售额≥1000元）</li>
              <li>分类配置</li>
              <li>全局配置（默认30%，最低优先级）</li>
            </ol>
          </Col>
          <Col span={12}>
            <h4>佣金设置建议</h4>
            <ul style={{ paddingLeft: 16, lineHeight: '1.8' }}>
              <li><strong>0% 佣金</strong>：平台不收取任何费用，适用于公益活动或特殊扶持</li>
              <li><strong>10-20% 佣金</strong>：低佣金率，鼓励优质创作者</li>
              <li><strong>25-30% 佣金</strong>：标准佣金率，平衡平台和创作者收益</li>
              <li><strong>40-50% 佣金</strong>：高佣金率，适用于需要平台深度扶持的内容</li>
              <li><strong>100% 佣金</strong>：完全由平台所有，适用于官方内容</li>
            </ul>
          </Col>
        </Row>
      </Card>

      {/* 编辑对话框 */}
      <Modal
        title={currentSetting ? '编辑佣金配置' : '新增佣金配置'}
        open={modalVisible}
        onOk={handleSave}
        onCancel={() => setModalVisible(false)}
        width={600}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="配置范围"
            name="scope"
            rules={[{ required: true, message: '请选择配置范围' }]}
          >
            <Select placeholder="选择范围">
              <Option value="global">全局配置</Option>
              <Option value="category">分类配置</Option>
              <Option value="user">用户配置</Option>
              <Option value="product">产品配置</Option>
              <Option value="top_creators">优质创作者</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="平台佣金比例（%）"
            name="commission_rate"
            rules={[
              { required: true, message: '请输入佣金比例' },
              { type: 'number', min: 0, max: 100, message: '范围 0-100' }
            ]}
            extra={
              <Space>
                <span>创作者分成: </span>
                <Statistic
                  value={100}
                  suffix="%"
                  valueStyle={{ fontSize: 14 }}
                />
                <span> - 佣金比例</span>
              </Space>
            }
          >
            <InputNumber
              min={0}
              max={100}
              precision={2}
              style={{ width: '100%' }}
              placeholder="例如：30.00"
            />
          </Form.Item>

          <Form.Item
            label="最小佣金比例（%）"
            name="min_commission_rate"
            rules={[{ required: true, message: '请输入最小值' }]}
          >
            <InputNumber
              min={0}
              max={100}
              precision={2}
              style={{ width: '100%' }}
              placeholder="例如：0.00"
            />
          </Form.Item>

          <Form.Item
            label="最大佣金比例（%）"
            name="max_commission_rate"
            rules={[{ required: true, message: '请输入最大值' }]}
          >
            <InputNumber
              min={0}
              max={100}
              precision={2}
              style={{ width: '100%' }}
              placeholder="例如：100.00"
            />
          </Form.Item>

          <Form.Item
            label="是否为自定义规则"
            name="is_custom"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item label="说明">
            <Input.TextArea
              rows={3}
              placeholder="配置说明，例如：教程分类优惠佣金比例"
            />
          </Form.Item>

          <Form.Item label="有效期开始">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item label="有效期结束">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="是否启用"
            name="is_active"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default CommissionManagement;
