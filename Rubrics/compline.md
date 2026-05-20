# Compline (Small and Great): Typikon Rubrics
## Derived from `01f_struct_compline.json` nodes, verified against Dolnytsky Parts I & IV

> This file contains two layers:
> - **§ Inline Rubrics** — compact instructions for placement directly into the service book at each structural node.
> - **§ Appendix** — exhaustive, case-by-case encyclopedia entries.

---

# § INLINE RUBRICS: SMALL COMPLINE

These are placed directly in the Word document at the corresponding structural point for standard Small Compline.

---

## 1. Opening and Psalmody
**JSON node:** `psalms_compline`

The priest vests in the **epitrachelion only**. The holy doors remain **closed**.
The priest stands before the closed holy doors, makes a small bow, and gives the common blessing: *"Blessed is our God..."*
Following the introductory prayers (*"O Heavenly King,"* Trisagion, etc.) and *"Come, let us worship"*, Psalms 50, 69, and 142 are read. Then the Small Doxology is read. The priest performs no censing.

---

## 2. The Creed
**JSON node:** `creed`

The Nicene-Constantinopolitan Creed (*"I believe in one God..."*) is read.

---

## 3. The Canon
**JSON node:** `canon_slot`

The appropriate Canon is chanted. Every Ode is read with the Irmos on 5, without Katavasias and without Litanies.
- *On ordinary weekdays (Mon-Thu):* The Canon to the Theotokos from the Octoechos (current tone) is read.
- *In a Forefeast/Afterfeast:* The Canon to the Forefeast/Feast is read instead.
*(See Appendix for Lenten exceptions).*

---

## 4. Hymns of the Theotokos and Troparia
**JSON node:** `troparia_slot`

*"It is truly meet"* is sung. The Trisagion is read. 
Following the *"Our Father"*, the appropriate troparia are read. 

*On ordinary weekdays:*
1. Troparion of the Temple.
2. Troparion of the Day of the Week.
3. Troparion of the Saint (from the Menaion).
4. ☨ Glory: Kontakion of the Saint.
5. Now: Kontakion of the Day.

*If it is a Forefeast:* Forefeast troparion, ☨ Glory... Now: Forefeast kontakion.
*On Saturday evening:* The Resurrection kontakion of the tone of the week is read.
*On a Sunday coinciding with a Feast:* The Hypakoe of the Resurrectional tone is read immediately after the Trisagion/Our Father, followed by ☨ Glory... Now: Kontakion of the Feast.

---

## 5. Conclusion
**JSON node:** `prayers_final`, `dismissal_sequence`

*"Lord, have mercy" (40 times)*.
The final prayers of Compline are read (*"O spotless, undefiled..."* and *"And grant unto us, O Master..."*).
The priest, standing before the closed holy doors, gives the Small Dismissal with Litany.

---
---

# § INLINE RUBRICS: GREAT COMPLINE

Great Compline is served during the weekdays of Great Lent and on the eves of the Nativity and Theophany (as part of a Vigil).

---

## 1. Part I: The Six Psalms and "God is with us"
**JSON node:** `part_1`

The priest vests in the **epitrachelion only**.
**[If served as a Festal Vigil (Nativity/Theophany/Annunciation):]**
The holy doors are opened. The priest/deacon performs a great censing of the entire church. Immediately after the exclamation *"Blessed is our God,"* the holy doors are **closed**. They remain closed until the Litiya at the end of the service.
**[If served during Great Lent:]**
The holy doors remain **closed**. There is no censing. The priest stands before the doors and exclaims *"Blessed is our God."*

Following the introductory prayers and *"Come let us worship..."*, the six psalms of Great Compline are read (Psalms 4, 6, 12, 24, 30, and 90).

The choir then sings **"God is with us"** in the appropriate melody (Lenten or Festal).
The troparia (*"The day being passed..."*) are sung, the Creed is read, and the Trisagion is read.

*Lenten interpolation:* The troparia *"Lighten mine eyes"* and *"Have mercy on us, O Lord, have mercy on us"* are sung.
*(If part of a Vigil:* The Festal Troparion is sung instead).

---

## 2. Part II: The Repentant Psalms
**JSON node:** `part_2`

Psalms 50 and 101, followed by the Prayer of Manasses, are read. The Trisagion is read.

*Lenten interpolation:* The kontakion *"Have mercy on us, O Lord"* is read.
*(If part of a Vigil:* The Festal Kontakion is read instead).

---

## 3. Part III: Praise and St. Ephrem
**JSON node:** `part_3`

Psalms 69 and 142 are read, followed by the Small Doxology.
The Canon to the Theotokos of the current tone is read.

After the Trisagion, the choir sings **"O Lord of Hosts, be with us"** (Tone 6 Lenten melody).
*(If part of a Festal Vigil: The Feast Kontakion is sung instead, and the service transitions directly to the Litiya and Artoklasia).*

*During Great Lent:* The **Prayer of St. Ephrem the Syrian** (*"O Lord and Master of my life..."*) is recited by the priest standing in the middle of the church before the closed holy doors. He makes **3 great prostrations**, followed by **12 small bows** (saying *"O God, cleanse me a sinner"*), concluding with the entire prayer again and **1 final great prostration**.

The Great Compline dismissal is given.

---
---

# § APPENDIX

---

## Appendix A: The Great Canon of St. Andrew of Crete

During the First Week of Great Lent (Monday through Thursday), the **Great Canon of St. Andrew** is interpolated into Great Compline immediately after Psalm 69 (before the Six Psalms of Part I).

The Canon is divided into four portions across the four days.

On **Thursday of the Fifth Week of Great Lent**, the *entire* Great Canon is typically read at Matins, not Compline (though local customs may vary). When at Matins, it is governed by the Triodion rubrics for the "Matins of the Great Canon."
