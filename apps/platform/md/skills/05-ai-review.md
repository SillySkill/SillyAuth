# 第五章：AI 审核系统

> 本文档描述 SillyMD 平台的 AI 审核机制和流程。
>
> 本章涵盖 AI 审核系统所需的所有数据库表结构设计。

## 5.0 数据库设计

### 5.0.1 枚举类型定义

```sql
-- ============================================
-- AI 审核系统枚举类型
-- ============================================

CREATE TYPE review_stage AS ENUM ('l1_auto', 'l2_ai', 'l3_manual', 'completed', 'rejected');
CREATE TYPE review_queue_status AS ENUM ('pending', 'reviewing', 'approved', 'rejected', 'appealed');
CREATE TYPE review_priority AS ENUM ('low', 'normal', 'high', 'urgent');
CREATE TYPE review_stage_type AS ENUM ('auto', 'ai', 'manual');
CREATE TYPE review_criterion_category AS ENUM ('format', 'safety', 'quality', 'compliance', 'originality');
CREATE TYPE review_check_type AS ENUM ('auto', 'ai', 'manual');
CREATE TYPE quota_type AS ENUM ('daily_free', 'daily_paid', 'monthly_total');
CREATE TYPE feedback_from AS ENUM ('submitter', 'reviewer', 'admin');
CREATE TYPE feedback_type AS ENUM ('complaint', 'suggestion', 'question', 'approval');
CREATE TYPE feedback_status AS ENUM ('pending', 'responded', 'resolved', 'closed');
CREATE TYPE ai_review_status AS ENUM ('success', 'failed', 'timeout');
```

### 5.0.2 审核队列表 (review_queues)

```sql
CREATE TABLE review_queues (
    id BIGSERIAL PRIMARY KEY,
    skill_id BIGINT NOT NULL,
    submitter_id BIGINT NOT NULL,
    reviewer_id BIGINT,
    stage review_stage NOT NULL DEFAULT 'l1_auto',
    status review_queue_status NOT NULL DEFAULT 'pending',
    priority review_priority NOT NULL DEFAULT 'normal',
    source VARCHAR(50) DEFAULT 'manual',
    ai_model_version VARCHAR(50),
    ai_confidence NUMERIC(4,3),
    ai_scores JSONB,
    manual_review_note TEXT,
    reject_reason TEXT,
    submit_note TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (submitter_id) REFERENCES users(id),
    FOREIGN KEY (reviewer_id) REFERENCES admin_users(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_review_queues_skill_id ON review_queues(skill_id);
CREATE INDEX idx_review_queues_submitter_id ON review_queues(submitter_id);
CREATE INDEX idx_review_queues_reviewer_id ON review_queues(reviewer_id);
CREATE INDEX idx_review_queues_stage ON review_queues(stage);
CREATE INDEX idx_review_queues_status ON review_queues(status);
CREATE INDEX idx_review_queues_priority ON review_queues(priority);
CREATE INDEX idx_review_queues_source ON review_queues(source);
CREATE INDEX idx_review_queues_submitted_at ON review_queues(submitted_at);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_review_queues_updated_at BEFORE UPDATE ON review_queues
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 5.0.3 审核阶段配置表 (review_stages)

```sql
CREATE TABLE review_stages (
    id BIGSERIAL PRIMARY KEY,
    stage_code VARCHAR(50) UNIQUE NOT NULL,
    stage_name VARCHAR(100) NOT NULL,
    stage_order INT NOT NULL,
    stage_type review_stage_type NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    config JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_review_stages_stage_order ON review_stages(stage_order);
CREATE INDEX idx_review_stages_is_active ON review_stages(is_active);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_review_stages_updated_at BEFORE UPDATE ON review_stages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 初始化审核阶段
INSERT INTO review_stages (stage_code, stage_name, stage_order, stage_type, description, config) VALUES
('l1_auto', 'L1 初审(自动)', 1, 'auto', 'AI 自动格式检查和基础合规检查', '{"auto_approve_threshold": 0.95}'),
('l2_ai', 'L2 深度审核(AI)', 2, 'ai', 'AI 深度内容分析和质量评估', '{"models": ["gpt-4", "claude-3"], "max_retries": 3}'),
('l3_manual', 'L3 人工审核', 3, 'manual', '人工复核和最终决策', '{"escalation_hours": 48}');
```

### 5.0.4 审核标准表 (review_criteria)

```sql
CREATE TABLE review_criteria (
    id BIGSERIAL PRIMARY KEY,
    criterion_code VARCHAR(50) UNIQUE NOT NULL,
    criterion_name VARCHAR(100) NOT NULL,
    category review_criterion_category NOT NULL,
    description TEXT,
    weight NUMERIC(4,3) NOT NULL DEFAULT 1.000,
    min_score NUMERIC(4,3) NOT NULL DEFAULT 0.000,
    check_type review_check_type NOT NULL,
    config JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_review_criteria_category ON review_criteria(category);
CREATE INDEX idx_review_criteria_check_type ON review_criteria(check_type);
CREATE INDEX idx_review_criteria_is_active ON review_criteria(is_active);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_review_criteria_updated_at BEFORE UPDATE ON review_criteria
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 初始化审核标准
INSERT INTO review_criteria (criterion_code, criterion_name, category, weight, min_score, check_type, description) VALUES
('format_structure', '格式结构检查', 'format', 0.15, 0.800, 'auto', '检查JSON结构、必填字段、数据类型'),
('format_documentation', '文档完整性', 'format', 0.10, 0.700, 'ai', '检查描述、使用说明、示例代码'),
('safety_malware', '恶意代码检测', 'safety', 0.25, 0.950, 'ai', '检测病毒、木马、恶意脚本'),
('sensitivity_check', '敏感信息检测', 'safety', 0.15, 0.900, 'ai', '检测隐私信息、敏感词汇'),
('quality_code', '代码质量评估', 'quality', 0.15, 0.700, 'ai', '评估代码可读性、可维护性'),
('quality_functional', '功能完整性', 'quality', 0.10, 0.750, 'ai', '评估功能实现完整性'),
('compliance_legal', '法律合规性', 'compliance', 0.05, 0.900, 'ai', '检查违法内容、侵权行为'),
('originality_check', '原创性检测', 'originality', 0.05, 0.800, 'ai', '检测抄袭、重复内容');
```

### 5.0.5 AI审核日志表 (ai_review_logs)

```sql
CREATE TABLE ai_review_logs (
    id BIGSERIAL PRIMARY KEY,
    review_queue_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    stage VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    input_prompt TEXT,
    input_data JSONB,
    output_result JSONB,
    score NUMERIC(4,3),
    criteria_scores JSONB,
    confidence NUMERIC(4,3),
    tokens_used INT,
    cost_usd NUMERIC(10,4),
    duration_ms INT,
    status ai_review_status NOT NULL,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_queue_id) REFERENCES review_queues(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id)
);

-- 索引
CREATE INDEX idx_ai_review_logs_review_queue_id ON ai_review_logs(review_queue_id);
CREATE INDEX idx_ai_review_logs_skill_id ON ai_review_logs(skill_id);
CREATE INDEX idx_ai_review_logs_stage ON ai_review_logs(stage);
CREATE INDEX idx_ai_review_logs_model_name ON ai_review_logs(model_name);
CREATE INDEX idx_ai_review_logs_created_at ON ai_review_logs(created_at);
```

### 5.0.6 审核反馈表 (review_feedback)

```sql
CREATE TABLE review_feedback (
    id BIGSERIAL PRIMARY KEY,
    review_queue_id BIGINT NOT NULL,
    skill_id BIGINT NOT NULL,
    feedback_from feedback_from NOT NULL,
    from_user_id BIGINT NOT NULL,
    feedback_type feedback_type NOT NULL,
    content TEXT NOT NULL,
    attachments JSONB,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    status feedback_status NOT NULL DEFAULT 'pending',
    admin_response TEXT,
    responded_at TIMESTAMPTZ,
    responded_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_queue_id) REFERENCES review_queues(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id),
    FOREIGN KEY (from_user_id) REFERENCES users(id),
    FOREIGN KEY (responded_by) REFERENCES admin_users(id)
);

-- 索引
CREATE INDEX idx_review_feedback_review_queue_id ON review_feedback(review_queue_id);
CREATE INDEX idx_review_feedback_skill_id ON review_feedback(skill_id);
CREATE INDEX idx_review_feedback_feedback_from ON review_feedback(feedback_from);
CREATE INDEX idx_review_feedback_status ON review_feedback(status);
CREATE INDEX idx_review_feedback_created_at ON review_feedback(created_at);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_review_feedback_updated_at BEFORE UPDATE ON review_feedback
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 5.0.7 审核配额表 (review_quotas)

```sql
CREATE TABLE review_quotas (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    quota_type quota_type NOT NULL,
    total_quota INT NOT NULL,
    used_quota INT NOT NULL DEFAULT 0,
    reset_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, quota_type),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_review_quotas_user_id ON review_quotas(user_id);
CREATE INDEX idx_review_quotas_reset_at ON review_quotas(reset_at);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_review_quotas_updated_at BEFORE UPDATE ON review_quotas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 5.0.7 数据表关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI审核系统数据库关系图                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐         ┌──────────────────┐                         │
│  │    skills    │────────>│ review_queues    │                         │
│  │              │         │                  │                         │
│  │ - id         │         │ - skill_id       │                         │
│  │ - submitter_id│        │ - submitter_id   │                         │
│  └──────────────┘         │ - reviewer_id    │                         │
│            │              │ - stage          │                         │
│            │              │ - status         │                         │
│            │              └────────┬─────────┘                         │
│            │                       │                                   │
│            │    ┌──────────────────┴──────────────┐                   │
│            │    │                                  │                   │
│            │    v                                  v                   │
│            │ ┌──────────────┐            ┌──────────────────┐          │
│            │ │review_stages │            │  ai_review_logs  │          │
│            │ │              │            │                  │          │
│            │ │ - stage_code │            │ - review_queue_id│          │
│            │ │ - stage_type │            │ - model_name     │          │
│            │ └──────────────┘            │ - score          │          │
│            │                            └──────────────────┘          │
│            │                                                                  │
│            v                                                            │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────┐       │
│  │review_criteria   │    │review_feedback   │    │review_quotas │       │
│  │                  │    │                  │    │              │       │
│  │ - criterion_code │    │ - review_queue_id│    │ - user_id    │       │
│  │ - category       │    │ - skill_id       │    │ - quota_type │       │
│  └──────────────────┘    │ - feedback_from  │    └──────────────┘       │
│                          └──────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5.1 审核目的

所有上架的 Skills 必须通过 AI 审核，确保：
- **合规性**：符合法律法规，无违法违规内容
- **安全性**：无恶意代码、无病毒木马
- **准确性**：内容真实有效，无虚假宣传
- **格式规范**：符合 Skills 格式标准

## 5.2 审核流程

```
┌─────────────────────────────────────────────────────────────┐
│                      AI 审核流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户提交 Skills                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │   L1 初审   │  AI 自动审核                               │
│  │  (AI 自动)  │  - 格式检查                                │
│  └──────┬──────┘  - 基础合规检查                            │
│         │          - 重复检测                                │
│         │          - 消耗额度：1 次/天 免费                  │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │   L2 复审   │  AI 深度审核                               │
│  │ (AI + 人工) │  - 专业准确性                              │
│  └──────┬──────┘  - 商业价值评估                            │
│         │          - 定价合理性                              │
│         │          - 市场需求分析                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │   L3 终审   │  平台管理员                                │
│  │  (管理员)   │  - 最终质量把关                            │
│  └──────┬──────┘  - 上架决定                                │
│         │                                                   │
│         ▼                                                   │
│   上架 / 驳回                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 5.3 审核维度

| 维度 | 技术 Skills | 产品 Skills | 设计 Skills | 市场/运营 Skills |
|------|-------------|-------------|-------------|------------------|
| 法律合规 | ✅ | ✅ | ✅ | ✅ |
| 内容安全 | ✅ | ✅ | ✅ | ✅ |
| 格式规范 | ✅ | ✅ | ✅ | ✅ |
| 专业准确 | ✅ | ✅ | ✅ | ✅ |
| 商业价值 | ✅ | ✅ | ✅ | ✅ |
| 原创性检测 | ✅ | ✅ | ✅ | ✅ |

## 5.4 审核配额与定价

| 用户类型 | 免费审核额度 | 超额费用 |
|---------|-------------|---------|
| 普通用户 | 3 次/月 | 10 AI Points/次 |
| 供应商 | 20 次/月 | 5 AI Points/次 |
| 金牌供应商 | 100 次/月 | 免费 |

## 5.5 审核结果处理

| 结果 | 说明 | 处理方式 |
|------|------|----------|
| **通过** | 符合所有标准 | 自动上架 |
| **需修正** | 存在小问题，可修正 | 返回用户修正后重新提交 |
| **驳回** | 存在重大问题 | 拒绝上架，说明原因 |
