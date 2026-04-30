"""
后台管理系统 - SQLAlchemy ORM模型定义
"""

from sqlalchemy import Column, BigInteger, String, Text, Boolean, Integer, SmallInteger, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class AdminUser(Base):
    """管理员表"""
    __tablename__ = 'admin_users'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment='管理员用户名')
    password_hash = Column(String(255), nullable=False, comment='密码哈希')
    real_name = Column(String(100), comment='真实姓名')
    email = Column(String(100), comment='邮箱')
    phone = Column(String(20), comment='手机号')
    role = Column(SmallInteger, default=1, comment='角色: 1=超级管理员, 2=应用管理员')
    status = Column(SmallInteger, default=1, comment='状态: 1=启用, 0=禁用')
    last_login_at = Column(DateTime, comment='最后登录时间')
    last_login_ip = Column(String(50), comment='最后登录IP')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    created_apps = relationship("App", foreign_keys="App.created_by", back_populates="creator")


class App(Base):
    """应用表"""
    __tablename__ = 'apps'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    app_key = Column(String(64), unique=True, nullable=False, comment='应用唯一标识')
    app_name = Column(String(100), nullable=False, comment='应用名称')
    app_name_en = Column(String(100), comment='应用英文名')
    app_description = Column(Text, comment='应用描述')
    app_icon = Column(String(500), comment='应用图标URL')
    package_name = Column(String(100), comment='Android包名')
    version = Column(String(20), default='1.0.0', comment='当前版本')
    status = Column(SmallInteger, default=1, comment='状态: 1=启用, 0=禁用')
    created_by = Column(BigInteger, ForeignKey('admin_users.id', ondelete='SET NULL'), comment='创建人ID')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    creator = relationship("AdminUser", foreign_keys=[created_by], back_populates="created_apps")
    modules = relationship("AppModule", back_populates="app", cascade="all, delete-orphan")
    assets = relationship("AppAsset", back_populates="app", cascade="all, delete-orphan")
    devices = relationship("AppDevice", back_populates="app", cascade="all, delete-orphan")
    push_tasks = relationship("ConfigPushTask", back_populates="app", cascade="all, delete-orphan")


class AppModule(Base):
    """应用模块表"""
    __tablename__ = 'app_modules'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    app_id = Column(BigInteger, ForeignKey('apps.id', ondelete='CASCADE'), nullable=False, comment='应用ID')
    module_key = Column(String(50), nullable=False, comment='模块标识(ai_show/quiz/lottery/inner)')
    module_name = Column(String(100), nullable=False, comment='模块名称')
    enabled = Column(Boolean, default=True, comment='是否启用')
    config = Column(JSON, comment='模块配置(JSON格式)')
    sort_order = Column(Integer, default=0, comment='排序')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    app = relationship("App", back_populates="modules")


class AppAsset(Base):
    """素材资源表"""
    __tablename__ = 'app_assets'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    app_id = Column(BigInteger, ForeignKey('apps.id', ondelete='CASCADE'), nullable=False, comment='应用ID')
    module_key = Column(String(50), comment='模块标识')
    asset_type = Column(String(20), nullable=False, comment='素材类型: image/video/audio/config/banner')
    asset_key = Column(String(100), nullable=False, comment='素材唯一标识')
    asset_name = Column(String(200), comment='素材名称')
    file_path = Column(String(500), nullable=False, comment='文件路径(OSS相对路径)')
    file_url = Column(String(500), comment='完整URL')
    file_size = Column(BigInteger, comment='文件大小(字节)')
    file_hash = Column(String(64), comment='文件哈希(MD5)')
    mime_type = Column(String(100), comment='MIME类型')
    metadata = Column(JSON, comment='元数据(宽/高/时长等)')
    status = Column(SmallInteger, default=1, comment='状态: 1=启用, 0=禁用')
    uploaded_by = Column(BigInteger, ForeignKey('admin_users.id', ondelete='SET NULL'), comment='上传人ID')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    app = relationship("App", back_populates="assets")


class AppDevice(Base):
    """设备管理表"""
    __tablename__ = 'app_devices'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    app_id = Column(BigInteger, ForeignKey('apps.id', ondelete='CASCADE'), nullable=False, comment='应用ID')
    device_id = Column(String(100), nullable=False, comment='设备唯一标识')
    device_name = Column(String(100), comment='设备名称')
    device_model = Column(String(100), comment='设备型号')
    os_version = Column(String(50), comment='系统版本')
    app_version = Column(String(20), comment='应用版本')
    push_token = Column(String(255), comment='推送令牌')
    last_active_at = Column(DateTime, comment='最后活跃时间')
    status = Column(SmallInteger, default=1, comment='状态: 1=在线, 0=离线')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    app = relationship("App", back_populates="devices")


class ConfigPushTask(Base):
    """配置推送任务表"""
    __tablename__ = 'config_push_tasks'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    app_id = Column(BigInteger, ForeignKey('apps.id', ondelete='CASCADE'), nullable=False, comment='应用ID')
    task_name = Column(String(200), nullable=False, comment='任务名称')
    push_type = Column(SmallInteger, nullable=False, comment='推送类型: 1=配置更新, 2=素材更新, 3=全量更新')
    target_devices = Column(JSON, comment='目标设备列表(device_id数组)')
    config_version = Column(String(20), comment='配置版本')
    status = Column(SmallInteger, default=0, comment='状态: 0=待推送, 1=推送中, 2=完成, 3=部分失败')
    total_devices = Column(Integer, default=0, comment='目标设备总数')
    success_count = Column(Integer, default=0, comment='成功数量')
    failed_count = Column(Integer, default=0, comment='失败数量')
    error_message = Column(Text, comment='错误信息')
    created_by = Column(BigInteger, ForeignKey('admin_users.id', ondelete='SET NULL'), comment='创建人ID')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    completed_at = Column(DateTime, comment='完成时间')

    # 关系
    app = relationship("App", back_populates="push_tasks")


class ApplicationConfig(Base):
    """应用配置表"""
    __tablename__ = 'application_configs'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    app_id = Column(String(100), unique=True, nullable=False, comment='统一应用标识(如com.jcoding.aiactivity)')
    app_name = Column(String(100), nullable=False, comment='应用名称')
    package_name = Column(String(100), comment='包名')
    version = Column(String(20), comment='版本号')
    config = Column(JSON, nullable=False, comment='JSON配置，存储所有配置项')
    status = Column(SmallInteger, default=1, comment='状态: 1=启用, 0=禁用')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class AdminOperationLog(Base):
    """管理员操作日志表"""
    __tablename__ = 'admin_operation_logs'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, ForeignKey('admin_users.id', ondelete='CASCADE'), nullable=False, comment='管理员ID')
    operation = Column(String(50), nullable=False, comment='操作类型')
    resource_type = Column(String(50), comment='资源类型')
    resource_id = Column(BigInteger, comment='资源ID')
    operation_desc = Column(Text, comment='操作描述')
    request_ip = Column(String(50), comment='请求IP')
    user_agent = Column(String(500), comment='User-Agent')
    status = Column(SmallInteger, default=1, comment='状态: 1=成功, 0=失败')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
