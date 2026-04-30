# -*- coding: utf-8 -*-
from application import db
from common.models.model.PageDataProperty import PageDataProperty
from datetime import datetime


class Device(db.Model, PageDataProperty):
    __tablename__ = 'devices'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), unique=True, nullable=False, index=True, comment='设备唯一标识')
    device_name = db.Column(db.String(200), comment='设备名称')
    device_type = db.Column(db.String(50), comment='设备类型: phone/tablet/tv')
    app_id = db.Column(db.Integer, db.ForeignKey('apps.id'), nullable=False, comment='关联应用ID')
    platform = db.Column(db.String(50), comment='平台: android/ios')
    os_version = db.Column(db.String(50), comment='操作系统版本')
    app_version = db.Column(db.String(50), comment='应用版本')
    device_model = db.Column(db.String(200), comment='设备型号')
    manufacturer = db.Column(db.String(200), comment='制造商')
    resolution = db.Column(db.String(50), comment='屏幕分辨率')
    density = db.Column(db.String(50), comment='屏幕密度')
    language = db.Column(db.String(20), comment='系统语言')
    network_type = db.Column(db.String(50), comment='网络类型')
    last_active_time = db.Column(db.DateTime, comment='最后活跃时间')
    config_version = db.Column(db.String(50), comment='当前配置版本')
    push_token = db.Column(db.String(500), comment='推送令牌')
    status = db.Column(db.Integer, nullable=False, default=1, comment='状态: 1-在线 2-离线 3-禁用')
    extra_info = db.Column(db.Text, comment='额外信息(JSON)')
    created_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    app = db.relationship('App', backref=db.backref('devices', lazy='dynamic'))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'app_id': self.app_id,
            'platform': self.platform,
            'os_version': self.os_version,
            'app_version': self.app_version,
            'device_model': self.device_model,
            'manufacturer': self.manufacturer,
            'resolution': self.resolution,
            'density': self.density,
            'language': self.language,
            'network_type': self.network_type,
            'last_active_time': self.last_active_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_active_time else None,
            'config_version': self.config_version,
            'status': self.status,
            'created_time': self.created_time.strftime('%Y-%m-%d %H:%M:%S') if self.created_time else None,
            'updated_time': self.updated_time.strftime('%Y-%m-%d %H:%M:%S') if self.updated_time else None
        }
