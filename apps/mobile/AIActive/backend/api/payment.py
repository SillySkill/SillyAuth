"""
支付订单API
"""
import os
import uuid
import time
from datetime import datetime
from flask import Blueprint, request, jsonify
from models.database import DatabaseManager

payment_bp = Blueprint('payment', __name__)

# 数据库连接
db = DatabaseManager()


@payment_bp.route('/create', methods=['POST'])
def create_payment():
    """
    创建支付订单

    POST /api/payment/create
    Body: {
        "style_id": "jst100001",
        "payment_method": "wechat",
        "amount": 9.9,
        "user_name": "张三",
        "user_phone": "13800138000",
        "device_id": "device_123"
    }
    """
    try:
        data = request.get_json()
        style_id = data.get('style_id', '')
        payment_method = data.get('payment_method', 'wechat')  # wechat/alipay
        amount = data.get('amount', 9.9)
        user_name = data.get('user_name', '')
        user_phone = data.get('user_phone', '')
        device_id = data.get('device_id', '')

        if not style_id:
            return jsonify({'code': 400, 'message': '风格ID不能为空'}), 400

        if payment_method not in ['wechat', 'alipay']:
            return jsonify({'code': 400, 'message': '不支持的支付方式'}), 400

        if not db.connect():
            return jsonify({'code': 500, 'message': '数据库连接失败'}), 500

        # 生成订单号
        order_id = f"ORDER{int(time.time())}{uuid.uuid4().hex[:8].upper()}"

        # 根据支付方式生成支付信息
        # 注意：这里是模拟实现，实际需要对接微信/支付宝SDK
        qr_code_url = None
        payment_url = None
        prepay_id = None

        if payment_method == 'wechat':
            # 微信支付 - 模拟生成Native支付二维码
            # 实际应调用微信统一下单API
            qr_code_url = f"weixin://wxpay/bizpayurl?pr={order_id}"
            prepay_id = f"wx{order_id}"
        else:
            # 支付宝支付 - 模拟生成支付二维码
            # 实际应调用支付宝统一收单下单API
            qr_code_url = f"https://qr.alipay.com/{order_id}"
            payment_url = f"https://openapi.alipay.com/gateway.do?{order_id}"

        # 插入订单记录
        sql = """
            INSERT INTO payment_orders
            (order_id, style_id, amount, payment_method, payment_status,
             prepay_id, qr_code_url, payment_url, user_name, user_phone, device_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        db.execute(sql, (
            order_id, style_id, amount, payment_method, 0,
            prepay_id, qr_code_url, payment_url, user_name, user_phone, device_id
        ))

        db.close()

        return jsonify({
            'code': 200,
            'message': '订单创建成功',
            'data': {
                'order_id': order_id,
                'amount': amount,
                'payment_method': payment_method,
                'qr_code_url': qr_code_url,
                'payment_url': payment_url
            }
        })
    except Exception as e:
        if db.connection:
            db.close()
        return jsonify({'code': 500, 'message': str(e)}), 500


@payment_bp.route('/query', methods=['GET'])
def query_payment():
    """
    查询支付订单状态

    GET /api/payment/query?order_id=ORDER123456
    """
    try:
        order_id = request.args.get('order_id', '')

        if not order_id:
            return jsonify({'code': 400, 'message': '订单号不能为空'}), 400

        if not db.connect():
            return jsonify({'code': 500, 'message': '数据库连接失败'}), 500

        # 查询订单
        sql = """
            SELECT order_id, style_id, amount, payment_method, payment_status,
                   transaction_id, qr_code_url, payment_url,
                   user_name, user_phone, paid_at, created_at
            FROM payment_orders
            WHERE order_id = %s
        """
        result = db.fetch_one(sql, (order_id,))

        if not result:
            db.close()
            return jsonify({'code': 404, 'message': '订单不存在'}), 404

        (order_id, style_id, amount, payment_method, payment_status,
         transaction_id, qr_code_url, payment_url,
         user_name, user_phone, paid_at, created_at) = result

        db.close()

        # 状态映射
        status_map = {
            0: '待支付',
            1: '已支付',
            2: '已取消',
            3: '已退款'
        }

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'order_id': order_id,
                'style_id': style_id,
                'amount': float(amount),
                'payment_method': payment_method,
                'payment_status': payment_status,
                'payment_status_text': status_map.get(payment_status, '未知'),
                'transaction_id': transaction_id,
                'qr_code_url': qr_code_url,
                'payment_url': payment_url,
                'user_name': user_name,
                'user_phone': user_phone,
                'paid_at': paid_at.strftime('%Y-%m-%d %H:%M:%S') if paid_at else None,
                'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        if db.connection:
            db.close()
        return jsonify({'code': 500, 'message': str(e)}), 500


@payment_bp.route('/notify', methods=['POST'])
def payment_notify():
    """
    支付回调通知（微信/支付宝回调）

    POST /api/payment/notify
    """
    try:
        # 这里需要验证签名
        # 根据不同的支付方式解析回调数据

        payment_method = request.headers.get('X-Payment-Method', 'wechat')

        if not db.connect():
            return jsonify({'code': 500, 'message': '数据库连接失败'}), 500

        if payment_method == 'wechat':
            # 微信支付回调处理
            # 实际需要解析XML格式数据并验证签名
            data = request.values
            order_id = data.get('out_trade_no')
            transaction_id = data.get('transaction_id')

            if data.get('return_code') == 'SUCCESS' and data.get('result_code') == 'SUCCESS':
                # 支付成功，更新订单状态
                sql = """
                    UPDATE payment_orders
                    SET payment_status = 1, transaction_id = %s, paid_at = NOW()
                    WHERE order_id = %s AND payment_status = 0
                """
                db.execute(sql, (transaction_id, order_id))

        elif payment_method == 'alipay':
            # 支付宝回调处理
            # 实际需要解析并验证签名
            data = request.form
            order_id = data.get('out_trade_no')
            trade_no = data.get('trade_no')

            if data.get('trade_status') == 'TRADE_SUCCESS':
                # 支付成功，更新订单状态
                sql = """
                    UPDATE payment_orders
                    SET payment_status = 1, transaction_id = %s, paid_at = NOW()
                    WHERE order_id = %s AND payment_status = 0
                """
                db.execute(sql, (trade_no, order_id))

        db.close()

        # 返回支付平台要求的格式
        if payment_method == 'wechat':
            return '<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>'
        else:
            return 'success'

    except Exception as e:
        if db.connection:
            db.close()
        return jsonify({'code': 500, 'message': str(e)}), 500


@payment_bp.route('/list', methods=['GET'])
def list_payments():
    """
    获取支付订单列表

    GET /api/payment/list?status=1&page=1&page_size=20
    """
    try:
        status = request.args.get('status', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))

        if not db.connect():
            return jsonify({'code': 500, 'message': '数据库连接失败'}), 500

        # 构建查询条件
        conditions = []
        params = []
        if status != '':
            conditions.append("payment_status = %s")
            params.append(int(status))

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        # 查询总数
        count_sql = f"SELECT COUNT(*) FROM payment_orders{where_clause}"
        total = db.fetch_one(count_sql, params)[0]

        # 查询列表
        offset = (page - 1) * page_size
        list_sql = f"""
            SELECT order_id, style_id, amount, payment_method, payment_status,
                   transaction_id, user_name, user_phone, paid_at, created_at
            FROM payment_orders
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([page_size, offset])

        results = db.execute(list_sql, params)

        # 状态映射
        status_map = {
            0: '待支付',
            1: '已支付',
            2: '已取消',
            3: '已退款'
        }

        orders = []
        for row in results:
            (order_id, style_id, amount, payment_method, payment_status,
             transaction_id, user_name, user_phone, paid_at, created_at) = row
            orders.append({
                'order_id': order_id,
                'style_id': style_id,
                'amount': float(amount),
                'payment_method': payment_method,
                'payment_status': payment_status,
                'payment_status_text': status_map.get(payment_status, '未知'),
                'transaction_id': transaction_id,
                'user_name': user_name,
                'user_phone': user_phone,
                'paid_at': paid_at.strftime('%Y-%m-%d %H:%M:%S') if paid_at else None,
                'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        db.close()

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'list': orders
            }
        })
    except Exception as e:
        if db.connection:
            db.close()
        return jsonify({'code': 500, 'message': str(e)}), 500
