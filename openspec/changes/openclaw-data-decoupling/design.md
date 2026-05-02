## Context

The /openclaw product page for 傻福虾盘 serves as a marketing + e-commerce landing page rendered server-side via FastAPI + Jinja2. Currently, the template (`src/templates/sillyclaw/openclaw.html`) reads data from PostgreSQL `config_data` table as three key-value records:

- `(sillyclaw, product)` — product specs, agent descriptions, mode data, etc.
- `(sillyclaw, variants)` — NOT seeded, always empty at runtime
- `(sillyclaw, openclaw)` — store info, channel links, AI features

Additionally, there's a separate `store_products` table with priced SKUs (128GB ¥69 — 1TB ¥269) that is NOT used by the template. The template also has ~40% hardcoded content (gallery images, showcase section, product photos, hero video path) and ~50 instances of inline `style="..."` attributes with fragile responsive overrides using `[style*='...']` selectors.

The admin-v2 panel already provides a JSON editor for config_data records, so backend CRUD is covered — we just need to ensure the template reads the new fields and the seed data populates them.

## Goals / Non-Goals

**Goals:**
- 100% of visible page content driven by config_data (not hardcoded in template)
- All inline styles extracted to a single, maintainable CSS file with design tokens
- Variants pipeline fixed so the spec selection section works end-to-end
- Seed data populated with complete, real-world content
- Template reduced from ~630 to ~400 lines via macros and DRY patterns
- Responsive design using proper CSS media queries (not `[style*='...'] !important`)

**Non-Goals:**
- No migration of store_products table usage (keeping two systems, just aligning prices)
- No image upload API — admin can manage image URLs as text fields in the JSON editor
- No SSR streaming or client-side rendering changes
- No i18n in this change — hero/badge text and section headings remain in Chinese in the template
- No automated visual regression testing

## Decisions

### Decision 1: Keep 3 config_data records (don't merge into 1)

**Choice**: Maintain separate `product`, `variants`, and `openclaw` records.

**Rationale**: Each has distinct update frequency and ownership:
- `product` — core product data (rarely changes after initial setup)
- `variants` — SKU list (changes with inventory/promotions; needs quick admin edits)
- `openclaw` — store-level config (channels, hero settings, independent of product)

Merging everything into one giant JSON blob would make partial updates error-prone and increase the risk of one admin overwriting another's changes.

### Decision 2: Route-level fallback for variants instead of restructuring

**Choice**: In `__init__.py`, if `config_data` query for `(sillyclaw, variants)` returns empty, fall back to `product.data.variants`.

**Rationale**: The seed currently puts variants inside `product.data`. Rather than rewriting the seed format (which would break existing production data without a migration), we add a two-line fallback. This makes the page work immediately regardless of which data format is used. Long-term, the seed will create an independent variants record.

**Alternatives considered**:
- *Migration script to move variants out* → Over-engineered for single-tenant setup
- *Change seed only and leave runtime* → Wouldn't fix existing installations

### Decision 3: CSS as a static file, not in-DB

**Choice**: Create `examples/css/openclaw.css` served at `/static/css/openclaw.css`.

**Rationale**: CSS is presentation, not content. Putting it in DB would:
- Require a CSS editor in admin UI (complex)
- Prevent browser caching (inline styles can't be cached)
- Lose CSS preprocessing capabilities
- Make it impossible to use CSS features like `@media`, `@keyframes`, `:hover` predictably

The boundary: **content** goes in DB, **presentation** goes in CSS.

### Decision 4: Jinja2 macros for repeated patterns

**Choice**: Define `oc_section()`, `oc_card()`, `oc_grid()` macros at template top, then use `{% call %}` blocks for section content.

**Rationale**: Currently the template repeats the same card structure ~15 times with different inline styles. A macro:
- Ensures visual consistency (all cards use the same padding/radius/shadow)
- Allows global style changes by editing one place
- Reduces template line count by ~40%
- Keeps markup readable (the macro call is 3 lines instead of 12)

### Decision 5: Sticky nav and purchase bar as progressive enhancement

**Choice**: Sticky nav appears via CSS `position: sticky` with `top: 0`. Sticky purchase bar appears when the user scrolls past the variants section, using a CSS class toggle via IntersectionObserver (not scroll event listener, for performance).

**Rationale**:
- `position: sticky` is well-supported (IE11 is not a target) and avoids JavaScript scroll handlers
- IntersectionObserver is more performant than scroll events for toggling visibility
- Both degrade gracefully — if JS fails, the page is still fully usable

### Decision 6: Match config_data variant prices with store_products

**Choice**: Seed config_data variants with the exact same prices as store_products table: 128GB ¥69, 256GB ¥99, 512GB ¥169, 1TB ¥269.

**Rationale**: Having two data sources with different prices would be confusing. Since the template reads from config_data, we align config_data with the "source of truth" (store_products). A future change could consolidate to a single source, but that's out of scope here.

## Risks / Trade-offs

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| [Risk] Template breakage from large refactor | Medium | Keep old template as backup. Test `/openclaw` route after each change phase. |
| [Risk] Forgetting to update seed_homepage.py | Low | The change explicitly tasks this. The running server's in-memory data won't update until re-seed, but that's existing behavior. |
| [Risk] Admin edits inline styles being lost | Low | All styles are now in openclaw.css, not inline. Admin edits data fields only. |
| [Risk] Sticky nav conflicting with existing page layout | Low | Sticky nav uses `z-index` layering. Test on mobile where screen real estate is limited. |
| [Trade-off] Two parallel product data systems remain | — | Acceptable for now. config_data serves the marketing page; store_* powers future cart/checkout. Documented in seed as known debt. |
| [Trade-off] Image URLs are plain text in JSON | — | Acceptable. Admin copies/pastes URLs. Image upload endpoint exists at `/api/v1/storage/upload` if needed later. |
