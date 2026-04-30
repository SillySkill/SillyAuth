## ADDED Requirements

### Requirement: Store Collection Management
Each product collection SHALL have a unique `collection_key` that identifies it in the URL.

#### Scenario: Collection data structure
Each collection SHALL contain:
- `collection_key`: Unique identifier for URL (e.g., "sillyclaw", "electronics")
- `name_zh`: Chinese name for display
- `name_en`: English name
- `description`: Collection description
- `logo_url`: Brand logo image
- `theme_config`: Optional JSON for per-collection styling
- `is_active`: Whether collection is publicly visible

### Requirement: Product Association
Products SHALL be associated with exactly one collection.

#### Scenario: Get products by collection
- **WHEN** requesting products for a collection
- **THEN** only products where `collection_id` matches SHALL be returned
- **AND** products SHALL be ordered by `sort_order` or `created_at`

#### Scenario: Product data structure
Each product SHALL contain:
- `product_key`: Unique within collection (e.g., "sillyclaw-128gb-silver")
- `name_zh` / `name_en`: Product names
- `description_zh` / `description_en`: Full descriptions
- `image_url`: Primary product image
- `gallery`: Array of additional image URLs
- `price`: Current price in RMB
- `original_price`: Original price for discount display
- `stock_count`: Available quantity (-1 for unlimited)
- `specifications`: JSON object with tech specs
