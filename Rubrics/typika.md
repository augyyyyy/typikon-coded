# The Typika (Obidnytsia): Typikon Rubrics
## Derived from `01e_struct_typika.json` nodes, verified against Dolnytsky Parts I & IV

> This file contains two layers:
> - **§ Inline Rubrics** — compact instructions for placement directly into the service book at each structural node.
> - **§ Appendix** — exhaustive, case-by-case encyclopedia entries.

---

# § INLINE RUBRICS: STANDARD TYPIKA

The Typika (or "Obidnytsia") is celebrated on days when the Divine Liturgy is not served, or as an act of devotion.

---

## 1. Opening and Psalmody
**JSON nodes:** `opening_blessing`, `horologion.psalm_102`, `horologion.psalm_145`, `only_begotten`

The priest vests in the **epitrachelion only**. The holy doors remain **closed**. There is no censing.
*If the Typika is served as a standalone service*, the priest stands before the closed holy doors, makes a small bow, and gives the blessing: *"Blessed is our God..."* followed by the introductory Trisagion prayers. *If it immediately follows the Sixth or Ninth Hour without interruption, the blessing and introductory prayers are omitted.*

Psalms 102 and 145 are read simply by the reader, not sung.
The hymn *"Only-Begotten Son"* is read.

---

## 2. The Beatitudes
**JSON node:** `beatitudes_block`

The Beatitudes (*"In Thy Kingdom remember us, O Lord..."*) are read. 

---

## 3. The Readings
**JSON node:** `readings_module`

*If the Typika is taking the place of the Divine Liturgy for the day*, the appointed readings for the day are read:
1. The Prokeimenon.
2. The Epistle.
3. The Alleluia (with verses).
4. The Gospel.

*(If the Typika is served merely for devotion and not replacing a Liturgy, these readings are omitted).*

---

## 4. The Prayers of Communion
**JSON node:** `communion_module`

The choir or reader chants: 
- *"Remember us, O Lord, when Thou comest into Thy Kingdom."*
- *"Remember us, O Master..."*
- *"Remember us, O Holy One..."*
- *"The heavenly choir praises Thee..."*
- *"Come unto Him, and be enlightened..."*
- *"The heavenly choir praises Thee..."*

The **Nicene-Constantinopolitan Creed** is read.
The prayer *"Remit, pardon, forgive, O God..."* is read, followed by *"Our Father."*

---

## 5. The Kontakia
**JSON nodes:** `kontakion_block`, `theotokion_typika`

After the *"Our Father"*, the kontakia are read instead of troparia.
**General Order:** 
1. Kontakion of the Temple.
2. Kontakion of the Day of the week.
3. Kontakion of the Saint of the day.
4. ☨ Glory... Now.
5. Fixed Theotokion: *"O Protection of Christians unashamed..."*
*(Note: If the temple is dedicated to the Lord or the Theotokos, its kontakion replaces "O Protection" at the end).*

---

## 6. Conclusion
**JSON node:** `conclusion_standard`

*"Lord, have mercy" (12 times)* (Wait: According to typical usage, 40 times is for Lent, usually 12 times or 40 times).
*"Blessed be the name of the Lord" (3x)*.
Psalm 33 is read.
The priest gives the Dismissal.

---
---

# § INLINE RUBRICS: LENTEN TYPIKA

During the weekdays of Great Lent, the Typika is strictly attached to the Ninth Hour.

---

## 1. The Beatitudes
**JSON node:** `beatitudes_lenten`

Following the conclusion of the Ninth Hour, the Beatitudes are chanted quickly and simply.
*Rubric:* The people make a small prostration (metania) at each verse of the Beatitudes.

At the conclusion of the Beatitudes, the choir sings loudly and solemnly: *"Remember us, O Lord, when Thou comest into Thy Kingdom."* 
*Rubric:* All make three great prostrations to the earth while these three petitions are sung.

---

## 2. The Creed and Prayers
**JSON node:** `creed_lenten`

*"The heavenly choir praises Thee..."*
The Creed (*"I believe in one God..."*) is read.
The prayer *"Remit, pardon, forgive..."* is read.
The *"Our Father."*

---

## 3. Lenten Kontakia and St. Ephrem
**JSON nodes:** `kontakia_lenten`, `prayer_st_ephrem`

Specific Lenten kontakia are read:
1. Kontakion of the Transfiguration.
2. Kontakion of the Day.
3. Kontakion of the Temple (Saint).
4. ☨ Theotokion of the tone.

*"Lord, have mercy" (40 times)*.
The **Prayer of St. Ephrem the Syrian** (*"O Lord and Master of my life..."*) is recited by the priest standing in the middle of the church before the closed holy doors. He makes **3 great prostrations**, followed by **12 small bows** (saying *"O God, cleanse me a sinner"*), concluding with the entire prayer again and **1 final great prostration**.

---

## 4. The Final Prayer and Dismissal
**JSON node:** `final_prayer_block`, `dismissal_lenten`

Immediately following the final prostration, the Trisagion is read, followed by *"Our Father"*.
*"Lord, have mercy" (12 times)*.
The **Prayer of the Ninth Hour** (*"O Master, Lord Jesus Christ our God, Who hast been long-suffering..."*) is read here. *(It is explicitly moved from its usual place in the 9th Hour to the end of the Typika in the Lenten order).*

The Lenten Dismissal is given.
