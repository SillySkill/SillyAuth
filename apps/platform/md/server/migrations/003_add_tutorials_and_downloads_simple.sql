-- ============================================
-- Migration 003: Add Tutorials and Downloads (Simplified)
-- Description: Add technical tutorials and resource download sections
-- Author: SillyMD Team
-- Date: 2026-02-04
-- ============================================

-- ============================================
-- Table 1: tutorials (技术教程表)
-- Purpose: Store AI tools tutorials (Claude Code, OpenClaw, etc.)
-- ============================================
CREATE TABLE IF NOT EXISTS tutorials (
    id BIGSERIAL PRIMARY KEY,

    -- Basic Info
    tutorial_key VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,

    -- Multi-language Title
    title_zh_CN VARCHAR(200) NOT NULL,
    title_en VARCHAR(200),
    title_ja VARCHAR(200),
    title_ko VARCHAR(200),

    -- Multi-language Description
    description_zh_CN TEXT,
    description_en TEXT,
    description_ja TEXT,
    description_ko TEXT,

    -- Multi-language Content
    content_zh_CN TEXT,
    content_en TEXT,
    content_ja TEXT,
    content_ko TEXT,

    -- Categorization
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    difficulty VARCHAR(20) DEFAULT 'beginner',
    tags VARCHAR(500),

    -- Media
    thumbnail VARCHAR(500),
    video_url VARCHAR(500),
    video_type VARCHAR(20),
    video_duration INT,
    video_file_size BIGINT,

    -- External Resources
    github_url VARCHAR(500),
    documentation_url VARCHAR(500),
    official_website VARCHAR(500),

    -- SEO
    meta_title VARCHAR(200),
    meta_description VARCHAR(500),
    meta_keywords VARCHAR(500),
    og_image VARCHAR(500),

    -- Display Settings
    position INT DEFAULT 0,
    view_count BIGINT DEFAULT 0,
    like_count INT DEFAULT 0,
    featured BOOLEAN DEFAULT FALSE,
    is_pinned BOOLEAN DEFAULT FALSE,

    -- Status
    is_published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMPTZ,

    -- Relations
    author_id BIGINT,
    related_tutorials VARCHAR(500),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_tutorials_author_id FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_tutorials_category ON tutorials(category);
CREATE INDEX IF NOT EXISTS idx_tutorials_subcategory ON tutorials(subcategory);
CREATE INDEX IF NOT EXISTS idx_tutorials_difficulty ON tutorials(difficulty);
CREATE INDEX IF NOT EXISTS idx_tutorials_slug ON tutorials(slug);
CREATE INDEX IF NOT EXISTS idx_tutorials_is_published ON tutorials(is_published);
CREATE INDEX IF NOT EXISTS idx_tutorials_featured ON tutorials(featured);
CREATE INDEX IF NOT EXISTS idx_tutorials_position ON tutorials(position);
CREATE INDEX IF NOT EXISTS idx_tutorials_published_at ON tutorials(published_at);


-- ============================================
-- Table 2: tutorial_chapters (教程章节表)
-- Purpose: Split tutorials into chapters for better organization
-- ============================================
CREATE TABLE IF NOT EXISTS tutorial_chapters (
    id BIGSERIAL PRIMARY KEY,

    -- Relations
    tutorial_id BIGINT NOT NULL,

    -- Chapter Info
    chapter_order INT NOT NULL,
    chapter_key VARCHAR(100) NOT NULL,

    -- Multi-language
    title_zh_CN VARCHAR(200) NOT NULL,
    title_en VARCHAR(200),
    title_ja VARCHAR(200),
    title_ko VARCHAR(200),

    description_zh_CN TEXT,
    description_en TEXT,

    -- Content
    content_zh_CN TEXT,
    content_en TEXT,

    -- Media
    video_url VARCHAR(500),
    video_start_time INT,
    video_end_time INT,

    -- Resources
    code_snippets TEXT,
    attachments TEXT,

    is_free BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_tutorial_chapters_tutorial_id FOREIGN KEY (tutorial_id) REFERENCES tutorials(id) ON DELETE CASCADE,
    CONSTRAINT uq_tutorial_chapters_order UNIQUE(tutorial_id, chapter_order)
);

CREATE INDEX IF NOT EXISTS idx_tutorial_chapters_tutorial_id ON tutorial_chapters(tutorial_id);
CREATE INDEX IF NOT EXISTS idx_tutorial_chapters_order ON tutorial_chapters(chapter_order);


-- ============================================
-- Table 3: downloads (资源下载表)
-- Purpose: Store downloadable resources (WSL, Python, GitHub, etc.)
-- ============================================
CREATE TABLE IF NOT EXISTS downloads (
    id BIGSERIAL PRIMARY KEY,

    -- Basic Info
    download_key VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,

    -- Multi-language
    title_zh_CN VARCHAR(200) NOT NULL,
    title_en VARCHAR(200),
    title_ja VARCHAR(200),
    title_ko VARCHAR(200),

    description_zh_CN TEXT,
    description_en TEXT,
    description_ja TEXT,
    description_ko TEXT,

    -- Categorization
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    version VARCHAR(50),
    platform VARCHAR(50),

    -- File Info
    file_name VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(50),
    file_checksum VARCHAR(100),

    -- Mirror Links
    mirror_url_1 VARCHAR(500),
    mirror_url_2 VARCHAR(500),
    mirror_url_3 VARCHAR(500),
    mirror_url_names TEXT,

    -- External Links
    github_url VARCHAR(500),
    official_url VARCHAR(500),
    documentation_url VARCHAR(500),

    -- Media
    thumbnail VARCHAR(500),
    screenshots TEXT,

    -- SEO
    meta_title VARCHAR(200),
    meta_description VARCHAR(500),
    meta_keywords VARCHAR(500),
    og_image VARCHAR(500),

    -- Stats
    download_count BIGINT DEFAULT 0,
    view_count BIGINT DEFAULT 0,
    like_count INT DEFAULT 0,

    -- Display
    position INT DEFAULT 0,
    featured BOOLEAN DEFAULT FALSE,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_official BOOLEAN DEFAULT FALSE,

    -- License
    license_type VARCHAR(50),
    license_url VARCHAR(500),

    -- Status
    is_published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMPTZ,

    -- Relations
    author_id BIGINT,
    related_downloads VARCHAR(500),

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_downloads_author_id FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_downloads_category ON downloads(category);
CREATE INDEX IF NOT EXISTS idx_downloads_subcategory ON downloads(subcategory);
CREATE INDEX IF NOT EXISTS idx_downloads_platform ON downloads(platform);
CREATE INDEX IF NOT EXISTS idx_downloads_slug ON downloads(slug);
CREATE INDEX IF NOT EXISTS idx_downloads_is_published ON downloads(is_published);
CREATE INDEX IF NOT EXISTS idx_downloads_featured ON downloads(featured);
CREATE INDEX IF NOT EXISTS idx_downloads_download_count ON downloads(download_count);
CREATE INDEX IF NOT EXISTS idx_downloads_position ON downloads(position);


-- ============================================
-- Table 4: download_versions (资源版本表)
-- Purpose: Track multiple versions of same resource
-- ============================================
CREATE TABLE IF NOT EXISTS download_versions (
    id BIGSERIAL PRIMARY KEY,

    download_id BIGINT NOT NULL,
    version VARCHAR(50) NOT NULL,
    version_code INT NOT NULL,

    file_name VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size BIGINT,
    file_checksum VARCHAR(100),

    changelog TEXT,
    release_date DATE,

    is_latest BOOLEAN DEFAULT FALSE,
    is_stable BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_download_versions_download_id FOREIGN KEY (download_id) REFERENCES downloads(id) ON DELETE CASCADE,
    CONSTRAINT uq_download_versions_version UNIQUE(download_id, version)
);

CREATE INDEX IF NOT EXISTS idx_download_versions_download_id ON download_versions(download_id);
CREATE INDEX IF NOT EXISTS idx_download_versions_is_latest ON download_versions(is_latest);


-- ============================================
-- Table 5: tutorial_progress (教程学习进度表)
-- Purpose: Track user progress in tutorials
-- ============================================
CREATE TABLE IF NOT EXISTS tutorial_progress (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL,
    tutorial_id BIGINT NOT NULL,

    current_chapter_id BIGINT,
    progress_percent INT DEFAULT 0,
    last_position INT,

    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,

    last_accessed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_tutorial_progress_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_tutorial_progress_tutorial_id FOREIGN KEY (tutorial_id) REFERENCES tutorials(id) ON DELETE CASCADE,
    CONSTRAINT fk_tutorial_progress_chapter_id FOREIGN KEY (current_chapter_id) REFERENCES tutorial_chapters(id) ON DELETE SET NULL,
    CONSTRAINT uq_tutorial_progress_user_tutorial UNIQUE(user_id, tutorial_id)
);

CREATE INDEX IF NOT EXISTS idx_tutorial_progress_user_id ON tutorial_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_tutorial_progress_tutorial_id ON tutorial_progress(tutorial_id);
CREATE INDEX IF NOT EXISTS idx_tutorial_progress_is_completed ON tutorial_progress(is_completed);


-- ============================================
-- Table 6: download_records (下载记录表)
-- Purpose: Track all download activities
-- ============================================
CREATE TABLE IF NOT EXISTS download_records (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT,
    download_id BIGINT NOT NULL,
    version_id BIGINT,

    download_ip VARCHAR(45),
    download_source VARCHAR(100),
    user_agent VARCHAR(500),

    download_status VARCHAR(20) DEFAULT 'completed',

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_download_records_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_download_records_download_id FOREIGN KEY (download_id) REFERENCES downloads(id) ON DELETE CASCADE,
    CONSTRAINT fk_download_records_version_id FOREIGN KEY (version_id) REFERENCES download_versions(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_download_records_user_id ON download_records(user_id);
CREATE INDEX IF NOT EXISTS idx_download_records_download_id ON download_records(download_id);
CREATE INDEX IF NOT EXISTS idx_download_records_created_at ON download_records(created_at);


-- ============================================
-- Seed initial data
-- ============================================

-- Insert sample tutorials
INSERT INTO tutorials (
    tutorial_key,
    slug,
    title_zh_CN,
    title_en,
    description_zh_CN,
    description_en,
    category,
    subcategory,
    difficulty,
    video_url,
    video_type,
    featured,
    is_published,
    published_at,
    author_id
) VALUES
(
    'claude-code-getting-started',
    'claude-code-getting-started',
    'Claude Code 入门教程',
    'Claude Code Getting Started',
    '学习如何安装和使用 Anthropic Claude Code，这款强大的 AI 编程助手',
    'Learn how to install and use Anthropic Claude Code, the powerful AI coding assistant',
    'claude-code',
    'installation',
    'beginner',
    'https://jc-st.tos-cn-shanghai.volces.com/sillymd/tutorials/claude-code-intro.mp4',
    'upload',
    TRUE,
    TRUE,
    CURRENT_TIMESTAMP,
    1
),
(
    'openclaw-ai-assistant',
    'openclaw-ai-assistant',
    'OpenClaw AI 助手完全指南',
    'OpenClaw AI Assistant Complete Guide',
    '深入了解 OpenClaw AI 助手的功能和使用技巧',
    'Deep dive into OpenClaw AI Assistant features and usage tips',
    'openclaw',
    'usage',
    'intermediate',
    'https://jc-st.tos-cn-shanghai.volces.com/sillymd/tutorials/openclaw-guide.mp4',
    'upload',
    TRUE,
    TRUE,
    CURRENT_TIMESTAMP,
    1
)
ON CONFLICT (tutorial_key) DO NOTHING;

-- Insert sample downloads
INSERT INTO downloads (
    download_key,
    slug,
    title_zh_CN,
    title_en,
    description_zh_CN,
    description_en,
    category,
    subcategory,
    version,
    platform,
    file_name,
    file_url,
    file_size,
    file_type,
    github_url,
    featured,
    is_published,
    is_official,
    published_at,
    author_id
) VALUES
(
    'wsl2-windows',
    'wsl2-windows',
    'WSL2 for Windows 安装包',
    'WSL2 for Windows Installer',
    '适用于 Windows 10/11 的 WSL2 安装包，国内镜像下载',
    'WSL2 installer for Windows 10/11, mirror download',
    'wsl',
    'installer',
    '2.0.0',
    'windows',
    'wsl.2.0.0.x64.msi',
    'https://jc-st.tos-cn-shanghai.volces.com/sillymd/downloads/wsl.2.0.0.x64.msi',
    256000000,
    'msi',
    'https://github.com/microsoft/WSL',
    TRUE,
    TRUE,
    TRUE,
    CURRENT_TIMESTAMP,
    1
),
(
    'python-312-windows',
    'python-312-windows',
    'Python 3.12 for Windows',
    'Python 3.12 for Windows',
    'Python 3.12.1 Windows x64 安装包，国内镜像下载',
    'Python 3.12.1 Windows x64 installer, mirror download',
    'python',
    'installer',
    '3.12.1',
    'windows',
    'python-3.12.1-amd64.exe',
    'https://jc-st.tos-cn-shanghai.volces.com/sillymd/downloads/python-3.12.1-amd64.exe',
    25600000,
    'exe',
    'https://www.python.org/downloads/',
    TRUE,
    TRUE,
    TRUE,
    CURRENT_TIMESTAMP,
    1
)
ON CONFLICT (download_key) DO NOTHING;
