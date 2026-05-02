## Why

The /openclaw product page currently mixes database-driven content (~60%) with hardcoded template data (~40%). Gallery images, showcase sections, product photos, variant data, hero video paths, and inline styles are all hardcoded or rely on fragile patterns. Additionally, the seed data has a mismatch where variants are nested inside the product record but the runtime reads them as a separate record, causing the variants section to always show "暂无规格信息". Two parallel product data systems (config_data and store_*) further fragment the architecture. This makes the page impossible to manage via the admin UI without editing template code.

## What Changes

1. **Fix variants data pipeline** — Fix the mismatch between seed (variants inside product) and runtime (variants as separate record). Add a fallback in the route handler so product.data.variants is used when the separate variants record doesn't exist.
2. **Make images and media fully DB-driven** — Gallery thumbnails, showcase image+features, and product photos sections will read from config_data fields (product.images, product.showcase, product.photos) instead of being hardcoded in the template.
3. **Extract all inline styles to a dedicated CSS file** — Create `examples/css/openclaw.css` with design tokens, card classes, grid system, and proper media queries. Remove all inline `style="..."` attributes and the fragile `[style*='...']` CSS selectors from the template.
4. **Refactor Jinja2 template** — Use macros for reusable patterns. Reduce template from ~630 lines to ~400 lines. Add sticky navigation and sticky purchase bar.
5. **Seed comprehensive data** — Update seed_homepage.py with complete product data including images, showcase, photos arrays and all agent/mode/security/color fields. Create the missing independent variants seed record.
6. **Reconcile pricing** — Variant pricing in config_data will match the store_products table data (128GB ¥69, 256GB ¥99, 512GB ¥169, 1TB ¥269).

## Capabilities

### New Capabilities
- `image-gallery`: Dynamic product image gallery with DB-driven thumbnails and main image switching
- `showcase-section`: DB-driven showcase section with image, title, description, and feature list
- `product-photos`: DB-driven product photography section with images and captions
- `page-styles`: Dedicated CSS architecture for the openclaw product page with design tokens, grid system, and card classes
- `sticky-navigation`: Sticky anchor navigation bar for long-form product page
- `sticky-purchase-bar`: Persistent purchase CTA bar at bottom of viewport on scroll

### Modified Capabilities
- (none — no existing specs in openspec/specs/)

## Impact

- **`src/templates/sillyclaw/openclaw.html`**: Major refactor — replace hardcoded sections with DB-driven loops, replace inline styles with CSS classes, add macros, add sticky nav and purchase bar
- **`examples/css/openclaw.css`**: New file — ~300 lines of structured CSS
- **`src/modules/sillyclaw/__init__.py`**: Add fallback for reading variants from product.data.variants
- **`src/seed_homepage.py`**: Update sillyclaw seed data with all new fields and independent variants record
- **`examples/css/sillymd.css`**: Remove the openclaw-specific rules (hero, responsive overrides) — migrated to openclaw.css
- **`apps/platform/md/admin-v2/`**: No code changes needed — admin-v2 config-data editor already supports editing arbitrary JSON objects
- **`config_data` table**: Updated seed data for records (sillyclaw, product), (sillyclaw, variants), (sillyclaw, openclaw)
