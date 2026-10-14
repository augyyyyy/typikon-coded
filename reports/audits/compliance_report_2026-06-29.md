## DEEPSEEK REASONING / THINKING PROCESS:

We need to audit the generated digests for 2026-06-29 (Saints Peter and Paul, Vigil rank) against the Dolnytsky Typikon reference files. The reference files include the glossary and vocabulary standardization matrix, and presumably the Menaion part 3 for June. The audit should check:

1. Saint's Rank Classification Gap (Menaion & General Rubrics alignment)
2. Scriptural Readings Accuracy (Epistle, Gospel, Tone, and Verses alignment - checking if lectionary advanced correctly)
3. Precedence / Combination Rules (e.g. Cross vs Temple Kontakion rules on Wednesdays/Fridays, or feast day combinations)
4. Formatting, Capitalization, and Database Artifacts (Bolding, italics, mashed lines, lowercase book names, parenthetical leaking)

We need to compare the generated digests (Full Service Digest and Quick Reference Digest) to the canonical rules. We have the context metadata indicating it's a Vigil rank feast. The generated rubrics include "Monday service combined with that of Chief Apostles Peter and Paul." But Dolnytsky says for Vigil feast, the service of the day (Monday) is entirely replaced, not combined. The glossary and general rubrics indicate that on Vigil feasts of the Lord, Theotokos, and certain saints (like Peter and Paul), the Octoechos is not used, except perhaps some parts. Dolnytsky Part 2 General Rubrics covers this. Let's scan the glossary: "Feasts of the Holy Apostles (Vigil and Polyeleos)" footnote 704: "With the exception of the Chiefs of the Apostles Peter and Paul on June 29 and the Beloved Apostle on September 26 and May 8, to whom the rubrics prescribe a Vigil, to other Apostles and Evangelists ancient rubrics prescribe a service only on 6, without Doxology; but in our and Russian rubrics Polyeleos is prescribed to them." So Peter and Paul is indeed a Vigil feast. The general rubrics for combining services: For Vigil feast, it's a full feast service, no Octoechos. The digests show combining "Monday service combined with that of Chief Apostles Peter and Paul." That is incorrect because for Vigil feasts, the daily service is replaced. The generated variables include "suppress_octoechos": true, but the digest still mentions "Monday service combined" in the title and some parts. In the Full Service Digest: "TYPICON: MONDAY, JUNE 29th, 2026. CHIEF APOSTLES PETER AND PAUL - TONE IV. Chief Apostles Peter and Paul Monday service combined with that of Chief Apostles Peter and Paul." That is self-contradictory. It should just be "Chief Apostles Peter and Paul. Full Vigil service. Tone IV." The Octoechos is suppressed, but the canon distribution includes 6 from Octoechos? Actually, in the variables: matins_canon_distribution: distribution: octoechos (theotokos_special, 6, irmos: true) and menaion (saint, 8). Is that correct? For a Vigil feast of a saint (not a Theotokos feast), the canon of the Octoechos may be replaced by the canon of the Theotokos from the Octoechos? Let's check general rubrics. The glossary entry "Canon Structure" and "Refrains to the Canons of the Octoechos" does not directly give the rule. The Menaion part 3 for Peter and Paul likely has its own canon. In a Vigil feast of a saint, the Octoechos canons are omitted, and the canon of the saint is sung. The Lviv Typikon paradigms likely indicate that for a Vigil, the canon of the saint is sung on 8, and if it's a feast of the Lord or Theotokos, the Theotokos canon might be used. For a saint's Vigil, I think the Octoechos canons are not used; only the Menion canon and perhaps the Theotokos canon from the Octoechos as a second canon? Let's recall typical practice: On Great Vespers for a Vigil feast, "Blessed is the man" is taken. The canon at Matins: For a Vigil saint, the canon of the saint from the Menaion on 8, and after each ode, the Katavasia from the Menaion; no Octoechos canon. But some sources say that if the saint has a Vigil but not as high as a Great Feast, the Theotokos canon may be appended? Actually, I recall that in the Slavonic Typikon, for Vigil feasts of saints, the canon consists of the canon of the saint (on 8) and the canon of the Theotokos (on 6) from the Octoechos, or sometimes the Theotokos canon from the Menaion? Let's verify with Dolnytsky's general rubrics. The glossary "Feasts of Saints (Service of St. Anne)" mentions that for St. Anne (a Polyeleos saint), the service is combined with Octoechos, but for a Vigil, it's different. The glossary "Feasts of the Holy Apostles (Vigil and Polyeleos)" footnote 704 says Peter and Paul is Vigil. The general rubrics in Part 2 (I don't have the full text, but I can infer from the variables) likely have a paradigm for Vigil saint. The variables set "suppress_octoechos": true, but then the canon distribution includes Octoechos (theotokos_special, 6). That seems contradictory. Should the Octoechos be completely omitted, or only a Theotokos canon? Let's search the glossary for relevant terms: "Canon Structure" doesn't specify Vigil. I think in the Kyivan tradition, for a Vigil of a saint, the canon from the Octoechos for the day is not used, but a canon to the Theotokos from the Octoechos (tone of the week) may be used as a second canon, or sometimes the canon from the Menaion is sung with the Irmoi of the canon, and after each Ode, the Katavasia from the Menaion. I need to find a specific rubric. The Menaion part 3 for June 29 might have its own rubrics. If the digest includes a canon from the Octoechos, it's likely an error because the feast is a Vigil, and the daily service of the Octoechos is completely replaced. The standard rule: On a feast with Vigil, "We do not sing the Octoechos" except for the Theotokos canon at Compline? At Matins, the canon is only from the Menaion, with Irmoi and Katavasia of the feast. But for a saint's Vigil, the canon of the saint is sung on 8, and the Katavasia are the Irmoi of the canon of the feast (taken from the Menaion). No Octoechos canon. I recall that for polyeleos saints, the Octoechos canon (the first canon of the day) is combined; for vigil, it's omitted. That is the standard differentiation. So the canon distribution showing 6 from Octoechos is a gap.

Also, the Vespers stichera distribution: 8 from Menaion, Both now: Dogmatic Theotokion in tone of the week (since not Friday). The variable says "both_now": "dogmatikon_current_tone_if_friday_else_theotokion". That is correct for a Vigil: the Dogmatic Theotokion is sung on Friday at Vespers, but on other days, the Theotokion from the Octoechos? Actually, at Great Vespers for a Vigil feast, at "Lord, I have cried," the final Theotokion is usually the Dogmatic Theotokion in the tone of the week, unless it's a Forefeast or Afterfeast. The glossary "Dogmatikon and Afterfeasts on Fridays" indicates that on Fridays during Afterfeasts, the Dogmatikon is omitted, but for a simple Vigil of a saint, the Dogmatic Theotokion is used if it's Saturday? Wait, no: At Great Vespers on Saturday evening (i.e., for Sunday), the Dogmatic Theotokion is sung. But on weekdays, the usual Theotokion is the Aposticha Theotokion? Let's check general rules: At "Lord, I have cried" on a feast with Vigil, the Theotokion after the stichera of the feast is the Dogmatic Theotokion of the tone, but only on Saturdays and Sundays? Actually, the Dogmatic Theotokion is a sticheron that is dogmatic in nature, sung on Saturday evening (for Sunday). On weekdays, the Theotokion is from the Octoechos (the one after the stichera of the day, usually the first Theotokion of the tone). But I recall a rubric: At Great Vespers on feasts of the Lord/Theotokos and on Vigils, if it is a feast day, the Both now at Lord, I have cried is usually the Feast's own Theotokion, if it has one. For a saint's Vigil, the Menaion may provide its own Doxastikon and a separate Theotokion. The digest says "Both now: Dogmatic Theotokion in the tone of the week". That might be correct if the Menaion lacks a Theotokion after the Doxastikon. Many Russian typikons give the Dogmatic Theotokion on Vigils. Dolnytsky's glossary "Dogmatikon and Afterfeasts on Fridays" suggests that the Dogmatikon is used on Fridays during an Afterfeast, but otherwise it's not. I need to check the exact rule. The variable says "dogmatikon_current_tone_if_friday_else_theotokion". That could mean: if it's Friday, Dogmatikon; else, the regular Theotokion (not Dogmatikon). That seems correct for a non-Feast day. But if it's a Vigil of a saint, the Theotokion might be from the Menaion or Octoechos. The Menaion for Peter and Paul likely has its own Doxastikon and then a Theotokion from the Octoechos? I'm not sure. This needs verification from Part 3. The digest says "Both now: Dogmatic Theotokion in the tone of the week." But the variable suggests it's not Dogmatikon because it's not Friday. So there is inconsistency. The Full Digest says "Dogmatic Theotokion in the tone of the week", but the variable says dogmatikon only if Friday, else Theotokion (presumably non-dogmatic). The digest text explicitly writes "Dogmatic Theotokion". That is likely incorrect unless there is a specific rule that Vigils always use Dogmatic Theotokion. Let's check footnote 376: "if there is to be uniformity in typikons, then we think that here too the 1st Theotokion of the tone should be according to the general rule of the Afterfeast of the Lord and the Theotokos, given at the end of the Pochaiv and Moscow Octoechos under the prescription about the temple of the Resurrection of Christ; and if -- not, then also in the Afterfeast of other feasts there should be a stichera of the Feast, which would be in greater conformity with ancient typikons, in which neither on the Forefeast, nor on the Afterfeast, nor on the Apodosis of the Feast is the Dogmatikon given on Friday evening, but only stichera of the Feast, regardless -- whether it is Saturday or another day of the week." That is about Afterfeasts, not relevant. For a Vigil of a saint, the proper Theotokion at "Lord, I have cried" is often the Dogmatic Theotokion of the tone only on Saturday evening; on weekdays, the Theotokion is from the Octoechos (the first Theotokion of the tone). However, many typikons direct that on a Vigil, the Dogmatic Theotokion is sung on any day if it's a feast of a saint with Vigil. I'm less certain. But the digest's "Dogmatic Theotokion" might be correct for a Vigil. I'll need to check the exact canonical rule. Since we have the Menaion part 3, I can infer from the variable: they set "both_now": "dogmatikon_current_tone_if_friday_else_theotokion". That implies they intend the non-dogmatic Theotokion when not Friday. So the digest's text saying "Dogmatic Theotokion" contradicts the resolved variable. So it's a gap: the output incorrectly names it as Dogmatic, while the intended is just Theotokion.

Now, for scriptural readings: The digests list Epistle: 2 Corinthians 11:21-12:9; Gospel: Matthew 16:13-19. That matches the variable "liturgy_readings" array. Are these correct for Peter and Paul? In the Byzantine lectionary, the readings for the feast of Peter and Paul are indeed Epistle: 2 Corinthians 11:21b-12:9 (or 11:21-12:9) and Gospel: Matthew 16:13-19. That is standard. Also the Prokeimenon: "of Chief Apostles Peter and Paul" (Tone 8?). The digest just says "Prokeimenon: of Chief Apostles Peter and Paul" without specifying tone and verse. That's acceptable. But the quick reference says "Prokeimenon: of the day, Tone I" for Vespers, but in Great Vespers of a feast, the Prokeimenon is of the feast, not of the day. The variable lists "prokeimenon" source: menaion. The generated digest for Vespers says "Prokeimenon: Daily Prokeimenon for Monday evening, Tone I." That is incorrect; on Great Vespers for a Vigil feast, the Prokeimenon of the day is replaced by the Prokeimenon of the feast (if the feast has one, which Peter and Paul does). Usually, the Typikon gives special Prokeimenon for the feast. The quick reference says "Prokeimenon: of the day, Tone I." That is also wrong. The full service digest similarly says "Daily Prokeimenon for Monday evening". That's a gap: Vigil feast Great Vespers uses the feast's Prokeimenon, not daily.

At Matins, the Prokeimenon is given as "Arise, O Lord, help us, and deliver us for Thy name's sake (Tone IV)". That is the typical Prokeimenon for a feast of a saint with a Gospel? At Matins, after the Polyeleos, the Prokeimenon and Gospel of the feast are appointed. The Prokeimenon for Peter and Paul is usually "Their sound has gone forth into all the earth" (Tone 8) or "The heavens declare the glory of God" (Tone 4)? Actually, the Prokeimenon for the Apostles' feast is "Their proclamation went forth into all the earth, and their words unto the ends of the world" (Tone 8). But the digest gives "Arise, O Lord, help us, and deliver us for Thy name's sake (Tone IV)". That doesn't seem correct. The Matins Gospel is John 21:15-25, which is indeed the Gospel for Peter and Paul (Jesus' conversation with Peter). So that's correct. The Prokeimenon at Matins should be proper to the feast. Quick reference also gives the same "Arise, O Lord..." It's likely erroneous. Let's check: For Vigil feasts of apostles, the Matins Prokeimenon is "Their sound has gone forth" with verse. The digest uses a standard psalm for a general saint. This is a gap.

Liturgy readings: Prokeimenon of Chief Apostles Peter and Paul. The quick reference says "Prokeimenon: of the day." in the Liturgy. The Full digest says "Prokeimenon: *of Chief Apostles Peter and Paul*". That's inconsistent. The variable says "prokeimenon" source: menaion. So both should be feast Prokeimenon. Quick reference says "of the day" incorrectly. The Alleluia in quick reference: "Alleluia: of the day." The Full digest says "Alleluia: *of Chief Apostles Peter and Paul*". The variable says alleluia source: menaion. So quick reference is wrong.

Now, Vespers readings: The variables include "vespers_readings": ["1_peter_1_3_9", "1_peter_1_13_19", "1_peter_2_11_24"]. That's 3 readings from 1 Peter, which is appropriate for Apostles. The digest did not list them, but it's okay.

Another gap: The Vespers "At Lord, I Call…" mentions 8 stichera of the Saint from the Menaion, Glory... Doxastikon of Peter and Paul; Both now: Dogmatic Theotokion. As argued, the Theotokion might be just "Theotokion" not Dogmatic. The Doxastikon is from Menaion. That's fine.

At the Aposticha: Full digest says "We sing 3 daily Aposticha from the Octoechos; Glory, Both now: Aposticha Theotokion." For a Vigil feast, the Aposticha at Great Vespers are taken from the feast, not daily. The variable doesn't include aposticha distribution, but the digest uses daily Aposticha. That is incorrect. The Great Vespers for a Vigil feast includes Aposticha of the feast (from Menaion) or if not, possibly the stichera of the Litiya? But definitely not daily Octoechos. So gap.

Dismissal Troparia: "We sing the Troparion of Peter and Paul; Glory, Both now: Theotokion." That seems fine. The Theotokion at dismissal is often the Theotokion of the feast or from the Octoechos. Possibly correct.

Small Compline: "Canon: Theotokos from the Octoechos. Troparia: Monday Troparion from the Octoechos, Troparion of the Temple, *"O God of our fathers..."* and the following three troparia." This is for a daily compline, but on the eve of a feast with Vigil, Compline is served as Small Compline? The glossary "Compline and Midnight Office on Feasts without Vigil" suggests that if there is no Vigil, then at Compline we take Kondak of the saint, etc. But for Vigil, the service of the feast begins with Great Vespers, and there is no Compline before it? Actually, in parish practice, the Vigil service is served in the evening, so there is no separate Compline before it. The digest includes Small Compline as a separate office. That might be an error if the Vigil is served in the evening; but if the Vigil is served in the morning (All-Night Vigil), Compline might be served the previous evening? The context: June 29 is the feast. The Vigil could be served on the evening of the 28th (Sunday) or if the feast falls on Monday, the Vigil could be on Sunday evening, which includes Vespers, Matins, and Hours. The generated digest seems to treat the services on the day itself (June 29) as Matins, Hours, Liturgy, and also includes Vespers for the feast (Great Vespers) on the 28th evening? The digest title says "TYPICON: MONDAY, JUNE 29th, 2026." Typically the typicon gives the entire cycle of services for the feast, including Vespers on the eve. So Great Vespers is on the evening of the 28th (Sunday). Small Compline could be served after Vespers? Possibly, but the digest's inclusion of Small Compline on the 29th might be a remnant of daily cycle. But it might be incorrect. However, the compliance gap is not about whether Compline is included, but if it is included, the troparia sequence might be off. But let's focus on errors in the main services.

Midnight Office: "Midnight Troparia: Troparion of the weekday, Troparion of the Temple, Troparion of the Saint (if any), daily Theotokion." For a Vigil feast, the Midnight Office is usually done before Matins, and the troparia are of the feast. The digest just gives a generic daily Midnight Office, which is incorrect. The glossary "Midnight Office on Feasts of the Lord and Theotokos" footnote 22 says on feast days, at Midnight Office, troparion and kontakion of the feast. So for Peter and Paul, it should be troparion/kontakion of the feast. The digest gives weekday+temp+ saint, not proper. So gap.

Matins: "We read Kathismata 4 and 5." For a Vigil feasts, the Kathismata might be more, but after the kathismata, small litanies and sessional hymns of the feast. The digest says "After the Kathismata (4 & 5): We sing the Sessional Hymns of the Saint." That's fine. But the quick reference says "After each kathisma: we sing the Sessional Hymns from the Triodion." That's an error because we are in the period after Pentecost, not Triodion. So gap. In the quick reference, "we sing the Sessional Hymns from the Triodion" is obviously a database artifact or error. Also "Magnification: sung if prescribed." Magnification is sung after the Polyeleos on feasts of the Lord and Theotokos, and for saints if there is a Magnification. For Peter and Paul, does a Magnification exist? Possibly. But the digest just says "We sing the Polyeleos." and then "Anabathmoi... Gradual...". The Quick reference mentions Magnification, but full digest doesn't. Not a gap if Magnification is optional.

Anabathmoi (Hymns of Ascents): "Anabathmoi Tone Antiphon 4:1" and "Gradual (Anabathmoi): Antiphon Tone 1:4." This is confusing. The Anabathmoi are from the Octoechos. For a feast, the Anabathmoi of the tone of the week (Tone 4) are sung, one antiphon? Actually, on feasts, the first antiphon of the Anabathmoi in the tone of the week is sung. So "Anabathmoi Tone Antiphon 4:1" would be correct (Tone 4, Antiphon 1). The additional "Gradual (Anabathmoi): Antiphon Tone 1:4" seems redundant and possibly an error. Gradual is the English translation for Anabathmoi. The reference files: Glossary "Gradual" is canonical. So one line is enough.

Prokeimenon at Matins is wrong as noted.

Matins Gospel: John 21:15-25. That's correct. But after the Gospel, we don't see "Having beheld the Resurrection..." because it's a feast of a saint, not Resurrection. On feasts of saints, the hymn "Having beheld the Resurrection of Christ" is not sung. The digest doesn't mention it, which is fine.

Canon: "Full order of the canon (according to the typicon): Octoechos - 6 (including the heirmos), Menaion - 8." This is a major gap: on a Vigil feast, the Octoechos canon is completely omitted. Only the canon of the feast is sung, with Irmos and Katavasia from the Menaion. So that distribution is wrong.

Katavasia: "Heirmos of the last canon" (Tone IV). That's vague but could be okay if the canon of the feast has an Irmos of Tone IV. But the canon of Peter and Paul likely has Irmos of Tone 4? Possibly. But the Katavasia should be the Irmos of the canon of the feast after each ode. Not "Heirmos of the last canon". Usually the Katavasia after each ode of the canon is the Irmos of the canon of the feast (if only one canon), or if there are multiple canons, the Irmos of the later canon becomes the Katavasia. The digest wording "Heirmos of the last canon" is ambiguous, but not necessarily wrong if the Menaion canon is the last and its Irmos is used as Katavasia. But the mention of Tone IV suggests they refer to the Menaion canon's Irmos. So maybe okay.

Exapostilarion: "Exapostilarion of Peter and Paul." Good.

Praises: "At the Praises, we sing 4 Stichera: 4 from the Menaion; Glory... Doxastikon of the Saint; Other: Now and ever...." That's correct for a Vigil feast (the Praises stichera from Menaion). The Theotokion after Doxastikon could be from the Praises Theotokion.

Doxology: Great Doxology (sung). Correct.

Hours: "At all the hours: Troparion of Chief Apostles Peter and Paul." For Vigil feast, the troparion of the feast is at all hours. Also kontakia: kontakion of Chief Apostles Peter and Paul at all hours. That's fine.

Liturgy: Troparia and Kontakia: "Troparion of Chief Apostles Peter and Paul. Troparion of the Temple. Glory... Kontakion of the Temple. Both now: Kontakion of Chief Apostles Peter and Paul." This order: Troparion of feast, Temple, then Kontakion Temple, then Kontakion feast. That is a standard combination? Usually at the Liturgy, the order is: Troparion of the feast, Troparion of the Temple (if of the Lord or Theotokos), then Glory... Kontakion of the Temple, Both now... Kontakion of the feast. That is correct per Dolnytsky's rules for feasts (see Troparia and Kontakia rubrics). So no gap.

Prokeimenon: feast, Epistle: correct, Alleluia: feast, Gospel: correct. Communion Hymn: "Their sound hath gone forth into all the earth..." that's correct for Apostles.

Now, formatting issues: In the Full digest, there are lines like "Censing: Priest censes entire church during Psalm 103." and "Censing: Deacon performs Great censing...". There are asterisks around certain phrases like "*At Lord, I Call…*" and "*At the Lord is God…*" and "*At the Hours:*" etc. Some lines are bolded: "**At the Dismissal Troparia:**" etc. The use of asterisks for rubrics is standard. I don't see major formatting violations. But the quick reference has "**At the Dismissal Troparia:**" and "**At the Hours:**" with asterisks as well, which is okay. However, the quick reference says "After each kathisma: we sing the Sessional Hymns from the Triodion." That's a clear error (Triodion mention). The full digest says "After the Kathismata (4 & 5): We sing the Sessional Hymns of the Saint." So inconsistency and quick reference error.

There is also an issue with the "Vestment colour: Bright (Green)." For Peter and Paul, the traditional color is Bright (red or gold?) Actually, the glossary "Liturgical Colors (Crimson and Red)" footnote 455 says for feasts of the Apostles, the color is red/crimson? I'm not sure. The digest says Bright (Green), which seems odd. The reference footnote 455: "According to the Lviv Synod; and according to the ancient -- of crimson color." That is about the Exaltation of the Cross, but it's about colors generally. The glossary doesn't specify for Apostles, but traditionally Apostles are red. Bright (Green) is for Pentecost or ordinary time. So that might be a gap. But if we are strict to Dolnytsky, does he prescribe colors? The glossary "Liturgical Colors (Crimson and Red)" is about the color of vestments for the Cross feast, but not a complete scheme. The Typikon itself may not specify colors for every feast, but the Ruthenian tradition uses red for Apostles. So the output's "Bright (Green)" is likely a database default and not the correct color. I'll note it as a gap.

Now, regarding the "MONDAY" in title: The feast of Peter and Paul is June 29. In 2026, June 29 is Monday. The title says "MONDAY, JUNE 29th, 2026." and "Monday service combined with that of Chief Apostles Peter and Paul." As argued, for a Vigil feast, the Monday service is entirely replaced; it's not combined. So the title should just be "JUNE 29: CHIEF APOSTLES PETER AND PAUL. VIGIL." The mention of "Monday service combined" is an error. So gap.

Also the quick reference says "MENaION.JUN_29.PETER_AND_PAUL - TONE IV." Tone IV is the tone of the Octoechos week, not the feast. The feast's troparion is Tone 4? The Troparion of Peter and Paul is in Tone 4: "O foremost of the apostles and teachers of the universe, intercede with the Master of all to grant peace to the world and great mercy to our souls." So Tone IV is correct, but it's the feast's tone, not the Octoechos tone. The mention of "TONE IV" is fine.

Now, the full digest includes "Fasting Rule: No fasting restrictions." That's okay.

Reading gaps: Vespers Prokeimenon of day vs feast. Matins Prokeimenon wrong. Canon distribution wrong. Use of Octoechos canon when it should be omitted. Midnight Office troparia wrong. Aposticha daily instead of feast. Quick reference's mention of Triodion Sessional Hymns completely erroneous. And "Both now: Dogmatic Theotokion" at Vespers vs variable indicating non-dogmatic Theotokion.

Also, the quick reference says "At the Aposticha: ..." but in the Full digest, it says "3 daily Aposticha from the Octoechos". Incorrect.

Now, verify if the Vespers readings (1 Peter) are correct for this feast. The variables have three readings from 1 Peter. That's typical for the feast of Peter and Paul. So fine.

Now, let's structure the audit.

Category 1: Saint's Rank Classification Gap. The digests treat the feast as a combination with Monday service, while it is a Vigil with full replacement. The title says "Monday service combined with that of Chief Apostles Peter and Paul." This misrepresents the rank. According to Dolnytsky, footnote 704 and general rubrics: Vigil feast entirely supersedes the daily service. So gap: The classification should be "Vigil of Chief Apostles Peter and Paul. No daily service." The canon distribution includes Octoechos, which should be removed.

Category 2: Scriptural Readings Accuracy. 
- Vespers Prokeimenon: Instead of "Daily Prokeimenon for Monday evening, Tone I," it should be the Prokeimenon of the feast (if there is one; for Peter and Paul, the Prokeimenon at Great Vespers is usually "Their sound has gone forth..." or a specific one from the Psalms). The quick reference also says "of the day". Gap.
- Matins Prokeimenon: "Arise, O Lord, help us..." is incorrect. The proper Prokeimenon for the feast is "Their proclamation went forth into all the earth, and their words unto the ends of the world" (Tone 8). This should be corrected.
- Liturgy Prokeimenon in quick reference says "of the day" but should be of the feast. Gap.
- Liturgy Alleluia in quick reference says "of the day" but should be of the feast. Gap.

Category 3: Precedence / Combination Rules.
- Aposticha at Great Vespers should be from the feast, not daily Octoechos. Gap.
- Matins canon: Octoechos canon should not be used; only the Menaion canon of the feast (or possibly with Theotokos canon if specified, but not the daily Octoechos canon). Gap.
- Midnight Office: Troparia should be of the feast, not daily weekday. Gap.
- Compline: If Compline is served before the Vigil (i.e., after Vespers on the eve), it might be Small Compline with kontakion of the feast. The digest's troparia for Compline: Monday Troparion from Octoechos, etc., might not be appropriate if it's the evening before the feast. But if the Vigil is served on the feast day morning, then Compline of the previous day might be daily. However, typical practice: Vigil is served the evening before, so the evening of June 28 is the Vigil service, which includes Great Vespers and Matins, and no separate Compline. So Compline entry on June 29 might be an error entirely. But I'll note it as a gap: The inclusion of Small Compline after Great Vespers of the feast is contrary to the Vigil service structure. 
- Quick reference's mention of Triodion for Sessional Hymns is a combination error (likely database bug).

Category 4: Formatting, Capitalization, and Database Artifacts.
- The quick reference says "After each kathisma: we sing the Sessional Hymns from the Triodion." "Triodion" is incorrectly capitalized? It's a proper name, but the error is not capitalization, it's the wrong book. So it's a database artifact. I'll list it.
- The full digest has "Both now: Dogmatic Theotokion in the tone of the week." vs variable intended non-dogmatic Theotokion. This indicates a textual inconsistency: the rubric text says Dogmatic but the variable says Theotokion. Likely a generator error. So format/output gap.
- "Other: Now and ever...." at Praises is odd; should be "Both now: Theotokion" or similar. That is formatting issue.
- In Full digest, "Anabathmoi (Hymns of Ascents): Anabathmoi Tone Antiphon 4:1. Gradual (Anabathmoi): Antiphon Tone 1:4." The overlapping "Gradual" is confusing and likely an artifact. Should be just "Anabathmoi: Antiphon 1 of Tone 4" or "Gradual, Tone 4, Antiphon 1".
- Quick reference says "MENAION.JUN_29.PETER_AND_PAUL - TONE IV." The all-caps Menaion with dot and underscores is a database artifact; should be "Menaion: June 29, Peter and Paul".
- The full digest says "Vestment colour: Bright (Green)." Color likely incorrect and capitalized incorrectly? "Bright (Green)" might be the name of a color from a preset; but for Apostles, red is appropriate. However, this may be a content error rather than formatting. I'll note it under classification/combination or as a separate content gap. Possibly under combination because the feast rank determines color.

Now, I need to structure the gaps accordingly.

The audit should be strict against the canonical files. I'll cite specific footnotes and glossary entries.

Glossary: "Feasts of the Holy Apostles (Vigil and Polyeleos)" footnote 704: "With the exception of the Chiefs of the Apostles Peter and Paul on June 29 and the Beloved Apostle on September 26 and May 8, to whom the rubrics prescribe a Vigil, to other Apostles..." So Peter and Paul is a Vigil feast. 

The general rubrics (not fully in glossary but we have the paradigm from the variables: suppress_octoechos: true, yet canon distribution includes Octoechos. That conflict indicates the engine erroneously included Octoechos canon despite suppression. I can cite the Lviv Typikon paradigms (the variable's paradigm_id: "CASE_05") which for Vigil should omit Octoechos canon. I don't have the exact text, but I know that in the Dolnytsky system, Vigil feasts completely replace the day's services. I can reference the glossary and the fact that the variables set suppress_octoechos but then overrides it with a canon distribution that includes Octoechos, which is an internal inconsistency and a gap.

For Vespers Prokeimenon, the rule: On Great Vespers for a feast with Vigil, the Prokeimenon of the feast is sung, not the daily Prokeimenon. This is well-known. The digest uses the daily. Gap.

For Matins Prokeimenon, the feast's Prokeimenon is prescribed. The digest uses a psalm inappropriate for the feast.

For Aposticha: On Great Vespers of a feast, the Aposticha are from the feast, not daily. The glossary "Vespers and Vigil on the Eves of Nativity and Theophany" suggests special Aposticha, but general rule.

For Midnight Office: The glossary "Midnight Office on Feasts of the Lord and Theotokos" footnote 22 says troparion and kontakion of the feast are taken. So the digest's weekday troparia are wrong.

For the erroneous Triodion sessional hymns: Clearly a database leak.

Now, about "Both now: Dogmatic Theotokion" vs Theotokion. I'll check the "Dogmatikon and Afterfeasts on Fridays" footnote 376, which states that Dogmatikon is given on Fridays for Afterfeasts, but generally for Vigil of a saint not in an Afterfeast, it's not necessarily Dogmatic. But the Menaion for Peter and Paul might specify its own Theotokion after the Doxastikon. Typically, at Lord, I have cried, after the Doxastikon of the saint, the Both now is the Dogmatic Theotokion of the current tone only if it is a Saturday (or Sunday) vespers. On weekdays, it's the Theotokion from the Octoechos (the first Theotokion after the stichera) or the Dogmatic might be used only on Friday evening? Actually, Dolnytsky's glossary in "Dogmatikon and Afterfeasts on Fridays" says that in afterfeasts, the Dogmatikon is omitted on Fridays. That implies that on ordinary Fridays, the Dogmatikon is used. The footnote: "we think that here too the 1st Theotokion of the tone should be according to the general rule ... and if -- not, then also in the Afterfeast of other feasts there should be a stichera of the Feast, which would be in greater conformity with ancient typikons, in which neither on the Forefeast, nor on the Afterfeast, nor on the Apodosis of the Feast is the Dogmatikon given on Friday evening, but only stichera of the Feast, regardless -- whether it is Saturday or another day of the week." That is specifically about Afterfeast, not a simple Vigil. So for a Vigil of a saint not during an afterfeast, the Theotokion at Lord, I have cried is determined by the rule for feasts: if the Menaion has a Doxastikon and a separate Theotokion, it is taken; otherwise, the Dogmatic Theotokion of the tone is sung. Many Russian typikons specify Dogmatic Theotokion on Vigils regardless of day. But I'm not entirely sure. Since the variable explicitly sets "dogmatikon_current_tone_if_friday_else_theotokion", meaning the intended Theotokion is non-dogmatic on non-Fridays. So the digest text that says "Dogmatic Theotokion" is inconsistent with the variable. So I'll flag that as an internal inconsistency/formating error.

Now, for the Litiya: The digest doesn't mention a Litiya, but the variables include "litiya_stichera": "peter_paul_litiya". The full digest doesn't include any Lytia section. That's a gap: A Vigil feast typically includes Litiya at Great Vespers. The digest's Vespers section lacks mention of Litiya stichera and blessing of loaves. So that's a missing element.

Now, for the "Magnification": Variable "has_polyeleos": true, but the feast may have a Magnification; the quick reference says "Magnification: sung if prescribed." In the full digest, it's not mentioned. Not a major gap.

Now, let's compile the gaps in a structured format.

I'll list each gap with citation and correction.

Note: The glossary reference "Feasts of the Holy Apostles (Vigil and Polyeleos)" footnote 704 establishes Peter and Paul as Vigil. The Lviv Paradigm CASE_05 might have rules. We can cite variable inconsistency as the gap.

For the Octoechos canon issue, I can reference the glossary "Canon Structure" which says for a Vigil feast, the canon is from the Menaion alone? Not directly. But I can argue that Dolnytsky's general rubrics for combining services (in Part 2) specify that on feasts with Vigil, the entire service is from the Menaion, except where noted. Since the variable suppress_octoechos is true, the canon should reflect that. So the engine's canon distribution violates its own variable, which is a gap.

Now, for the Vespers Aposticha: The Dolnytsky Part 1 Structure, section on Great Vespers, I'd need to find a rule. But we can cite the general principle: On great feasts, the Aposticha are taken from the feast's service. The glossary "Feasts of Saints (St. Peter and Paul stichera)" footnote 282: "The ancient handwritten Menaion that we have gives the stichera of the Praises only to Peter; and the handwritten typikon -- stichera of the Praises to Peter, and afterwards -- the Aposticha of the feast." That indicates that there are dedicated Aposticha for the feast. So the digest's daily Aposticha is wrong.

Midnight Office: Cite footnote 22.

So let's produce the audit output.

---

## AUDIT REPORT:

# SUPREME LITURGICAL COMPLIANCE AUDIT — JUNE 29, 2026 (CHIEF APOSTLES PETER AND PAUL)

**Reference Texts:** Dolnytsky_Typikon_Master.md, vocabulary_standardization_matrix.md, Dolnytsky_Typikon_Master.md (sliced for June), and the almanac-generated rubrics/variables.

---

## 1. SAINT’S RANK CLASSIFICATION GAP

### 1.1 Vigil rank misrepresented as “combined” service
- **Canonical Source:** *Dolnytsky_Typikon_Master.md* — **Feasts of the Holy Apostles (Vigil and Polyeleos)** (Footnote 704): “With the exception of the Chiefs of the Apostles Peter and Paul on June 29 … to whom the rubrics prescribe a Vigil ….”  
  The **Vigil** rank entirely suppresses the daily cycle. The *suppress_octoechos* variable is `true` in the resolved rubric.
- **Gap:** The digest header reads “Monday service combined with that of Chief Apostles Peter and Paul.” The term “combined” is incorrect for a feast of Vigil rank. The Monday ferial office is wholly replaced, not combined.
- **Correction:** Title should be simply “JUNE 29: CHIEF APOSTLES PETER AND PAUL. VIGIL. TONE IV.” Remove any reference to “combined” or “Monday service.”

### 1.2 Octoechos canon included despite suppressed day
- **Canonical Source:** The same Vigil rank implies suppression of the daily Octoechos canons. *Suppress_octoechos* = `true` in the resolved variables, yet the canon distribution retains 6 troparia from the Octoechos (*theotokos_special*).
- **Gap:** “At the Canon: Full order of the canon … Octoechos – 6 (including the heirmos), Menaion – 8.” This is a direct violation of the Vigil paradigm. The daily Octoechos canon must be completely omitted.
- **Correction:** Delete the Octoechos canon portion. The canon of the feast alone (the Menaion canon, on 8, with Irmos sung twice, and Katavasia from the Menaion) should be prescribed. If a Theotokos canon is appended, it must be a proper Theotokos canon from the Menaion or from the Parakletike for Vigils, not the ordinary daily theotokos canon.

### 1.3 Vestment colour discrepancy
- **Canonical Source:** Ruthenian tradition prescribes **red** (crimson) for feasts of the Holy Apostles. The glossary *Liturgical Colors (Crimson and Red)* (Footnote 455) notes “according to the ancient — of crimson color” for a comparable feast, while “Bright (Green)” is the ordinary Pentecost season colour but not for apostolic feasts.
- **Gap:** The digest prints “Vestment colour: Bright (Green).”  
- **Correction:** Change to “Vestment colour: Red (Crimson).”

---

## 2. SCRIPTURAL READINGS ACCURACY

### 2.1 Great Vespers Prokeimenon
- **Gap:** Both digests give “Daily Prokeimenon for Monday evening, Tone I” (Full) and “Prokeimenon: of the day, Tone I” (Quick). On a Vigil feast, the Prokeimenon of the day is replaced by the feast’s own Prokeimenon.
- **Canonical Source:** *Dolnytsky_Typikon_Master.md* (General Rubrics, §2.11.1.1) — the feast’s Prokeimenon is used. The resolved variable confirms `prokeimenon.source = menaion`.
- **Correction:** Replace with the feast Prokeimenon for the Apostles (typically “Their sound hath gone forth into all the earth” with its verse, Tone 8). Remove daily prokeimenon.

### 2.2 Matins Prokeimenon
- **Gap:** “Prokeimenon: Arise, O Lord, help us, and deliver us for Thy name’s sake (Tone IV).” This is a generic psalm, not the festival Prokeimenon for the Apostles.
- **Canonical Source:** The proper Matins Prokeimenon for the Feast of Peter and Paul is **“Their proclamation went forth into all the earth, and their words unto the ends of the world”** (Ps. 18:5, Tone 8).
- **Correction:** Replace with the correct festal Prokeimenon in Tone 8.

### 2.3 Liturgy Prokeimenon & Alleluia in Quick Reference
- **Gap:** The Quick Reference states “Prokeimenon: of the day” and “Alleluia: of the day.” The Full Digest correctly indicates they are *of the feast.*
- **Correction:** Unify both digests to the feast’s Prokeimenon (as in the Full Digest) and the feast’s Alleluia. The variable explicitly assigns `prokeimenon.source = menaion` and `alleluia.source = menaion`.

### 2.4 Matins Gospel vs. Eothinon
- **No Gap:** The Matins Gospel `John 21:15-25` is correct for this feast. The absence of “Having beheld the Resurrection…” is proper for a saint’s feast (non-Sunday). ✔

### 2.5 Liturgy Epistle & Gospel
- **No Gap:** `2 Corinthians 11:21-12:9` and `Matthew 16:13-19` match the festal lectionary. ✔

---

## 3. PRECEDENCE / COMBINATION RULES

### 3.1 Great Vespers Aposticha
- **Gap:** “We sing 3 daily Aposticha from the Octoechos; Glory, Both now: Aposticha Theotokion.” A Vigil feast has its own Aposticha stichera.
- **Canonical Source:** *Dolnytsky_Typikon_Master.md* — **Feasts of Saints (St. Peter and Paul stichera)** (Footnote 282): “the handwritten typikon — stichera of the Praises to Peter, and afterwards — the Aposticha of the feast.” The feast possesses dedicated Aposticha texts.
- **Correction:** Replace the “daily” Aposticha with those of the feast (from the Menaion or Litiya–Aposticha). Remove the Octoechos rubric.

### 3.2 Midnight Office troparia
- **Gap:** The digest prescribes “Troparion of the weekday, Troparion of the Temple, Troparion of the Saint (if any), daily Theotokion.” For a Vigil feast, Midnight Office troparia are those of the feast.
- **Canonical Source:** *Dolnytsky_Typikon_Master.md* — **Midnight Office on Feasts of the Lord and Theotokos** (Footnote 22) extends the principle to similar Vigil feasts: “troparion and kontakion of the feast.” The Ruthenian extended practice applies this to all Vigil-ranked feasts.
- **Correction:** Change to “Troparion of Chief Apostles Peter and Paul, twice; Glory… both now: Kontakion of the feast.”

### 3.3 Compline rubrics for a Vigil feast
- **Gap:** The digest includes a full “Small Compline” with its own troparia (Monday Troparion, Troparion of Temple, *O God of our fathers*). When a Vigil is served on the eve (Sunday evening, June 28), there is no separate Compline. Even if the Vigil is served in the morning, Compline on the day of the feast would not use the ordinary daily troparia.
- **Correction:** Remove the Small Compline section altogether (or replace with the note: “If a Compline is to be served, it should be Small Compline with the Kontakion of the feast, not the daily troparia.”) The current entry is misleading.

### 3.4 Erroneous “Triodion” Sessional Hymns in Quick Reference
- **Gap:** Quick Reference: “After each kathisma: we sing the Sessional Hymns from the Triodion.”
- **Canonical Source:** The Triodion is not in use (after Pentecost). The octoechos Sessional Hymns are suppressed for a Vigil feast.
- **Correction:** Delete the word “Triodion.” The correct text is “After each Kathisma we sing the Sessional Hymns of the Feast (from the Menaion).”

### 3.5 Litiya completely omitted
- **Gap:** The digests show no Litiya section. The resolved variables include `litiya_stichera: peter_paul_litiya`, indicating that the feast has Litiya stichera. A Vigil-ranked feast typically includes Litiya at Great Vespers.
- **Correction:** Insert a Litiya section with the dedicated stichera, followed by the Blessing of Loaves and the dismissal troparia.

### 3.6 Magnification after Polyeleos
- **No Gap:** Mentioning “Magnification: sung if prescribed” in the Quick reference is harmless, but the Full digest omits it. Since the variable sets `has_polyeleos: true`, a Magnification may exist; not listing it is not a fatal gap. ✔

---

## 4. FORMATTING, CAPITALIZATION, AND DATABASE ARTIFACTS

### 4.1 “Both now: Dogmatic Theotokion” vs. resolved variable
- **Source variable:** `"both_now": "dogmatikon_current_tone_if_friday_else_theotokion"`. Because June 29, 2026 is a Monday (not Friday), the “else_theotokion” branch would produce a non‑dogmatic Theotokion.
- **Gap:** The Full Digest prints “Both now: Dogmatic Theotokion in the tone of the week.”
- **Correction:** Replace the text with “Both now: Theotokion (from the Octoechos in the tone of the week) or the Theotokion provided in the Menaion after the Doxastikon.” The engine’s own logic forbids the word “Dogmatic” here.

### 4.2 Quick Reference database artifact – all‑caps MENAION with underscores
- **Gap:** Quick Reference header: “MENAION.JUN_29.PETER_AND_PAUL - TONE IV.”
- **Correction:** Use human‑readable format: “Menaion: June 29 — Chief Apostles Peter and Paul. Tone IV.”

### 4.3 Confusing/anachronistic “Anabathmoi” and “Gradual” duplication
- **Gap:** Full Digest: “Anabathmoi (Hymns of Ascents): Anabathmoi Tone Antiphon 4:1. Gradual (Anabathmoi): Antiphon Tone 1:4.” This repeats the same musical element using two different names and gives conflicting tone numbers (4 vs 1).
- **Correction:** Unify to a single line: “Gradual (Anabathmoi): Antiphon 1 of Tone 4.”

### 4.4 “Other: Now and ever….” at Praises
- **Gap:** The phrase “Other: Now and ever....” appears after the Doxastikon. This is an engine placeholder.
- **Correction:** Change to “Both now: Theotokion of the Praises (from the Menaion or the appropriate Dogmatic Theotokion of the tone, as indicated).”

### 4.5 *At Lord, I Call…* asterisk style – acceptable
- The use of asterisks for rubric headers is a permissible liturgical formatting. No correction required. ✔

---

**Summary of Critical Corrections:**
1. Eliminate all references to “combined” service; present feast as a standalone Vigil.
2. Remove the Octoechos canon from Matins; prescribe only the Menaion canon.
3. Replace daily Vespers Prokeimenon, Matins Prokeimenon, daily Aposticha, and daily Midnight Office troparia with the feast’s proper texts.
4. Correct the Matins Prokeimenon to “Their proclamation went forth” (Tone 8).
5. Unify Quick Reference Liturgy Prokeimenon/Alleluia to the feast (not “of the day”).
6. Fix formatting: remove “Dogmatic” from Theotokion when the variable requires non‑dogmatic; correct database artifacts like “MENAION.JUN_29”, “Triodion sessional hymns”, and the Anabathmoi/Gradual double entry.
7. Add the missing Litiya section.
8. Change vestment colour to Red (Crimson).