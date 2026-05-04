"""
库存管理外部对接接口

独立路由，供公司内部 ERP/进销存系统通过 REST API 对接。
同时 admin-v2 管理面板通过 /api/v1/store/admin 使用同一套 InventoryService。
"""

import logging
from fastapi import APIRouter, HTTPException, Query

from .inventory import InventoryService

logger = logging.getLogger(__name__)

# 外部对接接口 — 独立路由
external_router = APIRouter(prefix="/api/v1/inventory", tags=["inventory_external"])


# --- 库存查询 ---

@external_router.get("/products")
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: str = Query(None),
    low_stock_only: bool = Query(False),
    collection_key: str = Query(None),
):
    """[外部ERP] 获取产品库存列表（分页+筛选）"""
    return InventoryService.list_stock(
        page, page_size, search=search,
        low_stock_only=low_stock_only,
        collection_key=collection_key,
    )


@external_router.get("/products/key/{product_key}")
async def get_stock_by_key(product_key: str):
    """[外部ERP] 通过 product_key 查询库存"""
    return InventoryService.get_stock_by_key(product_key)


@external_router.get("/products/{product_id}")
async def get_stock(product_id: int):
    """[外部ERP] 查询单个产品库存"""
    try:
        return InventoryService.get_stock(product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# --- 库存调整 ---

@external_router.post("/stock/adjust")
async def adjust_stock(body: dict):
    """[外部ERP] 入库/出库/盘点（单条）"""
    try:
        if body.get('product_key'):
            return InventoryService.adjust_stock_by_key(
                body['product_key'], body['change_type'], body['quantity'],
                note=body.get('note'), reference_no=body.get('reference_no'),
                external_ref=body.get('external_ref'),
                source=body.get('source', 'external_api'),
                operator_name=body.get('operator_name'))
        else:
            return InventoryService.adjust_stock(
                body['product_id'], body['change_type'], body['quantity'],
                note=body.get('note'), reference_no=body.get('reference_no'),
                external_ref=body.get('external_ref'),
                source=body.get('source', 'external_api'),
                operator_name=body.get('operator_name'))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@external_router.post("/stock/batch-adjust")
async def batch_adjust_stock(body: dict):
    """[外部ERP] 批量库存调整"""
    return InventoryService.batch_adjust(body.get('items', []))


# --- 流水查询 ---

@external_router.get("/logs")
async def get_logs(
    product_id: int = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    change_type: str = Query(None),
    source: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    sync_status: str = Query(None),
):
    """[外部ERP] 库存流水查询（多条件筛选，对账用）"""
    return InventoryService.get_logs(
        product_id, page=page, page_size=page_size,
        change_type=change_type, source=source,
        start_date=start_date, end_date=end_date,
        sync_status=sync_status,
    )


# --- 同步状态 ---

@external_router.get("/logs/unsynced")
async def get_unsynced_logs(limit: int = Query(100, ge=1, le=1000)):
    """[外部ERP] 拉取未同步的流水记录（pull-model）"""
    return InventoryService.get_unsynced_logs(limit)


@external_router.put("/logs/sync-status")
async def mark_logs_synced(body: dict):
    """[外部ERP] 标记流水已同步到外部系统"""
    return InventoryService.mark_synced(
        body.get('log_ids', []), body.get('status', 'synced'))


# --- 健康检查 ---

@external_router.get("/health")
async def inventory_health():
    """[外部ERP] 进销存接口健康检查"""
    return {"status": "ok", "service": "sillymd-inventory", "version": "1.0.0"}
