# coding: utf-8
"""
Application Model
"""
from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime
from sqlalchemy.sql.expression import text
from application import db


class Application(db.Model):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='Application ID')
    app_key = Column(String(64), nullable=False, unique=True, comment='Application unique key')
    app_name = Column(String(100), nullable=False, comment='Application display name')
    app_name_en = Column(String(100), nullable=True, comment='Application English name')
    package_name = Column(String(200), nullable=True, comment='Android package name')
    version = Column(String(20), nullable=False, server_default='1.0.0', comment='Current version')
    version_code = Column(Integer, nullable=False, server_default='1', comment='Version code')
    min_sdk_version = Column(Integer, nullable=False, server_default='24', comment='Minimum SDK')
    target_sdk_version = Column(Integer, nullable=False, server_default='34', comment='Target SDK')
    icon_url = Column(String(500), nullable=True, comment='Icon URL')
    description = Column(Text, nullable=True, comment='Description')
    description_en = Column(Text, nullable=True, comment='English description')
    features = Column(db.JSON, nullable=True, comment='Features list')
    screenshots = Column(db.JSON, nullable=True, comment='Screenshots URLs')
    download_url = Column(String(500), nullable=True, comment='APK download URL')
    download_count = Column(BigInteger, nullable=False, server_default='0', comment='Download count')
    category = Column(String(50), nullable=False, server_default='entertainment', comment='Category')
    tags = Column(db.JSON, nullable=True, comment='Tags')
    developer = Column(String(100), nullable=False, server_default='jCoding', comment='Developer')
    website = Column(String(200), nullable=True, comment='Website')
    contact_email = Column(String(100), nullable=True, comment='Contact email')
    status = Column(db.SmallInteger, nullable=False, server_default='1', comment='Status')
    is_default = Column(db.SmallInteger, nullable=False, server_default='0', comment='Is default')
    sort_order = Column(Integer, nullable=False, server_default='0', comment='Sort order')
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='Created at')
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='Updated at')

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            'id': self.id,
            'app_key': self.app_key,
            'app_name': self.app_name,
            'app_name_en': self.app_name_en,
            'package_name': self.package_name,
            'version': self.version,
            'version_code': self.version_code,
            'icon_url': self.icon_url,
            'description': self.description,
            'download_count': self.download_count,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
