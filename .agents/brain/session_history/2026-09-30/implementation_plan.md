# Implementation Plan: Ingest & Normalize Kyivan Musicology Databases & Lexicon

This plan executes the deterministic ingestion, normalization, and verification of the remaining Kyivan Musicology Spoke assets in `Data/Inbox/` into `Data/`.

## 1. Targets & Scope

1. **`Data/Master_Incipits.json`**:
   - Expand from 1,092 entries to **1,363 entries** using `Data/Inbox/Master_Incipits.json`.
   - Normalize vocabulary:
     - `Praise the Lord from the heavens (Vitebsk Koinonikon)` $\rightarrow$ `Praise the Lord from the heavens (Vitebsk Communion Hymn)`
     - `The watery springs of the deep were revealed (Bulgarian Palm Sunday Irmos)` $\rightarrow$ `The watery springs of the deep were revealed (Bulgarian Palm Sunday Heirmos)`
   - Ensure clean UTF-8 encoding without BOM.

2. **`Data/Canonical_English_Lexicon.json`**:
   - Expand from 1,335 entries to **2,529 entries** using `Data/Inbox/Canonical_English_Lexicon.json`.
   - Normalize vocabulary:
     - `Praise the Lord from the heavens (Vitebsk Koinonikon)` $\rightarrow$ `Praise the Lord from the heavens (Vitebsk Communion Hymn)`
     - `The watery springs of the deep were revealed (Bulgarian Palm Sunday Irmos)` $\rightarrow$ `The watery springs of the deep were revealed (Bulgarian Palm Sunday Heirmos)`
   - Ensure clean UTF-8 encoding without BOM.

3. **Parsed Codex Databases (`Data/yas_no_*_parsed.json`)**:
   - Ingest all 15 codex parsed JSON databases into `Data/`:
     - `yas_no_21_parsed.json` (upgrade from 727 items to 1,064 items; strip the invalid UTF-8 BOM).
     - `yas_no_14_parsed.json` (273 items)
     - `yas_no_1629_parsed.json` (572 items, Kyiv Caves Lavra printed Irmologion)
     - `yas_no_22_parsed.json` (317 items)
     - `yas_no_2_parsed.json` (513 items)
     - `yas_no_31_parsed.json` (826 items)
     - `yas_no_38_parsed.json` (732 items)
     - `yas_no_39_parsed.json` (541 items)
     - `yas_no_40_parsed.json` (548 items)
     - `yas_no_44_parsed.json` (1,349 items)
     - `yas_no_45_parsed.json` (109 items)
     - `yas_no_47_parsed.json` (847 items)
     - `yas_no_53_parsed.json` (569 items)
     - `yas_no_5_parsed.json` (1,160 items)
     - `yas_no_76_parsed.json` (33 items)
     - `yas_no_14_chant_index.json` (273 items)
   - Ensure all files parse with standard Python `encoding="utf-8"`.

4. **Automated Verification Gate**:
   - Create `tests/test_musicology_ingestion.py` testing counts, schemas, and terminology compliance.
   - Run `pytest tests/test_session_compliance.py`.
   - Run `pytest --ignore=tests/test_ui_readability.py`.

## 2. Verification Protocol

- Test count assertions:
  - `Master_Incipits.json`: exactly 1,363 keys, 0 `koinonikon` in English strings, 0 `Irmos` in English strings.
  - `Canonical_English_Lexicon.json`: exactly 2,529 keys, 0 `koinonikon`, 0 `Irmos`.
  - All 15 `yas_no_*_parsed.json` files load with `utf-8` without error.
