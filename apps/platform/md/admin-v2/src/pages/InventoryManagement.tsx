import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  Tag,
  Button,
  Modal,
  Card,
  Space,
  Select,
  Input,
  Switch,
  message,
  Form,
  InputNumber,
  Divider,
  Typography,
} from 'antd';
import {
  PlusOutlined,
  MinusOutlined,
  SwapOutlined,
  HistoryOutlined,
  WarningOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getInventory, adjustStock, getStockLogs } from '../api/store';
import type { InventoryItem, StockLog, StockAdjustRequest } from '../api/store';
import { formatDate, formatCurrency } from '../utils';

const { TextArea } = Input;
const { Title } = Typography;

// ---- Constants ----

const CHANGE_TYPE_MAP: Record<string, { label: string; color: string }> = {
  in: { label: '入库', color: 'green' },
  out: { label: '出库', color: 'red' },
  adjust: { label: '盘点', color: 'blue' },
  order_deduct: { label: '订单扣减', color: 'orange' },
  order_cancel: { label: '订单取消', color: 'purple' },
};

// ---- Component ----

const InventoryManagement: React.FC = () => {
  // ===== Inventory Table State =====
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });
  const [searchText, setSearchText] = useState('');
  const [lowStockOnly, setLowStockOnly] = useState(false);

  // ===== Stock Adjust Modal State =====
  const [adjustModalVisible, setAdjustModalVisible] = useState(false);
  const [adjustingProduct, setAdjustingProduct] = useState<InventoryItem | null>(null);
  const [adjustSubmitting, setAdjustSubmitting] = useState(false);
  const [adjustForm] = Form.useForm();

  // ===== Stock Log Modal State =====
  const [logModalVisible, setLogModalVisible] = useState(false);
  const [logProductKey, setLogProductKey] = useState('');
  const [logs, setLogs] = useState<StockLog[]>([]);
  const [logsLoading, setLogsLoading] = useState(false);
  const [logPagination, setLogPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });

  // ============================================================
  // Fetch Inventory
  // ============================================================

  const fetchInventory = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {
        page: pagination.current,
        page_size: pagination.pageSize,
      };
      if (searchText.trim()) {
        params.search = searchText.trim();
      }
      if (lowStockOnly) {
        params.low_stock_only = true;
      }

      const response = await getInventory(params as any);
      if (response.success) {
        setInventory(response.data.items);
        setPagination((prev) => ({
          ...prev,
          total: response.data.total,
        }));
      }
    } catch (error) {
      message.error('加载库存数据失败');
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, searchText, lowStockOnly]);

  useEffect(() => {
    fetchInventory();
  }, [fetchInventory]);

  // ============================================================
  // Stock Adjust Handlers
  // ============================================================

  const handleOpenAdjust = (record: InventoryItem) => {
    setAdjustingProduct(record);
    adjustForm.resetFields();
    adjustForm.setFieldsValue({
      change_type: undefined,
      quantity: undefined,
      note: '',
    });
    setAdjustModalVisible(true);
  };

  const handleAdjustSubmit = async () => {
    if (!adjustingProduct) return;
    setAdjustSubmitting(true);
    try {
      const values = await adjustForm.validateFields();
      const data: StockAdjustRequest = {
        change_type: values.change_type,
        quantity: values.quantity,
        note: values.note || undefined,
      };

      await adjustStock(adjustingProduct.id as any, data);
      message.success(
        `${CHANGE_TYPE_MAP[values.change_type]?.label || '操作'}成功`
      );
      setAdjustModalVisible(false);
      fetchInventory();
    } catch (error: any) {
      if (error?.errorFields) return;
      message.error('库存操作失败');
    } finally {
      setAdjustSubmitting(false);
    }
  };

  // ============================================================
  // Stock Log Handlers
  // ============================================================

  const fetchStockLogs = useCallback(async () => {
    if (!adjustingProduct) return;
    setLogsLoading(true);
    try {
      const response = await getStockLogs(adjustingProduct.id as any, {
        page: logPagination.current,
        page_size: logPagination.pageSize,
      });
      if (response.success) {
        setLogs(response.data.items);
        setLogPagination((prev) => ({
          ...prev,
          total: response.data.total,
        }));
      }
    } catch (error) {
      message.error('加载库存日志失败');
    } finally {
      setLogsLoading(false);
    }
  }, [adjustingProduct, logPagination.current, logPagination.pageSize]);

  useEffect(() => {
    if (logModalVisible && adjustingProduct) {
      fetchStockLogs();
    }
  }, [logModalVisible, fetchStockLogs]);

  const handleOpenLogs = (record: InventoryItem) => {
    setAdjustingProduct(record);
    setLogProductKey(record.product_key);
    setLogPagination({ current: 1, pageSize: 10, total: 0 });
    setLogs([]);
    setLogModalVisible(true);
  };

  // ============================================================
  // Render Helpers
  // ============================================================

  const renderStockCount = (stock: number) => {
    if (stock === -1) {
      return <span style={{ color: '#8c8c8c' }}>无限</span>;
    }
    if (stock >= 0 && stock < 10) {
      return (
        <span style={{ color: '#ff4d4f', fontWeight: 600 }}>
          <WarningOutlined style={{ marginRight: 4 }} />
          {stock}
        </span>
      );
    }
    return <span>{stock}</span>;
  };

  const renderPrice = (price: number) => (
    <span style={{ fontWeight: 600, color: '#cf1322' }}>
      {formatCurrency(price, 'CNY')}
    </span>
  );

  const renderChangeTypeTag = (type: string) => {
    const info = CHANGE_TYPE_MAP[type];
    if (!info) return <Tag>{type}</Tag>;
    return <Tag color={info.color}>{info.label}</Tag>;
  };

  // ============================================================
  // Inventory Table Columns
  // ============================================================

  const inventoryColumns: ColumnsType<InventoryItem> = [
    {
      title: '产品标识',
      dataIndex: 'product_key',
      key: 'product_key',
      width: 160,
      render: (key: string) => (
        <Tag color="geekblue" style={{ fontFamily: 'monospace' }}>
          {key}
        </Tag>
      ),
    },
    {
      title: '商品名称',
      dataIndex: 'name_zh',
      key: 'name_zh',
      width: 200,
      ellipsis: true,
    },
    {
      title: '库存',
      dataIndex: 'stock_count',
      key: 'stock_count',
      width: 100,
      sorter: (a, b) => a.stock_count - b.stock_count,
      render: (stock: number) => renderStockCount(stock),
    },
    {
      title: '销量',
      dataIndex: 'sold_count',
      key: 'sold_count',
      width: 90,
      sorter: (a, b) => a.sold_count - b.sold_count,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 130,
      sorter: (a, b) => a.price - b.price,
      render: (price: number) => renderPrice(price),
    },
    {
      title: '商品集合',
      dataIndex: 'collection_name',
      key: 'collection_name',
      width: 150,
      render: (name: string) =>
        name ? (
          <Tag color="blue">{name}</Tag>
        ) : (
          <Tag color="default">未分类</Tag>
        ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (_: unknown, record: InventoryItem) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<SwapOutlined />}
            onClick={() => handleOpenAdjust(record)}
          >
            调整
          </Button>
          <Button
            type="link"
            size="small"
            icon={<HistoryOutlined />}
            onClick={() => handleOpenLogs(record)}
          >
            日志
          </Button>
        </Space>
      ),
    },
  ];

  // ============================================================
  // Stock Log Table Columns
  // ============================================================

  const logColumns: ColumnsType<StockLog> = [
    {
      title: '变更类型',
      dataIndex: 'change_type',
      key: 'change_type',
      width: 110,
      render: (type: string) => renderChangeTypeTag(type),
    },
    {
      title: '变动数量',
      dataIndex: 'change_quantity',
      key: 'change_quantity',
      width: 100,
      render: (qty: number) => {
        const color = qty > 0 ? '#52c41a' : qty < 0 ? '#ff4d4f' : 'inherit';
        const prefix = qty > 0 ? '+' : '';
        return (
          <span style={{ color, fontWeight: 600 }}>
            {prefix}
            {qty}
          </span>
        );
      },
    },
    {
      title: '库存变化',
      key: 'stock_range',
      width: 180,
      render: (_: unknown, record: StockLog) => (
        <span>
          <span style={{ color: '#8c8c8c' }}>{record.stock_before}</span>
          <span style={{ margin: '0 8px', color: '#bfbfbf' }}>{'→'}</span>
          <span>{record.stock_after}</span>
        </span>
      ),
    },
    {
      title: '来源',
      dataIndex: 'source',
      key: 'source',
      width: 100,
      render: (src: string) => <Tag>{src}</Tag>,
    },
    {
      title: '备注',
      dataIndex: 'note',
      key: 'note',
      ellipsis: true,
      render: (note: string) => note || '-',
    },
    {
      title: '操作时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => formatDate(date),
    },
  ];

  // ============================================================
  // Render
  // ============================================================

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        库存管理
      </Title>

      {/* Inventory Table */}
      <Card
        extra={
          <Space size="middle" wrap>
            <Input.Search
              placeholder="搜索产品标识或名称"
              allowClear
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onSearch={() => {
                setPagination((prev) => ({ ...prev, current: 1 }));
                fetchInventory();
              }}
              style={{ width: 260 }}
            />
            <Space>
              <WarningOutlined style={{ color: '#faad14' }} />
              <span>仅显示低库存</span>
              <Switch
                checked={lowStockOnly}
                onChange={(checked) => {
                  setLowStockOnly(checked);
                  setPagination((prev) => ({ ...prev, current: 1 }));
                }}
              />
            </Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={() => {
                setPagination((prev) => ({ ...prev, current: 1 }));
                fetchInventory();
              }}
            >
              刷新
            </Button>
          </Space>
        }
      >
        <Table<InventoryItem>
          columns={inventoryColumns}
          dataSource={inventory}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1000 }}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 个商品`,
            onChange: (page, pageSize) =>
              setPagination({ current: page, pageSize, total: pagination.total }),
          }}
          locale={{ emptyText: '暂无库存数据' }}
        />
      </Card>

      {/* Stock Adjust Modal */}
      <Modal
        title={
          <Space>
            <SwapOutlined />
            <span>库存操作</span>
            {adjustingProduct && (
              <>
                <Divider type="vertical" />
                <Tag color="geekblue">{adjustingProduct.product_key}</Tag>
                <span>{adjustingProduct.name_zh}</span>
                <Divider type="vertical" />
                <span style={{ color: '#8c8c8c' }}>
                  当前库存: {adjustingProduct.stock_count === -1 ? '无限' : adjustingProduct.stock_count}
                </span>
              </>
            )}
          </Space>
        }
        open={adjustModalVisible}
        onOk={handleAdjustSubmit}
        onCancel={() => setAdjustModalVisible(false)}
        width={560}
        confirmLoading={adjustSubmitting}
        okText="确认"
        cancelText="取消"
        destroyOnClose
      >
        <Form
          form={adjustForm}
          layout="vertical"
          preserve={false}
        >
          <Form.Item
            label="操作类型"
            name="change_type"
            rules={[{ required: true, message: '请选择操作类型' }]}
          >
            <Select placeholder="选择操作类型">
              <Select.Option value="in">
                <Space>
                  <Tag color="green">入库</Tag>
                  <span>增加库存</span>
                </Space>
              </Select.Option>
              <Select.Option value="out">
                <Space>
                  <Tag color="red">出库</Tag>
                  <span>减少库存</span>
                </Space>
              </Select.Option>
              <Select.Option value="adjust">
                <Space>
                  <Tag color="blue">盘点</Tag>
                  <span>直接设置库存</span>
                </Space>
              </Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="数量"
            name="quantity"
            rules={[
              { required: true, message: '请输入数量' },
              {
                validator: (_: any, value: number) => {
                  const changeType = adjustForm.getFieldValue('change_type');
                  if (changeType === 'adjust' && value < 0) {
                    return Promise.reject(new Error('盘点数量不能为负数'));
                  }
                  if (changeType === 'out') {
                    if (value <= 0) {
                      return Promise.reject(new Error('出库数量必须大于 0'));
                    }
                    if (
                      adjustingProduct &&
                      adjustingProduct.stock_count >= 0 &&
                      value > adjustingProduct.stock_count
                    ) {
                      return Promise.reject(new Error('出库数量不能超过当前库存'));
                    }
                  }
                  if (value <= 0) {
                    return Promise.reject(new Error('数量必须大于 0'));
                  }
                  return Promise.resolve();
                },
              },
            ]}
            extra={
              adjustingProduct && adjustingProduct.stock_count >= 0
                ? `当前库存: ${adjustingProduct.stock_count}`
                : adjustingProduct?.stock_count === -1
                ? '当前为无限库存'
                : undefined
            }
          >
            <InputNumber
              min={0}
              style={{ width: '100%' }}
              placeholder="请输入数量"
            />
          </Form.Item>

          <Form.Item label="备注" name="note">
            <TextArea
              rows={3}
              placeholder="操作原因或备注（可选）"
              maxLength={500}
              showCount
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* Stock Log Viewer Modal */}
      <Modal
        title={
          <Space>
            <HistoryOutlined />
            <span>库存日志</span>
            {adjustingProduct && (
              <>
                <Divider type="vertical" />
                <Tag color="geekblue">{adjustingProduct.product_key}</Tag>
                <span>{adjustingProduct.name_zh}</span>
              </>
            )}
          </Space>
        }
        open={logModalVisible}
        onCancel={() => setLogModalVisible(false)}
        width={900}
        footer={null}
        destroyOnClose
      >
        <Table<StockLog>
          columns={logColumns}
          dataSource={logs}
          rowKey="id"
          loading={logsLoading}
          scroll={{ x: 900 }}
          pagination={{
            current: logPagination.current,
            pageSize: logPagination.pageSize,
            total: logPagination.total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条记录`,
            onChange: (page, pageSize) =>
              setLogPagination((prev) => ({ ...prev, current: page, pageSize })),
          }}
          locale={{ emptyText: '暂无操作记录' }}
        />
      </Modal>
    </div>
  );
};

export default InventoryManagement;
