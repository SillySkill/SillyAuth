# SillyAuth - 身份验证器功能设计文档

## 1. 项目概述

### 1.1 项目名称
**SillyAuth** - 跨平台身份验证器

### 1.2 项目目标
开发一款与Google Authenticator功能一致的移动端身份验证器，支持Android、iOS、鸿蒙系统。

### 1.3 核心特性
- 基于TOTP（时间同步一次性密码）算法
- 二维码扫描快速添加账户
- 手动输入密钥添加账户
- 本地安全存储
- 跨平台支持（Android/iOS/鸿蒙）

---

## 2. 功能列表

### 2.1 核心功能

| 功能模块 | 功能名称 | 优先级 | 描述 |
|---------|---------|-------|------|
| 账户管理 | 扫描二维码添加 | P0 | 使用摄像头扫描TOTP二维码，自动解析并添加账户 |
| 账户管理 | 手动输入添加 | P0 | 手动输入账户名称和密钥添加账户 |
| 账户管理 | 账户列表展示 | P0 | 展示所有已添加的账户及其当前验证码 |
| 账户管理 | 验证码复制 | P0 | 一键复制当前验证码到剪贴板 |
| 账户管理 | 删除账户 | P0 | 删除指定账户 |
| 账户管理 | 编辑账户 | P1 | 修改账户名称 |
| 验证码 | 验证码生成 | P0 | 基于TOTP算法生成6位数字验证码 |
| 验证码 | 倒计时显示 | P0 | 显示验证码剩余有效时间（圆形进度条） |
| 验证码 | 刷新验证码 | P0 | 手动刷新当前显示的验证码 |

### 2.2 安全功能

| 功能模块 | 功能名称 | 优先级 | 描述 |
|---------|---------|-------|------|
| 应用锁 | 应用密码锁 | P1 | 启动应用时需要输入密码 |
| 应用锁 | 生物识别 | P1 | 支持指纹/面容解锁应用 |
| 数据安全 | 安全存储 | P0 | 使用加密方式存储账户密钥 |

### 2.3 辅助功能

| 功能模块 | 功能名称 | 优先级 | 描述 |
|---------|---------|-------|------|
| 账户排序 | 拖拽排序 | P1 | 通过拖拽调整账户显示顺序 |
| 搜索功能 | 搜索账户 | P2 | 根据账户名称搜索 |
| 主题设置 | 浅色/深色主题 | P2 | 切换应用主题 |
| 关于 | 版本信息 | P3 | 显示应用版本信息 |

---

## 3. TOTP算法实现

### 3.1 算法原理
TOTP (Time-based One-Time Password) 基于HMAC算法，结合当前时间戳生成一次性密码。

### 3.2 算法参数
- **密钥长度**: 20字节（160位）
- **验证码长度**: 6位数字
- **时间步长**: 30秒
- **哈希算法**: SHA-1

### 3.3 算法步骤
```
1. 获取当前Unix时间戳（秒）
2. 计算时间步长序号：counter = floor(current_time / 30)
3. 将counter转换为8字节大端字节序
4. 使用HMAC-SHA1(secret_key, counter)计算哈希
5. 取哈希最后4位作为偏移量
6. 从偏移量位置读取4字节，转换为31位整数
7. 取模1000000得到6位数字
8. 不足6位前面补0
```

---

## 4. 数据设计

### 4.1 账户数据模型

```dart
class AuthAccount {
  String id;           // 唯一标识符（UUID）
  String name;         // 账户名称（如：user@example.com）
  String issuer;       // 发卡方（如：Google, GitHub）
  String secret;       // Base32编码的密钥
  int digits;          // 验证码位数（默认6）
  int period;          // 时间步长（默认30秒）
  int sortOrder;       // 排序顺序
  DateTime createdAt;  // 创建时间
}
```

### 4.2 本地存储结构

使用Flutter的`flutter_secure_storage`进行安全存储：

```json
{
  "accounts": [
    {
      "id": "uuid-xxx",
      "name": "user@example.com",
      "issuer": "Google",
      "secret": "JBSWY3DPEHPK3PXP",
      "digits": 6,
      "period": 30,
      "sortOrder": 0,
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ],
  "settings": {
    "appLockEnabled": false,
    "biometricEnabled": false,
    "themeMode": "system"
  }
}
```

---

## 5. 界面设计

### 5.1 页面结构

```
App
├── 首页（账户列表）
│   ├── 顶部：应用标题 + 设置按钮
│   ├── 中间：账户列表（滚动）
│   │   └── 账户项：发卡方 + 账户名 + 验证码 + 倒计时
│   └── 底部：添加按钮（+）
├── 添加账户页面
│   ├── 扫描二维码选项
│   └── 手动输入选项
├── 账户详情/编辑页面
│   └── 编辑账户名称
└── 设置页面
    ├── 应用锁设置
    ├── 主题设置
    └── 关于
```

### 5.2 首页布局

```
┌─────────────────────────────┐
│  SillyAuth              ⚙️  │
├─────────────────────────────┤
│  ┌─────────────────────┐   │
│  │ Google              │   │
│  │ user@gmail.com     │   │
│  │        123 456      │ ↻ │
│  │  ████████░░ 25s    │   │
│  └─────────────────────┘   │
│                             │
│  ┌─────────────────────┐   │
│  │ GitHub             │   │
│  │ developer         │   │
│  │        789 012      │ ↻ │
│  │  ██████░░░░ 18s    │   │
│  └─────────────────────┘   │
│                             │
│                      [+]   │
└─────────────────────────────┘
```

### 5.3 交互设计

| 交互 | 行为 |
|-----|------|
| 点击验证码 | 复制到剪贴板，显示"已复制"Toast |
| 点击刷新按钮 | 立即刷新验证码显示 |
| 长按账户项 | 进入编辑/删除模式 |
| 下拉列表 | 刷新所有验证码 |
| 点击+按钮 | 打开添加账户页面 |

---

## 6. 技术架构

### 6.1 技术栈

| 层级 | 技术选型 |
|-----|---------|
| 框架 | Flutter 3.x |
| 语言 | Dart 3.x |
| 状态管理 | Provider / Riverpod |
| 本地存储 | flutter_secure_storage |
| 二维码扫描 | mobile_scanner |
| 加密 | crypto (Dart标准库) |
| UUID生成 | uuid |

### 6.2 项目结构

```
lib/
├── main.dart                 # 应用入口
├── app.dart                  # 应用配置
├── core/
│   ├── totp/                 # TOTP算法实现
│   │   └── totp_generator.dart
│   └── utils/                # 工具类
│       └── base32.dart
├── data/
│   ├── models/               # 数据模型
│   │   └── auth_account.dart
│   └── repositories/         # 数据仓库
│       └── account_repository.dart
├── features/
│   ├── home/                 # 首页
│   │   ├── home_screen.dart
│   │   └── widgets/
│   ├── add_account/          # 添加账户
│   │   ├── add_account_screen.dart
│   │   └── widgets/
│   ├── account_detail/       # 账户详情
│   └── settings/             # 设置
└── shared/
    ├── widgets/              # 共享组件
    ├── theme/                # 主题
    └── constants/            # 常量
```

---

## 7. 安全考虑

### 7.1 数据安全
- 密钥使用`flutter_secure_storage`存储在系统安全区域
- 不上传任何数据到服务器
- 不记录任何日志包含敏感信息

### 7.2 应用安全
- 支持应用锁（密码/生物识别）
- 离开应用后快速锁定
- 安全剪贴板（复制后自动清除）

---

## 8. 里程碑计划

### Phase 1: 核心功能
- [ ] 项目初始化
- [ ] TOTP算法实现
- [ ] 账户数据模型和存储
- [ ] 首页账户列表
- [ ] 验证码生成和显示
- [ ] 倒计时功能

### Phase 2: 账户管理
- [ ] 扫描二维码添加账户
- [ ] 手动输入添加账户
- [ ] 删除账户
- [ ] 编辑账户名称

### Phase 3: 安全功能
- [ ] 应用密码锁
- [ ] 生物识别解锁

### Phase 4: 增强功能
- [ ] 拖拽排序
- [ ] 搜索功能
- [ ] 主题切换

---

## 9. 多语言支持

### 9.1 支持语言
- 中文（简体）- zh
- 英文（English）- en

### 9.2 翻译内容

| Key | 中文 | English |
|-----|------|---------|
| app_name | 身份验证器 | Authenticator |
| add_account | 添加账户 | Add Account |
| scan_qrcode | 扫描二维码 | Scan QR Code |
| manual_input | 手动输入 | Manual Input |
| account_name | 账户名称 | Account Name |
| secret_key | 密钥 | Secret Key |
| issuer | 发行方 | Issuer |
| delete | 删除 | Delete |
| edit | 编辑 | Edit |
| cancel | 取消 | Cancel |
| save | 保存 | Save |
| copied | 已复制 | Copied |
| settings | 设置 | Settings |
| app_lock | 应用锁 | App Lock |
| biometric | 生物识别 | Biometric |
| theme | 主题 | Theme |
| light | 浅色 | Light |
| dark | 深色 | Dark |
| system | 跟随系统 | System |
| about | 关于 | About |
| version | 版本 | Version |
| import_account | 导入账户 | Import Account |
| search | 搜索 | Search |
| no_accounts | 暂无账户 | No accounts |
| delete_confirm | 确定删除此账户？ | Delete this account? |
| invalid_qrcode | 无效二维码 | Invalid QR Code |
| invalid_secret | 无效密钥 | Invalid Secret |

---

## 10. 待确认问题

> 以下问题需要在开发过程中根据实际情况调整：

1. **多语言**: 支持中文和英文 ✓
2. **测试策略**: 是否需要编写单元测试？

---

*文档版本: 1.0*
*创建日期: 2024-01-01*
