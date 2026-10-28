# Task Checklist: Anti-Potemkin (`SGC-01`..`SGC-05`) & Ecosystem Synchronization Remediation

- [x] **Pre-Flight Compliance Check (Master Rule 11)**
  - [x] Read `.agents/AGENTS.md`, `project_facts.md`, `learnings.md`, `anti_patterns.md`
  - [x] Run `tests/test_session_compliance.py` (`1 passed`)
  - [x] Resolve all 6 architectural branches via `/grill-me` (`ask_question`)

- [x] **Phase 1: Immediate `Typikon Coded` AST Violation Remediation (31 Violations -> 0)**
  - [x] Quarantine legacy DeepSeek & Potemkin synthesizer scripts (`scripts/build_searcher_via_deepseek.py`, `scripts/deepseek_*.py`, `scripts/perfect_plan_via_deepseek.py`, `scripts/reconcile_failures_via_deepseek.py`, `scripts/chronicle_synthesizer.py`, `scratch/move_parts.py`, `scratch/verify_complex.py`) and `docs/chronicle/` into `scripts/archived_pipelines/` (`SGC-05`)
  - [x] Refactor `scripts/chronicle_harvester.py` to remove hardcoded `VOLUME_MAP` prose
  - [x] Upgrade `scripts/validate_db.py`, `scripts/verify_propers_addressability.py`, `scripts/verify_function_coverage.py`, `tests/verify_semantics.py`, and `tests/verify_sliding_window.py` to open primary source files at runtime (`SGC-02`)

- [x] **Phase 2: Service Booklet Compiler & Auditor Grounding (`SGC-01a`, `SGC-01b`, `SGC-02`, `SGC-05`)**
  - [x] Create `json_db/01h_service_booklet_architecture.json` mapping all 17 Great Vespers stations and Appendices `§A..§K` to `01h_struct_vespers.json`, `Ordo_Celebrationis_1996_CLEAN.md`, `Dolnytsky_Typikon_Master.md`, and `text_horologion.json`
  - [x] Refactor `engine/service_book_compiler.py` to eliminate all hardcoded prose arrays (`md.append(...)`) and the `self.struct_vespers` Dead-Loader Facade, and recompile `docs/service_books/01_great_vespers_canonical.md`
  - [x] Upgrade `scripts/audit_service_booklet.py` with Layer 5 runtime primary-source verification (`_audit_layer_5_primary_sources`) and verify `tests/test_service_book_compilation_and_audit.py` (`8 passed`)

- [x] **Phase 3: Resolver `@liturgical_source` Re-Anchoring & Citation Matrix Regeneration**
  - [x] Re-anchor all 50 `@liturgical_source` decorators across `engine/resolvers/*.py` to exact current 1-indexed line ranges (`L<start>-<end>`) and section/paragraph IDs in `Ordo_Celebrationis_1996_CLEAN.md` and `Dolnytsky_Typikon_Master.md`
  - [x] Create `scripts/generate_citation_matrix.py` and deterministically regenerate `docs/encyclopedia/master_citation_matrix.md`
  - [x] Upgrade `scripts/audit_citations.py`, `tests/test_citations.py`, and `tests/test_source_grounding.py` to verify line ranges and verbatim section headers against primary sources (`5 passed`)

- [x] **Phase 4: 4-Shard Shared Atomic Corpus Hydration & `TextDB` Wiring (`Schism D` / `SGC-02` / `SGC-04`)**
  - [x] Create and run `scripts/register_hub_atomic_primitives.py` to populate `01_ordinarium_primitives.json`, `02_sticherarion.json`, `03_irmologion.json`, and `04_kanonnik.json` (including an explicit `SGC-04` `[UNRESOLVED_CANONICAL_GAP: ...]` record) and compile `master_liturgical_corpus.json` (`361` verified entries across 4 shards)
  - [x] Wire `engine/core.py` and `engine/text_db.py` (`_load_atomic_corpus` & `get_text`) to load and query `self.atomic_corpus_db` first
  - [x] Create and pass `tests/test_atomic_corpus_integration.py` (`2 passed`)

- [x] **Phase 5: Spoke Supply-Chain Sanitization & Hub Inbox Gatekeeper (`SGC-02` / `SGC-04`)**
  - [x] Create and run `scripts/sanitize_spoke_provenance.py` on `json_db/propers_comparisons/festal_propers_pure_typikon_database.json`, `Data/yas_no_*_parsed.json` (fixing the `f. 1r.2` Ode 3 Heirmos title contradiction in `yas_no_14_parsed.json`), and `Data/Inbox/*.json`
  - [x] Create `scripts/audit_inbox_handoffs.py` and `tests/test_inbox_gatekeeper.py`, and upgrade `tests/test_musicology_ingestion.py` (`20 passed`)

- [x] **Phase 6: Parent Hub AST Hardening & Artifact Lineage Law (`SGC-05`)**
  - [x] Upgrade `../scripts/verify_ecosystem_integrity.py` with `*_compiler.py`/`*_synthesizer.py`/`audit_*.py` matching, `SGC-01A-ATOMIZED-PROSE` detection, class `self.<attr>` Dead-Loader Facade detection, Gate 2 dict/list container taint fix, and Gate 4 non-empty shard enforcement
  - [x] Ground `scripts/audit_all_days_heuristics.py`, `scripts/audit_canonical_truth_pipeline.py`, `scripts/audit_day_cards.py`, `scripts/audit_liturgical_context.py`, and `scripts/audit_temple_collisions.py` in primary sources at runtime
  - [x] Codify Potemkin Goodharting Taxonomy (`SGC-01a`..`SGC-04`) and `SGC-05` ("No Crime-Scene Cleanup" Artifact Lineage Law) in `../GLOBAL_SYSTEM_RULES.md` §8, `../SPOKE_SYNCHRONIZATION_PROMPT.md`, and `.agents/AGENTS.md`
  - [x] Verify `python "../scripts/verify_ecosystem_integrity.py" --spoke "Typikon Coded"` (`0` violations across Gates 1–4)

- [x] **Mandatory Post-Flight Checklist (Master Rule 12)**
  - [x] Run `git --no-pager diff --stat HEAD`, `test_session_compliance.py`, `verify_ecosystem_integrity.py --spoke "Typikon Coded"`, and the full `pytest` suite
  - [x] Archive session planning artifacts (`implementation_plan.md`, `task.md`, `walkthrough.md`) to `.agents/brain/session_history/2026-10-18/`
