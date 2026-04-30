# 第三章：数据库设计总览

> 本文档提供 SillyMD 平台所有数据库表的全局视图，包括 ER 关系图、表分类和命名规范。

## 3.1 数据库架构概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SillyMD 数据库架构                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │   用户域         │    │   Skills 域      │    │   协作域         │  │
│  │                  │    │                  │    │                  │  │
│  │ - users          │◄───│ - skills         │◄───│ - teams          │  │
│  │ - admin_users    │    │ - skill_versions │    │ - team_members   │  │
│  │ - user_achievements│   │ - skill_tags     │    │ - team_projects  │  │
│  │ - achievements   │    │ - skill_favorites│    │                  │  │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘  │
│           │                       │                       │            │
│           └───────────────────────┴───────────────────────┘            │
│                                   │                                    │
│                          ┌────────▼─────────┐                          │
│                          │  交易域          │                          │
│                          │                  │                          │
│                          │ - licenses       │                          │
│                          │ - point_transactions│                       │
│                          │ - orders         │                          │
│                          │ - withdrawal_requests│                     │
│                          └──────────────────┘                          │
│                                                                         │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │   内容域         │    │   审核域         │    │   运营域         │  │
│  │                  │    │                  │    │                  │  │
│  │ - articles       │    │ - review_queue   │    │ - statistics     │  │
│  │ - article_tags   │    │ - crawler_tasks  │    │ - leaderboards   │  │
│  │ - media_files    │    │ - admin_logs     │    │ - invitations    │  │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │   外部应用集成域                                             │      │
│  │                                                              │      │
│  │ - upload_records (AI活动秀文件上传)                          │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.1.5 全局枚举类型定义

> **注意**: 以下枚举类型为 PostgreSQL 自定义枚举，需要在数据库初始化时统一创建。
> 详细文档请参考各模块文档。

#### 核心业务枚举

```sql
-- 用户角色（02-architecture.md）
CREATE TYPE user_role AS ENUM ('user', 'vendor', 'admin');

-- 管理员角色（19-admin-backend.md）
CREATE TYPE admin_role AS ENUM ('super_admin', 'admin', 'moderator');

-- 供应商等级（02-architecture.md）
CREATE TYPE vendor_level AS ENUM ('normal', 'premium', 'gold');

-- Skills 分类（02-architecture.md）
CREATE TYPE skill_category AS ENUM ('tech', 'product', 'design', 'marketing', 'ops');

-- Skills 类型（02-architecture.md）
CREATE TYPE skill_type AS ENUM ('free', 'commercial');

-- Skills 状态（02-architecture.md）
CREATE TYPE skill_status AS ENUM ('draft', 'reviewing', 'approved', 'rejected');

-- 团队角色（02-architecture.md）
CREATE TYPE team_role AS ENUM ('owner', 'admin', 'member', 'viewer');

-- 授权类型（02-architecture.md）
CREATE TYPE license_type AS ENUM ('personal', 'team', 'enterprise');
```

#### 交易与支付枚举

```sql
-- 订单状态（07-commerce.md）
CREATE TYPE order_status AS ENUM ('pending', 'paid', 'completed', 'cancelled', 'refunded');

-- 支付方式（07-commerce.md）
CREATE TYPE payment_method_type AS ENUM ('balance', 'alipay', 'wechat', 'bank');

-- 支付状态（07-commerce.md）
CREATE TYPE payment_status AS ENUM ('pending', 'processing', 'success', 'failed', 'cancelled');

-- 提现方式（07-commerce.md, 19-admin-backend.md）
CREATE TYPE withdrawal_method AS ENUM ('alipay', 'wechat', 'bank');

-- 提现状态（07-commerce.md, 19-admin-backend.md）
CREATE TYPE withdrawal_status AS ENUM ('pending', 'processing', 'completed', 'rejected', 'cancelled');

-- 积分交易类型（02-architecture.md）
CREATE TYPE transaction_type AS ENUM ('recharge', 'purchase', 'earning', 'refund', 'withdraw');

-- 商业交易类型（07-commerce.md）
CREATE TYPE commerce_transaction_type AS ENUM ('recharge', 'consume', 'refund', 'income', 'withdraw', 'reward', 'commission', 'fee');
```

#### 审核 AI 枚举

```sql
-- 审核阶段（05-ai-review.md）
CREATE TYPE review_stage AS ENUM ('l1_auto', 'l2_ai', 'l3_manual', 'completed', 'rejected');

-- 审核状态（05-ai-review.md）
CREATE TYPE review_queue_status AS ENUM ('pending', 'reviewing', 'approved', 'rejected', 'appealed');

-- 审核优先级（05-ai-review.md, 19-admin-backend.md）
CREATE TYPE review_priority AS ENUM ('low', 'normal', 'high', 'urgent');

-- 审核阶段类型（05-ai-review.md）
CREATE TYPE review_stage_type AS ENUM ('auto', 'ai', 'manual');

-- 审核标准类别（05-ai-review.md）
CREATE TYPE review_criterion_category AS ENUM ('format', 'safety', 'quality', 'compliance', 'originality');
```

#### 协作系统枚举

```sql
-- 活动类型（06-collaboration.md）
CREATE TYPE activity_type AS ENUM ('create', 'update', 'delete', 'join', 'leave', 'invite');

-- 资源类型（06-collaboration.md）
CREATE TYPE resource_type AS ENUM ('team', 'project', 'skill', 'member', 'milestone');

-- 依赖类型（06-collaboration.md）
CREATE TYPE dependency_type AS ENUM ('hard', 'soft', 'optional');

-- 依赖状态（06-collaboration.md）
CREATE TYPE dependency_status AS ENUM ('active', 'blocked', 'resolved', 'deferred');

-- 协作会话类型（06-collaboration.md, 16-skills-editor.md）
CREATE TYPE session_type AS ENUM ('create', 'edit', 'fork', 'document_edit', 'code_review', 'planning', 'brainstorm', 'retrospective');

-- 会话状态（06-collaboration.md）
CREATE TYPE session_status AS ENUM ('scheduled', 'active', 'paused', 'completed', 'cancelled');
```

#### 运营增长枚举

```sql
-- 排行榜类型（10-operations.md）
CREATE TYPE leaderboard_type AS ENUM ('skills_hot', 'skills_new', 'users_active', 'vendors_earnings', 'teams_active');

-- 时间周期（10-operations.md）
CREATE TYPE period_type AS ENUM ('daily', 'weekly', 'monthly', 'yearly', 'all_time');

-- 实体类型（10-operations.md）
CREATE TYPE entity_type AS ENUM ('skill', 'user', 'team');

-- 奖励类型（10-operations.md）
CREATE TYPE reward_type AS ENUM ('points', 'xp', 'badge', 'premium_days');

-- 奖励状态（10-operations.md）
CREATE TYPE reward_status AS ENUM ('pending', 'earned', 'paid', 'expired', 'cancelled');

-- 活动类型（10-operations.md）
CREATE TYPE campaign_type AS ENUM ('email', 'sms', 'push', 'in_app', 'reward');

-- 发送状态（10-operations.md）
CREATE TYPE send_status AS ENUM ('pending', 'sent', 'delivered', 'failed', 'bounced');
```

#### 数字存证枚举

```sql
-- 存证类型（08-digital-proof.md）
CREATE TYPE proof_type AS ENUM ('creation', 'modification', 'transfer', 'verification');

-- 验证状态（08-digital-proof.md）
CREATE TYPE verification_status AS ENUM ('pending', 'verified', 'failed', 'expired');

-- 签名者类型（08-digital-proof.md）
CREATE TYPE signer_type AS ENUM ('author', 'platform', 'notary', 'third_party');

-- 区块链类型（08-digital-proof.md）
CREATE TYPE blockchain_type AS ENUM ('ethereum', 'bitcoin', 'polygon', 'bsc', 'arweave', 'ipfs', 'custom');

-- 区块链网络（08-digital-proof.md）
CREATE TYPE blockchain_network AS ENUM ('mainnet', 'testnet', 'private');
```

#### 通知与消息枚举

```sql
-- 通知类型（02-architecture.md）
CREATE TYPE notification_type AS ENUM ('system', 'skill_update', 'comment', 'license', 'achievement', 'team');

-- 系统通知类型（19-admin-backend.md）
CREATE TYPE sys_notification_type AS ENUM ('info', 'warning', 'success', 'error');

-- 目标用户类型（19-admin-backend.md）
CREATE TYPE target_user_type AS ENUM ('all', 'users', 'vendors', 'admins');
```

#### 文件与内容枚举

```sql
-- 文件分类（16-skills-editor.md, 17-resource-center.md, 19-admin-backend.md）
CREATE TYPE file_category AS ENUM ('image', 'video', 'audio', 'document', 'archive', 'other');

-- 存储类型（16-skills-editor.md, 19-admin-backend.md）
CREATE TYPE storage_type AS ENUM ('local', 'oss', 'cos', 's3');

-- 内容类型（19-admin-backend.md）
CREATE TYPE content_type AS ENUM ('text', 'html', 'markdown');

-- 媒体类型（19-admin-backend.md）
CREATE TYPE media_type AS ENUM ('image', 'video');
```

#### 编辑器枚举

```sql
-- 编辑器模式（16-skills-editor.md）
CREATE TYPE editor_mode AS ENUM ('markdown', 'visual', 'split');

-- 保存类型（16-skills-editor.md）
CREATE TYPE save_type AS ENUM ('manual', 'auto', 'snapshot');

-- 上传状态（16-skills-editor.md）
CREATE TYPE upload_status AS ENUM ('uploading', 'processing', 'completed', 'failed', 'deleted');

-- 冲突类型（16-skills-editor.md）
CREATE TYPE conflict_type AS ENUM ('concurrent_edit', 'merge_failed', 'version_conflict');

-- 解决策略（16-skills-editor.md）
CREATE TYPE resolution_strategy AS ENUM ('keep_local', 'keep_remote', 'manual_merge', 'auto_merge');
```

#### 资源中心枚举

```sql
-- 资源类型（17-resource-center.md）
CREATE TYPE resource_type AS ENUM ('ide_plugin', 'ai_model', 'dev_tool', 'doc_template', 'sdk', 'cli', 'docker_image', 'other');

-- 许可证类型（17-resource-center.md）
CREATE TYPE resource_license_type AS ENUM ('free', 'commercial', 'trial', 'open_source');

-- 平台类型（17-resource-center.md）
CREATE TYPE platform_type AS ENUM ('windows', 'macos', 'linux', 'web', 'android', 'ios', 'cross_platform');

-- 安装类型（17-resource-center.md）
CREATE TYPE installer_type AS ENUM ('archive', 'installer', 'portable', 'docker');

-- 资源状态（17-resource-center.md）
CREATE TYPE resource_status AS ENUM ('draft', 'pending_review', 'published', 'archived', 'deleted');
```

#### 社区功能枚举

```sql
-- 视频类型（18-community.md）
CREATE TYPE video_type AS ENUM ('tutorial', 'demo', 'presentation', 'interview', 'other');

-- 难度级别（18-community.md）
CREATE TYPE difficulty_level AS ENUM ('beginner', 'intermediate', 'advanced');

-- 课程类型（18-community.md）
CREATE TYPE lesson_type AS ENUM ('video', 'document', 'quiz', 'assignment');

-- 注册状态（18-community.md）
CREATE TYPE enrollment_status AS ENUM ('active', 'completed', 'dropped', 'refunded');
```

#### 权限与认证枚举

```sql
-- API 密钥类型（09-user-permissions.md）
CREATE TYPE api_key_type AS ENUM ('read', 'write', 'admin');

-- 验证类型（09-user-permissions.md）
CREATE TYPE verification_type AS ENUM ('register', 'change', 'bind');

-- 登录状态（09-user-permissions.md）
CREATE TYPE login_status AS ENUM ('success', 'failed', 'blocked');

-- 登录类型（09-user-permissions.md）
CREATE TYPE login_type AS ENUM ('password', 'oauth', 'api_key', 'sms');
```

#### 举报与审核枚举

```sql
-- 举报目标类型（19-admin-backend.md）
CREATE TYPE report_target_type AS ENUM ('skill', 'user', 'comment', 'review');

-- 举报原因（19-admin-backend.md）
CREATE TYPE report_reason AS ENUM ('spam', 'inappropriate', 'copyright', 'fake', 'other');

-- 举报状态（19-admin-backend.md）
CREATE TYPE report_status AS ENUM ('pending', 'investigating', 'resolved', 'dismissed');
```

#### 配置与其他枚举

```sql
-- 配置类型（19-admin-backend.md）
CREATE TYPE config_type AS ENUM ('string', 'number', 'boolean', 'json');

-- 链接打开方式（19-admin-backend.md）
CREATE TYPE link_target AS ENUM ('_self', '_blank');

-- 文章状态（19-admin-backend.md）
CREATE TYPE article_status AS ENUM ('draft', 'pending_review', 'published', 'rejected', 'archived');

-- 富文本块类型（19-admin-backend.md）
CREATE TYPE block_type AS ENUM ('text', 'image', 'video', 'html', 'code');
```

### 枚举类型使用规范

1. **命名规范**: 使用 `{业务}_type` 或 `{业务}_status` 格式
2. **值定义**: 使用小写+下划线的命名方式
3. **扩展性**: 预留 `other` 或 `custom` 值用于扩展
4. **一致性**: 同一概念在不同模块中使用相同的枚举值

### 枚举类型统计

| 类别 | 数量 | 主要文档 |
|------|------|----------|
| 核心业务 | 10 | 02-architecture.md |
| 交易支付 | 8 | 07-commerce.md |
| AI 审核 | 5 | 05-ai-review.md |
| 协作系统 | 8 | 06-collaboration.md |
| 运营增长 | 10 | 10-operations.md |
| 数字存证 | 6 | 08-digital-proof.md |
| 文件内容 | 4 | 16-skills-editor.md |
| 社区功能 | 7 | 18-community.md |
| 权限认证 | 4 | 09-user-permissions.md |
| 其他 | 15 | 各模块文档 |
| **总计** | **77+** | - |

---

## 3.2 数据表分类统计

### 按领域分类

| 领域 | 表数量 | 文档位置 |
|------|--------|----------|
| **用户与权限** | 10 | 02-architecture.md, 09-user-permissions.md |
| **Skills 核心** | 7 | 02-architecture.md, 04-skills-system.md |
| **版本控制** | 3 | 02-architecture.md |
| **团队协作** | 7 | 06-collaboration.md |
| **商用交易** | 8 | 07-commerce.md |
| **数字存证** | 4 | 08-digital-proof.md |
| **AI 审核** | 4 | 05-ai-review.md |
| **运营增长** | 9 | 10-operations.md |
| **社区功能** | 7 | 18-community.md |
| **资源中心** | 7 | 17-resource-center.md |
| **管理后台** | 19 | 19-admin-backend.md |
| **编辑器** | 4 | 16-skills-editor.md |
| **外部应用集成** | 1 | 03-database-overview.md |

### 总计

- **总表数**: 约 90 张表
- **核心表**: 17 张 (users, skills, teams, licenses, 等)
- **扩展表**: 73 张 (各功能模块)

## 3.3 核心表关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        核心表关系图 (ER Diagram)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                     ┌──────────────┐                                   │
│                     │    users     │                                   │
│                     │              │                                   │
│                     │ - id (PK)    │                                   │
│                     │ - username   │                                   │
│                     │ - email      │                                   │
│                     │ - role       │                                   │
│                     └──────┬───────┘                                   │
│                            │                                            │
│         ┌──────────────────┼──────────────────┐                        │
│         │                  │                  │                        │
│         ▼                  ▼                  ▼                        │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐                   │
│  │   skills   │    │   teams    │    │  licenses  │                   │
│  │            │    │            │    │            │                   │
│  │ - id (PK)  │    │ - id (PK)  │    │ - id (PK)  │                   │
│  │ - author   │◄───│ - owner    │    │ - skill_id │◄──────┐           │
│  │ - content  │    │ - name     │    │ - buyer    │       │           │
│  └─────┬──────┘    └──────┬─────┘    └─────┬──────┘       │           │
│        │                  │                  │              │           │
│        │                  │                  └──────────────┘           │
│        ▼                  ▼                                            │
│  ┌────────────┐    ┌────────────┐                                     │
│  │skill_versions│   │team_members│                                     │
│  │            │    │            │                                     │
│  │ - skill_id │    │ - team_id  │                                     │
│  │ - version  │    │ - user_id  │                                     │
│  └────────────┘    └────────────┘                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 3.4 数据表详细清单

### 3.4.1 用户与权限域 (User & Permissions)

| 表名 | 说明 | 主文档 | 行数估算 |
|------|------|--------|----------|
| users | 用户主表 | 02-architecture.md | 10万+ |
| admin_users | 管理员表 | 02-architecture.md, 19-admin-backend.md | <100 |
| user_achievements | 用户成就关联 | 02-architecture.md | 50万+ |
| achievements | 成就定义 | 02-architecture.md | <100 |
| oauth_accounts | OAuth 账号绑定 | 09-user-permissions.md | 10万+ |
| api_keys | API 密钥 | 09-user-permissions.md | 1万+ |
| roles | 角色定义 | 09-user-permissions.md | <10 |
| permissions | 权限定义 | 09-user-permissions.md | <100 |
| role_permissions | 角色-权限关联 | 09-user-permissions.md | <500 |
| user_roles | 用户-角色关联 | 09-user-permissions.md | 20万+ |

### 3.4.2 Skills 核心域

| 表名 | 说明 | 主文档 |
|------|------|--------|
| skills | Skills 主表 | 02-architecture.md |
| skill_versions | Skills 版本 | 02-architecture.md |
| skill_dependencies | Skills 依赖关系 | 02-architecture.md |
| tags | 标签主表 | 02-architecture.md |
| skill_tags | Skills-标签关联 | 02-architecture.md |
| skill_favorites | Skills 收藏 | 02-architecture.md |
| skill_comments | Skills 评论 | 02-architecture.md |
| reviews | Skills 评分 | 02-architecture.md |

### 3.4.3 团队协作域

| 表名 | 说明 | 主文档 |
|------|------|--------|
| teams | 团队主表 | 02-architecture.md |
| team_members | 团队成员 | 02-architecture.md |
| team_projects | 团队项目 | 02-architecture.md |
| project_skills | 项目 Skills | 02-architecture.md |
| team_activity_logs | 团队活动日志 | 06-collaboration.md |
| project_dependencies | 项目依赖关系 | 06-collaboration.md |
| collaboration_sessions | 协作会话 | 06-collaboration.md |

### 3.4.4 商用交易域

| 表名 | 说明 | 主文档 |
|------|------|--------|
| licenses | 授权许可证 | 02-architecture.md |
| point_transactions | 积分交易记录 | 02-architecture.md |
| orders | 订单主表 | 07-commerce.md |
| order_items | 订单明细 | 07-commerce.md |
| payments | 支付记录 | 07-commerce.md |
| withdrawals | 提现申请 | 07-commerce.md |
| wallet_balances | 钱包余额 | 07-commerce.md |
| commercial_skills_meta | 商用 Skills 元数据 | 07-commerce.md |

### 3.4.5 数字存证域

| 表名 | 说明 | 主文档 |
|------|------|--------|
| content_proofs | 内容存证 | 08-digital-proof.md |
| blockchain_records | 区块链记录 | 08-digital-proof.md |
| verification_logs | 验证日志 | 08-digital-proof.md |
| signature_certificates | 签名证书 | 08-digital-proof.md |

### 3.4.6 AI 审核域

| 表名 | 说明 | 主文档 |
|------|------|--------|
| review_queue | 审核队列 | 05-ai-review.md |
| ai_review_results | AI 审核结果 | 05-ai-review.md |
| manual_reviews | 人工审核记录 | 05-ai-review.md |
| review_statistics | 审核统计 | 05-ai-review.md |

### 3.4.7 运营增长域

| 表名 | 说明 | 主文档 |
|------|------|--------|
| statistics | 统计数据 | 02-architecture.md |
| leaderboards | 排行榜 | 10-operations.md |
| recommendation_logs | 推荐日志 | 10-operations.md |
| invitation_rewards | 邀请奖励 | 10-operations.md |
| user_retention_data | 用户留存数据 | 10-operations.md |
| activity_analytics | 活动分析 | 10-operations.md |
| user_segments | 用户分群 | 10-operations.md |
| user_segment_members | 分群成员 | 10-operations.md |
| recall_campaigns | 召回活动 | 10-operations.md |

### 3.4.8 社区功能域

| 表名 | 说明 | 主文档 |
|------|------|--------|
| community_posts | 社区帖子 | 18-community.md |
| post_comments | 帖子评论 | 18-community.md |
| post_likes | 帖子点赞 | 18-community.md |
| topics | 话题标签 | 18-community.md |
| following_relationships | 关注关系 | 18-community.md |
| notifications | 通知 | 18-community.md |
| audit_logs | 审计日志 | 18-community.md |

### 3.4.9 资源中心域

| 表名 | 说明 | 主文档 |
|------|------|--------|
| resources | 资源主表 | 17-resource-center.md |
| resource_versions | 资源版本 | 17-resource-center.md |
| resource_categories | 资源分类 | 17-resource-center.md |
| download_tokens | 下载令牌 | 17-resource-center.md |
| download_logs | 下载日志 | 17-resource-center.md |
| resource_ratings | 资源评分 | 17-resource-center.md |
| resource_comments | 资源评论 | 17-resource-center.md |

### 3.4.10 管理后台域

| 表名 | 说明 | 主文档 |
|------|------|--------|
| crawler_tasks | 爬虫任务 | 19-admin-backend.md |
| crawler_logs | 爬虫日志 | 19-admin-backend.md |
| platform_config | 平台配置 | 19-admin-backend.md |
| admin_logs | 管理员操作日志 | 19-admin-backend.md |
| system_notifications | 系统通知 | 19-admin-backend.md |
| user_reports | 用户举报 | 19-admin-backend.md |
| withdrawal_requests | 提现申请 | 19-admin-backend.md |
| carousels | 轮播图 | 19-admin-backend.md |
| article_categories | 文章分类 | 19-admin-backend.md |
| articles | 文章 | 19-admin-backend.md |
| article_tags | 文章标签 | 19-admin-backend.md |
| article_tag_relations | 文章标签关联 | 19-admin-backend.md |
| page_contents | 页面内容 | 19-admin-backend.md |
| content_blocks | 内容块 | 19-admin-backend.md |
| friendly_links | 友情链接 | 19-admin-backend.md |
| media_files | 媒体文件 | 19-admin-backend.md |

### 3.4.11 外部应用集成域

| 表名 | 说明 | 主文档 |
|------|------|--------|
| upload_records | 文件上传记录表 | 本文档 |

### 3.4.12 编辑器域

| 表名 | 说明 | 主文档 |
|------|------|--------|
| editor_sessions | 编辑器会话 | 16-skills-editor.md |
| editor_snapshots | 编辑器快照 | 16-skills-editor.md |
| template_library | 模板库 | 16-skills-editor.md |
| template_categories | 模板分类 | 16-skills-editor.md |

### 3.4.13 外部应用集成域详细表设计

#### upload_records (文件上传记录表)

**用途**: 记录AI活动秀应用的文件上传信息，支持OSS存储和设备指纹追踪。

**表结构**:

```sql
-- ============================================
-- 外部应用集成：文件上传记录表
-- ============================================
CREATE TABLE upload_records (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(36) UNIQUE NOT NULL,
    filename VARCHAR(512) NOT NULL,
    stored_filename VARCHAR(512) NOT NULL,
    file_path VARCHAR(1024) NOT NULL,
    file_size BIGINT NOT NULL CHECK (file_size >= 0),
    mime_type VARCHAR(128) NOT NULL,
    package_name VARCHAR(256) NOT NULL,
    module_name VARCHAR(64) NOT NULL,
    uploader_fingerprint VARCHAR(128),
    uploader_ip VARCHAR(45),
    uploader_user_agent TEXT,
    upload_time BIGINT NOT NULL CHECK (upload_time > 0),
    upload_status VARCHAR(16) NOT NULL CHECK (upload_status IN ('success', 'failed')),
    error_message TEXT,
    oss_url TEXT,
    CONSTRAINT chk_file_size CHECK (file_size >= 0),
    CONSTRAINT chk_upload_time CHECK (upload_time > 0)
);

-- 索引
CREATE INDEX idx_package_module ON upload_records(package_name, module_name);
CREATE INDEX idx_upload_time ON upload_records(upload_time DESC);
CREATE INDEX idx_fingerprint ON upload_records(uploader_fingerprint);
CREATE UNIQUE INDEX upload_records_file_id_key ON upload_records(file_id);

-- 表注释
COMMENT ON TABLE upload_records IS 'AI活动秀应用文件上传记录表';
COMMENT ON COLUMN upload_records.id IS '自增主键';
COMMENT ON COLUMN upload_records.file_id IS '文件唯一ID，UUID格式';
COMMENT ON COLUMN upload_records.filename IS '原始文件名';
COMMENT ON COLUMN upload_records.stored_filename IS '存储文件名，时间戳格式';
COMMENT ON COLUMN upload_records.file_path IS 'OSS相对路径';
COMMENT ON COLUMN upload_records.file_size IS '文件大小(字节)';
COMMENT ON COLUMN upload_records.mime_type IS 'MIME类型，如 image/jpeg';
COMMENT ON COLUMN upload_records.package_name IS '应用包名，如 com.jcoding.aiactivity';
COMMENT ON COLUMN upload_records.module_name IS '模块名，如 style/quiz/lottery';
COMMENT ON COLUMN upload_records.uploader_fingerprint IS '设备指纹(MD5前16位)';
COMMENT ON COLUMN upload_records.uploader_ip IS '上传者IP地址';
COMMENT ON COLUMN upload_records.uploader_user_agent IS 'User-Agent字符串';
COMMENT ON COLUMN upload_records.upload_time IS '上传时间(毫秒时间戳)';
COMMENT ON COLUMN upload_records.upload_status IS '状态：success=成功, failed=失败';
COMMENT ON COLUMN upload_records.error_message IS '错误信息(失败时记录)';
COMMENT ON COLUMN upload_records.oss_url IS 'OSS完整URL';
```

**OSS路径格式**:

```
application/{package_name}/{module_name}/{timestamp}.ext
```

**示例路径**:

```
application/com.jcoding.aiactivity/style/1738754321234.jpg
application/com.jcoding.aiactivity/quiz/1738754321235.png
application/com.jcoding.aiactivity/lottery/1738754321236.gif
```

**相关API**:

| 接口 | 方法 | 说明 |
|------|------|------|
| /application/upload | GET | 上传页面 |
| /application/upload/api | POST | 上传API |
| /application/upload/health | GET | 健康检查 |

**约束说明**:

| 约束名 | 类型 | 说明 |
|--------|------|------|
| chk_file_size | CHECK | 文件大小必须 >= 0 |
| chk_upload_time | CHECK | 上传时间必须 > 0 |
| chk_upload_status | CHECK | 状态必须为 'success' 或 'failed' |
| upload_records_file_id_key | UNIQUE | file_id 必须唯一 |

**索引说明**:

| 索引名 | 字段 | 用途 |
|--------|------|------|
| idx_package_module | (package_name, module_name) | 按应用和模块查询 |
| idx_upload_time | upload_time DESC | 按时间倒序查询 |
| idx_fingerprint | uploader_fingerprint | 按设备指纹查询 |

**使用场景**:

1. **AI百变秀模块**: 用户上传照片进行风格转换
   - `package_name`: `com.jcoding.aiactivity`
   - `module_name`: `style`
   - 示例: `application/com.jcoding.aiactivity/style/1738754321234.jpg`

2. **知识问答模块**: 用户上传题目相关图片
   - `package_name`: `com.jcoding.aiactivity`
   - `module_name`: `quiz`
   - 示例: `application/com.jcoding.aiactivity/quiz/1738754321235.png`

3. **幸运抽奖模块**: 上传奖品图片或背景图
   - `package_name`: `com.jcoding.aiactivity`
   - `module_name`: `lottery`
   - 示例: `application/com.jcoding.aiactivity/lottery/1738754321236.gif`

**数据统计**:

| 统计项 | 预估值 |
|--------|--------|
| 日均上传量 | 1000-5000 条 |
| 数据增长 | 约 10万条/月 |
| 保留策略 | 建议保留 6 个月 |

**性能优化建议**:

1. 按月分区：按 `upload_time` 字段进行表分区
2. 定期归档：将 6 个月前的数据迁移到归档表
3. 索引优化：高频查询使用复合索引 `idx_package_module`

## 3.5 字段命名规范

### 3.5.1 通用规范

| 类型 | 命名规则 | 示例 |
|------|----------|------|
| 主键 | `id` 或 `{表名}_id` | `id`, `user_id` |
| 外键 | `{关联表}_id` | `skill_id`, `team_id` |
| 创建时间 | `created_at` | `created_at TIMESTAMPTZ` |
| 更新时间 | `updated_at` | `updated_at TIMESTAMPTZ` |
| 删除标记 | `is_deleted` / `deleted_at` | `is_deleted BOOLEAN` |
| 状态标记 | `status` | `status VARCHAR(20)` |
| 布尔字段 | `is_{形容词}` | `is_active`, `is_public` |
| 计数字段 | `{名词}_count` | `view_count`, `like_count` |

### 3.5.2 数据类型映射

| PostgreSQL 类型 | 用途 | 示例 |
|-----------------|------|------|
| BIGSERIAL | 自增主键 | `id BIGSERIAL PRIMARY KEY` |
| BIGINT | 外键、数量 | `user_id BIGINT` |
| VARCHAR(n) | 短文本 | `username VARCHAR(50)` |
| TEXT | 长文本 | `content TEXT` |
| TIMESTAMPTZ | 时间戳 | `created_at TIMESTAMPTZ` |
| JSONB | JSON 数据 | `metadata JSONB` |
| BOOLEAN | 布尔值 | `is_active BOOLEAN` |
| NUMERIC(m,n) | 精确数值 | `price NUMERIC(10,2)` |
| ENUM | 枚举值 | `status status_type` |

### 3.5.3 索引命名规范

| 索引类型 | 命名规则 | 示例 |
|----------|----------|------|
| 普通索引 | `idx_{表名}_{字段}` | `idx_users_email` |
| 唯一索引 | `uk_{表名}_{字段}` | `uk_users_username` |
| 外键索引 | `fk_{表名}_{字段}` | `fk_skills_author_id` |
| 全文索引 | `fts_{表名}_{字段}` | `fts_skills_content` |

## 3.6 数据库设计原则

### 3.6.1 性能优化

- ✅ 所有外键字段建立索引
- ✅ 高频查询字段建立复合索引
- ✅ 使用 `JSONB` 替代 `JSON` 以支持 GIN 索引
- ✅ 大文本字段使用 `TEXT` 类型
- ✅ 时间字段统一使用 `TIMESTAMPTZ`

### 3.6.2 数据完整性

- ✅ 所有表使用 `BIGSERIAL` 主键
- ✅ 外键约束确保引用完整性
- ✅ 使用 `ON DELETE CASCADE` 处理级联删除
- ✅ 使用触发器自动更新 `updated_at`
- ✅ 枚举类型使用自定义 ENUM

### 3.6.3 安全性

- ✅ 密码字段使用 `VARCHAR(255)` 存储 hash
- ✅ 敏感数据使用 `is_encrypted` 标记
- ✅ 审计日志记录所有关键操作
- ✅ 软删除使用 `is_deleted` 或 `deleted_at`

## 3.7 数据迁移策略

### 3.7.1 版本管理

使用 Alembic (Python) 管理数据库迁移：

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "add new table"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### 3.7.2 备份策略

- 每日全量备份：`pg_dump -Fc sillymd > backup.dump`
- 实时 WAL 归档
- 异地备份存储

### 3.7.3 扩展性设计

- 使用分区表处理历史数据
- 读写分离：主库写入，从库读取
- 分库分表预留：按 `user_id` hash 分片

## 3.8 相关文档

| 文档 | 说明 |
|------|------|
| [02-architecture.md](./02-architecture.md) | 核心数据库表详细设计 |
| [05-ai-review.md](./05-ai-review.md) | AI 审核相关表 |
| [06-collaboration.md](./06-collaboration.md) | 协作系统表 |
| [07-commerce.md](./07-commerce.md) | 交易系统表 |
| [08-digital-proof.md](./08-digital-proof.md) | 数字存证表 |
| [09-user-permissions.md](./09-user-permissions.md) | 权限系统表 |
| [10-operations.md](./10-operations.md) | 运营系统表 |
| [16-skills-editor.md](./16-skills-editor.md) | 编辑器表 |
| [17-resource-center.md](./17-resource-center.md) | 资源中心表 |
| [18-community.md](./18-community.md) | 社区系统表 |
| [19-admin-backend.md](./19-admin-backend.md) | 管理后台表 |

---

**文档版本**: v1.1 | **最后更新**: 2026-02-05
