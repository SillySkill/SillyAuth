## ADDED Requirements

### Requirement: Product photos section renders from config_data

The /openclaw page SHALL render the "产品实拍" section by reading the `product.photos` array from the `(sillyclaw, product)` config_data record. Each photo entry SHALL contain `src` (URL), `alt` (text), and `caption` (text) fields.

#### Scenario: Photos render in responsive grid

- **WHEN** `product.photos` contains 3 entries with `src`, `alt`, and `caption`
- **THEN** the section SHALL display photos in a responsive auto-fill grid (`auto-fit, minmax(300px, 1fr)`) with each photo showing the image in a 240px height container AND the caption text centered below

#### Scenario: Photos empty state

- **WHEN** `product.photos` is empty or undefined
- **THEN** the entire "产品实拍" section SHALL NOT render
