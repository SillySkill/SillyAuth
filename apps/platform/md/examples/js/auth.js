// ==================== 认证功能 ====================
const auth = {
    // API 基础地址 - 使用全局配置
    API_BASE_URL: typeof CONFIG !== 'undefined' ? CONFIG.API_BASE : 'http://47.96.133.238:8000',

    // 表单验证
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    // 密码强度检�?    checkPasswordStrength(password) {
        let strength = 0;
        if (password.length >= 8) strength++;
        if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
        if (password.match(/\d/)) strength++;
        if (password.match(/[^a-zA-Z\d]/)) strength++;
        return strength;
    },

    // 更新密码强度显示
    updatePasswordStrength(password) {
        const strengthBar = document.querySelector('.strength-bar');
        const strengthText = document.querySelector('.strength-text');
        if (!strengthBar || !strengthText) return;

        const strength = this.checkPasswordStrength(password);

        strengthBar.classList.remove('weak', 'medium', 'strong');

        if (password.length === 0) {
            strengthText.textContent = i18n ? i18n.t('form.passwordStrength') : '密码强度';
        } else if (strength <= 1) {
            strengthBar.classList.add('weak');
            strengthText.textContent = '�?;
        } else if (strength === 2) {
            strengthBar.classList.add('medium');
            strengthText.textContent = '�?;
        } else {
            strengthBar.classList.add('strong');
            strengthText.textContent = '�?;
        }
    },

    // 显示错误信息
    showError(fieldId, message) {
        const field = document.getElementById(fieldId);
        if (!field) return;

        // 移除已有的错误提�?        this.clearError(fieldId);

        field.classList.add('error');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        field.parentElement.appendChild(errorDiv);
    },

    // 清除错误信息
    clearError(fieldId) {
        const field = document.getElementById(fieldId);
        if (!field) return;

        field.classList.remove('error');
        const errorDiv = field.parentElement.querySelector('.error-message');
        if (errorDiv) {
            errorDiv.remove();
        }
    },

    // 显示全局消息
    showMessage(message, type = 'success') {
        // 移除已有消息
        const existingMsg = document.querySelector('.auth-global-message');
        if (existingMsg) {
            existingMsg.remove();
        }

        const msgDiv = document.createElement('div');
        msgDiv.className = `auth-global-message ${type}`;
        msgDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(msgDiv);

        // 3 秒后自动消失
        setTimeout(() => {
            msgDiv.classList.add('fade-out');
            setTimeout(() => msgDiv.remove(), 300);
        }, 3000);
    },

    // 显示加载状�?    setLoading(form, loading) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (!submitBtn) return;

        if (loading) {
            submitBtn.disabled = true;
            submitBtn.dataset.originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 加载�?..';
        } else {
            submitBtn.disabled = false;
            if (submitBtn.dataset.originalText) {
                submitBtn.innerHTML = submitBtn.dataset.originalText;
            }
        }
    },

    // API 请求辅助函数
    async apiRequest(endpoint, options = {}) {
        const url = `${this.API_BASE_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        // 添加认证令牌
        const token = this.getAccessToken();
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || data.message || '请求失败');
            }

            return data;
        } catch (error) {
// console.'API 请求错误:', error);
            throw error;
        }
    },

    // Token 管理
    saveTokens(accessToken, refreshToken, rememberMe = false) {
        const tokenKey = typeof CONFIG !== 'undefined' ? CONFIG.TOKEN_KEY : 'access_token';
        const refreshKey = typeof CONFIG !== 'undefined' ? CONFIG.REFRESH_TOKEN_KEY : 'refresh_token';

        if (rememberMe) {
            localStorage.setItem(tokenKey, accessToken);
            localStorage.setItem(refreshKey, refreshToken);
        } else {
            sessionStorage.setItem(tokenKey, accessToken);
            sessionStorage.setItem(refreshKey, refreshToken);
        }
    },

    getAccessToken() {
        const tokenKey = typeof CONFIG !== 'undefined' ? CONFIG.TOKEN_KEY : 'access_token';
        return localStorage.getItem(tokenKey) || sessionStorage.getItem(tokenKey);
    },

    getRefreshToken() {
        const refreshKey = typeof CONFIG !== 'undefined' ? CONFIG.REFRESH_TOKEN_KEY : 'refresh_token';
        return localStorage.getItem(refreshKey) || sessionStorage.getItem(refreshKey);
    },

    clearTokens() {
        const tokenKey = typeof CONFIG !== 'undefined' ? CONFIG.TOKEN_KEY : 'access_token';
        const refreshKey = typeof CONFIG !== 'undefined' ? CONFIG.REFRESH_TOKEN_KEY : 'refresh_token';

        localStorage.removeItem(tokenKey);
        localStorage.removeItem(refreshKey);
        sessionStorage.removeItem(tokenKey);
        sessionStorage.removeItem(refreshKey);
    },

    // 登录
    async login(email, password, remember = false) {
        try {
            // TODO: 临时模拟登录 - 需要后端实现真实的认证API
            // 当后端实�?/api/auth/login 后，请取消下面的注释并删除模拟代�?
            /*
            const response = await this.apiRequest('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify({
                    email: email,
                    password: password,
                    remember_me: remember
                })
            });

            // 保存令牌
            this.saveTokens(response.access_token, response.refresh_token, remember);

            // 保存用户信息
            if (remember) {
                localStorage.setItem('user', JSON.stringify(response.user));
            } else {
                sessionStorage.setItem('user', JSON.stringify(response.user));
            }

            return { success: true, user: response.user };
            */

            // ===== 临时模拟登录代码开�?=====
// console.'⚠️ 使用模拟登录模式 - 后端认证API尚未实现');

            // 模拟网络延迟
            await new Promise(resolve => setTimeout(resolve, 800));

            // 简单验证：邮箱和密码不为空
            if (!email || !password) {
                return { success: false, message: '请输入邮箱和密码' };
            }

            // 生成模拟响应
            const mockResponse = {
                access_token: 'mock_access_token_' + Date.now() + '_' + Math.random().toString(36).substr(2),
                refresh_token: 'mock_refresh_token_' + Date.now() + '_' + Math.random().toString(36).substr(2),
                user: {
                    id: Math.floor(Math.random() * 10000),
                    username: email.split('@')[0],
                    email: email,
                    first_name: '',
                    last_name: '',
                    role: 'user',
                    vendor_level: 'basic',
                    is_active: true,
                    is_verified: true
                }
            };

            // 保存令牌
            this.saveTokens(mockResponse.access_token, mockResponse.refresh_token, remember);

            // 保存用户信息
            if (remember) {
                localStorage.setItem('user', JSON.stringify(mockResponse.user));
            } else {
                sessionStorage.setItem('user', JSON.stringify(mockResponse.user));
            }

// // console.log('�?模拟登录成功:', mockResponse.user);
            return { success: true, user: mockResponse.user };
            // ===== 临时模拟登录代码结束 =====

        } catch (error) {
// console.'登录失败:', error);
            return { success: false, message: error.message };
        }
    },

    // 注册
    async register(userData) {
        try {
            // TODO: 临时模拟注册 - 需要后端实现真实的注册API
            // 当后端实�?/api/auth/register 后，请取消下面的注释并删除模拟代�?
            /*
            const response = await this.apiRequest('/api/auth/register', {
                method: 'POST',
                body: JSON.stringify(userData)
            });

            return { success: true, data: response.data, message: response.message };
            */

            // ===== 临时模拟注册代码开�?=====
// console.'⚠️ 使用模拟注册模式 - 后端注册API尚未实现');

            // 模拟网络延迟
            await new Promise(resolve => setTimeout(resolve, 1000));

            // 简单验�?            if (!userData.email || !userData.password) {
                return { success: false, message: '请填写完整信�? };
            }

            if (userData.password.length < 8) {
                return { success: false, message: '密码至少需�?个字�? };
            }

// // console.log('�?模拟注册成功:', userData.email);
            return {
                success: true,
                data: { email: userData.email, username: userData.username },
                message: '注册成功！请登录您的账户�?
            };
            // ===== 临时模拟注册代码结束 =====

        } catch (error) {
// console.'注册失败:', error);
            return { success: false, message: error.message };
        }
    },

    // 忘记密码
    async forgotPassword(email) {
        try {
            // TODO: 临时模拟忘记密码 - 需要后端实现真实的API
            // 当后端实�?/api/auth/forgot-password 后，请取消下面的注释并删除模拟代�?
            /*
            const response = await this.apiRequest('/api/auth/forgot-password', {
                method: 'POST',
                body: JSON.stringify({ email: email })
            });

            return { success: true, message: response.message, data: response.data };
            */

            // ===== 临时模拟代码开�?=====
// console.'⚠️ 使用模拟忘记密码模式 - 后端API尚未实现');

            // 模拟网络延迟
            await new Promise(resolve => setTimeout(resolve, 800));

            if (!email) {
                return { success: false, message: '请输入邮箱地址' };
            }

            // 生成模拟重置链接
            const resetToken = 'reset_' + Date.now() + '_' + Math.random().toString(36).substr(2);
            const resetLink = window.location.origin + '/examples/reset-password.html?token=' + resetToken;

// // console.log('📧 模拟发送重置邮件到:', email);
// // console.log('🔗 重置链接:', resetLink);

            return {
                success: true,
                message: '密码重置链接已发送到您的邮箱',
                data: { reset_link: resetLink }
            };
            // ===== 临时模拟代码结束 =====

        } catch (error) {
// console.'发送重置邮件失�?', error);
            return { success: false, message: error.message };
        }
    },

    // 重置密码
    async resetPassword(token, newPassword) {
        try {
            // TODO: 临时模拟重置密码 - 需要后端实现真实的API
            // 当后端实�?/api/auth/reset-password 后，请取消下面的注释并删除模拟代�?
            /*
            const response = await this.apiRequest('/api/auth/reset-password', {
                method: 'POST',
                body: JSON.stringify({
                    token: token,
                    new_password: newPassword,
                    confirm_password: newPassword
                })
            });

            return { success: true, message: response.message };
            */

            // ===== 临时模拟代码开�?=====
// console.'⚠️ 使用模拟重置密码模式 - 后端API尚未实现');

            // 模拟网络延迟
            await new Promise(resolve => setTimeout(resolve, 800));

            if (!token) {
                return { success: false, message: '无效的重置链�? };
            }

            if (!newPassword || newPassword.length < 8) {
                return { success: false, message: '密码至少需�?个字�? };
            }

// // console.log('�?模拟密码重置成功, token:', token);
            return { success: true, message: '密码重置成功！请使用新密码登录�? };
            // ===== 临时模拟代码结束 =====

        } catch (error) {
// console.'重置密码失败:', error);
            return { success: false, message: error.message };
        }
    },

    // 刷新令牌
    async refreshAccessToken() {
        try {
            const refreshToken = this.getRefreshToken();
            if (!refreshToken) {
                throw new Error('没有刷新令牌');
            }

            const response = await this.apiRequest('/api/auth/refresh-token', {
                method: 'POST',
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            // 更新令牌
            const tokenKey = typeof CONFIG !== 'undefined' ? CONFIG.TOKEN_KEY : 'access_token';
            const rememberMe = !!localStorage.getItem(tokenKey);
            this.saveTokens(response.access_token, response.refresh_token, rememberMe);

            return response.access_token;
        } catch (error) {
// console.'刷新令牌失败:', error);
            this.logout();
            throw error;
        }
    },

    // 检查登录状�?    isLoggedIn() {
        return !!this.getAccessToken();
    },

    // 获取当前用户
    getCurrentUser() {
        const user = localStorage.getItem('user') || sessionStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    // 登出
    logout() {
        this.clearTokens();
        localStorage.removeItem('user');
        sessionStorage.removeItem('user');
        window.location.href = 'login.html';
    },

    // 初始化登录表�?    initLoginForm() {
        const form = document.getElementById('loginForm');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // 清除之前的错�?            this.clearError('email');
            this.clearError('password');

            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const remember = document.querySelector('input[name="remember"]')?.checked || false;

            // 验证
            let hasError = false;

            if (!email) {
                this.showError('email', '请输入邮箱地址');
                hasError = true;
            } else if (!this.validateEmail(email)) {
                this.showError('email', '请输入有效的邮箱地址');
                hasError = true;
            }

            if (!password) {
                this.showError('password', '请输入密�?);
                hasError = true;
            }

            if (hasError) return;

            // 提交
            this.setLoading(form, true);

            try {
                const result = await this.login(email, password, remember);
                if (result.success) {
                    this.showMessage('登录成功，正在跳�?..');
                    setTimeout(() => {
                        window.location.href = 'dashboard.html';
                    }, 1000);
                } else {
                    this.showError('email', result.message || '登录失败，请检查邮箱和密码');
                }
            } catch (error) {
                this.showError('email', '登录失败，请稍后重试');
            } finally {
                this.setLoading(form, false);
            }
        });
    },

    // 初始化注册表�?    initRegisterForm() {
        const form = document.getElementById('registerForm');
        if (!form) return;

        // 密码强度检�?        const passwordInput = document.getElementById('password');
        if (passwordInput) {
            passwordInput.addEventListener('input', (e) => {
                this.updatePasswordStrength(e.target.value);
            });
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // 清除之前的错�?            ['firstName', 'lastName', 'email', 'password', 'confirmPassword'].forEach(id => {
                this.clearError(id);
            });

            const firstName = document.getElementById('firstName').value.trim();
            const lastName = document.getElementById('lastName').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const terms = document.querySelector('input[name="terms"]')?.checked || false;

            // 验证
            let hasError = false;

            if (!firstName) {
                this.showError('firstName', '请输入名�?);
                hasError = true;
            }

            if (!lastName) {
                this.showError('lastName', '请输入姓�?);
                hasError = true;
            }

            if (!email) {
                this.showError('email', '请输入邮箱地址');
                hasError = true;
            } else if (!this.validateEmail(email)) {
                this.showError('email', '请输入有效的邮箱地址');
                hasError = true;
            }

            if (!password) {
                this.showError('password', '请输入密�?);
                hasError = true;
            } else if (password.length < 8) {
                this.showError('password', '密码至少需�?个字�?);
                hasError = true;
            }

            if (password !== confirmPassword) {
                this.showError('confirmPassword', '两次输入的密码不一�?);
                hasError = true;
            }

            if (!terms) {
                this.showMessage('请同意服务条款和隐私政策', 'error');
                hasError = true;
            }

            if (hasError) return;

            // 提交
            this.setLoading(form, true);

            try {
                const username = firstName + lastName; // 简单生成用户名
                const result = await this.register({
                    username: username,
                    email: email,
                    password: password,
                    first_name: firstName,
                    last_name: lastName
                });

                if (result.success) {
                    this.showMessage(result.message || '注册成功！正在跳转到登录页面...');
                    setTimeout(() => {
                        window.location.href = 'login.html';
                    }, 2000);
                }
            } catch (error) {
                this.showMessage('注册失败，请稍后重试', 'error');
            } finally {
                this.setLoading(form, false);
            }
        });
    },

    // 初始化忘记密码表�?    initForgotPasswordForm() {
        const form = document.getElementById('forgotForm');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // 清除之前的错�?            this.clearError('email');

            const email = document.getElementById('email').value.trim();

            // 验证
            let hasError = false;

            if (!email) {
                this.showError('email', '请输入邮箱地址');
                hasError = true;
            } else if (!this.validateEmail(email)) {
                this.showError('email', '请输入有效的邮箱地址');
                hasError = true;
            }

            if (hasError) return;

            // 提交
            this.setLoading(form, true);

            try {
                const result = await this.forgotPassword(email);
                if (result.success) {
                    this.showMessage(result.message || '重置链接已发送到您的邮箱');

                    // 开发环境：显示重置链接
                    if (result.data && result.data.reset_link) {
// // console.log('密码重置链接:', result.data.reset_link);

                        // 可选：自动跳转到重置页面（仅用于开发测试）
                        // window.location.href = result.data.reset_link;
                    }

                    form.reset();
                }
            } catch (error) {
                this.showMessage('发送失败，请稍后重�?, 'error');
            } finally {
                this.setLoading(form, false);
            }
        });
    },

    // 初始化重置密码表�?    initResetPasswordForm() {
        const form = document.getElementById('resetPasswordForm');
        if (!form) return;

        // �?URL 获取 token
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');

        if (!token) {
            this.showMessage('无效的重置链�?, 'error');
            form.disabled = true;
            return;
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // 清除之前的错�?            this.clearError('newPassword');
            this.clearError('confirmPassword');

            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            // 验证
            let hasError = false;

            if (!newPassword) {
                this.showError('newPassword', '请输入新密码');
                hasError = true;
            } else if (newPassword.length < 8) {
                this.showError('newPassword', '密码至少需�?个字�?);
                hasError = true;
            }

            if (newPassword !== confirmPassword) {
                this.showError('confirmPassword', '两次输入的密码不一�?);
                hasError = true;
            }

            if (hasError) return;

            // 提交
            this.setLoading(form, true);

            try {
                const result = await this.resetPassword(token, newPassword);
                if (result.success) {
                    this.showMessage(result.message || '密码重置成功！正在跳转到登录页面...');
                    setTimeout(() => {
                        window.location.href = 'login.html';
                    }, 2000);
                }
            } catch (error) {
                this.showMessage('重置失败，请稍后重试', 'error');
            } finally {
                this.setLoading(form, false);
            }
        });
    },

    // 切换密码显示
    initPasswordToggle() {
        document.querySelectorAll('.toggle-password').forEach(btn => {
            btn.addEventListener('click', () => {
                const input = btn.parentElement.querySelector('input');
                const icon = btn.querySelector('i');

                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            });
        });
    },

    // 初始�?    init() {
        this.initLoginForm();
        this.initRegisterForm();
        this.initForgotPasswordForm();
        this.initResetPasswordForm();
        this.initPasswordToggle();

        // 检查是否在需要认证的页面
        const protectedPages = ['dashboard.html', 'settings.html', 'analytics.html'];
        const currentPage = window.location.pathname.split('/').pop();

        if (protectedPages.includes(currentPage) && !this.isLoggedIn()) {
            window.location.href = 'login.html';
        }
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    auth.init();
});
