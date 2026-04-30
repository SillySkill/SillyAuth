"""
AI生成API
"""
import os
import uuid
import time
import random
from flask import Blueprint, request, jsonify

generate_bp = Blueprint('generate', __name__)

# 模拟任务存储
GENERATION_TASKS = {}


@generate_bp.route('/generate', methods=['POST'])
def create_generation():
    """
    创建AI生成任务
    
    POST /api/generate
    Body: {
        "style_id": "jst100001",
        "image_url": "https://oss.example.com/user.jpg",
        "reference_images": []
    }
    """
    try:
        data = request.get_json()
        style_id = data.get('style_id')
        image_url = data.get('image_url')
        reference_images = data.get('reference_images', [])
        
        # 生成任务ID
        task_id = f"task_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # 创建任务
        task = {
            'task_id': task_id,
            'style_id': style_id,
            'image_url': image_url,
            'reference_images': reference_images,
            'status': 'processing',
            'created_at': int(time.time()),
            'estimated_time': random.randint(20, 40)
        }
        
        GENERATION_TASKS[task_id] = task
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'task_id': task_id,
                'status': 'processing',
                'estimated_time': task['estimated_time']
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500


@generate_bp.route('/generation/status', methods=['GET'])
def get_generation_status():
    """
    查询生成状态
    
    GET /api/generation/status?task_id={task_id}
    """
    try:
        task_id = request.args.get('task_id')
        
        if task_id not in GENERATION_TASKS:
            return jsonify({
                'code': 404,
                'message': '任务不存在'
            }), 404
        
        task = GENERATION_TASKS[task_id]
        
        # 模拟任务完成（实际应用中应该调用火山引擎API查询）
        elapsed = int(time.time()) - task['created_at']
        if elapsed >= task['estimated_time']:
            task['status'] = 'completed'
            task['result_url'] = f"https://oss.example.com/result/{task_id}.jpg"
            task['completed_at'] = int(time.time())
        
        return jsonify({
            'code': 200,
            'data': task
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500
