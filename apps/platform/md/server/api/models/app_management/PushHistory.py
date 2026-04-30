# -*- coding: utf-8 -*-
from application import db
from common.models.model.PageDataProperty import PageDataProperty
from datetime import datetime


class PushHistory(db.Model, PageDataProperty):
    __tablename__ = 'push_history'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    id = db.Column(db.Integer, primary_key=True)
    push_id = db.Column(db.String(100), unique=True, nullable=False, index=True, comment='推送任务ID')
    push_type = db.Column(db.String(50), nullable=False, comment='推送类型: config/announcement/force_update')
    target_type = db.Column(db.String(50), comment='目标类型: all/app/device/group')
    target_ids = db.Column(db.Text, comment='目标ID列表(JSON)')
    title = db.Column(db.String(200), comment='推送标题')
    content = db.Column(db.Text, comment='推送内容')
    push_data = db.Column(db.Text, comment='推送数据(JSON)')
    priority = db.Column(db.Integer, default=0, comment='优先级: 0-普通 1-高 2-紧急')
    scheduled_time = db.Column(db.DateTime, comment='计划推送时间')
    status = db.Column(db.Integer, nullable=False, default=0, comment='状态: 0-待推送 1-推送中 2-已完成 3-失败 4-已取消')
    total_devices = db.Column(db.Integer, default=0, comment='目标设备总数')
    success_count = db.Column(db.Integer, default=0, comment='成功数量')
    failure_count = db.Column(db.Integer, default=0, comment='失败数量')
    started_at = db.Column(db.DateTime, comment='开始推送时间')
    completed_at = db.Column(db.DateTime, comment='完成推送时间')
    error_message = db.Column(db.Text, comment='错误信息')
    retry_count = db.Column(db.Integer, default=0, comment='重试次数')
    created_by = db.Column(db.Integer, comment='创建人ID')
    created_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'push_id': self.push_id,
            'push_type': self.push_type,
            'target_type': self.target_type,
            'target_ids': self.target_ids,
            'title': self.title,
            'content': self.content,
            'push_data': self.push_data,
            'priority': self.priority,
            'scheduled_time': self.scheduled_time.strftime('%Y-%m-%d %H:%M:%S') if self.scheduled_time else None,
            'status': self.status,
            'total_devices': self.total_devices,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'started_at': self.started_at.strftime('%Y-%m-%d %H:%M:%S') if self.started_at else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'created_by': self.created_by,
            'created_time': self.created_time.strftime('%Y-%m-%d %H:%M:%S') if self.created_time else None,
            'updated_time': self.updated_time.strftime('%Y-%m-%d %H:%M:%S') if self.updated_time else None
        }
