"""
i18n 翻译服务

提供多语言翻译和语言检测功能
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class I18nService:
    """国际化服务"""

    SUPPORTED_LANGUAGES = ['zh', 'en', 'ja', 'ko', 'de', 'ru']

    LANGUAGE_NAMES = {
        'zh': '中文',
        'en': 'English',
        'ja': '日本語',
        'ko': '한국어',
        'de': 'Deutsch',
        'ru': 'Русский',
    }

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.locales: Dict[str, dict] = {}
        self._load_locales()

    def _load_locales(self):
        """加载所有语言文件"""
        # 获取当前模块路径
        module_dir = Path(__file__).parent
        locale_dir = module_dir / "locales"

        if not locale_dir.exists():
            logger.warning(f"Locale directory not found: {locale_dir}")
            return

        # 加载每个语言文件
        for lang_code in self.SUPPORTED_LANGUAGES:
            locale_file = locale_dir / f"{lang_code}.json"
            if locale_file.exists():
                try:
                    with open(locale_file, 'r', encoding='utf-8') as f:
                        self.locales[lang_code] = json.load(f)
                    logger.info(f"Loaded locale: {lang_code}")
                except Exception as e:
                    logger.error(f"Failed to load locale {lang_code}: {e}")
            else:
                logger.warning(f"Locale file not found: {locale_file}")

    def get_translations(self, lang: str) -> dict:
        """获取指定语言的翻译"""
        return self.locales.get(lang, self.locales.get('en', {}))

    def t(self, lang: str, key: str, default: str = None) -> str:
        """
        翻译单个键

        Args:
            lang: 语言代码 (zh, en, ja, ko, de, ru)
            key: 翻译键，使用点分隔 (e.g., "skills.title")
            default: 默认值

        Returns:
            翻译后的文本
        """
        translations = self.get_translations(lang)

        # 从嵌套字典中获取翻译
        keys = key.split('.')
        value = translations
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default or key

        return value if isinstance(value, str) else (default or key)

    def translate(self, lang: str, keys: List[str]) -> Dict[str, str]:
        """
        批量翻译多个键

        Args:
            lang: 语言代码
            keys: 翻译键列表

        Returns:
            键值对字典
        """
        result = {}
        for key in keys:
            result[key] = self.t(lang, key)
        return result

    def get_all_translations(self, lang: str) -> dict:
        """
        获取指定语言的所有翻译

        Args:
            lang: 语言代码

        Returns:
            完整的翻译字典
        """
        return self.get_translations(lang)

    def detect_language(
        self,
        query_param: str = None,
        cookie: str = None,
        accept_language: str = None,
        browser_lang: str = None
    ) -> str:
        """
        检测最佳语言

        Args:
            query_param: URL 参数 ?lang=zh
            cookie: Cookie 中的 locale
            accept_language: Accept-Language 请求头
            browser_lang: 浏览器语言

        Returns:
            检测到的语言代码
        """
        # 1. URL 参数优先级最高
        if query_param and query_param in self.SUPPORTED_LANGUAGES:
            return query_param

        # 2. Cookie
        if cookie and cookie in self.SUPPORTED_LANGUAGES:
            return cookie

        # 3. Accept-Language 头
        if accept_language:
            detected = self._parse_accept_language(accept_language)
            if detected:
                return detected

        # 4. 浏览器语言
        if browser_lang:
            detected = self._parse_accept_language(browser_lang)
            if detected:
                return detected

        # 5. 默认语言
        return 'en'

    def _parse_accept_language(self, accept_language: str) -> Optional[str]:
        """
        解析 Accept-Language 头

        例如: "en-US,en;q=0.9,zh-CN;q=0.8"
        """
        if not accept_language:
            return None

        # 解析语言优先级
        languages = []
        for part in accept_language.split(','):
            part = part.strip()
            if ';' in part:
                lang, q = part.split(';')
                lang = lang.strip()
                try:
                    q = float(q.split('=')[1])
                except:
                    q = 1.0
            else:
                lang = part
                q = 1.0
            languages.append((lang, q))

        # 按优先级排序
        languages.sort(key=lambda x: x[1], reverse=True)

        # 匹配支持的语言
        for lang, _ in languages:
            # 处理如 "zh-CN" -> "zh"
            base_lang = lang.split('-')[0].lower()
            if base_lang in self.SUPPORTED_LANGUAGES:
                return base_lang

        return None

    def is_supported(self, lang: str) -> bool:
        """检查语言是否支持"""
        return lang in self.SUPPORTED_LANGUAGES

    def get_supported_languages(self) -> List[dict]:
        """获取所有支持的语言列表"""
        return [
            {"code": code, "name": self.LANGUAGE_NAMES.get(code, code)}
            for code in self.SUPPORTED_LANGUAGES
        ]
