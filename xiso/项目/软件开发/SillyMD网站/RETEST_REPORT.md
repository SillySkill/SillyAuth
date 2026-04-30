# 一块变项目 - 复测报告

**测试日期**: 2026-02-15  
**测试人员**: AI·8002 (傻测试) - 功能测试专员  
**测试版本**: v1.0-fixed  
**测试类型**: 回归复测  

---

## 📋 复测概览

| 指标 | 值 |
|------|-----|
| 原Bug总数 | 6 (高危) |
| 已修复 | 4 |
| 未修复 | 2 |
| 新发现问题 | 0 |
| **修复率** | **66.7%** |

---

## 🔴 高危Bug复测结果

### Bug清单

| ID | 模块 | 问题描述 | 状态 | 修复质量 |
|----|------|---------|------|---------|
| F-001 | 前端-upload.ts | 上传后URL未保存 | ❌ 未修复 | - |
| F-004 | 前端-generate.ts | 价格硬编码 | ❌ 未修复 | - |
| B-001 | 后端-api_yibian.py | 缩略图未压缩 | ✅ 已修复 | 优秀 |
| B-004 | 后端-api_yibian.py | 未验证支付签名 | ✅ 已修复 | 良好 |
| B-005 | 后端-api_yibian.py | 支付回调格式错误 | ✅ 已修复 | 良好 |
| S-001 | 后端-api_yibian.py | API Key硬编码 | ✅ 已修复 | 优秀 |

---

## 📝 详细复测分析

### ❌ F-001: 上传后URL未保存 (前端)

**文件**: `silly/One/miniprogram/pages/upload/upload.ts`

**问题**: 上传成功后，服务器返回的URL没有保存到data中，导致后续页面无法使用。

**当前代码**:
```typescript
// uploadImages 方法
async uploadImages(localPaths: string[]) {
  // ...
  const uploadedUrls: string[] = [];
  for (const path of localPaths) {
    // 上传逻辑...
    uploadedUrls.push((data.data as any).url);
  }
  
  // ❌ 问题：uploadedUrls 没有保存到 this.data 中！
  this.setData({ uploading: false });
}

// onNextStep 方法
onNextStep() {
  wx.navigateTo({
    // ❌ 问题：没有传递 serverUrls 参数
    url: `/pages/generate/generate?styleId=${this.data.styleId}&styleName=${encodeURIComponent(this.data.styleName)}&images=${encodeURIComponent(JSON.stringify(this.data.images))}`
  });
}
```

**修复建议**:
```typescript
// 1. 添加 serverUrls 到 data interface
interface UploadData {
  // ... 现有字段
  serverUrls: string[];  // 新增
}

// 2. uploadImages 方法末尾添加
this.setData({ 
  uploading: false,
  serverUrls: [...this.data.serverUrls, ...uploadedUrls]  // 保存服务器URL
});

// 3. onNextStep 方法添加参数
url: `/pages/generate/generate?...&serverUrls=${encodeURIComponent(JSON.stringify(this.data.serverUrls))}`
```

**风险等级**: 🔴 高 - 核心功能受损

---

### ❌ F-004: 价格硬编码 (前端)

**文件**: `silly/One/miniprogram/pages/generate/generate.ts`

**问题**: 价格固定为10，没有从上一页传递，导致显示价格与实际不符。

**当前代码**:
```typescript
onLoad(options: any) {
  const { styleId, styleName, images } = options;  // ❌ 缺少 stylePrice
  
  try {
    const imageList = JSON.parse(decodeURIComponent(images));
    const stylePrice = 10; // ❌ 硬编码价格！
    
    this.setData({
      totalPrice: imageList.length * stylePrice
    });
  }
}
```

**修复建议**:
```typescript
onLoad(options: any) {
  const { styleId, styleName, images, stylePrice } = options;  // 获取价格
  
  try {
    const imageList = JSON.parse(decodeURIComponent(images));
    const price = Number(stylePrice) || 10;  // 使用传递的价格，默认10
    
    this.setData({
      stylePrice: price,
      totalPrice: imageList.length * price
    });
  }
}
```

**风险等级**: 🔴 高 - 用户看到的金额可能错误

---

### ✅ B-001: 缩略图未压缩 (后端)

**文件**: `silly/web/app/backend/api_yibian.py`

**修复方案**: 添加了 `create_thumbnail` 函数，使用PIL进行真正的图片压缩。

**代码验证**:
```python
def create_thumbnail(source_path: str, thumb_path: str, size: tuple = (200, 200)) -> bool:
    """创建缩略图"""
    if not PIL_AVAILABLE:
        return False
    
    try:
        with Image.open(source_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)  # 使用高质量重采样
            img.convert('RGB').save(thumb_path, 'JPEG', quality=85)  # 质量85
            return True
    except Exception as e:
        print(f"创建缩略图失败: {e}")
        return False
```

**修复质量**: ⭐⭐⭐⭐⭐ 优秀
- 使用PIL.Image进行真正的压缩
- 保持宽高比
- 质量设置为85，平衡文件大小和画质
- 有异常处理和降级方案

---

### ✅ B-004: 未验证支付签名 (后端)

**文件**: `silly/web/app/backend/api_yibian.py`

**修复方案**: 添加了 `verify_wechat_sign` 函数，实现微信支付签名验证。

**代码验证**:
```python
def verify_wechat_sign(xml_data: bytes, api_key: str) -> bool:
    """验证微信支付签名"""
    if not api_key:
        print("警告: 微信支付API Key未配置，跳过签名验证")
        return True  # 未配置时跳过（仅开发环境）
    
    try:
        root = ET.fromstring(xml_data)
        sign = root.find('sign').text
        
        # 收集所有字段（除了sign）
        params = {}
        for child in root:
            if child.tag != 'sign' and child.text:
                params[child.tag] = child.text
        
        # 按字典序排序并拼接
        sorted_params = sorted(params.items())
        sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_str += f"&key={api_key}"
        
        # 计算签名
        calculated_sign = hashlib.md5(sign_str.encode()).hexdigest().upper()
        return calculated_sign == sign
    except Exception as e:
        print(f"签名验证失败: {e}")
        return False
```

**修复质量**: ⭐⭐⭐⭐ 良好
- 实现了标准的微信支付签名验证流程
- 有开发环境的兼容处理
- 建议在生产环境强制验证

---

### ✅ B-005: 支付回调格式错误 (后端)

**文件**: `silly/web/app/backend/api_yibian.py`

**修复方案**: 修改回调接口接收XML格式数据。

**代码验证**:
```python
@router.post("/payment/callback")
async def payment_callback(request: Request, db: Session = Depends(get_db)):
    # 【修复B-005】获取原始XML数据
    xml_data = await request.body()
    
    # 【修复B-004】验证签名
    if WECHAT_PAY_API_KEY and not verify_wechat_sign(xml_data, WECHAT_PAY_API_KEY):
        return {"code": "FAIL", "message": "签名验证失败"}
    
    # 【修复B-005】解析XML
    try:
        root = ET.fromstring(xml_data)
        order_no = root.find('out_trade_no').text
        transaction_id = root.find('transaction_id').text
        result_code = root.find('result_code').text
    except Exception as e:
        return {"code": "FAIL", "message": f"XML解析失败: {e}"}
    
    # ... 业务逻辑
```

**修复质量**: ⭐⭐⭐⭐ 良好
- 正确接收XML格式
- 使用ElementTree解析
- 有异常处理

---

### ✅ S-001: API Key硬编码 (后端)

**文件**: `silly/web/app/backend/api_yibian.py`

**修复方案**: 所有敏感配置改用环境变量。

**代码验证**:
```python
# 【修复S-001】使用环境变量
VOLCANO_API_KEY = os.getenv("VOLCANO_API_KEY", "")
VOLCANO_API_URL = os.getenv("VOLCANO_API_URL", "https://api.volcengine.com/api/v3/image_generation")

# 微信支付配置（【修复S-001】从环境变量读取）
WECHAT_PAY_MCH_ID = os.getenv("WECHAT_PAY_MCH_ID", "")
WECHAT_PAY_APP_ID = os.getenv("WECHAT_PAY_APP_ID", "")
WECHAT_PAY_API_KEY = os.getenv("WECHAT_PAY_API_KEY", "")

# JWT配置
JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret-in-production")

# 启动时验证配置
if not VOLCANO_API_KEY:
    print("警告: 未设置环境变量 VOLCANO_API_KEY，AI生成功能将使用模拟数据")
if not JWT_SECRET or JWT_SECRET == "change-this-secret-in-production":
    print("警告: JWT_SECRET 未设置或使用默认值，请在生产环境中修改")
```

**修复质量**: ⭐⭐⭐⭐⭐ 优秀
- 所有敏感配置都使用环境变量
- 启动时有配置验证和警告
- 默认值安全（空字符串或警告性字符串）

---

## 🔒 安全性验证

### 已修复的安全问题

| ID | 问题 | 修复方案 | 状态 |
|----|------|---------|------|
| S-001 | API Key硬编码 | 使用 os.getenv() | ✅ 已修复 |
| S-002 | Token生成简单 | 添加JWT支持 | ✅ 已修复 |
| S-003 | 密码哈希弱 | 添加bcrypt支持 | ✅ 已修复 |

### 安全配置检查

```python
# ✅ 环境变量隔离
VOLCANO_API_KEY = os.getenv("VOLCANO_API_KEY", "")
WECHAT_PAY_API_KEY = os.getenv("WECHAT_PAY_API_KEY", "")
JWT_SECRET = os.getenv("JWT_SECRET", "")

# ✅ JWT Token
def create_jwt_token(user_id: int, username: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {"sub": str(user_id), "username": username, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# ✅ bcrypt密码哈希
def hash_password(password: str) -> str:
    if BCRYPT_AVAILABLE:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    else:
        return hashlib.sha256(password.encode()).hexdigest()

# ✅ 微信支付签名验证
def verify_wechat_sign(xml_data: bytes, api_key: str) -> bool:
    # ... 完整的签名验证逻辑
```

### 安全评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 敏感信息保护 | ⭐⭐⭐⭐⭐ | 已改用环境变量 |
| 认证安全 | ⭐⭐⭐⭐ | JWT+bcrypt，兼容旧版 |
| 支付安全 | ⭐⭐⭐⭐ | 签名验证已实现 |
| **整体安全性** | **4.5/5** | 后端安全性良好 |

---

## 🧪 功能完整性测试

### 核心流程测试

| 流程 | 状态 | 说明 |
|------|------|------|
| 用户登录 | ✅ 通过 | JWT认证正常 |
| 模板浏览 | ✅ 通过 | 分页筛选正常 |
| 图片上传 | ⚠️ 部分通过 | 上传成功但URL未保存 |
| AI生成 | ⚠️ 部分通过 | 价格显示可能错误 |
| 支付流程 | ✅ 通过 | 签名验证已实现 |
| NFT铸造 | ✅ 通过 | 流程完整 |

### 代码质量评估

| 维度 | 后端 | 前端 |
|------|------|------|
| 代码结构 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 错误处理 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 安全性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 可维护性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **平均分** | **4.5/5** | **3.5/5** |

---

## 📊 复测结论

### 总体评估

| 指标 | 结果 |
|------|------|
| 6个高危Bug修复率 | **66.7%** (4/6) |
| 后端安全性 | **优秀** (4.5/5) |
| 前端稳定性 | **一般** (3.5/5) |
| 核心流程完整性 | **部分通过** |

### 🔴 不通过原因

1. **F-001未修复**: 上传URL未保存，导致生成流程可能失败
2. **F-004未修复**: 价格硬编码，用户看到的金额可能与实际不符

### 阻塞发布的问题

| 优先级 | 问题 | 影响 |
|--------|------|------|
| 🔴 P0 | F-001 | 图片生成流程可能完全失败 |
| 🔴 P0 | F-004 | 用户支付金额错误 |

---

## ✅ 发布前必须完成

### 必须修复 (P0)

- [ ] **F-001**: upload.ts - 保存服务器返回的URL到data
- [ ] **F-001**: upload.ts - 在onNextStep中传递serverUrls参数
- [ ] **F-004**: generate.ts - 从options获取stylePrice参数

### 建议优化 (P1)

- [ ] 添加图片大小校验（限制5MB）
- [ ] 添加防重复提交逻辑
- [ ] 添加生成失败的重试机制

### 环境配置 (P0)

生产环境部署前，必须配置以下环境变量：

```bash
# .env 文件
VOLCANO_API_KEY=your_actual_api_key
WECHAT_PAY_MCH_ID=your_mch_id
WECHAT_PAY_APP_ID=your_app_id
WECHAT_PAY_API_KEY=your_api_key
JWT_SECRET=your_strong_random_secret_at_least_32_chars
```

---

## 🏁 最终结论

| 结论 | ❌ **不通过** |
|------|-------------|
| 原因 | 前端2个高危Bug未修复，核心流程受阻 |
| 建议 | 修复F-001和F-004后重新提交测试 |

---

**复测完成时间**: 2026-02-15 11:30:00  
**报告版本**: v1.0  
**测试人员**: AI·8002 (傻测试)

---

## 附录：快速修复代码

### F-001 修复代码 (upload.ts)

```typescript
// 1. 修改 interface
interface UploadData {
  styleId: string;
  styleName: string;
  styleThumbnail: string;
  stylePrice: number;
  images: string[];
  serverUrls: string[];  // 【新增】
  maxImages: number;
  uploading: boolean;
  uploadProgress: number;
  selectedImage: string;
  showCropper: boolean;
}

// 2. 初始化 data
data: {
  // ...
  serverUrls: []  // 【新增】
}

// 3. 修改 uploadImages 方法末尾
this.setData({ 
  uploading: false,
  serverUrls: [...this.data.serverUrls, ...uploadedUrls]  // 【新增】
});

// 4. 修改 onNextStep 方法
wx.navigateTo({
  url: `/pages/generate/generate?styleId=${this.data.styleId}&styleName=${encodeURIComponent(this.data.styleName)}&stylePrice=${this.data.stylePrice}&images=${encodeURIComponent(JSON.stringify(this.data.images))}&serverUrls=${encodeURIComponent(JSON.stringify(this.data.serverUrls))}`
});
```

### F-004 修复代码 (generate.ts)

```typescript
// 1. 修改 interface
interface GenerateData {
  styleId: string;
  styleName: string;
  stylePrice: number;  // 【新增】
  images: string[];
  serverUrls: string[];  // 【新增】
  // ...
}

// 2. 修改 onLoad 方法
onLoad(options: any) {
  const { styleId, styleName, images, stylePrice, serverUrls } = options;  // 【修改】
  
  try {
    const imageList = JSON.parse(decodeURIComponent(images));
    const serverUrlList = serverUrls ? JSON.parse(decodeURIComponent(serverUrls)) : [];  // 【新增】
    const price = Number(stylePrice) || 10;  // 【修改】使用传递的价格
    
    this.setData({
      styleId,
      styleName: decodeURIComponent(styleName || '默认风格'),
      stylePrice: price,  // 【新增】
      images: imageList,
      serverUrls: serverUrlList,  // 【新增】
      imageCount: imageList.length,
      totalPrice: imageList.length * price
    });
  }
}

// 3. 修改 onStartGenerate 方法
// 使用 serverUrls 而不是 images
const urlsToUse = this.data.serverUrls.length > 0 
  ? this.data.serverUrls 
  : this.data.images;

const res = await http.post('/api/one/generate/create', {
  styleId: this.data.styleId,
  images: urlsToUse,  // 【修改】
  count: this.data.imageCount
});
```

修复完成后，请重新提交测试。
