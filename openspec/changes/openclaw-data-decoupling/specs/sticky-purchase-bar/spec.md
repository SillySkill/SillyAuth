## ADDED Requirements

### Requirement: Sticky purchase bar at bottom of viewport

The /openclaw page SHALL display a fixed-position purchase bar at the bottom of the viewport that appears when the user scrolls past the variants section. The bar SHALL show the product name, selected variant info (if any), price, and a prominent "立即购买" button that opens the purchase modal.

#### Scenario: Purchase bar appears when variants section is scrolled past

- **WHEN** the variants section (`#variants`) scrolls above the top of the viewport
- **THEN** the sticky purchase bar SHALL slide up from the bottom of the viewport with a smooth transition

#### Scenario: Purchase bar is hidden initially

- **WHEN** the page first loads and the user is at the top of the page
- **THEN** the sticky purchase bar SHALL NOT be visible

#### Scenario: Purchase button opens modal

- **WHEN** user clicks the "立即购买" button in the sticky bar
- **THEN** the purchase modal SHALL open with the same behavior as clicking "立即购买" in the variants cards

#### Scenario: Variant selection from cards updates bar

- **WHEN** user selects a variant from the cards section
- **THEN** the sticky purchase bar SHALL update to show the selected variant's capacity, color, and price

#### Scenario: Bar is hidden on mobile to avoid crowding

- **WHEN** viewport width is 480px or less
- **THEN** the sticky purchase bar SHALL be hidden to avoid overlapping with content
