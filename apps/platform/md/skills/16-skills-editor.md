# 第十六章：Skills 编辑器

> 本文档描述 Skills 编辑器的功能特性和实现细节。
>
> 本章涵盖 Skills 编辑器所需的所有数据库表结构设计。

## 16.0 数据库设计

### 16.0.1 枚举类型定义

```sql
-- ============================================
-- Skills 编辑器枚举类型
-- ============================================

CREATE TYPE session_type AS ENUM ('create', 'edit', 'fork');
CREATE TYPE editor_mode AS ENUM ('markdown', 'visual', 'split');
CREATE TYPE session_status AS ENUM ('active', 'idle', 'closed', 'merged');
CREATE TYPE save_type AS ENUM ('manual', 'auto', 'snapshot');
CREATE TYPE file_category AS ENUM ('image', 'video', 'audio', 'document', 'archive', 'other');
CREATE TYPE upload_status AS ENUM ('uploading', 'processing', 'completed', 'failed', 'deleted');
CREATE TYPE storage_type AS ENUM ('local', 'oss', 'cos', 's3');
CREATE TYPE conflict_type AS ENUM ('concurrent_edit', 'merge_failed', 'version_conflict');
CREATE TYPE resolution_strategy AS ENUM ('keep_local', 'keep_remote', 'manual_merge', 'auto_merge');
CREATE TYPE conflict_status AS ENUM ('detected', 'pending', 'resolved', 'ignored');
CREATE TYPE action_type AS ENUM ('create', 'update', 'delete', 'format', 'insert', 'paste', 'save');
CREATE TYPE collaboration_permission AS ENUM ('read', 'comment', 'edit');
```

### 16.0.2 编辑会话表 (editor_sessions)

```sql
CREATE TABLE editor_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL,
    skill_id BIGINT,
    session_type session_type NOT NULL,
    parent_skill_id BIGINT,
    editor_mode editor_mode NOT NULL DEFAULT 'markdown',
    is_collaborative BOOLEAN NOT NULL DEFAULT FALSE,
    is_autosave_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    last_save_at TIMESTAMPTZ,
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    client_ip VARCHAR(45),
    user_agent VARCHAR(500),
    status session_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMPTZ,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_skill_id) REFERENCES skills(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_editor_sessions_session_id ON editor_sessions(session_id);
CREATE INDEX idx_editor_sessions_user_id ON editor_sessions(user_id);
CREATE INDEX idx_editor_sessions_skill_id ON editor_sessions(skill_id);
CREATE INDEX idx_editor_sessions_status ON editor_sessions(status);
CREATE INDEX idx_editor_sessions_last_activity ON editor_sessions(last_activity_at);

-- 自动更新 last_activity_at 触发器
CREATE TRIGGER update_editor_sessions_last_activity BEFORE UPDATE ON editor_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 16.0.3 草稿表 (drafts)

```sql
CREATE TABLE drafts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    skill_id BIGINT,
    session_id VARCHAR(64),
    draft_title VARCHAR(200) NOT NULL,
    draft_content TEXT NOT NULL,
    draft_metadata JSONB,
    word_count INT DEFAULT 0,
    character_count INT DEFAULT 0,
    is_autosave BOOLEAN NOT NULL DEFAULT FALSE,
    save_type save_type NOT NULL DEFAULT 'manual',
    parent_draft_id BIGINT,
    version_number INT DEFAULT 1,
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    published_skill_id BIGINT,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_draft_id) REFERENCES drafts(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_drafts_user_id ON drafts(user_id);
CREATE INDEX idx_drafts_skill_id ON drafts(skill_id);
CREATE INDEX idx_drafts_session_id ON drafts(session_id);
CREATE INDEX idx_drafts_is_published ON drafts(is_published);
CREATE INDEX idx_drafts_updated_at ON drafts(updated_at);

-- 自动更新 updated_at 触发器
CREATE TRIGGER update_drafts_updated_at BEFORE UPDATE ON drafts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 16.0.4 编辑协作表 (editor_collaboration)

```sql
CREATE TABLE editor_collaboration (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    user_id BIGINT NOT NULL,
    cursor_position INT,
    selection_range JSONB,
    is_online BOOLEAN NOT NULL DEFAULT TRUE,
    last_heartbeat TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMPTZ,
    permissions collaboration_permission NOT NULL DEFAULT 'edit',
    color VARCHAR(7),
    display_name VARCHAR(100),
    UNIQUE (session_id, user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_editor_collaboration_session_id ON editor_collaboration(session_id);
CREATE INDEX idx_editor_collaboration_user_id ON editor_collaboration(user_id);
CREATE INDEX idx_editor_collaboration_is_online ON editor_collaboration(is_online);
CREATE INDEX idx_editor_collaboration_last_heartbeat ON editor_collaboration(last_heartbeat);

-- 自动更新 last_heartbeat 触发器
CREATE TRIGGER update_editor_collaboration_last_heartbeat BEFORE UPDATE ON editor_collaboration
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 16.0.5 编辑快照表 (editor_snapshots)

```sql
CREATE TABLE editor_snapshots (
    id BIGSERIAL PRIMARY KEY,
    draft_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    snapshot_content TEXT NOT NULL,
    snapshot_metadata JSONB,
    snapshot_type save_type NOT NULL DEFAULT 'manual',
    trigger_reason VARCHAR(255),
    diff_data JSONB,
    content_hash VARCHAR(64),
    file_size INT,
    is_restorable BOOLEAN NOT NULL DEFAULT TRUE,
    restored_count INT DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (draft_id) REFERENCES drafts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_editor_snapshots_draft_id ON editor_snapshots(draft_id);
CREATE INDEX idx_editor_snapshots_user_id ON editor_snapshots(user_id);
CREATE INDEX idx_editor_snapshots_snapshot_type ON editor_snapshots(snapshot_type);
CREATE INDEX idx_editor_snapshots_created_at ON editor_snapshots(created_at);
```

### 16.0.6 媒体上传表 (media_uploads)

```sql
CREATE TABLE media_uploads (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    session_id VARCHAR(64),
    draft_id BIGINT,
    file_name VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_extension VARCHAR(20) NOT NULL,
    file_size BIGINT NOT NULL,
    file_category file_category NOT NULL,
    width INT,
    height INT,
    duration INT,
    thumbnail_url VARCHAR(500),
    alt_text VARCHAR(255),
    caption TEXT,
    is_temporary BOOLEAN NOT NULL DEFAULT TRUE,
    usage_count INT DEFAULT 0,
    used_in_drafts JSONB,
    used_in_skills JSONB,
    upload_status upload_status NOT NULL DEFAULT 'uploading',
    error_message TEXT,
    storage_type storage_type NOT NULL DEFAULT 'local',
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_media_uploads_user_id ON media_uploads(user_id);
CREATE INDEX idx_media_uploads_session_id ON media_uploads(session_id);
CREATE INDEX idx_media_uploads_draft_id ON media_uploads(draft_id);
CREATE INDEX idx_media_uploads_file_category ON media_uploads(file_category);
CREATE INDEX idx_media_uploads_is_temporary ON media_uploads(is_temporary);
CREATE INDEX idx_media_uploads_upload_status ON media_uploads(upload_status);
CREATE INDEX idx_media_uploads_created_at ON media_uploads(created_at);
```

### 16.0.7 编辑冲突表 (editor_conflicts)

```sql
CREATE TABLE editor_conflicts (
    id BIGSERIAL PRIMARY KEY,
    draft_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    conflict_type conflict_type NOT NULL,
    local_version INT NOT NULL,
    remote_version INT NOT NULL,
    local_content TEXT,
    remote_content TEXT,
    base_content TEXT,
    conflict_summary TEXT,
    resolved_content TEXT,
    resolution_strategy resolution_strategy,
    status conflict_status NOT NULL DEFAULT 'detected',
    resolved_by BIGINT,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (draft_id) REFERENCES drafts(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (resolved_by) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_editor_conflicts_draft_id ON editor_conflicts(draft_id);
CREATE INDEX idx_editor_conflicts_user_id ON editor_conflicts(user_id);
CREATE INDEX idx_editor_conflicts_status ON editor_conflicts(status);
CREATE INDEX idx_editor_conflicts_created_at ON editor_conflicts(created_at);
```

### 16.0.8 编辑历史表 (editor_history)

```sql
CREATE TABLE editor_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    draft_id BIGINT,
    skill_id BIGINT,
    session_id VARCHAR(64),
    action_type action_type NOT NULL,
    action_detail VARCHAR(255),
    content_before TEXT,
    content_after TEXT,
    diff_summary TEXT,
    cursor_position_before INT,
    cursor_position_after INT,
    selection_range JSONB,
    action_metadata JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (draft_id) REFERENCES drafts(id) ON DELETE SET NULL,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_editor_history_user_id ON editor_history(user_id);
CREATE INDEX idx_editor_history_draft_id ON editor_history(draft_id);
CREATE INDEX idx_editor_history_skill_id ON editor_history(skill_id);
CREATE INDEX idx_editor_history_action_type ON editor_history(action_type);
CREATE INDEX idx_editor_history_created_at ON editor_history(created_at);
```

### 16.0.9 数据表关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       Skills编辑器数据库关系图                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐         ┌──────────────┐                              │
│  │    users     │────────>│editor_sessions│                              │
│  │              │         │              │                              │
│  │ - id         │         │ - session_id │                              │
│  └──────────────┘         │ - skill_id   │                              │
│            │              └──────┬───────┘                              │
│            │                     │                                       │
│            │    ┌────────────────┴──────────────┐                       │
│            │    │                                │                       │
│            v    v                                v                       │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────┐       │
│  │     drafts       │    │editor_collab     │    │media_uploads │       │
│  │                  │    │     oration      │    │              │       │
│  │ - user_id        │    │ - session_id     │    │ - user_id    │       │
│  │ - skill_id       │    │ - user_id        │    │ - draft_id   │       │
│  │ - session_id     │    │ - is_online      │    └──────────────┘       │
│  └────────┬─────────┘    └──────────────────┘                            │
│           │                                                                  │
│           v                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                              │
│  │ editor_snapshots │    │ editor_conflicts │                              │
│  │                  │    │                  │                              │
│  │ - draft_id       │    │ - draft_id       │                              │
│  │ - content        │    │ - status         │                              │
│  └──────────────────┘    └──────────────────┘                              │
│                                                                         │
│  ┌──────────────────┐                                                     │
│  │ editor_history   │                                                     │
│  │                  │                                                     │
│  │ - user_id        │                                                     │
│  │ - draft_id       │                                                     │
│  │ - skill_id       │                                                     │
│  └──────────────────┘                                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 十六、Skills 编辑器

### 16.1 编辑器概述

Skills 编辑器是平台核心功能，支持创建、编辑、预览和发布 Skills 文档。

```
┌─────────────────────────────────────────────────────────────┐
│                    Skills 编辑器界面                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  顶部工具栏                                          │  │
│  │  [保存草稿] [预览] [发布] [设置] [导出] [历史版本]        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────┬───────────────────────────────────────────────┐  │
│  │      │                                               │  │
│  │ 左侧 │            主编辑区                           │  │
│  │ 工具 │                                               │  │
│  │ 栏   │  ┌─────────────────────────────────────────┐  │  │
│ │      │  │                                         │  │  │
│  │      │  │         [ 所见即所得编辑器 ]            │  │  │
│  │      │  │                                         │  │  │
│  │  📝   │  │  支持 Markdown + YAML Frontmatter       │  │  │
│  │  📎   │  │  实时预览                              │  │  │
│  │  🖼️   │  │                                         │  │  │
│  │  📊   │  │                                         │  │  │
│  │  💻   │  │                                         │  │  │
│  │  🔗   │  │                                         │  │  │
│  │  ⚙️   │  │                                         │  │  │
│  │      │  │                                         │  │  │
│  │      │  └─────────────────────────────────────────┘  │  │
│  │      │                                               │  │
│  │ ┌────┴─────────────────────────────────────────────┐ │  │
│  │ │                                               │ │  │
│  │ │  属性面板 (Properties)                        │ │  │
│  │ │  ┌─────────────────────────────────────────┐  │  │
│  │  │  │ Skill ID: tech-python-data-analysis     │  │  │
│  │  │  │ 名称: [_______________________]     │  │  │
│  │  │  │ 分类: [技术 ▼]                       │  │  │
│  │  │  │ 类型: [免费 ▼]                       │  │  │
│  │  │  │ 标签: [Python] [+]                 │  │  │
│  │  │  │                                       │  │  │
│  │  │  │ 版本: 1.0.0                           │  │  │
│  │  │  │ 定价: █████ (商用 Skills)             │  │  │
│  │  │  │                                       │  │  │
│  │  │  │ [ 高级设置 ▼ ]                        │  │  │
│  │  │  └─────────────────────────────────────────┘  │  │
│  │ └──────────────────────────────────────────────┘ │  │
│  └──────┴───────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  底部状态栏                                          │  │
│  │  字数: 1,234  |  阅读时间: 5分钟  |  上次保存: 2分钟前  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 16.2 编辑器功能特性

#### 16.2.1 核心功能

| 功能 | 说明 | 技术实现 |
|------|------|----------|
| **所见即所得编辑** | 实时预览 Markdown 渲染效果 | Toast UI + ReactMarkdown |
| **语法高亮** | Markdown、YAML、代码块语法高亮 | Prism.js / Shiki |
| **智能提示** | Skills 元素自动补全 | Monaco Editor |
| **版本历史** | Git 风格版本控制，可对比回滚 | isomorphic-git |
| **实时协作** | 多人同时编辑，显示光标位置 | Y.js / WebSocket |
| **拖拽上传** | 支持图片、文件拖拽上传 | react-dropzone |
| **离线编辑** | 支持离线编辑，自动同步 | IndexedDB + Service Worker |

#### 16.2.2 编辑工具栏

```typescript
// ============================================
// 编辑器工具栏配置
// ============================================

export const EDITOR_TOOLBAR = [
  // 文本格式
  {
    type: 'group',
    name: 'format',
    items: [
      { icon: 'bold', label: '粗体', action: 'toggleBold' },
      { icon: 'italic', label: '斜体', action: 'toggleItalic' },
      { icon: 'strikethrough', label: '删除线', action: 'toggleStrikethrough' },
      { icon: 'code', label: '行内代码', action: 'toggleCode' }
    ]
  },
  // 标题
  {
    type: 'group',
    name: 'headings',
    items: [
      { icon: 'h1', label: '一级标题', action: 'setHeading', level: 1 },
      { icon: 'h2', label: '二级标题', action: 'setHeading', level: 2 },
      { icon: 'h3', label: '三级标题', action: 'setHeading', level: 3 }
    ]
  },
  // 列表
  {
    type: 'group',
    name: 'lists',
    items: [
      { icon: 'ul', label: '无序列表', action: 'toggleBulletList' },
      { icon: 'ol', label: '有序列表', action: 'toggleOrderedList' },
      { icon: 'checklist', label: '任务列表', action: 'toggleCheckList' }
    ]
  },
  // 插入元素
  {
    type: 'group',
    name: 'insert',
    items: [
      { icon: 'link', label: '链接', action: 'insertLink' },
      { icon: 'image', label: '图片', action: 'insertImage' },
      { icon: 'table', label: '表格', action: 'insertTable' },
      { icon: 'code-block', label: '代码块', action: 'insertCodeBlock' },
      { icon: 'quote', label: '引用', action: 'toggleBlockquote' },
      { icon: 'divider', label: '分隔线', action: 'insertDivider' },
      { icon: 'callout', label: '提示框', action: 'insertCallout' }
    ]
  },
  // Skills 特有
  {
    type: 'group',
    name: 'skills',
    items: [
      { icon: 'metadata', label: '元数据', action: 'insertMetadata' },
      { icon: 'dependencies', label: '依赖关系', action: 'insertDependencies' },
      { icon: 'changelog', label: '更新日志', action: 'insertChangelog' }
    ]
  }
];
```

#### 16.2.3 YAML 元数据编辑器

```typescript
// ============================================
// Skills 元数据编辑器
// ============================================

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const skillMetadataSchema = z.object({
  id: z.string().min(3).max(50),
  name: z.string().min(1).max(200),
  description: z.string().max(500),
  category: z.enum(['tech', 'product', 'design', 'marketing', 'ops']),
  type: z.enum(['free', 'commercial']).default('free'),
  version: z.string().default('1.0.0'),
  tags: z.array(z.string()).default([]),
  price: z.number().min(0).optional(),
  licenseTypes: z.array(z.string()).optional(),
  dependencies: z.array(z.object({
    skill_id: z.string(),
    version: z.string(),
    type: z.enum(['required', 'optional'])
  })).default([])
});

export function SkillMetadataEditor({ skill, onSave }) {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(skillMetadataSchema),
    defaultValues: skill
  });

  return (
    <form onSubmit={handleSubmit(onSave)} className="space-y-4">
      {/* 基本信息 */}
      <div className="space-y-3">
        <div>
          <label className="block text-sm font-medium mb-1">Skill ID</label>
          <input {...register('id')} className="w-full px-3 py-2 border rounded-md" />
          {errors.id && <p className="text-red-500 text-sm">{errors.id.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">名称</label>
          <input {...register('name')} className="w-full px-3 py-2 border rounded-md" />
          {errors.name && <p className="text-red-500 text-sm">{errors.name.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">描述</label>
          <textarea {...register('description')} rows={3} className="w-full px-3 py-2 border rounded-md" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">分类</label>
            <select {...register('category')} className="w-full px-3 py-2 border rounded-md">
              <option value="tech">技术</option>
              <option value="product">产品</option>
              <option value="design">设计</option>
              <option value="marketing">市场</option>
              <option value="ops">运营</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">类型</label>
            <select {...register('type')} className="w-full px-3 py-2 border rounded-md">
              <option value="free">免费</option>
              <option value="commercial">商用</option>
            </select>
          </div>
        </div>

        {/* 标签 */}
        <TagInput
          value={watch('tags')}
          onChange={(tags) => setValue('tags', tags)}
          placeholder="添加标签，按回车确认"
        />

        {/* 商用字段 */}
        {watch('type') === 'commercial' && (
          <div className="mt-4 p-4 bg-yellow-50 rounded-md border border-yellow-200">
            <h4 className="font-semibold mb-3">商用设置</h4>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-1">价格 (AI Points)</label>
                <input
                  type="number"
                  {...register('price', { valueAsNumber: true })}
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">授权类型</label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      value="personal"
                      {...register('licenseTypes')}
                      className="mr-2"
                    />
                    个人授权 (1x)
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      value="team"
                      {...register('licenseTypes')}
                      className="mr-2"
                    />
                    团队授权 (3x)
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      value="enterprise"
                      {...register('licenseTypes')}
                      className="mr-2"
                    />
                    企业授权 (10x)
                  </label>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 依赖关系 */}
        <DependencyEditor
          value={watch('dependencies')}
          onChange={(deps) => setValue('dependencies', deps)}
        />

        <div className="flex justify-end gap-3 pt-4 border-t">
          <button type="button" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
            取消
          </button>
          <button type="submit" className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            保存
          </button>
        </div>
      </div>
    </form>
  );
}
```

#### 16.2.4 实时预览

```typescript
// ============================================
// 实时预览组件
// ============================================

import { useEffect, useState } from 'react';
import { Markdown } from '@/components/Markdown';
import { SkillPreview } from '@/components/SkillPreview';

export function EditorPreview({ content, metadata }) {
  const [html, setHtml] = useState('');

  useEffect(() => {
    // 实时渲染 Markdown
    setHtml(renderMarkdown(content));
  }, [content]);

  return (
    <div className="preview-container h-full overflow-auto">
      {/* 元数据预览 */}
      <SkillPreview.Header metadata={metadata} />

      {/* 内容预览 */}
      <Markdown content={content} />

      {/* 依赖关系可视化 */}
      {metadata.dependencies && metadata.dependencies.length > 0 && (
        <DependencyGraph dependencies={metadata.dependencies} />
      )}
    </div>
  );
}

// ============================================
// 依赖关系可视化
// ============================================

import { useGraph } from '@vis-network/react';

export function DependencyGraph({ dependencies }) {
  const { graph } = useGraph({
    nodes: [],
    edges: [],
    height: '400px'
  });

  useEffect(() => {
    const nodes = dependencies.map(dep => ({
      id: dep.skill_id,
      label: `${dep.skill_id}\n${dep.version}`,
      shape: 'box',
      color: getSkillColor(dep.category)
    }));

    const edges = dependencies.map(dep => ({
      from: 'current',
      to: dep.skill_id,
      label: dep.version_constraint,
      arrows: 'to',
      dashes: dep.type === 'optional'
    }));

    graph({ nodes, edges });
  }, [dependencies]);

  return <div ref={graph.ref} />;
}
```

#### 16.2.5 版本对比

```typescript
// ============================================
// 版本对比功能
============================================

import { Diff, Hunk } from 'react-diff-view';

export function SkillVersionDiff({ oldVersion, newVersion }) {
  return (
    <div className="version-diff">
      <h3 className="text-lg font-semibold mb-4">
        版本对比: {oldVersion.version} → {newVersion.version}
      </h3>

      {/* Skills 元数据对比 */}
      <Diff
        oldValue={JSON.stringify(oldVersion.metadata, null, 2)}
        newValue={JSON.stringify(newVersion.metadata, null, 2)}
        splitView={true}
        hideLineNumbers={false}
        showDiffOnly={true}
      />

      {/* 内容对比 */}
      <Diff
        oldValue={oldVersion.content}
        newValue={newVersion.content}
        splitView={true}
        hideLineNumbers={false}
        showDiffOnly={true}
      />
    </div>
  );
}
```

### 16.3 编辑器快捷键

```
┌─────────────────────────────────────────────────────────────┐
│                     编辑器快捷键                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  编辑操作                                                    │
│  ├── Ctrl/Cmd + S     保存草稿                               │
│  ├── Ctrl/Cmd + Shift + S   发布 Skill                         │
│  ├── Ctrl/Cmd + P       预览                                   │
│  ├── Ctrl/Cmd + /       打开命令面板                           │
│  └── Ctrl/Cmd + K         快速插入                               │
│                                                             │
│  文本格式                                                    │
│  ├── Ctrl/Cmd + B       粗体                                   │
│  ├── Ctrl/Cmd + I       斜体                                   │
│  ├── Ctrl/Cmd + U       下划线                                 │
│  ├── Ctrl/Cmd + K       插入代码块                               │
│  └── Ctrl/Cmd + L       插入链接                                 │
│                                                             │
│  导航                                                        │
│  ├── Ctrl/Cmd + F       查找                                    │
│  ├── Ctrl/Cmd + H       替换                                    │
│  ├── Ctrl/Cmd + G       跳转到行                               │
│  └── Ctrl/Cmd + T         打开文件树                             │
│                                                             │
│  视图                                                        │
│  ├── Ctrl/Cmd + Shift + P   切换预览/编辑                         │
│  ├── Ctrl/Cmd + \         切换侧边栏                             │
│  └── Ctrl/Cmd + Shift + F   全屏模式                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

