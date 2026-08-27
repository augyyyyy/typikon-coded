<!-- [GENERATOR: Gemini 3.7 Flash] -->
# Granular Triage Plan: Wing 1 — Core Logic Engine & Computus

## 1. Wing Identity & Scope
* **Wing Name**: Wing 1 (Core Logic Engine & Computus)
* **Codebase Location**: `Typikon Coded/engine/` (20 Python files, 16,163 LOC) + `typikon_digest_generator.py`
* **Health Status**: **100% Verified (379/379 tests passing)**.

---

## 2. Core Functional Components
1. **The Computus Engine (`engine/calendar.py`)**:
   - Gauss, Meeus, and Oudin Paschalion algorithms calculating Easter distance $\Delta_{\text{pascha}} \in [-70, +56]$ and Octoechos mode $\omega \in \{1..8\}$.
   - Dual calendar models: Traditional 2010 Lviv Typikon Part V (`calendar_typikon.json`) vs UGCC Synodal Reformed Calendar (`calendar_ugcc_official.json`).
2. **Dolnytsky 20 Paradigms & 60 Lviv Seasonal Cases (`engine/rubrics.py`, `02a_logic_general.json`)**:
   - Classifies all Sunday, Weekday, and Feast collisions into 20 exhaustive General Paradigms.
   - Enforces mathematical constraints on Matins Praises ($\Sigma \le 8$) and Canon Ode interleaving ($\Sigma \le 14$).
3. **Dynamic Slot Resolvers (`engine/resolvers/`)**:
   - 224 dynamic `resolve_` methods resolving variable liturgical components (Prokeimena, Troparia, Kontakia, Stichera, Theotokia, Readings, Litanies).

---

## 3. Strict Invariants & Precedence
* **Canonical Hierarchy**: Ordo Celebrationis 1944 (Choreography) > Dolnytsky Parts II–V (Propers) > Liturgicon > Dolnytsky Part I.
* **Hub Purity**: Zero hardcoded translation strings or raw database keys in engine logic.

---

## 4. Verification Checklist
- Run full pytest test suite:
  ```powershell
  .venv\Scripts\python -m pytest --ignore=tests/test_ui_readability.py
  ```
- Assert: 379 tests pass with 0 failures.
