<!-- [GENERATOR: DeepSeek-V4-Pro] -->
# Implementation Plan — Cantor Dashboard Panels & UI Elements Audit

> **Status:** PLANNING ONLY — no code changes have been made. No completion claims are asserted in this document. All evidence must be gathered via the Verification Plan (§7) before any status can be marked `[PASS]`.
>
> **Scope:** Element-by-element verification audit of all panels, controls, and data bindings in the Cantor Dashboard until `ALL ELEMENTS = PASS`.

---

## 0. Pre-Flight Checklist (Mandatory Before Any Code Change)

Per **Master Rule 11**, no file may be edited or created until the following are completed and their outputs pasted into the session log:

1. **Read** `.agents/AGENTS.md` and `.agents/references/project_facts.md` — re-confirm canonical architecture.
2. **Read** `.agents/references/learnings.md` and `.agents/references/anti_patterns.md` — re-confirm the 14 blacklisted anti-patterns.
3. **Cite at least ONE specific rule** applicable to this task:
   > `AGENTS.md — Master Rule 4: Zero-Tolerance Anti-Patterns. The 14 blacklisted anti-patterns (7 code + 7 behavioral) are zero-tolerance violations.`
   > `AGENTS.md — Master Rule 6: Evidence Gate Enforcement. Every claim of completion must be accompanied by actual terminal output.`
4. **Run the session compliance check and paste the output:**

```powershell
$env:PYTHONPATH="." ; .venv\Scripts\pytest tests/test_session_compliance.py --verbose
```

> ⛔ **Do not proceed as `[PASS]` on any element until the Pre-Flight Checklist output is in the session log.**

---

## 1. UGCC Royal Doors Terminology Compliance Matrix

Per **Master Rule 8** (UGCC Terminology Compliance), all user-facing text in the dashboard must use standardized UGCC English terms mapped to the **Royal Doors** recension vocabulary. The following terms are strictly enforced and must be verified in every panel, digest, and booklet output:

| # | Canonical Term (Royal Doors) | Forbidden/Rejected Variants | Verification Scope |
| :-: | :--- | :--- | :--- |
| **T01** | **Exapostilarion** | "Exapostelarion", "Exapostilary", "Evlogitaria" (unqualified) | Booklet content, Canon references, Digest rubrics |
| **T02** | **Irmos** | "Hirmos", "Irmus", "Heirmos" | Canon interlude output, Booklet chants |
| **T03** | **Prokeimenon** | "Prokimenon", "Prokimen", "Prokimenon O Gladsome Light" | Booklet content, Digest rubrics, Liturgy propers |
| **T04** | **Sessional Hymn** | "Sedalen", "Sedalin", "Kathisma hymn" (as raw key) | Canon Ode III interludes, Digest rubrics, Booklet content |
| **T05** | **Kontakion** | "Kondakion", "Kondak" | Feast day propers, Canon interludes |
| **T06** | **Troparion / Troparia** | "Tropari" (as UI label), "Trop" | Booklet, Digest |
| **T07** | **Theotokion** | "Theotokion (in the tone)" (without resolution) | Ode interludes, Aposticha sections |
| **T08** | **Sticheron / Stichera** | "Sticherion", "Stickeron" | Aposticha, Lord I Have Cried output |
| **T09** | **Aposticha** | "Apostikha", "Verse at the Stichos" | Booklet section headers |
| **T10** | **Divine Liturgy** (not "Mass") | "Liturgy of the Hours" (when referring to daily service), "Divine Liturgy of St. John Chrysostom" (when needed) | Booklet, Digest, UI headings |

> **Verification Rule:** Any occurrence of a forbidden variant in `cantor_dashboard/main.js`, `cantor_dashboard/index.html`, or `cantor_dashboard/style.css` must be replaced with the canonical term. No raw database key (e.g., `Eothinon_1_theotokion`) may leak into any user-facing DOM element or clipboard output (Anti-Pattern 3).

---

## 2. Dashboard Architecture & Panel Layout

The Cantor Dashboard is composed of:
- **1 Primary Header** (tab navigation, theme toggle)
- **1 Date Resolver Bar** (date input, quick jumps, parameter overrides drawer)
- **4 Primary Panel Groups** (Liturgical Context, Cantor Service Booklet, Service Rubrics Digest, Engine Logic Trace)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 CANTOR DASHBOARD HEADER                                │
│ [Tab: Liturgical Calendar]  [Tab: Book Browser]  [Tab: Feast & Roadmap]  [Theme Toggle]│
├────────────────────────────────────────────────────────────────────────────────────────┤
│ LITURGICAL DATE RESOLVER BAR                                                           │
│ [Date Input] [Resolve Date] [Quick Jumps: Clean Monday | Thomas Sunday | Today | etc.] │
│ [▼ Liturgical Parameter Overrides Drawer]                                              │
├────────────────────────┬───────────────────────────────┬───────────────────────────────┤
│ PANEL 1:               │ PANEL 2:                      │ PANEL 3:                      │
│ LITURGICAL CONTEXT     │ CANTOR SERVICE BOOKLET        │ SERVICE RUBRICS DIGEST        │
│                        │ (Main View)                   │ (Unified Reference Drawer)    │
│ • Date & Human Title   │ • Propers & Sung Chants       │ • View Office Dropdown        │
│ • Rank & Tone Badges   │ • Actor Tags ([PRIEST], etc.) │ • Copy Rubrics Button         │
│ • Vestment Color Swatch│ • Musical Phrasing Markings   │ • Step-by-Step Rubrics        │
│ • Fasting Rule Badge   │ • Copy & Print Actions        │ • Vestment & Fasting Badges   │
│ • Prostrations Rule    │ • [📖 Toggle Reference Panel] │ • Close [❌] Action           │
│ • Paradigm ID & Types  │                               │                               │
├────────────────────────┴───────────────────────────────┴───────────────────────────────┤
│ PANEL 4: ENGINE LOGIC TRACE (Dev Mode Drawer)                                          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

> **Correction from draft:** The original draft stated "5 primary panel groups" but enumerated only 4 panels. The correct count is **4 panels**, plus 1 header and 1 resolver bar. No 5th panel exists in the verified architecture.

---

## 3. Element-by-Element Dashboard Audit Matrix

> **Legend:** `[PENDING AUDIT]` — no verification performed yet. `[PASS]` — verified with evidence pasted per §7. `[FAIL]` — verification failed; fix applied and re-audited per §6.

### Section A: Resolver Controls & Parameter Overrides

| # | Element ID | UI Control Description | Data Binding & Expected Behavior | Status |
| :-: | :--- | :--- | :--- | :-: |
| **A01** | `liturgical-date-input` | Date Picker | Sets `state.selectedDate`, formats to `YYYY-MM-DD`; re-renders resolver call if auto-resolve enabled. | `[PENDING AUDIT]` |
| **A02** | `resolve-date-btn` | Primary Action Button | Triggers `/api/resolve` fetch with active query params (`recension`, `calendar-source`, `paschalion`, `temple-feast`, `include-ceremonial`, `digest-mode`) in the request payload. | `[PENDING AUDIT]` |
| **A03** | `quick-btn` (x4) | Preset Date Shortcuts | Instantly populates date input for: Clean Monday, Thomas Sunday, Today, Dormition. Each must calculate dates dynamically (not hardcode `YYYY-MM-DD`). | `[PENDING AUDIT]` |
| **A04** | `opt-recension` | Recension Dropdown | Switches text source: `Royal Doors` (primary), `Stamford` (backup fallback), `St. Sergius` (custom overlay). Must honor Primary-Backup resolution order from `.agents/references/project_facts.md` §3. | `[PENDING AUDIT]` |
| **A05** | `opt-calendar-source` | Calendar Source Dropdown | Decoupled calendar rule selector: `Default`, `UGCC Web`, `Lviv Typikon`. Changes must NOT mutate recension selection. | `[PENDING AUDIT]` |
| **A06** | `opt-paschalion` | Paschalion Dropdown | Toggles Easter computus: `Gregorian`, `Julian`, `Revised Julian`. Changing paschalion must trigger full re-resolve of movable feasts. | `[PENDING AUDIT]` |
| **A07** | `opt-temple-feast` | Temple Feast Override | Accepts patronal override (`MM-DD`) and applies Dolnytsky feast elevation rules. Empty input must disable override cleanly (not pass `null` as string). | `[PENDING AUDIT]` |
| **A08** | `opt-include-ceremonial` | Sanctuary Rubrics Checkbox | Toggles priest/deacon sanctuary choreography inside booklet. Must not leak raw actor keys to UI (Anti-Pattern 3). | `[PENDING AUDIT]` |
| **A09** | `opt-digest-mode` | Full vs. Quick Radio | Toggles comprehensive vs. abbreviated digest layout. Abbreviated mode must never hide `NOT IMPLEMENTED` markers — must display fallback explicitly (Anti-Pattern 5). | `[PENDING AUDIT]` |
| **A10** | `chk-dev-mode` | Dev Tools Checkbox | Shows/hides Panel 4 (`trace-card` / debug logs). Must not expose raw engine keys to UI in release mode (Anti-Pattern 3). | `[PENDING AUDIT]` |
| **A11** | `opt-profile` / `btn-save-profile` | Parish Profile Manager | Persists/loads custom parish parameter bundles to localStorage. Must use versioned schema (e.g., `profile_schema_version`) and detect stale/corrupt profiles with explicit error toast. | `[PENDING AUDIT]` |

---

### Section B: Panel 1 — Liturgical Context Sidebar

| # | Element ID | Display Component | Verification Criteria | Status |
| :-: | :--- | :--- | :--- | :-: |
| **B01** | `context-spinner` | Loading Indicator | Visible during fetch, hidden on `finally` (both success AND error paths); must never remain stuck visible. | `[PENDING AUDIT]` |
| **B02** | `context-title` | Human Feast/Day Title | Formats clear feast header with date in human-readable form; must not render raw `paradigm_id` or date object. | `[PENDING AUDIT]` |
| **B03** | `badge-rank` | Dolnytsky Feast Rank Badge | Displays correct Rank (1 to 7) with color-coded badge; rank values must come from engine resolver, not hardcoded lookup in `main.js` (Anti-Pattern 1). | `[PENDING AUDIT]` |
| **B04** | `badge-tone` | Tone of the Week Badge | Displays Tone 1–8 with Octoechos mode info; must use `humanize_key()` or equivalent before rendering (Anti-Pattern 3). | `[PENDING AUDIT]` |
| **B05** | `badge-color` | Vestment Color Swatch | Renders canonical color swatch (`Gold`, `White`, `Red`, `Blue`, `Purple`, `Green`); swatch hex values must come from a single source of truth in CSS/JS constants, not scattered string literals. | `[PENDING AUDIT]` |
| **B06** | `badge-fasting` | Fasting Rule Badge | Renders `strict`, `wine/oil`, `fish`, or `fast-free` with tooltip citing canonical authority; tooltip text must be static UI text (not engine output) and must not mislabel fasting levels. | `[PENDING AUDIT]` |
| **B07** | `badge-prostrations` | Prostrations Rule | Displays `Allowed` vs. `Forbidden` with canonical reason; must never contradict fasting badge when both appear. | `[PENDING AUDIT]` |
| **B08** | `paradigm-id` | Canonical Paradigm Box | Displays active CASE number (e.g., `CASE_01_SUNDAY_SIMPLE`). **Verify exact ID against engine output** — do not assume the example is correct; capture actual value from a live resolve query. | `[PENDING AUDIT]` |
| **B09** | `service-types-list` | Service Combination Grid | Displays resolved service types (`Vespers`, `Matins`, `Liturgy`, `Hours`); must render human labels, not engine enum values. | `[PENDING AUDIT]` |

---

### Section C: Panel 2 — Cantor Service Booklet

| # | Element ID | Component | Verification Criteria | Status |
| :-: | :--- | :--- | :--- | :-: |
| **C01** | `booklet-content` | Chants & Propers Stream | Formats liturgical texts with drop caps, red rubrics, and bold verses; must map all engine text through `engine/text_db.py` resolution (Hub-Spoke Model, AGENTS.md Rule 7); no hardcoded translation strings (Anti-Pattern 1). | `[PENDING AUDIT]` |
| **C02** | `actor` tags | Actor Badges | Renders `[PRIEST]:`, `[DEACON]:`, `[CANTOR]:` with styled badges; badges must be semantic `<span>` or `<aria-label>` elements, not raw text strings containing brackets. | `[PENDING AUDIT]` |
| **C03** | `cross-icon` | Liturgical Crosses | Renders blessing crosses (`✚`) cleanly in gold/accent styling; must use Unicode `U+271A` (Heavy Greek Cross) not mixed fallback glyphs. | `[PENDING AUDIT]` |
| **C04** | `btn-copy-booklet` | Copy Booklet Text Button | Copies plaintext booklet to clipboard via `navigator.clipboard.writeText` with success/error toast notification; copy payload must exclude HTML markup and actor badge spans. | `[PENDING AUDIT]` |
| **C05** | `print-booklet-btn` | Print View Button | Opens print stylesheet (`@media print`) formatted for 8.5×11 booklet printing; must ensure Panel 3 and Panel 4 are hidden in print output. | `[PENDING AUDIT]` |
| **C06** | `btn-toggle-reference` | Toggle Reference Button | Opens/closes Panel 3 with animated split-view width transition; animation must respect `prefers-reduced-motion` and not break during rapid toggling (debounce if needed). | `[PENDING AUDIT]` |

---

### Section D: Panel 3 — Service Rubrics Digest (Unified Reference Panel)

| # | Element ID | Component | Verification Criteria | Status |
| :-: | :--- | :--- | :--- | :-: |
| **D01** | `service-digest-select` | Office Filter Dropdown | Switches between `All Services`, `General Info`, `Vespers`, `Matins`, `Liturgy`, `Hours`; filter must not mutate underlying digest data, only visibility. | `[PENDING AUDIT]` |
| **D02** | `service-digest-content` | Rubrics Card Renderer | Formats step-by-step liturgical rubrics inside glass cards with titles; must render all output through `humanize_key()` or engine text resolution (Anti-Pattern 3). | `[PENDING AUDIT]` |
| **D03** | `metadata-badge` | Section Vestment/Fasting | Renders office-specific vestment/fasting badges extracted from digest; badges must be scoped to active office filter, not global context. | `[PENDING AUDIT]` |
| **D04** | `btn-copy-digest` | Copy Rubrics Button | Copies full markdown digest when `All` is active, or selected office text when filtered; must include section headers but omit UI-only elements (badges, buttons). | `[PENDING AUDIT]` |
| **D05** | `btn-close-reference` | Close Drawer Button (`❌`) | Closes the panel and restores Panel 2 to full width (100%); keyboard accessible (Enter/Escape triggers same action); ARIA `aria-expanded` must update. | `[PENDING AUDIT]` |
| **D06** | `reference-resize` | Split Resize Drag Handle | Allows dragging to customize width ratio between Booklet and Digest; must have min/max width constraints to prevent collapse or overflow. | `[PENDING AUDIT]` |

---

### Section E: Navigation & Secondary Tabs

| # | Element ID | Component | Verification Criteria | Status |
| :-: | :--- | :--- | :--- | :-: |
| **E01** | `theme-toggle-btn` | Light / Dark Mode Toggle | Toggles `dark-theme` class on `<body>` and persists via `localStorage.theme_preference`; must default to `prefers-color-scheme` when no saved preference exists. | `[PENDING AUDIT]` |
| **E02** | `tab-browser` | Liturgical Book Browser | Searches all database keys in `engine/text_db.py`; displays standardized text diffs with `git --no-pager diff` style compatibility; must never expose raw `json_db` file paths in UI. | `[PENDING AUDIT]` |
| **E03** | `tab-roadmap` | Feast & Roadmap Tab | Generates interactive annual calendar feast timeline for active year; must use engine-computed Feast dates (not hardcoded Gregorian approximations); displays `[PASS]` only after full-year smoke test. | `[PENDING AUDIT]` |

---

## 4. Anti-Pattern Prevention Protocol (Must Accompany Each Fix)

Before applying any fix during this audit, verify the proposed change against **all 14 blacklisted anti-patterns** from `.agents/references/anti_patterns.md`:

| Anti-Pattern Category | Check Applied | Verification Command |
| :--- | :--- | :--- |
| 1. Hardcoded Strings | No raw liturgical text in `main.js` — must call engine resolver | `rg "append\\(\"|textContent = \"" cantor_dashboard/main.js` |
| 2. Bare `except: pass` | No silent swallow in dashboard JS or server.py | `rg "catch\\s*\\{[^}]*\\}|except:\\s*pass" cantor_dashboard/ server.py` |
| 3. Raw Keys in UI | No `Eothinon_`, `Tone_`, `righteous_memory` (unprocessed) in output paths | `rg "Eothinon_|Tone_\\d+|righteous_memory" cantor_dashboard/main.js` |
| 4. Vague Stubs | No generic "We sing the Aposticha" without resolution | Runtime test against `typikon_digest_generator.py` output for a resolved day |
| 5. `hasattr` Without Else | No hasattr guard without fallback branch in dashboard touchpoints | `rg "hasattr" cantor_dashboard/ server.py` |
| 6. Interactive Pager Locks | Use only `git --no-pager diff` or `$env:PAGER="cat"` | All commands in this plan already compliant |
| 7. Code Changes Without Tests | No dashboard file edit without adding/running a pytest assertion in `tests/test_server_endpoints.py` or `tests/test_session_compliance.py` | Run relevant pytest immediately after fix |
| 8–14. Behavioral Anti-Patterns | No fabricated progress, rationalizations, drift, momentum, retroactive context, authority conflation, or UI jargon neglect | Self-audit each session turn; paste evidence before claiming `[PASS]` |

---

## 5. Execution & Verification Workflow (Per Element)

```
  ┌───────────────────────────────────────────────────────┐
  │  STEP 1: Inspect Element                              │
  │  - Read markup (index.html)                           │
  │  -