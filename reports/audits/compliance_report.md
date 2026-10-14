### *** Typikon Compliance Gate Report ***

**Test Suite Result:** `========================= 336 passed`
**Files Changed:** 45

#### Git Diff Summary:
```
.agents/brain/AGENT_STARTUP_CONTEXT.md    |   6 +-
 .agents/brain/PROJECT_STATE.json          |  11 +-
 .agents/brain/project_brainprint.md       |  14 +-
 .ai/learnings.md                         | 210 ++++++++
 .cursorrules                             |  16 +
 Digest_2026-02-01.md                     |  12 +-
 compliance_report.md                     | 137 ++---
 digest/formatters/common.py              |   3 +-
 engine/core.py                           |   2 +
 engine/generation.py                     | 721 ++++++++++++++++++++++++-
 engine/resolver_registry.py              |  10 +
 engine/resolvers/ceremonial.py           |   4 +-
 engine/resolvers/liturgy.py              |  84 ++-
 engine/resolvers/matins.py               |  46 +-
 engine/resolvers/vespers.py              |  28 +-
 engine/rubrics.py                        |  12 +-
 engine/text_db.py                        |  26 +
 json_db/02a_logic_general.json           |   6 +-
 json_db/02b_02_october.json              |  44 ++
 json_db/02b_03_november.json             |   6 +
 json_db/02b_04_december.json             |  19 +
 json_db/02b_05_january.json              |  84 +++
 json_db/02b_06_february.json             |   8 +
 json_db/02b_07_march.json                |  15 +
 json_db/02b_09_may.json                  |  24 +
 json_db/02b_11_july.json                 |  13 +
 json_db/02b_12_august.json               |  14 +
 json_db/almanac/annual_almanac_2026.json | 898 +++++++++++++++----------------
 scripts/audit_all_days_heuristics.py     |  85 +--
 scripts/audit_january.py                 |  45 +-
 scripts/compliance_gate.py               |   4 +-
 tests/test_annual_almanac_consistency.py |  17 +
 tests/test_horologion_core.py            |   9 +-
 tests/test_semantic_linting.py           |  90 ++++
 34 files changed, 2073 insertions(+), 650 deletions(-)
```

#### [WARNING] Compliance Violations:
- engine/generation.py:120 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:585 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:666 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:905 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:995 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:1105 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:1770 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:1890 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/resolvers/liturgy.py:208 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/resolvers/matins.py:581 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/resolvers/matins.py:1410 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/resolvers/vespers.py:777 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/resolvers/vespers.py:972 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/rubrics.py:1014 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/rubrics.py:1185 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/text_db.py:165 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/text_db.py:173 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/text_db.py:426 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- scripts/run_liturgical_audit_pipeline.py:203 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- scripts/run_liturgical_audit_pipeline.py:335 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- tests/test_musical_mode_coherence.py:115 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- tests/test_resolver_outputs_compliance.py:74 - Potential 'hasattr' guard check (ensure else branch is provided or documented).

#### Sample Digest Preview (First 30 Lines):
```markdown
# TYPICON: SUNDAY, FEBRUARY 1st, 2026.

FOREFEAST OF THE MEETING - TONE I.
Sunday service combined with that of the Triodion, and that of the forefeast.
The service to Martyr Tryphon is transferred to the previous Friday at Compline, or another convenient time, whenever the ecclesiarch so wishes.
Vestment colour: Bright (Gold or blue for the forefeast).

## GREAT VESPERS

Fasting Rule: Fast-free week, no fasting restrictions.
*At Lord, I Call…* we sing 4 Resurrectional Stichera from the Octoechos, 3 Stichera from the Triodion, and 3 Forefeast Stichera from the Menaion; Glory... doxastikon from the Triodion; Both now: Dogmatic Theotokion in the tone of the week.
<span class="rubric">Prokeimenon of Saturday Evening (Sunday prep), Tone VI:</span> <span class="sung-text">"The Lord reigns, He is clothed in majesty"</span>
<blockquote class="verse"><span class="rubric">Stichos:</span> <span class="sung-text">Robed is the Lord and girt about with strength.</span></blockquote>
<blockquote class="verse"><span class="rubric">Stichos:</span> <span class="sung-text">For He has made the world firm, which shall not be moved.</span></blockquote>
<blockquote class="verse"><span class="rubric">Stichos:</span> <span class="sung-text">Holiness befits Your house, O Lord, for length of days.</span></blockquote>
**At the Aposticha:** We sing the resurrectional aposticha in the tone of the week, from the Octoechos; Glory... doxastikon from the Triodion; Both now: doxastikon of the forefeast.
**At the Dismissal Troparia:** We sing the Sunday (resurrectional) troparion in the tone of the week; Glory, Both now: Theotokion.

## SMALL COMPLINE

Canon: Canon Forefeast from the Menaion.
Troparia: Sunday Troparion from the Octoechos, Troparion of the Temple, *"O God of our fathers..."* and the following three troparia.

## MIDNIGHT OFFICE (SUNDAY)

Triadic Canon: Canon Trinity in Tone 1.
Midnight Troparia: Sunday Hypakoe in Tone 1.
Prayer: Prayer Holy Trinity All Creating.

## SUNDAY MATINS
```