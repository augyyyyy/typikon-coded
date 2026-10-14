# Typikon Coded — Persistent Antigravity State & Handover Ledger

**Last Updated**: 2026-10-13  
**Full Forensic Report**: [`reports/audits/FORENSIC_AUDIT_REPORT.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/reports/audits/FORENSIC_AUDIT_REPORT.md)

---

## 1. Live 6-Tier Repository Map

`Typikon Coded` conforms to the **6-Tier Spoke Archetype** (`ECOSYSTEM_ARCHITECTURAL_STANDARD.md`):

1. **Tier 1 (`.agents/`)**: Agent Governance ([`AGENTS.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/AGENTS.md)), Persistent State ([`STATE.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/STATE.md)), References ([`project_facts.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/references/project_facts.md), [`learnings.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/references/learnings.md), [`anti_patterns.md`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/.agents/references/anti_patterns.md)), Skills, and `.agents/brain/session_history/<date>/`.
2. **Tier 2 (`_dedup_meta/`)**: Reorganization ledger ([`reorg_manifest.json`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/_dedup_meta/reorg_manifest.json)) and atomic LIFO rollback script (`rollback_reorg.py`).
3. **Tier 3 (`Data/`)**:
   - `Data/databases/json_db/` (linked at root via NTFS junction `json_db`), `Data/databases/chronicle_index.json`
   - `Data/schemas/schemas/` (linked at root via NTFS junction `schemas`)
   - `Data/rubrics/Rubrics/` (linked at root via NTFS junction `Rubrics`)
   - `Data/prototypes/cantor_dashboard/` (Cantor Dashboard web app & HTTP server `server.py`)
   - `Data/Canonical_English_Lexicon.json` (2,529 entries), `Data/Master_Incipits.json` (1,363 entries), and 15 `Data/yas_no_*_parsed.json` codex databases
   - `Data/Service Books/` (Gitignored local recension & Typikon source texts)
   - `Data/Inbox/` (Gitignored Spoke intake staging folder)
4. **Tier 4 (`reports/`)**:
   - `reports/audits/` (`FORENSIC_AUDIT_REPORT.md`, `gui_features_roadmap.md`, `scan_2026_systemic_bugs_report.json`, `audit_35_keys_results.json`, `decadal_audit_results.json`, `golden_window_50yr_results.json`, `temple_collision_audit_results.json`)
   - `reports/ARTIFACT_REGISTRY.md` (Master registry of 5,461 harvested historical session items)
   - `reports/digests/`, `reports/traces/`, `reports/final_results/`
5. **Tier 5 (`engine/`, `digest/`, `scripts/`, `tests/`)**:
   - `engine/`: 22 modules, 21,377 lines, 231 `resolve_` methods (re-exported via root shim `ruthenian_engine.py`)
   - `digest/`: 13 modules, 8,076 lines, 155 `_format_resolve_` methods (re-exported via root shim `typikon_digest_generator.py`)
   - `scripts/`: Operational auditors, compilers, `scripts/parsers/` (18 legacy parsers), `scripts/legacy_runners/` (`generate_typikon_service.py`, `generate_cantor_prototype.py`)
   - `tests/`: 1,425 deterministic pytest checks (always run via `.venv\Scripts\python.exe -m pytest`)
6. **Tier 6 (`scratch/`)**: Gitignored ephemeral debug probes and logs.

---

## 2. Verified Engine & Test Baseline Metrics

* **Pytest Suite**: **1,425 passed, 0 failed** (`.venv\Scripts\python.exe -m pytest --ignore=tests/test_ui_readability.py` + `tests/test_session_compliance.py`).
* **Systemic & Multi-Year Audits**:
  - 2026 365-Day Systemic Scan: **0 incidents**
  - 35-Paschalion Key Sweep (136 sweeps / 49,704 days): **0 violations**
  - 100-Year Golden Window (1950–2050): **0 violations**
  - Temple Patronal Collision Matrix (34 cases $\times$ 4 archetypes = 136 scenarios): **0 violations**
  - Annual Almanac Fast-Path Consistency (2025, 2026, 2027): **3/3 passed (100%)**
* **Recension Hydration**:
  - `Stamford Divine Office` (Backup): **2,854 keys** across 14 JSON files.
  - `Royal Doors` (Primary): **0 keys** across 12 empty `{}` JSON shells (falls back cleanly to Stamford).
  - `St. Sergius` (Overlay): **187 keys** (Tone 1 refined).
  - `Synodal Footnotes`: **786 keys** (`json_db/synodal_footnotes.json`).

---

## 3. Prioritized "Restart Engine" Action Plan

1. **Commit 6-Tier Stabilized Baseline**: Commit the stabilized 6-Tier directory moves, modernized `.gitignore`, `render.yaml`, and Sept 30 Kyivan Musicology databases (`Data/Canonical_English_Lexicon.json`, `Data/Master_Incipits.json`, `Data/yas_no_*.json`).
2. **`Data/Inbox/` Deduplication & PDF Eviction (~1.41 GB)**:
   - Delete the **202 exact SHA-256 duplicate PDFs** at the top level of `Data/Inbox/*.pdf`.
   - Route `Data/Inbox/PDFs/` (204 PDFs, 628.6 MB) and `Data/Inbox/Codex_No_*_Archive_v1_Baseline/` (55 PDFs, 186.7 MB) off Drive C per `ECOSYSTEM_ARCHITECTURAL_STANDARD.md`.
   - Clean already-ingested Sept 30 `yas_no_*` files from `Data/Inbox/`.
3. **Ingest Staged Translation Monuments (Monuments 1–6) from `Data/Inbox/`**:
   - Ingest `1891_Lviv_Provincial_Synod`, `1899_Dolnytsky_Typikon`, `1901_Mikita_Typikon`, `1852_Doskovsky_Typikon`, `1888_Violakis_Typikon`, and `1910_Skaballanovich_Typikon` into `Data/Service Books/` and archive duplicate raw cohort folders (`1891_Lviv_Synod`, `1910_Skaballanovich_Tolkovy_Typikon`).
4. **Ingest Staged Oct 12 Kyivan Musicology Payloads from `Data/Inbox/`**:
   - Promote homoglyph-normalized `Master_Incipits.json` (Oct 12), `lexicon_bridge_concordance.json`, `pan_catalogue_fortified_corpus.json` (590 monuments), `yasinovsky_catalogue_fortified_corpus.json` (526 codices), and `WO_01..WO_05_*_Deduplicated_Repertoire.json` (140 seasonal chant items) into `Data/` and `Data/databases/`.
5. **Hydrate `Royal Doors` Primary Recension & Cantor Repertoire UI**:
   - Populate `Data/Service Books/Recensions/Royal Doors/JSON/assets/` and expose the `WO_01..WO_05` seasonal chant repertoires in the Cantor Dashboard.
