# Walkthrough: Ingestion of Kyivan Musicology Databases & Lexicon

We have ingested, normalized, and verified all Musicology, Incipit, and Codex database assets from `Data/Inbox/` into `Data/`.

## Changes Summary

### 1. `Data/Canonical_English_Lexicon.json`
- Expanded from 1,335 to **2,529 entries** (+1,194 entries).
- Auto-remediated legacy terminology:
  - `Praise the Lord from the heavens (Vitebsk Koinonikon)` $\rightarrow$ `Praise the Lord from the heavens (Vitebsk Communion Hymn)`
  - `The watery springs of the deep were revealed (Bulgarian Palm Sunday Irmos)` $\rightarrow$ `The watery springs of the deep were revealed (Bulgarian Palm Sunday Heirmos)`
- Verified 100% clean UTF-8.

### 2. `Data/Master_Incipits.json`
- Expanded from 1,092 to **1,363 entries** (+271 entries) with cross-codex attestations (e.g. Yas. № 30).
- Standardized canonical English incipits for Vitebsk Communion Hymn and Bulgarian Palm Sunday Heirmos.
- Verified 100% clean UTF-8 without BOM.

### 3. Parsed Codex Databases (`Data/yas_no_*_parsed.json`)
- Ingested 15 codex databases (1629 Lavra + 14 Yasinovsky manuscripts):
  - `yas_no_14_parsed.json` (273 items) & `yas_no_14_chant_index.json` (273 items)
  - `yas_no_1629_parsed.json` (572 items, Kyiv Caves Lavra printed Irmologion)
  - `yas_no_21_parsed.json` (1,064 items, upgraded from 727 items; **stripped invalid UTF-8 BOM**)
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
  - `No. 76_evidence_manifest.json` (9 items)
- All files load cleanly with standard `encoding="utf-8"`.

### 4. Verification Test Suite (`tests/test_musicology_ingestion.py`)
- Automated 17 pytest checks covering cardinality, clean UTF-8 loading, and UGCC terminology compliance.
- 17/17 tests passing.
