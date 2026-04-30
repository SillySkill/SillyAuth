"""
Recommendations API Routes
推荐系统 API 路由
"""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from pydantic import BaseModel

from .services import RecommendationsService

router = APIRouter()

# 响应模型
class SkillResponse(BaseModel):
    """技能响应模型"""
    id: Optional[str] = None
    skill_index: Optional[int] = None
    skill_id: Optional[str] = None
    name: str
    description: str
    author: str
    version: str = "1.0.0"
    downloads: int = 0
    stars: int = 0
    tags: List[str] = []
    icon: str = "fa-code"
    category: str = "tech"
    download_url: Optional[str] = None
    source: str = "clawhub"  # 数据来源标识


class RecommendedSkillsResponse(BaseModel):
    """推荐技能列表响应"""
    skills: List[SkillResponse]
    total: int
    source: str = "clawhub"


class SyncResponse(BaseModel):
    """同步响应"""
    success: bool
    message: str
    stats: dict


class DownloadUrlResponse(BaseModel):
    """下载链接响应"""
    skill_index: int
    name: str
    download_url: str
    expires_in: int = 3600


# 创建服务实例
_service = RecommendationsService()


@router.get("/recommended", response_model=RecommendedSkillsResponse)
async def get_recommended_skills(
    locale: str = Query("zh-CN", description="语言设置: zh-CN, en-US"),
    limit: int = Query(10, ge=1, le=50, description="返回数量")
) -> RecommendedSkillsResponse:
    """
    获取推荐技能列表

    - 从 ClawHub API 获取热门技能
    - 支持中英文翻译
    - 返回推荐技能列表
    """
    skills = _service.get_recommended_skills(locale=locale, limit=limit)

    # 转换为响应模型
    skill_responses = []
    for i, skill in enumerate(skills):
        skill_responses.append(SkillResponse(
            id=f"clawhub-{i}",
            skill_index=skill.get("skill_index", i + 1),
            name=skill.get("name", ""),
            description=skill.get("description", ""),
            author=skill.get("author", "openclaw"),
            version=skill.get("version", "1.0.0"),
            downloads=skill.get("downloads", 0),
            stars=skill.get("stars", 0),
            tags=skill.get("tags", []),
            icon=skill.get("icon", "fa-code"),
            category=skill.get("category", "tech"),
            download_url=skill.get("download_url"),
            source="clawhub"
        ))

    return RecommendedSkillsResponse(
        skills=skill_responses,
        total=len(skill_responses),
        source="clawhub"
    )


@router.get("/trending", response_model=RecommendedSkillsResponse)
async def get_trending_skills(
    locale: str = Query("zh-CN", description="语言设置"),
    limit: int = Query(10, ge=1, le=50, description="返回数量")
) -> RecommendedSkillsResponse:
    """
    获取热门技能列表

    - 返回最受欢迎的技能
    - 按下载量和星级排序
    """
    skills = _service.get_trending_skills(limit=limit)

    # 翻译（如果需要中文）
    if locale == "zh-CN":
        skills = [_service.translate_to_chinese(s) for s in skills]

    skill_responses = []
    for i, skill in enumerate(skills):
        skill_responses.append(SkillResponse(
            id=f"trending-{i}",
            skill_index=skill.get("skill_index", i + 1),
            name=skill.get("name", ""),
            description=skill.get("description", ""),
            author=skill.get("author", "openclaw"),
            version=skill.get("version", "1.0.0"),
            downloads=skill.get("downloads", 0),
            stars=skill.get("stars", 0),
            tags=skill.get("tags", []),
            icon=skill.get("icon", "fa-code"),
            category=skill.get("category", "tech"),
            download_url=skill.get("download_url"),
            source="clawhub"
        ))

    return RecommendedSkillsResponse(
        skills=skill_responses,
        total=len(skill_responses),
        source="clawhub"
    )


@router.get("/latest", response_model=RecommendedSkillsResponse)
async def get_latest_skills(
    locale: str = Query("zh-CN", description="语言设置"),
    limit: int = Query(10, ge=1, le=50, description="返回数量")
) -> RecommendedSkillsResponse:
    """
    获取最新技能列表

    - 返回最新添加的技能
    """
    skills = _service.get_latest_skills(limit=limit)

    # 翻译（如果需要中文）
    if locale == "zh-CN":
        skills = [_service.translate_to_chinese(s) for s in skills]

    skill_responses = []
    for i, skill in enumerate(skills):
        skill_responses.append(SkillResponse(
            id=f"latest-{i}",
            skill_index=skill.get("skill_index", i + 1),
            name=skill.get("name", ""),
            description=skill.get("description", ""),
            author=skill.get("author", "openclaw"),
            version=skill.get("version", "1.0.0"),
            downloads=skill.get("downloads", 0),
            stars=skill.get("stars", 0),
            tags=skill.get("tags", []),
            icon=skill.get("icon", "fa-code"),
            category=skill.get("category", "tech"),
            download_url=skill.get("download_url"),
            source="clawhub"
        ))

    return RecommendedSkillsResponse(
        skills=skill_responses,
        total=len(skill_responses),
        source="clawhub"
    )


@router.post("/refresh", response_model=SyncResponse)
async def refresh_recommendations(background_tasks: BackgroundTasks):
    """
    手动刷新推荐数据 (Admin)

    - 强制从 ClawHub 重新获取数据
    - 更新数据库
    """
    try:
        # 执行同步
        stats = _service.sync_clawhub_skills()
        return SyncResponse(
            success=True,
            message=f"成功同步 {stats['total']} 个技能到数据库",
            stats=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新失败: {str(e)}")


@router.post("/sync", response_model=SyncResponse)
async def sync_to_tos():
    """
    同步技能到 TOS 存储 (Admin)

    - 将所有 ClawHub 技能上传到 TOS
    - 更新数据库中的 TOS 路径
    """
    try:
        # 获取所有技能
        result = _service.list_clawhub_skills(locale="en-US", limit=100, offset=0)
        skills = result.get("skills", [])

        uploaded = 0
        errors = []

        for skill in skills:
            try:
                skill_index = skill.get("skill_index")
                if skill_index:
                    tos_result = _service.upload_skill_to_tos(skill_index, skill)
                    if tos_result:
                        uploaded += 1
            except Exception as e:
                errors.append({"skill": skill.get("name"), "error": str(e)})

        return SyncResponse(
            success=True,
            message=f"成功上传 {uploaded} 个技能到 TOS",
            stats={
                "total": len(skills),
                "uploaded": uploaded,
                "errors": errors
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


@router.get("/download/{skill_index}", response_model=DownloadUrlResponse)
async def get_download_url(skill_index: int):
    """
    获取技能下载链接

    - 根据技能序号获取 TOS 签名下载链接
    - 链接有效期 1 小时
    """
    try:
        # 获取技能信息
        skill = _service.get_clawhub_skill_by_index(skill_index)
        if not skill:
            raise HTTPException(status_code=404, detail=f"技能 #{skill_index} 不存在")

        # 获取下载链接
        download_url = _service.get_clawhub_skill_download_url(skill_index)

        if not download_url:
            # 如果还没有上传到 TOS，先生成
            tos_result = _service.upload_skill_to_tos(skill_index, skill)
            if tos_result:
                download_url = tos_result["url"]
            else:
                raise HTTPException(status_code=503, detail="下载链接暂不可用，请稍后重试")

        return DownloadUrlResponse(
            skill_index=skill_index,
            name=skill.get("name", ""),
            download_url=download_url,
            expires_in=3600
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取下载链接失败: {str(e)}")


@router.get("/sources")
async def get_data_sources():
    """
    获取数据来源信息

    - 返回当前配置的外部数据源
    """
    return {
        "sources": [
            {
                "id": "clawhub",
                "name": "ClawHub",
                "url": _service.clawhub_base,
                "status": "active",
                "description": "官方技能市场"
            },
            {
                "id": "github",
                "name": "GitHub",
                "url": "https://github.com",
                "status": "planned",
                "description": "开源社区技能"
            }
        ]
    }


@router.get("/clawhub", response_model=RecommendedSkillsResponse)
async def get_clawhub_skills(
    locale: str = Query("zh-CN", description="语言设置"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量")
) -> RecommendedSkillsResponse:
    """
    获取 ClawHub 技能列表（从数据库）

    - 从数据库读取已同步的 ClawHub 技能
    - 支持分页
    """
    try:
        result = _service.list_clawhub_skills(
            locale=locale,
            limit=limit,
            offset=offset
        )

        skill_responses = []
        for skill in result.get("skills", []):
            skill_responses.append(SkillResponse(
                id=skill.get("skill_id"),
                skill_index=skill.get("skill_index"),
                name=skill.get("name", ""),
                description=skill.get("description", ""),
                author=skill.get("author", "openclaw"),
                version=skill.get("version", "1.0.0"),
                downloads=skill.get("downloads", 0),
                stars=skill.get("stars", 0),
                tags=skill.get("tags", []),
                icon=skill.get("icon", "fa-code"),
                category=skill.get("category", "tech"),
                download_url=skill.get("download_url"),
                source="clawhub"
            ))

        return RecommendedSkillsResponse(
            skills=skill_responses,
            total=result.get("total", 0),
            source="clawhub"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取 ClawHub 技能失败: {str(e)}")
