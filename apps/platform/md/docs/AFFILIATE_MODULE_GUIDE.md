# 分销系统模块 (Affiliate Module)

## 概述

分销系统模块是一个完整的员工分销统计系统，支持通过分享链接追踪订单和统计员工业绩。

## 功能特性

### 1. 员工管理
- 创建/更新/禁用分销员工
- 员工唯一码 (如 AFF12345678)
- 员工销售/订单/佣金统计

### 2. 分享链接
- 生成带追踪码的分享链接
- 支持指定商品或通用链接
- 链接有效期管理
- 点击/订单/转化率统计

### 3. 访问追踪
- 记录每次访问
- 记录来源、Referrer、IP、User-Agent
- 访问者识别 (visitor_id)

### 4. 订单归属
- 自动归属订单到对应员工
- 支持订单确认/取消
- 订单确认后自动计算佣金

### 5. 佣金系统
- 默认 5% 佣金比例
- 佣金状态管理 (pending/confirmed/paid)
- 支持批量发放佣金

### 6. 排行榜
- 按销售额/订单数排名
- 支持按时间周期筛选 (today/week/month/all)

### 7. 全局统计
- 所有员工的汇总数据
- 最佳员工展示

## API 端点

### 员工管理
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/affiliate/staffs | 获取员工列表 |
| POST | /api/affiliate/staffs | 创建员工 |
| GET | /api/affiliate/staffs/me | 获取当前用户员工信息 |
| GET | /api/affiliate/staffs/{id} | 获取员工详情 |
| PUT | /api/affiliate/staffs/{id} | 更新员工信息 |
| GET | /api/affiliate/staffs/{id}/stats | 获取员工统计 |

### 分享链接
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/affiliate/links | 生成分享链接 |
| GET | /api/affiliate/links | 获取链接列表 |
| GET | /api/affiliate/links/{code} | 获取链接详情 |
| GET | /api/affiliate/links/{code}/stats | 获取链接统计 |

### 访问追踪
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/affiliate/track | 记录访问 |
| GET | /api/affiliate/r/{code} | 短链接重定向 |

### 订单管理
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/affiliate/orders/assign | 分配订单归属 |
| POST | /api/affiliate/orders/{id}/confirm | 确认订单 |
| POST | /api/affiliate/orders/{id}/cancel | 取消订单 |
| GET | /api/affiliate/orders | 获取订单列表 |

### 其他
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/affiliate/leaderboard | 获取排行榜 |
| GET | /api/affiliate/commissions | 获取佣金列表 |
| POST | /api/affiliate/commissions/{id}/pay | 支付佣金 |
| GET | /api/affiliate/admin/stats | 获取全局统计 |

## 数据库表

### affiliate_staffs - 分销员工表
```sql
- id: SERIAL PRIMARY KEY
- user_id: INTEGER UNIQUE NOT NULL  -- 关联的用户ID
- staff_code: VARCHAR(50) UNIQUE NOT NULL  -- 员工码 (如 AFF12345678)
- staff_name: VARCHAR(100) NOT NULL  -- 员工姓名
- total_sales: DECIMAL(15,2) DEFAULT 0  -- 累计销售额
- total_orders: INTEGER DEFAULT 0  -- 累计订单数
- total_commission: DECIMAL(15,2) DEFAULT 0  -- 累计佣金
- status: VARCHAR(20) DEFAULT 'active'  -- 状态 (active/inactive)
- created_at: TIMESTAMP  -- 创建时间
- updated_at: TIMESTAMP  -- 更新时间
```

### affiliate_links - 分享链接表
```sql
- id: SERIAL PRIMARY KEY
- staff_id: INTEGER REFERENCES affiliate_staffs(id)
- product_id: INTEGER  -- 可选，指定商品
- link_code: VARCHAR(50) UNIQUE NOT NULL  -- 链接码
- short_url: VARCHAR(255)  -- 短链接路径
- click_count: INTEGER DEFAULT 0  -- 点击数
- order_count: INTEGER DEFAULT 0  -- 订单数
- conversion_rate: DECIMAL(5,4) DEFAULT 0  -- 转化率
- status: VARCHAR(20) DEFAULT 'active'  -- 状态
- created_at: TIMESTAMP  -- 创建时间
- expires_at: TIMESTAMP  -- 过期时间
```

### affiliate_orders - 分销订单表
```sql
- id: SERIAL PRIMARY KEY
- order_id: INTEGER NOT NULL  -- 外部订单ID
- staff_id: INTEGER REFERENCES affiliate_staffs(id)
- link_id: INTEGER REFERENCES affiliate_links(id)
- product_id: INTEGER  -- 商品ID
- amount: DECIMAL(15,2) NOT NULL  -- 订单金额
- commission: DECIMAL(15,2) DEFAULT 0  -- 佣金金额
- status: VARCHAR(20) DEFAULT 'pending'  -- pending/confirmed/cancelled
- created_at: TIMESTAMP  -- 创建时间
- confirmed_at: TIMESTAMP  -- 确认时间
```

### affiliate_commissions - 佣金记录表
```sql
- id: SERIAL PRIMARY KEY
- staff_id: INTEGER REFERENCES affiliate_staffs(id)
- order_id: INTEGER NOT NULL  -- 订单ID
- amount: DECIMAL(15,2) NOT NULL  -- 佣金金额
- status: VARCHAR(20) DEFAULT 'pending'  -- pending/confirmed/paid/cancelled
- created_at: TIMESTAMP  -- 创建时间
- paid_at: TIMESTAMP  -- 支付时间
```

### affiliate_visits - 访问记录表
```sql
- id: SERIAL PRIMARY KEY
- link_id: INTEGER REFERENCES affiliate_links(id)
- visitor_id: VARCHAR(100)  -- 访客标识
- source: VARCHAR(255)  -- 来源
- referrer: TEXT  -- 来源页面
- ip_address: VARCHAR(45)  -- IP地址
- user_agent: TEXT  -- User-Agent
- created_at: TIMESTAMP  -- 访问时间
```

## 使用示例

### 1. 创建分销员工
```python
from src.modules.affiliate import StaffService

staff = StaffService.create_staff(
    user_id=1,
    staff_name="张三"
)
# 返回: {'id': 1, 'staff_code': 'AFF12345678', 'staff_name': '张三', ...}
```

### 2. 生成分享链接
```python
from src.modules.affiliate import LinkService

link = LinkService.create_affiliate_link(
    staff_id=1,
    product_id=100  # 可选
)
# 返回: {
#   'link_code': 'abc123xyz789',
#   'short_url': '/r/abc123xyz789',
#   'full_url': '/openclaw/product/100?ref=abc123xyz789',
#   ...
# }
```

### 3. 追踪访问
```python
from src.modules.affiliate import VisitService

result = VisitService.track_visit(
    link_code='abc123xyz789',
    visitor_id='user_123',
    source='wechat'
)
# 返回: {'success': True, 'redirect_url': '/openclaw/product/100?ref=abc123xyz789'}
```

### 4. 订单归属
```python
from src.modules.affiliate import OrderService

order = OrderService.assign_order_to_staff(
    order_id=10001,
    link_code='abc123xyz789',
    product_id=100,
    amount=199.99
)
# 返回: {'id': 1, 'order_id': 10001, 'commission': 9.99, 'status': 'pending'}
```

### 5. 确认订单并发放佣金
```python
from src.modules.affiliate import OrderService

order = OrderService.confirm_order(order_id=10001)
# 返回: {'id': 1, 'order_id': 10001, 'status': 'confirmed', 'confirmed_at': '...'}
```

### 6. 获取排行榜
```python
from src.modules.affiliate import LeaderboardService

leaderboard = LeaderboardService.get_leaderboard(limit=10, period='month')
# 返回: {
#   'entries': [
#     {'rank': 1, 'staff_name': '张三', 'total_sales': 5000.00, ...},
#     ...
#   ],
#   'period': 'month',
#   'total_staffs': 50
# }
```

## 分享链接格式

### 链接格式
```
# 通用链接
/openclaw?ref=STAFF_CODE

# 商品链接
/openclaw/product/{product_id}?ref=STAFF_CODE

# 短链接 (自动重定向)
/r/{link_code}
```

### 使用流程
1. 员工登录后台，获取分享链接
2. 通过微信/QQ/短信等渠道分享链接
3. 用户点击链接访问，自动记录访问信息
4. 用户下单时，系统自动归属订单到对应员工
5. 订单确认后，佣金自动计入员工账户

## 配置说明

配置文件: `src/modules/affiliate/config.yaml`

```yaml
config:
  # 默认佣金比例 (5%)
  default_commission_rate: 0.05
  # 链接有效期（天）
  link_expiry_days: 365
  # 访问记录有效期（小时）
  visit_cookie_hours: 168
  # 排行榜限制
  leaderboard_limit: 50
  # 最小提现额度
  min_withdrawal: 100
```

## 集成到主应用

模块会自动被主应用加载，无需手动注册。

在 `main.py` 中，PluginManager 会自动扫描 `src/modules/` 目录，
发现 `affiliate` 模块后会：
1. 调用 `SillyMDModule()` 创建实例
2. 调用 `register(app)` 注册路由
3. 调用 `on_startup()` 初始化数据库表

## 测试

运行测试脚本:
```bash
python test_affiliate_api.py
```

## 文件结构

```
src/modules/affiliate/
├── __init__.py      # 模块入口，定义 SillyMDModule 类
├── config.yaml      # 模块配置
├── schemas.py       # Pydantic 数据模型
├── routes.py        # API 路由定义
└── services.py      # 业务逻辑服务
```

## 依赖

- FastAPI
- Pydantic
- psycopg2 (PostgreSQL)

---

## Phase 1 更新

> 分销模块 API 路径已统一为 `/api/v1/affiliate/*` (旧路径: `/api/affiliate/*`)。
> 后端入口: `src/main.py` (旧: `server/api/main.py`)。
