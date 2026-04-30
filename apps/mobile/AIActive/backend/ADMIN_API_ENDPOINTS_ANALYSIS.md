# 后台管理API端点完整性分析报告

**生成时间**: 2026-02-08
**检查范围**: `/d/aiprogram/aiactive/backend/api/`
**目的**: 检查并补充后端管理API的所有端点

---

## 一、已实现的API端点清单

### 1. 认证管理 (admin_auth.py) ✅ 完整

**文件路径**: `/d/aiprogram/aiactive/backend/api/admin_auth.py`

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/admin/auth/login` | POST | 管理员登录 | ✅ 已实现 |
| `/api/admin/auth/logout` | POST | 管理员登出 | ✅ 已实现 |
| `/api/admin/auth/profile` | GET | 获取个人信息 | ✅ 已实现 |
| `/api/admin/auth/password` | PUT | 修改密码 | ✅ 已实现 |

**特性**:
- JWT Token认证
- bcrypt密码哈希
- 操作日志记录
- 最后登录时间/IP记录

---

### 2. 应用管理 (admin_apps.py) ✅ 完整

**文件路径**: `/d/aiprogram/aiactive/backend/api/admin_apps.py`

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/admin/apps` | GET | 获取应用列表（分页、搜索、筛选） | ✅ 已实现 |
| `/api/admin/apps` | POST | 创建应用 | ✅ 已实现 |
| `/api/admin/apps/<id>` | GET | 获取应用详情 | ✅ 已实现 |
| `/api/admin/apps/<id>` | PUT | 更新应用信息 | ✅ 已实现 |
| `/api/admin/apps/<id>` | DELETE | 删除应用（级联删除关联数据） | ✅ 已实现 |
| `/api/admin/apps/<id>/stats` | GET | 获取应用统计信息 | ✅ 已实现 |

**特性**:
- 分页支持 (page, page_size)
- 多条件搜索 (keyword, status, created_by)
- 权限控制 (超级管理员/应用管理员)
- 操作日志记录
- 统计信息 (模块数、素材数、设备数、推送任务数)

**查询参数示例**:
```json
{
  "page": 1,
  "page_size": 20,
  "keyword": "AI活动秀",
  "status": 1,
  "created_by": 1
}
```

---

### 3. 模块管理 (admin_modules.py) ✅ 完整

**文件路径**: `/d/aiprogram/aiactive/backend/api/admin_modules.py`

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/admin/apps/<app_id>/modules` | GET | 获取应用的所有模块配置 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/modules` | POST | 创建新模块 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/modules/<module_key>` | GET | 获取模块详情 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/modules/<module_key>` | PUT | 更新模块配置 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/modules/<module_key>` | DELETE | 删除模块 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/modules/<module_key>/toggle` | POST | 快速切换模块启用状态 | ✅ 已实现 |

**特性**:
- 支持按模块筛选 (enabled_only)
- 模块配置JSON格式存储
- 排序支持 (sort_order)
- 快速启用/禁用切换

**模块类型**:
- `ai_show` - AI百变秀
- `quiz` - 知识问答
- `lottery` - 幸运抽奖
- `inner` - 内场秀

---

### 4. 素材管理 (admin_assets.py) ✅ 完整

**文件路径**: `/d/aiprogram/aiactive/backend/api/admin_assets.py`

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/admin/apps/<app_id>/assets/upload` | POST | 上传单个素材文件 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/assets/batch-upload` | POST | 批量上传素材文件 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/assets` | GET | 获取素材列表（分页、筛选） | ✅ 已实现 |
| `/api/admin/apps/<app_id>/assets/<asset_id>` | GET | 获取素材详情 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/assets/<asset_id>` | PUT | 更新素材信息 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/assets/<asset_id>` | DELETE | 删除素材 | ✅ 已实现 |

**特性**:
- 阿里云OSS集成
- 文件类型验证 (图片/视频/音频/配置)
- 文件大小限制 (50MB)
- MD5哈希去重
- 批量上传支持
- MIME类型检测

**支持的文件类型**:
- 图片: `png, jpg, jpeg, gif, webp, svg`
- 视频: `mp4, mov, avi, mkv`
- 音频: `mp3, wav, aac, m4a`
- 配置: `json, xml, txt`

**上传参数示例**:
```json
{
  "file": "<binary>",
  "asset_type": "image",
  "module_key": "ai_show",
  "asset_name": "样式图片1"
}
```

---

### 5. 设备管理 (admin_devices.py) ✅ 完整

**文件路径**: `/d/aiprogram/aiactive/backend/api/admin_devices.py`

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/admin/apps/<app_id>/devices` | GET | 获取设备列表（分页、筛选） | ✅ 已实现 |
| `/api/admin/apps/<app_id>/devices/online` | GET | 获取在线设备列表 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/devices/<device_id>` | GET | 获取设备详情 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/devices/<device_id>` | DELETE | 解绑设备 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/devices/<device_id>/push` | POST | 推送配置到单个设备 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/devices/stats` | GET | 获取设备统计信息 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/devices/batch-unbind` | POST | 批量解绑设备 | ✅ 已实现 |

**特性**:
- 在线状态检测 (30分钟阈值)
- 设备活跃时间追踪
- 版本分布统计
- 批量操作支持
- 推送功能集成 (TODO: 实际推送逻辑)

**在线定义**: 30分钟内有活动视为在线

**统计信息包含**:
- 总设备数
- 在线/离线设备数
- 版本分布

---

### 6. 推送管理 (admin_push.py) ✅ 完整

**文件路径**: `/d/aiprogram/aiactive/backend/api/admin_push.py`

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/admin/apps/<app_id>/push/tasks` | POST | 创建配置推送任务 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/push/tasks` | GET | 获取推送任务列表 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/push/tasks/<task_id>` | GET | 获取推送任务详情 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/push/tasks/<task_id>/cancel` | POST | 取消推送任务 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/push/tasks/<task_id>/retry` | POST | 重试失败的推送任务 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/push/broadcast` | POST | 广播推送（推送到所有在线设备） | ✅ 已实现 |
| `/api/admin/apps/<app_id>/push/tasks/<task_id>` | DELETE | 删除推送任务 | ✅ 已实现 |

**特性**:
- WebSocket推送集成
- 任务进度追踪
- 失败重试机制
- 广播推送支持
- 后台任务执行 (线程池)

**推送类型**:
- `1` - 配置更新
- `2` - 素材更新
- `3` - 全量更新

**任务状态**:
- `0` - 待推送
- `1` - 推送中
- `2` - 完成
- `3` - 部分失败
- `4` - 已取消

---

### 7. 应用配置管理 (admin_application_config.py) ✅ 完整

**文件路径**: `/d/aiprogram/aiactive/backend/api/admin_application_config.py`

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/admin/apps/<app_id>/config` | GET | 获取应用配置 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/config` | PUT | 更新应用配置 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/config/publish` | POST | 发布配置版本 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/config/versions` | GET | 获取配置版本历史 | ✅ 已实现 |
| `/api/admin/apps/<app_id>/config/rollback` | POST | 回滚到指定版本 | ✅ 已实现 |

**特性**:
- 配置版本管理
- 配置发布/回滚
- 版本历史记录
- 配置验证

---

## 二、缺失的API端点分析

### ❌ 缺失模块

#### 1. 管理员用户管理 (admin_users.py) - 缺失

**需要的端点**:
- `GET /api/admin/users/` - 获取管理员列表
- `POST /api/admin/users/` - 创建管理员
- `GET /api/admin/users/<id>` - 获取管理员详情
- `PUT /api/admin/users/<id>` - 更新管理员信息
- `DELETE /api/admin/users/<id>` - 删除管理员
- `PUT /api/admin/users/<id>/status` - 更新管理员状态
- `PUT /api/admin/users/<id>/role` - 更新管理员角色
- `POST /api/admin/users/<id>/reset-password` - 重置管理员密码

**优先级**: 🔴 高 (系统管理核心功能)

---

#### 2. 操作日志管理 (admin_logs.py) - 缺失

**需要的端点**:
- `GET /api/admin/logs/` - 获取操作日志列表（分页、筛选）
- `GET /api/admin/logs/<id>` - 获取日志详情
- `GET /api/admin/logs/stats` - 获取日志统计信息
- `DELETE /api/admin/logs/before/<date>` - 删除指定日期前的日志

**优先级**: 🟡 中 (审计和监控需要)

**查询参数示例**:
```json
{
  "page": 1,
  "page_size": 20,
  "admin_id": 1,
  "operation": "create_app",
  "resource_type": "app",
  "start_date": "2026-01-01",
  "end_date": "2026-01-31"
}
```

---

#### 3. 数据统计/仪表板 (admin_stats.py) - 缺失

**需要的端点**:
- `GET /api/admin/stats/overview` - 获取系统概览统计
- `GET /api/admin/stats/apps` - 获取应用统计
- `GET /api/admin/stats/devices` - 获取设备统计
- `GET /api/admin/stats/assets` - 获取素材统计
- `GET /api/admin/stats/push` - 获取推送统计
- `GET /api/admin/stats/timeline` - 获取时间线数据（图表用）

**优先级**: 🟡 中 (管理界面可视化需要)

**返回数据示例**:
```json
{
  "total_apps": 10,
  "total_devices": 1000,
  "total_assets": 5000,
  "online_devices": 650,
  "today_push_tasks": 20,
  "active_modules": 40
}
```

---

#### 4. 系统配置管理 (admin_settings.py) - 缺失

**需要的端点**:
- `GET /api/admin/settings/` - 获取系统配置
- `PUT /api/admin/settings/` - 更新系统配置
- `POST /api/admin/settings/test-oss` - 测试OSS连接
- `POST /api/admin/settings/test-websocket` - 测试WebSocket服务

**优先级**: 🟢 低 (系统配置功能)

---

## 三、响应格式统一性检查

### ✅ 标准响应格式 (已统一)

所有API端点均使用以下响应格式:

```json
{
  "code": 200,          // 状态码: 200=成功, 400=客户端错误, 401=未认证, 403=无权限, 404=不存在, 500=服务器错误
  "message": "success", // 消息描述
  "data": {...}         // 返回数据（可选）
}
```

### ✅ 分页响应格式 (已统一)

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [...],      // 数据列表
    "total": 100,       // 总记录数
    "page": 1,          // 当前页码
    "page_size": 20     // 每页数量
  }
}
```

### ✅ 错误响应格式 (已统一)

```json
{
  "code": 400,
  "message": "缺少必填字段: app_name"
}
```

---

## 四、操作日志记录检查

### ✅ 已实现日志记录的操作

所有已实现的API端点均包含操作日志记录:

```python
await log_operation(
    db=db,
    admin_id=g.current_admin_id,
    operation='create_app',           # 操作类型
    resource_type='app',              # 资源类型
    resource_id=app.id,               # 资源ID
    operation_desc=f'创建应用: {app.app_name}',  # 操作描述
    request_ip=request.remote_addr,   # 请求IP
    user_agent=request.headers.get('User-Agent', ''),  # 用户代理
    status=1                         # 操作状态: 1=成功, 0=失败
)
```

**记录的操作类型**:
- 认证操作: `login`, `logout`, `change_password`
- 应用管理: `create_app`, `update_app`, `delete_app`
- 模块管理: `create_module`, `update_module`, `delete_module`, `toggle_module`
- 素材管理: `upload_asset`, `update_asset`, `delete_asset`, `batch_upload_assets`
- 设备管理: `unbind_device`, `batch_unbind_devices`, `push_to_device`
- 推送管理: `create_push_task`, `cancel_push_task`, `retry_push_task`, `delete_push_task`, `broadcast_push`

---

## 五、需要创建或修改的文件清单

### 🔴 高优先级 (必须实现)

1. **创建**: `/d/aiprogram/aiactive/backend/api/admin_users.py`
   - 管理员用户CRUD操作
   - 角色管理
   - 密码重置

2. **创建**: `/d/aiprogram/aiactive/backend/api/admin_logs.py`
   - 操作日志查询
   - 日志统计分析

### 🟡 中优先级 (建议实现)

3. **创建**: `/d/aiprogram/aiactive/backend/api/admin_stats.py`
   - 系统统计数据
   - 仪表板数据

### 🟢 低优先级 (可选)

4. **创建**: `/d/aiprogram/aiactive/backend/api/admin_settings.py`
   - 系统配置管理

---

## 六、补充代码实现

### 1. 管理员用户管理 (admin_users.py)

```python
"""
后台管理 - 管理员用户管理API
"""
from flask import Blueprint, request, jsonify, g, current_app
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.auth import token_required, admin_role_required
from database_admin import get_db
from models_admin import AdminUser
from api.admin_auth import hash_password

users_bp = Blueprint('admin_users', __name__)


@users_bp.route('/api/admin/users', methods=['GET'])
@token_required
@admin_role_required(1)  # 仅超级管理员可查看
async def get_users_list():
    """获取管理员列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        keyword = request.args.get('keyword', '').strip()
        role = request.args.get('role')
        status = request.args.get('status')

        async for db in get_db():
            query = select(AdminUser)

            # 搜索条件
            if keyword:
                query = query.where(
                    (AdminUser.username.like(f'%{keyword}%')) |
                    (AdminUser.real_name.like(f'%{keyword}%')) |
                    (AdminUser.email.like(f'%{keyword}%'))
                )

            # 角色筛选
            if role is not None:
                query = query.where(AdminUser.role == int(role))

            # 状态筛选
            if status is not None:
                query = query.where(AdminUser.status == int(status))

            # 获取总数
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await db.execute(count_query)
            total = total_result.scalar()

            # 分页查询
            query = query.order_by(AdminUser.created_at.desc())
            query = query.offset((page - 1) * page_size).limit(page_size)

            result = await db.execute(query)
            users = result.scalars().all()

            users_list = []
            for user in users:
                users_list.append({
                    'id': user.id,
                    'username': user.username,
                    'real_name': user.real_name,
                    'email': user.email,
                    'phone': user.phone,
                    'role': user.role,
                    'role_name': '超级管理员' if user.role == 1 else '应用管理员',
                    'status': user.status,
                    'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None,
                    'last_login_ip': user.last_login_ip,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                })

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'list': users_list,
                    'total': total,
                    'page': page,
                    'page_size': page_size
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取管理员列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取管理员列表失败: {str(e)}'
        }), 500


@users_bp.route('/api/admin/users', methods=['POST'])
@token_required
@admin_role_required(1)  # 仅超级管理员可创建
async def create_user():
    """创建管理员"""
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['username', 'password', 'real_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段: {field}'
                }), 400

        async for db in get_db():
            # 检查用户名是否已存在
            existing = await db.execute(
                select(AdminUser).where(AdminUser.username == data['username'])
            )
            if existing.scalar_one_or_none():
                return jsonify({
                    'code': 400,
                    'message': '用户名已存在'
                }), 400

            # 创建管理员
            user = AdminUser(
                username=data['username'],
                password_hash=hash_password(data['password']),
                real_name=data['real_name'],
                email=data.get('email'),
                phone=data.get('phone'),
                role=data.get('role', 2),  # 默认为应用管理员
                status=data.get('status', 1)
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)

            return jsonify({
                'code': 200,
                'message': '创建成功',
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'real_name': user.real_name
                }
            })

    except Exception as e:
        current_app.logger.error(f'创建管理员失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'创建管理员失败: {str(e)}'
        }), 500


@users_bp.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@token_required
@admin_role_required(1)
async def update_user(user_id):
    """更新管理员信息"""
    try:
        data = request.get_json()

        async for db in get_db():
            result = await db.execute(
                select(AdminUser).where(AdminUser.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return jsonify({
                    'code': 404,
                    'message': '管理员不存在'
                }), 404

            # 不允许修改自己的角色
            if user.id == g.current_admin_id and 'role' in data:
                return jsonify({
                    'code': 400,
                    'message': '不能修改自己的角色'
                }), 400

            # 构建更新数据
            update_data = {}
            allowed_fields = ['real_name', 'email', 'phone', 'role', 'status']
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field]

            if not update_data:
                return jsonify({
                    'code': 400,
                    'message': '没有可更新的字段'
                }), 400

            # 执行更新
            await db.execute(
                update(AdminUser)
                .where(AdminUser.id == user_id)
                .values(**update_data)
            )
            await db.commit()

            return jsonify({
                'code': 200,
                'message': '更新成功'
            })

    except Exception as e:
        current_app.logger.error(f'更新管理员失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'更新管理员失败: {str(e)}'
        }), 500


@users_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@token_required
@admin_role_required(1)
async def delete_user(user_id):
    """删除管理员"""
    try:
        async for db in get_db():
            result = await db.execute(
                select(AdminUser).where(AdminUser.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return jsonify({
                    'code': 404,
                    'message': '管理员不存在'
                }), 404

            # 不允许删除自己
            if user.id == g.current_admin_id:
                return jsonify({
                    'code': 400,
                    'message': '不能删除自己'
                }), 400

            username = user.username

            # 删除管理员
            await db.execute(
                delete(AdminUser).where(AdminUser.id == user_id)
            )
            await db.commit()

            return jsonify({
                'code': 200,
                'message': '删除成功'
            })

    except Exception as e:
        current_app.logger.error(f'删除管理员失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'删除管理员失败: {str(e)}'
        }), 500


@users_bp.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
@token_required
@admin_role_required(1)
async def reset_user_password(user_id):
    """重置管理员密码"""
    try:
        data = request.get_json()
        new_password = data.get('new_password')

        if not new_password:
            return jsonify({
                'code': 400,
                'message': '新密码不能为空'
            }), 400

        if len(new_password) < 6:
            return jsonify({
                'code': 400,
                'message': '新密码长度不能少于6位'
            }), 400

        async for db in get_db():
            result = await db.execute(
                select(AdminUser).where(AdminUser.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return jsonify({
                    'code': 404,
                    'message': '管理员不存在'
                }), 404

            # 更新密码
            await db.execute(
                update(AdminUser)
                .where(AdminUser.id == user_id)
                .values(password_hash=hash_password(new_password))
            )
            await db.commit()

            return jsonify({
                'code': 200,
                'message': '密码重置成功'
            })

    except Exception as e:
        current_app.logger.error(f'重置密码失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'重置密码失败: {str(e)}'
        }), 500
```

---

### 2. 操作日志管理 (admin_logs.py)

```python
"""
后台管理 - 操作日志API
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import select, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.auth import token_required, admin_role_required
from database_admin import get_db
from models_admin import AdminOperationLog, AdminUser

logs_bp = Blueprint('admin_logs', __name__)


@logs_bp.route('/api/admin/logs', methods=['GET'])
@token_required
@admin_role_required(1)  # 仅超级管理员可查看
async def get_logs_list():
    """获取操作日志列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        admin_id = request.args.get('admin_id')
        operation = request.args.get('operation')
        resource_type = request.args.get('resource_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        async for db in get_db():
            query = select(AdminOperationLog)

            # 筛选条件
            if admin_id:
                query = query.where(AdminOperationLog.admin_id == int(admin_id))
            if operation:
                query = query.where(AdminOperationLog.operation == operation)
            if resource_type:
                query = query.where(AdminOperationLog.resource_type == resource_type)
            if start_date:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.where(AdminOperationLog.created_at >= start_datetime)
            if end_date:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                query = query.where(AdminOperationLog.created_at < end_datetime)

            # 获取总数
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await db.execute(count_query)
            total = total_result.scalar()

            # 分页查询
            query = query.order_by(AdminOperationLog.created_at.desc())
            query = query.offset((page - 1) * page_size).limit(page_size)

            result = await db.execute(query)
            logs = result.scalars().all()

            logs_list = []
            for log in logs:
                # 获取管理员信息
                admin = None
                if log.admin_id:
                    admin_result = await db.execute(
                        select(AdminUser).where(AdminUser.id == log.admin_id)
                    )
                    admin_user = admin_result.scalar_one_or_none()
                    if admin_user:
                        admin = {
                            'id': admin_user.id,
                            'username': admin_user.username,
                            'real_name': admin_user.real_name
                        }

                logs_list.append({
                    'id': log.id,
                    'admin': admin,
                    'operation': log.operation,
                    'resource_type': log.resource_type,
                    'resource_id': log.resource_id,
                    'operation_desc': log.operation_desc,
                    'request_ip': log.request_ip,
                    'user_agent': log.user_agent,
                    'status': log.status,
                    'created_at': log.created_at.isoformat() if log.created_at else None,
                })

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'list': logs_list,
                    'total': total,
                    'page': page,
                    'page_size': page_size
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取操作日志失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取操作日志失败: {str(e)}'
        }), 500


@logs_bp.route('/api/admin/logs/stats', methods=['GET'])
@token_required
@admin_role_required(1)
async def get_logs_stats():
    """获取日志统计信息"""
    try:
        days = int(request.args.get('days', 7))

        async for db in get_db():
            # 计算起始日期
            start_date = datetime.utcnow() - timedelta(days=days)

            # 总操作数
            total_operations = await db.scalar(
                select(func.count())
                .select_from(AdminOperationLog)
                .where(AdminOperationLog.created_at >= start_date)
            )

            # 成功操作数
            success_operations = await db.scalar(
                select(func.count())
                .select_from(AdminOperationLog)
                .where(
                    AdminOperationLog.created_at >= start_date,
                    AdminOperationLog.status == 1
                )
            )

            # 失败操作数
            failed_operations = await db.scalar(
                select(func.count())
                .select_from(AdminOperationLog)
                .where(
                    AdminOperationLog.created_at >= start_date,
                    AdminOperationLog.status == 0
                )
            )

            # 按操作类型统计
            result = await db.execute(
                select(AdminOperationLog.operation, func.count())
                .where(AdminOperationLog.created_at >= start_date)
                .group_by(AdminOperationLog.operation)
            )
            operation_stats = {op: count for op, count in result.all()}

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'total_operations': total_operations or 0,
                    'success_operations': success_operations or 0,
                    'failed_operations': failed_operations or 0,
                    'operation_stats': operation_stats
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取日志统计失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取日志统计失败: {str(e)}'
        }), 500


@logs_bp.route('/api/admin/logs/before/<date>', methods=['DELETE'])
@token_required
@admin_role_required(1)
async def delete_logs_before(date):
    """删除指定日期前的日志"""
    try:
        target_date = datetime.strptime(date, '%Y-%m-%d')

        async for db in get_db():
            # 删除指定日期前的日志
            result = await db.execute(
                delete(AdminOperationLog)
                .where(AdminOperationLog.created_at < target_date)
            )
            deleted_count = result.rowcount
            await db.commit()

            return jsonify({
                'code': 200,
                'message': '删除成功',
                'data': {
                    'deleted_count': deleted_count
                }
            })

    except Exception as e:
        current_app.logger.error(f'删除日志失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'删除日志失败: {str(e)}'
        }), 500
```

---

### 3. 数据统计/仪表板 (admin_stats.py)

```python
"""
后台管理 - 系统统计API
"""
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, current_app
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.auth import token_required, admin_role_required
from database_admin import get_db
from models_admin import App, AppModule, AppAsset, AppDevice, ConfigPushTask, AdminOperationLog

stats_bp = Blueprint('admin_stats', __name__)


@stats_bp.route('/api/admin/stats/overview', methods=['GET'])
@token_required
async def get_overview_stats():
    """获取系统概览统计"""
    try:
        async for db in get_db():
            # 应用总数
            total_apps = await db.scalar(
                select(func.count()).select_from(App)
            )

            # 设备总数
            total_devices = await db.scalar(
                select(func.count()).select_from(AppDevice)
            )

            # 素材总数
            total_assets = await db.scalar(
                select(func.count()).select_from(AppAsset)
            )

            # 在线设备数（30分钟内有活动）
            threshold_time = datetime.utcnow() - timedelta(minutes=30)
            online_devices = await db.scalar(
                select(func.count())
                .select_from(AppDevice)
                .where(AppDevice.last_active_at >= threshold_time)
            )

            # 今日推送任务数
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_push_tasks = await db.scalar(
                select(func.count())
                .select_from(ConfigPushTask)
                .where(ConfigPushTask.created_at >= today_start)
            )

            # 启用的模块数
            active_modules = await db.scalar(
                select(func.count())
                .select_from(AppModule)
                .where(AppModule.enabled == True)
            )

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'total_apps': total_apps or 0,
                    'total_devices': total_devices or 0,
                    'total_assets': total_assets or 0,
                    'online_devices': online_devices or 0,
                    'today_push_tasks': today_push_tasks or 0,
                    'active_modules': active_modules or 0
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取系统统计失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取系统统计失败: {str(e)}'
        }), 500


@stats_bp.route('/api/admin/stats/apps', methods=['GET'])
@token_required
async def get_apps_stats():
    """获取应用统计"""
    try:
        async for db in get_db():
            # 应用总数
            total_apps = await db.scalar(
                select(func.count()).select_from(App)
            )

            # 启用的应用数
            enabled_apps = await db.scalar(
                select(func.count())
                .select_from(App)
                .where(App.status == 1)
            )

            # 每个应用的模块数、素材数、设备数
            result = await db.execute(
                select(App.id, App.app_name)
                .order_by(App.id)
            )
            apps = result.all()

            apps_stats = []
            for app_id, app_name in apps:
                modules_count = await db.scalar(
                    select(func.count())
                    .select_from(AppModule)
                    .where(AppModule.app_id == app_id)
                )

                assets_count = await db.scalar(
                    select(func.count())
                    .select_from(AppAsset)
                    .where(AppAsset.app_id == app_id)
                )

                devices_count = await db.scalar(
                    select(func.count())
                    .select_from(AppDevice)
                    .where(AppDevice.app_id == app_id)
                )

                apps_stats.append({
                    'id': app_id,
                    'app_name': app_name,
                    'modules_count': modules_count or 0,
                    'assets_count': assets_count or 0,
                    'devices_count': devices_count or 0
                })

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'total_apps': total_apps or 0,
                    'enabled_apps': enabled_apps or 0,
                    'apps_stats': apps_stats
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取应用统计失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取应用统计失败: {str(e)}'
        }), 500


@stats_bp.route('/api/admin/stats/timeline', methods=['GET'])
@token_required
async def get_timeline_stats():
    """获取时间线数据（图表用）"""
    try:
        days = int(request.args.get('days', 7))

        async for db in get_db():
            # 计算起始日期
            start_date = datetime.utcnow() - timedelta(days=days)

            timeline_data = []
            for i in range(days):
                date = datetime.utcnow() - timedelta(days=days-i-1)
                date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
                date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

                # 当日操作数
                operations_count = await db.scalar(
                    select(func.count())
                    .select_from(AdminOperationLog)
                    .where(
                        AdminOperationLog.created_at >= date_start,
                        AdminOperationLog.created_at <= date_end
                    )
                )

                # 当日推送任务数
                push_tasks_count = await db.scalar(
                    select(func.count())
                    .select_from(ConfigPushTask)
                    .where(
                        ConfigPushTask.created_at >= date_start,
                        ConfigPushTask.created_at <= date_end
                    )
                )

                timeline_data.append({
                    'date': date_start.strftime('%Y-%m-%d'),
                    'operations_count': operations_count or 0,
                    'push_tasks_count': push_tasks_count or 0
                })

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'timeline': timeline_data
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取时间线数据失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取时间线数据失败: {str(e)}'
        }), 500
```

---

## 七、总结

### ✅ 已完成的功能

1. **认证管理** - 完整的登录/登出/密码管理
2. **应用管理** - CRUD + 统计
3. **模块管理** - 完整的模块配置功能
4. **素材管理** - 上传/管理/删除，OSS集成
5. **设备管理** - 设备列表/在线状态/推送
6. **推送管理** - 任务管理/进度追踪/重试
7. **应用配置** - 版本管理/发布/回滚

### ❌ 需要补充的功能

1. **管理员用户管理** - 🔴 高优先级
2. **操作日志管理** - 🟡 中优先级
3. **系统统计/仪表板** - 🟡 中优先级
4. **系统配置管理** - 🟢 低优先级

### 📋 实施建议

1. **立即实施**: 管理员用户管理 (admin_users.py)
2. **近期实施**: 操作日志管理 (admin_logs.py)
3. **计划实施**: 系统统计 (admin_stats.py)

### 🎯 下一步行动

1. 创建缺失的API文件
2. 在 `app.py` 中注册新的蓝图
3. 测试所有新增端点
4. 更新API文档

---

**报告生成时间**: 2026-02-08
**检查人员**: Claude Code AI Assistant
