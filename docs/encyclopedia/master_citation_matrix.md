# Master Liturgical Citation Matrix

> **Purpose**: Programmatic validation and canonical mapping of all coded rubrics against the 2010 Lviv Typikon (Dolnytsky) and the 1996 Ordo Celebrationis.
> **Status**: Verified and Synced (SGC-02 Bijective Grounding)

## 📊 Summary Statistics

- **Total JSON Source References**: 428
- **Resolved JSON Citations**: 428
- **Unresolved JSON Citations**: 0
- **Total Decorated Python Methods**: 50
- **Resolved Python Citations**: 50
- **Unresolved Python Citations**: 0

## 🐍 Python Engine Resolvers & Decoded Source Text

This section details the verbatim source text backing the core algorithmic resolvers in the Python engine.

### Method: `resolve_deacon_role`
- **Defined in**: [ceremonial.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/ceremonial.py#L1227) (`engine/resolvers/ceremonial.py:L1227`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L315-419,§29-§49`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L315-419`
```text
  315: ##### 29. The deacon, holding the sticharion and the orarion approaches the priest and with his head bowed says: Master, bless the sticharion and orarion. The priest, blessing, says: Blessed is our God, ... The deacon: Amen, and then[40] he dons the sticharion; having kissed the orarion, he places it on his left shoulder.[41]
  316: 
  317: The priest blesses the sticharion and orarion
  318: 
  319: ##### 30. The priest, who is already wearing the rason, blesses the epitrachelion, and puts it on. He leaves the Holy Table by the north door and stands before the closed royal doors, where he makes a small bow and says: Blessed is our God, ...
  320: After the Our Father ... he exclaims: For Thine is the kingdom ...
  321: 
  322: ##### 31. During the reading or chanting of Psalm 103, the priest quietly reads all the Prayers of Light[42] before the royal doors.[43]
  323: 
  324: After the recitation of Psalm 103, the deacon departs via the northern door and, having shown reverence to the priest by making a small bow, begins: In peace, let us pray to the Lord.
  325: 
  326: Upon completion of the Psalm, the priest returns to the Altar and, standing before the Holy Table, finishes the recitation of the Prayers of Light if he did not complete them before. After the priest’s exclamation: For to You is due all glory, ... the deacon makes a small bow, returns to the Altar through the southern door and stands at the priest’s right.
  327: 
  328: ##### 32. When the Kathisma[44] is finished, the deacon departs via the northern door and says the Small Synapte. Following the exclamation of the priest: For Yours is the might ... he makes a small bow and returns to the Altar.
  329: 
  330: ##### 33. When the choir begins to sing O Lord, I have cried to You, ... the deacon takes the thurible, presents it to the priest for blessing, and censes the Holy
  331: Table from four sides, then the apsidal icon, the icons in the Altar, and the priest. Then, having left the Altar via the northern door, he comes before the
  332: Royal Doors, makes a reverence and censes the icons of the southern part of the iconostasis beginning with the icon of the Savior. Having again made a reverence before the royal doors, he censes the northern part of the iconostasis beginning with the icon of the Theotokos, and then the right and left choirs. He censes the people from the soleas,[45] and finally enters the Altar via the southern door.
  333: 
  334: ##### 34. When the choir begins to sing the last stichera, the priest blesses and kisses the phelonion and vests in it; at the Glory ... he and the deacon come before the holy table. The royal doors are opened. The deacon takes the thurible and receives the priest’s blessing over it; preceded by candlebearers, the deacon and the priest, who lets his phelonion hang freely,[46] walk around the holy table starting from its right side, and then depart via the northern door.
  335: 
  336: They stand before the royal doors: the candlebearers facing one another, one near the icon of the Theotokos and the other near the icon
  337: 
  338: of the Savior, the deacon in the center, and behind him the priest. Both bow their heads, and after the deacon, holding the orarion with three fingers, has said: Let us pray to the Lord in a subdued voice, the priest, secretly says the
  339: Prayer of Entrance: O gracious King, You love mankind ...[47]
  340: 
  341: However, when the vigils of the Lord’s Nativity and Epiphany fall on a Saturday or a Sunday,[48] the deacon takes both the thurible and the Gospel[49] for making the Entrance.[50]
  342: 
  343: After the Prayer of the Entrance, the deacon, pointing his orarion eastward, says to the priest: Master, bless the holy entrance. Facing east and blessing,
  344: [ILLUSTRATION: the priest says: Blessed is the entrance ... Then the deacon proffers the Holy]
  345: Gospel (if he carries it) to the priest for kissing; standing in the royal doors in front of the priest, when the choir has finished the stichera, the deacon makes the sign of the Cross with the thurible or he raises the Holy Gospel,[51] exclaiming: Wisdom! Stand aright! While O Joyful Light ... is sung, the deacon and the priest enter the Altar to return to the Holy Table, and the candlebearers return through the side doors. Then the deacon censes everything as prescribed at O Lord, I have cried to You, ... (See § 33).[52]
  346: 
  347: [ILLUSTRATION: The deacon censes the iconostasis]
  348: 
  349: With the censing done and the hymn finished, the deacon comes to the royal doors and looking toward the people, exclaims: Let us be attentive! The priest,[53] facing the people, blesses: Peace be with all.[54] The deacon: Wisdom! Be attentive! And the priest remaining there with hands crossed over his breast awaits the end of the Prokeimenon.[55] Then,[56] if any lessons are to be read,[57] he makes a small bow before the Holy Table and proceeds to his chair.
```

---

### Method: `resolve_concelebration_roles`
- **Defined in**: [ceremonial.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/ceremonial.py#L1442) (`engine/resolvers/ceremonial.py:L1442`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L420-431,§50-§53`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L420-431`
```text
  420: ##### 50. The concelebrating priests, who are usually of an even number, vest in the epitrachelion and phelonion over the rason just before the Entrance, and they take their places at the sides of the Holy Table, but not in front where only the principal celebrant and deacon stand. They stand according to the order of dignity or priestly ordination; the first concelebrating priest at the right side of the Holy Table and the second at its left, the third at the right, and so on.
  421: 
  422: ##### 51. At the Entrance, all make a small bow and, with phelonia hanging freely and hands lowered, the younger priests preceding, the clergy leave via the northern door; they stand in double file, one to each side of the royal doors;[83] the principal celebrant, however, stands in the center and behind the others, and alone recites the Entrance Prayer.
  423: 
  424: After the exclamation of the deacon: Wisdom! Stand aright!,[84] all enter through the royal doors immediately following the deacon, and resume their places at the sides of the Holy Table.[85] As the deacon walks around the Holy
  425: Table for the censing, the concelebrants withdraw a little from the Holy Table in order to facilitate his passage.
  426: 
  427: ##### 52. The ekphonesis: For You are a merciful God ... is said by the main celebrant; the other: For You, O God, are gracious ... may be said by the first concelebrant, and the other: May the might of Your kingdom ... by the main celebrant. Following the Dismissal, all make a small bow before the Holy Table, depart and unvest.
  428: 
  429: --- VARIANT: With One Deacon ---
  430: 
  431: ##### 53. The deacon, holding the sticharion with the orarion, approaches the priest and with his head bowed says: Master, bless the sticharion and the orarion. The priest, blessing, says: Blessed is our God ... The deacon: Amen, and then he puts on the sticharion. After kissing the orarion, the deacon puts it on his left shoulder.[87]
```

---

### Method: `resolve_vespers_censing_sequence`
- **Defined in**: [ceremonial.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/ceremonial.py#L1644) (`engine/resolvers/ceremonial.py:L1644`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L330-405,§33,§39,§45`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L330-405`
```text
  330: ##### 33. When the choir begins to sing O Lord, I have cried to You, ... the deacon takes the thurible, presents it to the priest for blessing, and censes the Holy
  331: Table from four sides, then the apsidal icon, the icons in the Altar, and the priest. Then, having left the Altar via the northern door, he comes before the
  332: Royal Doors, makes a reverence and censes the icons of the southern part of the iconostasis beginning with the icon of the Savior. Having again made a reverence before the royal doors, he censes the northern part of the iconostasis beginning with the icon of the Theotokos, and then the right and left choirs. He censes the people from the soleas,[45] and finally enters the Altar via the southern door.
  333: 
  334: ##### 34. When the choir begins to sing the last stichera, the priest blesses and kisses the phelonion and vests in it; at the Glory ... he and the deacon come before the holy table. The royal doors are opened. The deacon takes the thurible and receives the priest’s blessing over it; preceded by candlebearers, the deacon and the priest, who lets his phelonion hang freely,[46] walk around the holy table starting from its right side, and then depart via the northern door.
  335: 
  336: They stand before the royal doors: the candlebearers facing one another, one near the icon of the Theotokos and the other near the icon
  337: 
  338: of the Savior, the deacon in the center, and behind him the priest. Both bow their heads, and after the deacon, holding the orarion with three fingers, has said: Let us pray to the Lord in a subdued voice, the priest, secretly says the
  339: Prayer of Entrance: O gracious King, You love mankind ...[47]
  340: 
  341: However, when the vigils of the Lord’s Nativity and Epiphany fall on a Saturday or a Sunday,[48] the deacon takes both the thurible and the Gospel[49] for making the Entrance.[50]
  342: 
  343: After the Prayer of the Entrance, the deacon, pointing his orarion eastward, says to the priest: Master, bless the holy entrance. Facing east and blessing,
  344: [ILLUSTRATION: the priest says: Blessed is the entrance ... Then the deacon proffers the Holy]
  345: Gospel (if he carries it) to the priest for kissing; standing in the royal doors in front of the priest, when the choir has finished the stichera, the deacon makes the sign of the Cross with the thurible or he raises the Holy Gospel,[51] exclaiming: Wisdom! Stand aright! While O Joyful Light ... is sung, the deacon and the priest enter the Altar to return to the Holy Table, and the candlebearers return through the side doors. Then the deacon censes everything as prescribed at O Lord, I have cried to You, ... (See § 33).[52]
  346: 
  347: [ILLUSTRATION: The deacon censes the iconostasis]
  348: 
  349: With the censing done and the hymn finished, the deacon comes to the royal doors and looking toward the people, exclaims: Let us be attentive! The priest,[53] facing the people, blesses: Peace be with all.[54] The deacon: Wisdom! Be attentive! And the priest remaining there with hands crossed over his breast awaits the end of the Prokeimenon.[55] Then,[56] if any lessons are to be read,[57] he makes a small bow before the Holy Table and proceeds to his chair.
  350: Where the custom prevails, the priest proceeds to his chair immediately after the deacon’s exclamation: Wisdom! Be attentive! The deacon, however, remains at the royal doors, and before the title of each lesson exclaims: Wisdom! to the people, and after the title he also exclaims: Let us be attentive!
  351: 
  352: ##### 35. After the lessons,[58] the priest returns to the Holy Table; the deacon, having shown a reverence to the priest, walks around the Holy Table and departs via the northern door; coming before the royal doors, he says the ektene: Let us all say ... The priest exclaims: For You are a merciful and gracious God, ...
  353: and after: O Lord, keep us this evening ...[59] the deacon says the Aitisis:[60]
  354: Let us complete our evening prayer ... The priest exclaims: For You, O God, are
  355: ... The choir: Amen. The priest, blessing: Peace be with all! The choir: And to your spirit. The deacon: Bow your heads to the Lord. The choir: To You, O Lord.
  356: And while the priest recites the Prayer of the Inclination of the Head, all bow their heads until the ekphonesis: May the might of Your kingdom ... After the ekphonesis, the deacon returns to the Altar via the southern door.
  357: 
  358: ##### 36. The choir begins to sing the Aposticha, then: Now You may dismiss your servant ... Trisagion;[61] and after: Our Father ... the priest exclaims: For
  359: Thine is the kingdom ...
  360: 
  361: After the troparia, the royal doors are opened.[62] The deacon leaves via the southern door and stands near the icon of the Savior; looking towards the people and elevating the orarion with the first three fingers of his right hand, he exclaims: Wisdom! The choir: Give the blessing! The priest: Blessed is the
  362: One-Who-Is ... The choir: Amen. O God, strengthen ... The priest: O most holy
  363: Theotokos ... The choir: More honorable than the Cherubim ... The priest, facing the east: Glory to You, O Christ, ... The choir: Glory to the Father ... now and ever ... Lord, have mercy (three times) ... Master, bless![63] The priest,
  364: 
```

---

### Method: `resolve_litya_procession`
- **Defined in**: [ceremonial.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/ceremonial.py#L1699) (`engine/resolvers/ceremonial.py:L1699`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L456-480,§59,§61`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L456-480`
```text
  456: ##### 59. After the prayer is completed, the choir sings: Blessed be the Name of the
  457: Lord... and the priest and the deacon enter the Altar via the southern door, or the priest goes through the royal doors and the
  458: 
  459: deacon via the southern door,[97] and they stand before the holy table. Then the choir says the 33rd Psalm: I will bless the Lord at all times ... to ... but those who seek the Lord shall not lack any good things.
  460: 
  461: Following this, the royal doors are opened (if they are not already open[98])
  462: and the priest blesses the people from the royal doors, saying: The blessing of the Lord be upon you... The choir: Amen, and the Dismissal takes place with the deacon beginning: Wisdom! as was prescribed for the end of “Vespers without the
  463: All-Night Vigil” (see § 36).
  464: 
  465: ##### 60. If Orthros is served immediately after Vespers as part of the All-Night
  466: Vigil, the priest closes the holy doors after the ekphonesis: The blessing of the Lord be upon you... and then removes his phelonion.
  467: 
  468: The lector prays aloud Glory to God in the Highest... (three times) and Lord,
  469: You shall open my lips... (twice) and the Six Psalms. The priest leaves via the northern door and secretly recites the Orthros Prayers before the royal doors.[99]
  470: 
  471: --- VARIANT: With Two Deacons ---
  472: 
  473: ##### 61. The priest is clothed in the epitrachelion and phelonion, the deacons in the sticharion and orarion. The priest opens the royal doors and the first deacon departs with a lighted candle via the southern door, before the royal doors he makes a small bow and exclaims: Command! and returns to the Altar via the southern door (see § 54).
  474: 
  475: Then the priest, preceded by the first deacon with a candle, incenses as prescribed above and finishes by saying in a moderate tone of voice: Bless, O
  476: Lord.
  477: 
  478: After this, the deacon and priest enter the Altar via the southern and royal doors respectively, having laid aside the thurible, the priest stands before the
  479: Holy Table and exclaims: Glory to the holy and life giving Trinity, One in
  480: Essence and undivided... The choir: Amen. Come let us ... (three times) and
```

---

### Method: `resolve_polyeleos_movement`
- **Defined in**: [ceremonial.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/ceremonial.py#L1738) (`engine/resolvers/ceremonial.py:L1738`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L587-595,§76`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L587-595`
```text
  587: ##### 76. During the recitation of the Six Psalms, the Priest, standing before the
  588: Holy Table, begins to say the Orthros prayers; however, after
  589: 
  590: the first three psalms have been read, he departs via the northern door and stands before the holy doors where he continues the recitation of the Orthros prayers. When the Psalms are completed, the priest acknowledges the reverence shown by the deacon, returns to the Altar via the southern door and stands before the Holy Table.
  591: 
  592: Toward the end of the Six Psalms, the deacon, vested in the sticharion and orarion, departs via the northern door, shows a reverence to the priest, and stands in his customary place from which he says the Great Synapte. The priest exclaims : For to You is due ... When the choir sings: God is the Lord... the deacon says the verses; then, having made a small bow, he returns to the Altar via the southern door.
  593: 
  594: [ILLUSTRATION: The deacon says the Great Synapte]
  595: 
```

---

### Method: `resolve_matins_gospel_censing`
- **Defined in**: [ceremonial.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/ceremonial.py#L1754) (`engine/resolvers/ceremonial.py:L1754`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L618-630,§79`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L618-630`
```text
  618: ##### 79. After the reading, the priest kisses the closed Gospel and takes it to the center of the church where he places it upon the tetrapod. He returns to the
  619: Altar through the royal doors.[116] If it is Sunday, the deacon reads:[117]
  620: Having beheld the resurrection of Christ ... The lector reads Psalm 50: Have mercy on me, God, in your kindness ...
  621: 
  622: Following the stichera, the deacon, in his customary place, says: Save O God,
  623: Your people ..., the choir responds with: Lord, have mercy (12 times). The priest exclaims: Through the mercies and compassions ... and the choir responds with: Amen and then begins the Canon. If there was no All-Night Vigil, the royal doors are closed.[118]
  624: 
  625: ##### 80. If there was an All-Night Vigil, then after the exclamation: Through the mercies ..., the priest, carrying the hand cross,[119] departs through the holy doors; the deacon takes the oil (which had been blessed at Vespers) and a quill,[120] and leaves via the northern door, then stands to the right of the tetrapod. There the priest anoints cruciformly the
  626: 
  627: foreheads of those who come to kiss the Gospel. The anointing having been completed, the priest and deacon return to the Altar through the royal doors and the southern door, respectively; the Royal Doors are closed and the priest takes off the phelonion.
  628: 
  629: ##### 81. After the third and sixth Odes, the deacon says the Small Synapte standing either before the royal doors or, if the anointing of the faithful is not yet completed, near the tetrapod. The priest says the ekphonesis either from the
  630: Altar, or near the tetrapod. When the Katavasia of the eighth Ode has been sung,[121] the deacon takes the thurible and, standing before the icon of the
```

---

### Method: `resolve_proskomedia_vessels`
- **Defined in**: [ceremonial.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/ceremonial.py#L1774) (`engine/resolvers/ceremonial.py:L1774`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L862-880,§115`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L862-880`
```text
  862: ##### 115. The deacon takes the thurible, sets incense into it, and says to the priest: Master, bless the incense and immediately thereafter Let us pray to the
  863: Lord. In blessing, the priest says the Prayer of Incense: We offer incense to
  864: You ...
  865: 
  866: [ILLUSTRATION: The deacon: Let us pray to the Lord. The priest censes the asterisk[140] by]
  867: holding it over the thurible and then he sets it over the holy bread, saying:
  868: And a star came and stood ...
  869: 
  870: [ILLUSTRATION: The deacon: Let us pray to the Lord. Master, cover. After censing the first veil]
  871: in the same manner, the priest covers the holy bread and diskarion, saying: The
  872: Lord has reigned, He is clothed ...
  873: 
  874: [ILLUSTRATION: The deacon: Let us pray to the Lord. Master, cover. Having censed the second]
  875: veil in the same manner, the priest covers the chalice saying: Your glory, O
  876: Christ, has covered ...
  877: 
  878: [ILLUSTRATION: The deacon: Let us pray to the Lord. Master, cover. After censing the large]
  879: veil, called the aer, in the same manner, the priest says: Shelter us under the cover of Your wings; drive away ... while
  880: 
```

---

### Method: `resolve_liturgy_entrances`
- **Defined in**: [ceremonial.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/ceremonial.py#L1785) (`engine/resolvers/ceremonial.py:L1785`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L940-1030,§122,§129`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L940-1030`
```text
  940: ##### 122. The chanters sing the third antiphon or the Beatitudes, if it is Sunday.
  941: When the chanters come to Glory...[143] the priest and deacon, standing before the Holy Table, make three small bows. Then the priest takes the Holy Gospel and gives it to the deacon. The priest allows his phelonion to hang freely.[144]
  942: Preceded by the candlebearers, the deacon and priest go to the right and pass behind the Holy Table and go out of the Altar through the north door to make the
  943: Little Entrance. When they come before the royal doors, the candlebearers, one near the icon of the Theotokos and the other near the icon of the Savior, stand facing each other. The priest is in the center and the deacon slightly in front of him and to his right; both bow their heads. In a subdued voice, the deacon says: Let us pray to the Lord, after which the priest quietly says the Prayer of the Entrance: O Lord, our Master and God, Who ...
  944: 
  945: [ILLUSTRATION: The Entrance with the Gospel around the Holy Table]
  946: 
  947: When the priest has finished the prayer, the deacon, holding the orarion with three fingers and pointing eastward with his right hand, says in a subdued voice: Master, bless the holy entrance. Blessing towards the east, the priest says: Blessed is the entrance ... Then the deacon presents the Holy Gospel to the priest, who kisses it. At the completion of the antiphon or the Beatitudes,
  948: [ILLUSTRATION: the deacon proceeds to the center and stands before the priest; raising his]
  949: hands a little and displaying the Holy Gospel, the deacon says loudly: Wisdom!
  950: Stand Aright! Holding the Gospel Book, the deacon enters the Altar through the royal doors and places the Holy Gospel upon the Holy Table. The priest follows the deacon into the Altar through the royal doors. Coming together before the royal doors, the candlebearers make a reverence and return to their places. The chanters sing: Come, let us worship ... wondrous in Your saints, ... or, if it is Sunday, ... risen from the dead, ... , and then the usual troparia.
  951: 
  952: [ILLUSTRATION: The Entrance with the Gospel]
  953: 
  954: ##### 123. The priest quietly says the Prayer of the Trisagion: O holy God, Who abide in the saints, ... When the chanters come to the last troparion, the deacon inclines his head towards the priest and, holding the orarion in three fingers of his hand, says: Bless, Master, the time...[145] Blessing him the priest exclaims: For You are holy, our God,...
  955: 
  956: [ILLUSTRATION: The deacon goes close to the royal doors; facing the people, he elevates the end]
  957: of his orarion with three fingers of his right hand and, in a raised voice, says: And unto ages of ages.[146] The choir: Amen.
  958: 
  959: During the singing of the Trisagion, the priest and deacon also recite it, simultaneously making three small bows before the Holy Table.
  960: 
  961: [ILLUSTRATION: The priest and deacon recite the Trisagion]
  962: 
  963: ##### 124. The deacon says to the priest: Master, command. And they go to the throne behind the Holy Table. As he goes the priest says: Blessed is he ... Then the deacon: Master, bless the high throne. The priest: Blessed are You on the throne
  964: ... And he blesses the apsidal throne.
  965: 
  966: Note that the priest does not ascend the throne nor sit upon it, but he should sit to the south side of the throne.
  967: 
  968: ##### 125. When the Trisagion is finished, the deacon comes near the royal doors, holds up the orarion with the first three fingers of his right hand says: Let us be attentive! Blessing the people, the priest announces: Peace be with all.[147]
  969: And the deacon again: Wisdom! Be attentive! and returns to the priest.
  970: 
  971: The choir sings the Prokeimenon from the Psalms of David.[148] After the
  972: Prokeimenon, the deacon announces: Wisdom! The lector, clothed in the sticharion[149] and standing before the soleas in the center of the church, sings the title of the Epistle: A reading from ..., and again the deacon: Let us be attentive!
  973: 
  974: Following the reading of the Epistle, the priest says: Peace be with you.[150]
```

---

### Method: `resolve_presanctified_censing`
- **Defined in**: [ceremonial.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/ceremonial.py#L1817) (`engine/resolvers/ceremonial.py:L1817`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L1713-1730,§235`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L1713-1730`
```text
 1713: ##### 235. After the reading of the second Prophecy is completed, the priest says:
 1714: Peace to you ... The deacon: Wisdom, let us be attentive.[298] The deacon takes a lighted candle and approaches the priest. The lector, who stands midway between the two choirs, or preferably the priest who stands in the Altar before the Holy Table and censes, sings: Let my prayer ascend ... After this verse has been sung by the lector or the priest, it is repeated by the choir.
 1715: 
 1716: The lector (or the priest who now, preceded by the deacon, stands at the southern side of the Holy Table and there censes) then sings the first verse of
 1717: Psalm 140: O Lord, I have cried ... The choir repeats: Let my prayer ascend ...
 1718: The lector (or the priest who, preceded by the deacon, now stands at the eastern side of the Holy Table and there censes) then sings the second verse of the
 1719: Psalm: O Lord, set a guard ... The choir repeats: Let my prayer ascend ... The lector (or the priest who, preceded by the deacon, now stands at the northern side of the Holy Table and there censes) then sings the third verse of the
 1720: Psalm: Let not my heart ... The choir repeats: Let my prayer ascend ... Once again the lector (or the priest who, preceded by the deacon, now stands in front of the Holy Table and there censes) then sings: Let my prayer
 1721: 
 1722: ascend like incense, and the choir concludes: And the lifting up of my hands like an evening sacrifice.
 1723: 
 1724: ##### 236. It should be noted that when the lector or priest sings: Let my prayer ascend ... or any other verse, the priest censes the Holy Table in strokes of three at the beginning and end of each verse which he sings; during that time, the choir and people pray on bended knees. When the choir sings, the priest, who returns the thurible to the server, and the others who serve in the Altar, likewise pray on bended knees.[299] At the end, all make three great metanies.[300]
 1725: 
 1726: ##### 237. If the feast of any Saint or the patron of the church falls during these days of Lent, then the royal doors are opened and the deacon says: Let us be attentive, and the lector reads the Prokeimenon of the Epistle. Then the Epistle and Gospel are read as usual.
 1727: 
 1728: ##### 238. The Holy Doors are closed. The deacon takes leave of the priest, departs via the northern door and, standing in his usual place, says the ektene: Let us all say ...; and everything is performed as usual until the ekphonesis of the
 1729: Prayer for the Catechumens, after which the priest, having removed the Gospel, unfolds the eiliton[301] on the Holy Table.
 1730: 
```

---

### Method: `resolve_hierarchical_ceremonial`
- **Defined in**: [ceremonial.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/ceremonial.py#L1847) (`engine/resolvers/ceremonial.py:L1847`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L677-735,§87-§96`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L677-735`
```text
  677: ##### 87. Following the Stichera of Lauds the royal doors are opened. The first deacon stands before the altar to the priest’s right, and the second deacon to the left; the Great Doxology having been completed, all make a small bow and proceed to the tetrapod; there, the priest takes the Holy Gospel and, preceded by the deacons, returns to the Altar.
  678: 
  679: ##### 88. Then the deacons leave – the first via the southern door, the second via the northern; the first deacon says the Ektene: Have mercy on us, O God ... The second deacon says the Aitisis: Let us complete our morning prayer to the Lord
  680: ... The first deacon says: Let us bow our heads to the Lord. The Dismissal is said with the first deacon beginning: Wisdom!
  681: 
  682: --- VARIANT: Without a Deacon ---
  683: 
  684: ##### 89. The priest serving Orthros without a deacon performs or recites all those prayers which are proper to the deacon, but bearing in mind the following:
  685: 
  686: ##### 90. Following the Six Psalms, he does not return to the Altar, but stands before the royal doors and says the Great Synapte and ekphonesis: For to You are due all glory... and also the verses when the choir sings: God is the Lord ... These completed, he makes a small bow and returns to the Altar via the southern door.
  687: 
  688: If time is lacking for the priest to say all the Orthros Prayers before the doors, he completes them in the Altar while the Kathismata are read.
  689: 
  690: Following the Prokeimenon, he exclaims: Let us pray to the Lord. He says the verses for: Let everything that breathes ..., and after the reading of the
  691: Gospel he says: Having beheld the Resurrection of Christ ...
  692: 
  693: Following the third and sixth Odes of the Canon he says the Small Synaptes and ekphoneses either before the Holy Table[123] or from the place where he performs the anointing. The anointing having been completed, he returns to the Altar through the royal doors and divests of the phelonion.
  694: 
  695: ##### 91. The Katavasia of the eighth Ode having been completed, he departs via the northern door clothed in the epitrachelion. Standing before the icon of the
  696: Theotokos he exclaims: The Theotokos and the Mother of Light let us magnify in songs! and censes as prescribed above (see § 33). Following the censing, he returns to the Altar via the southern door and says the Small Synapte and ekphonesis.
  697: 
  698: ##### 92. After the Stichera of Lauds at: Glory ..., clothed in the phelonion, he opens the royal doors; the last stichera having been completed, he exclaims:
  699: Glory to You Who have shown us the Light. All the rest follows as stated above
  700: (see § 82-83).
  701: 
  702: ##### 93. After the Dismissal, the royal doors are closed, the priest takes off the phelonion and the First Hour is read.
  703: 
  704: --- VARIANT: With Concelebrating Priests ---
  705: 
  706: ##### 94. The concelebrating priests, of even number, vest over the rason in the epitrachelion and phelonion while the Kathisma is read, and they take their places at the sides of the Holy Table as in Vespers (see § 50). While the
  707: Polyeleos is sung, all make a small bow and, with phelonia hanging freely and hands lowered, depart through the royal doors, the younger clergy leading. The first two priests carry the icon of the Feast or Saint and place it on the tetrapod (if it has not already been placed on the left side of the tetrapod between the two choirs). All arrange themselves in double file facing one another at the sides of the
  708: 
  709: tetrapod. The principal celebrant stands in the center before the tetrapod and the deacon is on his right.
  710: 
  711: ##### 95. Then all sing the We magnify You ... When the choir repeats the We magnify
```

---

### Method: `resolve_censing_sequence`
- **Defined in**: [ceremonial.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/ceremonial.py#L1873) (`engine/resolvers/ceremonial.py:L1873`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L330-405,L1713-1730,§33,§39,§45,§235`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L330-405`
```text
  330: ##### 33. When the choir begins to sing O Lord, I have cried to You, ... the deacon takes the thurible, presents it to the priest for blessing, and censes the Holy
  331: Table from four sides, then the apsidal icon, the icons in the Altar, and the priest. Then, having left the Altar via the northern door, he comes before the
  332: Royal Doors, makes a reverence and censes the icons of the southern part of the iconostasis beginning with the icon of the Savior. Having again made a reverence before the royal doors, he censes the northern part of the iconostasis beginning with the icon of the Theotokos, and then the right and left choirs. He censes the people from the soleas,[45] and finally enters the Altar via the southern door.
  333: 
  334: ##### 34. When the choir begins to sing the last stichera, the priest blesses and kisses the phelonion and vests in it; at the Glory ... he and the deacon come before the holy table. The royal doors are opened. The deacon takes the thurible and receives the priest’s blessing over it; preceded by candlebearers, the deacon and the priest, who lets his phelonion hang freely,[46] walk around the holy table starting from its right side, and then depart via the northern door.
  335: 
  336: They stand before the royal doors: the candlebearers facing one another, one near the icon of the Theotokos and the other near the icon
  337: 
  338: of the Savior, the deacon in the center, and behind him the priest. Both bow their heads, and after the deacon, holding the orarion with three fingers, has said: Let us pray to the Lord in a subdued voice, the priest, secretly says the
  339: Prayer of Entrance: O gracious King, You love mankind ...[47]
  340: 
  341: However, when the vigils of the Lord’s Nativity and Epiphany fall on a Saturday or a Sunday,[48] the deacon takes both the thurible and the Gospel[49] for making the Entrance.[50]
  342: 
  343: After the Prayer of the Entrance, the deacon, pointing his orarion eastward, says to the priest: Master, bless the holy entrance. Facing east and blessing,
  344: [ILLUSTRATION: the priest says: Blessed is the entrance ... Then the deacon proffers the Holy]
  345: Gospel (if he carries it) to the priest for kissing; standing in the royal doors in front of the priest, when the choir has finished the stichera, the deacon makes the sign of the Cross with the thurible or he raises the Holy Gospel,[51] exclaiming: Wisdom! Stand aright! While O Joyful Light ... is sung, the deacon and the priest enter the Altar to return to the Holy Table, and the candlebearers return through the side doors. Then the deacon censes everything as prescribed at O Lord, I have cried to You, ... (See § 33).[52]
  346: 
  347: [ILLUSTRATION: The deacon censes the iconostasis]
  348: 
  349: With the censing done and the hymn finished, the deacon comes to the royal doors and looking toward the people, exclaims: Let us be attentive! The priest,[53] facing the people, blesses: Peace be with all.[54] The deacon: Wisdom! Be attentive! And the priest remaining there with hands crossed over his breast awaits the end of the Prokeimenon.[55] Then,[56] if any lessons are to be read,[57] he makes a small bow before the Holy Table and proceeds to his chair.
  350: Where the custom prevails, the priest proceeds to his chair immediately after the deacon’s exclamation: Wisdom! Be attentive! The deacon, however, remains at the royal doors, and before the title of each lesson exclaims: Wisdom! to the people, and after the title he also exclaims: Let us be attentive!
  351: 
  352: ##### 35. After the lessons,[58] the priest returns to the Holy Table; the deacon, having shown a reverence to the priest, walks around the Holy Table and departs via the northern door; coming before the royal doors, he says the ektene: Let us all say ... The priest exclaims: For You are a merciful and gracious God, ...
  353: and after: O Lord, keep us this evening ...[59] the deacon says the Aitisis:[60]
  354: Let us complete our evening prayer ... The priest exclaims: For You, O God, are
  355: ... The choir: Amen. The priest, blessing: Peace be with all! The choir: And to your spirit. The deacon: Bow your heads to the Lord. The choir: To You, O Lord.
  356: And while the priest recites the Prayer of the Inclination of the Head, all bow their heads until the ekphonesis: May the might of Your kingdom ... After the ekphonesis, the deacon returns to the Altar via the southern door.
  357: 
  358: ##### 36. The choir begins to sing the Aposticha, then: Now You may dismiss your servant ... Trisagion;[61] and after: Our Father ... the priest exclaims: For
  359: Thine is the kingdom ...
  360: 
  361: After the troparia, the royal doors are opened.[62] The deacon leaves via the southern door and stands near the icon of the Savior; looking towards the people and elevating the orarion with the first three fingers of his right hand, he exclaims: Wisdom! The choir: Give the blessing! The priest: Blessed is the
  362: One-Who-Is ... The choir: Amen. O God, strengthen ... The priest: O most holy
  363: Theotokos ... The choir: More honorable than the Cherubim ... The priest, facing the east: Glory to You, O Christ, ... The choir: Glory to the Father ... now and ever ... Lord, have mercy (three times) ... Master, bless![63] The priest,
  364: 
```

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L1713-1730`
```text
 1713: ##### 235. After the reading of the second Prophecy is completed, the priest says:
 1714: Peace to you ... The deacon: Wisdom, let us be attentive.[298] The deacon takes a lighted candle and approaches the priest. The lector, who stands midway between the two choirs, or preferably the priest who stands in the Altar before the Holy Table and censes, sings: Let my prayer ascend ... After this verse has been sung by the lector or the priest, it is repeated by the choir.
 1715: 
 1716: The lector (or the priest who now, preceded by the deacon, stands at the southern side of the Holy Table and there censes) then sings the first verse of
 1717: Psalm 140: O Lord, I have cried ... The choir repeats: Let my prayer ascend ...
 1718: The lector (or the priest who, preceded by the deacon, now stands at the eastern side of the Holy Table and there censes) then sings the second verse of the
 1719: Psalm: O Lord, set a guard ... The choir repeats: Let my prayer ascend ... The lector (or the priest who, preceded by the deacon, now stands at the northern side of the Holy Table and there censes) then sings the third verse of the
 1720: Psalm: Let not my heart ... The choir repeats: Let my prayer ascend ... Once again the lector (or the priest who, preceded by the deacon, now stands in front of the Holy Table and there censes) then sings: Let my prayer
 1721: 
 1722: ascend like incense, and the choir concludes: And the lifting up of my hands like an evening sacrifice.
 1723: 
 1724: ##### 236. It should be noted that when the lector or priest sings: Let my prayer ascend ... or any other verse, the priest censes the Holy Table in strokes of three at the beginning and end of each verse which he sings; during that time, the choir and people pray on bended knees. When the choir sings, the priest, who returns the thurible to the server, and the others who serve in the Altar, likewise pray on bended knees.[299] At the end, all make three great metanies.[300]
 1725: 
 1726: ##### 237. If the feast of any Saint or the patron of the church falls during these days of Lent, then the royal doors are opened and the deacon says: Let us be attentive, and the lector reads the Prokeimenon of the Epistle. Then the Epistle and Gospel are read as usual.
 1727: 
 1728: ##### 238. The Holy Doors are closed. The deacon takes leave of the priest, departs via the northern door and, standing in his usual place, says the ektene: Let us all say ...; and everything is performed as usual until the ekphonesis of the
 1729: Prayer for the Catechumens, after which the priest, having removed the Gospel, unfolds the eiliton[301] on the Holy Table.
 1730: 
```

---

### Method: `resolve_canon_ode_troparion`
- **Defined in**: [common.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/common.py#L1730) (`engine/resolvers/common.py:L1730`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.5.1,L717-748`

#### Source: `Dolnytsky_Typikon_Master.md:L717-748`
```text
  717: #### 5. Order of the Matins Canon
  718: 
  719: *The Canon consists of eight odes (outside the Great Fast, where Ode 2 is omitted) or nine odes (during Lent). Canons are taken on 12 or 14 troparia.*
  720: 
  721: * **Distribution of Canons:**
  722:   * *Festal Services:* 1 or 2 canons taken to make 12 troparia, with the Heirmos sung twice.
  723:   * *Saint during a Feast:* Canons taken to make 12 (or 14 if two saints), with the Heirmos of the first canon only[^30].
  724:   * *Sunday with Saint:* Canons taken to make 14 (Resurrection, Cross-Resurrection, Theotokos, and *Menaion*)[^31].
  725: 
  726: * **Refrains to the Odes:**
  727:   * *Feast of the Lord:* "Glory, O Lord, to Thy holy (Transfiguration / Nativity / Cross)[^33]."
  728:   * *Resurrection (Sunday):* "Glory, O Lord, to Thy holy Resurrection."
  729:   * *Theotokos:* "O Most Holy Theotokos, save us."
  730:   * *Saint:* "[Title and Name], pray to God for us."
  731:   * *For the Departed:* "Give rest, O Lord, to the soul[s] of Thy departed servant[s]."
  732:   * *Before the penultimate troparion of the last canon:* "**Glory:**"
  733:   * *Before the final Theotokion:* "**Both now:**"
  734: 
  735: * **Katavasias:**
  736:   * Sung after each ode, according to the season (or the general Marian Katavasia "I shall open my mouth")[^32].
  737:   * *At the 8th Ode:* Preceded by the refrain: "We praise, we bless, we worship the Lord, praising and magnifying Him unto all ages."
  738: 
  739: * **The 9th Ode (Magnificat):**
  740:   * Introduced by the Deacon/Priest:
  741:     > **Deacon:** "The Theotokos and Mother of the Light let us magnify in songs."[^34]
  742:   * The Song of the Theotokos ("My soul magnifies the Lord") with the refrain *“More honorable than the Cherubim”* is sung, while the Deacon censes the altar and temple. (On Great Feasts of the Lord and Theotokos, proper festal refrains are sung instead of the Magnificat).
  743: 
  744: * **Hymnography after Odes 3, 6, and 9:**
  745:   * *After the 3rd Ode:* Small Litany, followed by the **Sessional Hymn** of the Saint / Feast (on a Polyeleos or six-troparia Saint, the Sessional Hymn and Exaposteilarion are taken twice[^35], then Both now: his Theotokion; if the Saint has two Sessional Hymns, the second is taken with the refrain Glory, then Both now: his Theotokion[^36]).
  746:   * *After the 6th Ode:* Small Litany, followed by the **Kontakion and Ikos** (Resurrectional or Festal)[^37].
  747:   * *After the 9th Ode:* Small Litany. On Sundays: "Holy is the Lord our God" (3), followed by the appointed **Exaposteilarion (Hymn of Light)**[^38].
  748: 
```

---

### Method: `check_day_range`
- **Defined in**: [compline.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/compline.py#L448) (`engine/resolvers/compline.py:L448`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:4.1.7,L7354-7539`

#### Source: `Dolnytsky_Typikon_Master.md:L7354-7539`
```text
 7354: ### 4.1.7 Beginning of Great Lent
 7355: 
 7356: > **Note:** The Synod of Lviv permits on all days of Great Lent, except Mondays, Wednesdays, and Fridays, meat, on the condition of [reciting] 5 "Our Father" and 5 "Virgin Theotokos" for the laity, and Psalm 50 – for the clergy; on the other three days – dairy products.
 7357: 
 7358: GENERAL RUBRICS
 7359: 
 7360: FOR THE FIVE FIRST LENTEN DAYS OF ALL WEEKS
 7361: 
 7362: OF GREAT LENT
 7363: 
 7364: ##### At the Midnight Office
 7365: 
 7366: On the first day of Great Lent we do not make prostrations at the Midnight Office, except three great ones at the prayer of St. Ephrem, and on other Lenten days we make 3 small prostrations: 1. At each of the three Trisagions. 2. At both "O come, let us worship". 3. At each Glory: "The Blameless"; also 16 usual ones at the prayer of St. Ephrem, that is 4 great and 12 small[^511].
 7367: 
 7368: ##### At Matins
 7369: 
 7370: > **Note:** We begin prostrations from the Kathismata and make: 1. At "Alleluia" of each "Glory" of the Kathismata – 3 prostrations[^512]. 2. At "More honorable" of each of the 6 verses of the Song of the Theotokos – 1 prostration. 3. At *“It is truly meet”* – 1 prostration. 4. At "Glory to God in the highest" – 3 prostrations. 5. At the final Trisagion – 3 prostrations. 6. At the prayer of St. Ephrem – 16 prostrations, that is 12 small and 4 great.
 7371: 
 7372: 1. From the beginning to the end of the litany "In peace let us pray to the Lord", everything, just as on every day
 7373: 
 7374: 2. **On *"God is the Lord"*:* Instead of *“God is the Lord”* we sing Alleluia in the sequential tone of the *Octoechos*
 7375: 
 7376: 3. We sing three Trinity Hymns of the current tone, given in the *Horologion*, three for each tone. They are all sung three times with the refrain "Glory" to the second, and "Both now" – to the third. At each first one we make a commemoration of the weekday service, at the second – a commemoration of all saints, at the third – a commemoration of the Theotokos. However, since the weekday service of the week changes daily, and the troparia are sung the same each day of the week (except Saturdays and Sundays, on which, because they are not Lenten, the Trinity Hymns are not sung), at the end of each first Trinity Hymn a colon is given, which signifies that the troparion must be completed with the commemoration of the weekday service, the form of which is indicated at the end of the 3rd troparion of Tone 1
 7377: 
 7378: Note
 7379: 
 7380: These three commemorations we make also at the Exaposteilaria following the canon. But the Lenten Exaposteilarion has only one troparion in each tone, which is sung three times, therefore, when it is sung the first time, the commemoration of the weekday service is added to it, when – the second time, with the refrain "Glory", then – the commemoration of all saints, and when the third time, with the refrain "Both now", then – the commemoration of the Theotokos. These commemorations are added where the colon is given, that is before "And save me".
 7381: 
 7382: 4. Three Kathismata with their Sessional Hymns, the Sessional Hymns of which, sung after the 1st Kathisma, are of the *Octoechos* of the current tone, given also at the end of the *Triodion*. The Sessional Hymns sung after the 2nd and 3rd Kathismata are of the *Triodion*
 7383: 
 7384: 5. Psalm 50 and the first petition of the Great Litany "Save, O God", and after the exclamation "Through the mercy and compassion" immediately – the Canon
 7385: 
 7386: 6. Odes and Canons. The Biblical Odes, given at the end of the Psalter, are intertwined with the odes of the canon, as given: before the ode of the canon the corresponding ode of the Psalter is recited, leaving its last verses for refrains to the troparia of the canon, in such quantity as there will be troparia in the ode of the canon, including the heirmos, except two, for to the penultimate troparion we refrain "Glory", and to the last – "Both now". The 2nd Ode is recited in full before the ode of the canon, and to the troparia of its canon we refrain: "Glory to Thee, our God, glory to Thee". According to our ancient custom, the Odes of the Psalter are recited only in those odes in which the triodion occurs, and in the other odes we refrain the usual refrains to the troparia of the canon. The Greek Typikon prescribes singing the Odes of the Psalter in the tone of the *Menaion* canon, but now we do not even know what their melody was
 7387: 
 7388: The Canons will be only of the *Menaion* and *Triodion*, for the *Octoechos*, according to the Greek rubric, during Great Lent is not sung, with the exception of Sundays. In some odes there will be 3 canons on 14, that is of the Saint of the *Menaion* with heirmos on 6 and both canons of the *Triodion* on 8: one on 4 and the second on 4. In some odes there will be only one canon of the saint on 4, and in the second ode there will be only two canons of the *Triodion* on 8, with heirmos on 9. This difference regarding the number of canons and their troparia in the odes arises because the *Triodion* canons do not occur daily in all odes, but in general only in three odes in the following sequence:
```

---

### Method: `resolve_royal_psalms`
- **Defined in**: [hours.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/hours.py#L385) (`engine/resolvers/hours.py:L385`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:3.4.7,L2789-2866`

#### Source: `Dolnytsky_Typikon_Master.md:L2789-2866`
```text
 2789: ### 3.4.7 December: Eve of the Nativity of Christ
 2790: 
 2791: Everything – according to the rule given above for the Forefeast of the Nativity of Christ, however, instead of the usual Hours we sing the Great Hours and the Liturgy of Basil with Vespers. Only, if the Eve falls on Saturday or on Sunday, we sing the Hours before that, on Friday, and the Liturgy of Basil – on the very day of the Feast. On the Eve – Liturgy of Chrysostom, at its proper time, and afterwards – Vespers, at its proper time.
 2792: 
 2793: HOURS
 2794: 
 2795: OF THE EVE OF THE NATIVITY OF CHRIST AND THEOPHANY
 2796: 
 2797: Notes
 2798: 
 2799: The Lviv Synod orders pastors to celebrate these Hours together with the Typika in church, in violet vestments, in view of the fast[^308], in bright vestments it is celebrated before Theophany only when the Hours from Saturday or Sunday are transferred back, to Friday, for then there is no fast, but it will be a general dispensation
 2800: 
 2801: Now we sing all the Hours adding "The Typika" (Typika); and therefore we begin the Hours 3rd, 6th and 9th from "O come, let us worship", and we make the dismissal only at the end of "The Typika"
 2802: 
 2803: These Hours are celebrated in the morning, earlier or later, at the decision of the Superior; according to the custom of the arch-cathedral church – at 9 o'clock before noon[^309], so that there would be a certain distance between the Hours and the Liturgy, which according to the custom of the same church begins at 11 o'clock. If the Hours begin earlier, then the Liturgy can also begin earlier, but since it is celebrated with Vespers, it should begin around 10 o'clock, as the Lviv Synod decreed about Vespers with the Presanctified[^310]
 2804: 
 2805: The composition and form of the Great Hours is the same as of the usual Hours, with the exception of three troparia and three readings, given after the Theotokion "What shall we call Thee" at the 1st Hour and after the corresponding ones at the other Hours. Regarding the essence, the Royal Hours differ from the usual ones also by the tripalm, which at the Royal Hours is special, appropriate to the given feast[^311]
 2806: 
 2807: In the temple, before the Holy Doors, opposite the people, two analogia are placed, on the first of which the Gospel is placed; the second, slightly lower, – opposite the Holy Doors, from which the Paremia and Apostle are to be read. Where there is no analogion for the Gospel, it lies on the Holy Table and is brought out by the Priest through the Holy Doors only for reading, and is supported by servers[^312]
 2808: 
 2809: The Royal Hours are celebrated with the Holy Doors closed, which are opened only for the reading of the Gospel
 2810: 
 2811: Candles on the altar are lit only for the reading of the Gospel
 2812: 
 2813: At the appointed time the Priest enters the temple and, having approached the Holy Table and having bowed low, kisses the Gospel, marks four Gospel readings and, having bowed again, goes out to the sacristy; puts on an epitrachelion, goes out before the closed Holy Doors, makes a low bow to the Holy Mysteries and begins the usual: "Blessed is our God". Choir: "Amen", also "Glory to Thee, our God, glory to Thee", "O Heavenly King" and everything else, as usual, up to "O come, let us worship" inclusive[^313]. At the second "O come, let us worship" the Priest, having bowed low, enters the sanctuary and, while the choirs sing the tripalm, reads it sitting in his place.
 2814: 
 2815: When, after the Troparion of the Forefeast "Once Mary was registered", the Theotokion is also read, the choirs sing three stichera idiomesa[^314]  on 6, that is twice each. The first stichera both the first and the second time is sung without a refrain; the second – the first time with a separate refrain, and the second – with another separate refrain; the third – the first time with the refrain "Glory", and the second – with the refrain "Both now". All four above-mentioned refrains at all Hours – are the same. At the 9th Hour the third stichera is taken three times, that is the first time it is read loudly and piously by the canonarch in the middle of the church, without a refrain, then the second time – by one choir with the refrain "Glory", and the third – by the other with the refrain "Both now"[^315].
 2816: 
 2817: After the singing of the three stichera there will be three readings: the first – of the Prophecy with a Prokimenon, the second – of the Apostle without a Prokimenon and without Alleluia, the third – of the Gospel, beginning it from "Wisdom, attend!", "Let us hear". All this is accompanied by the following actions: when the stichera end, the Priest puts on a phelonion and, having gone out before the steps of the altar and having bowed, opens the Holy Doors and exclaims: "Let us attend! Peace be unto all!" (blessing the people), "Wisdom! Let us attend!". The choirs sing the Prokimenon. After its conclusion the Priest, having exclaimed before the title of the Prophecy "Wisdom!" and before the reading "Let us attend!", waits before the steps of the altar for the end of the reading of the Prophecy and, after its conclusion, having exclaimed "Wisdom!" and "Let us attend!" before the reading of the Apostle, as usual, puts incense into the censer with the short prayer "Incense we offer to Thee" and, having blessed the incense with the words "Blessed is our God", censes everything as usual, that is the Holy Table from four sides, the iconostasis, the choirs and the people[^316]. At the end of the Apostle, and together with it the censing, the candle-bearers go out before the analogion, and the Priest approaches the Holy Table and, having bowed, takes the Holy Gospel and, having placed it on the analogion, begins to sing the Gospel from "Wisdom, attend". After the singing of the Gospel the Priest, having kissed the beginning of the reading, leaves it there, closes the Holy Doors and, having bowed low to the Holy Mysteries, goes out to the sacristy, takes off the phelonion, goes out through the side doors before the Holy Doors for "Thou Who at all times" and remains there until the end of the Hour.
 2818: 
 2819: > **Note:** Since we sing all the Hours together, the prayer of blessing the incense should be said only at the 1st Hour, at the others – only "Blessed is our God" just as at Great Vespers with All-Night Vigil.
 2820: 
 2821: If there be deacons, they put on dalmatics with an orarion before the beginning of the 1st Hour and remain vested until the end of the Typika. At the Prokimenon, together with the Priest, they go before the steps of the altar and, having bowed low all together to the Holy Mysteries, open the Holy Doors. The right Deacon exclaims: "Let us attend!", and the left, after the giving of peace by the Priest: "Wisdom! Let us attend!". Also before the first and second reading – the right: "Wisdom!", and the left: "Let us attend!" and they cense everything as usual, as at the beginning of the Liturgy. At the end of the Apostle, and together with it the censing, both deacons stand with the Priest before the steps of the altar and, having bowed all three together to the Holy Mysteries, go out from the sanctuary: the Priest with the Gospel through the middle [doors], and the deacons, having swapped their sides, through the side doors to the analogion. The right Deacon exclaims: "Wisdom, attend!", "Let us hear", the Priest: "The reading from the Holy Gospel according to (Name)", and the left deacon: "Let us attend!". The Priest sings the Gospel. Having finished, the Priest kisses the beginning of the reading, also the right deacon, and after him the left. Having bowed low, the deacons return through their doors to the sanctuary and, together with the Priest, close the Holy Doors. Having bowed low all three together to the Holy Mysteries, they withdraw: the deacons to their places, and the Priest before the iconostasis for "Thou Who at all times".
 2822: 
 2823: If the hierarch or other sacred dignitaries be present in the church, the deacons should cense them before the choirs, and neither the Priest nor the deacons should kiss the Gospel before the hierarch and sacred dignitaries, and therefore both deacons together carry the open Gospel to them for kissing, also to the Priest standing in the Holy Doors and, when he kisses it, the deacons themselves kiss [it], after which they place it on the analogion and, having bowed low to the Holy Mysteries, return, each through his doors, to the sanctuary.
```

---

### Method: `resolve_royal_stichera`
- **Defined in**: [hours.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/hours.py#L408) (`engine/resolvers/hours.py:L408`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:3.4.7,L2789-2866`

#### Source: `Dolnytsky_Typikon_Master.md:L2789-2866`
```text
 2789: ### 3.4.7 December: Eve of the Nativity of Christ
 2790: 
 2791: Everything – according to the rule given above for the Forefeast of the Nativity of Christ, however, instead of the usual Hours we sing the Great Hours and the Liturgy of Basil with Vespers. Only, if the Eve falls on Saturday or on Sunday, we sing the Hours before that, on Friday, and the Liturgy of Basil – on the very day of the Feast. On the Eve – Liturgy of Chrysostom, at its proper time, and afterwards – Vespers, at its proper time.
 2792: 
 2793: HOURS
 2794: 
 2795: OF THE EVE OF THE NATIVITY OF CHRIST AND THEOPHANY
 2796: 
 2797: Notes
 2798: 
 2799: The Lviv Synod orders pastors to celebrate these Hours together with the Typika in church, in violet vestments, in view of the fast[^308], in bright vestments it is celebrated before Theophany only when the Hours from Saturday or Sunday are transferred back, to Friday, for then there is no fast, but it will be a general dispensation
 2800: 
 2801: Now we sing all the Hours adding "The Typika" (Typika); and therefore we begin the Hours 3rd, 6th and 9th from "O come, let us worship", and we make the dismissal only at the end of "The Typika"
 2802: 
 2803: These Hours are celebrated in the morning, earlier or later, at the decision of the Superior; according to the custom of the arch-cathedral church – at 9 o'clock before noon[^309], so that there would be a certain distance between the Hours and the Liturgy, which according to the custom of the same church begins at 11 o'clock. If the Hours begin earlier, then the Liturgy can also begin earlier, but since it is celebrated with Vespers, it should begin around 10 o'clock, as the Lviv Synod decreed about Vespers with the Presanctified[^310]
 2804: 
 2805: The composition and form of the Great Hours is the same as of the usual Hours, with the exception of three troparia and three readings, given after the Theotokion "What shall we call Thee" at the 1st Hour and after the corresponding ones at the other Hours. Regarding the essence, the Royal Hours differ from the usual ones also by the tripalm, which at the Royal Hours is special, appropriate to the given feast[^311]
 2806: 
 2807: In the temple, before the Holy Doors, opposite the people, two analogia are placed, on the first of which the Gospel is placed; the second, slightly lower, – opposite the Holy Doors, from which the Paremia and Apostle are to be read. Where there is no analogion for the Gospel, it lies on the Holy Table and is brought out by the Priest through the Holy Doors only for reading, and is supported by servers[^312]
 2808: 
 2809: The Royal Hours are celebrated with the Holy Doors closed, which are opened only for the reading of the Gospel
 2810: 
 2811: Candles on the altar are lit only for the reading of the Gospel
 2812: 
 2813: At the appointed time the Priest enters the temple and, having approached the Holy Table and having bowed low, kisses the Gospel, marks four Gospel readings and, having bowed again, goes out to the sacristy; puts on an epitrachelion, goes out before the closed Holy Doors, makes a low bow to the Holy Mysteries and begins the usual: "Blessed is our God". Choir: "Amen", also "Glory to Thee, our God, glory to Thee", "O Heavenly King" and everything else, as usual, up to "O come, let us worship" inclusive[^313]. At the second "O come, let us worship" the Priest, having bowed low, enters the sanctuary and, while the choirs sing the tripalm, reads it sitting in his place.
 2814: 
 2815: When, after the Troparion of the Forefeast "Once Mary was registered", the Theotokion is also read, the choirs sing three stichera idiomesa[^314]  on 6, that is twice each. The first stichera both the first and the second time is sung without a refrain; the second – the first time with a separate refrain, and the second – with another separate refrain; the third – the first time with the refrain "Glory", and the second – with the refrain "Both now". All four above-mentioned refrains at all Hours – are the same. At the 9th Hour the third stichera is taken three times, that is the first time it is read loudly and piously by the canonarch in the middle of the church, without a refrain, then the second time – by one choir with the refrain "Glory", and the third – by the other with the refrain "Both now"[^315].
 2816: 
 2817: After the singing of the three stichera there will be three readings: the first – of the Prophecy with a Prokimenon, the second – of the Apostle without a Prokimenon and without Alleluia, the third – of the Gospel, beginning it from "Wisdom, attend!", "Let us hear". All this is accompanied by the following actions: when the stichera end, the Priest puts on a phelonion and, having gone out before the steps of the altar and having bowed, opens the Holy Doors and exclaims: "Let us attend! Peace be unto all!" (blessing the people), "Wisdom! Let us attend!". The choirs sing the Prokimenon. After its conclusion the Priest, having exclaimed before the title of the Prophecy "Wisdom!" and before the reading "Let us attend!", waits before the steps of the altar for the end of the reading of the Prophecy and, after its conclusion, having exclaimed "Wisdom!" and "Let us attend!" before the reading of the Apostle, as usual, puts incense into the censer with the short prayer "Incense we offer to Thee" and, having blessed the incense with the words "Blessed is our God", censes everything as usual, that is the Holy Table from four sides, the iconostasis, the choirs and the people[^316]. At the end of the Apostle, and together with it the censing, the candle-bearers go out before the analogion, and the Priest approaches the Holy Table and, having bowed, takes the Holy Gospel and, having placed it on the analogion, begins to sing the Gospel from "Wisdom, attend". After the singing of the Gospel the Priest, having kissed the beginning of the reading, leaves it there, closes the Holy Doors and, having bowed low to the Holy Mysteries, goes out to the sacristy, takes off the phelonion, goes out through the side doors before the Holy Doors for "Thou Who at all times" and remains there until the end of the Hour.
 2818: 
 2819: > **Note:** Since we sing all the Hours together, the prayer of blessing the incense should be said only at the 1st Hour, at the others – only "Blessed is our God" just as at Great Vespers with All-Night Vigil.
 2820: 
 2821: If there be deacons, they put on dalmatics with an orarion before the beginning of the 1st Hour and remain vested until the end of the Typika. At the Prokimenon, together with the Priest, they go before the steps of the altar and, having bowed low all together to the Holy Mysteries, open the Holy Doors. The right Deacon exclaims: "Let us attend!", and the left, after the giving of peace by the Priest: "Wisdom! Let us attend!". Also before the first and second reading – the right: "Wisdom!", and the left: "Let us attend!" and they cense everything as usual, as at the beginning of the Liturgy. At the end of the Apostle, and together with it the censing, both deacons stand with the Priest before the steps of the altar and, having bowed all three together to the Holy Mysteries, go out from the sanctuary: the Priest with the Gospel through the middle [doors], and the deacons, having swapped their sides, through the side doors to the analogion. The right Deacon exclaims: "Wisdom, attend!", "Let us hear", the Priest: "The reading from the Holy Gospel according to (Name)", and the left deacon: "Let us attend!". The Priest sings the Gospel. Having finished, the Priest kisses the beginning of the reading, also the right deacon, and after him the left. Having bowed low, the deacons return through their doors to the sanctuary and, together with the Priest, close the Holy Doors. Having bowed low all three together to the Holy Mysteries, they withdraw: the deacons to their places, and the Priest before the iconostasis for "Thou Who at all times".
 2822: 
 2823: If the hierarch or other sacred dignitaries be present in the church, the deacons should cense them before the choirs, and neither the Priest nor the deacons should kiss the Gospel before the hierarch and sacred dignitaries, and therefore both deacons together carry the open Gospel to them for kissing, also to the Priest standing in the Holy Doors and, when he kisses it, the deacons themselves kiss [it], after which they place it on the analogion and, having bowed low to the Holy Mysteries, return, each through his doors, to the sanctuary.
```

---

### Method: `resolve_royal_readings`
- **Defined in**: [hours.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/hours.py#L428) (`engine/resolvers/hours.py:L428`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:3.4.7,L2789-2866`

#### Source: `Dolnytsky_Typikon_Master.md:L2789-2866`
```text
 2789: ### 3.4.7 December: Eve of the Nativity of Christ
 2790: 
 2791: Everything – according to the rule given above for the Forefeast of the Nativity of Christ, however, instead of the usual Hours we sing the Great Hours and the Liturgy of Basil with Vespers. Only, if the Eve falls on Saturday or on Sunday, we sing the Hours before that, on Friday, and the Liturgy of Basil – on the very day of the Feast. On the Eve – Liturgy of Chrysostom, at its proper time, and afterwards – Vespers, at its proper time.
 2792: 
 2793: HOURS
 2794: 
 2795: OF THE EVE OF THE NATIVITY OF CHRIST AND THEOPHANY
 2796: 
 2797: Notes
 2798: 
 2799: The Lviv Synod orders pastors to celebrate these Hours together with the Typika in church, in violet vestments, in view of the fast[^308], in bright vestments it is celebrated before Theophany only when the Hours from Saturday or Sunday are transferred back, to Friday, for then there is no fast, but it will be a general dispensation
 2800: 
 2801: Now we sing all the Hours adding "The Typika" (Typika); and therefore we begin the Hours 3rd, 6th and 9th from "O come, let us worship", and we make the dismissal only at the end of "The Typika"
 2802: 
 2803: These Hours are celebrated in the morning, earlier or later, at the decision of the Superior; according to the custom of the arch-cathedral church – at 9 o'clock before noon[^309], so that there would be a certain distance between the Hours and the Liturgy, which according to the custom of the same church begins at 11 o'clock. If the Hours begin earlier, then the Liturgy can also begin earlier, but since it is celebrated with Vespers, it should begin around 10 o'clock, as the Lviv Synod decreed about Vespers with the Presanctified[^310]
 2804: 
 2805: The composition and form of the Great Hours is the same as of the usual Hours, with the exception of three troparia and three readings, given after the Theotokion "What shall we call Thee" at the 1st Hour and after the corresponding ones at the other Hours. Regarding the essence, the Royal Hours differ from the usual ones also by the tripalm, which at the Royal Hours is special, appropriate to the given feast[^311]
 2806: 
 2807: In the temple, before the Holy Doors, opposite the people, two analogia are placed, on the first of which the Gospel is placed; the second, slightly lower, – opposite the Holy Doors, from which the Paremia and Apostle are to be read. Where there is no analogion for the Gospel, it lies on the Holy Table and is brought out by the Priest through the Holy Doors only for reading, and is supported by servers[^312]
 2808: 
 2809: The Royal Hours are celebrated with the Holy Doors closed, which are opened only for the reading of the Gospel
 2810: 
 2811: Candles on the altar are lit only for the reading of the Gospel
 2812: 
 2813: At the appointed time the Priest enters the temple and, having approached the Holy Table and having bowed low, kisses the Gospel, marks four Gospel readings and, having bowed again, goes out to the sacristy; puts on an epitrachelion, goes out before the closed Holy Doors, makes a low bow to the Holy Mysteries and begins the usual: "Blessed is our God". Choir: "Amen", also "Glory to Thee, our God, glory to Thee", "O Heavenly King" and everything else, as usual, up to "O come, let us worship" inclusive[^313]. At the second "O come, let us worship" the Priest, having bowed low, enters the sanctuary and, while the choirs sing the tripalm, reads it sitting in his place.
 2814: 
 2815: When, after the Troparion of the Forefeast "Once Mary was registered", the Theotokion is also read, the choirs sing three stichera idiomesa[^314]  on 6, that is twice each. The first stichera both the first and the second time is sung without a refrain; the second – the first time with a separate refrain, and the second – with another separate refrain; the third – the first time with the refrain "Glory", and the second – with the refrain "Both now". All four above-mentioned refrains at all Hours – are the same. At the 9th Hour the third stichera is taken three times, that is the first time it is read loudly and piously by the canonarch in the middle of the church, without a refrain, then the second time – by one choir with the refrain "Glory", and the third – by the other with the refrain "Both now"[^315].
 2816: 
 2817: After the singing of the three stichera there will be three readings: the first – of the Prophecy with a Prokimenon, the second – of the Apostle without a Prokimenon and without Alleluia, the third – of the Gospel, beginning it from "Wisdom, attend!", "Let us hear". All this is accompanied by the following actions: when the stichera end, the Priest puts on a phelonion and, having gone out before the steps of the altar and having bowed, opens the Holy Doors and exclaims: "Let us attend! Peace be unto all!" (blessing the people), "Wisdom! Let us attend!". The choirs sing the Prokimenon. After its conclusion the Priest, having exclaimed before the title of the Prophecy "Wisdom!" and before the reading "Let us attend!", waits before the steps of the altar for the end of the reading of the Prophecy and, after its conclusion, having exclaimed "Wisdom!" and "Let us attend!" before the reading of the Apostle, as usual, puts incense into the censer with the short prayer "Incense we offer to Thee" and, having blessed the incense with the words "Blessed is our God", censes everything as usual, that is the Holy Table from four sides, the iconostasis, the choirs and the people[^316]. At the end of the Apostle, and together with it the censing, the candle-bearers go out before the analogion, and the Priest approaches the Holy Table and, having bowed, takes the Holy Gospel and, having placed it on the analogion, begins to sing the Gospel from "Wisdom, attend". After the singing of the Gospel the Priest, having kissed the beginning of the reading, leaves it there, closes the Holy Doors and, having bowed low to the Holy Mysteries, goes out to the sacristy, takes off the phelonion, goes out through the side doors before the Holy Doors for "Thou Who at all times" and remains there until the end of the Hour.
 2818: 
 2819: > **Note:** Since we sing all the Hours together, the prayer of blessing the incense should be said only at the 1st Hour, at the others – only "Blessed is our God" just as at Great Vespers with All-Night Vigil.
 2820: 
 2821: If there be deacons, they put on dalmatics with an orarion before the beginning of the 1st Hour and remain vested until the end of the Typika. At the Prokimenon, together with the Priest, they go before the steps of the altar and, having bowed low all together to the Holy Mysteries, open the Holy Doors. The right Deacon exclaims: "Let us attend!", and the left, after the giving of peace by the Priest: "Wisdom! Let us attend!". Also before the first and second reading – the right: "Wisdom!", and the left: "Let us attend!" and they cense everything as usual, as at the beginning of the Liturgy. At the end of the Apostle, and together with it the censing, both deacons stand with the Priest before the steps of the altar and, having bowed all three together to the Holy Mysteries, go out from the sanctuary: the Priest with the Gospel through the middle [doors], and the deacons, having swapped their sides, through the side doors to the analogion. The right Deacon exclaims: "Wisdom, attend!", "Let us hear", the Priest: "The reading from the Holy Gospel according to (Name)", and the left deacon: "Let us attend!". The Priest sings the Gospel. Having finished, the Priest kisses the beginning of the reading, also the right deacon, and after him the left. Having bowed low, the deacons return through their doors to the sanctuary and, together with the Priest, close the Holy Doors. Having bowed low all three together to the Holy Mysteries, they withdraw: the deacons to their places, and the Priest before the iconostasis for "Thou Who at all times".
 2822: 
 2823: If the hierarch or other sacred dignitaries be present in the church, the deacons should cense them before the choirs, and neither the Priest nor the deacons should kiss the Gospel before the hierarch and sacred dignitaries, and therefore both deacons together carry the open Gospel to them for kissing, also to the Priest standing in the Holy Doors and, when he kisses it, the deacons themselves kiss [it], after which they place it on the analogion and, having bowed low to the Holy Mysteries, return, each through his doors, to the sanctuary.
```

---

### Method: `resolve_royal_troparia`
- **Defined in**: [hours.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/hours.py#L447) (`engine/resolvers/hours.py:L447`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:3.4.7,L2789-2866`

#### Source: `Dolnytsky_Typikon_Master.md:L2789-2866`
```text
 2789: ### 3.4.7 December: Eve of the Nativity of Christ
 2790: 
 2791: Everything – according to the rule given above for the Forefeast of the Nativity of Christ, however, instead of the usual Hours we sing the Great Hours and the Liturgy of Basil with Vespers. Only, if the Eve falls on Saturday or on Sunday, we sing the Hours before that, on Friday, and the Liturgy of Basil – on the very day of the Feast. On the Eve – Liturgy of Chrysostom, at its proper time, and afterwards – Vespers, at its proper time.
 2792: 
 2793: HOURS
 2794: 
 2795: OF THE EVE OF THE NATIVITY OF CHRIST AND THEOPHANY
 2796: 
 2797: Notes
 2798: 
 2799: The Lviv Synod orders pastors to celebrate these Hours together with the Typika in church, in violet vestments, in view of the fast[^308], in bright vestments it is celebrated before Theophany only when the Hours from Saturday or Sunday are transferred back, to Friday, for then there is no fast, but it will be a general dispensation
 2800: 
 2801: Now we sing all the Hours adding "The Typika" (Typika); and therefore we begin the Hours 3rd, 6th and 9th from "O come, let us worship", and we make the dismissal only at the end of "The Typika"
 2802: 
 2803: These Hours are celebrated in the morning, earlier or later, at the decision of the Superior; according to the custom of the arch-cathedral church – at 9 o'clock before noon[^309], so that there would be a certain distance between the Hours and the Liturgy, which according to the custom of the same church begins at 11 o'clock. If the Hours begin earlier, then the Liturgy can also begin earlier, but since it is celebrated with Vespers, it should begin around 10 o'clock, as the Lviv Synod decreed about Vespers with the Presanctified[^310]
 2804: 
 2805: The composition and form of the Great Hours is the same as of the usual Hours, with the exception of three troparia and three readings, given after the Theotokion "What shall we call Thee" at the 1st Hour and after the corresponding ones at the other Hours. Regarding the essence, the Royal Hours differ from the usual ones also by the tripalm, which at the Royal Hours is special, appropriate to the given feast[^311]
 2806: 
 2807: In the temple, before the Holy Doors, opposite the people, two analogia are placed, on the first of which the Gospel is placed; the second, slightly lower, – opposite the Holy Doors, from which the Paremia and Apostle are to be read. Where there is no analogion for the Gospel, it lies on the Holy Table and is brought out by the Priest through the Holy Doors only for reading, and is supported by servers[^312]
 2808: 
 2809: The Royal Hours are celebrated with the Holy Doors closed, which are opened only for the reading of the Gospel
 2810: 
 2811: Candles on the altar are lit only for the reading of the Gospel
 2812: 
 2813: At the appointed time the Priest enters the temple and, having approached the Holy Table and having bowed low, kisses the Gospel, marks four Gospel readings and, having bowed again, goes out to the sacristy; puts on an epitrachelion, goes out before the closed Holy Doors, makes a low bow to the Holy Mysteries and begins the usual: "Blessed is our God". Choir: "Amen", also "Glory to Thee, our God, glory to Thee", "O Heavenly King" and everything else, as usual, up to "O come, let us worship" inclusive[^313]. At the second "O come, let us worship" the Priest, having bowed low, enters the sanctuary and, while the choirs sing the tripalm, reads it sitting in his place.
 2814: 
 2815: When, after the Troparion of the Forefeast "Once Mary was registered", the Theotokion is also read, the choirs sing three stichera idiomesa[^314]  on 6, that is twice each. The first stichera both the first and the second time is sung without a refrain; the second – the first time with a separate refrain, and the second – with another separate refrain; the third – the first time with the refrain "Glory", and the second – with the refrain "Both now". All four above-mentioned refrains at all Hours – are the same. At the 9th Hour the third stichera is taken three times, that is the first time it is read loudly and piously by the canonarch in the middle of the church, without a refrain, then the second time – by one choir with the refrain "Glory", and the third – by the other with the refrain "Both now"[^315].
 2816: 
 2817: After the singing of the three stichera there will be three readings: the first – of the Prophecy with a Prokimenon, the second – of the Apostle without a Prokimenon and without Alleluia, the third – of the Gospel, beginning it from "Wisdom, attend!", "Let us hear". All this is accompanied by the following actions: when the stichera end, the Priest puts on a phelonion and, having gone out before the steps of the altar and having bowed, opens the Holy Doors and exclaims: "Let us attend! Peace be unto all!" (blessing the people), "Wisdom! Let us attend!". The choirs sing the Prokimenon. After its conclusion the Priest, having exclaimed before the title of the Prophecy "Wisdom!" and before the reading "Let us attend!", waits before the steps of the altar for the end of the reading of the Prophecy and, after its conclusion, having exclaimed "Wisdom!" and "Let us attend!" before the reading of the Apostle, as usual, puts incense into the censer with the short prayer "Incense we offer to Thee" and, having blessed the incense with the words "Blessed is our God", censes everything as usual, that is the Holy Table from four sides, the iconostasis, the choirs and the people[^316]. At the end of the Apostle, and together with it the censing, the candle-bearers go out before the analogion, and the Priest approaches the Holy Table and, having bowed, takes the Holy Gospel and, having placed it on the analogion, begins to sing the Gospel from "Wisdom, attend". After the singing of the Gospel the Priest, having kissed the beginning of the reading, leaves it there, closes the Holy Doors and, having bowed low to the Holy Mysteries, goes out to the sacristy, takes off the phelonion, goes out through the side doors before the Holy Doors for "Thou Who at all times" and remains there until the end of the Hour.
 2818: 
 2819: > **Note:** Since we sing all the Hours together, the prayer of blessing the incense should be said only at the 1st Hour, at the others – only "Blessed is our God" just as at Great Vespers with All-Night Vigil.
 2820: 
 2821: If there be deacons, they put on dalmatics with an orarion before the beginning of the 1st Hour and remain vested until the end of the Typika. At the Prokimenon, together with the Priest, they go before the steps of the altar and, having bowed low all together to the Holy Mysteries, open the Holy Doors. The right Deacon exclaims: "Let us attend!", and the left, after the giving of peace by the Priest: "Wisdom! Let us attend!". Also before the first and second reading – the right: "Wisdom!", and the left: "Let us attend!" and they cense everything as usual, as at the beginning of the Liturgy. At the end of the Apostle, and together with it the censing, both deacons stand with the Priest before the steps of the altar and, having bowed all three together to the Holy Mysteries, go out from the sanctuary: the Priest with the Gospel through the middle [doors], and the deacons, having swapped their sides, through the side doors to the analogion. The right Deacon exclaims: "Wisdom, attend!", "Let us hear", the Priest: "The reading from the Holy Gospel according to (Name)", and the left deacon: "Let us attend!". The Priest sings the Gospel. Having finished, the Priest kisses the beginning of the reading, also the right deacon, and after him the left. Having bowed low, the deacons return through their doors to the sanctuary and, together with the Priest, close the Holy Doors. Having bowed low all three together to the Holy Mysteries, they withdraw: the deacons to their places, and the Priest before the iconostasis for "Thou Who at all times".
 2822: 
 2823: If the hierarch or other sacred dignitaries be present in the church, the deacons should cense them before the choirs, and neither the Priest nor the deacons should kiss the Gospel before the hierarch and sacred dignitaries, and therefore both deacons together carry the open Gospel to them for kissing, also to the Priest standing in the Holy Doors and, when he kisses it, the deacons themselves kiss [it], after which they place it on the analogion and, having bowed low to the Holy Mysteries, return, each through his doors, to the sanctuary.
```

---

### Method: `resolve_royal_kontakion`
- **Defined in**: [hours.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/hours.py#L456) (`engine/resolvers/hours.py:L456`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:3.4.7,L2789-2866`

#### Source: `Dolnytsky_Typikon_Master.md:L2789-2866`
```text
 2789: ### 3.4.7 December: Eve of the Nativity of Christ
 2790: 
 2791: Everything – according to the rule given above for the Forefeast of the Nativity of Christ, however, instead of the usual Hours we sing the Great Hours and the Liturgy of Basil with Vespers. Only, if the Eve falls on Saturday or on Sunday, we sing the Hours before that, on Friday, and the Liturgy of Basil – on the very day of the Feast. On the Eve – Liturgy of Chrysostom, at its proper time, and afterwards – Vespers, at its proper time.
 2792: 
 2793: HOURS
 2794: 
 2795: OF THE EVE OF THE NATIVITY OF CHRIST AND THEOPHANY
 2796: 
 2797: Notes
 2798: 
 2799: The Lviv Synod orders pastors to celebrate these Hours together with the Typika in church, in violet vestments, in view of the fast[^308], in bright vestments it is celebrated before Theophany only when the Hours from Saturday or Sunday are transferred back, to Friday, for then there is no fast, but it will be a general dispensation
 2800: 
 2801: Now we sing all the Hours adding "The Typika" (Typika); and therefore we begin the Hours 3rd, 6th and 9th from "O come, let us worship", and we make the dismissal only at the end of "The Typika"
 2802: 
 2803: These Hours are celebrated in the morning, earlier or later, at the decision of the Superior; according to the custom of the arch-cathedral church – at 9 o'clock before noon[^309], so that there would be a certain distance between the Hours and the Liturgy, which according to the custom of the same church begins at 11 o'clock. If the Hours begin earlier, then the Liturgy can also begin earlier, but since it is celebrated with Vespers, it should begin around 10 o'clock, as the Lviv Synod decreed about Vespers with the Presanctified[^310]
 2804: 
 2805: The composition and form of the Great Hours is the same as of the usual Hours, with the exception of three troparia and three readings, given after the Theotokion "What shall we call Thee" at the 1st Hour and after the corresponding ones at the other Hours. Regarding the essence, the Royal Hours differ from the usual ones also by the tripalm, which at the Royal Hours is special, appropriate to the given feast[^311]
 2806: 
 2807: In the temple, before the Holy Doors, opposite the people, two analogia are placed, on the first of which the Gospel is placed; the second, slightly lower, – opposite the Holy Doors, from which the Paremia and Apostle are to be read. Where there is no analogion for the Gospel, it lies on the Holy Table and is brought out by the Priest through the Holy Doors only for reading, and is supported by servers[^312]
 2808: 
 2809: The Royal Hours are celebrated with the Holy Doors closed, which are opened only for the reading of the Gospel
 2810: 
 2811: Candles on the altar are lit only for the reading of the Gospel
 2812: 
 2813: At the appointed time the Priest enters the temple and, having approached the Holy Table and having bowed low, kisses the Gospel, marks four Gospel readings and, having bowed again, goes out to the sacristy; puts on an epitrachelion, goes out before the closed Holy Doors, makes a low bow to the Holy Mysteries and begins the usual: "Blessed is our God". Choir: "Amen", also "Glory to Thee, our God, glory to Thee", "O Heavenly King" and everything else, as usual, up to "O come, let us worship" inclusive[^313]. At the second "O come, let us worship" the Priest, having bowed low, enters the sanctuary and, while the choirs sing the tripalm, reads it sitting in his place.
 2814: 
 2815: When, after the Troparion of the Forefeast "Once Mary was registered", the Theotokion is also read, the choirs sing three stichera idiomesa[^314]  on 6, that is twice each. The first stichera both the first and the second time is sung without a refrain; the second – the first time with a separate refrain, and the second – with another separate refrain; the third – the first time with the refrain "Glory", and the second – with the refrain "Both now". All four above-mentioned refrains at all Hours – are the same. At the 9th Hour the third stichera is taken three times, that is the first time it is read loudly and piously by the canonarch in the middle of the church, without a refrain, then the second time – by one choir with the refrain "Glory", and the third – by the other with the refrain "Both now"[^315].
 2816: 
 2817: After the singing of the three stichera there will be three readings: the first – of the Prophecy with a Prokimenon, the second – of the Apostle without a Prokimenon and without Alleluia, the third – of the Gospel, beginning it from "Wisdom, attend!", "Let us hear". All this is accompanied by the following actions: when the stichera end, the Priest puts on a phelonion and, having gone out before the steps of the altar and having bowed, opens the Holy Doors and exclaims: "Let us attend! Peace be unto all!" (blessing the people), "Wisdom! Let us attend!". The choirs sing the Prokimenon. After its conclusion the Priest, having exclaimed before the title of the Prophecy "Wisdom!" and before the reading "Let us attend!", waits before the steps of the altar for the end of the reading of the Prophecy and, after its conclusion, having exclaimed "Wisdom!" and "Let us attend!" before the reading of the Apostle, as usual, puts incense into the censer with the short prayer "Incense we offer to Thee" and, having blessed the incense with the words "Blessed is our God", censes everything as usual, that is the Holy Table from four sides, the iconostasis, the choirs and the people[^316]. At the end of the Apostle, and together with it the censing, the candle-bearers go out before the analogion, and the Priest approaches the Holy Table and, having bowed, takes the Holy Gospel and, having placed it on the analogion, begins to sing the Gospel from "Wisdom, attend". After the singing of the Gospel the Priest, having kissed the beginning of the reading, leaves it there, closes the Holy Doors and, having bowed low to the Holy Mysteries, goes out to the sacristy, takes off the phelonion, goes out through the side doors before the Holy Doors for "Thou Who at all times" and remains there until the end of the Hour.
 2818: 
 2819: > **Note:** Since we sing all the Hours together, the prayer of blessing the incense should be said only at the 1st Hour, at the others – only "Blessed is our God" just as at Great Vespers with All-Night Vigil.
 2820: 
 2821: If there be deacons, they put on dalmatics with an orarion before the beginning of the 1st Hour and remain vested until the end of the Typika. At the Prokimenon, together with the Priest, they go before the steps of the altar and, having bowed low all together to the Holy Mysteries, open the Holy Doors. The right Deacon exclaims: "Let us attend!", and the left, after the giving of peace by the Priest: "Wisdom! Let us attend!". Also before the first and second reading – the right: "Wisdom!", and the left: "Let us attend!" and they cense everything as usual, as at the beginning of the Liturgy. At the end of the Apostle, and together with it the censing, both deacons stand with the Priest before the steps of the altar and, having bowed all three together to the Holy Mysteries, go out from the sanctuary: the Priest with the Gospel through the middle [doors], and the deacons, having swapped their sides, through the side doors to the analogion. The right Deacon exclaims: "Wisdom, attend!", "Let us hear", the Priest: "The reading from the Holy Gospel according to (Name)", and the left deacon: "Let us attend!". The Priest sings the Gospel. Having finished, the Priest kisses the beginning of the reading, also the right deacon, and after him the left. Having bowed low, the deacons return through their doors to the sanctuary and, together with the Priest, close the Holy Doors. Having bowed low all three together to the Holy Mysteries, they withdraw: the deacons to their places, and the Priest before the iconostasis for "Thou Who at all times".
 2822: 
 2823: If the hierarch or other sacred dignitaries be present in the church, the deacons should cense them before the choirs, and neither the Priest nor the deacons should kiss the Gospel before the hierarch and sacred dignitaries, and therefore both deacons together carry the open Gospel to them for kissing, also to the Priest standing in the Holy Doors and, when he kisses it, the deacons themselves kiss [it], after which they place it on the analogion and, having bowed low to the Holy Mysteries, return, each through his doors, to the sanctuary.
```

---

### Method: `check_royal_hours_trigger`
- **Defined in**: [hours.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/hours.py#L655) (`engine/resolvers/hours.py:L655`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:3.4.6,L2759-2788`

#### Source: `Dolnytsky_Typikon_Master.md:L2759-2788`
```text
 2759: ### 3.4.6 -24 December: Forefeast of the Nativity of Christ
 2760: 
 2761: The Forefeast of the Nativity of Christ covers five days, of Theophany – four. The divine service is celebrated according to the general rule of the Forefeast of the Lord, with the following exceptions:
 2762: 
 2763: ##### At Vespers
 2764: 
 2765: At *“Lord, I have cried”*, on Saturday evening on the Sunday of the Holy Fathers, instead of the 1st Theotokion (Dogmatikon), a stichera of the Forefeast is taken. Likewise on the Apodosis of the Nativity of Christ; if it falls on a Sunday – a stichera of the Feast is taken[^303].
 2766: 
 2767: ##### At Compline
 2768: 
 2769: From 20 December to 14 January, that is until the Apodosis of Theophany, the *Octoechos* canon to the Theotokos is not taken; in the Forefeast of the Nativity of Christ and Theophany the canon of the Forefeast is taken: sometimes one three-ode canon (22, 23 December), sometimes one three-ode canon and a second two-ode canon with it (20 December, 2 January); sometimes two three-ode canons (3 January), sometimes an eight-ode canon (22, 24 December, 4, 5 January). These canons are taken thus: if there is only one canon, then the Heirmoi of each of its odes are taken twice each, troparia on 6 and, again the same Heirmos once for conclusion (instead of Katavasia); if there are two canons, then only the Heirmoi of the first canon are taken twice each, and the Heirmoi of the second canon are taken only once, and this only at the end of each ode; troparia of both canons together on 6. The refrain to the troparia of the canon will be: "Glory to Thee, our God, glory to Thee", "Glory" – on the penultimate, "Both now" – on the last, only instead of "Glory" at the 8th ode, we sing: "Let us bless the Father and the Son and the Holy Spirit, the Lord"[^304]; and to the Katavasia we sing: "We praise, we bless" and the rest, as at Matins. The Katavasia is sung by both choirs together with a bow at its end, at the 8th and 9th odes; also after the Heirmos of the 9th ode, before the troparia, a bow is prescribed[^305]. Otherwise at the 3rd, 6th and 9th odes the canon has nothing. After the canon – either *“It is truly meet”*, as the Moscow Typikon gives on 20 December, or only the Heirmos of the 9th ode, as the Pochaiv and Lviv Trefologia give on 2 January.
 2770: 
 2771: ##### At Matins
 2772: 
 2773: Stichera of the Praises of the Forefeast on 4, Small Doxology and further, in its place, also the Aposticha[^306].
 2774: 
 2775: ##### At the Hours
 2776: 
 2777: Nothing special, except Great Hours, called Royal, on the Eve of the Nativity and Theophany, if they fall on one of the fast days, starting from Monday to Friday, or on Friday before the Eve, if it falls on Saturday or on Sunday.
 2778: 
 2779: ##### At the Divine Liturgy
 2780: 
 2781: Nothing special, except the Liturgy of Basil the Great with Vespers of the Feast on the Eve of the Nativity and Theophany, if they fall on one of the five fast days, from Monday to Friday. For if they fall on Saturday or on Sunday, then on the Eve there will be the Liturgy of Chrysostom, at its proper time without Vespers, and afterwards – Vespers of the Feast, at its proper time. On the Feast itself – Liturgy of Basil the Great without Vespers. On Friday, before the Eve, to which the Royal Hours are transferred, the typikon gives no Liturgy, this is adhered to also by the Lviv Synod[^307].
 2782: 
 2783: Saturday before the Nativity of Christ
 2784: 
 2785: in the middle of the Forefeast of the Nativity of Christ
 2786: 
 2787: See the rule on p. 154.
 2788: 
```

---

### Method: `resolve_typika_kontakia`
- **Defined in**: [hours.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/hours.py#L789) (`engine/resolvers/hours.py:L789`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:3.4.7,L2789-2866`

#### Source: `Dolnytsky_Typikon_Master.md:L2789-2866`
```text
 2789: ### 3.4.7 December: Eve of the Nativity of Christ
 2790: 
 2791: Everything – according to the rule given above for the Forefeast of the Nativity of Christ, however, instead of the usual Hours we sing the Great Hours and the Liturgy of Basil with Vespers. Only, if the Eve falls on Saturday or on Sunday, we sing the Hours before that, on Friday, and the Liturgy of Basil – on the very day of the Feast. On the Eve – Liturgy of Chrysostom, at its proper time, and afterwards – Vespers, at its proper time.
 2792: 
 2793: HOURS
 2794: 
 2795: OF THE EVE OF THE NATIVITY OF CHRIST AND THEOPHANY
 2796: 
 2797: Notes
 2798: 
 2799: The Lviv Synod orders pastors to celebrate these Hours together with the Typika in church, in violet vestments, in view of the fast[^308], in bright vestments it is celebrated before Theophany only when the Hours from Saturday or Sunday are transferred back, to Friday, for then there is no fast, but it will be a general dispensation
 2800: 
 2801: Now we sing all the Hours adding "The Typika" (Typika); and therefore we begin the Hours 3rd, 6th and 9th from "O come, let us worship", and we make the dismissal only at the end of "The Typika"
 2802: 
 2803: These Hours are celebrated in the morning, earlier or later, at the decision of the Superior; according to the custom of the arch-cathedral church – at 9 o'clock before noon[^309], so that there would be a certain distance between the Hours and the Liturgy, which according to the custom of the same church begins at 11 o'clock. If the Hours begin earlier, then the Liturgy can also begin earlier, but since it is celebrated with Vespers, it should begin around 10 o'clock, as the Lviv Synod decreed about Vespers with the Presanctified[^310]
 2804: 
 2805: The composition and form of the Great Hours is the same as of the usual Hours, with the exception of three troparia and three readings, given after the Theotokion "What shall we call Thee" at the 1st Hour and after the corresponding ones at the other Hours. Regarding the essence, the Royal Hours differ from the usual ones also by the tripalm, which at the Royal Hours is special, appropriate to the given feast[^311]
 2806: 
 2807: In the temple, before the Holy Doors, opposite the people, two analogia are placed, on the first of which the Gospel is placed; the second, slightly lower, – opposite the Holy Doors, from which the Paremia and Apostle are to be read. Where there is no analogion for the Gospel, it lies on the Holy Table and is brought out by the Priest through the Holy Doors only for reading, and is supported by servers[^312]
 2808: 
 2809: The Royal Hours are celebrated with the Holy Doors closed, which are opened only for the reading of the Gospel
 2810: 
 2811: Candles on the altar are lit only for the reading of the Gospel
 2812: 
 2813: At the appointed time the Priest enters the temple and, having approached the Holy Table and having bowed low, kisses the Gospel, marks four Gospel readings and, having bowed again, goes out to the sacristy; puts on an epitrachelion, goes out before the closed Holy Doors, makes a low bow to the Holy Mysteries and begins the usual: "Blessed is our God". Choir: "Amen", also "Glory to Thee, our God, glory to Thee", "O Heavenly King" and everything else, as usual, up to "O come, let us worship" inclusive[^313]. At the second "O come, let us worship" the Priest, having bowed low, enters the sanctuary and, while the choirs sing the tripalm, reads it sitting in his place.
 2814: 
 2815: When, after the Troparion of the Forefeast "Once Mary was registered", the Theotokion is also read, the choirs sing three stichera idiomesa[^314]  on 6, that is twice each. The first stichera both the first and the second time is sung without a refrain; the second – the first time with a separate refrain, and the second – with another separate refrain; the third – the first time with the refrain "Glory", and the second – with the refrain "Both now". All four above-mentioned refrains at all Hours – are the same. At the 9th Hour the third stichera is taken three times, that is the first time it is read loudly and piously by the canonarch in the middle of the church, without a refrain, then the second time – by one choir with the refrain "Glory", and the third – by the other with the refrain "Both now"[^315].
 2816: 
 2817: After the singing of the three stichera there will be three readings: the first – of the Prophecy with a Prokimenon, the second – of the Apostle without a Prokimenon and without Alleluia, the third – of the Gospel, beginning it from "Wisdom, attend!", "Let us hear". All this is accompanied by the following actions: when the stichera end, the Priest puts on a phelonion and, having gone out before the steps of the altar and having bowed, opens the Holy Doors and exclaims: "Let us attend! Peace be unto all!" (blessing the people), "Wisdom! Let us attend!". The choirs sing the Prokimenon. After its conclusion the Priest, having exclaimed before the title of the Prophecy "Wisdom!" and before the reading "Let us attend!", waits before the steps of the altar for the end of the reading of the Prophecy and, after its conclusion, having exclaimed "Wisdom!" and "Let us attend!" before the reading of the Apostle, as usual, puts incense into the censer with the short prayer "Incense we offer to Thee" and, having blessed the incense with the words "Blessed is our God", censes everything as usual, that is the Holy Table from four sides, the iconostasis, the choirs and the people[^316]. At the end of the Apostle, and together with it the censing, the candle-bearers go out before the analogion, and the Priest approaches the Holy Table and, having bowed, takes the Holy Gospel and, having placed it on the analogion, begins to sing the Gospel from "Wisdom, attend". After the singing of the Gospel the Priest, having kissed the beginning of the reading, leaves it there, closes the Holy Doors and, having bowed low to the Holy Mysteries, goes out to the sacristy, takes off the phelonion, goes out through the side doors before the Holy Doors for "Thou Who at all times" and remains there until the end of the Hour.
 2818: 
 2819: > **Note:** Since we sing all the Hours together, the prayer of blessing the incense should be said only at the 1st Hour, at the others – only "Blessed is our God" just as at Great Vespers with All-Night Vigil.
 2820: 
 2821: If there be deacons, they put on dalmatics with an orarion before the beginning of the 1st Hour and remain vested until the end of the Typika. At the Prokimenon, together with the Priest, they go before the steps of the altar and, having bowed low all together to the Holy Mysteries, open the Holy Doors. The right Deacon exclaims: "Let us attend!", and the left, after the giving of peace by the Priest: "Wisdom! Let us attend!". Also before the first and second reading – the right: "Wisdom!", and the left: "Let us attend!" and they cense everything as usual, as at the beginning of the Liturgy. At the end of the Apostle, and together with it the censing, both deacons stand with the Priest before the steps of the altar and, having bowed all three together to the Holy Mysteries, go out from the sanctuary: the Priest with the Gospel through the middle [doors], and the deacons, having swapped their sides, through the side doors to the analogion. The right Deacon exclaims: "Wisdom, attend!", "Let us hear", the Priest: "The reading from the Holy Gospel according to (Name)", and the left deacon: "Let us attend!". The Priest sings the Gospel. Having finished, the Priest kisses the beginning of the reading, also the right deacon, and after him the left. Having bowed low, the deacons return through their doors to the sanctuary and, together with the Priest, close the Holy Doors. Having bowed low all three together to the Holy Mysteries, they withdraw: the deacons to their places, and the Priest before the iconostasis for "Thou Who at all times".
 2822: 
 2823: If the hierarch or other sacred dignitaries be present in the church, the deacons should cense them before the choirs, and neither the Priest nor the deacons should kiss the Gospel before the hierarch and sacred dignitaries, and therefore both deacons together carry the open Gospel to them for kissing, also to the Priest standing in the Holy Doors and, when he kisses it, the deacons themselves kiss [it], after which they place it on the analogion and, having bowed low to the Holy Mysteries, return, each through his doors, to the sanctuary.
```

---

### Method: `check_service_continuity`
- **Defined in**: [hours.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/hours.py#L799) (`engine/resolvers/hours.py:L799`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L465-472,§60`
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.2.1,L262-299`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L465-472`
```text
  465: ##### 60. If Orthros is served immediately after Vespers as part of the All-Night
  466: Vigil, the priest closes the holy doors after the ekphonesis: The blessing of the Lord be upon you... and then removes his phelonion.
  467: 
  468: The lector prays aloud Glory to God in the Highest... (three times) and Lord,
  469: You shall open my lips... (twice) and the Six Psalms. The priest leaves via the northern door and secretly recites the Orthros Prayers before the royal doors.[99]
  470: 
  471: --- VARIANT: With Two Deacons ---
  472: 
```

#### Source: `Dolnytsky_Typikon_Master.md:L262-299`
```text
  262: #### 1. Vesting and Initial Censing
  263: 
  264: *After the candles on the main Holy Table are lit and two censers prepared, if two deacons are to serve (if not, then one), the Priest, having blessed the epitrachelion with his hand arranged as for the blessing at Liturgy and having kissed the cross upon it, puts it on himself[^6]. The deacons take upon themselves the sticharion with the orarion, having kissed it beforehand. All three come out, one after another—first the second deacon, after him the first, and last the Priest—from the sacristy to the front of the steps of the Holy Table. Having taken their stand: the first deacon on the left, and the second on the right of the Priest, with the Priest between them, all three bow low to the Holy Mysteries and, having turned all together to the Holy Doors (the Priest and second deacon to the right, and the first deacon to the left), they open them and, having turned toward the Holy Table, likewise by a half-turn, the deacons take the censers, and the Priest, with his right hand, takes the spoon and puts incense first into the censer of the first, and then into the censer of the second deacon. And after the deacons say:*
  265: 
  266: > **Deacons:** "Bless, Master, the censer."
  267: 
  268: *...the Priest blesses both censers in the form of a cross, each separately, and they all recite together the prayer "Incense we offer to Thee," which is given in the *Sluzhebnik* at the end of the Proskomedia. At other censings, instead of this prayer, only the following is said:*
  269: 
  270: > **Priest:** "Blessed is our God always, now and ever, and unto ages of ages."
  271: 
  272: *In churches that are Cathedral Eparchial or Monastic, the second Deacon exclaims to the Priest who stands at that same place:*
  273: 
  274: > **Second Deacon:** "Command!"[^7]
  275: 
  276: *At this time, all rise; the deacons cense, always with three swings of the censer, first the Holy Table from the four sides—namely first from the front both together, bowing low to the Holy Mysteries while doing so; then the first deacon goes to the right side, and the second to the left, each censing his own side of the Holy Table, and also from behind (and, if it exists, the icon behind the Holy Table) both together, and they cense the Priest from the front corners of the Holy Table both together, and come out, each through his own door, to the front of the Holy Doors and, having bowed low to the Holy Mysteries, they turn to the local icons of the iconostasis, each censing the icon on his own side. Also, they go around the temple with smoking censers, each on his own side, censing while doing so the icons of the side altars, if such exist. After this, having returned from the great church doors through the middle of the temple to the front of the Holy Doors and having bowed low to the Holy Mysteries, they turn—the Deacon who is on the right to the left, and the Deacon who is on the left to the right—toward the west, and each censes the kliros on his own side (if the church is a cathedral, also the choirs) and, at the end, both together cense the people.*
  277: 
  278: > **Rubrics on Censing and Bowing:**
  279: > 1. **If the Bishop is present:** In this case, it is proper for the deacons to approach his throne and cense him both together, and after this, having withdrawn to the middle, to cense the kliroi, etc.
  280: > 2. **Bowing rules:** It is proper for the deacons and the Priest, upon the conclusion of the censing of each icon, the Bishop, the kliros, the Choir, and the people, to bow to them; but while censing the Holy Table, to bow only from the front.
  281: 
  282: *After censing the people, the deacons turn to the Holy Doors and the first exclaims:*
  283: 
  284: > **First Deacon:** "Lord, bless."[^8]
  285: 
  286: *After this, both deacons, having bowed low to the Holy Mysteries, return, each through his own door, to the sanctuary.*
  287: 
  288: *If there is only one deacon, he alone censes around the Holy Table and, having exited through the northern door, censes the icons of the local tier on the right side, likewise on the left; having gone around the temple from the right side to the left and having bowed from the Holy Doors to the Holy Mysteries, he censes everything else according to the rubric, and returns to the sanctuary through the southern door.*
  289: 
  290: *If there is no deacon at all, then the Priest censes alone and exclaims:*
  291: 
  292: > **Priest:** "Lord, bless."
  293: 
  294: *Having censed the Holy Table, He exits the sanctuary into the temple through the Holy Doors and, after censing the iconostasis, goes around the temple as prescribed when one deacon serves; upon the conclusion of the censing, he exclaims before the Holy Doors:*
  295: 
  296: > **Priest:** "Lord, bless."[^9]
```

---

### Method: `resolve_presanctified_transfer`
- **Defined in**: [lenten.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/lenten.py#L580) (`engine/resolvers/lenten.py:L580`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L1678-1712,§226`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L1678-1712`
```text
 1678: ##### 226. If the Presanctified Lamb is reserved in the artophorion on the Holy Table, the transfer to the Prothesis table is made at the beginning of the stikhologia
 1679: (18th Kathisma) in this manner: the diskarion, asterisk, and small veil are brought to the Holy Table by the deacon. The priest kisses the Holy Gospel and places it to the right side on the Holy Table.[278] Then he places the diskarion on the left part of the unfolded eiliton,[279] opens the artophorion, and makes a small bow. He takes the ciborium or pyx in which the Lamb is kept and places it in the center of the eiliton. Then, taking the Presanctified Lamb from the vessel, he places the Lamb upon the diskarion with the greatest reverence; he also takes out the Particles necessary for giving Communion to the faithful.[280] After returning the ciborium or pyx to the artophorion, he closes the artophorion. Then he places the diskarion in the center of the eiliton, censes the asterisk and small veil,[281] and covers the diskarion. Preceded by
 1680: [ILLUSTRATION: the deacon who bears a lighted candle, the priest takes the thurible and censes]
 1681: around the Holy Table.[282] After returning before the Holy Table and giving the thurible to the deacon, the priest bows profoundly[283] making the sign of the
 1682: Cross upon himself. Then, he takes the covered diskarion with both hands and, holding it to his forehead, proceeds along the right side of the Holy Table to the Prothesis table as the deacon leads with a lighted candle and censes.
 1683: 
 1684: ##### 227. The priest places the diskarion upon the unfolded eiliton[284] on the
 1685: Prothesis table. Then he pours wine and water into the chalice as prescribed, saying nothing. After he has censed the chalice veil by holding the veil in the smoke over the thurible, he covers the chalice with it; then he censes the large veil in the same manner and, with it, covers the diskarion and the chalice saying nothing except: Through the prayers of our holy Fathers, O Lord Jesus
 1686: Christ our God, have mercy on us. Amen. The priest and deacon make a profound bow[285] and return to the Holy Table; there the priest[286] replaces the book of Holy Gospels upon the folded eiliton.
 1687: 
 1688: ##### 228. If the Presanctified Lamb is kept in an artophorion on the Prothesis table,[287] then the priest and deacon go to the Prothesis table
 1689: 
 1690: at the beginning of the stikhologia. Both make a small bow; the priest opens the artophorion and again makes a small bow after which he censes the Presanctified
 1691: Holy Gifts in strokes of three. Then he takes the Presanctified Lamb from the artophorion and with great reverence places the Lamb upon the diskarion. He pours wine and water into the chalice as usual, but says nothing. After taking the thurible, he censes the asterisk and veils;[288] he then covers the diskarion and chalice with their respective veils and then covers both vessels with the large veil, saying only: Through the prayers ... He makes a profound bow and returns to the Holy Table.
 1692: 
 1693: ##### 229. If the priest considers this opportune,[289] he performs the ceremony of placing the Lamb on the diskarion when the first antiphon is read, the ceremony of censing[290] while the second antiphon is read, and the ceremony of transferring the Presanctified Gifts while the third antiphon is read.
 1694: 
 1695: ##### 230. If it is foreseen that many faithful will come for Communion, to the extent that the Presanctified Lamb alone will not suffice, the priest places an appropriate number of already consecrated Particles on the diskarion, and on these he places the Holy Lamb Itself.[291]
 1696: 
 1697: ##### 231. Following the completion of the stikhologia, the choir begins the Psalm:
 1698: Lord, I have cried ... and the deacon censes as prescribed (see § 33), however, he censes the Presanctified Gifts[292] three times, each time in strokes of three.
 1699: 
 1700: ##### 232. When the: Glory ... now and ever ... is sung, the Holy Doors are opened and the Entrance is made in the usual way; the deacon then censes. If the Gospel is to be read,[293] the deacon makes the Entrance with the Gospel.
 1701: 
 1702: ##### 233. After the deacon has said: Let us pray to the Lord in a subdued voice, the priest secretly recites the Entrance Prayer (In the evening, at dawn, and at noon ...) with its conclusion (... for to You are due all honor ...); when the stikhera are completed, the deacon exclaims: Wisdom! Stand Aright! The choirs: O
 1703: Joyful Light! ... And the priest and deacon enter the Altar. Then, standing at the royal doors, the deacon exclaims: Let us be attentive! Facing the people and blessing, the priest says: Peace be with all.[294] The deacon: Wisdom,
 1704: 
 1705: let us be attentive. The choir sings the Prokeimenon of the first Prophecy. The deacon: Wisdom! The lector, standing midway between the two choirs and looking toward the east: A reading from Genesis.[295] The deacon, Let us be attentive.
 1706: The lector reads the first Prophecy. Then the choir sings the second
 1707: Prokeimenon.
 1708: 
 1709: ##### 234. Immediately after the second Prokeimenon, the deacon, turning towards the priest, exclaims: Command! Taking a lighted candle together with the thurible,
 1710: [ILLUSTRATION: the priest holds them with both hands joined together and stands before the Holy]
 1711: Table facing the east; making a distinct sign of the Cross with the candle and thurible, he exclaims: Wisdom! Stand Aright! Then turning toward the west, in the direction of the people, he again makes the sign of the Cross, saying in a loud voice: The light of Christ ... And again turning toward the east, the priest returns the candle and thurible to the server. After this, all those present in the Altar and in the church make three great metanies.[296] The lector: A reading from Proverbs.[297] The deacon: Let us be attentive. The royal doors are closed and the second Prophecy is read.
 1712: 
```

---

### Method: `resolve_trisagion_type`
- **Defined in**: [liturgy.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/liturgy.py#L595) (`engine/resolvers/liturgy.py:L595`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:2.20,L1767-1774`

#### Source: `Dolnytsky_Typikon_Master.md:L1767-1774`
```text
 1767: ### At the Divine Liturgy
 1768: 
 1769: 1. **Antiphons:** Apodosis of the Lord—festal antiphons; Apodosis of Theotokos—daily antiphons.
 1770: 2. **Entrance:** Troparion; **Glory, Both now:** Kontakion of the Feast; Trisagion.
 1771: 3. **Prokimenon, Alleluia & Communion Hymn:** All of the Feast.
 1772: 4. **Readings:** On Apodosis of the Lord—Epistle and Gospel of the weekday alone; on Apodosis of Theotokos—first of the weekday, then of the Feast.
 1773: 
 1774: <div style="page-break-after: always;"></div>
```

---

### Method: `resolve_basil_megalynarion`
- **Defined in**: [liturgy.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/liturgy.py#L788) (`engine/resolvers/liturgy.py:L788`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:L11661-11720`

#### Source: `Dolnytsky_Typikon_Master.md:L11661-11720`
```text
11661: ## Rubrics of the Divine Liturgy of St. John Chrysostom & St. Basil
11662: 
11663: of St. John Chrysostom and St. Basil the Great
11664: 
11665: ### In Concelebration of One Deacon
11666: 
11667: 1. According to the ancient custom of the Eastern Church, only one Holy Liturgy may be celebrated at the same holy table. However, one may depart from this rule if the Divine Liturgy must be repeated for the benefit of the faithful. If there is one or several secondary churches in the parish, then the more solemn Liturgy is celebrated in the main sanctuary, and other liturgies should be celebrated rather in the side sanctuaries
11668: 
11669: 2. The Eucharistic bread does not absolutely have to be baked on the day the Holy Sacrifice is offered. The same bread can be kept for several days and used at several liturgies, provided that all the ceremonies of the Proskomedia are observed over it or over a part of it, cutting the bread and removing the Lamb and particles according to the prescription. Also, it is not necessary to always use five prosphora, if the Lamb and all particles can be taken from one and the same prosphora. The custom of using five prosphora may be kept, if one pleases, when celebrating more solemn liturgies (see no. 179)
11670: 
11671: 3. The Priest who wishes to serve the Sacrament must first of all be reconciled with all and hold nothing against anyone, keep his heart as far as possible from evil thoughts, be continent already from the evening and keep the fast until the very time of the service and prepare himself for the offering of the sacrifice by prayers (see no. 190)
11672: 
11673: 4. At the prescribed time, the Priest enters the church and, together with the Deacon, bows three times before the holy doors to the east
11674: 
11675: Then the Deacon says in a low voice: "Bless, Master."
11676: 
11677: > **Priest**: "Blessed is our God."
11678: 
11679: > **Deacon**: "Amen."
11680: 
11681: And the Deacon begins to say: "Glory to Thee, our God," "O Heavenly King," *“Holy God”* (3), "Glory, Both now," "Most Holy Trinity," "Lord, have mercy" (3), "Glory, Both now," "Our Father."
11682: 
11683: > **Priest**: "For Thine is the kingdom."
11684: 
11685: > **Deacon**: "Amen."
11686: 
11687: Then they recite together: "Have mercy on us, O Lord, have mercy on us," Glory: "Lord, have mercy on us," Both now: "The door of compassion."
11688: 
11689: They approach the icon of the Savior, venerate it with a small bow and, kissing it, say: "We worship Thine immaculate Icon."
11690: 
11691: Having bowed before the holy doors, in the same manner they venerate and kiss the icon of the Theotokos, saying the troparion "Forasmuch as Thou Art a well-spring of compassion."
11692: 
11693: 5. After this the Priest and deacon return before the holy doors, and the Priest, bowing his head, recites the prayer "O Lord, stretch forth Thy hand."
11694: 
11695: Then the Priest and deacon bow also to the right and left choirs and go into the sanctuary: the Priest – through the southern, and the Deacon – through the northern doors, saying: "I will enter into Thy house" (see no. 178).
```

---

### Method: `resolve_communion_hymn`
- **Defined in**: [liturgy.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/liturgy.py#L834) (`engine/resolvers/liturgy.py:L834`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:2.5,L1211-1216`

#### Source: `Dolnytsky_Typikon_Master.md:L1211-1216`
```text
 1211: ### At the Divine Liturgy
 1212: 
 1213: * Everything to the saint. Epistle and Gospel: first of the weekday, then of the saint.
 1214: 
 1215: ---
 1216: 
```

---

### Method: `resolve_post_communion_hymn`
- **Defined in**: [liturgy.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/liturgy.py#L1144) (`engine/resolvers/liturgy.py:L1144`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:2.2,L1053-1068`

#### Source: `Dolnytsky_Typikon_Master.md:L1053-1068`
```text
 1053: ### At the Divine Liturgy
 1054: 
 1055: 1. **Troparia & Kontakia (Daily Custom):** Troparion of the weekday; **Glory:** Kontakion of the day, **Both now:** Kontakion of the Temple (if of the Lord or Theotokos). If the Temple is of a saint: general Theotokion *“O Protection of Christians”*[^89] or festal Theotokion[^90]. (On Wednesday and Friday, replace the troparion of the day with the Kontakion of the Cross with *“Glory, Both now”*).
 1056: 2. **Prokimenon, Alleluia & Communion Hymn:** Of the weekday from the *Sluzhebnik* or *Apostolos*.
 1057: 3. **Readings:** Sequential daily Apostle and Gospel[^91].
 1058: 
 1059: > **Notes on Combining Services at Liturgy:**
 1060: > * *If celebrated only to the saint:* Theotokion or Kontakion of the Temple is taken as above.
 1061: > * *If celebrated for a specific need:* Theotokion of the need; if none, the troparion of the need is replaced by its Kontakion with *“Glory, Both now”*.
 1062: > * *If celebrated for both the day and the saint:* Troparion of the day, then of the saint; Kontakion of the day; **Glory:** Kontakion of the saint, **Both now:** Theotokion/Kontakion of the Temple.
 1063: > * *If celebrated for the day/saint and a need:* Service of the day/saint precedes the need; Kontakion of the day/saint; **Glory:** Kontakion for need, **Both now:** Theotokion for need.
 1064: > * *Votive / Need Liturgies:* Must always be celebrated singly, except for the daily Apostle/Gospel which may precede the readings for the dead[^92].
 1065: > * *Cathedral vs Parish Practice:* In cathedrals, the daily Apostle/Gospel is never omitted[^93]. Where multiple readings coincide, Slavic typikons combine them under the refrain of the first reading[^94][^95][^96][^97].
 1066: 
 1067: ---
 1068: 
```

---

### Method: `resolve_vesperal_liturgy_readings`
- **Defined in**: [liturgy.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/liturgy.py#L1237) (`engine/resolvers/liturgy.py:L1237`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:3.4.6,L2759-2788`

#### Source: `Dolnytsky_Typikon_Master.md:L2759-2788`
```text
 2759: ### 3.4.6 -24 December: Forefeast of the Nativity of Christ
 2760: 
 2761: The Forefeast of the Nativity of Christ covers five days, of Theophany – four. The divine service is celebrated according to the general rule of the Forefeast of the Lord, with the following exceptions:
 2762: 
 2763: ##### At Vespers
 2764: 
 2765: At *“Lord, I have cried”*, on Saturday evening on the Sunday of the Holy Fathers, instead of the 1st Theotokion (Dogmatikon), a stichera of the Forefeast is taken. Likewise on the Apodosis of the Nativity of Christ; if it falls on a Sunday – a stichera of the Feast is taken[^303].
 2766: 
 2767: ##### At Compline
 2768: 
 2769: From 20 December to 14 January, that is until the Apodosis of Theophany, the *Octoechos* canon to the Theotokos is not taken; in the Forefeast of the Nativity of Christ and Theophany the canon of the Forefeast is taken: sometimes one three-ode canon (22, 23 December), sometimes one three-ode canon and a second two-ode canon with it (20 December, 2 January); sometimes two three-ode canons (3 January), sometimes an eight-ode canon (22, 24 December, 4, 5 January). These canons are taken thus: if there is only one canon, then the Heirmoi of each of its odes are taken twice each, troparia on 6 and, again the same Heirmos once for conclusion (instead of Katavasia); if there are two canons, then only the Heirmoi of the first canon are taken twice each, and the Heirmoi of the second canon are taken only once, and this only at the end of each ode; troparia of both canons together on 6. The refrain to the troparia of the canon will be: "Glory to Thee, our God, glory to Thee", "Glory" – on the penultimate, "Both now" – on the last, only instead of "Glory" at the 8th ode, we sing: "Let us bless the Father and the Son and the Holy Spirit, the Lord"[^304]; and to the Katavasia we sing: "We praise, we bless" and the rest, as at Matins. The Katavasia is sung by both choirs together with a bow at its end, at the 8th and 9th odes; also after the Heirmos of the 9th ode, before the troparia, a bow is prescribed[^305]. Otherwise at the 3rd, 6th and 9th odes the canon has nothing. After the canon – either *“It is truly meet”*, as the Moscow Typikon gives on 20 December, or only the Heirmos of the 9th ode, as the Pochaiv and Lviv Trefologia give on 2 January.
 2770: 
 2771: ##### At Matins
 2772: 
 2773: Stichera of the Praises of the Forefeast on 4, Small Doxology and further, in its place, also the Aposticha[^306].
 2774: 
 2775: ##### At the Hours
 2776: 
 2777: Nothing special, except Great Hours, called Royal, on the Eve of the Nativity and Theophany, if they fall on one of the fast days, starting from Monday to Friday, or on Friday before the Eve, if it falls on Saturday or on Sunday.
 2778: 
 2779: ##### At the Divine Liturgy
 2780: 
 2781: Nothing special, except the Liturgy of Basil the Great with Vespers of the Feast on the Eve of the Nativity and Theophany, if they fall on one of the five fast days, from Monday to Friday. For if they fall on Saturday or on Sunday, then on the Eve there will be the Liturgy of Chrysostom, at its proper time without Vespers, and afterwards – Vespers of the Feast, at its proper time. On the Feast itself – Liturgy of Basil the Great without Vespers. On Friday, before the Eve, to which the Royal Hours are transferred, the typikon gives no Liturgy, this is adhered to also by the Lviv Synod[^307].
 2782: 
 2783: Saturday before the Nativity of Christ
 2784: 
 2785: in the middle of the Forefeast of the Nativity of Christ
 2786: 
 2787: See the rule on p. 154.
 2788: 
```

---

### Method: `resolve_liturgy_readings`
- **Defined in**: [liturgy.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/liturgy.py#L1351) (`engine/resolvers/liturgy.py:L1351`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:2.5,L1211-1216`

#### Source: `Dolnytsky_Typikon_Master.md:L1211-1216`
```text
 1211: ### At the Divine Liturgy
 1212: 
 1213: * Everything to the saint. Epistle and Gospel: first of the weekday, then of the saint.
 1214: 
 1215: ---
 1216: 
```

---

### Method: `resolve_reading_ot`
- **Defined in**: [liturgy.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/liturgy.py#L2295) (`engine/resolvers/liturgy.py:L2295`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.2.1,L370-385`

#### Source: `Dolnytsky_Typikon_Master.md:L370-385`
```text
  370: #### 4. Prokimenon and Readings
  371: 
  372: *After the singing of "Gladsome Light," the deacons approach the Holy Doors and the first of them, looking at the people, exclaims:*
  373: 
  374: > **First Deacon:** "Let us be attentive."
  375: 
  376: *...the Priest, also having turned his right side to the people, blesses them in the form of a cross with his right hand, arranged as for the blessing at Liturgy, singing:*
  377: 
  378: > **Priest:** "Peace be unto all."
  379: 
  380: *...and then, the second deacon also exclaims to the people:*
  381: 
  382: > **Second Deacon:** "Wisdom! Let us be attentive!"
  383: 
  384: *During the singing of the Prokimenon with its verses, all three turn to the Holy Table, and the Priest, having bowed low to the Holy Mysteries, goes to the right behind the Holy Table and sits there during the readings. The deacons remain near the Holy Doors and, before the title of each reading, the first of them exclaims to the people: "Wisdom!", and after the title—the second, likewise to the people: "Let us be attentive!". If there are no deacons, the Priest exclaims all this from his place.*
  385: 
```

---

### Method: `resolve_reading_epistle`
- **Defined in**: [liturgy.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/liturgy.py#L2317) (`engine/resolvers/liturgy.py:L2317`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.2.1,L370-385`

#### Source: `Dolnytsky_Typikon_Master.md:L370-385`
```text
  370: #### 4. Prokimenon and Readings
  371: 
  372: *After the singing of "Gladsome Light," the deacons approach the Holy Doors and the first of them, looking at the people, exclaims:*
  373: 
  374: > **First Deacon:** "Let us be attentive."
  375: 
  376: *...the Priest, also having turned his right side to the people, blesses them in the form of a cross with his right hand, arranged as for the blessing at Liturgy, singing:*
  377: 
  378: > **Priest:** "Peace be unto all."
  379: 
  380: *...and then, the second deacon also exclaims to the people:*
  381: 
  382: > **Second Deacon:** "Wisdom! Let us be attentive!"
  383: 
  384: *During the singing of the Prokimenon with its verses, all three turn to the Holy Table, and the Priest, having bowed low to the Holy Mysteries, goes to the right behind the Holy Table and sits there during the readings. The deacons remain near the Holy Doors and, before the title of each reading, the first of them exclaims to the people: "Wisdom!", and after the title—the second, likewise to the people: "Let us be attentive!". If there are no deacons, the Priest exclaims all this from his place.*
  385: 
```

---

### Method: `resolve_reading_gospel`
- **Defined in**: [liturgy.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/liturgy.py#L2345) (`engine/resolvers/liturgy.py:L2345`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.2.1,L370-385`

#### Source: `Dolnytsky_Typikon_Master.md:L370-385`
```text
  370: #### 4. Prokimenon and Readings
  371: 
  372: *After the singing of "Gladsome Light," the deacons approach the Holy Doors and the first of them, looking at the people, exclaims:*
  373: 
  374: > **First Deacon:** "Let us be attentive."
  375: 
  376: *...the Priest, also having turned his right side to the people, blesses them in the form of a cross with his right hand, arranged as for the blessing at Liturgy, singing:*
  377: 
  378: > **Priest:** "Peace be unto all."
  379: 
  380: *...and then, the second deacon also exclaims to the people:*
  381: 
  382: > **Second Deacon:** "Wisdom! Let us be attentive!"
  383: 
  384: *During the singing of the Prokimenon with its verses, all three turn to the Holy Table, and the Priest, having bowed low to the Holy Mysteries, goes to the right behind the Holy Table and sits there during the readings. The deacons remain near the Holy Doors and, before the title of each reading, the first of them exclaims to the people: "Wisdom!", and after the title—the second, likewise to the people: "Let us be attentive!". If there are no deacons, the Priest exclaims all this from his place.*
  385: 
```

---

### Method: `resolve_beatitudes`
- **Defined in**: [liturgy.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/liturgy.py#L2375) (`engine/resolvers/liturgy.py:L2375`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:2.2,L1053-1068`

#### Source: `Dolnytsky_Typikon_Master.md:L1053-1068`
```text
 1053: ### At the Divine Liturgy
 1054: 
 1055: 1. **Troparia & Kontakia (Daily Custom):** Troparion of the weekday; **Glory:** Kontakion of the day, **Both now:** Kontakion of the Temple (if of the Lord or Theotokos). If the Temple is of a saint: general Theotokion *“O Protection of Christians”*[^89] or festal Theotokion[^90]. (On Wednesday and Friday, replace the troparion of the day with the Kontakion of the Cross with *“Glory, Both now”*).
 1056: 2. **Prokimenon, Alleluia & Communion Hymn:** Of the weekday from the *Sluzhebnik* or *Apostolos*.
 1057: 3. **Readings:** Sequential daily Apostle and Gospel[^91].
 1058: 
 1059: > **Notes on Combining Services at Liturgy:**
 1060: > * *If celebrated only to the saint:* Theotokion or Kontakion of the Temple is taken as above.
 1061: > * *If celebrated for a specific need:* Theotokion of the need; if none, the troparion of the need is replaced by its Kontakion with *“Glory, Both now”*.
 1062: > * *If celebrated for both the day and the saint:* Troparion of the day, then of the saint; Kontakion of the day; **Glory:** Kontakion of the saint, **Both now:** Theotokion/Kontakion of the Temple.
 1063: > * *If celebrated for the day/saint and a need:* Service of the day/saint precedes the need; Kontakion of the day/saint; **Glory:** Kontakion for need, **Both now:** Theotokion for need.
 1064: > * *Votive / Need Liturgies:* Must always be celebrated singly, except for the daily Apostle/Gospel which may precede the readings for the dead[^92].
 1065: > * *Cathedral vs Parish Practice:* In cathedrals, the daily Apostle/Gospel is never omitted[^93]. Where multiple readings coincide, Slavic typikons combine them under the refrain of the first reading[^94][^95][^96][^97].
 1066: 
 1067: ---
 1068: 
```

---

### Method: `resolve_liturgy_alleluia`
- **Defined in**: [liturgy.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/liturgy.py#L2449) (`engine/resolvers/liturgy.py:L2449`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:2.5,L1211-1216`

#### Source: `Dolnytsky_Typikon_Master.md:L1211-1216`
```text
 1211: ### At the Divine Liturgy
 1212: 
 1213: * Everything to the saint. Epistle and Gospel: first of the weekday, then of the saint.
 1214: 
 1215: ---
 1216: 
```

---

### Method: `resolve_service_type`
- **Defined in**: [matins.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/matins.py#L2290) (`engine/resolvers/matins.py:L2290`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.1,L244-255`

#### Source: `Dolnytsky_Typikon_Master.md:L244-255`
```text
  244: ## 1.1 On the Constituent Parts of the Divine Service
  245: 
  246: There are nine parts of the Divine Service: Vespers, Compline, Midnight Office,[^4] Matins, four Hours (that is: I, III, VI, and IX), and the Liturgy or, instead of it, the Typika[^5].
  247: 
  248: Except for the four Hours, of which each has one and the same form, all other parts of the Divine Service have several forms, namely:
  249: 
  250: * **Vespers:** Great, Daily, and Small; and Great Vespers, in turn, can be with an All-Night Vigil or without it;
  251: * **Compline:** Great and Small, and Great Compline can be with an All-Night Vigil or without it;
  252: * **Midnight Office:** Daily, Saturday, and Sunday;
  253: * **Matins:** Great and Small (or Daily), and Great Matins can be with an All-Night Vigil or without it;
  254: * **Liturgy:** Full: of St. John Chrysostom and of St. Basil the Great; and Incomplete, that is, of the Presanctified Gifts.
  255: 
```

---

### Method: `resolve_god_is_lord_tone`
- **Defined in**: [matins.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/matins.py#L2298) (`engine/resolvers/matins.py:L2298`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.5.1,L683-693`

#### Source: `Dolnytsky_Typikon_Master.md:L683-693`
```text
  683: #### 2. Order of Troparia at *“God is the Lord”*
  684: 
  685: * **On a Feast of the Lord or of the Theotokos:** Troparion of the Feast twice; **Glory, Both now:** troparion of the Feast once more.
  686: * **On a Sunday with a Saint having a troparion:** Sunday troparion of the current tone twice; **Glory:** troparion of the Saint once; **Both now:** Sunday Theotokion in the tone of the Saint's troparion.
  687: * **On a Sunday with two Saints:** Sunday troparion once, troparion of the first Saint once; **Glory:** troparion of the second Saint once; **Both now:** Sunday Theotokion in the tone of the second Saint[^24].
  688: * **On a Sunday in a Feast/Afterfeast with a Saint:** Sunday troparion twice; **Glory:** troparion of the Saint; **Both now:** troparion of the Feast[^25].
  689: * **On a weekday with a Saint:** Troparion of the Saint twice; **Glory, Both now:** Theotokion (Sunday Theotokion if Polyeleos; Daily Dismissal Theotokion if non-Polyeleos).
  690: * **On a weekday with two non-Polyeleos Saints:** Troparion of the first Saint twice; **Glory:** of the second Saint once; **Both now:** Daily Dismissal Theotokion in the tone of the second Saint.
  691: * **On a weekday in a Feast with a Saint:** Troparion of the Feast twice; **Glory:** troparion of the Saint; **Both now:** troparion of the Feast[^3a].
  692: * **On a weekday in a Feast with two Saints:** Troparion of the Feast once, of the first Saint once; **Glory:** of the second Saint once; **Both now:** troparion of the Feast[^26].
  693: 
```

---

### Method: `calculate_canon_ratios`
- **Defined in**: [matins.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/matins.py#L2309) (`engine/resolvers/matins.py:L2309`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:2.2,L717-748,L1025-1047`

#### Source: `Dolnytsky_Typikon_Master.md:L717-748`
```text
  717: #### 5. Order of the Matins Canon
  718: 
  719: *The Canon consists of eight odes (outside the Great Fast, where Ode 2 is omitted) or nine odes (during Lent). Canons are taken on 12 or 14 troparia.*
  720: 
  721: * **Distribution of Canons:**
  722:   * *Festal Services:* 1 or 2 canons taken to make 12 troparia, with the Heirmos sung twice.
  723:   * *Saint during a Feast:* Canons taken to make 12 (or 14 if two saints), with the Heirmos of the first canon only[^30].
  724:   * *Sunday with Saint:* Canons taken to make 14 (Resurrection, Cross-Resurrection, Theotokos, and *Menaion*)[^31].
  725: 
  726: * **Refrains to the Odes:**
  727:   * *Feast of the Lord:* "Glory, O Lord, to Thy holy (Transfiguration / Nativity / Cross)[^33]."
  728:   * *Resurrection (Sunday):* "Glory, O Lord, to Thy holy Resurrection."
  729:   * *Theotokos:* "O Most Holy Theotokos, save us."
  730:   * *Saint:* "[Title and Name], pray to God for us."
  731:   * *For the Departed:* "Give rest, O Lord, to the soul[s] of Thy departed servant[s]."
  732:   * *Before the penultimate troparion of the last canon:* "**Glory:**"
  733:   * *Before the final Theotokion:* "**Both now:**"
  734: 
  735: * **Katavasias:**
  736:   * Sung after each ode, according to the season (or the general Marian Katavasia "I shall open my mouth")[^32].
  737:   * *At the 8th Ode:* Preceded by the refrain: "We praise, we bless, we worship the Lord, praising and magnifying Him unto all ages."
  738: 
  739: * **The 9th Ode (Magnificat):**
  740:   * Introduced by the Deacon/Priest:
  741:     > **Deacon:** "The Theotokos and Mother of the Light let us magnify in songs."[^34]
  742:   * The Song of the Theotokos ("My soul magnifies the Lord") with the refrain *“More honorable than the Cherubim”* is sung, while the Deacon censes the altar and temple. (On Great Feasts of the Lord and Theotokos, proper festal refrains are sung instead of the Magnificat).
  743: 
  744: * **Hymnography after Odes 3, 6, and 9:**
  745:   * *After the 3rd Ode:* Small Litany, followed by the **Sessional Hymn** of the Saint / Feast (on a Polyeleos or six-troparia Saint, the Sessional Hymn and Exaposteilarion are taken twice[^35], then Both now: his Theotokion; if the Saint has two Sessional Hymns, the second is taken with the refrain Glory, then Both now: his Theotokion[^36]).
  746:   * *After the 6th Ode:* Small Litany, followed by the **Kontakion and Ikos** (Resurrectional or Festal)[^37].
  747:   * *After the 9th Ode:* Small Litany. On Sundays: "Holy is the Lord our God" (3), followed by the appointed **Exaposteilarion (Hymn of Light)**[^38].
  748: 
```

#### Source: `Dolnytsky_Typikon_Master.md:L1025-1047`
```text
 1025: ### At Matins
 1026: 
 1027: 1. **On *"God is the Lord"*:* Troparion of the saint twice; **Glory, Both now:** Dismissal Theotokion in the tone of the saint's troparion and day of the week[^75].
 1028:    * *If two saints occur:* Troparion to the first saint twice; **Glory:** to the second once, **Both now:** Dismissal Theotokion in the tone of the second saint[^76].
 1029: 2. **Kathismata:** Two current Kathismata, after each of which: Small Litany and Sessional Hymn from the *Octoechos*[^77].
 1030: 3. **Canons (3 canons on 14):**
 1031:    * *Distribution:* First canon of the *Octoechos* with Heirmos on 6; second of the *Octoechos* without Heirmos on 4; and of the saint from the *Menaion* without Heirmos on 4.
 1032:    * *Katavasia:* Only after Odes 3, 6, 8, and 9 (the Heirmos of the saint's canon)[^78].
 1033:    * *After the 3rd Ode:* Sessional Hymn of the saint.
 1034:    * *After the 6th Ode:* Kontakion and Ikos of the saint (if appointed).
 1035:    * *After the 9th Ode:* Exaposteilarion from the *Octoechos*; **Glory:** Exaposteilarion of the saint (if appointed), **Both now:** Theotokion of the saint's Exaposteilarion. (If the saint has none: **Glory, Both now:** Theotokion of the *Octoechos* Exaposteilarion. On Wednesday/Friday, the Stavrotheotokion of the *Octoechos* is taken; on Thursday, the Theotokion of St. Nicholas from the *Octoechos*)[^79].
 1036:    * *If two saints occur:* First canon of the *Octoechos* with Heirmos on 6; canon of the first saint on 4; canon of the second saint on 4[^80]. Katavasia after Odes 3, 6, 8, 9 (Heirmos of the second saint)[^81]. After the 3rd Ode: Kontakion-Ikos of the second saint, Sessional Hymn of the first; **Glory:** Sessional Hymn of the second, **Both now:** his Theotokion[^82]. After the 6th Ode: Kontakion-Ikos of the first saint. After the 9th Ode: Exaposteilarion of the *Octoechos*, of the first saint; **Glory:** of the second, **Both now:** his Theotokion[^83].
 1037:    * *If a saint on 6 occurs:* First canon of the *Octoechos* with Heirmos on 4 (omitting 2 Martyria, except Thursday), second of the *Octoechos* on 4, and of the saint on 6[^84].
 1038: 4. **Aposticha:** All from the *Octoechos*. If there is a Doxastikon to the saint: **Both now:** Theotokion of the Matins Aposticha in the tone of the Doxastikon and day of the week.
 1039: 5. **Conclusion:** Troparion of the saint; **Glory, Both now:** Dismissal Theotokion in the tone of the saint's troparion and day of the week (different from the one at Vespers).
 1040:    * *If two saints occur:* Troparion of the first; **Glory:** of the second, **Both now:** Dismissal Theotokion in the tone of the second[^85].
 1041: 
 1042: > **Notes on a Saint on 6:**
 1043: > 1. Sometimes a saint on 6 differs from a saint on 4 only by having 6 troparia in the Matins Canon and 6 stichera on *“Lord, I have cried”* (e.g. September 9).
 1044: > 2. Sometimes he has a proper sticheron with refrain on the Aposticha of Matins, plus a Doxastikon (e.g. November 17).
 1045: > 3. Sometimes he has 4 Praises stichera, followed by the Small Doxology and the *Octoechos* Aposticha (e.g. September 6, October 7)[^86].
 1046: > 4. Sometimes he has Praises stichera, Great Doxology, Dogmatikon on *“Lord, I have cried”*, proper Aposticha, and Sunday Theotokia (e.g. October 23, July 25). If a Feast of the Lord or Theotokos on 6, the canon is taken without the *Octoechos* (July 2, August 16, 31).
 1047: 
```

---

### Method: `resolve_canon_combination`
- **Defined in**: [matins.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/matins.py#L2347) (`engine/resolvers/matins.py:L2347`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:2.2,L717-748,L1025-1047`

#### Source: `Dolnytsky_Typikon_Master.md:L717-748`
```text
  717: #### 5. Order of the Matins Canon
  718: 
  719: *The Canon consists of eight odes (outside the Great Fast, where Ode 2 is omitted) or nine odes (during Lent). Canons are taken on 12 or 14 troparia.*
  720: 
  721: * **Distribution of Canons:**
  722:   * *Festal Services:* 1 or 2 canons taken to make 12 troparia, with the Heirmos sung twice.
  723:   * *Saint during a Feast:* Canons taken to make 12 (or 14 if two saints), with the Heirmos of the first canon only[^30].
  724:   * *Sunday with Saint:* Canons taken to make 14 (Resurrection, Cross-Resurrection, Theotokos, and *Menaion*)[^31].
  725: 
  726: * **Refrains to the Odes:**
  727:   * *Feast of the Lord:* "Glory, O Lord, to Thy holy (Transfiguration / Nativity / Cross)[^33]."
  728:   * *Resurrection (Sunday):* "Glory, O Lord, to Thy holy Resurrection."
  729:   * *Theotokos:* "O Most Holy Theotokos, save us."
  730:   * *Saint:* "[Title and Name], pray to God for us."
  731:   * *For the Departed:* "Give rest, O Lord, to the soul[s] of Thy departed servant[s]."
  732:   * *Before the penultimate troparion of the last canon:* "**Glory:**"
  733:   * *Before the final Theotokion:* "**Both now:**"
  734: 
  735: * **Katavasias:**
  736:   * Sung after each ode, according to the season (or the general Marian Katavasia "I shall open my mouth")[^32].
  737:   * *At the 8th Ode:* Preceded by the refrain: "We praise, we bless, we worship the Lord, praising and magnifying Him unto all ages."
  738: 
  739: * **The 9th Ode (Magnificat):**
  740:   * Introduced by the Deacon/Priest:
  741:     > **Deacon:** "The Theotokos and Mother of the Light let us magnify in songs."[^34]
  742:   * The Song of the Theotokos ("My soul magnifies the Lord") with the refrain *“More honorable than the Cherubim”* is sung, while the Deacon censes the altar and temple. (On Great Feasts of the Lord and Theotokos, proper festal refrains are sung instead of the Magnificat).
  743: 
  744: * **Hymnography after Odes 3, 6, and 9:**
  745:   * *After the 3rd Ode:* Small Litany, followed by the **Sessional Hymn** of the Saint / Feast (on a Polyeleos or six-troparia Saint, the Sessional Hymn and Exaposteilarion are taken twice[^35], then Both now: his Theotokion; if the Saint has two Sessional Hymns, the second is taken with the refrain Glory, then Both now: his Theotokion[^36]).
  746:   * *After the 6th Ode:* Small Litany, followed by the **Kontakion and Ikos** (Resurrectional or Festal)[^37].
  747:   * *After the 9th Ode:* Small Litany. On Sundays: "Holy is the Lord our God" (3), followed by the appointed **Exaposteilarion (Hymn of Light)**[^38].
  748: 
```

#### Source: `Dolnytsky_Typikon_Master.md:L1025-1047`
```text
 1025: ### At Matins
 1026: 
 1027: 1. **On *"God is the Lord"*:* Troparion of the saint twice; **Glory, Both now:** Dismissal Theotokion in the tone of the saint's troparion and day of the week[^75].
 1028:    * *If two saints occur:* Troparion to the first saint twice; **Glory:** to the second once, **Both now:** Dismissal Theotokion in the tone of the second saint[^76].
 1029: 2. **Kathismata:** Two current Kathismata, after each of which: Small Litany and Sessional Hymn from the *Octoechos*[^77].
 1030: 3. **Canons (3 canons on 14):**
 1031:    * *Distribution:* First canon of the *Octoechos* with Heirmos on 6; second of the *Octoechos* without Heirmos on 4; and of the saint from the *Menaion* without Heirmos on 4.
 1032:    * *Katavasia:* Only after Odes 3, 6, 8, and 9 (the Heirmos of the saint's canon)[^78].
 1033:    * *After the 3rd Ode:* Sessional Hymn of the saint.
 1034:    * *After the 6th Ode:* Kontakion and Ikos of the saint (if appointed).
 1035:    * *After the 9th Ode:* Exaposteilarion from the *Octoechos*; **Glory:** Exaposteilarion of the saint (if appointed), **Both now:** Theotokion of the saint's Exaposteilarion. (If the saint has none: **Glory, Both now:** Theotokion of the *Octoechos* Exaposteilarion. On Wednesday/Friday, the Stavrotheotokion of the *Octoechos* is taken; on Thursday, the Theotokion of St. Nicholas from the *Octoechos*)[^79].
 1036:    * *If two saints occur:* First canon of the *Octoechos* with Heirmos on 6; canon of the first saint on 4; canon of the second saint on 4[^80]. Katavasia after Odes 3, 6, 8, 9 (Heirmos of the second saint)[^81]. After the 3rd Ode: Kontakion-Ikos of the second saint, Sessional Hymn of the first; **Glory:** Sessional Hymn of the second, **Both now:** his Theotokion[^82]. After the 6th Ode: Kontakion-Ikos of the first saint. After the 9th Ode: Exaposteilarion of the *Octoechos*, of the first saint; **Glory:** of the second, **Both now:** his Theotokion[^83].
 1037:    * *If a saint on 6 occurs:* First canon of the *Octoechos* with Heirmos on 4 (omitting 2 Martyria, except Thursday), second of the *Octoechos* on 4, and of the saint on 6[^84].
 1038: 4. **Aposticha:** All from the *Octoechos*. If there is a Doxastikon to the saint: **Both now:** Theotokion of the Matins Aposticha in the tone of the Doxastikon and day of the week.
 1039: 5. **Conclusion:** Troparion of the saint; **Glory, Both now:** Dismissal Theotokion in the tone of the saint's troparion and day of the week (different from the one at Vespers).
 1040:    * *If two saints occur:* Troparion of the first; **Glory:** of the second, **Both now:** Dismissal Theotokion in the tone of the second[^85].
 1041: 
 1042: > **Notes on a Saint on 6:**
 1043: > 1. Sometimes a saint on 6 differs from a saint on 4 only by having 6 troparia in the Matins Canon and 6 stichera on *“Lord, I have cried”* (e.g. September 9).
 1044: > 2. Sometimes he has a proper sticheron with refrain on the Aposticha of Matins, plus a Doxastikon (e.g. November 17).
 1045: > 3. Sometimes he has 4 Praises stichera, followed by the Small Doxology and the *Octoechos* Aposticha (e.g. September 6, October 7)[^86].
 1046: > 4. Sometimes he has Praises stichera, Great Doxology, Dogmatikon on *“Lord, I have cried”*, proper Aposticha, and Sunday Theotokia (e.g. October 23, July 25). If a Feast of the Lord or Theotokos on 6, the canon is taken without the *Octoechos* (July 2, August 16, 31).
 1047: 
```

---

### Method: `get_katavasia`
- **Defined in**: [matins.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/matins.py#L2356) (`engine/resolvers/matins.py:L2356`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:2.3,L735-738,L1097-1116`

#### Source: `Dolnytsky_Typikon_Master.md:L735-738`
```text
  735: * **Katavasias:**
  736:   * Sung after each ode, according to the season (or the general Marian Katavasia "I shall open my mouth")[^32].
  737:   * *At the 8th Ode:* Preceded by the refrain: "We praise, we bless, we worship the Lord, praising and magnifying Him unto all ages."
  738: 
```

#### Source: `Dolnytsky_Typikon_Master.md:L1097-1116`
```text
 1097: ### At Matins
 1098: 
 1099: 1. **On *"God is the Lord"*:* Troparion of the saint twice; **Glory, Both now:** Sunday Theotokion in the tone of the saint's troparion[^104].
 1100:    * *If two saints occur:* Troparion of the first saint twice; **Glory:** of the second, **Both now:** Sunday Theotokion in the tone of the second.
 1101: 2. **Kathismata:** Two current Kathismata, Small Litany, and Sessional Hymns (two Martyria and two for the departed).
 1102: 3. **Canons (3 canons on 14):**
 1103:    * *Distribution:* Canon of the Temple (if of the Lord or Theotokos) with Heirmos on 6 (Heirmoi twice, troparia on 4)[^105]; of the saint from the *Menaion* on 4; and 1st canon of the *Octoechos* (Martyria) on 4[^106][^107].
 1104:    * *If the Temple is of a saint:* Canon of the *Menaion* saint with Heirmos on 6, Temple saint on 4, and *Octoechos* Martyria on 4[^108].
 1105:    * *Katavasia:* After Odes 3, 6, 8, 9 (Heirmos of the *Octoechos* canon).
 1106:    * *After the 3rd Ode:* Sessional Hymn of the saint.
 1107:    * *After the 6th Ode:* Kontakion and Ikos of the saint.
 1108:    * *After the 9th Ode:* Exaposteilarion of the saint; **Glory:** Exaposteilarion of the *Octoechos*, **Both now:** its Theotokion.
 1109:    * *If two saints occur:* Canon of the Temple (if Lord/Theotokos) on 6, first saint on 4, second on 4. If Temple is of a saint: first saint on 6, second on 4, *Octoechos* Martyria on 4. After 3rd Ode: Kontakion-Ikos of the second saint, Sessional Hymn of the first; **Glory:** of the second, **Both now:** his Theotokion. After 6th Ode: Kontakion-Ikos of the first saint. After 9th Ode: Exaposteilarion of the first; **Glory:** of the second, **Both now:** his Theotokion.
 1110:    * *If a saint on 6 occurs:* Canon of Temple (if Lord/Theotokos) on 4, saint on 6, *Octoechos* Martyria on 4. If Temple of a saint: saint on 6, Temple on 4, *Octoechos* on 4[^109].
 1111: 4. **Doxology:** Small Doxology (a saint on 6 never has the Great Doxology on Saturday).
 1112: 5. **Aposticha:** Martyria stichera from the Praises[^110] with two weekday refrains[^111]; **Glory, Both now:** Theotokion from the Praises. (If there is a Doxastikon to the saint: Theotokion from the Praises of the *Octoechos* in the tone of the Doxastikon).
 1113: 6. **Conclusion:** Troparion of the saint; **Glory, Both now:** Daily Dismissal Theotokion in the tone of the saint's troparion and day of the week[^112].
 1114:    * *If two saints occur:* Troparion of the first; **Glory:** of the second, **Both now:** Dismissal Theotokion in the tone of the second.
 1115: 7. **Dismissal:** Great Dismissal with the commemoration of the day and of the saint (first and second).
 1116: 
```

---

### Method: `get_eothinon_exapostilarion`
- **Defined in**: [matins.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/matins.py#L2371) (`engine/resolvers/matins.py:L2371`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.5.1,L744-755`

#### Source: `Dolnytsky_Typikon_Master.md:L744-755`
```text
  744: * **Hymnography after Odes 3, 6, and 9:**
  745:   * *After the 3rd Ode:* Small Litany, followed by the **Sessional Hymn** of the Saint / Feast (on a Polyeleos or six-troparia Saint, the Sessional Hymn and Exaposteilarion are taken twice[^35], then Both now: his Theotokion; if the Saint has two Sessional Hymns, the second is taken with the refrain Glory, then Both now: his Theotokion[^36]).
  746:   * *After the 6th Ode:* Small Litany, followed by the **Kontakion and Ikos** (Resurrectional or Festal)[^37].
  747:   * *After the 9th Ode:* Small Litany. On Sundays: "Holy is the Lord our God" (3), followed by the appointed **Exaposteilarion (Hymn of Light)**[^38].
  748: 
  749: #### 6. Praises (Lauds), Great Doxology, and Dismissal
  750: 
  751: 1. **Praises (Psalms 148, 149, 150):**
  752:    * Begun with "Let everything that hath breath praise the Lord"[^39].
  753:    * 4, 6, or 8 stichera are sung with their verses.
  754:    * **Glory:** Gospel Sticheron (on Sunday) or Doxastikon of the Saint/Feast; **Both now:** "Most blessed art thou, O Virgin Theotokos."
  755: 2. **Great Doxology:**
```

---

### Method: `resolve_praises`
- **Defined in**: [matins.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/matins.py#L2382) (`engine/resolvers/matins.py:L2382`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.5.1,L744-755`

#### Source: `Dolnytsky_Typikon_Master.md:L744-755`
```text
  744: * **Hymnography after Odes 3, 6, and 9:**
  745:   * *After the 3rd Ode:* Small Litany, followed by the **Sessional Hymn** of the Saint / Feast (on a Polyeleos or six-troparia Saint, the Sessional Hymn and Exaposteilarion are taken twice[^35], then Both now: his Theotokion; if the Saint has two Sessional Hymns, the second is taken with the refrain Glory, then Both now: his Theotokion[^36]).
  746:   * *After the 6th Ode:* Small Litany, followed by the **Kontakion and Ikos** (Resurrectional or Festal)[^37].
  747:   * *After the 9th Ode:* Small Litany. On Sundays: "Holy is the Lord our God" (3), followed by the appointed **Exaposteilarion (Hymn of Light)**[^38].
  748: 
  749: #### 6. Praises (Lauds), Great Doxology, and Dismissal
  750: 
  751: 1. **Praises (Psalms 148, 149, 150):**
  752:    * Begun with "Let everything that hath breath praise the Lord"[^39].
  753:    * 4, 6, or 8 stichera are sung with their verses.
  754:    * **Glory:** Gospel Sticheron (on Sunday) or Doxastikon of the Saint/Feast; **Both now:** "Most blessed art thou, O Virgin Theotokos."
  755: 2. **Great Doxology:**
```

---

### Method: `get_eothinon_doxastikon`
- **Defined in**: [matins.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/matins.py#L2390) (`engine/resolvers/matins.py:L2390`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.5.1,L749-769`

#### Source: `Dolnytsky_Typikon_Master.md:L749-769`
```text
  749: #### 6. Praises (Lauds), Great Doxology, and Dismissal
  750: 
  751: 1. **Praises (Psalms 148, 149, 150):**
  752:    * Begun with "Let everything that hath breath praise the Lord"[^39].
  753:    * 4, 6, or 8 stichera are sung with their verses.
  754:    * **Glory:** Gospel Sticheron (on Sunday) or Doxastikon of the Saint/Feast; **Both now:** "Most blessed art thou, O Virgin Theotokos."
  755: 2. **Great Doxology:**
  756:    * The Priest opens the Holy Doors and exclaims:
  757:      > **Priest:** "Glory to Thee Who hast shown us the light!"
  758:    * The Choir sings the Great Doxology, concluding with the Holy God (Trisagion).
  759: 3. **Troparia after the Doxology:**
  760:    * *On Sundays:* The Resurrection Troparion:
  761:      * Odd tones (1, 3, 5, 7): *"Today salvation has come to the world."*
  762:      * Even tones (2, 4, 6, 8): *"Having risen from the tomb."*
  763:    * *On Feasts / Polyeleos Saints:* Troparion of the Feast or Saint; **Glory, Both now:** Theotokion / Festal troparion.
  764: 4. **Litanies and Dismissal:**
  765:    * Litany of Fervent Supplication ("Have mercy on us, O God") and Litany of Completion ("Let us complete our morning prayer").
  766:    * Sacerdotal Dismissal, as at Great Vespers without Vigil.
  767: 
  768: ---
  769: 
```

---

### Method: `resolve_doxology`
- **Defined in**: [matins.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/matins.py#L2401) (`engine/resolvers/matins.py:L2401`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L698-705,§92`
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.5.1,L755-765`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L698-705`
```text
  698: ##### 92. After the Stichera of Lauds at: Glory ..., clothed in the phelonion, he opens the royal doors; the last stichera having been completed, he exclaims:
  699: Glory to You Who have shown us the Light. All the rest follows as stated above
  700: (see § 82-83).
  701: 
  702: ##### 93. After the Dismissal, the royal doors are closed, the priest takes off the phelonion and the First Hour is read.
  703: 
  704: --- VARIANT: With Concelebrating Priests ---
  705: 
```

#### Source: `Dolnytsky_Typikon_Master.md:L755-765`
```text
  755: 2. **Great Doxology:**
  756:    * The Priest opens the Holy Doors and exclaims:
  757:      > **Priest:** "Glory to Thee Who hast shown us the light!"
  758:    * The Choir sings the Great Doxology, concluding with the Holy God (Trisagion).
  759: 3. **Troparia after the Doxology:**
  760:    * *On Sundays:* The Resurrection Troparion:
  761:      * Odd tones (1, 3, 5, 7): *"Today salvation has come to the world."*
  762:      * Even tones (2, 4, 6, 8): *"Having risen from the tomb."*
  763:    * *On Feasts / Polyeleos Saints:* Troparion of the Feast or Saint; **Glory, Both now:** Theotokion / Festal troparion.
  764: 4. **Litanies and Dismissal:**
  765:    * Litany of Fervent Supplication ("Have mercy on us, O God") and Litany of Completion ("Let us complete our morning prayer").
```

---

### Method: `resolve_dismissal`
- **Defined in**: [matins.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/matins.py#L2410) (`engine/resolvers/matins.py:L2410`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L641-645,§83-§84`
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.2.2,L515-543`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L641-645`
```text
  641: ##### 83. Then, the deacon, standing in his customary place, says the ektene: Have mercy upon us, O God ... and: Let us complete our morning prayer ... The priest blesses the faithful: Peace be with all. The choir: And with your spirit. The deacon: Bow your heads to the Lord. The choir: To You, O Lord. And the priest secretly says the prayer: Holy Lord, You live on high ... after which he exclaims: For it is You alone ... And the Dismissal is intoned with the deacon beginning: Wisdom! (see § 36).
  642: 
  643: ##### 84. After the Dismissal, the lector immediately reads the First Hour: Come, let us adore ... (three times) and the Psalms. After: Our Father ..., the priest, vested in the epitrachelion intones: For thine is
  644: 
  645: the Kingdom ... The lector: the Kontakion and: Lord, have mercy (forty times).
```

#### Source: `Dolnytsky_Typikon_Master.md:L515-543`
```text
  515: #### 3. Dismissal and Conclusion
  516: 
  517: > **Priest:** "Wisdom!"
  518: > 
  519: > **Choir:** "Bless."
  520: > 
  521: > **Priest:** "Blessed and pre-glorified Christ our God, always, now and ever, and unto ages of ages."[^16]
  522: > 
  523: > **Choir:** "Amen," *(and immediately)* "Confirm, O God, the holy Catholic faith unto ages of ages."
  524: > 
  525: > **Priest:** "O Most Holy Theotokos, save us."
  526: > 
  527: > **Choir:** "More honorable than the Cherubim..."
  528: > 
  529: > **Priest:** "Glory to Thee, O Christ God, our hope, glory to Thee." *(bowing low to the Holy Mysteries)*
  530: > 
  531: > **Choir:** "Glory, Both now. Lord, have mercy (3). Lord, bless."[^17]
  532: 
  533: *The Priest departs from the Holy Table and, standing in the Holy Doors facing the people, pronounces the dismissal, commemorating the current service.*
  534: 
  535: > **Notes:**
  536: > 1. If there are deacons, then at the end of the troparia they exit, each through his own door, to the front of the Holy Doors and, having bowed low to the Holy Mysteries, take their stand: one on the right, and the second on the left of the Holy Doors, facing one another. Then the first deacon, who is near the icon of the Savior, lifts the orarion with three fingers of his right hand toward the people and exclaims:
  537: >    > **First Deacon:** "Wisdom!"
  538: >    > **Second Deacon:** "Bless."
  539: >    > **Priest:** "Blessed and pre-glorified..."
  540: >    ...and remains there until the end of the dismissal. When the Priest pronounces the dismissal, both deacons hold their oraria raised, and at the end, having bowed all together to the Holy Mysteries, enter into the sanctuary and close the Holy Doors. If there is only one deacon, he exits through the southern door to the icon of the Savior and exclaims "Wisdom!" alone.
  541: > 2. It is not proper to sit at this Vespers either, when it is prescribed not to sit at Vespers with Vigil, up to and including the dismissal.
  542: 
  543: ---
```

---

### Method: `resolve_dismissal_troparion`
- **Defined in**: [matins.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/matins.py#L2418) (`engine/resolvers/matins.py:L2418`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.2.2,L515-543`

#### Source: `Dolnytsky_Typikon_Master.md:L515-543`
```text
  515: #### 3. Dismissal and Conclusion
  516: 
  517: > **Priest:** "Wisdom!"
  518: > 
  519: > **Choir:** "Bless."
  520: > 
  521: > **Priest:** "Blessed and pre-glorified Christ our God, always, now and ever, and unto ages of ages."[^16]
  522: > 
  523: > **Choir:** "Amen," *(and immediately)* "Confirm, O God, the holy Catholic faith unto ages of ages."
  524: > 
  525: > **Priest:** "O Most Holy Theotokos, save us."
  526: > 
  527: > **Choir:** "More honorable than the Cherubim..."
  528: > 
  529: > **Priest:** "Glory to Thee, O Christ God, our hope, glory to Thee." *(bowing low to the Holy Mysteries)*
  530: > 
  531: > **Choir:** "Glory, Both now. Lord, have mercy (3). Lord, bless."[^17]
  532: 
  533: *The Priest departs from the Holy Table and, standing in the Holy Doors facing the people, pronounces the dismissal, commemorating the current service.*
  534: 
  535: > **Notes:**
  536: > 1. If there are deacons, then at the end of the troparia they exit, each through his own door, to the front of the Holy Doors and, having bowed low to the Holy Mysteries, take their stand: one on the right, and the second on the left of the Holy Doors, facing one another. Then the first deacon, who is near the icon of the Savior, lifts the orarion with three fingers of his right hand toward the people and exclaims:
  537: >    > **First Deacon:** "Wisdom!"
  538: >    > **Second Deacon:** "Bless."
  539: >    > **Priest:** "Blessed and pre-glorified..."
  540: >    ...and remains there until the end of the dismissal. When the Priest pronounces the dismissal, both deacons hold their oraria raised, and at the end, having bowed all together to the Holy Mysteries, enter into the sanctuary and close the Holy Doors. If there is only one deacon, he exits through the southern door to the icon of the Savior and exclaims "Wisdom!" alone.
  541: > 2. It is not proper to sit at this Vespers either, when it is prescribed not to sit at Vespers with Vigil, up to and including the dismissal.
  542: 
  543: ---
```

---

### Method: `resolve_12_passion_gospels`
- **Defined in**: [matins.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/matins.py#L2427) (`engine/resolvers/matins.py:L2427`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L618-630,§79`
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:4.2.5,L8232-8300`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L618-630`
```text
  618: ##### 79. After the reading, the priest kisses the closed Gospel and takes it to the center of the church where he places it upon the tetrapod. He returns to the
  619: Altar through the royal doors.[116] If it is Sunday, the deacon reads:[117]
  620: Having beheld the resurrection of Christ ... The lector reads Psalm 50: Have mercy on me, God, in your kindness ...
  621: 
  622: Following the stichera, the deacon, in his customary place, says: Save O God,
  623: Your people ..., the choir responds with: Lord, have mercy (12 times). The priest exclaims: Through the mercies and compassions ... and the choir responds with: Amen and then begins the Canon. If there was no All-Night Vigil, the royal doors are closed.[118]
  624: 
  625: ##### 80. If there was an All-Night Vigil, then after the exclamation: Through the mercies ..., the priest, carrying the hand cross,[119] departs through the holy doors; the deacon takes the oil (which had been blessed at Vespers) and a quill,[120] and leaves via the northern door, then stands to the right of the tetrapod. There the priest anoints cruciformly the
  626: 
  627: foreheads of those who come to kiss the Gospel. The anointing having been completed, the priest and deacon return to the Altar through the royal doors and the southern door, respectively; the Royal Doors are closed and the priest takes off the phelonion.
  628: 
  629: ##### 81. After the third and sixth Odes, the deacon says the Small Synapte standing either before the royal doors or, if the anointing of the faithful is not yet completed, near the tetrapod. The priest says the ekphonesis either from the
  630: Altar, or near the tetrapod. When the Katavasia of the eighth Ode has been sung,[121] the deacon takes the thurible and, standing before the icon of the
```

#### Source: `Dolnytsky_Typikon_Master.md:L8232-8300`
```text
 8232: ### 4.2.5 Great Friday
 8233: 
 8234: ##### At Matins
 8235: 
 8236: THE SERVICE OF THE HOLY AND SAVING PASSION
 8237: 
 8238: OF OUR LORD JESUS CHRIST
 8239: 
 8240: > **Notes** 
 8241: 
 8242: 1. We sing this Matins after sunset; according to the rubric – at the 2nd hour of the night
 8243: 
 8244: 2. Before the holy doors is placed an analogion with two candlesticks, facing the people, and on it – the Gospel
 8245: 
 8246: GENERAL OVERVIEW
 8247: 
 8248: From the usual beginning to the end of the troparion after "Alleluia" and from the Canon to the end of Matins everything – according to the rubric of Matins of Great Thursday, here on [pp. 383-384](#great-thursday---matins). Between the troparion and the canon there will be five Sessional Hymns, each of which has before it three antiphons of the Passion troparia, without Kathismata and small litanies, then the Beatitudes, Prokimenon and Psalm 50. Besides this we read 12 Passion Gospels: the first – after the troparion, the five following – after each of the five Sessional Hymns, the seventh – after the Beatitudes, the eighth – after the 50th Psalm, the ninth – after the Exaposteilarion, the tenth – after the Praises, the eleventh – after "Let us complete", the twelfth – after the Aposticha. After the singing of each Gospel we ring all the church bells and, after the twelfth Gospel, we do not ring until the Resurrection itself, but instead of bells we use wooden clappers. But it is better already at Passion Matins not to ring, but to strike clappers or boards, for Passion Matins is a time of sorrow, to which the joyful sounds of bells do not correspond. Also in Rome already at Passion Matins clappers are used.
 8249: 
 8250: DETAILED RUBRIC
 8251: 
 8252: 3. From the usual beginning to the end of the litany "In peace let us pray to the Lord" everything – as at Matins daily[^585]
 8253: 
 8254: 4. **On *"God is the Lord"*:* Instead of *“God is the Lord”* we sing Alleluia in the tone of the following troparion
 8255: 
 8256: 5. **Troparia:** Troparion "When the glorious disciples" twice, Glory, Both now: once more the same
 8257: 
 8258: 6. When the troparion is sung the third time, the Priest vests in a violet phelonion, goes before the steps of the altar, bows to the Holy Mysteries and, having opened the holy doors, recites the prayer of the censer, after which, having blessed the censer: "Blessed is our God", censes around the holy table, then, having stood before the steps of the altar and bowed low, goes out through the holy doors before the iconostasis and censes the local icons, the choirs and the people and, having returned through the holy doors to the sanctuary, gives up the censer and, having again bowed low, sings the Small Litany without exclamation, then goes out through the holy doors to the analogion and exclaims: "And that we may be accounted worthy", "Peace be to all", "Wisdom, Aright" and the rest. The Choir, instead of "Glory to Thee, O Lord", sings "Glory to Thy Passion, O Lord"[^586]. Priest: "Let us attend" and reads the first Gospel. After the conclusion of the reading the Choir, instead of "Glory to Thee, O Lord", sings: "Glory to Thy long-suffering, O Lord"[^587]. The Priest, having kissed the beginning of the reading, returns to the sanctuary and, having closed the holy doors and bowed low to the Holy Mysteries, goes to the sacristy, takes off the phelonion and goes to his place
 8259: 
 8260: All this – exactly so at the readings of the other Gospels, with the exception of the litany and censing, which according to the rubric of our Triodia and the Typikon of the Lviv University, will be only at the 1st Gospel and at the five Sessional Hymns, and the censing – only of the holy table. They give thus: "We do not sit at these Sessional Hymns, since the Priest censes the holy table, but we sing them standing"[^588]. Finally we consider that it is fitting to cense not only at the Sessional Hymns, but also at all other Gospels, for the censing takes place not for the sake of the Sessional Hymns, but for the sake of the Gospels, however, only the holy table (around), as our Triodia have, which mention the censing only of the holy table. Everything should be censed only twice, that is at the 1st Gospel and at the Canon, at the heirmos of the 9th Ode.
 8261: 
 8262: According to Slavonic rubrics the Abbot or Superior should sing the first Gospel, and according to others also the twelfth. In the cathedral temple the Bishop reads them, others – the sacred ministers, according to the rank of their dignity[^589].
 8263: 
 8264: If there be deacons, they remain from the beginning of Matins, dressed in dalmatic with orarion of violet color, in the sanctuary, at their places, until they begin to sing the third time the troparion "When the glorious disciples"; then they come out together with the Priest who will sing the Gospel, dressed in a violet phelonion, before the steps of the altar and, having bowed together with him to the Holy Mysteries, open the holy doors, cense everything as usual, as at the beginning of the Liturgy, return before the steps of the altar and, having given up the censers and bowed both together to the Holy Mysteries, go out, each through his door, before the holy doors and, again having bowed to the Holy Mysteries, stand there until the second deacon after the singing of the troparion sings the Small Litany; then, having bowed to the Holy Mysteries and having exchanged their places, they proceed to the analogion so that, when the Priest approaches the analogion, the first Deacon is on the right, and the second – on the left of him. When the Priest, having bowed to the Holy Mysteries, comes out through the holy doors to the analogion, the first Deacon exclaims: "And that we may be accounted worthy". Priest: "Peace be to all". Second deacon: "Wisdom, Aright. Let us listen". Priest: "The Reading from (Name)". First deacon: "Let us attend". Priest – reading. After the conclusion of the reading, the Priest kisses the beginning of the reading first himself, afterwards the Deacon who is on the right kisses [it], and after him the one who is on the left. All three return to the sanctuary: the Priest – through the central, and the deacons – through the side doors, stand together with the Priest before the steps of the altar and, having closed the holy doors and bowed all together to the Holy Mysteries, go to their places. At the other Gospels, since there will be no Small Litany, the deacons, having come out before the holy doors, bow and, having exchanged places, proceed to the analogion and, when the Priest stands between them, exclaim: "And that we may be accounted worthy" and the rest, as above.
 8265: 
 8266: If the Bishop or other sacred ministers be present, the deacons should cense them before the choirs and neither the Priest nor the deacons kiss the Gospel before the Bishop and sacred ministers. And therefore both deacons together carry the open Gospel to the Bishop and sacred ministers to kiss, then to the Priest standing in the holy doors, and when he kisses it, then they also kiss [it] and place [it] on the analogion; then, having bowed low to the Holy Mysteries, return, each through his door, to the sanctuary.
```

---

### Method: `check_service_type`
- **Defined in**: [matins.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/matins.py#L2448) (`engine/resolvers/matins.py:L2448`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.2.1,L260-299`

#### Source: `Dolnytsky_Typikon_Master.md:L260-299`
```text
  260: ### 1.2.1 Order of Great Vespers with All-Night Vigil
  261: 
  262: #### 1. Vesting and Initial Censing
  263: 
  264: *After the candles on the main Holy Table are lit and two censers prepared, if two deacons are to serve (if not, then one), the Priest, having blessed the epitrachelion with his hand arranged as for the blessing at Liturgy and having kissed the cross upon it, puts it on himself[^6]. The deacons take upon themselves the sticharion with the orarion, having kissed it beforehand. All three come out, one after another—first the second deacon, after him the first, and last the Priest—from the sacristy to the front of the steps of the Holy Table. Having taken their stand: the first deacon on the left, and the second on the right of the Priest, with the Priest between them, all three bow low to the Holy Mysteries and, having turned all together to the Holy Doors (the Priest and second deacon to the right, and the first deacon to the left), they open them and, having turned toward the Holy Table, likewise by a half-turn, the deacons take the censers, and the Priest, with his right hand, takes the spoon and puts incense first into the censer of the first, and then into the censer of the second deacon. And after the deacons say:*
  265: 
  266: > **Deacons:** "Bless, Master, the censer."
  267: 
  268: *...the Priest blesses both censers in the form of a cross, each separately, and they all recite together the prayer "Incense we offer to Thee," which is given in the *Sluzhebnik* at the end of the Proskomedia. At other censings, instead of this prayer, only the following is said:*
  269: 
  270: > **Priest:** "Blessed is our God always, now and ever, and unto ages of ages."
  271: 
  272: *In churches that are Cathedral Eparchial or Monastic, the second Deacon exclaims to the Priest who stands at that same place:*
  273: 
  274: > **Second Deacon:** "Command!"[^7]
  275: 
  276: *At this time, all rise; the deacons cense, always with three swings of the censer, first the Holy Table from the four sides—namely first from the front both together, bowing low to the Holy Mysteries while doing so; then the first deacon goes to the right side, and the second to the left, each censing his own side of the Holy Table, and also from behind (and, if it exists, the icon behind the Holy Table) both together, and they cense the Priest from the front corners of the Holy Table both together, and come out, each through his own door, to the front of the Holy Doors and, having bowed low to the Holy Mysteries, they turn to the local icons of the iconostasis, each censing the icon on his own side. Also, they go around the temple with smoking censers, each on his own side, censing while doing so the icons of the side altars, if such exist. After this, having returned from the great church doors through the middle of the temple to the front of the Holy Doors and having bowed low to the Holy Mysteries, they turn—the Deacon who is on the right to the left, and the Deacon who is on the left to the right—toward the west, and each censes the kliros on his own side (if the church is a cathedral, also the choirs) and, at the end, both together cense the people.*
  277: 
  278: > **Rubrics on Censing and Bowing:**
  279: > 1. **If the Bishop is present:** In this case, it is proper for the deacons to approach his throne and cense him both together, and after this, having withdrawn to the middle, to cense the kliroi, etc.
  280: > 2. **Bowing rules:** It is proper for the deacons and the Priest, upon the conclusion of the censing of each icon, the Bishop, the kliros, the Choir, and the people, to bow to them; but while censing the Holy Table, to bow only from the front.
  281: 
  282: *After censing the people, the deacons turn to the Holy Doors and the first exclaims:*
  283: 
  284: > **First Deacon:** "Lord, bless."[^8]
  285: 
  286: *After this, both deacons, having bowed low to the Holy Mysteries, return, each through his own door, to the sanctuary.*
  287: 
  288: *If there is only one deacon, he alone censes around the Holy Table and, having exited through the northern door, censes the icons of the local tier on the right side, likewise on the left; having gone around the temple from the right side to the left and having bowed from the Holy Doors to the Holy Mysteries, he censes everything else according to the rubric, and returns to the sanctuary through the southern door.*
  289: 
  290: *If there is no deacon at all, then the Priest censes alone and exclaims:*
  291: 
  292: > **Priest:** "Lord, bless."
  293: 
  294: *Having censed the Holy Table, He exits the sanctuary into the temple through the Holy Doors and, after censing the iconostasis, goes around the temple as prescribed when one deacon serves; upon the conclusion of the censing, he exclaims before the Holy Doors:*
```

---

### Method: `resolve_psalm_50_intercession`
- **Defined in**: [matins.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/matins.py#L2485) (`engine/resolvers/matins.py:L2485`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.5.1,L711-716,4.1.9,L7574-7615`

#### Source: `Dolnytsky_Typikon_Master.md:L711-716`
```text
  711: 4. **Veneration of the Gospel & Psalm 50:** The Gospel is carried to the tetrapod for veneration while Psalm 50 and the post-Gospel stichera are sung.
  712: 5. **Anointing (at Vigil):** The Priest exits with the hand cross and the vessel of blessed oil[^29], anointing the faithful on the forehead:
  713:    > **Priest:** "Christ is in our midst."
  714:    > **Response:** "He is and shall be."
  715:    *(In the Paschal season: "Christ is risen!" — "Truly He is risen!").*
  716: 
```

#### Source: `Dolnytsky_Typikon_Master.md:L7574-7615`
```text
 7574: ### 4.1.9 First Saturday of Great Lent
 7575: 
 7576: Memory of the Holy Great Martyr Theodore the Tyro[^537]
 7577: 
 7578: #### On Friday Evening
 7579: 
 7580: ##### At Vespers
 7581: 
 7582: WITH PRESANCTIFIED: Everything according to the general rubric, here on page 349.
 7583: 
 7584: ##### At Compline
 7585: 
 7586: Note
 7587: 
 7588: Compline on all Fridays of Great Lent, according to the Greek rubric, is Small, and according to the Pochaiv *Triodion*, *Tserkovne Oko* and the Moscow Typikon – Great. However, in our times, when abbreviations prevail, we should adhere to the Greek rubric, the more so because even in our Horologia, in the order of Great Compline, troparia are given only for 4 days of the week, that is for Monday, Tuesday, Wednesday and Thursday. We do not make prostrations, as was already said on page 349.
 7589: 
 7590: 1. If it be Small Compline, then after *“It is truly meet”* we recite the Kontakion of the Great Martyr; if Great, then after the 1st Trisagion – Troparion of the Great Martyr, Glory, Both now: Theotokion (Sunday, in the tone of the Troparion of the Saint)[^538]; after the 2nd Trisagion – usual troparia "Have mercy on us, O Lord"; after *“It is truly meet”* – Kontakion of the Great Martyr, and the Troparion "O Lord of Hosts" we do not recite[^539]
 7591: 
 7592: ##### At Compline
 7593: 
 7594: we sing the Canon for the Dead, which is in the *Octoechos* for the current tone, and the Canons of the *Menaion* to the saints of the nearest Saturday and Sunday we sing, if the Ecclesiarch prefers, one – at Compline on Friday with the Canon for the Dead, and the other – on Sunday at Compline[^540]. The Greek *Triodion* adds: "we do so on all Friday evenings of holy and Great Lent". Before the Canon for the Dead we should sing also the usual Theotokion Canon of the *Octoechos*, for the rubric does not exclude it[^541]
 7595: 
 7596: ##### At Matins
 7597: 
 7598: 1. From the beginning to the canon everything – according to the general rubric for a saint without Polyeleos on Saturday, except the 2nd Sessional Hymn, which will not be of the *Octoechos*, but of the *Triodion* of St. Theodore
 7599: 
 7600: 2. **Canons:** Canons 3 on 14: Temple with heirmos on 6 and two of Theodore on 8. Katavasia after each ode – "I shall open"
 7601: 
 7602: After the 3rd Ode – Sessional Hymn of the Saint, after the 6th – Kontakion and Ikos of the Saint, after the 9th – Exaposteilarion of the Saint.
 7603: 
 7604: 3. **Praises (Lauds):** Stichera of the Praises to the Saint on 4, Doxastikon – to him, and Theotokion – in the *Triodion*
 7605: 
 7606: 4. **After the Great Doxology:** Small Doxology and, after "Let us complete", – Aposticha of the Saint with his two verses and the subsequent order of Matins according to the rubric for a saint without Polyeleos on Saturday
 7607: 
 7608: ##### At the Hours
```

---

### Method: `resolve_artoklasia`
- **Defined in**: [vespers.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/vespers.py#L588) (`engine/resolvers/vespers.py:L588`)
- **Citations**:
  - `ordo`: `Ordo_Celebrationis_1996_CLEAN.md:L491-505,§63`

#### Source: `Ordo_Celebrationis_1996_CLEAN.md:L491-505`
```text
  491: ##### 63. After the exclamation: May the might of Your kingdom ... the priest with the hand cross and the deacons with their thuribles,[101] depart via the northern door; or, where the royal doors are customarily open, the priest departs through the royal doors and the deacons via their own doors. Preceded by the choirs and candlebearers, they proceed to the narthex or, if there be none, to the main doors of the church. Their thuribles having been blessed, the deacons cense, each from his own side, the holy icons (if there be any in the narthex),[102] the priest, the choir and the people present.
  492: 
  493: Upon completion of the Stichera for the Litany the deacons alternately say the petitions:
  494: 
  495: First deacon: O God, save Your people... Second deacon: Again we pray for His
  496: Holiness...[103] First deacon: Again we pray [for the hierarchy]... Priest: Hear us, O God... Peace be with all! Second deacon: Let us bow our heads before the
  497: Lord...
  498: 
  499: After the ekphonesis, they return into the church proper.
  500: 
  501: ##### 64. While the Apolytikion is sung, the deacons cense the tetrapod from its four sides thus: first, both deacons together from the front, then the first deacon proceeds to the right side, the second to the left, and each censes his own side, then both proceed behind the tetrapod where they cense together; finally, they cense only the Superior and then the priest.[104]
  502: 
  503: ##### 65. At the blessing of the loaves, the first deacon exclaims: Let us pray to the
  504: Lord.
  505: 
```

---

### Method: `resolve_passion_vespers_readings`
- **Defined in**: [vespers.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/vespers.py#L1770) (`engine/resolvers/vespers.py:L1770`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:4.1.1,L6961-7018`

#### Source: `Dolnytsky_Typikon_Master.md:L6961-7018`
```text
 6961: ### 4.1.1 Sunday of the Publican and Pharisee
 6962: 
 6963: > **Note:** The service of a saint which falls on this Sunday, or on the Sundays of the Prodigal Son, Meatfare, and Cheesefare, we sing on the preceding Friday at Compline, or as the Ecclesiarch decides.
 6964: 
 6965: ##### At Great Vespers
 6966: 
 6967: 1. *“Blessed is the man”*, as usual.
 6968: 
 6969: 1. **On *"Lord, I have cried"*:* 10 stichera: 7 of the *Octoechos* and 3 of the *Triodion*, that is, the two given at *“Lord, I have cried”* and the one from the Doxastikon of the Litiya; Glory: *Triodion*, Both now: 1st Theotokion of the current tone (Dogmatikon)
 6970: 
 6971: 2. **Aposticha:** Aposticha of the Sunday *Octoechos*, Glory: *Triodion*, Both now: Theotokion of the Sunday Aposticha according to the tone of the Doxastikon
 6972: 
 6973: 3. At the end: Sunday Troparion, Glory, Both now: Sunday Theotokion according to its tone
 6974: 
 6975: ##### At Compline
 6976: 
 6977: After *“It is truly meet”* – Kontakion of the *Triodion* only.
 6978: 
 6979: Midnight Office – Sunday.
 6980: 
 6981: ##### At Great Matins
 6982: 
 6983: 1. **On *"God is the Lord"*:* Sunday Troparion twice, Glory, Both now: Sunday Theotokion according to its tone
 6984: 
 6985: 2. Everything else up to the canon is of the Sunday, as usual, only after the 50th Psalm, instead of Glory: "Through the prayers of the holy apostles" and the rest, at all odes of the Sundays of the *Triodion* we sing: Glory: *“Open to me the doors”*, Both now: *“Lead me on the paths of salvation”*, and after the verse "Have mercy on me, O God", the sticheron: *“Thinking upon the multitude”*
 6986: 
 6987: 3. **Canons:** *Distribution:* Canons 4 on 14: *Octoechos* Sunday with heirmos on 4, Cross-Resurrection on 2, Theotokos on 2, and *Triodion* on 6. 
 6988:    * *Katavasia:* Katavasia: The sequential "I shall open". 
 6989:    * *After the 3rd Ode:* Sessional Hymn of the *Triodion*; 
 6990:    * *After the 6th Ode:* Kontakion and Ikos of the *Triodion*; 
 6991:    * *After the 9th Ode:* "Holy is the Lord our God" and the Sunday Exaposteilarion, Glory: *Triodion*, Both now: Its Theotokion
 6992: 
 6993: 4. **Praises (Lauds):** 8: 4 of the *Octoechos* and 4 of the *Triodion* with two Sunday verses, Glory: *Triodion*, Both now: *“Most Blessed Art Thou”*
 6994: 
 6995: 5. Everything else to the end of Matins – as usual
```

---

### Method: `resolve_daily_kathisma`
- **Defined in**: [vespers.py](file:///C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/Typikon Coded/engine/resolvers/vespers.py#L1828) (`engine/resolvers/vespers.py:L1828`)
- **Citations**:
  - `dolnytsky`: `Dolnytsky_Typikon_Master.md:1.2.1,L300-339`

#### Source: `Dolnytsky_Typikon_Master.md:L300-339`
```text
  300: #### 2. From "Glory to the Holy" to the Entrance
  301: 
  302: *When the deacons, having put away the censers, take their stand, each on his own side, near the Priest in front of the steps, the Priest sings in a loud voice:*
  303: 
  304: > **Priest:** "Glory to the Holy, Consubstantial, and Life-Creating Trinity, always, now and ever, and unto ages of ages."[^10]
  305: 
  306: *After "Amen," the Choir sings immediately: "Come, let us worship" three times, and all three sacred ministers close the Holy Doors, and the candles on the Holy Table are extinguished.*
  307: 
  308: *During the singing of the Prefatory Psalm (Psalm 103), lit candles are handed to the deacons, and each of them exits through his own door to the front of the Holy Doors, and behind them the Priest also, having exited through the northern door, stands between them before the Holy Doors and, having bowed together with the deacons to the Holy Mysteries, reads quietly the Prayers of Vespers, while the deacons provide light for him.*
  309: 
  310: *After the Prefatory Psalm and "Alleluia," the first deacon sings the Litany of Peace:*
  311: 
  312: > **Deacon:** "In peace let us pray to the Lord."
  313: 
  314: *The Priest continues to read the Prayers of Vespers at that same place, and at the end of the litany exclaims:*
  315: 
  316: > **Priest:** "For to Thee belongs..."
  317: 
  318: *Afterward, all three, having bowed together, exit the sanctuary: the first deacon, and after him the Priest, through the southern door, and the second through the northern, and they sit there behind the Holy Table: the Priest in the middle, the first deacon to the right, and the second to the left of him.*
  319: 
  320: *After the first Kathisma, that is, after "Blessed is the man," the second deacon, having come out to the front of the Holy Doors, sings the Small Litany:*
  321: 
  322: > **Deacon:** "Again and again in peace let us pray to the Lord..."
  323: 
  324: *...and the Priest, having risen, exclaims from his place:*
  325: 
  326: > **Priest:** "For Thine is the dominion..."
  327: 
  328: *If there is no deacon, then this litany, according to local custom, is said by the Priest quietly, and the Choir responds to its petitions aloud.*
  329: 
  330: *After the litany, *“Lord, I have cried”* is sung according to the tone of the first sticheron. During the singing, the deacons turn to the Priest:*
  331: 
  332: > **Deacons:** "Bless, Master, the censer."
  333: 
  334: *...and the Priest blesses the censer with the words:*
```

---

## 📂 JSON Database Structure Mappings

This section catalogs how individual service slots in the JSON databases map to the canonical texts.

### Database File: `json_db/00_components.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `components.artoklasia.source_ref` | `Dolnytsky_Typikon_Master.md:1.2` | **Dolnytsky_Typikon_Master.md:1.2 (L258-259)**:<br>L258: ## 1.2 Vespers |
| `components.doxology_great_sung.source_ref` | `Dolnytsky_Typikon_Master.md:1.2` | **Dolnytsky_Typikon_Master.md:1.2 (L258-259)**:<br>L258: ## 1.2 Vespers |
| `components.doxology_small_read.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `components.entrance_great.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.1.1` | **Dolnytsky_Typikon_Master.md:1.2.1.1 (L262-292)**:<br>L262: #### 1. Vesting and Initial Censing |
| `components.exaltation_of_cross_stations.source_ref` | `Dolnytsky_Typikon_Master.md:3.1.4` | **Dolnytsky_Typikon_Master.md:3.1.4 (L2066-2096)**:<br>L2066: ### 3.1.4 September: Universal Exaltation of the Precious Cross |
| `components.kneeling_prayers_pentecost.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.23.1` | **Dolnytsky_Typikon_Master.md:4.2.23.1 (L9154-9184)**:<br>L9154: ### 4.2.23 Feast of the Most Holy Eucharist |
| `components.litiya_procession.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.1.9` | **Dolnytsky_Typikon_Master.md:1.2.1.9 (L460-481)**:<br>L460: #### 9. Conclusion of Vespers |
| `components.matins_gospel_rite.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.4` | **Dolnytsky_Typikon_Master.md:1.2.2.4 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `components.polyeleos.source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.6` | **Dolnytsky_Typikon_Master.md:1.5.1.6 (L749-769)**:<br>L749: #### 6. Praises (Lauds), Great Doxology, and Dismissal |
| `components.shroud_procession_and_burial.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.1.3` | **Dolnytsky_Typikon_Master.md:4.1.1.3 (L6961-6991)**:<br>L6961: ### 4.1.1 Sunday of the Publican and Pharisee |
| `components.tomb_encomia_stations.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.21.3` | **Dolnytsky_Typikon_Master.md:4.2.21.3 (L9094-9124)**:<br>L9094: ### 4.2.21 Sunday of All Saints |

---

### Database File: `json_db/01a_struct_hour_1.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.structure_lenten.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `structures.structure_paschal.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.20.2` | **Dolnytsky_Typikon_Master.md:4.2.20.2 (L9030-9060)**:<br>L9030: ### 4.2.20 Monday of the Holy Spirit |
| `structures.structure_royal.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.6.2, Dolnytsky_Typikon_Master.md:4.2.18.4` | **Dolnytsky_Typikon_Master.md:3.4.6.2 (L2759-2788)**:<br>L2759: ### 3.4.6 -24 December: Forefeast of the Nativity of Christ<br>**Dolnytsky_Typikon_Master.md:4.2.18.4 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |

---

### Database File: `json_db/01b_struct_hour_3.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.structure_lenten.overrides[2].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.12` | **Dolnytsky_Typikon_Master.md:4.1.12 (L7676-7706)**:<br>L7676: ### 4.1.12 Saturday of the Second Week of Great Lent |
| `structures.structure_lenten.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `structures.structure_paschal.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.20.2` | **Dolnytsky_Typikon_Master.md:4.2.20.2 (L9030-9060)**:<br>L9030: ### 4.2.20 Monday of the Holy Spirit |
| `structures.structure_royal.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.6.2, Dolnytsky_Typikon_Master.md:4.2.18.4` | **Dolnytsky_Typikon_Master.md:3.4.6.2 (L2759-2788)**:<br>L2759: ### 3.4.6 -24 December: Forefeast of the Nativity of Christ<br>**Dolnytsky_Typikon_Master.md:4.2.18.4 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.structure_standard.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |

---

### Database File: `json_db/01c_struct_hour_6.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.structure_lenten.overrides[2].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.12` | **Dolnytsky_Typikon_Master.md:4.1.12 (L7676-7706)**:<br>L7676: ### 4.1.12 Saturday of the Second Week of Great Lent |
| `structures.structure_lenten.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `structures.structure_paschal.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.20.2` | **Dolnytsky_Typikon_Master.md:4.2.20.2 (L9030-9060)**:<br>L9030: ### 4.2.20 Monday of the Holy Spirit |
| `structures.structure_royal.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.6.2, Dolnytsky_Typikon_Master.md:4.2.18.4` | **Dolnytsky_Typikon_Master.md:3.4.6.2 (L2759-2788)**:<br>L2759: ### 3.4.6 -24 December: Forefeast of the Nativity of Christ<br>**Dolnytsky_Typikon_Master.md:4.2.18.4 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.structure_standard.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |

---

### Database File: `json_db/01d_struct_hour_9.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.structure_lenten.overrides[2].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.12` | **Dolnytsky_Typikon_Master.md:4.1.12 (L7676-7706)**:<br>L7676: ### 4.1.12 Saturday of the Second Week of Great Lent |
| `structures.structure_lenten.overrides[4].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.12` | **Dolnytsky_Typikon_Master.md:4.1.12 (L7676-7706)**:<br>L7676: ### 4.1.12 Saturday of the Second Week of Great Lent |
| `structures.structure_lenten.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `structures.structure_paschal.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.20.2` | **Dolnytsky_Typikon_Master.md:4.2.20.2 (L9030-9060)**:<br>L9030: ### 4.2.20 Monday of the Holy Spirit |
| `structures.structure_royal.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.6.2, Dolnytsky_Typikon_Master.md:4.2.18.4` | **Dolnytsky_Typikon_Master.md:3.4.6.2 (L2759-2788)**:<br>L2759: ### 3.4.6 -24 December: Forefeast of the Nativity of Christ<br>**Dolnytsky_Typikon_Master.md:4.2.18.4 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.structure_standard.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |

---

### Database File: `json_db/01e_struct_typika.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.structure_lenten.sequence[0].source_ref` | `Dolnytsky_Typikon_Master.md:4.1.12.1` | **Dolnytsky_Typikon_Master.md:4.1.12.1 (L7676-7706)**:<br>L7676: ### 4.1.12 Saturday of the Second Week of Great Lent |
| `structures.structure_lenten.sequence[3].source_ref` | `Dolnytsky_Typikon_Master.md:4.1.13.1.2` | **Dolnytsky_Typikon_Master.md:4.1.13.1.2 (L7735-7765)**:<br>L7735: ### 4.1.13 Second Sunday of Great Lent |
| `structures.structure_lenten.sequence[5].source_ref` | `Dolnytsky_Typikon_Master.md:4.1.13.1.3` | **Dolnytsky_Typikon_Master.md:4.1.13.1.3 (L7735-7765)**:<br>L7735: ### 4.1.13 Second Sunday of Great Lent |
| `structures.structure_lenten.sequence[6].source_ref` | `Dolnytsky_Typikon_Master.md:4.1.13.1.4` | **Dolnytsky_Typikon_Master.md:4.1.13.1.4 (L7735-7765)**:<br>L7735: ### 4.1.13 Second Sunday of Great Lent |
| `structures.structure_lenten.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.7.3` | **Dolnytsky_Typikon_Master.md:4.1.7.3 (L7354-7384)**:<br>L7354: ### 4.1.7 Beginning of Great Lent |
| `structures.structure_standard.sequence[1].source_ref` | `Dolnytsky_Typikon_Master.md:3.4.7.1.2` | **Dolnytsky_Typikon_Master.md:3.4.7.1.2 (L2789-2819)**:<br>L2789: ### 3.4.7 December: Eve of the Nativity of Christ |
| `structures.structure_standard.sequence[2].source_ref` | `Dolnytsky_Typikon_Master.md:3.4.7.1.2` | **Dolnytsky_Typikon_Master.md:3.4.7.1.2 (L2789-2819)**:<br>L2789: ### 3.4.7 December: Eve of the Nativity of Christ |
| `structures.structure_standard.sequence[4].source_ref` | `Dolnytsky_Typikon_Master.md:3.4.7.1.3` | **Dolnytsky_Typikon_Master.md:3.4.7.1.3 (L2789-2819)**:<br>L2789: ### 3.4.7 December: Eve of the Nativity of Christ |
| `structures.structure_standard.sequence[6].source_ref` | `Dolnytsky_Typikon_Master.md:3.4.7.1.3` | **Dolnytsky_Typikon_Master.md:3.4.7.1.3 (L2789-2819)**:<br>L2789: ### 3.4.7 December: Eve of the Nativity of Christ |
| `structures.structure_standard.sequence[7].source_ref` | `Dolnytsky_Typikon_Master.md:3.4.7.1.3` | **Dolnytsky_Typikon_Master.md:3.4.7.1.3 (L2789-2819)**:<br>L2789: ### 3.4.7 December: Eve of the Nativity of Christ |
| `structures.structure_standard.sequence[9].source_ref` | `Dolnytsky_Typikon_Master.md:3.4.7.1.4` | **Dolnytsky_Typikon_Master.md:3.4.7.1.4 (L2789-2819)**:<br>L2789: ### 3.4.7 December: Eve of the Nativity of Christ |
| `structures.structure_standard.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.7.1.1` | **Dolnytsky_Typikon_Master.md:3.4.7.1.1 (L2789-2819)**:<br>L2789: ### 3.4.7 December: Eve of the Nativity of Christ |

---

### Database File: `json_db/01f_struct_compline.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.great_compline_lenten.sequence[3].source_ref` | `Dolnytsky_Typikon_Master.md:4.1.8.5` | **Dolnytsky_Typikon_Master.md:4.1.8.5 (L7540-7570)**:<br>L7540: ### 4.1.8 Vespers on Wednesday and Friday with Presanctified |
| `structures.great_compline_lenten.source_ref` | `Dolnytsky_Typikon_Master.md:1.3.2` | **Dolnytsky_Typikon_Master.md:1.3.2 (L622-635)**:<br>L622: ### 1.3.2 Order of Great Compline without Vigil |
| `structures.great_compline_vigil.source_ref` | `Dolnytsky_Typikon_Master.md:1.3.3` | **Dolnytsky_Typikon_Master.md:1.3.3 (L636-645)**:<br>L636: ### 1.3.3 Order of Great Compline with All-Night Vigil |
| `structures.small_compline.source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1` | **Dolnytsky_Typikon_Master.md:1.5.1 (L666-667)**:<br>L666: ### 1.5.1 Order of Great Matins (With Vigil and Without Vigil) |
| `structures.structure_paschal.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.20.2` | **Dolnytsky_Typikon_Master.md:4.2.20.2 (L9030-9060)**:<br>L9030: ### 4.2.20 Monday of the Holy Spirit |

---

### Database File: `json_db/01g_struct_midnight.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.midnight_daily.source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.3` | **Dolnytsky_Typikon_Master.md:1.5.1.3 (L694-702)**:<br>L694: #### 3. From the Kathismata to the Graduals (Polyeleos Rubrics) |
| `structures.midnight_holy_saturday.sequence[3].source_ref` | `Dolnytsky_Typikon_Master.md:4.2.24` | **Dolnytsky_Typikon_Master.md:4.2.24 (L9200-9225)**:<br>L9200: ### 4.2.24 Feast of the Co-suffering of the Most Holy Theotokos |
| `structures.midnight_holy_saturday.sequence[4].source_ref` | `Dolnytsky_Typikon_Master.md:4.2.24` | **Dolnytsky_Typikon_Master.md:4.2.24 (L9200-9225)**:<br>L9200: ### 4.2.24 Feast of the Co-suffering of the Most Holy Theotokos |
| `structures.midnight_holy_saturday.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.23.1` | **Dolnytsky_Typikon_Master.md:4.2.23.1 (L9154-9184)**:<br>L9154: ### 4.2.23 Feast of the Most Holy Eucharist |
| `structures.midnight_saturday.source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.3` | **Dolnytsky_Typikon_Master.md:1.5.1.3 (L694-702)**:<br>L694: #### 3. From the Kathismata to the Graduals (Polyeleos Rubrics) |
| `structures.midnight_sunday.source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.3` | **Dolnytsky_Typikon_Master.md:1.5.1.3 (L694-702)**:<br>L694: #### 3. From the Kathismata to the Graduals (Polyeleos Rubrics) |
| `structures.midnight_weekday.source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.3` | **Dolnytsky_Typikon_Master.md:1.5.1.3 (L694-702)**:<br>L694: #### 3. From the Kathismata to the Graduals (Polyeleos Rubrics) |

---

### Database File: `json_db/01h_struct_vespers.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.daily_vespers_memorial.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.3` | **Dolnytsky_Typikon_Master.md:4.1.3 (L7025-7055)**:<br>L7025: ### 4.1.3 Meatfare, or Soul Saturday |
| `structures.great_vespers_polyeleos.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.2` | **Dolnytsky_Typikon_Master.md:1.2.2.2 (L502-514)**:<br>L502: #### 2. Main Order of Service |
| `structures.great_vespers_simple.overrides[0].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.1` | **Dolnytsky_Typikon_Master.md:1.2.2.1 (L484-501)**:<br>L484: #### 1. Beginning and Introductory Prayers |
| `structures.great_vespers_vigil.sequence[0].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.1.1` | **Dolnytsky_Typikon_Master.md:1.2.1.1 (L262-292)**:<br>L262: #### 1. Vesting and Initial Censing |
| `structures.great_vespers_vigil.sequence[2].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.1.3` | **Dolnytsky_Typikon_Master.md:1.2.1.3 (L340-369)**:<br>L340: #### 3. Entrance and Censing at *“Gladsome Light”* |
| `structures.great_vespers_vigil.sequence[4].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.1.3` | **Dolnytsky_Typikon_Master.md:1.2.1.3 (L340-369)**:<br>L340: #### 3. Entrance and Censing at *“Gladsome Light”* |
| `structures.great_vespers_vigil.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.1.1` | **Dolnytsky_Typikon_Master.md:1.2.1.1 (L262-292)**:<br>L262: #### 1. Vesting and Initial Censing |
| `structures.kneeling_vespers.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.23.1` | **Dolnytsky_Typikon_Master.md:4.2.23.1 (L9154-9184)**:<br>L9154: ### 4.2.23 Feast of the Most Holy Eucharist |
| `structures.lenten_vespers.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.14` | **Dolnytsky_Typikon_Master.md:4.1.14 (L7769-7799)**:<br>L7769: ### 4.1.14 Third Week of Great Lent |
| `structures.lenten_vespers_presanctified.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.7.3` | **Dolnytsky_Typikon_Master.md:4.1.7.3 (L7354-7384)**:<br>L7354: ### 4.1.7 Beginning of Great Lent |
| `structures.paschal_vespers.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18.4` | **Dolnytsky_Typikon_Master.md:4.2.18.4 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_burial_vespers.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.1.3` | **Dolnytsky_Typikon_Master.md:4.1.1.3 (L6961-6991)**:<br>L6961: ### 4.1.1 Sunday of the Publican and Pharisee |
| `structures.presanctified_vespers.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.14.3.3` | **Dolnytsky_Typikon_Master.md:4.1.14.3.3 (L7769-7799)**:<br>L7769: ### 4.1.14 Third Week of Great Lent |

---

### Database File: `json_db/01i_struct_matins.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.bridegroom_matins.overrides[0].new_component.content.components[1].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.13.3` | **Dolnytsky_Typikon_Master.md:4.2.13.3 (L8706-8736)**:<br>L8706: ### 4.2.13 Sunday of the Paralytic |
| `structures.bridegroom_matins.overrides[0].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.13.3` | **Dolnytsky_Typikon_Master.md:4.2.13.3 (L8706-8736)**:<br>L8706: ### 4.2.13 Sunday of the Paralytic |
| `structures.bridegroom_matins.overrides[1].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.13.3` | **Dolnytsky_Typikon_Master.md:4.2.13.3 (L8706-8736)**:<br>L8706: ### 4.2.13 Sunday of the Paralytic |
| `structures.bridegroom_matins.overrides[2].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.13.3` | **Dolnytsky_Typikon_Master.md:4.2.13.3 (L8706-8736)**:<br>L8706: ### 4.2.13 Sunday of the Paralytic |
| `structures.bridegroom_matins.overrides[3].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.13.3` | **Dolnytsky_Typikon_Master.md:4.2.13.3 (L8706-8736)**:<br>L8706: ### 4.2.13 Sunday of the Paralytic |
| `structures.bridegroom_matins.overrides[4].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.13.3` | **Dolnytsky_Typikon_Master.md:4.2.13.3 (L8706-8736)**:<br>L8706: ### 4.2.13 Sunday of the Paralytic |
| `structures.bridegroom_matins.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.13.3` | **Dolnytsky_Typikon_Master.md:4.2.13.3 (L8706-8736)**:<br>L8706: ### 4.2.13 Sunday of the Paralytic |
| `structures.bright_matins.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.24` | **Dolnytsky_Typikon_Master.md:4.2.24 (L9200-9225)**:<br>L9200: ### 4.2.24 Feast of the Co-suffering of the Most Holy Theotokos |
| `structures.daily_matins.sequence[14].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `structures.daily_matins.sequence[15].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `structures.daily_matins.sequence[17].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `structures.daily_matins.sequence[3].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `structures.daily_matins.sequence[5].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `structures.daily_matins.sequence[7].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `structures.daily_matins.sequence[8].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `structures.daily_matins.sequence[9].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `structures.daily_matins.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `structures.great_matins.sequence[0].content.false_content.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.5` | **Dolnytsky_Typikon_Master.md:1.5.1.5 (L717-747)**:<br>L717: #### 5. Order of the Matins Canon |
| `structures.great_matins.sequence[0].content.true_content.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.5` | **Dolnytsky_Typikon_Master.md:1.5.1.5 (L717-747)**:<br>L717: #### 5. Order of the Matins Canon |
| `structures.great_matins.sequence[3].content.components[1].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2` | **Dolnytsky_Typikon_Master.md:1.2 (L258-259)**:<br>L258: ## 1.2 Vespers |
| `structures.great_matins.sequence[3].content.components[4].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2` | **Dolnytsky_Typikon_Master.md:1.2 (L258-259)**:<br>L258: ## 1.2 Vespers |
| `structures.great_matins.sequence[4].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.6` | **Dolnytsky_Typikon_Master.md:1.5.1.6 (L749-769)**:<br>L749: #### 6. Praises (Lauds), Great Doxology, and Dismissal |
| `structures.great_matins.sequence[5].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.4` | **Dolnytsky_Typikon_Master.md:1.2.2.4 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `structures.great_matins.sequence[7].content.components[14].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.1` | **Dolnytsky_Typikon_Master.md:1.2.2.1 (L484-501)**:<br>L484: #### 1. Beginning and Introductory Prayers |
| `structures.great_matins.sequence[7].content.components[16].components[0].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.6` | **Dolnytsky_Typikon_Master.md:1.5.1.6 (L749-769)**:<br>L749: #### 6. Praises (Lauds), Great Doxology, and Dismissal |
| `structures.great_matins.sequence[9].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:1.5.2` | **Dolnytsky_Typikon_Master.md:1.5.2 (L770-794)**:<br>L770: ### 1.5.2 Rubric for Deacons at Matins |
| `structures.great_matins.source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.5` | **Dolnytsky_Typikon_Master.md:1.5.1.5 (L717-747)**:<br>L717: #### 5. Order of the Matins Canon |
| `structures.lenten_matins_weekday.overrides[0].new_component.content.components[1].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.9.1.4` | **Dolnytsky_Typikon_Master.md:4.1.9.1.4 (L7574-7604)**:<br>L7574: ### 4.1.9 First Saturday of Great Lent |
| `structures.lenten_matins_weekday.overrides[0].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.9.1.4` | **Dolnytsky_Typikon_Master.md:4.1.9.1.4 (L7574-7604)**:<br>L7574: ### 4.1.9 First Saturday of Great Lent |
| `structures.lenten_matins_weekday.overrides[11].new_component.content.components[1].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.10.3.2` | **Dolnytsky_Typikon_Master.md:4.1.10.3.2 (L7616-7646)**:<br>L7616: ### 4.1.10 First Sunday of Great Lent |
| `structures.lenten_matins_weekday.overrides[11].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.10.3.2` | **Dolnytsky_Typikon_Master.md:4.1.10.3.2 (L7616-7646)**:<br>L7616: ### 4.1.10 First Sunday of Great Lent |
| `structures.lenten_matins_weekday.overrides[12].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.10.3.2` | **Dolnytsky_Typikon_Master.md:4.1.10.3.2 (L7616-7646)**:<br>L7616: ### 4.1.10 First Sunday of Great Lent |
| `structures.lenten_matins_weekday.overrides[13].new_component.content.components[1].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.9.1.6` | **Dolnytsky_Typikon_Master.md:4.1.9.1.6 (L7574-7604)**:<br>L7574: ### 4.1.9 First Saturday of Great Lent |
| `structures.lenten_matins_weekday.overrides[13].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.9.1.6` | **Dolnytsky_Typikon_Master.md:4.1.9.1.6 (L7574-7604)**:<br>L7574: ### 4.1.9 First Saturday of Great Lent |
| `structures.lenten_matins_weekday.overrides[1].new_component.content.components[1].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.9.1.6` | **Dolnytsky_Typikon_Master.md:4.1.9.1.6 (L7574-7604)**:<br>L7574: ### 4.1.9 First Saturday of Great Lent |
| `structures.lenten_matins_weekday.overrides[1].new_component.content.components[3].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.9.1.6` | **Dolnytsky_Typikon_Master.md:4.1.9.1.6 (L7574-7604)**:<br>L7574: ### 4.1.9 First Saturday of Great Lent |
| `structures.lenten_matins_weekday.overrides[1].new_component.content.components[5].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.9.1.6` | **Dolnytsky_Typikon_Master.md:4.1.9.1.6 (L7574-7604)**:<br>L7574: ### 4.1.9 First Saturday of Great Lent |
| `structures.lenten_matins_weekday.overrides[1].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.9.1.6` | **Dolnytsky_Typikon_Master.md:4.1.9.1.6 (L7574-7604)**:<br>L7574: ### 4.1.9 First Saturday of Great Lent |
| `structures.lenten_matins_weekday.overrides[2].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.10` | **Dolnytsky_Typikon_Master.md:4.1.10 (L7616-7646)**:<br>L7616: ### 4.1.10 First Sunday of Great Lent |
| `structures.lenten_matins_weekday.overrides[3].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.9.1.1` | **Dolnytsky_Typikon_Master.md:4.1.9.1.1 (L7574-7604)**:<br>L7574: ### 4.1.9 First Saturday of Great Lent |
| `structures.lenten_matins_weekday.overrides[4].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.10.3.1` | **Dolnytsky_Typikon_Master.md:4.1.10.3.1 (L7616-7646)**:<br>L7616: ### 4.1.10 First Sunday of Great Lent |
| `structures.lenten_matins_weekday.overrides[5].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.10` | **Dolnytsky_Typikon_Master.md:4.1.10 (L7616-7646)**:<br>L7616: ### 4.1.10 First Sunday of Great Lent |
| `structures.lenten_matins_weekday.overrides[6].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.11` | **Dolnytsky_Typikon_Master.md:4.1.11 (L7668-7675)**:<br>L7668: ### 4.1.11 Monday, Tuesday, Wednesday, Thursday and Friday of the Second Week of Great Lent |
| `structures.lenten_matins_weekday.overrides[7].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.10.3.2` | **Dolnytsky_Typikon_Master.md:4.1.10.3.2 (L7616-7646)**:<br>L7616: ### 4.1.10 First Sunday of Great Lent |
| `structures.lenten_matins_weekday.overrides[8].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.10.3.2` | **Dolnytsky_Typikon_Master.md:4.1.10.3.2 (L7616-7646)**:<br>L7616: ### 4.1.10 First Sunday of Great Lent |
| `structures.lenten_matins_weekday.overrides[9].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.10.3.2` | **Dolnytsky_Typikon_Master.md:4.1.10.3.2 (L7616-7646)**:<br>L7616: ### 4.1.10 First Sunday of Great Lent |
| `structures.lenten_matins_weekday.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.9.1.1` | **Dolnytsky_Typikon_Master.md:4.1.9.1.1 (L7574-7604)**:<br>L7574: ### 4.1.9 First Saturday of Great Lent |
| `structures.matins_memorial.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.3` | **Dolnytsky_Typikon_Master.md:4.1.3 (L7025-7055)**:<br>L7025: ### 4.1.3 Meatfare, or Soul Saturday |
| `structures.passion_matins.sequence[0].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.16.1` | **Dolnytsky_Typikon_Master.md:4.2.16.1 (L8890-8920)**:<br>L8890: ### 4.2.16 Sunday of the Man Born Blind |
| `structures.passion_matins.sequence[15].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18.2.4` | **Dolnytsky_Typikon_Master.md:4.2.18.2.4 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_matins.sequence[17].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.16.10` | **Dolnytsky_Typikon_Master.md:4.2.16.10 (L8890-8920)**:<br>L8890: ### 4.2.16 Sunday of the Man Born Blind |
| `structures.passion_matins.sequence[19].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18.3` | **Dolnytsky_Typikon_Master.md:4.2.18.3 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_matins.sequence[1].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18` | **Dolnytsky_Typikon_Master.md:4.2.18 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_matins.sequence[20].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18.3` | **Dolnytsky_Typikon_Master.md:4.2.18.3 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_matins.sequence[22].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18.4.1` | **Dolnytsky_Typikon_Master.md:4.2.18.4.1 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_matins.sequence[24].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18.4.2` | **Dolnytsky_Typikon_Master.md:4.2.18.4.2 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_matins.sequence[25].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18.4.2` | **Dolnytsky_Typikon_Master.md:4.2.18.4.2 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_matins.sequence[26].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18.4.2` | **Dolnytsky_Typikon_Master.md:4.2.18.4.2 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_matins.sequence[28].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18.4.4` | **Dolnytsky_Typikon_Master.md:4.2.18.4.4 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_matins.sequence[2].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18.1.1` | **Dolnytsky_Typikon_Master.md:4.2.18.1.1 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_matins.sequence[30].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18.4.5` | **Dolnytsky_Typikon_Master.md:4.2.18.4.5 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_matins.sequence[32].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18.4.5` | **Dolnytsky_Typikon_Master.md:4.2.18.4.5 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_matins.sequence[34].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18.4.5` | **Dolnytsky_Typikon_Master.md:4.2.18.4.5 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_matins.sequence[3].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18.1.3` | **Dolnytsky_Typikon_Master.md:4.2.18.1.3 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_matins.sequence[4].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.16.4` | **Dolnytsky_Typikon_Master.md:4.2.16.4 (L8890-8920)**:<br>L8890: ### 4.2.16 Sunday of the Man Born Blind |
| `structures.passion_matins.sequence[5].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18.2.3` | **Dolnytsky_Typikon_Master.md:4.2.18.2.3 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `structures.passion_matins.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.16` | **Dolnytsky_Typikon_Master.md:4.2.16 (L8890-8920)**:<br>L8890: ### 4.2.16 Sunday of the Man Born Blind |
| `structures.tomb_matins.overrides[0].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.21.2.5` | **Dolnytsky_Typikon_Master.md:4.2.21.2.5 (L9094-9124)**:<br>L9094: ### 4.2.21 Sunday of All Saints |
| `structures.tomb_matins.overrides[1].new_component.content.components[0].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.21.3` | **Dolnytsky_Typikon_Master.md:4.2.21.3 (L9094-9124)**:<br>L9094: ### 4.2.21 Sunday of All Saints |
| `structures.tomb_matins.overrides[1].new_component.content.components[1].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.21.3` | **Dolnytsky_Typikon_Master.md:4.2.21.3 (L9094-9124)**:<br>L9094: ### 4.2.21 Sunday of All Saints |
| `structures.tomb_matins.overrides[1].new_component.content.components[2].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.21.3` | **Dolnytsky_Typikon_Master.md:4.2.21.3 (L9094-9124)**:<br>L9094: ### 4.2.21 Sunday of All Saints |
| `structures.tomb_matins.overrides[1].new_component.content.components[3].content.components[0].rubric.source_ref` | `Dolnytsky_Typikon_Master.md` | **Dolnytsky_Typikon_Master.md:L237-262**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `structures.tomb_matins.overrides[1].new_component.content.components[3].content.components[2].rubric.source_ref` | `Dolnytsky_Typikon_Master.md` | **Dolnytsky_Typikon_Master.md:L237-262**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `structures.tomb_matins.overrides[1].new_component.content.components[3].content.components[3].rubric.source_ref` | `Dolnytsky_Typikon_Master.md` | **Dolnytsky_Typikon_Master.md:L237-262**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `structures.tomb_matins.overrides[1].new_component.content.components[3].content.components[4].rubric.source_ref` | `Dolnytsky_Typikon_Master.md` | **Dolnytsky_Typikon_Master.md:L237-262**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `structures.tomb_matins.overrides[1].new_component.content.components[3].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.21.3.2` | **Dolnytsky_Typikon_Master.md:4.2.21.3.2 (L9094-9124)**:<br>L9094: ### 4.2.21 Sunday of All Saints |
| `structures.tomb_matins.overrides[1].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.21.3` | **Dolnytsky_Typikon_Master.md:4.2.21.3 (L9094-9124)**:<br>L9094: ### 4.2.21 Sunday of All Saints |
| `structures.tomb_matins.overrides[5].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.21.3` | **Dolnytsky_Typikon_Master.md:4.2.21.3 (L9094-9124)**:<br>L9094: ### 4.2.21 Sunday of All Saints |
| `structures.tomb_matins.overrides[6].new_component.rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.23` | **Dolnytsky_Typikon_Master.md:4.2.23 (L9154-9184)**:<br>L9154: ### 4.2.23 Feast of the Most Holy Eucharist |
| `structures.tomb_matins.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.21.1.3` | **Dolnytsky_Typikon_Master.md:4.2.21.1.3 (L9094-9124)**:<br>L9094: ### 4.2.21 Sunday of All Saints |

---

### Database File: `json_db/01j_struct_litiya.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.litiya.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.1.9` | **Dolnytsky_Typikon_Master.md:1.2.1.9 (L460-481)**:<br>L460: #### 9. Conclusion of Vespers |

---

### Database File: `json_db/01j_struct_liturgy.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.liturgy_basil.source_ref` | `Dolnytsky_Typikon_Master.md:1.1` | **Dolnytsky_Typikon_Master.md:1.1 (L244-257)**:<br>L244: ## 1.1 On the Constituent Parts of the Divine Service |
| `structures.liturgy_chrysostom.sequence[0].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.15.4.2` | **Dolnytsky_Typikon_Master.md:4.2.15.4.2 (L8828-8858)**:<br>L8828: ### 4.2.15 Sunday of the Samaritan Woman |
| `structures.liturgy_chrysostom.sequence[16].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:6.4` | **Dolnytsky_Typikon_Master.md:L237-262**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `structures.liturgy_chrysostom.sequence[3].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:6.4` | **Dolnytsky_Typikon_Master.md:L237-262**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `structures.liturgy_chrysostom.source_ref` | `Dolnytsky_Typikon_Master.md:1.1` | **Dolnytsky_Typikon_Master.md:1.1 (L244-257)**:<br>L244: ## 1.1 On the Constituent Parts of the Divine Service |
| `structures.liturgy_chrysostom_vesperal.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.11` | **Dolnytsky_Typikon_Master.md:4.1.11 (L7668-7675)**:<br>L7668: ### 4.1.11 Monday, Tuesday, Wednesday, Thursday and Friday of the Second Week of Great Lent |
| `structures.liturgy_presanctified.sequence[3].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.12` | **Dolnytsky_Typikon_Master.md:4.1.12 (L7676-7706)**:<br>L7676: ### 4.1.12 Saturday of the Second Week of Great Lent |
| `structures.liturgy_presanctified.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.14.3.3` | **Dolnytsky_Typikon_Master.md:4.1.14.3.3 (L7769-7799)**:<br>L7769: ### 4.1.14 Third Week of Great Lent |
| `structures.vesperal_merge_logic.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.6.3` | **Dolnytsky_Typikon_Master.md:3.4.6.3 (L2759-2788)**:<br>L2759: ### 3.4.6 -24 December: Forefeast of the Nativity of Christ |

---

### Database File: `json_db/01k_struct_royal_hours.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.structure_royal.source_ref` | `Dolnytsky_Typikon_Master.md` | **Dolnytsky_Typikon_Master.md:L237-262**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |

---

### Database File: `json_db/01k_struct_vigil.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.all_night_vigil.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.1.1` | **Dolnytsky_Typikon_Master.md:1.2.1.1 (L262-292)**:<br>L262: #### 1. Vesting and Initial Censing |

---

### Database File: `json_db/01l_struct_presanctified.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.liturgy_presanctified.source_ref` | `Dolnytsky_Typikon_Master.md:1.3.2` | **Dolnytsky_Typikon_Master.md:1.3.2 (L622-635)**:<br>L622: ### 1.3.2 Order of Great Compline without Vigil |

---

### Database File: `json_db/01m_struct_vesperal_liturgy.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.vesperal_liturgy.source_ref` | `Dolnytsky_Typikon_Master.md:1.7` | **Dolnytsky_Typikon_Master.md:1.7 (L858-888)**:<br>L858: ## 1.7 On Vespers with Liturgy |

---

### Database File: `json_db/01n_struct_patronal_procession.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `structures.patronal_procession.source_ref` | `Dolnytsky_Typikon_Master.md:5.2` | **Dolnytsky_Typikon_Master.md:5.2 (L9252-9257)**:<br>L9252: ## 5.2 Chapter II: Temple Rubrics |
| `structures.patronal_water_blessing.source_ref` | `Dolnytsky_Typikon_Master.md:5.1` | **Dolnytsky_Typikon_Master.md:5.1 (L9226-9227)**:<br>L9226: ## 5.1 Chapter I |

---

### Database File: `json_db/02a_logic_general.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `logic_definitions.case_01_sunday_simple_saint.source_ref` | `Dolnytsky_Typikon_Master.md:2.1.3.4` | **Dolnytsky_Typikon_Master.md:2.1.3.4 (L919-949)**:<br>L919: ## 2.1 Saint without Polyeleos on a Sunday |
| `logic_definitions.case_01_sunday_simple_saint.variables.aposticha_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.1.1.4` | **Dolnytsky_Typikon_Master.md:2.1.1.4 (L919-949)**:<br>L919: ## 2.1 Saint without Polyeleos on a Sunday |
| `logic_definitions.case_01_sunday_simple_saint.variables.praises_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.1.3.8` | **Dolnytsky_Typikon_Master.md:2.1.3.8 (L919-949)**:<br>L919: ## 2.1 Saint without Polyeleos on a Sunday |
| `logic_definitions.case_01_sunday_simple_saint.variables.vespers_stichera_distribution.logic_switch.saint_on_6.source_ref` | `Dolnytsky_Typikon_Master.md:2.1.3.7` | **Dolnytsky_Typikon_Master.md:2.1.3.7 (L919-949)**:<br>L919: ## 2.1 Saint without Polyeleos on a Sunday |
| `logic_definitions.case_01_sunday_simple_saint.variables.vespers_stichera_distribution.logic_switch.saint_on_6_doxology.source_ref` | `Dolnytsky_Typikon_Master.md:2.1.3.7` | **Dolnytsky_Typikon_Master.md:2.1.3.7 (L919-949)**:<br>L919: ## 2.1 Saint without Polyeleos on a Sunday |
| `logic_definitions.case_02_weekday_simple_saint.source_ref` | `Dolnytsky_Typikon_Master.md:2.3.2` | **Dolnytsky_Typikon_Master.md:2.3.2 (L1069-1099)**:<br>L1069: ## 2.3 Saint without Polyeleos on a Saturday |
| `logic_definitions.case_03_saturday_simple_saint.source_ref` | `Dolnytsky_Typikon_Master.md:2.6.4` | **Dolnytsky_Typikon_Master.md:2.6.4 (L1217-1247)**:<br>L1217: ## 2.6 Saint with an All-Night Vigil on a Sunday |
| `logic_definitions.case_03_saturday_simple_saint.variables.aposticha_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.3.4` | **Dolnytsky_Typikon_Master.md:2.3.4 (L1069-1099)**:<br>L1069: ## 2.3 Saint without Polyeleos on a Saturday |
| `logic_definitions.case_04_sunday_polyeleos.source_ref` | `Dolnytsky_Typikon_Master.md:2.8.2.2` | **Dolnytsky_Typikon_Master.md:2.8.2.2 (L1275-1305)**:<br>L1275: ## 2.8 Forefeast with a Saint without a Polyeleos on a Sunday |
| `logic_definitions.case_04_sunday_polyeleos.variables.aposticha_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.4.1.4` | **Dolnytsky_Typikon_Master.md:2.4.1.4 (L1129-1159)**:<br>L1129: ## 2.4 Saint with Polyeleos on a Sunday |
| `logic_definitions.case_05_weekday_polyeleos.source_ref` | `Dolnytsky_Typikon_Master.md:2.10` | **Dolnytsky_Typikon_Master.md:2.10 (L1368-1398)**:<br>L1368: ## 2.10 Feast of the Lord on a Sunday and Weekdays |
| `logic_definitions.case_05_weekday_polyeleos.variables.aposticha_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.5.1.3` | **Dolnytsky_Typikon_Master.md:2.5.1.3 (L1174-1204)**:<br>L1174: ## 2.5 Saint with Polyeleos on Weekdays and Saturday |
| `logic_definitions.case_05_weekday_polyeleos.variables.praises_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.11.1.1` | **Dolnytsky_Typikon_Master.md:2.11.1.1 (L1415-1445)**:<br>L1415: ## 2.11 Feast of the Theotokos on a Sunday |
| `logic_definitions.case_06_sunday_vigil.source_ref` | `Dolnytsky_Typikon_Master.md:2.11.1.7` | **Dolnytsky_Typikon_Master.md:2.11.1.7 (L1415-1445)**:<br>L1415: ## 2.11 Feast of the Theotokos on a Sunday |
| `logic_definitions.case_06_sunday_vigil.variables.aposticha_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.12.5` | **Dolnytsky_Typikon_Master.md:2.12.5 (L1462-1479)**:<br>L1462: ## 2.12 Feast of the Theotokos on Weekdays |
| `logic_definitions.case_06_sunday_vigil.variables.praises_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.13.1.4` | **Dolnytsky_Typikon_Master.md:2.13.1.4 (L1480-1510)**:<br>L1480: ## 2.13 Afterfeast with a Saint without a Polyeleos on a Sunday |
| `logic_definitions.case_07_weekday_vigil.source_ref` | `Dolnytsky_Typikon_Master.md:2.13.2` | **Dolnytsky_Typikon_Master.md:2.13.2 (L1480-1510)**:<br>L1480: ## 2.13 Afterfeast with a Saint without a Polyeleos on a Sunday |
| `logic_definitions.case_07_weekday_vigil.variables.aposticha_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.14.2` | **Dolnytsky_Typikon_Master.md:2.14.2 (L1525-1555)**:<br>L1525: ## 2.14 Afterfeast with a Saint without a Polyeleos on Weekdays and Saturday |
| `logic_definitions.case_07_weekday_vigil.variables.praises_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.14.3` | **Dolnytsky_Typikon_Master.md:2.14.3 (L1525-1555)**:<br>L1525: ## 2.14 Afterfeast with a Saint without a Polyeleos on Weekdays and Saturday |
| `logic_definitions.case_08_sunday_forefeast.source_ref` | `Dolnytsky_Typikon_Master.md:2.14.1` | **Dolnytsky_Typikon_Master.md:2.14.1 (L1525-1555)**:<br>L1525: ## 2.14 Afterfeast with a Saint without a Polyeleos on Weekdays and Saturday |
| `logic_definitions.case_08_sunday_forefeast.variables.aposticha_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.8.1.2` | **Dolnytsky_Typikon_Master.md:2.8.1.2 (L1275-1305)**:<br>L1275: ## 2.8 Forefeast with a Saint without a Polyeleos on a Sunday |
| `logic_definitions.case_08_sunday_forefeast.variables.praises_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.15.1` | **Dolnytsky_Typikon_Master.md:2.15.1 (L1571-1601)**:<br>L1571: ## 2.15 Afterfeast with a Saint with a Polyeleos on a Sunday |
| `logic_definitions.case_09_weekday_forefeast.source_ref` | `Dolnytsky_Typikon_Master.md:2.15.3` | **Dolnytsky_Typikon_Master.md:2.15.3 (L1571-1601)**:<br>L1571: ## 2.15 Afterfeast with a Saint with a Polyeleos on a Sunday |
| `logic_definitions.case_10_feast_of_lord.source_ref` | `Dolnytsky_Typikon_Master.md:2.18` | **Dolnytsky_Typikon_Master.md:2.18 (L1675-1692)**:<br>L1675: ## 2.18 Afterfeast with a Saint with an All-Night Vigil on Weekdays |
| `logic_definitions.case_10_feast_of_lord.variables.aposticha_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.19.1.5` | **Dolnytsky_Typikon_Master.md:2.19.1.5 (L1693-1723)**:<br>L1693: ## 2.19 Apodosis of a Feast on a Sunday |
| `logic_definitions.case_10_feast_of_lord.variables.praises_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.18.1` | **Dolnytsky_Typikon_Master.md:2.18.1 (L1675-1692)**:<br>L1675: ## 2.18 Afterfeast with a Saint with an All-Night Vigil on Weekdays |
| `logic_definitions.case_11_feast_of_theotokos_sunday.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.3` | **Dolnytsky_Typikon_Master.md:2.20.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_11_feast_of_theotokos_sunday.variables.aposticha_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.11.1.6` | **Dolnytsky_Typikon_Master.md:2.11.1.6 (L1415-1445)**:<br>L1415: ## 2.11 Feast of the Theotokos on a Sunday |
| `logic_definitions.case_11_feast_of_theotokos_sunday.variables.praises_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_12_feast_of_theotokos_weekday.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_13_afterfeast_sunday_simple.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_13_afterfeast_sunday_simple.variables.aposticha_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.13.1.3` | **Dolnytsky_Typikon_Master.md:2.13.1.3 (L1480-1510)**:<br>L1480: ## 2.13 Afterfeast with a Saint without a Polyeleos on a Sunday |
| `logic_definitions.case_13_afterfeast_sunday_simple.variables.praises_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_14_afterfeast_weekday_simple.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_15_afterfeast_sunday_polyeleos.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_15_afterfeast_sunday_polyeleos.variables.aposticha_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.15.1.4` | **Dolnytsky_Typikon_Master.md:2.15.1.4 (L1571-1601)**:<br>L1571: ## 2.15 Afterfeast with a Saint with a Polyeleos on a Sunday |
| `logic_definitions.case_15_afterfeast_sunday_polyeleos.variables.praises_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_16_afterfeast_weekday_polyeleos.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_16_afterfeast_weekday_polyeleos.variables.praises_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_17_afterfeast_sunday_vigil.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_17_afterfeast_sunday_vigil.variables.praises_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_18_afterfeast_weekday_vigil.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_18_afterfeast_weekday_vigil.variables.praises_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_19_apodosis_sunday.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_19_apodosis_sunday.variables.aposticha_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.19.1.4` | **Dolnytsky_Typikon_Master.md:2.19.1.4 (L1693-1723)**:<br>L1693: ## 2.19 Apodosis of a Feast on a Sunday |
| `logic_definitions.case_19_apodosis_sunday.variables.praises_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_20_apodosis_weekday.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_20_apodosis_weekday.variables.aposticha_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.4` | **Dolnytsky_Typikon_Master.md:2.20.4 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.case_20_apodosis_weekday.variables.praises_distribution.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `logic_definitions.special_vigil_override.source_ref` | `Dolnytsky_Typikon_Master.md:2.14.4` | **Dolnytsky_Typikon_Master.md:2.14.4 (L1525-1555)**:<br>L1525: ## 2.14 Afterfeast with a Saint without a Polyeleos on Weekdays and Saturday |

---

### Database File: `json_db/02b_01_september.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `month_settings.days.01.source_ref` | `Dolnytsky_Typikon_Master.md:3.1` | **Dolnytsky_Typikon_Master.md:3.1 (L1782-1783)**:<br>L1782: ## 3.1 September |
| `month_settings.days.06.source_ref` | `Dolnytsky_Typikon_Master.md:3.1` | **Dolnytsky_Typikon_Master.md:3.1 (L1782-1783)**:<br>L1782: ## 3.1 September |
| `month_settings.days.07.source_ref` | `Dolnytsky_Typikon_Master.md:3.1.2.2` | **Dolnytsky_Typikon_Master.md:3.1.2.2 (L1890-1903)**:<br>L1890: ### 3.1.2 Saturday and Sunday before the Exaltation |
| `month_settings.days.08.source_ref` | `Dolnytsky_Typikon_Master.md:3.1.2.2.2` | **Dolnytsky_Typikon_Master.md:3.1.2.2.2 (L1904-1934)**:<br>L1904: #### 3.1.2.2.2 Prokimenon-Alleluia and Apostle-Gospel of the Saturday before the Exaltation (also, only according to Slavic typikons, the sequential Apostle-Gospel); Communion Hymn of the weekday[^247] |
| `month_settings.days.09.source_ref` | `Dolnytsky_Typikon_Master.md:3.1.2.2.2` | **Dolnytsky_Typikon_Master.md:3.1.2.2.2 (L1904-1934)**:<br>L1904: #### 3.1.2.2.2 Prokimenon-Alleluia and Apostle-Gospel of the Saturday before the Exaltation (also, only according to Slavic typikons, the sequential Apostle-Gospel); Communion Hymn of the weekday[^247] |
| `month_settings.days.12.source_ref` | `Dolnytsky_Typikon_Master.md:3.1.2.2.2` | **Dolnytsky_Typikon_Master.md:3.1.2.2.2 (L1904-1934)**:<br>L1904: #### 3.1.2.2.2 Prokimenon-Alleluia and Apostle-Gospel of the Saturday before the Exaltation (also, only according to Slavic typikons, the sequential Apostle-Gospel); Communion Hymn of the weekday[^247] |
| `month_settings.days.13.source_ref` | `Dolnytsky_Typikon_Master.md:3.1.3` | **Dolnytsky_Typikon_Master.md:3.1.3 (L1956-1986)**:<br>L1956: ### 3.1.3 September: Memory of the Renovation of the Temple of the Resurrection[^254] |
| `month_settings.days.14.source_ref` | `Dolnytsky_Typikon_Master.md:3.1.4` | **Dolnytsky_Typikon_Master.md:3.1.4 (L2066-2096)**:<br>L2066: ### 3.1.4 September: Universal Exaltation of the Precious Cross |
| `month_settings.days.21.source_ref` | `Dolnytsky_Typikon_Master.md:3.1.4` | **Dolnytsky_Typikon_Master.md:3.1.4 (L2066-2096)**:<br>L2066: ### 3.1.4 September: Universal Exaltation of the Precious Cross |
| `month_settings.days.23.source_ref` | `Dolnytsky_Typikon_Master.md:3.1.8` | **Dolnytsky_Typikon_Master.md:3.1.8 (L2124-2133)**:<br>L2124: ### 3.1.8 September: Conception of St. John the Baptist |
| `month_settings.days.26.source_ref` | `Dolnytsky_Typikon_Master.md:3.1.9` | **Dolnytsky_Typikon_Master.md:3.1.9 (L2134-2141)**:<br>L2134: ### 3.1.9 September: Falling Asleep of the Holy Apostle John the Theologian |

---

### Database File: `json_db/02b_02_october.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `month_settings.days.01.source_ref` | `Dolnytsky_Typikon_Master.md:3.2` | **Dolnytsky_Typikon_Master.md:3.2 (L2142-2143)**:<br>L2142: ## 3.2 October |
| `month_settings.days.06.source_ref` | `Dolnytsky_Typikon_Master.md:3.2` | **Dolnytsky_Typikon_Master.md:3.2 (L2142-2143)**:<br>L2142: ## 3.2 October |
| `month_settings.days.09.source_ref` | `Dolnytsky_Typikon_Master.md:3.2` | **Dolnytsky_Typikon_Master.md:3.2 (L2142-2143)**:<br>L2142: ## 3.2 October |
| `month_settings.days.18.source_ref` | `Dolnytsky_Typikon_Master.md:3.2` | **Dolnytsky_Typikon_Master.md:3.2 (L2142-2143)**:<br>L2142: ## 3.2 October |
| `month_settings.days.23.source_ref` | `Dolnytsky_Typikon_Master.md:3.2` | **Dolnytsky_Typikon_Master.md:3.2 (L2142-2143)**:<br>L2142: ## 3.2 October |
| `month_settings.days.26.source_ref` | `Dolnytsky_Typikon_Master.md:3.2` | **Dolnytsky_Typikon_Master.md:3.2 (L2142-2143)**:<br>L2142: ## 3.2 October |
| `month_settings.days.28.source_ref` | `Dolnytsky_Typikon_Master.md:3.2` | **Dolnytsky_Typikon_Master.md:3.2 (L2142-2143)**:<br>L2142: ## 3.2 October |
| `month_settings.floating_rules.sunday_fathers_seventh_council.source_ref` | `Dolnytsky_Typikon_Master.md:3.2.2` | **Dolnytsky_Typikon_Master.md:3.2.2 (L2158-2173)**:<br>L2158: ### 3.2.2 October: Sunday of the Holy Fathers |

---

### Database File: `json_db/02b_03_november.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `month_settings.days.08.source_ref` | `Dolnytsky_Typikon_Master.md:3.3` | **Dolnytsky_Typikon_Master.md:3.3 (L2236-2237)**:<br>L2236: ## 3.3 November |
| `month_settings.days.12.source_ref` | `Dolnytsky_Typikon_Master.md:3.3` | **Dolnytsky_Typikon_Master.md:3.3 (L2236-2237)**:<br>L2236: ## 3.3 November |
| `month_settings.days.13.source_ref` | `Dolnytsky_Typikon_Master.md:3.3` | **Dolnytsky_Typikon_Master.md:3.3 (L2236-2237)**:<br>L2236: ## 3.3 November |
| `month_settings.days.14.source_ref` | `Dolnytsky_Typikon_Master.md:3.3` | **Dolnytsky_Typikon_Master.md:3.3 (L2236-2237)**:<br>L2236: ## 3.3 November |
| `month_settings.days.15.source_ref` | `Dolnytsky_Typikon_Master.md:3.3` | **Dolnytsky_Typikon_Master.md:3.3 (L2236-2237)**:<br>L2236: ## 3.3 November |
| `month_settings.days.16.source_ref` | `Dolnytsky_Typikon_Master.md:3.3` | **Dolnytsky_Typikon_Master.md:3.3 (L2236-2237)**:<br>L2236: ## 3.3 November |
| `month_settings.days.21.source_ref` | `Dolnytsky_Typikon_Master.md:3.3` | **Dolnytsky_Typikon_Master.md:3.3 (L2236-2237)**:<br>L2236: ## 3.3 November |
| `month_settings.days.24.source_ref` | `Dolnytsky_Typikon_Master.md:3.3.3` | **Dolnytsky_Typikon_Master.md:3.3.3 (L2254-2284)**:<br>L2254: ### 3.3.3 November: Holy Great-Martyr Catherine and Holy Great-Martyr Mercurius |
| `month_settings.days.25.source_ref` | `Dolnytsky_Typikon_Master.md:3.3.4` | **Dolnytsky_Typikon_Master.md:3.3.4 (L2308-2338)**:<br>L2308: ### 3.3.4 November: Apodosis of the Entry of the Most Holy Theotokos |
| `month_settings.days.30.source_ref` | `Dolnytsky_Typikon_Master.md:3.3` | **Dolnytsky_Typikon_Master.md:3.3 (L2236-2237)**:<br>L2236: ## 3.3 November |

---

### Database File: `json_db/02b_04_december.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `month_settings.days.04.source_ref` | `Dolnytsky_Typikon_Master.md:3.4` | **Dolnytsky_Typikon_Master.md:3.4 (L2350-2351)**:<br>L2350: ## 3.4 December |
| `month_settings.days.05.source_ref` | `Dolnytsky_Typikon_Master.md:3.4` | **Dolnytsky_Typikon_Master.md:3.4 (L2350-2351)**:<br>L2350: ## 3.4 December |
| `month_settings.days.06.source_ref` | `Dolnytsky_Typikon_Master.md:3.4` | **Dolnytsky_Typikon_Master.md:3.4 (L2350-2351)**:<br>L2350: ## 3.4 December |
| `month_settings.days.09.source_ref` | `Dolnytsky_Typikon_Master.md:3.4` | **Dolnytsky_Typikon_Master.md:3.4 (L2350-2351)**:<br>L2350: ## 3.4 December |
| `month_settings.days.12.source_ref` | `Dolnytsky_Typikon_Master.md:3.4` | **Dolnytsky_Typikon_Master.md:3.4 (L2350-2351)**:<br>L2350: ## 3.4 December |
| `month_settings.days.13.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.3` | **Dolnytsky_Typikon_Master.md:3.4.3 (L2506-2536)**:<br>L2506: ### 3.4.3 December: Memory of the Holy Martyrs Eustratius and others |
| `month_settings.days.17.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.4` | **Dolnytsky_Typikon_Master.md:3.4.4 (L2557-2587)**:<br>L2557: ### 3.4.4 December: Memory of the Prophet Daniel and the Youths |
| `month_settings.days.24.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.7` | **Dolnytsky_Typikon_Master.md:3.4.7 (L2789-2819)**:<br>L2789: ### 3.4.7 December: Eve of the Nativity of Christ |
| `month_settings.days.25.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.8` | **Dolnytsky_Typikon_Master.md:3.4.8 (L2867-2876)**:<br>L2867: ### 3.4.8 December: Nativity of our Lord Jesus Christ |
| `month_settings.days.26.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.9` | **Dolnytsky_Typikon_Master.md:3.4.9 (L2969-2999)**:<br>L2969: ### 3.4.9 December: Synaxis of the Most Holy Theotokos |
| `month_settings.days.27.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.5.5.1` | **Dolnytsky_Typikon_Master.md:3.4.5.5.1 (L2615-2645)**:<br>L2615: ### 3.4.5 Sunday of the Holy Fathers before the Nativity of Christ |
| `month_settings.days.31.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.14` | **Dolnytsky_Typikon_Master.md:3.4.14 (L3273-3303)**:<br>L3273: ### 3.4.14 December: Apodosis of the Feast of the Nativity of Christ |
| `month_settings.floating_rules.sunday_ancestors.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.5` | **Dolnytsky_Typikon_Master.md:3.4.5 (L2615-2645)**:<br>L2615: ### 3.4.5 Sunday of the Holy Fathers before the Nativity of Christ |
| `month_settings.floating_rules.sunday_forefathers.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.2` | **Dolnytsky_Typikon_Master.md:3.4.2 (L2446-2476)**:<br>L2446: ### 3.4.2 Sunday of the Holy Forefathers |

---

### Database File: `json_db/02b_05_january.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `month_settings.days.01.source_ref` | `Dolnytsky_Typikon_Master.md:3.5` | **Dolnytsky_Typikon_Master.md:3.5 (L3331-3332)**:<br>L3331: ## 3.5 January |
| `month_settings.days.05.source_ref` | `Dolnytsky_Typikon_Master.md:3.4.6.3` | **Dolnytsky_Typikon_Master.md:3.4.6.3 (L2759-2788)**:<br>L2759: ### 3.4.6 -24 December: Forefeast of the Nativity of Christ |
| `month_settings.days.06.source_ref` | `Dolnytsky_Typikon_Master.md:3.5.4` | **Dolnytsky_Typikon_Master.md:3.5.4 (L3483-3506)**:<br>L3483: ### 3.5.4 January: Holy Theophany |
| `month_settings.days.07.source_ref` | `Dolnytsky_Typikon_Master.md:3.5.5` | **Dolnytsky_Typikon_Master.md:3.5.5 (L3507-3537)**:<br>L3507: ### 3.5.5 January: Synaxis of Saint John the Forerunner |
| `month_settings.days.11.source_ref` | `Dolnytsky_Typikon_Master.md:3.5.8` | **Dolnytsky_Typikon_Master.md:3.5.8 (L3648-3651)**:<br>L3648: ### 3.5.8 January: Our Venerable Father Theodosius |
| `month_settings.days.14.source_ref` | `Dolnytsky_Typikon_Master.md:3.5.9` | **Dolnytsky_Typikon_Master.md:3.5.9 (L3652-3682)**:<br>L3652: ### 3.5.9 January: Apodosis of Theophany |
| `month_settings.days.17.source_ref` | `Dolnytsky_Typikon_Master.md:3.5.17` | **Dolnytsky_Typikon_Master.md:3.5.17 (L3702-3705)**:<br>L3702: ### 3.5.17 JANUARY |
| `month_settings.days.20.source_ref` | `Dolnytsky_Typikon_Master.md:3.5.20` | **Dolnytsky_Typikon_Master.md:3.5.20 (L3706-3709)**:<br>L3706: ### 3.5.20 JANUARY |
| `month_settings.days.22.source_ref` | `Dolnytsky_Typikon_Master.md:3.5.22` | **Dolnytsky_Typikon_Master.md:3.5.22 (L3331-3332)**:<br>L3331: ## 3.5 January |
| `month_settings.days.25.source_ref` | `Dolnytsky_Typikon_Master.md:3.5.25` | **Dolnytsky_Typikon_Master.md:3.5.25 (L3710-3713)**:<br>L3710: ### 3.5.25 JANUARY |
| `month_settings.days.27.source_ref` | `Dolnytsky_Typikon_Master.md:3.5.27` | **Dolnytsky_Typikon_Master.md:3.5.27 (L3714-3733)**:<br>L3714: ### 3.5.27 JANUARY |
| `month_settings.days.30.source_ref` | `Dolnytsky_Typikon_Master.md:3.5.17` | **Dolnytsky_Typikon_Master.md:3.5.17 (L3702-3705)**:<br>L3702: ### 3.5.17 JANUARY |

---

### Database File: `json_db/02b_06_february.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `month_settings.days.01.source_ref` | `Dolnytsky_Typikon_Master.md:3.6.1` | **Dolnytsky_Typikon_Master.md:3.6.1 (L3852-3882)**:<br>L3852: ### 3.6.1 February: Forefeast of the Meeting of the Lord |
| `month_settings.days.02.source_ref` | `Dolnytsky_Typikon_Master.md:3.6.2` | **Dolnytsky_Typikon_Master.md:3.6.2 (L3999-4029)**:<br>L3999: ### 3.6.2 February: Meeting of the Lord |
| `month_settings.days.24.source_ref` | `Dolnytsky_Typikon_Master.md:3.6.4` | **Dolnytsky_Typikon_Master.md:3.6.4 (L4291-4294)**:<br>L4291: ### 3.6.4 February: First and Second Finding of the Precious Head of the Forerunner |

---

### Database File: `json_db/02b_07_march.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `month_settings.days.09.source_ref` | `Dolnytsky_Typikon_Master.md:3.7` | **Dolnytsky_Typikon_Master.md:3.7 (L4666-4667)**:<br>L4666: ## 3.7 March |
| `month_settings.days.24.source_ref` | `Dolnytsky_Typikon_Master.md:3.7.2.8.3` | **Dolnytsky_Typikon_Master.md:3.7.2.8.3 (L4733-4763)**:<br>L4733: ### 3.7.2 March: Forefeast of the Annunciation[^392] |
| `month_settings.days.25.source_ref` | `Dolnytsky_Typikon_Master.md:3.7.3.17` | **Dolnytsky_Typikon_Master.md:3.7.3.17 (L5001-5031)**:<br>L5001: ### 3.7.3 March: Annunciation to the Most Holy Theotokos |
| `month_settings.days.26.source_ref` | `Dolnytsky_Typikon_Master.md:3.7.3.26` | **Dolnytsky_Typikon_Master.md:3.7.3.26 (L5001-5031)**:<br>L5001: ### 3.7.3 March: Annunciation to the Most Holy Theotokos |

---

### Database File: `json_db/02b_08_april.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `month_settings.days.01.source_ref` | `Dolnytsky_Typikon_Master.md:3.8` | **Dolnytsky_Typikon_Master.md:3.8 (L5885-5886)**:<br>L5885: ## 3.8 April |
| `month_settings.days.23.source_ref` | `Dolnytsky_Typikon_Master.md:3.8` | **Dolnytsky_Typikon_Master.md:3.8 (L5885-5886)**:<br>L5885: ## 3.8 April |
| `month_settings.days.25.source_ref` | `Dolnytsky_Typikon_Master.md:3.8.2` | **Dolnytsky_Typikon_Master.md:3.8.2 (L6167-6176)**:<br>L6167: ### 3.8.2 April: Holy Apostle and Evangelist Mark |
| `month_settings.days.30.source_ref` | `Dolnytsky_Typikon_Master.md:3.8` | **Dolnytsky_Typikon_Master.md:3.8 (L5885-5886)**:<br>L5885: ## 3.8 April |

---

### Database File: `json_db/02b_09_may.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `month_settings.days.03.source_ref` | `Dolnytsky_Typikon_Master.md:3.9.1` | **Dolnytsky_Typikon_Master.md:3.9.1 (L6187-6192)**:<br>L6187: ### 3.9.1 May: Our Venerable Father Theodosius of the Caves |
| `month_settings.days.07.source_ref` | `Dolnytsky_Typikon_Master.md:3.9.2` | **Dolnytsky_Typikon_Master.md:3.9.2 (L6193-6223)**:<br>L6193: ### 3.9.2 May: Appearance of the Sign of the Precious Cross in the sky in Jerusalem |
| `month_settings.days.08.source_ref` | `Dolnytsky_Typikon_Master.md:3.9.3` | **Dolnytsky_Typikon_Master.md:3.9.3 (L6243-6273)**:<br>L6243: ### 3.9.3 May: Holy Apostle and Evangelist John the Theologian |
| `month_settings.days.09.source_ref` | `Dolnytsky_Typikon_Master.md:3.9.4` | **Dolnytsky_Typikon_Master.md:3.9.4 (L6430-6433)**:<br>L6430: ### 3.9.4 May: Translation of the relics of our holy father Nicholas |
| `month_settings.days.10.source_ref` | `Dolnytsky_Typikon_Master.md:3.9.5` | **Dolnytsky_Typikon_Master.md:3.9.5 (L6434-6464)**:<br>L6434: ### 3.9.5 May: Holy Apostle Simon |
| `month_settings.days.11.source_ref` | `Dolnytsky_Typikon_Master.md:3.8.3` | **Dolnytsky_Typikon_Master.md:3.8.3 (L6177-6184)**:<br>L6177: ### 3.8.3 April |
| `month_settings.days.21.source_ref` | `Dolnytsky_Typikon_Master.md:3.9.6` | **Dolnytsky_Typikon_Master.md:3.9.6 (L6470-6473)**:<br>L6470: ### 3.9.6 May: Constantine and Helen |
| `month_settings.days.25.source_ref` | `Dolnytsky_Typikon_Master.md:3.9.5` | **Dolnytsky_Typikon_Master.md:3.9.5 (L6434-6464)**:<br>L6434: ### 3.9.5 May: Holy Apostle Simon |

---

### Database File: `json_db/02b_10_june.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `month_settings.days.09.source_ref` | `Dolnytsky_Typikon_Master.md:3.8.1.2` | **Dolnytsky_Typikon_Master.md:3.8.1.2 (L5887-5917)**:<br>L5887: ### 3.8.1 April: Holy Great-Martyr George |
| `month_settings.days.10.source_ref` | `Dolnytsky_Typikon_Master.md:3.8.1.2.3` | **Dolnytsky_Typikon_Master.md:3.8.1.2.3 (L5887-5917)**:<br>L5887: ### 3.8.1 April: Holy Great-Martyr George |
| `month_settings.days.11.source_ref` | `Dolnytsky_Typikon_Master.md:3.10` | **Dolnytsky_Typikon_Master.md:3.10 (L6584-6585)**:<br>L6584: ## 3.10 June |
| `month_settings.days.19.source_ref` | `Dolnytsky_Typikon_Master.md:3.10` | **Dolnytsky_Typikon_Master.md:3.10 (L6584-6585)**:<br>L6584: ## 3.10 June |
| `month_settings.days.24.source_ref` | `Dolnytsky_Typikon_Master.md:3.10` | **Dolnytsky_Typikon_Master.md:3.10 (L6584-6585)**:<br>L6584: ## 3.10 June |
| `month_settings.days.29.source_ref` | `Dolnytsky_Typikon_Master.md:3.10.2` | **Dolnytsky_Typikon_Master.md:3.10.2 (L6634-6637)**:<br>L6634: ### 3.10.2 June: Nativity of Saint John the Baptist |
| `month_settings.days.30.source_ref` | `Dolnytsky_Typikon_Master.md:3.10` | **Dolnytsky_Typikon_Master.md:3.10 (L6584-6585)**:<br>L6584: ## 3.10 June |

---

### Database File: `json_db/02b_11_july.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `month_settings.days.02.source_ref` | `Dolnytsky_Typikon_Master.md:3.11.1` | **Dolnytsky_Typikon_Master.md:3.11.1 (L6676-6699)**:<br>L6676: ### 3.11.1 July: Deposition of the Precious Robe of the Most Holy Theotokos |
| `month_settings.days.05.source_ref` | `Dolnytsky_Typikon_Master.md:3.11` | **Dolnytsky_Typikon_Master.md:3.11 (L6674-6675)**:<br>L6674: ## 3.11 July |
| `month_settings.days.10.source_ref` | `Dolnytsky_Typikon_Master.md:3.11` | **Dolnytsky_Typikon_Master.md:3.11 (L6674-6675)**:<br>L6674: ## 3.11 July |
| `month_settings.days.11.source_ref` | `Dolnytsky_Typikon_Master.md:3.11` | **Dolnytsky_Typikon_Master.md:3.11 (L6674-6675)**:<br>L6674: ## 3.11 July |
| `month_settings.days.15.source_ref` | `Dolnytsky_Typikon_Master.md:3.11` | **Dolnytsky_Typikon_Master.md:3.11 (L6674-6675)**:<br>L6674: ## 3.11 July |
| `month_settings.days.20.source_ref` | `Dolnytsky_Typikon_Master.md:3.11` | **Dolnytsky_Typikon_Master.md:3.11 (L6674-6675)**:<br>L6674: ## 3.11 July |
| `month_settings.days.24.source_ref` | `Dolnytsky_Typikon_Master.md:3.11` | **Dolnytsky_Typikon_Master.md:3.11 (L6674-6675)**:<br>L6674: ## 3.11 July |
| `month_settings.days.25.source_ref` | `Dolnytsky_Typikon_Master.md:3.11.4` | **Dolnytsky_Typikon_Master.md:3.11.4 (L6712-6723)**:<br>L6712: ### 3.11.4 July: Dormition of St. Anne, mother of the Most Holy Theotokos |
| `month_settings.days.27.source_ref` | `Dolnytsky_Typikon_Master.md:3.11` | **Dolnytsky_Typikon_Master.md:3.11 (L6674-6675)**:<br>L6674: ## 3.11 July |
| `month_settings.days.31.source_ref` | `Dolnytsky_Typikon_Master.md:3.11.5` | **Dolnytsky_Typikon_Master.md:3.11.5 (L6724-6754)**:<br>L6724: ### 3.11.5 July: Forefeast of the Procession of the Precious Cross[^450] |
| `month_settings.floating_rules.sunday_fathers_six_councils.source_ref` | `Dolnytsky_Typikon_Master.md:3.11` | **Dolnytsky_Typikon_Master.md:3.11 (L6674-6675)**:<br>L6674: ## 3.11 July |

---

### Database File: `json_db/02b_12_august.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `month_settings.days.01.source_ref` | `Dolnytsky_Typikon_Master.md:3.12` | **Dolnytsky_Typikon_Master.md:3.12 (L6792-6793)**:<br>L6792: ## 3.12 August |
| `month_settings.days.06.source_ref` | `Dolnytsky_Typikon_Master.md:3.12.2` | **Dolnytsky_Typikon_Master.md:3.12.2 (L6830-6835)**:<br>L6830: ### 3.12.2 August: Transfiguration of the Lord |
| `month_settings.days.15.source_ref` | `Dolnytsky_Typikon_Master.md:3.12.3` | **Dolnytsky_Typikon_Master.md:3.12.3 (L6836-6839)**:<br>L6836: ### 3.12.3 August: Dormition of the Most Holy Theotokos |
| `month_settings.days.16.source_ref` | `Dolnytsky_Typikon_Master.md:3.12.4` | **Dolnytsky_Typikon_Master.md:3.12.4 (L6840-6870)**:<br>L6840: ### 3.12.4 August: Image Not-Made-By-Hands |
| `month_settings.days.23.source_ref` | `Dolnytsky_Typikon_Master.md:3.11.4.1` | **Dolnytsky_Typikon_Master.md:3.11.4.1 (L6712-6723)**:<br>L6712: ### 3.11.4 July: Dormition of St. Anne, mother of the Most Holy Theotokos |
| `month_settings.days.29.source_ref` | `Dolnytsky_Typikon_Master.md:3.12.5` | **Dolnytsky_Typikon_Master.md:3.12.5 (L6945-6948)**:<br>L6945: ### 3.12.5 August: Beheading of the Precious Head of St. John the Baptist |
| `month_settings.days.31.source_ref` | `Dolnytsky_Typikon_Master.md:3.12.6` | **Dolnytsky_Typikon_Master.md:3.12.6 (L6949-6958)**:<br>L6949: ### 3.12.6 August: Deposition of the Sash of the Most Holy Theotokos |

---

### Database File: `json_db/02b_logic_theotokia.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `aposticha_theotokia.source_ref` | `Dolnytsky_Typikon_Master.md:2.10.3` | **Dolnytsky_Typikon_Master.md:2.10.3 (L1368-1398)**:<br>L1368: ## 2.10 Feast of the Lord on a Sunday and Weekdays |
| `theotokia_tables.dismissal_theotokia.source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.6` | **Dolnytsky_Typikon_Master.md:1.5.1.6 (L749-769)**:<br>L749: #### 6. Praises (Lauds), Great Doxology, and Dismissal |
| `theotokia_tables.stavrotheotokia.source_ref` | `Dolnytsky_Typikon_Master.md:2.5.3.5` | **Dolnytsky_Typikon_Master.md:2.5.3.5 (L1174-1204)**:<br>L1174: ## 2.5 Saint with Polyeleos on Weekdays and Saturday |
| `theotokia_tables.sunday_theotokia.source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.6` | **Dolnytsky_Typikon_Master.md:1.5.1.6 (L749-769)**:<br>L749: #### 6. Praises (Lauds), Great Doxology, and Dismissal |

---

### Database File: `json_db/02c_logic_triodion.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `logic_map.apodosis_pascha.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.16.2` | **Dolnytsky_Typikon_Master.md:4.2.16.2 (L8890-8920)**:<br>L8890: ### 4.2.16 Sunday of the Man Born Blind |
| `logic_map.ascension.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.17` | **Dolnytsky_Typikon_Master.md:4.2.17 (L8948-8953)**:<br>L8948: ### 4.2.17 Ascension of the Lord |
| `logic_map.cheesefare_week_general.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.5` | **Dolnytsky_Typikon_Master.md:4.1.5 (L7099-7129)**:<br>L7099: ### 4.1.5 Cheesefare Week |
| `logic_map.co_suffering_theotokos.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.1.3` | **Dolnytsky_Typikon_Master.md:4.1.1.3 (L6961-6991)**:<br>L6961: ### 4.1.1 Sunday of the Publican and Pharisee |
| `logic_map.feast_of_eucharist.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.1.3` | **Dolnytsky_Typikon_Master.md:4.1.1.3 (L6961-6991)**:<br>L6961: ### 4.1.1 Sunday of the Publican and Pharisee |
| `logic_map.great_lent_clean_week.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.7` | **Dolnytsky_Typikon_Master.md:4.1.7 (L7354-7384)**:<br>L7354: ### 4.1.7 Beginning of Great Lent |
| `logic_map.holy_monday_tuesday_wednesday.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.16` | **Dolnytsky_Typikon_Master.md:4.1.16 (L7851-7858)**:<br>L7851: ### 4.1.16 Fourth Sunday of Great Lent |
| `logic_map.lent_general_weekday.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.7` | **Dolnytsky_Typikon_Master.md:4.1.7 (L7354-7384)**:<br>L7354: ### 4.1.7 Beginning of Great Lent |
| `logic_map.lent_wednesday_friday_presanctified.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.7.3` | **Dolnytsky_Typikon_Master.md:4.1.7.3 (L7354-7384)**:<br>L7354: ### 4.1.7 Beginning of Great Lent |
| `logic_map.mid_pentecost.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.13` | **Dolnytsky_Typikon_Master.md:4.2.13 (L8706-8736)**:<br>L8706: ### 4.2.13 Sunday of the Paralytic |
| `logic_map.monday_holy_spirit.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.24` | **Dolnytsky_Typikon_Master.md:4.2.24 (L9200-9225)**:<br>L9200: ### 4.2.24 Feast of the Co-suffering of the Most Holy Theotokos |
| `logic_map.pentecost.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.23` | **Dolnytsky_Typikon_Master.md:4.2.23 (L9154-9184)**:<br>L9154: ### 4.2.23 Feast of the Most Holy Eucharist |
| `logic_map.pentecostarion_general_weekday.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.9` | **Dolnytsky_Typikon_Master.md:4.2.9 (L8530-8555)**:<br>L8530: ### 4.2.9 On the Day of Resurrection in the Evening |
| `logic_map.saturday_akathist.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.12.3` | **Dolnytsky_Typikon_Master.md:4.1.12.3 (L7676-7706)**:<br>L7676: ### 4.1.12 Saturday of the Second Week of Great Lent |
| `logic_map.saturday_lazarus.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.14` | **Dolnytsky_Typikon_Master.md:4.1.14 (L7769-7799)**:<br>L7769: ### 4.1.14 Third Week of Great Lent |
| `logic_map.saturday_lent_1.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.8` | **Dolnytsky_Typikon_Master.md:4.1.8 (L7540-7570)**:<br>L7540: ### 4.1.8 Vespers on Wednesday and Friday with Presanctified |
| `logic_map.saturday_lent_2_3_4.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.9.2` | **Dolnytsky_Typikon_Master.md:4.1.9.2 (L7574-7604)**:<br>L7574: ### 4.1.9 First Saturday of Great Lent |
| `logic_map.saturday_meatfare.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.3` | **Dolnytsky_Typikon_Master.md:4.1.3 (L7025-7055)**:<br>L7025: ### 4.1.3 Meatfare, or Soul Saturday |
| `logic_map.saturday_soul_pentecost.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.22` | **Dolnytsky_Typikon_Master.md:4.2.22 (L9146-9153)**:<br>L9146: ### 4.2.22 Beginning of the Fast of the Saints Chief Apostles Peter and Paul |
| `logic_map.sunday_all_saints.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.26` | **Dolnytsky_Typikon_Master.md:4.2.26 (L7969-7999)**:<br>L7969: ## 4.2 Flower Triodion (Pentecostarion) |
| `logic_map.sunday_blind_man.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.16.1` | **Dolnytsky_Typikon_Master.md:4.2.16.1 (L8890-8920)**:<br>L8890: ### 4.2.16 Sunday of the Man Born Blind |
| `logic_map.sunday_cheesefare.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.6` | **Dolnytsky_Typikon_Master.md:4.1.6 (L7314-7344)**:<br>L7314: ### 4.1.6 Cheesefare Sunday |
| `logic_map.sunday_fathers_1st_council.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18` | **Dolnytsky_Typikon_Master.md:4.2.18 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `logic_map.sunday_lent_1.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.8.2` | **Dolnytsky_Typikon_Master.md:4.1.8.2 (L7540-7570)**:<br>L7540: ### 4.1.8 Vespers on Wednesday and Friday with Presanctified |
| `logic_map.sunday_lent_2.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.9.3` | **Dolnytsky_Typikon_Master.md:4.1.9.3 (L7574-7604)**:<br>L7574: ### 4.1.9 First Saturday of Great Lent |
| `logic_map.sunday_lent_3.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.10` | **Dolnytsky_Typikon_Master.md:4.1.10 (L7616-7646)**:<br>L7616: ### 4.1.10 First Sunday of Great Lent |
| `logic_map.sunday_lent_4.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.11.2` | **Dolnytsky_Typikon_Master.md:4.1.11.2 (L7668-7675)**:<br>L7668: ### 4.1.11 Monday, Tuesday, Wednesday, Thursday and Friday of the Second Week of Great Lent |
| `logic_map.sunday_lent_5.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.13` | **Dolnytsky_Typikon_Master.md:4.1.13 (L7735-7765)**:<br>L7735: ### 4.1.13 Second Sunday of Great Lent |
| `logic_map.sunday_meatfare.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.4` | **Dolnytsky_Typikon_Master.md:4.1.4 (L7093-7098)**:<br>L7093: ### 4.1.4 Meatfare Sunday |
| `logic_map.sunday_myrrhbearers.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.10.2` | **Dolnytsky_Typikon_Master.md:4.2.10.2 (L8556-8586)**:<br>L8556: ### 4.2.10 General Rubric for All Days of Bright Week |
| `logic_map.sunday_palm.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.15` | **Dolnytsky_Typikon_Master.md:4.1.15 (L7847-7850)**:<br>L7847: ### 4.1.15 Fourth Saturday of Great Lent |
| `logic_map.sunday_paralytic.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.12.4` | **Dolnytsky_Typikon_Master.md:4.2.12.4 (L8642-8672)**:<br>L8642: ### 4.2.12 Sunday of the Myrrh-Bearing Women |
| `logic_map.sunday_prodigal_son.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.2` | **Dolnytsky_Typikon_Master.md:4.1.2 (L7019-7024)**:<br>L7019: ### 4.1.2 Sunday of the Prodigal Son |
| `logic_map.sunday_publican_pharisee.source_ref` | `Dolnytsky_Typikon_Master.md:4.1` | **Dolnytsky_Typikon_Master.md:4.1 (L6959-6960)**:<br>L6959: ## 4.1 Lenten Triodion |
| `logic_map.sunday_samaritan.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.14.1` | **Dolnytsky_Typikon_Master.md:4.2.14.1 (L8764-8794)**:<br>L8764: ### 4.2.14 Mid-Pentecost |
| `logic_map.sunday_thomas.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.8` | **Dolnytsky_Typikon_Master.md:4.2.8 (L8446-8476)**:<br>L8446: ### 4.2.8 Resurrection Matins |
| `logic_map.thursday_great_canon.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.12` | **Dolnytsky_Typikon_Master.md:4.1.12 (L7676-7706)**:<br>L7676: ### 4.1.12 Saturday of the Second Week of Great Lent |

---

### Database File: `json_db/02c_logic_troparia_god_is_lord.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `troparia_rules.conditions[0].source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.2` | **Dolnytsky_Typikon_Master.md:1.5.1.2 (L683-693)**:<br>L683: #### 2. Order of Troparia at *“God is the Lord”* |
| `troparia_rules.conditions[1].source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `troparia_rules.conditions[2].source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.2` | **Dolnytsky_Typikon_Master.md:1.5.1.2 (L683-693)**:<br>L683: #### 2. Order of Troparia at *“God is the Lord”* |
| `troparia_rules.conditions[3].source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.2` | **Dolnytsky_Typikon_Master.md:1.5.1.2 (L683-693)**:<br>L683: #### 2. Order of Troparia at *“God is the Lord”* |
| `troparia_rules.conditions[4].source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.2` | **Dolnytsky_Typikon_Master.md:1.5.1.2 (L683-693)**:<br>L683: #### 2. Order of Troparia at *“God is the Lord”* |
| `troparia_rules.conditions[5].source_ref` | `Dolnytsky_Typikon_Master.md` | **Dolnytsky_Typikon_Master.md:L237-262**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `troparia_rules.conditions[6].source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.2` | **Dolnytsky_Typikon_Master.md:1.5.1.2 (L683-693)**:<br>L683: #### 2. Order of Troparia at *“God is the Lord”* |
| `troparia_rules.conditions[7].source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.2` | **Dolnytsky_Typikon_Master.md:1.5.1.2 (L683-693)**:<br>L683: #### 2. Order of Troparia at *“God is the Lord”* |
| `troparia_rules.conditions[8].source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.2` | **Dolnytsky_Typikon_Master.md:1.5.1.2 (L683-693)**:<br>L683: #### 2. Order of Troparia at *“God is the Lord”* |
| `troparia_rules.conditions[9].source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.3` | **Dolnytsky_Typikon_Master.md:1.5.1.3 (L694-702)**:<br>L694: #### 3. From the Kathismata to the Graduals (Polyeleos Rubrics) |

---

### Database File: `json_db/02d_logic_canon_refrains.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `canon_refrains.source_ref` | `Dolnytsky_Typikon_Master.md:1.5.1.5` | **Dolnytsky_Typikon_Master.md:1.5.1.5 (L717-747)**:<br>L717: #### 5. Order of the Matins Canon |

---

### Database File: `json_db/02d_logic_temple.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `specific_cases.case_10.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 10)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_11.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 11)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_12.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 12)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_13.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 13)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_14.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 14)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_15.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 15)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_16.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 16)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_17.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 17)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_18.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 18)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_19.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 19)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_1a.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 1a)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_1b.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 1b)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_2.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 2)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_20.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 20)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_21.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 21)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_22.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 22)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_23.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 23)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_24.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 24)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_25.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 25)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_26.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 26)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_27.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 27)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_28.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 28)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_29.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 29)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_3.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 3)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_30.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 30)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_31.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 31)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_32.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 32)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_33.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 33)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_4.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 4)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_5.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 5)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_6.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 6)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_7.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 7)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_8.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 8)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `specific_cases.case_9.source_ref` | `Final_Dolnytsky_part5_temple.md:5.2.2 (Case 9)` | **Dolnytsky_Typikon_Master.md:5.2.2 (L9272-9302)**:<br>L9272: ### 5.2.2 Specific Temple Rubrics[^669] |
| `system_settings.general_rules.G1.source_ref` | `Dolnytsky_Typikon_Master.md` | **Dolnytsky_Typikon_Master.md:L237-262**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `system_settings.general_rules.G3.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |

---

### Database File: `json_db/02e_logic_katavasia.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `daily_matins_override.source_ref` | `Dolnytsky_Typikon_Master.md:1.2.2.5` | **Dolnytsky_Typikon_Master.md:1.2.2.5 (L482-483)**:<br>L482: ### 1.2.2 Order of Great Vespers without Vigil |
| `katavasia_seasons.source_ref` | `Final_Dolnytsky_part5_temple.md:5.3` | **Dolnytsky_Typikon_Master.md:5.3 (L9732-9762)**:<br>L9732: ## 5.3 Rule of Services for the Whole Year |

---

### Database File: `json_db/02e_logic_matins.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `bridegroom_canon_type.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.13.3` | **Dolnytsky_Typikon_Master.md:4.2.13.3 (L8706-8736)**:<br>L8706: ### 4.2.13 Sunday of the Paralytic |
| `passion_gospel_formula.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.18` | **Dolnytsky_Typikon_Master.md:4.2.18 (L8954-8984)**:<br>L8954: ### 4.2.18 Sunday of the Holy Fathers of the First Nicaean Council |
| `psalm_50_intercession.source_ref` | `Dolnytsky_Typikon_Master.md:4.1.9.1.6` | **Dolnytsky_Typikon_Master.md:4.1.9.1.6 (L7574-7604)**:<br>L7574: ### 4.1.9 First Saturday of Great Lent |
| `tomb_matins_encomia_stations.source_ref` | `Dolnytsky_Typikon_Master.md:4.2.21.3` | **Dolnytsky_Typikon_Master.md:4.2.21.3 (L9094-9124)**:<br>L9094: ### 4.2.21 Sunday of All Saints |

---

### Database File: `json_db/02k_logic_collisions.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `collisions.06-11.rules[0].rubric.source_ref` | `Dolnytsky_Typikon_Master.md:3.10.1.10` | **Dolnytsky_Typikon_Master.md:3.10.1.10 (L6586-6616)**:<br>L6586: ### 3.10.1 June: Holy Apostles Bartholomew and Barnabas |
| `floating_collisions.saturday_after_exaltation.rubric.source_ref` | `Dolnytsky Part III (Menaion): Saturday after the Exaltation` | **Dolnytsky_Typikon_Master.md:Part I (L237-262)**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `floating_collisions.saturday_after_nativity.rubric.source_ref` | `Dolnytsky Part III (Menaion): Saturday after the Nativity of Christ (Dec 26-31)` | **Dolnytsky_Typikon_Master.md:Part I (L237-262)**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `floating_collisions.saturday_after_theophany.rubric.source_ref` | `Dolnytsky Part III (Menaion): Saturday after Theophany (Jan 7-13)` | **Dolnytsky_Typikon_Master.md:Part I (L237-262)**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `floating_collisions.saturday_before_exaltation.rubric.source_ref` | `Dolnytsky Part III (Menaion): Saturday before the Exaltation` | **Dolnytsky_Typikon_Master.md:Part I (L237-262)**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `floating_collisions.saturday_before_nativity.rubric.source_ref` | `Dolnytsky Part III (Menaion): Saturday before the Nativity of Christ (Dec 18-24)` | **Dolnytsky_Typikon_Master.md:Part I (L237-262)**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `floating_collisions.saturday_before_theophany.rubric.source_ref` | `Dolnytsky Part III (Menaion): Saturday before Theophany (Jan 1-5)` | **Dolnytsky_Typikon_Master.md:Part I (L237-262)**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `floating_collisions.sunday_after_exaltation.rubric.source_ref` | `Dolnytsky Part III (Menaion): Sunday after the Exaltation` | **Dolnytsky_Typikon_Master.md:Part I (L237-262)**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `floating_collisions.sunday_after_nativity.rubric.source_ref` | `Dolnytsky Part III (Menaion): Sunday after the Nativity (Dec 26-31)` | **Dolnytsky_Typikon_Master.md:Part I (L237-262)**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `floating_collisions.sunday_after_nativity_transferred.rubric.source_ref` | `Dolnytsky Part III (Menaion): Synaxis on Monday Dec 26 with Holy Kinsmen` | **Dolnytsky_Typikon_Master.md:Part I (L237-262)**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `floating_collisions.sunday_after_theophany.rubric.source_ref` | `Dolnytsky Part III (Menaion): Sunday after Theophany (Jan 7-13)` | **Dolnytsky_Typikon_Master.md:Part I (L237-262)**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `floating_collisions.sunday_before_exaltation.rubric.source_ref` | `Dolnytsky Part III (Menaion): Sunday before the Exaltation` | **Dolnytsky_Typikon_Master.md:Part I (L237-262)**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `floating_collisions.sunday_before_nativity.rubric.source_ref` | `Dolnytsky Part III (Menaion): Sunday of the Holy Fathers (Dec 18-24)` | **Dolnytsky_Typikon_Master.md:Part I (L237-262)**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `floating_collisions.sunday_before_theophany.rubric.source_ref` | `Dolnytsky Part III (Menaion): Sunday before Theophany (Jan 1-5)` | **Dolnytsky_Typikon_Master.md:Part I (L237-262)**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |
| `floating_collisions.sunday_forefathers.rubric.source_ref` | `Dolnytsky Part III (Menaion): Sunday of the Forefathers (Dec 11-17)` | **Dolnytsky_Typikon_Master.md:Part I (L237-262)**:<br>L237: # PART I: GENERAL VIEW OF THE DIVINE SERVICES |

---

### Database File: `json_db/04_logic_small_vespers.json`

| JSON Path | Citation Target | Source Excerpt |
| :--- | :--- | :--- |
| `small_vespers_distribution.case_06_sunday_vigil.source_ref` | `Dolnytsky_Typikon_Master.md:2.11.2.3` | **Dolnytsky_Typikon_Master.md:2.11.2.3 (L1415-1445)**:<br>L1415: ## 2.11 Feast of the Theotokos on a Sunday |
| `small_vespers_distribution.case_07_weekday_vigil.source_ref` | `Dolnytsky_Typikon_Master.md:2.13.2.3` | **Dolnytsky_Typikon_Master.md:2.13.2.3 (L1480-1510)**:<br>L1480: ## 2.13 Afterfeast with a Saint without a Polyeleos on a Sunday |
| `small_vespers_distribution.case_10_feast_lord.source_ref` | `Dolnytsky_Typikon_Master.md:2.18.1` | **Dolnytsky_Typikon_Master.md:2.18.1 (L1675-1692)**:<br>L1675: ## 2.18 Afterfeast with a Saint with an All-Night Vigil on Weekdays |
| `small_vespers_distribution.case_11_theotokos_sunday.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.1.1` | **Dolnytsky_Typikon_Master.md:2.20.1.1 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `small_vespers_distribution.case_12_theotokos_weekday.source_ref` | `Dolnytsky_Typikon_Master.md:2.18` | **Dolnytsky_Typikon_Master.md:2.18 (L1675-1692)**:<br>L1675: ## 2.18 Afterfeast with a Saint with an All-Night Vigil on Weekdays |
| `small_vespers_distribution.case_17_afterfeast_sunday_vigil.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |
| `small_vespers_distribution.case_18_afterfeast_weekday_vigil.source_ref` | `Dolnytsky_Typikon_Master.md:2.20.2.3` | **Dolnytsky_Typikon_Master.md:2.20.2.3 (L1740-1770)**:<br>L1740: ## 2.20 Apodosis of a Feast on Weekdays |

---
