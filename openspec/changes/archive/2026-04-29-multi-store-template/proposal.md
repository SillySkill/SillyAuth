## Why

The SillyMD platform needs a **reusable online store template** that can serve multiple product lines through different URLs. Currently, `/openclaw` displays 傻福虾盘 (SillyClaw USB) products at `sillyclaw.html`, but the same template should be usable for other products on different URLs. The store needs full e-commerce functionality (cart, checkout, payment) and should dynamically load products based on the current route.

## What Changes

- **Reusable Store Template**: Create a shared store template that works for any product line
- **Multi-Product Support**: URL-based product selection (e.g., `/openclaw` → 傻福虾盘, `/store/electronics` → 电子产品)
- **Product Collection System**: Products grouped by "store" or "brand" identifier
- **Dynamic Product Loading**: Store template fetches products based on current URL/brand
- **Full E-commerce Flow**: Shopping cart, checkout, payment integration (WeChat Pay, Alipay)
- **Consistent Design**: Unified visual design across all product stores using shared CSS/components

## Capabilities

### New Capabilities

- `store-template`: Reusable HTML/JS store template that can be instantiated for any product line
- `product-collection`: Products organized by collection/brand identifier, selectable via URL
- `store-router`: URL routing system to load appropriate product collection
- `multi-brand-cart`: Shopping cart that can optionally be shared or isolated per brand
- `store-checkout`: Unified checkout flow working with any product collection
- `payment-gateway`: Integration with WeChat Pay and Alipay for online payment

### Modified Capabilities

- None - this creates new infrastructure

## Impact

- **Frontend**: New `store.html` template that reads URL params to load specific product collection
- **Backend**: New API endpoints for store management and product collections
- **Database**: New `store_collections` and `store_products` tables for multi-brand support
- **Routing**: URL structure like `/store/{collection_id}` to serve different products
