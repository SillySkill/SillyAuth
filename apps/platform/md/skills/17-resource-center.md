# 第十七章：资源下载中心

> 本文档描述平台的资源下载中心和管理功能。
>
> 本章涵盖资源下载中心所需的所有数据库表结构设计。

## 17.0 数据库设计

### 17.0.1 枚举类型定义

```sql
-- ============================================
-- 资源下载中心枚举类型
-- ============================================

CREATE TYPE resource_type AS ENUM ('ide_plugin', 'ai_model', 'dev_tool', 'doc_template', 'sdk', 'cli', 'docker_image', 'other');
CREATE TYPE license_type AS ENUM ('free', 'commercial', 'trial', 'open_source');
CREATE TYPE platform_type AS ENUM ('windows', 'macos', 'linux', 'web', 'android', 'ios', 'cross_platform');
CREATE TYPE installer_type AS ENUM ('archive', 'installer', 'portable', 'docker');
CREATE TYPE file_category AS ENUM ('image', 'video', 'audio', 'document', 'archive', 'other');
CREATE TYPE resource_status AS ENUM ('draft', 'pending_review', 'published', 'archived', 'deleted');
```

### 17.0.2 资源表 (resources)

```sql
CREATE TABLE resources (
    id BIGSERIAL PRIMARY KEY,
    resource_name VARCHAR(200) NOT NULL,
    resource_slug VARCHAR(200) UNIQUE NOT NULL,
    summary VARCHAR(500),
    description TEXT,
    category_id BIGINT,
    resource_type resource_type NOT NULL,
    icon_url VARCHAR(500),
    cover_image VARCHAR(500),
    screenshots JSONB,
    version VARCHAR(50) NOT NULL,
    license_type license_type NOT NULL DEFAULT 'free',
    price INT DEFAULT 0,
    platform platform_type NOT NULL,
    download_url VARCHAR(500) NOT NULL,
    file_size BIGINT,
    file_hash VARCHAR(64),
    file_format VARCHAR(20),
    installer_type installer_type,
    requirements TEXT,
    dependencies JSONB,
    homepage_url VARCHAR(500),
    repository_url VARCHAR(500),
    documentation_url VARCHAR(500),
    author_id BIGINT,
    author_name VARCHAR(100),
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    is_official BOOLEAN NOT NULL DEFAULT FALSE,
    download_count INT DEFAULT 0,
    view_count INT DEFAULT 0,
    rating_average NUMERIC(3,2) DEFAULT 0.00,
    rating_count INT DEFAULT 0,
    status resource_status NOT NULL DEFAULT 'draft',
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES resource_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_resources_category_id ON resources(category_id);
CREATE INDEX idx_resources_resource_type ON resources(resource_type);
CREATE INDEX idx_resources_platform ON resources(platform);
CREATE INDEX idx_resources_status ON resources(status);
CREATE INDEX idx_resources_is_featured ON resources(is_featured);
CREATE INDEX idx_resources_download_count ON resources(download_count);
CREATE INDEX idx_resources_rating_average ON resources(rating_average);

-- 全文搜索索引（需要配置中文全文搜索）
-- CREATE INDEX idx_resources_fulltext ON resources USING gin(to_tsvector('simple', resource_name || ' ' || COALESCE(summary, '') || ' ' || COALESCE(description, '')));

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_resources_updated_at BEFORE UPDATE ON resources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 17.0.2 资源版本表 (resource_versions)

```sql
CREATE TABLE resource_versions (
    id BIGSERIAL PRIMARY KEY,
    resource_id BIGINT NOT NULL,
    version VARCHAR(50) NOT NULL,
    version_code INT NOT NULL,
    changelog TEXT,
    download_url VARCHAR(500) NOT NULL,
    file_size BIGINT,
    file_hash VARCHAR(64),
    is_stable BOOLEAN NOT NULL DEFAULT TRUE,
    is_latest BOOLEAN NOT NULL DEFAULT FALSE,
    download_count INT DEFAULT 0,
    released_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (resource_id, version),
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_resource_versions_resource_id ON resource_versions(resource_id);
CREATE INDEX idx_resource_versions_version_code ON resource_versions(version_code);
CREATE INDEX idx_resource_versions_is_latest ON resource_versions(is_latest);
```

### 17.0.3 资源分类表 (resource_categories)

```sql
CREATE TABLE resource_categories (
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
    FOREIGN KEY (parent_id) REFERENCES resource_categories(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_resource_categories_parent_id ON resource_categories(parent_id);
CREATE INDEX idx_resource_categories_slug ON resource_categories(category_slug);
CREATE INDEX idx_resource_categories_is_active ON resource_categories(is_active);
CREATE INDEX idx_resource_categories_sort_order ON resource_categories(sort_order);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_resource_categories_updated_at BEFORE UPDATE ON resource_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 初始化分类数据
INSERT INTO resource_categories (category_name, category_slug, description, icon, sort_order) VALUES
('IDE 插件', 'ide_plugins', 'VS Code、JetBrains 等 IDE 的插件', '🔌', 1),
('AI 模型', 'ai_models', '预训练 AI 模型和权重文件', '🤖', 2),
('开发工具', 'dev_tools', 'CLI 工具、调试器等开发辅助工具', '🛠️', 3),
('文档模板', 'doc_templates', '项目文档、API 文档等模板', '📄', 4),
('SDK 包', 'sdks', '各语言的 SDK 包', '📦', 5),
('容器镜像', 'docker_images', 'Docker 镜像和编排文件', '🐳', 6);
```

### 17.0.4 下载令牌表 (download_tokens)

```sql
CREATE TABLE download_tokens (
    id BIGSERIAL PRIMARY KEY,
    resource_id BIGINT NOT NULL,
    user_id BIGINT,
    token VARCHAR(64) UNIQUE NOT NULL,
    download_key VARCHAR(32) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    downloaded BOOLEAN NOT NULL DEFAULT FALSE,
    downloaded_at TIMESTAMPTZ,
    client_ip VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resource_id) REFERENCES resources(id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_download_tokens_resource_id ON download_tokens(resource_id);
CREATE INDEX idx_download_tokens_user_id ON download_tokens(user_id);
CREATE INDEX idx_download_tokens_token ON download_tokens(token);
CREATE INDEX idx_download_tokens_expires_at ON download_tokens(expires_at);
CREATE INDEX idx_download_tokens_downloaded ON download_tokens(downloaded);
```

### 17.0.5 下载日志表 (download_logs)

```sql
CREATE TYPE download_source AS ENUM ('direct', 'search', 'referral', 'share', 'api');
CREATE TYPE download_status AS ENUM ('started', 'completed', 'failed', 'cancelled');

CREATE TABLE download_logs (
    id BIGSERIAL PRIMARY KEY,
    resource_id BIGINT NOT NULL,
    version_id BIGINT,
    user_id BIGINT,
    download_token VARCHAR(64),
    client_ip VARCHAR(45),
    country VARCHAR(50),
    city VARCHAR(100),
    user_agent VARCHAR(500),
    platform VARCHAR(50),
    browser VARCHAR(100),
    download_source download_source NOT NULL DEFAULT 'direct',
    referrer VARCHAR(500),
    download_status download_status NOT NULL DEFAULT 'started',
    bytes_transferred BIGINT,
    download_speed INT,
    download_duration INT,
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    FOREIGN KEY (resource_id) REFERENCES resources(id),
    FOREIGN KEY (version_id) REFERENCES resource_versions(id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_download_logs_resource_id ON download_logs(resource_id);
CREATE INDEX idx_download_logs_user_id ON download_logs(user_id);
CREATE INDEX idx_download_logs_client_ip ON download_logs(client_ip);
CREATE INDEX idx_download_logs_started_at ON download_logs(started_at);
CREATE INDEX idx_download_logs_status ON download_logs(download_status);
```

### 17.0.6 资源评分表 (resource_ratings)

```sql
CREATE TABLE resource_ratings (
    id BIGSERIAL PRIMARY KEY,
    resource_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    rating INT NOT NULL,
    review TEXT,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    helpful_count INT DEFAULT 0,
    reply TEXT,
    replied_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (resource_id, user_id),
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_resource_ratings_resource_id ON resource_ratings(resource_id);
CREATE INDEX idx_resource_ratings_rating ON resource_ratings(rating);
CREATE INDEX idx_resource_ratings_created_at ON resource_ratings(created_at);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_resource_ratings_updated_at BEFORE UPDATE ON resource_ratings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 17.0.7 资源评论表 (resource_comments)

```sql
CREATE TABLE resource_comments (
    id BIGSERIAL PRIMARY KEY,
    resource_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    parent_id BIGINT,
    content TEXT NOT NULL,
    is_approved BOOLEAN NOT NULL DEFAULT TRUE,
    helpful_count INT DEFAULT 0,
    reply_count INT DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES resource_comments(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_resource_comments_resource_id ON resource_comments(resource_id);
CREATE INDEX idx_resource_comments_user_id ON resource_comments(user_id);
CREATE INDEX idx_resource_comments_parent_id ON resource_comments(parent_id);
CREATE INDEX idx_resource_comments_created_at ON resource_comments(created_at);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_resource_comments_updated_at BEFORE UPDATE ON resource_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 17.0.8 数据表关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      资源下载中心数据库关系图                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐         ┌──────────────────┐                      │
│  │    resources     │────────>│resource_versions │                      │
│  │                  │         │                  │                      │
│  │ - id             │         │ - resource_id    │                      │
│  │ - category_id    │         │ - version        │                      │
│  │ - author_id      │         │ - download_url   │                      │
│  └────────┬─────────┘         └──────────────────┘                      │
│           │                                                                  │
│           │    ┌──────────────────┐                                         │
│           ├───>│resource_categorie│                                         │
│           │    │       s          │                                         │
│           │    │                  │                                         │
│           │    │ - id             │                                         │
│           │    └──────────────────┘                                         │
│           │                                                                   │
│           │    ┌──────────────────┐    ┌──────────────┐                    │
│           └───>│download_tokens   │    │download_logs │                    │
│                │                  │    │              │                    │
│                │ - resource_id    │    │ - resource_id│                    │
│                │ - user_id        │    │ - user_id    │                    │
│                └──────────────────┘    └──────────────┘                    │
│                                                                         │
│  ┌──────────────────┐    ┌──────────────────┐                             │
│  │resource_ratings  │    │resource_comments │                             │
│  │                  │    │                  │                             │
│  │ - resource_id    │    │ - resource_id    │                             │
│  │ - user_id        │    │ - user_id        │                             │
│  │ - rating         │    │ - parent_id      │                             │
│  └──────────────────┘    └──────────────────┘                             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 十七、资源下载中心

### 17.1 资源分类

平台提供丰富的 AI 工具和开发资源下载，帮助用户快速上手。

```
┌─────────────────────────────────────────────────────────────┐
│                    资源下载中心                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  按类别筛选                                           │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │  │
│  │  │ IDE插件 │ │ AI模型  │ │ 开发工具 │ │ 文档   │        │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  热门资源                                             │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │ 📦 OpenClaw CLI                     ⭐ 4.9       │  │  │
│  │  │    openclaw-cli-v2.1.0-win-x64.zip                 │  │  │
│  │  │    下载: 12,345 | 大小: 45MB | 更新: 2024-01-15   │  │  │
│  │  │    [Windows] [macOS] [Linux] [文档]               │  │  │
│  │  ├──────────────────────────────────────────────────┤  │  │
│  │  │ 🤖 Claude Code Desktop              ⭐ 4.8       │  │  │
│  │  │    claude-code-desktop-1.2.0.dmg                    │  │  │
│  │  │    下载: 8,901 | 大小: 180MB | 更新: 2024-01-10  │  │  │
│  │  │    [Windows] [macOS] [Linux] [文档]               │  │  │
│  │  ├──────────────────────────────────────────────────┤  │  │
│  │  │ 🔧 Cursor 编辑器                    ⭐ 4.7       │  │  │
│  │  │    cursor-1.5.0-build222.exe                       │  │  │
│  │  │    下载: 6,789 | 大小: 95MB | 更新: 2024-01-08   │  │  │
│  │  │    [Windows] [macOS] [Linux] [文档]               │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 17.2 资源详情页

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  OpenClaw CLI                                     ⭐ 4.9      │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │                                                             │  │
│  │  OpenClaw CLI 是一个命令行工具，让您直接从终端访问...  │  │
│  │                                                             │  │
│  │  📊 统计                                                 │  │
│  │  • 总下载: 12,345                                             │  │
│  │  • 本周下载: 234                                             │  │
│  │  • 评分: 4.9 (256 评分)                                        │  │
│  │                                                             │  │
│  │  🏷️ 标签                                                 │  │
│  │  [AI 工具] [CLI] [OpenAI] [文档] [+ Add]                 │  │
│  │                                                             │  │
│  │  📁 下载版本                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ Version 2.1.0 (最新) • 2024-01-15 • 45MB           │  │  │
│  │  │ [Windows x64] [macOS x64] [Linux x64]               │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │ Version 2.0.0 • 2023-12-01 • 42MB                 │  │  │
│  │  │ [Windows x64] [macOS x64] [Linux x64]               │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  📚 使用文档                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ • 快速开始指南                                      │  │  │
│  │  │  • API 参考文档                                      │  │  │
│  │  │ • 常见问题解答                                      │  │  │  │
│  │  │  • 视频教程                                          │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  💬 用户评价                                             │  │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ @user1: 工具很好用，API 调用很方便！              │  │  │
│  │  │           └─ 3天前 • 👍 24                           │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │ @dev_master: 文档很详细，上手快。                     │  │  │
│  │  │           └─ 1周前 • 👍 18                           │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  [ ⬇️ 下载最新版 ]  [ ⭐ 收藏 ]  [ 🔗 分享 ]               │  │
│  │                                                             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  相关资源推荐                                           │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │  │
│  │  │             │ │             │ │             │       │  │
│  │  │ Claude Code  │ │   Cursor    │ │   Copilot    │       │  │
│  │  │             │ │             │ │             │       │  │
│  │  │    ⭐ 4.8   │ │    ⭐ 4.7   │ │    ⭐ 4.5   │       │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 17.3 资源管理（后台）

```typescript
// ============================================
// 资源管理后台
// ============================================

interface Resource {
  id: string;
  name: string;
  description: string;
  category: 'ide' | 'ai-tool' | 'dev-tool' | 'documentation';
  versions: ResourceVersion[];
  totalDownloads: number;
  averageRating: number;
  tags: string[];
  officialUrl: string;
  documentationUrl: string;
}

interface ResourceVersion {
  version: string;
  platform: 'windows' | 'macos' | 'linux';
  architecture: 'x64' | 'arm64';
  downloadUrl: string;
  fileSize: number;
  sha256: string;
  releaseDate: Date;
  isActive: boolean;
}

export function ResourceManagement() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  // 上传新资源
  const handleUpload = async (file: File, metadata: Partial<Resource>) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('metadata', JSON.stringify(metadata));

      const result = await api.post('/admin/resources/upload', formData);

      // 添加到资源列表
      setResources([result.data, ...resources]);
      toast.success('资源上传成功');
    } catch (error) {
      toast.error('资源上传失败');
    } finally {
      setIsUploading(false);
    }
  };

  // 更新资源
  const handleUpdateResource = async (id: string, updates: Partial<Resource>) => {
    try {
      await api.put(`/admin/resources/${id}`, updates);
      toast.success('资源更新成功');
    } catch (error) {
      toast.error('资源更新失败');
    }
  };

  // 删除资源
  const handleDeleteResource = async (id: string) => {
    if (!confirm('确定要删除这个资源吗？')) return;

    try {
      await api.delete(`/admin/resources/${id}`);
      setResources(resources.filter(r => r.id !== id));
      toast.success('资源删除成功');
    } catch (error) {
      toast.error('资源删除失败');
    }
  };

  return (
    <div className="resource-management">
      {/* 资源列表 */}
      <ResourceTable
        resources={resources}
        onUpdate={handleUpdateResource}
        onDelete={handleDeleteResource}
      />

      {/* 上传按钮 */}
      <UploadButton onUpload={handleUpload} isUploading={isUploading} />
    </div>
  );
}
```

### 17.4 下载链接安全

```typescript
// ============================================
// 临时下载链接生成
// ============================================

import { createHash } from 'crypto';

interface DownloadToken {
  token: string;
  resourceId: string;
  versionId: string;
  expiresAt: Date;
  maxDownloads: number;
  downloadCount: number;
}

export async function generateDownloadToken(
  resourceId: string,
  versionId: string,
  options: {
    expiresIn?: number; // 默认 24 小时
    maxDownloads?: number; // 默认 5 次
  } = {}
): Promise<string> {
  const { expiresIn = 86400, maxDownloads = 5 } = options;

  const token: DownloadToken = {
    token: generateToken(),
    resourceId,
    versionId,
    expiresAt: new Date(Date.now() + expiresIn * 1000),
    maxDownloads,
    downloadCount: 0
  };

  // 保存到数据库
  await db.downloadTokens.create({ data: token });

  // 返回加密的下载链接
  const encrypted = encryptToken(token);
  return `/download/${encrypted}`;
}

// ============================================
// 下载验证中间件
// ============================================

export async function validateDownloadToken(
  encryptedToken: string
): Promise<{ resourceId: string; versionId: string } | null> {
  try {
    const token: DownloadToken = decryptToken(encryptedToken);

    // 检查过期
    if (new Date() > token.expiresAt) {
      return null;
    }

    // 检查下载次数
    if (token.downloadCount >= token.maxDownloads) {
      return null;
    }

    // 增加下载计数
    await db.downloadTokens.update(token.id, {
      downloadCount: token.downloadCount + 1
    });

    return {
      resourceId: token.resourceId,
      versionId: token.versionId
    };
  } catch (error) {
    return null;
  }
}
```

---

