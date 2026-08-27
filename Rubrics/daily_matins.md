# Daily Matins: Typikon Rubrics
## Derived from `01i_struct_matins.json` nodes, verified against Dolnytsky Parts I & II

> This file contains two layers:
> - **§ Inline Rubrics** — compact instructions for placement directly into the service book at each structural node.
> - **§ Appendix** — exhaustive, case-by-case encyclopedia entries.

---

# § INLINE RUBRICS

These are placed directly in the Word document at the corresponding structural point.

---

## 1. The Enarxis (Opening) & Six Psalms
**JSON node:** `opening_daily`

The priest vests in the **epitrachelion only** (never the phelonion). The holy doors remain **closed**.
He exits through the northern door, stands before the closed holy doors, makes a small bow, and exclaims *"Blessed is our God."* The choir reads the introductory prayers and Trisagion.
The priest enters the sanctuary through the southern door, puts incense in the censer, censes around the holy table, exits the northern door, and censes the iconostasis, choirs, and people while Psalms 19 & 20 are read. Returning to the closed holy doors, he exclaims *"For thine is the kingdom"*, enters the southern door to put away the censer, exits the northern door, and recites the opening litany. Finally, he exclaims: *"Glory to the Holy, Consubstantial..."* and the Six Psalms begin.

*Crucial Rubric:* The Six Psalms are read with all piety and attention. It is strictly forbidden to walk or talk during the Six Psalms. The priest stands before the closed holy doors and reads the Morning Prayers silently.

---

## 2. "God is the Lord"
**JSON node:** `god_is_the_lord`

Following the Great Litany, the deacon intones the verses of *"God is the Lord"* in the appointed tone. The choir sings the troparia.

For a *simple saint*, the troparion of the saint is sung twice. ☨ Glory... Now: *Dismissal Theotokion in the tone of the saint’s troparion and of the day of the week.*
*See Appendix A for Troparia arrangements.*

---

## 3. The Kathismata
**JSON node:** `kathismata_daily_block`

Two Kathismata are chanted following the psalter schedule.
After each Kathisma and its Small Litany, the Sessional Hymn of the Octoechos is read.

---

## 4. Psalm 50
**JSON node:** `horologion.psalm_50`

Psalm 50 is read immediately after the final Sessional Hymn. There are no post-Gospel stichera or refrains.

---

## 5. The Canons
**JSON node:** `canon_daily`

Three canons are chanted, targeting a total of 14 troparia per ode. The Heirmoi are sung only for the first canon of the Octoechos. 
*See Appendix B for the exact mathematical distributions governing Daily Matins.*

Following the 3rd Ode: Sessional Hymn of the saint.
Following the 6th Ode: Kontakion and Ikos of the saint (if available).

---

## 6. Katavasia
**JSON nodes:** `katavasia_3`, `katavasia_6`, `katavasia_8`, `katavasia_9`

At Daily Matins, Katavasia is only sung following the 3rd, 6th, 8th, and 9th Odes.
In all cases, the Katavasia is the **Heirmos of the last canon** (the canon of the saint), *not* the seasonal heirmos.

---

## 7. The Magnificat
**JSON node:** `ode_9_magnificat`, `it_is_truly_meet`

The priest exits the sanctuary, and censes the altar, the iconostasis, the choirs, and the people as at Vespers. The choir sings *"More honorable than the Cherubim"*, with its refrains, for the 9th Ode.

---

## 8. Exapostilarion
**JSON node:** `exapostilarion`

Following the 9th Ode Katavasia and *"It is truly meet"*:
The Exapostilarion of the Octoechos is chanted.
☨ Glory: *Exapostilarion of the saint (if any)*.
Now: *Theotokion of the Exapostilarion of the saint.*
*(If the saint has none, then the Theotokion of the Octoechos is taken. **Exceptions**: On Wednesday and Friday, the Stavrotheotokion of the Octoechos is taken. On Thursday, because the Octoechos commemorates St. Nicholas, the Theotokion of the Octoechos is ALWAYS taken instead of the Menaion).*

---

## 9. The Praises (Psalms 148-150)
**JSON node:** `praises_read`

Psalms 148, 149, and 150 are read simply by the reader, without singing and without any stichera appended to them.
*(Exception: If it is a Saint on 6 who has stichera on the Praises, the stichera are sung here. The rector then chooses whether to proceed to the Great Doxology or keep the Small Doxology—see Appendix C).*

---

## 10. Small Doxology
**JSON node:** `small_doxology`, `litany_supplication`

The priest, standing before the closed holy doors, exclaims: *"Glory to Thee Who hast shown us the light!"*
At Daily Matins, the Small Doxology is READ. The priest does **not** exclaim "To thee belongs glory" before the Doxology. He remains standing before the doors. Following the Small Doxology, the Litany of Supplication (*"Let us complete"*) is sung by the priest.

---

## 11. Aposticha
**JSON node:** `aposticha`

All Aposticha stichera from the Octoechos for the day of the week, with their usual refrains.
If the saint in the Menaion has a Doxastikon, then ☨ Glory: *his Doxastikon*, Now: *Theotokion from the Matins Aposticha in the tone of the Doxastikon and of the day of the week.*

---

## 12. Conclusion and Dismissal
**JSON node:** `trisagion_block`, `dismissal_troparion`, `dismissal_theotokion`, `dismissal_daily`

*"It is a good thing to give thanks unto the Lord,"* Trisagion, *"Our Father."*

Then, the **Troparion of the saint** is sung.
☨ Glory... Now: *Dismissal Theotokion in the tone of the saint’s troparion and of the day of the week* (this Theotokion must be DIFFERENT from the one sung at Vespers and at "God is the Lord").

Litany of Fervent Supplication (*"Have mercy on us"*), followed by the Small Dismissal.

---
---

# § APPENDIX

---

## Appendix A: "God is the Lord" Troparia Combinations

*If Simple Saint:* Troparion of the saint (2x), ☨ Glory... Now: Dismissal Theotokion in the tone of the saint’s troparion and of the day of the week.
*If Two Saints:* Troparion of the first saint (2x), ☨ Glory: Troparion of the second saint (1x), Now: Dismissal Theotokion in the tone of the second saint and of the day of the week.

---

## Appendix B: Canon Distribution Mathematics

The combination of Canons must equal 14, inclusive of the Heirmos.
*Note: At Daily Matins, the Heirmos is only sung for the FIRST Canon listed.*

### Octoechos & Menaion Distributions

**Weekday + Simple Saint on 4 ("On 14")**
- `Octoechos Canon 1` (w/ Heirmos): 6
- `Octoechos Canon 2` (w/o Heirmos): 4
- `Saint` (w/o Heirmos): 4
*(Total: 14)*

**Weekday + Two Saints ("On 14")**
- `Octoechos Canon 1` (w/ Heirmos): 6 (The second Octoechos canon is not taken)
- `First Saint` (w/o Heirmos): 4
- `Second Saint` (w/o Heirmos): 4
*(Total: 14)*

**Weekday + Saint on 6 ("On 14")**
- `Octoechos Canon 1` (w/ Heirmos): 4 (Two martyria are omitted, except on Thursday)
- `Octoechos Canon 2` (w/o Heirmos): 4
- `Menaion Saint` (w/o Heirmos): 6
*(Total: 14)*

### Triodion & Pentecostarion Distributions

During the Pre-Lenten weeks (Publican & Pharisee to Cheesefare) and the Pentecostarion (Pascha to All Saints), Daily Matins is sung with additions from the seasonal book.

**Weekday + Triodion/Pentecostarion + Simple Saint ("On 14")**
- `Octoechos Canon 1` (w/ Heirmos): 6 (The second Octoechos canon is discarded)
- `Triodion/Pentecostarion` (w/o Heirmos): 4
- `Menaion Saint` (w/o Heirmos): 4
*(Total: 14)*

---

## Appendix C: Saint on 6 Exceptions

*When a "Saint on 6" occurs on a weekday, the general structure remains Daily Matins, but with possible interpolations based on the Menaion:*
- **The Rector's Choice:** If the Menaion provides Praises stichera (e.g., Sept 6), the decision must be made by the rector:
  1. Sing the Praises, then sing the **Great Doxology** (thereby suppressing the Aposticha entirely in favor of the Doxology's Trisagion transition).
  2. Sing the Praises, then read the **Small Doxology** (thereby executing the Litany of Supplication and retaining the Aposticha).
- In some rare cases, the Saint on 6 will have a fully proper Aposticha and proper Sessional Hymns (e.g. Oct 23). In these cases, those hymns supersede the Octoechos.
