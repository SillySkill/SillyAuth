# 一块变项目 - 测试报告

**测试日期**: 2026-02-15  
**测试人员**: AI·8002 (傻测试)  
**测试版本**: v1.0  
**测试状态**: ⚠️ 发现多处问题

---

## 📋 测试概览

| 测试项 | 数量 | 通过 | 失败 | 警告 |
|--------|------|------|------|------|
| 前端页面 | 5 | 2 | 2 | 1 |
| 后端API | 8 | 5 | 2 | 1 |
| 数据库连接 | 1 | 1 | 0 | 0 |
| 功能流程 | 4 | 2 | 1 | 1 |
| **总计** | **18** | **10** | **5** | **3** |

**整体通过率**: 55.6%

---

## 1️⃣ 前端页面测试

### 1.1 首页 (pages/index/index.ts)

**状态**: ✅ 通过 (有警告)

**功能点测试**:
- ✅ 轮播图加载
- ✅ 分类切换
- ✅ 风格列表加载
- ✅ 下拉刷新
- ✅ 上拉加载更多
- ⚠️ 风格卡片点击事件处理复杂

**代码质量**:
```typescript
// 问题：onStyleTap 中的styleId获取逻辑过于复杂
const style = e.detail.style || e.detail;
const styleId = style.styleId || style.id;
// 建议统一事件数据格式
```

**建议**: 
- 统一组件事件传递的数据格式
- 减少console.log调试代码

---

### 1.2 登录页 (pages/login/login.ts)

**状态**: ✅ 通过

**功能点测试**:
- ✅ 微信一键登录
- ✅ 用户协议勾选
- ✅ Token存储
- ✅ 游客模式
- ✅ 手机号登录(备用)

**代码质量**: 良好，有完善的错误处理

---

### 1.3 上传页 (pages/upload/upload.ts)

**状态**: ❌ 失败

**Bug清单**:

| ID | 严重程度 | 问题描述 | 位置 |
|----|---------|---------|------|
| F-001 | 🔴 高 | 上传后未保存服务器返回的URL | uploadImages方法 |
| F-002 | 🟡 中 | stylePrice参数未从上一页传递 | onLoad方法 |
| F-003 | 🟡 中 | 缺少图片大小和格式校验 | onChooseImage方法 |

**问题代码**:
```typescript
// F-001: 上传后的URL未使用
const uploadedUrls: string[] = [];
for (const path of localPaths) {
  // ... 上传逻辑
  uploadedUrls.push((data.data as any).url);
}
// ❌ uploadedUrls 没有被使用或保存到 data 中！
```

**建议**:
```typescript
// 修复建议：保存上传后的URL
this.setData({
  uploadedUrls: [...this.data.uploadedUrls, ...uploadedUrls]
});
```

---

### 1.4 生成页 (pages/generate/generate.ts)

**状态**: ❌ 失败

**Bug清单**:

| ID | 严重程度 | 问题描述 | 位置 |
|----|---------|---------|------|
| F-004 | 🔴 高 | stylePrice硬编码为10，应从上一页传递 | onLoad方法 |
| F-005 | 🟡 中 | 缺少生成失败的回退逻辑 | onStartGenerate方法 |
| F-006 | 🟡 中 | 余额检查后未锁定状态，可能重复提交 | onStartGenerate方法 |

**问题代码**:
```typescript
// F-004: 价格硬编码
const stylePrice = 10; // ❌ 默认价格，应该从上一页传递
this.setData({
  totalPrice: imageList.length * stylePrice
});
```

---

### 1.5 结果页 (pages/result/result.ts)

**状态**: ✅ 通过 (有警告)

**功能点测试**:
- ✅ 生成结果加载
- ✅ 图片预览
- ✅ 保存到相册
- ✅ 分享功能
- ✅ NFT信息展示
- ⚠️ 失败时使用模拟数据，可能隐藏真实错误

---

## 2️⃣ 后端API测试

### 2.1 用户登录接口 (/api/v1/yibian/user/login)

**状态**: ✅ 通过

**测试结果**:
```bash
# 测试命令
curl -X POST "http://localhost:8000/api/v1/yibian/user/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"password123"}'

# 响应
{
  "user_id": 1,
  "username": "user1",
  "token": "user1_abc123...",
  "credits": 1000
}
```

**问题**: 
- ⚠️ Token生成过于简单，应使用JWT
- ⚠️ 密码哈希使用SHA256，建议使用bcrypt

---

### 2.2 模板列表接口 (/api/v1/yibian/templates)

**状态**: ✅ 通过

**测试结果**:
- ✅ 分页正常
- ✅ 分类筛选正常
- ✅ 免费/付费筛选正常
- ✅ 排序正常

---

### 2.3 照片上传接口 (/api/v1/yibian/photo/upload)

**状态**: ❌ 失败

**Bug清单**:

| ID | 严重程度 | 问题描述 | 位置 |
|----|---------|---------|------|
| B-001 | 🔴 高 | 缩略图生成直接复制原图，未真正压缩 | upload_photo方法 |
| B-002 | 🟡 中 | 缺少图片尺寸验证，可能被恶意上传 | upload_photo方法 |
| B-003 | 🟡 中 | 文件名可能冲突（多用户同时上传） | upload_photo方法 |

**问题代码**:
```python
# B-001: 缩略图生成逻辑错误
thumbnail_filename = f"thumb_{filename}"
thumbnail_path = UPLOAD_DIR / thumbnail_filename
# 这里应该使用PIL生成缩略图，简化处理直接复制 ❌
shutil.copy(file_path, thumbnail_path)
```

---

### 2.4 AI生成接口 (/api/v1/yibian/ai/generate)

**状态**: ⚠️ 警告

**问题**:
- ⚠️ 火山引擎API调用被注释，实际使用模拟数据
- ⚠️ 异步任务使用asyncio.create_task，服务重启会丢失任务状态
- ⚠️ API Key硬编码在代码中

**问题代码**:
```python
# API Key 硬编码 - 安全风险
VOLCANO_API_KEY = "REDACTED_LLM_API_KEY"  # ❌ 应使用环境变量

# 异步调用使用内存，不持久化
asyncio.create_task(call_volcano_api(...))  # ❌ 服务重启任务丢失
```

---

### 2.5 支付接口 (/api/v1/yibian/payment/create)

**状态**: ✅ 通过

**测试结果**:
- ✅ 订单号生成正常
- ✅ 订单过期时间设置正确
- ⚠️ 微信支付为模拟，未实际对接

---

### 2.6 支付回调接口 (/api/v1/yibian/payment/callback)

**状态**: ❌ 失败

**Bug清单**:

| ID | 严重程度 | 问题描述 | 位置 |
|----|---------|---------|------|
| B-004 | 🔴 高 | 未验证微信支付签名，存在安全漏洞 | payment_callback方法 |
| B-005 | 🔴 高 | 接受JSON格式，但微信回调是XML | payment_callback方法 |

**问题代码**:
```python
# B-004 & B-005: 回调验证缺失
@router.post("/payment/callback")
async def payment_callback(data: dict, db: Session = Depends(get_db)):
    # 验证签名（实际应该验证微信签名）
    # 这里简化处理 ❌
    
    # 接收的是dict，但微信回调是XML格式 ❌
```

---

### 2.7 NFT生成接口 (/api/v1/yibian/nft/generate)

**状态**: ✅ 通过

**测试结果**:
- ✅ 验证生成记录存在
- ✅ 检查重复NFT生成
- ✅ 创建支付订单

---

### 2.8 NFT查询接口 (/api/v1/yibian/nft/{nft_id})

**状态**: ✅ 通过

**测试结果**:
- ✅ 单个NFT查询正常
- ✅ 用户NFT列表查询正常
- ✅ 分页正常

---

## 3️⃣ 数据库连接测试

**状态**: ✅ 通过

**测试结果**:
```python
# database.py 配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sillymd.db")
# ✅ 支持环境变量配置
# ✅ SQLite连接配置正确
# ✅ Session管理正常
```

**模型测试**:
- ✅ User模型正常
- ✅ Template模型正常
- ✅ UserPhoto模型正常
- ✅ AIGeneration模型正常
- ✅ PaymentOrder模型正常
- ✅ NFTCollection模型正常
- ✅ UserCredits模型正常
- ✅ CreditTransaction模型正常

---

## 4️⃣ 功能流程测试

### 4.1 用户登录流程

**状态**: ✅ 通过

**流程**:
1. 用户点击登录 → ✅
2. 获取微信code → ✅
3. 获取用户信息 → ✅
4. 调用后端接口 → ✅
5. 保存Token → ✅
6. 跳转首页 → ✅

---

### 4.2 图片生成流程

**状态**: ❌ 失败

**流程**:
1. 选择风格 → ✅
2. 上传图片 → ⚠️ (上传后URL未保存)
3. 确认生成 → ⚠️ (价格硬编码)
4. AI处理 → ⚠️ (模拟数据)
5. 显示结果 → ✅

**问题**: F-001, F-004 导致流程不完整

---

### 4.3 支付流程

**状态**: ⚠️ 警告

**流程**:
1. 创建订单 → ✅
2. 生成支付二维码 → ⚠️ (模拟)
3. 用户支付 → ❌ (未验证签名)
4. 回调处理 → ❌ (安全漏洞)
5. 更新积分 → ✅

---

### 4.4 NFT流程

**状态**: ✅ 通过

**流程**:
1. 选择生成结果 → ✅
2. 填写NFT信息 → ✅
3. 创建支付订单 → ✅
4. 铸造NFT → ⚠️ (模拟)
5. 查看NFT → ✅

---

## 🐛 Bug清单汇总

### 前端Bug (6个)

| ID | 严重程度 | 模块 | 问题描述 | 状态 |
|----|---------|------|---------|------|
| F-001 | 🔴 高 | upload | 上传后URL未保存 | 待修复 |
| F-002 | 🟡 中 | upload | stylePrice未传递 | 待修复 |
| F-003 | 🟡 中 | upload | 缺少图片校验 | 待修复 |
| F-004 | 🔴 高 | generate | 价格硬编码 | 待修复 |
| F-005 | 🟡 中 | generate | 缺少失败回退 | 待修复 |
| F-006 | 🟡 中 | generate | 可能重复提交 | 待修复 |

### 后端Bug (5个)

| ID | 严重程度 | 模块 | 问题描述 | 状态 |
|----|---------|------|---------|------|
| B-001 | 🔴 高 | upload | 缩略图未压缩 | 待修复 |
| B-002 | 🟡 中 | upload | 缺少尺寸验证 | 待修复 |
| B-003 | 🟡 中 | upload | 文件名可能冲突 | 待修复 |
| B-004 | 🔴 高 | payment | 未验证支付签名 | 待修复 |
| B-005 | 🔴 高 | payment | 回调格式错误 | 待修复 |

### 安全问题 (3个)

| ID | 严重程度 | 位置 | 问题描述 | 状态 |
|----|---------|------|---------|------|
| S-001 | 🔴 高 | api_yibian.py | API Key硬编码 | 待修复 |
| S-002 | 🔴 高 | api_yibian.py | Token生成简单 | 待修复 |
| S-003 | 🟡 中 | api_yibian.py | 密码哈希弱 | 待修复 |

---

## 🔧 修复建议

### 高优先级 (立即修复)

#### 1. F-001 & F-004: 上传URL和价格传递

**upload.ts 修改**:
```typescript
// 1. 添加uploadedUrls到data
interface UploadData {
  // ... 现有字段
  uploadedUrls: string[];  // 新增
}

// 2. 保存上传后的URL
this.setData({
  uploadedUrls: [...this.data.uploadedUrls, ...uploadedUrls]
});

// 3. 传递价格到下一页
wx.navigateTo({
  url: `/pages/generate/generate?styleId=${this.data.styleId}&stylePrice=${this.data.stylePrice}&...`
});
```

**generate.ts 修改**:
```typescript
// 从参数获取价格
const { styleId, styleName, images, stylePrice } = options;
this.setData({
  stylePrice: Number(stylePrice) || 10
});
```

#### 2. B-001: 缩略图生成

```python
from PIL import Image

def create_thumbnail(source_path, thumb_path, size=(200, 200)):
    with Image.open(source_path) as img:
        img.thumbnail(size)
        img.save(thumb_path, quality=85)

# 替换原来的复制操作
create_thumbnail(file_path, thumbnail_path)
```

#### 3. B-004 & B-005: 支付回调

```python
import xml.etree.ElementTree as ET
from wechatpay import WeChatPay  # 使用官方SDK

@router.post("/payment/callback")
async def payment_callback(request: Request, db: Session = Depends(get_db)):
    # 1. 获取原始XML数据
    xml_data = await request.body()
    
    # 2. 验证签名
    if not verify_wechat_signature(xml_data):
        return {"code": "FAIL", "message": "签名验证失败"}
    
    # 3. 解析XML
    root = ET.fromstring(xml_data)
    order_no = root.find('out_trade_no').text
    # ...
```

#### 4. S-001: API Key安全

```python
import os

# 使用环境变量
VOLCANO_API_KEY = os.getenv("VOLCANO_API_KEY")
WECHAT_PAY_MCH_ID = os.getenv("WECHAT_PAY_MCH_ID")
WECHAT_PAY_API_KEY = os.getenv("WECHAT_PAY_API_KEY")

# 启动时验证
if not VOLCANO_API_KEY:
    raise ValueError("请设置环境变量 VOLCANO_API_KEY")
```

### 中优先级 (近期修复)

#### 5. S-002: JWT认证

```python
from datetime import timedelta
from fastapi_jwt_auth import AuthJWT

@router.post("/user/login")
async def user_login(request: UserLoginRequest, Authorize: AuthJWT = Depends()):
    # ... 验证用户
    
    # 创建JWT Token
    access_token = Authorize.create_access_token(
        subject=str(user.id),
        expires_time=timedelta(days=7)
    )
    
    return {
        "user_id": user.id,
        "username": user.username,
        "token": access_token,
        "credits": balance
    }
```

#### 6. F-006: 防重复提交

```typescript
// generate.ts
data: {
  // ... 现有字段
  isSubmitting: false  // 新增
},

async onStartGenerate() {
  if (this.data.isSubmitting) return;  // 防止重复
  
  this.setData({ isSubmitting: true });
  
  try {
    // ... 生成逻辑
  } finally {
    this.setData({ isSubmitting: false });
  }
}
```

---

## 📊 测试结论

### 整体评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 功能完整性 | 6/10 | 核心功能基本实现，但关键流程有Bug |
| 代码质量 | 7/10 | 结构清晰，但缺少完善的错误处理 |
| 安全性 | 4/10 | 存在多个安全漏洞，需立即修复 |
| 可维护性 | 7/10 | 代码结构良好，有完善文档 |
| 用户体验 | 6/10 | 基本流程可用，但体验有提升空间 |

### 建议发布状态

**❌ 不建议直接发布生产环境**

**原因**:
1. 存在2个高危安全漏洞（支付签名、API Key暴露）
2. 核心流程（图片生成）存在数据丢失Bug
3. 支付回调存在格式和安全问题

### 修复后可发布的条件

- [ ] 修复所有高危Bug (F-001, F-004, B-001, B-004, B-005)
- [ ] 修复安全问题 (S-001, S-002, S-003)
- [ ] 完成集成测试
- [ ] 代码审查通过

---

## 📝 测试附录

### 测试环境

- **操作系统**: Windows 10/11
- **Node.js**: v24.13.0
- **Python**: 3.x
- **数据库**: SQLite
- **测试工具**: curl, Postman

### 相关文件

- 前端代码: `silly-complete/silly/One/miniprogram/`
- 后端代码: `silly-complete/silly/web/app/backend/`
- API文档: `API_TEST_GUIDE.md`

### 联系方式

如有问题，请联系测试人员：AI·8002 (傻测试)

---

**报告生成时间**: 2026-02-15 11:00:00  
**报告版本**: v1.0
