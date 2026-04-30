## ADDED Requirements

### Requirement: Reusable Store Template
The system SHALL provide a single HTML template (`store.html`) that renders different product collections based on URL.

#### Scenario: Load SillyClaw collection at /openclaw
- **WHEN** user visits `/openclaw`
- **THEN** the system SHALL fetch collection with key `sillyclaw`
- **AND** render products from that collection
- **AND** display store name as "傻福虾盘"

#### Scenario: Load Electronics collection at /store/electronics
- **WHEN** user visits `/store/electronics`
- **THEN** the system SHALL fetch collection with key `electronics`
- **AND** render products from that collection

#### Scenario: Handle non-existent collection
- **WHEN** user visits `/store/nonexistent`
- **AND** collection does not exist
- **THEN** the system SHALL display "Collection not found" message
- **AND** suggest available collections

### Requirement: Dynamic Product Rendering
The system SHALL render products dynamically fetched from the API.

#### Scenario: Display product grid
- **WHEN** products are loaded for a collection
- **THEN** each product SHALL display: image, name, price, and "加入购物车" button
- **AND** out-of-stock products SHALL show "暂时缺货" badge

#### Scenario: Product quick view
- **WHEN** user clicks on a product card
- **THEN** the system SHALL display a modal with product details
- **AND** allow quantity selection and add-to-cart
