# Project Facts & Base Metrics

> **Live Situational State**: See [`.agents/STATE.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/STATE.md) and [`reports/audits/FORENSIC_AUDIT_REPORT.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/reports/audits/FORENSIC_AUDIT_REPORT.md) (Updated 2026-10-28 after Spoke Payload Ingestion, `Royal Doors` Hydration, Schema Validation Closure, & Seasonal Chant Repertoire Wiring).

## 1. Verified Metrics (As of 2026-10-28)
* **Total Engine Modules**: 22 modules in `engine/` composition (21,377 lines of core logic).
* **Total Digest Modules**: 13 modules in `digest/` composition (8,076 lines of formatting logic).
* **Test Suite Status**: 1,452 non-UI tests across 56 test files (100% pass rate; 1,452 passed, 3 skipped). Run via `.venv\Scripts\python.exe -m pytest --ignore=tests/test_ui_readability.py`.
* **Computational Limit & Forensic Matrix Status**:
  - **2026 365-Day Consecutive Multi-Audit**: 365/365 days passing (`3,285` services, `0` errors).
  - **35-Paschal-Key Common + Leap Universe**: All 35 Common + 35 Leap Paschal keys across Gregorian and Julian Paschalions (`140` year sweeps = `51,170` days) passing with `0` violations.
  - **Temple Patronal Collision Matrix**: All 34 Dolnytsky Part V cases $\times$ 4 Patronal Archetypes (`136` scenarios) passing with `0` violations.
  - **Forensic Cohort Matrix**: All 26 Canonical Liturgical Formats (`01`–`26`) and all 18 Movable Sub-Cohorts verified (`0` remaining).
* **JSON Schema Validation**: 51 active database files passing with 0 errors against 4 strict schemas in `schemas/` (`text_asset.schema.json`, `triodion_nested_asset.schema.json`, `service_structure.schema.json`, `seasonal_repertoire.schema.json`), enforced in `pytest` via `tests/validate_schemas.py::test_all_json_schemas_valid`.
* **Resolvers & Formatters Status**: 231 `resolve_` methods defined in `engine/`, 88 unique resolvers referenced by the 16 `01*_struct_*.json` files in `json_db/`, 155 specific `_format_resolve_` methods in `digest/` (0 `TODO`/`FIXME` markers across `engine/` and `digest/`).
* **Zero-Cache Live-Engine Mode**: `json_db/almanac/` operates in Zero-Cache Live-Engine mode (any date `1583–9998` resolved live at ~70 days/sec; on-demand cache export available via `scripts/generate_annual_almanac.py`).

## 2. Hub-and-Spoke Ecosystem & 6-Tier Layout
* **The Hub (Typikon Coded)**: Core Logic Engine (Wing 1), Service Structures (Wing 2), and UI/API (Wing 5 — `Data/prototypes/cantor_dashboard/server.py`). Core logic and structure are 100% complete and airtight.
* **Root NTFS Junctions**: `json_db -> Data\databases\json_db`, `schemas -> Data\schemas\schemas`, `Rubrics -> Data\rubrics\Rubrics`.
* **The Spokes (Translation, Revitalize, Kyivan Musicology, Liturgical Aggregator)**: Ingest raw text, historical typika, and musicological catalogs into `Data/Inbox/` (gitignored staging folder) for deterministic ingestion into `Data/` and `json_db/`.

## 3. Primary-Backup Recension & Musicology Architecture
The engine operates on a strict **Primary-Backup** lookup model (`engine/text_db.py`):
* **Primary Recension (Royal Doors)**: Standard UGCC English propers and terminology. Loaded from `Data/Service Books/Recensions/Royal Doors/JSON/assets/` (**14 hydrated JSON files, 2,848 populated content keys / 2,854 entries**, standardized to UGCC Royal Doors vocabulary and hieratic capitalization with 228 fixed-date Royal Doors variant blocks linked).
* **Backup/Fallback Recension (Stamford)**: Used to resolve any missing keys in the primary database and for side-by-side comparison in the Cantor Dashboard. Loaded from `Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/` (14 files, **2,848 populated content keys / 2,854 entries**).
* **Ingested Translation Monuments**: 8 Typikon/Synod monuments in `Data/Service Books/Typikon/Monuments/` and 8 Liturgical Service Book monuments in `Data/Service Books/Monuments/`.
* **Custom Overlays & Scholarly Apparatus**: `json_db/st_sergius/octoechos_tone_1_refined.json` (**187 keys**), `json_db/synodal_footnotes.json` (**786 keys**), `Data/Canonical_English_Lexicon.json` (**2,529 entries**), `Data/Master_Incipits.json` (**1,363 homoglyph-normalized entries**), `Data/databases/pan_catalogue_fortified_corpus.json` (**616 monuments**), `Data/databases/yasinovsky_catalogue_fortified_corpus.json` (**572 codices**), `Data/databases/repertoires/WO_01..WO_05_*.json` (**140 seasonal chants across 5 cycles and 30 phases**, exposed via `GET /api/repertoires` and `seasonal_repertoire` in `GET /api/resolve`), 17 `Data/yas_no_*_parsed.json` files, and 7 `Data/irm_*_parsed.json` files.

Agents must NEVER fabricate missing liturgical text; they must let the engine resolve missing keys through fallback to Stamford, General Menaion, or return a clean missing placeholder stub.

## 4. Codebase Anomalies Registry (Do Not Alter Prematurely)
* **Historical Scratch Scripts (`scratch/legacy_root/`)**: `scratch_append_matins.py` and `scratch_insert_phase2.py` are historical injection scripts relocated during the 6-Tier Spoke reorganization. Do not delete them as they serve as migration references.
* **Empty Folder**: `assets/menaion/` is intentionally empty; Menaion data lives in `json_db/stamford/text_menaion.json`.
* **Stale Backup**: `json_db/stamford/text_horologion.json.bak` exists alongside the active file.
* **Pytest Launcher Shebang**: `.venv\Scripts\pytest.exe` fails silently with exit code `1` due to a stale path prior to the `Projects\` parent relocation; always invoke `.venv\Scripts\python.exe -m pytest`.
* **Resolved Historical Anomalies (2026-10-28)**:
  - **JSON Schema Validation Gaps (Resolved)**: `text_pentecostarion.json`, `text_theotokia.json`, `text_pentecostarion_pascha.json`, and nested Triodion files (`text_lenten_triodion.json`, `text_floral_triodion.json`) now validate 100% (`51/51` files, `0` errors) against `schemas/`.
  - **Cantor Dashboard Server Cleanup & `WO_01..WO_05` Wiring (Resolved)**: `Data/prototypes/cantor_dashboard/server.py` has a single canonical `api_resolve` definition, reuses a single `RuthenianEngine` instance in `api_roadmap`, exposes `GET /api/repertoires` and deterministic `seasonal_repertoire` resolution (`WO-01`–`WO-05` + Tone Dogmatikon), and all companion linter/audit scripts point to `Data/prototypes/cantor_dashboard/`.

## 5. In-Place References Catalog
The following folders contain read-only design documents and grounding matrices that are referenced by specialized skills:
* **Session State & Forensic Audit**: [`.agents/STATE.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/STATE.md) and [`reports/audits/FORENSIC_AUDIT_REPORT.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/reports/audits/FORENSIC_AUDIT_REPORT.md).
* **Brain Harvest Registry**: [`reports/ARTIFACT_REGISTRY.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/reports/ARTIFACT_REGISTRY.md) — Index of 1,353 harvested artifacts from 226 historical conversations (`docs/historical_artifacts/`, `docs/user_evidence/`, `scripts/archived_pipelines/`).
* **Architecture Docs**: [architecture/](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/brain/architecture) — `digest_authoring_rules.md`, `complete_book_schemas.md`, etc.
* **Audits Archive**: [audits/](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/brain/audits) — Matins coverage reports, recension gap audits.
* **Canonical Maximalist Standard**: [canonical_maximalist_digest_standard.md](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/references/canonical_maximalist_digest_standard.md) — Mandatory 7-card maximalist audit checkpoints.
* **Grounding Encyclopedia**: [docs/encyclopedia/](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/docs/encyclopedia) — 36 files including the 3.2MB [master_citation_matrix.md](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/docs/encyclopedia/master_citation_matrix.md).
