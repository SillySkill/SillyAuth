/**
 * SillyMD 真实数据加载�? * 从数据库 API 获取真实数据并替换到页面�? */

(function(global) {
  'use strict';

  const SillyMDRealData = {
    config: {
      // 使用全局配置或默认值
      get apiBaseUrl() {
        return typeof CONFIG !== 'undefined' ? CONFIG.API_BASE : 'http://47.96.133.238:8000';
      },
      get timeout() {
        return typeof CONFIG !== 'undefined' ? CONFIG.API_TIMEOUT : 10000;
      },
      get retries() {
        return typeof CONFIG !== 'undefined' ? CONFIG.RETRY_COUNT : 3;
      }
    },

    cache: {
      skills: null,
      users: null,
      teams: null,
      stats: null,
      timestamp: null
    },

    // 缓存时间�?分钟�?    cacheDuration: 5 * 60 * 1000,

    /**
     * 初始�?     */
    async init(options = {}) {
// // console.log('🚀 SillyMD 真实数据加载器初始化...');
      Object.assign(this.config, options);

      try {
        // 加载所有数�?        await this.loadAllData();

        // 渲染到页�?        this.renderToPage();

// // console.log('�?真实数据加载完成');
      } catch (error) {
// console.'�?加载失败:', error);
        this.showError('数据加载失败，请检查网络连�?);
      }
    },

    /**
     * 加载所有数�?     */
    async loadAllData() {
      // 检查缓�?      if (this.isCacheValid()) {
// // console.log('使用缓存数据');
        return;
      }

// // console.log('�?API 加载数据...');

      // 并行加载所有数�?      const [skills, users, teams, stats] = await Promise.all([
        this.fetchWithRetry('/api/skills?limit=100'),
        this.fetchWithRetry('/api/users?limit=50'),
        this.fetchWithRetry('/api/teams?limit=20'),
        this.fetchWithRetry('/api/market/stats')
      ]);

      this.cache = {
        skills,
        users,
        teams,
        stats,
        timestamp: Date.now()
      };

// // console.log('数据加载完成:', {
        skills: skills.length,
        users: users.length,
        teams: teams.length
      });
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
          await this.delay(1000 * (i + 1)); // 指数退�?        }
      }
    },

    /**
     * 检查缓存是否有�?     */
    isCacheValid() {
      return this.cache.timestamp &&
             (Date.now() - this.cache.timestamp) < this.cacheDuration;
    },

    /**
     * 渲染数据到页�?     */
    renderToPage() {
      // 渲染统计数据
      this.renderStats();

      // 渲染 Skills 列表
      this.renderSkills();

      // 渲染用户列表
      this.renderUsers();

      // 渲染团队列表
      this.renderTeams();

      // 触发自定义事�?      this.emitDataLoaded();
    },

    /**
     * 渲染统计数据
     */
    renderStats() {
      if (!this.cache.stats) return;

      const stats = this.cache.stats;

      // 查找统计卡片容器
      const statContainers = document.querySelectorAll('[data-stats]');

      statContainers.forEach(container => {
        // 更新总用户数
        const userCountEl = container.querySelector('[data-stat="users"]');
        if (userCountEl) {
          this.animateNumber(userCountEl, stats.total_users);
        }

        // 更新�?Skills �?        const skillCountEl = container.querySelector('[data-stat="skills"]');
        if (skillCountEl) {
          this.animateNumber(skillCountEl, stats.total_skills);
        }

        // 更新供应商数
        const vendorCountEl = container.querySelector('[data-stat="vendors"]');
        if (vendorCountEl) {
          this.animateNumber(vendorCountEl, stats.total_vendors);
        }

        // 更新免费 Skills
        const freeCountEl = container.querySelector('[data-stat="free-skills"]');
        if (freeCountEl) {
          this.animateNumber(freeCountEl, stats.free_skills);
        }

        // 更新付费 Skills
        const paidCountEl = container.querySelector('[data-stat="paid-skills"]');
        if (paidCountEl) {
          this.animateNumber(paidCountEl, stats.paid_skills);
        }
      });
    },

    /**
     * 渲染 Skills 列表
     */
    renderSkills() {
      if (!this.cache.skills) return;

      const containers = document.querySelectorAll('[data-skills-container]');

      containers.forEach(container => {
        const limit = parseInt(container.dataset.limit || '12');
        const skills = this.cache.skills.slice(0, limit);

        container.innerHTML = skills.map(skill => this.createSkillCard(skill)).join('');
      });
    },

    /**
     * 创建 Skill 卡片
     */
    createSkillCard(skill) {
      const priceNum = Number(skill.price || 0);
      const priceDisplay = skill.type === 'free' || priceNum === 0
        ? '<span style="color: var(--accent); font-weight: 600;">免费</span>'
        : `<span style="font-weight: 600;">💎 ${priceNum.toLocaleString()} 积分</span>`;

      const levelBadge = this.getVendorLevelBadge(skill.author_level);

      return `
        <div class="skill-card" data-skill-id="${skill.skill_id}">
          <span class="skill-type-badge">${skill.type === 'free' ? '免费' : '付费'}</span>

          <div class="skill-header">
            <div class="skill-icon">
              <i class="fas ${this.getSkillIcon(skill.category)}"></i>
            </div>
            <div class="skill-title-group">
              <h3 class="skill-title">${skill.name}</h3>
              <div class="skill-meta">
                <span class="tag tag-category">${skill.category}</span>
                ${skill.is_featured ? '<span class="tag tag-featured"><i class="fas fa-star"></i> 精�?/span>' : ''}
              </div>
            </div>
          </div>

          <p class="skill-description">${this.truncateText(skill.description, 100)}</p>

          <div class="skill-author">
            <img src="${skill.author_avatar || 'https://via.placeholder.com/40'}" alt="${skill.author_username}">
            <div class="author-info">
              <span class="author-name">${skill.author_username}</span>
              ${levelBadge}
            </div>
          </div>

          <div class="skill-footer">
            ${priceDisplay}
            <div class="skill-rating">
              <i class="fas fa-star" style="color: #FFC107;"></i>
              <span>${Number(skill.rating_avg || 0).toFixed(1)}</span>
              <span class="download-count">(${Number(skill.download_count || 0)} 下载)</span>
            </div>
          </div>
        </div>
      `;
    },

    /**
     * 渲染用户列表
     */
    renderUsers() {
      if (!this.cache.users) return;

      const containers = document.querySelectorAll('[data-users-container]');

      containers.forEach(container => {
        const limit = parseInt(container.dataset.limit || '12');
        const users = this.cache.users.slice(0, limit);

        container.innerHTML = users.map(user => this.createUserCard(user)).join('');
      });
    },

    /**
     * 创建用户卡片
     */
    createUserCard(user) {
      const levelBadge = this.getVendorLevelBadge(user.vendor_level);

      return `
        <div class="user-card" data-username="${user.username}">
          <div class="user-avatar">
            <img src="${user.avatar_url || 'https://via.placeholder.com/80'}" alt="${user.username}">
          </div>
          <div class="user-info">
            <h4 class="user-name">${user.username}</h4>
            <p class="user-bio">${this.truncateText(user.bio || '', 80)}</p>
            <div class="user-meta">
              ${levelBadge}
              <span class="user-skills">${user.skill_count} 个作�?/span>
            </div>
          </div>
        </div>
      `;
    },

    /**
     * 渲染团队列表
     */
    renderTeams() {
      if (!this.cache.teams) return;

      const containers = document.querySelectorAll('[data-teams-container]');

      containers.forEach(container => {
        const limit = parseInt(container.dataset.limit || '10');
        const teams = this.cache.teams.slice(0, limit);

        container.innerHTML = teams.map(team => this.createTeamCard(team)).join('');
      });
    },

    /**
     * 创建团队卡片
     */
    createTeamCard(team) {
      return `
        <div class="team-card" data-team-slug="${team.team_slug}">
          <div class="team-header">
            <h4 class="team-name">${team.team_name}</h4>
            <span class="team-members">${team.member_count} 成员</span>
          </div>
          <p class="team-description">${this.truncateText(team.description || '', 100)}</p>
          <div class="team-meta">
            <span>${team.project_count} 个项�?/span>
            <span>创建�? ${team.owner_username}</span>
          </div>
        </div>
      `;
    },

    /**
     * 获取供应商等级徽�?     */
    getVendorLevelBadge(level) {
      const badges = {
        'gold': '<span class="badge badge-gold"><i class="fas fa-crown"></i> 金牌</span>',
        'premium': '<span class="badge badge-premium"><i class="fas fa-gem"></i> 优质</span>',
        'normal': '<span class="badge badge-normal">供应�?/span>',
        'none': ''
      };
      return badges[level] || '';
    },

    /**
     * 获取 Skill 图标
     */
    getSkillIcon(category) {
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
     * 截断文本
     */
    truncateText(text, maxLength) {
      if (!text) return '';
      if (text.length <= maxLength) return text;
      return text.substring(0, maxLength) + '...';
    },

    /**
     * 数字动画
     */
    animateNumber(element, target) {
      const start = 0;
      const duration = 1000;
      const increment = target / (duration / 16);
      let current = start;

      const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
          current = target;
          clearInterval(timer);
        }
        element.textContent = Math.floor(current).toLocaleString();
      }, 16);
    },

    /**
     * 触发自定义事�?     */
    emitDataLoaded() {
      const event = new CustomEvent('sillymd-data-loaded', {
        detail: {
          skills: this.cache.skills,
          users: this.cache.users,
          teams: this.cache.teams,
          stats: this.cache.stats
        }
      });
      window.dispatchEvent(event);
    },

    /**
     * 显示错误
     */
    showError(message) {
      const containers = document.querySelectorAll('[data-skills-container], [data-users-container], [data-teams-container]');

      containers.forEach(container => {
        container.innerHTML = `
          <div class="error-message" style="grid-column: 1 / -1; text-align: center; padding: 60px 20px;">
            <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: var(--accent); margin-bottom: 16px;"></i>
            <p style="color: var(--text-light);">${message}</p>
            <button onclick="location.reload()" class="btn btn-primary">重新加载</button>
          </div>
        `;
      });
    },

    /**
     * 延迟
     */
    delay(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }
  };

  // 导出到全局
  global.SillyMDRealData = SillyMDRealData;

})(window);
