<!-- [GENERATOR: DeepSeek-V4-Pro] -->
# Onboarding & Granular Triage Plan: Propers Sourcer (`Festal Propers Comparisons` Spoke)

## 0. Document Authority & Compliance Statement
This plan is subordinate to `.agents/AGENTS.md` (the 12 Master Rules), `.agents/references/anti_patterns.md` (the blacklist of 7 code + 7 behavioral + 3 compliance-specific anti-patterns), and `.agents/references/liturgical_authority.md` (UGCC Royal Doors terminology standards). Any conflict between this plan and those references resolves in favor of the references.

All verification commands in this plan use non-interactive modes (`$env:PAGER="cat"`, `git --no-pager`) to comply with Anti-Patterns 6 and 17 (Interactive Pager Locks). No claim of completion is valid without pasted terminal output per Honor Protocol and Evidence Gate (Master Rule 6).

---

## 1. Spoke Identity & Architectural Role
- **Project Name**: `Festal Propers Comparisons` (UI Display Title: `Propers Sourcer`)
- **Physical Location**: `C:\Users\augus\OneDrive\Documents\Google Antigravity\Projects\Festal Propers Comparisons`
- **Architectural Role in Ecosystem**: Multi-Recension Hymnographic Comparison, Translation Alignment, and Propers Extraction Factory (Wing 3 Ingestion Engine).
- **Source Code Path Resolution Rule (Master Rule 10)**: All scripts MUST resolve paths dynamically relative to the Spoke project root (`Festal Propers Comparisons/`). The absolute path above is informational only and MUST NOT be hardcoded in any script.

---

## 2. Granular Corpus & Recension Database Inventory
The Propers Sourcer manages and cross-examines 7 distinct textual recension corpora:

| Recension Corpus | JSON Asset File | Source Description & Authority Level |
| :--- | :--- | :--- |
| **Royal Doors (Primary)** | `text_royaldoors.json`<br>`text_royaldoors_old.json` | Modern Ukrainian Greek Catholic Church (UGCC) English standard. Primary lookup database (`primary_db`). Curated under Royal Doors Vocabulary Standards. |
| **Stamford Printed (Backup)** | `text_stamford.json` | 2014 Stamford Divine Office printed edition. Comprehensive backup database (`backup_db`) providing full propers coverage. |
| **Stamford Web Corpus** | `text_stamford_web.json` | Online parish publication corpus used for tracking regional translation drift and editorial divergence. |
| **Sheptytsky Institute** | `text_sheptytsky.json` | Metropolitan Andrey Sheptytsky Institute (Ottawa) scholarly English translations of the Octoechos and Festal services. |
| **Byzantine Daily Worship (BDW)** | `text_bdw.json` | Archbishop Joseph Raya & Baron José de Vinck (1969) historical English liturgical translation. |
| **St. Sergius Monastic** | `text_st_sergius.json` | Russian Orthodox Monastic Tone 1 unabridged propers overlay. |
| **Father Paul Propers** | `father_paul_propers_options_report.md` | Pastoral propers variants and cantor performance options. |

**Primary-Backup Architecture (Hub Rule 3)**: Royal Doors is primary; Stamford Printed is fallback. St. Sergius and Father Paul are context-requested overlays with highest priority. Never fabricate missing propers — resolve through fallback chain or return a clean missing placeholder stub.

---

## 3. UGCC Royal Doors Terminology Enforcement Matrix
All JSON keys, values, and user-facing text MUST conform to the following canonical terminology map. No variant, custom, or transliterated term may be introduced.

| Canonical UGCC Term | Plural / Derived Form | Banned / Rejected Synonyms | Usage Context |
| :--- | :--- | :--- | :--- |
| **Sessional Hymn** | Sessional Hymns | Sedalion, Sessional, Kathisma Hymn | After Ode III of the Canon and after Psalm 50 at Matins |
| **Prokeimenon** | Prokeimena | Prokimen, Prokimenon, Prokimenon | Before Scripture readings at Vespers/Matins |
| **Irmos** | Irmoi | Irmosy, Heirmos, Hirmos | Opening stanza of each of the 9 Canon Odes |
| **Exapostilarion** | Exapostilaria | Exapostilario, Photagogikon, Svetilen | After Ode 9 of the Canon |
| **Sticheron** | Stichera | Stickheron, Stikhera, Stichiron | At "Lord, I Have Cried," Aposticha, Praises |
| **Aposticha** | — | Apostichon, Apostikhon | Stichera at end of Vespers |
| **Theotokion** | Theotokia | Theotokarion, Bogorodichen | Dedicated to the Theotokos |
| **Kontakion** | Kontakia | Kondakion, Kondak | After Ode 6 of the Canon |
| **Troparion** | Troparia | Troparyon, Tropar | Opening, Apolytikion, Dismissal |
| **Ode** | Odes (1–9) | Canticle (when referring to Canon Odes) | Canon structure |

**Enforcement Protocols**:
1. The scripts `scripts/deepseek_propers_auditor.py` and `scripts/compile_festal_propers_25_feasts.py` MUST emit a warning and refuse to write output if any banned term is detected in source content.
2. Onboarding agents MUST run the terminology guard (see §7 Verification Commands, item C) before every JSON export.
3. The `royaldoors_vocabulary_matrix.md` and `standardized_liturgical_vocabulary.json` files are the authoritative terminology dictionary for the entire Hub & Spoke ecosystem. Any proposed new term MUST be approved against these files before introduction.

**Flat Key Constraint (Schema)**: All JSON asset keys must match the pattern `^[a-z0-9_]+(\.[a-z0-9_]+){1,5}$` — i.e., 1 to 5 dot-separated lowercase segments composed of `a-z`, `0-9`, and underscore. No uppercase, spaces, hyphens, or LaTeX notation.

---

## 4. Anti-Pattern Audit Status (Pre-Flight)
The following anti-pattern categories are reviewed against this onboarding plan and its associated scripts:

| Anti-Pattern ID | Category | Status in This Plan | Mitigation Required |
| :--- | :--- | :--- | :--- |
| AP-1 | Hardcoded strings instead of resolved output | **PASS** | The Spoke exports flat-key JSON assets; no hardcoded liturgical strings in engine code. |
| AP-2 | Bare `except: pass` | **PASS** | All Spoke scripts must wrap errors with explicit handlers returning `[SCRIPT ERROR: ...]`. No silent suppresses. |
| AP-3 | Raw internal keys leaked to UI | **PASS** | JSON keys are machine data structures handed to the Hub engine; UI transcription is Hub-side. |
| AP-4 | Vague stubs disguised as implementations | **PASS** | The Spoke delivers complete propers, not placeholder stubs. |
| AP-5 | `hasattr` guard hiding missing methods | **PASS** | Spoke scripts do not introspect Hub engine methods; they emit flat assets. |
| AP-6 | Interactive terminal locking | **PASS (enforced)** | All git commands use `git --no-pager` or `$env:PAGER="cat"`. |
| AP-7 | Code changes without tests | **PASS (enforced)** | Any modification to Spoke scripts MUST include a pytest run before export (see §8 Post-Flight). |
| AP-8 | Fabricated progress narratives | **PASS (enforced)** | Deliverable metrics in §5 are marked as **prior-audit baselines requiring re-verification**. |
| AP-9 | Post-hoc rationalizations | **PASS** | No speculative justifications allowed. Run direct commands to investigate (Master Rule 5). |
| AP-10 | Exploratory drift | **PASS** | Onboarding scope is strictly limited to Spoke triage and integration tasks. |
| AP-11 | Agreeable momentum | **PASS** | Contradictions with Ordo Celebrationis / Dolnytsky hierarchy must be raised immediately. |
| AP-12 | Retroactive context fabrication | **PASS** | Session history is archived to `.agents/brain/session_history/<date>/`. |
| AP-13 | Liturgical authority conflation | **PASS (enforced)** | Only UGCC/Royal Doors terminology is permitted. No Russian/Greek custom terms. |
| AP-14 | UI robot jargon neglect | **PASS** | Export keys are pure machine tokens; human-readable UI text is generated by the Hub. |
| AP-15 | Pre-flight checklist neglect | **PASS (enforced)** | The full pre-flight checklist is embedded in §7 item A. |
| AP-16 | Banned phrase infestation (empty claims) | **PASS (enforced)** | No passing claim without pasted pytest output. |
| AP-17 | Interactive pager locks | **PASS (enforced)** | Duplicate enforcement of AP-6. |

---

## 5. Tooling, Automated Auditing & Deliverables

### 5.1 Key Python Tooling
1. **`scripts/compile_festal_propers_25_feasts.py`**:
   - Parses, aligns, and compiles variable propers (Troparia, Kontakia