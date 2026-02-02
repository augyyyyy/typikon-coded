# Recension Gap Report: Stamford (2014) vs. Dolnytsky Typikon

## Overview
This document tracks structural and content discrepancies between the implemented "Stamford (2014)" recension and the authoritative "Dolnytsky Typikon". The goal is to fully support the unabridged Dolnytsky standard while maintaining the ability to render the specific Stamford usage.

## 1. Matins (Great Matins)

### The Six Psalms (Hexapsalmos)
- **Dolnytsky Standard**: 
  - Comprised of Psalms 3, 37, 62, 87, 102, 142.
  - "Morning Prayers" (12 Silent Prayers) are read by the priest *during* the psalms (usually first 6 during the first half, last 6 during the second half, or all together).
  - Explicit timing for the priest's exit/re-entry.
- **Current Implementation (Stamford)**:
  - Psalms are atomized (`psalm_3` ... `psalm_142`).
  - **CRITICAL GAP**: The 12 "Morning Prayers" are lumped as a text block appended to `psalm_142`.
  - **CRITICAL GAP**: Missing "Mid-Six-Psalms Doxology" (Glory... Now... Alleluia...) between Psalm 62 (LXX 63) and Psalm 87 (LXX 88).
  - **Issue**: Causes a massive "wall of text" and misses the liturgical pause/division prescribed by Dolnytsky.
- **Remediation Plan**:
  - [x] Extract Morning Prayers from `psalm_142` into `horologion.matins.prayer_1` to `prayer_12`.
  - [x] Create `horologion.matins.mid_six_psalms_doxology` key.
  - [x] Update `01i_struct_matins.json` to insert Doxology and interleaving logic.

### God is the Lord
- **Dolnytsky Standard**:
  - Dynamic Tone selection based on the *first* Troparion (Resurrectional tone on Sunday, Feast tone otherwise).
  - Specific rules for "Glory/Both Now" separation.
  - Validated as working for Tone 6 Sunday (2026-01-04).
  - Logic engine correctly switches context.

### The Canon
- **Dolnytsky Standard**: Small Litanies after Ode 3 and Ode 6.
- **Current Implementation**:
  - ✅ **RESOLVED (2026-02-01)**: Added `horologion.litany_small` to `canon_insertions.after_3rd` and `after_6th` in `02e_logic_matins.json`.
- **Action**:
  - [x] Add `horologion.litany_small` to `canon_insertions.after_3rd` and `after_6th` in `02e_logic_matins.json`.

### Gospel Rite
- **Dolnytsky Standard**: Gospel Reading -> Ps 50 -> "Glory... Apostles..." -> "Have mercy on me..." -> "Having beheld the Resurrection".
- **Current Implementation**:
  - ✅ **Verified**: `matins_gospel_rite` components exist in JSON.
  - ✅ **RESOLVED (2026-02-01)**: Implemented `resolve_matins_gospel` and `resolve_post_gospel_stichera` in `ruthenian_engine.py`.
- **Action**:
  - [x] Implement `resolve_matins_gospel` (Eothinon logic).
  - [x] Implement `resolve_post_gospel_stichera` (Glory/BothNow/JesusRisen logic).

### Praises (The Ainoi)
- **Dolnytsky Standard**: Psalms 148-150 with Stichera. Sunday: 8 Stichera.
- **Current Implementation**:
  - ✅ **RESOLVED (2026-02-01)**: Implemented `resolve_praises_stichera` in `ruthenian_engine.py`.
- **Action**:
  - [x] Implement `resolve_praises_stichera` (Psalms + Stichera logic).

### Great Doxology
- **Dolnytsky Standard**: Sung or Read based on rank.
- **Current Implementation**:
  - ✅ **RESOLVED (2026-02-01)**: Updated `resolve_doxology_type` to return renderable `fixed_ref`.
- **Action**:
  - [x] Update Renderer or Logic to return renderable content (e.g. `fixed_ref`).

## 2. Fixed Text Gaps
- **Six Psalms Intro**: ✅ **Verified**. "Glory to God in the highest" (3x) and "Lord, open my lips" (2x) verified in structure.
- **Mid-Six-Psalms Doxology**: ✅ **Verified**. A liturgical Doxology was missing between Psalm 62 and 87. Added `horologion.matins.mid_six_psalms_doxology` to `01i_struct_matins.json` and `text_horologion.json`.

## 3. Structural/Order Issues
- **Morning Prayers**: ✅ **Verified**. Split into 12 atomic prayers (`prayer_1` to `prayer_12`). Listed in structure. Logic for interleaving is deferred but structural integrity is fixed.
