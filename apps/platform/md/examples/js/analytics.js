/**
 * Analytics Controller
 * 数据分析页面控制器
 *
 * 负责加载和显示网站访问分析数据
 */

const analytics = {
    // API基础URL - 使用全局配置
    get apiBaseUrl() {
        return typeof CONFIG !== 'undefined' ? `${CONFIG.API_BASE}/api` : 'http://47.96.133.238:8000/api';
    },

    // 当前用户信息
    currentUser: null,

    // 图表实例
    charts: {},

    // 当前选择的时间范围
    currentDays: 7,

    /**
     * 初始化分析页面
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

            // 加载分析数据
            await this.loadAnalyticsData();

            // 初始化事件监听
            this.initEventListeners();

            // 初始化图表
            this.initCharts();

        } catch (error) {
// console.'初始化分析页面失败:', error);
            this.showError('加载分析数据失败，请刷新页面重试');
        } finally {
            this.showLoading(false);
        }
    },

    /**
     * 加载分析数据
     */
    async loadAnalyticsData() {
        try {
            // 并行加载各种数据
            const [overview, trend, userActivity, topPages] = await Promise.all([
                this.fetchApi(`/analytics/overview?days=${this.currentDays}`),
                this.fetchApi(`/analytics/trend?days=${this.currentDays}`),
                this.fetchApi(`/analytics/user-activity?days=${this.currentDays}`),
                this.fetchApi(`/analytics/top-pages?days=${this.currentDays}&limit=10`)
            ]);

            // 更新统计数据
            if (overview.success) {
                this.updateStats(overview.data);
            }

            // 更新趋势图
            if (trend.success) {
                this.updateTrendChart(trend.data);
            }

            // 更新用户活动
            if (userActivity.success) {
                this.updateUserActivity(userActivity.data);
            }

            // 更新热门页面
            if (topPages.success) {
                this.updateTopPages(topPages.data);
            }

        } catch (error) {
// console.'加载分析数据失败:', error);
            throw error;
        }
    },

    /**
     * 更新统计卡片
     */
    updateStats(stats) {
        this.updateStatCard(0, stats.totalVisitors || 0, stats.visitorsChange || 0);
        this.updateStatCard(1, stats.pageViews || 0, stats.pageViewsChange || 0);
        this.updateStatCard(2, stats.avgTimeOnPage || 0, stats.timeOnPageChange || 0, true);
        this.updateStatCard(3, stats.bounceRate || 0, stats.bounceRateChange || 0, true);
    },

    /**
     * 更新单个统计卡片
     */
    updateStatCard(index, value, change, isTime = false) {
        const cards = document.querySelectorAll('.stat-card');
        const card = cards[index];
        if (!card) return;

        // 更新数值
        const valueElement = card.querySelector('.stat-value');
        if (valueElement) {
            let displayValue;
            if (index === 0 || index === 1) {
                displayValue = this.formatNumber(value);
            } else if (index === 2) {
                // 平均停留时间
                const minutes = Math.floor(value / 60);
                const seconds = Math.floor(value % 60);
                displayValue = `${minutes}m ${seconds}s`;
            } else if (index === 3) {
                // 跳出率
                displayValue = value.toFixed(1) + '%';
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
     * 更新趋势图表
     */
    updateTrendChart(trendData) {
        if (!trendData || trendData.length === 0) return;

        const labels = trendData.map(d => this.formatDate(d.date));
        const visitorsData = trendData.map(d => d.visitors);
        const pageViewsData = trendData.map(d => d.pageViews);

        // 如果图表已存在，更新数据
        if (this.charts.trend) {
            this.charts.trend.data.labels = labels;
            this.charts.trend.data.datasets[0].data = visitorsData;
            this.charts.trend.data.datasets[1].data = pageViewsData;
            this.charts.trend.update();
        }
    },

    /**
     * 更新用户活动
     */
    updateUserActivity(activityData) {
        // 可以在这里添加用户活动统计的显示逻辑
// // console.log('User activity data:', activityData);
    },

    /**
     * 更新热门页面
     */
    updateTopPages(pagesData) {
        // 可以在这里添加热门页面列表的显示逻辑
// // console.log('Top pages data:', pagesData);
    },

    /**
     * 初始化图表
     */
    initCharts() {
        // 检查Chart.js是否已加载
        if (typeof Chart === 'undefined') {
// console.'Chart.js未加载，无法显示图表');
            return;
        }

        // 创建趋势图表
        this.createTrendChart();

        // 创建小时统计图表
        this.createHourlyChart();
    },

    /**
     * 创建趋势图表
     */
    async createTrendChart() {
        const ctx = document.getElementById('trendChart');
        if (!ctx) {
// console.'趋势图表容器未找到');
            return;
        }

        // 获取趋势数据
        const trendResponse = await this.fetchApi(`/analytics/trend?days=${this.currentDays}`);
        if (!trendResponse.success) return;

        const trendData = trendResponse.data;
        const labels = trendData.map(d => this.formatDate(d.date));

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: '访问量',
                        data: trendData.map(d => d.visitors),
                        borderColor: 'rgb(99, 102, 241)',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: '页面浏览量',
                        data: trendData.map(d => d.pageViews),
                        borderColor: 'rgb(16, 185, 129)',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    },

    /**
     * 创建小时统计图表
     */
    async createHourlyChart() {
        const ctx = document.getElementById('hourlyChart');
        if (!ctx) return;

        // 获取小时统计数据
        const hourlyResponse = await this.fetchApi('/analytics/hourly?days=7');
        if (!hourlyResponse.success) return;

        const hourlyData = hourlyResponse.data;
        const labels = hourlyData.map(d => `${d.hour}:00`);

        this.charts.hourly = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '访问量',
                    data: hourlyData.map(d => d.views),
                    backgroundColor: 'rgba(99, 102, 241, 0.5)',
                    borderColor: 'rgb(99, 102, 241)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    },

    /**
     * 初始化事件监听
     */
    initEventListeners() {
        // 时间范围选择器
        const timeRangeButtons = document.querySelectorAll('[data-days]');
        timeRangeButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const days = parseInt(btn.dataset.days);
                if (days && days !== this.currentDays) {
                    this.currentDays = days;

                    // 更新按钮状态
                    timeRangeButtons.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');

                    // 重新加载数据
                    this.loadAnalyticsData();
                }
            });
        });

        // 导出按钮
        const exportBtn = document.querySelector('[data-action="export"]');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportData();
            });
        }

        // 刷新按钮
        const refreshBtn = document.querySelector('[data-action="refresh"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadAnalyticsData();
            });
        }
    },

    /**
     * 导出数据
     */
    async exportData() {
        try {
            const endDate = new Date();
            const startDate = new Date();
            startDate.setDate(startDate.getDate() - this.currentDays);

            const startDateStr = startDate.toISOString().split('T')[0];
            const endDateStr = endDate.toISOString().split('T')[0];

            const response = await this.fetchApi(
                `/analytics/export?start_date=${startDateStr}&end_date=${endDateStr}&format=csv`
            );

            if (response.success) {
                // 创建下载链接
                const blob = new Blob([response.data], { type: 'text/csv' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `analytics_${startDateStr}_${endDateStr}.csv`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                this.showSuccess('数据导出成功');
            } else {
                throw new Error(response.message || '导出失败');
            }

        } catch (error) {
// console.'导出数据失败:', error);
            this.showError('导出失败，请重试');
        }
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
     * 显示成功消息
     */
    showSuccess(message) {
        app.showToast(message, 'success');
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
     * 格式化日期
     */
    formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return `${date.getMonth() + 1}/${date.getDate()}`;
    },
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    analytics.init().catch(err => {
// console.'Analytics初始化失败:', err);
    });
});
