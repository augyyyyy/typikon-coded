# Divine Liturgy of St. Basil the Great: Typikon Rubrics
## Derived from `01j_struct_liturgy.json` nodes, verified against Dolnytsky Appendix V

> This file contains two layers:
> - **§ Inline Rubrics** — compact instructions for placement directly into the service book at each structural node.
> - **§ Appendix** — exhaustive, case-by-case encyclopedia entries.

---

# § INLINE RUBRICS

The Liturgy of St. Basil the Great follows the exact structural sequence of the Liturgy of St. John Chrysostom, with critical exceptions during the Anaphora and the Megalynarion. These rubrics define those specific overrides.

## Physical Choreography Note
The physical movements, liturgical vestments, and censing paths—specifically the mandate that the Little and Great Entrances exit via the **northern door** to process to the holy doors—are identical to the strict physical rubrics defined in the Liturgy of St. John Chrysostom. 

---

## 1. When is the Liturgy of St. Basil Served?
**JSON constraint:** `resolve_service_type`

The Liturgy of St. Basil is celebrated only ten times per year:
1. The five Sundays of Great Lent.
2. Holy Thursday.
3. Holy Saturday.
4. The Eve of the Nativity (if it falls on a weekday).
5. The Eve of Theophany (if it falls on a weekday).
6. January 1 (The Feast of St. Basil).

*(Note: On Holy Saturday, Holy Thursday, and the Eves of Nativity/Theophany, it is served as a **Vesperal Liturgy**, beginning with Great Vespers and bridging into the Liturgy at the Trisagion).*

---

## 2. The Anaphora of St. Basil
**JSON node override:** `basil_anaphora`

The Eucharistic Prayers (the Anaphora) of St. Basil are significantly longer than those of St. John Chrysostom. 

**Rubric for the Choir:** Because the priest must read these extended prayers silently while the choir sings the responses, the choir must sing the Anaphoral responses (*"A mercy of peace," "We lift them up," "It is meet and right," "Holy, Holy, Holy," "We praise Thee,"*) much more slowly and deliberately than usual, drawing out the melodies so the priest is not rushed.

---

## 3. The Megalynarion (Zadostoinyk)
**JSON node override:** `in_thee_rejoiceth`

Instead of *"It is truly meet"* (Axion Estin), the choir sings the proper Megalynarion of St. Basil's Liturgy:
*"In thee rejoiceth, O full of grace, all creation, the angelic hosts and the race of men..."*

*(Exception: On Holy Thursday, the Megalynarion is "Come, O faithful, let us enjoy the Master's hospitality..." On Holy Saturday, it is "Weep not for Me, O Mother...").*

---
---

# § APPENDIX

---

## Appendix A: Vesperal Liturgy Bridge Logic

On the days when the Liturgy of St. Basil is served in the evening (Holy Saturday, Holy Thursday, Eves of Nativity/Theophany), the service begins as **Great Vespers**.
The Vespers proceeds normally up to the Prokeimenon.

1. **Extended Readings:** Following the Prokeimenon, an extended set of Old Testament readings (Paremiya) is chanted (e.g., 8 on Nativity Eve, 13 on Theophany Eve, 15 on Holy Saturday).
2. **The Transition:** After the final reading, the Small Litany is intoned.
3. **The Bridge:** The service immediately transitions to the Divine Liturgy at the singing of the **Trisagion** (*"Holy God..."*). The Liturgy of St. Basil then proceeds from the Trisagion through to the Dismissal.
