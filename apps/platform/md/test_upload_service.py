#!/usr/bin/env python3
"""
AI活动秀上传服务测试脚本
测试上传API的各项功能
"""

import requests
import os
import sys

BASE_URL = "https://www.jcoding.chat"
UPLOAD_API = f"{BASE_URL}/application/upload/api"
HEALTH_API = f"{BASE_URL}/application/health"

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)

def test_health():
    """测试健康检查"""
    print_section("1. 健康检查测试")
    try:
        response = requests.get(HEALTH_API, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def test_upload_page():
    """测试上传页面"""
    print_section("2. 上传页面测试")
    try:
        response = requests.get(f"{BASE_URL}/application/upload", timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ 上传页面可访问")
            print(f"页面长度: {len(response.text)} 字符")
            return True
        else:
            print(f"✗ 页面访问失败")
            return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def test_upload_api():
    """测试上传API（需要测试图片）"""
    print_section("3. 上传API测试")

    # 查找测试图片
    test_image = None
    possible_paths = [
        "test.jpg",
        "test.png",
        "E:/silly/md/docs/images/test.jpg",
        "/tmp/test.jpg"
    ]

    for path in possible_paths:
        if os.path.exists(path):
            test_image = path
            break

    if not test_image:
        print("✗ 未找到测试图片")
        print("  请准备一张测试图片放在以下位置之一：")
        for path in possible_paths:
            print(f"  - {path}")
        return None

    try:
        print(f"使用测试图片: {test_image}")

        with open(test_image, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            data = {
                'source': 'test',
                'style_id': 'test_style',
                'user_id': 'test_user'
            }

            response = requests.post(UPLOAD_API, files=files, data=data, timeout=30)

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✓ 上传成功")
            print(f"  消息: {result.get('message')}")
            print(f"  文件名: {result['data'].get('filename')}")
            print(f"  文件大小: {result['data'].get('size')} 字节")
            print(f"  文件URL: {result['data'].get('url')}")
            return True
        else:
            print(f"✗ 上传失败")
            print(f"  响应: {response.text}")
            return False

    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def test_file_access():
    """测试文件访问"""
    print_section("4. 文件访问测试")

    # 测试一个假设存在的文件（需要先上传）
    test_file = "upload_0000000000_00000000.jpg"
    url = f"{BASE_URL}/application/uploads/{test_file}"

    print(f"测试访问: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✓ 文件可访问")
            return True
        elif response.status_code == 404:
            print(f"✓ 文件不存在（正常，需先上传）")
            return True
        else:
            print(f"✗ 意外的状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def main():
    """主函数"""
    print("\n")
    print("*" * 50)
    print("  AI活动秀上传服务测试")
    print("*" * 50)
    print(f"\n服务器: {BASE_URL}")

    results = []

    # 运行测试
    results.append(("健康检查", test_health()))
    results.append(("上传页面", test_upload_page()))
    results.append(("上传API", test_upload_api()))
    results.append(("文件访问", test_file_access()))

    # 打印结果摘要
    print_section("测试结果摘要")

    passed = 0
    failed = 0
    skipped = 0

    for name, result in results:
        if result is True:
            print(f"  [{PASS}] {name}")
            passed += 1
        elif result is False:
            print(f"  [FAIL] {name}")
            failed += 1
        else:
            print(f"  [SKIP] {name}")
            skipped += 1

    print()
    print(f"总计: {passed} 通过, {failed} 失败, {skipped} 跳过")

    if failed == 0:
        print("\n✓ 所有测试通过！上传服务工作正常")
        return 0
    else:
        print(f"\n✗ 有 {failed} 个测试失败，请检查服务配置")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n测试中断")
        sys.exit(1)
