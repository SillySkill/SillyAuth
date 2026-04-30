# -*- coding: utf-8 -*-
"""
应用管理 API - 完整的后端管理系统
包含应用、设备、配置、风格、题库、推送管理
"""
from web.controllers.admin.app_management import route_app_management
from flask import request, jsonify, g
from application import app, db
from common.models.app_management.App import App
from common.models.app_management.Device import Device
from common.models.app_management.AppConfig import AppConfig
from common.models.app_management.StyleConfig import StyleConfig
from common.models.app_management.QuestionBank import QuestionBank
from common.models.app_management.PushHistory import PushHistory
from common.models.app_management.AuditLog import AuditLog
from common.libs.app_management.AppService import AppManagementService
from common.libs.Helper import iPagination
from sqlalchemy import or_, and_, desc
import json


# ==================== 辅助函数 ====================

def get_operator_info():
    """获取操作人信息"""
    # 这里应该从认证信息中获取，暂时返回默认值
    return getattr(g, 'user_id', None), getattr(g, 'user_name', 'admin')


def get_client_info():
    """获取客户端信息"""
    return {
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'request_method': request.method,
        'request_url': request.url
    }


def standard_response(code=200, msg='操作成功', data=None):
    """标准响应格式"""
    resp = {
        'code': code,
        'msg': msg,
        'data': data if data is not None else {}
    }
    return jsonify(resp)


def validate_required_fields(data, required_fields):
    """验证必填字段"""
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"
    return True, None


# ==================== 应用管理 ====================

@route_app_management.route("/apps", methods=["GET"])
def get_apps():
    """
    获取应用列表
    ---
    tags:
      - 应用管理
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: 页码
      - name: page_size
        in: query
        type: integer
        default: 20
        description: 每页数量
      - name: app_name
        in: query
        type: string
        description: 应用名称(模糊搜索)
      - name: app_type
        in: query
        type: string
        description: 应用类型
      - name: status
        in: query
        type: integer
        description: 状态
    responses:
      200:
        description: 成功返回应用列表
    """
    try:
        req = request.values
        page = int(req.get('page', 1))
        page_size = int(req.get('page_size', 20))

        query = App.query.filter(App.status != 3)  # 排除已删除

        # 搜索条件
        if req.get('app_name'):
            query = query.filter(App.app_name.like(f"%{req.get('app_name')}%"))
        if req.get('app_type'):
            query = query.filter(App.app_type == req.get('app_type'))
        if req.get('status'):
            query = query.filter(App.status == int(req.get('status')))

        query = query.order_by(desc(App.id))

        # 分页
        pagination_info = AppManagementService.get_pagination(query, page, page_size)

        return standard_response(data=pagination_info)
    except Exception as e:
        app.logger.error(f"获取应用列表失败: {str(e)}")
        return standard_response(code=-1, msg=f"获取应用列表失败: {str(e)}")


@route_app_management.route("/apps", methods=["POST"])
def create_app():
    """
    创建应用
    ---
    tags:
      - 应用管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - app_name
            - app_type
          properties:
            app_name:
              type: string
              description: 应用名称
            app_type:
              type: string
              description: 应用类型
            package_name:
              type: string
              description: 包名
            bundle_id:
              type: string
              description: Bundle ID
            platform:
              type: string
              description: 平台
            version:
              type: string
              description: 版本号
            description:
              type: string
              description: 描述
    responses:
      200:
        description: 创建成功
    """
    try:
        data = request.get_json() if request.is_json else request.values.to_dict()

        # 验证必填字段
        is_valid, error_msg = validate_required_fields(data, ['app_name', 'app_type'])
        if not is_valid:
            return standard_response(code=-1, msg=error_msg)

        operator_id, _ = get_operator_info()

        app_model = AppManagementService.create_app(data, operator_id)

        return standard_response(data={'app': app_model.serialize}, msg='应用创建成功')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"创建应用失败: {str(e)}")
        return standard_response(code=-1, msg=f"创建应用失败: {str(e)}")


@route_app_management.route("/apps/<int:app_id>", methods=["PUT"])
def update_app(app_id):
    """
    更新应用
    ---
    tags:
      - 应用管理
    parameters:
      - name: app_id
        in: path
        type: integer
        required: true
        description: 应用ID
      - name: body
        in: body
        schema:
          type: object
          properties:
            app_name:
              type: string
            version:
              type: string
            description:
              type: string
    responses:
      200:
        description: 更新成功
    """
    try:
        data = request.get_json() if request.is_json else request.values.to_dict()

        operator_id, _ = get_operator_info()

        app_model = AppManagementService.update_app(app_id, data, operator_id)

        if not app_model:
            return standard_response(code=-1, msg='应用不存在')

        return standard_response(data={'app': app_model.serialize}, msg='应用更新成功')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"更新应用失败: {str(e)}")
        return standard_response(code=-1, msg=f"更新应用失败: {str(e)}")


@route_app_management.route("/apps/<int:app_id>", methods=["DELETE"])
def delete_app(app_id):
    """
    删除应用
    ---
    tags:
      - 应用管理
    parameters:
      - name: app_id
        in: path
        type: integer
        required: true
        description: 应用ID
    responses:
      200:
        description: 删除成功
    """
    try:
        operator_id, _ = get_operator_info()

        result = AppManagementService.delete_app(app_id, operator_id)

        if not result:
            return standard_response(code=-1, msg='应用不存在')

        return standard_response(msg='应用删除成功')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"删除应用失败: {str(e)}")
        return standard_response(code=-1, msg=f"删除应用失败: {str(e)}")


# ==================== 设备管理 ====================

@route_app_management.route("/devices", methods=["GET"])
def get_devices():
    """
    获取设备列表
    ---
    tags:
      - 设备管理
    parameters:
      - name: page
        in: query
        type: integer
      - name: page_size
        in: query
        type: integer
      - name: app_id
        in: query
        type: integer
      - name: status
        in: query
        type: integer
    responses:
      200:
        description: 成功返回设备列表
    """
    try:
        req = request.values
        page = int(req.get('page', 1))
        page_size = int(req.get('page_size', 20))

        query = Device.query

        if req.get('app_id'):
            query = query.filter(Device.app_id == int(req.get('app_id')))
        if req.get('status'):
            query = query.filter(Device.status == int(req.get('status')))

        query = query.order_by(desc(Device.id))

        pagination_info = AppManagementService.get_pagination(query, page, page_size)

        return standard_response(data=pagination_info)
    except Exception as e:
        app.logger.error(f"获取设备列表失败: {str(e)}")
        return standard_response(code=-1, msg=f"获取设备列表失败: {str(e)}")


@route_app_management.route("/devices/<device_id>", methods=["GET"])
def get_device_detail(device_id):
    """
    获取设备详情
    ---
    tags:
      - 设备管理
    parameters:
      - name: device_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: 成功返回设备详情
    """
    try:
        device = Device.query.filter_by(device_id=device_id).first()

        if not device:
            return standard_response(code=-1, msg='设备不存在')

        return standard_response(data={'device': device.serialize})
    except Exception as e:
        app.logger.error(f"获取设备详情失败: {str(e)}")
        return standard_response(code=-1, msg=f"获取设备详情失败: {str(e)}")


@route_app_management.route("/devices/<device_id>", methods=["PUT"])
def update_device(device_id):
    """
    更新设备
    ---
    tags:
      - 设备管理
    parameters:
      - name: device_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        schema:
          type: object
          properties:
            device_name:
              type: string
            status:
              type: integer
    responses:
      200:
        description: 更新成功
    """
    try:
        data = request.get_json() if request.is_json else request.values.to_dict()

        operator_id, _ = get_operator_info()

        device_model = AppManagementService.update_device(device_id, data, operator_id)

        if not device_model:
            return standard_response(code=-1, msg='设备不存在')

        return standard_response(data={'device': device_model.serialize}, msg='设备更新成功')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"更新设备失败: {str(e)}")
        return standard_response(code=-1, msg=f"更新设备失败: {str(e)}")


@route_app_management.route("/devices/<device_id>", methods=["DELETE"])
def delete_device(device_id):
    """
    删除设备
    ---
    tags:
      - 设备管理
    parameters:
      - name: device_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: 删除成功
    """
    try:
        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return standard_response(code=-1, msg='设备不存在')

        db.session.delete(device)
        db.session.commit()

        return standard_response(msg='设备删除成功')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"删除设备失败: {str(e)}")
        return standard_response(code=-1, msg=f"删除设备失败: {str(e)}")


@route_app_management.route("/devices/<device_id>/push-config", methods=["POST"])
def push_config_to_device(device_id):
    """
    推送配置到设备
    ---
    tags:
      - 设备管理
    parameters:
      - name: device_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        schema:
          type: object
          required:
            - config_id
          properties:
            config_id:
              type: integer
    responses:
      200:
        description: 推送成功
    """
    try:
        data = request.get_json() if request.is_json else request.values.to_dict()
        config_id = data.get('config_id')

        if not config_id:
            return standard_response(code=-1, msg='缺少配置ID')

        device = Device.query.filter_by(device_id=device_id).first()
        if not device:
            return standard_response(code=-1, msg='设备不存在')

        config = AppConfig.query.filter_by(id=config_id).first()
        if not config:
            return standard_response(code=-1, msg='配置不存在')

        # 创建推送任务
        push_data = {
            'push_id': f"push_{device_id}_{config_id}",
            'push_type': 'config',
            'target_type': 'device',
            'target_ids': [device_id],
            'title': f"推送配置: {config.config_name}",
            'content': f"向设备 {device.device_name} 推送配置 {config.config_name}",
            'push_data': {
                'config_id': config_id,
                'config_key': config.config_key,
                'config_version': config.config_version,
                'config_data': json.loads(config.config_data)
            },
            'total_devices': 1
        }

        operator_id, _ = get_operator_info()
        push_task = AppManagementService.create_push_task(push_data, operator_id)

        # TODO: 这里应该调用实际的推送服务，将配置推送到设备
        # 例如: WebSocket 推送、Firebase 推送等

        return standard_response(data={'push_id': push_task.push_id}, msg='配置推送任务已创建')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"推送配置失败: {str(e)}")
        return standard_response(code=-1, msg=f"推送配置失败: {str(e)}")


# ==================== 配置管理 ====================

@route_app_management.route("/configs", methods=["GET"])
def get_configs():
    """
    获取配置列表
    ---
    tags:
      - 配置管理
    parameters:
      - name: page
        in: query
        type: integer
      - name: page_size
        in: query
        type: integer
      - name: config_type
        in: query
        type: string
      - name: status
        in: query
        type: integer
    responses:
      200:
        description: 成功返回配置列表
    """
    try:
        req = request.values
        page = int(req.get('page', 1))
        page_size = int(req.get('page_size', 20))

        query = AppConfig.query

        if req.get('config_type'):
            query = query.filter(AppConfig.config_type == req.get('config_type'))
        if req.get('target_module'):
            query = query.filter(AppConfig.target_module == req.get('target_module'))
        if req.get('status'):
            query = query.filter(AppConfig.status == int(req.get('status')))

        query = query.order_by(desc(AppConfig.id))

        pagination_info = AppManagementService.get_pagination(query, page, page_size)

        return standard_response(data=pagination_info)
    except Exception as e:
        app.logger.error(f"获取配置列表失败: {str(e)}")
        return standard_response(code=-1, msg=f"获取配置列表失败: {str(e)}")


@route_app_management.route("/configs", methods=["POST"])
def create_config():
    """
    创建配置
    ---
    tags:
      - 配置管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - config_name
            - config_key
            - config_data
          properties:
            config_name:
              type: string
            config_key:
              type: string
            config_version:
              type: string
            config_data:
              type: object
            config_type:
              type: string
            target_module:
              type: string
    responses:
      200:
        description: 创建成功
    """
    try:
        data = request.get_json() if request.is_json else request.values.to_dict()

        is_valid, error_msg = validate_required_fields(data, ['config_name', 'config_key', 'config_data'])
        if not is_valid:
            return standard_response(code=-1, msg=error_msg)

        operator_id, _ = get_operator_info()

        config_model = AppManagementService.create_config(data, operator_id)

        return standard_response(data={'config': config_model.serialize}, msg='配置创建成功')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"创建配置失败: {str(e)}")
        return standard_response(code=-1, msg=f"创建配置失败: {str(e)}")


@route_app_management.route("/configs/<int:config_id>", methods=["GET"])
def get_config_detail(config_id):
    """
    获取配置详情
    ---
    tags:
      - 配置管理
    parameters:
      - name: config_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: 成功返回配置详情
    """
    try:
        config = AppConfig.query.filter_by(id=config_id).first()

        if not config:
            return standard_response(code=-1, msg='配置不存在')

        return standard_response(data={'config': config.serialize})
    except Exception as e:
        app.logger.error(f"获取配置详情失败: {str(e)}")
        return standard_response(code=-1, msg=f"获取配置详情失败: {str(e)}")


@route_app_management.route("/configs/<int:config_id>", methods=["PUT"])
def update_config(config_id):
    """
    更新配置
    ---
    tags:
      - 配置管理
    parameters:
      - name: config_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        schema:
          type: object
          properties:
            config_name:
              type: string
            config_data:
              type: object
    responses:
      200:
        description: 更新成功
    """
    try:
        data = request.get_json() if request.is_json else request.values.to_dict()

        config = AppConfig.query.filter_by(id=config_id).first()
        if not config:
            return standard_response(code=-1, msg='配置不存在')

        old_data = json.dumps(config.serialize)

        # 更新字段
        if 'config_name' in data:
            config.config_name = data['config_name']
        if 'config_data' in data:
            config.config_data = json.dumps(data['config_data'])
        if 'description' in data:
            config.description = data['description']
        if 'change_log' in data:
            config.change_log = data['change_log']

        config.updated_by = get_operator_info()[0]

        db.session.commit()

        return standard_response(data={'config': config.serialize}, msg='配置更新成功')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"更新配置失败: {str(e)}")
        return standard_response(code=-1, msg=f"更新配置失败: {str(e)}")


@route_app_management.route("/configs/publish", methods=["POST"])
def publish_config():
    """
    发布配置
    ---
    tags:
      - 配置管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - config_id
          properties:
            config_id:
              type: integer
    responses:
      200:
        description: 发布成功
    """
    try:
        data = request.get_json() if request.is_json else request.values.to_dict()
        config_id = data.get('config_id')

        if not config_id:
            return standard_response(code=-1, msg='缺少配置ID')

        operator_id, _ = get_operator_info()

        config_model = AppManagementService.publish_config(config_id, operator_id)

        if not config_model:
            return standard_response(code=-1, msg='配置不存在')

        return standard_response(data={'config': config_model.serialize}, msg='配置发布成功')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"发布配置失败: {str(e)}")
        return standard_response(code=-1, msg=f"发布配置失败: {str(e)}")


@route_app_management.route("/configs/active", methods=["GET"])
def get_active_config():
    """
    获取当前激活的配置
    ---
    tags:
      - 配置管理
    parameters:
      - name: target_module
        in: query
        type: string
        description: 目标模块
    responses:
      200:
        description: 成功返回激活的配置
    """
    try:
        req = request.values
        target_module = req.get('target_module')

        query = AppConfig.query.filter(AppConfig.is_active == 1)

        if target_module:
            query = query.filter(AppConfig.target_module == target_module)

        configs = query.all()

        return standard_response(data={
            'configs': [config.serialize for config in configs]
        })
    except Exception as e:
        app.logger.error(f"获取激活配置失败: {str(e)}")
        return standard_response(code=-1, msg=f"获取激活配置失败: {str(e)}")


# ==================== 风格配置 ====================

@route_app_management.route("/styles", methods=["GET"])
def get_styles():
    """
    获取风格列表
    ---
    tags:
      - 风格配置
    parameters:
      - name: page
        in: query
        type: integer
      - name: page_size
        in: query
        type: integer
      - name: style_category
        in: query
        type: string
      - name: status
        in: query
        type: integer
    responses:
      200:
        description: 成功返回风格列表
    """
    try:
        req = request.values
        page = int(req.get('page', 1))
        page_size = int(req.get('page_size', 20))

        query = StyleConfig.query.filter(StyleConfig.status != 3)

        if req.get('style_category'):
            query = query.filter(StyleConfig.style_category == req.get('style_category'))
        if req.get('ai_provider'):
            query = query.filter(StyleConfig.ai_provider == req.get('ai_provider'))
        if req.get('status'):
            query = query.filter(StyleConfig.status == int(req.get('status')))

        query = query.order_by(StyleConfig.sort_order.asc(), StyleConfig.id.desc())

        pagination_info = AppManagementService.get_pagination(query, page, page_size)

        return standard_response(data=pagination_info)
    except Exception as e:
        app.logger.error(f"获取风格列表失败: {str(e)}")
        return standard_response(code=-1, msg=f"获取风格列表失败: {str(e)}")


@route_app_management.route("/styles", methods=["POST"])
def create_style():
    """
    创建风格
    ---
    tags:
      - 风格配置
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - style_id
            - style_name
          properties:
            style_id:
              type: string
            style_name:
              type: string
            style_category:
              type: string
            ai_provider:
              type: string
            model_id:
              type: string
    responses:
      200:
        description: 创建成功
    """
    try:
        data = request.get_json() if request.is_json else request.values.to_dict()

        is_valid, error_msg = validate_required_fields(data, ['style_id', 'style_name'])
        if not is_valid:
            return standard_response(code=-1, msg=error_msg)

        # 检查 style_id 是否已存在
        if StyleConfig.query.filter_by(style_id=data['style_id']).first():
            return standard_response(code=-1, msg='风格ID已存在')

        style_model = StyleConfig(
            style_id=data.get('style_id'),
            style_name=data.get('style_name'),
            style_category=data.get('style_category'),
            thumbnail_url=data.get('thumbnail_url'),
            preview_images=json.dumps(data.get('preview_images', [])),
            ai_provider=data.get('ai_provider'),
            model_id=data.get('model_id'),
            model_params=json.dumps(data.get('model_params', {})),
            processing_time=data.get('processing_time'),
            quality_score=data.get('quality_score'),
            cost_per_generation=data.get('cost_per_generation'),
            is_premium=data.get('is_premium', 0),
            price=data.get('price'),
            sort_order=data.get('sort_order', 0),
            status=data.get('status', 1),
            description=data.get('description'),
            created_by=get_operator_info()[0],
            updated_by=get_operator_info()[0]
        )

        db.session.add(style_model)
        db.session.commit()

        return standard_response(data={'style': style_model.serialize}, msg='风格创建成功')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"创建风格失败: {str(e)}")
        return standard_response(code=-1, msg=f"创建风格失败: {str(e)}")


@route_app_management.route("/styles/<int:style_id>", methods=["PUT"])
def update_style(style_id):
    """
    更新风格
    ---
    tags:
      - 风格配置
    parameters:
      - name: style_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        schema:
          type: object
          properties:
            style_name:
              type: string
            description:
              type: string
    responses:
      200:
        description: 更新成功
    """
    try:
        data = request.get_json() if request.is_json else request.values.to_dict()

        style_model = StyleConfig.query.filter_by(id=style_id).first()
        if not style_model:
            return standard_response(code=-1, msg='风格不存在')

        # 更新字段
        for key, value in data.items():
            if hasattr(style_model, key) and key not in ['id', 'created_time']:
                if key in ['preview_images', 'model_params'] and isinstance(value, (dict, list)):
                    setattr(style_model, key, json.dumps(value))
                elif value is not None:
                    setattr(style_model, key, value)

        style_model.updated_by = get_operator_info()[0]

        db.session.commit()

        return standard_response(data={'style': style_model.serialize}, msg='风格更新成功')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"更新风格失败: {str(e)}")
        return standard_response(code=-1, msg=f"更新风格失败: {str(e)}")


@route_app_management.route("/styles/<int:style_id>", methods=["DELETE"])
def delete_style(style_id):
    """
    删除风格
    ---
    tags:
      - 风格配置
    parameters:
      - name: style_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: 删除成功
    """
    try:
        style_model = StyleConfig.query.filter_by(id=style_id).first()
        if not style_model:
            return standard_response(code=-1, msg='风格不存在')

        style_model.status = 3  # 标记为删除
        style_model.updated_by = get_operator_info()[0]

        db.session.commit()

        return standard_response(msg='风格删除成功')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"删除风格失败: {str(e)}")
        return standard_response(code=-1, msg=f"删除风格失败: {str(e)}")


# ==================== 题库管理 ====================

@route_app_management.route("/question-banks", methods=["GET"])
def get_question_banks():
    """
    获取题库列表
    ---
    tags:
      - 题库管理
    parameters:
      - name: page
        in: query
        type: integer
      - name: page_size
        in: query
        type: integer
      - name: bank_category
        in: query
        type: string
      - name: difficulty_level
        in: query
        type: string
    responses:
      200:
        description: 成功返回题库列表
    """
    try:
        req = request.values
        page = int(req.get('page', 1))
        page_size = int(req.get('page_size', 20))

        query = QuestionBank.query.filter(QuestionBank.status != 3)

        if req.get('bank_category'):
            query = query.filter(QuestionBank.bank_category == req.get('bank_category'))
        if req.get('difficulty_level'):
            query = query.filter(QuestionBank.difficulty_level == req.get('difficulty_level'))
        if req.get('is_public'):
            query = query.filter(QuestionBank.is_public == int(req.get('is_public')))

        query = query.order_by(QuestionBank.sort_order.asc(), QuestionBank.id.desc())

        pagination_info = AppManagementService.get_pagination(query, page, page_size)

        return standard_response(data=pagination_info)
    except Exception as e:
        app.logger.error(f"获取题库列表失败: {str(e)}")
        return standard_response(code=-1, msg=f"获取题库列表失败: {str(e)}")


@route_app_management.route("/question-banks", methods=["POST"])
def create_question_bank():
    """
    创建题库
    ---
    tags:
      - 题库管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - bank_id
            - bank_name
          properties:
            bank_id:
              type: string
            bank_name:
              type: string
            bank_category:
              type: string
            difficulty_level:
              type: string
            question_data:
              type: object
    responses:
      200:
        description: 创建成功
    """
    try:
        data = request.get_json() if request.is_json else request.values.to_dict()

        is_valid, error_msg = validate_required_fields(data, ['bank_id', 'bank_name'])
        if not is_valid:
            return standard_response(code=-1, msg=error_msg)

        # 检查 bank_id 是否已存在
        if QuestionBank.query.filter_by(bank_id=data['bank_id']).first():
            return standard_response(code=-1, msg='题库ID已存在')

        # 统计题目数量
        question_data = data.get('question_data', {})
        choice_count = len(question_data.get('choice_questions', []))
        judgement_count = len(question_data.get('judgement_questions', []))
        total_questions = choice_count + judgement_count

        bank_model = QuestionBank(
            bank_id=data.get('bank_id'),
            bank_name=data.get('bank_name'),
            bank_category=data.get('bank_category'),
            difficulty_level=data.get('difficulty_level'),
            total_questions=total_questions,
            choice_count=choice_count,
            judgement_count=judgement_count,
            time_limit=data.get('time_limit'),
            pass_score=data.get('pass_score'),
            total_score=data.get('total_score'),
            tags=data.get('tags'),
            cover_image=data.get('cover_image'),
            description=data.get('description'),
            question_data=json.dumps(question_data),
            prize_config=json.dumps(data.get('prize_config', {})),
            is_public=data.get('is_public', 1),
            sort_order=data.get('sort_order', 0),
            status=data.get('status', 1),
            created_by=get_operator_info()[0],
            updated_by=get_operator_info()[0]
        )

        db.session.add(bank_model)
        db.session.commit()

        return standard_response(data={'question_bank': bank_model.serialize}, msg='题库创建成功')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"创建题库失败: {str(e)}")
        return standard_response(code=-1, msg=f"创建题库失败: {str(e)}")


@route_app_management.route("/question-banks/<int:bank_id>", methods=["PUT"])
def update_question_bank(bank_id):
    """
    更新题库
    ---
    tags:
      - 题库管理
    parameters:
      - name: bank_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        schema:
          type: object
          properties:
            bank_name:
              type: string
            description:
              type: string
    responses:
      200:
        description: 更新成功
    """
    try:
        data = request.get_json() if request.is_json else request.values.to_dict()

        bank_model = QuestionBank.query.filter_by(id=bank_id).first()
        if not bank_model:
            return standard_response(code=-1, msg='题库不存在')

        # 更新字段
        for key, value in data.items():
            if hasattr(bank_model, key) and key not in ['id', 'created_time']:
                if key in ['question_data', 'prize_config'] and isinstance(value, (dict, list)):
                    setattr(bank_model, key, json.dumps(value))
                elif value is not None:
                    setattr(bank_model, key, value)

        bank_model.updated_by = get_operator_info()[0]

        db.session.commit()

        return standard_response(data={'question_bank': bank_model.serialize}, msg='题库更新成功')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"更新题库失败: {str(e)}")
        return standard_response(code=-1, msg=f"更新题库失败: {str(e)}")


@route_app_management.route("/question-banks/<int:bank_id>", methods=["DELETE"])
def delete_question_bank(bank_id):
    """
    删除题库
    ---
    tags:
      - 题库管理
    parameters:
      - name: bank_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: 删除成功
    """
    try:
        bank_model = QuestionBank.query.filter_by(id=bank_id).first()
        if not bank_model:
            return standard_response(code=-1, msg='题库不存在')

        bank_model.status = 3  # 标记为删除
        bank_model.updated_by = get_operator_info()[0]

        db.session.commit()

        return standard_response(msg='题库删除成功')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"删除题库失败: {str(e)}")
        return standard_response(code=-1, msg=f"删除题库失败: {str(e)}")


@route_app_management.route("/question-banks/import", methods=["POST"])
def import_question_bank():
    """
    导入题库
    ---
    tags:
      - 题库管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - bank_id
            - bank_name
            - file_data
          properties:
            bank_id:
              type: string
            bank_name:
              type: string
            file_data:
              type: string
              description: JSON格式的题库数据
    responses:
      200:
        description: 导入成功
    """
    try:
        data = request.get_json() if request.is_json else request.values.to_dict()

        is_valid, error_msg = validate_required_fields(data, ['bank_id', 'bank_name', 'file_data'])
        if not is_valid:
            return standard_response(code=-1, msg=error_msg)

        # 解析题库数据
        try:
            question_data = json.loads(data['file_data'])
        except:
            return standard_response(code=-1, msg='题库数据格式错误，必须是有效的JSON')

        # 检查 bank_id 是否已存在
        if QuestionBank.query.filter_by(bank_id=data['bank_id']).first():
            return standard_response(code=-1, msg='题库ID已存在')

        # 统计题目数量
        choice_count = len(question_data.get('choice_questions', []))
        judgement_count = len(question_data.get('judgement_questions', []))
        total_questions = choice_count + judgement_count

        bank_model = QuestionBank(
            bank_id=data.get('bank_id'),
            bank_name=data.get('bank_name'),
            bank_category=data.get('bank_category'),
            difficulty_level=data.get('difficulty_level'),
            total_questions=total_questions,
            choice_count=choice_count,
            judgement_count=judgement_count,
            time_limit=data.get('time_limit'),
            pass_score=data.get('pass_score'),
            total_score=data.get('total_score'),
            tags=data.get('tags'),
            cover_image=data.get('cover_image'),
            description=data.get('description'),
            question_data=json.dumps(question_data),
            prize_config=json.dumps(data.get('prize_config', {})),
            is_public=data.get('is_public', 1),
            sort_order=data.get('sort_order', 0),
            status=data.get('status', 1),
            created_by=get_operator_info()[0],
            updated_by=get_operator_info()[0]
        )

        db.session.add(bank_model)
        db.session.commit()

        return standard_response(
            data={'question_bank': bank_model.serialize},
            msg=f'题库导入成功，共导入 {total_questions} 道题目'
        )
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"导入题库失败: {str(e)}")
        return standard_response(code=-1, msg=f"导入题库失败: {str(e)}")


# ==================== 推送管理 ====================

@route_app_management.route("/push-history", methods=["GET"])
def get_push_history():
    """
    获取推送历史
    ---
    tags:
      - 推送管理
    parameters:
      - name: page
        in: query
        type: integer
      - name: page_size
        in: query
        type: integer
      - name: push_type
        in: query
        type: string
      - name: status
        in: query
        type: integer
    responses:
      200:
        description: 成功返回推送历史
    """
    try:
        req = request.values
        page = int(req.get('page', 1))
        page_size = int(req.get('page_size', 20))

        query = PushHistory.query

        if req.get('push_type'):
            query = query.filter(PushHistory.push_type == req.get('push_type'))
        if req.get('status'):
            query = query.filter(PushHistory.status == int(req.get('status')))

        query = query.order_by(PushHistory.id.desc())

        pagination_info = AppManagementService.get_pagination(query, page, page_size)

        return standard_response(data=pagination_info)
    except Exception as e:
        app.logger.error(f"获取推送历史失败: {str(e)}")
        return standard_response(code=-1, msg=f"获取推送历史失败: {str(e)}")


@route_app_management.route("/push/batch", methods=["POST"])
def batch_push():
    """
    批量推送
    ---
    tags:
      - 推送管理
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - push_type
            - target_type
            - target_ids
            - push_data
          properties:
            push_type:
              type: string
              description: 推送类型
            target_type:
              type: string
              description: 目标类型
            target_ids:
              type: array
              description: 目标ID列表
            title:
              type: string
              description: 推送标题
            content:
              type: string
              description: 推送内容
            push_data:
              type: object
              description: 推送数据
            priority:
              type: integer
              description: 优先级
    responses:
      200:
        description: 推送成功
    """
    try:
        data = request.get_json() if request.is_json else request.values.to_dict()

        is_valid, error_msg = validate_required_fields(data, ['push_type', 'target_type', 'target_ids', 'push_data'])
        if not is_valid:
            return standard_response(code=-1, msg=error_msg)

        target_ids = data.get('target_ids', [])
        if not isinstance(target_ids, list):
            return standard_response(code=-1, msg='target_ids 必须是数组')

        # 创建批量推送任务
        push_data = {
            'push_type': data.get('push_type'),
            'target_type': data.get('target_type'),
            'target_ids': target_ids,
            'title': data.get('title'),
            'content': data.get('content'),
            'push_data': data.get('push_data'),
            'priority': data.get('priority', 0),
            'total_devices': len(target_ids)
        }

        operator_id, _ = get_operator_info()
        push_task = AppManagementService.create_push_task(push_data, operator_id)

        # TODO: 这里应该调用实际的批量推送服务
        # 可以使用异步任务队列 (Celery) 进行批量推送

        return standard_response(
            data={'push_id': push_task.push_id, 'total_devices': len(target_ids)},
            msg=f'批量推送任务已创建，目标设备数: {len(target_ids)}'
        )
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"批量推送失败: {str(e)}")
        return standard_response(code=-1, msg=f"批量推送失败: {str(e)}")


@route_app_management.route("/push/<push_id>/status", methods=["GET"])
def get_push_status(push_id):
    """
    获取推送状态
    ---
    tags:
      - 推送管理
    parameters:
      - name: push_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: 成功返回推送状态
    """
    try:
        push_task = PushHistory.query.filter_by(push_id=push_id).first()

        if not push_task:
            return standard_response(code=-1, msg='推送任务不存在')

        status_info = {
            'push_id': push_task.push_id,
            'status': push_task.status,
            'status_text': ['待推送', '推送中', '已完成', '失败', '已取消'][push_task.status] if push_task.status < 5 else '未知',
            'total_devices': push_task.total_devices,
            'success_count': push_task.success_count,
            'failure_count': push_task.failure_count,
            'started_at': push_task.started_at.strftime('%Y-%m-%d %H:%M:%S') if push_task.started_at else None,
            'completed_at': push_task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if push_task.completed_at else None,
            'error_message': push_task.error_message
        }

        return standard_response(data={'push_status': status_info})
    except Exception as e:
        app.logger.error(f"获取推送状态失败: {str(e)}")
        return standard_response(code=-1, msg=f"获取推送状态失败: {str(e)}")


# ==================== 统计信息 ====================

@route_app_management.route("/statistics", methods=["GET"])
def get_statistics():
    """
    获取统计信息
    ---
    tags:
      - 统计信息
    responses:
      200:
        description: 成功返回统计信息
    """
    try:
        stats = {
            'total_apps': App.query.filter(App.status != 3).count(),
            'total_devices': Device.query.count(),
            'online_devices': Device.query.filter(Device.status == 1).count(),
            'total_configs': AppConfig.query.count(),
            'active_configs': AppConfig.query.filter(AppConfig.is_active == 1).count(),
            'total_styles': StyleConfig.query.filter(StyleConfig.status != 3).count(),
            'total_question_banks': QuestionBank.query.filter(QuestionBank.status != 3).count(),
            'total_push_tasks': PushHistory.query.count(),
            'push_success_rate': 0.0
        }

        # 计算推送成功率
        total_push = PushHistory.query.filter(PushHistory.status.in_([2, 3])).count()
        success_push = PushHistory.query.filter(PushHistory.status == 2).count()
        if total_push > 0:
            stats['push_success_rate'] = round(success_push / total_push * 100, 2)

        return standard_response(data={'statistics': stats})
    except Exception as e:
        app.logger.error(f"获取统计信息失败: {str(e)}")
        return standard_response(code=-1, msg=f"获取统计信息失败: {str(e)}")


# ==================== 审计日志 ====================

@route_app_management.route("/audit-logs", methods=["GET"])
def get_audit_logs():
    """
    获取审计日志
    ---
    tags:
      - 审计日志
    parameters:
      - name: page
        in: query
        type: integer
      - name: page_size
        in: query
        type: integer
      - name: module
        in: query
        type: string
      - name: action
        in: query
        type: string
      - name: resource_type
        in: query
        type: string
    responses:
      200:
        description: 成功返回审计日志
    """
    try:
        req = request.values
        page = int(req.get('page', 1))
        page_size = int(req.get('page_size', 50))

        query = AuditLog.query

        if req.get('module'):
            query = query.filter(AuditLog.module == req.get('module'))
        if req.get('action'):
            query = query.filter(AuditLog.action == req.get('action'))
        if req.get('resource_type'):
            query = query.filter(AuditLog.resource_type == req.get('resource_type'))

        query = query.order_by(AuditLog.id.desc())

        pagination_info = AppManagementService.get_pagination(query, page, page_size)

        return standard_response(data=pagination_info)
    except Exception as e:
        app.logger.error(f"获取审计日志失败: {str(e)}")
        return standard_response(code=-1, msg=f"获取审计日志失败: {str(e)}")
