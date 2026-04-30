"""
Logistics Module API Test Script
Tests all logistics API endpoints
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from decimal import Decimal
from src.modules.logistics import logistics_service
from src.modules.logistics.schemas import (
    ShippingCalculateRequest,
    OrderItem,
    ShippingAddress,
    ExpressLabelRequest,
)


def test_express_companies():
    """Test express companies listing."""
    print("\n" + "="*60)
    print("Testing Express Companies")
    print("="*60)

    companies = logistics_service.express_company_service.list_companies()

    print(f"\nTotal companies: {len(companies)}")
    for company in companies:
        print(f"  - {company.code}: {company.name} (status: {company.status})")

    return len(companies) > 0


def test_shipping_templates():
    """Test shipping templates listing."""
    print("\n" + "="*60)
    print("Testing Shipping Templates")
    print("="*60)

    templates = logistics_service.shipping_template_service.list_templates()

    print(f"\nTotal templates: {len(templates)}")
    for template in templates:
        print(f"\n  Template: {template.name}")
        print(f"    Type: {template.template_type}")
        print(f"    Free shipping: {template.is_free_shipping}")
        print(f"    Default fee: {template.default_fee}")
        print(f"    Rules: {len(template.rules)}")

        # template.rules is a list of dicts
        for rule in template.rules:
            region_names = rule.get("region_names", [])
            first_fee = rule.get("first_fee", 0)
            continue_fee = rule.get("continue_fee", 0)
            print(f"      - {region_names}: {first_fee} + {continue_fee}/unit")

    return len(templates) > 0


def test_calculate_shipping():
    """Test shipping calculation."""
    print("\n" + "="*60)
    print("Testing Shipping Calculation")
    print("="*60)

    request = ShippingCalculateRequest(
        items=[
            OrderItem(
                product_id=1,
                product_name="测试商品",
                quantity=2,
                weight=0.5,
                price=Decimal("99.00")
            )
        ],
        address=ShippingAddress(
            province="广东省",
            city="深圳市",
            district="南山区",
            address="科技园某路某号"
        )
    )

    result = logistics_service.calculate_shipping(request)

    print(f"\nTotal weight: {result.total_weight} kg")
    print(f"Free shipping threshold: {result.free_shipping_threshold} 元")
    print(f"Is free shipping: {result.is_free_shipping}")
    print(f"\nAvailable options: {len(result.options)}")

    for option in result.options:
        print(f"\n  {option.express_company_name}:")
        print(f"    Fee: {option.fee} 元")
        print(f"    Estimated days: {option.estimated_days}")
        print(f"    Is free: {option.is_free}")
        print(f"    Recommended: {option.is_recommend}")

    return len(result.options) > 0


async def test_tracking():
    """Test logistics tracking."""
    print("\n" + "="*60)
    print("Testing Logistics Tracking")
    print("="*60)

    # Test with mock tracking number
    tracking_number = "SF1234567890123"

    tracking_info = await logistics_service.get_tracking_info(
        tracking_number=tracking_number,
        express_company="shunfeng"
    )

    print(f"\nTracking number: {tracking_info.tracking_number}")
    print(f"Express company: {tracking_info.express_company_name}")
    print(f"Status: {tracking_info.status.value} ({tracking_info.status_text})")
    print(f"\nTraces: {len(tracking_info.traces)}")

    for trace in tracking_info.traces:
        print(f"\n  [{trace.time}] {trace.status}")
        print(f"    Location: {trace.location or 'N/A'}")
        print(f"    Description: {trace.description or 'N/A'}")

    return tracking_info.tracking_number == tracking_number


def test_generate_label():
    """Test express label generation."""
    print("\n" + "="*60)
    print("Testing Express Label Generation")
    print("="*60)

    request = ExpressLabelRequest(
        order_id=12345,
        express_company="shunfeng",
        sender_name="张三",
        sender_phone="13800138000",
        sender_address="广东省深圳市南山区科技园",
        receiver_name="李四",
        receiver_phone="13900139000",
        receiver_address="北京市朝阳区建国路88号",
        goods_name="电子产品",
        goods_weight=1.5
    )

    label_data = logistics_service.generate_express_label(request)

    print(f"\nOrder ID: {label_data.order_id}")
    print(f"Express company: {label_data.express_company_name}")
    print(f"Tracking number: {label_data.tracking_number}")
    print(f"\nSender:")
    print(f"  Name: {label_data.sender['name']}")
    print(f"  Phone: {label_data.sender['phone']}")
    print(f"  Address: {label_data.sender['address']}")
    print(f"\nReceiver:")
    print(f"  Name: {label_data.receiver['name']}")
    print(f"  Phone: {label_data.receiver['phone']}")
    print(f"  Address: {label_data.receiver['address']}")
    print(f"\nGoods:")
    print(f"  Name: {label_data.goods_name}")
    print(f"  Weight: {label_data.goods_weight} kg")
    print(f"  Created at: {label_data.created_at}")

    return label_data.tracking_number is not None


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("LOGISTICS MODULE API TESTS")
    print("="*60)

    results = {}

    # Test express companies
    try:
        results['express_companies'] = test_express_companies()
    except Exception as e:
        print(f"ERROR: {e}")
        results['express_companies'] = False

    # Test shipping templates
    try:
        results['shipping_templates'] = test_shipping_templates()
    except Exception as e:
        print(f"ERROR: {e}")
        results['shipping_templates'] = False

    # Test shipping calculation
    try:
        results['calculate_shipping'] = test_calculate_shipping()
    except Exception as e:
        print(f"ERROR: {e}")
        results['calculate_shipping'] = False

    # Test tracking (async)
    try:
        results['tracking'] = asyncio.run(test_tracking())
    except Exception as e:
        print(f"ERROR: {e}")
        results['tracking'] = False

    # Test express label generation
    try:
        results['generate_label'] = test_generate_label()
    except Exception as e:
        print(f"ERROR: {e}")
        results['generate_label'] = False

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"  {name}: {status}")

    print(f"\nTotal: {passed}/{total} passed")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
