# Project Facts & Base Metrics

## 1. Verified Metrics
* **Total Engine Modules**: 16 modules in `engine/` composition (11,795 lines of core logic).
* **Test Suite Status**: 337 tests, 100% pass rate. Run via `.venv\Scripts\pytest`.
* **JSON Schema Validation**: 14 files passing against schemas in `schemas/`.
* **Resolvers Status**: 207 `resolve_` methods defined, 83 unique resolvers referenced by JSON struct files, 150 specific formatters in `typikon_digest_generator.py` (0 fallbacks to `_format_generic`).

## 2. Hub-and-Spoke Ecosystem
* **The Hub (Typikon Coded)**: Core Logic Engine (Wing 1), Service Structures (Wing 2), and UI/API (Wing 5). Core logic and structure are 100% complete and airtight.
* **The Spokes (Translation, Revitalize, Kyivan Musicology)**: Ingest raw text and translate/format into JSON text assets, dropping them into `Data/Inbox/` to populate Wing 3.

## 3. Primary-Backup Recension Architecture (No Active In-Engine Hydration)
The engine does not have an active "hydration gap" baseline, as text assets are decoupled and stored as separate recension databases. The engine operates on a strict **Primary-Backup** lookup model:
* **Primary Recension (Royal Doors)**: Standard UGCC English propers and terminology. Loaded from `Data/Service Books/Recensions/Royal Doors/JSON/assets/`.
* **Backup/Fallback Recension (Stamford)**: Used to resolve any missing keys in the primary database. Loaded from `Data/Service Books/Recensions/Stamford Divine Office/JSON/assets/`.
* **Custom Overlays**: Custom recensions (like `st_sergius` for Tone 1) can be requested in the context and take highest priority in the lookup chain.

Agents must NEVER fabricate missing liturgical text; they must let the engine resolve missing keys through fallback to Stamford, General Menaion, or return a clean missing placeholder stub.

## 4. Codebase Anomalies Registry (Do Not Alter Prematurely)
* **Dead Code at Root**: `scratch_append_matins.py` and `scratch_insert_phase2.py` are historical injection scripts with hardcoded paths. Do not delete them as they serve as migration references.
* **Empty Folder**: `assets/menaion/` is intentionally empty; Menaion data lives in `json_db/stamford/text_menaion.json`.
* **Stale Backup**: `json_db/stamford/text_horologion.json.bak` exists alongside the active file.
* **Duplicate Handler**: `cantor_dashboard/server.py` contains duplicate `api_resolve` method definitions. The first instance is dead code.
* **Validation Gaps**: `schemas/README.md` documents unresolved validation failures in `text_pentecostarion.json` and `text_theotokia.json`.

## 5. In-Place References Catalog
The following folders contain read-only design documents and grounding matrices that are referenced by specialized skills:
* **Architecture Docs**: [architecture/](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agent/brain/architecture) — `digest_authoring_rules.md`, `complete_book_schemas.md`, etc.
* **Audits Archive**: [audits/](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agent/brain/audits) — Matins coverage reports, recension gap audits.
* **Grounding Encyclopedia**: [docs/encyclopedia/](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/docs/encyclopedia) — 36 files including the 3.2MB [master_citation_matrix.md](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/docs/encyclopedia/master_citation_matrix.md).
