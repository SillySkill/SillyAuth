"""
Test script for Admin Orders API
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_get_orders():
    """Test get orders list"""
    print("Testing GET /api/admin/orders...")
    response = requests.get(f"{BASE_URL}/api/admin/orders")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total orders: {data.get('total', 0)}")
        print(f"Items on current page: {len(data.get('items', []))}")
        return data.get('items', [])
    else:
        print(f"Error: {response.text}")
        return []


def test_get_order_stats():
    """Test get order statistics"""
    print("\nTesting GET /api/admin/orders/stats...")
    response = requests.get(f"{BASE_URL}/api/admin/orders/stats")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total orders: {data.get('total_orders', 0)}")
        print(f"Pending orders: {data.get('pending_orders', 0)}")
        print(f"Paid orders: {data.get('paid_orders', 0)}")
        print(f"Total revenue: ${data.get('total_revenue', 0)}")
        return data
    else:
        print(f"Error: {response.text}")
        return None


def test_get_order_by_id(order_id):
    """Test get order by ID"""
    print(f"\nTesting GET /api/admin/orders/{order_id}...")
    response = requests.get(f"{BASE_URL}/api/admin/orders/{order_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Order No: {data.get('order_no')}")
        print(f"Status: {data.get('status')}")
        print(f"Final Amount: ${data.get('final_amount')}")
        return data
    else:
        print(f"Error: {response.text}")
        return None


def test_ship_order(order_id):
    """Test ship order"""
    print(f"\nTesting POST /api/admin/orders/{order_id}/ship...")
    data = {
        "tracking_number": "SF1234567890",
        "express_company": "sf",
        "remark": "Test shipment"
    }
    response = requests.post(
        f"{BASE_URL}/api/admin/orders/{order_id}/ship",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Shipped order: {result.get('order_no')}")
        print(f"Tracking: {result.get('tracking_number')}")
        return result
    else:
        print(f"Error: {response.text}")
        return None


def test_refund_order(order_id):
    """Test refund order"""
    print(f"\nTesting POST /api/admin/orders/{order_id}/refund...")
    data = {
        "reason": "Customer requested refund",
        "refund_amount": 100.00,
        "remark": "Test refund"
    }
    response = requests.post(
        f"{BASE_URL}/api/admin/orders/{order_id}/refund",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Refunded order: {result.get('order_no')}")
        print(f"Status: {result.get('status')}")
        return result
    else:
        print(f"Error: {response.text}")
        return None


def test_update_status(order_id):
    """Test update order status"""
    print(f"\nTesting PUT /api/admin/orders/{order_id}/status...")
    data = {
        "status": "processing",
        "remark": "Processing started"
    }
    response = requests.put(
        f"{BASE_URL}/api/admin/orders/{order_id}/status",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Updated order: {result.get('order_no')}")
        print(f"New status: {result.get('status')}")
        return result
    else:
        print(f"Error: {response.text}")
        return None


def test_batch_ship(order_ids):
    """Test batch ship orders"""
    print(f"\nTesting POST /api/admin/orders/batch-ship...")
    data = {
        "order_ids": order_ids[:2],  # Ship first 2 orders
        "tracking_number": "YT9876543210",
        "express_company": "yto",
        "remark": "Batch shipment"
    }
    response = requests.post(
        f"{BASE_URL}/api/admin/orders/batch-ship",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Batch shipped: {result.get('total')} orders")
        return result
    else:
        print(f"Error: {response.text}")
        return None


def test_filter_orders():
    """Test filter orders by status"""
    print("\nTesting GET /api/admin/orders with filters...")
    params = {
        "status": "paid",
        "page": 1,
        "limit": 5
    }
    response = requests.get(f"{BASE_URL}/api/admin/orders", params=params)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total paid orders: {data.get('total', 0)}")
        return data.get('items', [])
    else:
        print(f"Error: {response.text}")
        return []


def test_export_orders():
    """Test export orders"""
    print("\nTesting GET /api/admin/orders/export/download...")
    params = {"format": "json"}
    response = requests.get(f"{BASE_URL}/api/admin/orders/export/download", params=params)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Exported: {data.get('total')} orders")
        return data
    else:
        print(f"Error: {response.text}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("Admin Orders API Test")
    print("=" * 60)

    # Test get orders
    orders = test_get_orders()

    # Test get stats
    stats = test_get_order_stats()

    # Test get single order
    if orders:
        first_order = orders[0]
        order_id = first_order.get('id')
        if order_id:
            test_get_order_by_id(order_id)

    # Test filter orders
    test_filter_orders()

    # Test update status
    if orders:
        for order in orders:
            if order.get('status') == 'pending':
                test_update_status(order.get('id'))
                break

    # Test ship order
    if orders:
        for order in orders:
            if order.get('status') in ['paid', 'processing']:
                test_ship_order(order.get('id'))
                break

    # Test refund order
    if orders:
        for order in orders:
            if order.get('status') == 'paid':
                test_refund_order(order.get('id'))
                break

    # Test batch ship
    if len(orders) >= 2:
        order_ids = [o.get('id') for o in orders if o.get('status') in ['paid', 'processing']]
        if order_ids:
            test_batch_ship(order_ids)

    # Test export
    test_export_orders()

    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)
