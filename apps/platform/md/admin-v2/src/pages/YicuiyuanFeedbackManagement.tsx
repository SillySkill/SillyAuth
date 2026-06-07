import React, { useEffect, useState, useCallback } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  message,
  Typography,
  Spin,
} from 'antd';
import {
  EyeOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getFeedbacks, updateFeedback } from '@/api/yicuiyuan';
import type { YicuiyuanFeedback, YicuiyuanFeedbackUpdateRequest } from '@/api/yicuiyuan';

const { Title, Text } = Typography;
const { TextArea } = Input;

const FEEDBACK_TYPE_COLORS: Record<string, string> = {
  suggestion: 'blue',
  complaint: 'red',
  question: 'orange',
  praise: 'green',
  other: 'default',
};

const FEEDBACK_TYPE_LABELS: Record<string, string> = {
  suggestion: '建议',
  complaint: '投诉',
  question: '咨询',
  praise: '表扬',
  other: '其他',
};

const STATUS_COLORS: Record<string, string> = {
  pending: 'orange',
  processing: 'blue',
  resolved: 'green',
  rejected: 'red',
};

const STATUS_LABELS: Record<string, string> = {
  pending: '待处理',
  processing: '处理中',
  resolved: '已解决',
  rejected: '已驳回',
};

const YicuiyuanFeedbackManagement: React.FC = () => {
  const [items, setItems] = useState<YicuiyuanFeedback[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const [searchText, setSearchText] = useState('');
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedItem, setSelectedItem] = useState<YicuiyuanFeedback | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();

  const fetchItems = useCallback(async () => {
    setLoading(true);
    try {
      const result = await getFeedbacks({
        page,
        page_size: pageSize,
        search: searchText || undefined,
        status: statusFilter,
      });
      if (result.success) {
        setItems(result.data?.items || []);
        setTotal(result.data?.total || 0);
      }
    } catch {
      message.error('加载反馈列表失败');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, searchText, statusFilter]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const handleViewDetail = (record: YicuiyuanFeedback) => {
    setSelectedItem(record);
    form.setFieldsValue({
      status: record.status,
      admin_reply: record.admin_reply || '',
    });
    setDetailVisible(true);
  };

  const handleReply = async () => {
    if (!selectedItem) return;
    try {
      const values = await form.validateFields();
      setSubmitting(true);

      const updateData: YicuiyuanFeedbackUpdateRequest = {
        status: values.status,
        admin_reply: values.admin_reply || '',
      };
      const result = await updateFeedback(selectedItem.id, updateData);
      if (result.success) {
        message.success('回复已保存');
        setDetailVisible(false);
        fetchItems();
      } else {
        message.error(result.message || '保存失败');
      }
    } catch {
      // Validation failed - do nothing
    } finally {
      setSubmitting(false);
    }
  };

  const columns: ColumnsType<YicuiyuanFeedback> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: '提交人',
      dataIndex: 'submitter_name',
      key: 'submitter_name',
      width: 120,
      ellipsis: true,
    },
    {
      title: '类型',
      dataIndex: 'feedback_type',
      key: 'feedback_type',
      width: 100,
      render: (type: string) => (
        <Tag color={FEEDBACK_TYPE_COLORS[type] || 'default'}>
          {FEEDBACK_TYPE_LABELS[type] || type}
        </Tag>
      ),
    },
    {
      title: '内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
      width: 300,
      render: (val: string) =>
        val.length > 60 ? `${val.substring(0, 60)}...` : val,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={STATUS_COLORS[status] || 'default'}>
          {STATUS_LABELS[status] || status}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (val: string) => (val ? new Date(val).toLocaleString('zh-CN') : '-'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 100,
      render: (_: unknown, record: YicuiyuanFeedback) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetail(record)}
        >
          查看
        </Button>
      ),
    },
  ];

  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 16,
        }}
      >
        <Title level={3} style={{ margin: 0 }}>
          意见反馈
        </Title>
        <Space>
          <Select
            placeholder="筛选状态"
            allowClear
            style={{ width: 140 }}
            value={statusFilter}
            onChange={(val) => {
              setStatusFilter(val);
              setPage(1);
            }}
          >
            <Select.Option value="pending">待处理</Select.Option>
            <Select.Option value="processing">处理中</Select.Option>
            <Select.Option value="resolved">已解决</Select.Option>
            <Select.Option value="rejected">已驳回</Select.Option>
          </Select>
          <Input.Search
            placeholder="搜索提交人..."
            allowClear
            onSearch={(value) => {
              setSearchText(value);
              setPage(1);
            }}
            style={{ width: 200 }}
          />
          <Button icon={<ReloadOutlined />} onClick={fetchItems}>
            刷新
          </Button>
        </Space>
      </div>

      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={items}
          rowKey="id"
          pagination={{
            current: page,
            pageSize,
            total,
            showSizeChanger: true,
            showTotal: (t) => `共 ${t} 条`,
            onChange: (p, ps) => {
              setPage(p);
              setPageSize(ps);
            },
          }}
          scroll={{ x: 1000 }}
        />
      </Spin>

      <Modal
        title="反馈详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setDetailVisible(false)}>
            关闭
          </Button>,
          <Button key="submit" type="primary" loading={submitting} onClick={handleReply}>
            回复
          </Button>,
        ]}
        width={640}
        destroyOnClose
      >
        {selectedItem && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <Text strong>提交人：</Text>
              <Text>{selectedItem.submitter_name}</Text>
            </div>
            {selectedItem.contact_info && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>联系方式：</Text>
                <Text>{selectedItem.contact_info}</Text>
              </div>
            )}
            <div style={{ marginBottom: 16 }}>
              <Text strong>类型：</Text>
              <Tag color={FEEDBACK_TYPE_COLORS[selectedItem.feedback_type] || 'default'}>
                {FEEDBACK_TYPE_LABELS[selectedItem.feedback_type] || selectedItem.feedback_type}
              </Tag>
            </div>
            <div style={{ marginBottom: 16 }}>
              <Text strong>状态：</Text>
              <Tag color={STATUS_COLORS[selectedItem.status] || 'default'}>
                {STATUS_LABELS[selectedItem.status] || selectedItem.status}
              </Tag>
            </div>
            <div style={{ marginBottom: 16 }}>
              <Text strong>反馈内容：</Text>
              <div
                style={{
                  background: '#f5f5f5',
                  padding: 12,
                  borderRadius: 4,
                  marginTop: 8,
                  whiteSpace: 'pre-wrap',
                }}
              >
                {selectedItem.content}
              </div>
            </div>
            {selectedItem.admin_reply && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>历史回复：</Text>
                <div
                  style={{
                    background: '#f6ffed',
                    padding: 12,
                    borderRadius: 4,
                    marginTop: 8,
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {selectedItem.admin_reply}
                </div>
                {selectedItem.replied_at && (
                  <div style={{ marginTop: 4, color: '#999', fontSize: 12 }}>
                    回复时间：{new Date(selectedItem.replied_at).toLocaleString('zh-CN')}
                  </div>
                )}
              </div>
            )}

            <Form form={form} layout="vertical">
              <Form.Item label="状态" name="status">
                <Select>
                  <Select.Option value="pending">待处理</Select.Option>
                  <Select.Option value="processing">处理中</Select.Option>
                  <Select.Option value="resolved">已解决</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item label="管理员回复" name="admin_reply">
                <TextArea rows={4} placeholder="输入回复内容..." />
              </Form.Item>
            </Form>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default YicuiyuanFeedbackManagement;
