"""
API路由模块
"""
from .config import config_bp
from .generate import generate_bp
from .upload import upload_bp
from .invite import invite_bp
from .payment import payment_bp

# 后台管理API
from .admin_auth import auth_bp
from .admin_apps import apps_bp
from .admin_modules import modules_bp
from .admin_assets import assets_bp
from .admin_devices import devices_bp
from .admin_push import push_bp
from .admin_users import users_bp
from .admin_logs import logs_bp
from .admin_stats import stats_bp
from .admin_application_config import router as application_config_bp

__all__ = [
    'config_bp', 'generate_bp', 'upload_bp', 'invite_bp', 'payment_bp',
    'auth_bp', 'apps_bp', 'modules_bp', 'assets_bp', 'devices_bp', 'push_bp',
    'users_bp', 'logs_bp', 'stats_bp', 'application_config_bp'
]
