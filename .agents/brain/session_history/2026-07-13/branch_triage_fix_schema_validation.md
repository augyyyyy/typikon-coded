<!-- [GENERATOR: DeepSeek-V4-Pro] -->
# Perfected Implementation & Triage Plan: `fix/schema-validation-repair`

## 1. Branch Identity, Evidence Status & Merge Classification

| Field | Value |
|---|---|
| **Branch Name** | `fix/schema-validation-repair` |
| **Base Commit** | `2bbf1ba` — *“Update schema validator paths and remove outdated known issues from documentation”* |
| **Working Tree State** | 15 modified files + 6 untracked tool/test files. This state is **not yet passed through the Evidence Gate**. No file is accepted for merge until the gates in Sections 2–6 are executed and pasted. |
| **Merge Mode** | Fast-forward only (`git merge --ff-only`). Never force `--no-ff`. If `main` has diverged, stop, do not reconcile manually, and report back. |
| **Classification** | Active repair and quality-gate fortification branch. |

---

## 2. Mandatory Pre-Flight Checklist Before Any Code Change

This plan is not approved for execution until the following pre-flight is run and the terminal output is pasted. Do **not** edit any file first.

### 2.1 Statement of Context Alignment

Before any command or file edit, the executing agent must state:

1. I have read `.agents/AGENTS.md` and `.agents/references/project_facts.md`.
2. I have read `.agents/references/learnings.md` and `.agents/references/anti_patterns.md`.
3. I am citing the following binding rule for this task:
   - **AGENTS.md Master Rule 4**: Zero-tolerance anti-patterns.
   - **AGENTS.md Master Rule 6**: Evidence Gate enforcement.
   - **AGENTS.md Master Rule 10**: UTF-8 enforcement and no hardcoded absolute paths.
   - **AGENTS.md Pre-Flight Checklist**: Run compliance check before touching code.
4. I have not edited any file before running the pre-flight commands.

### 2.2 Pre-Flight Compliance Check

Run:

```powershell
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\pytest tests/test_session_compliance.py --verbose
```

**Required Evidence**: Paste full pytest output. The plan is not valid if this output is missing or if a compliance failure is ignored.

### 2.3 Pre-Flight Working Tree Snapshot

Run:

```powershell
$env:PAGER="cat" ; git status --porcelain=v1
```

**Required Evidence**: Paste the exact file list. Every file listed must map to a component in Section 3. If any unknown or unrelated file appears, stop and triage before continuing.

---

## 3. Granular Working Tree Triage with Anti-Pattern Audit

All 14 blacklisted anti-patterns from `.agents/references/anti_patterns.md` plus the 3 compliance-specific anti-patterns are in force. No file may enter the commit if it introduces:

- Hardcoded absolute paths
- Hardcoded liturgical strings instead of resolver output
- Bare `except: pass`
- Raw internal keys leaked to UI
- Vague stubs
- `hasattr` guards without fallback
- Interactive pager locks
- Any change without tests
- Fabricated progress narratives
- Post-hoc rationalizations
- Exploratory drift
- Agreeable momentum
- Retroactive context fabrication
- Liturgical authority conflation
- UI robot jargon
- Skipped pre-flight
- Banned phrases without evidence

### 3.1 File-by-File Triage Matrix

| Component Area | Files | Required Verification |
|---|---|---|
| **Compliance & Brain** | `.agents/AGENTS.md`<br>`.agents/references/anti_patterns.md`<br>`.agents/references/learnings.md`<br>`.agents/skills/compliance_gate/SKILL.md`<br>`tests/test_session_compliance.py` | Run compliance test. Review diff for no weakening of zero-tolerance rules. Ensure the compliance checker does not use interactive commands or bare `except`. |
| **Key Aliasing & Recension Fallback** | `engine/text_db.py`<br>`engine/core.py`<br>`tests/test_recensions.py` | Run `tests/test_recensions.py`. Ensure legacy aliases are internal only; UI must still receive resolved, humanized text. Ensure fallback to Stamford is not bypassed. |
| **Calendar Source Endpoint & UI** | `cantor_dashboard/server.py`<br>`cantor_dashboard/main.js`<br>`cantor_dashboard/index.html`<br>`tests/test_server_endpoints.py`<br>`tests/test_calendar_recensions.py` | Run endpoint and calendar tests. Inspect UI diff for robot jargon. Ensure query parameter values do not leak raw into display labels. |
| **Triodion Parser Modernization** | `parsers/parse_triodia.py` | Inspect parser diff for dynamic `pathlib.Path` resolution and `encoding='utf-8'`. No absolute `c:\Users\...` paths may remain. |
| **Schema Validation Repair** | `tests/validate_schemas.py`<br>`schemas/README.md`<br>`Data/.../text_lenten_triodion.json`<br>`Data/.../text_floral_triodion.json` | Run `tests/validate_schemas.py`. Required final output: `Scanned: 42 files | Errors: 0`, or actual recorded count with 0 errors. |
| **Perfection & Searcher Tools** | `scripts/anti_pattern_searcher.py`<br>`scripts/perfect_plan_via_deepseek.py`<br>`scripts/build_searcher_via_deepseek.py`<br>`scripts/reconcile_failures_via_deepseek.py` | Run `scripts/anti_pattern_searcher.py --help` and then run it against the current diff. If it reports hits, stop and revert before commit. |

---

## 4. UGCC Royal Doors Terminology & Key Map Gate

The following canonical terminology must be enforced. Do **not** introduce custom variants, Russian/Greek conflations, or raw machine keys in user-facing texts.

| Concept | Canonical UGCC Royal Doors Term | Hard Rule |
|---|---|---|
| Dismissal hymn at Matins after canon | **Exapostilarion** | Use this exact spelling. Do not substitute `Exapostilary` or other variants. |
| Canon initial troparion | **Irmos** | Use this exact spelling. Do not invent pluralized or transliterated variants. |
| Chant preceding Epistle | **Prokeimenon** | Use this exact spelling. Do not substitute `Prokimenon`. |
| Hymn after psalm/ode | **Sessional Hymn** | Use this exact spelling. Do not use `Sedalen` in user-facing output. |
| Raw internal keys | `Eothinon_1_theotokion`, `Tone_1`, `righteous_memory` | Never leak raw keys into UI or generated booklet output. They must be resolved through `humanize_key()` or `get_text()`. |

### 4.1 Terminology Verification Commands

Run before commit:

```powershell
$env:PAGER="cat" ; git --no-pager grep -n -E "Exapostilarion|Irmos|Prokeimenon|Sessional Hymn" -- Data schemas engine cantor_dashboard
```

This confirms canonical tokens are present where relevant.

Run a reverse scan for known raw-key leakage:

```powershell
$env:PAGER="cat" ; git --no-pager grep -n -E "Eothinon_[0-9]+_theotokion|Tone_[0-9]+|righteous_memory" -- cantor_dashboard
```

If any raw key appears in user-facing files, stop and fix before commit.

Run a duplicate-handler check for `cantor_dashboard/server.py`:

```powershell
$env:PAGER="cat" ; git --no-pager diff -- cantor_dashboard/server.py
```

Manually verify no dead duplicate handler remains and that the exposed `calendar_source` query parameter is validated.

---

## 5. Atomic Step-by-Step Resolution & Evidence Plan

### Step 1: Repair Triodion Parser Key Prefixes and Dynamic Paths

1. Inspect current parser diff before editing:

```powershell
$env:PAGER="cat" ; git --no-pager diff -- parsers/parse_triodia.py
```

2. Update `parsers/parse_triodia.py`:
   - Replace all hardcoded absolute paths with dynamic path resolution using `pathlib.Path(__file__).resolve().parents[...]`. Do not use `c:\Users\...`.
   - Prepend `triodion.` to all generated Sunday and service keys using a module-level constant, e.g. `KEY_PREFIX = "triodion."`.
   - Ensure every file operation uses `encoding='utf-8'`.

3. Regenerate the triodion JSON assets:

```powershell
$env:PYTHONPATH="." ; .venv\Scripts\python parsers/parse_triodia.py
```

4. Verify generated files are updated and no raw internal keys leaked:

```powershell
$env:PAGER="cat" ; git --no-pager diff --stat HEAD -- Data
$env:PAGER="cat" ; git --no-pager diff -- Data/Service\ Books
```

**Required Evidence**: Paste `git --no-pager diff --stat` output and sample diff showing path replacement removal and `triodion.` key prefixes.

---

### Step 2: Validate 100% Schema Pass Rate

Run:

```powershell
$env:PYTHONPATH="." ; .venv\Scripts\python tests/validate_schemas.py
```

**Required Evidence**: Paste full validator output. It must show `Errors: 0`. If the reported scanned count differs from 42, record the actual count and paste the output. Do not hand-edit JSON data files only to force schema pass; regeneration must be reproducible from parser.

Also inspect `schemas/README.md` diff:

```powershell
$env:PAGER="cat" ; git --no-pager diff -- schemas/README.md
```

Ensure the README does not contain stale validation-failure claims.

---

### Step 3: Run Targeted Regression Tests

Run each targeted suite separately and capture actual counts:

```powershell
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python -m pytest tests/test_session_compliance.py -v
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python -m pytest tests/test_recensions.py -v
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python -m pytest tests/test_server_endpoints.py -v
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python -m pytest tests/test_calendar_recensions.py -v
$env:PYTHONPATH="." ; $env:PAGER="cat" ; .venv\Scripts\python -m