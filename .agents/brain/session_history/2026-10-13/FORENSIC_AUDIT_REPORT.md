# Master Forensic Audit & State Reconstruction Report (`Typikon Coded`)

**Audit Date**: October 13, 2026  
**Baseline Git Commit (`HEAD`)**: `e8b43df` (*feat(typikon): Dolnytsky master markdown compiler, synodal footnotes, temple logic & regional chant rules*)  
**Runtime Environment**: Windows / Python `3.14.2` / `pytest-9.0.2`  
**Canonical Location**: [`reports/audits/FORENSIC_AUDIT_REPORT.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/reports/audits/FORENSIC_AUDIT_REPORT.md)

---

## 1. Antigravity "Brain" & Session Forensics (Reconstruction of Recent Workstreams)

Cross-referencing `.agents/brain/session_history/`, `git log -n 15 --oneline`, and [`_dedup_meta/reorg_manifest.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/_dedup_meta/reorg_manifest.json) establishes the exact sequence of workstreams leading up to the current state:

| Date | Session / Commit | Status Prior to Audit | Verified Scope & Findings |
| :--- | :--- | :--- | :--- |
| **2026-09-28** | [`2026-09-28/walkthrough.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/brain/session_history/2026-09-28/walkthrough.md) (`e8b43df`) | **Committed (`HEAD`)** | Compiled `Dolnytsky_Typikon_Master.md` (14,413 lines) via [`scripts/compile_master_typikon_md.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/compile_master_typikon_md.py); decontaminated Footnotes 775 & 784 in [`json_db/synodal_footnotes.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/synodal_footnotes.json) (786 entries); migrated line-number citations to canonical section headings across `02d_logic_temple.json` and `docs/DOLNYTSKY_IMPLEMENTATION.md`. |
| **2026-09-30** | [`2026-09-30/walkthrough.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/brain/session_history/2026-09-30/walkthrough.md) | **Uncommitted in Working Tree** | 1. Harvested 5,461 historical brain items (190.56 MB across 200 past sessions) via [`scripts/harvest_historical_brain_artifacts.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/harvest_historical_brain_artifacts.py) into `ARTIFACT_REGISTRY.md`, `docs/historical_artifacts/`, `docs/user_evidence/`, `scripts/archived_pipelines/`, and `Data/historical_data_caches/`.<br>2. Ingested 15 Kyivan Musicology codex databases (`Data/yas_no_*_parsed.json`), expanded [`Data/Canonical_English_Lexicon.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/Canonical_English_Lexicon.json) to **2,529 entries**, expanded [`Data/Master_Incipits.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/Master_Incipits.json) to **1,363 entries**, and added [`tests/test_musicology_ingestion.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_musicology_ingestion.py) (17/17 tests passing). |
| **2026-10-05** | [`2026-10-05/walkthrough.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/brain/session_history/2026-10-05/walkthrough.md) | **Uncommitted in Working Tree** | Executed [`scripts/execute_spoke_reorg.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/execute_spoke_reorg.py) to align `Typikon Coded` with the **6-Tier Spoke Archetype** ([`ECOSYSTEM_ARCHITECTURAL_STANDARD.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/ECOSYSTEM_ARCHITECTURAL_STANDARD.md)). Moved 50+ loose root files into `reports/`, `Data/prototypes/`, `scripts/legacy_runners/`, and `scripts/parsers/`, and established Windows NTFS junctions (`json_db`, `schemas`, `Rubrics`). |
| **2026-10-05 to 2026-10-12** | Cross-Spoke Deliveries into [`Data/Inbox/`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/Inbox) | **Staged in `Data/Inbox/` (Pending Hub Ingestion)** | The **Translation** and **Kyivan Musicology** Spokes deposited Monuments 1–6 (`1891_Lviv_Provincial_Synod`, `1899_Dolnytsky_Typikon`, `1901_Mikita_Typikon`, `1852_Doskovsky_Typikon`, `1888_Violakis_Typikon`, `1910_Skaballanovich_Typikon`), Pillar 1–3 concordances/catalogues (`lexicon_bridge_concordance.json`, `pan_catalogue_fortified_corpus.json` [590 monuments], `yasinovsky_catalogue_fortified_corpus.json` [526 codices]), and 5 seasonal deduplicated chant repertoires (`WO_01`–`WO_05`). |

### Collateral Anomalies Repaired During Phase 2 Stabilization
1. **The `Data/` `.gitignore` Trap (Fixed)**: Moving `cantor_dashboard` into `data/prototypes/cantor_dashboard` placed it inside the blanket-ignored `Data/` directory on Windows NTFS, causing Git to mark `cantor_dashboard/*` as deleted (`D`) while ignoring its new location and hiding the 18 Sept 30 Kyivan Musicology JSONs. Modernized [`.gitignore`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.gitignore) to selectively ignore only raw/external subdirectories (`Data/Inbox/`, `Data/Service Books/`, `Data/historical_data_caches/`, `Data/archive/`, `Data/*.pdf`, `Data/*.txt`) and junction targets (`Data/databases/json_db/`, `Data/schemas/schemas/`, `Data/rubrics/Rubrics/`).
2. **False Directory Collisions (Fixed)**: Resolved `scripts/parsers_collision_20261005115528/` $\rightarrow$ `scripts/parsers/` (18 files) and `reports/final_results_collision_20261005115528/` $\rightarrow$ `reports/final_results/` (5 files), and fixed the pre-creation bug in [`scripts/execute_spoke_reorg.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/execute_spoke_reorg.py).
3. **Duplicate Root Shims (Fixed)**: Restored original [`ruthenian_engine.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/ruthenian_engine.py) and [`typikon_digest_generator.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/typikon_digest_generator.py) from `scripts/legacy_runners/`, eliminating unnecessary root diffs and duplicate shims.
4. **Root Read-Only Law & 177 MB Brain Harvest (Fixed)**: Moved `ARTIFACT_REGISTRY.md` (1.43 MB) from root to [`reports/ARTIFACT_REGISTRY.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/reports/ARTIFACT_REGISTRY.md) with updated relative links, and gitignored the 177 MB bulk archives (`docs/historical_artifacts/`, `docs/user_evidence/`, `scripts/archived_pipelines/`).
5. **Broken Git Refs & Deployment Path (Fixed)**: Purged OneDrive `desktop.ini` files from `.git/refs/**` and updated [`render.yaml`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/render.yaml) to `python Data/prototypes/cantor_dashboard/server.py`.

---

## 2. Entry Points, Monolith-to-Module Architecture & Deployment Verification

| File / Package | Role | Line Count / Size | Live Status |
| :--- | :--- | :--- | :--- |
| [`engine/`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/__init__.py) | Primary Modular Liturgical Engine (22 files, mixin composition) | **21,377 lines** (`231` `resolve_` methods) | 🟢 **Active Core** |
| [`digest/`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/digest/__init__.py) | Primary Modular Digest & Booklet Formatter (13 files) | **8,076 lines** (`155` `_format_resolve_` methods) | 🟢 **Active Core** |
| [`ruthenian_engine.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/ruthenian_engine.py) | Root backward-compatibility shim (`from engine import RuthenianEngine`) | 15 lines (459 bytes) | 🟢 **Clean Shim** |
| [`typikon_digest_generator.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/typikon_digest_generator.py) | Root backward-compatibility shim (`from digest import TypikonDigestGenerator`) | 5 lines (109 bytes) | 🟢 **Clean Shim** |
| [`Data/prototypes/cantor_dashboard/server.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/prototypes/cantor_dashboard/server.py) | Cantor Dashboard HTTP/API Server (dynamically walks up 5 levels to find `engine/` & `.agents/`) | 664 lines (27.8 KB) | 🟢 **Verified (6/6 Endpoint Tests Pass)** |
| [`scripts/legacy_runners/generate_typikon_service.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/legacy_runners/generate_typikon_service.py) | Legacy CLI runner for single-date service/digest generation | 134 lines (5.5 KB) | 🟡 **Relocated Legacy CLI** (requires `$env:PYTHONPATH="."`) |
| [`scripts/legacy_runners/generate_cantor_prototype.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/legacy_runners/generate_cantor_prototype.py) | Legacy prototype renderer (`CantorRenderer` imported by `tests/test_renderer_st_sergius.py`) | 530 lines (24.3 KB) | 🟡 **Relocated Legacy Module** |

> [!NOTE]
> **Virtual Environment Note**: Direct execution of `.venv\Scripts\pytest.exe` fails silently with exit code `1` due to a stale Windows `.exe` wrapper shebang. Always invoke pytest via `.venv\Scripts\python.exe -m pytest`, which executes cleanly on Python `3.14.2`.

---

## 3. Core Engine, Almanac Fast-Path & Recension Matrix

### 3.1 Dolnytsky Coverage & Almanac Sync
* **General Paradigms (Part II)**: All **20 Dolnytsky Paradigms** (`CASE_01`–`CASE_20`) + **7 Moveable Cycle General Paradigms** (`21`–`27`) are mapped in [`json_db/02a_logic_general.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02a_logic_general.json) and [`json_db/lviv_format_map.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/lviv_format_map.json).
* **Fixed Menaion Specific Rubrics (Part III)**: All **26 dates** implemented across `json_db/02b_*.json`.
* **Triodion & Pentecostarion (Part IV)**: Full Paschalion offset coverage across all **35 Paschalion Keys** (Gregorian & Julian, Common & Leap years).
* **Temple Patronal Collisions (Part V)**: All **34 collision cases $\times$ 4 temple archetypes = 136 scenarios** implemented in [`json_db/02d_logic_temple.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/02d_logic_temple.json).
* **Almanac Fast-Path Parity (`json_db/almanac/`)**: Verified 100% parity between runtime `engine/` computation and precomputed almanacs across **2025, 2026, and 2027** (`tests/test_annual_almanac_consistency.py`: **3/3 PASSED**).

### 3.2 Recension & Text Database Hydration Matrix
The Hub uses a decoupled **Primary-Backup** lookup architecture (`engine/core.py` & `engine/text_db.py`):

| Database / Layer | Location | Files | Populated Keys | Status & Role |
| :--- | :--- | :---: | :---: | :--- |
| **Royal Doors (Primary)** | `Data/Service Books/Recensions/Royal Doors/JSON/assets/` | 12 | **0** | 🟡 **Empty JSON Shells (`{}`)**: Awaits Spoke population; engine automatically falls back to Stamford Backup. |
| **Stamford Divine Office (Backup)** | `Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/` | 14 | **2,854** | 🟢 **Active Primary Hydration Corpus**: Menaion (`1,322`), Octoechos (`531`), Pentecostarion (`297`), General Menaion (`176`), Horologion (`145`), Triodion (`138`), Eothinon (`92`), Theotokia (`71`), Floral Triodion (`24`), Horologion Supp (`20`), Weekdays (`13`), Lenten Triodion (`12`), Liturgikon (`8`), Praises (`5`). |
| **St. Sergius (Monastic Overlay)** | [`json_db/st_sergius/octoechos_tone_1_refined.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/st_sergius/octoechos_tone_1_refined.json) | 1 | **187** | 🟡 **Tone 1 Complete**: Context-dependent override for Tone 1; Tones 2–8 not populated. |
| **Synodal Footnotes Apparatus** | [`json_db/synodal_footnotes.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/json_db/synodal_footnotes.json) | 1 | **786** | 🟢 **Verified Complete** (1.11 MB, decontaminated Sept 28). |
| **Propers Drift & Pure Typikon** | `json_db/propers_comparisons/` | 3 | **Multi-Recension** | 🟢 **Active Comparison Layer** (`festal_propers_pure_typikon_database.json`, `festal_propers_database.json`, `royaldoors_daily_drift_mapping.json`). |
| **Kyivan Musicology Lexicon & Incipits** | [`Data/Canonical_English_Lexicon.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/Canonical_English_Lexicon.json) & [`Data/Master_Incipits.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/Data/Master_Incipits.json) | 18 | **2,529** lexicon / **1,363** incipits / **15** codices | 🟢 **Verified Ingested** (`tests/test_musicology_ingestion.py`: **17/17 PASSED**). |

---

## 4. Subsystem Status Matrix

| Subsystem | Status | Completion | Forensic Notes |
| :--- | :---: | :---: | :--- |
| **1. Core Liturgical Engine (`engine/` & `json_db/02*_logic_*.json`)** | 🟢 **Verified Complete** | **100%** | 231 `resolve_` methods across 22 modules; all 88 JSON structural hooks wired; 0 `TODO`/`FIXME` markers. |
| **2. Service Structures (`json_db/01*_struct_*.json`)** | 🟢 **Verified Complete** | **100%** | 16 structural JSON files covering Vespers (8 variants), Compline, Midnight Office, Matins, Hours (1, 3, 6, 9, Royal), Liturgy (Chrysostom, Basil, Presanctified), and Vigil. |
| **3. Digest & Booklet Generator (`digest/`)** | 🟢 **Verified Complete** | **100%** | 155 `_format_resolve_` methods across 13 modules; 0 fallbacks to `_format_generic`; UGCC Royal Doors terminology filter enforced. |
| **4. Cantor Dashboard & API (`Data/prototypes/cantor_dashboard/`)** | 🟢 **Verified Complete** | **95%** | All 6 HTTP API endpoints pass; IDE split-drawer layout, badges, and tooltipped citations operational. Duplicate `api_resolve` dead-code definition remains in `server.py` (non-breaking). |
| **5. Text Recension Hydration (`Data/Service Books/Recensions/`)** | 🟡 **Partially Implemented** | **Stamford: ~85% / Royal Doors: 0%** | Stamford backup database houses 2,854 keys; Royal Doors JSON files are currently empty `{}` shells. |
| **6. Legacy Parsers (`scripts/parsers/`)** | 🧟 **Archived / Superseded** | **Historical** | 18 one-off migration/extraction scripts relocated to `scripts/parsers/`. Per `GLOBAL_SYSTEM_RULES.md`, third-party OCR/LLM APIs are permanently banned in favor of Native Gemini Vision in the Translation/Musicology Spokes. |

---

## 5. Diagnostic Audit Reports Triage (`reports/audits/`)

Every historical diagnostic JSON report relocated from root to `reports/audits/` was inspected and cross-checked against the current engine:

| Audit Artifact | Scope Audited | Logged Violations / Incidents | Current Code Status |
| :--- | :--- | :---: | :--- |
| [`scan_2026_systemic_bugs_report.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/reports/audits/scan_2026_systemic_bugs_report.json) | 365 days of 2026 across 8 bug classes | **0 incidents** (`unique_days_affected: 0`) | 🟢 **100% Resolved & Clean** |
| [`audit_35_keys_results.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/reports/audits/audit_35_keys_results.json) | 136 sweeps across all 35 Paschalion keys (49,704 days) | **0 violations** | 🟢 **100% Resolved & Clean** |
| [`decadal_audit_results.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/reports/audits/decadal_audit_results.json) | 42 annual sweeps | **0 violations** | 🟢 **100% Resolved & Clean** |
| [`golden_window_50yr_results.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/reports/audits/golden_window_50yr_results.json) | 100 annual sweeps (1950–2050 Golden Window) | **0 violations** | 🟢 **100% Resolved & Clean** |
| [`temple_collision_audit_results.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/reports/audits/temple_collision_audit_results.json) | 34 Dolnytsky Part V cases $\times$ 4 temple archetypes (136 scenarios) | **0 violations** | 🟢 **100% Resolved & Clean** |

---

## 6. `Data/Inbox/` Complete Spoke Payload & SHA-256 Duplicate Ledger

`Data/Inbox/` currently contains **542 top-level entries** (**1.58 GB total**). Per your instruction, zero files in `Data/Inbox/` were modified during this pass; below is the exact forensic ledger for Phase 2 Inbox Cleanup & Ingestion:

### 6.1 SHA-256 PDF Duplicate & Drive-E Routing Ledger (`1,413.35 MB` / `461 PDFs`)
Under [`ECOSYSTEM_ARCHITECTURAL_STANDARD.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/ECOSYSTEM_ARCHITECTURAL_STANDARD.md) Section 1 & 2, PDFs do not belong in Drive C `Data/Inbox/`.

| `Data/Inbox/` Path | PDF Count | Size (MB) | SHA-256 Forensic Finding & Recommended Action |
| :--- | :---: | :---: | :--- |
| `Data/Inbox/*.pdf` (Top-level loose PDFs) | **202** | **~598.0 MB** | **100% Exact SHA-256 Byte-for-Byte Duplicates** of files inside `Data/Inbox/PDFs/` (`202/202` identical hashes, `0` diffs). Safe to deduplicate immediately. |
| `Data/Inbox/PDFs/*.pdf` | **204** | **628.59 MB** | Contains all 202 top-level PDFs + 2 additional PDFs. Route/verify against Drive E (`E:\Google Drive\Liturgical Library\`) and remove from Drive C `Data/Inbox/`. |
| `Data/Inbox/Codex_No_*_Archive_v1_Baseline/*.pdf` (5 folders) | **55** (11 $\times$ 5) | **186.73 MB** | Legacy v1 baseline archives for Codices № 2, 14, 21, 22, 30 (superseded by sealed v3.1 editions). Route to Drive E or `_dedup_meta` vault. |

### 6.2 Staged Translation Spoke Monuments (Monuments 1–6)

| Monument | Canonical Folder in `Data/Inbox/` | Files / Size | Duplicate / Draft Folder in `Data/Inbox/` | Ingestion Status |
| :--- | :--- | :---: | :--- | :--- |
| **Monument 1: 1891 Lviv Provincial Synod** | `1891_Lviv_Provincial_Synod/` (Oct 9) | 9 files (1.41 MB) | `1891_Lviv_Synod/` (Oct 7, 78 files, 6.47 MB — contains raw cohorts & `.txt` duplicates) | 🔴 **Ready to Ingest** into `Data/Service Books/` (archive `1891_Lviv_Synod/` cohorts). |
| **Monument 2: 1899 Dolnytsky Typikon** | `1899_Dolnytsky_Typikon/` (Oct 7) | 79 files (6.94 MB) | Includes `1899_dolnytsky_typikon_complete.md`, Parts 0–6, footnotes, and 30 cohorts | 🔴 **Ready to Ingest** into `Data/Service Books/Typikon/`. |
| **Monument 3: 1901 Mikita Typikon** | `1901_Mikita_Typikon/` (Oct 7) | 77 files (5.08 MB) | Includes `1901_mikita_typikon_complete.md`, Parts 0–2, footnotes, and 32 cohorts | 🔴 **Ready to Ingest** into `Data/Service Books/Typikon/`. |
| **Monument 4: 1852 Doskovsky Typikon** | `1852_Doskovsky_Typikon/` (Oct 7) | 51 files (4.09 MB) | Includes `1852_doskovsky_typikon_complete.md`, Parts 0–6, footnotes, and 15 cohorts | 🔴 **Ready to Ingest** into `Data/Service Books/Typikon/`. |
| **Monument 5: 1888 Violakis Typikon** | `1888_Violakis_Typikon/` (Oct 9) | 129 files (23.39 MB) | Includes `1888_violakis_part0..5.md`, footnotes (1.42 MB), and 121 cohorts | 🔴 **Ready to Ingest** into `Data/Service Books/Typikon/`. |
| **Monument 6: 1910 Skaballanovich Tolkovy Typikon** | `1910_Skaballanovich_Typikon/` (Oct 9) | 9 files (7.26 MB) | `1910_Skaballanovich_Tolkovy_Typikon/` (108 raw cohort files, 10.13 MB) | 🔴 **Ready to Ingest** into `Data/Service Books/Typikon/` (archive raw cohort folder). |

### 6.3 Staged Kyivan Musicology Payloads (Oct 12, 2026)

| Payload File in `Data/Inbox/` | Size | Records / Scope | Ingestion Action Needed |
| :--- | :---: | :---: | :--- |
| `Master_Incipits.json` (Oct 12, `sha256=2a905ad181bb`) | 3.55 MB | **1,363 incipits** (homoglyph-normalized update over Sept 30 `Data/Master_Incipits.json` `sha256=63d233b44c79`) | Promote to `Data/Master_Incipits.json` and verify with `test_musicology_ingestion.py`. |
| `lexicon_bridge_concordance.json` (Oct 12) | 41.3 KB | Pillar 1 Stop 3 Pan-Ecosystem Lexicon Bridge (35 Tier-1 genres + concordance metadata) | Promote to `Data/databases/` and wire into `test_musicology_ingestion.py`. |
| `pan_catalogue_fortified_corpus.json` (Oct 12) | 455.7 KB | **590 monuments** (526 Yasinovsky + 46 Supp + 11 Prints + 7 Dzherela) | Promote to `Data/databases/pan_catalogue_fortified_corpus.json`. |
| `yasinovsky_catalogue_fortified_corpus.json` (Oct 12) | 385.1 KB | **526 Yasinovsky codices** (100% Zero-Default certified) | Promote to `Data/databases/yasinovsky_catalogue_fortified_corpus.json`. |
| `WO_01` through `WO_05_*_Deduplicated_Repertoire.json` (Oct 12) | 159.5 KB (5 files) | **140 canonical seasonal chant items** across 5 liturgical cycles (32 + 24 + 22 + 32 + 30 items) | Promote to `Data/databases/repertoires/` and expose in Cantor Dashboard / Engine. |

---

## 7. Code Markers (`TODO` / `FIXME`) & Known Anomalies Inventory

* **`engine/` (22 files)**: `0` `TODO`/`FIXME`/`HACK` markers.
* **`digest/` (13 files)**: `0` `TODO`/`FIXME`/`HACK` markers.
* **`Data/prototypes/cantor_dashboard/`**: `0` `TODO`/`FIXME`/`HACK` markers. (Contains duplicate `def api_resolve` definition in `server.py` where the second definition overrides the first).
* **`tests/`**: `1` marker at [`tests/test_typikon_logic.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/tests/test_typikon_logic.py#L18) (`# TODO: Implement distribution logic`).
* **`schemas/README.md`**: Notes historical schema validation edge cases in `text_pentecostarion.json` and `text_theotokia.json`.

---

## 8. The "Restart Engine" Top 5 Action Plan

1. **Completed in This Session — 6-Tier Working-Tree Stabilization**:
   - Fixed `.gitignore` so `Data/prototypes/cantor_dashboard/`, `Data/databases/chronicle_index.json`, and the 18 Sept 30 Kyivan Musicology JSONs are tracked in Git while ignoring the 177 MB bulk brain harvest and `Data/Inbox/`.
   - Resolved `scripts/parsers/` and `reports/final_results/` false collision folders, restored clean root shims, moved `ARTIFACT_REGISTRY.md` to `reports/`, cleaned `.git/refs/**/desktop.ini`, and updated `render.yaml`.
2. **Next Immediate Step — Commit the Stabilized 6-Tier Baseline**:
   - Stage and commit the stabilized 6-Tier reorganization and Sept 30 Kyivan Musicology ingestion so `HEAD` matches the 6-Tier directory structure.
3. **Phase 2A — `Data/Inbox/` Deduplication & PDF Eviction (Reclaim ~1.41 GB on Drive C)**:
   - Remove the 202 SHA-256-identical top-level duplicate PDFs in `Data/Inbox/`, route `Data/Inbox/PDFs/` and `Codex_No_*_Archive_v1_Baseline/` PDFs off Drive C, and purge already-ingested Sept 30 `yas_no_*` files from `Data/Inbox/`.
4. **Phase 2B — Ingest Oct 7–12 Spoke Payloads from `Data/Inbox/`**:
   - Promote Monuments 1–6 (`1891_Lviv_Provincial_Synod`, `1899_Dolnytsky_Typikon`, `1901_Mikita_Typikon`, `1852_Doskovsky_Typikon`, `1888_Violakis_Typikon`, `1910_Skaballanovich_Typikon`) into `Data/Service Books/Typikon/` (archiving superseded raw cohort folders).
   - Promote `Master_Incipits.json` (Oct 12), `lexicon_bridge_concordance.json`, `pan_catalogue_fortified_corpus.json` (590 monuments), `yasinovsky_catalogue_fortified_corpus.json` (526 codices), and `WO_01..WO_05` seasonal repertoire JSONs into `Data/`, expanding `tests/test_musicology_ingestion.py`.
5. **Phase 3 — Royal Doors Recension Hydration & Repertoire Integration**:
   - Populate the 12 `Royal Doors` JSON shells in `Data/Service Books/Recensions/Royal Doors/JSON/assets/` and wire the `WO_01..WO_05` deduplicated seasonal chant repertoires into the Cantor Dashboard.
