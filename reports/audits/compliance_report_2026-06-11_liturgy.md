## DEEPSEEK REASONING / THINKING PROCESS:

We need to perform a rigorous audit of the two generated digests for 2026-06-11 against the canonical Dolnytsky references. The date is the Apodosis of the Eucharist combined with Apostles Bartholomew and Barnabas (Polyeleos). The canon references provide general rules for combining such feasts. We must examine the digests for compliance with the glossary, standardization matrix, and the specific rubric from Part 3 Menaion for June (3.10.1 June: Holy Apostles Bartholomew and Barnabas) and Part 4 Triodion regarding the Eucharist Apodosis.

First, the expected ground truth from the context: The Apodosis of the Eucharist collides with Saints Bartholomew and Barnabas, Polyeleos rank. According to the Menaion section (3.10.1 June) we have: "3.10.1 June: Holy Apostles Bartholomew and Barnabas. Have 11 following cases: ... 3.10.1.10 On the Apodosis of the Feast of the Eucharist ... According to the rule of Constantine and the Finding, when they fall on the Apodosis of the Ascension and Pentecost, here on p. 300-301." That refers to the rule for Constantine and Helen? Actually, it says "According to the rule of Constantine and the Finding" but that might be a cross-reference. The Menaion reference says "On Friday of the Apodosis of the Ascension" etc. The rule is likely the combination rule for a Polyeleos saint with an Apodosis of a feast of the Lord. Dolnytsky gives a general rule: "For the Apodosis of a feast combined with a Saint with Polyeleos: at Small Vespers... everything is sung to the Saint... etc." But here there is no All-Night Vigil (not a Vigil feast, just Polyeleos, so Small Vespers is not held? Actually, if it's not a Vigil, there is no Small Vespers. The instruction might be about the case. The ground truth explicitly states: "The Apodosis of the Eucharist combined with a Polyeleos Saint does NOT have an All-Night Vigil. The day is celebrated using standard Great Vespers and Festal Matins structures (no Small Vespers, no Litya, and no blessing of loaves)."

Check the reference Menaion: For the Apodosis of the Eucharist, the feast is a Lord's feast (Eucharist) which has Apodosis. The saints are Polyeleos. The case is covered in 3.10.1.10 which references "on p. 300-301", which might be the rule for "Constantine and the Finding" (the Finding of the Precious Head of the Forerunner) on the Apodosis of the Ascension and Pentecost. Part 3 Menaion around p. 300-301 would be the Finding of the Head (May 25) when it falls on Apodosis of Ascension or Pentecost. The principle: combine, but no Vigil. The ground truth says no Small Vespers, no Litya, no blessing of loaves because no Vigil.

Now, compare the generated digests.

First, the Service Digest's title: "APODOSIS OF THE EUCHARIST - TONE I. Apostles Bartholomew and Barnabas. Thursday service combined with that of the Triodion, and that of Apostles Bartholomew and Barnabas." This is fine.

It says "Vestment colour: Bright (White)." Apodosis of Eucharist is a feast of the Lord, colour is bright/white, okay.

It says "Vestments (priest): epitrachelion, phelonion. The phelonion is blessed and kissed before the Entrance." Not relevant to the rubric audit.

"Fasting Rule: No fasting restrictions." Apodosis, so no fasting? Actually, in the period after Pentecost, normal days no fasting. Fine.

"Censing: Priest censes entire church during Psalm 103. Censing: Deacon performs Great censing of the entire church during 'Lord, I Call'." The ground truth mentions that censing at Great Vespers: priest censes during Psalm 103, deacon (or priest if no deacon) censes at "Lord, I have cried". This is correct.

"At Lord, I Call… we sing 6 Feast Stichera from the Triodion, and 4 Stichera of the Saint from the Menaion; Glory... Doxastikon of Apostles Bartholomew and Barnabas; Both now: Sticheron of the Feast (Eucharist)." The variable resolved gives 6 Feast (Triodion) and 4 Saint. Is that correct? The ground truth says: "At Lord, I have cried: we sing 6 Feast stichera from the Triodion and 4 Stichera of the Saint from the Menaion; Glory... Doxastikon of the Saint; Both now: Sticheron of the Feast." The resolved variable's vespers_stichera_distribution says 6 feast (from Triodion) and 4 saint, which matches the ground truth. Good.

But note: The Menaion source says Triodion? For Apodosis of a feast, the stichera are from the Triodion (Pentecostarion), which includes the Apodosis of the Eucharist. So "Feast Stichera from the Triodion" is correct.

"Prokeimenon: Daily Prokeimenon for Thursday evening, Tone VII." The ground truth says Prokeimenon at Vespers is of the day, Tone VII. Correct.

"At the Aposticha: We sing 3 Aposticha Feast from the Triodion; Glory... Doxastikon of the Saint; Both now: Theotokion of the Feast." The ground truth says same: 3 Aposticha of the Feast, Glory: Doxastikon of Saint, Both now: Theotokion of the Feast. So okay.

"At the Dismissal Troparia: We sing the Troparion of Apostles Bartholomew and Barnabas; Glory, Both now: Troparion of the Feast." Ground truth: Troparion of the Saint, Glory, Both now: Troparion of the Feast. Yes.

On Compline: "Canon: Theotokos from the Octoechos. Troparia: Kontakion of Apostles Bartholomew and Barnabas; Glory... Both now: Kontakion of the Feast (Eucharist)." Compline for a feast without Vigil: According to footnote 341, "If there is no All-Night Vigil, at Compline -- Kontakion to the Saint, Glory, Both now: of the Feast". So that is correct.

Midnight Office: "After the 1st Trisagion — Troparion of the Feast (Eucharist). After the 2nd Trisagion — Kontakion of the Feast." Then "Prayer of St. Mardarius." For a Lord's feast without Vigil? According to the glossary, "Midnight Office on Feasts of the Lord and Theotokos" footnote 22 says: "To the aforementioned cases which the Greek and Slavonic Typikons present, the Moscow Octoechos of 1782 adds also other Feasts of the Lord and of the Theotokos, presenting at the Midnight Office on the feast day itself, on the first day of Afterfeast, the troparion and kontakion of the feast; however, we do not have this new Typikon." That indicates that for feasts of the Lord, at Midnight Office we would take feast troparion/kontakion after Trisagions. But is the Apodosis considered "feast day itself"? It's the Apodosis, i.e., the Leavetaking. The Apodosis of a feast is the last day of afterfeast. For Apodosis, the feast's troparion and kontakion are used. So having Troparion and Kontakion of the Feast at Midnight Office is correct. After 1st Trisagion, Troparion of the Feast; after 2nd, Kontakion of the Feast. That matches the general practice for Afterfeast/Apodosis. The prayer "Remember" is omitted for feasts. The digest adds "Prayer of St. Mardarius" which is typical for Midnight Office? The usual Midnight Office prayer is "Remember, O Lord", but for feasts it is replaced with "Lord, have mercy" (12) and dismissal. In the digest it says "Prayer of St. Mardarius" — that might be a standard part of the Midnight Office after the 2nd Trisagion? Actually, in the Daily Midnight Office, after the 2nd Trisagion we say the prayer "Remember, O Lord" (for the departed) or for feasts we omit it and say "Lord, have mercy" 12 times and dismissal. The Lord's feast Midnight Office would be: after 1st Trisagion — Troparion of Feast, after 2nd Trisagion — Kontakion of Feast, then "Lord, have mercy" 12 times, and dismissal. No "Remember" prayer. So "Prayer of St. Mardarius" might be a reference to the prayer "O Master, God the Father Almighty..."? Actually, "Prayer of St. Mardarius" is a monastic daily midnight office prayer. In the Dolnytsky Typikon, the Midnight Office on feasts is slightly different. The digest's mention of "Prayer of St. Mardarius" might be for the normal daily Midnight Office but for feasts they would omit the prayer for the dead and use "Lord, have mercy" 12. However, the digest includes "Prayer of St. Mardarius" which is a different prayer, maybe not the usual one. Let's check the glossary/notes: there is no mention. The standard Daily Midnight Office after "Lord, have mercy" 12 times, the Priest says the prayer "Remember, O Lord" (if no feast) or, if it's a feast, they omit that prayer and instead say "Lord, have mercy" 12 times and then dismissal. But the digest says "Prayer of St. Mardarius" - maybe it's a reference to a specific prayer but it's not part of the standard Dolnytsky Midnight Office. The expected is that the Midnight Office follows the usual pattern but with feast troparion and kontakion, and no prayer for the dead, just "Lord, have mercy" 12 times, dismissal. So "Prayer of St. Mardarius" might be a database artifact from the Horologion that is not applicable here, or it could be an incorrect insertion. I'll flag it as a potential gap, need to verify: In the Midnight Office on feasts without Vigil, according to footnote 341, it says: "At Midnight Office, after the 1st Trisagion -- Troparion of the Feast; after the 2nd -- Kontakion of the Feast; we do not say the prayer 'Remember', but 'Lord, have mercy' (12) and dismissal." So there is no "Prayer of St. Mardarius". The digest should say "Lord, have mercy" (12) and dismissal, not "Prayer of St. Mardarius". This is a compliance gap.

At Matins: "At The Lord is God… we sing: Troparion of the feast, twice; Glory. Troparion of Apostles Bartholomew and Barnabas, once; Both now. Troparion of the feast, once." The ground truth says: Troparion of the feast, twice; Glory... Troparion of the Saint; Both now... Troparion of the Feast. Yes, that is the pattern for a Saint with Polyeleos in the middle of a feast: feast troparion twice, Glory: Saint, Both now: feast. So correct.

Kathismata: "We read Kathismata 10 and 11." For Great Matins on a weekday, the usual number of kathismata is two. So Kathismata 10 and 11 are correct (Thursday, ordinary time). Good.

After Kathismata: "After the Kathismata (10 & 11): We sing: after the 1st (10): Small Litany, then we sing the Sessional Hymns from the Triodion; after the 2nd (11): Small Litany, then we sing the Sessional Hymns from the Triodion." For Polyeleos saint, after the kathismata, the sessional hymns are from the Menaion (feast and saint) not just Triodion? Actually, in the context of Apodosis of a feast, the Sessional Hymns after kathismata at Matins are of the Feast (from Triodion) and Saint. But the resolved variables might indicate that. The digest simply says "Sessional Hymns from the Triodion" after each kathisma. Is that sufficient? The ground truth: "After the Kathismata, Small Litany, then Sessional Hymns from the Triodion" – since the feast is Apodosis, the Triodion includes the feast's sessional hymns. Usually on a Polyeleos, after the second kathisma, there is the Polyeleos. The digest mentions "We sing the Polyeleos" after the sessional hymns. That's correct.

Polyeleos: "We sing the Polyeleos. Anabathmoi (Hymns of Ascents): Anabathmoi Tone Antiphon 4:1. Gradual (Anabathmoi): Antiphon Tone 1:4." This seems odd. The Anabathmoi (Gradual) are the Hymns of Ascent, sung after the Polyeleos, before the Gospel. Usually for a Polyeleos feast, the Gradual is in Tone 4 of the week? Actually, the Typikon for Polyeleos saints: if the saint is celebrated, the Gradual is from the 4th Tone, first antiphon ("From my youth..."), and the Prokeimenon is in the tone of the week? The Glossary "Polyeleos Feasts (Greek and Slavic Rubrics)" doesn't specify. But the general rule for Polyeleos saint days: The Prokeimenon of Matins is in the tone of the Octoechos of the day (which is Tone I, because the tone of the week is I after Pentecost? Today Thursday, tone of the week is 1). So Prokeimenon should be Tone I. The digest says "Arise, Lord, help us, and redeem us for Thy mercy's sake (Tone I)". That is correct for Thursday in Tone I? Actually, the Prokeimenon for Matins on Thursday in Tone I is "Arise, Lord, help us..." Yes. So fine.

But for the Gradual (Anabathmoi), the rubric for Polyeleos saint: "After the Polyeleos, we sing the Gradual Antiphon of the 4th Tone: 'From my youth...'" (not the tone of the day). This is a standard rule: for saints with Polyeleos or Doxology (not a Sunday), the Gradual is always from Tone 4, first antiphon. Not the tone of the day. So the expected Gradual is from Tone 4, first antiphon. The digest says "Anabathmoi Tone Antiphon 4:1" and "Gradual (Anabathmoi): Antiphon Tone 1:4." It's confused. The digest first gives "Anabathmoi Tone Antiphon 4:1" which might mean the Gradual in Tone 4, Antiphon 1. Then it gives "Gradual (Anabathmoi): Antiphon Tone 1:4" which seems contradictory (Tone 1:4?). The correct is simply the Gradual Antiphon in Tone 4, first antiphon. The duplication may be a database artifact. The "Anabathmoi Tone Antiphon 4:1" might refer to the Tone, and "Gradual: Antiphon Tone 1:4" might be something else? No. So there is an error: The Gradual should be "The Gradual, Tone 4: 'From my youth many passions war against me...'" without mentioning Tone 1. The digest's both mentions might be garbled. So we note a gap.

Prokeimenon of Matins: correct.

Matins Gospel: "Gospel to Apostles Bartholomew and Barnabas: Luke 10:16-21." The ground truth says Matins Gospel is for the Saint. So correct. (The Feast of the Eucharist does not have a special Matins Gospel; for Apodosis of a feast, if there is no Gospel of the feast, we read the Saint's Gospel, but the feast's Apodosis might also have a Gospel? The Triodion may have a Gospel for Saturday vespers etc. But at Matins, the Gospel is of the Saint. Good.)

At the Canon: "Full order of the canon (according to the typicon): Triodion - 10 (including the heirmos), Menaion - 4." The resolved canon distribution: Feast (Triodion) on 10, Saint on 4, total 14. That matches the ground truth: "Feast - 4 (from Triodion) and Saint - 4 (from Menaion)"? Wait, ground truth: "Beatitudes: Feast - 4 (from Triodion) and Saint - 4 (from Menaion). " That's for Beatitudes. Canon: The ground truth says "Feast - 10 (including heirmos) and Saint - 4." Actually the context variable says matins_canon_distribution: feast 10, saint 4. So that's fine.

Katavasia: "The bread of heaven He gave them" (Tone V). That seems to be a Katavasia of the Eucharist feast. The Triodion's Katavasia for the Eucharist might be that. Correct.

At Ode 8: "At Ode 8 (Glory): 'Let us bless the Father, and the Son, and the Holy Spirit, the Lord.'" This is correct for any time.

At Ode IX: "we sing the Festal magnification and the Heirmos of Ode IX of the Feast." Then "It is truly meet (Axion Estin)." For a feast of the Lord, the usual is that at the 9th Ode, instead of "More honorable," we sing the Magnification and then the Heirmos of the 9th Ode (or the Katavasia). So "Festal magnification" is appropriate. Then after the Katavasia, "It is truly meet" is sung. That is correct.

Exapostilarion: "Exapostilarion of the Feast; Exapostilarion of Apostles Bartholomew and Barnabas; Theotokion of the Feast." For Polyeleos saint with feast, after the canon, Exaposteilarion: of the Feast, then of the Saint, then Theotokion of the Feast (or of the saint?). The pattern: Feast Exaposteilarion, Saint Exaposteilarion, then Both now: Theotokion of the Feast (or the Theotokion of the Saint if from Sunday Exaposteilaria?). The glossary (Canon Structure) says: "When several services coincide, each with its own Sessional Hymn, Kontakion-Ikos and Exaposteilarion, then they are taken one after another, according to the order of services... The sequence of Sessional Hymns and Exaposteilaria in the middle of a Feast of the Lord and of the Theotokos ends with the Sessional Hymn or Exaposteilarion of the Feast." So after the 9th Ode: Exaposteilarion of the Feast, then of the Saint, then Theotokion of the Feast (i.e., the feast's Theotokion). So it says Theotokion of the Feast. The digest says "Theotokion of the Feast." Good.

At the Praises: "we sing 6 Stichera: 3 from the Triodion, and 3 from the Menaion; Glory... Doxastikon of the Saint; Both now: Theotokion of the Feast." The ground truth says same.

Doxology: Great Doxology (sung). Correct.

"At the Dismissal Troparia: We sing: Troparion of Bartholomew Barnabas in Tone I; Glory, Both now: Troparion of the Feast in Tone VIII." That's the pattern after the Great Doxology? Usually after the Doxology, the troparion of the day is sung. For a Polyeleos saint in a feast, after the Great Doxology, the troparion of the feast is sung, or the saint? The order: after the Doxology, the troparion is of the feast (or saint?), but the ground truth says: "At the Dismissal Troparia (i.e., after the Doxology): Troparion of the Saint, Glory, Both now: Troparion of the Feast." That's what the digest says? It says "Troparion of Bartholomew Barnabas in Tone I; Glory, Both now: Troparion of the Feast in Tone VIII." So yes, Saint then Both now: Feast. That's fine.

At the Hours: "At the First and Sixth Hours: Troparion of the feast; At the Third and Ninth Hours: Troparion of Apostles Bartholomew and Barnabas. Kontakia: at the First and Sixth Hours – Kontakion of the Eucharist; at the Third and Ninth Hours – Kontakion of Apostles Bartholomew and Barnabas." According to the Glossary "Sunday Troparia and Kontakia at the Liturgical Hours" footnote 65, the pattern: at all Hours, the troparion of the feast (or Sunday) is the primary; the Saint's troparion is alternated with Glory... But the digest assigns feast troparion to 1st and 6th, and Saint to 3rd and 9th. That's consistent with Slavic Typikon, where the feast troparion is said at all Hours, and Glory: at 1st and 6th — the feast? Actually, the rule for a feast of the Lord with a saint: at the Hours, the Troparion of the Feast is said at all Hours; Glory: at the 1st and 6th Hours, the Troparion of the Saint (if he has one) is said, at the 3rd and 9th, the Troparion of the second saint (if there is one) but here only one saint. So the digest's distribution is correct: the feast troparion is always the primary; Glory at 1st and 6th — the Saint's troparion; at 3rd and 9th — also the Saint? Actually, the note says: "At all [Hours], the Sunday Troparion, and the Kontakion is of the feast." For a Sunday with saint, but for a feast of the Lord without Sunday, the rule is similar: the Troparion of the Feast is at all Hours; then Glory: at 1st and 6th — the Troparion of the Saint (if one), at 3rd and 9th — also of the Saint (if only one). So the digest's arrangement: 1st & 6th: Troparion of the feast; 3rd & 9th: Troparion of the Saint — that is correct, and Glory alternates? Actually, the digest says "At the First and Sixth Hours: Troparion of the feast; At the Third and Ninth Hours: Troparion of Apostles Bartholomew and Barnabas." That might mean the troparion that is said after "Glory"? Wait, the typical format: after the Trisagion, we say the Kontakion of the feast, but for Hours, the Troparion and Kontakion are placed: "Troparion of the Feast, Glory... Troparion of the Saint, Both now... Theotokion." For a feast of the Lord, the whole Troparion sequence is: Troparion of the Feast; Glory: Troparion of the Saint; Both now: Theotokion of the Hour (or of the feast). But at the Hours, the Kontakion is only the feast's. So the digest's listing "Troparion of the feast" at 1st and 6th and "Troparion of the Saint" at 3rd and 9th could be misinterpreted. However, the Typical practice for a feast with saint: at the 1st Hour: Troparion of the Feast, Glory: Troparion of the Saint; at the 3rd Hour: Troparion of the Feast, Glory: Troparion of the Saint (or the second saint). But the digest simply says "At the First and Sixth Hours: Troparion of the feast; At the Third and Ninth Hours: Troparion of Apostles Bartholomew and Barnabas." This is ambiguous and not strictly according to Dolnytsky. The correct is: at all Hours, the Troparion of the Feast is sung; after "Glory", the Troparion of the Saint (if one saint) is sung at the 1st and 6th Hours, and at the 3rd and 9th Hours also the Troparion of the Saint (if there is only one saint). So it's the same sequence each Hour: Troparion of the Feast; Glory: Troparion of Saint; Both now: Theotokion. The digest's attempt to alternate is not the standard for a feast of Lord with a single Polyeleos saint. The proper rule: at all Hours, Troparion of the Feast; Glory: (Troparion of Saint) at 1st and 6th, and (if only one saint) also at 3rd and 9th? Actually, footnote 65: "According to the ancient typikon there was to be a Sunday troparion at all hours, also 'Glory' at the 1st and 6th -- Goes also to the first saint, at the 3rd and 9th -- to the second; Kontakia -- alternating: at the 1st and 6th -- to the first, at the 3rd and 9th -- to the second saint." If there is only one saint, the Sunday Troparion (or Feast Troparion) is at all hours, and the Saint's Troparion is at both 1st/6th and 3rd/9th? "When the Kontakion is only for one saint, then it alone is taken at all [hours]; and when for neither, nor for the feast, then the Hypakoe of the tone is taken." Actually, that refers to Sunday. For a feast of the Lord, the troparion of the feast is at all hours. The saint's troparion is alternated: at 1st and 6th, after "Glory" the saint's troparion; at 3rd and 9th, after "Glory" also the saint's troparion (since only one). So the digest's separation of "First and Sixth: Troparion of the feast" and "Third and Ninth: Troparion of Apostles..." is wrong because it omits the feast troparion at 3rd and 9th. The correct: all Hours have Troparion of the Feast. Then at all Hours, after "Glory", the Troparion of the Saint (if only one) is sung. So I'll note this gap.

Kontakia: "at the First and Sixth Hours – Kontakion of the Eucharist; at the Third and Ninth Hours – Kontakion of Apostles Bartholomew and Barnabas." That's the rule for Sunday with two saints? The note says for a Sunday with two saints, the Kontakia alternate. For a feast of the Lord with a saint, the Kontakion at all Hours is the feast's Kontakion? Actually, the general rule for a feast: at Hours, the Kontakion is of the feast (since it's a Lord's feast). The saint's Kontakion is not used at the Hours because the feast's Kontakion reigns. The digest giving alternating Kontakia is incorrect. So I'll flag that as a gap.

Liturgy section: "Psalms of Typica; Beatitudes on 8: Triodion - 4, Menaion - 4." Correct.

Troparia and Kontakia at Liturgy: "Troparion of the Feast. Troparion of Apostles Bartholomew and Barnabas. Glory... Kontakion of Apostles Bartholomew and Barnabas. Both now: Kontakion of the Feast." The order: After the Entrance, the troparia and kontakia sequence: Troparion of the Feast; Troparion of the Saint; Glory... Kontakion of the Saint; Both now: Kontakion of the Feast. This is correct.

Prokeimena: "Prokeimenon (Feast - sung twice): Tone VI: 'O Lord, save Your people and bless Your inheritance'. Prokeimenon (Saint - sung once, without verse): Tone VIII: 'Their proclamation...'". The ground truth said first Feast Tone VI, second Saint Tone VIII. The feast Prokeimenon is sung twice (with verse), the saint's once without verse. That matches Dolnytsky's rule for multiple Prokeimena (Part 2 General Rubrics #7). So correct.

Epistle: Romans 8:22-27 and Acts 11:19-26,29-30. That's indeed the readings: first Epistle of the day (Thursday after Pentecost 3rd week? Actually, the ground truth says "Epistle: Romans 8:22-27" (day) and "Acts 11:19-26, 29-30" (Saint). So correct.

Alleluias: "Tone VI, with verses: 'He who eats My flesh...' Tone I, with verses: 'The heavens shall confess...'". Yes.

Gospel: Matthew 10:23-31 and Luke 10:16-21. Correct.

Communion Hymn: "Receive the Body of Christ; taste the fountain of immortality. And of the Saint: Their sound hath gone forth..." The Communion Hymn for the feast (Eucharist) is "Receive the Body of Christ...", and for the Saint "Their sound...". Combined, as per ground truth, "Communion Hymns: Combined (Feast & Saint)." The digest has them together in one line, okay.

Post-Communion Hymn: "We have seen the true light..." standard.

Dismissal: "May Christ our true God..." okay.

Now check Quick Reference Digest for same errors. It's condensed but might have similar issues.

Digest: "At Lord, I Call…" same.

"Aposticha: 3 Aposticha Feast from Triodion; Glory... Doxastikon of the Saint; Both now: Theotokion of the Feast." Good.

"At the Dismissal Troparia: Troparion of Apostles Bartholomew and Barnabas; Glory, Both now: Troparion of the Feast." Good.

"At The Lord is God… Troparion of the feast, twice; Glory. Troparion of Apostles Bartholomew and Barnabas, once; Both now. Troparion of the feast, once." Good.

"After each kathisma: Small Litany, then we sing the Sessional Hymns from the Triodion." Same issue as above? But since the saint is Polyeleos, we might also have sessional hymns from the Menaion. But the ground truth says "from the Triodion". So okay.

"Prokeimenon: Arise, Lord, help us..." correct.

"Matins Gospel: Gospel to Apostles Bartholomew and Barnabas: Luke 10:16-21." Good.

"Canon: Triodion on 10, Saint on 4." Good.

"At each ode: Heirmos from the Feast; troparia with refrains; Glory... Both now." Good.

"After Ode III: Sessional hymns; Glory... Both now: Theotokion." Too generic, but not a gap.

"After Ode VI: Kontakion and Ikos."

"At Ode IX: We sing the Magnification." Good.

"Katavasia: 'The bread of heaven He gave them'."

"Exapostilarion - Saint; Theotokion." It says only Saint and Theotokion, missing Feast Exaposteilarion. But in quick reference they might have omitted. In the first digest they had all three. However, the quick reference says "Exapostilarion - Saint; Theotokion." That is incomplete; they should have Feast Exaposteilarion as well. So a gap.

"At the Praises: 6 Stichera: 3 Triodion, 3 Menaion; Glory... Doxastikon; Both now: Theotokion." Good.

"At the Dismissal Troparia: Troparion of Bartholomew Barnabas in Tone I; Glory, Both now: Troparion of the Feast in Tone VIII." Good.

"At the Hours: At the First and Sixth Hours: Troparion of the feast; At the Third and Ninth Hours: Troparion of Apostles Bartholomew and Barnabas." Same issue as before, gap.

"Kontakia: at the First and Sixth Hours – Kontakion of the Eucharist; at the Third and Ninth Hours – Kontakion of Apostles Bartholomew and Barnabas." Same gap.

Liturgy part similar.

Now need to identify all gaps.

Now also check for terminology compliance: The matrix says reject variants like "Prokimenon", but both use "Prokeimenon" correctly. Check for "Leavetaking"? The digests use "APODOSIS" correctly. In the title "APODOSIS OF THE EUCHARIST", fine. They use "Feast" and "Saint" terms. "Theotokion" used. "Doxastikon" used. "Anabathmoi" used but that's not a canonical term? The matrix lists "Gradual" as canonical, and rejects "Stepenna". The digest uses "Anabathmoi (Hymns of Ascents)" and "Gradual (Anabathmoi)". That's confusing but not a rejected variant. However, canonical is "Gradual". The digest tries to keep both. But the glossary's note: "Gradual is the canonical term; Stepenna is a rejected variant." The digest says "Anabathmoi (Hymns of Ascents): Anabathmoi Tone Antiphon 4:1. Gradual (Anabathmoi): Antiphon Tone 1:4." That is messy. I'd flag that the liturgical heading should be simply "Gradual" or "The Gradual Hymns (Anabathmoi)". But the actual content is arguably a compliance issue: the second line "Gradual (Anabathmoi): Antiphon Tone 1:4" suggests a wrong tone. I'll categorize under formatting/database artifacts.

Next, the mention of "Prayer of St. Mardarius" at Midnight Office – that is a non-canonical insertion. It should be "Lord, have mercy (12)" and dismissal. So a gap.

Also, the Quick Reference "Exapostilarion - Saint; Theotokion." is missing the Feast Exaposteilarion. Gap.

Now regarding the "Glory... Both now: Theotokion" pattern in Sessional Hymns and Exaposteilaria: the full digest gave full order, good.

Now, check the Precedence / Combination Rules: The combination of Apodosis of Eucharist with Polyeleos Saint – is the order of troparia at Liturgy correct? According to the general rule, the feast's Troparion first, then the Saint's, Glory: Kontakion of Saint, Both now: Kontakion of Feast. That is correct. The ground truth confirms that. No issue.

But note: The Apodosis of the Eucharist is a feast of the Lord, and at the Liturgy, instead of the Trisagion there is "Before Thy Cross" only on the Exaltation and Veneration of Cross, but not on Eucharist. So Trisagion is normal.

Now, the digest includes "Vestments (priest): epitrachelion, phelonion. The phelonion is blessed and kissed before the Entrance." That might be a local custom but not a gap.

Now, the Feast's Katavasia "The bread of heaven He gave them" is from the Eucharist Triodion. Good.

Now, one more:

---

## AUDIT REPORT:

*(No content returned, showing reasoning process above)*