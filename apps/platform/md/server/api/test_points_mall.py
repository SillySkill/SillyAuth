"""
积分商城API测试脚本
用于验证积分商城各接口功能
"""

import requests
import json

API_BASE = "http://localhost:8000"
TEST_USER_ID = 1

def print_response(title, response):
    """打印响应结果"""
    print(f"\n{'='*60}")
    print(f"📌 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")


def test_api():
    """测试积分商城API"""

    print("🚀 开始测试积分商城API...")

    # 1. 测试健康检查
    response = requests.get(f"{API_BASE}/api/health")
    print_response("1. 健康检查", response)

    # 2. 获取商品分类
    response = requests.get(f"{API_BASE}/api/points/categories")
    print_response("2. 获取商品分类", response)

    # 3. 获取所有商品
    response = requests.get(f"{API_BASE}/api/points/products?is_active=true&limit=20")
    print_response("3. 获取商品列表", response)

    if response.status_code == 200:
        products = response.json()
        if products:
            first_product_id = products[0]['id']

            # 4. 获取商品详情
            response = requests.get(f"{API_BASE}/api/points/products/{first_product_id}")
            print_response("4. 获取商品详情", response)

            # 5. 添加到购物车
            cart_data = {
                "user_id": TEST_USER_ID,
                "product_id": first_product_id,
                "quantity": 1
            }
            response = requests.post(
                f"{API_BASE}/api/points/cart",
                json=cart_data,
                headers={"Content-Type": "application/json"}
            )
            print_response("5. 添加到购物车", response)

            # 6. 获取购物车
            response = requests.get(f"{API_BASE}/api/points/cart?user_id={TEST_USER_ID}")
            print_response("6. 获取购物车", response)

            # 7. 获取用户积分余额
            response = requests.get(f"{API_BASE}/api/points/balance?user_id={TEST_USER_ID}")
            print_response("7. 获取用户积分余额", response)

            # 如果用户有足够积分，测试兑换功能
            if response.status_code == 200:
                balance = response.json()
                print(f"\n💰 用户当前积分: {balance['ai_points']}")

                if balance['ai_points'] > 0:
                    # 8. 兑换商品
                    exchange_data = {
                        "user_id": TEST_USER_ID,
                        "product_id": first_product_id,
                        "quantity": 1
                    }

                    # 检查商品价格
                    products_response = requests.get(f"{API_BASE}/api/points/products/{first_product_id}")
                    if products_response.status_code == 200:
                        product = products_response.json()
                        if balance['ai_points'] >= product['points_required']:
                            response = requests.post(
                                f"{API_BASE}/api/points/exchange",
                                json=exchange_data,
                                headers={"Content-Type": "application/json"}
                            )
                            print_response("8. 兑换商品", response)

                            # 9. 获取兑换记录
                            response = requests.get(f"{API_BASE}/api/points/exchanges?user_id={TEST_USER_ID}")
                            print_response("9. 获取兑换记录", response)
                        else:
                            print(f"\n⚠️  积分不足，跳过兑换测试（需要 {product['points_required']} 积分，当前 {balance['ai_points']} 积分）")

            # 10. 获取商城统计
            response = requests.get(f"{API_BASE}/api/points/stats")
            print_response("10. 获取商城统计", response)

            # 11. 清空购物车（清理测试数据）
            response = requests.delete(f"{API_BASE}/api/points/cart?user_id={TEST_USER_ID}")
            print_response("11. 清空购物车", response)

    # 12. 测试分类筛选
    response = requests.get(f"{API_BASE}/api/points/products?category=content")
    print_response("12. 筛选内容兑换类商品", response)

    # 13. 测试精选商品
    response = requests.get(f"{API_BASE}/api/points/products?is_featured=true")
    print_response("13. 获取精选商品", response)

    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)


def test_create_product():
    """测试创建商品（管理员功能）"""
    print("\n🔧 测试创建商品（管理员功能）...")

    product_data = {
        "product_key": "test_product",
        "category_key": "custom",
        "name_en": "Test Product",
        "name_zh": "测试商品",
        "description_en": "This is a test product",
        "description_zh": "这是一个测试商品",
        "points_required": 100,
        "stock_count": 50,
        "is_featured": False,
        "sort_order": 100
    }

    response = requests.post(
        f"{API_BASE}/api/points/products",
        json=product_data,
        headers={"Content-Type": "application/json"}
    )
    print_response("创建测试商品", response)

    if response.status_code == 200:
        result = response.json()
        product_id = result.get('product_id')

        # 更新商品
        update_data = {
            "points_required": 150,
            "is_featured": True
        }

        response = requests.put(
            f"{API_BASE}/api/points/products/{product_id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        print_response("更新测试商品", response)

        # 删除商品
        response = requests.delete(f"{API_BASE}/api/points/products/{product_id}")
        print_response("删除测试商品", response)


if __name__ == "__main__":
    try:
        # 基础功能测试
        test_api()

        # 管理员功能测试（可选）
        # test_create_product()

    except requests.exceptions.ConnectionError:
        print("\n❌ 错误：无法连接到API服务器")
        print("请确保API服务器正在运行：")
        print("cd server/api && python main.py")
    except Exception as e:
        print(f"\n❌ 测试出错: {str(e)}")
