# ============================================
# SillyMD Backend - Configuration
# ============================================

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""

    # Basic
    PROJECT_NAME: str = "SillyMD Backend"
    DESCRIPTION: str = "AI Skills Hosting & Collaboration Platform"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sillymd"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CLUSTER_MODE: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://sillymd.com",
        "https://sillymd.com"
    ]

    # AI/ML
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_REVIEW_MODEL: str = "gpt-4o-mini"
    AI_MAX_TOKENS: int = 2000
    AI_TEMPERATURE: float = 0.3

    # Search
    MEILISEARCH_URL: str = "http://localhost:7700"
    MEILISEARCH_MASTER_KEY: str = "masterKey"

    # OSS (Aliyun)
    OSS_ACCESS_KEY_ID: Optional[str] = None
    OSS_ACCESS_KEY_SECRET: Optional[str] = None
    OSS_BUCKET_NAME: Optional[str] = None
    OSS_ENDPOINT: Optional[str] = None

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_SKILLS: str = "skills-events"
    KAFKA_TOPIC_REVIEWS: str = "reviews-events"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Crawler
    CRAWLER_ENABLED: bool = True
    CRAWLER_MAX_DAILY_IMPORTS: int = 50
    CRAWLER_IMPORT_INTERVAL: int = 600  # seconds
    CRAWLER_SOURCES: List[str] = ["github", "gitee", "npm", "pypi"]

    # Review System
    REVIEW_DIFFICULTY: str = "medium"  # easy, medium, hard
    REVIEW_AUTO_PUBLISH: bool = True
    REVIEW_AUTO_PUBLISH_MIN_STARS: int = 3

    # Transaction
    PLATFORM_FEE_RATE: float = 0.15  # 15%
    MIN_WITHDRAWAL: int = 500  # Points
    POINTS_EXCHANGE_RATE: int = 10  # 100 Points = 10 CNY

    # Tracing
    ENABLE_TRACING: bool = False
    JAEGER_HOST: str = "localhost"
    JAEGER_PORT: int = 6831

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [
        ".md", ".txt", ".json", ".yaml", ".yml",
        ".png", ".jpg", ".jpeg", ".gif"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Create settings instance
settings = Settings()


# Log configuration on startup
import logging
logger = logging.getLogger(__name__)
logger.info(f"Configuration loaded for environment: {settings.ENVIRONMENT}")
