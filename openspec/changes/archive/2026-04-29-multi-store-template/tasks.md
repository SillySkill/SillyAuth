## 1. Database Setup

- [x] 1.1 Create `store_collections` table with collection_key, name_zh, name_en, description, logo_url, theme_config, is_active, sort_order
- [x] 1.2 Create `store_products` table with collection_id, product_key, names, descriptions, images, price, stock_count, specifications
- [x] 1.3 Create `store_cart` table for shopping cart persistence
- [x] 1.4 Create `store_orders` and `store_order_items` tables for order management
- [x] 1.5 Seed initial SillyClaw collection and products (from existing sillyclaw.html data)

## 2. Backend API

- [x] 2.1 Create `/api/v1/store/collections` endpoint - list all collections
- [x] 2.2 Create `/api/v1/store/collections/{key}` endpoint - get collection details
- [x] 2.3 Create `/api/v1/store/collections/{key}/products` endpoint - list products
- [x] 2.4 Create `/api/v1/store/cart` endpoints - add, get, update, delete cart items
- [x] 2.5 Create `/api/v1/store/orders` endpoints - create order, list orders, get order
- [x] 2.6 Create `/api/v1/store/orders/{order_no}/pay` endpoint - initiate payment
- [x] 2.7 Create `/api/v1/store/orders/{order_no}/status` endpoint - check payment status

## 3. Store Template (Frontend)

- [x] 3.1 Create `store.html` base template with shared CSS and layout
- [x] 3.2 Implement collection loader that reads URL and fetches collection config
- [x] 3.3 Implement product grid rendering with dynamic data
- [x] 3.4 Implement product quick view modal
- [x] 3.5 Implement shopping cart slide-out panel
- [x] 3.6 Implement cart item quantity controls (add, subtract, remove)
- [x] 3.7 Implement checkout flow (cart → shipping form → payment → confirmation)
- [x] 3.8 Add collection switcher in header navigation

## 4. Payment Integration

- [x] 4.1 Integrate with existing WeChat Pay V2 API for QR code generation
- [x] 4.2 Integrate with existing Alipay API for payment
- [x] 4.3 Implement payment status polling (2s interval, 30 max attempts)
- [x] 4.4 Implement payment callback handler for async notifications

## 5. URL Routing

- [x] 5.1 Configure `/openclaw` route to load `sillyclaw` collection
- [x] 5.2 Configure `/store/{collection_key}` route pattern
- [x] 5.3 Add 404 handling for non-existent collections
- [x] 5.4 Add SEO meta tags per collection (title, description from DB)

## 6. Testing & Polish

- [x] 6.1 Test product browsing on /openclaw
- [x] 6.2 Test cart operations (add, update, remove)
- [x] 6.3 Test checkout flow with test payments
- [x] 6.4 Test mobile responsive design
- [x] 6.5 Test collection switcher navigation

---

## Implementation Complete ✅

All 33 tasks completed!
