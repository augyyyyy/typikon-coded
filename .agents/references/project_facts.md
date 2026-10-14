# Project Facts & Base Metrics

> **Live Situational State**: See [`.agents/STATE.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/STATE.md) and [`reports/audits/FORENSIC_AUDIT_REPORT.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/reports/audits/FORENSIC_AUDIT_REPORT.md) (October 13, 2026 Software Forensics Audit Baseline).

## 1. Verified Metrics (As of 2026-10-13)
* **Total Engine Modules**: 22 modules in `engine/` composition (21,377 lines of core logic).
* **Total Digest Modules**: 13 modules in `digest/` composition (8,076 lines of formatting logic).
* **Test Suite Status**: 1,425 non-UI tests across 53 test files (100% pass rate). Run via `.venv\Scripts\python.exe -m pytest --ignore=tests/test_ui_readability.py`.
* **JSON Schema Validation**: 14 files passing against schemas in `schemas/` (`Data/schemas/schemas/`).
* **Resolvers & Formatters Status**: 231 `resolve_` methods defined in `engine/`, 88 unique resolvers referenced by the 16 `01*_struct_*.json` files in `json_db/`, 155 specific `_format_resolve_` methods in `digest/` (0 `TODO`/`FIXME` markers across `engine/` and `digest/`).
* **Annual Almanac Cache**: 12 precomputed monthly JSON files (`json_db/almanac/2026_01.json`–`2026_12.json`, 365 days, 100% live-engine parity verified by `tests/test_annual_almanac_consistency.py`).

## 2. Hub-and-Spoke Ecosystem & 6-Tier Layout
* **The Hub (Typikon Coded)**: Core Logic Engine (Wing 1), Service Structures (Wing 2), and UI/API (Wing 5 — `Data/prototypes/cantor_dashboard/server.py`). Core logic and structure are 100% complete and airtight.
* **Root NTFS Junctions**: `json_db -> Data\databases\json_db`, `schemas -> Data\schemas\schemas`, `Rubrics -> Data\rubrics\Rubrics`.
* **The Spokes (Translation, Revitalize, Kyivan Musicology, Liturgical Aggregator)**: Ingest raw text, historical typika, and musicological catalogs into `Data/Inbox/` (gitignored staging folder) for deterministic ingestion into `Data/` and `json_db/`.

## 3. Primary-Backup Recension & Musicology Architecture
The engine operates on a strict **Primary-Backup** lookup model (`engine/text_db.py`):
* **Primary Recension (Royal Doors)**: Standard UGCC English propers and terminology. Loaded from `Data/Service Books/Recensions/Royal Doors/JSON/assets/` (currently 12 empty `{}` JSON shells — 0 keys populated).
* **Backup/Fallback Recension (Stamford)**: Used to resolve any missing keys in the primary database. Loaded from `Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/` (14 files, **2,854 populated text keys**).
* **Custom Overlays & Scholarly Apparatus**: `json_db/st_sergius/octoechos_tone_1_refined.json` (**187 keys**), `json_db/synodal_footnotes.json` (**786 keys**), `Data/Canonical_English_Lexicon.json` (**2,529 entries**), `Data/Master_Incipits.json` (**1,363 entries**), and 15 `Data/Codex_*_Structured_DB.json` files.

Agents must NEVER fabricate missing liturgical text; they must let the engine resolve missing keys through fallback to Stamford, General Menaion, or return a clean missing placeholder stub.

## 4. Codebase Anomalies Registry (Do Not Alter Prematurely)
* **Historical Scratch Scripts (`scratch/legacy_root/`)**: `scratch_append_matins.py` and `scratch_insert_phase2.py` are historical injection scripts relocated during the 6-Tier Spoke reorganization. Do not delete them as they serve as migration references.
* **Empty Folder**: `assets/menaion/` is intentionally empty; Menaion data lives in `json_db/stamford/text_menaion.json`.
* **Stale Backup**: `json_db/stamford/text_horologion.json.bak` exists alongside the active file.
* **Duplicate Handler**: `Data/prototypes/cantor_dashboard/server.py` contains duplicate `api_resolve` method definitions (lines 171 and 290). The first instance is dead code shadowed by the second.
* **Validation Gaps**: `schemas/README.md` documents unresolved validation failures in `text_pentecostarion.json` and `text_theotokia.json`.
* **Pytest Launcher Shebang**: `.venv\Scripts\pytest.exe` fails silently with exit code `1` due to a stale path prior to the `Projects\` parent relocation; always invoke `.venv\Scripts\python.exe -m pytest`.

## 5. In-Place References Catalog
The following folders contain read-only design documents and grounding matrices that are referenced by specialized skills:
* **Session State & Forensic Audit**: [`.agents/STATE.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/STATE.md) and [`reports/audits/FORENSIC_AUDIT_REPORT.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/reports/audits/FORENSIC_AUDIT_REPORT.md).
* **Brain Harvest Registry**: [`reports/ARTIFACT_REGISTRY.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/reports/ARTIFACT_REGISTRY.md) — Index of 1,353 harvested artifacts from 226 historical conversations (`docs/historical_artifacts/`, `docs/user_evidence/`, `scripts/archived_pipelines/`).
* **Architecture Docs**: [architecture/](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/brain/architecture) — `digest_authoring_rules.md`, `complete_book_schemas.md`, etc.
* **Audits Archive**: [audits/](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/brain/audits) — Matins coverage reports, recension gap audits.
* **Canonical Maximalist Standard**: [canonical_maximalist_digest_standard.md](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/references/canonical_maximalist_digest_standard.md) — Mandatory 7-card maximalist audit checkpoints.
* **Grounding Encyclopedia**: [docs/encyclopedia/](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/docs/encyclopedia) — 36 files including the 3.2MB [master_citation_matrix.md](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/docs/encyclopedia/master_citation_matrix.md).

