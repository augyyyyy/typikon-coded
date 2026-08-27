# Cantor Dashboard Multi-Device Responsive Layout & Klieros Stand Mode

This plan details the styling and layout modernization of the **Cantor Dashboard** to provide an optimal user experience across all screen sizes:
1. **Small Mobile** (320px – 480px, e.g., iPhone SE, modern smartphones)
2. **Tablets & Foldables** (600px – 1024px, e.g., iPad Mini, iPad Air, Surface Go)
3. **Small Laptops & PCs** (1024px – 1440px)
4. **Large / Ultra-Wide Displays** (1440px – 4K / 3840px)
5. **Klieros / Analogion Stand Mode** (high-legibility fullscreen chant view with Screen Wake Lock API)

---

## User Review Required

> [!IMPORTANT]
> The redesign introduces:
> - A dedicated **Mobile Bottom Navigation Bar** for screens `< 768px` (replaces the top sidebar stack to reclaim 200px+ vertical space).
> - Dynamic Viewport Units (`100dvh`) with safe-area insets for iOS Safari and Android Chrome.
> - A **Stand Mode & Font Scaler (`[A−] [A+]`)** in the booklet toolbar with Screen Wake Lock to prevent tablet screens from turning off mid-service.
> - Fluid container layouts removing the hardcoded `min-width: 650px` collision on tablets and small laptops.
> - An optimal reading measure (`max-width: 78ch`) on ultra-wide screens to prevent eye strain.

---

## Proposed Changes

### Cantor Dashboard Styling & Design System

#### [MODIFY] [cantor_dashboard/style.css](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/cantor_dashboard/style.css)
- **Root & Dynamic Viewport**:
  - Update `html, body, .app-container` to use `min-height: 100dvh` and safe area insets.
  - Define custom properties for font scaling (`--font-scale-modifier`) and line measure.
- **Mobile Bottom Navigation Bar**:
  - Add `.mobile-bottom-nav` styles (fixed bottom, 4 icon tabs, active state indicators, 48px touch targets, frosted glass styling).
  - Add `.mobile-top-bar` for compact header with logo, theme toggle, and settings drawer button.
  - Hide standard desktop `.app-sidebar` on mobile viewports (`< 768px`).
- **Tablet & Small Laptop Fluid Layout**:
  - Remove fixed `min-width: 650px` on `.document-col` and `.document-content-wrapper`.
  - Add `.context-collapsed` state allowing the Cantor Booklet to expand to 100% width.
  - Add tablet icon rail styles (64px compact mode for 768px–1024px).
- **Controls & Quick Jumps Strip**:
  - Style `.quick-links` as a horizontal swipeable pill container with smooth scrolling.
  - Wrap and align `.doc-controls` with flex wrap and touch-friendly button padding.
- **Ultra-Wide & Reading Constraints**:
  - Add `.book-style` measure constraints (`max-width: 78ch; margin: 0 auto;`) for single-column views on wide screens.
  - Add optional `.two-column-book-mode` multi-column layout for ultra-wide monitors.
- **Klieros Stand Mode**:
  - Fullscreen chant view with high contrast red/black typography, hidden navigation chrome, and enlarged liturgical drop caps.

---

### Cantor Dashboard HTML Template

#### [MODIFY] [cantor_dashboard/index.html](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/cantor_dashboard/index.html)
- Add `<nav class="mobile-bottom-nav">` with 4 navigation buttons (📅 Resolver, 📖 Books, 🔍 Auditor, 🗺️ Feasts).
- Add `<header class="mobile-top-bar">` with brand title, theme toggle, and overrides quick toggle.
- Add Font Scaler controls (`[A−] [A+]`) and Stand Mode toggle button (`📖 Stand Mode`) inside `.doc-controls`.
- Add Context Toggle button (`◀ Context`) to the liturgical calendar controls.

---

### Cantor Dashboard Interactive Engine

#### [MODIFY] [cantor_dashboard/main.js](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/cantor_dashboard/main.js)
- Wire mobile bottom navigation buttons to the existing `switchTab()` controller.
- Implement Font Scaler (`cantor-font-scale` in `localStorage`) to adjust text size from 80% to 150%.
- Implement **Klieros Stand Mode**:
  - Toggle full-screen mode (`requestFullscreen`).
  - Request browser Screen Wake Lock (`navigator.wakeLock.request('screen')`) to prevent screen timeout while chanting.
- Implement Context Sidebar Toggle (hide/show context card to give 100% width on tablet stands).
- Ensure resize drag handles smoothly adapt and respect container boundaries.

---

## Verification Plan

### Automated Tests
- Run session compliance check:
  `python -m pytest tests/test_session_compliance.py --verbose`
- Run UI readability and layout tests across Mobile (375x667), Tablet (768x1024), and Desktop (1200x800):
  `python -m pytest tests/test_ui_readability.py --verbose`
- Run full test suite:
  `python -m pytest --ignore=tests/test_ui_readability.py --verbose`

### Manual & Responsive Verification
- Verify layout across viewport breakpoints:
  - 375px (iPhone SE / mobile portrait)
  - 414px (iPhone Pro Max / Android phone)
  - 768px (iPad Mini portrait)
  - 1024px (iPad landscape / Surface Go)
  - 1366px (Standard laptop)
  - 1920px (1080p Desktop)
  - 2560px+ (Ultra-wide monitor)
- Verify Stand Mode toggle, Wake Lock activation, and Font Scaling controls.
