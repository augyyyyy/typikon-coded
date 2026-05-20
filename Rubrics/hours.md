# The Minor Hours (1st, 3rd, 6th, 9th): Typikon Rubrics
## Derived from `01[a-d]_struct_hour_[1,3,6,9].json`, verified against Dolnytsky Part I

> This file contains two layers:
> - **§ Inline Rubrics** — compact instructions for placement directly into the service book at each structural node.
> - **§ Appendix** — exhaustive, case-by-case encyclopedia entries.

---

# § INLINE RUBRICS

These are placed directly in the Word document at the corresponding structural point.

---

## 1. Opening
**JSON node:** `opening_hour_1 / 3 / 6 / 9`

The priest vests in the **epitrachelion only**. The holy doors remain **closed** and the priest performs no censing.
*The First Hour* typically follows Matins immediately; it begins with *"Come, let us worship"* without an initial blessing.
*The 3rd, 6th, and 9th Hours* begin with the priest standing before the closed holy doors, making a small bow, and giving the blessing: *"Blessed is our God..."* followed by the introductory prayers (*"O Heavenly King,"* Trisagion, etc.) and *"Come, let us worship..."*

---

## 2. The Psalms of the Hour
**JSON node:** `psalms_hour_X`

Three psalms are read depending on the hour.
- **1st Hour:** Psalms 5, 89, 100
- **3rd Hour:** Psalms 16, 24, 50
- **6th Hour:** Psalms 53, 54, 90
- **9th Hour:** Psalms 83, 84, 85

*(Note: On the Eves of Nativity and Theophany, and on Great Friday, "Royal Hours" are served with special proper psalms replacing the standard array).*

---

## 3. Troparia
**JSON node:** `troparia_block`

If there is only **one troparion**, it is read after the psalms. ☨ Glory... Now: *The fixed Theotokion of the Hour.*
If there are **two troparia**, the first is read, ☨ Glory: *the second is read*, Now: *Theotokion of the Hour.*

*See Appendix A for the logic resolving which troparia to read when multiple feasts collide.*

**Fixed Theotokia of the Hours:**
- 1st: *"What shall we call thee, O Full of Grace?"*
- 3rd: *"O Theotokos, thou art the true vine..."*
- 6th: *"Seeing that we have no boldness..."*
- 9th: *"Who was born of a Virgin..."*

---

## 4. Let Thy compassions / Let Thy tender mercies / Deliver us not up
Following the Theotokion, a specific short prayer is read:
- 1st: *"Direct my steps..."*
- 3rd: *"Blessed is the Lord God..."*
- 6th: *"Let Thy compassions quickly anticipate us..."*
- 9th: *"Deliver us not up utterly..."*

---

## 5. The Trisagion Block
**JSON node:** `trisagion_our_father`

The Trisagion is read, followed by *"Most Holy Trinity"*, and *"Our Father."*

---

## 6. The Kontakion
**JSON node:** `kontakion_block`

A single Kontakion is read after the *"Our Father."* Unlike troparia, you may never read two kontakia at the Hours; they must rotate throughout the day.
*See Appendix A for the rotation rules.*

---

## 7. The Conclusion of the Hour
**JSON node:** `conclusion_block`

*"Lord, have mercy"* (40 times).
*"Thou Who at every season and every hour..."*
*"Lord, have mercy"* (3 times), ☨ Glory... Now.
*"More honorable than the Cherubim..."*
*"In the name of the Lord, Father, bless."*
The Priest proclaims the exclamation (*"God be bountiful to us..."*).

---

## 8. The Prayer of the Hour
**JSON node:** `prayer_of_hour`

*(In Great Lent, the **Prayer of St. Ephrem the Syrian** is interpolated here. The priest stands in the middle of the church before the closed doors. He makes **3 great prostrations**, followed by **12 small bows**, concluding with the entire prayer again and **1 final great prostration**).*

The specific prayer corresponding to each hour is then read from before the doors:
- 1st Hour: *"O Christ, the True Light..."*
- 3rd Hour: *"O Master, God the Father Almighty..."*
- 6th Hour: *"O God and Lord of Hosts..."*
- 9th Hour: *"O Master, Lord Jesus Christ our God..."*

The dismissal is then given.

---
---

# § APPENDIX

---

## Appendix A: Troparia and Kontakia Collisions & Rotations

The Typikon strictly governs which hymns "win" the slots at each Hour. The general rule is that Troparia stack (up to two), but Kontakia rotate by hour.

### 1. Great Feasts of the Lord and the Theotokos
*At all hours (1st, 3rd, 6th, and 9th):*
- **Troparion:** The Festal Troparion only. (No other troparion is sung, even if it is Sunday).
- **Kontakion:** The Festal Kontakion only.

### 2. Standard Sunday (with a simple saint)
- **Troparia:** At every hour, the Resurrection Troparion is read first. 
  - 1st Hour: ☨ Glory... Now: *Theotokion of the Hour*.
  - 3rd, 6th, 9th Hour: ☨ Glory: *Saint's Troparion*. Now: *Theotokion of the Hour*.
- **Kontakia:** Alternate by hour.
  - 1st Hour: **Resurrection**
  - 3rd Hour: **Saint**
  - 6th Hour: **Temple Patron**
  - 9th Hour: **Resurrection**

### 3. Standard Sunday with Two Saints
- **Troparia:** At every hour, the Resurrection Troparion is read first. 
  - 3rd Hour: ☨ Glory: *1st Saint's Troparion*.
  - 6th Hour: ☨ Glory: *Temple Troparion*.
  - 9th Hour: ☨ Glory: *2nd Saint's Troparion*.
- **Kontakia:**
  - 1st Hour: **Resurrection**
  - 3rd Hour: **1st Saint**
  - 6th Hour: **Temple Patron**
  - 9th Hour: **2nd Saint**

### 4. Standard Weekday (Mon–Fri)
- **Troparia:**
  - 1st Hour: Day of the Week
  - 3rd Hour: Saint (Menaion)
  - 6th Hour: Temple Patron
  - 9th Hour: Saint (Menaion)
- **Kontakia:** Match the Troparion of the respective hour.

### 5. Sunday in an Afterfeast
- **Troparia:** At every hour, the Resurrection Troparion is read first.
  - 1st Hour: ☨ Glory: *Feast Troparion*.
  - 3rd Hour: ☨ Glory: *Saint's Troparion*.
  - 6th Hour: ☨ Glory: *Feast Troparion*.
  - 9th Hour: ☨ Glory: *Saint's Troparion*.
- **Kontakia:**
  - 1st Hour: **Feast**
  - 3rd Hour: **Resurrection**
  - 6th Hour: **Feast**
  - 9th Hour: **Resurrection**

### 6. Sunday in an Afterfeast WITH a Polyeleos Saint
- **Troparia:** At every hour, the Resurrection Troparion is read first.
  - 1st Hour: ☨ Glory: *Feast Troparion*.
  - 3rd Hour: ☨ Glory: *Saint's Troparion*.
  - 6th Hour: ☨ Glory: *Feast Troparion*.
  - 9th Hour: ☨ Glory: *Saint's Troparion*.
- **Kontakia:** A unique three-way rotation.
  - 1st Hour: **Resurrection**
  - 3rd Hour: **Feast**
  - 6th Hour: **Saint**
  - 9th Hour: **Resurrection**
