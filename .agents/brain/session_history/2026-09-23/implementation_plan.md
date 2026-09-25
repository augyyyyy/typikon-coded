# Implementation Plan: Option 2 — 35-Paschalion All-Key Golden Window Stress Matrix (1970–2050)

## Problem Statement & Context
Currently, the **34-Gate Day/Service Multi-Auditor** (`scripts/service_day_multi_auditor.py`) has only been exhaustively executed against **Year 2026** (Gregorian Pascha April 5) and the 136 Temple Patron collision scenarios. 

However, in the Byzantine liturgical tradition, the movable cycle shifts across **35 possible dates for Pascha** (March 22 through April 25). Every single movable-on-fixed collision (e.g., Annunciation from Great Lent through Bright Week, St. George in Holy Week, Peter and Paul Fast lasting from 0 to 42 days, the Lucan Jump, and Meatfare/Cheesefare boundaries) is uniquely determined by which of the 35 Paschal Keys governs the year.

Until all 35 Paschal Keys are stress-tested against all 34 gates across both Common (365-day) and Leap (366-day) years, edge cases occurring only in rare Paschal positions (such as Annunciation on Holy Thursday, Kyriopascha, or Annunciation on Bright Thursday) remain unverified by the multi-auditor.

---

## User Review Required

> [!IMPORTANT]
> **Execution Scale**: Auditing all 35 Paschal Keys across full annual cycles comprises **35 years $\times$ ~365.25 days = 12,775 liturgical days $\times$ 9 services = ~114,975 services**.
> At current single-process engine speeds (~15–25 days/sec), a complete 35-key sweep takes approximately 8–12 minutes. We will implement high-throughput batched execution in `scripts/audit_35_paschal_matrix.py` with progress tracking, granular failure capture, and JSON summary persistence (`audit_35_keys_results.json`).

> [!NOTE]
> **Logic Hub vs Text Spoke Principle (Master Rule 7)**:
> In accordance with Hub-Spoke architecture, missing verbatim hymn text in Spokes emits non-blocking text warnings (`⚠️ [Text Warning]`), while logical, structural, rubric, tone, or rank precedence errors result in hard halts.

---

## Open Questions
*None currently blocking.* The 35 Paschal Key mappings for both Gregorian and Julian calendars are already cataloged in `scripts/audit_35_paschal_keys.py`.

---

## Proposed Changes

### 1. Matrix Auditor Engine & Script

#### [NEW] [scripts/audit_35_paschal_matrix.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/audit_35_paschal_matrix.py)
A specialized high-throughput multi-year auditor that:
- Iterates over all 35 canonical Paschal Key years across the Golden Window (1970–2050) and representative leap years.
- Initializes `RuthenianEngine` and `ServiceDayMultiAuditor` for each key year.
- Runs all 9 services of each day through the 34 validation gates.
- Audits deep cross-calendar invariants:
  1. **Annunciation Movable Spectrum (March 25)**: Kyriopascha, Palm Sunday, Lazarus Saturday, Holy Thursday, Holy Friday, Holy Saturday, Bright Monday through Bright Saturday, Thomas Sunday, and 3rd–6th weeks of Great Lent.
  2. **St. George Movable Spectrum (April 23)**: Holy Week transfers to Bright Monday/Tuesday.
  3. **Lucan Jump Continuity**: 18th Sunday after Pentecost through 32nd Sunday sequence and gospel reading distribution.
  4. **Peter and Paul Fast Duration**: Continuity for lengths from 0 days (when Pascha is latest) to 42 days (when Pascha is earliest).
  5. **Tone Cycle Continuity**: Tones 1 through 8 uninterrupted rotation across movable and fixed boundaries.
  6. **Triodion Season Bounds**: Zacchaeus Sunday, Publican & Pharisee Sunday, and Lent start offsets.
- Produces structured output `audit_35_paschal_matrix_results.json` documenting every scanned key, total days, total services, and zero tolerance for halts.

### 2. Regression Test Integration

#### [NEW] [tests/test_35_paschal_matrix.py](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_35_paschal_matrix.py)
Automated pytest suite that samples boundary and edge Paschal Keys:
- Earliest possible Pascha (March 22): Tests longest Pentecost/Lent gap, 42-day Peter & Paul Fast.
- Latest possible Pascha (April 25): Tests Kyriopascha, 0-day Peter & Paul Fast, Annunciation on Pascha.
- Mid-spectrum keys (March 25, April 5, April 12): Tests Annunciation on Holy Week / Bright Week.
- Leap year edge keys.

---

## Verification Plan

### Automated Tests
1. **Pre-flight & Compliance**:
   ```powershell
   $env:PYTHONPATH="." ; .venv\Scripts\python.exe -m pytest tests/test_session_compliance.py --verbose
   ```
2. **Execute 35-Paschal-Key Matrix Auditor**:
   ```powershell
   $env:PYTHONPATH="." ; .venv\Scripts\python.exe scripts/audit_35_paschal_matrix.py --paschalion both --type both
   ```
3. **Run 35-Paschalion Pytest Suite**:
   ```powershell
   $env:PYTHONPATH="." ; .venv\Scripts\python.exe -m pytest tests/test_35_paschal_matrix.py --verbose
   ```
4. **Full Test Suite Regression**:
   ```powershell
   $env:PYTHONPATH="." ; .venv\Scripts\python.exe -m pytest --ignore=tests/test_ui_readability.py --verbose
   ```

### Manual Verification
- Verify `audit_35_paschal_matrix_results.json` reports 0 halting violations across all 35 keys.
- Check specific edge days in output logs (Kyriopascha March 25, St. George transfers, Lucan Jump).
