"""
i18n API 路由

提供语言切换和翻译查询 API
"""

import logging
from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request
from typing import List, Optional

from .services import I18nService
from . import SUPPORTED_LANGUAGES, LANGUAGE_NAMES

logger = logging.getLogger(__name__)

router = APIRouter()


def get_i18n_service() -> I18nService:
    """获取 i18n 服务实例"""
    from .. import i18n as i18n_module
    if i18n_module.service:
        return i18n_module.service
    # 如果模块未初始化，返回默认服务
    return I18nService()


@router.get("/languages")
async def get_supported_languages():
    """获取支持的语言列表"""
    service = get_i18n_service()
    return {
        "languages": service.get_supported_languages(),
        "default": "en"
    }


@router.get("/translations")
async def get_translations(
    request: Request,
    lang: str = "en",
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    key: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    service: I18nService = Depends(get_i18n_service)
):
    """
    获取翻译

    两种模式:
    1. 公开模式 (无 page 参数): 返回指定语言的 locale JSON 翻译
       - lang: 语言代码 (zh, en, ja, ko, de, ru)

    2. 管理端模式 (有 page 参数): 返回 DB 中管理的翻译条目（分页）
       - page: 页码
       - page_size: 每页数量
       - key: 搜索键名
       - module: 按模块筛选
    """
    # 检测是否为管理端请求（有 page 参数）
    if page is not None:
        return await _admin_list_translations(page, page_size, key, module)

    # 公开模式：返回 locale JSON 翻译
    if not service.is_supported(lang):
        lang = "en"

    return {
        "language": lang,
        "translations": service.get_all_translations(lang)
    }


async def _admin_list_translations(
    page: int = 1,
    page_size: int = 20,
    key: Optional[str] = None,
    module: Optional[str] = None,
):
    """List translations with pagination and search/filter (admin)."""
    _ensure_translations_table()
    try:
        from core.db_adapter import get_db_cursor
        conditions = []
        params = []
        if key:
            conditions.append("key ILIKE %s")
            params.append(f"%{key}%")
        if module:
            conditions.append("module = %s")
            params.append(module)

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        count_sql = f"SELECT COUNT(*) as cnt FROM i18n_translations {where}"
        data_sql = f"SELECT id, key, zh_CN, en, module, created_at FROM i18n_translations {where} ORDER BY id ASC LIMIT %s OFFSET %s"

        with get_db_cursor() as cur:
            cur.execute(count_sql, params)
            total = cur.fetchone()["cnt"]

            data_params = params + [page_size, (page - 1) * page_size]
            cur.execute(data_sql, data_params)
            rows = cur.fetchall()

        return {
            "success": True,
            "data": {
                "items": rows,
                "total": total,
                "page": page,
                "page_size": page_size,
            }
        }
    except Exception as e:
        logger.error(f"Failed to list translations: {e}")
        return {"success": True, "data": {"items": [], "total": 0, "page": page, "page_size": page_size}}


@router.get("/translate")
async def translate_key(
    key: str,
    lang: str = "en",
    service: I18nService = Depends(get_i18n_service)
):
    """
    翻译单个键

    Query params:
        key: 翻译键 (e.g., "skills.title")
        lang: 语言代码
    """
    if not service.is_supported(lang):
        lang = "en"

    return {
        "key": key,
        "language": lang,
        "translation": service.t(lang, key)
    }


@router.post("/translate/batch")
async def translate_batch(
    keys: List[str],
    lang: str = "en",
    service: I18nService = Depends(get_i18n_service)
):
    """
    批量翻译

    Body:
        keys: 翻译键列表
        lang: 语言代码
    """
    if not service.is_supported(lang):
        lang = "en"

    return {
        "language": lang,
        "translations": service.translate(lang, keys)
    }


@router.get("/detect")
async def detect_language(request: Request):
    """
    检测用户语言

    从 URL 参数、Cookie、请求头等检测最佳语言
    """
    service = get_i18n_service()

    # 从查询参数获取
    query_lang = request.query_params.get('lang')

    # 从 Cookie 获取
    cookie_lang = request.cookies.get('locale')

    # 从 Accept-Language 头获取
    accept_lang = request.headers.get('accept-language')

    # 检测语言
    detected = service.detect_language(
        query_param=query_lang,
        cookie=cookie_lang,
        accept_language=accept_lang
    )

    return {
        "detected": detected,
        "name": LANGUAGE_NAMES.get(detected, detected),
        "all_supported": SUPPORTED_LANGUAGES
    }


@router.post("/set-language")
async def set_language(lang: str):
    """
    设置用户语言 (返回设置指令)

    Query params:
        lang: 语言代码
    """
    if lang not in SUPPORTED_LANGUAGES:
        return {"error": f"Unsupported language: {lang}"}

    return {
        "success": True,
        "language": lang,
        "name": LANGUAGE_NAMES.get(lang, lang),
        "message": f"Language set to {LANGUAGE_NAMES.get(lang, lang)}"
    }


# ============================================================================
# Admin Translation Management
# ============================================================================


def _ensure_translations_table():
    """Create i18n_translations table if it doesn't exist."""
    from core.db_adapter import get_db_cursor
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS i18n_translations (
                    id SERIAL PRIMARY KEY,
                    key VARCHAR(255) NOT NULL UNIQUE,
                    zh_CN TEXT NOT NULL DEFAULT '',
                    en TEXT NOT NULL DEFAULT '',
                    module VARCHAR(100) NOT NULL DEFAULT 'common',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
    except Exception as e:
        logger.error(f"Failed to ensure translations table: {e}")


@router.post("/translations")
async def create_translation(data: dict):
    """Create a new translation entry."""
    _ensure_translations_table()
    key = data.get("key", "").strip()
    if not key:
        raise HTTPException(status_code=400, detail="key is required")
    try:
        from core.db_adapter import get_db_cursor
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO i18n_translations (key, zh_CN, en, module) VALUES (%s, %s, %s, %s) RETURNING id, key, zh_CN, en, module, created_at",
                (key, data.get("zh_CN", ""), data.get("en", ""), data.get("module", "common"))
            )
            row = cur.fetchone()
        return {"success": True, "data": row}
    except Exception as e:
        logger.error(f"Failed to create translation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/translations/{translation_id}")
async def update_translation(translation_id: int, data: dict):
    """Update a translation entry."""
    _ensure_translations_table()
    try:
        from core.db_adapter import get_db_cursor
        sets = []
        params = []
        for field in ["key", "zh_CN", "en", "module"]:
            if field in data:
                sets.append(f"{field} = %s")
                params.append(data[field])
        if not sets:
            raise HTTPException(status_code=400, detail="No fields to update")
        sets.append("updated_at = NOW()")
        params.append(translation_id)

        with get_db_cursor() as cur:
            cur.execute(
                f"UPDATE i18n_translations SET {', '.join(sets)} WHERE id = %s RETURNING id, key, zh_CN, en, module, created_at",
                params
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Translation not found")
        return {"success": True, "data": row}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update translation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/translations/{translation_id}")
async def delete_translation(translation_id: int):
    """Delete a translation entry."""
    _ensure_translations_table()
    try:
        from core.db_adapter import get_db_cursor
        with get_db_cursor() as cur:
            cur.execute("DELETE FROM i18n_translations WHERE id = %s", (translation_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Translation not found")
        return {"success": True, "message": "翻译删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete translation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
