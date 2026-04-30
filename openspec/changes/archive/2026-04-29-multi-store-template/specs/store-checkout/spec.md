## ADDED Requirements

### Requirement: Checkout Flow
The system SHALL provide a complete checkout flow from cart to order confirmation.

#### Scenario: Start checkout
- **WHEN** user clicks "结算" in cart
- **AND** user is logged in
- **THEN** the system SHALL proceed to checkout page
- **AND** display order summary

#### Scenario: Guest checkout
- **WHEN** user is not logged in and attempts checkout
- **THEN** the system SHALL redirect to login with return URL

### Requirement: Shipping Information
The system SHALL collect shipping information during checkout.

#### Scenario: Collect shipping details
- **WHEN** user proceeds to checkout
- **THEN** the system SHALL display a form for:
- **AND**收货人姓名 (Recipient name)
- **AND**联系电话 (Contact phone)
- **AND**收货地址 (Shipping address)

### Requirement: Order Creation
After payment, the system SHALL create an order record.

#### Scenario: Create order on payment success
- **WHEN** payment is confirmed successful
- **THEN** the system SHALL create an order with status `paid`
- **AND** clear the shopping cart
- **AND** display order confirmation with order number

#### Scenario: Order data structure
Each order SHALL contain:
- `order_no`: Unique order number (format: `ORD{YYYYMMDD}{sequence}`)
- `user_id`: Buyer user ID
- `collection_id`: Source collection
- `total_amount`: Total order amount
- `status`: Order status (pending, paid, shipped, completed, cancelled)
- `payment_method`: WeChat Pay or Alipay
- `payment_no`: Payment platform transaction ID
- `shipping_name`, `shipping_phone`, `shipping_address`: Shipping info
