/**
 * 积分管理页面
 * Points Management
 */
import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  InputNumber,
  message,
  Card,
  Statistic,
  Row,
  Col
} from 'antd';
import {
  GiftOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  TrophyOutlined,
  StarOutlined,
  ShoppingCartOutlined,
  EyeOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { pointsApi } from '@/api/points';

interface UserPoint {
  id: number;
  user_id: number;
  username: string;
  email: string;
  avatar_url: string;
  balance: number;
  total_earned: number;
  total_spent: number;
  level: number;
  experience: number;
}

interface PointTransaction {
  id: number;
  user_id: number;
  username: string;
  transaction_type: string;
  transaction_source: string;
  amount: number;
  balance_before: number;
  balance_after: number;
  description: string;
  created_at: string;
}

interface PointProduct {
  id: number;
  product_name: string;
  product_type: string;
  description: string;
  points_price: number;
  original_price: number;
  content_type: string;
  content_id: number;
  stock: number;
  sold_count: number;
  is_featured: boolean;
  is_active: boolean;
}

const PointsManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'users' | 'transactions' | 'products'>('users');
  const [users, setUsers] = useState<UserPoint[]>([]);
  const [transactions, setTransactions] = useState<PointTransaction[]>([]);
  const [products, setProducts] = useState<PointProduct[]>([]);
  const [loading, setLoading] = useState(false);

  // 统计数据
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalPoints: 0,
    totalEarned: 0,
    totalSpent: 0
  });

  useEffect(() => {
    if (activeTab === 'users') loadUsers();
    if (activeTab === 'transactions') loadTransactions();
    if (activeTab === 'products') loadProducts();
    loadStats();
  }, [activeTab]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const response = await pointsApi.listUsers();
      if (response.data) {
        setUsers(response.data);
      }
    } catch (error) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const loadTransactions = async () => {
    setLoading(true);
    try {
      const response = await pointsApi.listTransactions();
      if (response.data) {
        setTransactions(response.data);
      }
    } catch (error) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const loadProducts = async () => {
    setLoading(true);
    try {
      const response = await pointsApi.listProducts();
      if (response.data) {
        setProducts(response.data);
      }
    } catch (error) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await pointsApi.getStats();
      if (response.data) {
        setStats(response.data);
      }
    } catch (error) {
      console.error('加载统计失败', error);
    }
  };

  // 调整用户积分
  const handleAdjustPoints = (userId: number, username: string) => {
    Modal.confirm({
      title: '调整用户积分',
      content: (
        <div>
          <p>正在调整用户：<strong>{username}</strong></p>
          <Form layout="vertical">
            <Form.Item label="积分数量">
              <InputNumber
                placeholder="正数为增加，负数为扣除"
                style={{ width: '100%' }}
              />
            </Form.Item>
            <Form.Item label="说明">
              <Input.TextArea rows={3} placeholder="调整原因" />
            </Form.Item>
          </Form>
        </div>
      ),
      onOk: async () => {
        const form = document.querySelector('form');
        const amount = parseInt((form?.[0] as HTMLInputElement)?.value || '0');
        const description = (form?.[1] as HTMLTextAreaElement)?.value;

        try {
          await pointsApi.adjustPoints(userId, { amount, description });
          message.success('调整成功');
          loadUsers();
          loadTransactions();
        } catch (error) {
          message.error('调整失败');
        }
      }
    });
  };

  const userColumns: ColumnsType<UserPoint> = [
    {
      title: '用户',
      dataIndex: 'username',
      key: 'username',
      render: (text: string, record: UserPoint) => (
        <Space>
          {record.avatar_url && (
            <img
              src={record.avatar_url}
              alt=""
              style={{ width: 32, height: 32, borderRadius: '50%' }}
            />
          )}
          <div>
            <div>{text}</div>
            <div style={{ fontSize: 12, color: '#999' }}>{record.email}</div>
          </div>
        </Space>
      )
    },
    {
      title: '积分余额',
      dataIndex: 'balance',
      key: 'balance',
      render: (balance: number) => (
        <Statistic
          title=""
          value={balance}
          valueStyle={{ color: '#faad14', fontSize: 16 }}
        />
      ),
      sorter: (a, b) => a.balance - b.balance
    },
    {
      title: '累计获得',
      dataIndex: 'total_earned',
      key: 'total_earned',
      render: (value: number) => value.toLocaleString()
    },
    {
      title: '累计消费',
      dataIndex: 'total_spent',
      key: 'total_spent',
      render: (value: number) => value.toLocaleString()
    },
    {
      title: '等级',
      dataIndex: 'level',
      key: 'level',
      render: (level: number) => (
        <Tag icon={<TrophyOutlined />} color="blue">Lv.{level}</Tag>
      )
    },
    {
      title: '经验值',
      dataIndex: 'experience',
      key: 'experience'
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record: UserPoint) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleAdjustPoints(record.user_id, record.username)}
          >
            调整
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => window.open(`/users/${record.user_id}/points`, '_blank')}
          >
            详情
          </Button>
        </Space>
      )
    }
  ];

  const transactionColumns: ColumnsType<PointTransaction> = [
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString()
    },
    {
      title: '用户',
      dataIndex: 'username',
      key: 'username'
    },
    {
      title: '类型',
      dataIndex: 'transaction_type',
      key: 'transaction_type',
      render: (type: string) => {
        const map: any = {
          'earn': { text: '获得', color: 'green' },
          'spend': { text: '消费', color: 'blue' },
          'refund': { text: '退款', color: 'orange' },
          'admin_grant': { text: '管理员赠送', color: 'purple' },
          'admin_deduct': { text: '管理员扣除', color: 'red' }
        };
        const config = map[type] || { text: type, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '来源',
      dataIndex: 'transaction_source',
      key: 'transaction_source'
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount: number) => (
        <span style={{ color: amount > 0 ? '#52c41a' : '#ff4d4f' }}>
          {amount > 0 ? '+' : ''}{amount}
        </span>
      )
    },
    {
      title: '余额变化',
      key: 'balance',
      render: (_, record: PointTransaction) => (
        <Space direction="vertical" size={4}>
          <div style={{ fontSize: 12 }}>
            前: {record.balance_before}
          </div>
          <div style={{ fontSize: 12 }}>
            后: <strong style={{ color: '#1890ff' }}>{record.balance_after}</strong>
          </div>
        </Space>
      )
    },
    {
      title: '说明',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
    }
  ];

  const productColumns: ColumnsType<PointProduct> = [
    {
      title: '商品名称',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 200
    },
    {
      title: '类型',
      dataIndex: 'product_type',
      key: 'product_type',
      width: 100,
      render: (type: string) => {
        const map: any = {
          'content': { text: '内容', color: 'blue' },
          'coupon': { text: '优惠券', color: 'green' },
          'vip': { text: 'VIP', color: 'purple' },
          'custom': { text: '自定义', color: 'orange' }
        };
        const config = map[type] || { text: type, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: '积分价格',
      dataIndex: 'points_price',
      key: 'points_price',
      width: 120,
      render: (price: number, record: PointProduct) => (
        <Space>
          <span style={{ color: '#faad14', fontWeight: 600 }}>{price}</span>
          <span style={{ color: '#999', fontSize: 12 }}>积分</span>
          {record.original_price && record.original_price > price && (
            <Tag color="green" style={{ marginLeft: 4 }}>优惠</Tag>
          )}
        </Space>
      ),
      sorter: (a, b) => a.points_price - b.points_price
    },
    {
      title: '库存',
      dataIndex: 'stock',
      key: 'stock',
      width: 100,
      render: (stock: number) => (
        <span style={{ color: stock === -1 ? '#52c41a' : stock < 10 ? '#ff4d4f' : '#1890ff' }}>
          {stock === -1 ? '无限制' : stock}
        </span>
      )
    },
    {
      title: '已售',
      dataIndex: 'sold_count',
      key: 'sold_count',
      width: 100
    },
    {
      title: '状态',
      key: 'status',
      width: 100,
      render: (_: any, record: PointProduct) => (
        <Space>
          {record.is_featured && <Tag color="orange">精选</Tag>}
          <Tag color={record.is_active ? 'green' : 'red'}>
            {record.is_active ? '上架' : '下架'}
          </Tag>
        </Space>
      )
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      fixed: 'right',
      render: (_: any, record: PointProduct) => (
        <Space>
          <Button
            type="text"
            size="small"
            icon={<EditOutlined />}
          >
            编辑
          </Button>
          <Button
            type="text"
            size="small"
            icon={<DeleteOutlined />}
            danger
          >
            删除
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h2>积分管理</h2>
        <p style={{ color: 'var(--text-light)'}}>
          管理用户积分、积分交易记录和积分商品
        </p>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="累计用户"
              value={stats.totalUsers}
              prefix={<GiftOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总积分发行"
              value={stats.totalPoints}
              prefix={<StarOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="累计获得"
              value={stats.totalEarned}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="累计消费"
              value={stats.totalSpent}
              prefix={<ShoppingCartOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Tab 切换 */}
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Button
            type={activeTab === 'users' ? 'primary' : 'default'}
            onClick={() => setActiveTab('users')}
          >
            用户积分
          </Button>
          <Button
            type={activeTab === 'transactions' ? 'primary' : 'default'}
            onClick={() => setActiveTab('transactions')}
          >
            交易记录
          </Button>
          <Button
            type={activeTab === 'products' ? 'primary' : 'default'}
            onClick={() => setActiveTab('products')}
          >
            积分商品
          </Button>
          <Button icon={<ReloadOutlined />} onClick={() => {
            if (activeTab === 'users') loadUsers();
            if (activeTab === 'transactions') loadTransactions();
            if (activeTab === 'products') loadProducts();
            loadStats();
          }}>
            刷新
          </Button>
        </Space>

        {/* 用户积分列表 */}
        {activeTab === 'users' && (
          <Table
            columns={userColumns}
            dataSource={users}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个用户`
            }}
          />
        )}

        {/* 交易记录列表 */}
        {activeTab === 'transactions' && (
          <>
            <Input.Search
              placeholder="搜索交易记录"
              allowClear
              enterButton
              style={{ width: 300, marginBottom: 16 }}
              onSearch={() => {
                // TODO: 实现搜索
              }}
            />
            <Table
              columns={transactionColumns}
              dataSource={transactions}
              rowKey="id"
              loading={loading}
              pagination={{
                pageSize: 50,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 条记录`
              }}
            />
          </>
        )}

        {/* 积分商品列表 */}
        {activeTab === 'products' && (
          <>
            <div style={{ marginBottom: 16, textAlign: 'right' }}>
              <Button
                type="primary"
                icon={<PlusOutlined />}
              >
                新增积分商品
              </Button>
            </div>
            <Table
              columns={productColumns}
              dataSource={products}
              rowKey="id"
              loading={loading}
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 个商品`
              }}
            />
          </>
        )}
      </Card>
    </div>
  );
};

export default PointsManagement;
