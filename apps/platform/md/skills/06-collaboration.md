# 第六章：多领域协作系统

> 本文档介绍 SillyMD 平台的团队协作功能和项目管理体系。
>
> 本章涵盖多领域协作系统所需的所有数据库表结构设计。

## 6.0 数据库设计

### 6.0.1 枚举类型定义

```sql
-- ============================================
-- 多领域协作系统枚举类型
-- ============================================

CREATE TYPE activity_type AS ENUM ('create', 'update', 'delete', 'join', 'leave', 'invite');
CREATE TYPE resource_type AS ENUM ('team', 'project', 'skill', 'member', 'milestone');
CREATE TYPE dependency_type AS ENUM ('hard', 'soft', 'optional');
CREATE TYPE dependency_status AS ENUM ('active', 'blocked', 'resolved', 'deferred');
CREATE TYPE session_type AS ENUM ('document_edit', 'code_review', 'planning', 'brainstorm', 'retrospective');
CREATE TYPE session_status AS ENUM ('scheduled', 'active', 'paused', 'completed', 'cancelled');
CREATE TYPE reference_type AS ENUM ('import', 'extend', 'implement', 'depend_on', 'relate_to');
CREATE TYPE reference_status AS ENUM ('active', 'deprecated', 'broken');
CREATE TYPE milestone_type AS ENUM ('release', 'review', 'delivery', 'checkpoint');
CREATE TYPE milestone_status AS ENUM ('planned', 'in_progress', 'completed', 'delayed', 'cancelled');
CREATE TYPE priority_level AS ENUM ('low', 'normal', 'high', 'critical');
```

### 6.0.2 团队活动日志表 (team_activity_logs)

```sql
CREATE TABLE team_activity_logs (
    id BIGSERIAL PRIMARY KEY,
    team_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    activity_type activity_type NOT NULL,
    resource_type resource_type NOT NULL,
    resource_id BIGINT,
    activity_title VARCHAR(255) NOT NULL,
    activity_detail TEXT,
    metadata JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_team_activity_logs_team_id ON team_activity_logs(team_id);
CREATE INDEX idx_team_activity_logs_user_id ON team_activity_logs(user_id);
CREATE INDEX idx_team_activity_logs_activity_type ON team_activity_logs(activity_type);
CREATE INDEX idx_team_activity_logs_resource ON team_activity_logs(resource_type, resource_id);
CREATE INDEX idx_team_activity_logs_created_at ON team_activity_logs(created_at);

-- 表注释
COMMENT ON TABLE team_activity_logs IS '团队活动日志表，记录所有团队成员的操作';
COMMENT ON COLUMN team_activity_logs.team_id IS '团队 ID';
COMMENT ON COLUMN team_activity_logs.user_id IS '操作用户 ID';
COMMENT ON COLUMN team_activity_logs.activity_type IS '活动类型：create/update/delete/join/leave/invite';
COMMENT ON COLUMN team_activity_logs.resource_type IS '资源类型：team/project/skill/member/milestone';
COMMENT ON COLUMN team_activity_logs.resource_id IS '资源 ID';
COMMENT ON COLUMN team_activity_logs.activity_title IS '活动标题';
COMMENT ON COLUMN team_activity_logs.activity_detail IS '活动详情描述';
COMMENT ON COLUMN team_activity_logs.metadata IS '额外元数据（JSONB 格式）';
COMMENT ON COLUMN team_activity_logs.ip_address IS '操作者 IP 地址';
```

### 6.0.3 项目依赖关系表 (project_dependencies)

```sql
CREATE TABLE project_dependencies (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT NOT NULL,
    depends_on_project_id BIGINT NOT NULL,
    dependency_type dependency_type NOT NULL DEFAULT 'soft',
    dependency_reason TEXT,
    status dependency_status NOT NULL DEFAULT 'active',
    created_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (project_id, depends_on_project_id),
    FOREIGN KEY (project_id) REFERENCES team_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_project_id) REFERENCES team_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_project_dependencies_project_id ON project_dependencies(project_id);
CREATE INDEX idx_project_dependencies_depends_on ON project_dependencies(depends_on_project_id);
CREATE INDEX idx_project_dependencies_status ON project_dependencies(status);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_project_dependencies_updated_at BEFORE UPDATE ON project_dependencies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 表注释
COMMENT ON TABLE project_dependencies IS '项目间依赖关系表';
COMMENT ON COLUMN project_dependencies.project_id IS '项目 ID';
COMMENT ON COLUMN project_dependencies.depends_on_project_id IS '依赖的项目 ID';
COMMENT ON COLUMN project_dependencies.dependency_type IS '依赖类型：hard=强依赖, soft=弱依赖, optional=可选';
COMMENT ON COLUMN project_dependencies.dependency_reason IS '依赖原因说明';
COMMENT ON COLUMN project_dependencies.status IS '依赖状态：active/blocked/resolved/deferred';
COMMENT ON COLUMN project_dependencies.created_by IS '创建人 ID';
COMMENT ON COLUMN project_dependencies.created_at IS '创建时间';
COMMENT ON COLUMN project_dependencies.updated_at IS '最后更新时间';
```

### 6.0.4 协作会话表 (collaboration_sessions)

```sql
CREATE TABLE collaboration_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) UNIQUE NOT NULL,
    project_id BIGINT,
    skill_id BIGINT,
    session_type session_type NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    host_user_id BIGINT NOT NULL,
    max_participants INT DEFAULT 10,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    password VARCHAR(255),
    status session_status NOT NULL DEFAULT 'scheduled',
    scheduled_start_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    duration_minutes INT,
    recording_url VARCHAR(500),
    transcript TEXT,
    action_items JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES team_projects(id) ON DELETE SET NULL,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL,
    FOREIGN KEY (host_user_id) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_collaboration_sessions_session_id ON collaboration_sessions(session_id);
CREATE INDEX idx_collaboration_sessions_project_id ON collaboration_sessions(project_id);
CREATE INDEX idx_collaboration_sessions_skill_id ON collaboration_sessions(skill_id);
CREATE INDEX idx_collaboration_sessions_host_user_id ON collaboration_sessions(host_user_id);
CREATE INDEX idx_collaboration_sessions_status ON collaboration_sessions(status);
CREATE INDEX idx_collaboration_sessions_scheduled_start ON collaboration_sessions(scheduled_start_at);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_collaboration_sessions_updated_at BEFORE UPDATE ON collaboration_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 表注释
COMMENT ON TABLE collaboration_sessions IS '实时协作会话表（如视频会议、代码审查等）';
COMMENT ON COLUMN collaboration_sessions.session_id IS '会话唯一标识';
COMMENT ON COLUMN collaboration_sessions.project_id IS '关联项目 ID（可选）';
COMMENT ON COLUMN collaboration_sessions.skill_id IS '关联 Skill ID（可选）';
COMMENT ON COLUMN collaboration_sessions.session_type IS '会话类型：document_edit/code_review/planning/brainstorm/retrospective';
COMMENT ON COLUMN collaboration_sessions.title IS '会话标题';
COMMENT ON COLUMN collaboration_sessions.description IS '会话描述';
COMMENT ON COLUMN collaboration_sessions.host_user_id IS '主持人 ID';
COMMENT ON COLUMN collaboration_sessions.max_participants IS '最大参与者数量';
COMMENT ON COLUMN collaboration_sessions.is_public IS '是否公开会话';
COMMENT ON COLUMN collaboration_sessions.password IS '会话密码（NULL=无密码）';
COMMENT ON COLUMN collaboration_sessions.status IS '会话状态：scheduled/active/paused/completed/cancelled';
COMMENT ON COLUMN collaboration_sessions.scheduled_start_at IS '计划开始时间';
COMMENT ON COLUMN collaboration_sessions.started_at IS '实际开始时间';
COMMENT ON COLUMN collaboration_sessions.ended_at IS '结束时间';
COMMENT ON COLUMN collaboration_sessions.duration_minutes IS '会话时长（分钟）';
COMMENT ON COLUMN collaboration_sessions.recording_url IS '录制文件 URL';
COMMENT ON COLUMN collaboration_sessions.transcript IS '会话文字记录';
COMMENT ON COLUMN collaboration_sessions.action_items IS '行动项清单（JSONB 数组）';
```

### 6.0.5 协作参与者表 (collaboration_participants)

```sql
-- 会话参与者表
CREATE TABLE collaboration_participants (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    user_id BIGINT NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'participant',
    joined_at TIMESTAMPTZ,
    left_at TIMESTAMPTZ,
    is_online BOOLEAN NOT NULL DEFAULT FALSE,
    last_heartbeat TIMESTAMPTZ,
    metadata JSONB,
    UNIQUE (session_id, user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_collaboration_participants_session_id ON collaboration_participants(session_id);
CREATE INDEX idx_collaboration_participants_user_id ON collaboration_participants(user_id);
CREATE INDEX idx_collaboration_participants_is_online ON collaboration_participants(is_online);
```

### 6.0.5 Skills引用关系表 (skill_references)

```sql
CREATE TABLE skill_references (
    id BIGSERIAL PRIMARY KEY,
    source_skill_id BIGINT NOT NULL,
    target_skill_id BIGINT NOT NULL,
    reference_type reference_type NOT NULL,
    reference_description TEXT,
    is_required BOOLEAN NOT NULL DEFAULT FALSE,
    version_constraint VARCHAR(100),
    status reference_status NOT NULL DEFAULT 'active',
    created_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source_skill_id, target_skill_id, reference_type),
    FOREIGN KEY (source_skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (target_skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_skill_references_source_skill ON skill_references(source_skill_id);
CREATE INDEX idx_skill_references_target_skill ON skill_references(target_skill_id);
CREATE INDEX idx_skill_references_reference_type ON skill_references(reference_type);
CREATE INDEX idx_skill_references_status ON skill_references(status);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_skill_references_updated_at BEFORE UPDATE ON skill_references
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 6.0.6 项目里程碑表 (project_milestones)

```sql
CREATE TABLE project_milestones (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT NOT NULL,
    milestone_name VARCHAR(200) NOT NULL,
    description TEXT,
    milestone_type milestone_type NOT NULL,
    target_date DATE NOT NULL,
    actual_date DATE,
    status milestone_status NOT NULL DEFAULT 'planned',
    progress INT DEFAULT 0,
    deliverables JSONB,
    dependencies JSONB,
    assigned_to BIGINT,
    priority priority_level NOT NULL DEFAULT 'normal',
    completion_notes TEXT,
    completed_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES team_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    FOREIGN KEY (completed_by) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_project_milestones_project_id ON project_milestones(project_id);
CREATE INDEX idx_project_milestones_target_date ON project_milestones(target_date);
CREATE INDEX idx_project_milestones_status ON project_milestones(status);
CREATE INDEX idx_project_milestones_assigned_to ON project_milestones(assigned_to);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_project_milestones_updated_at BEFORE UPDATE ON project_milestones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 6.0.6 数据表关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     多领域协作系统数据库关系图                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐         ┌──────────────┐                              │
│  │    teams     │────────>│team_projects │                              │
│  │              │         │              │                              │
│  │ - id         │         │ - id         │                              │
│  └──────────────┘         └──────┬───────┘                              │
│            │                      │                                       │
│            │    ┌─────────────────┴──────────────┐                       │
│            │    │                                │                       │
│            v    v                                v                       │
│  ┌──────────────────┐   ┌──────────────────┐   ┌──────────────┐        │
│  │team_activity_logs│   │project_dependencies│  │collaboration │        │
│  │                  │   │                  │   │   _sessions  │        │
│  │ - team_id        │   │ - project_id     │   │ - project_id │        │
│  │ - user_id        │   │ - depends_on_id  │   │ - skill_id   │        │
│  └──────────────────┘   └──────────────────┘   └──────┬───────┘        │
│                                                         │                │
│                                                         v                │
│  ┌──────────────────┐                     ┌──────────────────────┐       │
│  │project_milestones│                     │collaboration_        │       │
│  │                  │                     │    participants       │       │
│  │ - project_id     │                     │ - session_id         │       │
│  │ - assigned_to    │                     │ - user_id            │       │
│  └──────────────────┘                     └──────────────────────┘       │
│                                                                         │
│  ┌──────────────┐                                                       │
│  │skill_        │                                                       │
│  │ references   │                                                       │
│  │              │                                                       │
│  │ - source_id  │                                                       │
│  │ - target_id  │                                                       │
│  └──────────────┘                                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6.1 协作理念

**核心理念**：将 Skills 标准化扩展到所有工作领域。

**SillyMD 的解决方案**：所有团队都用 Skills 标准来管理和协作。

## 6.2 团队组织结构

```
团队域名结构：sillymd.com/{team_slug}

示例：
├── sillymd.com/acme-tech          → ACME 科技公司
│   └── sillymd.com/acme-tech/payment-system  → 项目：支付系统
├── sillymd.com/design-studio      → 某设计工作室
├── sillymd.com/marketing-agency   → 某营销公司
└── sillymd.com/startup-abc        → 某创业团队
```

## 6.3 团队角色

| 角色 | 权限 | 说明 |
|------|------|------|
| **Owner** | 完全控制 | 团队创建者，可解散团队 |
| **Admin** | 管理 | 管理成员、设置、项目 |
| **Member** | 编辑 | 创建/编辑 Skills，参与项目 |
| **Viewer** | 查看 | 只读访问团队内容 |

## 6.4 项目协作模式

```
┌─────────────────────────────────────────────────────────────┐
│                    项目协作模式                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  项目启动                                                   │
│    ├── 产品经理创建 "产品需求 Skill"                        │
│    ├── 设计师基于需求创建 "设计规范 Skill"                  │
│    ├── 开发者基于规范创建 "技术实现 Skill"                  │
│    └── 运营创建 "推广方案 Skill"                            │
│                                                             │
│  项目迭代                                                   │
│    ├── 每个 Skill 独立版本控制                              │
│    ├── Skill 之间通过依赖关系自动关联                       │
│    ├── 上游 Skill 变更通知下游维护者                        │
│    └── 形成完整的知识沉淀                                   │
│                                                             │
│  项目交付                                                   │
│    ├── 所有 Skills 形成项目资产                             │
│    ├── 可导出为完整项目文档                                 │
│    ├── 可打包发布为商用 Skill                               │
│    └── 可复用至新项目                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 6.5 Skills 引用系统

Skills 可以相互引用，形成知识网络：

```yaml
# 产品需求 Skill
skill:
  id: "prd-user-auth"
  name: "用户认证需求"
  version: "1.0.0"
  dependencies:
    - skill_id: "design-auth-ui"
      type: "design"
      version: ">=1.0.0"
    - skill_id: "impl-auth-api"
      type: "tech"
      version: ">=1.2.0"

# 技能依赖图自动生成
dependency_graph:
  prd-user-auth:
    ├── design-auth-ui
    │   └── design-color-palette (底层依赖)
    └── impl-auth-api
        ├── tech-database-base (底层依赖)
        └── tech-cache (可选依赖)
```
