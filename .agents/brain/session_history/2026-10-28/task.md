# Task Checklist: Full-Text Service Booklet & Text Asset Hydration (Wing 3)

- [x] Pre-Flight Checklist & Forensic Discovery (`tests/test_session_compliance.py`)
- [x] Interactive Design Alignment (`/grill-me` 4-branch decision tree) & `implementation_plan.md` approval
- [x] Write TDD regression test suite (`tests/test_booklet_hydration_and_lenten_readings.py`)
- [x] Update `engine/text_db.py`:
  - [x] Add `ATOMIC_CORPUS_HUB_ALIASES` mapping `horologion.*` and `liturgikon.*` keys to `HOR.PRIM.*`, `ORD.PRIM.*`, `HOR.VESP.*`, and `LIT.PRIM.*`
  - [x] Unblock `atomic_corpus_db` lookup when `primary_db` / `text_db` / `backup_db` only holds a `[STUB]` record
  - [x] Normalize `prokimenon` / `prokimena` $\to$ `Prokeimenon` / `Prokeimena` and `anabathmoi` $\to$ `Gradual`, and strip residual `[STUB]` markers in `get_text()`
- [x] Update `engine/resolvers/lenten.py` & `engine/generation.py`:
  - [x] Include Polyeleos saint Paremias (`isaiah_43`, `isaiah_49`, `martyrs_readings_3`) and Feast Liturgy reading metadata (`hebrews_12_1_10`, `matthew_20_1_16`) in `resolve_presanctified_readings()`
  - [x] Add `presanctified_readings` hydration branch in `_hydrate_and_format_logic_result()` and UGCC terminology normalization pass in `generate_full_booklet()`
- [x] Update `scripts/audit_service_booklet.py`:
  - [x] Add `"prokimenon": "prokeimenon"` and `"anabathmoi": "gradual"` to `BANNED_TERMINOLOGY_MAP`
  - [x] Add `[STUB]` leak check in `_audit_layer_4()`
- [x] Run Post-Flight Checklist (`git diff --stat`, `test_session_compliance.py`, `verify_ecosystem_integrity.py`, full `pytest`, archive artifacts to `.agents/brain/session_history/2026-10-28/`)
