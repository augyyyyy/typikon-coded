# Walkthrough: Footnote & Synodal Callout Graceful Formatting Overhaul

## Problem Identified
In the Cantor Dashboard and Service Rubrics Digest, Dolnytsky Synodal Footnote callouts (e.g. `💡 Dolnytsky Note [^7] (Synodal Rubric Alternative): ...`) were rendered as unstyled generic blockquotes:
1. **Lack of Spacing & Container**: The note lacked vertical separation from the preceding rubric line and had no container box.
2. **Text Collision**: The entire header was styled in bright rubric red due to generic `<strong>` tag styling inside service bodies.
3. **Unformatted Badges**: The category badge (`Synodal Rubric Alternative` vs `Parish Custom`) was rendered as raw parenthetical text rather than a distinct pill badge.

---

## Solutions Implemented

### 1. Dedicated Callout Card Component (`.synodal-callout`)
Transformed inline Synodal Footnotes into structured card containers with:
- **Vertical Spacing**: Generous `margin: 18px 0 8px 0; padding: 12px 16px; border-radius: 8px;` ensuring clear demarcation.
- **Accented Container**: Subtle gold tint background with a 4px solid gold accent left border (`border-left: 4px solid var(--gold-accent)`).
- **Graceful Header**: Dedicated header flex row with:
  - 💡 Icon
  - **Dolnytsky Note <sup>[^N]</sup>** in gold heading typography
  - Distinct category pill badge (`.badge-synodal-alt` vs `.badge-parish-custom`)
- **Proper Body Styling**: Clean secondary text color in `font-style: normal; line-height: 1.55;` with italic highlights for liturgical terms.

### 2. End-of-Digest Footnotes List Cards (`.synodal-footnote-item`)
Transformed the end-of-digest appendix notes (`## SYNODAL FOOTNOTES & ALTERNATIVE PRACTICES`) into structured list cards with badge chips and part markers.

### 3. Backend Separator Refinement (`digest/formatters/footnotes.py`)
Updated `_format_service_synodal_callouts` to separate multiple consecutive callouts with `\n\n` for clean block boundaries.

---

## Verification Evidence
- **Pre-flight & Session Compliance**: Passed (100%).
- **Synodal Footnote Tests**: 4 passed in 0.56s (`tests/test_synodal_footnotes.py`).
- **Full Test Suite**: **397 passed in 106.58s** (0 failures).
