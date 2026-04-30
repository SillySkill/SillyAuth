"""
i18n API 路由

提供语言切换和翻译查询 API
"""

from fastapi import APIRouter, Cookie, Depends, Request
from typing import List, Optional

from .services import I18nService
from . import SUPPORTED_LANGUAGES, LANGUAGE_NAMES

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
    lang: str = "en",
    service: I18nService = Depends(get_i18n_service)
):
    """
    获取指定语言的翻译

    Query params:
        lang: 语言代码 (zh, en, ja, ko, de, ru)
    """
    if not service.is_supported(lang):
        lang = "en"

    return {
        "language": lang,
        "translations": service.get_all_translations(lang)
    }


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
