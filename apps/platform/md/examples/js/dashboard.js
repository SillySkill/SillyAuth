/**
 * Dashboard Controller
 * 仪表板页面控制器
 *
 * 负责加载和显示用户仪表板数据
 */

const dashboard = {
    // API基础URL - 使用全局配置
    get apiBaseUrl() {
        return typeof CONFIG !== 'undefined' ? `${CONFIG.API_BASE}/api` : 'http://47.96.133.238:8000/api';
    },

    // 当前用户信息
    currentUser: null,

    /**
     * 初始化仪表板
     */
    async init() {
        try {
            // 检查登录状态
            this.currentUser = auth.getCurrentUser();
            if (!this.currentUser) {
                window.location.href = 'login.html';
                return;
            }

            // 显示加载状态
            this.showLoading(true);

            // 加载仪表板数据
            await this.loadDashboardData();

            // 初始化事件监听
            this.initEventListeners();

        } catch (error) {
// console.'初始化仪表板失败:', error);
            this.showError('加载仪表板数据失败，请刷新页面重试');
        } finally {
            this.showLoading(false);
        }
    },

    /**
     * 加载仪表板数据
     */
    async loadDashboardData() {
        try {
            // 加载概览数据（一次性获取所有需要的数据）
            const overviewResponse = await this.fetchApi('/dashboard/overview');

            if (overviewResponse.success) {
                const data = overviewResponse.data;

                // 更新统计卡片
                this.updateStats(data.stats || {});

                // 更新最近活动
                this.updateRecentActivity(data.recentActivity || []);

                // 更新快速操作
                this.updateQuickActions(data.quickActions || []);
            } else {
                throw new Error(overviewResponse.message || '加载数据失败');
            }

            // 更新用户信息显示
            this.updateUserInfo();

        } catch (error) {
// console.'加载仪表板数据失败:', error);
            throw error;
        }
    },

    /**
     * 更新统计卡片
     */
    updateStats(stats) {
        // 访问量
        this.updateStatCard('totalViews', stats.totalViews || 0, stats.viewsChange || 0);

        // 新用户
        this.updateStatCard('totalUsers', stats.totalUsers || 0, stats.usersChange || 0);

        // 转化率
        this.updateStatCard('conversionRate', stats.conversionRate || 0, stats.conversionChange || 0, true);

        // 收入
        this.updateStatCard('revenue', stats.revenue || 0, stats.revenueChange || 0, false, '¥');
    },

    /**
     * 更新单个统计卡片
     */
    updateStatCard(type, value, change, isPercentage = false, prefix = '') {
        // 查找对应的卡片
        const cards = document.querySelectorAll('.stat-card');

        // 根据类型匹配卡片（这里简化处理，实际应该用更精确的选择器）
        let cardIndex = 0;
        if (type === 'totalViews') cardIndex = 0;
        else if (type === 'totalUsers') cardIndex = 1;
        else if (type === 'conversionRate') cardIndex = 2;
        else if (type === 'revenue') cardIndex = 3;

        const card = cards[cardIndex];
        if (!card) return;

        // 更新数值
        const valueElement = card.querySelector('.stat-value');
        if (valueElement) {
            let displayValue = value;
            if (type === 'totalViews' || type === 'totalUsers') {
                displayValue = this.formatNumber(value);
            } else if (isPercentage) {
                displayValue = value.toFixed(1) + '%';
            } else if (type === 'revenue') {
                displayValue = prefix + this.formatNumber(value);
            }
            valueElement.textContent = displayValue;
        }

        // 更新变化率
        const changeElement = card.querySelector('.stat-change');
        if (changeElement) {
            const isPositive = change >= 0;
            changeElement.textContent = (isPositive ? '+' : '') + change.toFixed(1) + '%';
            changeElement.className = 'stat-change' + (isPositive ? '' : ' negative');
        }
    },

    /**
     * 更新最近活动列表
     */
    updateRecentActivity(activities) {
        const activityList = document.querySelector('.activity-list');
        if (!activityList) return;

        if (!activities || activities.length === 0) {
            activityList.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">暂无活动记录</p>';
            return;
        }

        activityList.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="fas ${activity.icon || 'fa-circle'}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-text">${this.sanitize(activity.description)}</div>
                    <div class="activity-time">${this.formatRelativeTime(activity.timestamp)}</div>
                </div>
            </div>
        `).join('');
    },

    /**
     * 更新快速操作
     */
    updateQuickActions(actions) {
        const quickActionsContainer = document.querySelector('.quick-actions');
        if (!quickActionsContainer) return;

        quickActionsContainer.innerHTML = actions.map(action => `
            <a href="${this.sanitize(action.url)}" class="action-btn">
                <i class="fas ${this.sanitize(action.icon)}"></i>
                <span>${this.sanitize(action.name)}</span>
            </a>
        `).join('');
    },

    /**
     * 更新用户信息显示
     */
    updateUserInfo() {
        // 更新欢迎标题
        const welcomeTitle = document.querySelector('.page-header h1');
        if (welcomeTitle && this.currentUser) {
            welcomeTitle.textContent = `欢迎回来，${this.currentUser.name || this.currentUser.username || 'User'}`;
        }

        // 更新侧边栏用户信息
        const userNameElements = document.querySelectorAll('.user-name');
        userNameElements.forEach(el => {
            if (this.currentUser) {
                el.textContent = this.currentUser.name || this.currentUser.username || 'User';
            }
        });

        // 更新用户角色/计划
        const userRoleElements = document.querySelectorAll('.user-role');
        userRoleElements.forEach(el => {
            el.textContent = this.currentUser?.role || 'Free Plan';
        });
    },

    /**
     * 初始化事件监听
     */
    initEventListeners() {
        // 刷新按钮
        const refreshBtn = document.querySelector('[data-action="refresh"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadDashboardData();
            });
        }

        // 自动刷新（每5分钟）
        setInterval(() => {
            this.loadDashboardData().catch(err => {
// console.'自动刷新失败:', err);
            });
        }, 5 * 60 * 1000);
    },

    /**
     * 调用API
     */
    async fetchApi(endpoint, options = {}) {
        const url = `${this.apiBaseUrl}${endpoint}`;

        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        // 添加认证令牌 - 使用全局配置
        const tokenKey = typeof CONFIG !== 'undefined' ? CONFIG.TOKEN_KEY : 'access_token';
        const token = localStorage.getItem(tokenKey) || sessionStorage.getItem(tokenKey);
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }

        const finalOptions = { ...defaultOptions, ...options };

        const response = await fetch(url, finalOptions);

        if (!response.ok) {
            if (response.status === 401) {
                // 未授权，清除登录信息并跳转到登录页
                auth.logout();
                throw new Error('未授权，请重新登录');
            }
            throw new Error(`API请求失败: ${response.status}`);
        }

        return await response.json();
    },

    /**
     * 显示加载状态
     */
    showLoading(show) {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = show ? 'flex' : 'none';
        }
    },

    /**
     * 显示错误消息
     */
    showError(message) {
        app.showToast(message, 'error');
    },

    /**
     * 格式化数字
     */
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },

    /**
     * 格式化相对时间
     */
    formatRelativeTime(timestamp) {
        if (!timestamp) return '未知时间';

        const now = new Date();
        const time = new Date(timestamp);
        const diff = now - time;

        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (seconds < 60) return '刚刚';
        if (minutes < 60) return `${minutes}分钟前`;
        if (hours < 24) return `${hours}小时前`;
        if (days < 7) return `${days}天前`;

        return time.toLocaleDateString('zh-CN');
    },

    /**
     * HTML转义
     */
    sanitize(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    dashboard.init().catch(err => {
// console.'Dashboard初始化失败:', err);
    });
});
