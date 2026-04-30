# 第十九章：管理后台系统

> 本文档描述平台管理后台的功能，包括爬虫系统、审核管理和系统设置。
>
> 本章涵盖管理后台所需的所有数据库表结构设计。

## 十九、管理后台系统

### 19.0 数据库设计

#### 19.0.0 枚举类型定义

```sql
-- 管理员角色
CREATE TYPE admin_role AS ENUM ('super_admin', 'admin', 'moderator');

-- 爬虫数据源
CREATE TYPE crawler_source AS ENUM ('github', 'gitee', 'gitlab', 'npm', 'pypi');

-- 爬虫任务状态
CREATE TYPE crawler_task_status AS ENUM ('pending', 'running', 'completed', 'failed', 'paused');

-- 爬虫日志状态
CREATE TYPE crawler_log_status AS ENUM ('success', 'failed', 'skipped');

-- 审核状态
CREATE TYPE review_status AS ENUM ('pending', 'reviewing', 'approved', 'rejected');

-- 审核优先级
CREATE TYPE review_priority AS ENUM ('low', 'normal', 'high', 'urgent');

-- 配置类型
CREATE TYPE config_type AS ENUM ('string', 'number', 'boolean', 'json');

-- 通知类型
CREATE TYPE notification_type AS ENUM ('info', 'warning', 'success', 'error');

-- 目标用户类型
CREATE TYPE target_user_type AS ENUM ('all', 'users', 'vendors', 'admins');

-- 举报目标类型
CREATE TYPE report_target_type AS ENUM ('skill', 'user', 'comment', 'review');

-- 举报原因
CREATE TYPE report_reason AS ENUM ('spam', 'inappropriate', 'copyright', 'fake', 'other');

-- 举报处理状态
CREATE TYPE report_status AS ENUM ('pending', 'investigating', 'resolved', 'dismissed');

-- 提现方式
CREATE TYPE withdrawal_method AS ENUM ('alipay', 'wechat', 'bank');

-- 提现状态
CREATE TYPE withdrawal_status AS ENUM ('pending', 'processing', 'completed', 'rejected', 'cancelled');

-- 媒体类型
CREATE TYPE media_type AS ENUM ('image', 'video');

-- 链接打开方式
CREATE TYPE link_target AS ENUM ('_self', '_blank');

-- 文章状态
CREATE TYPE article_status AS ENUM ('draft', 'pending_review', 'published', 'rejected', 'archived');

-- 内容类型
CREATE TYPE content_type AS ENUM ('text', 'html', 'markdown');

-- 富文本块类型
CREATE TYPE block_type AS ENUM ('text', 'image', 'video', 'html', 'code');

-- 友情链接分类
CREATE TYPE link_category AS ENUM ('friend', 'partner', 'sponsor', 'media');

-- 文件分类
CREATE TYPE file_category AS ENUM ('image', 'video', 'audio', 'document', 'other');

-- 存储类型
CREATE TYPE storage_type AS ENUM ('local', 'oss', 'cos', 's3');

-- 自动更新 updated_at 字段的函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

#### 19.0.1 管理员表 (admin_users)

```sql
CREATE TABLE admin_users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role admin_role NOT NULL DEFAULT 'moderator',
    permissions JSONB,
    last_login_at TIMESTAMPTZ,
    last_login_ip VARCHAR(45),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admin_users_role ON admin_users(role);
CREATE INDEX idx_admin_users_is_active ON admin_users(is_active);

CREATE TRIGGER update_admin_users_updated_at
    BEFORE UPDATE ON admin_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE admin_users IS '管理员用户表';
COMMENT ON COLUMN admin_users.username IS '管理员用户名';
COMMENT ON COLUMN admin_users.email IS '邮箱';
COMMENT ON COLUMN admin_users.password_hash IS '密码哈希';
COMMENT ON COLUMN admin_users.role IS '角色';
COMMENT ON COLUMN admin_users.permissions IS '权限列表';
COMMENT ON COLUMN admin_users.last_login_at IS '最后登录时间';
COMMENT ON COLUMN admin_users.last_login_ip IS '最后登录IP';
COMMENT ON COLUMN admin_users.is_active IS '是否激活';
```

#### 19.0.2 爬虫任务表 (crawler_tasks)

```sql
CREATE TABLE crawler_tasks (
    id BIGSERIAL PRIMARY KEY,
    task_name VARCHAR(100) NOT NULL,
    source crawler_source NOT NULL,
    keywords JSONB,
    status crawler_task_status NOT NULL DEFAULT 'pending',
    total_count INT DEFAULT 0,
    success_count INT DEFAULT 0,
    failed_count INT DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    config JSONB,
    created_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_crawler_tasks_created_by FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL
);

CREATE INDEX idx_crawler_tasks_source ON crawler_tasks(source);
CREATE INDEX idx_crawler_tasks_status ON crawler_tasks(status);
CREATE INDEX idx_crawler_tasks_created_at ON crawler_tasks(created_at);

CREATE TRIGGER update_crawler_tasks_updated_at
    BEFORE UPDATE ON crawler_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE crawler_tasks IS '爬虫任务表';
COMMENT ON COLUMN crawler_tasks.task_name IS '任务名称';
COMMENT ON COLUMN crawler_tasks.source IS '数据源';
COMMENT ON COLUMN crawler_tasks.keywords IS '搜索关键词列表';
COMMENT ON COLUMN crawler_tasks.status IS '状态';
COMMENT ON COLUMN crawler_tasks.total_count IS '总数';
COMMENT ON COLUMN crawler_tasks.success_count IS '成功数';
COMMENT ON COLUMN crawler_tasks.failed_count IS '失败数';
COMMENT ON COLUMN crawler_tasks.started_at IS '开始时间';
COMMENT ON COLUMN crawler_tasks.completed_at IS '完成时间';
COMMENT ON COLUMN crawler_tasks.error_message IS '错误信息';
COMMENT ON COLUMN crawler_tasks.config IS '爬虫配置';
COMMENT ON COLUMN crawler_tasks.created_by IS '创建人ID';
```

#### 19.0.3 爬虫日志表 (crawler_logs)

```sql
CREATE TABLE crawler_logs (
    id BIGSERIAL PRIMARY KEY,
    task_id BIGINT NOT NULL,
    source_url VARCHAR(500),
    source_id VARCHAR(100),
    status crawler_log_status NOT NULL,
    skill_id BIGINT,
    error_message TEXT,
    processing_time INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_crawler_logs_task_id FOREIGN KEY (task_id) REFERENCES crawler_tasks(id) ON DELETE CASCADE,
    CONSTRAINT fk_crawler_logs_skill_id FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL
);

CREATE INDEX idx_crawler_logs_task_id ON crawler_logs(task_id);
CREATE INDEX idx_crawler_logs_status ON crawler_logs(status);
CREATE INDEX idx_crawler_logs_created_at ON crawler_logs(created_at);

COMMENT ON TABLE crawler_logs IS '爬虫日志表';
COMMENT ON COLUMN crawler_logs.task_id IS '任务ID';
COMMENT ON COLUMN crawler_logs.source_url IS '来源URL';
COMMENT ON COLUMN crawler_logs.source_id IS '源平台ID';
COMMENT ON COLUMN crawler_logs.status IS '状态';
COMMENT ON COLUMN crawler_logs.skill_id IS '创建的Skill ID';
COMMENT ON COLUMN crawler_logs.error_message IS '错误信息';
COMMENT ON COLUMN crawler_logs.processing_time IS '处理耗时(毫秒)';
```

#### 19.0.4 审核队列表 (review_queues)

```sql
-- 注意: 审核队列表使用 05-ai-review.md 中定义的 review_queues
-- 该表包含完整的 AI 审核流程支持，包括:
--   - 多阶段审核 (L1自动, L2 AI, L3人工)
--   - 审核优先级管理
--   - AI 审核结果记录
--   - 人工审核备注

-- 主要字段:
--   - id: 主键
--   - skill_id: Skill ID
--   - submitter_id: 提交人 ID (引用 users 表)
--   - reviewer_id: 审核人 ID (引用 admin_users 表)
--   - stage: 审核阶段 (l1_auto, l2_ai, l3_manual, completed, rejected)
--   - status: 状态 (pending, reviewing, approved, rejected, appealed)
--   - priority: 优先级 (low, normal, high, urgent)
--   - ai_confidence: AI 置信度
--   - ai_scores: AI 评分详情 (JSONB)

-- 详细定义请参考: 05-ai-review.md 第 5.0.2 节
```

#### 19.0.5 平台配置表 (platform_config)

```sql
CREATE TABLE platform_config (
    id BIGSERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    config_type config_type NOT NULL DEFAULT 'json',
    category VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    is_encrypted BOOLEAN NOT NULL DEFAULT FALSE,
    updated_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_platform_config_updated_by FOREIGN KEY (updated_by) REFERENCES admin_users(id) ON DELETE SET NULL
);

CREATE INDEX idx_platform_config_category ON platform_config(category);
CREATE INDEX idx_platform_config_is_public ON platform_config(is_public);

CREATE TRIGGER update_platform_config_updated_at
    BEFORE UPDATE ON platform_config
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE platform_config IS '平台配置表';
COMMENT ON COLUMN platform_config.config_key IS '配置键';
COMMENT ON COLUMN platform_config.config_value IS '配置值(JSON)';
COMMENT ON COLUMN platform_config.config_type IS '配置类型';
COMMENT ON COLUMN platform_config.category IS '配置分类';
COMMENT ON COLUMN platform_config.description IS '配置描述';
COMMENT ON COLUMN platform_config.is_public IS '是否公开(前端可访问)';
COMMENT ON COLUMN platform_config.is_encrypted IS '是否加密存储';
COMMENT ON COLUMN platform_config.updated_by IS '更新人ID';

-- 初始配置数据
INSERT INTO platform_config (config_key, config_value, config_type, category, description, is_public) VALUES
('site.name', '"SillyMD Skills"', 'string', 'basic', '站点名称', TRUE),
('site.url', '"https://sillymd.com"', 'string', 'basic', '站点URL', TRUE),
('site.support_email', '"support@sillymd.com"', 'string', 'basic', '支持邮箱', TRUE),
('transaction.fee_rate', '0.15', 'number', 'transaction', '平台手续费率(0-1)', FALSE),
('transaction.min_withdrawal', '500', 'number', 'transaction', '最低提现金额(积分)', FALSE),
('transaction.exchange_rate', '10', 'number', 'transaction', '汇率(100积分=多少元)', FALSE),
('review.difficulty', '"medium"', 'string', 'review', '审核难度(easy/medium/hard)', FALSE),
('review.auto_publish_enabled', 'true', 'boolean', 'review', '是否启用自动发布', FALSE),
('review.auto_publish_min_stars', '3', 'number', 'review', '自动发布最低星数', FALSE),
('content.allow_public_registration', 'true', 'boolean', 'content', '是否允许公开注册', TRUE),
('content.require_email_verification', 'true', 'boolean', 'content', '是否需要邮箱验证', TRUE),
('crawling.enabled', 'true', 'boolean', 'crawling', '是否启用爬虫', FALSE),
('crawling.max_daily_imports', '50', 'number', 'crawling', '每日最大导入数', FALSE),
('crawling.import_interval', '600', 'number', 'crawling', '导入间隔(秒)', FALSE);
```

#### 19.0.6 管理员操作日志表 (admin_logs)

```sql
CREATE TABLE admin_logs (
    id BIGSERIAL PRIMARY KEY,
    admin_id BIGINT NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id BIGINT,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_admin_logs_admin_id FOREIGN KEY (admin_id) REFERENCES admin_users(id)
);

CREATE INDEX idx_admin_logs_admin_id ON admin_logs(admin_id);
CREATE INDEX idx_admin_logs_action ON admin_logs(action);
CREATE INDEX idx_admin_logs_resource ON admin_logs(resource_type, resource_id);
CREATE INDEX idx_admin_logs_created_at ON admin_logs(created_at);

COMMENT ON TABLE admin_logs IS '管理员操作日志表';
COMMENT ON COLUMN admin_logs.admin_id IS '管理员ID';
COMMENT ON COLUMN admin_logs.action IS '操作类型';
COMMENT ON COLUMN admin_logs.resource_type IS '资源类型';
COMMENT ON COLUMN admin_logs.resource_id IS '资源ID';
COMMENT ON COLUMN admin_logs.details IS '操作详情';
COMMENT ON COLUMN admin_logs.ip_address IS 'IP地址';
COMMENT ON COLUMN admin_logs.user_agent IS '用户代理';
```

#### 19.0.7 系统通知表 (system_notifications)

```sql
CREATE TABLE system_notifications (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    type notification_type NOT NULL DEFAULT 'info',
    target_type target_user_type NOT NULL DEFAULT 'all',
    target_ids JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    start_at TIMESTAMPTZ,
    end_at TIMESTAMPTZ,
    created_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_system_notifications_created_by FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL
);

CREATE INDEX idx_system_notifications_type ON system_notifications(type);
CREATE INDEX idx_system_notifications_is_active ON system_notifications(is_active);
CREATE INDEX idx_system_notifications_start_at ON system_notifications(start_at);

CREATE TRIGGER update_system_notifications_updated_at
    BEFORE UPDATE ON system_notifications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE system_notifications IS '系统通知表';
COMMENT ON COLUMN system_notifications.title IS '通知标题';
COMMENT ON COLUMN system_notifications.content IS '通知内容';
COMMENT ON COLUMN system_notifications.type IS '通知类型';
COMMENT ON COLUMN system_notifications.target_type IS '目标用户类型';
COMMENT ON COLUMN system_notifications.target_ids IS '特定用户ID列表';
COMMENT ON COLUMN system_notifications.is_active IS '是否激活';
COMMENT ON COLUMN system_notifications.start_at IS '开始时间';
COMMENT ON COLUMN system_notifications.end_at IS '结束时间';
COMMENT ON COLUMN system_notifications.created_by IS '创建人ID';
```

#### 19.0.8 数据统计表 (statistics)

```sql
CREATE TABLE statistics (
    id BIGSERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value BIGINT NOT NULL,
    dimension VARCHAR(50),
    date DATE NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (metric_name, date, dimension)
);

CREATE INDEX idx_statistics_metric_name ON statistics(metric_name);
CREATE INDEX idx_statistics_date ON statistics(date);

CREATE TRIGGER update_statistics_updated_at
    BEFORE UPDATE ON statistics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE statistics IS '数据统计表';
COMMENT ON COLUMN statistics.metric_name IS '指标名称';
COMMENT ON COLUMN statistics.metric_value IS '指标值';
COMMENT ON COLUMN statistics.dimension IS '维度(如: daily, monthly)';
COMMENT ON COLUMN statistics.date IS '统计日期';
COMMENT ON COLUMN statistics.metadata IS '元数据';
```

#### 19.0.9 用户举报表 (user_reports)

```sql
CREATE TABLE user_reports (
    id BIGSERIAL PRIMARY KEY,
    reporter_id BIGINT NOT NULL,
    target_type report_target_type NOT NULL,
    target_id BIGINT NOT NULL,
    reason report_reason NOT NULL,
    description TEXT,
    status report_status NOT NULL DEFAULT 'pending',
    assigned_to BIGINT,
    admin_note TEXT,
    resolution TEXT,
    resolved_by BIGINT,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_reports_reporter_id FOREIGN KEY (reporter_id) REFERENCES users(id),
    CONSTRAINT fk_user_reports_assigned_to FOREIGN KEY (assigned_to) REFERENCES admin_users(id) ON DELETE SET NULL,
    CONSTRAINT fk_user_reports_resolved_by FOREIGN KEY (resolved_by) REFERENCES admin_users(id) ON DELETE SET NULL
);

CREATE INDEX idx_user_reports_status ON user_reports(status);
CREATE INDEX idx_user_reports_target ON user_reports(target_type, target_id);
CREATE INDEX idx_user_reports_reporter_id ON user_reports(reporter_id);
CREATE INDEX idx_user_reports_created_at ON user_reports(created_at);

CREATE TRIGGER update_user_reports_updated_at
    BEFORE UPDATE ON user_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE user_reports IS '用户举报表';
COMMENT ON COLUMN user_reports.reporter_id IS '举报人ID';
COMMENT ON COLUMN user_reports.target_type IS '举报目标类型';
COMMENT ON COLUMN user_reports.target_id IS '举报目标ID';
COMMENT ON COLUMN user_reports.reason IS '举报原因';
COMMENT ON COLUMN user_reports.description IS '详细描述';
COMMENT ON COLUMN user_reports.status IS '处理状态';
COMMENT ON COLUMN user_reports.assigned_to IS '分配给管理员ID';
COMMENT ON COLUMN user_reports.admin_note IS '管理员备注';
COMMENT ON COLUMN user_reports.resolution IS '处理结果';
COMMENT ON COLUMN user_reports.resolved_by IS '处理人ID';
COMMENT ON COLUMN user_reports.resolved_at IS '处理时间';
```

#### 19.0.10 提现申请表 (withdrawal_requests)

```sql
CREATE TABLE withdrawal_requests (
    id BIGSERIAL PRIMARY KEY,
    withdrawal_no VARCHAR(32) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL,
    amount INT NOT NULL,
    fee INT NOT NULL DEFAULT 0,
    actual_amount INT NOT NULL,
    exchange_rate NUMERIC(10,4) NOT NULL,
    cny_amount NUMERIC(10,2) NOT NULL,
    method withdrawal_method NOT NULL,
    account_info JSONB NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    status withdrawal_status NOT NULL DEFAULT 'pending',
    transaction_id VARCHAR(100),
    rejection_reason TEXT,
    admin_note TEXT,
    processed_by BIGINT,
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_withdrawal_requests_user_id FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_withdrawal_requests_processed_by FOREIGN KEY (processed_by) REFERENCES admin_users(id) ON DELETE SET NULL
);

CREATE INDEX idx_withdrawal_requests_withdrawal_no ON withdrawal_requests(withdrawal_no);
CREATE INDEX idx_withdrawal_requests_user_id ON withdrawal_requests(user_id);
CREATE INDEX idx_withdrawal_requests_status ON withdrawal_requests(status);
CREATE INDEX idx_withdrawal_requests_created_at ON withdrawal_requests(created_at);

CREATE TRIGGER update_withdrawal_requests_updated_at
    BEFORE UPDATE ON withdrawal_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE withdrawal_requests IS '提现申请表';
COMMENT ON COLUMN withdrawal_requests.user_id IS '用户ID';
COMMENT ON COLUMN withdrawal_requests.amount IS '提现金额(积分)';
COMMENT ON COLUMN withdrawal_requests.fee IS '手续费(积分)';
COMMENT ON COLUMN withdrawal_requests.actual_amount IS '实际到账(积分)';
COMMENT ON COLUMN withdrawal_requests.method IS '提现方式';
COMMENT ON COLUMN withdrawal_requests.account_info IS '账户信息';
COMMENT ON COLUMN withdrawal_requests.status IS '状态';
COMMENT ON COLUMN withdrawal_requests.transaction_id IS '交易ID';
COMMENT ON COLUMN withdrawal_requests.rejection_reason IS '驳回原因';
COMMENT ON COLUMN withdrawal_requests.processed_by IS '处理人ID';
COMMENT ON COLUMN withdrawal_requests.processed_at IS '处理时间';
```

#### 19.0.11 轮播图表 (carousels)

```sql
CREATE TABLE carousels (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    media_type media_type NOT NULL DEFAULT 'image',
    media_url VARCHAR(500) NOT NULL,
    poster_url VARCHAR(500),
    link_url VARCHAR(500),
    link_target link_target DEFAULT '_self',
    description TEXT,
    alt_text VARCHAR(200),
    position INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    start_date DATE,
    end_date DATE,
    click_count INT DEFAULT 0,
    impression_count INT DEFAULT 0,
    created_by BIGINT,
    updated_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_carousels_created_by FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL,
    CONSTRAINT fk_carousels_updated_by FOREIGN KEY (updated_by) REFERENCES admin_users(id) ON DELETE SET NULL
);

CREATE INDEX idx_carousels_is_active ON carousels(is_active);
CREATE INDEX idx_carousels_position ON carousels(position);
CREATE INDEX idx_carousels_date_range ON carousels(start_date, end_date);

CREATE TRIGGER update_carousels_updated_at
    BEFORE UPDATE ON carousels
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE carousels IS '轮播图表';
COMMENT ON COLUMN carousels.title IS '轮播图标题';
COMMENT ON COLUMN carousels.media_type IS '媒体类型';
COMMENT ON COLUMN carousels.media_url IS '媒体URL';
COMMENT ON COLUMN carousels.poster_url IS '视频封面图(仅视频)';
COMMENT ON COLUMN carousels.link_url IS '跳转链接';
COMMENT ON COLUMN carousels.link_target IS '链接打开方式';
COMMENT ON COLUMN carousels.description IS '描述文字';
COMMENT ON COLUMN carousels.alt_text IS '替代文本(图片)';
COMMENT ON COLUMN carousels.position IS '排序位置(数字越小越靠前)';
COMMENT ON COLUMN carousels.is_active IS '是否启用';
COMMENT ON COLUMN carousels.start_date IS '展示开始日期';
COMMENT ON COLUMN carousels.end_date IS '展示结束日期';
COMMENT ON COLUMN carousels.click_count IS '点击次数';
COMMENT ON COLUMN carousels.impression_count IS '展示次数';
COMMENT ON COLUMN carousels.created_by IS '创建人ID';
COMMENT ON COLUMN carousels.updated_by IS '更新人ID';
```

#### 19.0.12 文章分类表 (article_categories)

```sql
CREATE TABLE article_categories (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id BIGINT,
    icon VARCHAR(200),
    cover_image VARCHAR(500),
    sort_order INT DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    seo_title VARCHAR(200),
    seo_description VARCHAR(500),
    seo_keywords VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_article_categories_parent_id FOREIGN KEY (parent_id) REFERENCES article_categories(id) ON DELETE SET NULL
);

CREATE INDEX idx_article_categories_parent_id ON article_categories(parent_id);
CREATE INDEX idx_article_categories_slug ON article_categories(slug);
CREATE INDEX idx_article_categories_is_active ON article_categories(is_active);
CREATE INDEX idx_article_categories_sort_order ON article_categories(sort_order);

CREATE TRIGGER update_article_categories_updated_at
    BEFORE UPDATE ON article_categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE article_categories IS '文章分类表';
COMMENT ON COLUMN article_categories.name IS '分类名称';
COMMENT ON COLUMN article_categories.slug IS 'URL别名';
COMMENT ON COLUMN article_categories.description IS '分类描述';
COMMENT ON COLUMN article_categories.parent_id IS '父分类ID';
COMMENT ON COLUMN article_categories.icon IS '分类图标URL';
COMMENT ON COLUMN article_categories.cover_image IS '分类封面图';
COMMENT ON COLUMN article_categories.sort_order IS '排序';
COMMENT ON COLUMN article_categories.is_active IS '是否启用';
```

#### 19.0.13 文章表 (articles)

```sql
CREATE TABLE articles (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    summary VARCHAR(500),
    content TEXT NOT NULL,
    cover_image VARCHAR(500),
    category_id BIGINT,
    author_id BIGINT,
    author_name VARCHAR(100),
    status article_status NOT NULL DEFAULT 'draft',
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    is_top BOOLEAN NOT NULL DEFAULT FALSE,
    is_hot BOOLEAN NOT NULL DEFAULT FALSE,
    allow_comment BOOLEAN NOT NULL DEFAULT TRUE,
    view_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    share_count INT DEFAULT 0,
    published_at TIMESTAMPTZ,
    reject_reason TEXT,
    reviewed_by BIGINT,
    reviewed_at TIMESTAMPTZ,
    seo_title VARCHAR(200),
    seo_description VARCHAR(500),
    seo_keywords VARCHAR(500),
    template VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_articles_category_id FOREIGN KEY (category_id) REFERENCES article_categories(id) ON DELETE SET NULL,
    CONSTRAINT fk_articles_author_id FOREIGN KEY (author_id) REFERENCES admin_users(id) ON DELETE SET NULL,
    CONSTRAINT fk_articles_reviewed_by FOREIGN KEY (reviewed_by) REFERENCES admin_users(id) ON DELETE SET NULL
);

CREATE INDEX idx_articles_category_id ON articles(category_id);
CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_slug ON articles(slug);
CREATE INDEX idx_articles_published_at ON articles(published_at);
CREATE INDEX idx_articles_is_featured ON articles(is_featured);
CREATE INDEX idx_articles_is_top ON articles(is_top);
CREATE INDEX idx_articles_view_count ON articles(view_count);

-- Full-text search using PostgreSQL's built-in full-text search
CREATE INDEX idx_articles_title_content_fts ON articles USING gin(to_tsvector('english', title || ' ' || content));

CREATE TRIGGER update_articles_updated_at
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE articles IS '文章表';
COMMENT ON COLUMN articles.title IS '文章标题';
COMMENT ON COLUMN articles.slug IS 'URL别名';
COMMENT ON COLUMN articles.summary IS '文章摘要';
COMMENT ON COLUMN articles.content IS '文章内容(富文本HTML)';
COMMENT ON COLUMN articles.cover_image IS '封面图片';
COMMENT ON COLUMN articles.category_id IS '分类ID';
COMMENT ON COLUMN articles.author_id IS '作者ID(管理员)';
COMMENT ON COLUMN articles.author_name IS '作者名称(显示用)';
COMMENT ON COLUMN articles.status IS '状态';
COMMENT ON COLUMN articles.is_featured IS '是否精选';
COMMENT ON COLUMN articles.is_top IS '是否置顶';
COMMENT ON COLUMN articles.is_hot IS '是否热门';
COMMENT ON COLUMN articles.allow_comment IS '是否允许评论';
COMMENT ON COLUMN articles.view_count IS '浏览次数';
COMMENT ON COLUMN articles.like_count IS '点赞次数';
COMMENT ON COLUMN articles.comment_count IS '评论次数';
COMMENT ON COLUMN articles.share_count IS '分享次数';
COMMENT ON COLUMN articles.published_at IS '发布时间';
COMMENT ON COLUMN articles.reject_reason IS '驳回原因';
COMMENT ON COLUMN articles.reviewed_by IS '审核人ID';
COMMENT ON COLUMN articles.reviewed_at IS '审核时间';
```

#### 19.0.14 文章标签表 (article_tags)

```sql
CREATE TABLE article_tags (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(20),
    description VARCHAR(200),
    article_count INT DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_article_tags_slug ON article_tags(slug);
CREATE INDEX idx_article_tags_article_count ON article_tags(article_count);

COMMENT ON TABLE article_tags IS '文章标签表';
COMMENT ON COLUMN article_tags.name IS '标签名称';
COMMENT ON COLUMN article_tags.slug IS 'URL别名';
COMMENT ON COLUMN article_tags.color IS '标签颜色';
COMMENT ON COLUMN article_tags.description IS '标签描述';
COMMENT ON COLUMN article_tags.article_count IS '文章数量';
```

#### 19.0.15 文章标签关联表 (article_tag_relations)

```sql
CREATE TABLE article_tag_relations (
    id BIGSERIAL PRIMARY KEY,
    article_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (article_id, tag_id),
    CONSTRAINT fk_article_tag_relations_article_id FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    CONSTRAINT fk_article_tag_relations_tag_id FOREIGN KEY (tag_id) REFERENCES article_tags(id) ON DELETE CASCADE
);

CREATE INDEX idx_article_tag_relations_article_id ON article_tag_relations(article_id);
CREATE INDEX idx_article_tag_relations_tag_id ON article_tag_relations(tag_id);

COMMENT ON TABLE article_tag_relations IS '文章标签关联表';
COMMENT ON COLUMN article_tag_relations.article_id IS '文章ID';
COMMENT ON COLUMN article_tag_relations.tag_id IS '标签ID';
```

#### 19.0.16 页面内容表 (page_contents)

```sql
CREATE TABLE page_contents (
    id BIGSERIAL PRIMARY KEY,
    page_key VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    content_type content_type NOT NULL DEFAULT 'html',
    section_name VARCHAR(100),
    page VARCHAR(100),
    template_vars JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by BIGINT,
    updated_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_page_contents_created_by FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL,
    CONSTRAINT fk_page_contents_updated_by FOREIGN KEY (updated_by) REFERENCES admin_users(id) ON DELETE SET NULL
);

CREATE INDEX idx_page_contents_page_key ON page_contents(page_key);
CREATE INDEX idx_page_contents_page ON page_contents(page);
CREATE INDEX idx_page_contents_is_active ON page_contents(is_active);

CREATE TRIGGER update_page_contents_updated_at
    BEFORE UPDATE ON page_contents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE page_contents IS '页面内容表';
COMMENT ON COLUMN page_contents.page_key IS '页面标识(如: home_about, contact_info)';
COMMENT ON COLUMN page_contents.title IS '内容标题';
COMMENT ON COLUMN page_contents.content IS '内容(富文本HTML)';
COMMENT ON COLUMN page_contents.content_type IS '内容类型';
COMMENT ON COLUMN page_contents.section_name IS '区块名称';
COMMENT ON COLUMN page_contents.page IS '所属页面';
COMMENT ON COLUMN page_contents.template_vars IS '模板变量';
COMMENT ON COLUMN page_contents.is_active IS '是否启用';
COMMENT ON COLUMN page_contents.created_by IS '创建人ID';
COMMENT ON COLUMN page_contents.updated_by IS '更新人ID';
```

#### 19.0.17 富文本块表 (content_blocks)

```sql
CREATE TABLE content_blocks (
    id BIGSERIAL PRIMARY KEY,
    block_key VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(200),
    content TEXT,
    block_type block_type NOT NULL DEFAULT 'text',
    media_url VARCHAR(500),
    link_url VARCHAR(500),
    button_text VARCHAR(100),
    style_config JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_by BIGINT,
    updated_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_content_blocks_created_by FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL,
    CONSTRAINT fk_content_blocks_updated_by FOREIGN KEY (updated_by) REFERENCES admin_users(id) ON DELETE SET NULL
);

CREATE INDEX idx_content_blocks_block_key ON content_blocks(block_key);
CREATE INDEX idx_content_blocks_block_type ON content_blocks(block_type);
CREATE INDEX idx_content_blocks_is_active ON content_blocks(is_active);
CREATE INDEX idx_content_blocks_sort_order ON content_blocks(sort_order);

CREATE TRIGGER update_content_blocks_updated_at
    BEFORE UPDATE ON content_blocks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE content_blocks IS '富文本块表';
COMMENT ON COLUMN content_blocks.block_key IS '区块标识';
COMMENT ON COLUMN content_blocks.title IS '区块标题';
COMMENT ON COLUMN content_blocks.content IS '区块内容(富文本)';
COMMENT ON COLUMN content_blocks.block_type IS '区块类型';
COMMENT ON COLUMN content_blocks.media_url IS '媒体URL';
COMMENT ON COLUMN content_blocks.link_url IS '链接URL';
COMMENT ON COLUMN content_blocks.button_text IS '按钮文字';
COMMENT ON COLUMN content_blocks.style_config IS '样式配置';
COMMENT ON COLUMN content_blocks.is_active IS '是否启用';
COMMENT ON COLUMN content_blocks.sort_order IS '排序';
COMMENT ON COLUMN content_blocks.created_by IS '创建人ID';
COMMENT ON COLUMN content_blocks.updated_by IS '更新人ID';
```

#### 19.0.18 友情链接表 (friendly_links)

```sql
CREATE TABLE friendly_links (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    url VARCHAR(500) NOT NULL,
    logo_url VARCHAR(500),
    description VARCHAR(200),
    category link_category NOT NULL DEFAULT 'friend',
    target link_target DEFAULT '_blank',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    click_count INT DEFAULT 0,
    contact_email VARCHAR(100),
    created_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_friendly_links_created_by FOREIGN KEY (created_by) REFERENCES admin_users(id) ON DELETE SET NULL
);

CREATE INDEX idx_friendly_links_category ON friendly_links(category);
CREATE INDEX idx_friendly_links_is_active ON friendly_links(is_active);
CREATE INDEX idx_friendly_links_sort_order ON friendly_links(sort_order);

CREATE TRIGGER update_friendly_links_updated_at
    BEFORE UPDATE ON friendly_links
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE friendly_links IS '友情链接表';
COMMENT ON COLUMN friendly_links.title IS '链接标题';
COMMENT ON COLUMN friendly_links.url IS '链接URL';
COMMENT ON COLUMN friendly_links.logo_url IS 'Logo图片';
COMMENT ON COLUMN friendly_links.description IS '链接描述';
COMMENT ON COLUMN friendly_links.category IS '链接分类';
COMMENT ON COLUMN friendly_links.target IS '打开方式';
COMMENT ON COLUMN friendly_links.is_active IS '是否启用';
COMMENT ON COLUMN friendly_links.sort_order IS '排序';
COMMENT ON COLUMN friendly_links.click_count IS '点击次数';
COMMENT ON COLUMN friendly_links.contact_email IS '联系邮箱';
COMMENT ON COLUMN friendly_links.created_by IS '创建人ID';
```

#### 19.0.19 文件管理表 (media_files)

```sql
CREATE TABLE media_files (
    id BIGSERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_extension VARCHAR(20) NOT NULL,
    file_size BIGINT NOT NULL,
    file_category file_category NOT NULL,
    width INT,
    height INT,
    duration INT,
    thumbnail_url VARCHAR(500),
    storage_type storage_type NOT NULL DEFAULT 'local',
    bucket VARCHAR(100),
    extra_info JSONB,
    upload_by BIGINT,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_media_files_upload_by FOREIGN KEY (upload_by) REFERENCES admin_users(id) ON DELETE SET NULL
);

CREATE INDEX idx_media_files_file_category ON media_files(file_category);
CREATE INDEX idx_media_files_upload_by ON media_files(upload_by);
CREATE INDEX idx_media_files_is_used ON media_files(is_used);
CREATE INDEX idx_media_files_created_at ON media_files(created_at);

COMMENT ON TABLE media_files IS '文件管理表';
COMMENT ON COLUMN media_files.file_name IS '文件名';
COMMENT ON COLUMN media_files.original_name IS '原始文件名';
COMMENT ON COLUMN media_files.file_path IS '文件路径';
COMMENT ON COLUMN media_files.file_url IS '文件URL';
COMMENT ON COLUMN media_files.file_type IS 'MIME类型';
COMMENT ON COLUMN media_files.file_extension IS '文件扩展名';
COMMENT ON COLUMN media_files.file_size IS '文件大小(字节)';
COMMENT ON COLUMN media_files.file_category IS '文件分类';
COMMENT ON COLUMN media_files.width IS '图片/视频宽度';
COMMENT ON COLUMN media_files.height IS '图片/视频高度';
COMMENT ON COLUMN media_files.duration IS '视频/音频时长(秒)';
COMMENT ON COLUMN media_files.thumbnail_url IS '缩略图URL';
COMMENT ON COLUMN media_files.storage_type IS '存储类型';
COMMENT ON COLUMN media_files.bucket IS '存储桶名';
COMMENT ON COLUMN media_files.extra_info IS '额外信息';
COMMENT ON COLUMN media_files.upload_by IS '上传人ID';
COMMENT ON COLUMN media_files.is_used IS '是否已使用';
COMMENT ON COLUMN media_files.usage_count IS '使用次数';
```

#### 19.0.20 数据表关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        管理后台数据库关系图                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐         ┌──────────────────┐                      │
│  │   admin_users    │────────>│   admin_logs     │                      │
│  │                  │         │                  │                      │
│  │ - id             │         │ - admin_id       │                      │
│  │ - username       │         │ - action         │                      │
│  │ - role           │         └──────────────────┘                      │
│  │ - permissions    │                                                  │
│  └────────┬─────────┘                                                          │
│           │                                                                  │
│           │    ┌──────────────────┐    ┌──────────────────┐                 │
│           ├───>│  crawler_tasks   │    │   carousels      │                 │
│           │    │                  │    │                  │                 │
│           │    │ - created_by     │    │ - created_by     │                 │
│           │    └──────┬───────────┘    │ - updated_by     │                 │
│           │           │                 └──────────────────┘                 │
│           │           v                                                            │
│           │    ┌──────────────┐                                                │
│           │    │crawler_logs  │                                                │
│           │    │              │                                                │
│           │    │ - task_id    │                                                │
│           │    │ - skill_id   │─────┐                                          │
│           │    └──────────────┘     │                                          │
│           │                          v                                          │
│           │    ┌──────────────┐  ┌──────────────┐                             │
│           │    │review_queue  │  │   skills     │                             │
│           │    │              │──│              │                             │
│           │    │ - skill_id   │  │ - id         │                             │
│           │    │ - assigned_to│  └──────────────┘                             │
│           │    │ - reviewed_by│                                                 │
│           │    └──────────────────┘                                            │
│           │                                                                   │
│           │    ┌──────────────────┐    ┌──────────────────┐                  │
│           │    │  articles        │    │ page_contents    │                  │
│           │    │                  │    │                  │                  │
│           │    │ - author_id      │    │ - created_by     │                  │
│           │    │ - reviewed_by    │    │ - updated_by     │                  │
│           │    │ - category_id    │    └──────────────────┘                  │
│           │    └──────┬───────────┘                                                │
│           │           │                                                              │
│           │           v                                                              │
│           │    ┌──────────────────────┐                                            │
│           │    │ article_categories   │                                            │
│           │    │                      │                                            │
│           │    │ - parent_id          │                                            │
│           │    └──────────────────────┘                                            │
│           │                                                                   │
│           │    ┌──────────────────────┐    ┌──────────────────┐               │
│           │    │ article_tags         │<──>| article_tag_relations│             │
│           │    │                      │    │                  │               │
│           │    └──────────────────────┘    │ - article_id     │               │
│           │                                  │ - tag_id         │               │
│           │                                  └──────────────────┘               │
│           │                                                                   │
│           │    ┌──────────────────┐    ┌──────────────────┐                  │
│           │    │ content_blocks   │    │ media_files      │                  │
│           │    │                  │    │                  │                  │
│           │    │ - created_by     │    │ - upload_by      │                  │
│           │    │ - updated_by     │    └──────────────────┘                  │
│           │    └──────────────────┘                                           │
│           │                                                                   │
│           │    ┌──────────────────┐    ┌──────────────────┐                  │
│           │    │friendly_links    │    │system_notifications│                │
│           │    │                  │    │                  │                  │
│           │    │ - created_by     │    │ - created_by     │                  │
│           │    └──────────────────┘    └──────────────────┘                  │
│           │                                                                   │
│           v                                                                   │
│  ┌──────────────────┐    ┌──────────────────┐                               │
│  │ platform_config  │    │ system_notifications                             │
│  │                  │    │                  │                               │
│  │ - updated_by     │    └──────────────────┘                               │
│  └──────────────────┘                                                       │
│                                                                             │
│  ┌──────────────────┐    ┌──────────────────┐                              │
│  │ user_reports     │    │withdrawal_requests│                             │
│  │                  │    │                  │                              │
│  │ - assigned_to    │    │ - processed_by   │                              │
│  │ - resolved_by    │    └──────────────────┘                              │
│  └──────────────────┘                                                        │
│                                                                             │
│  ┌──────────────┐                                                          │
│  │ statistics   │                                                          │
│  │              │                                                          │
│  └──────────────┘                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 19.0.21 初始化管理员账户

```sql
-- 创建超级管理员
INSERT INTO admin_users (username, email, password_hash, role, is_active) VALUES
('admin', 'admin@sillymd.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7xIXU2bq4i', 'super_admin', TRUE);

-- 密码是: admin123 (实际部署时需要修改)
```

---



### 19.1 后台首页

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    管理后台                                 │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  📊 数据概览                                        │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  实时统计                                             │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────┐ │  │
│  │  │            │ │            │ │            │ │        │ │  │
│  │  │  总用户数   │ │  总Skills  │ │  待审核   │ │ 今日   │ │  │
│  │  │   12,345   │ │    5,678   │ │   23      │ │ 新增   │ │  │
│  │  │            │ │            │ │            │ │        │ │  │
│  │  │  +156 今日 │ │  +89 今日 │ │  ↓ 45%    │ │ +12.5% │ │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  快捷操作                                             │  │
│  │  [ 审核 Skills ]  [ 管理用户 ]  [ 系统设置 ]              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  待办事项                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ ⚠️   Skills 待审核：23                              │  │  │
│  │  │ ⚠️  用户举报：5                                     │  │  │
│  │  │ ⚠️  提现申请：2                                     │  │  │  │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  数据趋势图表                                         │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  用户增长曲线 (近30天)                               │  │  │
│  │  │  ╭───────────────────────────────────────╮          │  │  │
│  │  │  │    ╭──────╮──────╮──────╮──────╮          │  │ │
│  │  │    │     │      │      │      │          │  │ │ │
│  │  │    │ 12k  │ 12k  │ 11k  │ 11k  │          │  │ │ │
│  │  │    └──────┴──────┴──────┴──────┴          │  │ │ │
│  │  └─────────────────────────────────────────────────────┘  │  │ │  │ │
│  │  └─────────────────────────────────────────────────────┘  │  │ │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 19.2 自动爬虫系统

#### 19.2.1 爬虫架构

```python
# ============================================
# 自动爬虫系统
# ============================================

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import random

class SkillCrawler:
    """Skills 自动爬虫"""

    def __init__(self):
        self.sources = [
            'github.com',
            'gitee.com',
            'gitlab.com',
            'npmjs.com',
            'pypi.org'
        ]
        self.ai_reviewer = AIReviewService()

    async def search_skills(self, keywords: List[str]) -> List[dict]:
        """搜索潜在的 Skills"""
        skills_found = []

        for keyword in keywords:
            # GitHub 搜索
            github_skills = await self.search_github(keyword)
            skills_found.extend(github_skills)

            # NPM 搜索
            npm_skills = await self.search_npm(keyword)
            skills_found.extend(npm_skills)

            # PyPI 搜索
            pypi_skills = await self.search_pypi(keyword)
            skills_found.extend(pypi_skills)

        return skills_found

    async def search_github(self, keyword: str) -> List[dict]:
        """搜索 GitHub 仓库"""
        url = f"https://api.github.com/search/repositories?q={keyword}+language:python"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return self.parse_github_repo(data)
        return []

    def parse_github_repo(self, data: dict) -> List[dict]:
        """解析 GitHub 仓库信息为 Skill"""
        skills = []

        for item in data.get('items', [])[:10]:  # 限制数量
            if item.get('stargazers', 0) >= 50:  # 只爬取热门项目
                skill = {
                    'name': item['name'],
                    'description': item['description'],
                    'category': self.guess_category(item),
                    'url': item['html_url'],
                    'stars': item['stargazers'],
                    'language': item['language'],
                    'source': 'github'
                }
                skills.append(skill)

        return skills

    def guess_category(self, repo: dict) -> str:
        """根据仓库信息猜测分类"""
        topics = repo.get('topics', [])
        language = repo.get('language', '').lower()

        # 基于语言和主题猜测
        if language in ['python', 'javascript', 'java', 'go']:
            return 'tech'
        elif any(t in topics for t in ['design', 'ui', 'ux', 'frontend']):
            return 'design'
        elif any(t in topics for t in ['blog', 'cms', 'ecommerce']):
            return 'tech'
        elif any(t in topics for t in ['marketing', 'seo', 'analytics']):
            return 'marketing'
        else:
            return 'tech'

    async def process_and_create_skill(self, raw_skill: dict) -> dict:
        """处理并创建 Skill（自动流程）"""
        # 1. 清洗数据
        cleaned_skill = self.clean_skill_data(raw_skill)

        # 2. 生成随机假人身份
        fake_user = await self.generate_fake_user()

        # 3. 发送 AI 审核
        review_result = await self.ai_reviewer.review(cleaned_skill)

        # 4. 根据审核结果处理
        if review_result.approved:
            # 创建 Skill
            skill = await db.skills.create({
                **cleaned_skill,
                author_id: fake_user.id,
                status: 'approved',
                published_at: datetime.utcnow(),
                content_hash: self.generate_hash(cleaned_skill),
                platform_signature: self.sign_skill(cleaned_skill)
            })
            return skill
        else:
            # 进入待审核队列
            skill = await db.skills.create({
                **cleaned_skill,
                author_id: fake_user.id,
                status: 'reviewing'
            })
            return skill

    async def generate_fake_user(self) -> dict:
        """生成随机假人用户"""
        fake = self.fake.user()

        # 随机生成用户数据，避免重复
        username = f"{fake.first_name}{random.randint(1000, 9999)}"

        # 检查用户名是否存在，存在则重新生成
        while await db.users.find_by_username(username):
            username = f"{fake.first_name}{random.randint(1000, 9999)}"

        user = await db.users.create({
            username: username,
            email: f"{username}@temp-sillymd.com",
            password_hash = self.hash_password('default_password_123'),
            role: 'user',
            vendor_level: 'normal',
            is_active: True,
            is_verified: True,
            created_at: datetime.utcnow(),
            updated_at: datetime.utcnow()
        })

        return user

    async def run_crawler(self):
        """运行爬虫任务"""
        # 获取搜索关键词
        keywords = await self.get_trending_keywords()

        # 搜索 Skills
        skills = await self.search_skills(keywords)

        # 处理并创建
        for skill_data in skills:
            try:
                await self.process_and_create_skill(skill_data)
                # 随机延迟，避免操作过快
                await asyncio.sleep(random.uniform(5, 15))
            except Exception as e:
                logger.error(f"Failed to process skill: {e}")
                continue
```

#### 19.2.2 审核难度设置

```typescript
// ============================================
// 审核难度配置
// ============================================

interface ReviewDifficultyConfig {
  level: 'easy' | 'medium' | 'hard';
  autoApprovalThreshold: number; // 自动通过阈值 (0-1)
  aiModelCost: number; // AI 审核消耗的积分
  manualReviewRequired: boolean;
  randomApprovalRate: number; // 随机自动通过率 (0-1)
}

const REVIEW_DIFFICULTY_LEVELS: Record<string, ReviewDifficultyConfig> = {
  easy: {
    level: 'easy',
    autoApprovalThreshold: 0.7,  // 70% 自动通过
    aiModelCost: 1,
    manualReviewRequired: false,
    randomApprovalRate: 0.9  // 90% 随机通过
  },
  medium: {
    level: 'medium',
    autoApprovalThreshold: 0.3,  // 30% 自动通过
    aiModelCost: 3,
    manualReviewRequired: false,
    randomApprovalRate: 0.5  // 50% 随机通过
  },
  hard: {
    level: 'hard',
    autoApprovalThreshold: 0,    // 0% 自动通过
    aiModelCost: 10,
    manualReviewRequired: true, // 必须人工审核
    randomApprovalRate: 0.1  // 10% 随机通过
  }
};

// ============================================
// AI 审核控制器
// ============================================

export class AIReviewController {
  private config: ReviewDifficultyConfig;

  constructor(config: ReviewDifficultyConfig) {
    this.config = config;
  }

  async review(skill: dict): Promise<ReviewResult> {
    // 1. 基础格式检查
    const formatCheck = this.checkFormat(skill);

    // 2. 内容安全检查
    const safetyCheck = await this.checkSafety(skill);

    // 3. 专业性评估（根据难度调整）
    const qualityScore = this.assessQuality(skill);

    // 4. 综合评分
    const finalScore = (
      formatCheck.score * 0.2 +
      safetyCheck.score * 0.3 +
      qualityScore * 0.5
    );

    // 5. 根据难度决定是否自动通过
    if (finalScore >= this.config.autoApprovalThreshold) {
      // 随机决定是否真的审核（增加真实性）
      if (Math.random() < this.config.randomApprovalRate) {
        return {
          approved: true,
          reason: 'Auto-approved by system',
          confidence: finalScore
        };
      }
    }

    // 进入人工审核
    return {
      approved: false,
      reason: 'Requires manual review',
      confidence: finalScore,
      suggestions: [
        '完善文档描述',
        '添加使用示例',
        '补充技术细节'
      ]
    };
  }
}
```

#### 19.2.3 手动审核管理

```typescript
// ============================================
// 审核队列管理
// ============================================

export function ReviewQueue() {
  const [queue, setQueue] = useState<ReviewItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<ReviewItem | null>(null);

  const fetchQueue = async () => {
    const response = await api.get('/admin/review/queue');
    setQueue(response.data);
  };

  const approveItem = async (id: string, note?: string) => {
    await api.post(`/admin/review/${id}/approve`, { note });
    await fetchQueue();
  };

  const rejectItem = async (id: string, reason: string) => {
    await api.post(`/admin/review/${id}/reject`, { reason });
    await fetchQueue();
  };

  return (
    <div className="review-queue">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">审核队列</h2>
        <DifficultySelector
          value={currentDifficulty}
          onChange={(level) => setDifficulty(level)}
        />
        <div className="text-sm text-gray-600">
          待审核: {queue.length} 项
        </div>
      </div>

      {/* 审核列表 */}
      <div className="space-y-4">
        {queue.map((item) => (
          <ReviewQueueItem
            key={item.id}
            item={item}
            isSelected={selectedItem?.id === item.id}
            onSelect={setSelectedItem}
            onApprove={approveItem}
            onReject={rejectItem}
          />
        ))}
      </div>
    </div  );
}

// ============================================
// 审核项组件
// ============================================

interface ReviewQueueItemProps {
  item: ReviewItem;
  isSelected: boolean;
  onSelect: (item: ReviewItem) => void;
  onApprove: (id: string, note?: string) => void;
  onReject: (id: string, reason: string) => void;
}

function ReviewQueueItem({ item, isSelected, onSelect, onApprove, onReject }: ReviewQueueItemProps) {
  return (
    <div
      className={`
        p-6 border rounded-lg cursor-pointer transition-all
        ${isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}
      `}
      onClick={() => onSelect(item)}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-semibold">{item.skill_name}</h3>
            <span className={`px-2 py-1 text-xs rounded ${
              item.source === 'github' ? 'bg-gray-800 text-white' :
              item.source === 'npm' ? 'bg-red-600 text-white' :
              'bg-blue-600 text-white'
            }`}>
              {item.source}
            </span>
            <span className={`px-2 py-1 text-xs rounded ${
              item.category === 'tech' ? 'bg-purple-100 text-purple-800' :
              item.category === 'design' ? 'bg-pink-100 text-pink-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {item.category}
            </span>
          </div>

          <p className="text-sm text-gray-600 line-clamp-2">
            {item.description}
          </p>

          {/* AI 评估 */}
          <div className="mt-3 p-3 bg-white rounded border">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">AI 评估</span>
              <span className="text-sm text-gray-500">
                置信度: {item.confidence}%
              </span>
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">格式:</span>
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 bg-green-500 rounded-full"
                    style={{ width: `${item.scores.format * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500">{item.scores.format}%</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">安全:</span>
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 bg-green-500 rounded-full"
                    style={{ width: `${item.scores.safety * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500">{item.scores.safety}%</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">质量:</span>
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 bg-yellow-500 rounded-full"
                    style={{ width: `${item.scores.quality * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500">{item.scores.quality}%</span>
              </div>
            </div>
          </div>

          {/* 来源信息 */}
          <div className="mt-3 text-xs text-gray-500">
            来源: {item.source_url}
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="flex gap-2">
          <button
            onClick={() => onApprove(item.id)}
            className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
          >
            ✓ 通过
          </button>
          <button
            onClick={() => {
              const reason = prompt('请输入驳回原因：');
              if (reason) {
                onReject(item.id, reason);
              }
            }}
            className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
          >
            ✗ 驳回
          </button>
        </div>
      </div>
    </div>
  );
}
```

### 19.3 系统设置

#### 19.3.1 平台配置

```typescript
// ============================================
// 平台配置界面
// ============================================

interface PlatformConfig {
  basic: {
    siteName: string;
    siteUrl: string;
    supportEmail: string;
  };
  transaction: {
    platformFeeRate: number; // 0.15 - 0.20
    minWithdrawal: number; // 500 Points
    withdrawalCycle: 'weekly' | 'monthly';
    exchangeRate: number; // 100 Points = ? CNY
  };
  review: {
    difficulty: 'easy' | 'medium' | 'hard';
    autoPublishEnabled: boolean; // 是否启用自动发布
    autoPublishMinStars: number; // 自动发布最低星数
  };
  content: {
    allowPublicRegistration: boolean;
    requireEmailVerification: boolean;
    enableGuestBrowsing: boolean;
  };
  crawling: {
    enabled: boolean;
    sources: ('github' | 'gitee' | 'gitlab' | 'npm' | 'pypi')[];
    maxDailyImports: number; // 每日最大导入数
    importInterval: number; // 导入间隔(秒)
  };
}

export function PlatformSettings() {
  const [config, setConfig] = useState<PlatformConfig>({
    basic: {
      siteName: 'SillyMD Skills',
      siteUrl: 'https://sillymd.com',
      supportEmail: 'support@sillymd.com'
    },
    transaction: {
      platformFeeRate: 0.15,
      minWithdrawal: 500,
      withdrawalCycle: 'weekly',
      exchangeRate: 10
    },
    review: {
      difficulty: 'medium',
      autoPublishEnabled: true,
      autoPublishMinStars: 3
    },
    content: {
      allowPublicRegistration: true,
      requireEmailVerification: true,
      enableGuestBrowsing: true
    },
    crawling: {
      enabled: true,
      sources: ['github', 'gitee', 'npm', 'pypi'],
      maxDailyImports: 50,
      importInterval: 600
    }
  });

  const handleSaveConfig = async () => {
    await api.put('/admin/config', config);
    toast.success('配置已保存');
  };

  return (
    <div className="platform-settings space-y-6">
      <h1 className="text-2xl font-bold">平台设置</h1>

      {/* 基础设置 */}
      <SettingsSection title="基础设置">
        <FormField label="站点名称">
          <input
            type="text"
            value={config.basic.siteName}
            onChange={(e) => setConfig({
              ...config,
              basic: { ...config.basic, siteName: e.target.value }
            })}
          />
        </FormField>
        <FormField label="支持邮箱">
          <input
            type="email"
            value={config.basic.supportEmail}
            onChange={(e) => setConfig({
              ...config,
              basic: { ...config.basic, supportEmail: e.target.value }
            })}
          />
        </FormField>
      </SettingsSection>

      {/* 交易设置 */}
      <SettingsSection title="交易设置">
        <div className="grid grid-cols-2 gap-4">
          <FormField label="平台手续费率 (%)">
            <input
              type="number"
              min="0"
              max="100"
              step="1"
              value={config.transaction.platformFeeRate * 100}
              onChange={(e) => setConfig({
                ...config,
                transaction: {
                  ...config.transaction,
                  platformFeeRate: Number(e.target.value) / 100
                }
              })}
            />
          </FormField>
          <FormField label="最低提现金额">
            <input
              type="number"
              min="0"
              value={config.transaction.minWithdrawal}
              onChange={(e) => setConfig({
                ...config,
                transaction: {
                  ...config.transaction,
                  minWithdrawal: Number(e.target.value)
                }
              })}
            />
          </FormField>
          <FormField label="汇率 (100 Points = ? 元)">
            <input
              type="number"
              min="0"
              value={config.transaction.exchangeRate}
              onChange={(e) => setConfig({
                ...config,
                transaction: {
                  ...config.transaction,
                  exchangeRate: Number(e.target.value)
                }
              })}
            />
          </FormField>
        </div>
      </SettingsSection>

      {/* 审核设置 */}
      <SettingsSection title="审核设置">
        <div className="grid grid-cols-2 gap-4">
          <FormField label="审核难度">
            <select
              value={config.review.difficulty}
              onChange={(e) => setConfig({
                ...config,
                review: { ...config.review, difficulty: e.target.value as 'easy' | 'medium' | 'hard' }
              })}
            >
              <option value="easy">简单（高通过率）</option>
              <option value="medium">中等（平衡）</option>
              <option value="hard">严格（需人工审核）</option>
            </select>
          </FormField>
          <FormField label="自动发布最低星数">
            <input
              type="number"
              min="1"
              max="5"
              value={config.review.autoPublishMinStars}
              onChange={(e) => setConfig({
                ...config,
                review: {
                  ...config.review,
                  autoPublishMinStars: Number(e.target.value)
                }
              })}
            />
          </FormField>
        </div>
        <div className="mt-2">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={config.review.autoPublishEnabled}
              onChange={(e) => setConfig({
                ...config,
                review: {
                  ...config.review,
                  autoPublishEnabled: e.target.checked
                }
              })}
              className="mr-2"
            />
            <span>启用自动发布（高星数自动通过）</span>
          </label>
        </div>
      </SettingsSection>

      {/* 爬虫设置 */}
      <SettingsSection title="爬虫设置">
        <div className="space-y-4">
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={config.crawling.enabled}
                onChange={(e) => setConfig({
                  ...config,
                  crawling: {
                    ...config.crawling,
                    enabled: e.target.checked
                  }
                })}
                className="mr-2"
              />
              <span>启用自动爬虫</span>
            </label>
          </div>

          {config.crawling.enabled && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <FormField label="每日最大导入数">
                  <input
                    type="number"
                    min="1"
                    max="1000"
                    value={config.crawling.maxDailyImports}
                    onChange={(e) => setConfig({
                      ...config,
                      crawling: {
                        ...config.crawling,
                        maxDailyImports: Number(e.target.value)
                      }
                    })}
                  />
                </FormField>
                <FormField label="导入间隔（秒）">
                  <input
                    type="number"
                    min="60"
                    max="3600"
                    value={config.crawling.importInterval}
                    onChange={(e) => setConfig({
                      ...config,
                      crawling: {
                        ...config.crawling,
                        importInterval: Number(e.target.value)
                      }
                    })}
                  />
                </FormField>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">数据源</label>
                <div className="space-y-2">
                  {['github', 'gitee', 'npm', 'pypi'].map((source) => (
                    <label key={source} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={config.crawling.sources.includes(source)}
                        onChange={(e) => {
                          const newSources = e.target.checked
                            ? [...config.crawling.sources, source]
                            : config.crawling.sources.filter(s => s !== source);
                          setConfig({
                            ...config,
                            crawling: {
                              ...config.crawling,
                              sources: newSources
                            }
                          });
                        }}
                        className="mr-2"
                      />
                      <span className="capitalize">{source}</span>
                    </label>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </SettingsSection>

      {/* 保存按钮 */}
      <div className="flex justify-end">
        <Button onClick={handleSaveConfig} className="px-6 py-2 bg-blue-600 text-white rounded-lg">
          保存设置
