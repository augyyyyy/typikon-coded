---
name: Terminology Enforcer
description: Enforces the UGCC terminology map, prevents key leaks in output, and checks General Menaion category badges.
---
## Trigger Conditions
Triggers when editing user-facing UI labels, cantor dashboard HTML templates, or generating textual output for digests.

## Step-by-Step Procedure
1. Cross-reference all user-facing names with the Royal Doors vocabulary standards defined in `.agents/references/liturgical_authority.md`.
2. Scan output strings for leaked internal machine identifiers (e.g. `Tone_1`, `saint_1`). Use formatters to translate them.
3. Verify that all category badges and names use clean, natural English rather than programmer jargon.

## Verification Checklist
- Confirm zero machine identifiers are present in the final user-facing text.
- Verify that general saint categories map correctly based on `liturgical_authority.md` standards.

## Error Handling
Flag any non-compliant terms and output a mapping warning before writing changes.
