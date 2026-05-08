"""
Skill2 自动审核与打包模块
敏感内容扫描、AES-256-GCM 加密、平台签名、.skill2 打包
"""

import logging
from pathlib import Path
from typing import Optional

import yaml

from core.module import ModuleInfo

logger = logging.getLogger(__name__)


class SillyMDModule:
    """Skill2 module for automatic skill review and packaging."""

    module_id: str = "skill2"
    info = ModuleInfo(
        id="skill2",
        name="Skill2 自动审核与打包模块",
        version="1.0.0",
        description="Skill2 安全标准 — 敏感内容扫描、AES-256-GCM 加密、平台签名、.skill2 打包",
        dependencies=["skills", "storage"],
    )

    def __init__(self, config_path: Optional[str] = None):
        self.config: Optional[dict] = None
        self.app = None
        self.state = None
        self._service = None
        self._load_config(config_path)

    def _load_config(self, config_path: Optional[str] = None) -> None:
        """Load config.yaml from module directory."""
        if config_path is None:
            config_path = str(Path(__file__).parent / "config.yaml")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
            self.config = {}

    def register(self, app) -> None:
        """Register module routes with the FastAPI app."""
        self.app = app
        from .routes import router as skill2_router
        app.include_router(skill2_router)
        logger.info("Skill2 module routes registered")

    def install(self, app) -> None:
        """Alias for register() — for PluginManager compatibility."""
        self.register(app)

    def on_startup(self) -> None:
        """Initialize module: ensure DB tables and generate platform key."""
        from .services import Skill2Service
        self._service = Skill2Service()

        # Ensure database tables exist
        self._service.ensure_tables()

        # Generate initial platform key pair if none exists
        if not self._service.get_active_key():
            logger.info("No active platform key found. Generating RSA-2048 key pair...")
            key = self._service.generate_key_pair()
            if key:
                logger.info(f"Platform key generated: version {key['key_version']}")
            else:
                logger.warning("Failed to generate platform key")
        else:
            logger.info("Platform key exists")

        logger.info("Skill2 module startup complete")

    def on_shutdown(self) -> None:
        """Cleanup on shutdown."""
        logger.info("Skill2 module shutting down")
