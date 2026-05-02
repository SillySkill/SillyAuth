## ADDED Requirements

### Requirement: Sticky anchor navigation bar

The /openclaw page SHALL display a horizontal navigation bar below the hero section that sticks to the top of the viewport as the user scrolls. The nav SHALL contain anchor links to the major page sections: 产品概览, 双Agent, 运行模式, 安全保障, 规格价格, and an emphasized "立即购买" link.

#### Scenario: Nav bar is sticky on scroll

- **WHEN** user scrolls past the hero section
- **THEN** the navigation bar SHALL stick to the top of the viewport (using `position: sticky; top: 0`) AND SHALL remain visible while scrolling through content sections

#### Scenario: Nav links scroll to correct sections

- **WHEN** user clicks any nav link (e.g., "双Agent")
- **THEN** the page SHALL smoothly scroll to the corresponding section's anchor ID (`#agents`)

#### Scenario: Nav bar has emphasized purchase link

- **WHEN** viewing the navigation bar
- **THEN** the "立即购买" link SHALL be visually distinct (primary button styling) from the other nav items AND SHALL scroll to the `#variants` section

#### Scenario: Nav bar is hidden on very small screens

- **WHEN** viewport width is 480px or less
- **THEN** the sticky navigation bar SHALL be hidden to preserve screen space
