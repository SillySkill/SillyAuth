"""
后台管理系统API测试脚本
快速验证所有API是否正常工作
"""
import requests
import json
import sys

# 配置
BASE_URL = "https://www.jcoding.chat/api/admin"
USERNAME = "admin"
PASSWORD = "admin123"

# 全局变量存储token
TOKEN = None


def print_response(response, title):
    """打印响应结果"""
    print(f"\n{'='*60}")
    print(f"测试: {title}")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    try:
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"响应: {response.text}")


def test_login():
    """测试登录"""
    global TOKEN
    print("\n【测试1: 管理员登录】")

    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": USERNAME,
        "password": PASSWORD
    })

    print_response(response, "登录")

    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 200:
            TOKEN = data['data']['token']
            print(f"\n✓ 登录成功! Token: {TOKEN[:50]}...")
            return True
        else:
            print(f"\n✗ 登录失败: {data.get('message')}")
            return False
    else:
        print(f"\n✗ 登录请求失败")
        return False


def test_get_profile():
    """测试获取个人信息"""
    print("\n【测试2: 获取个人信息】")

    if not TOKEN:
        print("✗ 未登录，跳过测试")
        return False

    response = requests.get(
        f"{BASE_URL}/auth/profile",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )

    print_response(response, "获取个人信息")
    return response.status_code == 200


def test_get_apps():
    """测试获取应用列表"""
    print("\n【测试3: 获取应用列表】")

    if not TOKEN:
        print("✗ 未登录，跳过测试")
        return False

    response = requests.get(
        f"{BASE_URL}/apps",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )

    print_response(response, "获取应用列表")

    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 200:
            apps = data['data']['list']
            print(f"\n✓ 获取成功! 共 {len(apps)} 个应用")
            return True
    return False


def test_get_app_detail():
    """测试获取应用详情"""
    print("\n【测试4: 获取应用详情】")

    if not TOKEN:
        print("✗ 未登录，跳过测试")
        return False

    response = requests.get(
        f"{BASE_URL}/apps/1",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )

    print_response(response, "获取应用详情")
    return response.status_code == 200


def test_get_app_stats():
    """测试获取应用统计"""
    print("\n【测试5: 获取应用统计】")

    if not TOKEN:
        print("✗ 未登录，跳过测试")
        return False

    response = requests.get(
        f"{BASE_URL}/apps/1/stats",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )

    print_response(response, "获取应用统计")
    return response.status_code == 200


def test_get_modules():
    """测试获取模块列表"""
    print("\n【测试6: 获取模块列表】")

    if not TOKEN:
        print("✗ 未登录，跳过测试")
        return False

    response = requests.get(
        f"{BASE_URL}/apps/1/modules",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )

    print_response(response, "获取模块列表")

    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 200:
            modules = data['data']['modules']
            print(f"\n✓ 获取成功! 共 {len(modules)} 个模块")
            for module in modules:
                print(f"  - {module['module_name']}: {'启用' if module['enabled'] else '禁用'}")
            return True
    return False


def test_get_module_detail():
    """测试获取模块详情"""
    print("\n【测试7: 获取模块详情】")

    if not TOKEN:
        print("✗ 未登录，跳过测试")
        return False

    response = requests.get(
        f"{BASE_URL}/apps/1/modules/ai_show",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )

    print_response(response, "获取模块详情")
    return response.status_code == 200


def test_get_assets():
    """测试获取素材列表"""
    print("\n【测试8: 获取素材列表】")

    if not TOKEN:
        print("✗ 未登录，跳过测试")
        return False

    response = requests.get(
        f"{BASE_URL}/apps/1/assets",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )

    print_response(response, "获取素材列表")
    return response.status_code == 200


def test_get_devices():
    """测试获取设备列表"""
    print("\n【测试9: 获取设备列表】")

    if not TOKEN:
        print("✗ 未登录，跳过测试")
        return False

    response = requests.get(
        f"{BASE_URL}/apps/1/devices",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )

    print_response(response, "获取设备列表")
    return response.status_code == 200


def test_get_devices_stats():
    """测试获取设备统计"""
    print("\n【测试10: 获取设备统计】")

    if not TOKEN:
        print("✗ 未登录，跳过测试")
        return False

    response = requests.get(
        f"{BASE_URL}/apps/1/devices/stats",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )

    print_response(response, "获取设备统计")
    return response.status_code == 200


def test_get_push_tasks():
    """测试获取推送任务列表"""
    print("\n【测试11: 获取推送任务列表】")

    if not TOKEN:
        print("✗ 未登录，跳过测试")
        return False

    response = requests.get(
        f"{BASE_URL}/apps/1/push/tasks",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )

    print_response(response, "获取推送任务列表")
    return response.status_code == 200


def test_logout():
    """测试登出"""
    print("\n【测试12: 登出】")

    if not TOKEN:
        print("✗ 未登录，跳过测试")
        return False

    response = requests.post(
        f"{BASE_URL}/auth/logout",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )

    print_response(response, "登出")
    return response.status_code == 200


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("后台管理系统API测试")
    print("="*60)

    tests = [
        ("登录", test_login),
        ("获取个人信息", test_get_profile),
        ("获取应用列表", test_get_apps),
        ("获取应用详情", test_get_app_detail),
        ("获取应用统计", test_get_app_stats),
        ("获取模块列表", test_get_modules),
        ("获取模块详情", test_get_module_detail),
        ("获取素材列表", test_get_assets),
        ("获取设备列表", test_get_devices),
        ("获取设备统计", test_get_devices_stats),
        ("获取推送任务列表", test_get_push_tasks),
        ("登出", test_logout),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ 测试失败: {str(e)}")
            results.append((name, False))

    # 打印测试结果汇总
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    passed = 0
    failed = 0

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:.<30} {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("\n" + "-"*60)
    print(f"总计: {len(results)} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print(f"成功率: {passed/len(results)*100:.1f}%")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
