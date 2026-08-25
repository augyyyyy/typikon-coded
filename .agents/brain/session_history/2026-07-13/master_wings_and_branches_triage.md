<!-- [GENERATOR: DeepSeek-V4-Pro] -->
# Master Architectural & Git Triage: All Wings & Branches — Perfected, Evidence-Gated & Terminology-Enforced

## Purpose
This document provides a granular, atomic, evidence-gated, and anti-pattern-free triage across the entire Typikon Coded ecosystem. It is structured into four parts:
1. **Mandatory Pre-Flight Checklist** (AGENTS.md Rule 11)
2. **The 5 Architectural Wings of the Hub & Spoke Ecosystem** with UGCC Royal Doors terminology enforcement
3. **The 3 Active / Archival Git Branches** with step-by-step verification commands
4. **Mandatory Post-Flight Checklist** (AGENTS.md Rule 12)

All claims are marked as **REPORTED** (pending verification) or **VERIFIED** (backed by terminal output) per the Honesty Protocol and Evidence Gate.

---

## PART 0: MANDATORY PRE-FLIGHT CHECKLIST (Before ANY Code Change)

Before editing or creating any files, the working agent MUST run this mental check and paste the output:

1. **Read** `.agents/AGENTS.md` and `.agents/references/project_facts.md`.
2. **Verify** you have read `.agents/references/learnings.md` and `.agents/references/anti_patterns.md`.
3. **Cite at least ONE specific rule** from these files relevant to the current task. (Example: "I cite AGENTS.md Rule 2 — Liturgical Source-Grounded Claims: all assertions must cite the canonical hierarchy Ordo > Dolnytsky Parts II–V > Liturgicon > Dolnytsky Part I.")
4. **Run the session compliance check and paste the output**:

```powershell
$env:PYTHONPATH="." ; .venv\Scripts\pytest tests/test_session_compliance.py --verbose
```

**Evidence Gate**: The raw terminal output of the compliance check MUST be pasted before any file modification. If the check fails, no edits are permitted until failures are resolved.

---

## PART I: UGCC ROYAL DOORS TERMINOLOGY MAP — STRICT ENFORCEMENT

The following canonical vocabulary map is the **only** authorized terminology for all code, JSON keys, UI labels, and documentation. Any deviation is a zero-tolerance terminology violation (anti-pattern #13).

| ✅ Canonical Royal Doors Term | ❌ Banned/Incorrect Variants | Context |
|---|---|---|
| **Exapostilarion** | Exapostilaria, Exapostolarion, Exapostilar | Matins hymn after the Canon |
| **Irmos** | Irmosy, Irmoi (when used as singular), Heirmos | Model stanza at start of each Canon Ode |
| **Prokeimenon** | Prokimen, Prokeimena (when used as singular), Prokimenon | Psalm verse before Scripture readings |
| **Sessional Hymn** | Sedalion, Kathisma Hymn, Sidalion, Kathisma Troparion | Hymn sung after the Kathisma at Matins |
| **Aposticha** | Apostichon, Apostikha, Stichos | Verses at the end of Vespers/Matins |
| **Theotokion** | Marian Hymn, Mother of God Hymn, Bogorodichen | Hymn honouring the Theotokos |
| **Kontakion** | Kondakion, Kondak | Hymn after Ode 6 of the Canon |
| **Oikos** | Ikos, Oikos Hymn | Stanza following the Kontakion |
| **Sticheron** / **Stichera** (pl.) | Sessional Sticheron, Stichira, Stikhera | Verses at "Lord I have cried", Aposticha, Lauds |
| **Troparion** / **Troparia** (pl.) | Dismissal Hymn, Tropary | Dismissal or commemorative hymn |
| **Kathisma** | Cathisma, Kathismata (pl.) | Psalter section at Matins |
| **Canon** | Kanon, Ode sequence | Nine-ode hymnographic unit at Matins |
| **Typikon** | Typicon, Typika (incorrect context) | Liturgical rule book (2010 Lviv Typikon) |

**Terminology Verification Command** (run at any time, requires zero output for pass):

```powershell
$env:PAGER="cat"; git grep -n -E "Sidalion|Sedalion|Kathisma Hymn|Irmosy|Prokimen[^o]|Marian Hymn|Bogorodichen|Kondak|Ikos|Stikhera|Stichira|Dismissal Hymn as key|Tropary|Cathisma" -- "*.py" "*.json" "*.md" "*.js" "*.html" "*.css" ; if ($LASTEXITCODE -eq 1) { Write-Output "PASS: No banned terminology found." } else { Write-Output "FAIL: Banned terminology detected. See lines above." }
```

**Schema Key Terminology Rule**: All JSON flat keys MUST use the canonical terms above. For example:
- ✅ `exapostilarion_1` — ❌ `exapostilaria_1`
- ✅ `irmos_tone1` — ❌ `irmosy_tone1`
- ✅ `sessional_hymn_tone1` — ❌ `sidalion_tone1`
- ✅ `prokeimenon_tone1` — ❌ `prokimen_tone1`

---

## PART II: THE 5 ARCHITECTURAL WINGS

```mermaid
graph TD
    subgraph The Hub (Typikon Coded)
        W1[Wing 1: Core Logic Engine]
        W2[Wing 2: Service Structures]
        W5[Wing 5: Cantor Dashboard & UI API]
    end

    subgraph The Spokes & Data Repositories
        W3[Wing 3: Text Assets & Recensions]
        W4[Wing 4: Musicology & Chant Notation]
    end

    W1 --> W2
    W2 --> W5
    W3 -->|Hydrates Propers| W1
    W4 -->|Supplies Melodies & Neumes| W5
```

---

### 1. Wing 1: Core Logic Engine & Computus (The Brain)

- **Code Location**: `engine/` (REPORTED: 16 discrete mixin modules, ~11,795 lines) + `typikon_digest_generator.py`
- **Core Function**:
  - Computus calculation (Paschal cycle, moveable calendar offsets, Eothinon, weekly tones).
  - Paradigm matching (Dolnytsky 20 General Paradigms, Lviv 1–60 seasonal cases in `02a_logic_general.json`).
  - Liturgical collision resolution (Menaion feasts on Sundays, Lenten weekday suppression, Triodion/Pentecostarion precedence).
  - REPORTED: 207 `resolve_` methods providing dynamic slot resolution.
- **Current Health Status**: **VERIFIED** by project_facts.md: 337 tests pass at baseline. Additional compliance tests reported on the active branch require re-verification (see target count below).
- **Key Invariants**:
  - Zero hardcoded text (Rule 7, anti-pattern #1).
  - Strict precedence: Ordo Celebrationis (Choreography) > Dolnytsky Parts II–V (Propers) > Ruthenian Liturgicon > Dolnytsky Part I.
  - Pure deterministic execution (Temperature = 0.0 simulation).
  - No bare `except: pass` (anti-pattern #2).
  - No `hasattr` guard without a fallback `[NOT IMPLEMENTED: method_name]` else branch (anti-pattern #5).
- **Triage Directives & Action Items**:
  - **TDD**: Any new resolver MUST follow Double-Blind TDD: write a failing test in `tests/` grounded in canonical sources, then implement, then re-run pytest.
  - **Terminology**: New resolver keys must use the Royal Doors terminology map (Part I above).
  - **Evidence Gate**: Every new resolver must be verified with:
    ```powershell
    $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\pytest tests/test_<new_resolver>.py --verbose
    ```
  - **Test Count Target**: REPORTED target of 379 passing tests (baseline 337 + 42 new compliance/schema tests). Actual count MUST be verified with:
    ```powershell
    $env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\pytest --ignore=tests/test_ui_readability.py --verbose
    ```

---

### 2. Wing 2: Service Structures & Skeletons (The Bones)

- **Code Location**: `json_db/01*_struct_*.json` (REPORTED: 11 core service structure skeletons) + `schemas/service_structure.schema.json`
- **Core Function**:
  - Defines the canonical skeletal slot order of every Byzantine service:
    - `01a_struct_small_vespers.json`, `01b_struct_great_vespers.json`, `01c_struct_daily_vespers.json`
    - `01d_struct_festal_matins.json`, `01e_struct_sunday_matins.json`, `01f_struct_daily_matins.json`
    - `01g_struct_midnight.json`, `01h_struct_compline.json`, `01i_struct_hours.json`
    - `01j_struct_liturgy.json`, `01k_struct_presanctified.json`, `01l_struct_royal_hours.json`
  - Encodes physical liturgical choreography per Ordo Celebrationis 1944 (Holy Doors opening/closing, curtain state, censing routes, clergy positions, bow types).
- **Current Health Status**: **VERIFIED** by project_facts.md: schema validation passing for baseline files. Active branch requires re-validation (see Part III).
- **Key Invariants**:
  - Envelope schema compliance: `{ "file_metadata": {}, "structures": {} }`.
  - All dynamic slots must bind to registered resolvers in Wing 1.
  - Structure skeletons must use the Royal Doors terminology for slot names (e.g., `exapostilarion`, `sessional_hymn`, `irmos`).
- **Triage Directives & Action Items**:
  - Do NOT suppress daily cycle services (Compline/Midnight Office) in core structure files; suppressions only permitted in quick-reference digest view mode.
  - **Verify schema compliance**:
    ```powershell
    $env:PYTHONPATH="." ; $env:PAGER="cat" ; python tests/validate_schemas.py --verbose
    ```
  - **Verify no hardcoded text in structure slots**: each dynamic slot must resolve via a `resolve_` method, never a literal string.

---

### 3. Wing 3: Text Databases & Recensions (The Flesh)

- **Code Location**: `Data/Service Books/Recensions/` + `json_db/stamford/` + `schemas/text_asset.schema.json`
- **Core Function**:
  - Decoupled English and Church Slavonic propers, ordinaries, and rubrical texts.
  - Multi