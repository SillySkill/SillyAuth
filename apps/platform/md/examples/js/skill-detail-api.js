/**
 * SillyMD Skill Detail API Client
 * 连接真实后端 API �?Skill 详情页模�? */

(function(global) {
  'use strict';

  const SkillDetailAPI = {
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
      skillId: null,
      skillData: null,
      reviewsData: null,
      versionsData: null
    },

    /**
     * 初始�?     */
    async init(options = {}) {
// // console.log('🚀 Skill Detail API 初始�?..');
      Object.assign(this.config, options);

      try {
        // �?URL 获取 skill ID
        const urlParams = new URLSearchParams(window.location.search);
        this.state.skillId = urlParams.get('id');

        if (!this.state.skillId) {
          this.showError('缺少 Skill ID 参数');
          return;
        }

        // 加载数据
        await this.loadSkillDetail();
        await this.loadReviews();
        await this.loadVersions();

        // 渲染页面
        this.render();

// // console.log('�?Skill Detail 加载完成');
      } catch (error) {
// console.'�?Skill Detail 加载失败:', error);
        this.showError('Skill 详情加载失败，请稍后重试');
      }
    },

    /**
     * 加载 Skill 详情
     */
    async loadSkillDetail() {
      const url = `/api/skills/${this.state.skillId}`;
      this.state.skillData = await this.fetchWithRetry(url);
      return this.state.skillData;
    },

    /**
     * 加载评论
     */
    async loadReviews() {
      // TODO: 后端需要添加评�?API
      // 临时使用空数�?      this.state.reviewsData = [];
      return this.state.reviewsData;
    },

    /**
     * 加载版本历史
     */
    async loadVersions() {
      // TODO: 后端需要添加版本历�?API
      // 临时使用空数�?      this.state.versionsData = [];
      return this.state.versionsData;
    },

    /**
     * 渲染页面
     */
    render() {
      const skill = this.state.skillData;
      if (!skill) return;

      // 渲染基本信息
      this.renderBasicInfo(skill);

      // 渲染价格
      this.renderPrice(skill);

      // 渲染供应商信�?      this.renderAuthor(skill);

      // 渲染标签
      this.renderTags(skill);

      // 渲染评论
      this.renderReviews();
    },

    /**
     * 渲染基本信息
     */
    renderBasicInfo(skill) {
      // 标题和描�?      const nameEl = document.getElementById('skillName');
      const descEl = document.getElementById('skillDescription');

      if (nameEl) nameEl.textContent = skill.name;
      if (descEl) descEl.textContent = skill.description || '暂无描述';

      // 分类和场�?      const categoryIcon = this.getCategoryIcon(skill.category);
      const categoryName = this.getCategoryName(skill.category);

      const industryEl = document.getElementById('skillIndustry');
      if (industryEl) {
        industryEl.textContent = `${categoryIcon} ${categoryName}`;
      }

      const scenarioEl = document.getElementById('skillScenario');
      if (scenarioEl) {
        scenarioEl.textContent = `📦 ${skill.type === 'free' ? '免费' : '商用'}`;
      }

      // 供应商等�?      const levelEl = document.getElementById('skillLevel');
      if (levelEl) {
        levelEl.textContent = this.getVendorLevelText(skill.author_level);
      }

      // 统计数据
      const ratingEl = document.getElementById('skillRating');
      const downloadsEl = document.getElementById('skillDownloads');
      const versionEl = document.getElementById('skillVersion');
      const updatedEl = document.getElementById('skillUpdated');

      if (ratingEl) ratingEl.textContent = Number(skill.rating_avg || 0).toFixed(1);
      if (downloadsEl) downloadsEl.textContent = (skill.download_count || 0).toLocaleString();
      if (versionEl) versionEl.textContent = skill.version;
      if (updatedEl) {
        const date = skill.updated_at ? new Date(skill.updated_at) : new Date();
        updatedEl.textContent = date.toLocaleDateString('zh-CN');
      }
    },

    /**
     * 渲染价格
     */
    renderPrice(skill) {
      const priceEl = document.getElementById('skillPrice');
      if (!priceEl) return;

      const priceNum = Number(skill.price || 0);
      if (skill.type === 'free' || priceNum === 0) {
        priceEl.textContent = '免费';
      } else {
        priceEl.textContent = `💎 ${priceNum.toLocaleString()}`;
      }
    },

    /**
     * 渲染供应商信�?     */
    renderAuthor(skill) {
      const avatarEl = document.getElementById('authorAvatar');
      const nameEl = document.getElementById('authorName');
      const bioEl = document.getElementById('authorBio');

      if (avatarEl) {
        avatarEl.src = skill.author_avatar || 'https://via.placeholder.com/60';
        avatarEl.alt = skill.author_username;
      }
      if (nameEl) nameEl.textContent = skill.author_username;
      if (bioEl) bioEl.textContent = skill.author_bio || '暂无简�?;

      // 统计数据（需要从 API 获取更详细的信息�?      // 临时使用静态数�?      const skillsEl = document.getElementById('authorSkills');
      const salesEl = document.getElementById('authorSales');
      const ratingEl = document.getElementById('authorRating');

      if (skillsEl) skillsEl.textContent = skill.skill_count || '0';
      if (ratingEl) ratingEl.textContent = Number(skill.avg_rating || 0).toFixed(1);
      if (salesEl) salesEl.textContent = '0'; // 需要从后端获取
    },

    /**
     * 渲染标签
     */
    renderTags(skill) {
      const tagsContainer = document.getElementById('skillTags');
      if (!tagsContainer) return;

      // 临时生成一些标�?      const tags = [
        this.getCategoryName(skill.category),
        skill.type === 'free' ? '免费' : '付费',
        `v${skill.version}`
      ];

      tagsContainer.innerHTML = tags.map(tag =>
        `<span class="tag" style="font-size: 0.75rem; padding: 2px 8px;">${tag}</span>`
      ).join('');
    },

    /**
     * 渲染评论
     */
    renderReviews() {
      const reviewsContainer = document.getElementById('reviewsList');
      const countEl = document.getElementById('reviewCount');

      if (!reviewsContainer) return;

      const reviews = this.state.reviewsData || [];

      if (countEl) countEl.textContent = reviews.length;

      if (reviews.length === 0) {
        reviewsContainer.innerHTML = `
          <div class="card" style="padding: 40px; text-align: center;">
            <i class="fas fa-comment-slash" style="font-size: 2rem; color: var(--text-light); margin-bottom: 16px;"></i>
            <p style="color: var(--text-light);">暂无评价</p>
            <p style="color: var(--text-light); font-size: 0.9rem; margin-top: 8px;">成为第一个评价的人吧�?/p>
          </div>
        `;
        return;
      }

      reviewsContainer.innerHTML = reviews.map(review => this.createReviewCard(review)).join('');
    },

    /**
     * 创建评论卡片
     */
    createReviewCard(review) {
      const stars = this.createStarRating(review.rating);

      return `
        <div class="review-card">
          <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <img src="${review.avatar || 'https://via.placeholder.com/40'}"
                 alt="${review.username}"
                 style="width: 40px; height: 40px; border-radius: 50%;">
            <div style="flex: 1;">
              <div style="font-weight: 600;">${review.username}</div>
              <div style="display: flex; gap: 2px;">${stars}</div>
            </div>
            <span style="color: var(--text-light); font-size: 0.85rem;">
              ${new Date(review.created_at).toLocaleDateString('zh-CN')}
            </span>
          </div>
          <p style="color: var(--text-light); line-height: 1.6;">${review.content}</p>
        </div>
      `;
    },

    /**
     * 创建星级评分
     */
    createStarRating(rating) {
      const fullStars = Math.floor(rating);
      const hasHalfStar = rating % 1 >= 0.5;
      let stars = '';

      for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star" style="color: #FFC107; font-size: 0.8rem;"></i>';
      }

      if (hasHalfStar) {
        stars += '<i class="fas fa-star-half-alt" style="color: #FFC107; font-size: 0.8rem;"></i>';
      }

      const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
      for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star" style="color: #FFC107; font-size: 0.8rem;"></i>';
      }

      return stars;
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
     * 获取供应商等级文�?     */
    getVendorLevelText(level) {
      const levels = {
        'gold': '🏅 金牌',
        'premium': '💎 优质',
        'normal': '供应�?
      };
      return levels[level] || '供应�?;
    },

    /**
     * 获取分类图标
     */
    getCategoryIcon(category) {
      const icons = {
        'tech': '💻',
        'product': '📦',
        'design': '🎨',
        'marketing': '📢',
        'ops': '⚙️'
      };
      return icons[category] || '📦';
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
     * 显示错误
     */
    showError(message) {
      const container = document.querySelector('.skill-detail-content');
      if (!container) return;

      container.innerHTML = `
        <div class="container" style="text-align: center; padding: 60px 20px;">
          <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: var(--accent); margin-bottom: 16px;"></i>
          <h2 style="margin-bottom: 16px;">加载失败</h2>
          <p style="color: var(--text-light); margin-bottom: 24px;">${message}</p>
          <button onclick="location.reload()" class="btn btn-primary">重新加载</button>
          <a href="skills.html" class="btn btn-secondary" style="margin-left: 12px;">返回列表</a>
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
  global.SkillDetailAPI = SkillDetailAPI;

})(window);
