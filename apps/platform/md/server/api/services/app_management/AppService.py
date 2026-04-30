# -*- coding: utf-8 -*-
import uuid
import json
from datetime import datetime
from application import db
from common.models.app_management.App import App
from common.models.app_management.Device import Device
from common.models.app_management.AppConfig import AppConfig
from common.models.app_management.StyleConfig import StyleConfig
from common.models.app_management.QuestionBank import QuestionBank
from common.models.app_management.PushHistory import PushHistory
from common.models.app_management.AuditLog import AuditLog
from common.libs.Helper import getCurrentDate


class AppManagementService:
    """应用管理服务类"""

    @staticmethod
    def generate_app_key():
        """生成应用唯一标识"""
        return f"app_{uuid.uuid4().hex[:24]}"

    @staticmethod
    def generate_app_secret():
        """生成应用密钥"""
        return uuid.uuid4().hex + uuid.uuid4().hex

    @staticmethod
    def create_app(data, operator_id=None):
        """创建应用"""
        app_key = AppManagementService.generate_app_key()
        app_secret = AppManagementService.generate_app_secret()

        app_model = App(
            app_key=app_key,
            app_secret=app_secret,
            app_name=data.get('app_name'),
            package_name=data.get('package_name'),
            bundle_id=data.get('bundle_id'),
            app_type=data.get('app_type', 'android'),
            platform=data.get('platform'),
            version=data.get('version'),
            build_number=data.get('build_number'),
            description=data.get('description'),
            icon_url=data.get('icon_url'),
            status=data.get('status', 1),
            config_id=data.get('config_id'),
            created_by=operator_id,
            updated_by=operator_id
        )

        db.session.add(app_model)
        db.session.commit()

        # 记录审计日志
        AppManagementService.log_audit(
            module='app_management',
            action='create',
            resource_type='app',
            resource_id=str(app_model.id),
            resource_name=app_model.app_name,
            operator_id=operator_id,
            new_data=json.dumps(app_model.serialize),
            result='success'
        )

        return app_model

    @staticmethod
    def update_app(app_id, data, operator_id=None):
        """更新应用"""
        app_model = App.query.filter_by(id=app_id).first()
        if not app_model:
            return None

        old_data = json.dumps(app_model.serialize)

        # 更新字段
        for key, value in data.items():
            if hasattr(app_model, key) and value is not None:
                setattr(app_model, key, value)

        app_model.updated_by = operator_id
        app_model.updated_time = getCurrentDate()

        db.session.commit()

        # 记录审计日志
        new_data = json.dumps(app_model.serialize)
        AppManagementService.log_audit(
            module='app_management',
            action='update',
            resource_type='app',
            resource_id=str(app_model.id),
            resource_name=app_model.app_name,
            operator_id=operator_id,
            old_data=old_data,
            new_data=new_data,
            result='success'
        )

        return app_model

    @staticmethod
    def delete_app(app_id, operator_id=None):
        """删除应用"""
        app_model = App.query.filter_by(id=app_id).first()
        if not app_model:
            return False

        old_data = json.dumps(app_model.serialize)
        app_model.status = 3  # 标记为删除
        app_model.updated_by = operator_id
        app_model.updated_time = getCurrentDate()

        db.session.commit()

        # 记录审计日志
        AppManagementService.log_audit(
            module='app_management',
            action='delete',
            resource_type='app',
            resource_id=str(app_model.id),
            resource_name=app_model.app_name,
            operator_id=operator_id,
            old_data=old_data,
            result='success'
        )

        return True

    @staticmethod
    def create_device(data, operator_id=None):
        """创建设备"""
        device_model = Device(
            device_id=data.get('device_id'),
            device_name=data.get('device_name'),
            device_type=data.get('device_type'),
            app_id=data.get('app_id'),
            platform=data.get('platform'),
            os_version=data.get('os_version'),
            app_version=data.get('app_version'),
            device_model=data.get('device_model'),
            manufacturer=data.get('manufacturer'),
            resolution=data.get('resolution'),
            density=data.get('density'),
            language=data.get('language'),
            network_type=data.get('network_type'),
            push_token=data.get('push_token'),
            extra_info=json.dumps(data.get('extra_info')) if data.get('extra_info') else None,
            status=data.get('status', 1)
        )

        db.session.add(device_model)
        db.session.commit()

        # 记录审计日志
        AppManagementService.log_audit(
            module='app_management',
            action='create',
            resource_type='device',
            resource_id=device_model.device_id,
            resource_name=device_model.device_name,
            operator_id=operator_id,
            new_data=json.dumps(device_model.serialize),
            result='success'
        )

        return device_model

    @staticmethod
    def update_device(device_id, data, operator_id=None):
        """更新设备"""
        device_model = Device.query.filter_by(device_id=device_id).first()
        if not device_model:
            return None

        old_data = json.dumps(device_model.serialize)

        for key, value in data.items():
            if hasattr(device_model, key) and value is not None:
                setattr(device_model, key, value)

        device_model.updated_time = getCurrentDate()
        db.session.commit()

        # 记录审计日志
        new_data = json.dumps(device_model.serialize)
        AppManagementService.log_audit(
            module='app_management',
            action='update',
            resource_type='device',
            resource_id=device_model.device_id,
            resource_name=device_model.device_name,
            operator_id=operator_id,
            old_data=old_data,
            new_data=new_data,
            result='success'
        )

        return device_model

    @staticmethod
    def create_config(data, operator_id=None):
        """创建配置"""
        config_model = AppConfig(
            config_name=data.get('config_name'),
            config_key=data.get('config_key'),
            config_version=data.get('config_version', 'v1.0.0'),
            config_data=json.dumps(data.get('config_data')),
            config_type=data.get('config_type', 'global'),
            target_module=data.get('target_module'),
            is_active=data.get('is_active', 0),
            is_published=data.get('is_published', 0),
            description=data.get('description'),
            change_log=data.get('change_log'),
            status=data.get('status', 1),
            created_by=operator_id,
            updated_by=operator_id
        )

        db.session.add(config_model)
        db.session.commit()

        # 记录审计日志
        AppManagementService.log_audit(
            module='app_management',
            action='create',
            resource_type='config',
            resource_id=str(config_model.id),
            resource_name=config_model.config_name,
            operator_id=operator_id,
            new_data=json.dumps(config_model.serialize),
            result='success'
        )

        return config_model

    @staticmethod
    def publish_config(config_id, operator_id=None):
        """发布配置"""
        config_model = AppConfig.query.filter_by(id=config_id).first()
        if not config_model:
            return None

        # 先取消其他激活的配置
        if config_model.target_module:
            AppConfig.query.filter(
                AppConfig.target_module == config_model.target_module,
                AppConfig.is_active == 1
            ).update({'is_active': 0})

        config_model.is_active = 1
        config_model.is_published = 1
        config_model.published_at = getCurrentDate()
        config_model.published_by = operator_id
        config_model.status = 2  # 已发布
        config_model.updated_by = operator_id
        config_model.updated_time = getCurrentDate()

        db.session.commit()

        # 记录审计日志
        AppManagementService.log_audit(
            module='app_management',
            action='publish',
            resource_type='config',
            resource_id=str(config_model.id),
            resource_name=config_model.config_name,
            operator_id=operator_id,
            new_data=json.dumps(config_model.serialize),
            result='success'
        )

        return config_model

    @staticmethod
    def create_push_task(data, operator_id=None):
        """创建推送任务"""
        push_model = PushHistory(
            push_id=data.get('push_id', f"push_{uuid.uuid4().hex[:20]}"),
            push_type=data.get('push_type'),
            target_type=data.get('target_type', 'all'),
            target_ids=json.dumps(data.get('target_ids', [])),
            title=data.get('title'),
            content=data.get('content'),
            push_data=json.dumps(data.get('push_data', {})),
            priority=data.get('priority', 0),
            scheduled_time=data.get('scheduled_time'),
            status=0,  # 待推送
            total_devices=data.get('total_devices', 0),
            created_by=operator_id
        )

        db.session.add(push_model)
        db.session.commit()

        # 记录审计日志
        AppManagementService.log_audit(
            module='app_management',
            action='create',
            resource_type='push',
            resource_id=push_model.push_id,
            resource_name=push_model.title,
            operator_id=operator_id,
            new_data=json.dumps(push_model.serialize),
            result='success'
        )

        return push_model

    @staticmethod
    def log_audit(module, action, resource_type, resource_id, resource_name=None,
                  operator_id=None, ip_address=None, request_method=None,
                  request_url=None, request_params=None, old_data=None,
                  new_data=None, changes=None, result='success', error_message=None):
        """记录审计日志"""
        log_model = AuditLog(
            log_id=f"log_{uuid.uuid4().hex[:20]}",
            module=module,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            operator_id=operator_id,
            ip_address=ip_address,
            request_method=request_method,
            request_url=request_url,
            request_params=json.dumps(request_params) if request_params else None,
            old_data=old_data,
            new_data=new_data,
            changes=changes,
            result=result,
            error_message=error_message
        )

        db.session.add(log_model)
        db.session.commit()

        return log_model

    @staticmethod
    def get_pagination(query, page=1, page_size=20):
        """分页查询"""
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        return {
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'page_size': page_size,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'items': [item.serialize for item in pagination.items]
        }
