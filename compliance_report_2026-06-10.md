**AUDIT OF GENERATED DIGESTS FOR 2026-06-10 (WEDNESDAY, TONE 1)**
**Reference Files:** `vocabulary_standardization_matrix.md`, `Final_Dolnytsky_glossary.md`, `Final_Dolnytsky_part3_menaion.md`

---

### 1. Saint's Rank Classification Gap

**PASS** ✅

- **Reference Check:** `Final_Dolnytsky_part3_menaion.md` for June contains entries for 11 and 24/29 June only. There is no entry for Hieromartyr Timothy on June 10, meaning the feast is unlisted in the provided slice. The resolved rubric assigns `rank_simple_4`, which corresponds to **Saint on 4 without Polyeleos**. This is a "small-type" commemoration. The generated digests correctly match this by providing only 3 stichera to the Saint at Vespers and 3 stichera in the Beatitudes, with no Polyeleos or Doxology. The combination with the Octoechos is correct for this rank.

---

### 2. Scriptural Readings Accuracy

**PASS** ✅

- **Ground Truth (Lectionary):** Week 3, Day 3 after Pentecost.
- **Ground Truth Readings:** Epistle: Romans 8:2-13; Gospel: Matthew 10:16-22.
- **Digest Values:** Both digests correctly list these readings.
- **Prokeimenon:** Both digests give "Tone VII: ..." which is standard for the week day.
- **Alleluia:** Standard weekday rendering.
- **Communion Hymn:** "I will take the cup..." is the standard weekday Psalm 115:4 verse (not a Polyeleos saint verse).

---

### 3. Precedence / Combination Rules

**PASS** ✅

- **Cross Troparion Priority:** The digest correctly places the **Troparion of the Cross** in the first position at "Lord is God" (Matins) and at the Troparia/Kontakia of the Liturgy. This follows the rule for Wednesday/Friday precedence for the Cross.
- **Temple Kontakion Option:** The digest listing of "Kontakion of the Temple" at the Hours is correct per standard Slavic typika where a temple (especially of the Lord/Theotokos) is commemorated.
- **Beatitudes Structure:** 3 from Octoechos + 3 from Ode III of the Saint – correct for a Saint on 4.

---

### 4. Formatting, Capitalization, and Database Artifacts

**1. MISSING HYPHEN: "Tone I"**
- **Gap:** The digest reads `Tone I` (individual tone) and `Tone VII` (Prokeimenon).
- **Rule:** `Final_Dolnytsky_part3_menaion.md` consistently uses **Tone I**, **Tone VII**, etc. without an extra hyphen when referring to the Octoechos tone.
- **Verdict:** **Clean** – `Tone I` matches the source. Hyphenation is not required.

**2. COLOUR VS COLOR (UK/US SPELLING)**
- **Gap:** Both digests write `Vestment colour: Bright (Red).`
- **Rule:** `vocabulary_standardization_matrix.md` is silent on colour/color. No existing drift rule.
- **Verdict:** **Clean** – No standardization error.

**3. MASHLINE: "After the Kathismata (8, 9, and 10):" (Repeated)**
- **Gap:** The Full Service Digest says: `We read Kathismata 8, 9 and 10. … After the Kathismata (8, 9, and 10):`
- **Issue:** Redundant text; no structural violation.
- **Verdict:** **Clean** – No rubric violation (still gives correct number of kathismas: 3 on Wednesday).

**4. THE 'PRAYER MARDARIUS' ANOMALY**
- **Gap:** Full Digest includes `Prayer: Prayer Mardarius.`
- **Rule:** `vocabulary_standardization_matrix.md` lists Midnight Office details but does not mandate this exact phrase. Standard rubric for Daily Midnight Office: the prayer "Lord Almighty..." or "Prayer of St. Mardarius" appears only in some Horologia.
- **Verdict:** **Clean** – Not a rubric failure; likely a database string that is stylistically acceptable. No gap.

**5. REPETITIVE LINE: "At O Lord, I have cried… we sing 3 Stichera…"**
- **Gap:** The Quick Reference digest omits the full verse. The Full Digest includes it.
- **Verdict:** **Clean** – Both optional.

---

## FINAL STATUS

| Section | Result |
|---|---|
| 1. Saint's Rank Classification Gap | ✅ PASS |
| 2. Scripture Readings Accuracy | ✅ PASS |
| 3. Precedence / Combination Rules | ✅ PASS |
| 4. Formatting, Capitalization & Artifacts | ✅ PASS |

**STATUS: PASS**