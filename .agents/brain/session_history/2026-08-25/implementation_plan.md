# Gate 11: Typography, Readability & Visual Formatting Standards

## Overview
Added Gate 11 (Formatting & Readability Standards) to the 365-day sequential multi-auditor suite and refactored digest formatters across all 7 service cards to eliminate dense semicolon walls of text and enforce structured markdown bold leads.

## Key Changes
1. **Hours Formatter Refactoring (`digest/formatters/hours.py`)**:
   - Split Troparia and Kontakia into distinct, structured blocks with bold rubric leads (`**Troparia:**`, `**Kontakia:**`).
   - Formatted each hour on its own line separated by markdown linebreaks (`  \n`).
2. **Paschal Vespers Formatter (`digest/formatters/vespers.py`)**:
   - Implemented `_format_paschal_vespers` generating clean, structured rubrics for Agape Vespers and Bright Week Vespers with bold rubric leads.
3. **Auditor Suite Gate 11 (`scripts/service_day_multi_auditor.py`)**:
   - Added `gate11_formatting_readability` to check all 7 service cards across all 365 days for:
     - Mandatory bold rubric leads.
     - Separation of Troparia and Kontakia blocks.
     - Prohibition of monolithic unbroken lines (>250 chars) with raw semicolons.
4. **Vocabulary Standardization Matrix Alignment**:
   - Standardized all 25 warning messages in `scripts/audit_all_days_heuristics.py`, `scripts/service_day_multi_auditor.py`, and `scripts/run_liturgical_audit_pipeline.py`.
   - Removed erroneous `holy doors` rule.

## Verification Results
- **Multi-Auditor**: `365/365 days passed (3,214 services checked)`.
- **PyTest Suite**: `393 passed in 87.32s`.
- **Session Compliance**: `1 passed in 0.38s`.