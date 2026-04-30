"""
后台管理 - 素材管理API
支持文件上传到阿里云OSS、素材管理、批量操作
"""
import os
import uuid
import hashlib
from datetime import datetime
from flask import Blueprint, request, jsonify, g, current_app
from werkzeug.utils import secure_filename
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from middleware.auth import token_required, admin_role_required
from database_admin import get_db
from models_admin import AppAsset, App

# 尝试导入阿里云OSS SDK
try:
    import oss2
    OSS_AVAILABLE = True
except ImportError:
    OSS_AVAILABLE = False
    current_app.logger.warning('阿里云OSS SDK未安装，文件上传功能将不可用')

# 创建蓝图
assets_bp = Blueprint('admin_assets', __name__)

# 允许的文件类型
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'aac', 'm4a'}
ALLOWED_CONFIG_EXTENSIONS = {'json', 'xml', 'txt'}

# 文件大小限制（字节）
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def get_oss_bucket():
    """获取OSS Bucket对象"""
    if not OSS_AVAILABLE:
        return None

    auth = oss2.Auth(
        os.getenv('OSS_ACCESS_KEY_ID'),
        os.getenv('OSS_ACCESS_KEY_SECRET')
    )
    bucket = oss2.Bucket(
        auth,
        os.getenv('OSS_ENDPOINT'),
        os.getenv('OSS_BUCKET_NAME')
    )
    return bucket


def allowed_file(filename, asset_type):
    """检查文件类型是否允许"""
    filename = secure_filename(filename)
    if '.' not in filename:
        return False

    ext = filename.rsplit('.', 1)[1].lower()

    if asset_type == 'image':
        return ext in ALLOWED_IMAGE_EXTENSIONS
    elif asset_type == 'video':
        return ext in ALLOWED_VIDEO_EXTENSIONS
    elif asset_type == 'audio':
        return ext in ALLOWED_AUDIO_EXTENSIONS
    elif asset_type in ['config', 'banner']:
        return ext in ALLOWED_CONFIG_EXTENSIONS
    else:
        return False


def calculate_file_hash(file_stream):
    """计算文件MD5哈希"""
    md5_hash = hashlib.md5()
    for chunk in iter(lambda: file_stream.read(8192), b''):
        md5_hash.update(chunk)
    file_stream.seek(0)  # 重置指针
    return md5_hash.hexdigest()


async def upload_file_to_oss(file, app_id, asset_type, filename):
    """
    上传文件到阿里云OSS

    Args:
        file: 文件对象
        app_id: 应用ID
        asset_type: 素材类型
        filename: 文件名

    Returns:
        (object_key, file_url, file_size, file_hash)
    """
    if not OSS_AVAILABLE:
        raise Exception('阿里云OSS SDK未安装')

    bucket = get_oss_bucket()

    # 生成唯一的对象键
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    unique_name = f'{uuid.uuid4().hex}.{ext}'
    object_key = f'admin/{app_id}/{asset_type}/{unique_name}'

    # 计算文件哈希
    file_hash = calculate_file_hash(file)

    # 读取文件内容
    file_content = file.read()
    file_size = len(file_content)

    # 上传到OSS
    bucket.put_object(object_key, file_content)

    # 生成访问URL
    endpoint = os.getenv('OSS_ENDPOINT')
    bucket_name = os.getenv('OSS_BUCKET_NAME')
    file_url = f'https://{bucket_name}.{endpoint}/{object_key}'

    return object_key, file_url, file_size, file_hash


@assets_bp.route('/api/admin/apps/<int:app_id>/assets/upload', methods=['POST'])
@token_required
async def upload_asset(app_id):
    """
    上传单个素材文件

    Path Parameters:
        app_id: 应用ID

    Form Data:
        file: 文件对象
        asset_type: 素材类型（image/video/audio/config/banner）
        module_key: 模块标识（可选）
        asset_name: 素材名称（可选，默认使用文件名）

    Returns:
        上传的素材信息
    """
    try:
        # 检查文件是否存在
        if 'file' not in request.files:
            return jsonify({
                'code': 400,
                'message': '未选择文件'
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'code': 400,
                'message': '未选择文件'
            }), 400

        # 获取参数
        asset_type = request.form.get('asset_type', 'image')
        module_key = request.form.get('module_key')
        asset_name = request.form.get('asset_name', file.filename)

        # 验证文件类型
        if not allowed_file(file.filename, asset_type):
            return jsonify({
                'code': 400,
                'message': f'不支持的文件类型，仅支持: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}'
            }), 400

        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'code': 400,
                'message': f'文件大小超过限制（最大{MAX_FILE_SIZE // (1024*1024)}MB）'
            }), 400

        async for db in get_db():
            # 检查应用是否存在
            app_result = await db.execute(
                select(App).where(App.id == app_id)
            )
            app = app_result.scalar_one_or_none()

            if not app:
                return jsonify({
                    'code': 404,
                    'message': '应用不存在'
                }), 404

            # 上传到OSS
            try:
                object_key, file_url, file_size, file_hash = await upload_file_to_oss(
                    file, app_id, asset_type, file.filename
                )
            except Exception as e:
                current_app.logger.error(f'文件上传失败: {str(e)}')
                return jsonify({
                    'code': 500,
                    'message': f'文件上传失败: {str(e)}'
                }), 500

            # 获取MIME类型
            mime_type = file.content_type

            # 创建素材记录
            asset = AppAsset(
                app_id=app_id,
                module_key=module_key,
                asset_type=asset_type,
                asset_key=f'{asset_type}_{uuid.uuid4().hex[:16]}',
                asset_name=asset_name,
                file_path=object_key,
                file_url=file_url,
                file_size=file_size,
                file_hash=file_hash,
                mime_type=mime_type,
                status=1,
                uploaded_by=g.current_admin_id
            )

            db.add(asset)
            await db.commit()
            await db.refresh(asset)

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='upload_asset',
                resource_type='asset',
                resource_id=asset.id,
                operation_desc=f'上传素材: {asset.asset_name}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '上传成功',
                'data': {
                    'id': asset.id,
                    'asset_key': asset.asset_key,
                    'asset_name': asset.asset_name,
                    'asset_type': asset.asset_type,
                    'file_url': asset.file_url,
                    'file_size': asset.file_size
                }
            })

    except Exception as e:
        current_app.logger.error(f'上传素材失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'上传素材失败: {str(e)}'
        }), 500


@assets_bp.route('/api/admin/apps/<int:app_id>/assets/batch-upload', methods=['POST'])
@token_required
async def batch_upload_assets(app_id):
    """
    批量上传素材文件

    Path Parameters:
        app_id: 应用ID

    Form Data:
        files: 多个文件对象
        asset_type: 素材类型
        module_key: 模块标识（可选）

    Returns:
        批量上传结果
    """
    try:
        # 检查文件是否存在
        if 'files' not in request.files:
            return jsonify({
                'code': 400,
                'message': '未选择文件'
            }), 400

        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({
                'code': 400,
                'message': '未选择文件'
            }), 400

        # 获取参数
        asset_type = request.form.get('asset_type', 'image')
        module_key = request.form.get('module_key')

        async for db in get_db():
            # 检查应用是否存在
            app_result = await db.execute(
                select(App).where(App.id == app_id)
            )
            app = app_result.scalar_one_or_none()

            if not app:
                return jsonify({
                    'code': 404,
                    'message': '应用不存在'
                }), 404

            success_count = 0
            failed_count = 0
            failed_files = []
            uploaded_assets = []

            # 逐个上传文件
            for file in files:
                try:
                    # 验证文件类型
                    if not allowed_file(file.filename, asset_type):
                        failed_count += 1
                        failed_files.append({
                            'filename': file.filename,
                            'reason': '不支持的文件类型'
                        })
                        continue

                    # 检查文件大小
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)

                    if file_size > MAX_FILE_SIZE:
                        failed_count += 1
                        failed_files.append({
                            'filename': file.filename,
                            'reason': '文件大小超过限制'
                        })
                        continue

                    # 上传到OSS
                    object_key, file_url, file_size, file_hash = await upload_file_to_oss(
                        file, app_id, asset_type, file.filename
                    )

                    # 创建素材记录
                    asset = AppAsset(
                        app_id=app_id,
                        module_key=module_key,
                        asset_type=asset_type,
                        asset_key=f'{asset_type}_{uuid.uuid4().hex[:16]}',
                        asset_name=file.filename,
                        file_path=object_key,
                        file_url=file_url,
                        file_size=file_size,
                        file_hash=file_hash,
                        mime_type=file.content_type,
                        status=1,
                        uploaded_by=g.current_admin_id
                    )

                    db.add(asset)
                    await db.flush()  # 获取ID但不提交

                    uploaded_assets.append({
                        'id': asset.id,
                        'asset_key': asset.asset_key,
                        'asset_name': asset.asset_name,
                        'file_url': asset.file_url
                    })

                    success_count += 1

                except Exception as e:
                    failed_count += 1
                    failed_files.append({
                        'filename': file.filename,
                        'reason': str(e)
                    })
                    current_app.logger.error(f'文件上传失败 {file.filename}: {str(e)}')

            # 提交所有成功的记录
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='batch_upload_assets',
                resource_type='asset',
                operation_desc=f'批量上传素材: 成功{success_count}个, 失败{failed_count}个',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '批量上传完成',
                'data': {
                    'success_count': success_count,
                    'failed_count': failed_count,
                    'failed_files': failed_files,
                    'uploaded_assets': uploaded_assets
                }
            })

    except Exception as e:
        current_app.logger.error(f'批量上传失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'批量上传失败: {str(e)}'
        }), 500


@assets_bp.route('/api/admin/apps/<int:app_id>/assets', methods=['GET'])
@token_required
async def get_assets_list(app_id):
    """
    获取素材列表（分页、筛选）

    Path Parameters:
        app_id: 应用ID

    Query Parameters:
        page: 页码（默认1）
        page_size: 每页数量（默认20）
        asset_type: 素材类型筛选
        module_key: 模块筛选
        keyword: 搜索关键词

    Returns:
        素材列表
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        asset_type = request.args.get('asset_type')
        module_key = request.args.get('module_key')
        keyword = request.args.get('keyword', '').strip()

        async for db in get_db():
            # 检查应用是否存在
            app_result = await db.execute(
                select(App).where(App.id == app_id)
            )
            app = app_result.scalar_one_or_none()

            if not app:
                return jsonify({
                    'code': 404,
                    'message': '应用不存在'
                }), 404

            # 构建查询
            query = select(AppAsset).where(AppAsset.app_id == app_id)

            # 筛选条件
            if asset_type:
                query = query.where(AppAsset.asset_type == asset_type)
            if module_key:
                query = query.where(AppAsset.module_key == module_key)
            if keyword:
                query = query.where(
                    (AppAsset.asset_name.like(f'%{keyword}%')) |
                    (AppAsset.asset_key.like(f'%{keyword}%'))
                )

            # 获取总数
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await db.execute(count_query)
            total = total_result.scalar()

            # 分页查询
            query = query.order_by(AppAsset.created_at.desc())
            query = query.offset((page - 1) * page_size).limit(page_size)

            result = await db.execute(query)
            assets = result.scalars().all()

            assets_list = []
            for asset in assets:
                assets_list.append({
                    'id': asset.id,
                    'asset_key': asset.asset_key,
                    'asset_name': asset.asset_name,
                    'asset_type': asset.asset_type,
                    'module_key': asset.module_key,
                    'file_url': asset.file_url,
                    'file_size': asset.file_size,
                    'mime_type': asset.mime_type,
                    'status': asset.status,
                    'created_at': asset.created_at.isoformat() if asset.created_at else None,
                })

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'list': assets_list,
                    'total': total,
                    'page': page,
                    'page_size': page_size
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取素材列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取素材列表失败: {str(e)}'
        }), 500


@assets_bp.route('/api/admin/apps/<int:app_id>/assets/<int:asset_id>', methods=['GET'])
@token_required
async def get_asset_detail(app_id, asset_id):
    """
    获取素材详情

    Path Parameters:
        app_id: 应用ID
        asset_id: 素材ID

    Returns:
        素材详细信息
    """
    try:
        async for db in get_db():
            result = await db.execute(
                select(AppAsset).where(
                    AppAsset.id == asset_id,
                    AppAsset.app_id == app_id
                )
            )
            asset = result.scalar_one_or_none()

            if not asset:
                return jsonify({
                    'code': 404,
                    'message': '素材不存在'
                }), 404

            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'id': asset.id,
                    'app_id': asset.app_id,
                    'module_key': asset.module_key,
                    'asset_type': asset.asset_type,
                    'asset_key': asset.asset_key,
                    'asset_name': asset.asset_name,
                    'file_path': asset.file_path,
                    'file_url': asset.file_url,
                    'file_size': asset.file_size,
                    'file_hash': asset.file_hash,
                    'mime_type': asset.mime_type,
                    'metadata': asset.metadata,
                    'status': asset.status,
                    'uploaded_by': asset.uploaded_by,
                    'created_at': asset.created_at.isoformat() if asset.created_at else None,
                    'updated_at': asset.updated_at.isoformat() if asset.updated_at else None,
                }
            })

    except Exception as e:
        current_app.logger.error(f'获取素材详情失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取素材详情失败: {str(e)}'
        }), 500


@assets_bp.route('/api/admin/apps/<int:app_id>/assets/<int:asset_id>', methods=['PUT'])
@token_required
async def update_asset(app_id, asset_id):
    """
    更新素材信息

    Path Parameters:
        app_id: 应用ID
        asset_id: 素材ID

    Request Body:
        {
            "asset_name": "新名称",
            "status": 1
        }

    Returns:
        更新结果
    """
    try:
        data = request.get_json()

        async for db in get_db():
            # 检查素材是否存在
            result = await db.execute(
                select(AppAsset).where(
                    AppAsset.id == asset_id,
                    AppAsset.app_id == app_id
                )
            )
            asset = result.scalar_one_or_none()

            if not asset:
                return jsonify({
                    'code': 404,
                    'message': '素材不存在'
                }), 404

            # 构建更新数据
            update_data = {}
            allowed_fields = ['asset_name', 'status', 'metadata']
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field]

            if not update_data:
                return jsonify({
                    'code': 400,
                    'message': '没有可更新的字段'
                }), 400

            # 执行更新
            await db.execute(
                update(AppAsset)
                .where(AppAsset.id == asset_id)
                .values(**update_data)
            )
            await db.commit()

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='update_asset',
                resource_type='asset',
                resource_id=asset_id,
                operation_desc=f'更新素材: {asset.asset_name}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '更新成功'
            })

    except Exception as e:
        current_app.logger.error(f'更新素材失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'更新素材失败: {str(e)}'
        }), 500


@assets_bp.route('/api/admin/apps/<int:app_id>/assets/<int:asset_id>', methods=['DELETE'])
@token_required
async def delete_asset(app_id, asset_id):
    """
    删除素材

    Path Parameters:
        app_id: 应用ID
        asset_id: 素材ID

    注意：仅删除数据库记录，OSS文件需要手动清理
    """
    try:
        async for db in get_db():
            # 检查素材是否存在
            result = await db.execute(
                select(AppAsset).where(
                    AppAsset.id == asset_id,
                    AppAsset.app_id == app_id
                )
            )
            asset = result.scalar_one_or_none()

            if not asset:
                return jsonify({
                    'code': 404,
                    'message': '素材不存在'
                }), 404

            asset_name = asset.asset_name
            file_path = asset.file_path

            # 删除数据库记录
            await db.execute(
                delete(AppAsset).where(AppAsset.id == asset_id)
            )
            await db.commit()

            # TODO: 可选 - 同时删除OSS文件
            # if OSS_AVAILABLE:
            #     bucket = get_oss_bucket()
            #     bucket.delete_object(file_path)

            # 记录操作日志
            await log_operation(
                db=db,
                admin_id=g.current_admin_id,
                operation='delete_asset',
                resource_type='asset',
                resource_id=asset_id,
                operation_desc=f'删除素材: {asset_name}',
                request_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )

            return jsonify({
                'code': 200,
                'message': '删除成功'
            })

    except Exception as e:
        current_app.logger.error(f'删除素材失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'删除素材失败: {str(e)}'
        }), 500


# ==================== 辅助函数 ====================

async def log_operation(db: AsyncSession, admin_id: int, operation: str,
                        operation_desc: str = None, resource_type: str = None,
                        resource_id: int = None, request_ip: str = None,
                        user_agent: str = None, status: int = 1):
    """记录管理员操作日志"""
    from models_admin import AdminOperationLog

    log = AdminOperationLog(
        admin_id=admin_id,
        operation=operation,
        resource_type=resource_type,
        resource_id=resource_id,
        operation_desc=operation_desc,
        request_ip=request_ip,
        user_agent=user_agent,
        status=status
    )

    db.add(log)
    await db.commit()
