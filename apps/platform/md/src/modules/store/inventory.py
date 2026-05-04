"""
进销存服务 — 独立接口层

提供完整的库存管理 API，供：
  - admin-v2 管理面板
  - 公司内部 ERP/进销存系统
  - 外部系统通过 REST API 对接
"""

import logging
from typing import Optional
from psycopg2.extras import RealDictCursor
from core.db_adapter import get_db_cursor, get_db

logger = logging.getLogger(__name__)


class InventoryService:
    """进销存服务 — 入库/出库/盘点/流水/查询/同步"""

    # ==================== 库存调整 ====================

    @staticmethod
    def adjust_stock(product_id: int, change_type: str, quantity: int, *,
                     note: str = None, operator_id: int = None,
                     operator_name: str = None, reference_no: str = None,
                     external_ref: str = None, source: str = 'admin') -> dict:
        """库存调整（入库/出库/盘点），写入完整流水日志"""
        if change_type not in ('in', 'out', 'adjust'):
            raise ValueError("change_type 必须为 in/out/adjust")
        if quantity <= 0:
            raise ValueError("数量必须 > 0")

        conn = get_db()
        cur = None
        try:
            conn.autocommit = False
            cur = conn.cursor(cursor_factory=RealDictCursor)

            cur.execute(
                "SELECT id, stock_count, name_zh FROM store_products WHERE id=%s FOR UPDATE",
                (product_id,))
            product = cur.fetchone()
            if not product:
                raise ValueError("产品不存在")
            old_stock = product['stock_count']
            if old_stock == -1:
                raise ValueError("无限库存产品不需要手动调整")

            if change_type == 'in':
                new_stock = old_stock + quantity
            elif change_type == 'out':
                if old_stock < quantity:
                    raise ValueError(f"库存不足，当前库存 {old_stock}")
                new_stock = old_stock - quantity
            else:  # adjust 盘点
                new_stock = quantity

            cur.execute(
                "UPDATE store_products SET stock_count=%s, updated_at=NOW() WHERE id=%s",
                (new_stock, product_id))

            change_qty = abs(new_stock - old_stock)
            cur.execute("""INSERT INTO store_inventory_logs
                (product_id, change_type, change_quantity, stock_before, stock_after,
                 reference_no, external_ref, source, note, operator_id, operator_name)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                (product_id, change_type, change_qty,
                 old_stock, new_stock, reference_no, external_ref,
                 source, note, operator_id, operator_name))

            log_id = cur.fetchone()['id']
            conn.commit()
            return {
                "success": True, "log_id": log_id,
                "product_id": product_id, "product_name": product['name_zh'],
                "stock_before": old_stock, "stock_after": new_stock,
                "change_type": change_type, "change_quantity": change_qty,
            }
        except Exception:
            conn.rollback()
            raise
        finally:
            if cur:
                cur.close()
            conn.close()

    @staticmethod
    def adjust_stock_by_key(product_key: str, change_type: str, quantity: int, **kwargs) -> dict:
        """通过 product_key 调整库存（外部系统常用）"""
        with get_db_cursor() as cur:
            cur.execute("SELECT id FROM store_products WHERE product_key=%s", (product_key,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"产品 {product_key} 不存在")
            product_id = row['id']
        return InventoryService.adjust_stock(product_id, change_type, quantity, **kwargs)

    @staticmethod
    def batch_adjust(items: list) -> dict:
        """批量库存调整（外部ERP一次性同步多个产品）"""
        results, errors = [], []
        for item in items:
            try:
                if item.get('product_key'):
                    r = InventoryService.adjust_stock_by_key(
                        item['product_key'], item['change_type'],
                        item['quantity'],
                        note=item.get('note'),
                        reference_no=item.get('reference_no'),
                        external_ref=item.get('external_ref'),
                        source=item.get('source', 'external_api'),
                        operator_name=item.get('operator_name'))
                else:
                    r = InventoryService.adjust_stock(
                        item['product_id'], item['change_type'],
                        item['quantity'],
                        note=item.get('note'),
                        reference_no=item.get('reference_no'),
                        external_ref=item.get('external_ref'),
                        source=item.get('source', 'external_api'),
                        operator_name=item.get('operator_name'))
                results.append(r)
            except Exception as e:
                errors.append({"item": item, "error": str(e)})
        return {
            "success": len(errors) == 0,
            "processed": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors,
        }

    # ==================== 库存查询 ====================

    @staticmethod
    def get_stock(product_id: int) -> dict:
        """查询单个产品库存"""
        with get_db_cursor() as cur:
            cur.execute("""SELECT id, product_key, name_zh, name_en,
                stock_count, sold_count, price, is_active
                FROM store_products WHERE id=%s""", (product_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError("产品不存在")
            return dict(row)

    @staticmethod
    def get_stock_by_key(product_key: str) -> dict:
        """通过 product_key 查询库存"""
        with get_db_cursor() as cur:
            cur.execute("""SELECT id, product_key, name_zh, name_en,
                stock_count, sold_count, price, is_active
                FROM store_products WHERE product_key=%s""", (product_key,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"产品 {product_key} 不存在")
            return dict(row)

    @staticmethod
    def list_stock(page: int = 1, page_size: int = 50, *,
                   search: str = None, low_stock_only: bool = False,
                   collection_key: str = None) -> dict:
        """库存列表（分页+筛选）"""
        with get_db_cursor() as cur:
            query = """SELECT p.id, p.product_key, p.name_zh, p.name_en,
                       p.stock_count, p.sold_count, p.price, p.original_price,
                       p.is_active, c.name_zh as collection_name, c.collection_key
                       FROM store_products p
                       LEFT JOIN store_collections c ON p.collection_id = c.id
                       WHERE 1=1"""
            count_q = """SELECT COUNT(*) as total
                         FROM store_products p
                         LEFT JOIN store_collections c ON p.collection_id = c.id
                         WHERE 1=1"""
            params, cp = [], []

            if search:
                clause = " AND (p.name_zh ILIKE %s OR p.product_key ILIKE %s)"
                query += clause
                count_q += clause
                params.extend([f"%{search}%", f"%{search}%"])
                cp.extend([f"%{search}%", f"%{search}%"])

            if low_stock_only:
                clause = " AND p.stock_count >= 0 AND p.stock_count < 10"
                query += clause
                count_q += clause

            if collection_key:
                clause = " AND c.collection_key = %s"
                query += clause
                count_q += clause
                params.append(collection_key)
                cp.append(collection_key)

            cur.execute(count_q, cp)
            total = cur.fetchone()['total']

            query += " ORDER BY p.stock_count ASC NULLS LAST LIMIT %s OFFSET %s"
            params.extend([page_size, (page - 1) * page_size])

            cur.execute(query, params)
            items = [dict(r) for r in cur.fetchall()]
            return {
                "items": items, "total": total,
                "page": page, "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
            }

    # ==================== 库存流水 ====================

    @staticmethod
    def get_logs(product_id: int = None, *, page: int = 1, page_size: int = 20,
                 change_type: str = None, source: str = None,
                 start_date: str = None, end_date: str = None,
                 sync_status: str = None) -> dict:
        """库存流水查询（多条件筛选，供外部系统对账）"""
        with get_db_cursor() as cur:
            query = "SELECT * FROM store_inventory_logs WHERE 1=1"
            count_q = "SELECT COUNT(*) as total FROM store_inventory_logs WHERE 1=1"
            params, cp = [], []

            if product_id:
                clause = " AND product_id = %s"
                query += clause
                count_q += clause
                params.append(product_id)
                cp.append(product_id)
            if change_type:
                clause = " AND change_type = %s"
                query += clause
                count_q += clause
                params.append(change_type)
                cp.append(change_type)
            if source:
                clause = " AND source = %s"
                query += clause
                count_q += clause
                params.append(source)
                cp.append(source)
            if sync_status:
                clause = " AND sync_status = %s"
                query += clause
                count_q += clause
                params.append(sync_status)
                cp.append(sync_status)
            if start_date:
                clause = " AND created_at >= %s"
                query += clause
                count_q += clause
                params.append(start_date)
                cp.append(start_date)
            if end_date:
                clause = " AND created_at <= %s"
                query += clause
                count_q += clause
                params.append(end_date + ' 23:59:59')
                cp.append(end_date + ' 23:59:59')

            cur.execute(count_q, cp)
            total = cur.fetchone()['total']

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([page_size, (page - 1) * page_size])
            cur.execute(query, params)
            items = [dict(r) for r in cur.fetchall()]
            return {
                "items": items, "total": total,
                "page": page, "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
            }

    # ==================== 同步状态（对接外部ERP） ====================

    @staticmethod
    def mark_synced(log_ids: list, status: str = 'synced') -> dict:
        """标记流水日志已同步到外部系统"""
        with get_db_cursor() as cur:
            cur.execute("""UPDATE store_inventory_logs
                SET sync_status=%s, synced_at=NOW()
                WHERE id = ANY(%s)""", (status, log_ids))
        return {"updated": cur.rowcount}

    @staticmethod
    def get_unsynced_logs(limit: int = 100) -> list:
        """获取未同步的流水（供外部系统拉取）"""
        with get_db_cursor() as cur:
            cur.execute("""SELECT * FROM store_inventory_logs
                WHERE sync_status='local'
                ORDER BY created_at ASC LIMIT %s""", (limit,))
        return [dict(r) for r in cur.fetchall()]
