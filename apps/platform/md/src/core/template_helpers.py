"""
Template Helpers - Shared Jinja2Templates instance and context utilities.
All modules import `templates` from here to render page templates.
"""
from fastapi.templating import Jinja2Templates
from fastapi import Request
from starlette.responses import HTMLResponse
from jinja2 import ChainableUndefined, Environment, FileSystemLoader, select_autoescape
import logging
import os
import json as _json

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DB-driven context loading helpers
# ---------------------------------------------------------------------------

def _load_config_data(category: str, name: str):
    """Load a single config_data entry from database. Returns parsed data or None."""
    try:
        from core.db_adapter import get_db_cursor
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT data FROM config_data WHERE category = %s AND name = %s",
                (category, name)
            )
            row = cur.fetchone()
            if row and row.get('data') is not None:
                raw = row['data']
                return _json.loads(raw) if isinstance(raw, str) else raw
    except Exception as e:
        logger.warning(f"Failed to load config_data {category}/{name}: {e}")
    return None


def _load_all_config(category: str):
    """Load all config_data entries for a category. Returns dict of {name: data}."""
    try:
        from core.db_adapter import get_db_cursor
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT name, data FROM config_data WHERE category = %s",
                (category,)
            )
            rows = cur.fetchall()
            result = {}
            for row in rows:
                raw = row['data']
                result[row['name']] = _json.loads(raw) if isinstance(raw, str) else raw
            return result
    except Exception as e:
        logger.warning(f"Failed to load config_data for category {category}: {e}")
    return {}


def _get_cached_state(request: Request, key: str, factory):
    """Get or compute a value, cached in request.state for the request duration."""
    cache = getattr(request.state, '_template_cache', None)
    if cache is None:
        cache = {}
        request.state._template_cache = cache
    if key not in cache:
        cache[key] = factory()
    return cache[key]


class SafeChainableUndefined(ChainableUndefined):
    """ChainableUndefined that also handles comparison and arithmetic operators safely.

    Standard ChainableUndefined raises UndefinedError for operators like:
      {% if total_pages > 1 %}   -- __gt__ not supported
      {% if items|length > 0 %}  -- __gt__ not supported
      {{ total_pages + 1 }}      -- __add__ not supported

    This class returns False for comparisons and self for arithmetic,
    allowing templates to render safely even when context data is missing.
    """
    def __lt__(self, other): return False
    def __le__(self, other): return False
    def __gt__(self, other): return False
    def __ge__(self, other): return False
    def __add__(self, other): return self
    def __radd__(self, other): return self
    def __sub__(self, other): return self
    def __rsub__(self, other): return self
    def __mul__(self, other): return self
    def __rmul__(self, other): return self
    def __iter__(self): return iter([])
    def __len__(self): return 0
    def __getitem__(self, key): return self
    def __truediv__(self, other): return self
    def __rtruediv__(self, other): return self
    def __floordiv__(self, other): return self
    def __rfloordiv__(self, other): return self
    def __mod__(self, other): return self
    def __rmod__(self, other): return self
    def __pow__(self, other): return self
    def __rpow__(self, other): return self
    def __neg__(self): return self
    def __pos__(self): return self
    def __abs__(self): return self
    def __int__(self): return 0
    def __float__(self): return 0.0


# ---------------------------------------------------------------------------
# I18n helper for Jinja2 templates
# ---------------------------------------------------------------------------

_TRANSLATIONS = {
    "site.name": "挺傻的网站",
    "site.tagline": "承认自己有时候挺傻的，这是智慧的开始",
    "home.title": "首页",
    "home.hero_title": "AI Skills 托管中心",
    "home.hero_subtitle": "发现、学习和分享 AI Skills",
    "skills.explore": "探索 Skills",
    "skills.title": "Skills 列表",
    "tutorials.title": "技术讲解",
    "tutorials.featured_badge": "精选 AI 工具教程",
    "tutorials.hero_title": "掌握 AI 编程工具",
    "tutorials.hero_subtitle": "学习 Claude Code、OpenClaw、Cursor 等最新 AI 工具的使用技巧",
    "tutorials.all": "全部教程",
    "tutorials.featured": "精选教程",
    "tutorials.featured_tutorial_title": "AI 编程入门",
    "tutorials.featured_tutorial_desc": "从零开始学习 AI 编程，掌握最新的 AI 开发工具",
    "tutorials.watch_now": "立即观看",
    "tutorials.latest": "最新教程",
    "tutorials.latest_subtitle": "持续更新的 AI 工具使用教程",
    "tutorials.filter_all": "全部",
    "tutorials.filter_installation": "安装",
    "tutorials.filter_usage": "使用",
    "tutorials.filter_tips": "技巧",
    "tutorials.filter_advanced": "进阶",
    "tutorials.no_tutorials": "暂无教程",
    "tutorials.load_more": "加载更多教程",
    "downloads.title": "资源下载",
    "downloads.mirror_badge": "国内高速镜像",
    "downloads.hero_title": "开发工具资源下载",
    "downloads.hero_subtitle": "WSL、Python、Git、VS Code 等开发工具，国内镜像高速下载",
    "downloads.stat_tools": "开发工具",
    "downloads.stat_files": "资源文件",
    "downloads.stat_downloads": "总下载量",
    "downloads.stat_uptime": "可用性",
    "downloads.all": "全部资源",
    "downloads.other_tools": "其他工具",
    "downloads.all_platforms": "全部平台",
    "downloads.popular": "热门资源",
    "downloads.popular_subtitle": "最常用的开发工具和框架",
    "downloads.search_placeholder": "搜索资源...",
    "downloads.version": "版本",
    "downloads.official": "官方",
    "downloads.direct_download": "直接下载",
    "downloads.download": "下载",
    "downloads.mirror": "镜像下载",
    "downloads.mirror_badge_text": "镜像",
    "downloads.github": "GitHub 仓库",
    "downloads.no_downloads": "暂无下载资源",
    "marketplace.title": "供应商市场",
    "marketplace.hero_title": "供应商市场",
    "marketplace.hero_subtitle": "成为 Skills 供应商，将你的专业知识和经验变现",
    "marketplace.apply_now": "立即申请成为供应商",
    "marketplace.tiers_title": "供应商等级体系",
    "marketplace.tiers_subtitle": "三级成长体系，收益逐级提升",
    "marketplace.tier_bronze": "普通供应商",
    "marketplace.tier_bronze_desc": "刚起步的创作者，可以发布和销售 Skills",
    "marketplace.tier_silver": "优质供应商",
    "marketplace.tier_silver_desc": "累计销售额 ≥ 1,000 AI Points",
    "marketplace.tier_gold": "金牌供应商",
    "marketplace.tier_gold_desc": "累计销售额 ≥ 10,000 AI Points，好评率 ≥ 95%",
    "marketplace.revenue": "收益",
    "marketplace.hot_vendors": "热门供应商",
    "marketplace.hot_vendors_desc": "认识我们优秀的创作者",
    "marketplace.vendor": "供应商",
    "marketplace.works": "作品",
    "marketplace.sales": "销量",
    "marketplace.rating": "评分",
    "marketplace.no_vendors": "暂无供应商",
    "marketplace.cta_title": "准备好开始了吗？",
    "marketplace.cta_subtitle": "无论你是开发者、设计师还是领域专家，都可以在这里分享你的技能",
    "marketplace.learn_more": "了解更多",
    "marketplace.total_vendors": "供应商总数",
    "marketplace.total_skills": "Skills 总数",
    "marketplace.total_sales": "总销售额",
    "auth.login": "登录",
    "auth.register": "注册",
    "auth.forgot_password": "忘记密码",
    "auth.reset_password": "重置密码",
    "dashboard.title": "控制台",
    "analytics.title": "数据分析",
    "messages.title": "消息中心",
    "points.mall": "积分商城",
    "tasks.title": "任务中心",
    "vendor.apply": "供应商申请",
    "store.title": "商店",
    "user.center": "用户中心",
    "user.settings": "设置",
    "user.projects": "我的项目",
    "user.creation": "创作中心",
    "user.messages": "我的消息",
    "nav.home": "首页",
    "nav.skills": "探索 Skills",
    "nav.tutorials": "教程",
    "nav.downloads": "下载",
    "nav.marketplace": "供应商市场",
    "nav.store": "商店",

    # Skills translations
    "skills.reset": "重置",
    "skills.sort_default": "默认排序",
    "skills.sort_newest": "最新发布",
    "skills.sort_downloads": "下载最多",
    "skills.sort_price_asc": "价格从低到高",
    "skills.sort_price_desc": "价格从高到低",

    # Home
    "home.create_team": "创建团队",
    "home.hero_features": "核心功能",
    "home.feature_skills": "Skills 市场",
    "home.feature_skills_desc": "发现和使用各种 AI Skills",
    "home.feature_tutorials": "视频教程",
    "home.feature_tutorials_desc": "从入门到精通的完整教程体系",
    "home.feature_downloads": "资源下载",
    "home.feature_downloads_desc": "开发工具国内镜像高速下载",
    "home.feature_marketplace": "供应商市场",
    "home.feature_marketplace_desc": "成为供应商，变现你的技能",
    "home.feature_store": "商品商店",
    "home.feature_store_desc": "购买 SillyFu 等实体商品",
    "home.start_now": "立即开始",
    "home.learn_more": "了解更多",
    "home.featured_skills": "精选 Skills",
    "home.featured_skills_desc": "发现热门 AI Skills",
    "home.top_vendors": "热门供应商",
    "home.top_vendors_desc": "认识优质供应商",
    "home.marketplace_cta": "供应商市场",
    "home.marketplace_cta_desc": "成为供应商，发布你的 Skills",
    "home.stats_users": "注册用户",
    "home.stats_skills": "Skills 总数",
    "home.stats_downloads": "总下载量",
    "home.stats_vendors": "入驻供应商",
    "home.stats_satisfaction": "用户满意度",

    # OpenClaw
    "openclaw.hero_title": "OpenClaw - 开源 AI Skills 平台",
    "openclaw.hero_desc": "开源、可扩展的 AI Skills 生态系统",
    "features.title": "平台功能特性",
    "features.hero_title": "SillyMD 平台功能特性",
    "features.hero_desc": "全方位 AI Skills 管理与交易平台",
    "store.hero_title": "SillyMD 商店",
    "store.hero_desc": "精选 SillyFu 实体商品和数字产品",

    # Footer
    "footer.product": "产品",
    "footer.developer": "开发者",
    "footer.support": "支持",
    "footer.about": "关于",
    "footer.features": "功能特性",
    "footer.sillyfu": "SillyFu",
    "footer.openclaw": "OpenClaw",
    "footer.docs": "文档",
    "footer.api": "API",
    "footer.sdk": "SDK",
    "footer.help": "帮助中心",
    "footer.contact": "联系我们",
    "footer.rights": "All rights reserved.",

    # Messages
    "messages.no_messages": "暂无消息",
    "messages.type_message": "输入消息...",
    "points.no_items": "暂无积分商品",
    "tasks.no_tasks": "暂无任务",
    "tasks.daily_checkin": "每日签到",
    "dashboard.welcome": "欢迎回来",
    "dashboard.overview": "总览",
    "analytics.page_title": "数据分析",
    "analytics.page_desc": "查看平台数据趋势和用户行为分析",

    # Form keys
    "form.email": "邮箱",
    "form.password": "密码",
    "form.passwordPlaceholder": "请输入密码",
    "form.firstName": "名",
    "form.firstNamePlaceholder": "请输入名",
    "form.lastName": "姓",
    "form.lastNamePlaceholder": "请输入姓",
    "form.username": "用户名",
    "form.usernamePlaceholder": "请输入用户名",
    "form.passwordStrength": "密码强度",
    "form.confirmPassword": "确认密码",
    "form.agreeTerms": "同意",
    "form.termsOfService": "服务条款",
    "form.and": "和",
    "form.privacyPolicy": "隐私政策",
    "form.passwordsDoNotMatch": "两次输入的密码不一致",
    "form.remember": "记住密码",
    "form.forgotPassword": "忘记密码？",

    # Login keys
    "login.title": "登录",
    "login.passwordTab": "密码登录",
    "login.qrcodeTab": "扫码登录",
    "login.submit": "登录",
    "login.qrGenerating": "正在生成二维码...",
    "login.qrWaiting": "等待扫码...",
    "login.qrHint": "请使用手机客户端扫码登录",
    "login.qrRefresh": "刷新二维码",
    "login.noAccount": "还没有账号？",
    "login.registerNow": "立即注册",
    "login.qrError": "二维码加载失败",
    "login.networkError": "网络错误",
    "login.qrScanned": "已扫码，请在手机上确认",
    "login.qrConfirmed": "登录确认成功",
    "login.qrExpired": "二维码已过期",
    "login.qrCancelled": "扫码登录已取消",

    # Register keys
    "register.title": "注册",
    "register.heading": "创建账号",
    "register.subtitle": "注册以开始使用 SillyMD",
    "register.button": "注册",
    "register.hasAccount": "已有账号？",
    "register.loginNow": "立即登录",

    # Forgot Password keys
    "forgotPassword.title": "忘记密码",
    "forgotPassword.heading": "重置密码",
    "forgotPassword.instruction": "输入注册邮箱，我们将发送重置链接",
    "forgotPassword.submit": "发送重置链接",
    "forgotPassword.backToLogin": "返回登录",

    # Reset Password keys
    "resetPassword.title": "重置密码",
    "resetPassword.heading": "设置新密码",
    "resetPassword.instruction": "请设置新密码",
    "resetPassword.newPassword": "新密码",
    "resetPassword.confirmPassword": "确认新密码",
    "resetPassword.submit": "重置密码",
    "resetPassword.backToLogin": "返回登录",

    # Auth misc
    "auth.orContinueWith": "或使用以下方式继续",

    # Additional downloads keys
    "downloads.meta_description": "WSL、Python、Git、VS Code 等开发工具国内镜像下载",
    "downloads.meta_keywords": "WSL下载, Python下载, Git下载, 开发工具",
    "downloads.hero_badge": "国内高速镜像",
    "downloads.popular_title": "热门资源",
    "downloads.no_results": "未找到匹配的资源",

    # Additional marketplace keys
    "marketplace.vendors_title": "热门供应商",
    "marketplace.vendors_subtitle": "认识我们优秀的创作者",
    "marketplace.search_placeholder": "搜索供应商...",
    "marketplace.sort_popular": "最受欢迎",
    "marketplace.sort_newest": "最新加入",
    "marketplace.sort_rating": "评分最高",
    "marketplace.sort_skills": "作品最多",
    "marketplace.no_results": "未找到匹配的供应商",
    "marketplace.cta_apply": "立即申请",
    "marketplace.cta_learn": "了解更多",

    # Additional tutorials keys
    "tutorials.meta_description": "AI 工具安装使用教程",
    "tutorials.meta_keywords": "Claude Code, OpenClaw, Cursor, AI 工具",
    "tutorials.hero_badge": "精选 AI 工具教程",
    "tutorials.latest_title": "最新教程",
    "tutorials.no_results": "未找到匹配的教程",

    # Additional skills keys (list + detail)
    "skills.subtitle": "发现、学习和分享 AI Skills",
    "skills.search_placeholder": "搜索 Skills...",
    "skills.hot_searches": "热门搜索",
    "skills.filters": "分类筛选",
    "skills.sort": "排序方式",
    "skills.no_results": "未找到匹配的 Skills",
    "skills.downloads": "下载",
    "skills.version": "版本",
    "skills.updated_on": "更新于",
    "skills.tab_overview": "概览",
    "skills.tab_docs": "文档",
    "skills.tab_reviews": "评价",
    "skills.tab_changelog": "更新日志",
    "skills.features": "功能特性",
    "skills.quickstart": "快速开始",
    "skills.vendor_info": "供应商信息",
    "skills.skills": "作品",
    "skills.sales": "销量",
    "skills.rating": "评分",
    "skills.docs_title": "文档",
    "skills.docs_unavailable": "暂无文档",
    "skills.reviews_title": "用户评价",
    "skills.no_reviews": "暂无评价",
    "skills.changelog_title": "更新日志",
    "skills.no_changelog": "暂无更新日志",
    "skills.one_time_purchase": "一次性购买",
    "skills.buy_now": "立即购买",
    "skills.download": "下载",
    "skills.favorite": "收藏",
    "skills.tags": "标签",
    "skills.free": "免费",
    "skills.total_count": "共找到 {count} 个 Skills",

    # Additional home keys
    "home.free_skills_title": "免费 Skills",
    "home.free_skills_subtitle": "免费实用的 AI Skills",
    "home.commercial_skills_title": "商业 Skills",
    "home.commercial_skills_subtitle": "精选付费 Skills",
    "home.vendors_title": "热门供应商",
    "home.vendors_subtitle": "优秀的 Skills 创作者",
    "home.skills": "个 Skills",
    "home.downloads": "次下载",
    "home.rating": "评分",
    "home.team_title": "团队协作",
    "home.team_subtitle": "与团队一起创造更好的 AI Skills",
    "home.team_domain_title": "专属域名",
    "home.team_domain_desc": "为你的团队提供专属域名",
    "home.team_domain_detail": "支持自定义域名",
    "home.team_domain_example": "your-team.example.com",
    "home.view_all": "查看全部",
    "home.stats_skills_assets": "Skills 资产",
    "home.stats_vendors_certified": "认证供应商",
    "home.stats_enterprise_teams": "企业团队",
    "home.stats_ai_accuracy": "AI 审核准确率",

    # Navbar keys
    "nav.teams": "团队协作",
    "nav.docs": "文档",
    "theme.select": "主题",
    "theme.tech_blue": "科技蓝",
    "theme.ocean": "海洋",
    "theme.forest": "森林",
    "theme.sunset": "日落",
    "theme.purple": "紫韵",
    "theme.cyberpunk": "赛博",

    # Footer keys
    "footer.platform": "平台",
    "footer.pricing": "定价",
    "footer.dev_docs": "开发文档",
    "footer.api_ref": "API 参考",
    "footer.community": "社区论坛",
    "footer.help_center": "帮助中心",
    "footer.privacy": "隐私政策",
    "footer.terms": "服务条款",
    "footer.about_us": "关于我们",
}


def _translate(key: str, default: str = None, **kwargs) -> str:
    """Simple i18n translation function for Jinja2 templates.
    Accepts optional default value and kwargs (like count) for Jinja2 i18n compatibility.
    """
    val = _TRANSLATIONS.get(key)
    if val is not None:
        if kwargs:
            try:
                return val.format(**kwargs)
            except KeyError:
                pass
        return val
    if default is not None:
        return default
    return key


# ---------------------------------------------------------------------------
# Jinja2 Templates instance with i18n support
# ---------------------------------------------------------------------------

_templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
_jinja_env = Environment(
    loader=FileSystemLoader(_templates_dir),
    autoescape=select_autoescape(),
    undefined=SafeChainableUndefined,
)
templates = Jinja2Templates(env=_jinja_env)
templates.env.globals["_"] = _translate
logger.info(f"Jinja2Templates initialized at {_templates_dir} with i18n support")


def get_template_context(request: Request, extra_context: dict = None) -> dict:
    """
    Build standard template context with user, theme, lang info.
    Called by every page route handler.
    All data loaded from config_data table (DB-driven, no hardcoded values).
    """
    user = getattr(request.state, "user", None)
    theme = getattr(request.state, "theme", "tech-blue")
    lang = getattr(request.state, "lang", "zh-CN")

    lang_names = {
        "zh-CN": "中文", "zh": "中文",
        "en": "English",
        "ja": "日本語",
        "ko": "한국어",
    }
    lang_short = lang[:2]  # "zh" from "zh-CN"

    # Load system settings from config_data (cached per request)
    sys_settings = _get_cached_state(request, 'system_settings',
        lambda: _load_config_data("system", "settings") or {})

    # Load navbar items from config_data
    nav_items = _get_cached_state(request, 'nav_items',
        lambda: _load_config_data("navigation", "navbar") or [])

    # Load footer sections from config_data (platform, developer, about)
    footer_sections_def = [
        ("平台", "footer.platform", "footer_platform"),
        ("开发者", "footer.developer", "footer_developer"),
        ("关于", "footer.about", "footer_about"),
    ]
    footer_sections_raw = _get_cached_state(request, 'footer_sections_raw',
        lambda: _load_all_config("navigation"))
    footer_sections = []
    for title, i18n_key, name in footer_sections_def:
        items = footer_sections_raw.get(name, [])
        footer_sections.append({"title": title, "title_i18n": i18n_key, "items": items})

    # Load social links from config_data
    social_links = _get_cached_state(request, 'social_links',
        lambda: _load_config_data("footer", "social_links") or [])

    context = {
        "request": request,
        "user": user,
        "theme": theme,
        "lang": lang,
        "lang_short": lang_short,
        "lang_name": lang_names.get(lang, lang_names.get(lang_short, "中文")),
        "current_path": request.url.path,
        "site_name": sys_settings.get("site_name", "挺傻的网站"),
        "tagline": sys_settings.get("tagline", ""),
        "copyright_text": sys_settings.get("copyright", "2026 SillyMD. All rights reserved."),
        "icp": sys_settings.get("icp", ""),
        "psb": sys_settings.get("psb", ""),
        "nav_items": nav_items,
        "footer_sections": footer_sections,
        "social_links": social_links,
        "page_heroes": {},
        "current_year": 2026,
    }
    if extra_context:
        context.update(extra_context)
    return context


def render_template(request: Request, template_name: str, extra_context: dict = None) -> HTMLResponse:
    """
    Render a Jinja2 template with standard context.
    """
    try:
        context = get_template_context(request, extra_context)
        return templates.TemplateResponse(request, template_name, context)
    except Exception as e:
        import traceback
        logger.error(f"Template rendering error for {template_name}: {e}")
        logger.error(traceback.format_exc())
        raise
