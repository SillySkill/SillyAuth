"""
测试教程和下载资源API
"""
import os
import sys

# 添加server/api到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server', 'api'))

def test_api():
    """测试API端点"""
    import requests

    base_url = "http://47.96.133.238:8000"

    print("=" * 60)
    print("测试教程和下载资源API")
    print("=" * 60)

    # 测试教程列表
    print("\n1. 测试教程列表 API")
    print("-" * 60)
    try:
        response = requests.get(f"{base_url}/api/content/tutorials/?limit=5")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            print(f"总数: {data.get('data', {}).get('total')}")
            print(f"返回数量: {len(data.get('data', {}).get('items', []))}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试教程详情
    print("\n2. 测试教程详情 API (ID)")
    print("-" * 60)
    try:
        response = requests.get(f"{base_url}/api/content/tutorials/1")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            print(f"教程标题: {data.get('data', {}).get('title')}")
            print(f"章节数: {len(data.get('data', {}).get('chapters', []))}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试教程详情 (slug)
    print("\n3. 测试教程详情 API (slug)")
    print("-" * 60)
    try:
        response = requests.get(f"{base_url}/api/content/tutorials/claude-code-getting-started")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            print(f"教程标题: {data.get('data', {}).get('title')}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试下载列表
    print("\n4. 测试下载资源列表 API")
    print("-" * 60)
    try:
        response = requests.get(f"{base_url}/api/content/downloads/?limit=5")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            print(f"总数: {data.get('data', {}).get('total')}")
            print(f"返回数量: {len(data.get('data', {}).get('items', []))}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试下载详情
    print("\n5. 测试下载资源详情 API (ID)")
    print("-" * 60)
    try:
        response = requests.get(f"{base_url}/api/content/downloads/1")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            print(f"资源标题: {data.get('data', {}).get('title')}")
            print(f"版本数: {len(data.get('data', {}).get('versions', []))}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试下载详情 (slug)
    print("\n6. 测试下载资源详情 API (slug)")
    print("-" * 60)
    try:
        response = requests.get(f"{base_url}/api/content/downloads/wsl2-windows")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            print(f"资源标题: {data.get('data', {}).get('title')}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试教程分类
    print("\n7. 测试教程分类统计 API")
    print("-" * 60)
    try:
        response = requests.get(f"{base_url}/api/content/tutorials/categories")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            categories = data.get('data', {})
            print(f"分类数: {len(categories)}")
            for cat, info in categories.items():
                if info['count'] > 0:
                    print(f"  - {info['name']}: {info['count']}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试下载分类
    print("\n8. 测试下载资源分类统计 API")
    print("-" * 60)
    try:
        response = requests.get(f"{base_url}/api/content/downloads/categories")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            categories = data.get('data', {})
            print(f"分类数: {len(categories)}")
            for cat, info in categories.items():
                if info['count'] > 0:
                    print(f"  - {info['name']}: {info['count']}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试筛选功能
    print("\n9. 测试教程筛选 API (难度: beginner)")
    print("-" * 60)
    try:
        response = requests.get(f"{base_url}/api/content/tutorials/?difficulty=beginner&limit=5")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            print(f"筛选结果数: {len(data.get('data', {}).get('items', []))}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试搜索功能
    print("\n10. 测试教程搜索 API (关键词: Claude)")
    print("-" * 60)
    try:
        response = requests.get(f"{base_url}/api/content/tutorials/?search=Claude&limit=5")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            print(f"搜索结果数: {len(data.get('data', {}).get('items', []))}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

    print("\n" + "=" * 60)
    print("API测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_api()
