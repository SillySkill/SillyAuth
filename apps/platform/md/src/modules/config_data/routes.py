from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from .schemas import ConfigDataCreate, ConfigDataUpdate, ConfigDataResponse, ConfigDataListResponse
from .services import config_data_service


class BatchUpdateItem(BaseModel):
    name: str
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    data: Optional[dict] = None


class BatchUpdateRequest(BaseModel):
    category: str
    items: List[BatchUpdateItem]

router = APIRouter(prefix="/api/v1/config-data", tags=["ConfigData"])


@router.get("/list/{category}", response_model=dict)
async def list_by_category(
    category: str,
):
    """
    按分类获取所有配置数据
    - category: 分类标识
    """
    try:
        items, total = await config_data_service.list_by_category(category)
        return {
            "success": True,
            "data": {
                "items": [ConfigDataResponse.model_validate(item) for item in items],
                "total": total
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/item/{category}/{name}", response_model=dict)
async def get_by_name(
    category: str,
    name: str,
):
    """按分类和名称获取单个配置数据"""
    data = await config_data_service.get_by_name(category, name)
    if not data:
        raise HTTPException(status_code=404, detail="数据不存在")
    return {
        "success": True,
        "data": ConfigDataResponse.model_validate(data)
    }


@router.post("", response_model=dict)
async def create(data: ConfigDataCreate):
    """创建配置数据"""
    try:
        result = await config_data_service.create(data.model_dump())
        return {
            "success": True,
            "data": ConfigDataResponse.model_validate(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{category}/{name}", response_model=dict)
async def update(
    category: str,
    name: str,
    data: ConfigDataUpdate,
):
    """更新配置数据"""
    try:
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        result = await config_data_service.update(category, name, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="数据不存在")
        return {
            "success": True,
            "data": ConfigDataResponse.model_validate(result)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{category}/{name}", response_model=dict)
async def delete(category: str, name: str):
    """删除配置数据"""
    success = await config_data_service.delete(category, name)
    if not success:
        raise HTTPException(status_code=404, detail="数据不存在")
    return {"success": True, "message": "删除成功"}


@router.post("/batch-update", response_model=dict)
async def batch_update(data: BatchUpdateRequest):
    """批量更新配置数据（用于拖拽保存坐标）"""
    try:
        items_dict = [item.model_dump() for item in data.items]
        updated_count = await config_data_service.batch_update(data.category, items_dict)
        return {
            "success": True,
            "message": f"成功更新 {updated_count} 条数据",
            "updated_count": updated_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
