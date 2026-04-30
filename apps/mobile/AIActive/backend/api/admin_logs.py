"""
后台管理 - 操作日志API
提供操作日志查询、统计分析、日志清理等功能
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.auth import token_required, admin_role_required
from database_admin import get_db
from models_admin import AdminOperationLog, AdminUser

# 创建蓝图
logs_bp = Blueprint('admin_logs', __name__)


@logs_bp.route('/api/admin/logs', methods=['GET'])
@token_required
@admin_role_required(1)  # 仅超级管理员可查看
async def get_logs_list():
    """
    获取操作日志列表（分页、筛选）

    Query Parameters:
        page: 页码（默认1）
        page_size: 每页数量（默认20）
        admin_id: 管理员ID筛选
        operation: 操作类型筛选
        resource_type: 资源类型筛选
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）

    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {
                "list": [...],
                "total": 100,
                "page": 1,
                "page_size": 20
            }
        }
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        admin_id = request.args.get('admin_id')
        operation = request.args.get('operation')
        resource_type = request.args.get('resource_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        async for db in get_db():
            query = select(AdminOperationLog)

            # 筛选条件
            if admin_id:
                query = query.where(AdminOperationLog.admin_id == int(admin_id))
            if operation:
                query = query.where(AdminOperationLog.operation == operation)
            if resource_type:
                query = query.where(AdminOperationLog.resource_type == resource_type)
            if start_date:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.where(AdminOperationLog.created_at >= start_datetime)
            if end_date:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                query = query.where(AdminOperationLog.created_at < end_datetime)

            # 获取总数
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await db.execute(count_query)
            total = total_result.scalar()

            # 分页查询
            query = query.order_by(AdminOperationLog.created_at.desc())
            query = query.offset((page - 1) * page_size).limit(page_size)

            result = await db.execute(query)
            logs = result.scalars().all()

            logs_list = []
            for log in logs:
                # 获取管理员信息
                admin = None
                if log.admin_id:
                    admin_result = await db.execute(
                        select(AdminUser).where(AdminUser.id == log.admin_id)
                    )
                    admin_user = admin_result.scalar_one_or_none()
                    if admin_user:
                        admin = {
                            'id': admin_user.id,
                            'username': admin_user.username,
                            'real_name': admin_user.real_name
                        }

                logs_list.append({
                    'id': log.id,
                    'admin': admin,
                    'operation': log.operation,
                    'resource_type': log.resource_type,
                    'resource_id': log.resource_id,
                    'operation_desc': log.operation_desc,
                    'request_ip': log.request_ip,
                    'user_agent': log.user_agent,
                    'status': log.status,
                    'created_at': log.created_at.isoformat() if log.created_at else None,
                })

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'list': logs_list,
                    'total': total,
                    'page': page,
                    'page_size': page_size
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取操作日志失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取操作日志失败: {str(e)}'
        }), 500


@logs_bp.route('/api/admin/logs/<int:log_id>', methods=['GET'])
@token_required
@admin_role_required(1)
async def get_log_detail(log_id):
    """
    获取日志详情

    Path Parameters:
        log_id: 日志ID

    Returns:
        日志详细信息
    """
    try:
        async for db in get_db():
            result = await db.execute(
                select(AdminOperationLog).where(AdminOperationLog.id == log_id)
            )
            log = result.scalar_one_or_none()

            if not log:
                return jsonify({
                    'code': 404,
                    'message': '日志不存在'
                }), 404

            # 获取管理员信息
            admin = None
            if log.admin_id:
                admin_result = await db.execute(
                    select(AdminUser).where(AdminUser.id == log.admin_id)
                )
                admin_user = admin_result.scalar_one_or_none()
                if admin_user:
                    admin = {
                        'id': admin_user.id,
                        'username': admin_user.username,
                        'real_name': admin_user.real_name,
                        'email': admin_user.email
                    }

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'id': log.id,
                    'admin': admin,
                    'operation': log.operation,
                    'resource_type': log.resource_type,
                    'resource_id': log.resource_id,
                    'operation_desc': log.operation_desc,
                    'request_ip': log.request_ip,
                    'user_agent': log.user_agent,
                    'status': log.status,
                    'created_at': log.created_at.isoformat() if log.created_at else None,
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取日志详情失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取日志详情失败: {str(e)}'
        }), 500


@logs_bp.route('/api/admin/logs/stats', methods=['GET'])
@token_required
@admin_role_required(1)
async def get_logs_stats():
    """
    获取日志统计信息

    Query Parameters:
        days: 统计天数（默认7天）

    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {
                "total_operations": 1000,
                "success_operations": 950,
                "failed_operations": 50,
                "operation_stats": {
                    "login": 100,
                    "create_app": 50,
                    ...
                }
            }
        }
    """
    try:
        days = int(request.args.get('days', 7))

        async for db in get_db():
            # 计算起始日期
            start_date = datetime.utcnow() - timedelta(days=days)

            # 总操作数
            total_operations = await db.scalar(
                select(func.count())
                .select_from(AdminOperationLog)
                .where(AdminOperationLog.created_at >= start_date)
            )

            # 成功操作数
            success_operations = await db.scalar(
                select(func.count())
                .select_from(AdminOperationLog)
                .where(
                    AdminOperationLog.created_at >= start_date,
                    AdminOperationLog.status == 1
                )
            )

            # 失败操作数
            failed_operations = await db.scalar(
                select(func.count())
                .select_from(AdminOperationLog)
                .where(
                    AdminOperationLog.created_at >= start_date,
                    AdminOperationLog.status == 0
                )
            )

            # 按操作类型统计
            result = await db.execute(
                select(AdminOperationLog.operation, func.count())
                .where(AdminOperationLog.created_at >= start_date)
                .group_by(AdminOperationLog.operation)
            )
            operation_stats = {op: count for op, count in result.all()}

            # 按管理员统计
            result = await db.execute(
                select(AdminOperationLog.admin_id, func.count())
                .where(AdminOperationLog.created_at >= start_date)
                .group_by(AdminOperationLog.admin_id)
                .order_by(func.count().desc())
                .limit(10)
            )
            top_admins = []
            for admin_id, count in result.all():
                admin_result = await db.execute(
                    select(AdminUser).where(AdminUser.id == admin_id)
                )
                admin_user = admin_result.scalar_one_or_none()
                if admin_user:
                    top_admins.append({
                        'id': admin_user.id,
                        'username': admin_user.username,
                        'real_name': admin_user.real_name,
                        'operation_count': count
                    })

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'total_operations': total_operations or 0,
                    'success_operations': success_operations or 0,
                    'failed_operations': failed_operations or 0,
                    'operation_stats': operation_stats,
                    'top_admins': top_admins
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取日志统计失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取日志统计失败: {str(e)}'
        }), 500


@logs_bp.route('/api/admin/logs/before/<date>', methods=['DELETE'])
@token_required
@admin_role_required(1)
async def delete_logs_before(date):
    """
    删除指定日期前的日志

    Path Parameters:
        date: 日期（YYYY-MM-DD）

    Returns:
        删除结果
    """
    try:
        target_date = datetime.strptime(date, '%Y-%m-%d')

        async for db in get_db():
            # 先统计要删除的数量
            count = await db.scalar(
                select(func.count())
                .select_from(AdminOperationLog)
                .where(AdminOperationLog.created_at < target_date)
            )

            # 删除指定日期前的日志
            await db.execute(
                delete(AdminOperationLog)
                .where(AdminOperationLog.created_at < target_date)
            )
            await db.commit()

            return jsonify({
                'code': 200,
                'message': '删除成功',
                'data': {
                    'deleted_count': count or 0
                }
            })

    except Exception as e:
        current_app.logger.error(f'删除日志失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'删除日志失败: {str(e)}'
        }), 500


@logs_bp.route('/api/admin/logs/operations', methods=['GET'])
@token_required
async def get_operation_types():
    """
    获取所有操作类型列表（用于筛选下拉框）

    Returns:
        操作类型列表
    """
    try:
        async for db in get_db():
            result = await db.execute(
                select(AdminOperationLog.operation)
                .distinct()
                .order_by(AdminOperationLog.operation)
            )
            operations = [row[0] for row in result.all() if row[0]]

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'operations': operations
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取操作类型失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取操作类型失败: {str(e)}'
        }), 500


@logs_bp.route('/api/admin/logs/export', methods=['GET'])
@token_required
@admin_role_required(1)
async def export_logs():
    """
    导出操作日志（CSV格式）

    Query Parameters:
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
        admin_id: 管理员ID筛选（可选）
        operation: 操作类型筛选（可选）

    Returns:
        CSV文件
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        admin_id = request.args.get('admin_id')
        operation = request.args.get('operation')

        if not start_date or not end_date:
            return jsonify({
                'code': 400,
                'message': '请指定开始和结束日期'
            }), 400

        async for db in get_db():
            query = select(AdminOperationLog)

            # 筛选条件
            if start_date:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.where(AdminOperationLog.created_at >= start_datetime)
            if end_date:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                query = query.where(AdminOperationLog.created_at < end_datetime)
            if admin_id:
                query = query.where(AdminOperationLog.admin_id == int(admin_id))
            if operation:
                query = query.where(AdminOperationLog.operation == operation)

            query = query.order_by(AdminOperationLog.created_at.desc())

            result = await db.execute(query)
            logs = result.scalars().all()

            # 构建CSV数据
            import csv
            from io import StringIO

            output = StringIO()
            writer = csv.writer(output)

            # 写入表头
            writer.writerow([
                'ID', '管理员', '操作', '资源类型', '资源ID',
                '操作描述', '请求IP', '状态', '创建时间'
            ])

            # 写入数据行
            for log in logs:
                # 获取管理员名称
                admin_name = ''
                if log.admin_id:
                    admin_result = await db.execute(
                        select(AdminUser).where(AdminUser.id == log.admin_id)
                    )
                    admin_user = admin_result.scalar_one_or_none()
                    if admin_user:
                        admin_name = admin_user.username

                writer.writerow([
                    log.id,
                    admin_name,
                    log.operation,
                    log.resource_type or '',
                    log.resource_id or '',
                    log.operation_desc or '',
                    log.request_ip or '',
                    '成功' if log.status == 1 else '失败',
                    log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else ''
                ])

            # 生成CSV文件
            csv_data = output.getvalue()

            from flask import Response
            response = Response(
                csv_data,
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=operation_logs_{start_date}_to_{end_date}.csv'
                }
            )

            return response

    except Exception as e:
        current_app.logger.error(f'导出日志失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'导出日志失败: {str(e)}'
        }), 500
