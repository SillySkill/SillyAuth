# -*- coding: utf-8 -*-
from application import db
from common.models.model.PageDataProperty import PageDataProperty
from datetime import datetime


class App(db.Model, PageDataProperty):
    __tablename__ = 'apps'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    id = db.Column(db.Integer, primary_key=True)
    app_key = db.Column(db.String(64), unique=True, nullable=False, index=True, comment='应用唯一标识')
    app_secret = db.Column(db.String(128), nullable=False, comment='应用密钥')
    app_name = db.Column(db.String(100), nullable=False, comment='应用名称')
    package_name = db.Column(db.String(200), comment='Android包名')
    bundle_id = db.Column(db.String(200), comment='iOS Bundle ID')
    app_type = db.Column(db.String(20), nullable=False, default='android', comment='应用类型: android/ios')
    platform = db.Column(db.String(50), comment='平台标识')
    version = db.Column(db.String(50), comment='应用版本')
    build_number = db.Column(db.String(50), comment='构建号')
    description = db.Column(db.Text, comment='应用描述')
    icon_url = db.Column(db.String(500), comment='应用图标URL')
    status = db.Column(db.Integer, nullable=False, default=1, comment='状态: 1-正常 2-禁用 3-删除')
    config_id = db.Column(db.Integer, db.ForeignKey('app_configs.id'), comment='关联配置ID')
    created_by = db.Column(db.Integer, comment='创建人ID')
    updated_by = db.Column(db.Integer, comment='更新人ID')
    created_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    config = db.relationship('AppConfig', backref=db.backref('apps', lazy='dynamic'))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'app_key': self.app_key,
            'app_name': self.app_name,
            'package_name': self.package_name,
            'bundle_id': self.bundle_id,
            'app_type': self.app_type,
            'platform': self.platform,
            'version': self.version,
            'build_number': self.build_number,
            'description': self.description,
            'icon_url': self.icon_url,
            'status': self.status,
            'config_id': self.config_id,
            'created_time': self.created_time.strftime('%Y-%m-%d %H:%M:%S') if self.created_time else None,
            'updated_time': self.updated_time.strftime('%Y-%m-%d %H:%M:%S') if self.updated_time else None
        }
