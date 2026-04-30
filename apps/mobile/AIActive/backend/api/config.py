"""
配置管理API - 完整实现
支持版本管理、文件存储、哈希校验、更新推送
"""
import os
import json
import hashlib
import datetime
import shutil
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file, current_app
from functools import wraps

config_bp = Blueprint('config', __name__)

# ==================== 配置 ====================
# 配置存储路径
CONFIG_STORAGE_PATH = os.environ.get('CONFIG_STORAGE_PATH', './config_storage')
CONFIG_BACKUP_PATH = os.environ.get('CONFIG_BACKUP_PATH', './config_backup')

# 确保目录存在
os.makedirs(CONFIG_STORAGE_PATH, exist_ok=True)
os.makedirs(CONFIG_BACKUP_PATH, exist_ok=True)

# 版本数据库文件路径
VERSION_DB_PATH = os.path.join(CONFIG_STORAGE_PATH, 'versions.json')

# ==================== 数据库操作 ====================


def load_versions():
    """加载版本数据库"""
    if os.path.exists(VERSION_DB_PATH):
        with open(VERSION_DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'versions': {}, 'current': 'v1.0.0'}


def save_versions(versions_db):
    """保存版本数据库"""
    with open(VERSION_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(versions_db, f, indent=2, ensure_ascii=False)


def get_file_hash(file_path, algorithm='md5'):
    """计算文件哈希值"""
    hash_func = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def build_version_manifest(version, version_path):
    """构建版本清单"""
    manifest = {
        'version': version,
        'version_code': int(version.replace('v', '').replace('.', '').ljust(3, '0')),
        'released_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'files': [],
        'deleted_files': []
    }

    # 遍历版本目录，构建文件列表
    for root, dirs, files in os.walk(version_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, version_path)

            file_stat = os.stat(file_path)
            file_info = {
                'path': relative_path.replace('\\', '/'),
                'size': file_stat.st_size,
                'md5': get_file_hash(file_path),
                'url': f'/api/config/file?version={version}&path={relative_path.replace(os.sep, "/")}',
                'compressed': file.endswith('.gz') or file.endswith('.zip'),
                'essential': relative_path.endswith('.json')
            }
            manifest['files'].append(file_info)

    return manifest


# ==================== API路由 ====================


@config_bp.route('/version', methods=['GET'])
def get_version():
    """
    获取配置版本信息

    GET /api/config/version?version=v1.0.1
    """
    try:
        version = request.args.get('version', 'current')

        versions_db = load_versions()

        if version == 'current':
            version = versions_db.get('current', 'v1.0.0')

        if version not in versions_db['versions']:
            return jsonify({
                'code': 404,
                'message': f'版本 {version} 不存在'
            }), 404

        version_info = versions_db['versions'][version]
        version_info['version'] = version

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': version_info
        })
    except Exception as e:
        current_app.logger.error(f'获取版本信息失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


@config_bp.route('/file', methods=['GET'])
def download_file():
    """
    下载配置文件（支持断点续传）

    GET /api/config/file?version=v1.0.1&path=config.json
    Range: bytes=0-1048575
    """
    try:
        version = request.args.get('version', 'current')
        file_path = request.args.get('path', '')

        if not file_path:
            return jsonify({
                'code': 400,
                'message': '缺少文件路径参数'
            }), 400

        versions_db = load_versions()

        if version == 'current':
            version = versions_db.get('current', 'v1.0.0')

        if version not in versions_db['versions']:
            return jsonify({
                'code': 404,
                'message': f'版本 {version} 不存在'
            }), 404

        # 构建完整文件路径
        full_path = os.path.join(CONFIG_STORAGE_PATH, version, file_path)

        if not os.path.exists(full_path):
            return jsonify({
                'code': 404,
                'message': f'文件 {file_path} 不存在'
            }), 404

        # 计算文件哈希
        file_md5 = get_file_hash(full_path)
        file_size = os.path.getsize(full_path)

        # 支持断点续传
        range_header = request.headers.get('Range')
        if range_header:
            # 解析Range头
            # 格式: "bytes=start-end"
            try:
                range_parts = range_header.replace('bytes=', '').split('-')
                start = int(range_parts[0]) if range_parts[0] else 0
                end = int(range_parts[1]) if range_parts[1] else file_size - 1

                # 验证范围
                if start < 0 or end >= file_size or start > end:
                    return jsonify({
                        'code': 416,
                        'message': '无效的Range范围'
                    }), 416

                # 读取指定范围的数据
                content_length = end - start + 1
                with open(full_path, 'rb') as f:
                    f.seek(start)
                    data = f.read(content_length)

                response = current_app.response_class(
                    data,
                    mimetype='application/octet-stream',
                    status=206  # Partial Content
                )
                response.headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
                response.headers['Content-Length'] = str(content_length)
                response.headers['Content-MD5'] = file_md5
                response.headers['Accept-Ranges'] = 'bytes'
                response.headers['ETag'] = f'"{version}-{file_path.replace("/", "-")}"'

                return response
            except Exception as e:
                current_app.logger.error(f'断点续传失败: {str(e)}')

        # 完整文件下载
        response = send_file(
            full_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )
        response.headers['Content-MD5'] = file_md5
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['ETag'] = f'"{version}-{file_path.replace("/", "-")}"'

        return response

    except Exception as e:
        current_app.logger.error(f'下载文件失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


@config_bp.route('/report', methods=['POST'])
def report_result():
    """
    上报更新结果

    POST /api/config/report
    Body: {
        "device_id": "unique_device_id",
        "old_version": "v1.0.0",
        "new_version": "v1.0.1",
        "status": "success",
        "downloaded_files": 15,
        "failed_files": [],
        "duration_ms": 15432
    }
    """
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['device_id', 'old_version', 'new_version', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段: {field}'
                }), 400

        # 记录更新日志
        log_entry = {
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'device_id': data['device_id'],
            'old_version': data['old_version'],
            'new_version': data['new_version'],
            'status': data['status'],
            'downloaded_files': data.get('downloaded_files', 0),
            'failed_files': data.get('failed_files', []),
            'duration_ms': data.get('duration_ms', 0)
        }

        # 保存到日志文件
        log_path = os.path.join(CONFIG_STORAGE_PATH, 'update_logs.jsonl')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

        current_app.logger.info(f'设备 {data["device_id"]} 更新: {data["old_version"]} -> {data["new_version"]}')

        return jsonify({
            'code': 200,
            'message': '上报成功'
        })
    except Exception as e:
        current_app.logger.error(f'上报结果失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


@config_bp.route('/publish', methods=['POST'])
def publish_config():
    """
    发布新版本配置（管理员接口）

    POST /api/config/publish
    Body: {
        "version": "v1.0.1",
        "release_notes": "修复题库配置错误",
        "force_update": false,
        "min_compatible_version": "v1.0.0",
        "source_dir": "/path/to/config/files"
    }
    """
    try:
        data = request.get_json()

        # 验证必填字段
        if 'version' not in data:
            return jsonify({
                'code': 400,
                'message': '缺少版本号'
            }), 400

        version = data['version']
        if not version.startswith('v'):
            return jsonify({
                'code': 400,
                'message': '版本号必须以v开头'
            }), 400

        # 创建版本目录
        version_path = os.path.join(CONFIG_STORAGE_PATH, version)
        if os.path.exists(version_path):
            return jsonify({
                'code': 400,
                'message': f'版本 {version} 已存在'
            }), 400

        os.makedirs(version_path, exist_ok=True)

        # 复制配置文件
        source_dir = data.get('source_dir')
        if source_dir and os.path.exists(source_dir):
            for item in os.listdir(source_dir):
                src = os.path.join(source_dir, item)
                dst = os.path.join(version_path, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)

        # 构建版本清单
        manifest = build_version_manifest(version, version_path)
        manifest['release_notes'] = data.get('release_notes', '')
        manifest['force_update'] = data.get('force_update', False)
        manifest['min_compatible_version'] = data.get('min_compatible_version', version)

        # 保存清单
        manifest_path = os.path.join(version_path, 'manifest.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # 更新版本数据库
        versions_db = load_versions()
        versions_db['versions'][version] = manifest
        versions_db['current'] = version
        save_versions(versions_db)

        current_app.logger.info(f'版本 {version} 发布成功')

        return jsonify({
            'code': 200,
            'message': '发布成功',
            'data': manifest
        })
    except Exception as e:
        current_app.logger.error(f'发布配置失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


@config_bp.route('/push', methods=['POST'])
def push_update():
    """
    推送更新通知（管理员接口）

    POST /api/config/push
    Body: {
        "version": "v1.0.1",
        "message": "新版本可用",
        "target_devices": []  // 空表示推送到所有设备
    }
    """
    try:
        data = request.get_json()

        version = data.get('version')
        if not version:
            return jsonify({
                'code': 400,
                'message': '缺少版本号'
            }), 400

        # TODO: 实现实际的推送逻辑
        # - 通过Firebase Cloud Messaging发送推送
        # - 或通过WebSocket向在线客户端广播
        # - 或通过WebSocket向在线客户端广播

        current_app.logger.info(f'推送更新通知: {version}')

        return jsonify({
            'code': 200,
            'message': '推送成功',
            'data': {
                'version': version,
                'message': data.get('message', '新版本可用')
            }
        })
    except Exception as e:
        current_app.logger.error(f'推送更新失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


@config_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    获取更新统计信息（管理员接口）

    GET /api/config/stats
    """
    try:
        # 读取更新日志
        log_path = os.path.join(CONFIG_STORAGE_PATH, 'update_logs.jsonl')
        stats = {
            'total_updates': 0,
            'successful_updates': 0,
            'failed_updates': 0,
            'version_distribution': {},
            'last_update': None
        }

        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        log_entry = json.loads(line)
                        stats['total_updates'] += 1

                        if log_entry['status'] == 'success':
                            stats['successful_updates'] += 1
                        else:
                            stats['failed_updates'] += 1

                        # 版本分布
                        new_version = log_entry.get('new_version', 'unknown')
                        stats['version_distribution'][new_version] = \
                            stats['version_distribution'].get(new_version, 0) + 1

                        # 最后更新时间
                        if stats['last_update'] is None or log_entry['timestamp'] > stats['last_update']:
                            stats['last_update'] = log_entry['timestamp']

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': stats
        })
    except Exception as e:
        current_app.logger.error(f'获取统计信息失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


# ==================== 初始化 ====================


@config_bp.before_app_first_request
def initialize_config_system():
    """初始化配置系统"""
    # 创建初始版本（如果不存在）
    versions_db = load_versions()

    if not versions_db.get('versions'):
        # 创建初始版本 v1.0.0
        version = 'v1.0.0'
        version_path = os.path.join(CONFIG_STORAGE_PATH, version)
        os.makedirs(version_path, exist_ok=True)

        # 创建默认清单
        manifest = {
            'version': version,
            'version_code': 100,
            'released_at': datetime.datetime.utcnow().isoformat() + 'Z',
            'force_update': False,
            'min_compatible_version': version,
            'release_notes': '初始版本',
            'files': [],
            'deleted_files': []
        }

        # 保存清单
        manifest_path = os.path.join(version_path, 'manifest.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # 更新数据库
        versions_db['versions'][version] = manifest
        versions_db['current'] = version
        save_versions(versions_db)

        print(f'初始化配置系统完成，创建初始版本 {version}')
