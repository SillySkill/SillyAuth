## 1. Data Layer — Fix route and seed

- [x] 1.1 Add fallback: In `__init__.py` openclaw route, if `variants` query returns empty, fall back to `product.get("variants", [])`
- [x] 1.2 Update `seed_homepage.py` sillyclaw product data: add `images`, `showcase`, `photos` arrays, all `agents`/`modes`/`security`/`color_system`/`tech_specs`/`use_cases` fields, and `purchase_links` with real URLs
- [x] 1.3 Add independent `variants` seed record with prices matching store_products (128GB ¥69, 256GB ¥99, 512GB ¥169, 1TB ¥269)
- [ ] 1.4 Update `openclaw` seed record: add `hero_video`, `hero_poster`, `badges` array with trust signals
- [x] 1.5 Re-seed database and verify all three config_data records populate correctly

## 2. CSS — Create openclaw.css

- [x] 2.1 Create `examples/css/openclaw.css` with design tokens in `:root` (colors, radius, padding, shadows, transitions)
- [x] 2.2 Add `.oc-card` base class with hover effect (shadow + translateY)
- [x] 2.3 Add color variant classes: `.oc-card-red`, `.oc-card-cyan`, `.oc-card-green`, `.oc-card-orange`
- [x] 2.4 Add grid classes: `.oc-grid-2`, `.oc-grid-3`, `.oc-grid-4`, `.oc-grid-auto` with responsive breakpoints at 900px and 600px
- [x] 2.5 Add section classes: `.oc-section`, `.oc-section-alt`, `.oc-section-header`
- [x] 2.6 Add icon container classes: `.oc-icon-circle`, `.oc-icon-square`
- [x] 2.7 Add sticky nav styles: `.oc-sticky-nav` with `position: sticky; top: 0; z-index: 100`
- [x] 2.8 Add sticky purchase bar styles: `.oc-sticky-bar` with `position: fixed; bottom: 0` and slide-up animation
- [x] 2.9 Add gallery styles (migrated from template `<style>` block)
- [x] 2.10 Add showcase grid and spec table styles (migrated from template)
- [x] 2.11 Add mobile responsive overrides at 480px, 600px, 768px, 900px breakpoints (hiding sticky nav/bar on 480px)

## 3. Template — Refactor openclaw.html

- [x] 3.1 Add `<link rel="stylesheet" href="/static/css/openclaw.css">` to `extra_head` block
- [x] 3.2 Remove the entire `<style>...</style>` block from `extra_head` (styles migrated to openclaw.css)
- [x] 3.3 Define Jinja2 macros at top of template: `oc_section(title, icon, subtitle, alt)`, `oc_card(icon, icon_color, color_variant)`, `oc_grid(n)`
- [x] 3.4 Replace gallery section: use `{% for img in product.images %}` loop instead of hardcoded thumbnails
- [x] 3.5 Replace agents section: use `{% call oc_card() %}` macros with icon circle, remove inline styles
- [x] 3.6 Replace modes section: use `oc_grid(3)` + `oc_card()` with dynamic border colors from DB
- [x] 3.7 Replace "why collaborate" section: use `oc_grid(2)` + `oc_card()`, remove inline styles
- [x] 3.8 Replace quality dimensions: use `oc_grid(3)` + `oc_card()`, remove inline styles
- [x] 3.9 Replace workflow step pills: add CSS classes, remove inline styles
- [x] 3.10 Replace security dimensions: use `oc_grid(4)` + `oc_card()`, remove inline styles
- [x] 3.11 Replace color system table: add CSS class for specs table, remove inline styles
- [x] 3.12 Replace dual interface showcase section: use `{% if product.showcase %}` with DB-driven content
- [x] 3.13 Replace tech specs section: add CSS class, remove inline styles
- [x] 3.14 Replace use cases section: use `oc_grid(2)`, remove inline styles
- [x] 3.15 Replace product photos section: use `{% for photo in product.photos %}` loop with `oc-grid-auto`
- [x] 3.16 Replace AI features section: verify it uses existing CSS classes, remove any inline styles
- [x] 3.17 Replace variants section: verify CSS classes, remove inline styles from image tag
- [x] 3.18 Replace channels section: verify CSS classes, remove inline styles
- [x] 3.19 Replace specs table: verify CSS classes, remove inline styles
- [x] 3.20 Add sticky navigation bar HTML after hero section, with anchor links to all section IDs
- [x] 3.21 Add sticky purchase bar HTML at end of content, with IntersectionObserver JS to toggle visibility
- [x] 3.22 Refactor purchase modal: remove inline styles, add CSS classes
- [x] 3.23 Add section anchor IDs to all major sections for sticky nav linking
- [x] 3.24 Update `switchGallery` JS to handle dynamic image count (remove hardcoded query assumption)
- [x] 3.25 Verify template has zero `style="..."` attributes remaining (except DB-driven dynamic colors)

## 4. Cleanup — Remove old code

- [x] 4.1 Remove openclaw-specific CSS rules from `sillymd.css` (hero section override rules, responsive overrides) — now in openclaw.css
- [x] 4.2 Verify `/openclaw` page renders correctly after all changes — hero, gallery, agents, modes, security, showcase, photos, variants, channels, specs all display
- [x] 4.3 Verify sticky nav appears on scroll past hero and links work
- [x] 4.4 Verify sticky purchase bar appears on scroll past variants
- [x] 4.5 Test responsive layout at 480px, 768px, 1024px widths — no broken grids, no horizontal scroll
- [x] 4.6 Test with empty DB fields — verify sections gracefully hide (conditional rendering)
