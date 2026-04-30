"""
初始化管理员账户
"""
import asyncio
import sys
import os
import bcrypt

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from models_admin import AdminUser
from database_admin import get_db_session


def hash_password(password: str) -> str:
    """对密码进行哈希"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


async def create_admin_user():
    """创建管理员用户"""
    print("=" * 60)
    print("初始化管理员账户")
    print("=" * 60)

    # 获取输入
    username = input("请输入管理员用户名 (默认: admin): ").strip() or "admin"
    password = input("请输入密码 (默认: admin123): ").strip() or "admin123"
    real_name = input("请输入真实姓名 (默认: 管理员): ").strip() or "管理员"
    email = input("请输入邮箱 (可选): ").strip() or None
    phone = input("请输入手机号 (可选): ").strip() or None

    # 密码长度验证
    if len(password) < 6:
        print("✗ 密码长度不能少于6位")
        return

    # 连接数据库
    db = await get_db_session()

    try:
        # 检查用户名是否已存在
        result = await db.execute(
            select(AdminUser).where(AdminUser.username == username)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"✗ 用户名 '{username}' 已存在")
            confirm = input("是否更新该用户密码? (y/n): ").strip().lower()
            if confirm != 'y':
                return

            # 更新密码
            existing_user.password_hash = hash_password(password)
            existing_user.real_name = real_name
            existing_user.email = email
            existing_user.phone = phone
            existing_user.status = 1
            await db.commit()

            print(f"✓ 管理员账户 '{username}' 更新成功")
        else:
            # 创建新用户
            admin_user = AdminUser(
                username=username,
                password_hash=hash_password(password),
                real_name=real_name,
                email=email,
                phone=phone,
                role=1,  # 超级管理员
                status=1
            )

            db.add(admin_user)
            await db.commit()

            print(f"✓ 管理员账户 '{username}' 创建成功")

        print("\n管理员信息:")
        print(f"  用户名: {username}")
        print(f"  真实姓名: {real_name}")
        print(f"  邮箱: {email or '未设置'}")
        print(f"  手机号: {phone or '未设置'}")
        print(f"  角色: 超级管理员")

    except Exception as e:
        print(f"✗ 创建管理员失败: {e}")
        await db.rollback()
    finally:
        await db.close()

    print("\n您现在可以使用以下API登录:")
    print(f"  POST http://localhost:8000/api/admin/auth/login")
    print(f"  {{'username': '{username}', 'password': '{password}'}}")


if __name__ == "__main__":
    asyncio.run(create_admin_user())
