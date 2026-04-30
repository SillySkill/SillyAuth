# 第十章：运营与增长系统

> 本文档描述 SillyMD 平台的运营功能和用户增长策略。
>
> 本章涵盖运营与增长系统所需的所有数据库表结构设计。

## 10.0 数据库设计

### 10.0.1 枚举类型定义

```sql
-- ============================================
-- 运营与增长系统枚举类型
-- ============================================

CREATE TYPE leaderboard_type AS ENUM ('skills_hot', 'skills_new', 'users_active', 'vendors_earnings', 'teams_active');
CREATE TYPE period_type AS ENUM ('daily', 'weekly', 'monthly', 'yearly', 'all_time');
CREATE TYPE entity_type AS ENUM ('skill', 'user', 'team');
CREATE TYPE recommendation_entity_type AS ENUM ('skill', 'user', 'team', 'resource');
CREATE TYPE reward_type AS ENUM ('points', 'xp', 'badge', 'premium_days');
CREATE TYPE reward_status AS ENUM ('pending', 'earned', 'paid', 'expired', 'cancelled');
CREATE TYPE trigger_condition AS ENUM ('register', 'first_skill', 'first_purchase', 'vendor_approved');
CREATE TYPE metric_type AS ENUM ('count', 'sum', 'avg', 'rate');
CREATE TYPE segment_type AS ENUM ('manual', 'rule_based', 'ai_predicted');
CREATE TYPE campaign_type AS ENUM ('email', 'sms', 'push', 'in_app', 'reward');
CREATE TYPE campaign_target_type AS ENUM ('all', 'users', 'vendors', 'admins');
CREATE TYPE send_status AS ENUM ('pending', 'sent', 'delivered', 'failed', 'bounced');
```

### 10.0.2 排行榜表 (leaderboards)

```sql
CREATE TABLE leaderboards (
    id BIGSERIAL PRIMARY KEY,
    leaderboard_type leaderboard_type NOT NULL,
    period_type period_type NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    entity_type entity_type NOT NULL,
    entity_id BIGINT NOT NULL,
    rank_position INT NOT NULL,
    score_value BIGINT NOT NULL,
    metadata JSONB,
    is_trending BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (leaderboard_type, period_type, entity_type, entity_id, period_start)
);

-- 索引
CREATE INDEX idx_leaderboards_type ON leaderboards(leaderboard_type);
CREATE INDEX idx_leaderboards_period_type ON leaderboards(period_type);
CREATE INDEX idx_leaderboards_period ON leaderboards(period_start, period_end);
CREATE INDEX idx_leaderboards_entity ON leaderboards(entity_type, entity_id);
CREATE INDEX idx_leaderboards_rank ON leaderboards(rank_position);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_leaderboards_updated_at BEFORE UPDATE ON leaderboards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 10.0.3 推荐日志表 (recommendation_logs)

```sql
CREATE TABLE recommendation_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    recommendation_type recommendation_entity_type NOT NULL,
    recommended_entity_id BIGINT NOT NULL,
    algorithm VARCHAR(100),
    score NUMERIC(5,4),
    reason VARCHAR(255),
    position INT,
    is_shown BOOLEAN NOT NULL DEFAULT FALSE,
    is_clicked BOOLEAN NOT NULL DEFAULT FALSE,
    is_converted BOOLEAN NOT NULL DEFAULT FALSE,
    shown_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,
    converted_at TIMESTAMPTZ,
    context JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_recommendation_logs_user_id ON recommendation_logs(user_id);
CREATE INDEX idx_recommendation_logs_type ON recommendation_logs(recommendation_type);
CREATE INDEX idx_recommendation_logs_entity_id ON recommendation_logs(recommended_entity_id);
CREATE INDEX idx_recommendation_logs_is_clicked ON recommendation_logs(is_clicked);
CREATE INDEX idx_recommendation_logs_created_at ON recommendation_logs(created_at);
```

### 10.0.4 邀请奖励表 (invitation_rewards)

```sql
CREATE TABLE invitation_rewards (
    id BIGSERIAL PRIMARY KEY,
    inviter_id BIGINT NOT NULL,
    invitee_id BIGINT,
    invitation_code VARCHAR(20) NOT NULL,
    invitation_channel VARCHAR(100),
    reward_type reward_type NOT NULL,
    reward_amount INT NOT NULL,
    reward_status reward_status NOT NULL DEFAULT 'pending',
    trigger_condition trigger_condition NOT NULL,
    invitee_registered_at TIMESTAMPTZ,
    trigger_completed_at TIMESTAMPTZ,
    reward_paid_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inviter_id) REFERENCES users(id),
    FOREIGN KEY (invitee_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_invitation_rewards_inviter_id ON invitation_rewards(inviter_id);
CREATE INDEX idx_invitation_rewards_invitee_id ON invitation_rewards(invitee_id);
CREATE INDEX idx_invitation_rewards_code ON invitation_rewards(invitation_code);
CREATE INDEX idx_invitation_rewards_status ON invitation_rewards(reward_status);
CREATE INDEX idx_invitation_rewards_created_at ON invitation_rewards(created_at);
```

### 10.0.5 用户留存数据表 (user_retention_data)

```sql
CREATE TABLE user_retention_data (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    cohort_date DATE NOT NULL,
    activity_date DATE NOT NULL,
    day_number INT NOT NULL,
    is_active BOOLEAN NOT NULL,
    session_count INT DEFAULT 0,
    session_duration INT DEFAULT 0,
    actions_count INT DEFAULT 0,
    last_action_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, activity_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_user_retention_data_cohort_date ON user_retention_data(cohort_date);
CREATE INDEX idx_user_retention_data_day_number ON user_retention_data(day_number);
CREATE INDEX idx_user_retention_data_is_active ON user_retention_data(is_active);
```

### 10.0.6 活动分析表 (activity_analytics)

```sql
CREATE TABLE activity_analytics (
    id BIGSERIAL PRIMARY KEY,
    activity_date DATE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value BIGINT NOT NULL,
    metric_type metric_type NOT NULL,
    segment VARCHAR(50),
    platform VARCHAR(50),
    channel VARCHAR(100),
    comparison_value BIGINT,
    comparison_rate NUMERIC(5,2),
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (activity_date, metric_name, segment, platform)
);

-- 索引
CREATE INDEX idx_activity_analytics_date ON activity_analytics(activity_date);
CREATE INDEX idx_activity_analytics_metric_name ON activity_analytics(metric_name);
CREATE INDEX idx_activity_analytics_segment ON activity_analytics(segment);
CREATE INDEX idx_activity_analytics_platform ON activity_analytics(platform);
```

### 10.0.7 用户分群表 (user_segments)

```sql
CREATE TABLE user_segments (
    id BIGSERIAL PRIMARY KEY,
    segment_name VARCHAR(100) UNIQUE NOT NULL,
    segment_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    segment_type segment_type NOT NULL,
    criteria JSONB,
    user_count INT DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES admin_users(id)
);

-- 索引
CREATE INDEX idx_user_segments_type ON user_segments(segment_type);
CREATE INDEX idx_user_segments_is_active ON user_segments(is_active);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_user_segments_updated_at BEFORE UPDATE ON user_segments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 用户分群关联表
CREATE TABLE user_segment_members (
    id BIGSERIAL PRIMARY KEY,
    segment_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    score NUMERIC(5,4),
    added_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    removed_at TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (segment_id, user_id),
    FOREIGN KEY (segment_id) REFERENCES user_segments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_user_segment_members_segment_id ON user_segment_members(segment_id);
CREATE INDEX idx_user_segment_members_user_id ON user_segment_members(user_id);
CREATE INDEX idx_user_segment_members_is_active ON user_segment_members(is_active);
```

### 10.0.8 召回活动表 (recall_campaigns)

```sql
CREATE TABLE recall_campaigns (
    id BIGSERIAL PRIMARY KEY,
    campaign_name VARCHAR(200) NOT NULL,
    campaign_type campaign_type NOT NULL,
    target_segment_id BIGINT,
    target_criteria JSONB,
    message_template TEXT NOT NULL,
    reward_type VARCHAR(20),
    reward_amount INT,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    scheduled_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    target_count INT DEFAULT 0,
    sent_count INT DEFAULT 0,
    delivered_count INT DEFAULT 0,
    opened_count INT DEFAULT 0,
    clicked_count INT DEFAULT 0,
    converted_count INT DEFAULT 0,
    budget NUMERIC(10,2),
    cost NUMERIC(10,2) DEFAULT 0,
    created_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (target_segment_id) REFERENCES user_segments(id),
    FOREIGN KEY (created_by) REFERENCES admin_users(id)
);

-- 索引
CREATE INDEX idx_recall_campaigns_type ON recall_campaigns(campaign_type);
CREATE INDEX idx_recall_campaigns_status ON recall_campaigns(status);
CREATE INDEX idx_recall_campaigns_scheduled_at ON recall_campaigns(scheduled_at);
CREATE INDEX idx_recall_campaigns_target_segment_id ON recall_campaigns(target_segment_id);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_recall_campaigns_updated_at BEFORE UPDATE ON recall_campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 10.0.9 召回日志表 (recall_logs)

```sql
CREATE TABLE recall_logs (
    id BIGSERIAL PRIMARY KEY,
    campaign_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    status send_status NOT NULL DEFAULT 'pending',
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,
    converted_at TIMESTAMPTZ,
    failed_reason TEXT,
    error_code VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES recall_campaigns(id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_recall_logs_campaign_id ON recall_logs(campaign_id);
CREATE INDEX idx_recall_logs_user_id ON recall_logs(user_id);
CREATE INDEX idx_recall_logs_status ON recall_logs(status);
CREATE INDEX idx_recall_logs_sent_at ON recall_logs(sent_at);
```

### 10.0.10 页面访问统计表 (page_views)

```sql
CREATE TABLE page_views (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    page_path VARCHAR(500) NOT NULL,
    session_id VARCHAR(255),
    view_duration INT,
    referrer VARCHAR(500),
    user_agent VARCHAR(500),
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 表注释
COMMENT ON TABLE page_views IS '页面访问统计表';
COMMENT ON COLUMN page_views.id IS '访问 ID';
COMMENT ON COLUMN page_views.user_id IS '用户 ID（NULL=匿名用户）';
COMMENT ON COLUMN page_views.page_path IS '页面路径';
COMMENT ON COLUMN page_views.session_id IS '会话 ID';
COMMENT ON COLUMN page_views.view_duration IS '浏览时长（秒）';
COMMENT ON COLUMN page_views.referrer IS '来源页面';
COMMENT ON COLUMN page_views.user_agent IS '用户代理';
COMMENT ON COLUMN page_views.ip_address IS 'IP 地址';
COMMENT ON COLUMN page_views.created_at IS '访问时间';

-- 索引
CREATE INDEX idx_page_views_user_created ON page_views(user_id, created_at DESC);
CREATE INDEX idx_page_views_path_created ON page_views(page_path, created_at DESC);
CREATE INDEX idx_page_views_session_id ON page_views(session_id);
CREATE INDEX idx_page_views_created_at ON page_views(created_at DESC);
```

### 10.0.11 用户活动日志表 (user_activity_logs)

```sql
CREATE TABLE user_activity_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id BIGINT,
    activity_title VARCHAR(255) NOT NULL,
    activity_detail TEXT,
    metadata JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 表注释
COMMENT ON TABLE user_activity_logs IS '用户活动日志表';
COMMENT ON COLUMN user_activity_logs.id IS '日志 ID';
COMMENT ON COLUMN user_activity_logs.user_id IS '用户 ID';
COMMENT ON COLUMN user_activity_logs.activity_type IS '活动类型：login, logout, view, create, update, delete, download';
COMMENT ON COLUMN user_activity_logs.resource_type IS '资源类型：skill, team, project, user';
COMMENT ON COLUMN user_activity_logs.resource_id IS '资源 ID';
COMMENT ON COLUMN user_activity_logs.activity_title IS '活动标题';
COMMENT ON COLUMN user_activity_logs.activity_detail IS '活动详情';
COMMENT ON COLUMN user_activity_logs.metadata IS '额外元数据（JSONB 格式）';
COMMENT ON COLUMN user_activity_logs.ip_address IS 'IP 地址';
COMMENT ON COLUMN user_activity_logs.created_at IS '活动时间';

-- 索引
CREATE INDEX idx_user_activity_logs_user_id ON user_activity_logs(user_id);
CREATE INDEX idx_user_activity_logs_type ON user_activity_logs(activity_type);
CREATE INDEX idx_user_activity_logs_resource ON user_activity_logs(resource_type, resource_id);
CREATE INDEX idx_user_activity_logs_created_at ON user_activity_logs(created_at DESC);
```

### 10.0.9 数据表关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      运营与增长系统数据库关系图                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐         ┌──────────────────┐                      │
│  │   leaderboards   │         │recommendation_logs│                     │
│  │                  │         │                  │                      │
│  │ - entity_id      │         │ - user_id        │                      │
│  │ - rank_position  │         │ - recommended_id │                      │
│  └──────────────────┘         │ - is_clicked     │                      │
│                                └──────────────────┘                      │
│                                                                         │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────┐       │
│  │invitation_rewards│    │user_retention    │    │  activity_   │       │
│  │                  │    │     _data        │    │  analytics   │       │
│  │ - inviter_id     │    │                  │    │              │       │
│  │ - invitee_id     │    │ - user_id        │    │ - metric_name│       │
│  │ - reward_status  │    │ - cohort_date    │    │ - metric_value│       │
│  └──────────────────┘    └──────────────────┘    └──────────────┘       │
│                                                                         │
│  ┌──────────────────┐         ┌──────────────────┐                      │
│  │  user_segments   │────────>│recall_campaigns  │                      │
│  │                  │         │                  │                      │
│  │ - segment_id     │         │ - target_segment │                      │
│  │ - criteria       │         │ - status         │                      │
│  └────────┬─────────┘         └────────┬─────────┘                      │
│           │                            │                                │
│           v                            v                                │
│  ┌──────────────────────┐    ┌──────────────────┐                       │
│  │user_segment_members  │    │   recall_logs    │                       │
│  │                      │    │                  │                       │
│  │ - segment_id         │    │ - campaign_id    │                       │
│  │ - user_id            │    │ - user_id        │                       │
│  └──────────────────────┘    └──────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 10.1 成就系统

| 成就 | 条件 | 奖励 |
|------|------|------|
| **初出茅庐** | 创建第一个 Skill | 10 XP |
| **创作新星** | 创建 10 个 Skills | 100 XP + 50 Points |
| **优质创作者** | Skills 平均评分 > 4.5 | 200 XP + 100 Points |
| **开源先锋** | 免费 Skills 下载 > 1000 | 500 XP + 200 Points |
| **商业精英** | 商用销售额 > 10000 Points | 1000 XP + 500 Points |
| **社区领袖** | 获赞 > 1000 | 300 XP + 100 Points |
| **评论达人** | 发表评论 > 100 | 100 XP |
| **团队玩家** | 创建团队 > 5 个 | 200 XP |

## 10.2 排行榜

```
┌─────────────────────────────────────────────────────────────┐
│                        排行榜                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  热门 Skills 排行                                           │
│  ├── 今日热门                                               │
│  ├── 本周热门                                               │
│  ├── 本月热门                                               │
│  └── 历史热门                                               │
│                                                             │
│  优秀创作者排行                                             │
│  ├── 按作品数量                                             │
│  ├── 按下载量                                               │
│  └── 按销售额                                               │
│                                                             │
│  团队排行                                                   │
│  ├── 按成员数量                                             │
│  ├── 按项目数量                                             │
│  └── 按活跃度                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 10.3 推荐系统

```python
# 推荐算法
def recommend_skills(user_id: int, limit: int = 10) -> List[str]:
    score = {}

    # 1. 协同过滤 (40%)
    similar_users = get_similar_users(user_id, top_n=20)
    for user in similar_users:
        for skill in user.favorited_skills:
            score[skill.id] = score.get(skill.id, 0) + 40

    # 2. 内容匹配 (30%)
    user_tags = get_user_interest_tags(user_id)
    for skill in all_active_skills:
        overlap = len(set(skill.tags) & set(user_tags))
        score[skill.id] = score.get(skill.id, 0) + overlap * 30

    # 3. 热度加成 (20%)
    trending = get_trending_skills(period='7d')
    for skill in trending:
        score[skill.id] = score.get(skill.id, 0) + 20

    # 4. 新手优惠 (10%)
    if is_new_user(user_id):
        free_skills = get_free_skills()
        for skill in free_skills:
            score[skill.id] = score.get(skill.id, 0) + 10

    # 排序并返回
    ranked = sorted(score.items(), key=lambda x: x[1], reverse=True)
    return [skill_id for skill_id, _ in ranked[:limit]]
```

## 10.4 邀请返利系统

| 行为 | 奖励 |
|------|------|
| 邀请新用户注册 | 50 AI Points |
| 被邀请人首次充值 | 额外 20% 奖励 |
| 被邀请人成为供应商 | 100 AI Points |

## 10.5 用户召回机制

```
┌─────────────────────────────────────────────────────────────┐
│                    用户召回策略                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  流失用户定义                                               │
│  └── 7 天未登录为轻度流失                                   │
│  └── 30 天未登录为重度流失                                  │
│                                                             │
│  召回策略                                                   │
│  ├── 邮件通知                                               │
│  │   ├── 新 Skills 推荐                                     │
│  │   ├── 专属优惠码                                         │
│  │   └── 社区动态                                           │
│  ├── 站内消息                                               │
│  └── 积分回归奖励                                           │
│      └── 回归即送 100 Points                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 10.6 数据统计与分析

```
用户活跃度分析
├── 日活 (DAU)
├── 周活 (WAU)
├── 月活 (MAU)
└── 留存率
    ├── 次日留存
    ├── 7日留存
    └── 30日留存

Skills 数据分析
├── 浏览量排行
├── 下载量排行
├── 转化率分析
└── 评分分析

商业数据分析
├── 销售额统计
├── ARPU (每用户平均收入)
├── 付费转化率
└── 复购率
```
