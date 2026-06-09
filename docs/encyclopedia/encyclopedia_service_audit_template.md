# Universal Dolnytsky Service Audit Template

> **Purpose**: Reusable methodology for auditing ANY service to 100% implementation
> **Method**: Apply 7-step Typikon search process (see typikon_search_methodology.md)

---

## Service Location Matrix

| Service | Typikon Part | Line Range | Variants | Struct File |
|:--------|:-------------|:-----------|:---------|:------------|
| **Vespers** | Part I | 1-100 | Great (Vigil), Great, Daily, Small | `01h_struct_vespers.json` |
| **Compline** | Part I | 100-150 | Great (Vigil), Great, Small | `01f_struct_compline.json` |
| **Midnight Office** | Part I | 150-180 | Sunday, Daily, Saturday | `01g_struct_midnight.json` |
| **Matins** | Part I | 180-220 | Great, Daily, + **Part IV** for Lenten | `01i_struct_matins.json` |
| **Hours (1,3,6,9)** | Part I | 209-220 | Usual, Lenten, Royal | `01a-d_struct_hour_*.json` |
| **Typika** | Part IV | 132-136 | Standard, Lenten | `01e_struct_typika.json` |
| **Liturgy** | Appendix | 1-500 | Chrysostom, Basil, Presanctified | `01j_struct_liturgy.json` |

---

## Per-Service Audit Checklist Template

```markdown
### [SERVICE NAME] Audit

**Source**: Dolnytsky Part [X], Lines [Y-Z]

#### Step 1: Locate Orders
- [ ] Find "ORDER OF [SERVICE]" header
- [ ] Note exact line numbers

#### Step 2: Extract Elements (Variant 1: [TYPE])
| # | Element | Typikon Line | Current JSON | Status |
|:-:|:--------|:-------------|:-------------|:-------|
| 1 | | | | |

#### Step 3: Extract Elements (Variant 2: [TYPE])
| # | Element | Typikon Line | Current JSON | Status |
|:-:|:--------|:-------------|:-------------|:-------|
| 1 | | | | |

#### Step 4: Cross-Reference Part II (Paradigms)
- [ ] Check paradigms affecting this service
- [ ] Note 2-saint stacking rules

#### Step 5: Verify Implementation
- [ ] All elements have JSON representation
- [ ] All variable elements have resolve functions
- [ ] No definitional gaps (false positives)

#### Step 6: Implement Gaps
- [ ] Add missing hooks
- [ ] Add Typikon citations to rubrics
- [ ] Validate JSON

#### Step 7: Create Stress Tests
- [ ] 2-saint scenario
- [ ] Feast + saint collision
- [ ] Seasonal override (Lent, Pascha)
```

---

## Quick Reference: Key Typikon Sections

| Section | Content | Audit Priority |
|:--------|:--------|:---------------|
| Part I: Orders | Service structures | HIGH |
| Part II: Paradigms | 20 stacking rules | HIGH |
| Part III: Menaion | Fixed feast rubrics | MEDIUM |
| Part IV: Triodion | Lenten/Paschal overrides | HIGH |
| Part V: Temple | Temple feast rules | LOW |
| Footnotes | Exception clarifications | AS NEEDED |

---

## Maximum Liturgical Day (Stress Test Baseline)

Per Dolnytsky Part II Line 31:
> **"The ecclesiastical rubric does NOT provide for more than TWO services to saints [on one day]."**

| Scenario | Components | Complexity |
|:---------|:-----------|:-----------|
| Sunday + 2 Saints | Resurrection + 2 Menaion | MAX |
| Great Feast + Saint | Feast dominates | HIGH |
| Forefeast + 2 Saints | e.g., November 2 | HIGH |
| Lenten Weekday + Saint | Triodion + Menaion | MEDIUM |
| Afterfeast + Apodosis + 2 Saints | Ultimate edge case | EXTREME |

---

## Replication Instructions for Other Models

1. **Start with typikon_search_methodology.md** — Follow 7 steps exactly
2. **Use this template** — Copy audit checklist for each service
3. **Reference matins_variants_gap_matrix.md** — Pattern for element comparison
4. **Apply to struct JSON files** — Add missing elements with Typikon citations
5. **Validate JSON** — `py -c "import json; json.load(open(file))"`
6. **Update task.md** — Track progress per service

---

## Services Audit Status

| Service | Variants | Great | Daily | Lenten | Status |
|:--------|:---------|:-----:|:-----:|:------:|:-------|
| **Matins** | 3 | ✅ | ✅ | ✅ | **100%** |
| **Vespers** | 4 | 🔶 | 🔶 | — | Partial |
| **Compline** | 3 | 🔶 | — | 🔶 | Partial |
| **Midnight** | 3 | 🔶 | 🔶 | — | Partial |
| **Hours** | 3 each | 🔶 | — | 🔶 | Partial |
| **Typika** | 2 | — | ✅ | 🔶 | Partial |
| **Liturgy** | 3 | 🔶 | — | 🔶 | Partial |
