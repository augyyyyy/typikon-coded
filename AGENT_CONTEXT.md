# Agent Context: Project Memory Map

> **READ THIS FIRST** - This file contains everything an AI model needs to continue work on this project without losing context.

## Quick Start Checklist

1. Read `PROJECT_STATE.json` for active tasks and implementation plans
2. Check `known_issues` array for current bugs
3. Read `context_for_next_session` field for urgent notes
4. Review recent git commits: `git log --oneline -10`

---

## Project Identity

| Field | Value |
|-------|-------|
| **Name** | Ruthenian Typikon Logic Engine |
| **Purpose** | Automate Byzantine liturgical service generation |
| **Primary Source** | Dolnytsky's Typikon (1899) |
| **Language** | Python 3.x |
| **Architecture** | Logic-First (JSON rules + Python engine) |

---

## File Map (What's Where)

### Core Engine
| File | Purpose |
|------|---------|
| `ruthenian_engine.py` | Main logic engine (4300+ lines) |
| `generate_my_service.py` | CLI entry point |

### Logic Layers (`json_db/`)
| Pattern | Purpose |
|---------|---------|
| `01*_struct_*.json` | Service structure definitions |
| `02*_logic_*.json` | Logic rules (paradigms, collisions) |
| `03*_text_*.json` | Text content |

### Source Texts (`Data/Service Books/`)
| Path | Content |
|------|---------|
| `Typikon/dolnytsky_part*.txt` | Primary source (7 parts + footnotes) |
| `Services/MATINS.txt` | Comprehensive matins layout |
| `Services/Resolves/*.txt` | Service-specific resolve files |

### Documentation (`docs/`)
| File | Status |
|------|--------|
| `encyclopedia_matins_hooks.md` | Gate 5 needs fix |
| `encyclopedia_sidalen_logic.md` | Line 181 has "presumably" |
| `encyclopedia_repetition_logic.md` | Needs hymn counts |
| `encyclopedia_proposed_topics.md` | 18 topics to audit |

### Schemas (`schemas/`)
| Schema | Validates |
|--------|-----------|
| `text_asset.schema.json` | Text JSON files |
| `service_structure.schema.json` | Structure JSON files |
| `project_context.schema.json` | PROJECT_STATE.json |

---

## Current State Summary

**Active Work**: Encyclopedia Documentation Reconciliation (7 phases, ~120 hours)

**Known Bugs**:
1. `matins_logic_audit.md` - Summary contradicts details
2. Gate 5 - Hypakoe/Anabathmoi shown as alternatives (should be sequential)
3. Missing functions - `resolve_anabathmoi()`, `resolve_hypakoe()`

**Recent Milestones**:
- 2026-01-31: 13/13 Matins Gates (core), Schema Governance, Stamford ingestion

---

## Key Decisions (Immutable)

1. **Logic-First Architecture** - Rules in JSON, engine interprets
2. **20 Paradigm System** - Dolnytsky's feast ranking hierarchy
3. **Hypakoe THEN Anabathmoi** - Sequential, not exclusive (Part I Line 159)
4. **All docs must cite Dolnytsky line numbers** - No vague language

---

## Persistence Protocol

> **CRITICAL**: To prevent loss of work:

1. **Save plans immediately** - Write to `PROJECT_STATE.json`
2. **Commit often** - `git add PROJECT_STATE.json && git commit -m "update state"`
3. **Update this file** - Add new decisions, change status
4. **Never leave plans in chat only** - Always persist to disk

---

## Validation Commands

```bash
# Validate schemas
python tests/validate_schemas.py

# Run matins tests  
python -m pytest test_matins_*.py -v

# Check Dolnytsky implementation
python stress_test_dolnytsky.py
```

---

## Session Handoff Template

When ending a session, update `PROJECT_STATE.json`:
```json
{
  "context_for_next_session": "Describe exactly where you left off..."
}
```
