"""
快速验证脚本 - API服务器重启后使用
用于快速验证教程和下载资源API是否正常工作
"""
import requests
import json
from datetime import datetime

def test_endpoint(name, url, method='GET', expected_status=200):
    """测试单个端点"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, timeout=5)

        status = "✅" if response.status_code == expected_status else "❌"
        elapsed = response.elapsed.total_seconds() * 1000

        print(f"{status} {name}")
        print(f"   URL: {url}")
        print(f"   状态码: {response.status_code} (预期: {expected_status})")
        print(f"   响应时间: {elapsed:.2f}ms")

        if response.status_code == 200:
            try:
                data = response.json()
                if 'data' in data and 'items' in data['data']:
                    print(f"   返回数据: {len(data['data']['items'])} 条")
                elif 'data' in data:
                    print(f"   返回数据: {type(data['data']).__name__}")
            except:
                print(f"   返回数据: {response.text[:100]}")
        else:
            print(f"   错误: {response.text[:100]}")

        print()
        return response.status_code == expected_status

    except Exception as e:
        print(f"❌ {name}")
        print(f"   URL: {url}")
        print(f"   错误: {str(e)}")
        print()
        return False


def main():
    base_url = "http://47.96.133.238:8000"

    print("=" * 80)
    print("教程和下载资源API - 快速验证")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"服务器: {base_url}")
    print("=" * 80)
    print()

    results = []

    # 1. 健康检查
    print("1. 健康检查")
    print("-" * 80)
    results.append(test_endpoint(
        "API健康状态",
        f"{base_url}/api/health"
    ))

    # 2. 教程列表
    print("2. 教程列表API")
    print("-" * 80)
    results.append(test_endpoint(
        "教程列表 - 基础查询",
        f"{base_url}/api/content/tutorials/?limit=5"
    ))

    results.append(test_endpoint(
        "教程列表 - 分类筛选",
        f"{base_url}/api/content/tutorials/?category=claude-code&limit=5"
    ))

    results.append(test_endpoint(
        "教程列表 - 难度筛选",
        f"{base_url}/api/content/tutorials/?difficulty=beginner&limit=5"
    ))

    results.append(test_endpoint(
        "教程列表 - 搜索",
        f"{base_url}/api/content/tutorials/?search=Claude&limit=5"
    ))

    # 3. 教程详情
    print("3. 教程详情API")
    print("-" * 80)
    results.append(test_endpoint(
        "教程详情 - ID查询",
        f"{base_url}/api/content/tutorials/1"
    ))

    results.append(test_endpoint(
        "教程详情 - Slug查询",
        f"{base_url}/api/content/tutorials/claude-code-getting-started"
    ))

    # 4. 教程统计
    print("4. 教程统计API")
    print("-" * 80)
    results.append(test_endpoint(
        "教程分类统计",
        f"{base_url}/api/content/tutorials/categories"
    ))

    results.append(test_endpoint(
        "精选教程列表",
        f"{base_url}/api/content/tutorials/featured?limit=6"
    ))

    # 5. 下载资源列表
    print("5. 下载资源API")
    print("-" * 80)
    results.append(test_endpoint(
        "下载资源列表",
        f"{base_url}/api/content/downloads/?limit=5"
    ))

    results.append(test_endpoint(
        "下载资源详情 - ID",
        f"{base_url}/api/content/downloads/1"
    ))

    results.append(test_endpoint(
        "下载资源详情 - Slug",
        f"{base_url}/api/content/downloads/wsl2-windows"
    ))

    results.append(test_endpoint(
        "下载资源分类统计",
        f"{base_url}/api/content/downloads/categories"
    ))

    # 6. 交互功能
    print("6. 交互功能API")
    print("-" * 80)
    results.append(test_endpoint(
        "记录浏览",
        f"{base_url}/api/content/tutorials/1/view",
        method='POST'
    ))

    results.append(test_endpoint(
        "点赞",
        f"{base_url}/api/content/tutorials/1/like",
        method='POST'
    ))

    results.append(test_endpoint(
        "记录下载",
        f"{base_url}/api/content/downloads/1/download",
        method='POST'
    ))

    # 总结
    print("=" * 80)
    print("测试总结")
    print("=" * 80)

    total = len(results)
    passed = sum(results)
    failed = total - passed
    pass_rate = (passed / total * 100) if total > 0 else 0

    print(f"\n总测试数: {total}")
    print(f"通过: {passed} ✅")
    print(f"失败: {failed} ❌")
    print(f"通过率: {pass_rate:.1f}%")

    if pass_rate == 100:
        print("\n🎉 所有API测试通过！")
    elif pass_rate >= 80:
        print("\n⚠️ 大部分API工作正常，有少量失败")
    else:
        print("\n❌ 多个API失败，需要检查")

    print("\n" + "=" * 80)
    print(f"验证完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    return pass_rate


if __name__ == "__main__":
    import sys
    pass_rate = main()
    sys.exit(0 if pass_rate >= 80 else 1)
