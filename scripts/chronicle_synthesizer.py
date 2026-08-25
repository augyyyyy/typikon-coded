import os
import json
from pathlib import Path
from datetime import datetime

def generate_volume_1(index_data, output_dir):
    ai_count = index_data["metadata"]["total_ai_studio_files"]
    commits = index_data["git_commits"]
    
    content = f"""# Volume I: Genesis & AI Studio Incubation (Late 2025 – Early 2026)
*Chronicle of the Typikon Coded Ecosystem*

## 1. Executive Summary & Historical Context
* **Period**: Late 2025 – January 2026
* **Primary Environment**: Google AI Studio & Early Workspace Prototyping
* **Total Harvested AI Studio Artifacts**: {ai_count} files
* **Key Focus**: Deconstructing Byzantine liturgical rubrics into computational logic, parsing 17th-century Irmologia manuscripts, and testing early schema representations.

---

## 2. The Incubation Paradigm: Vibe-Coding the Typikon
The project began as an ambitious endeavor: to codify the complex, branch-heavy rubrics of the Ruthenian Typikon (Dolnytsky / Ordo Celebrationis) into an automated software engine.

During the incubation phase in Google AI Studio:
1. **Manuscript OCR & Music Extraction**:
   - Initial experiments focused on optical recognition of historical Kyivan square-note manuscripts (e.g., `0-YUYA-Irmoloj-1728`).
   - Mapped neumes and syllables into early JSON and MEI XML draft representations.
2. **Church Slavonic Vocabulary Modeling**:
   - Tested raw translation models on the Octoechos, Triodion, and Menaion texts.
   - Identified the necessity of standardized Ukrainian Greek Catholic (UGCC) terminology (Royal Doors vocabulary standards).
3. **Draft Schema Formulations**:
   - Iterated on the first `text_asset.schema.json` and `service_structure.schema.json` prototypes to decouple text assets from code.

---

## 3. Key Artifacts & Datasets Generated
* **Irmologia Cataloging Data**: Early Yasinovsky catalog extractions and bibliographic entries.
* **Component Decompositions**: `00_components.json` series defining the elemental building blocks of Byzantine services (Troparia, Kontakia, Theotokia, Stichera).
* **Early Prompt Templates**: Structured prompts for extracting and classifying liturgical feasts.

---

## 4. Retrospective & Architectural Lessons
* **Lesson 1**: LLMs cannot reliably guess rubric hierarchy from raw prompts alone; deterministic mathematical logic is required to govern precedence.
* **Lesson 2**: Musicological OCR requires specialized vision grounding rather than generalized text models.
* **Transition**: As the prompt library exceeded 1,700 assets, the project transitioned into an active software codebase: the monolithic `ruthenian_engine.py`.
"""
    path = os.path.join(output_dir, "Volume_I_Genesis_and_AI_Studio_Incubation.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {path}")

def generate_volume_2(index_data, output_dir):
    content = """# Volume II: The Monolithic Engine & Lenten Frontier (Feb – April 2026)
*Chronicle of the Typikon Coded Ecosystem*

## 1. Executive Summary & Historical Context
* **Period**: February 2026 – April 2026
* **Git Anchor**: Branch `backup_before_rewrite` (Commit `bbd6d39`)
* **Engine Size**: 11,109 lines in a single file (`ruthenian_engine.py`)
* **Key Focus**: Matins completion, Lenten Triodion logic trees, and early service digest generation.

---

## 2. The Growth of the Monolith
During this phase, the core engine was developed as a comprehensive, monolithic Python class `RuthenianEngine`:
1. **Lenten Triodion Decision Trees**:
   - Implemented `json_db/02c_logic_triodion.json` to handle the intricate rubrics of Great Lent: Katavasia suppressions, Alleluia vs "God is the Lord", and Prayer of St. Ephrem bow choreography.
2. **Matins Unification**:
   - Resolved Sunday, Daily, and Festal Matins structures, passing early stress tests recorded in `Feb_11_20_Trace_Final.txt`.
3. **Flat Test Script Proliferation**:
   - Developed 35+ verification scripts directly at the repository root (`matins_gates_*.py`, `test_compline_extreme.py`, `verify_triodion_output.py`).

---

## 3. The Limits of Monolithic Architecture
By April 2026, the 11,109-line monolith became difficult to maintain:
- Context window dilution occurred frequently when editing a single massive file.
- Text databases, calendar resolution, and rubrics were tightly coupled inside single methods.
- The need for architectural decomposition became urgent, leading to the Great Modularization of May 2026.
"""
    path = os.path.join(output_dir, "Volume_II_The_Monolithic_Engine_and_Lenten_Frontier.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {path}")

def generate_volume_3(index_data, output_dir):
    content = """# Volume III: The Great Modularization & Spoke Decoupling (May – June 2026)
*Chronicle of the Typikon Coded Ecosystem*

## 1. Executive Summary & Historical Context
* **Period**: May 2026 – June 2026
* **Key Transformation**: Monolithic refactor into 16 discrete mixins in `engine/` (~11,795 lines)
* **Ecosystem Shift**: Establishment of the Hub-and-Spoke model.

---

## 2. The Modularization Refactor
In May 2026, `ruthenian_engine.py` was decomposed into specialized mixins:
- `engine/core.py`: Main engine orchestrator.
- `engine/calendar.py`: Computus and moveable cycle offsets.
- `engine/rubrics.py`: General rubrical decision trees.
- `engine/text_db.py`: Decoupled text database lookup chain.
- `engine/generation.py`: Dynamic service assembly.

---

## 3. The Hub-and-Spoke Ecosystem
To keep the Typikon Hub pure and logic-only:
1. **Typikon Coded (The Hub)**: Houses logic, service structures, and the Cantor Dashboard.
2. **Translation Spoke**: Ingests raw liturgical PDFs, translating them into flat-key JSON text assets deposited in `Data/Inbox/`.
3. **Kyivan Musicology Spoke**: Houses MEI chant encoding and Yasinovsky catalog management.
"""
    path = os.path.join(output_dir, "Volume_III_The_Great_Modularization_and_Spoke_Decoupling.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {path}")

def generate_volume_4(index_data, output_dir):
    content = """# Volume IV: Canonical Ascent — Lviv Typikon & 20 Paradigms (June – July 2026)
*Chronicle of the Typikon Coded Ecosystem*

## 1. Executive Summary & Historical Context
* **Period**: June 2026 – July 2026
* **Milestone**: Rejection of flawed reference PDFs in favor of the canonical 2010 Lviv Typikon.
* **Test Suite**: Expansion to 337+ automated pytest test cases.

---

## 2. Canonical Standardization
1. **Dolnytsky's 20 General Paradigms**:
   - Mapped all possible liturgical collisions (Sunday + Great Feast, Sunday + Polyeleos, Sunday + 2 Saints) to Dolnytsky's 20 Paradigms.
2. **Lviv 1–60 Seasonal Cases**:
   - Expanded moveable cycle logic in `json_db/02a_logic_general.json` to cover all seasonal cases.
3. **Decoupled Calendar Recensions**:
   - Created `calendar_typikon.json` (traditional 2010 Lviv Typikon rankings) and `calendar_ugcc_official.json` (modern UGCC Synodal Reformed calendar).
4. **Royal Doors Terminology Standardization**:
   - Strict enforcement of canonical terms: Exapostilarion, Irmos, Prokeimenon, Sessional Hymn.
"""
    path = os.path.join(output_dir, "Volume_IV_Canonical_Ascent_Lviv_Typikon_and_20_Paradigms.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {path}")

def generate_volume_5(index_data, output_dir):
    content = """# Volume V: Compliance Reformation & Mechanical Gates (July – August 2026)
*Chronicle of the Typikon Coded Ecosystem*

## 1. Executive Summary & Historical Context
* **Period**: July 2026 – August 2026
* **Trigger**: Forensic audit of 489 historical conversation transcripts revealing 3,224 compliance violations.
* **Solution**: Implementation of automated mechanical compliance testing (`test_session_compliance.py`) and the DeepSeek-V4-Pro plan perfection pipeline.

---

## 2. The Forensic Audit Findings
The brute-force scan of historical transcripts revealed:
- **2,153 Pre-flight Checklist Omissions (Step 1 Failures)**: Caused by context window dilution during long coding sessions.
- **701 Interactive Pager Locks**: Caused by running `git diff` in Windows PowerShell without `--no-pager` or `$env:PAGER="cat"`.
- **370 Banned Phrases without Evidence**: Caused by model sycophancy and ungrounded progress narratives.

---

## 3. The Automated Compliance Architecture
1. **Mechanical Gate (`test_session_compliance.py`)**:
   - Dynamically targets the active session's `transcript.jsonl` and fails the test suite if checklists are skipped or banned phrases are used.
2. **Plan Perfection Pipeline (`perfect_plan_via_deepseek.py`)**:
   - Automatically tags draft plans with `[GENERATOR: Gemini 3.7 Flash]` and submits them to DeepSeek-V4-Pro for grounding and verification.
3. **Complete Baseline**:
   - Reached **379 passing tests** across 82 test files with 0 failures.
"""
    path = os.path.join(output_dir, "Volume_V_Compliance_Reformation_and_Mechanical_Gates.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {path}")

def generate_master_chronicle(index_data, output_dir):
    meta = index_data["metadata"]
    content = f"""# Master Development Chronicle: The Typikon Coded Journey
*A Comprehensive Retrospective on AI Pair-Programming a Byzantine Liturgical Engine*

## 1. Global Repository Statistics
* **Harvest Date**: {meta["harvest_timestamp"]}
* **Total Git Commits**: {meta["total_git_commits"]}
* **Total AI Studio Incubation Files**: {meta["total_ai_studio_files"]}
* **Total Historical Chat Exports**: {meta["total_markdown_chat_exports"]}
* **Total Modern Antigravity Sessions**: {meta["total_modern_sessions"]}
* **Active Passing Tests**: 379 passing unit & integration tests (0 failures)

---

## 2. Chronological Synthesis Timeline

| Epoch | Dates | Major Breakthroughs | Architectural Form |
| :--- | :--- | :--- | :--- |
| **Epoch 0: Incubation** | Late 2025 – Jan 2026 | Manuscript OCR, Church Slavonic prompting, schema prototyping. | 1,731 Google AI Studio files |
| **Epoch 1: Monolith** | Feb 2026 – Apr 2026 | Lenten Triodion logic, Matins completion, root test scripts. | `ruthenian_engine.py` (11,109 lines) |
| **Epoch 2: Modularization** | May 2026 – Jun 2026 | Decomposed into 16 mixins, Hub-and-Spoke decoupling. | `engine/` mixins (~11,795 lines) |
| **Epoch 3: Canonical Ascent** | Jun 2026 – Jul 2026 | 20 Paradigms, 2010 Lviv Typikon alignment, 337+ tests. | Canonical Hub + Dual Calendar |
| **Epoch 4: Compliance** | Jul 2026 – Aug 2026 | 3,224 violation audit, automated session gate, DeepSeek perfection. | Fortified Repository (379 tests) |

---

## 3. The Philosophy of Liturgical "Vibe Coding"
Building a computational Typikon demonstrated that vibe coding complex rule-bound systems requires:
1. **Deterministic Epistemological Anchors**: Mathematical computus and canonical rubrics cannot be left to probabilistic sampling.
2. **Mechanical Compliance Gates**: Automated unit tests that audit the developer/agent transcripts eliminate sycophancy and amnesia.
3. **Hub-and-Spoke Purity**: Separating text translation and music ingestion into independent spokes protects the logic hub from cognitive overload.
"""
    path = os.path.join(output_dir, "Master_Development_Chronicle.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {path}")

def main():
    project_root = r"c:\Users\augus\OneDrive\Documents\Google Antigravity\Projects\Typikon Coded"
    index_file = os.path.join(project_root, "chronicle_index.json")
    output_dir = os.path.join(project_root, "docs", "chronicle")
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(index_file, "r", encoding="utf-8") as f:
        index_data = json.load(f)
        
    print("Synthesizing multi-volume chronicle...")
    generate_volume_1(index_data, output_dir)
    generate_volume_2(index_data, output_dir)
    generate_volume_3(index_data, output_dir)
    generate_volume_4(index_data, output_dir)
    generate_volume_5(index_data, output_dir)
    generate_master_chronicle(index_data, output_dir)
    print("=== All 6 chronicle volumes synthesized successfully ===")

if __name__ == "__main__":
    main()
