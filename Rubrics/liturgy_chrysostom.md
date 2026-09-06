# Divine Liturgy of St. John Chrysostom: Typikon Rubrics
## Derived from `01j_struct_liturgy.json` nodes, verified against Dolnytsky Parts I & II

> This file contains two layers:
> - **§ Inline Rubrics** — compact instructions for placement directly into the service book at each structural node.
> - **§ Appendix** — exhaustive, case-by-case encyclopedia entries.

---

# § INLINE RUBRICS

These are placed directly in the Word document at the corresponding structural point.

---

## 1. The Prothesis
**JSON node:** `prothesis`

The priest and deacon prepare the Holy Gifts at the proskomedia table. *On Sundays and Feasts*, the priest cuts the Lamb for the communicants. *On Holy Thursday*, two Lambs are prepared (the second Lamb is consecrated and reserved for the Viaticum and communion of the sick throughout the entire liturgical year per *Ordo Celebrationis §142*). The deacon pours the wine and water and covers the Gifts.

---

## 2. The Opening
**JSON node:** `opening_blessing`

The holy doors and the curtain are opened. The deacon exclaims *"Bless, Master!"* The priest lifts the Gospel Book, makes the sign of the cross over the Antimension, and exclaims *"Blessed is the Kingdom..."*

---

## 3. The Antiphons
**JSON node:** `antiphons_block`

Following the Great Litany, the Antiphons are sung.
*On ordinary Sundays and weekdays*, the Typical Antiphons (Psalms 102 and 145) and the Beatitudes are sung.
*On Great Feasts of the Lord*, the Festal Antiphons (proper psalms assigned to the feast) are sung.
*On Temple Feasts*, the special Temple Antiphons may be sung.

The deacon stands at his usual place and intones the Small Litanies between the Antiphons.

---

## 4. The Little Entrance
**JSON node:** `little_entrance`

The priest recites the Prayer of the Entrance silently and blesses the Entrance. 
**Physical Choreography:** The priest and deacon, preceded by candle-bearers, exit the sanctuary via the **northern door** and proceed to the center of the solea, standing before the holy doors. 
The deacon, elevating the Gospel Book, exclaims *"Wisdom! Stand aright!"* and they enter the sanctuary through the holy doors.

The Entrance Hymn *"Come let us worship..."* is sung. 
- *On Sundays:* "...save us, O Son of God, Who art risen from the dead..."
- *On Weekdays:* "...Who art wondrous in Thy saints..."
- *On Feasts of the Lord:* A proper festal variant is sung.
- *(During Pascha: The Entrance Hymn is replaced entirely by "Christ is risen...").*

---

## 5. Troparia and Kontakia
**JSON node:** `troparia_kontakia_block`

The troparia and kontakia are sung according to a strict order of precedence (usually: Resurrection/Temple, Day, Saint, then Kontakia).
*See Appendix A for precedence rules.*

---

## 6. The Trisagion
**JSON node:** `trisagion_module`

The priest recites the Prayer of the Trisagion silently. The choir sings *"Holy God..."*
*Exception:* On Nativity, Theophany, Pascha, and Pentecost (and Bright Week), it is replaced by *"As many as have been baptized into Christ..."* On the Exaltation of the Cross and Veneration of the Cross, it is replaced by *"Before Thy Cross..."*

---

## 7. The Readings (Prokeimenon, Epistle, Alleluia, Gospel)
**JSON node:** `readings_block`

The reader intones the **Prokeimenon** (in the appointed tone).
The reader chants the **Epistle**. The priest sits.
The choir sings the **Alleluia** with its verses. The deacon censes the altar and the people.
The deacon reads the **Gospel** from the ambo. The priest stands.

*If multiple commemorations occur (e.g., Sunday + Saint), two Epistles and two Gospels may be read. If it is a Great Feast, only the Festal readings are used.*

---

## 8. The Cherubic Hymn and Great Entrance
**JSON nodes:** `cherubic_hymn_block`, `great_entrance`

Following the Litanies for the Catechumens and Faithful, the choir sings the Cherubic Hymn: *"Let us who mystically represent the Cherubim..."*
*(On Holy Thursday: replaced by "Of Thy Mystical Supper." On Holy Saturday: replaced by "Let all mortal flesh keep silence").*

The deacon does a full censing of the altar and church while reciting Psalm 50. The priest recites the prayer of the Cherubic Hymn silently.
**Physical Choreography:** The Great Entrance is made. The deacon carries the diskos and the priest carries the chalice. They exit the sanctuary via the **northern door** and process to the center of the solea, standing together facing the people.
They exclaim the prescribed commemorations for the hierarchs, state, and people, before entering through the holy doors to place the Gifts on the altar.

---

## 9. The Anaphora
**JSON node:** `anaphora_block`

The Anaphora of St. John Chrysostom is celebrated.

---

## 10. The Megalynarion (Zadostoinyk)
**JSON node:** `megalynarion_block`

*Usually*, the choir sings the Megalynarion (Axion Estin): *"It is truly meet to bless thee, O Theotokos..."*
*On Great Feasts (and their afterfeasts/leavetakings)*, the Heirmos of the 9th Ode of the Feast's Canon is sung instead.
*During the Paschal season*, *"The Angel Cried..."* is sung.

---

## 11. Communion
**JSON node:** `communion_module`

Following the Lord's Prayer and *"Holy Things for the Holy"*, the choir sings the **Communion Hymn (Kinonikon)**.
- *Sundays:* *"Praise the Lord from the heavens..."*
- *Weekdays:* The proper hymn of the day.
- *Feasts:* The festal proper.

The priest breaks the Lamb and communes himself and the deacon.
The deacon exclaims *"With the fear of God and with faith, draw near!"* and the faithful are communed while the choir sings *"Receive the Body of Christ..."*

---

## 12. Post-Communion and Dismissal
**JSON nodes:** `post_communion`, `dismissal`

The choir sings *"We have seen the true light..."*
*(From Pascha to Ascension Eve: replaced by "Christ is risen from the dead" (1x). From Ascension to its Leavetaking: replaced by the Troparion of Ascension. From Theophany to its Leavetaking: replaced by the Troparion of Theophany. From Nativity to its Leavetaking: replaced by the Troparion of the Nativity per Ordo Celebrationis §98).*

The priest reads the Ambo Prayer.
The priest gives the Dismissal, blessing the people with the hand cross (on Sundays/Feasts) or his hand (on weekdays). The preamble of the dismissal varies by season (e.g., *"May Christ our true God, risen from the dead..."* for Sundays).

---
---

# § APPENDIX

---

## Appendix A: Precedence of Troparia and Kontakia at the Little Entrance
*(Dolnytsky Part V §1 & Ordo Celebrationis §§62–67)*

When multiple commemorations occur on the same day, the troparia and kontakia at the Little Entrance are chanted in the following canonical order based on the Temple dedication:

### 1. In a Temple Dedicated to the Lord:
- *On Sunday:* Sunday Troparion, then Troparion of the Saint of the day (Temple Troparion is omitted). ☨ Glory: Kontakion of the Saint, Both now: Sunday Kontakion (or "Steadfast Protectress").

### 2. In a Temple Dedicated to the Theotokos:
- *On Sunday:* Sunday Troparion, then Temple Troparion of the Theotokos, then Troparion of the Saint. ☨ Glory: Kontakion of the Saint, Both now: Temple Kontakion of the Theotokos.

### 3. In a Temple Dedicated to a Saint:
- *On Sunday:* Sunday Troparion, then Troparion of the Saint of the day (Temple Troparion of the Patron is omitted). ☨ Glory: Kontakion of the Saint of the day, Both now: "Steadfast Protectress of Christians" (or Sunday Kontakion).

### 4. On a Great Feast of the Lord:
- Festal Troparion (1x). ☨ Glory.. now.. Festal Kontakion (1x). All other troparia and kontakia are suppressed.
