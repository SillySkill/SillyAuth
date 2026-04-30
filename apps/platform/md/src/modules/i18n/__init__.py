"""
i18n - 国际化模块

提供多语言支持，包括：
- 语言检测中间件
- 翻译服务
- API 路由
"""

import logging
from typing import List

from .services import I18nService

logger = logging.getLogger(__name__)

# 支持的语言列表
SUPPORTED_LANGUAGES = ['zh', 'en', 'ja', 'ko', 'de', 'ru']

# 语言名称映射
LANGUAGE_NAMES = {
    'zh': '中文',
    'en': 'English',
    'ja': '日本語',
    'ko': '한국어',
    'de': 'Deutsch',
    'ru': 'Русский',
}


class SillyMDModule:
    """i18n 模块定义"""

    module_id = "i18n"
    name = "Internationalization"
    version = "1.0.0"

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.service = None

    def install(self, app, plugin_manager=None):
        """安装模块到 FastAPI 应用"""
        from .routes import router

        # 初始化服务
        self.service = I18nService(self.config)

        # 注册路由
        app.include_router(router, prefix="/api/i18n", tags=["i18n"])

        logger.info("i18n module installed")

    def get_service(self) -> I18nService:
        """获取 i18n 服务实例"""
        return self.service

    @property
    def info(self) -> dict:
        return {
            "id": self.module_id,
            "name": self.name,
            "version": self.version,
            "supported_languages": SUPPORTED_LANGUAGES,
        }


# 导出模块类
__all__ = ["SillyMDModule", "I18nService", "SUPPORTED_LANGUAGES", "LANGUAGE_NAMES"]
