"""
后台管理 - 应用管理API - FastAPI版本
提供应用的CRUD操作和统计功能
"""

import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import select, update, delete, func

from database import get_db
from models_admin import App, AdminUser, AppModule, AppAsset, AppDevice, ConfigPushTask, AdminOperationLog

router = APIRouter(prefix="/api/admin/apps", tags=["Admin Apps"])

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

class CreateAppRequest(BaseModel):
    app_name: str
    app_name_en: Optional[str] = None
    app_description: Optional[str] = None
    app_icon: Optional[str] = None
    package_name: Optional[str] = None
    version: Optional[str] = "1.0.0"
    status: Optional[int] = 1
    app_key: Optional[str] = None


class UpdateAppRequest(BaseModel):
    app_name: Optional[str] = None
    app_name_en: Optional[str] = None
    app_description: Optional[str] = None
    app_icon: Optional[str] = None
    package_name: Optional[str] = None
    version: Optional[str] = None
    status: Optional[int] = None


# ==================== API路由 ====================

@router.get('/')
async def get_apps_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    created_by: Optional[int] = Query(None),
    current_admin: dict = Depends(get_current_admin)
):
    """获取应用列表"""
    async for db in get_db():
        # 构建查询
        query = select(App)

        # 搜索条件
        if keyword:
            query = query.where(
                (App.app_name.like(f'%{keyword}%')) |
                (App.app_key.like(f'%{keyword}%')) |
                (App.package_name.like(f'%{keyword}%'))
            )

        # 状态筛选
        if status is not None:
            query = query.where(App.status == status)

        # 创建人筛选
        if created_by:
            query = query.where(App.created_by == created_by)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.order_by(App.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        apps = result.scalars().all()

        # 序列化结果
        apps_list = []
        for app in apps:
            apps_list.append({
                'id': app.id,
                'app_key': app.app_key,
                'app_name': app.app_name,
                'app_name_en': app.app_name_en,
                'app_description': app.app_description,
                'app_icon': app.app_icon,
                'package_name': app.package_name,
                'version': app.version,
                'status': app.status,
                'created_by': app.created_by,
                'created_at': app.created_at.isoformat() if app.created_at else None,
                'updated_at': app.updated_at.isoformat() if app.updated_at else None,
            })

        return {
            'code': 200,
            'message': 'success',
            'data': {
                'list': apps_list,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }


@router.post('/')
async def create_app(
    request_data: CreateAppRequest,
    request: Request,
    current_admin: dict = Depends(get_current_admin)
):
    """创建应用（仅超级管理员）"""
    if current_admin['role'] != 1:
        raise HTTPException(status_code=403, detail="权限不足")

    async for db in get_db():
        # 生成唯一的app_key
        app_key = request_data.app_key or f'app_{uuid.uuid4().hex[:16]}'

        # 检查app_key是否已存在
        existing = await db.execute(
            select(App).where(App.app_key == app_key)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="应用标识已存在")

        # 创建应用
        app = App(
            app_key=app_key,
            app_name=request_data.app_name,
            app_name_en=request_data.app_name_en,
            app_description=request_data.app_description,
            app_icon=request_data.app_icon,
            package_name=request_data.package_name,
            version=request_data.version,
            status=request_data.status,
            created_by=current_admin['admin_id']
        )

        db.add(app)
        await db.commit()
        await db.refresh(app)

        # 记录操作日志
        await log_operation(
            db=db,
            admin_id=current_admin['admin_id'],
            operation='create_app',
            resource_type='app',
            resource_id=app.id,
            operation_desc=f'创建应用: {app.app_name}',
            request_ip=request.client.host
        )

        return {
            'code': 200,
            'message': '创建成功',
            'data': {
                'id': app.id,
                'app_key': app.app_key,
                'app_name': app.app_name,
                'version': app.version,
                'status': app.status
            }
        }


@router.get('/{app_id}')
async def get_app_detail(
    app_id: int,
    current_admin: dict = Depends(get_current_admin)
):
    """获取应用详情"""
    async for db in get_db():
        result = await db.execute(
            select(App).where(App.id == app_id)
        )
        app = result.scalar_one_or_none()

        if not app:
            raise HTTPException(status_code=404, detail="应用不存在")

        # 获取创建人信息
        creator = None
        if app.created_by:
            creator_result = await db.execute(
                select(AdminUser).where(AdminUser.id == app.created_by)
            )
            creator_user = creator_result.scalar_one_or_none()
            if creator_user:
                creator = {
                    'id': creator_user.id,
                    'username': creator_user.username,
                    'real_name': creator_user.real_name
                }

        return {
            'code': 200,
            'message': 'success',
            'data': {
                'id': app.id,
                'app_key': app.app_key,
                'app_name': app.app_name,
                'app_name_en': app.app_name_en,
                'app_description': app.app_description,
                'app_icon': app.app_icon,
                'package_name': app.package_name,
                'version': app.version,
                'status': app.status,
                'created_by': app.created_by,
                'creator': creator,
                'created_at': app.created_at.isoformat() if app.created_at else None,
                'updated_at': app.updated_at.isoformat() if app.updated_at else None,
            }
        }


@router.put('/{app_id}')
async def update_app(
    app_id: int,
    request_data: UpdateAppRequest,
    request: Request,
    current_admin: dict = Depends(get_current_admin)
):
    """更新应用信息"""
    async for db in get_db():
        # 检查应用是否存在
        result = await db.execute(
            select(App).where(App.id == app_id)
        )
        app = result.scalar_one_or_none()

        if not app:
            raise HTTPException(status_code=404, detail="应用不存在")

        # 权限检查：只有超级管理员或应用创建者可以修改
        if current_admin['role'] != 1 and app.created_by != current_admin['admin_id']:
            raise HTTPException(status_code=403, detail="权限不足")

        # 构建更新数据
        update_data = {}
        if request_data.app_name is not None:
            update_data['app_name'] = request_data.app_name
        if request_data.app_name_en is not None:
            update_data['app_name_en'] = request_data.app_name_en
        if request_data.app_description is not None:
            update_data['app_description'] = request_data.app_description
        if request_data.app_icon is not None:
            update_data['app_icon'] = request_data.app_icon
        if request_data.package_name is not None:
            update_data['package_name'] = request_data.package_name
        if request_data.version is not None:
            update_data['version'] = request_data.version
        if request_data.status is not None:
            update_data['status'] = request_data.status

        if not update_data:
            raise HTTPException(status_code=400, detail="没有可更新的字段")

        # 执行更新
        await db.execute(
            update(App)
            .where(App.id == app_id)
            .values(**update_data)
        )
        await db.commit()

        # 记录操作日志
        await log_operation(
            db=db,
            admin_id=current_admin['admin_id'],
            operation='update_app',
            resource_type='app',
            resource_id=app_id,
            operation_desc=f'更新应用: {app.app_name}',
            request_ip=request.client.host
        )

        return {
            'code': 200,
            'message': '更新成功'
        }


@router.delete('/{app_id}')
async def delete_app(
    app_id: int,
    request: Request,
    current_admin: dict = Depends(get_current_admin)
):
    """删除应用（仅超级管理员）"""
    if current_admin['role'] != 1:
        raise HTTPException(status_code=403, detail="权限不足")

    async for db in get_db():
        # 检查应用是否存在
        result = await db.execute(
            select(App).where(App.id == app_id)
        )
        app = result.scalar_one_or_none()

        if not app:
            raise HTTPException(status_code=404, detail="应用不存在")

        app_name = app.app_name

        # 删除应用（级联删除关联数据）
        await db.execute(
            delete(App).where(App.id == app_id)
        )
        await db.commit()

        # 记录操作日志
        await log_operation(
            db=db,
            admin_id=current_admin['admin_id'],
            operation='delete_app',
            resource_type='app',
            resource_id=app_id,
            operation_desc=f'删除应用: {app_name}',
            request_ip=request.client.host
        )

        return {
            'code': 200,
            'message': '删除成功'
        }


@router.get('/{app_id}/stats')
async def get_app_stats(
    app_id: int,
    current_admin: dict = Depends(get_current_admin)
):
    """获取应用统计信息"""
    async for db in get_db():
        # 检查应用是否存在
        result = await db.execute(
            select(App).where(App.id == app_id)
        )
        app = result.scalar_one_or_none()

        if not app:
            raise HTTPException(status_code=404, detail="应用不存在")

        # 统计模块数量
        modules_count = await db.scalar(
            select(func.count())
            .select_from(AppModule)
            .where(AppModule.app_id == app_id)
        )

        # 统计素材数量
        assets_count = await db.scalar(
            select(func.count())
            .select_from(AppAsset)
            .where(AppAsset.app_id == app_id)
        )

        # 统计设备总数
        devices_count = await db.scalar(
            select(func.count())
            .select_from(AppDevice)
            .where(AppDevice.app_id == app_id)
        )

        # 统计在线设备数
        online_devices_count = await db.scalar(
            select(func.count())
            .select_from(AppDevice)
            .where(AppDevice.app_id == app_id, AppDevice.status == 1)
        )

        # 统计推送任务数
        push_tasks_count = await db.scalar(
            select(func.count())
            .select_from(ConfigPushTask)
            .where(ConfigPushTask.app_id == app_id)
        )

        return {
            'code': 200,
            'message': 'success',
            'data': {
                'modules_count': modules_count or 0,
                'assets_count': assets_count or 0,
                'devices_count': devices_count or 0,
                'online_devices_count': online_devices_count or 0,
                'push_tasks_count': push_tasks_count or 0
            }
        }
