# Great Vespers: Typikon Rubrics
## Derived from `01h_struct_vespers.json` nodes, verified against Dolnytsky Part II

> This file contains two layers:
> - **§ Inline Rubrics** — compact instructions for placement directly into the service book at each structural node.
> - **§ Appendix** — exhaustive, case-by-case encyclopedia entries covering all 20 paradigm cases.

---

# § INLINE RUBRICS

These are placed directly in the Word document at the corresponding structural point.

---

## 1. The Enarxis (Opening) & Psalm 103
**JSON node:** `opening_vigil` / `beginning_polyeleos` / `horologion.psalm_103_vigil`

The choreography differs dramatically depending on whether a Vigil is prescribed.

**[Vespers WITH All-Night Vigil]**
The priest vests in the epitrachelion and phelonion. The holy doors are opened. The deacon(s) and priest cense the Holy Table, the entire sanctuary, the iconostasis, and the entire church. Returning to the holy doors, the deacon exclaims: *"Master, give the blessing!"* (or *"Lord, bless!"*).
The priest, from the altar, sings in a loud voice: *"Glory to the Holy, Consubstantial, Life-Creating, and Undivided Trinity, always, now and ever, and unto ages of ages."*
Following the "Amen," the choir immediately sings *"Come, let us worship,"* and begins Psalm 103 (Festal/Vigil melody).
*Crucial Rubric:* The holy doors are immediately **closed**. The priest takes off the phelonion and, vested only in his epitrachelion, exits through the northern door to stand before the closed holy doors where he reads the Prayers of Light silently.

**[Great Vespers WITHOUT Vigil]**
The priest vests in the epitrachelion (and mantle) only.
He exits the sanctuary via the northern door and stands before the **closed** holy doors. Making a small bow, he exclaims: *"Blessed is our God, always, now and ever, and unto ages of ages."*
Following the "Amen" and the introductory prayers ("Glory to thee O God", "O Heavenly King", Trisagion, etc.), the choir sings *"Come, let us worship"* and begins the standard chanting of Psalm 103. The priest reads the Prayers of Light silently from his position before the closed doors.

---

## 3. The Kathisma
**JSON node:** `kathisma_vigil` / `kathisma_daily`

*On Saturday evening* (evaluating Sunday), the entire 1st Kathisma *"Blessed is the man"* is sung.

*On weekday evenings* preceding a feast with an All-Night Vigil, only the 1st Antiphon of the 1st Kathisma is sung.

*On Sunday evenings* preceding a feast, if an All-Night Vigil is served, the Kathisma is completely omitted.

---

## 4. Lord, I Have Cried (Stichera at the Lamplighting Psalms)
**JSON node:** `lord_i_have_cried_10` / `lord_i_have_cried_8`

On *Sundays*, we chant **10 stichera**: the *Resurrection stichera* and the *stichera for the saint* or *feast*, ☨ Glory: *doxastikon* (if any), Now: *Dogmatikon of the tone*.

On *weekdays with a great feast* or a *saint with an all-night vigil*, we chant **8 stichera**: all to the *feast* or to the *saint*, ☨ Glory: *doxastikon*, Now: *Dogmatikon in the tone of the doxastikon*.

On *weekdays with a saint with Polyeleos*, we chant **6 or 8 stichera** according to the provision of the Menaion.

*See Appendix A for the exact mathematical distributions governing Great Vespers.*

---

## 5. The Entrance
**JSON node:** `entrance_great`

*At Great Vespers, an entrance is always made.* At the *Glory be...*, the holy doors are opened. The priest, vested in the phelonion, and the deacon, holding the kadilo, proceed around the altar and exit through the northern door and stand before the holy doors.

---

## 6. O Joyful Light
Sung festively after the Entrance.

---

## 7. Prokeimenon and Readings
**JSON node:** `prokeimenon_readings`

*On Saturday evenings*, the Great Prokeimenon *"The Lord is King"* is sung.

*On feasts and saints with Polyeleos or vigil*, the daily Prokeimenon of the day is sung, followed by 3 Old Testament Readings (Paremiya) to the saint or feast.

*On feasts of the Lord*, festal Paremiya are read.

---

## 8. Litanies
**JSON node:** `litanies_fervent_supplication`

The Fervent Supplication (*"Let us all say"*), *"Vouchsafe, O Lord"*, and the Litany of Supplication (*"Let us complete"*).

---

## 9. The Litiya
**JSON node:** `litiya_rite`

*If the Vespers is served with an all-night vigil*, a procession is made to the narthex where the Litiya petitions and stichera are sung. *If Vespers is standalone*, the Litiya is omitted.

---

## 10. Aposticha
**JSON node:** `aposticha`

*On Sundays*: 4 Resurrection stichera of the Octoechos. ☨ Glory: *doxastikon of the saint* (if any), Now: *Theotokion from the Sunday Aposticha in the tone of the doxastikon*.

*On weekday feasts/vigils*: all stichera to the saint or feast with his refrains. ☨ Glory: *doxastikon*, Now: *Theotokion from the Sunday Aposticha in the tone of the doxastikon*.

*On Sundays in a forefeast, afterfeast, or apodosis*: Resurrection stichera, ☨ Glory, Now: *of the feast*.

*See Appendix B for the complete distribution.*

---

## 11. St. Simeon and Trisagion
**JSON node:** `nunc_dimittis_trisagion`

*"Now lettest Thou Thy servant depart in peace"*, Trisagion, *"Our Father"*.

---

## 12. Troparia
**JSON node:** `artoklasia_rite` (Vigil) / `troparia_resurrectional` (Standalone)

*If the Vespers is served with an all-night vigil*, the Blessing of Loaves (Artoklasia) is performed. The Troparion arrangement at the loaves varies by case. *See Appendix C.*

*If Vespers is standalone*, the troparia are chanted according to the paradigm case. *See Appendix C.*

---

## 13. The Friday Evening Override

On *Friday evening for Saturday*, the *Dogmatikon of the current tone* is always taken at *Both now*, in view of the leavetaking of the tone—except on *feasts of the Lord*, *feasts of the Theotokos*, and on the *leavetaking of the Nativity, Theophany, and Pentecost*, when *Both now* remains *of the feast*.

---

## 14. Conclusion
**JSON node:** `dismissal_vigil` / `dismissal_great`

*If Vigil:* transition to Matins. *If Standalone:* Great Dismissal.

---
---

# § APPENDIX

---

## Appendix A: Lord, I Have Cried — Mathematical Distributions

These rules govern the combination of structural books exclusively for **Great Vespers** (yielding 10 or 8 stichera).

### For 10 Stichera (Saturday Evenings for Sunday)

#### Octoechos & Menaion
- **Sunday + Simple Saint (on 4):** 7 Resurrection, 3 Saint.
- **Sunday + Saint on 6:** 6 Resurrection, 4 Saint.
- **Sunday + Two Saints (on 4):** 4 Resurrection, 3 First Saint, 3 Second Saint.
- **Sunday + Polyeleos or Vigil Saint:** 4 Resurrection, 6 Saint.
- **Sunday + Festal Afterfeast:** 4 Resurrection, 3 Afterfeast, 3 Saint (or 4/6 without saint).
- **Sunday + Theotokos Feast / Apodosis:** 4 Resurrection, 6 Feast.

**Glory/Now Rules:** ☨ Glory: *doxastikon* (if any), Now: *1st Theotokion of the current tone (Dogmatikon)*.

#### Octoechos & Triodion (Lenten Season)
During the Triodion, the Menaion is often suppressed on Saturday nights in favor of the Triodion.
- **Sunday of the Publican and Pharisee:** 7 Resurrection, 3 Triodion.
- **Sunday of the Prodigal Son / Meatfare / Cheesefare:** 6 Resurrection, 4 Triodion.
- **Sundays of Great Lent (Orthodoxy, Cross Veneration):** 6 Resurrection, 4 Triodion.

**Glory/Now Rules (Triodion):** ☨ Glory: *Triodion doxastikon*, Both now: *1st Theotokion of the current tone (Dogmatikon)*.

### For 8 Stichera (Festal & Vigil Weekdays)

- **Weekdays + Great Feast:** 8 Festal. (Octoechos suppressed).
- **Weekdays + Vigil Saint:** 8 Saint. (Octoechos suppressed).
- **Weekdays + Afterfeast & Vigil Saint:** 3 Festal, 5 Saint.

**Glory/Now Rules:** ☨ Glory: *doxastikon*, Now: *1st Theotokion (Dogmatikon) in the tone of the doxastikon*. (Exception: Friday evening for Saturday always takes the Dogmatikon of the current tone to conclude the week).

---

## Appendix B: Aposticha — Mathematical Distributions

### On Sundays (all cases)
*4 Resurrection stichera* of the Octoechos with two refrains from the Horologion. ☨ *Glory*: *doxastikon of the saint or Triodion* (if appointed), *Both now*: *Theotokion from the Sunday Aposticha of the Octoechos, in the tone of the doxastikon*.

### On Sundays with a Forefeast, Afterfeast, or Apodosis
*4 Resurrection stichera*, ☨ *Glory*.. now...: *of the feast (or forefeast/afterfeast)*. 

### On Weekdays with a Vigil or Polyeleos Saint
All stichera to the saint with his refrains. ☨ *Glory*: *doxastikon*, *Both now*: *Theotokion from the Sunday Aposticha in the tone of the doxastikon*.

### On Feasts of the Lord and the Theotokos
All stichera of the feast.

---

## Appendix C: Troparia — Complete Distribution

### At the Blessing of Loaves (Vigil)
- *Feast of the Lord or Theotokos*: Festal Troparion (2x), ☨ Glory.. now.. Festal Troparion (1x)
- *Sunday + Vigil Saint*: **Rejoice, O Virgin Theotokos** (2x), Saint Troparion (1x).
- *Weekday + Vigil Saint*: Saint Troparion (2x), **Rejoice, O Virgin Theotokos** (1x).
- *Saint with Polyeleos*: Saint Troparion (2x), **Rejoice, O Virgin Theotokos** (1x).

### At Standalone Great Vespers (Without Vigil / Artoklasia)
- *Sundays (Simple)*: Resurrection Troparion (1x), ☨ Glory: Saint (1x, if appointed), Both now: Dismissal Theotokion of the tone of the preceding Troparion (or Resurrection Theotokion if no Saint troparion).
- *Sunday + 2 Saints*: Resurrection (1x), Saint A (1x), ☨ Glory: Saint B (1x), Both now: Dismissal Theotokion in tone of Saint B.
- *Feast of the Lord or Theotokos*: Festal Troparion (1x sung alone; 3x is appointed exclusively at the Blessing of Loaves).
