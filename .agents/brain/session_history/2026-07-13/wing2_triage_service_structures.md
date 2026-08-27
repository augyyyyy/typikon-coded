<!-- [GENERATOR: Gemini 3.7 Flash] -->
# Granular Triage Plan: Wing 2 — Service Structures & Choreography

## 1. Wing Identity & Scope
* **Wing Name**: Wing 2 (Service Structures & Choreography)
* **Codebase Location**: `Typikon Coded/json_db/01*_struct_*.json` (11 core service structure skeletons) + `schemas/service_structure.schema.json`
* **Health Status**: **100% Schema Validated & Wired**.

---

## 2. Core Service Skeletons
1. **Vespers Cycle**: `01a_struct_small_vespers.json`, `01b_struct_great_vespers.json`, `01c_struct_daily_vespers.json`.
2. **Matins Cycle**: `01d_struct_festal_matins.json`, `01e_struct_sunday_matins.json`, `01f_struct_daily_matins.json`.
3. **Daily Canonical Hours**: `01g_struct_midnight.json`, `01h_struct_compline.json`, `01i_struct_hours.json`.
4. **Liturgical Assemblies**: `01j_struct_liturgy.json`, `01k_struct_presanctified.json`, `01l_struct_royal_hours.json`.

---

## 3. Liturgical Choreography & Ordo Celebrationis Rules
* **Physical Postures & Routes**: Encodes opening and closing of Holy Doors, curtain movements, Great and Small Censing paths, and bow/prostration categories (Metania, Proskynesis).
* **Slot-Resolver Binding**: Every dynamic item (`is_variable: true`) binds to a registered resolver in Wing 1.

---

## 4. Verification Checklist
- Run structural schema validation:
  ```powershell
  .venv\Scripts\python tests/validate_schemas.py
  ```
- Run choreography test suite:
  ```powershell
  .venv\Scripts\python -m pytest tests/test_ordo_vespers_choreography.py tests/test_ordo_remaining_choreography.py
  ```
