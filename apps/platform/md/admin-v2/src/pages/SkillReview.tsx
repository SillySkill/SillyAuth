import React, { useEffect, useState, useCallback } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Input,
  message,
  Card,
  Typography,
  Select,
  Descriptions,
  Tooltip,
} from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  EyeOutlined,
  SearchOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  getSkillsForReview,
  approveSkill,
  rejectSkill,
  getSkill2Status,
  type ReviewSkill,
  type Skill2Status,
} from '../api/skillReview';
import { formatDate } from '../utils';

const { TextArea } = Input;
const { Title } = Typography;
const { Option } = Select;

const categoryLabels: Record<string, string> = {
  tech: '技术',
  product: '产品',
  design: '设计',
  marketing: '市场',
  ops: '运营',
};

const statusConfig: Record<string, { color: string; label: string }> = {
  draft: { color: 'default', label: '草稿' },
  reviewing: { color: 'processing', label: '审核中' },
  approved: { color: 'success', label: '已通过' },
  rejected: { color: 'error', label: '已拒绝' },
};

const SkillReview: React.FC = () => {
  const [skills, setSkills] = useState<ReviewSkill[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20, total: 0 });
  const [statusFilter, setStatusFilter] = useState<string>('reviewing');
  const [searchText, setSearchText] = useState('');
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState<ReviewSkill | null>(null);
  const [skill2Status, setSkill2Status] = useState<Record<number, Skill2Status>>({});
  const [rejectModalVisible, setRejectModalVisible] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [rejectingSkillId, setRejectingSkillId] = useState<number | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchSkills = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getSkillsForReview({
        status: statusFilter,
        page: pagination.current,
        limit: pagination.pageSize,
        search: searchText || undefined,
      });
      if (response.success) {
        setSkills(response.data.items);
        setPagination((prev) => ({ ...prev, total: response.data.total }));
      }
      // Fetch Skill2 status for each skill
      if (response.success && response.data.items.length > 0) {
        const statusMap: Record<number, Skill2Status> = {};
        await Promise.allSettled(
          response.data.items.map(async (skill) => {
            try {
              const s2resp = await getSkill2Status(skill.id);
              if (s2resp.success) {
                statusMap[skill.id] = s2resp.data;
              }
            } catch {
              // ignore Skill2 status fetch errors
            }
          })
        );
        setSkill2Status(statusMap);
      }
    } catch (error) {
      message.error('加载技能列表失败');
    } finally {
      setLoading(false);
    }
  }, [statusFilter, pagination.current, pagination.pageSize, searchText]);

  useEffect(() => {
    fetchSkills();
  }, [fetchSkills]);

  const handleApprove = async (skillId: number) => {
    setActionLoading(true);
    try {
      await approveSkill(skillId);
      message.success('技能审核通过');
      fetchSkills();
    } catch (error) {
      message.error('操作失败');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!rejectingSkillId) return;
    setActionLoading(true);
    try {
      await rejectSkill(rejectingSkillId, rejectReason);
      message.success('技能已拒绝');
      setRejectModalVisible(false);
      setRejectReason('');
      setRejectingSkillId(null);
      fetchSkills();
    } catch (error) {
      message.error('操作失败');
    } finally {
      setActionLoading(false);
    }
  };

  const openRejectModal = (skillId: number) => {
    setRejectingSkillId(skillId);
    setRejectReason('');
    setRejectModalVisible(true);
  };

  const showDetail = (skill: ReviewSkill) => {
    setSelectedSkill(skill);
    setDetailModalVisible(true);
  };

  const handleTableChange = (page: number, pageSize: number) => {
    setPagination({ current: page, pageSize, total: pagination.total });
  };

  const columns: ColumnsType<ReviewSkill> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: '技能名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (name: string) => (
        <span style={{ fontWeight: 500 }}>{name}</span>
      ),
    },
    {
      title: '作者',
      dataIndex: 'author_username',
      key: 'author_username',
      width: 120,
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 100,
      render: (cat: string) => (
        <Tag color="purple">{categoryLabels[cat] || cat}</Tag>
      ),
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
      width: 80,
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 80,
      render: (type: string) =>
        type === 'free' ? (
          <Tag color="green">免费</Tag>
        ) : (
          <Tag color="gold">付费 ¥{selectedSkill?.price || 0}</Tag>
        ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 90,
      render: (status: string) => {
        const cfg = statusConfig[status] || { color: 'default', label: status };
        return <Tag color={cfg.color}>{cfg.label}</Tag>;
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      render: (date: string) => formatDate(date),
    },
    {
      title: 'Skill2',
      key: 'skill2',
      width: 100,
      render: (_: unknown, record: ReviewSkill) => {
        const s2 = skill2Status[record.id];
        if (!s2) return <Tag>待处理</Tag>;
        switch (s2.status) {
          case 'packaged':
            return <Tag color="success">已加密</Tag>;
          case 'scanned':
            return <Tag color="processing">扫描完成</Tag>;
          case 'failed':
            return <Tag color="error">失败</Tag>;
          default:
            return <Tag>待处理</Tag>;
        }
      },
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (_: unknown, record: ReviewSkill) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="link"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => showDetail(record)}
            />
          </Tooltip>
          {(record.status === 'reviewing' || record.status === 'draft') && (
            <>
              <Button
                type="link"
                size="small"
                icon={<CheckCircleOutlined />}
                style={{ color: '#52c41a' }}
                onClick={() => handleApprove(record.id)}
              >
                通过
              </Button>
              <Button
                type="link"
                size="small"
                danger
                icon={<CloseCircleOutlined />}
                onClick={() => openRejectModal(record.id)}
              >
                拒绝
              </Button>
            </>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        技能审核
      </Title>

      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Select
            value={statusFilter}
            onChange={(val) => {
              setStatusFilter(val);
              setPagination((prev) => ({ ...prev, current: 1 }));
            }}
            style={{ width: 160 }}
          >
            <Option value="reviewing">审核中</Option>
            <Option value="draft">草稿</Option>
            <Option value="approved">已通过</Option>
            <Option value="rejected">已拒绝</Option>
            <Option value="">全部</Option>
          </Select>
          <Input
            placeholder="按名称搜索..."
            prefix={<SearchOutlined />}
            style={{ width: 220 }}
            allowClear
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onPressEnter={() => {
              setPagination((prev) => ({ ...prev, current: 1 }));
            }}
          />
          <Button icon={<ReloadOutlined />} onClick={() => fetchSkills()}>
            刷新
          </Button>
        </Space>
      </Card>

      <Card>
        <Table<ReviewSkill>
          columns={columns}
          dataSource={skills}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1100 }}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 个技能`,
            onChange: (page, pageSize) => handleTableChange(page, pageSize),
          }}
          locale={{ emptyText: '暂无技能' }}
        />
      </Card>

      {/* Detail Modal */}
      <Modal
        title="技能详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        {selectedSkill && (
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="名称" span={2}>
              {selectedSkill.name}
            </Descriptions.Item>
            <Descriptions.Item label="作者">
              {selectedSkill.author_username}
            </Descriptions.Item>
            <Descriptions.Item label="分类">
              {categoryLabels[selectedSkill.category] || selectedSkill.category}
            </Descriptions.Item>
            <Descriptions.Item label="版本">
              v{selectedSkill.version}
            </Descriptions.Item>
            <Descriptions.Item label="类型">
              {selectedSkill.type === 'free' ? '免费' : `付费 ¥${selectedSkill.price}`}
            </Descriptions.Item>
            <Descriptions.Item label="状态" span={2}>
              <Tag color={statusConfig[selectedSkill.status]?.color}>
                {statusConfig[selectedSkill.status]?.label}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="描述" span={2}>
              {selectedSkill.description || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="主题说明" span={2}>
              {selectedSkill.theme_description || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="仓库地址" span={2}>
              {selectedSkill.repo_url ? (
                <a href={selectedSkill.repo_url} target="_blank" rel="noreferrer">
                  {selectedSkill.repo_url}
                </a>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="封面图片" span={2}>
              {selectedSkill.cover_image ? (
                <a href={selectedSkill.cover_image} target="_blank" rel="noreferrer">
                  <img
                    src={selectedSkill.cover_image}
                    alt="技能封面"
                    style={{ maxWidth: 300, maxHeight: 180, borderRadius: 6, border: '1px solid #f0f0f0' }}
                  />
                </a>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="技能包文件" span={2}>
              {selectedSkill.package_url ? (
                <a href={selectedSkill.package_url} target="_blank" rel="noreferrer">
                  {selectedSkill.package_url}
                </a>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="浏览量">
              {selectedSkill.view_count}
            </Descriptions.Item>
            <Descriptions.Item label="下载量">
              {selectedSkill.download_count}
            </Descriptions.Item>
            <Descriptions.Item label="创建时间">
              {formatDate(selectedSkill.created_at)}
            </Descriptions.Item>
            <Descriptions.Item label="更新时间">
              {formatDate(selectedSkill.updated_at)}
            </Descriptions.Item>
          </Descriptions>

          {/* Skill2 Scan Results */}
          {skill2Status[selectedSkill.id] && (
            <div style={{ marginTop: 24 }}>
              <Title level={5}>Skill2 安全扫描</Title>
              <Descriptions column={2} bordered size="small">
                <Descriptions.Item label="状态">
                  <Tag color={
                    skill2Status[selectedSkill.id].status === 'packaged' ? 'success' :
                    skill2Status[selectedSkill.id].status === 'failed' ? 'error' :
                    'processing'
                  }>
                    {skill2Status[selectedSkill.id].status === 'packaged' ? '已加密打包' :
                     skill2Status[selectedSkill.id].status === 'scanned' ? '扫描完成' :
                     skill2Status[selectedSkill.id].status === 'failed' ? '处理失败' :
                     skill2Status[selectedSkill.id].status}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="敏感项数量">
                  {skill2Status[selectedSkill.id].total_sensitive}
                </Descriptions.Item>
              </Descriptions>
              {skill2Status[selectedSkill.id].sensitive_items.length > 0 && (
                <div style={{ marginTop: 12 }}>
                  <Title level={5} style={{ fontSize: 14 }}>敏感内容检测明细</Title>
                  <Table
                    dataSource={skill2Status[selectedSkill.id].sensitive_items}
                    rowKey={(item, idx) => `${item.line_number}-${idx}`}
                    size="small"
                    pagination={false}
                    columns={[
                      { title: '行号', dataIndex: 'line_number', width: 60 },
                      {
                        title: '类型',
                        dataIndex: 'marker_type',
                        width: 120,
                        render: (t: string) => {
                          const labels: Record<string, string> = {
                            p1_explicit: '显式声明',
                            p2_field_name: '字段名匹配',
                            p3_format: '格式匹配',
                            p4_semantic: '语义识别',
                            p5_position: '位置加权',
                          };
                          return <Tag>{labels[t] || t}</Tag>;
                        },
                      },
                      { title: '预览', dataIndex: 'content_preview', ellipsis: true },
                      {
                        title: '置信度',
                        dataIndex: 'confidence',
                        width: 80,
                        render: (v: number) => `${Math.round(v * 100)}%`,
                      },
                      {
                        title: '建议',
                        dataIndex: 'suggested_action',
                        width: 80,
                        render: (a: string) => (
                          <Tag color={a === 'encrypt' ? 'red' : 'orange'}>
                            {a === 'encrypt' ? '加密' : '审查'}
                          </Tag>
                        ),
                      },
                    ]}
                  />
                </div>
              )}
              {skill2Status[selectedSkill.id].manifest_url && (
                <div style={{ marginTop: 8 }}>
                  <a
                    href={skill2Status[selectedSkill.id].manifest_url!}
                    target="_blank"
                    rel="noreferrer"
                  >
                    查看 .skill2 清单
                  </a>
                </div>
              )}
              {skill2Status[selectedSkill.id].error_message && (
                <div style={{ marginTop: 8, color: '#ff4d4f' }}>
                  错误: {skill2Status[selectedSkill.id].error_message}
                </div>
              )}
            </div>
          )}
        )}
      </Modal>

      {/* Reject Modal */}
      <Modal
        title="拒绝技能"
        open={rejectModalVisible}
        onOk={handleReject}
        onCancel={() => {
          setRejectModalVisible(false);
          setRejectReason('');
          setRejectingSkillId(null);
        }}
        okText="确认拒绝"
        cancelText="取消"
        okButtonProps={{ danger: true, loading: actionLoading }}
      >
        <div style={{ marginBottom: 12 }}>请填写拒绝原因（选填）：</div>
        <TextArea
          rows={4}
          value={rejectReason}
          onChange={(e) => setRejectReason(e.target.value)}
          placeholder="输入拒绝原因，此内容将通知技能作者..."
        />
      </Modal>
    </div>
  );
};

export default SkillReview;
