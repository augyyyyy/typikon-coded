# Liturgical Hierarchy of Precedence & Terminology Standards

## 1. The Hierarchy of Precedence (The Canonical Triad)

Liturgical resolution in the engine is governed by a strict hierarchy of precedence. When two or more sources disagree, the higher-ranking source always overrides the lower:

1. **Ordo Celebrationis (1944/1996)**: Physical choreography, temple movement, censing paths, vestment sequences, door/curtain states, and bow types.
   * *Location*: `Data/Service Books/Typikon/Ordo/Ordo_Celebrationis_1996_CLEAN.md`
2. **Dolnytsky Typikon (Parts II–V)**: Selection of proper variables (troparia, kontakia, scripture lessons, tones, canon distributions, praises ratios) based on rank and calendars.
   * *Location*: `Data/Service Books/Typikon/Dolnytsky_Typikon_Master.md`
3. **Ruthenian Liturgicon (1942/1989/2006)**: Verbatim spoken text assets, prayers, and standard English translations.
   * *Location*: `Data/Service Books/Typikon/vocabulary_standardization_matrix.md`
4. **Dolnytsky Part I**: Historical supplement of service templates, used *only* where it supplements or does not contradict the Ordo Celebrationis.
   * *Location*: `Data/Service Books/Typikon/Dolnytsky_Typikon_Master.md`

### Dispute Resolution Rule
If the **Ordo Celebrationis** and the **Dolnytsky Typikon** disagree on physical rubrics (e.g., whether to open the royal doors at a specific moment or when the priest censes), the **Ordo always wins**. The Ordo is the codified canonical standard promulgated by the Sacred Congregation for the Eastern Churches.

### Primary-Backup Recension Text Lookup Order
When the engine retrieves any liturgical text asset, it queries databases in the following strict order of precedence:
1. **Context-Specific Recension**: If requested via `context["recension"]` (e.g., `st_sergius_db` for Tone 1).
2. **Primary Recension (Royal Doors)**: Standard UGCC propers style (`royal_doors_db`).
3. **Backup Recension (Stamford)**: Used to resolve any missing keys in Royal Doors (`stamford_db`).
4. **General Menaion Fallback**: Resolves generic saint troparia, kontakia, and stichera if not present in individual recensions.
5. **System Logic Placeholder**: Returns a clean missing key badge `[Missing key (recension)]`.

---

## 2. UGCC Royal Doors Terminology Translation Map

To prevent terminology drift between different translation layers, the engine enforces strict standards aligned with the **Royal Doors Daily Propers** (vocabulary matrix 2017-2026). Where gaps exist in Royal Doors, Stamford namespace terms are used to fill them:

### A. Liturgical Element Vocabulary Mapping
* **Prokeimenon** (Accepted: Great Prokeimenon. Deprecated/Banned: *Prokimenon*, *Prokimen*).
* **Troparion / Troparia** (Deprecated/Banned: *Tropar*, *Troparion******, *TROPARION*).
* **Kontakion / Kontakia** (Deprecated/Banned: *Tropaion and Kontakion*, *Kontakion Tone*******).
* **Sessional Hymn / Sessional Hymns** (Accepted: Kathisma Reading / Kathisma. Deprecated/Banned: *Sedalion*, *Kathisma & Small Litany*).
* **Gradual Hymn / Gradual Hymns** (Accepted: Gradual Hymn Antiphon. Deprecated/Banned: *Stepenna*, *Antiphons of the Gradual*).
* **Exapostilarion / Exapostilaria** (Accepted: Hymn of Light, Hymn of Light (Gospel). Deprecated/Banned: *Svetilen*, *Lamp-Lighting Psalms*).
* **Communion Hymn** (Accepted: Communion Verse. Deprecated/Banned: *Koinonikon*).
* **At Psalm 140 (Lord, I Call)** (Deprecated/Banned: *Lord, I have cried*, *At Psalm*).
* **Aposticha** (Accepted: At the Aposticha. Deprecated/Banned: *Apostikh*).
* **Praises / At the Praises** (Accepted: Stichera of the Praises. Deprecated/Banned: *Lauds*).
* **Canon** (Deprecated/Banned: *CANON*).

### B. Core Translation Standards (Royal Doors & Stamford Fallbacks)
* **Royal Doors** is used instead of *Holy Doors* (an Orthodox/Greek-inspired term).
* **Royal Hours** is used instead of *Great Hours*.
* **Tserkovne Oko** (lit. "Eye of the Church") is retained untranslated for the Slavic title of the Typikon.
* **Sluzhebnik** and **Sluzhebnyky** (plural) are retained untranslated.

### C. General Menaion Category Badges Mapping (Stamford Fallbacks)
When importing/parsing raw General Menaion files, translate their names to align with the standard UGCC classification:
* Monastic -> venerable
* Monastics -> venerables
* Nun -> venerable_woman
* Nuns -> venerable_women
* NunMartyr -> venerable_woman_martyr
* MonasticMartyr -> venerable_martyr
* MonasticMartyrs -> venerable_martyrs
* Martyress -> woman_martyr
* Martyresses -> women_martyrs
* Heirarch -> hierarch
* Heirarchs -> hierarchs
* Hieromartyr / Heiromartyrs -> hierarchomartyr / hierarchomartyrs
* Unmercenaries -> unmercenaries
* Cross -> cross
* Angels -> angels
* Fools -> fools_for_christ
* St John Baptist -> forerunner

---

## 3. Liturgical Seasons Grounding

1. **Paschal Week**: Bright Week services are completely resurrectional. Daily Compline and Midnight Office are suppressed. Standard Matins and Hours are replaced by Paschal Hours. Grounded in *Dolnytsky Part IV: Paschalion*.
2. **Apostles' Fast**: The fast starts on the Monday after All Saints Sunday (Pascha offset >= 57) and ends June 28 (eve of SS Peter and Paul). Mondays, Wednesdays, and Fridays are strict fasting days (abstinence from meat/dairy) subject to Synodal mitigations (wine/oil on Polyeleos/Vigil feasts). Grounded in *Lviv Synod (1891) and Dolnytsky Part V*.
3. **Saint Suppressions**: How minor saints (rank_simple_4, rank_none) are combined or suppressed when colliding with major feasts or Sundays. Sunday resurrectional elements always take sequence precedence. Grounded in *Dolnytsky Chapter 1 & 2 (General Rubrics)*.
