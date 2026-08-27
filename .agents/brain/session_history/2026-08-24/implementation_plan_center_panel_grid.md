# Implementation Plan: 4x2 Grid Service Cards for Center Panel

Restructure the Center Panel (`#main-document-panel` / `#booklet-content`) from a single continuous wall of text into a responsive **4x2 Grid of Service Cards** mirroring the 8 options from the Right Panel dropdown menu.

## Proposed Changes

### 1. Structure & Layout (`cantor_dashboard/index.html`)
- Update `#doc-booklet` to include a view filter dropdown (`All Services (4x2 Grid)` + individual service selectors).
- Add the focus/maximize modal overlay (`#card-focus-modal`) for single-service kiosk and music stand reading.

### 2. Styling (`cantor_dashboard/style.css`)
- Implement `.booklet-grid` with CSS Grid (4 columns × 2 rows on desktop, responsive breakpoints on smaller screens).
- Create `.service-card`, `.service-card-header`, `.service-card-title`, `.service-card-badge`, `.service-card-actions`, `.service-card-body`, and `.service-card-footer`.
- Style the focus modal dialog for full-screen reading with font zoom and print controls.
- Maintain full compatibility with Light and Dark modes.

### 3. Rendering & Event Logic (`cantor_dashboard/main.js`)
- Add `parseBookletServices(bookletText)` to partition full booklet text into 8 discrete service blocks:
  1. `General Info`
  2. `Vespers`
  3. `Compline`
  4. `Midnight Office`
  5. `Matins`
  6. `Hours`
  7. `Divine Liturgy`
  8. `All Services`
- Implement `renderBookletGrid()` to dynamically build the 8 service cards with liturgical icons, tone badges, status indicators (Appointed vs. Suppressed), and formatted chant/rubric text.
- Wire up card maximize/focus modals, individual card copy/print actions, and top view-filter selector.

## Verification Plan

### Automated Tests
- Run `tests/test_session_compliance.py` to ensure zero regressions and compliance.
- Run full pytest suite: `pytest --ignore=tests/test_ui_readability.py`.

### Manual / Browser Verification
- Start the server on port 8080 and resolve multiple dates:
  - Clean Monday (Lent)
  - Sunday after Feast (Apodosis / Vigil)
  - Pascha / Great Feast
- Verify the 4x2 grid renders all 8 service cards cleanly.
- Verify focus modal, copy, and print functions.
