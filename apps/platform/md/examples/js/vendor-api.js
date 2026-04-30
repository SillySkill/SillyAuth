/**
 * SillyMD 供应商申请 API 客户端
 */

const VendorAPI = {
  config: {
    // 使用全局配置或默认值
    get apiBaseUrl() {
      return typeof CONFIG !== 'undefined' ? `${CONFIG.API_BASE}/api/v1` : 'http://47.96.133.238:8000/api/v1';
    },
    get timeout() {
      return typeof CONFIG !== 'undefined' ? CONFIG.API_TIMEOUT : 15000;
    }
  },

  /**
   * 获取认证 token - 使用全局配置
   */
  getToken() {
    const tokenKey = typeof CONFIG !== 'undefined' ? CONFIG.TOKEN_KEY : 'token';
    return localStorage.getItem(tokenKey) || sessionStorage.getItem(tokenKey);
  },

  /**
   * 通用请求方法
   */
  async request(endpoint, options = {}) {
    const token = this.getToken();
    const url = `${this.config.apiBaseUrl}${endpoint}`;

    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: AbortSignal.timeout(this.config.timeout)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || '请求失败');
      }

      return data;
    } catch (error) {
// console.'API 请求失败:', error);
      throw error;
    }
  },

  // ==================== 供应商申请相关 ====================

  /**
   * 提交供应商申请
   */
  async submitApplication(data) {
    return this.request('/vendor-applications', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * 获取用户的申请状态
   */
  async getApplicationStatus() {
    return this.request('/vendor-applications/status');
  },

  /**
   * 获取所有供应商申请（管理员）
   */
  async getAllApplications(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/vendor-applications?${queryString}`);
  },

  /**
   * 审核供应商申请（管理员）
   */
  async reviewApplication(id, data) {
    return this.request(`/vendor-applications/${id}/review`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  /**
   * 获取供应商等级配置
   */
  async getVendorTiers() {
    return this.request('/vendor-applications/tiers');
  },

  /**
   * 获取用户供应商认证状态
   */
  async getVendorStatus() {
    return this.request('/vendor-applications/vendor-status');
  },

  // ==================== 项目管理相关 ====================

  /**
   * 获取项目列表
   */
  async getProjects(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/projects?${queryString}`);
  },

  /**
   * 获取项目详情
   */
  async getProjectById(id) {
    return this.request(`/projects/${id}`);
  },

  /**
   * 创建项目
   */
  async createProject(data) {
    return this.request('/projects', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * 更新项目
   */
  async updateProject(id, data) {
    return this.request(`/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  /**
   * 删除项目
   */
  async deleteProject(id) {
    return this.request(`/projects/${id}`, {
      method: 'DELETE'
    });
  },

  /**
   * 添加项目 Skill
   */
  async addProjectSkill(id, data) {
    return this.request(`/projects/${id}/skills`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * 移除项目 Skill
   */
  async removeProjectSkill(id, skillId) {
    return this.request(`/projects/${id}/skills/${skillId}`, {
      method: 'DELETE'
    });
  },

  /**
   * 创建项目里程碑
   */
  async createMilestone(id, data) {
    return this.request(`/projects/${id}/milestones`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // ==================== 市场相关 ====================

  /**
   * 获取供应商列表
   */
  async getMarketVendors(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/market/vendors?${queryString}`);
  },

  /**
   * 获取供应商详情
   */
  async getVendorProfile(username) {
    return this.request(`/market/vendors/${username}`);
  },

  /**
   * 获取市场统计数据
   */
  async getMarketStats() {
    return this.request('/market/stats');
  },

  /**
   * 搜索产品
   */
  async searchProducts(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/market/products?${queryString}`);
  },

  /**
   * 获取产品详情
   */
  async getProductDetail(id) {
    return this.request(`/market/products/${id}`);
  }
};

// 导出到全局
if (typeof window !== 'undefined') {
  window.VendorAPI = VendorAPI;
}
