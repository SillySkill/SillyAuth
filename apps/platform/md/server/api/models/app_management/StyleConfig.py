# -*- coding: utf-8 -*-
from application import db
from common.models.model.PageDataProperty import PageDataProperty
from datetime import datetime


class StyleConfig(db.Model, PageDataProperty):
    __tablename__ = 'style_configs'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    id = db.Column(db.Integer, primary_key=True)
    style_id = db.Column(db.String(100), unique=True, nullable=False, index=True, comment='风格ID')
    style_name = db.Column(db.String(200), nullable=False, comment='风格名称')
    style_category = db.Column(db.String(100), comment='风格分类')
    thumbnail_url = db.Column(db.String(500), comment='缩略图URL')
    preview_images = db.Column(db.Text, comment='预览图片(JSON数组)')
    ai_provider = db.Column(db.String(100), comment='AI服务提供商: volcengine/tencent')
    model_id = db.Column(db.String(200), comment='模型ID')
    model_params = db.Column(db.Text, comment='模型参数(JSON)')
    processing_time = db.Column(db.Integer, comment='平均处理时间(秒)')
    quality_score = db.Column(db.Integer, comment='质量评分(1-100)')
    cost_per_generation = db.Column(db.Decimal(10, 2), comment='每次生成成本')
    is_premium = db.Column(db.Integer, nullable=False, default=0, comment='是否付费: 0-免费 1-付费')
    price = db.Column(db.Decimal(10, 2), comment='价格')
    sort_order = db.Column(db.Integer, default=0, comment='排序顺序')
    status = db.Column(db.Integer, nullable=False, default=1, comment='状态: 1-正常 2-禁用 3-删除')
    description = db.Column(db.Text, comment='风格描述')
    created_by = db.Column(db.Integer, comment='创建人ID')
    updated_by = db.Column(db.Integer, comment='更新人ID')
    created_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'style_id': self.style_id,
            'style_name': self.style_name,
            'style_category': self.style_category,
            'thumbnail_url': self.thumbnail_url,
            'preview_images': self.preview_images,
            'ai_provider': self.ai_provider,
            'model_id': self.model_id,
            'model_params': self.model_params,
            'processing_time': self.processing_time,
            'quality_score': self.quality_score,
            'cost_per_generation': str(self.cost_per_generation) if self.cost_per_generation else None,
            'is_premium': self.is_premium,
            'price': str(self.price) if self.price else None,
            'sort_order': self.sort_order,
            'status': self.status,
            'description': self.description,
            'created_time': self.created_time.strftime('%Y-%m-%d %H:%M:%S') if self.created_time else None,
            'updated_time': self.updated_time.strftime('%Y-%m-%d %H:%M:%S') if self.updated_time else None
        }
