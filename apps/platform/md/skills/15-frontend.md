# 第十五章：前端设计

> 本文档详细描述 SillyMD 平台的前端设计系统、页面结构和主题配置。

## 十五、前端设计

### 15.1 设计系统

#### 15.1.1 色彩主题

平台支持多种色彩风格，用户可自由切换：

```
┌─────────────────────────────────────────────────────────────┐
│                      色彩主题                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  主题名称          主色      辅色      背景      文字       │
│  ─────────────────────────────────────────────────────      │
│  Light (明亮)     #3B82F6   #60A5FA   #FFFFFF   #1F2937   │
│  Dark (暗黑)      #3B82F6   #60A5FA   #111827   #F9FAFB   │
│  Ocean (海洋)     #0EA5E9   #38BDF8   #F0F9FF   #0C4A6E   │
│  Forest (森林)    #10B981   #34D399   #ECFDF5   #064E3B   │
│  Sunset (日落)    #F59E0B   #FBBF24   #FFFBEB   #78350F   │
│  Purple (紫韵)    #8B5CF6   #A78BFA   #F5F3FF   #5B21B6   │
│  Rose (玫瑰)      #EC4899   #F472B6   #FDF2F8   #9F1239   │
│  Custom (自定义)   可自定义色调                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 15.1.2 设计令牌 (Design Tokens)

```css
/* ============================================
   Design Tokens - CSS Variables
   ============================================ */

:root {
  /* 主色系 */
  --color-primary: #3B82F6;
  --color-primary-hover: #2563EB;
  --color-primary-light: #DBEAFE;

  /* 中性色 */
  --color-gray-50: #F9FAFB;
  --color-gray-100: #F3F4F6;
  --color-gray-200: #E5E7EB;
  --color-gray-300: #D1D5DB;
  --color-gray-400: #9CA3AF;
  --color-gray-500: #6B7280;
  --color-gray-600: #4B5563;
  --color-gray-700: #374151;
  --color-gray-800: #1F2937;
  --color-gray-900: #111827;

  /* 语义色 */
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
  --color-info: #3B82F6;

  /* 间距 */
  --spacing-xs: 0.25rem;    /* 4px */
  --spacing-sm: 0.5rem;     /* 8px */
  --spacing-md: 1rem;       /* 16px */
  --spacing-lg: 1.5rem;     /* 24px */
  --spacing-xl: 2rem;       /* 32px */
  --spacing-2xl: 3rem;      /* 48px */

  /* 圆角 */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;

  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);

  /* 字体大小 */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;

  /* 过渡 */
  --transition-fast: 150ms ease-in-out;
  --transition-base: 200ms ease-in-out;
  --transition-slow: 300ms ease-in-out;
}

/* Dark Theme Override */
[data-theme="dark"] {
  --color-bg-primary: #111827;
  --color-bg-secondary: #1F2937;
  --color-bg-tertiary: #374151;
  --color-text-primary: #F9FAFB;
  --color-text-secondary: #D1D5DB;
  --color-border: #374151;
}

/* Ocean Theme Override */
[data-theme="ocean"] {
  --color-primary: #0EA5E9;
  --color-primary-hover: #0284C7;
  --color-bg-primary: #F0F9FF;
  --color-text-primary: #0C4A6E;
}

/* Forest Theme Override */
[data-theme="forest"] {
  --color-primary: #10B981;
  --color-primary-hover: #059669;
  --color-bg-primary: #ECFDF5;
  --color-text-primary: #064E3B;
}
```

#### 15.1.3 组件库规范

```typescript
// ============================================
// 组件 Props 类型定义
// ============================================

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  children: React.ReactNode;
  onClick?: () => void;
}

interface CardProps {
  variant?: 'elevated' | 'outlined' | 'flat';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hoverable?: boolean;
  children: React.ReactNode;
}

interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number';
  size?: 'sm' | 'md' | 'lg';
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
  placeholder?: string;
}

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  children: React.ReactNode;
  footer?: React.ReactNode;
}
```

### 15.2 页面结构

#### 15.2.1 整体布局架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Header 顶部导航                           │
│  ┌──────┐  ┌─────────────┐  ┌──────────┐  ┌─────────┐  ┌────┐  │
│  │ Logo │  │  搜索框     │  │ 探索     │  │ 创建    │  │用户│  │
│  │      │  │             │  │ 下拉菜单  │  │ Skill   │  │头像│  │
│  └──────┘  └─────────────┘  └──────────┘  └─────────┘  └────┘  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────────────────────────────────────────┐  │
│  │          │  │                                              │  │
│  │ Sidebar  │  │            Main Content 主内容区              │  │
│  │  侧边栏  │  │                                              │  │
│  │          │  │                                              │  │
│  │ - 首页   │  │         (根据当前页面动态渲染)                │  │
│  │ - 探索   │  │                                              │  │
│  │ - 分类   │  │                                              │  │
│  │ - 我的   │  │                                              │  │
│  │ - 团队   │  │                                              │  │
│  │ - 设置   │  │                                              │  │
│  │          │  │                                              │  │
│  └──────────┘  └──────────────────────────────────────────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                        Footer 页脚                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  快速链接                                            │  │  │
│  │  │  关于 | 隐私政策 | 服务条款 | 帮助中心 | 联系我们  │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  社交媒体                                            │  │  │
│  │  │  [抖音] [小红书] [视频号] [GitHub] [Discord]        │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  备案信息                                            │  │  │
│  │  │  © 2026 SillyMD. All rights reserved.               │  │  │
│  │  │  浙ICP备2026000000号-1 | 浙公网安备 33010002000000号│  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

#### 15.2.2 首页 (Home)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Header                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Hero Section 英雄区                            │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │                                                      │  │  │
│  │  │     "AI Skills 托管中心"                              │  │  │
│  │  │     打造专业的 AI Skills 协作平台                       │  │  │
│  │  │                                                      │  │  │
│  │  │     [ 开始使用 ]    [ 探索 Skills ]                   │  │  │
│  │  │                                                      │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Stats 数据统计                                │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │ 10,000+  │  │  5,000+  │  │  2,000+  │  │  100+    │ │  │
│  │  │  Skills   │  │  用户     │  │  团队    │  │  国家    │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Skills Showcase Skills 展示                    │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐           │  │
│  │  │            │ │            │ │            │           │  │
│  │  │   Skill    │ │   Skill    │ │   Skill    │  ...     │  │
│  │  │   Card 1   │ │   Card 2   │ │   Card 3   │           │  │
│  │  │            │ │            │ │            │           │  │
│  │  └────────────┘ └────────────┘ └────────────┘           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Categories 分类展示                            │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────┐ │  │
│  │  │ 🛠️ 技术   │ │ │ 📦 产品   │ │ │ 🎨 设计   │ │ │ 📊 市场│ │  │
│  │  │ Skills    │ │ │ Skills    │ │ │ Skills    │ │ │ Skills│ │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 15.2.3 探索页 (Explore)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Header                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Filter Bar 筛选栏                             │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐           │  │
│  │  │ 分类筛选   │ │ 类型筛选   │ │ 排序方式   │           │  │
│  │  │  全部 ▼   │ │  全部 ▼   │ │  热度 ▼   │           │  │
│  │  └────────────┘ └────────────┘ └────────────┘           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ 🔍 搜索 Skills...                                  │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ 标签: [Python] [React] [数据分析] [+ Add]          │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Skills Grid Skills 网格                      │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐           │  │
│  │  │            │ │            │ │            │           │  │
│  │  │   Skill    │ │   Skill    │ │   Skill    │  ...     │  │
│  │  │   Card     │ │   Card     │ │   Card     │           │  │
│  │  │            │ │            │ │            │           │  │
│  │  │ ⭐ 4.8     │ │ ⭐ 4.5     │ │ ⭐ 4.9     │           │  │
│  │  │ 📥 1.2k     │ │ 📥 856     │ │ 📥 2.3k     │           │  │
│  │  │            │ │            │ │            │           │  │
│  │  └────────────┘ └────────────┘ └────────────┘           │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐           │  │
│  │  │            │ │            │ │            │           │  │
│  │  │   Skill    │ │   Skill    │ │   Skill    │  ...     │  │
│  │  │   Card     │ │   Card     │ │   Card     │           │  │
│  │  └────────────┘ └────────────┘ └────────────┘           │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │                    [ 加载更多 ]                      │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 15.2.4 Skill 详情页 (Skill Detail)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Header                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Skill Header Skill 头部                        │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ 🛠️                                                  │  │  │
│  │  │  Python 数据分析模板                                 │  │  │
│  │  │  by @username                                       │  │  │
│  │  │                                                      │  │  │
│  │  │  ⭐ 4.8 (128 评分)  📥 1,234 下载  ❤️ 256 收藏      │  │  │
│  │  │                                                      │  │  │
│  │  │  [ ⬇️ 下载 ] [ ❤️ 收藏 ] [ 🔗 分享 ]                 │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────┬─────────────────────┐ │
│  │                                       │                     │ │
│  │            Main Content             │   Sidebar 侧边栏    │ │
│  │                                       │                     │ │
│  │  ┌─────────────────────────────────┐ │  ┌───────────────┐ │ │
│  │  │  Description 描述               │ │  │  Author 作者  │ │
│  │  │  标准化的 Python 数据分析...    │ │  │               │ │ │
│  │  └─────────────────────────────────┘ │  │  @avatar      │ │ │
│  │                                       │  │  @username    │ │ │
│  │  ┌─────────────────────────────────┐ │  │               │ │ │
│  │  │  Features 特性                  │ │  │  Skills 列表  │ │ │
│  │  │  ✓ Jupyter Notebook 支持       │ │  │               │ │ │
│  │  │  ✓ 数据可视化模板               │ │  │  • Skill A    │ │ │
│  │  │  ✓ 最佳实践指南                 │ │  │  • Skill B    │ │ │
│  │  └─────────────────────────────────┘ │  │  • Skill C    │ │ │
│  │                                       │  │               │ │ │
│  │  ┌─────────────────────────────────┐ │  └───────────────┘ │ │
│  │  │  Usage 使用方法                 │ │                     │ │
│  │  │                                 │ │  ┌───────────────┐ │ │
│  │  │  npm install @sillymd/sdk      │ │  │  Statistics   │ │ │
│  │  │                                 │ │  │  统计数据      │ │ │
│  │  └─────────────────────────────────┘ │  │               │ │ │
│  │                                       │  │  📊 本月: 234  │ │ │
│  │  ┌─────────────────────────────────┐ │  │  📊 总计: 1.2k│ │ │
│  │  │  Dependencies 依赖              │ │  └───────────────┘ │ │
│  │  │  • tech-python-base >= 1.0.0    │ │                     │ │
│  │  │  • pandas >= 1.3.0              │ │  ┌───────────────┐ │ │
│  │  └─────────────────────────────────┘ │  │  Tags 标签    │ │ │
│  │                                       │  │               │ │ │
│  │  ┌─────────────────────────────────┐ │  │  #python      │ │ │
│  │  │  Version History 版本历史        │ │  │  #data        │ │ │
│  │  │  v1.0.0 (当前)                   │ │  │  #analysis    │ │ │
│  │  │  v0.9.0                         │ │  └───────────────┘ │ │
│  │  └─────────────────────────────────┘ │                     │ │
│  │                                       │                     │ │
│  └───────────────────────────────────────┴─────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Comments 评论区                                │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  @user1: 这个模板太棒了！感谢分享 🎉               │  │  │
│  │  │           └─ 2小时前                                │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │  @author: @user1 谢谢支持！有需要帮助随时联系      │  │  │
│  │  │           └─ 1小时前                                │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │  [ 添加评论... ]                                     │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 15.2.5 用户仪表板 (User Dashboard)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Header                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              User Profile 用户概览                          │  │
│  │  ┌──────────┐  ┌─────────────────────────────────────────┐ │  │
│  │  │          │  │  @username                                  │ │  │
│  │  │  Avatar  │  │  产品经理 | 优质供应商 ⭐                   │ │  │
│  │  │          │  │                                             │ │  │
│  │  │  [编辑]  │  │  ⭐ 1,250 XP  |  💎 5,000 AI Points       │ │  │
│  │  └──────────┘  └─────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Dashboard Cards 仪表板卡片                     │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────┐ │  │
│  │  │            │ │            │ │            │ │        │ │  │
│  │  │    我的    │ │    我的    │ │    收入    │ │  审核  │ │  │
│  │  │   Skills   │ │   团队    │ │   统计    │ │  状态  │ │  │
│  │  │            │ │            │ │            │ │        │ │  │
│  │  │    12      │ │     3      │ │  ¥2,500   │ │  1 待审│ │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Recent Activity 最近活动                      │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  ✅ 您的 Skill "Python 数据分析" 已通过审核          │  │  │
│  │  │     2小时前                                          │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │  💰 您收到了一笔新的授权购买订单 +¥150              │  │  │
│  │  │     5小时前                                          │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │  💬 @user2 评论了您的 Skill                          │  │  │
│  │  │     1天前                                           │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Quick Actions 快捷操作                         │  │
│  │  [ + 创建 Skill ]  [ + 创建团队 ]  [ + 充值积分 ]        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 15.2.6 团队协作页 (Team)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Header                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Team Header 团队头部                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  🏢 ACME 科技                                       │  │  │
│  │  │  sillymd.com/acme-tech                             │  │  │
│  │  │                                                     │  │  │
│  │  │  👥 8 成员  |  📁 5 项目  |  📝 12 Skills          │  │  │
│  │  │                                                     │  │  │
│  │  │  [ 邀请成员 ]  [ 创建项目 ]  [ 团队设置 ]           │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Projects 项目列表                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  📁 支付系统                                        │  │  │
│  │  │     📝 3 Skills  |  👥 4 成员  |  🕒 更新于 2天前    │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │  📁 用户系统                                        │  │  │
│  │  │     📝 5 Skills  |  👥 6 成员  |  🕒 更新于 5天前    │  │  │
│  │  ├─────────────────────────────────────────────────────┤  │  │
│  │  │  📁 数据平台                                        │  │  │
│  │  │     📝 4 Skills  |  👥 3 成员  |  🕒 更新于 1周前    │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  [ + 新建项目 ]                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Team Members 团队成员                         │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │  │
│  │  │          │ │          │ │          │ │          │     │  │
│  │  │ @owner   │ │ @dev1    │ │ @dev2    │ │ @design  │ ... │  │
│  │  │ 👑 管理员 │ │ 💻 开发  │ │ 💻 开发  │ │ 🎨 设计  │     │  │
│  │  │          │ │          │ │          │ │          │     │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │  │
│  │                                                           │  │
│  │  [ 管理成员 ]                                             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 15.2.7 登录/注册页 (Auth)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                                                                 │
│              ┌─────────────────────────┐                        │
│              │                         │                        │
│              │      [ LOGO ]          │                        │
│              │                         │                        │
│              │    SillyMD Skills     │                        │
│              │      托管中心          │                        │
│              │                         │                        │
│              └─────────────────────────┘                        │
│                                                                 │
│              ┌─────────────────────────┐                        │
│              │                         │                        │
│              │    欢迎来到 SillyMD     │                        │
│              │    Skills 托管平台       │                        │
│              │                         │                        │
│              │   [ 登录 ]  [ 注册 ]     │                        │
│              │                         │                        │
│              └─────────────────────────┘                        │
│                                                                 │
│              ┌───────────────────────────────────────┐          │
│              │                                       │          │
│              │   ────  或使用以下方式登录  ────       │          │
│              │                                       │          │
│              │   [ Google ]  [ GitHub ]  [ 微信 ]    │          │
│              │                                       │          │
│              └───────────────────────────────────────┘          │
│                                                                 │
│              ┌───────────────────────────────────────┐          │
│              │            首次使用？                   │          │
│              │         [ 立即注册 →]                  │          │
│              └───────────────────────────────────────┘          │
│                                                                 │
│                     © 2026 SillyMD. All rights reserved.         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 15.3 多语言支持

#### 15.3.1 支持语言列表

```typescript
// ============================================
// 多语言配置
// ============================================

export const SUPPORTED_LANGUAGES = [
  { code: 'zh-CN', name: '简体中文', flag: '🇨🇳' },
  { code: 'zh-TW', name: '繁體中文', flag: '🇹🇼' },
  { code: 'en-US', name: 'English', flag: '🇺🇸' },
  { code: 'ja-JP', name: '日本語', flag: '🇯🇵' },
  { code: 'ko-KR', name: '한국어', flag: '🇰🇷' },
  { code: 'es-ES', name: 'Español', flag: '🇪🇸' },
  { code: 'fr-FR', name: 'Français', flag: '🇫🇷' },
  { code: 'de-DE', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'pt-BR', name: 'Português', flag: '🇧🇷' },
  { code: 'ru-RU', name: 'Русский', flag: '🇷🇺' },
] as const;

export type LanguageCode = typeof SUPPORTED_LANGUAGES[number]['code'];
```

#### 15.3.2 i18n 翻译文件结构

```
locales/
├── zh-CN/
│   ├── common.json        # 通用翻译
│   ├── home.json          # 首页
│   ├── auth.json          # 登录/注册
│   ├── skills.json        # Skills 相关
│   ├── team.json          # 团队相关
│   └── dashboard.json     # 仪表板
├── en-US/
│   ├── common.json
│   ├── home.json
│   ├── auth.json
│   ├── skills.json
│   ├── team.json
│   └── dashboard.json
└── ja-JP/
    ├── common.json
    └── ...
```

#### 15.3.3 翻译示例

```json
// locales/zh-CN/common.json
{
  "app.name": "SillyMD Skills",
  "app.slogan": "AI Skills 托管中心",
  "nav.home": "首页",
  "nav.explore": "探索",
  "nav.mySkills": "我的 Skills",
  "nav.teams": "团队",
  "nav.settings": "设置",
  "button.login": "登录",
  "button.register": "注册",
  "button.logout": "退出",
  "theme.light": "明亮",
  "theme.dark": "暗黑",
  "theme.ocean": "海洋",
  "theme.forest": "森林"
}

// locales/en-US/common.json
{
  "app.name": "SillyMD Skills",
  "app.slogan": "AI Skills Hosting Center",
  "nav.home": "Home",
  "nav.explore": "Explore",
  "nav.mySkills": "My Skills",
  "nav.teams": "Teams",
  "nav.settings": "Settings",
  "button.login": "Login",
  "button.register": "Register",
  "button.logout": "Logout",
  "theme.light": "Light",
  "theme.dark": "Dark",
  "theme.ocean": "Ocean",
  "theme.forest": "Forest"
}

// locales/ja-JP/common.json
{
  "app.name": "SillyMD Skills",
  "app.slogan": "AI Skills ホスティングセンター",
  "nav.home": "ホーム",
  "nav.explore": "探索",
  "nav.mySkills": "マイスキル",
  "nav.teams": "チーム",
  "nav.settings": "設定",
  "button.login": "ログイン",
  "button.register": "登録",
  "button.logout": "ログアウト",
  "theme.light": "ライト",
  "theme.dark": "ダーク",
  "theme.ocean": "オーシャン",
  "theme.forest": "フォレスト"
}
```

#### 15.3.4 语言切换实现

```typescript
// ============================================
// 语言切换 Hook
// ============================================

import { useTranslation } from 'react-i18next';
import { useState, useEffect } from 'react';

export const useLanguage = () => {
  const { i18n } = useTranslation();
  const [currentLang, setCurrentLang] = useState('zh-CN');

  useEffect(() => {
    // 从 localStorage 读取保存的语言偏好
    const savedLang = localStorage.getItem('preferred-language');
    if (savedLang && SUPPORTED_LANGUAGES.find(l => l.code === savedLang)) {
      setCurrentLang(savedLang);
      i18n.changeLanguage(savedLang);
    }
  }, []);

  const changeLanguage = (langCode: LanguageCode) => {
    setCurrentLang(langCode);
    i18n.changeLanguage(langCode);
    localStorage.setItem('preferred-language', langCode);

    // 更新 HTML lang 属性
    document.documentElement.lang = langCode;
  };

  return {
    currentLang,
    changeLanguage,
    languages: SUPPORTED_LANGUAGES
  };
};

// ============================================
// 语言切换器组件
// ============================================

import { Select, SelectContent, SelectItem, SelectTrigger } from '@/components/ui/select';

export function LanguageSwitcher() {
  const { currentLang, changeLanguage, languages } = useLanguage();

  return (
    <Select value={currentLang} onValueChange={changeLanguage}>
      <SelectTrigger className="w-[140px]">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {languages.map((lang) => (
          <SelectItem key={lang.code} value={lang.code}>
            <span className="mr-2">{lang.flag}</span>
            {lang.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
```

#### 15.3.2 页脚组件 (Footer Component)

```typescript
// ============================================
// 页脚组件
// ============================================

import { Link } from 'react-router-dom';
import { Github, MessageCircle, Video } from 'lucide-react';

interface FooterLink {
  label: string;
  href: string;
}

interface SocialMedia {
  name: string;
  icon: React.ReactNode;
  href: string;
  ariaLabel: string;
}

interface FilingInfo {
  icp: string;
  publicSecurity: string;
}

const FOOTER_LINKS: FooterLink[] = [
  { label: '关于', href: '/about' },
  { label: '隐私政策', href: '/privacy' },
  { label: '服务条款', href: '/terms' },
  { label: '帮助中心', href: '/help' },
  { label: '联系我们', href: '/contact' }
];

const SOCIAL_MEDIA: SocialMedia[] = [
  {
    name: 'douyin',
    icon: <Video className="w-5 h-5" />,
    href: 'https://douyin.com/sillymd',
    ariaLabel: '抖音'
  },
  {
    name: 'xiaohongshu',
    icon: <MessageCircle className="w-5 h-5" />,
    href: 'https://xiaohongshu.com/user/sillymd',
    ariaLabel: '小红书'
  },
  {
    name: 'video_account',
    icon: <Video className="w-5 h-5" />,
    href: 'https://weixin.qq.com/sillymd/video',
    ariaLabel: '视频号'
  },
  {
    name: 'github',
    icon: <Github className="w-5 h-5" />,
    href: 'https://github.com/sillymd',
    ariaLabel: 'GitHub'
  }
];

const FILING_INFO: FilingInfo = {
  icp: '沪ICP备2025133866号-1',
  publicSecurity: '沪公网安备 33010002000000号'
};

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-gray-300 mt-auto">
      <div className="container mx-auto px-6 py-8">
        {/* 快速链接 */}
        <div className="flex flex-wrap justify-center gap-6 mb-6">
          {FOOTER_LINKS.map((link) => (
            <Link
              key={link.href}
              to={link.href}
              className="text-gray-400 hover:text-white transition-colors duration-200"
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* 社交媒体 */}
        <div className="flex justify-center gap-6 mb-6">
          {SOCIAL_MEDIA.map((social) => (
            <a
              key={social.name}
              href={social.href}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={social.ariaLabel}
              className="text-gray-400 hover:text-white transition-colors duration-200"
            >
              {social.icon}
            </a>
          ))}
        </div>

        {/* 备案信息 */}
        <div className="text-center text-sm text-gray-500">
          <p className="mb-2">
            © {currentYear} SillyMD. All rights reserved.
          </p>
          <div className="flex justify-center gap-4">
            <a
              href="https://beian.miit.gov.cn/"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-gray-400 transition-colors"
            >
              {FILING_INFO.icp}
            </a>
            <span>|</span>
            <span>{FILING_INFO.publicSecurity}</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

// ============================================
// 多语言页脚配置
// ============================================

import { useTranslation } from 'react-i18next';

export function FooterWithI18n() {
  const { t } = useTranslation();

  const FOOTER_LINKS_I18N: Record<string, FooterLink[]> = {
    zh: [
      { label: t('footer.about'), href: '/about' },
      { label: t('footer.privacy'), href: '/privacy' },
      { label: t('footer.terms'), href: '/terms' },
      { label: t('footer.help'), href: '/help' },
      { label: t('footer.contact'), href: '/contact' }
    ],
    en: [
      { label: 'About', href: '/about' },
      { label: 'Privacy', href: '/privacy' },
      { label: 'Terms', href: '/terms' },
      { label: 'Help', href: '/help' },
      { label: 'Contact', href: '/contact' }
    ]
  };

  return (
    <footer className="bg-gray-900 text-gray-300 mt-auto">
      <div className="container mx-auto px-6 py-8">
        <div className="flex flex-wrap justify-center gap-6 mb-6">
          {FOOTER_LINKS_I18N[useLanguage().currentLang]?.map((link) => (
            <Link
              key={link.href}
              to={link.href}
              className="text-gray-400 hover:text-white transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* 其余部分同上 */}
        <div className="flex justify-center gap-6 mb-6">
          {SOCIAL_MEDIA.map((social) => (
            <a
              key={social.name}
              href={social.href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition-colors"
            >
              {social.icon}
            </a>
          ))}
        </div>

        <div className="text-center text-sm text-gray-500">
          <p className="mb-2">
            © {new Date().getFullYear()} SillyMD. {t('footer.rights')}
          </p>
          <div className="flex justify-center gap-4">
            <a
              href="https://beian.miit.gov.cn/"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-gray-400 transition-colors"
            >
              {FILING_INFO.icp}
            </a>
            <span>|</span>
            <span>{FILING_INFO.publicSecurity}</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
```

### 15.4 认证系统

#### 15.4.1 支持的登录方式

```typescript
// ============================================
// 认证方式配置
// ============================================

export const AUTH_PROVIDERS = {
  EMAIL: {
    id: 'email',
    name: '邮箱登录',
    icon: '✉️',
    enabled: true,
    priority: 1
  },
  PHONE: {
    id: 'phone',
    name: '手机登录',
    icon: '📱',
    enabled: true,
    priority: 2
  },
  GITHUB: {
    id: 'github',
    name: 'GitHub',
    icon: '🐙',
    enabled: true,
    priority: 3,
    oauthUrl: '/api/v1/auth/github'
  },
  GOOGLE: {
    id: 'google',
    name: 'Google',
    icon: '🔵',
    enabled: true,
    priority: 4,
    oauthUrl: '/api/v1/auth/google'
  },
  WECHAT: {
    id: 'wechat',
    name: '微信',
    icon: '💬',
    enabled: true,
    priority: 5,
    oauthUrl: '/api/v1/auth/wechat'
  },
  ENTERPRISE_WECHAT: {
    id: 'enterprise-wechat',
    name: '企业微信',
    icon: '🏢',
    enabled: true,
    priority: 6,
    oauthUrl: '/api/v1/auth/work-wechat'
  }
} as const;
```

#### 15.4.2 登录页面组件

```typescript
// ============================================
// 登录页面组件
// ============================================

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export function LoginPage() {
  const [isLoading, setIsLoading] = useState(false);

  const handleEmailLogin = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      // 邮箱登录逻辑
      await authApi.loginWithEmail(email, password);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOAuthLogin = (provider: string) => {
    // OAuth 登录跳转
    window.location.href = `/api/v1/auth/${provider}`;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Logo */}
          <div className="text-center mb-8">
            <img src="/logo.svg" alt="SillyMD" className="h-12 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900">欢迎回来</h1>
            <p className="text-gray-600 mt-2">登录到 SillyMD Skills 托管中心</p>
          </div>

          {/* 认证选项卡 */}
          <Tabs defaultValue="email" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="email">邮箱登录</TabsTrigger>
              <TabsTrigger value="phone">手机登录</TabsTrigger>
            </TabsList>

            {/* 邮箱登录 */}
            <TabsContent value="email" className="mt-6">
              <EmailLoginForm onSubmit={handleEmailLogin} isLoading={isLoading} />
            </TabsContent>

            {/* 手机登录 */}
            <TabsContent value="phone" className="mt-6">
              <PhoneLoginFlow isLoading={isLoading} />
            </TabsContent>
          </Tabs>

          {/* 分隔线 */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">或</span>
            </div>
          </div>

          {/* OAuth 登录按钮 */}
          <div className="space-y-3">
            <OAuthButton
              provider="github"
              onClick={() => handleOAuthLogin('github')}
            />
            <OAuthButton
              provider="google"
              onClick={() => handleOAuthLogin('google')}
            />
            <OAuthButton
              provider="wechat"
              onClick={() => handleOAuthLogin('wechat')}
            />
          </div>

          {/* 注册链接 */}
          <p className="text-center text-sm text-gray-600 mt-6">
            还没有账号？
            <a href="/register" className="text-blue-600 hover:text-blue-700 font-medium ml-1">
              立即注册
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

// ============================================
// OAuth 登录按钮组件
// ============================================

interface OAuthButtonProps {
  provider: 'github' | 'google' | 'wechat' | 'enterprise-wechat';
  onClick: () => void;
}

function OAuthButton({ provider, onClick }: OAuthButtonProps) {
  const config = AUTH_PROVIDERS[provider.toUpperCase()];

  if (!config.enabled) return null;

  return (
    <Button
      type="button"
      variant="outline"
      className="w-full"
      onClick={onClick}
    >
      <span className="text-xl mr-2">{config.icon}</span>
      使用 {config.name} 登录
    </Button>
  );
}

// ============================================
// 手机登录流程组件
// ============================================

function PhoneLoginFlow({ isLoading }: { isLoading: boolean }) {
  const [step, setStep] = useState<'input' | 'verify'>('input');
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');

  const handleSendCode = async () => {
    isLoading = true;
    // 发送验证码逻辑
    await authApi.sendVerificationCode(phone);
    setStep('verify');
  };

  const handleVerifyCode = async () => {
    isLoading = true;
    // 验证码验证逻辑
    await authApi.verifyCode(phone, code);
  };

  if (step === 'input') {
    return (
      <div className="space-y-4">
        <Input
          type="tel"
          placeholder="请输入手机号"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
        />
        <Button
          className="w-full"
          onClick={handleSendCode}
          disabled={!phone || phone.length < 11}
        >
          发送验证码
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Input
          type="text"
          placeholder="验证码"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          maxLength={6}
        />
        <Button
          variant="outline"
          onClick={handleSendCode}
          disabled={isLoading}
        >
          重新发送
        </Button>
      </div>
      <Button
        className="w-full"
        onClick={handleVerifyCode}
        disabled={!code || code.length < 6}
      >
        登录
      </Button>
    </div>
  );
}
```

#### 15.4.3 注册页面

```typescript
// ============================================
// 注册页面组件
// ============================================

export function RegisterPage() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    phone: '',
    verificationCode: ''
  });

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* 进度指示器 */}
          <div className="flex items-center justify-center mb-8">
            <div className={`flex items-center ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className="w-8 h-8 rounded-full border-2 flex items-center justify-center font-semibold">1</div>
              <div className="w-16 h-1 border-t-2 mx-2"></div>
            </div>
            <div className={`flex items-center ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className="w-8 h-8 rounded-full border-2 flex items-center justify-center font-semibold">2</div>
              <div className="w-16 h-1 border-t-2 mx-2"></div>
            </div>
            <div className={`flex items-center ${step >= 3 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className="w-8 h-8 rounded-full border-2 flex items-center justify-center font-semibold">3</div>
            </div>
          </div>

          {/* 步骤 1: 基本信息 */}
          {step === 1 && (
            <>
              <h2 className="text-2xl font-bold text-center mb-6">创建账号</h2>
              <RegisterStep1
                data={formData}
                onChange={setFormData}
                onNext={() => setStep(2)}
              />
            </>
          )}

          {/* 步骤 2: 验证 */}
          {step === 2 && (
            <>
              <h2 className="text-2xl font-bold text-center mb-6">验证联系方式</h2>
              <RegisterStep2
                data={formData}
                onChange={setFormData}
                onNext={() => setStep(3)}
                onBack={() => setStep(1)}
              />
            </>
          )}

          {/* 步骤 3: 完成 */}
          {step === 3 && (
            <>
              <h2 className="text-2xl font-bold text-center mb-6">欢迎加入!</h2>
              <RegisterStep3
                data={formData}
                onChange={setFormData}
                onBack={() => setStep(2)}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
```

### 15.5 主题切换器

#### 15.5.1 主题选择组件

```typescript
// ============================================
// 主题切换组件
// ============================================

import { useState } from 'react';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Button } from '@/components/ui/button';

export function ThemeSwitcher() {
  const [theme, setTheme] = useState<'light' | 'dark' | 'ocean' | 'forest' | 'sunset' | 'custom'>('light');

  const themes = [
    { id: 'light', name: '明亮', preview: 'bg-white border-gray-200' },
    { id: 'dark', name: '暗黑', preview: 'bg-gray-900 border-gray-700' },
    { id: 'ocean', name: '海洋', preview: 'bg-blue-50 border-blue-200' },
    { id: 'forest', name: '森林', preview: 'bg-green-50 border-green-200' },
    { id: 'sunset', name: '日落', preview: 'bg-orange-50 border-orange-200' },
    { id: 'purple', name: '紫韵', preview: 'bg-purple-50 border-purple-200' },
    { id: 'rose', name: '玫瑰', preview: 'bg-pink-50 border-pink-200' },
  ];

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="icon">
          <PaletteIcon className="h-5 w-5" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-64 p-4">
        <h3 className="font-semibold mb-3">选择主题</h3>
        <div className="grid grid-cols-4 gap-2">
          {themes.map((t) => (
            <button
              key={t.id}
              onClick={() => setTheme(t.id)}
              className={`
                w-12 h-12 rounded-lg border-2 ${t.preview}
                ${theme === t.id ? 'ring-2 ring-offset-2 ring-blue-500' : ''}
                hover:opacity-80 transition-opacity
              `}
              title={t.name}
            />
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}
```

#### 15.5.2 主题 Provider

```typescript
// ============================================
// 主题 Provider
// ============================================

import { createContext, useContext, useEffect, ReactNode } from 'react';

type Theme = 'light' | 'dark' | 'ocean' | 'forest' | 'sunset' | 'purple' | 'rose' | 'custom';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>('light');

  useEffect(() => {
    // 从 localStorage 读取主题偏好
    const savedTheme = localStorage.getItem('theme') as Theme;
    if (savedTheme) {
      setTheme(savedTheme);
    }
  }, []);

  const setTheme = (theme: Theme) => {
    setThemeState(theme);
    localStorage.setItem('theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
```

### 15.6 响应式设计

#### 15.6.1 断点配置

```typescript
// ============================================
// Tailwind CSS 断点配置
// ============================================

const breakpoints = {
  xs: '0px',      // 移动设备 (< 640px)
  sm: '640px',     // 平板竖屏 (≥ 640px)
  md: '768px',     // 平板横屏 (≥ 768px)
  lg: '1024px',    // 笔记本 (≥ 1024px)
  xl: '1280px',    // 桌面 (≥ 1280px)
  '2xl': '1536px', // 大屏 (≥ 1536px)
};

// ============================================
// 响应式工具类
// ============================================

/*
  移动优先策略：

  - 默认样式为移动端
  - 使用 sm:、md:、lg:、xl:、2xl: 前缀适配更大屏幕

  示例：
  <div className="w-full md:w-1/2 lg:w-1/3">
    - 移动端: 100% 宽度
    - 平板及以上: 50% 宽度
    - 桌面及以上: 33% 宽度
  </div>
*/
```

#### 15.6.2 响应式导航

```typescript
// ============================================
// 响应式导航栏
// ============================================

export function ResponsiveNav() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <nav className="bg-white border-b sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <a href="/" className="flex items-center">
              <img src="/logo.svg" alt="SillyMD" className="h-8" />
            </a>
          </div>

          {/* 桌面导航 */}
          <div className="hidden md:flex md:items-center md:space-x-6">
            <a href="/explore" className="text-gray-700 hover:text-blue-600">探索</a>
            <a href="/pricing" className="text-gray-700 hover:text-blue-600">定价</a>
            <a href="/docs" className="text-gray-700 hover:text-blue-600">文档</a>
            <a href="/login" className="text-gray-700 hover:text-blue-600">登录</a>
            <a href="/register" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
              注册
            </a>
          </div>

          {/* 移动端菜单按钮 */}
          <div className="md:hidden">
            <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
              <MenuIcon className="h-6 w-6" />
            </button>
          </div>
        </div>
      </div>

      {/* 移动端菜单 */}
      {isMobileMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1">
            <a href="/explore" className="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">
              探索
            </a>
            <a href="/pricing" className="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">
              定价
            </a>
            <a href="/docs" className="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">
              文档
            </a>
            <a href="/login" className="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">
              登录
            </a>
            <a href="/register" className="block px-3 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700">
              注册
            </a>
          </div>
        </div>
      )}
    </nav>
  );
}
```

### 15.7 页面路由配置

```typescript
// ============================================
// 路由配置
// ============================================

import { createBrowserRouter } from 'react-router-dom';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        path: '/',
        element: <HomePage />
      },
      {
        path: '/explore',
        element: <ExplorePage />
      },
      {
        path: '/skills/:skillId',
        element: <SkillDetailPage />
      },
      {
        path: '/login',
        element: <LoginPage />
      },
      {
        path: '/register',
        element: <RegisterPage />
      },
      {
        path: '/dashboard',
        element: <ProtectedRoute />,
        children: [
          {
            path: '',
            element: <DashboardHome />
          },
          {
            path: 'skills',
            element: <MySkillsPage />
          },
          {
            path: 'settings',
            element: <SettingsPage />
          }
        ]
      },
      {
        path: '/teams/:teamSlug',
        element: <TeamPage />,
        children: [
          {
            path: '',
            element: <TeamOverview />
          },
          {
            path: 'projects/:projectSlug',
            element: <ProjectPage />
          }
        ]
      },
      {
        path: '/admin',
        element: <AdminRoute />,
        children: [
          {
            path: '',
            element: <AdminDashboard />
          },
          {
            path: 'skills',
            element: <SkillReview />
          },
          {
            path: 'users',
            element: <UserManagement />
          }
        ]
      }
    ]
  },
  {
    path: '*',
    element: <NotFoundPage />
  }
]);
```

### 15.8 性能优化

```typescript
// ============================================
// 性能优化配置
// ============================================

// 1. 代码分割 (Code Splitting)
import { lazy, Suspense } from 'react';

const DashboardHome = lazy(() => import('./pages/DashboardHome'));
const SkillDetailPage = lazy(() => import('./pages/SkillDetailPage'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<DashboardHome />} />
        <Route path="/skills/:id" element={<SkillDetailPage />} />
      </Routes>
    </Suspense>
  );
}

// 2. 图片懒加载
import { LazyLoadImage } from '@/components/LazyLoadImage';

<LazyLoadImage
  src="/hero-image.jpg"
  alt="Hero"
  className="w-full h-64 object-cover"
  loading="lazy"
/>

// 3. 虚拟列表 (长列表优化)
import { useVirtualizer } from '@tanstack/react-virtual';

function SkillList({ skills }: { skills: Skill[] }) {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: skills.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 200, // 预估每项高度
    overscan: 5
  });

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto">
      <div style={{ height: `${rowVirtualizer.getTotalSize()}px` }}>
        {rowVirtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={virtualRow.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`
            }}
          >
            <SkillCard skill={skills[virtualRow.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

