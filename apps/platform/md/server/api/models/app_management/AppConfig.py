# -*- coding: utf-8 -*-
from application import db
from common.models.model.PageDataProperty import PageDataProperty
from datetime import datetime


class AppConfig(db.Model, PageDataProperty):
    __tablename__ = 'app_configs'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    id = db.Column(db.Integer, primary_key=True)
    config_name = db.Column(db.String(200), nullable=False, comment='配置名称')
    config_key = db.Column(db.String(100), unique=True, nullable=False, index=True, comment='配置键')
    config_version = db.Column(db.String(50), nullable=False, comment='配置版本')
    config_data = db.Column(db.Text, nullable=False, comment='配置数据(JSON)')
    config_type = db.Column(db.String(50), comment='配置类型: global/module/feature')
    target_module = db.Column(db.String(100), comment='目标模块')
    is_active = db.Column(db.Integer, nullable=False, default=0, comment='是否激活: 0-否 1-是')
    is_published = db.Column(db.Integer, nullable=False, default=0, comment='是否已发布: 0-否 1-是')
    published_at = db.Column(db.DateTime, comment='发布时间')
    published_by = db.Column(db.Integer, comment='发布人ID')
    description = db.Column(db.Text, comment='配置描述')
    change_log = db.Column(db.Text, comment='变更日志')
    status = db.Column(db.Integer, nullable=False, default=1, comment='状态: 1-草稿 2-已发布 3-已归档')
    created_by = db.Column(db.Integer, comment='创建人ID')
    updated_by = db.Column(db.Integer, comment='更新人ID')
    created_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'config_name': self.config_name,
            'config_key': self.config_key,
            'config_version': self.config_version,
            'config_data': self.config_data,
            'config_type': self.config_type,
            'target_module': self.target_module,
            'is_active': self.is_active,
            'is_published': self.is_published,
            'published_at': self.published_at.strftime('%Y-%m-%d %H:%M:%S') if self.published_at else None,
            'published_by': self.published_by,
            'description': self.description,
            'change_log': self.change_log,
            'status': self.status,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'created_time': self.created_time.strftime('%Y-%m-%d %H:%M:%S') if self.created_time else None,
            'updated_time': self.updated_time.strftime('%Y-%m-%d %H:%M:%S') if self.updated_time else None
        }
