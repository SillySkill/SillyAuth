# -*- coding: utf-8 -*-
from application import db
from common.models.model.PageDataProperty import PageDataProperty
from datetime import datetime


class AuditLog(db.Model, PageDataProperty):
    __tablename__ = 'audit_logs'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    id = db.Column(db.Integer, primary_key=True)
    log_id = db.Column(db.String(100), unique=True, nullable=False, index=True, comment='日志ID')
    module = db.Column(db.String(100), comment='模块名称')
    action = db.Column(db.String(100), comment='操作类型: create/update/delete/publish')
    resource_type = db.Column(db.String(100), comment='资源类型: app/device/config/style/question_bank')
    resource_id = db.Column(db.String(100), comment='资源ID')
    resource_name = db.Column(db.String(200), comment='资源名称')
    operator_id = db.Column(db.Integer, comment='操作人ID')
    operator_name = db.Column(db.String(200), comment='操作人姓名')
    ip_address = db.Column(db.String(50), comment='IP地址')
    user_agent = db.Column(db.String(500), comment='用户代理')
    request_method = db.Column(db.String(10), comment='请求方法: GET/POST/PUT/DELETE')
    request_url = db.Column(db.String(500), comment='请求URL')
    request_params = db.Column(db.Text, comment='请求参数')
    old_data = db.Column(db.Text, comment='修改前数据(JSON)')
    new_data = db.Column(db.Text, comment='修改后数据(JSON)')
    changes = db.Column(db.Text, comment='变更内容(JSON)')
    result = db.Column(db.String(50), comment='操作结果: success/failed/partial')
    error_message = db.Column(db.Text, comment='错误信息')
    created_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'log_id': self.log_id,
            'module': self.module,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'operator_id': self.operator_id,
            'operator_name': self.operator_name,
            'ip_address': self.ip_address,
            'request_method': self.request_method,
            'request_url': self.request_url,
            'request_params': self.request_params,
            'result': self.result,
            'error_message': self.error_message,
            'created_time': self.created_time.strftime('%Y-%m-%d %H:%M:%S') if self.created_time else None
        }
