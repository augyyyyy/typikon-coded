# Midnight Office (Mesonyktikon): Typikon Rubrics
## Derived from `01g_struct_midnight.json` nodes, verified against Dolnytsky Parts I & IV

> This file contains two layers:
> - **§ Inline Rubrics** — compact instructions for placement directly into the service book at each structural node.
> - **§ Appendix** — exhaustive, case-by-case encyclopedia entries.

---

# § INLINE RUBRICS: STANDARD MIDNIGHT OFFICE

These are placed directly in the Word document at the corresponding structural point.

---

## 1. Opening and Psalm 50
**JSON node:** `trisagion_prayers`, `horologion.psalm_50`

The priest vests in the **epitrachelion only**. The holy doors remain **closed**.
The priest stands before the closed holy doors, makes a small bow, and gives the common blessing: *"Blessed is our God..."*
Following the introductory prayers (*"O Heavenly King,"* Trisagion, etc.) and *"Come, let us worship"*, Psalm 50 is read. The priest performs no censing.

---

## 2. The Kathisma / Canon
**JSON node:** `horologion.kathisma_17`

- *On ordinary weekdays (Mon-Fri):* **Kathisma 17** (Psalm 118, "Blessed are the undefiled") is read in its entirety.
- *On Saturday (Friday night):* **Kathisma 9** is read instead of Kathisma 17.
- *On Sunday (Saturday night):* The Kathisma is omitted entirely. Instead, the **Triadic Canon** (Canon to the Holy Trinity) in the current tone of the Octoechos is chanted.

---

## 3. The Creed and Troparia
**JSON node:** `creed`, `troparia_block`

The Nicene-Constantinopolitan Creed is read. Following the Trisagion and *"Our Father"*, specific troparia are read based on the day:

- *On ordinary weekdays:* *"Behold, the Bridegroom cometh at midnight..."*
- *On Saturday:* The abbreviated troparia for the reposed (*"O Thou Who by the depth of Thy wisdom..."*).
- *On Sunday:* The Resurrectional Hypakoe of the tone of the week.

Thereafter, *"Thou Who at every season..."* is read.

---

## 4. The Closing Prayer (Part I)
**JSON node:** `closing_prayer`

The priest reads the prayer appropriate to the day:
- *Weekdays and Saturday:* *"O Lord God Almighty, Who receivest confession..."*
- *Sunday:* The specific prayer to the Holy Trinity determined by the Triadic Canon.

---

## 5. Part II: Prayers for the Departed 
**JSON node:** `part_ii_block`

*This entire section is OMITTED on Saturdays and Sundays.*

On weekdays, Part II begins with *"Come let us worship..."* followed by Psalms 120 and 133.
After the Trisagion and *"Our Father"*, the troparia for the reposed are read (*"Remember, O Lord, the souls of Thy servants..."*).
The priest reads the prayer for the departed.

---

## 6. Lenten Interpolation and Dismissal
**JSON node:** `prayer_st_ephrem`, `dismissal`

*During Great Lent (Monday through Friday):* The **Prayer of St. Ephrem the Syrian** is recited by the priest standing in the middle of the church before the closed holy doors. He makes **3 great prostrations**, followed by **12 small bows** (saying *"O God, cleanse me a sinner"*), concluding with the entire prayer again and **1 final great prostration**.

The priest, standing before the closed holy doors, gives the Small Dismissal with Litany (*"Have mercy on us, O God..."*).

---
---

# § APPENDIX

---

## Appendix A: The Holy Saturday "Tomb" Midnight Office

The Midnight Office served on Holy Saturday night (technically early Sunday morning before Paschal Matins) follows a completely unique structure, focused on the Holy Shroud (Plaschanitsa) situated in the middle of the church.

### 1. Opening
The service begins as usual with the blessing, Trisagion prayers, and Psalm 50, read before the Holy Shroud.

### 2. The Tomb Canon
The entire **Canon of Holy Saturday** (*"He Who closed the abyss lies dead..."*) is chanted. This replaces Kathisma 17 or the Triadic Canon.
During the 9th Ode of this canon, the clergy incense the Holy Shroud.

### 3. The Transfer to the Altar
At the conclusion of the 9th Ode and the subsequent Trisagion, while the troparion *"When Thou didst descend unto death..."* is sung, the bishop/priest lifts the Holy Shroud from the tomb. It is carried into the sanctuary through the holy doors and laid upon the holy table, where it will remain until the Ascension.

### 4. Dismissal
The dismissal of Holy Saturday is given. The clergy then immediately vest in bright vestments for the commencement of Paschal Matins.
