## Context

The platform needs a shared online store template that can serve different product lines. For example:
- `/openclaw` → SillyClaw USB drives (傻福虾盘)
- `/store/electronics` → Electronics products
- `/store/custom` → Custom/bespoke products

Each store should have its own:
- Product catalog
- Branding/theme (optional)
- Product data

But they all share:
- Same HTML/CSS template
- Same shopping cart logic
- Same checkout flow
- Same payment integration

## Goals / Non-Goals

**Goals:**
- Create a single reusable store template
- Support multiple product collections via URL routing
- Load products dynamically based on URL/collection ID
- Provide full e-commerce: cart, checkout, payment
- Allow per-store or shared cart options

**Non-Goals:**
- Multi-vendor marketplace (single-vendor, multi-collection)
- Full CMS for store customization (products only)
- Internationalization (i18n) initially

## Decisions

### 1. URL Structure

**Decision:** Use `/store/{collection_id}` pattern, with `/openclaw` as alias for `sillyclaw` collection.

**Examples:**
- `/openclaw` → Collection: `sillyclaw` (SillyClaw USB)
- `/store/electronics` → Collection: `electronics`
- `/store` → Default collection or redirect

**Rationale:**
- Clean, RESTful URL structure
- Easy to remember branded URLs
- Collection ID maps to database records

### 2. Template Architecture

**Decision:** Single `store.html` template that:
1. Reads `collection_id` from URL path
2. Fetches collection config (name, theme, products) from API
3. Renders products dynamically
4. Shares cart/checkout logic across all collections

**Rationale:**
- DRY principle - one template for all stores
- Easier maintenance
- Consistent UX across brands

### 3. Product Data Model

```sql
CREATE TABLE store_collections (
  id SERIAL PRIMARY KEY,
  collection_key VARCHAR(50) UNIQUE NOT NULL,  -- e.g., 'sillyclaw', 'electronics'
  name_zh VARCHAR(100) NOT NULL,
  name_en VARCHAR(100),
  description TEXT,
  logo_url VARCHAR(500),
  theme_config JSON,  -- Optional per-store styling
  is_active BOOLEAN DEFAULT TRUE,
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE store_products (
  id SERIAL PRIMARY KEY,
  collection_id INTEGER REFERENCES store_collections(id),
  product_key VARCHAR(50) NOT NULL,
  name_zh VARCHAR(200) NOT NULL,
  name_en VARCHAR(200),
  description_zh TEXT,
  description_en TEXT,
  image_url VARCHAR(500),
  gallery JSON,  -- Array of image URLs
  price DECIMAL(10,2) NOT NULL,
  original_price DECIMAL(10,2),  -- For discount display
  stock_count INTEGER DEFAULT 0,  -- -1 for unlimited
  is_active BOOLEAN DEFAULT TRUE,
  specifications JSON,  -- Technical specs
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(collection_id, product_key)
);
```

### 4. Cart Strategy

**Decision:** Cart is **per-collection** (isolated) but can be **merged** at checkout if user shops across collections.

**Rationale:**
- Simpler implementation
- Clearer user experience
- Can add cross-collection cart later if needed

### 5. API Endpoints

```
GET  /api/v1/store/collections                    - List all collections
GET  /api/v1/store/collections/{key}            - Get collection details
GET  /api/v1/store/collections/{key}/products   - List products in collection

POST /api/v1/store/cart                          - Add to cart
GET  /api/v1/store/cart?collection=X&user_id=Y   - Get cart
PUT  /api/v1/store/cart/{item_id}                - Update quantity
DELETE /api/v1/store/cart/{item_id}             - Remove item

POST /api/v1/store/orders                        - Create order
GET  /api/v1/store/orders?user_id=X             - List user orders
GET  /api/v1/store/orders/{order_no}            - Get order details
POST /api/v1/store/orders/{order_no}/pay        - Initiate payment
GET  /api/v1/store/orders/{order_no}/status     - Check payment status
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| SEO per collection | Each collection has unique meta tags from DB |
| Performance | Cache collection/product data, lazy load images |
| Payment per collection | Each collection has own payment config |

## Open Questions

1. **Shared auth**: Should user login be shared across all collections?
2. **Order history**: Show orders from all collections or filter by current?
3. **Collection-specific themes**: Support per-collection color/logo theming?
