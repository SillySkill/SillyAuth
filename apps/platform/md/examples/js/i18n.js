// ==================== 多语言支持 ====================
const i18n = {
    // 当前语言
    currentLang: localStorage.getItem('language') || 'zh-CN',
    
    // 翻译数据
    translations: {
        'zh-CN': {
            'site.name': '挺傻的网站',
            'site.title': '挺傻的网站 - 首页',
            'nav.home': '首页',
            'nav.features': '功能',
            'nav.pricing': '价格',
            'nav.about': '关于',
            'nav.login': '登录',
            'nav.register': '注册',
            'nav.dashboard': '控制台',
            'nav.profile': '个人资料',
            'nav.settings': '设置',
            'nav.logout': '退出登录',
            'hero.title': '让复杂变简单',
            'hero.subtitle': '挺傻的网站提供一站式解决方案，帮助您轻松管理业务、提升效率、实现增长',
            'hero.ctaPrimary': '免费开始使用',
            'hero.ctaSecondary': '了解更多',
            'hero.users': '活跃用户',
            'hero.uptime': '正常运行时间',
            'hero.countries': '覆盖国家',
            'features.title': '强大功能',
            'features.subtitle': '为您提供全方位的解决方案',
            'features.fast.title': '极速体验',
            'features.fast.desc': '采用最新技术架构，确保毫秒级响应速度',
            'features.secure.title': '安全可靠',
            'features.secure.desc': '企业级安全标准，端到端加密保护',
            'features.integrate.title': '轻松集成',
            'features.integrate.desc': '丰富的API接口，与现有系统无缝对接',
            'features.support.title': '24/7 支持',
            'features.support.desc': '专业技术团队全天候为您服务',
            'cta.title': '准备好开始了吗？',
            'cta.subtitle': '立即注册，享受14天免费试用',
            'cta.button': '立即注册',
            'footer.slogan': '让复杂变简单',
            'footer.product': '产品',
            'footer.company': '公司',
            'footer.legal': '法律',
            'footer.contact': '联系我们',
            'footer.careers': '招聘',
            'footer.privacy': '隐私政策',
            'footer.terms': '服务条款',
            'login.title': '登录 - 挺傻的网站',
            'login.heading': '欢迎回来',
            'login.subtitle': '登录您的账户继续使用',
            'login.button': '登录',
            'login.noAccount': '还没有账户？',
            'login.registerNow': '立即注册',
            'register.title': '注册 - 挺傻的网站',
            'register.heading': '创建账户',
            'register.subtitle': '开始您的免费试用之旅',
            'register.button': '创建账户',
            'register.hasAccount': '已有账户？',
            'register.loginNow': '立即登录',
            'form.email': '邮箱地址',
            'form.emailPlaceholder': 'name@example.com',
            'form.password': '密码',
            'form.passwordPlaceholder': '••••••••',
            'form.confirmPassword': '确认密码',
            'form.confirmPasswordPlaceholder': '••••••••',
            'form.firstName': '名',
            'form.firstNamePlaceholder': 'John',
            'form.lastName': '姓',
            'form.lastNamePlaceholder': 'Doe',
            'form.remember': '记住我',
            'form.forgotPassword': '忘记密码？',
            'form.passwordStrength': '密码强度',
            'form.agreeTerms': '我同意',
            'form.termsOfService': '服务条款',
            'form.and': '和',
            'form.privacyPolicy': '隐私政策',
            'auth.orContinueWith': '或使用以下方式',
            'dashboard.title': '控制台 - 挺傻的网站',
            'dashboard.welcome': '欢迎回来',
            'dashboard.overview': '概览',
            'dashboard.analytics': '分析',
            'dashboard.projects': '项目',
            'dashboard.messages': '消息',
            'settings.title': '设置 - 挺傻的网站',
            'settings.account': '账户设置',
            'settings.security': '安全',
            'settings.notifications': '通知',
            'settings.language': '语言',
            'settings.theme': '主题',
            'btn.save': '保存',
            'btn.cancel': '取消',
            'btn.edit': '编辑',
            'btn.delete': '删除',
            'btn.create': '创建',
            'btn.upload': '上传',
            'btn.download': '下载',
            'msg.success': '操作成功',
            'msg.error': '操作失败',
            'msg.loading': '加载中...',
            'msg.confirmDelete': '确定要删除吗？',
            'msg.sessionExpired': '会话已过期，请重新登录',
        },
        'en': {
            'site.name': 'TingSha Website',
            'site.title': 'TingSha Website - Home',
            'nav.home': 'Home',
            'nav.features': 'Features',
            'nav.pricing': 'Pricing',
            'nav.about': 'About',
            'nav.login': 'Login',
            'nav.register': 'Register',
            'nav.dashboard': 'Dashboard',
            'nav.profile': 'Profile',
            'nav.settings': 'Settings',
            'nav.logout': 'Logout',
            'hero.title': 'Make Complex Simple',
            'hero.subtitle': 'TingSha Website provides one-stop solutions to help you manage business, improve efficiency and achieve growth',
            'hero.ctaPrimary': 'Get Started Free',
            'hero.ctaSecondary': 'Learn More',
            'hero.users': 'Active Users',
            'hero.uptime': 'Uptime',
            'hero.countries': 'Countries',
            'features.title': 'Powerful Features',
            'features.subtitle': 'Comprehensive solutions for you',
            'features.fast.title': 'Lightning Fast',
            'features.fast.desc': 'Latest tech architecture ensures millisecond response time',
            'features.secure.title': 'Secure & Reliable',
            'features.secure.desc': 'Enterprise-grade security with end-to-end encryption',
            'features.integrate.title': 'Easy Integration',
            'features.integrate.desc': 'Rich APIs for seamless integration with existing systems',
            'features.support.title': '24/7 Support',
            'features.support.desc': 'Professional technical team at your service round the clock',
            'cta.title': 'Ready to Get Started?',
            'cta.subtitle': 'Sign up now for a 14-day free trial',
            'cta.button': 'Sign Up Now',
            'footer.slogan': 'Make Complex Simple',
            'footer.product': 'Product',
            'footer.company': 'Company',
            'footer.legal': 'Legal',
            'footer.contact': 'Contact Us',
            'footer.careers': 'Careers',
            'footer.privacy': 'Privacy Policy',
            'footer.terms': 'Terms of Service',
            'login.title': 'Login - TingSha Website',
            'login.heading': 'Welcome Back',
            'login.subtitle': 'Sign in to continue to your account',
            'login.button': 'Sign In',
            'login.noAccount': "Don't have an account?",
            'login.registerNow': 'Sign up now',
            'register.title': 'Register - TingSha Website',
            'register.heading': 'Create Account',
            'register.subtitle': 'Start your free trial journey',
            'register.button': 'Create Account',
            'register.hasAccount': 'Already have an account?',
            'register.loginNow': 'Sign in now',
            'form.email': 'Email Address',
            'form.emailPlaceholder': 'name@example.com',
            'form.password': 'Password',
            'form.passwordPlaceholder': '••••••••',
            'form.confirmPassword': 'Confirm Password',
            'form.confirmPasswordPlaceholder': '••••••••',
            'form.firstName': 'First Name',
            'form.firstNamePlaceholder': 'John',
            'form.lastName': 'Last Name',
            'form.lastNamePlaceholder': 'Doe',
            'form.remember': 'Remember me',
            'form.forgotPassword': 'Forgot password?',
            'form.passwordStrength': 'Password Strength',
            'form.agreeTerms': 'I agree to the',
            'form.termsOfService': 'Terms of Service',
            'form.and': 'and',
            'form.privacyPolicy': 'Privacy Policy',
            'auth.orContinueWith': 'Or continue with',
            'dashboard.title': 'Dashboard - TingSha Website',
            'dashboard.welcome': 'Welcome back',
            'dashboard.overview': 'Overview',
            'dashboard.analytics': 'Analytics',
            'dashboard.projects': 'Projects',
            'dashboard.messages': 'Messages',
            'settings.title': 'Settings - TingSha Website',
            'settings.account': 'Account Settings',
            'settings.security': 'Security',
            'settings.notifications': 'Notifications',
            'settings.language': 'Language',
            'settings.theme': 'Theme',
            'btn.save': 'Save',
            'btn.cancel': 'Cancel',
            'btn.edit': 'Edit',
            'btn.delete': 'Delete',
            'btn.create': 'Create',
            'btn.upload': 'Upload',
            'btn.download': 'Download',
            'msg.success': 'Operation successful',
            'msg.error': 'Operation failed',
            'msg.loading': 'Loading...',
            'msg.confirmDelete': 'Are you sure you want to delete?',
            'msg.sessionExpired': 'Session expired, please login again',
        },
        'ja': {
            'site.name': 'TingSha ウェブサイト',
            'site.title': 'TingSha ウェブサイト - ホーム',
            'nav.home': 'ホーム',
            'nav.features': '機能',
            'nav.pricing': '料金',
            'nav.about': '概要',
            'nav.login': 'ログイン',
            'nav.register': '登録',
            'hero.title': '複雑をシンプルに',
            'hero.subtitle': 'TingShaはワンストップソリューションを提供し、ビジネス管理と成長をサポートします',
            'hero.ctaPrimary': '無料で始める',
            'hero.ctaSecondary': '詳細を見る',
            'login.title': 'ログイン - TingSha',
            'login.heading': 'おかえりなさい',
            'login.subtitle': 'アカウントにログインして続ける',
            'login.button': 'ログイン',
            'register.title': '登録 - TingSha',
            'register.heading': 'アカウント作成',
            'register.button': 'アカウント作成',
            'form.email': 'メールアドレス',
            'form.password': 'パスワード',
            'form.remember': 'ログイン状態を保存',
        },
        'ko': {
            'site.name': 'TingSha 웹사이트',
            'site.title': 'TingSha 웹사이트 - 홈',
            'nav.home': '홈',
            'nav.features': '기능',
            'nav.pricing': '가격',
            'nav.about': '소개',
            'nav.login': '로그인',
            'nav.register': '가입',
            'hero.title': '복잡함을 단순하게',
            'hero.subtitle': 'TingSha는 비즈니스 관리와 성장을 위한 원스톱 솔루션을 제공합니다',
            'hero.ctaPrimary': '무료로 시작',
            'hero.ctaSecondary': '자세히 알아보기',
            'login.title': '로그인 - TingSha',
            'login.heading': '환영합니다',
            'login.subtitle': '계속하려면 계정에 로그인하세요',
            'login.button': '로그인',
            'register.title': '가입 - TingSha',
            'register.heading': '계정 만들기',
            'register.button': '계정 만들기',
            'form.email': '이메일 주소',
            'form.password': '비밀번호',
            'form.remember': '로그인 상태 유지',
        }
    },
    
    // 获取翻译
    t(key) {
        const langData = this.translations[this.currentLang];
        return langData && langData[key] ? langData[key] : key;
    },
    
    // 切换语言
    setLanguage(lang) {
        if (this.translations[lang]) {
            this.currentLang = lang;
            localStorage.setItem('language', lang);
            this.updatePage();
            this.updateLangSelector();
        }
    },
    
    // 更新页面文本
    updatePage() {
        // 更新带 data-i18n 属性的元素
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            const translation = this.t(key);
            if (translation !== key) {
                if (el.tagName === 'TITLE') {
                    document.title = translation;
                } else if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                    el.placeholder = translation;
                } else {
                    el.textContent = translation;
                }
            }
        });
        
        // 更新 placeholder
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            const translation = this.t(key);
            if (translation !== key) {
                el.placeholder = translation;
            }
        });
        
        // 更新 HTML lang 属性
        document.documentElement.lang = this.currentLang;
    },
    
    // 更新语言选择器显示
    updateLangSelector() {
        const langNames = {
            'zh-CN': '中文',
            'en': 'English',
            'ja': '日本語',
            'ko': '한국어'
        };
        
        document.querySelectorAll('.lang-btn span').forEach(el => {
            el.textContent = langNames[this.currentLang] || this.currentLang;
        });
    },
    
    // 初始化
    init() {
        this.updatePage();
        this.updateLangSelector();
        
        // 绑定语言切换事件
        document.querySelectorAll('.lang-dropdown a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const lang = link.getAttribute('data-lang');
                this.setLanguage(lang);
            });
        });
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    i18n.init();
});
