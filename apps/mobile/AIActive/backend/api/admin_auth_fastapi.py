"""
后台管理认证API - FastAPI版本
提供管理员登录、登出、个人信息管理等功能
"""

import bcrypt
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import select, update
from typing import Optional

from database import get_db
from models_admin import AdminUser, AdminOperationLog

router = APIRouter(prefix="/api/admin/auth", tags=["Admin Auth"])

# JWT配置
import jwt
import os
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'

security = HTTPBearer()


# ==================== 数据模型 ====================

class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


# ==================== 辅助函数 ====================

def generate_token(admin_id: int, username: str, role: int) -> str:
    """生成JWT Token"""
    from datetime import timedelta
    payload = {
        'admin_id': admin_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """解码JWT Token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def hash_password(password: str) -> str:
    """对密码进行哈希"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前管理员"""
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")

    return payload


# ==================== API路由 ====================

@router.post('/login')
async def login(request_data: LoginRequest, request: Request):
    """管理员登录"""
    async for db in get_db():
        # 查询管理员
        result = await db.execute(
            select(AdminUser).where(
                AdminUser.username == request_data.username,
                AdminUser.status == 1
            )
        )
        admin = result.scalar_one_or_none()

        if not admin:
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        # 验证密码
        if not verify_password(request_data.password, admin.password_hash):
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        # 生成token
        token = generate_token(admin.id, admin.username, admin.role)

        # 更新最后登录信息
        await db.execute(
            update(AdminUser)
            .where(AdminUser.id == admin.id)
            .values(
                last_login_at=datetime.utcnow(),
                last_login_ip=request.client.host
            )
        )
        await db.commit()

        return {
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': token,
                'admin': {
                    'id': admin.id,
                    'username': admin.username,
                    'real_name': admin.real_name,
                    'email': admin.email,
                    'role': admin.role,
                    'role_name': '超级管理员' if admin.role == 1 else '应用管理员'
                }
            }
        }


@router.post('/logout')
async def logout(current_admin: dict = Depends(get_current_admin)):
    """管理员登出"""
    return {
        'code': 200,
        'message': '登出成功'
    }


@router.get('/profile')
async def get_profile(current_admin: dict = Depends(get_current_admin)):
    """获取当前管理员个人信息"""
    async for db in get_db():
        result = await db.execute(
            select(AdminUser).where(AdminUser.id == current_admin['admin_id'])
        )
        admin = result.scalar_one_or_none()

        if not admin:
            raise HTTPException(status_code=404, detail="管理员不存在")

        return {
            'code': 200,
            'message': 'success',
            'data': {
                'id': admin.id,
                'username': admin.username,
                'real_name': admin.real_name,
                'email': admin.email,
                'phone': admin.phone,
                'role': admin.role,
                'role_name': '超级管理员' if admin.role == 1 else '应用管理员',
                'status': admin.status,
                'last_login_at': admin.last_login_at.isoformat() if admin.last_login_at else None,
                'last_login_ip': admin.last_login_ip,
                'created_at': admin.created_at.isoformat() if admin.created_at else None
            }
        }


@router.put('/password')
async def change_password(
    request_data: ChangePasswordRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """修改密码"""
    if len(request_data.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码长度不能少于6位")

    async for db in get_db():
        # 查询管理员
        result = await db.execute(
            select(AdminUser).where(AdminUser.id == current_admin['admin_id'])
        )
        admin = result.scalar_one_or_none()

        if not admin:
            raise HTTPException(status_code=404, detail="管理员不存在")

        # 验证旧密码
        if not verify_password(request_data.old_password, admin.password_hash):
            raise HTTPException(status_code=401, detail="旧密码错误")

        # 更新密码
        await db.execute(
            update(AdminUser)
            .where(AdminUser.id == admin.id)
            .values(password_hash=hash_password(request_data.new_password))
        )
        await db.commit()

        return {
            'code': 200,
            'message': '密码修改成功'
        }
