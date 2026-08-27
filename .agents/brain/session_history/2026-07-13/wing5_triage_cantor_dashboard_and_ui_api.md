<!-- [GENERATOR: Gemini 3.7 Flash] -->
# Granular Triage Plan: Wing 5 — Cantor Dashboard & UI API

## 1. Wing Identity & Scope
* **Wing Name**: Wing 5 (Cantor Dashboard, Server API & Digest Generator)
* **Codebase Location**: `Typikon Coded/cantor_dashboard/` (`server.py`, `main.js`, `index.html`, `styles.css`) + `typikon_digest_generator.py`
* **Health Status**: **Operational; Enhanced with calendar switching and SSE status**.

---

## 2. Core Frontend & API Architecture
1. **Cantor Dashboard Frontend**:
   - High-contrast, responsive glassmorphic web interface for parish cantors and priests.
   - Dynamic service booklet viewer and roadmap visualizer.
2. **Backend Server API (`cantor_dashboard/server.py`)**:
   - Python `ThreadingTCPServer` exposing `/api/resolve`, `/api/roadmap`, `/api/books`, `/api/text`, `/api/lint`.
   - Supports dynamic query parameters: `date`, `version`, `calendar_source`, `paschalion`.
3. **Typikon Digest Generator (`typikon_digest_generator.py`)**:
   - Formats full liturgical booklets and quick-reference digests with liturgical styling ("Say the Black, Do the Red", gold blockquotes, pill badges).

---

## 3. Strict UI Invariants
* **Zero Programmer Jargon**: No raw labels like "Active: True" or "Max: 9"; all badges use clean liturgical English.
* **Non-Destructive DOM**: No `parent.innerHTML = ""` calls on shared reference panes.

---

## 4. Verification Checklist
- Run server endpoint tests:
  ```powershell
  .venv\Scripts\python -m pytest tests/test_server_endpoints.py
  ```
- Run booklet rendering tests:
  ```powershell
  .venv\Scripts\python -m pytest tests/test_booklet_rendering.py
  ```
