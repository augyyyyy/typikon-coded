### *** Typikon Compliance Gate Report ***

**Test Suite Result:** `========================= 303 passed`
**Files Changed:** 12

#### Git Diff Summary:
```
engine/core.py                     |   2 +-
 engine/generation.py               |  48 ++++++++++++++-
 engine/text_db.py                  |  12 +++-
 generate_typikon_service.py        |   4 +-
 tests/test_integration_registry.py |   2 +-
 tests/test_matins_gold_standard.py |   3 +-
 tests/test_matins_suite.py         |   3 +-
 typikon_digest_generator.py        | 118 ++++++++++++++++++++++++++++++-------
 8 files changed, 162 insertions(+), 30 deletions(-)
```

#### [WARNING] Compliance Violations:
- engine/generation.py:97 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:530 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:611 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:778 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- engine/generation.py:850 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- typikon_digest_generator.py:262 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- typikon_digest_generator.py:302 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- typikon_digest_generator.py:1224 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- typikon_digest_generator.py:1368 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- typikon_digest_generator.py:1373 - Potential 'hasattr' guard check (ensure else branch is provided or documented).
- typikon_digest_generator.py:1456 - Potential 'hasattr' guard check (ensure else branch is provided or documented).

#### Sample Digest Preview (First 30 Lines):
```markdown
# TYPICON: SUNDAY, FEBRUARY 1st, 2026.

FOREFEAST OF THE ENCOUNTER - SUNDAY OF THE PRODIGAL SON - TONE I
Sunday service combined with the triodion, and that of the forefeast.
The service to St. Martyr Tryphon. is transferred to the previous Friday at Compline, or another convenient time, whenever the ecclesiarch so wishes.
Vestment colour: Bright (Gold or blue for the forefeast).

## GREAT VESPERS

> [!NOTE]
> **Rubric**: Vesting and Censing — [Ordo §29–§30]

Vestments (priest): epitrachelion, phelonion - Phelonion blessed and kissed before Entrance. (Ordo §22–§24).
Fasting Rule: No fasting restrictions (Dolnytsky Appendix — Normal day).
Censing: Priest censes entire church during Psalm 103 (Dolnytsky I:16 — Great censing at Psalm 103).

> [!NOTE]
> **Rubric**: The Proemial Psalm — [Ordo §31]

Censing: Great censing of the entire church (Dolnytsky I:20 — At 'Lord I have cried').
At O Lord, I have cried, we sing 4 resurrectional stichera from the Octoechos, 3 Stichera from the Triodion, 3 Forefeast from the Menaion; Glory... doxasticon from the Triodion; Both now... Dogmatic Theotokion in the tone of the week.
Censing: Small censing at the entrance (Dolnytsky I — At the Entrance).
Royal Doors: OPEN -  (Ordo §19b).

> [!NOTE]
> **Rubric**: [Ordo §34]

Prokeimenon: The Lord is King (Tone VI).
We sing the resurrectional aposticha in the tone of the week, from the Octoechos; Glory... doxasticon from the Triodion; Both now... doxasticon of the forefeast.

```