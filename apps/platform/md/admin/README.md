# SillyMD CMS Admin Panel

管理后台前端应用，基于 React + Vite + Ant Design 构建。

## 功能模块

- **仪表盘** - 数据统计和概览
- **内容管理** - 页面内容编辑和发布
- **导航管理** - 网站导航菜单配置
- **轮播图管理** - 首页轮播图配置
- **技能管理** - 技能栈展示管理
- **供应商管理** - 合作伙伴管理
- **SEO设置** - 搜索引擎优化配置
- **多语言管理** - 国际化翻译管理
- **用户管理** - 用户和权限管理

## 技术栈

- React 18
- TypeScript
- Vite 5
- Ant Design 5
- React Router 6
- Zustand
- Axios
- React Quill

## 开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 环境变量

参见 `.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:3001/api/v1
VITE_UPLOAD_URL=http://localhost:3001/uploads
```

## 目录结构

```
src/
├── api/              # API 接口
├── components/       # 公共组件
├── pages/           # 页面组件
├── stores/          # 状态管理
├── utils/           # 工具函数
├── types/           # TypeScript 类型
├── App.tsx
└── main.tsx
```

## 页面说明

### Dashboard（仪表盘）
显示系统整体统计数据和最近活动日志。

### ContentManagement（内容管理）
- 创建、编辑、删除内容
- 富文本编辑器
- 内容发布流程
- 版本历史记录

### NavigationEdit（导航管理）
- 树形导航结构
- 拖拽排序
- 图标选择

### CarouselEdit（轮播图管理）
- 图片/视频上传
- 链接配置
- 启用/禁用控制

### SkillsManagement（技能管理）
- 技能分类
- 熟练度可视化

### VendorManagement（供应商管理）
- Logo上传
- 网站链接
- 排序管理

### SEOSettings（SEO设置）
- Meta标签配置
- Open Graph设置
- Schema.org数据

### I18nManagement（多语言管理）
- 翻译键值对编辑
- 语言切换

### UserManagement（用户管理）
- 用户CRUD
- 角色权限分配
- 状态管理

## 组件说明

### MainLayout
主布局组件，包含侧边栏导航和顶部栏。

### 表单组件
所有管理页面都使用 Ant Design 的 Form 组件进行数据验证和提交。

### 表格组件
使用 Ant Design 的 Table 组件展示数据列表，支持分页、排序、筛选。

## 状态管理

使用 Zustand 进行全局状态管理：

```typescript
// authStore.ts
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      setAuth: (token, user) => set({ token, user, isAuthenticated: true }),
      clearAuth: () => set({ token: null, user: null, isAuthenticated: false }),
    }),
    { name: 'auth-storage' }
  )
);
```

## API 调用

统一的 Axios 实例，自动处理认证和错误：

```typescript
// api/index.ts
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
});

// 请求拦截器 - 添加 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 错误处理逻辑
  }
);
```

## 路由配置

使用 React Router v6：

```typescript
<Routes>
  <Route path="/login" element={<Login />} />
  <Route path="/" element={<PrivateRoute><MainLayout /></PrivateRoute>}>
    <Route path="dashboard" element={<Dashboard />} />
    <Route path="content" element={<ContentManagement />} />
    {/* 其他路由... */}
  </Route>
</Routes>
```

## 认证流程

1. 用户登录后，后端返回 JWT token
2. Token 存储在 localStorage
3. 后续请求自动在 header 中携带 token
4. token 过期后自动跳转登录页

## 开发建议

1. 遵循 ESLint 规则
2. 使用 TypeScript 类型检查
3. 组件使用函数式组件 + Hooks
4. 合理拆分组件和逻辑
5. 使用 Ant Design 组件保持一致性

## 构建部署

```bash
# 构建
npm run build

# 输出目录：dist/
# 将 dist/ 目录部署到静态服务器
```
