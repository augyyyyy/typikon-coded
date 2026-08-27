<!-- [GENERATOR: Gemini 3.7 Flash] -->
# Granular Triage Plan: Wing 4 — Kyivan Musicology & MEI

## 1. Wing Identity & Scope
* **Wing Name**: Wing 4 (Kyivan Musicology, Chant Notation & MEI)
* **Codebase Location**: `Kyivan Musicology/` (Spoke) + `Typikon Coded/engine/resolvers/regional_chant.py`
* **Health Status**: **Decoupled to Kyivan Musicology Spoke to preserve Hub logic purity**.

---

## 2. Core Functional Scope
1. **Manuscript Codicological Database**:
   - 580 normalized manuscript records from the Yasinovsky Catalogue.
   - Dual-mirror cloud/offline repository (106,067 files, 167.64 GB).
2. **Music Encoding Initiative (MEI) Pipeline**:
   - Extracts 17th-century square-note neumatic notation structures into standardized MEI XML elements (`<meiHead>`, `<nc>`, `<syl>`).
3. **Melodic Assignment in Hub**:
   - Assigns 8-tone melodic models (Samopodobny, Irmoi, Prokeimena melodies) to dynamic slots.

---

## 3. Integration Interface
* **Handoff Directory**: `Typikon Coded/Data/Inbox/` (receives compiled MEI XML files and audio files).
* **Logging Protocol**: All manuscript compilations and MEI drops are recorded in `GLOBAL_ECOSYSTEM_STATE.md`.
