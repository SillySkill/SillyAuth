"""
分销系统API路由
提供分销员工管理、分享链接、订单追踪、佣金统计等功能
"""

import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .schemas import (
    # Staff
    StaffCreate,
    StaffUpdate,
    StaffResponse,
    StaffStats,
    # Link
    LinkCreate,
    LinkResponse,
    LinkStats,
    # Order
    OrderAssignRequest,
    OrderResponse,
    OrderListResponse,
    # Visit
    VisitTrackRequest,
    VisitResponse,
    # Commission
    CommissionResponse,
    CommissionListResponse,
    # Leaderboard
    LeaderboardEntry,
    LeaderboardResponse,
    # Stats
    GlobalStats,
)
from .services import (
    StaffService,
    LinkService,
    VisitService,
    OrderService,
    CommissionService,
    LeaderboardService,
    StatsService,
    init_tables,
)


router = APIRouter(prefix="/api/v1/affiliate", tags=["分销系统"])


# ==================== 初始化 ====================

@router.on_event("startup")
async def startup_event():
    """初始化数据库表"""
    init_tables()


# ==================== 员工管理 ====================

@router.get("/staffs", response_model=List[StaffResponse])
async def list_staffs(
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(50, ge=1, le=100, description="每页数量")
):
    """
    获取分销员工列表
    """
    try:
        staffs = StaffService.list_staffs(status, page, limit)
        return [StaffResponse(**s) for s in staffs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/staffs", response_model=StaffResponse)
async def create_staff(staff: StaffCreate):
    """
    创建分销员工

    - user_id: 关联的用户ID
    - staff_name: 员工姓名
    - staff_code: 员工编码（可选，自动生成）
    """
    try:
        result = StaffService.create_staff(
            user_id=staff.user_id,
            staff_name=staff.staff_name,
            staff_code=staff.staff_code
        )
        return StaffResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/staffs/me", response_model=StaffResponse)
async def get_my_staff_info(user_id: int = Query(..., description="用户ID")):
    """
    获取当前用户的分销员工信息
    """
    try:
        staff = StaffService.get_staff_by_user_id(user_id)
        if not staff:
            raise HTTPException(status_code=404, detail="不是分销员工")
        return StaffResponse(**staff)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/staffs/{staff_id}", response_model=StaffResponse)
async def get_staff(staff_id: int):
    """
    获取分销员工详情
    """
    try:
        staff = StaffService.get_staff(staff_id)
        if not staff:
            raise HTTPException(status_code=404, detail="员工不存在")
        return StaffResponse(**staff)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/staffs/{staff_id}", response_model=StaffResponse)
async def update_staff(staff_id: int, staff: StaffUpdate):
    """
    更新分销员工信息
    """
    try:
        result = StaffService.update_staff(
            staff_id=staff_id,
            staff_name=staff.staff_name,
            status=staff.status.value if staff.status else None
        )
        if not result:
            raise HTTPException(status_code=404, detail="员工不存在")
        return StaffResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/staffs/{staff_id}/stats", response_model=StaffStats)
async def get_staff_stats(
    staff_id: int,
    period: str = Query("all", description="统计周期: today, week, month, all")
):
    """
    获取员工统计数据

    - staff_id: 员工ID
    - period: 统计周期 (today/week/month/all)
    """
    try:
        stats = StaffService.get_staff_stats(staff_id, period)
        return StaffStats(**stats)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 分享链接管理 ====================

@router.post("/links", response_model=LinkResponse)
async def create_link(link: LinkCreate):
    """
    生成分享链接

    - staff_id: 员工ID
    - product_id: 商品ID（可选）
    - expires_in_days: 有效期天数（可选，默认365天）
    """
    try:
        result = LinkService.create_affiliate_link(
            staff_id=link.staff_id,
            product_id=link.product_id,
            expires_in_days=link.expires_in_days
        )
        return LinkResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/links", response_model=List[LinkResponse])
async def list_links(
    staff_id: Optional[int] = Query(None, description="员工ID筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(50, ge=1, le=100, description="每页数量")
):
    """
    获取分享链接列表
    """
    try:
        links = LinkService.list_links(staff_id, status, page, limit)
        return [LinkResponse(**l) for l in links]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/links/{code}", response_model=LinkResponse)
async def get_link(code: str):
    """
    获取链接详情
    """
    try:
        link = LinkService.get_link_by_code(code)
        if not link:
            raise HTTPException(status_code=404, detail="链接不存在")
        return LinkResponse(**link)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/links/{code}/stats", response_model=LinkStats)
async def get_link_stats(code: str):
    """
    获取链接统计数据
    """
    try:
        stats = LinkService.get_link_stats(code)
        return LinkStats(**stats)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 访问追踪 ====================

@router.post("/track", response_model=VisitResponse)
async def track_visit(track: VisitTrackRequest, request: Request):
    """
    记录访问

    - link_code: 分享链接码
    - visitor_id: 访客ID（可选）
    - source: 来源（可选）
    - referrer: 来源页面（可选）
    """
    try:
        # 获取客户端信息
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        result = VisitService.track_visit(
            link_code=track.link_code,
            visitor_id=track.visitor_id,
            source=track.source,
            referrer=track.referrer,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return VisitResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 短链接重定向 ====================

@router.get("/r/{code}")
async def redirect_short_link(code: str):
    """
    短链接重定向

    访问 /r/{code} 会重定向到完整的分享链接
    """
    try:
        link = LinkService.get_link_by_code(code)
        if not link:
            raise HTTPException(status_code=404, detail="链接不存在")

        if link['status'] != 'active':
            raise HTTPException(status_code=400, detail="链接已失效")

        if link['expires_at'] and link['expires_at'] < datetime.now():
            raise HTTPException(status_code=400, detail="链接已过期")

        # 增加点击数
        LinkService.increment_click_count(code)

        # 重定向到完整URL
        if link['product_id']:
            redirect_url = f"/openclaw/product/{link['product_id']}?ref={code}"
        else:
            redirect_url = f"/openclaw?ref={code}"

        return RedirectResponse(url=redirect_url, status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 订单归属 ====================

@router.post("/orders/assign", response_model=OrderResponse)
async def assign_order(order: OrderAssignRequest):
    """
    订单归属

    将订单归属给通过分享链接访问的用户

    - order_id: 订单ID
    - link_code: 分享链接码
    - product_id: 商品ID（可选）
    - amount: 订单金额
    """
    try:
        result = OrderService.assign_order_to_staff(
            order_id=order.order_id,
            link_code=order.link_code,
            product_id=order.product_id,
            amount=order.amount
        )
        return OrderResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orders/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order(order_id: int):
    """
    确认订单

    确认订单后，佣金将计入员工账户
    """
    try:
        result = OrderService.confirm_order(order_id)
        return OrderResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: int):
    """
    取消订单

    取消订单后，如果已确认将回退佣金
    """
    try:
        OrderService.cancel_order(order_id)
        return {"success": True, "message": "订单已取消"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders", response_model=OrderListResponse)
async def list_orders(
    staff_id: Optional[int] = Query(None, description="员工ID筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(50, ge=1, le=100, description="每页数量")
):
    """
    获取分销订单列表
    """
    try:
        result = OrderService.list_orders(staff_id, status, page, limit)
        return OrderListResponse(
            orders=[OrderResponse(**o) for o in result['orders']],
            total=result['total'],
            page=result['page'],
            limit=result['limit']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 排行榜 ====================

@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = Query(50, ge=1, le=100, description="返回数量"),
    period: str = Query("all", description="统计周期: today/week/month/all")
):
    """
    获取业绩排行榜

    - limit: 返回数量
    - period: 统计周期
    """
    try:
        result = LeaderboardService.get_leaderboard(limit, period)
        return LeaderboardResponse(
            entries=[LeaderboardEntry(**e) for e in result['entries']],
            period=result['period'],
            total_staffs=result['total_staffs']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 佣金管理 ====================

@router.get("/commissions", response_model=CommissionListResponse)
async def list_commissions(
    staff_id: Optional[int] = Query(None, description="员工ID筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(50, ge=1, le=100, description="每页数量")
):
    """
    获取佣金列表
    """
    try:
        result = CommissionService.list_commissions(staff_id, status, page, limit)
        return CommissionListResponse(
            commissions=[CommissionResponse(**c) for c in result['commissions']],
            total=result['total'],
            pending=result['pending'],
            confirmed=result['confirmed'],
            paid=result['paid']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/commissions/{commission_id}/pay", response_model=CommissionResponse)
async def pay_commission(commission_id: int):
    """
    支付佣金
    """
    try:
        result = CommissionService.pay_commission(commission_id)
        return CommissionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 管理后台统计 ====================

@router.get("/admin/stats", response_model=GlobalStats)
async def get_global_stats():
    """
    获取全局统计数据（管理员功能）
    """
    try:
        stats = StatsService.get_global_stats()
        return GlobalStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 需要导入 datetime
from datetime import datetime
