// ============================================
// 全局配置文件 - 统一API配置
// ============================================

/**
 * 获取当前页面的基础URL（协议+域名+端口）
 * @returns {string} 基础URL，如 https://jcoding.chat
 */
function getBaseUrl() {
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  const port = window.location.port ? `:${window.location.port}` : '';
  return `${protocol}//${hostname}${port}`;
}

/**
 * 全局配置对象
 * 所有前端页面都应使用此配置文件中的API地址和参数
 */
const CONFIG = {
  // API基础地址 - 动态获取当前域名
  API_BASE: getBaseUrl(),

  // Token存储键名
  TOKEN_KEY: 'access_token',

  // API请求超时时间（毫秒）
  API_TIMEOUT: 10000,

  // 请求重试次数
  RETRY_COUNT: 3,

  // 刷新Token键名
  REFRESH_TOKEN_KEY: 'refresh_token',

  // 用户信息存储键名
  USER_KEY: 'user',

  // API版本
  API_VERSION: 'v1'
};

/**
 * 获取API基础URL
 * @param {string} version - API版本（可选）
 * @returns {string} 完整的API基础URL
 */
function getApiBaseUrl(version = CONFIG.API_VERSION) {
  return `${CONFIG.API_BASE}/api/${version}`;
}

/**
 * 获取Token
 * @returns {string|null} Token或null
 */
function getToken() {
  return localStorage.getItem(CONFIG.TOKEN_KEY) || sessionStorage.getItem(CONFIG.TOKEN_KEY);
}

/**
 * 获取刷新Token
 * @returns {string|null} 刷新Token或null
 */
function getRefreshToken() {
  return localStorage.getItem(CONFIG.REFRESH_TOKEN_KEY) || sessionStorage.getItem(CONFIG.REFRESH_TOKEN_KEY);
}

/**
 * 保存Token
 * @param {string} accessToken - 访问Token
 * @param {string} refreshToken - 刷新Token
 * @param {boolean} remember - 是否记住登录状态
 */
function saveToken(accessToken, refreshToken, remember = false) {
  if (remember) {
    localStorage.setItem(CONFIG.TOKEN_KEY, accessToken);
    localStorage.setItem(CONFIG.REFRESH_TOKEN_KEY, refreshToken);
  } else {
    sessionStorage.setItem(CONFIG.TOKEN_KEY, accessToken);
    sessionStorage.setItem(CONFIG.REFRESH_TOKEN_KEY, refreshToken);
  }
}

/**
 * 清除Token
 */
function clearToken() {
  localStorage.removeItem(CONFIG.TOKEN_KEY);
  localStorage.removeItem(CONFIG.REFRESH_TOKEN_KEY);
  sessionStorage.removeItem(CONFIG.TOKEN_KEY);
  sessionStorage.removeItem(CONFIG.REFRESH_TOKEN_KEY);
}

/**
 * 构建带认证的请求头
 * @param {Object} customHeaders - 自定义请求头
 * @returns {Object} 包含认证信息的请求头
 */
function getAuthHeaders(customHeaders = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...customHeaders
  };

  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}

/**
 * 统一的fetch封装（带认证）
 * @param {string} url - 请求URL
 * @param {Object} options - fetch选项
 * @returns {Promise} fetch Promise
 */
async function authenticatedFetch(url, options = {}) {
  const headers = getAuthHeaders(options.headers);

  const finalOptions = {
    ...options,
    headers
  };

  const response = await fetch(url, finalOptions);

  // 处理401未授权
  if (response.status === 401) {
    clearToken();
    window.location.href = '/examples/login.html';
    throw new Error('未授权，请重新登录');
  }

  return response;
}

// ============================================
// 文件代理URL生成函数
// ============================================

/**
 * 生成文件代理URL（用于加载OSS资源，避免CORS问题）
 * @param {string} path - OSS文件相对路径，如 hero/lay-1080.mp4
 * @returns {string} 完整的文件代理URL，如 https://jcoding.chat/api/file/hero/lay-1080.mp4
 * @example
 *   getFileProxyUrl('hero/lay-1080.mp4')
 *   // 返回: 'https://jcoding.chat/api/file/hero/lay-1080.mp4'
 */
function getFileProxyUrl(path) {
  // 移除前导斜杠和sillymd前缀（如果存在）
  const normalizedPath = path
    .replace(/^\/+/, '')           // 移除开头的斜杠
    .replace(/^sillymd\//, '');     // 移除sillymd/前缀

  // 使用当前域名构建完整URL
  // URL格式: /api/file/{path}
  // 实际获取OSS: https://jc-st.oss-cn-shanghai.aliyuncs.com/sillymd/{path}
  return `${getBaseUrl()}/api/file/${normalizedPath}`;
}

// ============================================
// OSS资源配置（统一管理所有OSS资源路径）
// ============================================

const OSS_RESOURCES = {
  // 轮播图资源
  HERO: {
    // 视频1: lay-1080.mp4
    VIDEO_1: () => getFileProxyUrl('hero/lay-1080.mp4'),

    // 视频2: man-1080.mp4
    VIDEO_2: () => getFileProxyUrl('hero/man-1080.mp4'),

    // 图片3: chapter3-features.png
    IMAGE_3: () => getFileProxyUrl('hero/chapter3-features.png'),

    // 视频占位图
    POSTER_1: 'image/hero/slide1.svg',
    POSTER_2: 'image/hero/slide2.svg',
    POSTER_3: 'image/hero/slide3.svg',
  },

  // Logo
  LOGO: 'image/logo-1.png',

  // 其他常用资源可以在这里添加...
};

// ============================================
// 导出到 window 对象（全局访问）
// ============================================

// 对于非模块化环境，也导出到window对象
if (typeof window !== 'undefined') {
  window.CONFIG = CONFIG;
  window.getApiBaseUrl = getApiBaseUrl;
  window.getToken = getToken;
  window.getRefreshToken = getRefreshToken;
  window.saveToken = saveToken;
  window.clearToken = clearToken;
  window.getAuthHeaders = getAuthHeaders;
  window.authenticatedFetch = authenticatedFetch;

  // 导出文件代理URL生成函数和OSS资源配置
  window.getFileProxyUrl = getFileProxyUrl;
  window.getBaseUrl = getBaseUrl;
  window.OSS_RESOURCES = OSS_RESOURCES;
}

// 打印配置信息（调试用）
// // console.log('✅ 全局配置已加载:', {
  API_BASE: CONFIG.API_BASE,
  API_TIMEOUT: CONFIG.API_TIMEOUT,
  RETRY_COUNT: CONFIG.RETRY_COUNT
});
