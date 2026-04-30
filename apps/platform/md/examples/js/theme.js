// ==================== 主题管理 ====================
const theme = {
    // 当前主题
    currentTheme: localStorage.getItem('theme') || 'tech-blue',
    currentMode: localStorage.getItem('themeMode') || 'dark',

    // 主题配置
    themes: {
        'tech-blue': {
            name: '科技蓝',
            primary: '#0ea5e9',
            secondary: '#6366f1',
            preview: 'linear-gradient(135deg, #0f172a, #1e293b)'
        },
        'cyber-purple': {
            name: '赛博紫',
            primary: '#9333ea',
            secondary: '#ec4899',
            preview: 'linear-gradient(135deg, #1a0f2e, #2d1b4e)'
        },
        'emerald-green': {
            name: '翡翠绿',
            primary: '#10b981',
            secondary: '#34d399',
            preview: 'linear-gradient(135deg, #064e3b, #065f46)'
        },
        'coral-orange': {
            name: '珊瑚橙',
            primary: '#f97316',
            secondary: '#fb923c',
            preview: 'linear-gradient(135deg, #7c2d12, #9a3412)'
        },
        'rose-pink': {
            name: '玫瑰粉',
            primary: '#f43f5e',
            secondary: '#fb7185',
            preview: 'linear-gradient(135deg, #881337, #9f1239)'
        },
        'midnight-dark': {
            name: '午夜黑',
            primary: '#525252',
            secondary: '#737373',
            preview: 'linear-gradient(135deg, #000000, #1a1a1a)'
        },
        'sunset-gold': {
            name: '日落金',
            primary: '#f59e0b',
            secondary: '#fbbf24',
            preview: 'linear-gradient(135deg, #451a03, #78350f)'
        },
        'ocean-teal': {
            name: '海洋青',
            primary: '#14b8a6',
            secondary: '#2dd4bf',
            preview: 'linear-gradient(135deg, #134e4a, #115e59)'
        }
    },

    // 应用主题
    applyTheme(themeName) {
        if (!this.themes[themeName]) return;
        
        this.currentTheme = themeName;
        localStorage.setItem('theme', themeName);
        
        // 更新 CSS 变量
        const t = this.themes[themeName];
        document.documentElement.style.setProperty('--primary-color', t.primary);
        document.documentElement.style.setProperty('--secondary-color', t.secondary);
        
        // 更新 theme-css 链接
        const themeLink = document.getElementById('theme-css');
        if (themeLink) {
            themeLink.href = `css/themes/${themeName}.css`;
        }
        
        // 更新界面状态
        this.updateThemeUI();
        
        // 显示提示
        this.showToast(`主题已切换为：${t.name}`);
    },

    // 应用模式（深色/浅色/自动）
    applyMode(mode) {
        this.currentMode = mode;
        localStorage.setItem('themeMode', mode);
        
        document.body.classList.remove('dark-mode', 'light-mode');
        
        if (mode === 'dark') {
            document.body.classList.add('dark-mode');
        } else if (mode === 'light') {
            document.body.classList.add('light-mode');
        } else {
            // 自动模式 - 跟随系统
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                document.body.classList.add('dark-mode');
            } else {
                document.body.classList.add('light-mode');
            }
        }
        
        this.updateModeUI();
        this.showToast(mode === 'auto' ? '已切换到跟随系统' : `已切换到${mode === 'dark' ? '深色' : '浅色'}模式`);
    },

    // 更新主题选择器 UI
    updateThemeUI() {
        document.querySelectorAll('.theme-option').forEach(option => {
            option.classList.remove('active');
            if (option.dataset.theme === this.currentTheme) {
                option.classList.add('active');
            }
        });
    },

    // 更新模式选择器 UI
    updateModeUI() {
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.mode === this.currentMode) {
                btn.classList.add('active');
            }
        });
    },

    // 显示提示消息
    showToast(message) {
        // 移除已有的 toast
        const existingToast = document.querySelector('.toast-notification');
        if (existingToast) {
            existingToast.remove();
        }
        
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        document.body.appendChild(toast);
        
        // 动画显示
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });
        
        // 3秒后移除
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    // 初始化主题选择器
    initThemeSelector() {
        // 主题卡片点击
        document.querySelectorAll('.theme-option').forEach(option => {
            option.addEventListener('click', () => {
                const themeName = option.dataset.theme;
                this.applyTheme(themeName);
            });
        });
        
        // 模式按钮点击
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const mode = btn.dataset.mode;
                this.applyMode(mode);
            });
        });
    },

    // 初始化
    init() {
        // 应用保存的设置
        this.applyTheme(this.currentTheme);
        this.applyMode(this.currentMode);
        
        // 绑定事件
        this.initThemeSelector();
    }
};

// ==================== 设置页面功能 ====================
const settings = {
    // 初始化所有设置
    init() {
        this.initLanguageSettings();
        this.initNotificationSettings();
        this.initAccountSettings();
        this.initThemeAndMode();
    },

    // 初始化语言和模式设置
    initThemeAndMode() {
        theme.init();
    },

    // 初始化语言设置
    initLanguageSettings() {
        const savedLang = localStorage.getItem('language') || 'zh-CN';
        
        // 设置语言选择状态
        document.querySelectorAll('.language-option input').forEach(input => {
            input.checked = input.value === savedLang;
        });
        
        // 绑定语言切换
        document.querySelectorAll('.language-option').forEach(option => {
            option.addEventListener('click', (e) => {
                const radio = option.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                    const lang = radio.value;
                    i18n.setLanguage(lang);
                    this.updateLanguageUI(lang);
                }
            });
        });
    },

    // 更新语言选择器 UI
    updateLanguageUI(lang) {
        document.querySelectorAll('.language-option').forEach(option => {
            option.classList.remove('active');
            const input = option.querySelector('input');
            if (input && input.value === lang) {
                option.classList.add('active');
            }
        });
    },

    // 初始化通知设置
    initNotificationSettings() {
        // 从 localStorage 加载设置
        const notifications = JSON.parse(localStorage.getItem('notifications') || '{}');
        
        document.querySelectorAll('.toggle-switch input').forEach(toggle => {
            const settingName = toggle.closest('.setting-item')?.querySelector('.setting-name')?.textContent;
            if (settingName) {
                const key = this.getNotificationKey(settingName);
                toggle.checked = notifications[key] !== false; // 默认开启
            }
            
            // 绑定切换事件
            toggle.addEventListener('change', (e) => {
                const settingName = e.target.closest('.setting-item')?.querySelector('.setting-name')?.textContent;
                if (settingName) {
                    const key = this.getNotificationKey(settingName);
                    const currentSettings = JSON.parse(localStorage.getItem('notifications') || '{}');
                    currentSettings[key] = e.target.checked;
                    localStorage.setItem('notifications', JSON.stringify(currentSettings));
                    
                    const status = e.target.checked ? '已开启' : '已关闭';
                    theme.showToast(`${settingName} ${status}`);
                }
            });
        });
    },

    // 获取通知设置的 key
    getNotificationKey(name) {
        const keyMap = {
            '邮件通知': 'email',
            '推送通知': 'push',
            '营销邮件': 'marketing'
        };
        return keyMap[name] || name;
    },

    // 初始化账户设置
    initAccountSettings() {
        // 加载用户数据
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        
        const nameInput = document.querySelector('.settings-form input[type="text"]');
        const emailInput = document.querySelector('.settings-form input[type="email"]');
        const bioInput = document.querySelector('.settings-form textarea');
        
        if (nameInput && userData.name) nameInput.value = userData.name;
        if (emailInput && userData.email) emailInput.value = userData.email;
        if (bioInput && userData.bio) bioInput.value = userData.bio;
        
        // 保存按钮
        const saveBtn = document.querySelector('.settings-form .btn-primary');
        if (saveBtn) {
            saveBtn.addEventListener('click', (e) => {
                e.preventDefault();
                
                const newData = {
                    name: nameInput?.value || '',
                    email: emailInput?.value || '',
                    bio: bioInput?.value || ''
                };
                
                localStorage.setItem('userData', JSON.stringify(newData));
                theme.showToast('账户信息已保存');
                
                // 更新侧边栏用户名
                const sidebarName = document.querySelector('.user-name');
                if (sidebarName && newData.name) {
                    sidebarName.textContent = newData.name;
                }
            });
        }
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    settings.init();
});
