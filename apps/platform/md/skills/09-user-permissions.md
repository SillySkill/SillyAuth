# 第九章：用户与权限系统

> 本文档描述 SillyMD 平台的用户类型和权限体系。
>
> 本章涵盖用户与权限系统所需的所有数据库表结构设计。

## 9.0 数据库设计

### 9.0.1 OAuth账号关联表 (oauth_accounts)

```sql
CREATE TABLE oauth_accounts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    provider VARCHAR(50) NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    provider_username VARCHAR(255),
    provider_email VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    avatar_url VARCHAR(500),
    profile_url VARCHAR(500),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (provider, provider_user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_oauth_accounts_user_id ON oauth_accounts(user_id);
CREATE INDEX idx_oauth_accounts_provider ON oauth_accounts(provider);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_oauth_accounts_updated_at BEFORE UPDATE ON oauth_accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 9.0.2 API密钥表 (api_keys)

```sql
CREATE TYPE api_key_type AS ENUM ('read', 'write', 'admin');

CREATE TABLE api_keys (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    key_name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,
    key_type api_key_type NOT NULL DEFAULT 'read',
    scopes JSONB,
    rate_limit INT DEFAULT 1000,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_by_ip VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMPTZ,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_prefix ON api_keys(key_prefix);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);
```

### 9.0.3 角色表 (roles)

```sql
CREATE TABLE roles (
    id BIGSERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    role_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    level INT NOT NULL DEFAULT 0,
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_roles_role_code ON roles(role_code);
CREATE INDEX idx_roles_level ON roles(level);
CREATE INDEX idx_roles_is_active ON roles(is_active);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 初始化角色数据
INSERT INTO roles (role_name, role_code, description, level, is_system) VALUES
('超级管理员', 'super_admin', '拥有所有权限', 100, TRUE),
('管理员', 'admin', '拥有大部分管理权限', 80, TRUE),
('供应商', 'vendor', '可以创建和售卖商用Skills', 50, TRUE),
('团队管理员', 'team_admin', '可以创建和管理团队', 40, TRUE),
('团队成员', 'team_member', '团队成员', 30, TRUE),
('普通用户', 'user', '普通注册用户', 10, TRUE),
('访客', 'guest', '未登录访客', 0, TRUE);
```

### 9.0.4 权限表 (permissions)

```sql
CREATE TABLE permissions (
    id BIGSERIAL PRIMARY KEY,
    permission_name VARCHAR(100) UNIQUE NOT NULL,
    permission_code VARCHAR(100) UNIQUE NOT NULL,
    module VARCHAR(50) NOT NULL,
    description TEXT,
    resource_type VARCHAR(50),
    action VARCHAR(50),
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_permissions_permission_code ON permissions(permission_code);
CREATE INDEX idx_permissions_module ON permissions(module);
CREATE INDEX idx_permissions_resource_action ON permissions(resource_type, action);

-- 初始化权限数据
INSERT INTO permissions (permission_name, permission_code, module, resource_type, action) VALUES
-- Skills相关
('查看Skills', 'skills.read', 'skills', 'skill', 'read'),
('创建Skills', 'skills.create', 'skills', 'skill', 'create'),
('编辑Skills', 'skills.update', 'skills', 'skill', 'update'),
('删除Skills', 'skills.delete', 'skills', 'skill', 'delete'),
('发布商用Skills', 'skills.publish_commercial', 'skills', 'skill', 'publish'),
-- 用户相关
('查看用户', 'users.read', 'users', 'user', 'read'),
('管理用户', 'users.manage', 'users', 'user', 'update'),
('删除用户', 'users.delete', 'users', 'user', 'delete'),
-- 团队相关
('创建团队', 'teams.create', 'teams', 'team', 'create'),
('管理团队', 'teams.manage', 'teams', 'team', 'update'),
('解散团队', 'teams.delete', 'teams', 'team', 'delete'),
-- 订单相关
('查看订单', 'orders.read', 'orders', 'order', 'read'),
('管理订单', 'orders.manage', 'orders', 'order', 'update'),
-- 财务相关
('查看财务', 'finance.read', 'finance', 'transaction', 'read'),
('提现', 'finance.withdraw', 'finance', 'withdrawal', 'create'),
('充值', 'finance.recharge', 'finance', 'recharge', 'create'),
-- 审核相关
('审核Skills', 'review.skills', 'review', 'skill', 'review'),
('审核用户', 'review.users', 'review', 'user', 'review'),
-- 系统相关
('系统配置', 'system.config', 'system', 'config', 'update'),
('查看日志', 'system.logs', 'system', 'log', 'read');
```

### 9.0.5 角色权限关联表 (role_permissions)

```sql
CREATE TABLE role_permissions (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission_id ON role_permissions(permission_id);
```

### 9.0.6 用户角色关联表 (user_roles)

```sql
CREATE TABLE user_roles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    granted_by BIGINT,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX idx_user_roles_is_active ON user_roles(is_active);
CREATE INDEX idx_user_roles_expires_at ON user_roles(expires_at);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_user_roles_updated_at BEFORE UPDATE ON user_roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 9.0.7 密码重置令牌表 (password_reset_tokens)

```sql
CREATE TABLE password_reset_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    client_ip VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX idx_password_reset_tokens_expires_at ON password_reset_tokens(expires_at);
```

### 9.0.8 邮箱验证表 (email_verifications)

```sql
CREATE TYPE verification_type AS ENUM ('register', 'change', 'bind');

CREATE TABLE email_verifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    email VARCHAR(255) NOT NULL,
    verification_type verification_type NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    verified_at TIMESTAMPTZ,
    client_ip VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_email_verifications_user_id ON email_verifications(user_id);
CREATE INDEX idx_email_verifications_email ON email_verifications(email);
CREATE INDEX idx_email_verifications_token ON email_verifications(token);
CREATE INDEX idx_email_verifications_expires_at ON email_verifications(expires_at);
```

### 9.0.9 登录历史表 (login_history)

```sql
CREATE TYPE login_status AS ENUM ('success', 'failed', 'blocked');
CREATE TYPE login_type AS ENUM ('password', 'oauth', 'api_key', 'sms');

CREATE TABLE login_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    login_type login_type NOT NULL,
    oauth_provider VARCHAR(50),
    client_ip VARCHAR(45),
    country VARCHAR(50),
    city VARCHAR(100),
    device_type VARCHAR(50),
    browser VARCHAR(100),
    os VARCHAR(50),
    user_agent VARCHAR(500),
    login_status login_status NOT NULL,
    failure_reason VARCHAR(255),
    geolocation JSONB,
    login_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    logout_at TIMESTAMPTZ,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_login_history_user_id ON login_history(user_id);
CREATE INDEX idx_login_history_login_type ON login_history(login_type);
CREATE INDEX idx_login_history_client_ip ON login_history(client_ip);
CREATE INDEX idx_login_history_login_at ON login_history(login_at);
CREATE INDEX idx_login_history_login_status ON login_history(login_status);
```

### 9.0.10 会话表 (sessions)

```sql
CREATE TABLE sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    client_ip VARCHAR(45),
    user_agent VARCHAR(500),
    device_fingerprint VARCHAR(255),
    last_activity TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_last_activity ON sessions(last_activity);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
```

### 9.0.11 数据表关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     用户与权限系统数据库关系图                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐         ┌──────────────┐                              │
│  │    users     │────────>│user_roles    │                              │
│  │              │         │              │                              │
│  │ - id         │         │ - user_id    │                              │
│  │ - username   │         │ - role_id    │                              │
│  └──────┬───────┘         └──────┬───────┘                              │
│         │                        │                                       │
│         │    ┌───────────────────┴──────────────┐                       │
│         │    │                                     │                       │
│         │    v                                     v                       │
│         │ ┌──────────────┐              ┌──────────────┐                 │
│         │ │oauth_accounts│              │    roles     │                 │
│         │ │              │              │              │                 │
│         │ │ - user_id    │              │ - id         │                 │
│         │ │ - provider   │              │ - role_code  │                 │
│         │ └──────────────┘              └──────┬───────┘                 │
│         │                                      │                         │
│         │    ┌─────────────────────────────────┘                         │
│         │    │                                                           │
│         │    v                                                           │
│         │ ┌──────────────────┐                    ┌──────────────┐       │
│         │ │role_permissions  │<───────────────────│ permissions  │       │
│         │ │                  │                    │              │       │
│         │ │ - role_id        │                    │ - id         │       │
│         │ │ - permission_id  │                    │ - permission_code│   │
│         │ └──────────────────┘                    └──────────────┘       │
│         │                                                                  │
│         v                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────┐       │
│  │   api_keys       │    │password_reset    │    │ email_verify │       │
│  │                  │    │    _tokens       │    │  ications    │       │
│  │ - user_id        │    │                  │    │              │       │
│  │ - key_hash       │    │ - user_id        │    │ - user_id    │       │
│  └──────────────────┘    │ - token          │    │ - token      │       │
│                          └──────────────────┘    └──────────────┘       │
│                                                                         │
│  ┌──────────────────┐    ┌──────────────┐                              │
│  │  login_history   │    │  sessions    │                              │
│  │                  │    │              │                              │
│  │ - user_id        │    │ - user_id    │                              │
│  │ - client_ip      │    │ - id         │                              │
│  └──────────────────┘    └──────────────┘                              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 9.1 用户类型

| 用户类型 | 权限 | 升级条件 |
|----------|------|----------|
| **访客** | 浏览公开 Skills | - |
| **普通用户** | 下载免费 Skills、创建 Skills | 注册 + 邮箱验证 |
| **供应商** | 创建商用 Skills、设置价格 | 实名认证 + 审核 |
| **团队管理员** | 创建团队、管理成员 | 创建团队 |
| **平台管理员** | 全局管理权限 | 平台任命 |

## 9.2 登录方式

| 方式 | 说明 | 优先级 |
|------|------|--------|
| 邮箱注册 | 基础方式 | P0 |
| 手机号 | 国内用户 | P0 |
| GitHub OAuth | 开发者友好 | P1 |
| 企业微信 | 企业用户 | P2 |

## 9.3 权限矩阵

| 操作 | 访客 | 普通用户 | 供应商 | 管理员 |
|------|------|----------|--------|--------|
| 浏览免费 Skills | ✅ | ✅ | ✅ | ✅ |
| 下载免费 Skills | ❌ | ✅ | ✅ | ✅ |
| 创建免费 Skills | ❌ | ✅ | ✅ | ✅ |
| 创建商用 Skills | ❌ | ❌ | ✅ | ✅ |
| 审核 Skills | ❌ | ❌ | ❌ | ✅ |
| 管理用户 | ❌ | ❌ | ❌ | ✅ |

## 9.4 API 密钥管理

| 密钥类型 | 用途 | 权限 |
|---------|------|------|
| `pk_live_xxx` | 生产环境 | 完整权限 |
| `pk_test_xxx` | 测试环境 | 测试权限 |
| `sk_live_xxx` | 服务端密钥 | 隐私操作权限 |
