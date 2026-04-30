"""
AI活动秀 - Flask后端应用
"""
import os
import sys
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入API路由
from api import (
    config_bp, generate_bp, upload_bp, invite_bp, payment_bp,
    auth_bp, apps_bp, modules_bp, assets_bp, devices_bp, push_bp,
    users_bp, logs_bp, stats_bp
)

# 导入WebSocket服务
from websocket_server import init_websocket

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 注册蓝图 - 现有API
app.register_blueprint(config_bp, url_prefix='/api/config')
app.register_blueprint(generate_bp, url_prefix='/api')
app.register_blueprint(upload_bp, url_prefix='/api/upload')
app.register_blueprint(invite_bp, url_prefix='/api/invite')
app.register_blueprint(payment_bp, url_prefix='/api/payment')

# 注册蓝图 - 后台管理API
app.register_blueprint(auth_bp)
app.register_blueprint(apps_bp)
app.register_blueprint(modules_bp)
app.register_blueprint(assets_bp)
app.register_blueprint(devices_bp)
app.register_blueprint(push_bp)
app.register_blueprint(users_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(stats_bp)

# 初始化WebSocket服务
ws_server = init_websocket(app)


@app.route('/')
def index():
    """健康检查"""
    return jsonify({
        'code': 200,
        'message': 'AI活动秀 API服务正在运行',
        'version': '1.0.0'
    })


@app.route('/health')
def health():
    """健康检查端点"""
    return jsonify({'status': 'healthy'})


@app.route('/upload')
def upload_page():
    """手机端上传页面"""
    try:
        # 获取项目根目录的上一级（即backend的父目录）
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        html_path = os.path.join(base_dir, 'upload_final.html')

        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return jsonify({
                'code': 404,
                'message': f'上传页面文件不存在: {html_path}'
            }), 404
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'加载上传页面失败: {str(e)}'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'code': 404,
        'message': '请求的资源不存在'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'code': 500,
        'message': '服务器内部错误'
    }), 500


if __name__ == '__main__':
    # 开发环境
    if os.getenv('FLASK_ENV') == 'development':
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        # 生产环境使用gunicorn
        pass
