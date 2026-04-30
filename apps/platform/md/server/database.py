"""
数据库连接和核心服务模块
====================================

版本: v1.0
创建日期: 2026-02-12
说明: 提供数据库连接和基础功能
"""

import asyncpg
from databases import get_db
from models import User, GenerationTask
from typing import Optional, List


# ============================================================================
# 数据库连接
# ============================================================================

async def get_user_by_openid(openid: str) -> Optional[dict]:
    """通过openid获取用户"""
    conn = await get_db()
    try:
        query = """
            SELECT id, openid, unionid, nickname, avatar_url, phone, status
            FROM users
            WHERE openid = $1
        """
        result = await conn.fetchrow(query, openid)
        if result:
            return {
                "id": result[0],
                "openid": result[1],
                "unionid": result[2],
                "nickname": result[3],
                "avatar_url": result[4],
                "phone": result[5],
                "status": result[6]
            }
    finally:
        await conn.close()
    return None


async def get_or_create_user(openid: str, unionid: Optional[str] = None,
                         nickname: Optional[str] = None,
                         avatar_url: Optional[str] = None) -> dict:
    """获取或创建用户（支持百变秀临时用户）"""
    user = await get_user_by_openid(openid)

    if user:
        return user

    # 创建新用户
    conn = await get_db()
    try:
        query = """
            INSERT INTO users (openid, unionid, nickname, avatar_url, status, created_at)
            VALUES ($1, $2, $3, $4, 1, CURRENT_TIMESTAMP)
            RETURNING id, openid, unionid, nickname, avatar_url
        """
        if unionid:
            params = (unionid, unionid, nickname, avatar_url)
        else:
            # 百变秀场景：临时用户
            params = (openid, "", nickname or "扫码用户", avatar_url)

        result = await conn.fetchrow(query, *params)
        await conn.close()

        return {
            "id": result[0],
            "openid": result[1],
            "unionid": result[2],
            "nickname": result[3],
            "avatar_url": result[4]
        }


async def create_generation_task(
    style_id: int,
    original_image_url: str,
    scene_type: str,
    user_id: Optional[int] = None,
    activity_id: Optional[int] = None,
    uploader_name: Optional[str] = None
) -> dict:
    """创建AI生成任务"""
    conn = await get_db()
    try:
        # 生成任务ID
        task_id = f"TASK_{scene_type}_{os.urandom(16)}"

        query = """
            INSERT INTO one_generation_tasks
                (task_id, scene_type, user_id, activity_id, uploader_name,
                 style_id, original_image_url, original_image_tos_url,
                 status, progress, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, '', '',
                     0, 0, CURRENT_TIMESTAMP)
            RETURNING id, task_id, scene_type
        """

        params = (task_id, scene_type, user_id, activity_id, uploader_name,
                   style_id, original_image_url, original_image_tos_url)

        result = await conn.fetchrow(query, *params)
        await conn.close()

        return {
            "task_id": result[0],
            "scene_type": result[1],
            "status": "processing",
            "qr_code_url": f"/api/generate/upload?task_id={result[0]}"
        }


async def update_generation_task(task_id: str, status: str, **kwargs) -> bool:
    """更新生成任务状态"""
    conn = await get_db()
    try:
        set_parts = []
        set_values = []

        for key, value in kwargs.items():
            if key == "progress":
                set_parts.append(f"progress = {value}")
            elif key == "result_image_url":
                set_parts.append(f"result_image_url = '{value}'")
            elif key == "error_message":
                set_parts.append(f"error_message = '{value}'")

        set_clause = ", ".join(set_parts) if set_parts else "1=1"

        query = f"""
            UPDATE one_generation_tasks
            SET {set_clause}
            WHERE task_id = $1
        """

        await conn.execute(query, task_id)
        await conn.close()
        return True


async def get_user_balance(user_id: int, scene_type: str) -> dict:
    """获取用户余额"""
    conn = await get_db()
    try:
        query = """
            SELECT user_id, growth_points, image_points, video_points, total_recharged, total_discount
            FROM one_user_balance
            WHERE user_id = $1 AND scene_type = $2
        """
        result = await conn.fetchrow(query, user_id, scene_type)
        await conn.close()

        return {
            "user_id": result[0],
            "scene_type": result[1],
            "growth_points": result[2] if result[2] else 0,
            "image_points": result[3] if result[3] else 0,
            "video_points": result[4] if result[4] else 0,
            "total_recharged": float(result[5]) if result[5] else 0,
            "total_discount": float(result[6]) if result[6] else 0,
        }


async def consume_points(user_id: int, points: int, scene_type: str) -> dict:
    """扣减成长分"""
    conn = await get_db()
    try:
        # 获取当前余额
        balance = await get_user_balance(user_id, scene_type)
        if not balance:
            raise HTTPException(status_code=400, detail="用户余额不存在")

        points_before = balance["growth_points"]

        if points_before < points:
            raise HTTPException(status_code=400, detail="余额不足")

        # 更新余额
        await update_user_balance(user_id, scene_type,
                              points_before - points,
                              points_before - points,
                              points_before - points)

        # 记录变更日志
        # TODO: 添加余额变更日志

        return {
            "points_consumed": points,
            "points_before": points_before,
            "points_after": points_before - points
        }
    finally:
        pass


async def update_user_balance(user_id: int, scene_type: str,
                            image_points: int = 0, video_points: int = 0,
                            growth_points: int = 0) -> bool:
    """更新用户余额"""
    conn = await get_db()
    try:
        query = """
            UPDATE one_user_balance
            SET growth_points = growth_points + $1,
                image_points = image_points + $2,
                video_points = video_points + $3,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = $4 AND scene_type = $5
        """

        await conn.execute(query, growth_points, image_points, video_points, user_id, scene_type)
        await conn.close()
        return True
    except Exception as e:
        print(f"更新余额失败: {str(e)}")
        return False
