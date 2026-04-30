# 第十八章：交流学习社区

> 本文档描述平台的社区功能，包括视频教程、文档系统和讨论区。
>
> 本章涵盖交流学习社区所需的所有数据库表结构设计。

## 18.0 数据库设计

### 18.0.1 枚举类型定义

```sql
-- ============================================
-- 社区系统枚举类型
-- ============================================

CREATE TYPE video_type AS ENUM ('tutorial', 'demo', 'presentation', 'interview', 'other');
CREATE TYPE difficulty_level AS ENUM ('beginner', 'intermediate', 'advanced');
CREATE TYPE video_status AS ENUM ('draft', 'processing', 'published', 'archived');
CREATE TYPE content_type AS ENUM ('markdown', 'html', 'plaintext');
CREATE TYPE doc_type AS ENUM ('guide', 'reference', 'tutorial', 'faq', 'announcement', 'other');
CREATE TYPE discussion_type AS ENUM ('question', 'discussion', 'idea', 'bug_report', 'feedback');
CREATE TYPE discussion_status AS ENUM ('open', 'answered', 'closed', 'archived');
CREATE TYPE job_type AS ENUM ('upload', 'transcode', 'thumbnail', 'subtitle', 'compress');
CREATE TYPE job_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
CREATE TYPE lesson_type AS ENUM ('video', 'document', 'quiz', 'assignment');
CREATE TYPE enrollment_status AS ENUM ('active', 'completed', 'dropped', 'refunded');
```

### 18.0.2 视频分类表 (video_categories)

```sql
CREATE TABLE video_categories (
    id BIGSERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    category_slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id BIGINT,
    icon VARCHAR(200),
    cover_image VARCHAR(500),
    sort_order INT DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES video_categories(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_video_categories_parent_id ON video_categories(parent_id);
CREATE INDEX idx_video_categories_slug ON video_categories(category_slug);
CREATE INDEX idx_video_categories_is_active ON video_categories(is_active);
CREATE INDEX idx_video_categories_sort_order ON video_categories(sort_order);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_video_categories_updated_at BEFORE UPDATE ON video_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 18.0.3 视频表 (videos)

```sql
CREATE TABLE videos (
    id BIGSERIAL PRIMARY KEY,
    video_title VARCHAR(200) NOT NULL,
    video_slug VARCHAR(200) UNIQUE NOT NULL,
    summary VARCHAR(500),
    description TEXT,
    category_id BIGINT,
    video_type video_type NOT NULL DEFAULT 'tutorial',
    difficulty difficulty_level NOT NULL DEFAULT 'beginner',
    thumbnail_url VARCHAR(500),
    poster_url VARCHAR(500),
    video_url VARCHAR(500) NOT NULL,
    video_duration INT,
    file_size BIGINT,
    resolution VARCHAR(20),
    format VARCHAR(20),
    subtitles JSONB,
    related_skill_id BIGINT,
    author_id BIGINT NOT NULL,
    author_name VARCHAR(100),
    view_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    share_count INT DEFAULT 0,
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    is_official BOOLEAN NOT NULL DEFAULT FALSE,
    status video_status NOT NULL DEFAULT 'draft',
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES video_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (related_skill_id) REFERENCES skills(id) ON DELETE SET NULL,
    FOREIGN KEY (author_id) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_videos_category_id ON videos(category_id);
CREATE INDEX idx_videos_video_type ON videos(video_type);
CREATE INDEX idx_videos_difficulty ON videos(difficulty);
CREATE INDEX idx_videos_related_skill_id ON videos(related_skill_id);
CREATE INDEX idx_videos_author_id ON videos(author_id);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_view_count ON videos(view_count);
CREATE INDEX idx_videos_is_featured ON videos(is_featured);

-- 全文搜索索引（需要配置中文全文搜索）
-- CREATE INDEX idx_videos_fulltext ON videos USING gin(to_tsvector('simple', video_title || ' ' || COALESCE(summary, '') || ' ' || COALESCE(description, '')));

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 18.0.4 视频处理任务表 (video_processing_jobs)

```sql
CREATE TABLE video_processing_jobs (
    id BIGSERIAL PRIMARY KEY,
    video_id BIGINT NOT NULL,
    job_type job_type NOT NULL,
    source_url VARCHAR(500),
    target_url VARCHAR(500),
    status job_status NOT NULL DEFAULT 'pending',
    progress INT DEFAULT 0,
    output_format VARCHAR(20),
    resolution VARCHAR(20),
    bitrate INT,
    file_size BIGINT,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_video_processing_jobs_video_id ON video_processing_jobs(video_id);
CREATE INDEX idx_video_processing_jobs_job_type ON video_processing_jobs(job_type);
CREATE INDEX idx_video_processing_jobs_status ON video_processing_jobs(status);
CREATE INDEX idx_video_processing_jobs_created_at ON video_processing_jobs(created_at);
```

### 18.0.5 文档分类表 (document_categories)

```sql
CREATE TABLE document_categories (
    id BIGSERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    category_slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id BIGINT,
    icon VARCHAR(200),
    cover_image VARCHAR(500),
    sort_order INT DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES document_categories(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_document_categories_parent_id ON document_categories(parent_id);
CREATE INDEX idx_document_categories_slug ON document_categories(category_slug);
CREATE INDEX idx_document_categories_is_active ON document_categories(is_active);
CREATE INDEX idx_document_categories_sort_order ON document_categories(sort_order);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_document_categories_updated_at BEFORE UPDATE ON document_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 18.0.6 文档表 (documents)

```sql
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    doc_title VARCHAR(200) NOT NULL,
    doc_slug VARCHAR(200) UNIQUE NOT NULL,
    summary VARCHAR(500),
    content TEXT NOT NULL,
    content_type content_type NOT NULL DEFAULT 'markdown',
    category_id BIGINT,
    doc_type doc_type NOT NULL DEFAULT 'guide',
    icon VARCHAR(200),
    cover_image VARCHAR(500),
    order_index INT DEFAULT 0,
    parent_doc_id BIGINT,
    related_skill_id BIGINT,
    author_id BIGINT NOT NULL,
    author_name VARCHAR(100),
    view_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    is_official BOOLEAN NOT NULL DEFAULT FALSE,
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES document_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_doc_id) REFERENCES documents(id) ON DELETE SET NULL,
    FOREIGN KEY (related_skill_id) REFERENCES skills(id) ON DELETE SET NULL,
    FOREIGN KEY (author_id) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_documents_category_id ON documents(category_id);
CREATE INDEX idx_documents_doc_type ON documents(doc_type);
CREATE INDEX idx_documents_parent_doc_id ON documents(parent_doc_id);
CREATE INDEX idx_documents_related_skill_id ON documents(related_skill_id);
CREATE INDEX idx_documents_author_id ON documents(author_id);
CREATE INDEX idx_documents_is_published ON documents(is_published);
CREATE INDEX idx_documents_order_index ON documents(order_index);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 18.0.7 讨论分类表 (discussion_categories)

```sql
CREATE TABLE discussion_categories (
    id BIGSERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    category_slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(200),
    color VARCHAR(20),
    sort_order INT DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_discussion_categories_slug ON discussion_categories(category_slug);
CREATE INDEX idx_discussion_categories_is_active ON discussion_categories(is_active);
CREATE INDEX idx_discussion_categories_sort_order ON discussion_categories(sort_order);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_discussion_categories_updated_at BEFORE UPDATE ON discussion_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 初始化讨论分类
INSERT INTO discussion_categories (category_name, category_slug, description, icon, color, sort_order) VALUES
('技术讨论', 'tech', '技术相关问题讨论', '💻', '#3B82F6', 1),
('产品交流', 'product', '产品设计与需求交流', '📦', '#10B981', 2),
('设计分享', 'design', 'UI/UX设计作品分享', '🎨', '#8B5CF6', 3),
('市场运营', 'marketing', '市场推广与运营策略', '📈', '#F59E0B', 4),
('Bug反馈', 'bugs', 'Bug 报告与问题反馈', '🐛', '#EF4444', 5),
('新手问答', 'q&a', '新手问答区', '❓', '#6366F1', 6);
```

### 18.0.8 讨论主题表 (discussions)

```sql
CREATE TABLE discussions (
    id BIGSERIAL PRIMARY KEY,
    discussion_title VARCHAR(255) NOT NULL,
    discussion_slug VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    category_id BIGINT,
    user_id BIGINT NOT NULL,
    related_skill_id BIGINT,
    related_video_id BIGINT,
    related_doc_id BIGINT,
    discussion_type discussion_type NOT NULL DEFAULT 'discussion',
    status discussion_status NOT NULL DEFAULT 'open',
    is_pinned BOOLEAN NOT NULL DEFAULT FALSE,
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    is_solved BOOLEAN NOT NULL DEFAULT FALSE,
    view_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    reply_count INT DEFAULT 0,
    follower_count INT DEFAULT 0,
    last_reply_at TIMESTAMPTZ,
    last_reply_by BIGINT,
    solved_reply_id BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES discussion_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (related_skill_id) REFERENCES skills(id) ON DELETE SET NULL,
    FOREIGN KEY (related_video_id) REFERENCES videos(id) ON DELETE SET NULL,
    FOREIGN KEY (related_doc_id) REFERENCES documents(id) ON DELETE SET NULL,
    FOREIGN KEY (last_reply_by) REFERENCES users(id),
    FOREIGN KEY (solved_reply_id) REFERENCES discussion_comments(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_discussions_category_id ON discussions(category_id);
CREATE INDEX idx_discussions_user_id ON discussions(user_id);
CREATE INDEX idx_discussions_related_skill_id ON discussions(related_skill_id);
CREATE INDEX idx_discussions_discussion_type ON discussions(discussion_type);
CREATE INDEX idx_discussions_status ON discussions(status);
CREATE INDEX idx_discussions_is_pinned ON discussions(is_pinned);
CREATE INDEX idx_discussions_last_reply_at ON discussions(last_reply_at);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_discussions_updated_at BEFORE UPDATE ON discussions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 18.0.9 讨论评论表 (discussion_comments)

```sql
CREATE TABLE discussion_comments (
    id BIGSERIAL PRIMARY KEY,
    discussion_id BIGINT NOT NULL,
    parent_id BIGINT,
    user_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    is_answer BOOLEAN NOT NULL DEFAULT FALSE,
    like_count INT DEFAULT 0,
    reply_count INT DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (discussion_id) REFERENCES discussions(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES discussion_comments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_discussion_comments_discussion_id ON discussion_comments(discussion_id);
CREATE INDEX idx_discussion_comments_parent_id ON discussion_comments(parent_id);
CREATE INDEX idx_discussion_comments_user_id ON discussion_comments(user_id);
CREATE INDEX idx_discussion_comments_is_answer ON discussion_comments(is_answer);
CREATE INDEX idx_discussion_comments_created_at ON discussion_comments(created_at);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_discussion_comments_updated_at BEFORE UPDATE ON discussion_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 18.0.10 课程分类表 (course_categories)

```sql
CREATE TABLE course_categories (
    id BIGSERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    category_slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(200),
    cover_image VARCHAR(500),
    sort_order INT DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_course_categories_slug ON course_categories(category_slug);
CREATE INDEX idx_course_categories_is_active ON course_categories(is_active);
CREATE INDEX idx_course_categories_sort_order ON course_categories(sort_order);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_course_categories_updated_at BEFORE UPDATE ON course_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 初始化课程分类
INSERT INTO course_categories (category_name, category_slug, description, icon, sort_order) VALUES
('前端开发', 'frontend', 'HTML/CSS/JavaScript 等前端技术', '🎨', 1),
('后端开发', 'backend', 'Python/Java/Go 等后端技术', '⚙️', 2),
('人工智能', 'ai', '机器学习/深度学习/AI 应用', '🤖', 3),
('数据库', 'database', 'MySQL/PostgreSQL/MongoDB 等', '🗄️', 4),
('运维部署', 'devops', 'Docker/K8s/CI/CD 等', '🔧', 5),
('设计工具', 'design', 'Figma/Sketch/Adobe 等', '🎨', 6);
```

### 18.0.11 课程表 (courses)

```sql
CREATE TABLE courses (
    id BIGSERIAL PRIMARY KEY,
    course_title VARCHAR(200) NOT NULL,
    course_slug VARCHAR(200) UNIQUE NOT NULL,
    summary VARCHAR(500),
    description TEXT,
    instructor_id BIGINT NOT NULL,
    instructor_name VARCHAR(100),
    category_id BIGINT,
    difficulty difficulty_level NOT NULL DEFAULT 'beginner',
    thumbnail_url VARCHAR(500),
    cover_image VARCHAR(500),
    promo_video_url VARCHAR(500),
    duration_minutes INT,
    lesson_count INT DEFAULT 0,
    prerequisites JSONB,
    learning_objectives JSONB,
    target_audience TEXT,
    price INT DEFAULT 0,
    enrollment_count INT DEFAULT 0,
    completion_rate NUMERIC(5,2) DEFAULT 0,
    rating_average NUMERIC(3,2) DEFAULT 0.00,
    rating_count INT DEFAULT 0,
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instructor_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES course_categories(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_courses_instructor_id ON courses(instructor_id);
CREATE INDEX idx_courses_category_id ON courses(category_id);
CREATE INDEX idx_courses_difficulty ON courses(difficulty);
CREATE INDEX idx_courses_is_published ON courses(is_published);
CREATE INDEX idx_courses_enrollment_count ON courses(enrollment_count);
CREATE INDEX idx_courses_rating_average ON courses(rating_average);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_courses_updated_at BEFORE UPDATE ON courses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 18.0.12 课程课时表 (course_lessons)

```sql
CREATE TABLE course_lessons (
    id BIGSERIAL PRIMARY KEY,
    course_id BIGINT NOT NULL,
    lesson_title VARCHAR(200) NOT NULL,
    lesson_order INT NOT NULL,
    lesson_type lesson_type NOT NULL,
    content_url VARCHAR(500),
    content_text TEXT,
    duration_minutes INT,
    is_preview BOOLEAN NOT NULL DEFAULT FALSE,
    is_free BOOLEAN NOT NULL DEFAULT FALSE,
    resources JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (course_id, lesson_order),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_course_lessons_course_id ON course_lessons(course_id);
CREATE INDEX idx_course_lessons_lesson_order ON course_lessons(lesson_order);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_course_lessons_updated_at BEFORE UPDATE ON course_lessons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 18.0.13 课程报名表 (course_enrollments)

```sql
CREATE TABLE course_enrollments (
    id BIGSERIAL PRIMARY KEY,
    course_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    enrollment_status enrollment_status NOT NULL DEFAULT 'active',
    progress_percent INT DEFAULT 0,
    last_lesson_id BIGINT,
    last_watched_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    certificate_url VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (course_id, user_id),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (last_lesson_id) REFERENCES course_lessons(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_course_enrollments_course_id ON course_enrollments(course_id);
CREATE INDEX idx_course_enrollments_user_id ON course_enrollments(user_id);
CREATE INDEX idx_course_enrollments_enrollment_status ON course_enrollments(enrollment_status);
CREATE INDEX idx_course_enrollments_progress_percent ON course_enrollments(progress_percent);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_course_enrollments_updated_at BEFORE UPDATE ON course_enrollments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 18.0.14 视频观看历史表 (video_watch_history)

```sql
CREATE TABLE video_watch_history (
    id BIGSERIAL PRIMARY KEY,
    video_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    watch_position INT DEFAULT 0,
    watch_duration INT DEFAULT 0,
    total_watch_duration INT DEFAULT 0,
    watch_count INT DEFAULT 1,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    last_watched_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    first_watched_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (video_id, user_id),
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_video_watch_history_video_id ON video_watch_history(video_id);
CREATE INDEX idx_video_watch_history_user_id ON video_watch_history(user_id);
CREATE INDEX idx_video_watch_history_last_watched ON video_watch_history(last_watched_at);
CREATE INDEX idx_video_watch_history_completed ON video_watch_history(completed);
```

### 18.0.15 数据表关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       交流学习社区数据库关系图                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐         ┌──────────────┐                              │
│  │    videos    │────────>│video_processi│                              │
│  │              │         │     ng_jobs   │                              │
│  │ - id         │         │              │                              │
│  │ - author_id  │         │ - video_id   │                              │
│  └──────┬───────┘         └──────────────┘                              │
│           │                                                                  │
│           v                                                                  │
│  ┌──────────────────┐    ┌──────────────┐                                 │
│  │video_watch_history│    │  documents   │                                 │
│  │                  │    │              │                                 │
│  │ - video_id       │    │ - author_id  │                                 │
│  │ - user_id        │    │ - category_id│                                 │
│  └──────────────────┘    └──────┬───────┘                                 │
│           │                      │                                        │
│           │    ┌─────────────────┴──────────────┐                         │
│           │    │                                │                         │
│           v    v                                v                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                │
│  │  discussions │    │   courses    │    │course_       │                │
│  │              │    │              │    │enrollments   │                │
│  │ - user_id     │    │ - instructor │    │ - course_id  │                │
│  │ - skill_id    │    │ - category_id│    │ - user_id    │                │
│  └──────┬───────┘    └──────┬───────┘    └──────────────┘                │
│         │                   │                                                   │
│         v                   v                                                   │
│  ┌──────────────┐    ┌──────────────┐                                        │
│  │discussion_   │    │course_       │                                        │
│  │  comments    │    │  lessons     │                                        │
│  │              │    │              │                                        │
│  │ - user_id     │    │ - course_id  │                                        │
│  └──────────────┘    └──────────────┘                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 十八、交流学习社区

### 18.1 社区首页

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  社区顶部 Banner                                      │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  学习 • 交流 • 分享 • 成长                           │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  内容导航                                             │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐   │  │
│  │  │ 📺 视频  │ │ 📄 文档  │ │ 💬 讨论  │ │ 🎓 课程 │   │  │
│  │  │  128    │ │  256    │ │  512    │ │  16    │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  热门内容                                             │  │
│  │  ┌───────────────────────────────────────────────────────┐  │  │
│  │  │  📺 置页设计完整教程 - 从 0 到 1                        │  │  │
│  │  │     • 👁️ 2,345 观看  • ⭐ 4.8  • 15分钟             │  │  │
│  │  ├───────────────────────────────────────────────────────┤  │  │
│  │  │  📄 Python FastAPI 完整开发指南                           │  │  │
│  │  │     • 👁️ 5,678 阅读  • ⭐ 4.9  • 25分钟             │  │  │
│  │  ├───────────────────────────────────────────────────────┤  │  │
│  │  │  💬 如何使用 Claude Code 提升 100% 开发效率            │  │  │
│  │  │     • 👁️ 892 回复   • 🔥 热门话题                       │  │  │
│  │  └───────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  最新内容                                             │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │  │
│  │  │             │ │             │ │             │          │  │
│  │  │ 📺 视频教程  │ │ 📄 技术文档  │ │ 💬 社区讨论  │          │  │
│  │  │             │ │             │ │             │          │  │
│  │  │ 发布于 2天前 │ │ 发布于 5小时前│ 发布于 1天前 │          │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  精选课程                                             │  │
│  │  ┌───────────────────────────────────────────────────────┐  │  │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐                        │  │  │
│  │  │  │         │ │         │ │         │                        │  │  │
│  │  │  │ Python  │ │  React  │ │  AI 技术  │  ...                   │  │  │
│  │  │  │  入门    │  │  实战   │  │  实战    │                        │  │  │
│  │  │  │  12 课时  │  │  8 课时  │  │ 10 课时 │                        │  │  │
│  │  │  │  ⭐ 4.9  │  │  ⭐ 4.7  │  │  │  │  │
│  │  │  └─────────┘ └─────────┘ └─────────┘                        │  │  │
│  │  └───────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  [ 查看全部课程 → ]                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 18.2 视频教程

#### 18.2.1 视频播放器

```typescript
// ============================================
// 视频播放器组件
// ============================================

import { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, FullScreen } from 'lucide-react';

interface VideoPlayerProps {
  src: string;
  poster?: string;
  title: string;
  description?: string;
  subtitles?: { language: string; url: string }[];
  relatedVideos?: Video[];
}

export function VideoPlayer({ src, poster, title, description, subtitles, relatedVideos }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);

  // 格式化时间
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // 快捷键控制
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === ' ') {
        e.preventDefault();
        togglePlay();
      } else if (e.key === 'ArrowLeft') {
        videoRef.current!.currentTime -= 5;
      } else if (e.key === 'ArrowRight') {
        videoRef.current!.currentTime += 5;
      } else if (e.key === 'f') {
        e.preventDefault();
        toggleFullscreen();
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, []);

  const togglePlay = () => {
    if (isPlaying) {
      videoRef.current?.pause();
    } else {
      videoRef.current?.play();
    }
    setIsPlaying(!isPlaying);
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  };

  return (
    <div className="video-player">
      <video
        ref={videoRef}
        src={src}
        poster={poster}
        className="w-full aspect-video bg-black rounded-lg"
        onTimeUpdate={() => setCurrentTime(videoRef.current!.currentTime)}
        onLoadedMetadata={() => setDuration(videoRef.current!.duration)}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
      >
        {subtitles?.map((sub, index) => (
          <track key={index} kind="subtitles" src={sub.url} srcLang={sub.language} />
        ))}
      </video>

      {/* 控制栏 */}
      <div className="controls mt-4">
        {/* 进度条 */}
        <input
          type="range"
          min={0}
          max={duration}
          value={currentTime}
          onChange={(e) => {
            videoRef.current!.currentTime = Number(e.target.value);
            setCurrentTime(Number(e.target.value));
          }}
          className="w-full accent-blue-600"
        />

        <div className="flex items-center justify-between mt-2">
          {/* 播放/暂停 */}
          <button onClick={togglePlay} className="p-2 hover:bg-gray-100 rounded-full">
            {isPlaying ? <Pause size={20} /> : <Play size={20} />}
          </button>

          {/* 时间显示 */}
          <span className="text-sm text-gray-600">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>

          {/* 播放速度 */}
          <select
            value={playbackSpeed}
            onChange={(e) => {
              setPlaybackSpeed(Number(e.target.value));
              if (videoRef.current) {
                videoRef.current.playbackRate = Number(e.target.value);
              }
            }}
            className="ml-4 text-sm border rounded px-2 py-1"
          >
            <option value={0.5}>0.5x</option>
            <option value={1}>1x</option>
            <option value={1.25}>1.25x</option>
            <option value={1.5}>1.5x</option>
            <option value={2}>2x</option>
          </select>

          {/* 音量 */}
          <button className="ml-4 p-2 hover:bg-gray-100 rounded-full">
            <Volume2 size={20} />
          </button>

          {/* 全屏 */}
          <button onClick={toggleFullscreen} className="ml-4 p-2 hover:bg-gray-100 rounded-full">
            <FullScreen size={20} />
          </button>
        </div>
      </div>

      {/* 标题和描述 */}
      <div className="mt-4">
        <h3 className="text-xl font-semibold">{title}</h3>
        {description && (
          <p className="text-gray-600 mt-2">{description}</p>
        )}
      </div>

      {/* 相关视频 */}
      {relatedVideos && relatedVideos.length > 0 && (
        <div className="mt-6">
          <h4 className="font-semibold mb-3">相关视频</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {relatedVideos.map((video) => (
              <RelatedVideoCard key={video.id} video={video} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

#### 18.2.2 视频上传

```typescript
// ============================================
// 视频上传功能
// ============================================

interface UploadProgress {
  file: File;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  videoId?: string;
  error?: string;
}

export function VideoUpload() {
  const [uploads, setUploads] = useState<UploadProgress[]>([]);

  const handleFileSelect = async (files: FileList) => {
    const fileArray = Array.from(files);

    // 添加到上传队列
    const newUploads: UploadProgress[] = fileArray.map(file => ({
      file,
      progress: 0,
      status: 'uploading'
    }));

    setUploads([...uploads, ...newUploads]);

    // 逐个上传
    for (const upload of newUploads) {
      await uploadFile(upload);
    }
  };

  const uploadFile = async (upload: UploadProgress) => {
    const formData = new FormData();
    formData.append('video', upload.file);
    formData.append('title', upload.file.name.replace(/\.[^/.]+$/, ''));

    try {
      // 上传文件
      const xhr = new XMLHttpRequest();
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          upload.progress = (e.loaded / e.total) * 100;
          setUploads([...uploads]);
        }
      };

      xhr.onload = async () => {
        if (xhr.status === 200) {
          const result = JSON.parse(xhr.responseText);
          upload.status = 'processing';
          upload.videoId = result.id;
          setUploads([...uploads]);

          // 触发视频处理（转码、生成缩略图等）
          await processVideo(result.id);
        }
      };

      xhr.open('POST', '/api/v1/videos/upload');
      xhr.send(formData);

    } catch (error) {
      upload.status = 'error';
      upload.error = '上传失败';
      setUploads([...uploads]);
    }
  };

  const processVideo = async (videoId: string) => {
    try {
      await api.post(`/api/v1/videos/${videoId}/process`);

      const uploadIndex = uploads.findIndex(u => u.videoId === videoId);
      if (uploadIndex !== -1) {
        uploads[uploadIndex].status = 'completed';
        setUploads([...uploads]);
      }

      toast.success('视频上传并处理成功');
    } catch (error) {
      const uploadIndex = uploads.findIndex(u => u.videoId === videoId);
      if (uploadIndex !== -1) {
        uploads[uploadIndex].status = 'error';
        uploads[uploadIndex].error = '处理失败';
        setUploads([...uploads]);
      }
    }
  };

  return (
    <div className="video-upload">
      <input
        type="file"
        accept="video/*"
        multiple
        onChange={(e) => handleFileSelect(e.target.files)}
        className="hidden"
        id="video-upload"
      />
      <label
        htmlFor="video-upload"
        className="flex flex-col items-center justify-center w-64 h-32 border-2 border-dashed rounded-lg cursor-pointer hover:border-blue-500"
      >
        <UploadCloud className="w-8 h-8 text-gray-400 mb-2" />
        <span className="text-sm text-gray-600">点击或拖拽上传视频</span>
        <span className="text-xs text-gray-400 mt-1">支持 MP4, WebM, MOV</span>
      </label>

      {/* 上传进度列表 */}
      {uploads.map((upload, index) => (
        <UploadProgressItem key={index} upload={upload} />
      ))}
    </div>
  );
}
```

### 18.3 文档系统

#### 18.3.1 文档结构

```
docs/
├── getting-started/
│   ├── installation.md
│   ├── quick-start.md
│   └── first-skill.md
├── tutorials/
│   ├── python/
│   │   ├── basics.md
│   │   ├── web-development.md
│   │   └── data-science.md
│   ├── frontend/
│   │   ├── react/
│   │   │   ├── introduction.md
│   │   │   ├── components.md
│   │   │   └── state-management.md
│   │   └── vue/
│   │       └── introduction.md
│   └── ai/
│       ├── prompt-engineering/
│       └── llm-apis/
├── api-reference/
│   ├── overview.md
│   ├── authentication.md
│   ├── skills/
│   │   ├── list.md
│   │   ├── create.md
│   │   ├── update.md
│   │   └── delete.md
│   └── users/
│       └── management.md
├── examples/
│   └── code-snippets/
└── glossary.md
```

#### 18.3.2 文档渲染

```typescript
// ============================================
// 文档渲染器
// ============================================

import { useMemo } from 'react';
import { ReactMarkdown } from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';

interface DocsContentProps {
  content: string;
}

export function DocsContent({ content }: DocsContentProps) {
  const components = {
    // 代码块
    pre: ({ children, className, ...props }) => {
      const language = /language-(\w+)/.exec(className || '')?.[1];
      return (
        <div className="relative group">
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
            <code className={className}>{children}</code>
          </pre>
          <CopyButton
            code={String(children?.props?.children || '')}
            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100"
          />
        </div>
      );
    },
    // 标题
    h1: ({ children, id }) => (
      <h1 id={id} className="text-3xl font-bold mt-8 mb-4 scroll-mt-20">
        {children}
        <a
          href={`#${id}`}
          className="ml-2 text-blue-600 opacity-0 hover:opacity-100"
        >
          #
        </a>
      </h1>
    ),
    h2: ({ children, id }) => (
      <h2 id={id} className="text-2xl font-semibold mt-8 mb-4 scroll-mt-20">
        {children}
        <a
          href={`#${id}`}
          className="ml-2 text-blue-600 opacity-0 hover:opacity-100"
        >
          #
        </a>
      </h2>
    ),
    h3: ({ children, id }) => (
      <h3 id={id} className="text-xl font-semibold mt-6 mb-3 scroll-mt-16">
        {children}
        <a
          href={`#${id}`}
          className="ml-2 text-blue-600 opacity-0 hover:opacity-100"
        >
          #
        </a>
      </h3>
    ),
    // 引用块
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-700 my-4">
        {children}
      </blockquote>
    ),
    // 表格
    table: ({ children }) => (
      <div className="overflow-x-auto my-4">
        <table className="min-w-full divide-y divide-gray-200">
          {children}
        </table>
      </div>
    ),
    // 警告框
    div: ({ className, children }) => {
      if (className?.includes('callout')) {
        const type = className.match(/callout-(\w+)/)?.[1];
        const styles = {
          note: 'bg-blue-50 border-blue-200 text-blue-800',
          tip: 'bg-yellow-50 border-yellow-200 text-yellow-800',
          warning: 'bg-red-50 border-red-200 text-red-800',
        };
        return (
          <div className={`p-4 rounded-lg border my-4 ${styles[type as keyof typeof styles] || 'note'}`}>
            {children}
          </div>
        );
      }
      return <div>{children}</div>;
    }
  };

  return (
    <ReactMarkdown
      components={components}
      rehypePlugins={[
        rehypeHighlight,
        rehypeSlug,
        rehypeAutolinkHeadings,
        [{ type: 'html', render: ({ children }) => <div>{children}</div> }]
      ]}
    >
      {content}
    </ReactMarkdown>
  );
}
```

### 18.4 讨论区功能

```typescript
// ============================================
// 讨论区组件
// ============================================

interface Comment {
  id: string;
  content: string;
  author: {
    id: string;
    username: string;
    avatar: string;
  };
  createdAt: Date;
  updatedAt?: Date;
  parentId?: string;
  replies?: Comment[];
  likes: number;
  isLiked: boolean;
}

export function DiscussionThread({ threadId }: { threadId: string }) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [replyTo, setReplyTo] = useState<string | null>(null);

  const fetchComments = async () => {
    const response = await api.get(`/api/v1/discussions/${threadId}/comments`);
    setComments(response.data);
  };

  const handleSubmitComment = async (content: string) => {
    await api.post(`/api/v1/discussions/${threadId}/comments`, {
      content,
      parentId: replyTo || undefined
    });
    await fetchComments();
    setReplyTo(null);
  };

  const handleLike = async (commentId: string) => {
    await api.post(`/api/v1/comments/${commentId}/like`);
    await fetchComments();
  };

  return (
    <div className="discussion-thread">
      {/* 评论输入框 */}
      <CommentForm onSubmit={handleSubmitComment} />

      {/* 评论列表 */}
      <div className="mt-6 space-y-4">
        {comments.map((comment) => (
          <CommentItem
            key={comment.id}
            comment={comment}
            onReply={setReplyTo}
            onLike={handleLike}
          />
        ))}
      </div>
    </div>
  );
}
```

---

