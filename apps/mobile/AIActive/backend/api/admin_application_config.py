"""
应用配置管理API - FastAPI版本
提供应用配置的CRUD操作、验证和重置功能
"""

from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import select, update, delete, func

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_admin import get_db
from models_admin import ApplicationConfig, AdminOperationLog
from utils.config_validator import (
    validate_config,
    get_default_config,
    reset_to_defaults,
    merge_config,
    get_config_schema
)

router = APIRouter(prefix="/api/admin/application/config", tags=["Application Config"])

security = HTTPBearer()


# ==================== 辅助函数 ====================

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前管理员"""
    import jwt
    import os
    JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
    JWT_ALGORITHM = 'HS256'

    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")


async def log_operation(db, admin_id: int, operation: str,
                        operation_desc: str = None, resource_type: str = None,
                        resource_id: int = None, request_ip: str = None):
    """记录管理员操作日志"""
    log = AdminOperationLog(
        admin_id=admin_id,
        operation=operation,
        resource_type=resource_type,
        resource_id=resource_id,
        operation_desc=operation_desc,
        request_ip=request_ip,
        status=1
    )
    db.add(log)
    await db.commit()


# ==================== 数据模型 ====================

class CreateConfigRequest(BaseModel):
    app_id: str  # 统一应用标识，如 'com.jcoding.aiactivity'
    app_name: str
    package_name: Optional[str] = None
    version: Optional[str] = None
    config: Dict[str, Any]


class UpdateConfigRequest(BaseModel):
    app_name: Optional[str] = None
    package_name: Optional[str] = None
    version: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[int] = None


class PartialUpdateRequest(BaseModel):
    """部分更新配置（只更新指定的字段）"""
    config: Dict[str, Any]  # 要更新的配置字段，会与现有配置合并


# ==================== API路由 ====================

@router.get('/')
async def get_configs_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    current_admin: dict = Depends(get_current_admin)
):
    """获取应用配置列表"""
    async for db in get_db():
        # 构建查询
        query = select(ApplicationConfig)

        # 搜索条件
        if keyword:
            query = query.where(
                (ApplicationConfig.app_name.like(f'%{keyword}%')) |
                (ApplicationConfig.app_id.like(f'%{keyword}%')) |
                (ApplicationConfig.package_name.like(f'%{keyword}%'))
            )

        # 状态筛选
        if status is not None:
            query = query.where(ApplicationConfig.status == status)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.order_by(ApplicationConfig.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        configs = result.scalars().all()

        # 序列化结果
        configs_list = []
        for config in configs:
            configs_list.append({
                'id': config.id,
                'app_id': config.app_id,
                'app_name': config.app_name,
                'package_name': config.package_name,
                'version': config.version,
                'config': config.config,
                'status': config.status,
                'created_at': config.created_at.isoformat() if config.created_at else None,
                'updated_at': config.updated_at.isoformat() if config.updated_at else None,
            })

        return {
            'code': 200,
            'message': 'success',
            'data': {
                'list': configs_list,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }


@router.get('/{app_id}')
async def get_config_by_app_id(
    app_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """根据app_id获取应用配置"""
    async for db in get_db():
        result = await db.execute(
            select(ApplicationConfig).where(ApplicationConfig.app_id == app_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            raise HTTPException(status_code=404, detail="应用配置不存在")

        return {
            'code': 200,
            'message': 'success',
            'data': {
                'id': config.id,
                'app_id': config.app_id,
                'app_name': config.app_name,
                'package_name': config.package_name,
                'version': config.version,
                'config': config.config,
                'status': config.status,
                'created_at': config.created_at.isoformat() if config.created_at else None,
                'updated_at': config.updated_at.isoformat() if config.updated_at else None,
            }
        }


@router.post('/')
async def create_config(
    request_data: CreateConfigRequest,
    request: Request,
    current_admin: dict = Depends(get_current_admin)
):
    """创建应用配置"""
    async for db in get_db():
        # 检查app_id是否已存在
        existing = await db.execute(
            select(ApplicationConfig).where(ApplicationConfig.app_id == request_data.app_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="应用配置已存在")

        # 验证配置
        is_valid, errors = validate_config(request_data.config)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "配置验证失败",
                    "errors": errors
                }
            )

        # 创建配置
        config = ApplicationConfig(
            app_id=request_data.app_id,
            app_name=request_data.app_name,
            package_name=request_data.package_name,
            version=request_data.version,
            config=request_data.config,
            status=1
        )

        db.add(config)
        await db.commit()
        await db.refresh(config)

        # 记录操作日志
        await log_operation(
            db=db,
            admin_id=current_admin['admin_id'],
            operation='create_config',
            resource_type='application_config',
            resource_id=config.id,
            operation_desc=f'创建应用配置: {config.app_name}',
            request_ip=request.client.host
        )

        return {
            'code': 200,
            'message': '创建成功',
            'data': {
                'id': config.id,
                'app_id': config.app_id,
                'app_name': config.app_name,
                'version': config.version
            }
        }


@router.put('/{app_id}')
async def update_config(
    app_id: str,
    request_data: UpdateConfigRequest,
    request: Request,
    current_admin: dict = Depends(get_current_admin)
):
    """更新应用配置（完整更新）"""
    async for db in get_db():
        # 检查配置是否存在
        result = await db.execute(
            select(ApplicationConfig).where(ApplicationConfig.app_id == app_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            raise HTTPException(status_code=404, detail="应用配置不存在")

        # 如果提供了config，验证配置
        if request_data.config is not None:
            is_valid, errors = validate_config(request_data.config)
            if not is_valid:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "配置验证失败",
                        "errors": errors
                    }
                )

        # 构建更新数据
        update_data = {}
        if request_data.app_name is not None:
            update_data['app_name'] = request_data.app_name
        if request_data.package_name is not None:
            update_data['package_name'] = request_data.package_name
        if request_data.version is not None:
            update_data['version'] = request_data.version
        if request_data.config is not None:
            update_data['config'] = request_data.config
        if request_data.status is not None:
            update_data['status'] = request_data.status

        if not update_data:
            raise HTTPException(status_code=400, detail="没有可更新的字段")

        # 执行更新
        await db.execute(
            update(ApplicationConfig)
            .where(ApplicationConfig.app_id == app_id)
            .values(**update_data)
        )
        await db.commit()

        # 记录操作日志
        await log_operation(
            db=db,
            admin_id=current_admin['admin_id'],
            operation='update_config',
            resource_type='application_config',
            resource_id=config.id,
            operation_desc=f'更新应用配置: {config.app_name}',
            request_ip=request.client.host
        )

        return {
            'code': 200,
            'message': '更新成功'
        }


@router.patch('/{app_id}')
async def partial_update_config(
    app_id: str,
    request_data: PartialUpdateRequest,
    request: Request,
    current_admin: dict = Depends(get_current_admin)
):
    """部分更新应用配置（合并更新）"""
    async for db in get_db():
        # 检查配置是否存在
        result = await db.execute(
            select(ApplicationConfig).where(ApplicationConfig.app_id == app_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            raise HTTPException(status_code=404, detail="应用配置不存在")

        # 合并配置
        merged_config = merge_config(config.config, request_data.config)

        # 验证合并后的配置
        is_valid, errors = validate_config(merged_config)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "配置验证失败",
                    "errors": errors
                }
            )

        # 执行更新
        await db.execute(
            update(ApplicationConfig)
            .where(ApplicationConfig.app_id == app_id)
            .values(config=merged_config)
        )
        await db.commit()

        # 记录操作日志
        await log_operation(
            db=db,
            admin_id=current_admin['admin_id'],
            operation='partial_update_config',
            resource_type='application_config',
            resource_id=config.id,
            operation_desc=f'部分更新应用配置: {config.app_name}',
            request_ip=request.client.host
        )

        return {
            'code': 200,
            'message': '更新成功',
            'data': {
                'config': merged_config
            }
        }


@router.delete('/{app_id}')
async def delete_config(
    app_id: str,
    request: Request,
    current_admin: dict = Depends(get_current_admin)
):
    """删除应用配置（仅超级管理员）"""
    if current_admin['role'] != 1:
        raise HTTPException(status_code=403, detail="权限不足")

    async for db in get_db():
        # 检查配置是否存在
        result = await db.execute(
            select(ApplicationConfig).where(ApplicationConfig.app_id == app_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            raise HTTPException(status_code=404, detail="应用配置不存在")

        app_name = config.app_name

        # 删除配置
        await db.execute(
            delete(ApplicationConfig).where(ApplicationConfig.app_id == app_id)
        )
        await db.commit()

        # 记录操作日志
        await log_operation(
            db=db,
            admin_id=current_admin['admin_id'],
            operation='delete_config',
            resource_type='application_config',
            resource_id=config.id,
            operation_desc=f'删除应用配置: {app_name}',
            request_ip=request.client.host
        )

        return {
            'code': 200,
            'message': '删除成功'
        }


@router.get('/{app_id}/schema')
async def get_config_schema_endpoint(
    app_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """获取配置结构（用于前端生成表单）"""
    async for db in get_db():
        # 检查配置是否存在
        result = await db.execute(
            select(ApplicationConfig).where(ApplicationConfig.app_id == app_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            raise HTTPException(status_code=404, detail="应用配置不存在")

        # 获取配置schema
        schema_info = get_config_schema()

        return {
            'code': 200,
            'message': 'success',
            'data': {
                'app_id': app_id,
                'current_config': config.config,
                'schema': schema_info['schema'],
                'default_config': schema_info['default'],
                'ui_schema': schema_info['ui_schema']
            }
        }


@router.post('/{app_id}/reset')
async def reset_config(
    app_id: str,
    request: Request,
    current_admin: dict = Depends(get_current_admin)
):
    """重置为默认配置"""
    async for db in get_db():
        # 检查配置是否存在
        result = await db.execute(
            select(ApplicationConfig).where(ApplicationConfig.app_id == app_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            raise HTTPException(status_code=404, detail="应用配置不存在")

        # 重置为默认配置
        default_config = reset_to_defaults(config.config)

        # 执行更新
        await db.execute(
            update(ApplicationConfig)
            .where(ApplicationConfig.app_id == app_id)
            .values(config=default_config)
        )
        await db.commit()

        # 记录操作日志
        await log_operation(
            db=db,
            admin_id=current_admin['admin_id'],
            operation='reset_config',
            resource_type='application_config',
            resource_id=config.id,
            operation_desc=f'重置应用配置为默认值: {config.app_name}',
            request_ip=request.client.host
        )

        return {
            'code': 200,
            'message': '重置成功',
            'data': {
                'config': default_config
            }
        }


@router.post('/{app_id}/validate')
async def validate_config_endpoint(
    app_id: str,
    request_data: Dict[str, Any],
    current_admin: dict = Depends(get_current_admin)
):
    """验证配置（不保存，仅验证）"""
    async for db in get_db():
        # 检查配置是否存在
        result = await db.execute(
            select(ApplicationConfig).where(ApplicationConfig.app_id == app_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            raise HTTPException(status_code=404, detail="应用配置不存在")

        # 验证配置
        is_valid, errors = validate_config(request_data)

        return {
            'code': 200,
            'message': '验证完成',
            'data': {
                'valid': is_valid,
                'errors': errors if not is_valid else []
            }
        }


@router.get('/{app_id}/history')
async def get_config_history(
    app_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_admin: dict = Depends(get_current_admin)
):
    """获取配置修改历史（从操作日志中获取）"""
    async for db in get_db():
        # 检查配置是否存在
        result = await db.execute(
            select(ApplicationConfig).where(ApplicationConfig.app_id == app_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            raise HTTPException(status_code=404, detail="应用配置不存在")

        # 查询操作日志
        from sqlalchemy import desc
        query = select(AdminOperationLog).where(
            AdminOperationLog.resource_type == 'application_config',
            AdminOperationLog.resource_id == config.id,
            AdminOperationLog.operation.in_(['create_config', 'update_config', 'partial_update_config', 'reset_config'])
        )

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.order_by(desc(AdminOperationLog.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        logs = result.scalars().all()

        # 序列化结果
        logs_list = []
        for log in logs:
            logs_list.append({
                'id': log.id,
                'operation': log.operation,
                'operation_desc': log.operation_desc,
                'request_ip': log.request_ip,
                'status': log.status,
                'created_at': log.created_at.isoformat() if log.created_at else None,
            })

        return {
            'code': 200,
            'message': 'success',
            'data': {
                'list': logs_list,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }
