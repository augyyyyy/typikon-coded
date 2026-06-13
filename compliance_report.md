### *** Typikon Compliance Gate Report ***

**Test Suite Result:** `========================= 317 passed`
**Files Changed:** 43

#### Git Diff Summary:
```
.ai/learnings.md                         |    67 +
 .cursorrules                             |    26 +-
 Digest_2026-02-01.md                     |   101 +-
 Digest_2026-06-11.md                     |    20 +-
 Digest_2026-06-24.md                     |    31 +-
 cantor_dashboard/index.html              |     4 +
 cantor_dashboard/main.js                 |   440 +-
 cantor_dashboard/style.css               |   105 +-
 compliance_report.md                     |   130 +-
 digest/base.py                           |    67 +-
 digest/formatters/common.py              |     6 +-
 digest/formatters/compline.py            |     5 +-
 digest/formatters/matins.py              |     4 +-
 engine/calendar.py                       |   222 +-
 engine/core.py                           |     1 +
 engine/generation.py                     |    21 +-
 engine/resolvers/ceremonial.py           |    16 +
 engine/resolvers/common.py               |     7 +
 engine/resolvers/hours.py                |    28 +-
 engine/resolvers/liturgy.py              |   164 +-
 engine/resolvers/matins.py               |    26 +-
 engine/resolvers/vespers.py              |    47 +-
 engine/rubrics.py                        |    55 +-
 engine/text_db.py                        |    11 +
 json_db/01g_struct_midnight.json         |    14 +
 json_db/02a_logic_general.json           |     4 +-
 json_db/02c_logic_triodion.json          |    14 +-
 json_db/almanac/annual_almanac_2026.json | 10363 +++++++++++++++++------------
 json_db/calendar_dolnytsky.json          |     2 +-
 json_db/text_pentecostarion_pascha.json  |    30 +
 scripts/deepseek_compliance_audit.py     |    12 +-
 scripts/lint_liturgical_db.py            |     4 +-
 scripts/standardize_liturgical_db.py     |     4 +-
 scripts/test_pascha_rubrics.py           |     2 +-
 tests/test_advanced_collisions.py        |     2 +-
 tests/test_gospel_selection.py           |     4 +-
 tests/test_matins_gold_standard.py       |     6 +-
 tests/test_prokeimenon_precedence.py     |    45 +
 tests/test_semantic_linting.py           |    16 +-
 39 files changed, 7554 insertions(+), 4572 deletions(-)
```

#### [WARNING] Compliance Violations:
- digest/base.py:646 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- digest/base.py:686 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- digest/base.py:814 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- digest/base.py:1991 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- digest/base.py:2152 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- digest/base.py:2157 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- digest/base.py:2242 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- digest/formatters/matins.py:182 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:120 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:573 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:654 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:821 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:893 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/resolvers/common.py:469 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/resolvers/common.py:695 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/resolvers/common.py:808 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/resolvers/common.py:1247 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/resolvers/common.py:1327 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/resolvers/hours.py:87 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/resolvers/hours.py:194 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/resolvers/hours.py:372 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/resolvers/hours.py:496 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/resolvers/liturgy.py:208 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/resolvers/matins.py:581 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/resolvers/matins.py:1410 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/resolvers/vespers.py:775 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/resolvers/vespers.py:970 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/rubrics.py:968 - Bare 'except: pass' detected (violates compliance rule 2).
- engine/rubrics.py:1139 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- scripts/deepseek_compliance_audit.py:459 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- scripts/audit_ui_with_llm.py:215 - Potential 'hasattr' guard check (ensure else branch is provided or documented).

#### Sample Digest Preview (First 30 Lines):
```markdown
# TYPICON: SUNDAY, FEBRUARY 1st, 2026.

FOREFEAST OF THE MEETING - TONE I.
Sunday service combined with that of the Triodion, and that of the forefeast.
The service to St. Martyr Tryphon. is transferred to the previous Friday at Compline, or another convenient time, whenever the ecclesiarch so wishes.
Vestment colour: Bright (Gold or blue for the forefeast).

## GREAT VESPERS

Vestments (priest): epitrachelion, phelonion. The phelonion is blessed and kissed before the Entrance.
Fasting Rule: No fasting restrictions.
Censing: Priest censes entire church during Psalm 103.
Censing: Deacon performs Great censing of the entire church during 'Lord, I Call'.
*At Lord, I Call…* we sing 4 Resurrectional Stichera from the Octoechos, 3 Stichera from the Triodion, and 3 Forefeast Stichera from the Menaion; Glory... doxastikon from the Triodion; Both now: Theotokion of the Feast.
Censing: Small censing at the entrance.
The Royal Doors are opened.
Prokeimenon: The Lord is King (Tone VI).
**At the Aposticha:** We sing the resurrectional aposticha in the tone of the week, from the Octoechos; Glory... doxastikon from the Triodion; Both now: doxastikon of the forefeast.
**At the Dismissal Troparia:** We sing the Sunday (resurrectional) troparion in the tone of the week; Glory, Both now: Theotokion.

## SMALL COMPLINE

Canon: Canon Forefeast from the Menaion.
Troparia: Sunday Troparion from the Octoechos, Troparion of the Temple, *"O God of our fathers..."* and the following three troparia.

## MIDNIGHT OFFICE (SUNDAY)

Triadic Canon: Canon Trinity in Tone 1.
Midnight Troparia: Sunday Hypakoe in Tone 1.
Prayer: Prayer Holy Trinity All Creating.
```