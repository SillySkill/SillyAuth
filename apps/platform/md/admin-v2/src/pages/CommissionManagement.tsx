/**
 * Commission Management
 *
 * Admin page displaying commission stats cards and commission records table.
 * Supports filtering by status and date range.
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Select,
  DatePicker,
  message,
  Card,
  Statistic,
  Row,
  Col,
  Typography,
  Empty,
  Spin,
} from 'antd';
import {
  DollarOutlined,
  BarChartOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  ReloadOutlined,
  FilterOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getCommissionRecords, getCommissionStats } from '../api/commission';

const { Title } = Typography;
const { RangePicker } = DatePicker;

// ============================================================
// Interfaces
// ============================================================

interface CommissionRecordItem {
  id: number;
  order_id: number;
  content_type: string;
  content_id: number;
  gross_amount: number;
  platform_commission: number;
  creator_share: number;
  settlement_status: 'pending' | 'settled';
  created_at: string;
}

interface CommissionStatsData {
  total_commission: number;
  platform_revenue: number;
  creator_payouts: number;
  pending_payouts: number;
}

// ============================================================
// Component
// ============================================================

const CommissionManagement: React.FC = () => {
  const [records, setRecords] = useState<CommissionRecordItem[]>([]);
  const [stats, setStats] = useState<CommissionStatsData>({
    total_commission: 0,
    platform_revenue: 0,
    creator_payouts: 0,
    pending_payouts: 0,
  });
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const [dateRange, setDateRange] = useState<[string, string] | null>(null);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });

  // ============================================================
  // Data Loading
  // ============================================================

  const loadRecords = useCallback(async (page = 1, pageSize = 20) => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = { page, page_size: pageSize };
      if (statusFilter) params.status = statusFilter;
      if (dateRange) {
        params.date_from = dateRange[0];
        params.date_to = dateRange[1];
      }
      const response = await getCommissionRecords(params);
      const data = response?.data?.items ?? response?.data ?? [];
      const total = response?.data?.total ?? (Array.isArray(data) ? data.length : 0);
      setRecords(Array.isArray(data) ? data : []);
      setPagination({ current: page, pageSize, total });
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : 'Failed to load commission records';
      message.error(msg);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, dateRange]);

  const loadStats = useCallback(async () => {
    try {
      const response = await getCommissionStats();
      if (response?.data) {
        setStats({
          total_commission: response.data.total_commission ?? 0,
          platform_revenue: response.data.platform_revenue ?? 0,
          creator_payouts: response.data.creator_payouts ?? 0,
          pending_payouts: response.data.pending_payouts ?? 0,
        });
      }
    } catch (error: unknown) {
      console.error('Failed to load commission stats', error);
    }
  }, []);

  useEffect(() => {
    loadRecords();
    loadStats();
  }, [loadRecords, loadStats]);

  // ============================================================
  // Handlers
  // ============================================================

  const handleStatusFilterChange = (value: string | undefined) => {
    setStatusFilter(value);
  };

  const handleDateRangeChange = (_: unknown, dateStrings: [string, string]) => {
    setDateRange(dateStrings[0] ? dateStrings : null);
  };

  const handleResetFilters = () => {
    setStatusFilter(undefined);
    setDateRange(null);
  };

  // ============================================================
  // Helpers
  // ============================================================

  const getSettlementStatusTag = (status: string) => {
    const config: Record<string, { color: string; text: string }> = {
      pending: { color: 'orange', text: 'Pending' },
      settled: { color: 'green', text: 'Settled' },
    };
    const info = config[status] || { color: 'default', text: status };
    return <Tag color={info.color}>{info.text}</Tag>;
  };

  const getContentTypeTag = (type: string) => {
    const config: Record<string, { color: string; label: string }> = {
      article: { color: 'blue', label: 'Article' },
      tutorial: { color: 'purple', label: 'Tutorial' },
      skill: { color: 'cyan', label: 'Skill' },
      download: { color: 'geekblue', label: 'Download' },
    };
    const info = config[type] || { color: 'default', label: type };
    return <Tag color={info.color}>{info.label}</Tag>;
  };

  // ============================================================
  // Columns
  // ============================================================

  const columns: ColumnsType<CommissionRecordItem> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
      sorter: true,
    },
    {
      title: 'Order ID',
      dataIndex: 'order_id',
      key: 'order_id',
      width: 100,
    },
    {
      title: 'Content Type',
      dataIndex: 'content_type',
      key: 'content_type',
      width: 130,
      render: (type: string) => getContentTypeTag(type),
      filters: [
        { text: 'Article', value: 'article' },
        { text: 'Tutorial', value: 'tutorial' },
        { text: 'Skill', value: 'skill' },
        { text: 'Download', value: 'download' },
      ],
      onFilter: (value, record) => record.content_type === value,
    },
    {
      title: 'Content ID',
      dataIndex: 'content_id',
      key: 'content_id',
      width: 100,
    },
    {
      title: 'Gross Amount',
      dataIndex: 'gross_amount',
      key: 'gross_amount',
      width: 130,
      sorter: (a, b) => a.gross_amount - b.gross_amount,
      render: (amount: number) =>
        `¥${(amount ?? 0).toFixed(2)}`,
    },
    {
      title: 'Platform Commission',
      dataIndex: 'platform_commission',
      key: 'platform_commission',
      width: 160,
      sorter: (a, b) => a.platform_commission - b.platform_commission,
      render: (amount: number) => (
        <span style={{ color: '#ff4d4f' }}>
          -¥{(amount ?? 0).toFixed(2)}
        </span>
      ),
    },
    {
      title: 'Creator Share',
      dataIndex: 'creator_share',
      key: 'creator_share',
      width: 130,
      sorter: (a, b) => a.creator_share - b.creator_share,
      render: (amount: number) => (
        <span style={{ color: '#52c41a', fontWeight: 600 }}>
          +¥{(amount ?? 0).toFixed(2)}
        </span>
      ),
    },
    {
      title: 'Settlement Status',
      dataIndex: 'settlement_status',
      key: 'settlement_status',
      width: 140,
      render: (status: string) => getSettlementStatusTag(status),
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      sorter: true,
      render: (date: string) => (date ? new Date(date).toLocaleString() : 'N/A'),
    },
  ];

  // ============================================================
  // Render
  // ============================================================

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>Commission Management</Title>
        <p style={{ color: '#888' }}>
          View platform commissions, revenue breakdown, and creator payouts.
        </p>
      </div>

      {/* Commission Stats Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Commission"
              value={stats.total_commission}
              precision={2}
              prefix="¥"
              prefixIcon={<DollarOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Platform Revenue"
              value={stats.platform_revenue}
              precision={2}
              prefix="¥"
              prefixIcon={<BarChartOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Creator Payouts"
              value={stats.creator_payouts}
              precision={2}
              prefix="¥"
              prefixIcon={<TrophyOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Pending Payouts"
              value={stats.pending_payouts}
              precision={2}
              prefix="¥"
              prefixIcon={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Commission Records Table */}
      <Card
        extra={
          <Button
            icon={<ReloadOutlined />}
            onClick={() => loadRecords(pagination.current, pagination.pageSize)}
          >
            Refresh
          </Button>
        }
      >
        {/* Filters Row */}
        <div style={{ marginBottom: 16 }}>
          <Space wrap>
            <span style={{ color: '#888' }}>
              <FilterOutlined /> Filters:
            </span>
            <Select
              allowClear
              placeholder="Status"
              style={{ width: 150 }}
              value={statusFilter}
              onChange={handleStatusFilterChange}
              options={[
                { label: 'Pending', value: 'pending' },
                { label: 'Settled', value: 'settled' },
              ]}
            />
            <RangePicker
              onChange={handleDateRangeChange}
              placeholder={['Start Date', 'End Date']}
            />
            {(statusFilter || dateRange) && (
              <Button onClick={handleResetFilters}>Reset Filters</Button>
            )}
          </Space>
        </div>

        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={records}
            rowKey="id"
            loading={loading}
            onChange={(pag) =>
              loadRecords(pag.current ?? 1, pag.pageSize ?? 20)
            }
            pagination={{
              ...pagination,
              showSizeChanger: true,
              showTotal: (total) => `Total ${total} records`,
            }}
            scroll={{ x: 1200 }}
            locale={{
              emptyText: <Empty description="No commission records found" />,
            }}
          />
        </Spin>
      </Card>
    </div>
  );
};

export default CommissionManagement;
