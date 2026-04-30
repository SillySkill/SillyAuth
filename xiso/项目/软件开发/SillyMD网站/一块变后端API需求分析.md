# 一块变后端API需求分析

> **分析日期**: 2026-02-15  
> **分析师**: 傻老憨（AI·2002）  
> **项目背景**: 一块变小程序春节上线项目

---

## 📋 一、项目架构概览

### 1.1 项目位置
- **主目录**: `silly-complete\silly\`
- **后端API**: `One\server\`（FastAPI + Python）
- **小程序前端**: `One\miniprogram\`（微信小程序）
- **参考项目**: `AIActive\`（AI拍照秀）

### 1.2 技术栈
- **后端框架**: FastAPI（Python异步框架）
- **数据库**: PostgreSQL
- **云服务**: 火山引擎（AI生成）、阿里云TOS（对象存储）
- **支付**: 微信支付、支付宝、抖音支付

---

## 🎯 二、一块变业务流程分析

### 2.1 核心流程
```
用户点击"按一下，一块变"
    ↓
1. 校验用户身份（微信登录）
    ↓
2. 检查账户余额（成长分）
    ↓
    ├── 有余额 → 上传照片
    └── 无余额 → 引导充值
                    ↓
                3种充值方式：
                - 直接付款
                - 转发裂变获取优惠
                - 渠道分销
                    ↓
4. 上传照片到云存储
    ↓
5. 调用AI生成图片/视频
    ↓
6. 展示生成结果
    ↓
7. 分享裂变（可选）
```

### 2.2 成长分体系
- **图片生成**: 消耗1成长分/张
- **视频生成**: 消耗3.2成长分/秒
- **充值档位**: 1/10/20/50/100/200/500/1000/2000/5000/10000元（共11档）
- **权益选择**: 图片权益 OR 视频权益（二选一）

---

## 🗄️ 三、数据库设计分析

### 3.1 核心表结构（已实现）

| 表名 | 说明 | 状态 |
|------|------|------|
| `one_recharge_packages` | 充值套餐表（11档） | ✅ 已完成 |
| `one_user_balance` | 用户余额表（成长分） | ✅ 已完成 |
| `one_recharge_orders` | 充值订单表 | ✅ 已完成 |
| `one_generation_records` | AI生成记录表 | ✅ 已完成 |
| `platform_share_records` | 分享裂变记录表 | ✅ 已完成 |
| `one_balance_change_log` | 余额变更日志表 | ✅ 已完成 |

### 3.2 关键数据表详情

#### 3.2.1 充值套餐表 (one_recharge_packages)
```sql
- amount: 充值金额（1-10000元）
- image_base: 图片基础次数
- image_bonus: 图片赠送次数
- video_base: 视频基础秒数
- video_bonus: 视频赠送秒数
- is_hot: 是否热门档位
```

#### 3.2.2 用户余额表 (one_user_balance)
```sql
- user_id: 用户ID
- growth_points: 总成长分
- image_points: 图片专属成长分
- video_points: 视频专属成长分
- total_recharged: 累计充值金额
- total_discount: 累计优惠金额
```

#### 3.2.3 生成记录表 (one_generation_records)
```sql
- generation_type: 'image' | 'video'
- style_id: 风格ID
- points_consumed: 消耗的成长分
- status: 0处理中/1已完成/2失败
- result_url: 生成结果URL
```

---

## 📡 四、现有API接口分析

### 4.1 已实现的API（位于 `One\server\routes\`）

#### 用户模块 (user_routes.py)
| 接口 | 方法 | 说明 | 状态 |
|------|------|------|------|
| `/user/login` | POST | 微信登录/注册 | ✅ 已实现 |
| `/user/profile` | GET | 获取用户资料 | ✅ 已实现 |
| `/user/profile` | PUT | 更新用户资料 | ✅ 已实现 |
| `/user/balance` | GET | 获取用户余额 | ✅ 已实现 |

#### 生成模块 (generation_routes.py)
| 接口 | 方法 | 说明 | 状态 |
|------|------|------|------|
| `/generate/styles` | GET | 获取风格列表 | ✅ 已实现 |
| `/generate/image` | POST | 生成图片 | ✅ 已实现 |
| `/generate/video` | POST | 生成视频 | ✅ 已实现 |
| `/generate/status` | GET | 查询任务状态 | ✅ 已实现 |
| `/generate/records` | GET | 获取生成记录 | ✅ 已实现 |

#### 充值模块 (recharge_routes.py)
| 接口 | 方法 | 说明 | 状态 |
|------|------|------|------|
| `/recharge/packages` | GET | 获取充值套餐 | ✅ 已实现 |
| `/recharge/create-order` | POST | 创建充值订单 | ✅ 已实现 |
| `/recharge/payment-callback` | POST | 支付回调 | ⚠️ 需完善 |
| `/recharge/orders` | GET | 获取订单列表 | ✅ 已实现 |

#### 分享模块 (share_routes.py)
| 接口 | 方法 | 说明 | 状态 |
|------|------|------|------|
| `/share/create` | POST | 创建分享记录 | ⚠️ 需实现 |
| `/share/stats` | GET | 获取分享统计 | ⚠️ 需实现 |
| `/share/discount` | GET | 获取优惠比例 | ⚠️ 需实现 |

---

## ⚠️ 五、一块变需要新增/完善的API

### 5.1 🔴 高优先级（春节上线必需）

#### 1. 支付接口对接
```python
# 需要实现真实的支付对接
POST /payment/wechat/create     # 微信支付下单
POST /payment/wechat/notify     # 微信支付回调
POST /payment/alipay/create     # 支付宝支付下单
POST /payment/alipay/notify     # 支付宝支付回调
POST /payment/douyin/create     # 抖音支付下单
POST /payment/douyin/notify     # 抖音支付回调
GET  /payment/query/{order_id}  # 查询支付状态
```

#### 2. 分享裂变接口
```python
POST /share/create              # 创建分享记录
POST /share/template            # 支付前模板分享
POST /share/result              # 支付后结果图分享
GET  /share/discount/{user_id}  # 获取用户可享优惠
GET  /share/stats/{share_id}    # 分享统计数据
```

#### 3. 图片上传接口
```python
POST /upload/image              # 上传原始图片
POST /upload/tos-signature      # 获取TOS上传签名（直传）
```

#### 4. AI生成回调接口
```python
POST /generate/callback         # 火山引擎AI生成完成回调
```

### 5.2 🟡 中优先级（重要功能）

#### 1. 定制服务接口
```python
POST /custom/logo               # 上传定制Logo
POST /custom/slogan             # 设置定制Slogan
GET  /custom/preview            # 预览定制效果
```

#### 2. 海报生成接口
```python
POST /poster/generate           # 生成带二维码海报
GET  /poster/templates          # 获取海报模板列表
```

#### 3. 渠道分销接口
```python
POST /distribution/bind         # 绑定分销渠道
GET  /distribution/qr/{employee_id}  # 获取员工专属二维码
```

### 5.3 🟢 低优先级（后续优化）

#### 1. 用户管理增强
```python
GET  /user/history              # 使用历史
GET  /user/statistics           # 统计数据
POST /user/feedback             # 用户反馈
```

#### 2. 退款接口
```python
POST /refund/apply              # 申请退款
GET  /refund/status/{refund_id} # 退款状态查询
```

---

## 📊 六、API接口完整性评估

### 6.1 已实现 vs 待开发统计

| 模块 | 已实现 | 待开发 | 完成度 |
|------|--------|--------|--------|
| 用户模块 | 4 | 2 | 67% |
| 生成模块 | 5 | 1 | 83% |
| 充值模块 | 3 | 7 | 30% |
| 分享模块 | 0 | 5 | 0% |
| 支付模块 | 1 | 7 | 12% |
| 上传模块 | 0 | 2 | 0% |
| 定制模块 | 0 | 3 | 0% |
| 海报模块 | 0 | 2 | 0% |
| **总计** | **13** | **29** | **31%** |

### 6.2 参考AIActive项目可复用代码

| 功能模块 | AIActive代码位置 | 可复用度 |
|----------|------------------|----------|
| 支付API | `AIActive\backend\api\payment.py` | 🟢 高（80%可复用） |
| 上传API | `AIActive\backend\api\upload.py` | 🟢 高（90%可复用） |
| AI生成API | `AIActive\backend\api\generate.py` | 🟡 中（需适配） |
| 邀请/分享API | `AIActive\backend\api\invite.py` | 🟡 中（需重构） |

---

## 🔗 七、API接口详细设计（新增）

### 7.1 支付接口设计（参考AIActive）

#### POST /payment/wechat/create
```python
# 请求体
{
    "order_id": "ORD1234567890",
    "amount": 100,  # 单位：分
    "openid": "oXXXXX"
}

# 响应体
{
    "code": 200,
    "data": {
        "prepay_id": "wx123456",
        "qr_code_url": "weixin://wxpay/...",
        "payment_url": "weixin://..."
    }
}
```

### 7.2 分享裂变接口设计

#### POST /share/create
```python
# 请求体
{
    "user_id": 12345,
    "share_type": "template",  # template | result
    "template_id": 1,
    "result_id": null
}

# 响应体
{
    "code": 200,
    "data": {
        "share_id": "sh_abc123",
        "share_url": "https://tingsilly.com/one/share/abc123",
        "discount_rate": 0.05,  # 5%优惠
        "expire_at": "2026-03-15 12:00:00"
    }
}
```

### 7.3 上传接口设计

#### POST /upload/tos-signature
```python
# 请求体
{
    "filename": "user_photo.jpg",
    "content_type": "image/jpeg"
}

# 响应体
{
    "code": 200,
    "data": {
        "upload_url": "https://tos-cn-beijing.xxx.com/...",
        "signature": "xxx",
        "expires": 3600,
        "object_key": "application/one/user_photo_123.jpg"
    }
}
```

---

## 📝 八、数据库表补充建议

### 8.1 需要新增的表

#### 1. 用户表 (one_users)
```sql
CREATE TABLE one_users (
    id BIGSERIAL PRIMARY KEY,
    openid VARCHAR(64) UNIQUE NOT NULL,
    unionid VARCHAR(64),
    nickname VARCHAR(100),
    avatar_url VARCHAR(500),
    phone VARCHAR(20),
    scene_type VARCHAR(20) NOT NULL,  -- 'personal' | 'activity'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. 风格表 (one_styles)
```sql
CREATE TABLE one_styles (
    id SERIAL PRIMARY KEY,
    style_id VARCHAR(20) UNIQUE NOT NULL,  -- jst000001
    name VARCHAR(100) NOT NULL,
    description TEXT,
    thumbnail VARCHAR(500),
    preview_urls TEXT[],  -- 数组
    category VARCHAR(50),
    is_video_supported BOOLEAN DEFAULT false,
    price_image INTEGER DEFAULT 1,
    price_video_per_second DECIMAL DEFAULT 3.2,
    is_active BOOLEAN DEFAULT true
);
```

---

## 🎯 九、关键问题与建议

### 9.1 ⚠️ 关键问题

1. **支付接口未真实对接**
   - 现有代码仅模拟，需对接真实微信/支付宝SDK
   - 需配置支付证书和回调地址

2. **分享裂变体系未完整实现**
   - 优惠比例计算逻辑存在，但接口缺失
   - 需要前端配合实现分享功能

3. **AI生成回调机制不完善**
   - 需要火山引擎回调接口
   - 需要异步任务状态同步机制

4. **用户体系需完善**
   - 微信登录需真实对接
   - 区分临时用户(activity)和正式用户(personal)

### 9.2 💡 技术建议

1. **复用AIActive代码**
   - 支付模块：80%可复用
   - 上传模块：90%可复用
   - 需适配火山引擎API调用

2. **优先级开发顺序**
   ```
   第一阶段（核心）：
   ├─ 微信登录对接
   ├─ 支付接口对接
   └─ 图片上传直传TOS
   
   第二阶段（重要）：
   ├─ AI生成完整流程
   ├─ 分享裂变功能
   └─ 订单状态同步
   
   第三阶段（优化）：
   ├─ 定制服务
   ├─ 海报生成
   └─ 渠道分销
   ```

3. **配置管理**
   - 需要配置文件区分环境（开发/测试/生产）
   - 需要配置火山引擎API密钥
   - 需要配置TOS访问密钥
   - 需要配置支付商户信息

---

## 📌 十、总结

### 10.1 现有基础
- ✅ 数据库设计完善（核心表已创建）
- ✅ 基础API框架搭建完成（FastAPI）
- ✅ 成长分体系设计完整
- ✅ AIActive参考代码可复用度高

### 10.2 待开发重点
- 🔴 支付接口对接（微信/支付宝/抖音）
- 🔴 分享裂变功能实现
- 🟡 AI生成完整流程
- 🟡 图片上传直传

### 10.3 技术风险
- ⚠️ 支付对接复杂度高（涉及证书、签名验证）
- ⚠️ AI生成异步回调需要稳定的状态同步
- ⚠️ 分享裂变优惠计算需要精确的金额计算

---

**文档版本**: v1.0  
**最后更新**: 2026-02-15 09:35
