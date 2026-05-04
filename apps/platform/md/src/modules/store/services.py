"""
Store 服务层
多产品线商城模块的服务层，处理所有业务逻辑

提供 StoreService（公共API）和 AdminStoreService（管理API）两个服务类
"""
import os
import re
import json
import time
import random
import string
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import HTTPException
from psycopg2.extras import RealDictCursor

from core.db_adapter import get_db_cursor, get_db

logger = logging.getLogger(__name__)


# ==================== Helper Functions ====================

def generate_order_no() -> str:
    """生成订单号: STO{timestamp}{6位随机字符}"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"STO{timestamp}{random_str}"


def generate_collection_key(name_zh: str) -> str:
    """从中文名称生成集合键: col_{cleaned}{timestamp%10000}"""
    key = re.sub(r'[^a-zA-Z0-9]', '', name_zh).lower()
    return f"col_{key}{int(time.time()) % 10000}"[:50]


def generate_product_key(name_zh: str) -> str:
    """从中文名称生成产品键: prod_{cleaned}{timestamp%10000}"""
    key = re.sub(r'[^a-zA-Z0-9]', '', name_zh).lower()
    return f"prod_{key}{int(time.time()) % 10000}"[:50]


def json_serialize(obj):
    """JSON 序列化辅助函数"""
    if obj is None:
        return None
    return json.dumps(obj)


def json_deserialize(data):
    """JSON 反序列化辅助函数"""
    if data is None:
        return None
    if isinstance(data, str):
        return json.loads(data)
    return data


# ==================== Public Store Service ====================

class StoreService:
    """商城公共服务 - 产品、购物车、订单、支付"""

    # ---- Collections ----

    @staticmethod
    def get_collections() -> list:
        """获取所有活跃的商城集合，按 sort_order 排序"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT id, collection_key, name_zh, name_en, description,
                       logo_url, theme_config, is_active, sort_order, created_at
                FROM store_collections
                WHERE is_active = TRUE
                ORDER BY sort_order ASC, created_at DESC
            """)
            rows = cur.fetchall()
            collections = []
            for row in rows:
                row['theme_config'] = row['theme_config'] if row['theme_config'] else None
                collections.append(dict(row))
            return collections

    @staticmethod
    def get_collection(collection_key: str) -> dict:
        """根据 collection_key 获取集合详情"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT id, collection_key, name_zh, name_en, description,
                       logo_url, theme_config, is_active, sort_order, created_at
                FROM store_collections
                WHERE collection_key = %s AND is_active = TRUE
            """, (collection_key,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Collection not found")
            row['theme_config'] = row['theme_config'] if row['theme_config'] else None
            return dict(row)

    # ---- Products ----

    @staticmethod
    def get_collection_products(collection_key: str, is_active: bool = True) -> list:
        """获取指定集合的产品列表"""
        with get_db_cursor() as cur:
            cur.execute("SELECT id FROM store_collections WHERE collection_key = %s", (collection_key,))
            collection = cur.fetchone()
            if not collection:
                raise HTTPException(status_code=404, detail="Collection not found")

            collection_id = collection['id']

            query = """
                SELECT
                    p.*,
                    c.name_zh as collection_name,
                    CASE
                        WHEN p.stock_count = -1 THEN TRUE
                        WHEN p.stock_count > 0 THEN TRUE
                        ELSE FALSE
                    END as available
                FROM store_products p
                LEFT JOIN store_collections c ON p.collection_id = c.id
                WHERE p.collection_id = %s
            """
            params = [collection_id]

            if is_active:
                query += " AND p.is_active = TRUE"

            query += " ORDER BY p.sort_order ASC, p.created_at DESC"

            cur.execute(query, params)
            rows = cur.fetchall()

            products = []
            for row in rows:
                row['gallery'] = row['gallery'] if row['gallery'] else []
                row['specifications'] = row['specifications'] if row['specifications'] else None
                products.append(dict(row))
            return products

    @staticmethod
    def get_product_detail(product_id: int) -> dict:
        """获取产品详情（含集合名称和库存可用状态）"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT
                    p.*,
                    c.name_zh as collection_name,
                    CASE
                        WHEN p.stock_count = -1 THEN TRUE
                        WHEN p.stock_count > 0 THEN TRUE
                        ELSE FALSE
                    END as available
                FROM store_products p
                LEFT JOIN store_collections c ON p.collection_id = c.id
                WHERE p.id = %s
            """, (product_id,))

            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Product not found")

            row['gallery'] = row['gallery'] if row['gallery'] else []
            row['specifications'] = row['specifications'] if row['specifications'] else None
            return dict(row)

    # ---- Cart ----

    @staticmethod
    def get_cart(user_id: int, collection_id: int) -> list:
        """获取用户购物车"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT
                    c.id,
                    c.user_id,
                    c.collection_id,
                    c.product_id,
                    c.quantity,
                    p.product_key,
                    p.name_zh as product_name,
                    p.image_url as product_image,
                    p.price,
                    p.price * c.quantity as total_price,
                    CASE
                        WHEN p.stock_count = -1 THEN TRUE
                        WHEN p.stock_count >= c.quantity THEN TRUE
                        ELSE FALSE
                    END as stock_available
                FROM store_cart c
                LEFT JOIN store_products p ON c.product_id = p.id
                WHERE c.user_id = %s AND c.collection_id = %s AND p.is_active = TRUE
                ORDER BY c.created_at DESC
            """, (user_id, collection_id))

            rows = cur.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def add_to_cart(user_id: int, collection_id: int, product_id: int, quantity: int) -> dict:
        """添加到购物车（INSERT ON CONFLICT DO UPDATE）"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT id, is_active, stock_count, price, name_zh
                FROM store_products
                WHERE id = %s
            """, (product_id,))

            product = cur.fetchone()
            if not product:
                raise HTTPException(status_code=404, detail="商品不存在")

            if not product['is_active']:
                raise HTTPException(status_code=400, detail="商品已下架")

            if product['stock_count'] != -1 and product['stock_count'] < quantity:
                raise HTTPException(status_code=400, detail="库存不足")

            cur.execute("""
                INSERT INTO store_cart (user_id, collection_id, product_id, quantity)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, collection_id, product_id)
                DO UPDATE SET quantity = store_cart.quantity + %s,
                              updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (user_id, collection_id, product_id, quantity, quantity))

            return {"message": "已添加到购物车", "product_name": product['name_zh']}

    @staticmethod
    def update_cart_item(cart_id: int, quantity: int) -> dict:
        """更新购物车项数量（验证库存）"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT c.product_id, p.stock_count
                FROM store_cart c
                JOIN store_products p ON c.product_id = p.id
                WHERE c.id = %s
            """, (cart_id,))

            item = cur.fetchone()
            if not item:
                raise HTTPException(status_code=404, detail="购物车项不存在")

            if item['stock_count'] != -1 and item['stock_count'] < quantity:
                raise HTTPException(status_code=400, detail="库存不足")

            cur.execute("""
                UPDATE store_cart
                SET quantity = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (quantity, cart_id))

            return {"message": "购物车已更新"}

    @staticmethod
    def remove_from_cart(cart_id: int) -> dict:
        """从购物车移除"""
        with get_db_cursor() as cur:
            cur.execute("DELETE FROM store_cart WHERE id = %s", (cart_id,))

            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="购物车项不存在")

            return {"message": "已从购物车移除"}

    @staticmethod
    def clear_cart(user_id: int, collection_id: int) -> dict:
        """清空购物车"""
        with get_db_cursor() as cur:
            cur.execute(
                "DELETE FROM store_cart WHERE user_id = %s AND collection_id = %s",
                (user_id, collection_id)
            )
            return {"message": "购物车已清空"}

    # ---- Orders ----

    @staticmethod
    def create_order(
        user_id: int,
        collection_id: int,
        shipping_name: str,
        shipping_phone: str,
        shipping_address: str
    ) -> dict:
        """创建订单（事务：验证购物车 -> 计算总额 -> 创建订单+订单项 -> 更新库存 -> 清空购物车）"""
        conn = get_db()
        cur = None
        try:
            conn.autocommit = False
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # 获取购物车内容
            cur.execute("""
                SELECT c.*, p.name_zh, p.price, p.stock_count
                FROM store_cart c
                JOIN store_products p ON c.product_id = p.id
                WHERE c.user_id = %s AND c.collection_id = %s AND p.is_active = TRUE
            """, (user_id, collection_id))

            cart_items = cur.fetchall()
            if not cart_items:
                raise HTTPException(status_code=400, detail="购物车为空")

            # 计算总金额并验证库存
            total_amount = 0
            order_items = []
            for item in cart_items:
                if item['stock_count'] != -1 and item['stock_count'] < item['quantity']:
                    raise HTTPException(
                        status_code=400,
                        detail=f"商品「{item['name_zh']}」库存不足"
                    )
                subtotal = float(item['price']) * item['quantity']
                total_amount += subtotal
                order_items.append({
                    'product_id': item['product_id'],
                    'product_name': item['name_zh'],
                    'quantity': item['quantity'],
                    'unit_price': float(item['price']),
                    'subtotal': subtotal
                })

            # 生成订单号
            order_no = generate_order_no()

            # 创建订单
            cur.execute("""
                INSERT INTO store_orders (
                    order_no, user_id, collection_id, total_amount,
                    shipping_name, shipping_phone, shipping_address, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
                RETURNING id
            """, (
                order_no, user_id, collection_id, total_amount,
                shipping_name, shipping_phone, shipping_address
            ))

            order_id = cur.fetchone()['id']

            # 创建订单项
            for item in order_items:
                cur.execute("""
                    INSERT INTO store_order_items
                        (order_id, product_id, product_name, quantity, unit_price, subtotal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    order_id, item['product_id'], item['product_name'],
                    item['quantity'], item['unit_price'], item['subtotal']
                ))

                # 更新库存（跳过无限库存），记录进销存流水
                cur.execute(
                    "SELECT stock_count FROM store_products WHERE id=%s FOR UPDATE",
                    (item['product_id'],))
                prod = cur.fetchone()
                old_stock = prod['stock_count'] if prod else -1
                if old_stock != -1:
                    cur.execute("""
                        UPDATE store_products
                        SET stock_count = stock_count - %s, sold_count = sold_count + %s
                        WHERE id = %s AND stock_count != -1
                    """, (item['quantity'], item['quantity'], item['product_id']))
                    new_stock = old_stock - item['quantity']
                    cur.execute("""INSERT INTO store_inventory_logs
                        (product_id, change_type, change_quantity, stock_before, stock_after,
                         reference_no, source)
                        VALUES (%s,'order_deduct',%s,%s,%s,%s,'order')""",
                        (item['product_id'], item['quantity'], old_stock, new_stock, order_no))

            # 清空购物车
            cur.execute(
                "DELETE FROM store_cart WHERE user_id = %s AND collection_id = %s",
                (user_id, collection_id)
            )

            conn.commit()

            return {
                "message": "订单创建成功",
                "order_no": order_no,
                "total_amount": total_amount,
                "order_id": order_id
            }

        except HTTPException:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            logger.exception("创建订单失败")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if cur:
                cur.close()
            conn.close()

    @staticmethod
    def get_user_orders(
        user_id: int,
        collection_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> list:
        """获取用户订单列表（分页、筛选）"""
        with get_db_cursor() as cur:
            query = """
                SELECT id, order_no, user_id, collection_id, total_amount, status,
                       payment_method, payment_no, shipping_name, shipping_phone,
                       shipping_address, created_at, updated_at
                FROM store_orders
                WHERE user_id = %s
            """
            params = [user_id]

            if collection_id:
                query += " AND collection_id = %s"
                params.append(collection_id)

            if status:
                query += " AND status = %s"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cur.execute(query, params)
            rows = cur.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def get_order_detail(order_no: str) -> dict:
        """获取订单详情"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT id, order_no, user_id, collection_id, total_amount, status,
                       payment_method, payment_no, shipping_name, shipping_phone,
                       shipping_address, created_at, updated_at
                FROM store_orders
                WHERE order_no = %s
            """, (order_no,))

            order = cur.fetchone()
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")

            return dict(order)

    @staticmethod
    def get_order_items(order_no: str) -> list:
        """获取订单商品列表"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT oi.*
                FROM store_order_items oi
                JOIN store_orders o ON oi.order_id = o.id
                WHERE o.order_no = %s
            """, (order_no,))

            rows = cur.fetchall()
            return [dict(row) for row in rows]

    # ---- Payment ----

    @staticmethod
    def _generate_wechat_pay_params(order_no: str, amount: float) -> dict:
        """
        生成微信支付参数
        对接微信支付 V2 API: https://api.mch.weixin.qq.com/pay/unifiedorder
        """
        import hashlib
        import requests

        wechat_mch_id = os.getenv("WECHAT_MCH_ID")
        wechat_appid = os.getenv("WECHAT_APPID")
        wechat_api_key = os.getenv("WECHAT_API_KEY")
        wechat_notify_url = os.getenv("WECHAT_NOTIFY_URL", "https://sillymd.com/api/v1/store/callback/wechat")

        if not wechat_appid:
            raise HTTPException(status_code=500, detail="微信支付 APPID 未配置，请设置 WECHAT_APPID 环境变量")
        if not wechat_mch_id:
            raise HTTPException(status_code=500, detail="微信支付未配置")
        if not wechat_api_key:
            raise HTTPException(status_code=500, detail="微信 API 密钥未配置，请设置 WECHAT_API_KEY 环境变量")

        nonce_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

        pay_params = {
            "appid": wechat_appid,
            "mch_id": wechat_mch_id,
            "nonce_str": nonce_str,
            "body": f"SillyMD商城订单-{order_no}",
            "out_trade_no": order_no,
            "total_fee": int(amount * 100),
            "spbill_create_ip": "127.0.0.1",
            "notify_url": wechat_notify_url,
            "trade_type": "NATIVE"
        }

        sorted_keys = sorted([k for k in pay_params if pay_params[k]])
        sign_str = "&".join([f"{k}={pay_params[k]}" for k in sorted_keys]) + f"&key={wechat_api_key}"
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
        pay_params["sign"] = sign

        try:
            response = requests.post(
                "https://api.mch.weixin.qq.com/pay/unifiedorder",
                data=pay_params,
                timeout=10
            )
            result = response.text

            import xml.etree.ElementTree as ET
            root = ET.fromstring(result)

            if root.find("return_code").text == "SUCCESS":
                code_url = root.find("code_url").text
                prepay_id = root.find("prepay_id").text
                return {
                    "code_url": code_url,
                    "prepay_id": prepay_id
                }
            else:
                err_msg = root.find("return_msg").text or "Unknown error"
                raise HTTPException(status_code=500, detail=f"微信支付下单失败: {err_msg}")

        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"微信支付API调用失败: {str(e)}")

    @staticmethod
    def _generate_alipay_params(order_no: str, amount: float) -> dict:
        """
        生成支付宝支付参数
        对接支付宝当面付 API
        """
        alipay_appid = os.getenv("ALIPAY_APP_ID")
        alipay_private_key = os.getenv("ALIPAY_PRIVATE_KEY")
        alipay_public_key = os.getenv("ALIPAY_PUBLIC_KEY")

        if not alipay_appid:
            raise HTTPException(status_code=500, detail="支付宝 APPID 未配置，请设置 ALIPAY_APP_ID 环境变量")
        if not alipay_private_key:
            raise HTTPException(status_code=500, detail="支付宝私钥未配置，请设置 ALIPAY_PRIVATE_KEY 环境变量")
        if not alipay_public_key:
            raise HTTPException(status_code=500, detail="支付宝公钥未配置，请设置 ALIPAY_PUBLIC_KEY 环境变量")

        raise HTTPException(status_code=500, detail="支付宝支付未配置")

    @staticmethod
    def initiate_payment(order_no: str, payment_method: str) -> dict:
        """发起支付"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT id, total_amount, status, payment_method
                FROM store_orders
                WHERE order_no = %s
            """, (order_no,))

            order = cur.fetchone()
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")

            if order['status'] != 'pending':
                raise HTTPException(status_code=400, detail="Order cannot be paid")

            if payment_method not in ['wechat', 'alipay']:
                raise HTTPException(status_code=400, detail="Invalid payment method")

            amount = float(order['total_amount'])

            if payment_method == 'wechat':
                pay_params = StoreService._generate_wechat_pay_params(order_no, amount)
                return {
                    "success": True,
                    "order_no": order_no,
                    "payment_method": "wechat",
                    "code_url": pay_params["code_url"],
                    "prepay_id": pay_params["prepay_id"],
                    "amount": amount
                }
            else:
                pay_params = StoreService._generate_alipay_params(order_no, amount)
                return {
                    "success": True,
                    "order_no": order_no,
                    "payment_method": "alipay",
                    "qr_code": pay_params.get("qr_code"),
                    "amount": amount
                }

    # ---- Payment Callbacks ----

    @staticmethod
    def wechat_callback(xml_data: dict) -> dict:
        """处理微信支付回调"""
        order_no = xml_data.get("out_trade_no")
        transaction_id = xml_data.get("transaction_id")
        return_code = xml_data.get("return_code")

        if return_code != "SUCCESS":
            return {"return_code": "FAIL", "return_msg": "支付失败"}

        conn = get_db()
        cur = None
        try:
            conn.autocommit = False
            cur = conn.cursor(cursor_factory=RealDictCursor)

            cur.execute("""
                UPDATE store_orders
                SET status = 'paid', payment_method = 'wechat',
                    payment_no = %s, updated_at = CURRENT_TIMESTAMP
                WHERE order_no = %s AND status = 'pending'
            """, (transaction_id, order_no))

            if cur.rowcount > 0:
                conn.commit()
                return {"return_code": "SUCCESS", "return_msg": "OK"}
            else:
                conn.commit()
                return {"return_code": "SUCCESS", "return_msg": "Already processed"}

        except Exception as e:
            conn.rollback()
            logger.exception("微信支付回调处理失败")
            return {"return_code": "FAIL", "return_msg": str(e)}
        finally:
            if cur:
                cur.close()
            conn.close()

    @staticmethod
    def alipay_callback(form_data: dict) -> str:
        """处理支付宝支付回调"""
        trade_status = form_data.get("trade_status")
        out_trade_no = form_data.get("out_trade_no")
        trade_no = form_data.get("trade_no")

        if trade_status not in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
            return "fail"

        conn = get_db()
        cur = None
        try:
            conn.autocommit = False
            cur = conn.cursor(cursor_factory=RealDictCursor)

            cur.execute("""
                UPDATE store_orders
                SET status = 'paid', payment_method = 'alipay',
                    payment_no = %s, updated_at = CURRENT_TIMESTAMP
                WHERE order_no = %s AND status = 'pending'
            """, (trade_no, out_trade_no))

            conn.commit()
            return "success"

        except Exception as e:
            conn.rollback()
            logger.exception("支付宝支付回调处理失败")
            return "fail"
        finally:
            if cur:
                cur.close()
            conn.close()

    @staticmethod
    def check_payment_status(order_no: str) -> dict:
        """检查支付状态"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT status, payment_no, payment_method
                FROM store_orders
                WHERE order_no = %s
            """, (order_no,))

            order = cur.fetchone()
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")

            return {
                "order_no": order_no,
                "status": order['status'],
                "payment_no": order['payment_no'],
                "payment_method": order['payment_method'],
                "paid": order['status'] == 'paid'
            }

    # ---- Stats ----

    @staticmethod
    def get_collection_stats(collection_id: int) -> dict:
        """获取集合统计信息"""
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) as count FROM store_products WHERE collection_id = %s AND is_active = TRUE",
                (collection_id,)
            )
            product_count = cur.fetchone()['count']

            cur.execute(
                "SELECT COUNT(*) as count FROM store_orders WHERE collection_id = %s",
                (collection_id,)
            )
            order_count = cur.fetchone()['count']

            cur.execute("""
                SELECT COALESCE(SUM(total_amount), 0) as total
                FROM store_orders
                WHERE collection_id = %s AND status IN ('paid', 'shipped', 'completed')
            """, (collection_id,))
            total_sales = float(cur.fetchone()['total'])

            return {
                "product_count": product_count,
                "order_count": order_count,
                "total_sales": total_sales
            }


# ==================== Admin Store Service ====================

class AdminStoreService:
    """商城管理服务 - 产品集合、产品、订单管理，统计"""

    # ---- Collections ----

    @staticmethod
    def list_collections(
        page: int = 1,
        page_size: int = 20,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> dict:
        """获取所有商城集合（管理端分页）"""
        with get_db_cursor() as cur:
            query = "SELECT * FROM store_collections WHERE 1=1"
            count_query = "SELECT COUNT(*) as total FROM store_collections WHERE 1=1"
            params = []
            count_params = []

            if is_active is not None:
                clause = " AND is_active = %s"
                query += clause
                count_query += clause
                params.append(is_active)
                count_params.append(is_active)

            if search:
                clause = " AND (name_zh ILIKE %s OR name_en ILIKE %s OR collection_key ILIKE %s)"
                query += clause
                count_query += clause
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern, search_pattern])
                count_params.extend([search_pattern, search_pattern, search_pattern])

            cur.execute(count_query, count_params)
            total = cur.fetchone()['total']

            query += " ORDER BY sort_order ASC, created_at DESC LIMIT %s OFFSET %s"
            params.extend([page_size, (page - 1) * page_size])

            cur.execute(query, params)
            rows = cur.fetchall()

            collections = []
            for row in rows:
                row['theme_config'] = json_deserialize(row.get('theme_config'))
                collections.append(dict(row))

            total_pages = (total + page_size - 1) // page_size

            return {
                "items": collections,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }

    @staticmethod
    def create_collection(data: dict) -> dict:
        """创建商城集合"""
        collection_key = data.get('collection_key')
        if not collection_key:
            collection_key = generate_collection_key(data['name_zh'])

        with get_db_cursor() as cur:
            cur.execute("SELECT id FROM store_collections WHERE collection_key = %s", (collection_key,))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail=f"Collection key '{collection_key}' already exists")

            cur.execute("""
                INSERT INTO store_collections (
                    collection_key, name_zh, name_en, description, logo_url,
                    theme_config, is_active, sort_order, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING *
            """, (
                collection_key,
                data['name_zh'],
                data.get('name_en'),
                data.get('description'),
                data.get('logo_url'),
                json_serialize(data.get('theme_config')),
                data.get('is_active', True),
                data.get('sort_order', 0)
            ))

            row = cur.fetchone()
            row['theme_config'] = json_deserialize(row.get('theme_config'))
            return dict(row)

    @staticmethod
    def update_collection(collection_id: int, data: dict) -> dict:
        """更新商城集合（部分更新）"""
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM store_collections WHERE id = %s", (collection_id,))
            existing = cur.fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="Collection not found")

            update_fields = []
            params = []

            if 'collection_key' in data and data['collection_key'] is not None:
                cur.execute(
                    "SELECT id FROM store_collections WHERE collection_key = %s AND id != %s",
                    (data['collection_key'], collection_id)
                )
                if cur.fetchone():
                    raise HTTPException(status_code=400, detail="Collection key already exists")
                update_fields.append("collection_key = %s")
                params.append(data['collection_key'])

            if 'name_zh' in data and data['name_zh'] is not None:
                update_fields.append("name_zh = %s")
                params.append(data['name_zh'])

            if 'name_en' in data and data['name_en'] is not None:
                update_fields.append("name_en = %s")
                params.append(data['name_en'])

            if 'description' in data and data['description'] is not None:
                update_fields.append("description = %s")
                params.append(data['description'])

            if 'logo_url' in data and data['logo_url'] is not None:
                update_fields.append("logo_url = %s")
                params.append(data['logo_url'])

            if 'theme_config' in data and data['theme_config'] is not None:
                update_fields.append("theme_config = %s")
                params.append(json_serialize(data['theme_config']))

            if 'is_active' in data and data['is_active'] is not None:
                update_fields.append("is_active = %s")
                params.append(data['is_active'])

            if 'sort_order' in data and data['sort_order'] is not None:
                update_fields.append("sort_order = %s")
                params.append(data['sort_order'])

            if not update_fields:
                raise HTTPException(status_code=400, detail="No fields to update")

            params.append(collection_id)
            cur.execute(
                f"UPDATE store_collections SET {', '.join(update_fields)} WHERE id = %s RETURNING *",
                params
            )

            row = cur.fetchone()
            row['theme_config'] = json_deserialize(row.get('theme_config'))
            return dict(row)

    @staticmethod
    def delete_collection(collection_id: int) -> dict:
        """软删除商城集合（设置 is_active=FALSE，拒绝有产品的集合）"""
        with get_db_cursor() as cur:
            cur.execute("SELECT id FROM store_collections WHERE id = %s", (collection_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Collection not found")

            cur.execute(
                "SELECT COUNT(*) as count FROM store_products WHERE collection_id = %s",
                (collection_id,)
            )
            if cur.fetchone()['count'] > 0:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot delete collection with associated products"
                )

            cur.execute(
                "UPDATE store_collections SET is_active = FALSE WHERE id = %s",
                (collection_id,)
            )

            return {"message": "Collection deleted successfully"}

    # ---- Products ----

    @staticmethod
    def list_products(
        page: int = 1,
        page_size: int = 20,
        collection_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: Optional[str] = "created_at",
        sort_order: Optional[str] = "desc"
    ) -> dict:
        """获取所有产品（管理端分页+筛选+排序）"""
        with get_db_cursor() as cur:
            query = """
                SELECT p.*, c.name_zh as collection_name
                FROM store_products p
                LEFT JOIN store_collections c ON p.collection_id = c.id
                WHERE 1=1
            """
            count_query = """
                SELECT COUNT(*) as total FROM store_products p
                LEFT JOIN store_collections c ON p.collection_id = c.id
                WHERE 1=1
            """
            params = []
            count_params = []

            if collection_id is not None:
                clause = " AND p.collection_id = %s"
                query += clause
                count_query += clause
                params.append(collection_id)
                count_params.append(collection_id)

            if is_active is not None:
                clause = " AND p.is_active = %s"
                query += clause
                count_query += clause
                params.append(is_active)
                count_params.append(is_active)

            if search:
                clause = " AND (p.name_zh ILIKE %s OR p.name_en ILIKE %s OR p.product_key ILIKE %s)"
                query += clause
                count_query += clause
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern, search_pattern])
                count_params.extend([search_pattern, search_pattern, search_pattern])

            if min_price is not None:
                clause = " AND p.price >= %s"
                query += clause
                count_query += clause
                params.append(min_price)
                count_params.append(min_price)

            if max_price is not None and max_price > 0:
                clause = " AND p.price <= %s"
                query += clause
                count_query += clause
                params.append(max_price)
                count_params.append(max_price)

            allowed_sort = {'created_at': 'p.created_at', 'price': 'p.price', 'sort_order': 'p.sort_order'}
            sort_column = allowed_sort.get(sort_by, 'p.created_at')
            sort_dir = "DESC" if sort_order == "desc" else "ASC"
            query += f" ORDER BY {sort_column} {sort_dir}"

            cur.execute(count_query, count_params)
            total = cur.fetchone()['total']

            query += " LIMIT %s OFFSET %s"
            params.extend([page_size, (page - 1) * page_size])

            cur.execute(query, params)
            rows = cur.fetchall()

            products = []
            for row in rows:
                row['gallery'] = json_deserialize(row.get('gallery')) or []
                row['specifications'] = json_deserialize(row.get('specifications'))
                products.append(dict(row))

            total_pages = (total + page_size - 1) // page_size

            return {
                "items": products,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }

    @staticmethod
    def get_product(product_id: int) -> dict:
        """获取产品详情（管理端）"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT p.*, c.name_zh as collection_name
                FROM store_products p
                LEFT JOIN store_collections c ON p.collection_id = c.id
                WHERE p.id = %s
            """, (product_id,))

            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Product not found")

            row['gallery'] = json_deserialize(row.get('gallery')) or []
            row['specifications'] = json_deserialize(row.get('specifications'))
            return dict(row)

    @staticmethod
    def create_product(data: dict) -> dict:
        """创建产品"""
        product_key = data.get('product_key')
        if not product_key:
            product_key = generate_product_key(data['name_zh'])

        with get_db_cursor() as cur:
            cur.execute("SELECT id FROM store_collections WHERE id = %s", (data['collection_id'],))
            if not cur.fetchone():
                raise HTTPException(status_code=400, detail="Collection not found")

            cur.execute("SELECT id FROM store_products WHERE product_key = %s", (product_key,))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail=f"Product key '{product_key}' already exists")

            cur.execute("""
                INSERT INTO store_products (
                    collection_id, product_key, name_zh, name_en, description_zh, description_en,
                    image_url, gallery, price, original_price, stock_count, specifications,
                    is_active, sort_order, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING *
            """, (
                data['collection_id'],
                product_key,
                data['name_zh'],
                data.get('name_en'),
                data.get('description_zh'),
                data.get('description_en'),
                data.get('image_url'),
                json_serialize(data.get('gallery', [])),
                data['price'],
                data.get('original_price'),
                data.get('stock_count', -1),
                json_serialize(data.get('specifications')),
                data.get('is_active', True),
                data.get('sort_order', 0)
            ))

            row = cur.fetchone()
            row['gallery'] = json_deserialize(row.get('gallery')) or []
            row['specifications'] = json_deserialize(row.get('specifications'))

            cur.execute("SELECT name_zh FROM store_collections WHERE id = %s", (data['collection_id'],))
            col_row = cur.fetchone()
            row['collection_name'] = col_row['name_zh'] if col_row else None

            return dict(row)

    @staticmethod
    def update_product(product_id: int, data: dict) -> dict:
        """更新产品（部分更新）"""
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM store_products WHERE id = %s", (product_id,))
            existing = cur.fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="Product not found")

            update_fields = []
            params = []

            if 'collection_id' in data and data['collection_id'] is not None:
                cur.execute("SELECT id FROM store_collections WHERE id = %s", (data['collection_id'],))
                if not cur.fetchone():
                    raise HTTPException(status_code=400, detail="Collection not found")
                update_fields.append("collection_id = %s")
                params.append(data['collection_id'])

            if 'product_key' in data and data['product_key'] is not None:
                cur.execute(
                    "SELECT id FROM store_products WHERE product_key = %s AND id != %s",
                    (data['product_key'], product_id)
                )
                if cur.fetchone():
                    raise HTTPException(status_code=400, detail="Product key already exists")
                update_fields.append("product_key = %s")
                params.append(data['product_key'])

            if 'name_zh' in data and data['name_zh'] is not None:
                update_fields.append("name_zh = %s")
                params.append(data['name_zh'])

            if 'name_en' in data and data['name_en'] is not None:
                update_fields.append("name_en = %s")
                params.append(data['name_en'])

            if 'description_zh' in data and data['description_zh'] is not None:
                update_fields.append("description_zh = %s")
                params.append(data['description_zh'])

            if 'description_en' in data and data['description_en'] is not None:
                update_fields.append("description_en = %s")
                params.append(data['description_en'])

            if 'image_url' in data and data['image_url'] is not None:
                update_fields.append("image_url = %s")
                params.append(data['image_url'])

            if 'gallery' in data and data['gallery'] is not None:
                update_fields.append("gallery = %s")
                params.append(json_serialize(data['gallery']))

            if 'price' in data and data['price'] is not None:
                update_fields.append("price = %s")
                params.append(data['price'])

            if 'original_price' in data and data['original_price'] is not None:
                update_fields.append("original_price = %s")
                params.append(data['original_price'])

            if 'stock_count' in data and data['stock_count'] is not None:
                update_fields.append("stock_count = %s")
                params.append(data['stock_count'])

            if 'specifications' in data and data['specifications'] is not None:
                update_fields.append("specifications = %s")
                params.append(json_serialize(data['specifications']))

            if 'is_active' in data and data['is_active'] is not None:
                update_fields.append("is_active = %s")
                params.append(data['is_active'])

            if 'sort_order' in data and data['sort_order'] is not None:
                update_fields.append("sort_order = %s")
                params.append(data['sort_order'])

            if not update_fields:
                raise HTTPException(status_code=400, detail="No fields to update")

            params.append(product_id)
            cur.execute(
                f"UPDATE store_products SET {', '.join(update_fields)} WHERE id = %s RETURNING *",
                params
            )

            row = cur.fetchone()
            row['gallery'] = json_deserialize(row.get('gallery')) or []
            row['specifications'] = json_deserialize(row.get('specifications'))

            cur.execute("SELECT name_zh FROM store_collections WHERE id = %s", (row['collection_id'],))
            col_row = cur.fetchone()
            row['collection_name'] = col_row['name_zh'] if col_row else None

            return dict(row)

    @staticmethod
    def delete_product(product_id: int) -> dict:
        """软删除产品（设置 is_active=FALSE）"""
        with get_db_cursor() as cur:
            cur.execute("SELECT id FROM store_products WHERE id = %s", (product_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Product not found")

            cur.execute(
                "UPDATE store_products SET is_active = FALSE WHERE id = %s",
                (product_id,)
            )

            return {"message": "Product deleted successfully"}

    # ---- Orders ----

    @staticmethod
    def list_orders(
        page: int = 1,
        page_size: int = 20,
        collection_id: Optional[int] = None,
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        order_no: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> dict:
        """获取所有订单（管理端分页+筛选）"""
        with get_db_cursor() as cur:
            query = """
                SELECT o.*, c.name_zh as collection_name
                FROM store_orders o
                LEFT JOIN store_collections c ON o.collection_id = c.id
                WHERE 1=1
            """
            count_query = """
                SELECT COUNT(*) as total FROM store_orders o
                LEFT JOIN store_collections c ON o.collection_id = c.id
                WHERE 1=1
            """
            params = []
            count_params = []

            if collection_id is not None:
                clause = " AND o.collection_id = %s"
                query += clause
                count_query += clause
                params.append(collection_id)
                count_params.append(collection_id)

            if status:
                clause = " AND o.status = %s"
                query += clause
                count_query += clause
                params.append(status)
                count_params.append(status)

            if user_id is not None:
                clause = " AND o.user_id = %s"
                query += clause
                count_query += clause
                params.append(user_id)
                count_params.append(user_id)

            if order_no:
                clause = " AND o.order_no ILIKE %s"
                query += clause
                count_query += clause
                params.append(f"%{order_no}%")
                count_params.append(f"%{order_no}%")

            if start_date:
                clause = " AND DATE(o.created_at) >= %s"
                query += clause
                count_query += clause
                params.append(start_date)
                count_params.append(start_date)

            if end_date:
                clause = " AND DATE(o.created_at) <= %s"
                query += clause
                count_query += clause
                params.append(end_date)
                count_params.append(end_date)

            cur.execute(count_query, count_params)
            total = cur.fetchone()['total']

            query += " ORDER BY o.created_at DESC LIMIT %s OFFSET %s"
            params.extend([page_size, (page - 1) * page_size])

            cur.execute(query, params)
            rows = cur.fetchall()

            orders = [dict(row) for row in rows]
            total_pages = (total + page_size - 1) // page_size

            return {
                "items": orders,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }

    @staticmethod
    def get_order_detail(order_no: str) -> dict:
        """获取订单详情含订单项（管理端）"""
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT o.*, c.name_zh as collection_name
                FROM store_orders o
                LEFT JOIN store_collections c ON o.collection_id = c.id
                WHERE o.order_no = %s
            """, (order_no,))

            order_row = cur.fetchone()
            if not order_row:
                raise HTTPException(status_code=404, detail="Order not found")

            cur.execute("SELECT * FROM store_order_items WHERE order_id = %s", (order_row['id'],))
            items = [dict(row) for row in cur.fetchall()]

            return {
                "order": dict(order_row),
                "items": items
            }

    @staticmethod
    def update_order_status(order_no: str, status: str) -> dict:
        """更新订单状态（验证状态转换规则）"""
        valid_statuses = ['pending', 'paid', 'shipped', 'completed', 'cancelled']
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        conn = get_db()
        cur = None
        try:
            conn.autocommit = False
            cur = conn.cursor(cursor_factory=RealDictCursor)

            cur.execute("SELECT * FROM store_orders WHERE order_no = %s", (order_no,))
            order = cur.fetchone()
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")

            current_status = order['status']

            if current_status == 'completed' and status != 'completed':
                raise HTTPException(status_code=400, detail="Cannot change status of completed order")

            if current_status == 'cancelled':
                raise HTTPException(status_code=400, detail="Cannot change status of cancelled order")

            # 取消订单时回滚库存并记录进销存流水
            if status == 'cancelled' and current_status in ['pending', 'paid', 'shipped']:
                cur.execute("""
                    SELECT oi.product_id, oi.quantity
                    FROM store_order_items oi
                    JOIN store_orders o ON oi.order_id = o.id
                    WHERE o.order_no = %s
                """, (order_no,))

                for item in cur.fetchall():
                    cur.execute(
                        "SELECT stock_count, sold_count FROM store_products WHERE id=%s FOR UPDATE",
                        (item['product_id'],))
                    prod_row = cur.fetchone()
                    if prod_row and prod_row['stock_count'] != -1:
                        old_stock = prod_row['stock_count']
                        cur.execute("""
                            UPDATE store_products
                            SET stock_count = stock_count + %s, sold_count = sold_count - %s
                            WHERE id = %s AND stock_count != -1
                        """, (item['quantity'], item['quantity'], item['product_id']))
                        new_stock = old_stock + item['quantity']
                        cur.execute("""INSERT INTO store_inventory_logs
                            (product_id, change_type, change_quantity, stock_before, stock_after,
                             reference_no, source)
                            VALUES (%s,'order_cancel',%s,%s,%s,%s,'order')""",
                            (item['product_id'], item['quantity'], old_stock, new_stock, order_no))

            cur.execute("""
                UPDATE store_orders
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE order_no = %s
                RETURNING *
            """, (status, order_no))

            conn.commit()
            updated_order = cur.fetchone()

            return {
                "message": f"Order status updated from '{current_status}' to '{status}'",
                "order_no": order_no,
                "new_status": status
            }

        except HTTPException:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            logger.exception("更新订单状态失败")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if cur:
                cur.close()
            conn.close()

    # ---- Stats ----

    @staticmethod
    def get_store_stats() -> dict:
        """获取商城统计信息"""
        with get_db_cursor() as cur:
            stats = {}

            cur.execute("SELECT COUNT(*) as count FROM store_collections")
            stats['total_collections'] = cur.fetchone()['count']

            cur.execute("SELECT COUNT(*) as count FROM store_collections WHERE is_active = TRUE")
            stats['active_collections'] = cur.fetchone()['count']

            cur.execute("SELECT COUNT(*) as count FROM store_products")
            stats['total_products'] = cur.fetchone()['count']

            cur.execute("SELECT COUNT(*) as count FROM store_products WHERE is_active = TRUE")
            stats['active_products'] = cur.fetchone()['count']

            cur.execute("SELECT COUNT(*) as count FROM store_orders")
            stats['total_orders'] = cur.fetchone()['count']

            cur.execute("SELECT COUNT(*) as count FROM store_orders WHERE status = 'pending'")
            stats['pending_orders'] = cur.fetchone()['count']

            cur.execute("""
                SELECT COALESCE(SUM(total_amount), 0) as total
                FROM store_orders
                WHERE status IN ('paid', 'shipped', 'completed')
            """)
            stats['total_revenue'] = float(cur.fetchone()['total'])

            return stats
