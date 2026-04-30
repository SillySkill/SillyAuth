"""
统一配置加载模块
从 .env 文件加载所有配置
"""
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


def load_env():
    """加载 .env 文件"""
    if ENV_FILE.exists():
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()


# 初始化时加载环境变量
load_env()


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str
    port: int
    database: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        return cls(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'sillymd'),
            user=os.getenv('DB_USER', 'sillyAdmin'),
            password=os.getenv('DB_PASSWORD', '')
        )


@dataclass
class TOSConfig:
    """TOS 对象存储配置"""
    endpoint: str
    bucket: str
    access_key: str
    secret_key: str
    custom_domain: Optional[str] = None
    default_prefix: str = "webs"

    @classmethod
    def from_env(cls) -> 'TOSConfig':
        return cls(
            endpoint=os.getenv('TOS_ENDPOINT', 'tos-cn-shanghai.volces.com'),
            bucket=os.getenv('TOS_BUCKET', 'sillymd'),
            access_key=os.getenv('TOS_ACCESS_KEY', ''),
            secret_key=os.getenv('TOS_SECRET_KEY', ''),
            custom_domain=os.getenv('TOS_CUSTOM_DOMAIN'),
            default_prefix=os.getenv('TOS_DEFAULT_PREFIX', 'webs')
        )


@dataclass
class JWTConfig:
    """JWT 配置"""
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    @classmethod
    def from_env(cls) -> 'JWTConfig':
        return cls(
            secret_key=os.getenv('JWT_SECRET', 'change-this-in-production'),
            algorithm=os.getenv('JWT_ALGORITHM', 'HS256'),
            access_token_expire_minutes=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '43200'))
        )


@dataclass
class ServerConfig:
    """服务器配置"""
    host: str
    port: int

    @classmethod
    def from_env(cls) -> 'ServerConfig':
        return cls(
            host=os.getenv('SERVER_HOST', '0.0.0.0'),
            port=int(os.getenv('SERVER_PORT', '8000'))
        )


# 导出便捷方法
def get_db_config() -> DatabaseConfig:
    """获取数据库配置"""
    return DatabaseConfig.from_env()


def get_tos_config() -> TOSConfig:
    """获取 TOS 配置"""
    return TOSConfig.from_env()


def get_jwt_config() -> JWTConfig:
    """获取 JWT 配置"""
    return JWTConfig.from_env()


def get_server_config() -> ServerConfig:
    """获取服务器配置"""
    return ServerConfig.from_env()
