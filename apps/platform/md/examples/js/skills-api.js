/**
 * SillyMD Skills API Client
 * 连接真实后端 API �?Skills 功能模块
 */

(function(global) {
  'use strict';

  const SkillsAPI = {
    config: {
      // 使用全局配置或默认值
      get apiBaseUrl() {
        return typeof CONFIG !== 'undefined' ? CONFIG.API_BASE : 'http://47.96.133.238:8000';
      },
      get timeout() {
        return typeof CONFIG !== 'undefined' ? CONFIG.API_TIMEOUT : 15000;
      },
      get retries() {
        return typeof CONFIG !== 'undefined' ? CONFIG.RETRY_COUNT : 3;
      }
    },

    state: {
      currentPage: 1,
      itemsPerPage: 12,
      totalItems: 0,
      currentFilters: {},
      currentSort: 'default',
      cache: null,
      cacheTimestamp: null
    },

    // 缓存时间�?分钟�?    cacheDuration: 2 * 60 * 1000,

    /**
     * 初始�?     */
    async init(options = {}) {
// // console.log('🚀 Skills API 初始�?..');
      Object.assign(this.config, options);

      try {
        await this.loadSkills();
        this.render();
// // console.log('�?Skills 加载完成');
      } catch (error) {
// console.'�?Skills 加载失败:', error);
        this.showError('Skills 加载失败，请稍后重试');
      }
    },

    /**
     * 加载 Skills 数据
     */
    async loadSkills() {
      // 检查缓�?      if (this.isCacheValid()) {
// // console.log('使用缓存数据');
        return this.state.cache;
      }

// // console.log('�?API 加载 Skills...');

      const params = new URLSearchParams({
        status: 'approved',
        limit: 100,
        offset: 0
      });

      // 添加筛选参�?      if (this.state.currentFilters.category) {
        params.append('category', this.state.currentFilters.category);
      }
      if (this.state.currentFilters.type) {
        params.append('type', this.state.currentFilters.type);
      }
      if (this.state.currentFilters.search) {
        // 搜索功能需要后端支持，暂时在前端过�?      }

      const url = `/api/skills?${params.toString()}`;
      const data = await this.fetchWithRetry(url);

      // 前端搜索过滤
      let filteredData = data;
      if (this.state.currentFilters.search) {
        const searchTerm = this.state.currentFilters.search.toLowerCase();
        filteredData = data.filter(skill =>
          skill.name.toLowerCase().includes(searchTerm) ||
          (skill.description && skill.description.toLowerCase().includes(searchTerm)) ||
          skill.category.toLowerCase().includes(searchTerm)
        );
      }

      // 排序
      filteredData = this.sortSkills(filteredData, this.state.currentSort);

      this.state.cache = filteredData;
      this.state.cacheTimestamp = Date.now();
      this.state.totalItems = filteredData.length;

      return filteredData;
    },

    /**
     * 排序 Skills
     */
    sortSkills(skills, sortType) {
      const sorted = [...skills];

      switch(sortType) {
        case 'newest':
          sorted.sort((a, b) => {
            const dateA = a.published_at ? new Date(a.published_at) : new Date(0);
            const dateB = b.published_at ? new Date(b.published_at) : new Date(0);
            return dateB - dateA;
          });
          break;

        case 'downloads':
          sorted.sort((a, b) => (b.download_count || 0) - (a.download_count || 0));
          break;

        case 'rating':
          sorted.sort((a, b) => (b.rating_avg || 0) - (a.rating_avg || 0));
          break;

        case 'price-asc':
          sorted.sort((a, b) => (a.price || 0) - (b.price || 0));
          break;

        case 'price-desc':
          sorted.sort((a, b) => (b.price || 0) - (a.price || 0));
          break;

        case 'default':
        default:
          // 综合排序：评�?+ 下载�?          sorted.sort((a, b) => {
            const scoreA = (a.rating_avg || 0) * 0.4 + Math.log((a.download_count || 0) + 1) * 0.6;
            const scoreB = (b.rating_avg || 0) * 0.4 + Math.log((b.download_count || 0) + 1) * 0.6;
            return scoreB - scoreA;
          });
          break;
      }

      return sorted;
    },

    /**
     * 渲染页面
     */
    render() {
      const skills = this.state.cache;
      const startIndex = (this.state.currentPage - 1) * this.state.itemsPerPage;
      const endIndex = startIndex + this.state.itemsPerPage;
      const pageData = skills.slice(startIndex, endIndex);

      // 渲染 Skills 列表
      this.renderSkillsList(pageData);

      // 渲染统计
      this.renderStats();

      // 渲染分页
      this.renderPagination();

      // 渲染筛选器
      this.renderFilters();
    },

    /**
     * 渲染 Skills 列表
     */
    renderSkillsList(skills) {
      const container = document.querySelector('[data-demo-skills]');
      if (!container) return;

      if (skills.length === 0) {
        container.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px;">
            <i class="fas fa-search" style="font-size: 3rem; color: var(--text-light); margin-bottom: 16px;"></i>
            <p style="color: var(--text-light);">未找到匹配的 Skills</p>
            <button onclick="SkillsAPI.resetFilters()" class="btn btn-primary" style="margin-top: 16px;">清除筛�?/button>
          </div>
        `;
        return;
      }

      container.innerHTML = skills.map(skill => this.createSkillCard(skill)).join('');
    },

    /**
     * 创建 Skill 卡片
     */
    createSkillCard(skill) {
      const priceNum = Number(skill.price || 0);
      const priceDisplay = skill.type === 'free' || priceNum === 0
        ? '<span style="color: var(--accent); font-weight: 600;">免费</span>'
        : `<span style="font-weight: 600;">💎 ${priceNum.toLocaleString()}</span>`;

      const levelBadge = this.getVendorLevelBadge(skill.author_level);
      const categoryIcon = this.getCategoryIcon(skill.category);
      const categoryName = this.getCategoryName(skill.category);

      return `
        <div class="card" style="padding: 24px; transition: all 0.3s; cursor: pointer;"
             onclick="window.location.href='skill-detail.html?id=${skill.skill_id}'">
          <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 12px;">
              <div style="width: 48px; height: 48px; background: rgba(0, 102, 255, 0.1); border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                <i class="fas ${categoryIcon}" style="font-size: 1.5rem; color: var(--primary);"></i>
              </div>
              <div>
                <h3 style="font-size: 1.1rem; font-weight: 600; margin-bottom: 4px;">${skill.name}</h3>
                <span class="tag">${categoryName}</span>
              </div>
            </div>
            ${skill.is_featured ? '<span class="badge badge-success" style="font-size: 0.75rem;"><i class="fas fa-star"></i> 精�?/span>' : ''}
          </div>

          <p style="color: var(--text-light); font-size: 0.9rem; line-height: 1.6; margin-bottom: 16px; min-height: 60px;">
            ${this.truncateText(skill.description, 100)}
          </p>

          <div style="display: flex; align-items: center; gap: 12px; padding-top: 16px; border-top: 1px solid var(--border-light);">
            <img src="${skill.author_avatar || 'https://via.placeholder.com/32'}"
                 alt="${skill.author_username}"
                 style="width: 32px; height: 32px; border-radius: 50%;">
            <div style="flex: 1;">
              <div style="font-size: 0.85rem; font-weight: 500;">${skill.author_username}</div>
              ${levelBadge}
            </div>
            <div style="text-align: right;">
              <div style="font-size: 0.9rem;">${priceDisplay}</div>
            </div>
          </div>

          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-light); font-size: 0.85rem;">
            <div style="display: flex; align-items: center; gap: 6px; color: var(--text-light);">
              <i class="fas fa-star" style="color: #FFC107;"></i>
              <span>${Number(skill.rating_avg || 0).toFixed(1)}</span>
              <span>(${skill.rating_count || 0})</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px; color: var(--text-light);">
              <i class="fas fa-download"></i>
              <span>${(skill.download_count || 0).toLocaleString()}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px; color: var(--text-light);">
              <i class="fas fa-eye"></i>
              <span>${(skill.view_count || 0).toLocaleString()}</span>
            </div>
          </div>
        </div>
      `;
    },

    /**
     * 渲染统计信息
     */
    renderStats() {
      const countEl = document.querySelector('[data-demo-count]');
      if (!countEl) return;

      const startIndex = (this.state.currentPage - 1) * this.state.itemsPerPage;
      const endIndex = Math.min(startIndex + this.state.itemsPerPage, this.state.totalItems);

      countEl.textContent = `显示 ${startIndex + 1}-${endIndex} / �?${this.state.totalItems} �?Skills`;
    },

    /**
     * 渲染分页
     */
    renderPagination() {
      const container = document.querySelector('[data-demo-pagination]');
      if (!container) return;

      const totalPages = Math.ceil(this.state.totalItems / this.state.itemsPerPage);

      if (totalPages <= 1) {
        container.innerHTML = '';
        return;
      }

      let html = '';

      // 上一�?      if (this.state.currentPage > 1) {
        html += `<button onclick="SkillsAPI.goToPage(${this.state.currentPage - 1})" class="btn btn-ghost btn-sm">上一�?/button>`;
      }

      // 页码
      const startPage = Math.max(1, this.state.currentPage - 2);
      const endPage = Math.min(totalPages, this.state.currentPage + 2);

      if (startPage > 1) {
        html += `<button onclick="SkillsAPI.goToPage(1)" class="btn btn-ghost btn-sm">1</button>`;
        if (startPage > 2) {
          html += `<span style="padding: 8px;">...</span>`;
        }
      }

      for (let i = startPage; i <= endPage; i++) {
        const isActive = i === this.state.currentPage ? 'btn-primary' : 'btn-ghost';
        html += `<button onclick="SkillsAPI.goToPage(${i})" class="btn ${isActive} btn-sm">${i}</button>`;
      }

      if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
          html += `<span style="padding: 8px;">...</span>`;
        }
        html += `<button onclick="SkillsAPI.goToPage(${totalPages})" class="btn btn-ghost btn-sm">${totalPages}</button>`;
      }

      // 下一�?      if (this.state.currentPage < totalPages) {
        html += `<button onclick="SkillsAPI.goToPage(${this.state.currentPage + 1})" class="btn btn-ghost btn-sm">下一�?/button>`;
      }

      container.innerHTML = html;
    },

    /**
     * 渲染筛选器
     */
    renderFilters() {
      const container = document.querySelector('[data-demo-filters]');
      if (!container) return;

      container.innerHTML = `
        <div style="margin-bottom: 24px;">
          <label style="display: block; font-size: 0.9rem; font-weight: 600; margin-bottom: 8px;">分类</label>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
              <input type="radio" name="category" value="" ${!this.state.currentFilters.category ? 'checked' : ''}
                     onchange="SkillsAPI.setFilter('category', this.value)">
              <span style="font-size: 0.9rem;">全部分类</span>
            </label>
            ${this.getCategoryOptions()}
          </div>
        </div>

        <div style="margin-bottom: 24px;">
          <label style="display: block; font-size: 0.9rem; font-weight: 600; margin-bottom: 8px;">类型</label>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
              <input type="radio" name="type" value="" ${!this.state.currentFilters.type ? 'checked' : ''}
                     onchange="SkillsAPI.setFilter('type', this.value)">
              <span style="font-size: 0.9rem;">全部类型</span>
            </label>
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
              <input type="radio" name="type" value="free" ${this.state.currentFilters.type === 'free' ? 'checked' : ''}
                     onchange="SkillsAPI.setFilter('type', this.value)">
              <span style="font-size: 0.9rem;">免费</span>
            </label>
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
              <input type="radio" name="type" value="commercial" ${this.state.currentFilters.type === 'commercial' ? 'checked' : ''}
                     onchange="SkillsAPI.setFilter('type', this.value)">
              <span style="font-size: 0.9rem;">付费</span>
            </label>
          </div>
        </div>

        <div>
          <label style="display: block; font-size: 0.9rem; font-weight: 600; margin-bottom: 8px;">评分</label>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
              <input type="radio" name="rating" value="" ${!this.state.currentFilters.rating ? 'checked' : ''}
                     onchange="SkillsAPI.setFilter('rating', this.value)">
              <span style="font-size: 0.9rem;">全部</span>
            </label>
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
              <input type="radio" name="rating" value="4.5" ${this.state.currentFilters.rating === '4.5' ? 'checked' : ''}
                     onchange="SkillsAPI.setFilter('rating', this.value)">
              <span style="font-size: 0.9rem;">4.5 分以�?/span>
            </label>
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
              <input type="radio" name="rating" value="4.0" ${this.state.currentFilters.rating === '4.0' ? 'checked' : ''}
                     onchange="SkillsAPI.setFilter('rating', this.value)">
              <span style="font-size: 0.9rem;">4.0 分以�?/span>
            </label>
          </div>
        </div>
      `;
    },

    /**
     * 获取分类选项
     */
    getCategoryOptions() {
      const categories = [
        { value: 'tech', label: '技术开�?, icon: 'fa-code' },
        { value: 'product', label: '产品设计', icon: 'fa-cube' },
        { value: 'design', label: '设计创意', icon: 'fa-palette' },
        { value: 'marketing', label: '市场营销', icon: 'fa-bullhorn' },
        { value: 'ops', label: '运营管理', icon: 'fa-cogs' }
      ];

      return categories.map(cat => `
        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
          <input type="radio" name="category" value="${cat.value}" ${this.state.currentFilters.category === cat.value ? 'checked' : ''}
                 onchange="SkillsAPI.setFilter('category', this.value)">
          <span style="font-size: 0.9rem;"><i class="fas ${cat.icon}"></i> ${cat.label}</span>
        </label>
      `).join('');
    },

    /**
     * 设置筛选条�?     */
    async setFilter(type, value) {
      if (value === '') {
        delete this.state.currentFilters[type];
      } else {
        this.state.currentFilters[type] = value;
      }

      this.state.currentPage = 1;
      this.state.cache = null; // 清除缓存

      await this.loadSkills();
      this.render();
    },

    /**
     * 重置筛�?     */
    async resetFilters() {
      this.state.currentFilters = {};
      this.state.currentPage = 1;
      this.state.currentSort = 'default';
      this.state.cache = null;

      document.getElementById('sortSelect').value = 'default';

      await this.loadSkills();
      this.render();
    },

    /**
     * 排序
     */
    async handleSort(sortType) {
      this.state.currentSort = sortType;
      this.state.cache = null; // 清除缓存重新排序

      await this.loadSkills();
      this.render();
    },

    /**
     * 搜索
     */
    async search(keyword) {
      this.state.currentFilters.search = keyword;
      this.state.currentPage = 1;
      this.state.cache = null;

      await this.loadSkills();
      this.render();
    },

    /**
     * 跳转页面
     */
    goToPage(page) {
      this.state.currentPage = page;
      this.render();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    /**
     * 带重试的请求
     */
    async fetchWithRetry(url, retries = this.config.retries) {
      for (let i = 0; i < retries; i++) {
        try {
          const response = await fetch(this.config.apiBaseUrl + url, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
            signal: AbortSignal.timeout(this.config.timeout)
          });

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }

          return await response.json();
        } catch (error) {
// console.`请求失败 (${i + 1}/${retries}):`, url, error);
          if (i === retries - 1) throw error;
          await this.delay(1000 * (i + 1));
        }
      }
    },

    /**
     * 检查缓存是否有�?     */
    isCacheValid() {
      return this.state.cache &&
             this.state.cacheTimestamp &&
             (Date.now() - this.state.cacheTimestamp) < this.cacheDuration;
    },

    /**
     * 获取供应商等级徽�?     */
    getVendorLevelBadge(level) {
      const badges = {
        'gold': '<span class="badge badge-gold" style="font-size: 0.7rem;">🏅 金牌</span>',
        'premium': '<span class="badge badge-premium" style="font-size: 0.7rem;">💎 优质</span>',
        'normal': '<span class="badge badge-normal" style="font-size: 0.7rem;">供应�?/span>'
      };
      return badges[level] || '';
    },

    /**
     * 获取分类图标
     */
    getCategoryIcon(category) {
      const icons = {
        'tech': 'fa-code',
        'product': 'fa-cube',
        'design': 'fa-palette',
        'marketing': 'fa-bullhorn',
        'ops': 'fa-cogs'
      };
      return icons[category] || 'fa-star';
    },

    /**
     * 获取分类名称
     */
    getCategoryName(category) {
      const names = {
        'tech': '技术开�?,
        'product': '产品设计',
        'design': '设计创意',
        'marketing': '市场营销',
        'ops': '运营管理'
      };
      return names[category] || category;
    },

    /**
     * 截断文本
     */
    truncateText(text, maxLength) {
      if (!text) return '';
      if (text.length <= maxLength) return text;
      return text.substring(0, maxLength) + '...';
    },

    /**
     * 显示错误
     */
    showError(message) {
      const container = document.querySelector('[data-demo-skills]');
      if (!container) return;

      container.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px;">
          <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: var(--accent); margin-bottom: 16px;"></i>
          <p style="color: var(--text-light); margin-bottom: 16px;">${message}</p>
          <button onclick="SkillsAPI.init()" class="btn btn-primary">重新加载</button>
        </div>
      `;
    },

    /**
     * 延迟
     */
    delay(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }
  };

  // 导出到全局
  global.SkillsAPI = SkillsAPI;

})(window);
