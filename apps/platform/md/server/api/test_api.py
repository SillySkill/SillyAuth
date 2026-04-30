# -*- coding: utf-8 -*-
"""
应用管理 API 测试脚本
用于快速测试 API 端点是否正常工作
"""
import requests
import json

BASE_URL = "http://api.jcoding.tech/api/admin"


def print_response(response):
    """打印响应结果"""
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print("-" * 80)


def test_get_apps():
    """测试获取应用列表"""
    print("\n【测试】获取应用列表")
    response = requests.get(f"{BASE_URL}/apps", params={
        'page': 1,
        'page_size': 10
    })
    print_response(response)


def test_create_app():
    """测试创建应用"""
    print("\n【测试】创建应用")
    data = {
        "app_name": "测试应用",
        "app_type": "android",
        "package_name": "com.test.app",
        "platform": "android",
        "version": "1.0.0",
        "description": "这是一个测试应用"
    }
    response = requests.post(f"{BASE_URL}/apps", json=data)
    print_response(response)


def test_get_devices():
    """测试获取设备列表"""
    print("\n【测试】获取设备列表")
    response = requests.get(f"{BASE_URL}/devices", params={
        'page': 1,
        'page_size': 10
    })
    print_response(response)


def test_get_configs():
    """测试获取配置列表"""
    print("\n【测试】获取配置列表")
    response = requests.get(f"{BASE_URL}/configs", params={
        'page': 1,
        'page_size': 10
    })
    print_response(response)


def test_create_config():
    """测试创建配置"""
    print("\n【测试】创建配置")
    data = {
        "config_name": "测试配置",
        "config_key": "test_config_001",
        "config_version": "v1.0.0",
        "config_data": {
            "theme": "dark",
            "language": "zh-CN"
        },
        "config_type": "global"
    }
    response = requests.post(f"{BASE_URL}/configs", json=data)
    print_response(response)


def test_get_styles():
    """测试获取风格列表"""
    print("\n【测试】获取风格列表")
    response = requests.get(f"{BASE_URL}/styles", params={
        'page': 1,
        'page_size': 10
    })
    print_response(response)


def test_get_question_banks():
    """测试获取题库列表"""
    print("\n【测试】获取题库列表")
    response = requests.get(f"{BASE_URL}/question-banks", params={
        'page': 1,
        'page_size': 10
    })
    print_response(response)


def test_get_statistics():
    """测试获取统计信息"""
    print("\n【测试】获取统计信息")
    response = requests.get(f"{BASE_URL}/statistics")
    print_response(response)


def test_get_audit_logs():
    """测试获取审计日志"""
    print("\n【测试】获取审计日志")
    response = requests.get(f"{BASE_URL}/audit-logs", params={
        'page': 1,
        'page_size': 10
    })
    print_response(response)


def test_create_push():
    """测试创建推送任务"""
    print("\n【测试】创建推送任务")
    data = {
        "push_type": "config",
        "target_type": "device",
        "target_ids": ["device_001", "device_002"],
        "title": "测试推送",
        "content": "这是一个测试推送",
        "push_data": {
            "config_id": 1,
            "config_key": "test_config"
        }
    }
    response = requests.post(f"{BASE_URL}/push/batch", json=data)
    print_response(response)


def main():
    """主测试函数"""
    print("=" * 80)
    print("应用管理 API 测试")
    print("=" * 80)

    try:
        # 基础查询测试
        test_get_apps()
        test_get_devices()
        test_get_configs()
        test_get_styles()
        test_get_question_banks()
        test_get_statistics()
        test_get_audit_logs()

        # 创建测试 (注意: 这些会创建实际数据，谨慎使用)
        # test_create_app()
        # test_create_config()
        # test_create_push()

        print("\n【测试完成】所有测试已完成")

    except requests.exceptions.ConnectionError:
        print("\n【错误】无法连接到服务器，请确保服务已启动")
    except Exception as e:
        print(f"\n【错误】测试过程中出现错误: {str(e)}")


if __name__ == "__main__":
    main()
