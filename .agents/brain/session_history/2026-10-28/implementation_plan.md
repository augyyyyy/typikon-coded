# Implementation Plan: Full-Text Service Booklet & Text Asset Hydration (Wing 3)

## Goal
Remediate the three full-text booklet hydration and compliance gaps surfaced during bundle generation while strictly preserving the diplomatic integrity of the raw Stamford JSON files and adhering to the Hub-Spoke Exclusive Write-Ownership Matrix (`GLOBAL_SYSTEM_RULES.md` §7):

1. **Dynamic UGCC Terminology Normalization**: Normalize `prokimenon`/`prokimena` $\to$ `Prokeimenon`/`Prokeimena` and `Anabathmoi` $\to$ `Gradual` dynamically at the engine and booklet output boundaries ([`engine/text_db.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/text_db.py) and [`engine/generation.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/generation.py)) without mutating raw Stamford witness JSON files.
2. **Shared Atomic Corpus Unblocking & `[STUB]` Resolution**: Fix [`TextDBMixin.get_text()`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/text_db.py#L411-L580) so `[STUB]` records in `self.text_db` / `self.stamford_db` never shadow `self.atomic_corpus_db`, register the Hub key aliases mapping `horologion.*` and `liturgikon.*` keys to their existing `HOR.PRIM.*`, `ORD.PRIM.*`, `HOR.VESP.*`, and `LIT.PRIM.*` entries in the 4-shard Shared Atomic Corpus, and strip any residual `[STUB]` markers on fallback.
3. **Lenten Polyeleos Lectionary Rendering (`2026-03-09`, 40 Martyrs of Sebaste)**:
   - Update [`LentenMixin.resolve_presanctified_readings()`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/lenten.py#L684-L812) so that when a Polyeleos feast falls on a Lenten weekday (`rank <= 3`), the Saint's 3 Old Testament Paremias (`isaiah_43`, `isaiah_49`, `martyrs_readings_3` resolved via `resolve_vespers_readings_logic`) and the full Feast Liturgy reading metadata (Prokeimenon, Epistle `hebrews_12_1_10`, Alleluia, Gospel `matthew_20_1_16`) are included in the Presanctified readings payload.
   - Add a dedicated `result.get("type") == "presanctified_readings"` branch in [`GenerationMixin._hydrate_and_format_logic_result()`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/generation.py#L1520-L1555) before Case 4 (`"sequence" in result`) so Presanctified readings are no longer misrouted into the `Troparia & Kontakia` formatter and all 5 festal readings (`isaiah_43`, `isaiah_49`, `martyrs_readings_3`, `hebrews_12_1_10`, `matthew_20_1_16`) plus the 2 Triodion Paremias render into the full-text booklet.
4. **Booklet Auditor & Regression Gate**: Expand [`scripts/audit_service_booklet.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/audit_service_booklet.py) Layer 4 checks and add `tests/test_booklet_hydration_and_lenten_readings.py`.

---

## Proposed Changes

### 1. Text Database Layer ([`engine/text_db.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/text_db.py))
* **`ATOMIC_CORPUS_HUB_ALIASES` Registry**:
  * Map the Hub's canonical `horologion.*` and `liturgikon.*` keys to their existing structural IDs in `Projects/Shared_Lexicon/atomic_corpus/01_ordinarium_primitives.json`:
    * `horologion.common.creed` $\to$ `ORD.PRIM.CREED`
    * `horologion.common.axion_estin` $\to$ `ORD.PRIM.MORE_HONORABLE`
    * `horologion.common.our_father` $\to$ `ORD.PRIM.OUR_FATHER`
    * `horologion.common.lord_have_mercy_3x` $\to$ `ORD.PRIM.KYRIES_THREEFOLD`
    * `horologion.common.lord_have_mercy_12` $\to$ `ORD.PRIM.KYRIES_TWELVEFOLD`
    * `horologion.common.blessing` $\to$ `ORD.PRIM.INITIAL_BLESSING`
    * `horologion.matins.blessing_vigil` / `horologion.glory_to_holy` $\to$ `HOR.PRIM.CONSUBSTANTIAL_BLESSING`
    * `horologion.matins.great_doxology` $\to$ `HOR.PRIM.GREAT_DOXOLOGY`
    * `horologion.matins.small_doxology_read` $\to$ `ORD.PRIM.SMALL_DOXOLOGY`
    * `horologion.matins.hexapsalmos` / `horologion.matins.six_psalms` $\to$ `HOR.PRIM.HEXAPSALMOS`
    * `horologion.matins.praises_psalms` $\to$ `HOR.PRIM.PRAISES_PSALMS`
    * `horologion.matins.invitatory_3x` $\to$ `HOR.COMMON.INVITATORY_3X`
    * `horologion.vespers.nunc_dimittis` $\to$ `HOR.VESP.NUNC_DIMITTIS`
    * `horologion.vespers.phos_hilaron_read` $\to$ `HOR.VESP.PHOS_HILARON`
    * `horologion.vespers.vouchsafe_o_lord` $\to$ `HOR.VESP.VOUCHSAFE_O_LORD`
    * `horologion.vespers.psalm_103` $\to$ `HOR.VESP.PSALM_103`
    * `horologion.vespers.psalm_140` $\to$ `HOR.VESP.PSALM_140`
    * `horologion.vespers.psalm_33` $\to$ `HOR.VESP.PSALM_33`
    * `horologion.vespers.great_litany` $\to$ `HOR.VESP.GREAT_LITANY`
    * `horologion.vespers.fervent_litany` $\to$ `ORD.PRIM.AUGMENTED_LITANY`
    * `horologion.vespers.supplication_litany` $\to$ `ORD.PRIM.LITANY_OF_SUPPLICATION`
    * `horologion.common.small_litany` $\to$ `ORD.PRIM.LITTLE_LITANY`
    * `horologion.dismissal_full` / `horologion.dismissal_great` $\to$ `ORD.PRIM.DAILY_MAJOR_DISMISSAL`
    * `horologion.dismissal_small` $\to$ `ORD.PRIM.MINOR_DISMISSAL`
    * `horologion.only_begotten` $\to$ `LIT.PRIM.O_MONOGENES`
    * `horologion.protection_christians` $\to$ `ORD.PRIM.STEADFAST_PROTECTRESS`
    * `liturgikon.ambo_prayer` $\to$ `LIT.PRIM.AMBO_PRAYER`
    * `liturgikon.blessing_kingdom` $\to$ `LIT.PRIM.KINGDOM_BLESSING`
    * `liturgikon.litanies_catechumens` $\to$ `LIT.PRIM.LITANY_OF_CATECHUMENS`
* **Unblock `atomic_corpus_db` Precedence Over `[STUB]` Records**:
  * Add helper `_is_stub_record(val)` in [`TextDBMixin`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/text_db.py) that detects `[STUB]` / `STUB:` placeholders.
  * In `get_text()`, check both `text_id` and `LEGACY_KEY_ALIASES.get(text_id)` against `self.atomic_corpus_aliases`, and only treat `in_primary` as `True` when `self.primary_db` has a non-stub entry for `text_id`.
* **Runtime Terminology & Residual `[STUB]` Sanitization**:
  * In `get_text()` content processing (lines 563–580), normalize `prokimenon` $\to$ `Prokeimenon`, `prokimena` $\to$ `Prokeimena`, and `anabathmoi` $\to$ `Gradual` (case-preserving), and strip any residual `[STUB]` / `STUB:` prefix from fallback items so raw `[STUB]` markers never leak into output while preserving key-identity invariants in `tests/test_horologion_key_migration.py` and `tests/test_service_structures_migration.py`.

### 2. Lenten Polyeleos Presanctified Lectionary ([`engine/resolvers/lenten.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/lenten.py) & [`engine/generation.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/generation.py))
* **[`engine/resolvers/lenten.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/resolvers/lenten.py#L684-L780) (`resolve_presanctified_readings`)**:
  * When `rank <= 3` (Polyeleos or higher on a Lenten weekday):
    1. Query `self.resolve_vespers_readings_logic(context)` and append any saint/feast Paremias (e.g., `isaiah_43`, `isaiah_49`, `martyrs_readings_3` on `2026-03-09`) to `result["sequence"]` after the second Triodion Paremia (`Proverbs`), matching Dolnytsky Part III §3.6.4 / §3.7.1.
    2. Query `self.resolve_liturgy_readings(context, rubrics)` to populate `result["feast_readings"]` with the exact resolved `ref_key` and `text` for the Feast Prokeimenon, Epistle (`hebrews_12_1_10` / `Hebrews 12:1–10`), Alleluia, and Gospel (`matthew_20_1_16` / `Matthew 20:1–16`).
* **[`engine/generation.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/engine/generation.py)**:
  * In `_hydrate_and_format_logic_result()`, add **Case 3.6 (`result.get("type") == "presanctified_readings"`)** before Case 4 (`"sequence" in result`):
    * Render each item in `result["sequence"]` (Triodion Prokeimena, Genesis & Proverbs Paremias, *"The Light of Christ illumines all!"* exclamation, and any Polyeleos Saint Paremias such as `isaiah_43`, `isaiah_49`, `martyrs_readings_3` with their `ref_key` and hydrated text).
    * When `result.get("has_feast_readings")` is `True`, render the Feast Prokeimenon, Epistle (`hebrews_12_1_10` / `Hebrews 12:1–10`), Alleluia, and Gospel (`matthew_20_1_16` / `Matthew 20:1–16`).
  * In `generate_full_booklet()`, apply a final UGCC terminology pass normalizing any residual `prokimenon` $\to$ `Prokeimenon` and `Anabathmoi` $\to$ `Gradual`.

### 3. Booklet Auditor & Regression Test Suite ([`scripts/audit_service_booklet.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/audit_service_booklet.py) & `tests/test_booklet_hydration_and_lenten_readings.py`)
* **[`scripts/audit_service_booklet.py`](file:///c:/Users/augus/OneDrive/Documents/Google%20Antigravity/Projects/Typikon%20Coded/scripts/audit_service_booklet.py#L178-L185)**:
  * Add `"prokimenon": "prokeimenon"` and `"anabathmoi": "gradual"` to `BANNED_TERMINOLOGY_MAP`.
  * Add a Layer 4 check in `_audit_layer_4()` flagging any leaked `[STUB]` or `STUB:` placeholder string.
* **`tests/test_booklet_hydration_and_lenten_readings.py`**:
  * Verify `0` occurrences of `prokimenon`, `anabathmoi`, or `[STUB]` across `get_text()` and `generate_full_booklet()` outputs.
  * Verify that `horologion.common.creed`, `horologion.matins.great_doxology`, `horologion.vespers.nunc_dimittis`, etc., resolve to their full Shared Atomic Corpus texts.
  * Verify that `generate_full_booklet()` on `2026-03-09` (40 Martyrs of Sebaste) renders all 3 Vespers Paremias (`isaiah_43`, `isaiah_49`, `martyrs_readings_3`) and both Liturgy readings (`hebrews_12_1_10` / `Hebrews 12:1–10` and `matthew_20_1_16` / `Matthew 20:1–16`).

---

## Verification Plan
1. Run the new targeted test suite:
   `$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python.exe -m pytest tests/test_booklet_hydration_and_lenten_readings.py tests/test_horologion_key_migration.py tests/test_service_structures_migration.py --verbose`
2. Run the Canonical Service Booklet Auditor against `docs/service_books/01_great_vespers_canonical.md`:
   `.venv\Scripts\python.exe scripts/audit_service_booklet.py --booklet docs/service_books/01_great_vespers_canonical.md`
3. Run the Post-Flight Checklist (`tests/test_session_compliance.py`, `../scripts/verify_ecosystem_integrity.py --spoke "Typikon Coded"`, and full `pytest --ignore=tests/test_ui_readability.py`).
