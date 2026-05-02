## ADDED Requirements

### Requirement: Showcase section renders from config_data

The /openclaw page SHALL render its feature showcase section (currently the "双接口展示" section) by reading the `product.showcase` object from the `(sillyclaw, product)` config_data record. The showcase SHALL contain: `image` (URL), `title` (string), `desc` (string), and `features` (array of strings).

#### Scenario: Showcase renders with full data

- **WHEN** `product.showcase` contains all required fields (`image`, `title`, `desc`, `features`)
- **THEN** the showcase section SHALL display the image on the left, title + description + feature list on the right

#### Scenario: Showcase empty state

- **WHEN** `product.showcase` is undefined or null
- **THEN** the showcase section SHALL NOT render

#### Scenario: Feature list renders each item

- **WHEN** `product.showcase.features` is an array of 3+ strings
- **THEN** each string SHALL render as a list item with a check-circle icon prefix
