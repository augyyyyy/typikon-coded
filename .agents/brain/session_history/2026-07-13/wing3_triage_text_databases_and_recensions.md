<!-- [GENERATOR: Gemini 3.7 Flash] -->
# Granular Triage Plan: Wing 3 — Text Databases & Recensions

## 1. Wing Identity & Scope
* **Wing Name**: Wing 3 (Text Databases & Recensions)
* **Codebase Location**: `Typikon Coded/Data/Service Books/Recensions/` + `json_db/stamford/` + `schemas/text_asset.schema.json`
* **Health Status**: **40/42 Schemas Pass; 2 Triodion files pending key prefix repair**.

---

## 2. Multi-Recension Hierarchy & Lookup Chain
1. **Primary Recension (Royal Doors)**: Standard modern Ukrainian Greek Catholic Church (UGCC) English vocabulary (`primary_db`).
2. **Backup/Fallback Recension (Stamford)**: Houses comprehensive corpus of variable propers (`backup_db`).
3. **Monastic Overlay (St. Sergius)**: Unabridged Tone 1 monastic propers overlay.
4. **Legacy Key Alias Support**: Automatic mapping from flat keys (e.g. `horologion.litany_great`) to standardized hierarchical keys (`horologion.vespers.great_litany`).

---

## 3. Immediate Action Items
* **Triodion Asset Repair**: In `parsers/parse_triodia.py`, prepend `triodion.` to Sunday/service keys in `text_lenten_triodion.json` and `text_floral_triodion.json` so that 42/42 files pass `tests/validate_schemas.py`.

---

## 4. Verification Checklist
- Run schema validation:
  ```powershell
  .venv\Scripts\python tests/validate_schemas.py
  ```
- Run recension fallback test:
  ```powershell
  .venv\Scripts\python -m pytest tests/test_recensions.py
  ```
