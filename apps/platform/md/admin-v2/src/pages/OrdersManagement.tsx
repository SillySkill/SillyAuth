import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  Tag,
  Button,
  Modal,
  Card,
  Space,
  Select,
  message,
  Descriptions,
  Typography,
} from 'antd';
import {
  EyeOutlined,
  ReloadOutlined,
  SendOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  getOrders,
  getOrderDetail,
  updateOrderStatus,
} from '../api/store';
import type {
  StoreOrder,
  StoreOrderItem,
  OrderDetail,
} from '../api/store';
import { formatDate, formatCurrency } from '../utils';

const { Title } = Typography;

// ---- Constants ----

const STATUS_MAP: Record<string, { color: string; label: string }> = {
  pending: { color: 'gold', label: '待处理' },
  paid: { color: 'blue', label: '已支付' },
  shipped: { color: 'cyan', label: '已发货' },
  completed: { color: 'green', label: '已完成' },
  cancelled: { color: 'red', label: '已取消' },
};

const STATUS_OPTIONS = [
  { value: '', label: '全部状态' },
  { value: 'pending', label: '待处理' },
  { value: 'paid', label: '已支付' },
  { value: 'shipped', label: '已发货' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' },
];

// ---- Component ----

const OrdersManagement: React.FC = () => {
  // ============================================================
  // State
  // ============================================================

  const [orders, setOrders] = useState<StoreOrder[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });
  const [statusFilter, setStatusFilter] = useState<string>('');

  // Detail modal state
  const [detailVisible, setDetailVisible] = useState(false);
  const [detail, setDetail] = useState<OrderDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [statusUpdating, setStatusUpdating] = useState(false);

  // ============================================================
  // Data Fetching
  // ============================================================

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {
        page: pagination.current,
        page_size: pagination.pageSize,
      };
      if (statusFilter) {
        params.status = statusFilter;
      }
      const response = await getOrders(
        params as Parameters<typeof getOrders>[0]
      );
      if (response.success) {
        setOrders(response.data.items);
        setPagination((prev) => ({
          ...prev,
          total: response.data.total,
        }));
      }
    } catch (error) {
      message.error('加载订单失败');
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, statusFilter]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  // ============================================================
  // Detail Handlers
  // ============================================================

  const handleViewDetail = useCallback(async (orderNo: string) => {
    setDetailVisible(true);
    setDetailLoading(true);
    setDetail(null);
    try {
      const response = await getOrderDetail(orderNo);
      if (response.success) {
        setDetail(response.data);
      }
    } catch (error) {
      message.error('加载订单详情失败');
    } finally {
      setDetailLoading(false);
    }
  }, []);

  const handleCloseDetail = useCallback(() => {
    setDetailVisible(false);
    setDetail(null);
  }, []);

  // ============================================================
  // Status Update
  // ============================================================

  const handleStatusUpdate = useCallback(
    async (orderNo: string, status: string) => {
      setStatusUpdating(true);
      try {
        const response = await updateOrderStatus(orderNo, { status });
        if (response.success) {
          const targetLabel = STATUS_MAP[status]?.label || status;
          message.success(`订单已更新为【${targetLabel}】`);
          fetchOrders();
          if (detail && detail.order.order_no === orderNo) {
            handleViewDetail(orderNo);
          }
        }
      } catch (error) {
        message.error('更新订单状态失败');
      } finally {
        setStatusUpdating(false);
      }
    },
    [fetchOrders, detail, handleViewDetail]
  );

  // ============================================================
  // Filter Handlers
  // ============================================================

  const handleStatusFilterChange = useCallback((value: string) => {
    setStatusFilter(value);
    setPagination((prev) => ({ ...prev, current: 1 }));
  }, []);

  // ============================================================
  // Action Buttons (based on current status)
  // ============================================================

  const renderStatusActions = useCallback(
    (record: StoreOrder) => {
      const buttons: React.ReactNode[] = [];

      buttons.push(
        <Button
          key="view"
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetail(record.order_no)}
        >
          详情
        </Button>
      );

      switch (record.status) {
        case 'pending':
          buttons.push(
            <Button
              key="cancel"
              type="link"
              size="small"
              danger
              icon={<CloseCircleOutlined />}
              onClick={() =>
                Modal.confirm({
                  title: '取消订单',
                  content: `确定要取消订单 ${record.order_no} 吗？`,
                  okText: '确认取消',
                  cancelText: '返回',
                  okType: 'danger',
                  onOk: () =>
                    handleStatusUpdate(record.order_no, 'cancelled'),
                })
              }
            >
              取消
            </Button>
          );
          break;
        case 'paid':
          buttons.push(
            <Button
              key="ship"
              type="link"
              size="small"
              icon={<SendOutlined />}
              onClick={() =>
                Modal.confirm({
                  title: '确认发货',
                  content: `确定将订单 ${record.order_no} 标记为已发货吗？`,
                  okText: '确认发货',
                  cancelText: '取消',
                  onOk: () =>
                    handleStatusUpdate(record.order_no, 'shipped'),
                })
              }
            >
              发货
            </Button>,
            <Button
              key="cancel"
              type="link"
              size="small"
              danger
              icon={<CloseCircleOutlined />}
              onClick={() =>
                Modal.confirm({
                  title: '取消订单',
                  content: `确定要取消订单 ${record.order_no} 吗？`,
                  okText: '确认取消',
                  cancelText: '返回',
                  okType: 'danger',
                  onOk: () =>
                    handleStatusUpdate(record.order_no, 'cancelled'),
                })
              }
            >
              取消
            </Button>
          );
          break;
        case 'shipped':
          buttons.push(
            <Button
              key="complete"
              type="link"
              size="small"
              icon={<CheckCircleOutlined />}
              style={{ color: '#52c41a' }}
              onClick={() =>
                Modal.confirm({
                  title: '确认完成',
                  content: `确定将订单 ${record.order_no} 标记为已完成吗？`,
                  okText: '确认完成',
                  cancelText: '取消',
                  onOk: () =>
                    handleStatusUpdate(record.order_no, 'completed'),
                })
              }
            >
              完成
            </Button>
          );
          break;
        default:
          // completed, cancelled: no extra action buttons
          break;
      }

      return <Space size="small">{buttons}</Space>;
    },
    [handleViewDetail, handleStatusUpdate]
  );

  // ============================================================
  // Table Columns
  // ============================================================

  const columns: ColumnsType<StoreOrder> = [
    {
      title: '订单号',
      dataIndex: 'order_no',
      key: 'order_no',
      width: 200,
      ellipsis: true,
    },
    {
      title: '金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 140,
      render: (amount: number) => (
        <span style={{ fontWeight: 600, color: '#cf1322' }}>
          {formatCurrency(amount, 'CNY')}
        </span>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const config = STATUS_MAP[status] || {
          color: 'default',
          label: status,
        };
        return <Tag color={config.color}>{config.label}</Tag>;
      },
    },
    {
      title: '收件人',
      dataIndex: 'shipping_name',
      key: 'shipping_name',
      width: 120,
      render: (name: string) => name || '-',
    },
    {
      title: '联系电话',
      dataIndex: 'shipping_phone',
      key: 'shipping_phone',
      width: 140,
      render: (phone: string) => phone || '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => formatDate(date),
    },
    {
      title: '操作',
      key: 'actions',
      width: 220,
      fixed: 'right',
      render: (_: unknown, record: StoreOrder) => renderStatusActions(record),
    },
  ];

  // ============================================================
  // Detail Modal - Items Table Columns
  // ============================================================

  const itemColumns: ColumnsType<StoreOrderItem> = [
    {
      title: '商品名称',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 200,
      ellipsis: true,
    },
    {
      title: '单价',
      dataIndex: 'unit_price',
      key: 'unit_price',
      width: 120,
      render: (price: number) => formatCurrency(price, 'CNY'),
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 80,
    },
    {
      title: '小计',
      dataIndex: 'subtotal',
      key: 'subtotal',
      width: 120,
      render: (subtotal: number) => (
        <span style={{ fontWeight: 600 }}>
          {formatCurrency(subtotal, 'CNY')}
        </span>
      ),
    },
  ];

  // ============================================================
  // Render
  // ============================================================

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        订单管理
      </Title>

      <Card
        extra={
          <Space>
            <Button icon={<ReloadOutlined />} onClick={fetchOrders}>
              刷新
            </Button>
          </Space>
        }
      >
        <div style={{ marginBottom: 16 }}>
          <Space>
            <span>状态筛选：</span>
            <Select
              value={statusFilter}
              onChange={handleStatusFilterChange}
              style={{ width: 140 }}
              options={STATUS_OPTIONS}
            />
          </Space>
        </div>

        <Table<StoreOrder>
          columns={columns}
          dataSource={orders}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1100 }}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 个订单`,
            onChange: (page, pageSize) =>
              setPagination({
                current: page,
                pageSize,
                total: pagination.total,
              }),
          }}
          locale={{ emptyText: '暂无订单' }}
        />
      </Card>

      {/* Order Detail Modal */}
      <Modal
        title={`订单详情 - ${detail?.order?.order_no || ''}`}
        open={detailVisible}
        onCancel={handleCloseDetail}
        width={800}
        footer={
          <Button onClick={handleCloseDetail}>关闭</Button>
        }
        destroyOnClose
        loading={detailLoading}
      >
        {detail && (
          <div>
            <Descriptions
              bordered
              column={2}
              size="small"
              style={{ marginBottom: 24 }}
            >
              <Descriptions.Item label="订单号" span={2}>
                {detail.order.order_no}
              </Descriptions.Item>
              <Descriptions.Item label="订单状态">
                <Tag color={STATUS_MAP[detail.order.status]?.color}>
                  {STATUS_MAP[detail.order.status]?.label ||
                    detail.order.status}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="总金额">
                <span style={{ fontWeight: 600, color: '#cf1322' }}>
                  {formatCurrency(detail.order.total_amount, 'CNY')}
                </span>
              </Descriptions.Item>
              <Descriptions.Item label="支付方式">
                {detail.order.payment_method || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="支付单号">
                {detail.order.payment_no || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="收件人">
                {detail.order.shipping_name || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="联系电话">
                {detail.order.shipping_phone || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="收货地址" span={2}>
                {detail.order.shipping_address || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {formatDate(detail.order.created_at)}
              </Descriptions.Item>
              <Descriptions.Item label="更新时间">
                {formatDate(detail.order.updated_at || '')}
              </Descriptions.Item>
            </Descriptions>

            <Title level={5} style={{ marginBottom: 12 }}>
              订单商品
            </Title>
            <Table<StoreOrderItem>
              columns={itemColumns}
              dataSource={detail.items}
              rowKey="id"
              pagination={false}
              size="small"
              locale={{ emptyText: '暂无商品' }}
              summary={(pageData) => {
                const total = pageData.reduce(
                  (sum, item) => sum + item.subtotal,
                  0
                );
                return (
                  <Table.Summary.Row>
                    <Table.Summary.Cell index={0} colSpan={3} align="right">
                      <strong>合计：</strong>
                    </Table.Summary.Cell>
                    <Table.Summary.Cell index={1}>
                      <strong style={{ color: '#cf1322' }}>
                        {formatCurrency(total, 'CNY')}
                      </strong>
                    </Table.Summary.Cell>
                  </Table.Summary.Row>
                );
              }}
            />
          </div>
        )}

        {!detail && !detailLoading && (
          <div
            style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}
          >
            暂无数据
          </div>
        )}
      </Modal>
    </div>
  );
};

export default OrdersManagement;
