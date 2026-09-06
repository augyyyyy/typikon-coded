# Daily Vespers: Typikon Rubrics
## Derived from `01h_struct_vespers.json` nodes, verified against Dolnytsky Part II

> This file contains two layers:
> - **§ Inline Rubrics** — compact instructions for placement directly into the service book at each structural node.
> - **§ Appendix** — exhaustive, case-by-case encyclopedia entries.

---

# § INLINE RUBRICS

These are placed directly in the Word document at the corresponding structural point.

---

## 1. The Enarxis (Opening) & Psalm 103
**JSON node:** `beginning_daily` / `psalm_103_simple`

The priest vests in the **epitrachelion only** (never the phelonion). The holy doors are **never opened** at this service.
He exits through the northern door and stands before the closed holy doors. Making a small bow, he exclaims *"Blessed is our God..."*
Following the choir's "Amen" and introductory prayers, Psalm 103 is read simply by the reader, not sung. The priest remains standing before the closed holy doors to read the Prayers of Light silently.

---

## 3. The Kathisma
**JSON node:** `kathisma_daily`

The stichology of the Psalter at Daily Vespers follows the canonical 4-season matrix (*Dolnytsky Part I §2 / Typikon Chapter 17*):
- **Summer Season (All Saints to Sep 21)**: Mon Eve Kathisma 6; Tue Eve Kathisma 9; Wed Eve Kathisma 12; Thu Eve Kathisma 15; Fri Eve Kathisma 18; Sat Eve Kathisma 1; Sun Eve None.
- **Winter Season (Sep 22 to Dec 19 / Jan 15 to Cheesefare)**: Weekday Evenings (Mon–Fri) Kathisma 18.
- **Lenten Season (Great Lent)**: Sunday Eve Kathisma 4; Weekday Evenings (Mon–Fri) Kathisma 18.
- **Bright Week & Great Feasts of the Lord**: Psalter stichology is completely suppressed.

---

## 4. Lord, I Have Cried (Stichera at the Lamplighting Psalms) & Censing
**JSON node:** `lord_i_have_cried_6`

*At Daily Vespers, the count of stichera is always 6.*
The priest performs the standard censing (the entire church) during the singing of "Lord, I have cried". This is the **only** censing prescribed at Daily Vespers.

On *ordinary weekdays* (Mon–Fri) with a *simple saint*, we chant **6 stichera**: *3 daily stichera* of the Octoechos and *3 stichera for the saint*, ☨ Glory... Now... the *theotokion* (on Wednesday and Friday, the *stavrotheotokion*).

If there are *two saints*, the Octoechos is suppressed, and we chant **6 stichera**: *3 for the first saint* and *3 for the second saint*, ☨ Glory... Now... the *theotokion* (or *stavrotheotokion*).

If it be a *saint on 6*, the Octoechos is suppressed, and all **6 stichera** are sung to the saint, ☨ Glory: his *doxastikon*, Now... the *theotokion in the tone of the doxastikon and of the day of the week*.

*See Appendix A for the exact mathematical distributions governing Daily Vespers (6 stichera).*

---

## 5. O Joyful Light
**JSON node:** `entrance_suppression` (Small Vespers) / *(No specific node in Daily Vespers until Prokeimenon)*

**There is no Entrance.** Consequently, the Prayer of the Entrance is omitted.
The priest exits the sanctuary via the northern door to stand before the closed holy doors. When the stichera conclude, he exclaims *"Wisdom! Upright!"*
Because there is no Entrance, the hymn *"O Joyful Light"* is usually read rather than sung.

---

## 6. Prokeimenon & Vouchsafe, O Lord
**JSON node:** `prokeimenon_daily` / `vouchsafe_read`

Immediately following "O Joyful Light", the priest (still before the doors) exclaims *"Let us be attentive! Peace be unto all!"* and, turning to the people, blesses them. Then *"Wisdom! Let us be attentive!"*
The daily Prokeimenon is sung. There are no Old Testament readings (Paremiya). 
*Note: The litany "Let us say all" is strictly omitted here.*
*"Vouchsafe, O Lord"* is read by the reader immediately following the Prokeimenon.

---

## 8. Aposticha
**JSON node:** `aposticha`

All stichera from the Octoechos for the day of the week, with their usual refrains. 
☨ Glory: *doxastikon of the saint* (if any), Now: *theotokion of the Aposticha of the Octoechos, in the tone of the doxastikon and the day of the week*.
If there is no doxastikon to the saint, ☨ Glory... Now: *theotokion of the Aposticha (or stavrotheotokion on Wed/Fri)*.

---

## 9. St. Simeon and Trisagion
**JSON node:** `nunc_dimittis_read`, `trisagion`

*"Now lettest Thou Thy servant depart in peace"* (read). Trisagion, *"Our Father"*.

---

## 10. Troparia
**JSON node:** `troparia_daily`

Troparion of the saint. ☨ Glory... Now: *Dismissal Theotokion from the Horologion, in the tone of the saint’s troparion and of the day of the week*.

If there are *two saints*: Troparion of the first saint, ☨ Glory: *troparion of the second saint*, Now: *Dismissal Theotokion in the tone of the second saint and of the day of the week.*

---

## 10. Conclusion & Dismissal
**JSON node:** `dismissal_daily`

The litany *"Have mercy on us, O God"* is sung (which replaces its omission earlier). 
The priest makes the middle dismissal from before the holy doors (*"Wisdom!" "More honorable..."*). Upon exclaiming *"Christ our True God,"* the priest turns to the people, and concluding the dismissal, enters the sanctuary via the southern door.

---
---

# § APPENDIX

---

## Appendix A: Lord, I Have Cried — Mathematical Distributions

These rules govern the combination of structural books exclusively for **Daily Vespers**. At Daily Vespers, the count of stichera is always exactly **6**.

### Octoechos & Menaion Distributions

- **Ordinary Weekday (Mon–Fri) + Simple Saint:** 3 Octoechos, 3 Menaion.
- **Ordinary Weekday (Mon–Fri) + Two Saints:** 3 First Saint, 3 Second Saint (Octoechos suppressed).
- **Ordinary Weekday (Mon–Fri) + Saint on 6:** 6 Saint (Octoechos suppressed).
- **Friday Evening for Saturday + Simple Saint:** 3 Saint, 3 Octoechos *(reverse of weekday order)*.
- **Friday Evening for Saturday + Two Saints:** 3 First Saint, 3 Second Saint.
- **Friday Evening for Saturday + Saint on 6:** 6 Saint.
- **Weekday + Forefeast/Afterfeast + Simple Saint:** 3 Feast, 3 Saint.
- **Weekday + Forefeast/Afterfeast + Two Saints (or on 6):** 3 First Saint, 3 Second Saint (or 3 Feast, 3 Saint if capped).
- **Weekday + Apodosis (Leavetaking):** 6 Feast.

**Glory/Now Rules (Weekdays):** ☨ Glory: *doxastikon* (if any), Now: *Theotokion/Stavrotheotokion in the tone of the doxastikon and the day of the week*.
**Glory/Now Rules (Friday Evening for Saturday):** ☨ Glory: *doxastikon* (if any), Now: *1st Theotokion of the current tone being taken leave of (Dogmatikon of the past Sunday).*

### Triodion Distributions (Lenten Season)

During Great Lent, Daily Vespers takes on a penitential character (Lenten Vespers/Presanctified). The daily stichera of the Octoechos are suppressed in favor of the Triodion.

- **Lenten Weekdays (Mon-Fri) + Simple Saint:** 3 Triodion, 3 Menaion Saint.
- **Holy Week (Mon-Wed):** 6 Triodion. 

**Glory/Now Rules (Triodion):** ☨ Glory: *doxastikon of the saint* (if any), Now: *Theotokion in tone of the Doxastikon*. If no doxastikon, ☨ Glory... Now... *Triodion Theotokion*.
