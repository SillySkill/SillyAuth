"""
文件上传API
"""
import os
import time
import uuid
from flask import Blueprint, request, jsonify

upload_bp = Blueprint('upload', __name__)

# 模拟上传存储和生成任务
UPLOADED_FILES = {}
GENERATION_TASKS = {}


@upload_bp.route('/', methods=['POST'])
def upload_file():
    """
    文件上传接口（通过代理）

    POST /api/upload
    Form Data:
        file: 文件内容
        source: 来源标识（camera/file）
        style_id: 风格ID（可选）
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'code': 400,
                'message': '没有上传文件'
            }), 400

        file = request.files['file']
        source = request.form.get('source', 'file')
        style_id = request.form.get('style_id', '')

        if file.filename == '':
            return jsonify({
                'code': 400,
                'message': '文件名为空'
            }), 400

        # 生成文件名和任务ID
        file_ext = os.path.splitext(file.filename)[1]
        timestamp = int(time.time())
        new_filename = f"{source}_{timestamp}_{uuid.uuid4().hex[:8]}{file_ext}"

        # 生成唯一的任务ID，用于轮询追踪
        task_id = f"task_{timestamp}_{uuid.uuid4().hex[:8]}"

        # 实际应用中应该上传到OSS
        file_url = f"https://oss.example.com/upload/{new_filename}"

        # 模拟保存文件信息
        UPLOADED_FILES[new_filename] = {
            'original_name': file.filename,
            'url': file_url,
            'source': source,
            'uploaded_at': timestamp
        }

        # 创建生成任务记录（初始状态为pending）
        GENERATION_TASKS[task_id] = {
            'task_id': task_id,
            'status': 'pending',
            'progress': 0,
            'status_text': '等待生成...',
            'file_url': file_url,
            'style_id': style_id,
            'created_at': timestamp,
            'updated_at': timestamp
        }

        return jsonify({
            'code': 200,
            'message': '上传成功',
            'data': {
                'file_url': file_url,
                'task_id': task_id  # 返回任务ID供手机端轮询使用
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500


@upload_bp.route('/files', methods=['GET'])
def list_files():
    """
    获取已上传文件列表

    GET /api/upload/files
    """
    try:
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': list(UPLOADED_FILES.values())
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500


@upload_bp.route('/query', methods=['GET'])
def query_generation_status():
    """
    查询生成任务状态

    GET /api/upload/query?limit=10

    返回最新的生成任务状态，用于手机端轮询
    """
    try:
        limit = int(request.args.get('limit', '1'))

        # 获取最新的生成任务
        tasks = list(GENERATION_TASKS.values())
        # 按创建时间倒序排序
        tasks.sort(key=lambda x: x.get('created_at', 0), reverse=True)

        # 返回最新的N个任务
        result = tasks[:limit]

        return jsonify({
            'code': 200,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500


@upload_bp.route('/task/update', methods=['POST'])
def update_generation_task():
    """
    更新生成任务状态（由APP端调用）

    POST /api/upload/task/update
    Body: {
        "task_id": "xxx",
        "status": "processing|completed|failed",
        "progress": 50,
        "result_url": "https://...",
        "error": "错误信息"
    }
    """
    try:
        data = request.get_json()
        task_id = data.get('task_id')

        if not task_id:
            return jsonify({
                'code': 400,
                'message': '缺少task_id'
            }), 400

        # 更新或创建任务
        if task_id not in GENERATION_TASKS:
            GENERATION_TASKS[task_id] = {
                'task_id': task_id,
                'created_at': int(time.time())
            }

        task = GENERATION_TASKS[task_id]

        # 更新任务状态
        if 'status' in data:
            task['status'] = data['status']
        if 'progress' in data:
            task['progress'] = data['progress']
        if 'result_url' in data:
            task['result_url'] = data['result_url']
        if 'error' in data:
            task['error'] = data['error']
        if 'status_text' in data:
            task['status_text'] = data['status_text']

        # 记录更新时间
        task['updated_at'] = int(time.time())

        return jsonify({
            'code': 200,
            'message': '任务状态已更新'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500
