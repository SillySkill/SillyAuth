## ADDED Requirements

### Requirement: Payment Integration
The system SHALL integrate with WeChat Pay and Alipay for online payments.

#### Scenario: Initiate WeChat Pay
- **WHEN** user selects WeChat Pay and confirms payment
- **THEN** the system SHALL call payment API to generate WeChat Pay QR code or deep link
- **AND** display payment QR code for user to scan

#### Scenario: Initiate Alipay
- **WHEN** user selects Alipay and confirms payment
- **THEN** the system SHALL call payment API to generate Alipay payment
- **AND** redirect to Alipay or display QR code

### Requirement: Payment Status Check
The system SHALL verify payment status after user completes payment.

#### Scenario: Poll for payment completion
- **WHEN** user scans QR code or completes payment
- **THEN** the system SHALL poll payment status every 2 seconds
- **AND** up to 30 times (60 seconds timeout)
- **AND** update order status when payment is confirmed

#### Scenario: Payment timeout
- **WHEN** payment is not confirmed within 60 seconds
- **THEN** the system SHALL display "Payment timeout, please try again"
- **AND** allow user to retry or cancel

### Requirement: Payment Callback
The system SHALL handle payment callbacks from WeChat/Alipay.

#### Scenario: Process payment callback
- **WHEN** payment platform sends callback with payment result
- **THEN** the system SHALL verify signature
- **AND** update order status accordingly
- **AND** respond with success to payment platform
