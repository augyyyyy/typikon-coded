# Proposed Encyclopedia Topics: Deep Logic Expansion

The following topics are prioritized by **Horologion** components (Hours, Compline, Midnight Office, Typika) as requested, followed by the General Liturgical Engines.

## SECTION A: HOROLOGION LOGIC (The Priority List)

### 1. Encyclopedia of Hours Collision (Troparia & Kontakia)
*   **The Problem:** The Hours only allow for specific "Glory" and "Both Now" slots, creating collisions when we have Sunday + Feast + Saint.
*   **Deep Logic:**
    *   *Troparia:* How to alternate "Glory" between Resurrection, Feast, and Saint. (e.g., "Glory... Resurrection, Both now... Theotokion of Hour. [Trisagion]. Glory... Saint...").
    *   *Kontakia:* The "One Standard" rule. We never say two Kontakia in the Hours. Which one wins? (Sunday vs Feast vs Temple).
*   **Dolnytsky Ref:** Part I (The Hours).

### 2. Encyclopedia of Lenten Hours (The "Alleluia" Mode)
*   **The Problem:** The Hours change drastically during Great Lent.
*   **Deep Logic:**
    *   Triggering "Alleluia" instead of "God is the Lord".
    *   Replacing Troparia with the specific Lenten Troparia (with prostrations).
    *   The "Prayer of St. Ephrem" insertion points.
    *   The Kathisma readings in the Hours (First Hour, etc.).
*   **Dolnytsky Ref:** Part III (Triodion).

### 3. Encyclopedia of Dismissal Construction (Horologion Core)
*   **The Problem:** Generating the correct "Apolysis" string at the end of every service (Hours, Vespers, Matins).
*   **Deep Logic:**
    *   The "Festal Preamble" (e.g., "Christ our True God who was born in a cavern...").
    *   The list of Saints: Day of Week (Angels/John/Cross) vs Day of Month (Saint) vs Temple Patron.
    *   Suppression of the Temple Patron on Great Feasts.
*   **Dolnytsky Ref:** Part I (Dismissals).

### 4. Encyclopedia of Compline Canons (The "Octoechos" Gap)
*   **The Problem:** Which Canon is read at Small Compline?
*   **Deep Logic:**
    *   Standard Weekday: Theotokos Canon from Octoechos? Or Saint of the Day?
    *   Friday Night: Canon for the Departed vs Canon to the Trinity.
    *   Lenten Compline: The "Great Canon" segments.
*   **Dolnytsky Ref:** Part I (Compline).

### 5. Encyclopedia of Midnight Office Variants
*   **The Problem:** It has 3 distinct "Modes".
*   **Deep Logic:**
    *   *Weekday:* Psalm 118 throughout.
    *   *Saturday:* The "Non-sedulous" (Kathisma 9) replacement logic.
    *   *Sunday:* The Triadic Canons of the Tone (replacing Ps 118).
*   **Dolnytsky Ref:** Part I (Nocturns).

### 6. Encyclopedia of Typika Beatitudes
*   **The Problem:** Typika replaces Liturgy on aliturgical days, but also has complex Beatitude verses.
*   **Deep Logic:**
    *   Mapping Octoechos Beatitudes (Sunday).
    *   Merging Ode 3+6 from the Canon (Feast Days).
    *   The "Blessed are they" Psalm logic for funeral/departed days.
*   **Dolnytsky Ref:** Part I (Typika).

### 7. Encyclopedia of Royal Hours Triggers
*   **The Problem:** Determining when the Standard Hours are replaced by Royal Hours.
*   **Deep Logic:**
    *   The "Paramony" Rule (Christmas Eve, Theophany Eve) - unless Sat/Sun?
    *   Good Friday Royal Hours.
    *   The collision of Annunciation with Royal Hours.
*   **Dolnytsky Ref:** Part III.

### 8. Encyclopedia of The Common (Litya & Artoklasia)
*   **The Problem:** Often attached to Great Vespers, but structurally part of the Horologion flow (Vigil).
*   **Deep Logic:**
    *   Calculating the "Litya Sticheron" stack (Temple vs Feast vs Saint).
    *   The Artoklasia bread blessing mechanism (only on Vigils).
*   **Dolnytsky Ref:** Part I (Litya).

### 9. Encyclopedia of Inter-Hour Prayers (Meshchorie)
*   **The Problem:** The "Between-Hours" contained in the First Hour etc. during Lent.
*   **Deep Logic:**
    *   When are these explicitly taken? (Strict Lenten days only).
    *   The structure of the "Biblical Odes" if read here.
*   **Dolnytsky Ref:** Part III.

### 10. Encyclopedia of Hierarchical Commemorations
*   **The Problem:** Who gets commemorated in the Litanies?
*   **Deep Logic:**
    *   Inserting the correct Hierarchy (Pope, Patriarch, Metropolitan, Bishop) based on jurisdiction.
    *   Handling "Sede Vacante" (vacant see) scenarios.
*   **Dolnytsky Ref:** Part V (Hierarchical Services).

---

## SECTION B: GENERAL LITURGICAL LOGIC (Remaining Topics)

### 11. Encyclopedia of Lenten Canon Mergers
*   **The Problem:** Triodion Weekdays involve merging two canons from the Menaion with specific Odes from the Triodion (e.g., Odes 1, 8, 9 on Monday).
*   **Deep Logic:** Handling the "Three Odes" vs "Menaion Odes", the rules for "covering" missing Odes, and the suppression of the Menaion canon on specific days.
*   **Dolnytsky Ref:** Part III (Triodion).

### 12. Encyclopedia of Pre-Sanctified Liturgy Triggers
*   **The Problem:** Determining when the Liturgy of the Presanctified Gifts is served, focusing on exceptions (e.g., Annunciation, Temple Feasts).
*   **Deep Logic:** The "Wed/Fri" rule, the "Polyeleos Exception" (does a Saint cancel it?), and the complex reading structure (Genesis/Proverbs vs Epistles).
*   **Dolnytsky Ref:** Part III (Lent).

### 13. Encyclopedia of Gospel Selection (The "Lookback" vs "Jump")
*   **The Problem:** The complex rules for Matthew/Luke jumps after Exaltation of the Cross and Theophany.
*   **Deep Logic:** The "Lucan Jump" (starting Luke in late Sept), the "Sunday before/after" logic, and handling the "11 Eothina" cycle interruptions.
*   **Dolnytsky Ref:** Part IV (Gospel Tables).

### 14. Encyclopedia of Transfer Logic (The "Mark of St. Mark")
*   **The Problem:** Feasts colliding with Pascha, Bright Week, or Holy Week must be transferred.
*   **Deep Logic:** The specific dates blocked (Lazarus Sat -> Thomas Sunday), the destination dates (Bright Monday/Tuesday), and the "Kyrio-Pascha" logic (Annunciation on Pascha).
*   **Dolnytsky Ref:** Part III (Triodion/Pentecostarion).

### 15. Encyclopedia of Octoechos Rotation (The "Tone Engine")
*   **The Problem:** Calculating the correct Tone for any given week, accounting for Paschal resets and "Tone-Free" weeks.
*   **Deep Logic:** The math of `(WeeksFromPascha % 8)`, handling Bright Week (one tone per day), and the "Leave-taking" interruptions.
*   **Dolnytsky Ref:** Part IV.

### 16. Encyclopedia of Censing Rules (The "Fragrant Logic")
*   **The Problem:** When to cense "Greatly" (All Temple) vs "Simply" (Iconostas/Pre-Ambo).
*   **Deep Logic:** The specific trigger points in Vespers/Matins (e.g., Polyeleos, Magnificat, 9th Ode) and how Rank modifies them (Polyeleos vs Doxology).
*   **Dolnytsky Ref:** Part I (Censing).

### 17. Encyclopedia of Prokeimena Precedence
*   **The Problem:** Which Psalm verse wins? (Sunday vs Saint vs Feast).
*   **Deep Logic:** The hierarchy of "Great Prokeimenon" (Lent/Feasts) vs "Sunday Prokeimenon" vs "Saint Prokeimenon". The "Glory/Both Now" logic for splitting verses.
*   **Dolnytsky Ref:** Part I.

### 18. Encyclopedia of Fasting Levels
*   **The Problem:** Calculating the strictness of the fast (Wine/Oil/Fish/Cheese/Meat).
*   **Deep Logic:** The intersection of Day of Week (Wed/Fri) with Feast Rank (Polyeleos=Oil, Vigil=Fish?). The specific "Harbinger" weeks (Publican/Pharisee).
*   **Dolnytsky Ref:** Part IV (Fasting).
