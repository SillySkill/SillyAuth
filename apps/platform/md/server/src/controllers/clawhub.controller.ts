/**
 * Clawhub 控制器
 * 处理 Clawhub 热门应用翻译相关业务逻辑
 */

import { Request, Response } from 'express';

// Clawhub API 基础 URL
const CLAWHUB_API_BASE = 'https://clawhub.ai/api';

// 简单的内存缓存
interface CacheEntry {
  data: any;
  timestamp: number;
}

const cache: Map<string, CacheEntry> = new Map();
const CACHE_TTL = 60 * 60 * 1000; // 1小时

// 内置热门应用数据（当 API 不可用时的备选）
const BUILTIN_HOT_APPS = [
  {
    slug: 'code-assistant',
    name: 'Code Assistant',
    description: 'AI-powered code completion and refactoring assistant',
    author: 'openclaw',
    version: '1.2.0',
    downloads: 15420,
    stars: 892,
    tags: ['coding', 'ai', 'productivity'],
    icon: 'fa-code',
    category: 'Development'
  },
  {
    slug: 'web-search',
    name: 'Web Search',
    description: 'Search the web for current information and news',
    author: 'openclaw',
    version: '2.0.0',
    downloads: 28350,
    stars: 1243,
    tags: ['search', 'information', 'browsing'],
    icon: 'fa-globe',
    category: 'Information'
  },
  {
    slug: 'file-operations',
    name: 'File Operations',
    description: 'Read, write, and manage files on your system',
    author: 'openclaw',
    version: '1.5.0',
    downloads: 19800,
    stars: 756,
    tags: ['files', 'system', 'storage'],
    icon: 'fa-folder',
    category: 'System'
  },
  {
    slug: 'git-helper',
    name: 'Git Helper',
    description: 'Enhanced Git operations with interactive UI',
    author: 'community',
    version: '1.8.0',
    downloads: 12100,
    stars: 534,
    tags: ['git', 'version-control', 'development'],
    icon: 'fa-code-branch',
    category: 'Development'
  },
  {
    slug: 'translate-pro',
    name: 'Translate Pro',
    description: 'Professional translation with 50+ language support',
    author: 'community',
    version: '2.3.0',
    downloads: 8900,
    stars: 421,
    tags: ['translation', 'languages', 'communication'],
    icon: 'fa-language',
    category: 'Communication'
  },
  {
    slug: 'data-analysis',
    name: 'Data Analysis',
    description: 'Analyze and visualize data with AI insights',
    author: 'openclaw',
    version: '1.1.0',
    downloads: 6700,
    stars: 298,
    tags: ['data', 'analytics', 'visualization'],
    icon: 'fa-chart-bar',
    category: 'Analytics'
  },
  {
    slug: 'docker-manager',
    name: 'Docker Manager',
    description: 'Manage Docker containers and images with ease',
    author: 'community',
    version: '1.4.0',
    downloads: 5400,
    stars: 267,
    tags: ['docker', 'containers', 'devops'],
    icon: 'fa-ship',
    category: 'DevOps'
  },
  {
    slug: 'database-client',
    name: 'Database Client',
    description: 'Connect and query multiple database types',
    author: 'community',
    version: '2.1.0',
    downloads: 4200,
    stars: 189,
    tags: ['database', 'sql', 'nosql'],
    icon: 'fa-database',
    category: 'Development'
  }
];

// 中文翻译映射
const APP_TRANSLATIONS: Record<string, Record<string, string>> = {
  'zh-CN': {
    'Code Assistant': '代码助手',
    'AI-powered code completion and refactoring assistant': 'AI驱动的代码补全和重构助手',
    'Web Search': '网页搜索',
    'Search the web for current information and news': '搜索网络获取最新信息和新闻',
    'File Operations': '文件操作',
    'Read, write, and manage files on your system': '在您的系统上读取、写入和管理文件',
    'Git Helper': 'Git 助手',
    'Enhanced Git operations with interactive UI': '增强型 Git 操作，带有交互式界面',
    'Translate Pro': '翻译专家',
    'Professional translation with 50+ language support': '支持50多种语言的专业翻译',
    'Data Analysis': '数据分析',
    'Analyze and visualize data with AI insights': '使用 AI 洞察分析和可视化数据',
    'Docker Manager': 'Docker 管理器',
    'Manage Docker containers and images with ease': '轻松管理 Docker 容器和镜像',
    'Database Client': '数据库客户端',
    'Connect and query multiple database types': '连接和查询多种数据库类型',
    // Categories
    'Development': '开发',
    'Information': '信息',
    'System': '系统',
    'Communication': '沟通',
    'Analytics': '分析',
    'DevOps': '运维',
    // Tags
    'coding': '编程',
    'ai': '人工智能',
    'productivity': '效率',
    'search': '搜索',
    'information': '信息',
    'browsing': '浏览',
    'files': '文件',
    'system': '系统',
    'storage': '存储',
    'git': 'Git',
    'version-control': '版本控制',
    'translation': '翻译',
    'languages': '语言',
    'communication': '沟通',
    'data': '数据',
    'analytics': '分析',
    'visualization': '可视化',
    'docker': 'Docker',
    'containers': '容器',
    'devops': 'DevOps',
    'database': '数据库',
    'sql': 'SQL',
    'nosql': 'NoSQL'
  }
};

// 获取缓存数据
function getCache(key: string): any | null {
  const entry = cache.get(key);
  if (entry && Date.now() - entry.timestamp < CACHE_TTL) {
    return entry.data;
  }
  cache.delete(key);
  return null;
}

// 设置缓存数据
function setCache(key: string, data: any): void {
  cache.set(key, {
    data,
    timestamp: Date.now()
  });
}

// 翻译文本
function translate(text: string, locale: string): string {
  if (locale === 'en') {
    return text;
  }

  const translations = APP_TRANSLATIONS[locale] || APP_TRANSLATIONS['zh-CN'];
  if (translations && translations[text]) {
    return translations[text];
  }

  // 如果没有找到翻译，尝试翻译成中文再回退到英文
  return text;
}

// 翻译应用对象
function translateApp(app: any, locale: string): any {
  if (locale === 'en') {
    return app;
  }

  const translations = APP_TRANSLATIONS[locale] || APP_TRANSLATIONS['zh-CN'];

  return {
    ...app,
    name: translations[app.name] || app.name,
    description: translations[app.description] || app.description,
    category: translations[app.category] || app.category,
    tags: app.tags.map((tag: string) => translations[tag] || tag)
  };
}

// 获取热门应用
export const getHotApps = async (req: Request, res: Response): Promise<void> => {
  try {
    const locale = (req.query.locale as string) || 'zh-CN';
    const cacheKey = `hot-apps-${locale}`;

    // 检查缓存
    const cachedData = getCache(cacheKey);
    if (cachedData) {
      res.json({
        success: true,
        data: cachedData,
        cached: true
      });
      return;
    }

    // 尝试从 Clawhub API 获取数据
    let apps = BUILTIN_HOT_APPS;

    try {
      const response = await fetch(`${CLAWHUB_API_BASE}/skills/popular?limit=20`, {
        headers: {
          'Accept': 'application/json'
        },
        signal: AbortSignal.timeout(3000) // 3秒超时
      });

      if (response.ok) {
        const data = await response.json();
        if (data.skills && Array.isArray(data.skills)) {
          apps = data.skills.map((skill: any) => ({
            slug: skill.slug || skill.name?.toLowerCase().replace(/\s+/g, '-'),
            name: skill.name,
            description: skill.description,
            author: skill.author || 'community',
            version: skill.version || '1.0.0',
            downloads: skill.downloads || 0,
            stars: skill.stars || 0,
            tags: skill.tags || [],
            icon: skill.icon || 'fa-cube',
            category: skill.category || 'General'
          }));
        }
      }
    } catch (apiError) {
      console.log('Clawhub API 不可用，使用内置数据');
    }

    // 翻译应用数据
    const translatedApps = apps.map((app: any) => translateApp(app, locale));

    // 缓存结果
    setCache(cacheKey, translatedApps);

    res.json({
      success: true,
      data: translatedApps,
      cached: false
    });
  } catch (error) {
    console.error('获取热门应用失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'GET_HOT_APPS_FAILED',
        message: '获取热门应用失败'
      }
    });
  }
};

// 搜索应用
export const searchApps = async (req: Request, res: Response): Promise<void> => {
  try {
    const { q } = req.query;
    const locale = (req.query.locale as string) || 'zh-CN';

    if (!q || typeof q !== 'string') {
      res.status(400).json({
        success: false,
        error: {
          code: 'INVALID_QUERY',
          message: '请提供搜索关键词'
        }
      });
      return;
    }

    const searchTerm = q.toLowerCase();
    const cacheKey = `search-${searchTerm}-${locale}`;

    // 检查缓存
    const cachedData = getCache(cacheKey);
    if (cachedData) {
      res.json({
        success: true,
        data: cachedData,
        cached: true
      });
      return;
    }

    // 搜索内置应用
    let results = BUILTIN_HOT_APPS.filter(app =>
      app.name.toLowerCase().includes(searchTerm) ||
      app.description.toLowerCase().includes(searchTerm) ||
      app.tags.some((tag: string) => tag.toLowerCase().includes(searchTerm))
    );

    // 翻译结果
    const translatedResults = results.map((app: any) => translateApp(app, locale));

    // 缓存结果
    setCache(cacheKey, translatedResults);

    res.json({
      success: true,
      data: translatedResults,
      query: q,
      cached: false
    });
  } catch (error) {
    console.error('搜索应用失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'SEARCH_APPS_FAILED',
        message: '搜索应用失败'
      }
    });
  }
};

// 获取应用详情
export const getAppDetails = async (req: Request, res: Response): Promise<void> => {
  try {
    const { slug } = req.params;
    const locale = (req.query.locale as string) || 'zh-CN';
    const cacheKey = `app-${slug}-${locale}`;

    // 检查缓存
    const cachedData = getCache(cacheKey);
    if (cachedData) {
      res.json({
        success: true,
        data: cachedData,
        cached: true
      });
      return;
    }

    // 在内置应用中找到
    const app = BUILTIN_HOT_APPS.find(a => a.slug === slug);

    if (!app) {
      res.status(404).json({
        success: false,
        error: {
          code: 'APP_NOT_FOUND',
          message: '应用不存在'
        }
      });
      return;
    }

    // 翻译应用数据
    const translatedApp = translateApp(app, locale);

    // 缓存结果
    setCache(cacheKey, translatedApp);

    res.json({
      success: true,
      data: translatedApp,
      cached: false
    });
  } catch (error) {
    console.error('获取应用详情失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'GET_APP_DETAILS_FAILED',
        message: '获取应用详情失败'
      }
    });
  }
};

// 清除缓存（管理员）
export const clearCache = async (req: Request, res: Response): Promise<void> => {
  try {
    cache.clear();
    res.json({
      success: true,
      message: '缓存已清除'
    });
  } catch (error) {
    console.error('清除缓存失败:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'CLEAR_CACHE_FAILED',
        message: '清除缓存失败'
      }
    });
  }
};
