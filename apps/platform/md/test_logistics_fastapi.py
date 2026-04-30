"""
Test FastAPI routes for Logistics Module
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.core import ConfigLoader, PluginManager
from src.modules.logistics import SillyMDModule


def test_logistics_routes():
    """Test logistics module routes are registered."""
    print("\n" + "="*60)
    print("Testing FastAPI Logistics Routes")
    print("="*60)

    # Create app manually with module
    app = FastAPI(title="Test App")

    # Create and register logistics module
    config_loader = ConfigLoader(os.path.join(os.path.dirname(__file__), 'src'))
    plugin_manager = PluginManager(config_loader)
    plugin_manager.set_app(app)

    # Manually install logistics module
    logistics_module = SillyMDModule()
    logistics_module.install(app)

    # List all logistics routes
    logistics_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and '/api/logistics' in route.path:
            methods = getattr(route, 'methods', {'GET'})
            logistics_routes.append({
                'path': route.path,
                'methods': list(methods)
            })

    print(f"\nFound {len(logistics_routes)} logistics routes:")
    for r in logistics_routes:
        print(f"  {r['methods'][0] if r['methods'] else 'GET'} {r['path']}")

    return len(logistics_routes) > 0, app


def test_api_endpoints(app):
    """Test API endpoints with TestClient."""
    print("\n" + "="*60)
    print("Testing API Endpoints with TestClient")
    print("="*60)

    client = TestClient(app)

    results = {}

    # Test 1: Get express companies
    print("\n1. Testing GET /api/logistics/companies")
    response = client.get("/api/logistics/companies")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Companies count: {len(data)}")
        results['companies'] = True
    else:
        print(f"   ERROR: {response.status_code} - {response.text}")
        results['companies'] = False

    # Test 2: Get shipping templates
    print("\n2. Testing GET /api/logistics/templates")
    response = client.get("/api/logistics/templates")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Templates count: {len(data)}")
        results['templates'] = True
    else:
        print(f"   ERROR: {response.status_code} - {response.text}")
        results['templates'] = False

    # Test 3: Calculate shipping
    print("\n3. Testing POST /api/logistics/calculate")
    request_data = {
        "items": [
            {
                "product_id": 1,
                "product_name": "Test Product",
                "quantity": 2,
                "weight": 0.5,
                "price": 99.00
            }
        ],
        "address": {
            "province": "广东省",
            "city": "深圳市",
            "district": "南山区"
        }
    }
    response = client.post("/api/logistics/calculate", json=request_data)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Options: {len(data.get('options', []))}")
        print(f"   Free shipping: {data.get('is_free_shipping', False)}")
        results['calculate'] = True
    else:
        print(f"   ERROR: {response.status_code} - {response.text}")
        results['calculate'] = False

    # Test 4: Track shipment
    print("\n4. Testing GET /api/logistics/track/SF123456789")
    response = client.get("/api/logistics/track/SF123456789", params={"express_company": "shunfeng"})
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Success: {data.get('success', False)}")
        print(f"   Tracking: {data.get('data', {}).get('tracking_number', 'N/A')}")
        results['track'] = True
    else:
        print(f"   ERROR: {response.status_code} - {response.text}")
        results['track'] = False

    # Test 5: Generate express label
    print("\n5. Testing POST /api/logistics/print")
    label_request = {
        "order_id": 12345,
        "express_company": "shunfeng",
        "sender_name": "张三",
        "sender_phone": "13800138000",
        "sender_address": "广东省深圳市南山区",
        "receiver_name": "李四",
        "receiver_phone": "13900139000",
        "receiver_address": "北京市朝阳区",
        "goods_name": "电子产品",
        "goods_weight": 1.5
    }
    response = client.post("/api/logistics/print", json=label_request)
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Success: {data.get('success', False)}")
        print(f"   Tracking: {data.get('data', {}).get('tracking_number', 'N/A')}")
        results['print'] = True
    else:
        print(f"   ERROR: {response.status_code} - {response.text}")
        results['print'] = False

    # Test 6: Health check
    print("\n6. Testing GET /api/logistics/health")
    response = client.get("/api/logistics/health")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Success: {data.get('success', False)}")
        print(f"   Message: {data.get('message', 'N/A')}")
        results['health'] = True
    else:
        print(f"   ERROR: {response.status_code} - {response.text}")
        results['health'] = False

    return results


if __name__ == "__main__":
    # Test routes are registered
    routes_ok, app = test_logistics_routes()

    # Test endpoints
    results = test_api_endpoints(app)

    # Summary
    print("\n" + "="*60)
    print("API TEST SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"  {name}: {status}")

    print(f"\nRoutes registered: {'YES' if routes_ok else 'NO'}")
    print(f"Total: {passed}/{total} API tests passed")

    success = routes_ok and passed == total
    sys.exit(0 if success else 1)
