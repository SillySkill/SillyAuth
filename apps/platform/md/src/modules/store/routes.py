"""
Store API Routes
多产品线商城 API 路由

提供产品集合、购物车、订单、支付等功能
包含公共API和管理API两个路由器
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Request

from .schemas import (
    StoreCollection,
    StoreProductDetail,
    StoreCartItem,
    StoreOrder,
    StoreOrderItem,
    CartAddRequest,
    CreateOrderRequest,
    PaymentRequest,
    StoreCollectionCreate,
    StoreCollectionUpdate,
    StoreProductCreate,
    StoreProductUpdate,
    OrderStatusUpdate,
    StoreProductListResponse,
    StoreCollectionListResponse,
    StoreOrderDetailResponse,
    StoreOrderListResponse,
    StoreStats,
    CollectionStats,
    PaymentResponse,
    PaymentStatusResponse,
    CreateOrderResponse,
)
from .services import StoreService, AdminStoreService


# ==================== Public Router ====================

router = APIRouter(prefix="/api/v1/store", tags=["store"])

# ==================== Admin Router ====================

admin_router = APIRouter(prefix="/api/v1/store/admin", tags=["store_admin"])


# ==================== Collections API (Public) ====================

@router.get("/collections", response_model=List[StoreCollection])
async def get_collections():
    """获取所有活跃的商城集合"""
    try:
        result = StoreService.get_collections()
        return [StoreCollection(**item) for item in result]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections/{collection_key}", response_model=StoreCollection)
async def get_collection(collection_key: str):
    """获取指定集合详情"""
    try:
        result = StoreService.get_collection(collection_key)
        return StoreCollection(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections/{collection_key}/products", response_model=List[StoreProductDetail])
async def get_collection_products(
    collection_key: str,
    is_active: bool = Query(True, description="是否只返回上架商品")
):
    """获取指定集合的产品列表"""
    try:
        result = StoreService.get_collection_products(collection_key, is_active)
        return [StoreProductDetail(**item) for item in result]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Products API (Public) ====================

@router.get("/products/{product_id}", response_model=StoreProductDetail)
async def get_product_detail(product_id: int):
    """获取产品详情"""
    try:
        result = StoreService.get_product_detail(product_id)
        return StoreProductDetail(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Cart API (Public) ====================

@router.get("/cart", response_model=List[StoreCartItem])
async def get_cart(
    user_id: int = Query(..., description="用户ID"),
    collection_id: int = Query(..., description="集合ID")
):
    """获取用户购物车"""
    try:
        result = StoreService.get_cart(user_id, collection_id)
        return [StoreCartItem(**item) for item in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cart")
async def add_to_cart(
    cart_req: CartAddRequest,
    user_id: int = Query(..., description="用户ID"),
    collection_id: int = Query(..., description="集合ID")
):
    """添加到购物车"""
    try:
        result = StoreService.add_to_cart(user_id, collection_id, cart_req.product_id, cart_req.quantity)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/cart/{cart_id}")
async def update_cart_item(
    cart_id: int,
    quantity: int = Query(..., ge=1, le=99)
):
    """更新购物车项数量"""
    try:
        result = StoreService.update_cart_item(cart_id, quantity)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cart/{cart_id}")
async def remove_from_cart(cart_id: int):
    """从购物车移除"""
    try:
        result = StoreService.remove_from_cart(cart_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cart")
async def clear_cart(
    user_id: int = Query(..., description="用户ID"),
    collection_id: int = Query(..., description="集合ID")
):
    """清空购物车"""
    try:
        result = StoreService.clear_cart(user_id, collection_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Orders API (Public) ====================

@router.post("/orders")
async def create_order(
    order_req: CreateOrderRequest,
    user_id: int = Query(..., description="用户ID"),
    collection_id: int = Query(..., description="集合ID")
):
    """创建订单"""
    try:
        result = StoreService.create_order(
            user_id=user_id,
            collection_id=collection_id,
            shipping_name=order_req.shipping_name,
            shipping_phone=order_req.shipping_phone,
            shipping_address=order_req.shipping_address
        )
        return CreateOrderResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders", response_model=List[StoreOrder])
async def get_user_orders(
    user_id: int = Query(..., description="用户ID"),
    collection_id: Optional[int] = Query(None, description="集合ID筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """获取用户订单列表"""
    try:
        result = StoreService.get_user_orders(user_id, collection_id, status, limit, offset)
        return [StoreOrder(**item) for item in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/{order_no}", response_model=StoreOrder)
async def get_order_detail(order_no: str):
    """获取订单详情"""
    try:
        result = StoreService.get_order_detail(order_no)
        return StoreOrder(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/{order_no}/items", response_model=List[StoreOrderItem])
async def get_order_items(order_no: str):
    """获取订单商品列表"""
    try:
        result = StoreService.get_order_items(order_no)
        return [StoreOrderItem(**item) for item in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Payment API (Public) ====================

@router.post("/orders/{order_no}/pay")
async def initiate_payment(
    order_no: str,
    pay_req: PaymentRequest
):
    """发起支付"""
    try:
        result = StoreService.initiate_payment(order_no, pay_req.payment_method)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Payment Callbacks (Public) ====================

@router.post("/callback/wechat")
async def wechat_payment_callback(request: Request):
    """微信支付回调 - 解析XML通知并更新订单状态"""
    import xml.etree.ElementTree as ET

    try:
        body = await request.body()
        root = ET.fromstring(body)
        data = {child.tag: child.text for child in root}

        result = StoreService.wechat_callback(data)
        return result
    except Exception as e:
        return {"return_code": "FAIL", "return_msg": str(e)}


@router.post("/callback/alipay")
async def alipay_payment_callback(request: Request):
    """支付宝支付回调 - 解析表单数据并更新订单状态"""
    try:
        form_data = await request.form()
        data = {key: value for key, value in form_data.items()}

        result = StoreService.alipay_callback(data)
        return result
    except Exception as e:
        return "fail"


@router.get("/orders/{order_no}/status")
async def check_payment_status(order_no: str):
    """检查支付状态"""
    try:
        result = StoreService.check_payment_status(order_no)
        return PaymentStatusResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Stats API (Public) ====================

@router.get("/stats/collection/{collection_id}")
async def get_collection_stats(collection_id: int):
    """获取集合统计"""
    try:
        result = StoreService.get_collection_stats(collection_id)
        return CollectionStats(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Admin Collections API ====================

@admin_router.get("/collections", response_model=StoreCollectionListResponse)
async def admin_list_collections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, description="搜索名称或key")
):
    """获取所有商城集合（管理端）"""
    try:
        result = AdminStoreService.list_collections(page, page_size, is_active, search)
        return StoreCollectionListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.post("/collections", response_model=StoreCollection, status_code=201)
async def admin_create_collection(collection: StoreCollectionCreate):
    """创建商城集合（管理端）"""
    try:
        data = collection.model_dump()
        result = AdminStoreService.create_collection(data)
        return StoreCollection(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.put("/collections/{collection_id}", response_model=StoreCollection)
async def admin_update_collection(collection_id: int, collection: StoreCollectionUpdate):
    """更新商城集合（管理端）"""
    try:
        data = collection.model_dump(exclude_unset=True)
        result = AdminStoreService.update_collection(collection_id, data)
        return StoreCollection(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.delete("/collections/{collection_id}")
async def admin_delete_collection(collection_id: int):
    """删除商城集合（管理端）- 软删除"""
    try:
        result = AdminStoreService.delete_collection(collection_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Admin Products API ====================

@admin_router.get("/products", response_model=StoreProductListResponse)
async def admin_list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    collection_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, description="搜索名称或key"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort_by: Optional[str] = Query("created_at", description="排序字段: created_at, price, sort_order"),
    sort_order: Optional[str] = Query("desc", description="排序方向: asc, desc")
):
    """获取所有产品（管理端）"""
    try:
        result = AdminStoreService.list_products(
            page=page,
            page_size=page_size,
            collection_id=collection_id,
            is_active=is_active,
            search=search,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return StoreProductListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.get("/products/{product_id}", response_model=StoreProductDetail)
async def admin_get_product(product_id: int):
    """获取产品详情（管理端）"""
    try:
        result = AdminStoreService.get_product(product_id)
        return StoreProductDetail(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.post("/products", response_model=StoreProductDetail, status_code=201)
async def admin_create_product(product: StoreProductCreate):
    """创建产品（管理端）"""
    try:
        data = product.model_dump()
        result = AdminStoreService.create_product(data)
        return StoreProductDetail(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.put("/products/{product_id}", response_model=StoreProductDetail)
async def admin_update_product(product_id: int, product: StoreProductUpdate):
    """更新产品（管理端）"""
    try:
        data = product.model_dump(exclude_unset=True)
        result = AdminStoreService.update_product(product_id, data)
        return StoreProductDetail(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.delete("/products/{product_id}")
async def admin_delete_product(product_id: int):
    """删除产品（管理端）- 软删除"""
    try:
        result = AdminStoreService.delete_product(product_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Admin Orders API ====================

@admin_router.get("/orders")
async def admin_list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    collection_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None, description="pending, paid, shipped, completed, cancelled"),
    user_id: Optional[int] = Query(None),
    order_no: Optional[str] = Query(None, description="订单号模糊搜索"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD")
):
    """获取所有订单（管理端）"""
    try:
        result = AdminStoreService.list_orders(
            page=page,
            page_size=page_size,
            collection_id=collection_id,
            status=status,
            user_id=user_id,
            order_no=order_no,
            start_date=start_date,
            end_date=end_date
        )
        return StoreOrderListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.get("/orders/{order_no}/detail")
async def admin_get_order_detail(order_no: str):
    """获取订单详情（管理端，含订单项）"""
    try:
        result = AdminStoreService.get_order_detail(order_no)
        return StoreOrderDetailResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.put("/orders/{order_no}/status")
async def admin_update_order_status(order_no: str, status_update: OrderStatusUpdate):
    """更新订单状态（管理端）"""
    try:
        result = AdminStoreService.update_order_status(order_no, status_update.status)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Admin Stats API ====================

@admin_router.get("/stats")
async def admin_get_store_stats():
    """获取商城统计（管理端）"""
    try:
        result = AdminStoreService.get_store_stats()
        return StoreStats(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
