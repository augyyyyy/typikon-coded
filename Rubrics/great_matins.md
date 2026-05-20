# Great Matins: Typikon Rubrics
## Derived from `01i_struct_matins.json` nodes, verified against Dolnytsky Parts I & II

> This file contains two layers:
> - **§ Inline Rubrics** — compact instructions for placement directly into the service book at each structural node.
> - **§ Appendix** — exhaustive, case-by-case encyclopedia entries covering variations and math.

---

# § INLINE RUBRICS

These are placed directly in the Word document at the corresponding structural point.

---

## 1. The Enarxis (Opening) & Six Psalms
**JSON node:** `matins_opening`

The opening choreography differs dramatically based on the presence of a Vigil.

**[Great Matins WITH All-Night Vigil]**
The priest is already vested in the epitrachelion and phelonion. The holy doors remain **open** from Vespers. The priest stands before the holy table and exclaims *"Glory to the Holy, Consubstantial, Life-Creating, and Undivided Trinity."*
Following the choir's response ("Glory to God in the highest..."), the priest **closes** the holy doors, takes off the phelonion, exits through the northern door, and stands before the closed holy doors to recite the Morning Prayers silently while the choir reads the Six Psalms.

**[Great Matins WITHOUT Vigil]**
The priest vests only in the epitrachelion. He exits the northern door to stand before the **closed** holy doors, makes a small bow, and exclaims *"Blessed is our God."* The choir reads the introductory prayers and Trisagion.
The priest enters the sanctuary through the southern door, puts incense in the censer, censes around the holy table, exits the northern door, and censes the iconostasis, choirs, and people while Psalms 19 & 20 are read. Returning to the closed holy doors, he exclaims *"For thine is the kingdom"*, enters the southern door to put away the censer, exits the northern door, and recites the opening litany. Finally, he exclaims: *"Glory to the Holy, Consubstantial..."* and the Six Psalms begin.

*Crucial Rubric:* The Six Psalms are read with all piety and attention. It is strictly forbidden to walk or talk during the Six Psalms.

---

## 2. "God is the Lord"
**JSON node:** `god_is_the_lord`

Following the Great Litany, the deacon intones the verses of *"God is the Lord"* in the appointed tone. The choir sings the troparia.

*On Sundays*, the Tone is determined by the Tone of the Week.
*On Weekday Feasts*, the Tone is determined by the Feast's Troparion.
*See Appendix A for Troparia arrangements.*

---

## 3. The Kathismata and Sessional Hymns (Sidalnyi)
**JSON node:** `kathismata_block`

Two Kathismata are chanted (typically Kathismata 2 & 3 on Sunday, varying by season).
After each Kathisma and its Small Litany, the Sessional Hymns are appointed.

*On Sundays with a Polyeleos Saint*, a unique "Double Stack" occurs where the Sessional Hymns are shifted to accommodate the Polyeleos. *See Appendix B.*

---

## 4. The Third Kathisma (Kathisma 17 or Polyeleos) & Evlogitaria
**JSON node:** `polyeleos_block` (and `evlogitaria_block`)

*On Sundays*, a third Kathisma is required. This is either **Kathisma 17 ("The Blameless")** or **Kathisma 19 (The Polyeleos)** depending on the season.
*The Polyeleos (Psalms 134/135) is sung on all Sundays from September 22 to December 19 (inclusive), and from January 15 to Cheesefare Sunday (inclusive). It is also sung for any Major Feast or Saint of Polyeleos rank or higher.* Outside of these periods, Kathisma 17 is sung on Sundays.

*On all Sundays*, the Evlogitaria of the Resurrection *"Blessed art Thou, O Lord"* (also called "The Angelic Council") are sung immediately following this third Kathisma slot, whether it was Kathisma 17 or the Polyeleos.

---

## 5. Hypakoe and Anabathmoi (Degrees / Stepenna)
**JSON node:** `hypakoe_anabathmoi_prokeimenon`

Structurally, this node is occupied by the Hypakoe on Sundays, and by the 3rd Sessional Hymn (Sidalen) on Feasts. They serve identical functions for their respective services.
*On Sundays*, the 3rd Sessional Hymn is suppressed and the Resurrectional **Hypakoe** of the tone is read FIRST, followed by the Anabathmoi (Stepenna) of the **Tone of the Week**.
*On Feasts*, the **Polyeleos Sessional Hymn** of the Feast is sung FIRST (no Hypakoe is taken), followed by the 1st Antiphon of Tone 4 *"From my youth..."* as the Anabathmoi.
*(Exception: On Sundays that coincide with a Polyeleos Saint or Feast, BOTH elements are taken. See Appendix B for the "Double Stack").*

---

## 6. The Matins Gospel
**JSON node:** `matins_gospel_block`

As the Gradual ends, the priest vests in the **phelonion**, opens the holy doors, and exclaims: *"Let us be attentive. Peace be unto all!"*
The choir sings *"Let every breath praise the Lord"*. The priest does a full censing of the holy table, sanctuary, iconostasis, choirs, and people.
Upon the conclusion of the Gospel reading at the holy doors, the priest closes the Gospel Book and, preceded by candle-bearers, carries it out to the tetrapod for veneration.

*On Sundays*, the appointed Eothinon (Morning) Resurrectional Gospel is read. "*Having beheld the Resurrection of Christ*" is then sung.
*On Feasts*, the festal Gospel is read. *(Note: "Having beheld the Resurrection" is inherently a Resurrectional hymn and is suppressed on week-day Feasts, except for specific exceptions like the Exaltation of the Cross).*

---

## 7. Psalm 50, Post-Gospel Stichera, & The Anointing (Myrovania)
**JSON nodes:** `psalm_50_block`, `anointing_block`

Psalm 50 is read.
*On Sundays:* ☨ Glory: *"Through the prayers of the Apostles..."*, Now: *"Through the prayers of the Theotokos..."*, then *"Have mercy on me, O God,"* and the sticheron *"Jesus having risen from the grave..."*
*On Feasts:* Special festal refrains replace the Sunday ones.

Following these stichera, the priest exclaims *"O God, save thy people..."*

**[With All-Night Vigil]**
The priest remains in the phelonion. He exits through the open holy doors, stands to the right of the tetrapod, and anoints the faithful with the blessed oil from Vespers as they venerate the Gospel. He says *"Christ is in our midst"*, to which they reply *"He is and shall be"*. After all have been anointed, he returns to the sanctuary, closes the holy doors, and removes the phelonion.
**[Without Vigil]**
The priest does NOT anoint. Upon exclaiming *"By the mercy and compassions..."*, he bows, closes the holy doors, and immediately removes the phelonion. The choir sings the Canon.

## 8. The Canons
**JSON node:** `canons_block`

The Canons are combined from the Octoechos, Triodion/Pentecostarion (if applicable), and Menaion, targeting a total of 14 (or 12) troparia per ode.
*See Appendix C for the exact mathematical distributions governing Great Matins.*

Following the 3rd Ode: Sessional Hymns.
Following the 6th Ode: Kontakion and Ikos.

---

## 9. Katavasia
**JSON node:** `katavasia_block`

The Katavasia is sung at the end of each Ode (or at the conclusion of Odes 3, 6, 8, and 9 during daily services). The seasonal Katavasia is chosen based on the Typikon's festal cycle.

---

## 10. The Magnificat (Ode 9)
**JSON node:** `magnificat_block`

Usually, the deacon censes and exclaims *"The Theotokos and Mother of the Light, let us magnify in hymns,"* and the choir sings *"My soul magnifies the Lord..."* (The Magnificat).
*On Great Feasts of the Lord and the Theotokos*, the Magnificat is suppressed and replaced by the Festal Megalynaria (Zadostoinyks) assigned to the 9th Ode.

---

## 11. "Holy is the Lord" vs. "It is truly meet" & The Exapostilarion
**JSON node:** `exapostilarion_block`

This slot is occupied by a specific preamble depending on the day:
*On Sundays*, **"Holy is the Lord our God"** is sung (3x) according to the Tone of the Matins Prokeimenon. *(Note: "It is truly meet" is entirely suppressed).*
*On Weekday Feasts*, **"It is truly meet"** is sung instead. *(Note: "Holy is the Lord" is entirely suppressed).*

Immediately following this preamble, the Exapostilarion (Hymn of Light) is read/chanted.
*On Sundays*, the Exapostilarion matches the **Morning Eothinon Gospel (1-11)** that was read earlier, NOT the Tone of the week.

---

## 12. The Praises (Psalms 148-150)
**JSON node:** `praises_block`

*On Sundays*, 8 Stichera are chanted (varying by rank).
☨ Glory: The **Eothinon Doxastikon** matching the morning Gospel (1-11).
Now: *"Most blessed art thou, O Virgin Theotokos..."*

---

## 13. Great Doxology
**JSON node:** `doxology_block`

The priest exclaims: *"Glory to Thee Who hast shown us the light!"*
At Great Matins, the Great Doxology is ALWAYS sung festively, concluding with the sung *"Holy God"*. (It is never read at Great Matins).

---

## 14. Dismissal Troparion
**JSON node:** `dismissal_troparion_block`

Immediately following the Trisagion of the Doxology:
*On Sundays*, only the Resurrection Troparion is sung (*"Today salvation has come to the world"* for odd tones; *"Having risen from the tomb"* for even tones).
*On Great Feasts*, the festal troparion is sung once.

---
---

# § APPENDIX

---

## Appendix A: "God is the Lord" Troparia Combinations

*If Sunday + Simple Saint:* Sunday troparion (2x), ☨ Glory: Saint troparion (1x), Now: Sunday Theotokion in the tone of the Saint.
*If Sunday + Two Saints:* Sunday troparion (1x), Troparion of First Saint (1x), ☨ Glory: Troparion of Second Saint (1x), Now: Sunday Theotokion in the tone of the Second Saint.
*(Note: If two saints fall on Sunday, the Tone for the "God is the Lord" theotokion is controlled by the SECOND saint listed.)*
*If Feast of the Lord:* Festal troparion (3x).

---

## Appendix B: Sessional Hymns (Sidalnyi) Stacking Logic

The Sessional Hymns (Sidalnyi) must carefully intercalate with the Kathismata readings.

### The Sunday Polyeleos "Double Stack"
When a *Saint with Polyeleos* falls on a Sunday, the saint's sessional hymns are displaced by the Resurrectional ones. This creates a "Double Stack" after the Polyeleos:
1. *After Kathisma 1:* Resurrectional Sessional Hymns (Tone of the Week).
2. *After Kathisma 2:* Resurrectional Sessional Hymns (Tone of the Week).
3. *After Polyeleos (The Stack):*
   - Resurrectional Hypakoe of the tone.
   - 1st Sessional Hymn of the Saint.
   - 2nd Sessional Hymn of the Saint.
   - ☨ Glory: The Polyeleos Sessional Hymn of the Saint.
   - Now: His Theotokion.

---

## Appendix C: Canon Distribution Mathematics

The combination of Canons must equal 14 (sometimes 12 on Feasts), inclusive of the Irmos.
*Note: The Irmos is only sung for the FIRST Canon listed.*

### Octoechos & Menaion Distributions

**Sunday + Simple Saint on 4 ("On 14")**
- `Resurrection` (w/ Irmos): 4
- `Cross-Resurrection` (w/o Irmos): 3
- `Theotokos` (w/o Irmos): 3
- `Saint`: 4
*(Total: 14)*

**Sunday + Two Saints ("On 14")**
- `Resurrection` (w/ Irmos): 4
- `Theotokos`: 2
- `First Saint`: 4
- `Second Saint`: 4
*(Total: 14. Cross-Resurrection is suppressed.)*

**Sunday + Polyeleos or Vigil Saint on 8 ("On 14")**
- `Resurrection` (w/ Irmos): 4
- `Theotokos`: 2
- `Saint`: 8
*(Total: 14. Cross-Resurrection is suppressed.)*

**Feast of the Lord or Theotokos ("On 12" or "On 14")**
- `Feast Canon 1 + Canon 2`: 12 (Irmoi sung twice to equal 14 total, or troparia read to 12).
- *If Sunday + Feast of Theotokos:* `Resurrection` 4 + `Theotokos (Octoechos)` 2 + `Feast` 8 = 14.

### Triodion Distributions (Lenten Season)

During the Lenten season, the Menaion is often suppressed to Compline to make room for the Triodion.

**Sundays of Great Lent (e.g. Sunday of Orthodoxy, Cross Veneration) ("On 14")**
- `Resurrection` (w/ Irmos): 4
- `Cross-Resurrection`: 2
- `Theotokos`: 2
- `Triodion`: 6
*(Total: 14. Menaion is suppressed.)*

**Sunday of the Publican & Pharisee / Prodigal Son ("On 14")**
- `Resurrection` (w/ Irmos): 4
- `Cross-Resurrection` (or *Theotokos* if only one is taken): 2
- `Triodion`: 4
- `Menaion`: 4
*(Total: 14).*
