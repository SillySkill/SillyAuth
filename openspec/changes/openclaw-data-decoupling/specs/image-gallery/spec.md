## ADDED Requirements

### Requirement: Product image gallery renders from config_data

The /openclaw page SHALL render the product image gallery section by reading the `product.images` array from the `(sillyclaw, product)` config_data record. Each image entry SHALL contain `src` (URL string) and `alt` (text description) fields. The gallery SHALL display a main image and thumbnail strip below it.

#### Scenario: Gallery renders with images from DB

- **WHEN** the `product.images` array contains 3+ entries with valid `src` and `alt` fields
- **THEN** the gallery SHALL display the first image as the main image AND render a thumbnail for each entry below it

#### Scenario: Gallery empty state

- **WHEN** `product.images` is empty or undefined
- **THEN** the gallery section SHALL NOT render (no empty placeholder)

#### Scenario: Thumbnail click switches main image

- **WHEN** user clicks a gallery thumbnail
- **THEN** the main image SHALL update to show the clicked thumbnail's full-size image AND the clicked thumbnail SHALL receive an `active` visual state

#### Scenario: First thumbnail is active by default

- **WHEN** the gallery first renders
- **THEN** the first thumbnail SHALL have the `active` CSS class applied

#### Scenario: Images use fallback to hardcoded list if DB field missing

- **WHEN** `product.images` is undefined but the template context contains a default image list
- **THEN** the gallery SHALL render with the hardcoded fallback images (for backward compatibility during transition)
