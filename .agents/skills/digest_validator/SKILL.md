---
name: Digest Validator
description: Extracts PDF gold standard text via PyMuPDF and performs line-by-line comparison.
---
## Trigger Conditions
Triggers when modifying liturgical generation logic, layout formatting, or digest generation parameters.

## Step-by-Step Procedure
1. Generate the service digest for a specific target date (e.g. `2026-02-01`) using `generate_typikon_service.py`.
2. Locate the corresponding PDF reference file in `C:\Users\augus\OneDrive\Desktop\Typikon digest\`.
3. Extract the PDF text programmatically using PyMuPDF (`fitz`).
4. Perform a line-by-line comparison between the generated output and the extracted PDF reference text.
5. Record correct lines, wrong lines, missing lines, and extra lines.

## Verification Checklist
- Perform comparative line count check.
- Report all four metrics: correct, wrong, missing, and extra.
- Ensure 100% compliance before declaring a layout change completed.

## Error Handling
If any lines are incorrect or missing, treat it as a blocking regression and revert or fix the corresponding resolver logic.
