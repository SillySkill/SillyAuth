"""
邀请码管理API
"""
import os
import uuid
import random
import string
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, send_file
from models.database import DatabaseManager

invite_bp = Blueprint('invite', __name__)

# 数据库连接
db = DatabaseManager()


def generate_invite_code(length=8):
    """生成随机邀请码"""
    # 生成大写字母和数字的组合
    chars = string.ascii_uppercase + string.digits
    # 排除容易混淆的字符（如0和O，1和I）
    chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
    return ''.join(random.choice(chars) for _ in range(length))


@invite_bp.route('/generate', methods=['POST'])
def create_invite_codes():
    """
    生成邀请码

    POST /api/invite/generate
    Body: {
        "batch_name": "活动A",
        "quantity": 100,
        "max_usage": 1,
        "valid_days": 30,
        "created_by": "admin"
    }
    """
    try:
        data = request.get_json()
        batch_name = data.get('batch_name', f'批次_{datetime.now().strftime("%Y%m%d%H%M%S")}')
        quantity = data.get('quantity', 1)
        max_usage = data.get('max_usage', 1)
        valid_days = data.get('valid_days')
        created_by = data.get('created_by', 'system')

        if not db.connect():
            return jsonify({'code': 500, 'message': '数据库连接失败'}), 500

        # 计算有效期
        valid_from = datetime.now()
        valid_until = None
        if valid_days:
            valid_until = valid_from + timedelta(days=valid_days)

        # 生成邀请码
        codes = []
        for _ in range(quantity):
            # 确保邀请码唯一
            while True:
                code = generate_invite_code()
                # 检查是否已存在
                check_sql = "SELECT id FROM invite_codes WHERE code = %s"
                result = db.fetch_one(check_sql, (code,))
                if not result:
                    break

            # 插入数据库
            sql = """
                INSERT INTO invite_codes (code, batch_name, max_usage, valid_from, valid_until, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            db.execute(sql, (code, batch_name, max_usage, valid_from, valid_until, created_by))
            codes.append(code)

        db.close()

        return jsonify({
            'code': 200,
            'message': f'成功生成{quantity}个邀请码',
            'data': {
                'batch_name': batch_name,
                'quantity': quantity,
                'codes': codes
            }
        })
    except Exception as e:
        if db.connection:
            db.close()
        return jsonify({'code': 500, 'message': str(e)}), 500


@invite_bp.route('/verify', methods=['POST'])
def verify_invite_code():
    """
    验证邀请码

    POST /api/invite/verify
    Body: {
        "invite_code": "ABC12345",
        "style_id": "jst100001",
        "user_name": "张三",
        "user_phone": "13800138000",
        "device_id": "device_123"
    }
    """
    try:
        data = request.get_json()
        invite_code = data.get('invite_code', '').strip().upper()
        style_id = data.get('style_id', '')
        user_name = data.get('user_name', '')
        user_phone = data.get('user_phone', '')
        device_id = data.get('device_id', '')

        if not invite_code:
            return jsonify({'code': 400, 'message': '邀请码不能为空'}), 400

        if not db.connect():
            return jsonify({'code': 500, 'message': '数据库连接失败'}), 500

        # 查询邀请码
        sql = """
            SELECT id, code, batch_name, max_usage, used_count, status,
                   valid_from, valid_until
            FROM invite_codes
            WHERE code = %s
        """
        result = db.fetch_one(sql, (invite_code,))

        if not result:
            db.close()
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {'valid': False, 'message': '邀请码不存在'}
            })

        (code_id, code, batch_name, max_usage, used_count, status,
         valid_from, valid_until) = result

        # 检查状态
        if status != 1:
            db.close()
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {'valid': False, 'message': '邀请码已被禁用'}
            })

        # 检查有效期
        now = datetime.now()
        if valid_from and now < valid_from:
            db.close()
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {'valid': False, 'message': f'邀请码尚未生效，生效时间：{valid_from.strftime("%Y-%m-%d %H:%M")}'}
            })

        if valid_until and now > valid_until:
            db.close()
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {'valid': False, 'message': f'邀请码已过期，过期时间：{valid_until.strftime("%Y-%m-%d %H:%M")}'}
            })

        # 检查使用次数
        if used_count >= max_usage:
            db.close()
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {'valid': False, 'message': '邀请码使用次数已达上限'}
            })

        # 验证通过，记录使用
        update_sql = "UPDATE invite_codes SET used_count = used_count + 1 WHERE id = %s"
        db.execute(update_sql, (code_id,))

        # 插入使用记录
        record_sql = """
            INSERT INTO invite_code_usage
            (invite_code, user_name, user_phone, style_id, device_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        db.execute(record_sql, (invite_code, user_name, user_phone, style_id, device_id))

        db.close()

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'valid': True,
                'user_name': user_name,
                'batch_name': batch_name,
                'remaining_times': max_usage - used_count - 1
            }
        })
    except Exception as e:
        if db.connection:
            db.close()
        return jsonify({'code': 500, 'message': str(e)}), 500


@invite_bp.route('/list', methods=['GET'])
def list_invite_codes():
    """
    获取邀请码列表

    GET /api/invite/list?batch_name=xxx&status=1&page=1&page_size=20
    """
    try:
        batch_name = request.args.get('batch_name', '')
        status = request.args.get('status', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))

        if not db.connect():
            return jsonify({'code': 500, 'message': '数据库连接失败'}), 500

        # 构建查询条件
        conditions = []
        params = []
        if batch_name:
            conditions.append("batch_name LIKE %s")
            params.append(f'%{batch_name}%')
        if status != '':
            conditions.append("status = %s")
            params.append(int(status))

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        # 查询总数
        count_sql = f"SELECT COUNT(*) FROM invite_codes{where_clause}"
        total = db.fetch_one(count_sql, params)[0]

        # 查询列表
        offset = (page - 1) * page_size
        list_sql = f"""
            SELECT id, code, batch_name, max_usage, used_count, status,
                   valid_from, valid_until, created_by, created_at
            FROM invite_codes
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([page_size, offset])

        results = db.execute(list_sql, params)

        codes = []
        for row in results:
            codes.append({
                'id': row[0],
                'code': row[1],
                'batch_name': row[2],
                'max_usage': row[3],
                'used_count': row[4],
                'status': row[5],
                'valid_from': row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None,
                'valid_until': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None,
                'created_by': row[8],
                'created_at': row[9].strftime('%Y-%m-%d %H:%M:%S')
            })

        db.close()

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'list': codes
            }
        })
    except Exception as e:
        if db.connection:
            db.close()
        return jsonify({'code': 500, 'message': str(e)}), 500


@invite_bp.route('/delete', methods=['POST'])
def delete_invite_codes():
    """
    删除邀请码

    POST /api/invite/delete
    Body: {
        "ids": [1, 2, 3]
    }
    """
    try:
        data = request.get_json()
        ids = data.get('ids', [])

        if not ids:
            return jsonify({'code': 400, 'message': '请选择要删除的邀请码'}), 400

        if not db.connect():
            return jsonify({'code': 500, 'message': '数据库连接失败'}), 500

        placeholders = ','.join(['%s'] * len(ids))
        sql = f"DELETE FROM invite_codes WHERE id IN ({placeholders})"
        db.execute(sql, ids)

        db.close()

        return jsonify({
            'code': 200,
            'message': f'成功删除{len(ids)}个邀请码'
        })
    except Exception as e:
        if db.connection:
            db.close()
        return jsonify({'code': 500, 'message': str(e)}), 500


@invite_bp.route('/export', methods=['POST'])
def export_invite_codes():
    """
    导出邀请码到Excel

    POST /api/invite/export
    Body: {
        "batch_name": "活动A",
        "quantity": 100
    }
    """
    try:
        data = request.get_json()
        batch_name = data.get('batch_name', f'批次_{datetime.now().strftime("%Y%m%d%H%M%S")}')
        quantity = data.get('quantity', 1)

        if not db.connect():
            return jsonify({'code': 500, 'message': '数据库连接失败'}), 500

        # 查询该批次的邀请码
        sql = """
            SELECT code, max_usage, used_count, status,
                   valid_from, valid_until, created_at
            FROM invite_codes
            WHERE batch_name = %s
            ORDER BY id
        """
        results = db.execute(sql, (batch_name,))

        db.close()

        # 生成CSV格式数据（简单实现，生产环境建议使用openpyxl）
        import io
        import csv

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['邀请码', '批次名称', '最大使用次数', '已使用次数', '状态',
                        '有效期开始', '有效期结束', '创建时间'])

        for row in results:
            code, max_usage, used_count, status, valid_from, valid_until, created_at = row
            writer.writerow([
                code,
                batch_name,
                max_usage,
                used_count,
                '有效' if status == 1 else '禁用',
                valid_from.strftime('%Y-%m-%d %H:%M:%S') if valid_from else '',
                valid_until.strftime('%Y-%m-%d %H:%M:%S') if valid_until else '',
                created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        # 返回CSV文件
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'邀请码_{batch_name}_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    except Exception as e:
        if db.connection:
            db.close()
        return jsonify({'code': 500, 'message': str(e)}), 500


@invite_bp.route('/disable', methods=['POST'])
def disable_invite_codes():
    """
    禁用/启用邀请码

    POST /api/invite/disable
    Body: {
        "ids": [1, 2, 3],
        "status": 0
    }
    """
    try:
        data = request.get_json()
        ids = data.get('ids', [])
        status = data.get('status', 0)

        if not ids:
            return jsonify({'code': 400, 'message': '请选择要操作的邀请码'}), 400

        if not db.connect():
            return jsonify({'code': 500, 'message': '数据库连接失败'}), 500

        placeholders = ','.join(['%s'] * len(ids))
        sql = f"UPDATE invite_codes SET status = %s WHERE id IN ({placeholders})"
        db.execute(sql, [status] + ids)

        db.close()

        return jsonify({
            'code': 200,
            'message': f'成功更新{len(ids)}个邀请码状态'
        })
    except Exception as e:
        if db.connection:
            db.close()
        return jsonify({'code': 500, 'message': str(e)}), 500
