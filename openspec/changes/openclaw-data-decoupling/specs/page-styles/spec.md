## ADDED Requirements

### Requirement: Dedicated CSS file with design tokens

The /openclaw page SHALL load a dedicated CSS file from `/static/css/openclaw.css`. This file SHALL define CSS custom properties (design tokens) for all reusable visual values: colors, border-radius, padding, shadows, and transitions. The template SHALL NOT contain any inline `style="..."` attributes for layout or visual styling (with the exception of dynamic color values like agent accent colors that come from DB).

#### Scenario: CSS file loads correctly

- **WHEN** the /openclaw page renders
- **THEN** the `<head>` SHALL include a `<link rel="stylesheet" href="/static/css/openclaw.css">` tag AND the browser SHALL successfully load the file (HTTP 200)

#### Scenario: Design tokens are defined

- **WHEN** inspecting the openclaw.css `:root` block
- **THEN** the following CSS custom properties SHALL be present: `--oc-primary`, `--oc-text`, `--oc-text-secondary`, `--oc-bg`, `--oc-bg-alt`, `--oc-border`, `--oc-radius`, `--oc-radius-sm`, `--oc-padding`, `--oc-shadow`, `--oc-shadow-hover`, `--oc-transition`

#### Scenario: Card class provides consistent styling

- **WHEN** an element has the `.oc-card` class
- **THEN** it SHALL have: white background, `--oc-radius` border-radius, `--oc-padding` padding, 1px solid `--oc-border` border, and `--oc-shadow` box-shadow. On hover it SHALL apply `--oc-shadow-hover` and translateY(-2px).

#### Scenario: Grid classes for 2/3/4 columns

- **WHEN** an element has the `.oc-grid-2` class
- **THEN** it SHALL render as a 2-column grid with 24px gap

- **WHEN** an element has the `.oc-grid-3` class
- **THEN** it SHALL render as a 3-column grid with 20px gap

- **WHEN** an element has the `.oc-grid-4` class
- **THEN** it SHALL render as a 4-column grid with 16px gap

#### Scenario: Grid classes collapse on mobile

- **WHEN** viewport width is 900px or less
- **THEN** `.oc-grid-4` SHALL become 2 columns AND `.oc-grid-3` SHALL become 2 columns

- **WHEN** viewport width is 600px or less
- **THEN** `.oc-grid-2`, `.oc-grid-3`, and `.oc-grid-4` SHALL all become 1 column

#### Scenario: No [style*='...'] selectors in CSS

- **WHEN** inspecting the final openclaw.css
- **THEN** there SHALL be zero CSS selectors using the `[style*=...]` attribute selector pattern AND there SHALL be zero `!important` declarations for responsive overrides
