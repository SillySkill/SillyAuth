/**
 * Settings Controller
 * 用户设置页面控制器
 *
 * 负责管理用户个人信息和偏好设置
 */

const settings = {
    // API基础URL - 使用全局配置
    get apiBaseUrl() {
        return typeof CONFIG !== 'undefined' ? `${CONFIG.API_BASE}/api` : 'http://47.96.133.238:8000/api';
    },

    // 当前用户信息
    currentUser: null,
    userId: null,

    /**
     * 初始化设置页面
     */
    async init() {
        try {
            // 检查登录状态
            this.currentUser = auth.getCurrentUser();
            if (!this.currentUser) {
                window.location.href = 'login.html';
                return;
            }

            // 获取用户ID（实际应该从token中解析）
            this.userId = this.currentUser.id || 1;

            // 显示加载状态
            this.showLoading(true);

            // 加载用户设置
            await this.loadUserSettings();

            // 初始化事件监听
            this.initEventListeners();

        } catch (error) {
// console.'初始化设置页面失败:', error);
            this.showError('加载设置失败，请刷新页面重试');
        } finally {
            this.showLoading(false);
        }
    },

    /**
     * 加载用户设置
     */
    async loadUserSettings() {
        try {
            const response = await this.fetchApi(`/user/settings/settings?user_id=${this.userId}`);

            if (response.success) {
                const data = response.data;

                // 填充个人信息表单
                this.populateProfileForm(data.profile || {});

                // 填充偏好设置
                this.populatePreferences(data.preferences || {});

            } else {
                throw new Error(response.message || '加载设置失败');
            }

        } catch (error) {
// console.'加载用户设置失败:', error);
            throw error;
        }
    },

    /**
     * 填充个人信息表单
     */
    populateProfileForm(profile) {
        // 显示名称
        const nameInput = document.querySelector('input[placeholder="您的名称"]');
        if (nameInput && profile.username) {
            nameInput.value = profile.username;
        }

        // 用户名（通常不可编辑）
        const usernameInput = document.querySelector('input[placeholder="用户名"]');
        if (usernameInput && profile.username) {
            usernameInput.value = '@' + profile.username;
        }

        // 邮箱
        const emailInput = document.querySelector('input[type="email"]');
        if (emailInput && profile.email) {
            emailInput.value = profile.email;
        }

        // 个人简介
        const bioTextarea = document.querySelector('textarea');
        if (bioTextarea && profile.bio) {
            bioTextarea.value = profile.bio;
        }

        // 头像
        if (profile.avatar_url) {
            this.updateAvatar(profile.avatar_url);
        }
    },

    /**
     * 填充偏好设置
     */
    populatePreferences(preferences) {
        // 语言
        if (preferences.language) {
            this.setLanguage(preferences.language);
        }

        // 主题
        if (preferences.theme) {
            this.setTheme(preferences.theme);
        }
    },

    /**
     * 保存个人信息
     */
    async saveProfile() {
        try {
            const nameInput = document.querySelector('input[placeholder="您的名称"]');
            const emailInput = document.querySelector('input[type="email"]');
            const bioTextarea = document.querySelector('textarea');

            const profileData = {
                username: nameInput?.value.trim(),
                email: emailInput?.value.trim(),
                bio: bioTextarea?.value.trim()
            };

            // 验证
            if (!profileData.username) {
                this.showError('请输入显示名称');
                return;
            }

            if (!profileData.email) {
                this.showError('请输入邮箱地址');
                return;
            }

            if (!this.validateEmail(profileData.email)) {
                this.showError('请输入有效的邮箱地址');
                return;
            }

            // 显示保存中状态
            this.showSaving(true);

            // 调用API
            const response = await this.fetchApi(`/user/settings/profile?user_id=${this.userId}`, {
                method: 'PUT',
                body: JSON.stringify(profileData)
            });

            if (response.success) {
                this.showSuccess('个人信息保存成功');

                // 更新本地用户信息
                if (this.currentUser) {
                    this.currentUser.name = profileData.username;
                    this.currentUser.email = profileData.email;
                    localStorage.setItem('user', JSON.stringify(this.currentUser));
                }
            } else {
                throw new Error(response.message || '保存失败');
            }

        } catch (error) {
// console.'保存个人信息失败:', error);
            this.showError(error.message || '保存失败，请重试');
        } finally {
            this.showSaving(false);
        }
    },

    /**
     * 保存偏好设置
     */
    async savePreferences() {
        try {
            const currentLanguage = this.getCurrentLanguage();
            const currentTheme = this.getCurrentTheme();

            const preferencesData = {
                preferred_language: currentLanguage,
                theme_preference: currentTheme
            };

            // 显示保存中状态
            this.showSaving(true);

            // 调用API
            const response = await this.fetchApi(`/user/settings/preferences?user_id=${this.userId}`, {
                method: 'PUT',
                body: JSON.stringify(preferencesData)
            });

            if (response.success) {
                this.showSuccess('偏好设置保存成功');
            } else {
                throw new Error(response.message || '保存失败');
            }

        } catch (error) {
// console.'保存偏好设置失败:', error);
            this.showError(error.message || '保存失败，请重试');
        } finally {
            this.showSaving(false);
        }
    },

    /**
     * 修改密码
     */
    async changePassword() {
        const oldPassword = document.getElementById('oldPassword')?.value;
        const newPassword = document.getElementById('newPassword')?.value;
        const confirmPassword = document.getElementById('confirmPassword')?.value;

        // 验证
        if (!oldPassword || !newPassword || !confirmPassword) {
            this.showError('请填写所有密码字段');
            return;
        }

        if (newPassword !== confirmPassword) {
            this.showError('两次输入的新密码不一致');
            return;
        }

        if (newPassword.length < 8) {
            this.showError('新密码至少需要8个字符');
            return;
        }

        try {
            // 显示保存中状态
            this.showSaving(true);

            // 调用API
            const response = await this.fetchApi(`/user/settings/change-password?user_id=${this.userId}`, {
                method: 'POST',
                body: JSON.stringify({
                    old_password: oldPassword,
                    new_password: newPassword
                })
            });

            if (response.success) {
                this.showSuccess('密码修改成功，请重新登录');

                // 清空密码字段
                document.getElementById('oldPassword').value = '';
                document.getElementById('newPassword').value = '';
                document.getElementById('confirmPassword').value = '';

                // 3秒后跳转到登录页
                setTimeout(() => {
                    auth.logout();
                }, 3000);
            } else {
                throw new Error(response.message || '修改失败');
            }

        } catch (error) {
// console.'修改密码失败:', error);
            this.showError(error.message || '修改失败，请重试');
        } finally {
            this.showSaving(false);
        }
    },

    /**
     * 初始化事件监听
     */
    initEventListeners() {
        // 保存按钮
        const saveBtn = document.querySelector('.settings-form .btn-primary');
        if (saveBtn) {
            saveBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.saveProfile();
            });
        }

        // 主题切换
        const themeOptions = document.querySelectorAll('.theme-option');
        themeOptions.forEach(option => {
            option.addEventListener('click', () => {
                const theme = option.dataset.theme;
                if (theme) {
                    this.setTheme(theme);
                    this.savePreferences();
                }
            });
        });

        // 模式切换
        const modeBtns = document.querySelectorAll('.mode-btn');
        modeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const mode = btn.dataset.mode;
                if (mode) {
                    this.setMode(mode);
                }
            });
        });

        // 语言选择器
        const langBtns = document.querySelectorAll('.lang-dropdown a');
        langBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const lang = btn.dataset.lang;
                if (lang) {
                    this.setLanguage(lang);
                    this.savePreferences();
                }
            });
        });
    },

    /**
     * 设置主题
     */
    setTheme(theme) {
        // 移除所有活动状态
        document.querySelectorAll('.theme-option').forEach(el => {
            el.classList.remove('active');
        });

        // 添加当前活动状态
        const currentOption = document.querySelector(`[data-theme="${theme}"]`);
        if (currentOption) {
            currentOption.classList.add('active');
        }

        // 实际应用主题（需要配合CSS）
// // console.log('Setting theme:', theme);
    },

    /**
     * 设置模式
     */
    setMode(mode) {
        // 移除所有活动状态
        document.querySelectorAll('.mode-btn').forEach(el => {
            el.classList.remove('active');
        });

        // 添加当前活动状态
        const currentBtn = document.querySelector(`[data-mode="${mode}"]`);
        if (currentBtn) {
            currentBtn.classList.add('active');
        }

        // 应用模式
// // console.log('Setting mode:', mode);
    },

    /**
     * 设置语言
     */
    setLanguage(lang) {
        // 更新显示
        const langBtn = document.getElementById('langBtn');
        if (langBtn) {
            const span = langBtn.querySelector('span');
            const langMap = {
                'zh-CN': '中文',
                'en': 'English',
                'ja': '日本語',
                'ko': '한국어'
            };
            if (span) {
                span.textContent = langMap[lang] || lang;
            }
        }

        // 实际应用语言（需要配合i18n）
// // console.log('Setting language:', lang);
    },

    /**
     * 获取当前语言
     */
    getCurrentLanguage() {
        const langBtn = document.getElementById('langBtn');
        if (langBtn) {
            const span = langBtn.querySelector('span');
            const langMap = {
                '中文': 'zh-CN',
                'English': 'en',
                '日本語': 'ja',
                '한국어': 'ko'
            };
            return langMap[span?.textContent] || 'zh-CN';
        }
        return 'zh-CN';
    },

    /**
     * 获取当前主题
     */
    getCurrentTheme() {
        const activeOption = document.querySelector('.theme-option.active');
        return activeOption?.dataset.theme || 'tech-blue';
    },

    /**
     * 更新头像显示
     */
    updateAvatar(url) {
        const avatarImg = document.querySelector('.user-avatar img');
        if (avatarImg) {
            avatarImg.src = url;
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
     * 显示保存中状态
     */
    showSaving(show) {
        const saveBtns = document.querySelectorAll('.btn-primary');
        saveBtns.forEach(btn => {
            if (show) {
                btn.disabled = true;
                btn.dataset.originalText = btn.textContent;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 保存中...';
            } else {
                btn.disabled = false;
                if (btn.dataset.originalText) {
                    btn.textContent = btn.dataset.originalText;
                }
            }
        });
    },

    /**
     * 显示成功消息
     */
    showSuccess(message) {
        this.showToast(message, 'success');
    },

    /**
     * 显示错误消息
     */
    showError(message) {
        this.showToast(message, 'error');
    },

    /**
     * 显示提示消息
     */
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast-notification`;
        toast.style.position = 'fixed';
        toast.style.bottom = '24px';
        toast.style.right = '24px';
        toast.style.background = type === 'success'
            ? 'linear-gradient(135deg, #10b981, #34d399)'
            : 'linear-gradient(135deg, #ef4444, #f87171)';
        toast.style.color = 'white';
        toast.style.padding = '14px 24px';
        toast.style.borderRadius = '12px';
        toast.style.display = 'flex';
        toast.style.alignItems = 'center';
        toast.style.gap = '12px';
        toast.style.zIndex = '10000';

        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
        toast.innerHTML = `<i class="fas ${icon}"></i><span>${message}</span>`;

        document.body.appendChild(toast);

        // 动画进入
        setTimeout(() => toast.style.transform = 'translateY(0)', 10);
        setTimeout(() => toast.style.opacity = '1', 10);

        // 自动消失
        setTimeout(() => {
            toast.style.transform = 'translateY(100px)';
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    /**
     * 验证邮箱格式
     */
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    settings.init().catch(err => {
// console.'Settings初始化失败:', err);
    });
});
