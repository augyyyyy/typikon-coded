# Encyclopedia of Repetition Logic (The "On X" Rules)

> [!IMPORTANT]
> **Core Principle:** In the Dolnytsky Typikon, when a rubric prescribes a count (e.g., "on 4", "on 6") that exceeds the distinct text elements available in the Menaion or Octoechos, **repetition** is the mandatory mechanism to satisfy the count.

## 1. Stichera (Vespers & Praises)
**The Rule:** You must always fill the prescribed number of stichera to match the number of "Verse Refrains" (Psalm verses).

*   **Case A: Surplus Texts.** (Rare). If the Menaion provides *more* stichera than the count (e.g., 6 provided, rule says "on 4"), you take the first 4.
*   **Case B: Exact Match.** (Ideal). If the Menaion provides 3 stichera and the rule is "on 3", sing each once.
*   **Case C: Insufficient Texts (The Repetition Rule).**
    *   **Goal:** Reach the target count (N).
    *   **Method:** Repeat the **first** stichera first.
    *   *Example 1 (Rule "On 6", Menaion has 3):*
        1.  Stichera 1
        2.  Stichera 2
        3.  Stichera 3
        4.  Stichera 1 (Repeat)
        5.  Stichera 2 (Repeat)
        6.  Stichera 3 (Repeat)
        *   *(Alternative tradition: 1,1, 2,2, 3,3 - check local custom, but standard is looping).*
    *   *Example 2 (Rule "On 4", Menaion has 3):*
        1.  Stichera 1
        2.  Stichera 2
        3.  Stichera 3
        4.  Stichera 1 (Repeat)

> **Primary Source Logic:**
> "When the Typikon prescribes more stichera than are in the Menaion, the first ones are repeated to make up the number." (Dolnytsky, Part I, General Notes).
> "If two saints occur... to the first saint - 3, and to the second - 2 (Total 5)." (Dolnytsky, Part II, Line 37). *Implies filling the count.*

## 2. Canon Troparia ("On 4", "On 6", "On 8", "On 14")
**The Rule:** The "Irmos" is strictly distinct from the Troparia count. The count refers *only* to the troparia that follow the Irmos.

*   **Standard Repetition Patterns:**
    *   **Have 3, Need 4:** 1st comes twice. (1, 1, 2, 3).
    *   **Have 2, Need 4:** Both come twice. (1, 1, 2, 2).
    *   **Have 3, Need 6:** All come twice. (1, 1, 2, 2, 3, 3) or (1, 2, 3, 1, 2, 3).
    *   **Have 4, Need 6:** First two come twice. (1, 1, 2, 2, 3, 4).

> [!NOTE]
> **Dolnytsky Specifics:** Dolnytsky often specifies "The Irmos of the first canon is taken, the others are not." The total count (e.g., "14") usually includes the Irmos of the *leading* canon but excludes the others.
> *   *Formula:* Total = (Irmos x 1) + (Canon A Troparia) + (Canon B Troparia).

## 3. Sessional Hymns (Sidalnyi)

### The "Twice" Rule
Often, a rubric will say: *"Sessional Hymn of the Saint twice."*
*   **Meaning:**
    1.  Read the Sessional Hymn.
    2.  **Glory, Both now:**
    3.  Read the *same* Sessional Hymn again (or its Theotokion if explicitly provided).
    *   *Correction:* Usually "Twice" means: Sessional, Glory, Sessional (Repeat), Both now, Theotokion.

> **Primary Source Logic:**
> "The Sessional Hymn on Feasts of the Lord and of the Theotokos [is taken] twice; that is once – simply the Sessional Hymn, and the second time – with the refrain Glory, Both now." (Dolnytsky, Part I, Line 176).
> *Clarification:* "If the Saint has two Sessional Hymns... then they are taken once each, that is the first – simply, the second – with the refrain Glory, then Both now: his Theotokion." (Dolnytsky, Part I, Line 176).

### Shortage of Sessionals (The "Double Stack" nuance)
When combining Sunday + Saint (Polyeleos), we need to fill **3** slots for the Saint after the Polyeleos (Sess 1, Sess 2, Poly Sess).
*   **If the Menaion lacks 3 distinct Service Sessionals:**
    *   **Scenario:** Menaion has only 1 Sessional (common for simple saints).
    *   **Action:** You do typically *not* repeat the same sessional 3 times to fill slots. Instead, the logic might shift to using the Octoechos or collapsing the structure.
    *   **However, Dolnytsky says:** "If the Saint has two Sessional Hymns... then they are taken once each... Glory: his Polyeleos Sessional." (Part II). This implies strict mapping:
        *   Slot 1 <- Sessional 1
        *   Slot 2 <- Sessional 2
        *   Slot 3 <- Poly Sess
    *   **If Missing:** If a specific slot is empty (e.g., no "Polyeleos Sessional" explicitly named), the General Sessional or the 2nd Sessional is repeated/used in that high-value slot.

## 4. Troparia at "God is the Lord"
*   **Rule:** "Troparion of the Saint twice."
*   **Action:** Sing the Troparion, then "Glory...", then sing **the same Troparion again**. Then "Both now...", Theotokion.

## Summary Table

| Element | Rule "On X" | Asset Has Y (Y < X) | Action |
| :--- | :--- | :--- | :--- |
| **Stichera** | On 4 | Has 3 | 1 (x2), 2, 3 |
| **Stichera** | On 4 | Has 2 | 1 (x2), 2 (x2) |
| **Canon** | On 4 | Has 3 | 1 (x2), 2, 3 |
| **Canon** | On 6 | Has 4 | 1 (x2), 2 (x2), 3, 4 |
| **Troparion** | Twice | Has 1 | Sing, Glory, Sing (Repeat) |
| **Sessional**| Twice | Has 1 | Read, Glory, Read (Repeat) |

---

## 🔧 ENGINE IMPLEMENTATION STATUS

| Logic Feature | Function Name | Dolnytsky Ref | Status |
|:---|:---|:---|:---|
| **Stichera Repetition** | `fill_to_count(strategy='leading')` | Part I (Vespers) | ✅ **DONE** |
| **Canon Repetition** | `fill_to_count(strategy='doubling')` | Part I (Canon) | ✅ **DONE** |
| **Sessional "Twice"** | `resolve_sidalen_content` | Part I, Ln 176 | ✅ **DONE** |
| **Double Stack Sizing** | `resolve_sidalen_content` | Part II (Polyeleos) | ✅ **DONE** |
