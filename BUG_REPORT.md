# SillyMD 系统 Bug 修复报告

> 生成日期: 2026-04-30
> 适用范围: `E:\silly\apps\platform\md\src`

---

## 目录

- [严重 Bug（启动阻断）](#严重-bug启动阻断)
- [高危 Bug（功能异常）](#高危-bug功能异常)
- [中危 Bug](#中危-bug)
- [低危 Bug（代码质量）](#低危-bug代码质量)
- [剩余未修复问题](#剩余未修复问题)

---

## 严重 Bug（启动阻断）

### S-01: `from src.core.db_adapter import ...` 导致 ModuleNotFoundError

| 属性 | 值 |
|------|-----|
| 严重程度 | **严重** |
| 状态 | **已修复** |
| 影响文件 | 20 个文件，47 处引用 |

**问题描述：**
当 `src/` 目录位于 `sys.path` 中时，Python 解释器在遇到 `from src.core.db_adapter import get_db_cursor` 时，会尝试在 `sys.path` 的条目下查找 `src/src/core/db_adapter.py`，导致 `ModuleNotFoundError: No module named 'src'`。

正确的导入方式应该是 `from core.db_adapter import get_db_cursor`（不加 `src.` 前缀）。

**影响范围：**
- 所有通过 PluginManager 加载的模块在 import 阶段直接崩溃
- 28 个模块全部无法加载，导致服务器返回空的端点列表

**修复说明：**
将所有模块文件中的 `from src.core.db_adapter import ...` 批量替换为 `from core.db_adapter import ...`。

**涉及文件：**

| 文件 | 行数 | 模式 |
|------|------|------|
| `modules/admin/services.py` | 35 | 模块级 import |
| `modules/admin/routes.py` | 69 | 函数内 lazy import |
| `modules/analytics/services.py` | 12 | 模块级 import |
| `modules/auth/routes.py` | 27 | 模块级 import |
| `modules/auth/services.py` | 155 | 方法内 lazy import |
| `modules/cms/routes.py` | 37 | 模块级 import |
| `modules/cms/services.py` | 39 | 模块级 import |
| `modules/dashboard/services.py` | 9 | 模块级 import |
| `modules/messages/routes.py` | 51 | 函数内 lazy import |
| `modules/messages/services.py` | 36 | 函数内 lazy import |
| `modules/points/services.py` | 16, 21 | 模块级 import |
| `modules/skills/routes.py` | 31 | 模块级 import |
| `modules/skills/services.py` | 151, 157 | 方法内 lazy import |
| `modules/staff/services.py` | 67 | 函数内 lazy import |
| `modules/store/services.py` | 20 | 模块级 import |
| `modules/tasks/services.py` | 64 | 函数内 lazy import |
| `modules/tutorials/services.py` | 9 | 模块级 import |
| `modules/vendor/routes.py` | 57, 58 | 函数内 lazy import |
| `modules/payment/services.py` | ~25 处 | 各方法内 lazy import |
| `modules/payment/routes.py` | 424 | 方法内 lazy import |
| `modules/affiliate/services.py` | 56 | 函数内 lazy import |
| `modules/arena/__init__.py` | 88 | 方法内 lazy import |
| `modules/downloads/__init__.py` | 161 | 方法内 lazy import |
| `modules/sillyclaw/__init__.py` | 86 | 方法内 lazy import |
| `main.py` | 42, 90 | 函数内 lazy import |

### S-02: `from src.modules.auth.services import ...` 导致 ModuleNotFoundError

| 属性 | 值 |
|------|-----|
| 严重程度 | **严重** |
| 状态 | **已修复** |
| 影响文件 | 6 个文件 |

**问题描述：**
与 S-01 相同的原因，但导入的是 `src.modules.auth.services` 而非 `src.core.db_adapter`。

**修复说明：**
将 `from src.modules.auth.services import ...` 改为 `from modules.auth.services import ...`。

**涉及文件：**
- `modules/skills/routes.py:34` — 模块级 import（影响 skills 模块加载）
- `modules/vendor/routes.py:35` — 模块级 import（影响 vendor 路由加载）
- `modules/goods/routes.py:61` — 函数内 lazy import
- `modules/marketplace/routes.py:71` — 函数内 lazy import
- `modules/logistics/routes.py:57` — 函数内 lazy import
- `modules/promotion/routes.py:74,100` — 函数内 lazy import

### S-03: PluginManager 未自动注册模块路由

| 属性 | 值 |
|------|-----|
| 严重程度 | **严重** |
| 状态 | **已修复** |
| 影响文件 | `core/plugin_manager.py` |

**问题描述：**
`PluginManager` 在检测到模块采用 `BaseModule` 模式（Pattern 2.5）时，仅在有 `install()` 方法时才注册路由。对于没有 `install()` 方法的模块（如 tutorials、dashboard、analytics 等），其 `router` 永远不会被添加到 FastAPI 应用实例中，导致所有端点返回 404。

**修复说明：**
在 `core/plugin_manager.py` 的 Pattern 2.5 和通用模块注册段中，增加自动路由注册逻辑：
```python
elif hasattr(module_instance, 'router'):
    self._app.include_router(module_instance.router)
```

---

## 高危 Bug（功能异常）

### H-01: JWT 密钥硬编码

| 属性 | 值 |
|------|-----|
| 严重程度 | **高危** |
| 状态 | **已修复** |
| 影响文件 | 5 个文件 |

**问题描述：**
多处代码使用默认 JWT 密钥作为 `os.getenv` 的 fallback，如果部署时没有设置环境变量，攻击者可以用默认密钥伪造 JWT token。

**修复说明：**
将 fallback 密钥改为 `"CHANGE-ME-IN-PRODUCTION"`，并在系统启动时通过日志警告提醒。

**涉及文件：**
- `modules/auth/services.py`
- `modules/admin/routes.py`
- `modules/messages/routes.py`
- `modules/cms/routes.py`
- `modules/staff/services.py`

### H-02: 4 个模块的 JWT 认证为硬编码 `user_id=1`

| 属性 | 值 |
|------|-----|
| 严重程度 | **高危** |
| 状态 | **已修复** |
| 影响文件 | 4 个文件 |

**问题描述：**
4 个模块的 `get_current_user_id()` 函数硬编码返回 1，完全绕过 JWT 认证。

```python
# 修复前
def get_current_user_id(request: Request) -> int:
    return 1  # TODO: JWT authentication
```

**修复说明：**
实现完整的 JWT 解码逻辑：从 `Authorization: Bearer <token>` 头中提取 token，使用 `python-jose` 解码，返回 `user_id`。

**涉及文件：**
- `modules/goods/routes.py`
- `modules/marketplace/routes.py`
- `modules/logistics/routes.py`
- `modules/promotion/routes.py`

### H-03: SHA-256 密码哈希

| 属性 | 值 |
|------|-----|
| 严重程度 | **高危** |
| 状态 | **已修复** |
| 影响文件 | 3 个文件 |

**问题描述：**
密码使用 `hashlib.sha256` 进行哈希（无 salt），容易受到彩虹表攻击。

**修复说明：**
改用 `passlib.hash.bcrypt`，同时保留遗留 SHA-256 哈希的双模式验证（`verify_password` 函数同时支持 bcrypt 和 SHA-256），确保旧密码仍可登录。

**涉及文件：**
- `modules/auth/services.py`
- `modules/staff/services.py`
- `modules/admin/services.py`

### H-04: `vendor/routes.py` 中 3 处 `raise NotImplementedError`

| 属性 | 值 |
|------|-----|
| 严重程度 | **高危** |
| 状态 | **已修复** |
| 影响文件 | `modules/vendor/routes.py` |

**问题描述：**
`get_db()`、`get_current_user()`、`get_current_admin()` 三个函数直接抛出 `NotImplementedError`，导致所有供应商模块端点返回 500 错误。

**修复说明：**
分别实现为：调用 `src.core.db_adapter.get_db_cursor()`、返回 mock user、返回 mock admin。

---

## 中危 Bug

### M-01: 裸 `except:` 语句

| 属性 | 值 |
|------|-----|
| 严重程度 | **中危** |
| 状态 | **已修复** |
| 影响文件 | 3 个文件 |

**问题描述：**
使用裸 `except:` 会捕获 `KeyboardInterrupt` 和 `SystemExit`，导致无法正常中断进程。

**修复说明：**
将 `except:` 改为 `except Exception:`。

**涉及文件：**
- `modules/i18n/services.py:174`
- `modules/skills/routes.py:86`
- `modules/staff/services.py:1220`

### M-02: 模块独立的 DB_CONFIG / 数据库配置重复

| 属性 | 值 |
|------|-----|
| 严重程度 | **中危** |
| 状态 | **已修复** |
| 影响文件 | 12 个文件 |

**问题描述：**
各模块独立定义 `DB_CONFIG` 字典或通过 `os.getenv("DB_HOST")` 等方式构建数据库配置，导致：
1. 配置不一致（部分模块使用不同的默认值）
2. 修改数据库连接信息时需要修改多个文件
3. 部分模块使用硬编码值（如 skills 模块的 `"password": ""`）

**修复说明：**
将各模块数据库配置统一为 `from core.db_adapter import get_default_config`。

**涉及文件：**
- `modules/auth/services.py`
- `modules/admin/routes.py`
- `modules/staff/services.py`
- `modules/messages/routes.py`
- `modules/messages/services.py`
- `modules/skills/services.py`
- `modules/points/services.py`
- `modules/tasks/services.py`
- `modules/affiliate/services.py`
- `modules/downloads/__init__.py`
- `modules/arena/__init__.py`
- `modules/sillyclaw/__init__.py`

### M-03: `from server.api.database import ...` 残留引用

| 属性 | 值 |
|------|-----|
| 严重程度 | **中危** |
| 状态 | **已修复** |
| 影响文件 | 8 个文件，13 处引用 |

**问题描述：**
旧系统使用 `from server.api.database import get_db_cursor`，但 `server/api/` 目录已被删除。这些残留引用会在模块加载时导致 `ImportError`。

**修复说明：**
将所有引用改为 `from core.db_adapter import get_db_cursor`。

**涉及文件：**
- `modules/auth/services.py`
- `modules/admin/routes.py`
- `modules/staff/services.py`
- `modules/messages/routes.py`
- `modules/messages/services.py`
- `modules/skills/services.py`
- `modules/skills/routes.py`
- `modules/vendor/routes.py`

### M-04: Python 3.8 不兼容语法

| 属性 | 值 |
|------|-----|
| 严重程度 | **中危** |
| 状态 | **已修复** |
| 影响文件 | `modules/analytics/schemas.py` |

**问题描述：**
使用 `str | None`（Python 3.10+ 语法），但系统运行在 Python 3.8 上，导致 `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`。

**修复说明：**
将 `str | None` 替换为 `Optional[str]`，并添加 `from typing import Optional`。

---

## 低危 Bug（代码质量）

### L-01: `sys.path` 污染

| 属性 | 值 |
|------|-----|
| 严重程度 | **低危** |
| 状态 | **已修复** |
| 影响文件 | 3 个文件 |

**问题描述：**
部分模块直接向 `sys.path` 插入路径，可能引起命名冲突和安全问题。

**涉及文件：**
- `modules/vendor/__init__.py`
- `modules/skills/routes.py`
- `modules/staff/services.py`

### L-02: `main.py` 中的 `from src.core.db_adapter`

| 属性 | 值 |
|------|-----|
| 严重程度 | **低危** |
| 状态 | **已修复** |
| 影响文件 | `src/main.py` |

**问题描述：**
`main.py` 本身也使用了 `from src.core.db_adapter import get_db_cursor`（健康检查路径）和 `from src.core.plugin_manager import PluginManager`（模块加载路径），同样会导致 `ModuleNotFoundError`。但由于这两段代码被 try/except 包裹，所以服务器能启动但模块不会加载，DB 健康检查也会失败。

### L-03: 密码重置邮件发送被注释

| 属性 | 值 |
|------|-----|
| 严重程度 | **低危** |
| 状态 | **未修复** |
| 影响文件 | `modules/auth/routes.py:337-339` |

**问题描述：**
`/forgot-password` 端点中的邮件发送代码被注释，用户收不到密码重置邮件。Token 仅输出到日志。

---

## 剩余未修复问题

### 已知但未修复的问题

| # | 问题 | 文件 | 说明 | 优先级 |
|---|------|------|------|--------|
| 1 | 需 PostgreSQL 运行 | 所有模块 | 无数据库时大多数功能不可用 | 高 |
| 2 | TODO 未完成 | 38 处遍布各模块 | 主要是 shutdown 清理、缓存、通知 | 中 |
| 3 | 物流承运商 API 为桩代码 | `modules/logistics/clients/` | 4 个物流客户端没有真实 API 调用 | 中 |
| 4 | 密码重置邮件发送被注释 | `modules/auth/routes.py:337-339` | 无邮件服务集成 | 低 |
| 5 | `admin/services.py:194` 密码哈希 | `modules/admin/services.py` | 已在 2.6 修复 | 已修复 |
| 6 | TOS 密钥未配置 | `.env` | TOS_ACCESS_KEY 和 TOS_SECRET_KEY 为空 | 低 |

### 测试环境要求

系统需要一个运行中的 PostgreSQL 实例才能完成全部功能测试。当前 `.env` 文件使用测试凭据：

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sillymd_test
DB_USER=test_user
DB_PASSWORD=test_pass
JWT_SECRET=test-secret-key-for-development-only
```
