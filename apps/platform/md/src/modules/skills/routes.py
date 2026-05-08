"""
Skills Module Routes
API endpoints for Skills management

Provides REST API endpoints for CRUD operations, publishing, and statistics
"""

import math
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from .schemas import (
    SkillCreate,
    SkillUpdate,
    SkillResponse,
    SkillListItem,
    SkillListResponse,
    CategoryResponse,
    CategoryInfo,
    SkillStats,
    AuthorInfo,
    PublishResponse,
    SkillStatsResponse,
    SkillVersionInfo,
)
from .services import skill_service

# Import auth dependencies
from core.db_adapter import get_db_cursor

# Auth imports from the auth module
from modules.auth.services import auth_service, SECRET_KEY, ALGORITHM
from jose import JWTError

def get_current_user():
    """Get current user from JWT - placeholder for now"""
    return {"id": 1, "username": "test", "role": "user"}

def get_current_admin():
    """Get current admin from JWT - placeholder for now"""
    return {"id": 1, "username": "admin", "role": "super_admin"}

def get_client_ip(request):
    """Get client IP from request"""
    if hasattr(request, 'client') and request.client:
        return request.client.host
    return "127.0.0.1"


class User:
    def __init__(self, id=1, username="user"):
        self.id = id
        self.username = username


HAS_AUTH = True

logger = __import__('logging').getLogger(__name__)

router = APIRouter(prefix="/api/v1/skills", tags=["Skills"])


# ============================================
# Helper Functions
# ============================================

def format_skill_response(skill: dict) -> SkillResponse:
    """Format skill dict to SkillResponse"""
    # Parse tags
    tags = []
    if skill.get('tags'):
        if isinstance(skill['tags'], str):
            tags = [t.strip() for t in skill['tags'].split(',') if t.strip()]
        elif isinstance(skill['tags'], list):
            tags = skill['tags']

    # Parse license_types
    license_types = None
    if skill.get('license_types'):
        if isinstance(skill['license_types'], str):
            import json
            try:
                license_types = json.loads(skill['license_types'])
            except Exception:
                license_types = None
        elif isinstance(skill['license_types'], list):
            license_types = skill['license_types']

    return SkillResponse(
        id=skill['id'],
        skill_id=skill['skill_id'],
        name=skill['name'],
        description=skill.get('description'),
        author=AuthorInfo(
            id=skill['author_id'],
            username=skill.get('author_username', 'unknown'),
            avatar_url=skill.get('author_avatar')
        ),
        category=skill['category'],
        type=skill['type'],
        version=skill['version'],
        status=skill['status'],
        tags=tags,
        stats=SkillStats(
            view_count=skill.get('view_count', 0),
            download_count=skill.get('download_count', 0),
            favorite_count=skill.get('favorite_count', 0),
            rating_avg=float(skill['rating_avg']) if skill.get('rating_avg') else 0.0,
            rating_count=skill.get('rating_count', 0)
        ),
        price=skill.get('price', 0),
        license_types=license_types,
        repo_url=skill.get('repo_url'),
        is_featured=skill.get('is_featured', False),
        published_at=skill.get('published_at'),
        created_at=skill['created_at'],
        updated_at=skill['updated_at']
    )


def format_skill_list_item(skill: dict) -> SkillListItem:
    """Format skill dict to SkillListItem"""
    tags = []
    if skill.get('tags'):
        if isinstance(skill['tags'], str):
            tags = [t.strip() for t in skill['tags'].split(',') if t.strip()]
        elif isinstance(skill['tags'], list):
            tags = skill['tags']

    # Use localized fields if available
    display_name = skill.get('display_name') or skill.get('name') or 'Unknown'
    display_description = skill.get('display_description') or skill.get('description')

    return SkillListItem(
        id=skill['id'],
        skill_id=skill['skill_id'],
        name=display_name,
        description=display_description,
        author=AuthorInfo(
            id=skill['author_id'],
            username=skill.get('author_username', 'unknown'),
            avatar_url=skill.get('author_avatar')
        ),
        category=skill['category'],
        type=skill['type'],
        version=skill['version'],
        tags=tags,
        stats=SkillStats(
            view_count=skill.get('view_count', 0),
            download_count=skill.get('download_count', 0),
            favorite_count=skill.get('favorite_count', 0),
            rating_avg=float(skill['rating_avg']) if skill.get('rating_avg') else 0.0,
            rating_count=skill.get('rating_count', 0)
        ),
        price=skill.get('price', 0),
        is_featured=skill.get('is_featured', False),
        published_at=skill.get('published_at'),
        created_at=skill['created_at']
    )


# ============================================
# Skills CRUD Endpoints
# ============================================

@router.get("", response_model=dict)
async def list_skills(
    category: Optional[str] = Query(None, description="Category filter"),
    tag: Optional[str] = Query(None, description="Tag filter"),
    search: Optional[str] = Query(None, description="Search keyword"),
    type: Optional[str] = Query(None, description="Type filter (free/commercial)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    lang: Optional[str] = Query("en", description="Language code (en/zh/ja/ko/de/ru)"),
):
    """
    List skills with filters and pagination

    Returns paginated list of skills with optional filtering by category, tag, search keyword, and type.
    Supports multilingual display based on the 'lang' parameter.
    """
    skills, total = skill_service.list_skills(
        category=category,
        tag=tag,
        search=search,
        type=type,
        page=page,
        limit=limit,
        lang=lang
    )

    total_pages = math.ceil(total / limit) if total > 0 else 1

    return {
        "success": True,
        "data": {
            "items": [format_skill_list_item(s) for s in skills],
            "total": total,
            "page": page,
            "page_size": limit,
            "total_pages": total_pages,
            "language": lang
        }
    }


@router.post("", response_model=dict)
async def create_skill(
    skill_data: SkillCreate,
    request: Request,
    current_user: User = Depends(get_current_user) if HAS_AUTH else None
):
    """
    Create a new skill

    Requires authentication. Creates a new skill with draft status.
    """
    if not current_user and HAS_AUTH:
        raise HTTPException(status_code=401, detail="需要登录才能创建 Skill")

    user_id = getattr(current_user, 'id', 1)  # Default to 1 for testing

    skill = skill_service.create_skill(
        author_id=user_id,
        data=skill_data.model_dump()
    )

    if not skill:
        raise HTTPException(status_code=400, detail="创建 Skill 失败")

    return {
        "success": True,
        "message": "Skill 创建成功",
        "data": format_skill_response(skill)
    }


@router.get("/{skill_id}", response_model=dict)
async def get_skill(
    skill_id: int,
    request: Request
):
    """
    Get skill details by ID

    Increments view count and returns full skill information.
    """
    skill = skill_service.get_skill_by_id(skill_id)

    if not skill:
        raise HTTPException(status_code=404, detail="Skill 不存在")

    # Increment view count
    skill_service.increment_view_count(skill_id)

    return {
        "success": True,
        "data": format_skill_response(skill)
    }


@router.put("/{skill_id}", response_model=dict)
async def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    request: Request,
    current_user: User = Depends(get_current_user) if HAS_AUTH else None
):
    """
    Update an existing skill

    Requires authentication and must be the skill author.
    """
    if not current_user and HAS_AUTH:
        raise HTTPException(status_code=401, detail="需要登录才能更新 Skill")

    user_id = getattr(current_user, 'id', 1)

    skill = skill_service.update_skill(
        skill_id=skill_id,
        author_id=user_id,
        data=skill_data.model_dump(exclude_unset=True)
    )

    if not skill:
        raise HTTPException(status_code=404, detail="Skill 不存在或无权限更新")

    return {
        "success": True,
        "message": "Skill 更新成功",
        "data": format_skill_response(skill)
    }


@router.delete("/{skill_id}", response_model=dict)
async def delete_skill(
    skill_id: int,
    request: Request,
    current_user: User = Depends(get_current_user) if HAS_AUTH else None
):
    """
    Delete a skill (soft delete)

    Requires authentication and must be the skill author.
    """
    if not current_user and HAS_AUTH:
        raise HTTPException(status_code=401, detail="需要登录才能删除 Skill")

    user_id = getattr(current_user, 'id', 1)

    success = skill_service.delete_skill(skill_id=skill_id, author_id=user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Skill 不存在或无权限删除")

    return {
        "success": True,
        "message": "Skill 删除成功"
    }


# ============================================
# Publish/Unpublish Endpoints
# ============================================

@router.post("/{skill_id}/publish", response_model=dict)
async def publish_skill(
    skill_id: int,
    request: Request,
    current_user: User = Depends(get_current_user) if HAS_AUTH else None
):
    """
    Publish a skill (submit for review)

    Requires authentication and must be the skill author.
    Changes skill status from 'draft' to 'reviewing'.
    """
    if not current_user and HAS_AUTH:
        raise HTTPException(status_code=401, detail="需要登录才能发布 Skill")

    user_id = getattr(current_user, 'id', 1)

    skill = skill_service.publish_skill(skill_id=skill_id, author_id=user_id)

    if not skill:
        raise HTTPException(status_code=400, detail="发布失败或无权操作")

    # 触发 skill2 后台扫描 + 打包
    try:
        from modules.skill2.services import skill2_service
        from core.config import get_skill2_config
        import asyncio
        asyncio.create_task(skill2_service.scan_skill_content(skill_id))
        if get_skill2_config().auto_package_on_publish:
            asyncio.create_task(skill2_service.process_full_pipeline(skill_id))
    except Exception:
        pass

    return {
        "success": True,
        "message": "Skill 已提交审核",
        "data": {
            "skill_id": skill['id'],
            "status": skill['status']
        }
    }


@router.post("/{skill_id}/unpublish", response_model=dict)
async def unpublish_skill(
    skill_id: int,
    request: Request,
    current_user: User = Depends(get_current_user) if HAS_AUTH else None
):
    """
    Unpublish a skill (revert to draft)

    Requires authentication and must be the skill author.
    Changes skill status from 'reviewing' back to 'draft'.
    """
    if not current_user and HAS_AUTH:
        raise HTTPException(status_code=401, detail="需要登录才能取消发布")

    user_id = getattr(current_user, 'id', 1)

    skill = skill_service.unpublish_skill(skill_id=skill_id, author_id=user_id)

    if not skill:
        raise HTTPException(status_code=400, detail="取消发布失败或无权操作")

    return {
        "success": True,
        "message": "Skill 已取消发布",
        "data": {
            "skill_id": skill['id'],
            "status": skill['status']
        }
    }


# ============================================
# Categories Endpoint
# ============================================

@router.get("/categories/list", response_model=dict)
async def get_categories():
    """
    Get all categories with skill counts

    Returns list of categories with their names and skill counts.
    """
    categories = skill_service.get_categories()

    category_list = [
        CategoryInfo(
            key=cat['key'],
            name=cat['name'],
            name_en=cat['name_en'],
            description=cat.get('description'),
            skill_count=cat.get('skill_count', 0)
        )
        for cat in categories
    ]

    return {
        "success": True,
        "data": {
            "categories": [c.model_dump() for c in category_list]
        }
    }


# ============================================
# Statistics Endpoint
# ============================================

@router.get("/{skill_id}/stats", response_model=dict)
async def get_skill_stats(skill_id: int):
    """
    Get skill statistics

    Returns view count, download count, favorite count, rating, and comment count.
    """
    stats = skill_service.get_skill_stats(skill_id)

    if not stats:
        raise HTTPException(status_code=404, detail="Skill 不存在")

    return {
        "success": True,
        "data": stats
    }


# ============================================
# Versions Endpoint
# ============================================

@router.get("/{skill_id}/versions", response_model=dict)
async def get_skill_versions(skill_id: int):
    """
    Get skill version history

    Returns list of all versions with their content hashes and commit messages.
    """
    skill = skill_service.get_skill_by_id(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill 不存在")

    versions = skill_service.get_skill_versions(skill_id)

    version_list = [
        SkillVersionInfo(
            version=v['version'],
            content=v.get('content', ''),
            content_hash=v['content_hash'],
            commit_message=v.get('commit_message'),
            created_at=v['created_at']
        )
        for v in versions
    ]

    return {
        "success": True,
        "data": {
            "versions": [v.model_dump() for v in version_list]
        }
    }


# ============================================
# Admin Endpoints
# ============================================

@router.post("/{skill_id}/approve", response_model=dict)
async def approve_skill(
    skill_id: int,
    request: Request,
    current_admin: User = Depends(get_current_admin) if HAS_AUTH else None
):
    """
    Approve a skill (admin only)

    Changes skill status from 'reviewing' to 'approved'.
    """
    if not current_admin and HAS_AUTH:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    try:
        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE skills
                SET status = 'approved',
                    published_at = COALESCE(published_at, CURRENT_TIMESTAMP),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND status = 'reviewing' AND is_deleted = FALSE
                RETURNING *
            """, (skill_id,))
            skill = cur.fetchone()

        if not skill:
            raise HTTPException(status_code=404, detail="Skill 不存在或不在审核状态")

        # 触发 skill2 后台打包（如尚未完成）
        try:
            from modules.skill2.services import skill2_service
            from core.config import get_skill2_config
            import asyncio
            if get_skill2_config().auto_package_on_publish:
                asyncio.create_task(skill2_service.process_full_pipeline(skill_id))
        except Exception:
            pass

        return {
            "success": True,
            "message": "Skill 审核通过",
            "data": {
                "skill_id": skill['id'],
                "status": skill['status']
            }
        }

    except Exception as e:
        logger.error(f"Failed to approve skill: {str(e)}")
        raise HTTPException(status_code=500, detail=f"审核失败: {str(e)}")


@router.post("/{skill_id}/reject", response_model=dict)
async def reject_skill(
    skill_id: int,
    request: Request,
    reason: str = Query(..., description="Rejection reason"),
    current_admin: User = Depends(get_current_admin) if HAS_AUTH else None
):
    """
    Reject a skill (admin only)

    Changes skill status from 'reviewing' to 'rejected'.
    """
    if not current_admin and HAS_AUTH:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    try:
        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE skills
                SET status = 'rejected', updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND status = 'reviewing' AND is_deleted = FALSE
                RETURNING *
            """, (skill_id,))
            skill = cur.fetchone()

        if not skill:
            raise HTTPException(status_code=404, detail="Skill 不存在或不在审核状态")

        # TODO: Create notification for author

        return {
            "success": True,
            "message": "Skill 已驳回",
            "data": {
                "skill_id": skill['id'],
                "status": skill['status'],
                "reason": reason
            }
        }

    except Exception as e:
        logger.error(f"Failed to reject skill: {str(e)}")
        raise HTTPException(status_code=500, detail=f"驳回失败: {str(e)}")


@router.post("/{skill_id}/feature", response_model=dict)
async def feature_skill(
    skill_id: int,
    request: Request,
    current_admin: User = Depends(get_current_admin) if HAS_AUTH else None
):
    """
    Mark/unmark skill as featured (admin only)

    Toggles the is_featured flag.
    """
    if not current_admin and HAS_AUTH:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    try:
        with get_db_cursor() as cur:
            # Get current status
            cur.execute("""
                SELECT is_featured FROM skills
                WHERE id = %s AND is_deleted = FALSE
            """, (skill_id,))
            skill = cur.fetchone()

            if not skill:
                raise HTTPException(status_code=404, detail="Skill 不存在")

            new_featured = not skill['is_featured']

            cur.execute("""
                UPDATE skills
                SET is_featured = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING *
            """, (new_featured, skill_id))

            return {
                "success": True,
                "message": f"Skill {'已设为精选' if new_featured else '已取消精选'}",
                "data": {
                    "skill_id": skill_id,
                    "is_featured": new_featured
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle featured: {str(e)}")
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


# ============================================
# Download Endpoint
# ============================================

@router.get("/{skill_id}/download", response_model=dict)
async def download_skill(skill_id: int):
    """
    获取技能下载链接

    返回技能的下载 URL，可以是 TOS 签名 URL 或源文件路径。
    """
    skill = skill_service.get_skill_by_id(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill 不存在")

    # 优先使用 demo_url
    if skill.get('demo_url'):
        return {
            "success": True,
            "data": {
                "url": skill['demo_url'],
                "type": "demo",
                "skill_id": skill['skill_id'],
                "name": skill['name']
            }
        }

    # 其次使用 source_path（本地文件）
    if skill.get('source_path'):
        # 返回本地文件路径供前端处理
        return {
            "success": True,
            "data": {
                "url": f"/api/skills/{skill_id}/source",
                "type": "local",
                "skill_id": skill['skill_id'],
                "name": skill['name']
            }
        }

    # 如果都没有，返回源仓库信息
    return {
        "success": True,
        "data": {
            "url": None,
            "type": "none",
            "skill_id": skill['skill_id'],
            "name": skill['name'],
            "message": "此技能暂无下载链接"
        }
    }


@router.get("/{skill_id}/source")
async def get_skill_source(skill_id: int):
    """
    获取技能源文件

    从 source_path 读取技能文件并返回。
    """
    skill = skill_service.get_skill_by_id(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill 不存在")

    source_path = skill.get('source_path')
    if not source_path:
        raise HTTPException(status_code=404, detail="此技能没有源文件")

    import os
    from fastapi.responses import FileResponse

    skill_md_path = os.path.join(source_path, 'SKILL.md')
    if os.path.exists(skill_md_path):
        # 返回 SKILL.md 文件
        return FileResponse(
            skill_md_path,
            media_type='text/markdown',
            filename=f"{skill['skill_id']}.md"
        )

    # 如果没有 SKILL.md，返回整个目录
    if os.path.isdir(source_path):
        import tempfile
        import zipfile

        # 创建临时 zip 文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_path)
                    zipf.write(file_path, arcname)

        return FileResponse(
            temp_file.name,
            media_type='application/zip',
            filename=f"{skill['skill_id']}.zip"
        )

    raise HTTPException(status_code=404, detail="未找到源文件")
