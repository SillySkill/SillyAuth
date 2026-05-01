/**
 * Module Management
 *
 * Admin page for enabling/disabling system modules.
 * Shows module details and allows toggling module status.
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Switch,
  message,
  Card,
  Typography,
  Empty,
  Spin,
  Modal,
  Statistic,
  Row,
  Col,
} from 'antd';
import {
  ReloadOutlined,
  AppstoreOutlined,
  PoweroffOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getModules, enableModule, disableModule } from '../api/modules';

const { Title } = Typography;

// ============================================================
// Interfaces
// ============================================================

interface ModuleItem {
  id: number;
  name: string;
  version: string;
  status: 'enabled' | 'disabled';
  dependencies: string[];
  description: string;
  key?: string;
  is_enabled?: boolean;
}

// ============================================================
// Component
// ============================================================

const ModuleManagement: React.FC = () => {
  const [modules, setModules] = useState<ModuleItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [toggling, setToggling] = useState<Record<number, boolean>>({});

  // ============================================================
  // Data Loading
  // ============================================================

  const loadModules = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getModules();
      const rawData = response?.data ?? [];

      // Normalize data shape
      const normalized: ModuleItem[] = (Array.isArray(rawData) ? rawData : []).map(
        (m: Record<string, unknown>) => ({
          id: m.id as number,
          name: (m.name || m.key) as string,
          version: (m.version as string) || '1.0.0',
          status: ((m.is_enabled || m.status) === true || (m.is_enabled || m.status) === 'enabled'
            ? 'enabled'
            : 'disabled') as 'enabled' | 'disabled',
          dependencies: Array.isArray(m.dependencies) ? (m.dependencies as string[]) : [],
          description: (m.description as string) || '',
          key: m.key as string,
          is_enabled: m.is_enabled as boolean,
        })
      );
      setModules(normalized);
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : '加载模块失败';
      message.error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadModules();
  }, [loadModules]);

  // ============================================================
  // Handlers
  // ============================================================

  const handleToggleModule = async (record: ModuleItem, checked: boolean) => {
    const moduleId = record.id;
    setToggling((prev) => ({ ...prev, [moduleId]: true }));

    try {
      if (checked) {
        await enableModule(moduleId);
        message.success(`模块 "${record.name}" 已启用`);
      } else {
        await disableModule(moduleId);
        message.success(`模块 "${record.name}" 已禁用`);
      }
      loadModules();
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : '切换失败';
      message.error(msg);
    } finally {
      setToggling((prev) => ({ ...prev, [moduleId]: false }));
    }
  };

  // ============================================================
  // Stats
  // ============================================================

  const enabledCount = modules.filter((m) => m.status === 'enabled').length;
  const disabledCount = modules.filter((m) => m.status === 'disabled').length;

  // ============================================================
  // Columns
  // ============================================================

  const columns: ColumnsType<ModuleItem> = [
    {
      title: '模块ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 180,
      ellipsis: true,
    },
    {
      title: '版本号',
      dataIndex: 'version',
      key: 'version',
      width: 100,
      render: (version: string) => <Tag>{version || '1.0.0'}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string, record: ModuleItem) => {
        const enabled = status === 'enabled';
        return (
          <Space>
            <Tag color={enabled ? 'green' : 'red'}>{enabled ? '已启用' : '已禁用'}</Tag>
            <Switch
              checked={enabled}
              size="small"
              loading={toggling[record.id]}
              onChange={(checked) => handleToggleModule(record, checked)}
            />
          </Space>
        );
      },
    },
    {
      title: '依赖项',
      dataIndex: 'dependencies',
      key: 'dependencies',
      width: 250,
      render: (deps: string[]) =>
        deps && deps.length > 0 ? (
          <Space size={[4, 4]} wrap>
            {deps.map((dep: string) => (
              <Tag key={dep} color="purple">
                {dep}
              </Tag>
            ))}
          </Space>
        ) : (
          <Tag color="default">无</Tag>
        ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: (_: unknown, record: ModuleItem) => {
        const enabled = record.status === 'enabled';
        return (
          <Button
            type={enabled ? 'default' : 'primary'}
            danger={enabled}
            size="small"
            icon={<PoweroffOutlined />}
            loading={toggling[record.id]}
            onClick={() => handleToggleModule(record, !enabled)}
          >
            {enabled ? '禁用' : '启用'}
          </Button>
        );
      },
    },
  ];

  // ============================================================
  // Render
  // ============================================================

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>模块管理</Title>
        <p style={{ color: '#888' }}>
          启用或禁用系统模块并查看依赖关系。
        </p>
      </div>

      {/* Module Stats */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="模块总数"
              value={modules.length}
              prefix={<AppstoreOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="已启用"
              value={enabledCount}
              valueStyle={{ color: '#52c41a' }}
              suffix={`/ ${modules.length}`}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="已禁用"
              value={disabledCount}
              valueStyle={{ color: '#ff4d4f' }}
              suffix={`/ ${modules.length}`}
            />
          </Card>
        </Col>
      </Row>

      {/* Modules Table */}
      <Card
        extra={
          <Button icon={<ReloadOutlined />} onClick={loadModules}>
            刷新
          </Button>
        }
      >
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={modules}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个模块`,
            }}
            scroll={{ x: 1000 }}
            locale={{
              emptyText: <Empty description="暂无模块" />,
            }}
          />
        </Spin>
      </Card>
    </div>
  );
};

export default ModuleManagement;
