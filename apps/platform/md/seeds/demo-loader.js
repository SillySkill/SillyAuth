/**
 * SillyMD 前端演示数据加载器 - 真实版
 * 
 * 用于在前端展示生成的真实模拟数据
 */

(function(global) {
  'use strict';

  const SillyMDDemo = {
    config: {
      dataUrl: './js/demo-data.json',
      skillsPerPage: 12,
      currentPage: 1,
      filters: {
        industry: null,
        scenario: null,
        price: null,
        rating: null
      }
    },

    data: {
      users: [],
      skills: [],
      stats: {}
    },

    industries: [
      { name: '金融', icon: '🟣', color: '#FFD700' },
      { name: '电商', icon: '🟢', color: '#4CAF50' },
      { name: '教育', icon: '🟡', color: '#FFC107' },
      { name: '医疗', icon: '🟣', color: '#9C27B0' },
      { name: '制造', icon: '🟠', color: '#FF9800' },
      { name: '旅游', icon: '🔵', color: '#2196F3' },
      { name: '娱乐', icon: '🟣', color: '#E91E63' },
      { name: '餐饮', icon: '🟧', color: '#795548' }
    ],

    scenarios: [
      { name: '数据分析', icon: '📊' },
      { name: '自动化', icon: '🤖' },
      { name: '客户服务', icon: '🎧' },
      { name: '市场营销', icon: '📱' },
      { name: '产品开发', icon: '💻' },
      { name: '项目管理', icon: '📋' },
      { name: '内容创作', icon: '✍️' }
    ],

    async init(options = {}) {
      console.log('🥚 SillyMD Demo Loader (Real Edition) 初始化...');
      Object.assign(this.config, options);
      
      try {
        await this.loadData();
        this.renderStats();
        this.renderSkills();
        this.renderFilters();
        console.log('✅ Demo 加载完成');
      } catch (error) {
        console.error('❌ 加载失败:', error);
        this.showError('数据加载失败，请刷新页面重试');
      }
    },

    async loadData() {
      if (window.SILLY_MOCK_DATA) {
        this.data = window.SILLY_MOCK_DATA;
        return;
      }

      try {
        const response = await fetch(this.config.dataUrl);
        if (response.ok) {
          this.data = await response.json();
          return;
        }
      } catch (e) {
        console.log('使用示例数据');
      }
      
      this.loadExampleData();
    },

    loadExampleData() {
      // 使用真实姓名和头像的示例数据
      const exampleUsers = [
        { id: 'user_001', username: 'wang1990', displayName: '王伟', nickname: 'CodeMaster', gender: 'male', avatar: 'https://randomuser.me/api/portraits/men/32.jpg', bio: '现任阿里巴巴高级前端工程师，专注前端领域8年。', role: 'vendor', vendorLevel: 'gold', location: '杭州', stats: { totalSkills: 15, totalSales: 45000, rating: 4.9 } },
        { id: 'user_002', username: 'li_dev', displayName: '李芳', nickname: 'PixelArtist', gender: 'female', avatar: 'https://randomuser.me/api/portraits/women/45.jpg', bio: '前字节跳动设计总监，现自由职业。10年设计经验。', role: 'vendor', vendorLevel: 'premium', location: '北京', stats: { totalSkills: 8, totalSales: 12000, rating: 4.8 } },
        { id: 'user_003', username: 'zhang_pro', displayName: '张伟', nickname: 'DataWizard', gender: 'male', avatar: 'https://randomuser.me/api/portraits/men/67.jpg', bio: '腾讯数据科学家，专注AI应用开发。', role: 'vendor', vendorLevel: 'gold', location: '深圳', stats: { totalSkills: 12, totalSales: 38000, rating: 4.9 } },
        { id: 'user_004', username: 'liu_88', displayName: '刘洋', nickname: 'DevOps', gender: 'female', avatar: 'https://randomuser.me/api/portraits/women/23.jpg', bio: '美团技术专家，云原生技术布道者。', role: 'vendor', vendorLevel: 'premium', location: '北京', stats: { totalSkills: 6, totalSales: 8000, rating: 4.7 } },
        { id: 'user_005', username: 'chen_ai', displayName: '陈明', nickname: 'AIGuru', gender: 'male', avatar: 'https://randomuser.me/api/portraits/men/91.jpg', bio: '独立AI开发者，开源爱好者。', role: 'vendor', vendorLevel: 'normal', location: '上海', stats: { totalSkills: 4, totalSales: 2500, rating: 4.5 } },
        { id: 'user_006', username: 'yang_pm', displayName: '杨静', nickname: 'ProductHunter', gender: 'female', avatar: 'https://randomuser.me/api/portraits/women/56.jpg', bio: '前产品经理，现创业中。', role: 'vendor', vendorLevel: 'premium', location: '深圳', stats: { totalSkills: 7, totalSales: 15000, rating: 4.8 } },
        { id: 'user_007', username: 'huang_dev', displayName: '黄强', nickname: 'FullStack', gender: 'male', avatar: 'https://randomuser.me/api/portraits/men/12.jpg', bio: '全栈工程师，远程工作。', role: 'user', vendorLevel: 'user', location: '成都', stats: { totalSkills: 0, totalSales: 0, rating: 0 } },
        { id: 'user_008', username: 'zhao_ux', displayName: '赵琳', nickname: 'UXExpert', gender: 'female', avatar: 'https://randomuser.me/api/portraits/women/78.jpg', bio: '用户体验设计师，专注B端产品。', role: 'vendor', vendorLevel: 'normal', location: '杭州', stats: { totalSkills: 3, totalSales: 1800, rating: 4.6 } },
      ];

      const industries = ['金融', '电商', '教育', '医疗', '制造', '旅游', '娱乐', '餐饮'];
      const scenarios = ['数据分析', '自动化', '客户服务', '市场营销', '产品开发', '项目管理', '内容创作'];
      
      const exampleSkills = Array.from({ length: 50 }, (_, i) => {
        const author = exampleUsers[i % exampleUsers.length];
        return {
          id: `skill_${String(i + 1).padStart(3, '0')}`,
          name: ['AI交易机器人Pro', '代码审查助手', '数据分析大师', '自动化测试平台', '文档生成器'][i % 5] + (i > 4 ? ` ${i}` : ''),
          description: '专业级工具，支持多种功能，适用于各行业的数据分析场景。已帮助500+企业提升效率。',
          authorId: author.id,
          authorName: author.displayName,
          authorNickname: author.nickname,
          authorAvatar: author.avatar,
          authorLevel: author.vendorLevel,
          authorLocation: author.location,
          type: ['code', 'design', 'product', 'marketing'][i % 4],
          industry: industries[i % industries.length],
          industryIcon: ['🟣', '🟢', '🟡', '🟣', '🟠', '🔵', '🟣', '🟧'][i % 8],
          scenario: scenarios[i % scenarios.length],
          scenarioIcon: ['📊', '🤖', '🎧', '📱', '💻', '📋', '✍️'][i % 7],
          pricing: { type: i % 3 === 0 ? 'free' : 'onetime', price: i % 3 === 0 ? 0 : [299, 599, 1299, 2999, 5999, 9999][i % 6] },
          rating: [4.5, 4.6, 4.7, 4.8, 4.9, 5.0][i % 6],
          downloads: [1234, 2345, 3456, 4567, 5678, 6789][i % 6],
          tags: ['AI', '自动化', 'Python', '数据分析'].slice(0, (i % 4) + 1),
          icon: ['fa-robot', 'fa-code', 'fa-chart-line', 'fa-bug', 'fa-file-alt'][i % 5],
          status: 'approved',
          createdAt: '2024-06-15'
        };
      });

      window.SILLY_MOCK_DATA = {
        users: exampleUsers,
        skills: exampleSkills,
        stats: {
          totalUsers: 50,
          totalSkills: 200,
          totalVendors: 35,
          freeSkills: 70,
          paidSkills: 130
        }
      };
      
      this.data = window.SILLY_MOCK_DATA;
    },

    renderStats() {
      const stats = this.data.stats;
      const statsContainer = document.querySelector('[data-demo-stats]');
      if (!statsContainer) return;

      statsContainer.innerHTML = `
        <div class="stat-card">
          <div class="stat-value">${this.formatNumber(stats.totalSkills)}+</div>
          <div class="stat-label">Skills 资产</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${this.formatNumber(stats.totalVendors)}+</div>
          <div class="stat-label">认证供应商</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${this.formatNumber(stats.totalUsers)}+</div>
          <div class="stat-label">活跃用户</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">99.9%</div>
          <div class="stat-label">AI 审核准确率</div>
        </div>
      `;
    },

    renderSkills() {
      const container = document.querySelector('[data-demo-skills]');
      if (!container) return;

      let skills = this.filterSkills();
      const total = skills.length;
      
      const start = (this.config.currentPage - 1) * this.config.skillsPerPage;
      const end = start + this.config.skillsPerPage;
      skills = skills.slice(start, end);

      const countEl = document.querySelector('[data-demo-count]');
      if (countEl) {
        countEl.textContent = `共找到 ${total} 个 Skills`;
      }

      container.innerHTML = skills.map(skill => this.createSkillCard(skill)).join('');
      this.renderPagination(total);
    },

    createSkillCard(skill) {
      const badgeClass = skill.pricing.type === 'free' ? 'badge-free' : 'badge-paid';
      const priceText = skill.pricing.type === 'free' 
        ? '<span style="color: var(--accent); font-weight: 600;">免费</span>'
        : `<span class="skill-card-price">💎 ${skill.pricing.price.toLocaleString()}</span>`;

      // 徽章显示
      let authorBadge = '';
      if (skill.authorLevel === 'gold') {
        authorBadge = '<span class="badge badge-success" style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; font-size: 0.7rem;"><i class="fas fa-crown" style="font-size: 0.6rem;"></i> 金牌</span>';
      } else if (skill.authorLevel === 'premium') {
        authorBadge = '<span class="badge badge-info" style="display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; font-size: 0.7rem;"><i class="fas fa-gem" style="font-size: 0.6rem;"></i> 优质</span>';
      } else if (skill.authorLevel === 'normal') {
        authorBadge = '<span class="badge" style="background: var(--bg-dark-tertiary); color: var(--text-light); padding: 2px 8px; font-size: 0.7rem;">供应商</span>';
      }

      // 显示位置信息（如果有）
      const locationText = skill.authorLocation ? `<span style="color: var(--text-muted); font-size: 0.7rem;"><i class="fas fa-map-marker-alt" style="font-size: 0.65rem;"></i> ${skill.authorLocation}</span>` : '';

      return `
        <div class="skill-card" data-skill-id="${skill.id}" style="transition: transform 0.2s, box-shadow 0.2s; display: flex; flex-direction: column; height: 100%;" onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 24px rgba(0,0,0,0.3)';" onmouseout="this.style.transform=''; this.style.boxShadow='';">
          <span class="skill-card-badge ${badgeClass}" style="position: absolute; top: 12px; right: 12px; z-index: 10;">${skill.pricing.type === 'free' ? '免费' : '付费'}</span>
          
          <!-- 头部：小图标 + 标题 + 标签 -->
          <div style="padding: 16px 16px 12px 16px;">
            <div style="display: flex; align-items: flex-start; gap: 12px; margin-bottom: 10px;">
              <!-- 小图标 -->
              <div style="flex-shrink: 0; width: 40px; height: 40px; background: rgba(0,0,0,0.3); border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                <i class="fas ${skill.icon}" style="color: ${this.getSkillColor(skill.type)}; font-size: 1.2rem;"></i>
              </div>
              
              <!-- 标题区域 -->
              <div style="flex: 1; min-width: 0;">
                <h3 class="skill-card-title" style="font-size: 1.05rem; font-weight: 600; margin: 0 0 6px 0; line-height: 1.3;">${skill.name}</h3>
                <div style="display: flex; gap: 4px; flex-wrap: wrap;">
                  <span class="tag tag-industry" style="font-size: 0.7rem; padding: 2px 6px;">${skill.industryIcon} ${skill.industry}</span>
                  <span class="tag tag-scenario" style="font-size: 0.7rem; padding: 2px 6px;">${skill.scenarioIcon} ${skill.scenario}</span>
                </div>
              </div>
            </div>
            
            <!-- 描述区域 - 主要幅面 -->
            <p class="skill-card-desc" style="font-size: 0.9rem; line-height: 1.7; color: var(--text-light); margin: 0; min-height: 80px;">${skill.description}</p>
          </div>
          
          <!-- 底部：作者信息 + 价格评分 -->
          <div style="margin-top: auto; padding: 12px 16px 16px 16px; border-top: 1px solid var(--border-light);">
            <!-- 作者信息 - 更紧凑 -->
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
              <img src="${skill.authorAvatar}" alt="${skill.authorName}" style="width: 28px; height: 28px; border-radius: 50%; object-fit: cover; border: 1px solid var(--border-light);">
              <div style="flex: 1; min-width: 0; display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                <span style="font-size: 0.85rem; font-weight: 500; color: var(--text-white);">${skill.authorName}</span>
                ${locationText}
              </div>
              ${authorBadge}
            </div>
            
            <!-- 价格和评分 -->
            <div style="display: flex; align-items: center; justify-content: space-between;">
              ${priceText}
              <span class="skill-card-rating" style="display: inline-flex; align-items: center; gap: 4px;">
                <i class="fas fa-star" style="color: #FFC107; font-size: 0.85rem;"></i> 
                <span style="font-weight: 600; font-size: 0.9rem;">${skill.rating}</span>
                <span style="color: var(--text-muted); font-size: 0.8rem;">(${skill.downloads})</span>
              </span>
            </div>
          </div>
        </div>
      `;
    },

    getSkillColor(type) {
      const colors = {
        code: '#A8E063',
        design: '#5CB8D1',
        product: '#FFB6C1',
        marketing: '#FFD700',
        content: '#FF6B6B',
        operation: '#9C27B0'
      };
      return colors[type] || '#A8E063';
    },

    filterSkills() {
      let skills = [...this.data.skills];
      const filters = this.config.filters;

      if (filters.industry) {
        skills = skills.filter(s => s.industry === filters.industry);
      }
      if (filters.scenario) {
        skills = skills.filter(s => s.scenario === filters.scenario);
      }
      if (filters.price) {
        if (filters.price === 'free') {
          skills = skills.filter(s => s.pricing.type === 'free');
        } else if (filters.price === 'paid') {
          skills = skills.filter(s => s.pricing.type !== 'free');
        }
      }
      if (filters.rating) {
        skills = skills.filter(s => s.rating >= filters.rating);
      }

      return skills;
    },

    renderFilters() {
      const container = document.querySelector('[data-demo-filters]');
      if (!container) return;

      container.innerHTML = `
        <div style="margin-bottom: 24px;">
          <h4 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 12px;">行业</h4>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 0;">
              <input type="radio" name="industry" value="" ${!this.config.filters.industry ? 'checked' : ''} 
                     onchange="SillyMDDemo.setFilter('industry', this.value || null)" style="accent-color: var(--primary);">
              <span style="font-size: 0.9rem; color: var(--text-light);">全部行业</span>
            </label>
            ${this.industries.map(ind => `
              <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 0;">
                <input type="radio" name="industry" value="${ind.name}" ${this.config.filters.industry === ind.name ? 'checked' : ''}
                       onchange="SillyMDDemo.setFilter('industry', this.value)" style="accent-color: var(--primary);">
                <span style="font-size: 0.9rem; color: var(--text-light);">${ind.icon} ${ind.name}</span>
              </label>
            `).join('')}
          </div>
        </div>

        <div style="margin-bottom: 24px;">
          <h4 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 12px;">应用场景</h4>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 0;">
              <input type="radio" name="scenario" value="" ${!this.config.filters.scenario ? 'checked' : ''}
                     onchange="SillyMDDemo.setFilter('scenario', this.value || null)" style="accent-color: var(--primary);">
              <span style="font-size: 0.9rem; color: var(--text-light);">全部场景</span>
            </label>
            ${this.scenarios.map(sce => `
              <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 0;">
                <input type="radio" name="scenario" value="${sce.name}" ${this.config.filters.scenario === sce.name ? 'checked' : ''}
                       onchange="SillyMDDemo.setFilter('scenario', this.value)" style="accent-color: var(--primary);">
                <span style="font-size: 0.9rem; color: var(--text-light);">${sce.icon} ${sce.name}</span>
              </label>
            `).join('')}
          </div>
        </div>

        <div style="margin-bottom: 24px;">
          <h4 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 12px;">价格</h4>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 0;">
              <input type="radio" name="price" value="" ${!this.config.filters.price ? 'checked' : ''}
                     onchange="SillyMDDemo.setFilter('price', this.value || null)" style="accent-color: var(--primary);">
              <span style="font-size: 0.9rem; color: var(--text-light);">全部</span>
            </label>
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 0;">
              <input type="radio" name="price" value="free" ${this.config.filters.price === 'free' ? 'checked' : ''}
                     onchange="SillyMDDemo.setFilter('price', this.value)" style="accent-color: var(--primary);">
              <span style="font-size: 0.9rem; color: var(--text-light);">免费</span>
            </label>
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 0;">
              <input type="radio" name="price" value="paid" ${this.config.filters.price === 'paid' ? 'checked' : ''}
                     onchange="SillyMDDemo.setFilter('price', this.value)" style="accent-color: var(--primary);">
              <span style="font-size: 0.9rem; color: var(--text-light);">付费</span>
            </label>
          </div>
        </div>

        <div>
          <h4 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 12px;">评分</h4>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 0;">
              <input type="radio" name="rating" value="" ${!this.config.filters.rating ? 'checked' : ''}
                     onchange="SillyMDDemo.setFilter('rating', this.value ? parseFloat(this.value) : null)" style="accent-color: var(--primary);">
              <span style="font-size: 0.9rem; color: var(--text-light);">全部评分</span>
            </label>
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 0;">
              <input type="radio" name="rating" value="4.5" ${this.config.filters.rating === 4.5 ? 'checked' : ''}
                     onchange="SillyMDDemo.setFilter('rating', parseFloat(this.value))" style="accent-color: var(--primary);">
              <span style="font-size: 0.9rem; color: var(--text-light);">⭐⭐⭐⭐⭐ 4.5分以上</span>
            </label>
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 0;">
              <input type="radio" name="rating" value="4.0" ${this.config.filters.rating === 4.0 ? 'checked' : ''}
                     onchange="SillyMDDemo.setFilter('rating', parseFloat(this.value))" style="accent-color: var(--primary);">
              <span style="font-size: 0.9rem; color: var(--text-light);">⭐⭐⭐⭐ 4.0分以上</span>
            </label>
          </div>
        </div>
      `;
    },

    setFilter(key, value) {
      this.config.filters[key] = value;
      this.config.currentPage = 1;
      this.renderSkills();
    },

    renderPagination(total) {
      const container = document.querySelector('[data-demo-pagination]');
      if (!container) return;

      const totalPages = Math.ceil(total / this.config.skillsPerPage);
      const current = this.config.currentPage;

      let html = `
        <button class="btn btn-ghost btn-sm" ${current === 1 ? 'disabled' : ''} 
                onclick="SillyMDDemo.goToPage(${current - 1})">
          <i class="fas fa-chevron-left"></i>
        </button>
      `;

      for (let i = 1; i <= Math.min(totalPages, 5); i++) {
        html += `<button class="btn ${i === current ? 'btn-primary' : 'btn-ghost'} btn-sm" 
                        onclick="SillyMDDemo.goToPage(${i})">${i}</button>`;
      }

      html += `
        <button class="btn btn-ghost btn-sm" ${current === totalPages ? 'disabled' : ''}
                onclick="SillyMDDemo.goToPage(${current + 1})">
          <i class="fas fa-chevron-right"></i>
        </button>
      `;

      container.innerHTML = html;
    },

    goToPage(page) {
      const totalPages = Math.ceil(this.filterSkills().length / this.config.skillsPerPage);
      if (page < 1 || page > totalPages) return;
      
      this.config.currentPage = page;
      this.renderSkills();
      
      const container = document.querySelector('[data-demo-skills]');
      if (container) {
        container.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    },

    formatNumber(num) {
      if (num >= 10000) {
        return (num / 10000).toFixed(1) + '万';
      }
      return num.toString();
    },

    showError(message) {
      const container = document.querySelector('[data-demo-skills]');
      if (container) {
        container.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 60px;">
            <i class="fas fa-exclamation-circle" style="font-size: 3rem; color: var(--accent); margin-bottom: 16px;"></i>
            <p style="color: var(--text-light);">${message}</p>
          </div>
        `;
      }
    }
  };

  global.SillyMDDemo = SillyMDDemo;

})(window);
