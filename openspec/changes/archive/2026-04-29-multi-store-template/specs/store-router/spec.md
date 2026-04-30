## ADDED Requirements

### Requirement: URL-based Collection Routing
The system SHALL route requests to the appropriate store collection based on URL path.

#### Scenario: Route to SillyClaw via /openclaw
- **WHEN** user navigates to `/openclaw`
- **THEN** the system SHALL resolve this to collection key `sillyclaw`
- **AND** load the SillyClaw product collection

#### Scenario: Route to collection via /store/{key}
- **WHEN** user navigates to `/store/electronics`
- **THEN** the system SHALL extract `electronics` as the collection key
- **AND** load the electronics product collection

#### Scenario: Collection alias
- **WHEN** a collection has an alias configured (e.g., `openclaw` for `sillyclaw`)
- **THEN** both `/openclaw` and `/store/sillyclaw` SHALL resolve to the same collection

### Requirement: Collection Navigation
The system SHALL provide navigation to switch between collections.

#### Scenario: Collection switcher
- **WHEN** user is on any store page
- **THEN** the system SHALL display a collection switcher in the header
- **AND** allow quick navigation to other collections
