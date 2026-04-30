## ADDED Requirements

### Requirement: Collection-isolated Shopping Cart
Each collection SHALL have its own separate shopping cart.

#### Scenario: Add item to cart
- **WHEN** user clicks "加入购物车" on a product
- **THEN** the item SHALL be added to the cart for the current collection only
- **AND** cart SHALL store `collection_id` with each item

#### Scenario: View cart
- **WHEN** user clicks the cart icon
- **THEN** the system SHALL display items from the current collection only
- **AND** show subtotal for the collection

### Requirement: Cart Item Management
Users SHALL be able to modify cart item quantities and remove items.

#### Scenario: Update quantity
- **WHEN** user changes quantity of a cart item
- **THEN** the system SHALL update the item via API
- **AND** recalculate the subtotal

#### Scenario: Remove item
- **WHEN** user clicks remove/delete