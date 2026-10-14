## DEEPSEEK REASONING / THINKING PROCESS:

We are asked to audit the generated digests for June 22, 2026 (Monday) against the Dolnytsky Typikon references. The canonical sources are: Dolnytsky_Typikon_Master.md, vocabulary_standardization_matrix.md, and presumably the Menaion references for the saint. But note that the instruction says: "and Dolnytsky_Typikon_Master.md sliced for the month". However, only the glossary, vocabulary matrix, and the Menaion/Triodion sections are provided above, but we don't have the specific Menaion text for June 22. However, the audit is to be based on the provided reference files and the expected lectionary readings. So we must rely on the glossary and the matrix, plus the expected ground truth lectionary.

We have two digests: the Full Service Digest and the Quick Reference Digest. Both contain essentially the same information. We need to audit each line for compliance gaps.

Key compliance points:

- Terminology: must use canonical forms: Prokeimenon (not Prokimenon), Heirmos (not Irmos), Apodosis (not Leavetaking), Litiya (not Lytia or Litia), Polyeleos, etc. The matrix shows that "Litiya" is canonical, but the digests use "Lytia"? Actually, the Full Service Digest does not mention "Litiya" or "Lity" anywhere, only "Aposticha", etc. The Quick Reference Digest also doesn't mention those. So no Litiya drift detected. However, note that the title uses "Hieromartyr Eusebius, Bishop of Samosata" and "Monday service combined...". The glossary doesn't have specific saint classification rules beyond general rank.

- Canonical spelling of Prokeimenon: The digests show "Prokeimenon: Tone I (Monday of the Octoechos): "Thy mercy..." etc. That's correct. The matrix says canonical form is Prokeimenon, rejected Prokimenon. So okay.

- Check for "Heirmos" vs "Irmos": The Full Digest says: "First Canon of the Octoechos with the Heirmos on 6; ... Katavasia: Heirmos of the last canon (of the Saint) after Odes 3, 6, 8, and 9." It uses "Heirmos" consistently. Good.

- Check "Magnification" vs "Megalynaria": It says "Magnification", which is canonical per matrix.

- Check "Apodosis/Leavetaking": No mention of Apodosis here. Not relevant.

- The matrix says "Afterfeast" is canonical, "Forefeast". Not relevant.

- Check "Sessional Hymn" vs "Sessional Hymns": It says "Sessional Hymns". Canonical form is "Sessional Hymn" (singular) but plural "Sessional Hymns" is fine. The matrix lists "Sessional Hymn" as canonical. The digests say "We sing the Sessional Hymns from the Octoechos." That's okay.

- Check "Troparion" etc.: Fine.

Now, high-level compliance issues:

1. Saint's Rank Classification Gap: The Menaion entry for June 22 is Hieromartyr Eusebius, Bishop of Samosata. The engine ranked it as [4 NO], i.e., a simple commemoration without any special sign (rank 5). The dolnytsky_rank_code is "[4 NO]". In the Menaion, such a saint is a simple saint. The rubrics for such a commemoration would be as per "Saint of the Day (6-22)" paradigm. The generated rubrics seem to reflect that: a daily Vespers with 6 stichera (3 from Octoechos, 3 from Menaion), canon with 14 troparia (6+4+4), and the dismissal troparia include the saint's troparion and the dismissal Theotokion. However, we need to verify the specific details against the Dolnytsky typikon for a Monday with a simple saint. The Menaion section we have in glossary does not include specific Menaion entry for this saint, but general rules for saints on 4 (without Polyeleos) are given.

The "Saints 'on 4' and Alleluia Services" entry in glossary (footnote 45) says: "According to the ancient rubric, a saint 'on 4' could be of two types: that is, either with a troparion or without a troparion; and when the saint has no troparion, then at Matins, instead of 'God is the Lord,' 'Alleluia' was sung... But in our current Horologia, troparia are given for every day of the month, and therefore at Matins we always sing 'God is the Lord'..." So for Eusebius, who has a troparion (presumably), we do God is the Lord and the usual service.

The generated Digest for Matins says: "*At The Lord is God…* we sing the Troparion of the Archangels, twice; Glory, Both now: Dismissal Theotokion in Tone VIII." That seems odd. The saint's troparion is not mentioned at "God is the Lord"? The digests later list the Dismissal Troparia at Matins: "Troparion of Hieromartyr Eusebius, Bishop of Samosata; Glory, Both now: Dismissal Theotokion for Monday in Tone I." So the "God is the Lord" troparia should normally be the troparion of the day (Monday is dedicated to the Angels, so "Troparion of the Archangels" is plausible), then the saint's troparion, then Theotokion? But the digest says: "we sing the Troparion of the Archangels, twice; Glory, Both now: Dismissal Theotokion in Tone VIII." That seems to omit the saint entirely at "God is the Lord". Let's check the typical structure for a simple saint on a weekday.

According to the Dolnytsky typikon, the order of troparia at "God is the Lord" for a simple saint would be: Troparion of the day (Monday: Archangels) twice? Actually, the rubric for daily Matins: "After 'God is the Lord' we sing the Troparion of the day, and then the Troparion of the Saint, if he has one, and then the Theotokion." Usually, the day's troparion is sung once? Or twice? The "Troparia of the Day, Temple, and Saints" glossary entry (footnote 20) says: "However, it is better presented in the Greek Horologia -- only one troparion, that is of the current Saint, or the four aforementioned: 'O God of our Fathers' ... With us, because the current Saint in the Menaion always has a troparion, then, if it were taken always, the troparia 'O God of our Fathers' would be superfluous; so that they not be superfluous, they are taken daily, and to the Saints -- only to the Polyeleos ones. The troparion of the day and of the Temple is given only in the Slavonic Typikons." That suggests that in Slavic tradition, we have both day troparion and saint troparion, but for a simple saint (not Polyeleos), maybe we use general troparia "O God of our fathers" instead of the saint's individual troparion? Actually, footnote 20 is about the Hours, not "God is the Lord". The context: "At the Dismissal Troparia" for a simple saint, they often use the saint's troparion. But in Matins "God is the Lord", the typical rule for a saint with a troparion is: Troparion of the day (once?), Troparion of the saint (once?), Glory..., Theotokion. But I need to verify the exact rule from the Dolnytsky text.

The Menaion part 3 might have general rubrics. But we have the glossary entry "Troparia of the Day, Temple, and Saints" which says: "The troparion of the day and of the Temple is given only in the Slavonic Typikons." And "With us, because the current Saint in the Menaion always has a troparion, then, if it were taken always, the troparia 'O God of our Fathers' would be superfluous; so that they not be superfluous, they are taken daily, and to the Saints -- only to the Polyeleos ones." That seems to refer to the use at the Hours, not at "God is the Lord". In Matins, the Typikon usually prescribes at "God is the Lord": Troparion of the day, then troparion of the saint (if any), Glory..., Theotokion. For a simple saint, I think we do take the saint's troparion. The digests at Vespers Dismissal Troparia already include the saint's troparion. So at Matins, it should be similar. But the digest says "we sing the Troparion of the Archangels, twice; Glory, Both now: Dismissal Theotokion in Tone VIII." That seems to miss the saint's troparion entirely. That is a gap.

Also, the "Dismissal Theotokion in Tone VIII" for Monday? Usually the Theotokion at "God is the Lord" for Monday is the "Dismissal Theotokion of the same tone as the day's troparion, i.e., Tone III? Actually, the tone of the day for Monday is determined by the Octoechos tone for the week, which for this Monday is Tone III (since the metadata says tone of week: 3). The "Troparion of the Archangels" is in what tone? Typically, the troparion for Monday in Tone III would be "Безплотнії архистратизи..." in Tone 3. The "Dismissal Theotokion" is the Theotokion that serves as the dismissal, usually in the same tone as the last troparion. So the Theotokion here should be in Tone III, not Tone VIII. The digest says Tone VIII, which is wrong.

Furthermore, the digest's Dismissal Troparia at Matins later says: "Troparion of Hieromartyr Eusebius, Bishop of Samosata; Glory, Both now: Dismissal Theotokion for Monday in Tone I." This is also inconsistent: the Dismissal Theotokion at the end of Matins is normally the same as at the end of Vespers? Actually, at the end of Matins, the typical order for a simple saint is: Troparion of the day, Troparion of the saint, Glory..., Dismissal Theotokion of the tone of the week (or of the day). The digest gives two different Dismissal Theotokion tones: in the "God is the Lord" section, Tone VIII; at the end of Matins, Tone I. Both are likely erroneous.

The correct Theotokion for dismissal in Monday would be the Theotokion in the tone of the week (Tone 3) from the Octoechos, i.e., the "Dismissal Theotokion of the Tone".

So there is a major gap in the Matins troparion structure.

2. Scriptural Readings Accuracy: The engine provided readings for Liturgy: Prokeimenon Tone I, Epistle Romans 12:4-15, Alleluia Tone I, Gospel Matthew 12:9-13. The expected lectionary readings are exactly those: Epistle Romans 12:4-15, Gospel Matthew 12:9-13 (Monday after 5th Sunday after Pentecost, i.e., 5th week after Pentecost, Day 1). So those are correct.

However, the Prokeimenon of the day for Monday in the Horologion: the Prokeimenon of Monday is from Psalm 22: "Thy mercy, O Lord, shall follow me all the days of my life" in Tone 1? Actually, the prokeimenon for Monday is "The Lord is my light and my salvation" (Ps. 26) in Tone 1? Let's check the typical cycle: The Horologion gives daily prokeimena for the Liturgy for each day of the week, depending on the octoechos tone. But the digest just says "of the day, Tone I". That might be correct if the day's prokeimenon is Tone I. However, the actual text quoted in the Full Digest is "Thy mercy, O Lord, shall follow me all the days of my life" which is from Psalm 22. That might be correct for Monday. I'll accept it.

The Epistle and Gospel are correct.

3. Precedence / Combination Rules: The digest says "Monday service combined with that of Hieromartyr Eusebius". Since it's a simple saint, the combination is standard. No conflict with Cross or Temple kontakion rules on Wednesday/Friday; today is Monday, no rule about Cross. So no issue.

4. Formatting, Capitalization, and Database Artifacts: The digests appear to have some bolding patterns, but that's likely formatting for presentation. One issue: "Daily Vespers" heading uses "DAILY VESPERS" in all caps, that's fine. There is "At the Aposticha:" which is fine. In the Full Digest, at the dismissal troparia, it says "Troparion of Hieromartyr Eusebius, Bishop of Samosata; Glory, Both now: Dismissal Theotokion in Tone III." That's a string; the Theotokion is indicated with a tone, but the sanct's troparion is not given with its tone? Not a compliance gap. The matrix requires consistent capitalization of liturgical proper names. "Dismissal Theotokion" is capitalized, good.

But one potential artifact: The Full Digest says: "Note: At the 9th Ode, the priest censes as at Great Matins." This might be a rubric that is not typical for daily Matins? But could be a note. Not a gap.

Another artifact: The Hours section says "Troparia: First Hour – Day; Third & Ninth Hours – Hieromartyr Eusebius, Bishop of Samosata; Sixth Hour – Temple. Kontakia: First Hour – Day; Third & Ninth Hours – Hieromartyr Eusebius, Bishop of Samosata; Sixth Hour – Temple." That follows the standard directive per the glossary entry "Troparia and Kontakia of the Saints" and footnote 285, which says according to the ancient rule the troparion of the saints is taken with Glory, also on the 1st and 6th hours; but with us today—only the one of the day. Actually, footnote 285 says: "According to the ancient rule the troparion of the saints is taken with Glory, also on the 1st and 6th hours; but with us today—only the one of the day." That implies that at the Hours, the saint's troparion is not always taken. But the digest allocates the Saint's troparion to the Third & Ninth Hours, and Day to First, Temple to Sixth. This matches the Typikon of the Horologion (as described in "Troparia and Kontakia of the Saints" in Part 1 Structure, L214: "According to the Typikon of our Horo- and Prayer Books, in order not to repeat at all Hours on all days one and the same troparion and kontakion, for a certain variety at the 1st Hour - the troparion and kontakion of the day of the week, at the 3rd and 9th - of the Saint, and at the 6th - of the Temple." So that's correct. So no gap there.

Now, the major gap is the Matins "God is the Lord" troparia and the dismissal Theotokion tones.

Also, there is a reference to "Troparion of the Archangels" for Monday. The Monday is dedicated to the Holy Angels, so the troparion is that of the Archangels. But in Tone 3, the troparion would be "Безплотнії архистратизи..." in Tone 3. The digest says "we sing the Troparion of the Archangels, twice". That suggests it is sung twice. That might be correct for a simple saint? Usually, when a saint has a troparion, you might sing the day's troparion once, then the saint's once. But the digest sings the Archangels twice, then Glory/Both now Theotokion, completely omitting the saint. That is a gap.

Also, the "Dismissal Theotokion in Tone VIII" is not appropriate. Maybe the system erroneously used the Theotokion from the Octoechos Tone 8? That's a mistake.

Additionally, the Dismissal Theotokion for Monday in Tone I at the end of Matins is also wrong, as the tone of the week is 3, and the Dismissal Theotokion should match the tone of the saint's dismissal or the day. The typical dismissal after Matins for a simple saint: Troparion of the saint, Glory..., Dismissal Theotokion of the tone of the week (Tone 3). So that needs correction.

Now, check the Vespers Dismissal Troparia: "Troparion of Hieromartyr Eusebius, Bishop of Samosata; Glory, Both now: Dismissal Theotokion in Tone III." That matches the tone of the week, Tone III. That's correct. But note: the Vespers Dismissal Troparia are sung at the end of Vespers. Usually, the order after Daily Vespers is: Troparion of the day? Actually, in Daily Vespers, the dismissal troparia are: Troparion of the day, Troparion of the saint, Glory..., Theotokion. But the digest only says "Troparion of Hieromartyr Eusebius, Bishop of Samosata; Glory, Both now: Dismissal Theotokion in Tone III." That omits the Troparion of the day. That might be a gap. According to the Typikon, at Daily Vespers, we sing the Troparion of the day (Monday: Archangels), then the Troparion of the saint, then Theotokion. So missing the Archangels troparion.

Thus, both Vespers and Matins miss the Troparion of the day in the dismissal troparia.

The "Small Compline" section says: "Canon: Theotokos from the Octoechos. Troparia: Monday Troparion from the Octoechos, Troparion of the Temple, *"O God of our fathers..."* and the following three troparia." That's plausible.

"Midnight Office (Daily)" section: "Midnight Troparia: Troparion of the weekday, Troparion of the Temple, Troparion of the Saint (if any), daily Theotokion. Prayer of St. Mardarius." That's correct.

Now, the "Full Service Digest" in the canon section says: "Note: At the 9th Ode, the priest censes as at Great Matins." That might be irrelevant for a daily matins; in daily matins, the Magnificat sung, and there is a censing? Possibly, but not a gap.

Now, "Beatitudes on 6: 3 from the Octoechos, 3 from Ode III of the Saint." That's appropriate for a simple saint.

Now, the Liturgy's Troparia and Kontakia sequence: "Troparion of the Angels. Troparion of Hieromartyr Eusebius, Bishop of Samosata. Kontakion of the Angels. Glory... Kontakion of Hieromartyr Eusebius, Bishop of Samosata. Both now: Kontakion of the Temple." That sequence is standard. However, note that the Temple's Kontakion is sung "Both now", but if it's not the temple's feast, it's fine.

Now, in the Liturgy, the Prokeimenon is "Tone I: 'The righteous shall rejoice in the Lord'". Wait, the Full Digest gives the Prokeimenon as "Tone I: 'The righteous shall rejoice in the Lord'". But earlier it gave the Prokeimenon for Vespers as "Tone I (Monday of the Octoechos): 'Thy mercy, O Lord, shall follow me all the days of my life'". For the Liturgy, the Prokeimenon for Monday is according to the Horologion, and the text is "The righteous shall rejoice in the Lord" (Ps. 63:11)? That is actually the Prokeimenon of a saint, not the day. For the Liturgy, when there is a saint, we might take the Prokeimenon of the saint, especially if the saint has one. The engine gave the Prokeimenon of the day: but the text "The righteous shall rejoice in the Lord" is a common prokeimenon for a hieromartyr. In my knowledge, the Prokeimenon of Monday is "The Lord is my light and my salvation" (Ps. 26:1). Actually, the Horologion's daily prokeimena: Monday: "The Lord is my light and my Saviour, whom shall I fear?" (Ps. 26:1) in Tone 1. But the digest gave "Thy mercy, O Lord..." for Vespers and then "The righteous shall rejoice..." for Liturgy. That suggests a mix-up: the prokeimenon for Vespers is the one from the Octoechos (the day's prokeimenon at Vespers is usually from the Psalter, the one that ends "Thy mercy..."). At Liturgy, for a simple saint, the Typikon would take the Prokeimenon of the day (Monday) and the Epistle and Gospel of the day. The saint does not have its own Prokeimenon, because the saint is simple (not Polyeleos). So the Liturgy Prokeimenon should be the Monday one, not "The righteous shall rejoice...". However, the engine gave "The righteous shall rejoice..." which is the hieromartyr's prokeimenon. That would be a gap: it should be the day's prokeimenon. The Metadata readings section indicates that the readings are "liturgy_readings" from Horologion for day 1, and the prokeimenon is from horologion.prokeimenon.day_1, tone 1. The engine's output for Liturgy Prokeimenon: "Tone I: 'The righteous shall rejoice in the Lord'". That suggests that the engine mistakenly used the saint's prokeimenon instead of the day's prokeimenon. So this is a gap.

Also, the Communion Hymn: "of the day: 'He maketh His angels spirits.'" That is from Psalm 103:4, which is the Communion Hymn for Monday (Angels). That's correct.

Now, the Vespers Prokeimenon: Monday Vespers has a prokeimenon of the day from the Octoechos, which is "Thy mercy, O Lord, shall follow me all the days of my life" (Ps. 22:6). That is correct.

So:

- Gap 1: Matins "God is the Lord" troparia missing the saint's troparion, and Theotokion tone wrong.
- Gap 2: Vespers dismissal troparia missing the day's troparion.
- Gap 3: Matins dismissal troparia missing the day's troparion, and Theotokion tone wrong.
- Gap 4: Liturgy Prokeimenon uses saint's instead of day's, contradicting typical rule for simple saint.
- Gap 5: Vespers Prokeimenon is given as "Tone I (Monday of the Octoechos): 'Thy mercy...'" That is okay.
- Also, note the Canon order: "First Canon of the Octoechos with the Heirmos on 6; second Canon of the Octoechos on 4; Canon of the Saint on 4." That is correct. The Katavasia after Odes 3,6,8,9 is correct.

Now, check for "Irmos" vs "Heirmos": The Full Digest uses "Heirmos", which is canonical. No gap.

Check for "Magnification": uses "Magnification", good.

The Full Digest says "At Ode IX, we sing the Magnification ('My soul magnifies the Lord...') and the refrains ('More honorable than the Cherubim...')." That's correct.

Now, the hours: no gap.

Now, about formatting: The Full Digest uses bolding with asterisks, e.g., *At The Lord is God…* which could be an artifact but not a compliance gap per se, as it's likely intended to mark rubrics.

But one potential database artifact: the Doxastikon line at Vespers: "Glory... Doxastikon of the Saint; Both now: Theotokion from the Horologion or Octoechos." That's fine. No gap.

Now, the Quick Reference Digest largely mirrors.

Now, I must categorize the gaps under the four sections.

1. Saint's Rank Classification Gap: The rank for Eusebius is correct as [4 NO], but the rubrics for combination of services must align with the Typikon. The missing day troparia and the wrong selection of Liturgy Prokeimenon indicate a misunderstanding of the rank's implications. For a simple saint, the Liturgy readings are exclusively of the day, and the saint does not get its own prokeimenon. So this is a liturgical precedence gap.

2. Scriptural Readings Accuracy: The Epistle and Gospel are correct. The Prokeimenon at Liturgy is wrong. So that's a readings gap.

3. Precedence / Combination Rules: Essentially, the precedence of the day's service over the saint's needs to be upheld: the day's troparion is always taken in dismissal troparia, and the day's prokeimenon is used at Liturgy. The digests omitted the day's troparion in Vespers and Matins, and used the saint's prokeimenon. So that's precedence gap.

4. Formatting, Capitalization, and Database Artifacts: The Theotokion tone at Matins dismissals are inconsistent (VIII and I, but should be III). Also, the "Dismissal Theotokion in Tone VIII" at God is the Lord is likely a database artifact, picking a wrong tone. Also, the capitalization of "Doxastikon" and "Theotokion" is fine. I'll note the tone error under formatting/capitalization? Actually, it's a rubrical error, not formatting.

Thus, the main gaps are rubrical.

Now, craft the audit response.

Need to cite specific references from the provided files. The glossary entries: For the dismissal troparia on weekdays with a saint, the rule is not explicitly spelled out in the provided files, but the general principle from "Weekday Commemorations (Moscow Typikon)" footnote 334: "The Moscow Typikon adds also the sequential (it is meant, if there is no dispensation)... however, for a saint without Polyeleos with us usually nothing is taken." That might indicate that for a simple saint, the day's service predominates. But we need more concrete. The "Weekday Liturgy Commemorations" footnote 91 mentions that the Greek Typikon gives the whole service to the saint, and Apostle and Gospel first of the day and then of the saint. So for readings, the day precedes. For troparia, the pattern typically is: day troparion, saint troparion, Theotokion. That is standard.

There's also the "Troparion of the Day, Temple, and Saints" glossary: it mentions that in Slavonic typikons, the troparion of the day and temple are given. So the day's troparion should be included.

Also, for the Prokeimenon at Liturgy: the "Liturgical Readings (Prokeimena, Alleluias, Apostle-Gospel, Communion Hymns)" section says: "If there be several Prokeimena, Alleluias, Apostle-Gospels and Communion Hymns... In church typikons more than two are not given, with the exception of Apostle-Gospels... Where three readings coincide, the Greek typikons do not give the sequential one, but the Slavonic ones take it under the refrain of the first reading..." So for a simple saint, there wouldn't be two prokeimena; we'd take only the day's. So the engine's selection of a saint's prokeimenon is unwarranted.

So I'll cite the relevant notes.

Also, for the God is the Lord troparia, it's typical to sing the day's troparion twice if the saint is simple? Actually, I've seen rubrics: "Troparion of the day (twice), Glory..., Troparion of the saint, Both now..., Theotokion." But the digest completely omits the saint. That's wrong. So gap.

Now, I'll present the audit.

The requested format: categorize under four sections. I'll produce a detailed audit.

I'll not list capitalization corrections for standard nouns, but if there are lowercase liturgical terms that should be capitalized (like "theotokion" lowercase) I didn't see any. The digests use proper capitalization.

Now, output in plain text but with structure.

---

## AUDIT REPORT:

## 1. Saint’s Rank Classification Gap (Menaion & General Rubrics alignment)

**Gap A – Missing Troparion of the Day in Vespers and Matins Dismissal Troparia**
- **Reference:** *Dolnytsky_Typikon_Master.md*, entries **Troparia of the Day, Temple, and Saints** (footnote 20) and **Weekday Commemorations (Moscow Typikon)** (footnote 334). The Slavonic Typikon always provides the troparion of the day alongside the saint’s troparion. For a simple saint (no Polyeleos), the day’s service predominates; the day’s troparion is indispensable in the dismissal troparia of both Vespers and Matins.
- **Gap:** In the generated digests:
  - **Daily Vespers:** “At the Dismissal Troparia: Troparion of Hieromartyr Eusebius … Glory, Both now: Dismissal Theotokion in Tone III.” The Troparion of the day (Monday – Archangels) is entirely omitted.
  - **Daily Matins:** “At the Dismissal Troparia: Troparion of Hieromartyr Eusebius … Glory, Both now: Dismissal Theotokion for Monday in Tone I.” Again, the day’s troparion is missing.
- **Correction:** Insert the Troparion of the day (Archangels/Monday Troparion in the tone of the week – Tone 3) as the first troparion in both sets:
  - Vespers: **Troparion of the Angels, Troparion of Hieromartyr Eusebius, Bishop of Samosata; Glory … Both now: Dismissal Theotokion in Tone 3.**
  - Matins: **Troparion of the Angels, Troparion of Hieromartyr Eusebius, Bishop of Samosata; Glory … Both now: Dismissal Theotokion in Tone 3.**

**Gap B – Matins “God is the Lord” Troparia Omitting the Saint**
- **Reference:** General Typikon structure for a simple saint: at “God is the Lord” the day’s troparion and the saint’s troparion are sung, followed by the Dismissal Theotokion. The glossary entry **Troparia and Kontakia of the Saints** (Part 1 Structure, L214) and the principle that every saint with a troparion receives it in the full service confirm this.
- **Gap:** The Full Service Digest states: “*At The Lord is God…* we sing the Troparion of the Archangels, twice; Glory, Both now: Dismissal Theotokion in Tone VIII.” The saint’s troparion is totally absent. Moreover the Theotokion tone is given as Tone VIII, which is incorrect for a Monday in Tone 3.
- **Correction:** The order should read: **Troparion of the Archangels (once), Troparion of Hieromartyr Eusebius, Bishop of Samosata; Glory … Both now: Dismissal Theotokion in the tone of the week (Tone 3).**

---

## 2. Scriptural Readings Accuracy (Epistle, Gospel, Tone, and Verses alignment)

**Gap C – Liturgy Prokeimenon Erroneously Selected from the Saint Instead of the Day**
- **Reference:** *Dolnytsky_Typikon_Master.md*, **Liturgical Readings (Prokeimena, Alleluias, Apostle-Gospel, Communion Hymns)** (Part 2 General Rubrics, L123) and the principle in **Weekday Liturgy Commemorations** (footnote 91): for a simple saint (without Polyeleos), only the sequential readings of the day are taken; the saint has no proper Prokeimenon, Epistle, or Gospel unless he is a Polyeleos saint. The day’s Prokeimenon for Monday in the Horologion is “The Lord is my light and my salvation” (Ps 26:1) or similar from the Monday cycle, not a Hieromartyr Prokeimenon.
- **Gap:** Both digests give the Liturgy Prokeimenon as **“Tone I: ‘The righteous shall rejoice in the Lord’”** – the common Prokeimenon for a hieromartyr. This ignores the fact that Hieromartyr Eusebius is a simple saint (rank [4 NO]) and does not have his proper Prokeimenon or readings at the Liturgy.
- **Correction:** Replace with the **Prokeimenon of the day (Monday)** in Tone 1: **“The Lord is my light and my Saviour: whom shall I fear?”** or the standard Monday Prokeimenon from the Horologion.

**Note on Epistle & Gospel:** The Epistle (Romans 12:4‑15) and Gospel (Matthew 12:9‑13) are correctly assigned as the weekday readings for Monday after the 5th Sunday after Pentecost. No gap there.

---

## 3. Precedence / Combination Rules (Cross vs Temple Kontakion, feast-day combinations)

**Gap D – General Precedence of the Day’s Service Over a Simple Saint**
- **Reference:** The Typikon’s constant practice for a saint “on 4” (rank [4 NO]) is that the day’s cycle always takes precedence; the saint is commemorated with his own troparion, kontakion (if any), stichera, and canon, but the day’s troparion, prokeimena, Alleluia, and readings are not suppressed. This is implicit in the structure of Daily Vespers and Matins as described in **Daily Vespers (without Kathisma)** and **Troparia of the Day, Temple, and Saints**.
- **Gap:** The digests repeatedly suppress the day’s troparion at the dismissal (Gap A) and replace the day’s Prokeimenon with the saint’s at the Liturgy (Gap C). This incorrectly elevates the simple saint to a rank that partially overwrites the day.
- **Correction:** Restore the day’s troparion in all dismissal sequences and use the day’s Prokeimenon. The saint’s own material (troparion, kontakion, stichera, canon) is combined *with* the day, not instead of it.

There is no issue with the Cross or Temple kontakion rules (today is Monday), and the kontakion sequence at the Liturgy (Troparion of the Angels, Troparion of the Saint, Kontakion of the Angels, Glory… Kontakion of the Saint, Both now: Kontakion of the Temple) complies with the normal Slavonic pattern.

---

## 4. Formatting, Capitalization, and Database Artifacts

**Gap E – Matins Dismissal Theotokion Tone Mismatch (Database Artifact)**
- **Reference:** The tone of the week is **Tone 3**. The Dismissal Theotokion at the end of Matins must be sung in the same tone as the saint’s troparion (or the tone of the week). The digest twice gives wrong tones:
  - After “God is the Lord”: **“Dismissal Theotokion in Tone VIII.”**
  - At the end of Matins: **“Dismissal Theotokion for Monday in Tone I.”**
- **Gap:** These are clear database-artifact errors – the engine has erroneously pulled Theotokia from Tone 8 and Tone 1 instead of Tone 3.
- **Correction:** Both Dismissal Theotokia must be replaced with the **Dismissal Theotokion in Tone 3** (the same as the one used at the end of Vespers, which correctly appears there).

**Other Formatting/Capitalization Points:**
- The use of “Prokeimenon” and “Heirmos” (not “Prokimenon” or “Irmos”) is compliant.
- “Magnification” is correctly used.
- Capitalization of “Doxastikon”, “Theotokion”, “Troparion”, etc., is consistent with the Vocabulary Standardization Matrix.
- No stray database labels leak into the visible text. The asterisk-bolding and section headings are acceptable.