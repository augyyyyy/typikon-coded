"""
Service Card Formatter Mixin
Implements Universal 6-Tier Service Card Schema according to canonical_maximalist_digest_standard.md.
"""

from datetime import datetime


class ServiceCardFormatterMixin:
    """Mixin for TypikonDigestGenerator providing Universal 6-Tier Service Card formatting."""

    def resolve_service_card(self, service_def_or_name, context, rubrics):
        """
        Resolves the Universal 6-Tier Service Card for a given service.
        Returns a dictionary with tier_1 through tier_6 conforming to
        canonical_maximalist_digest_standard.md.
        """
        if isinstance(service_def_or_name, dict):
            service_name = service_def_or_name.get("name", "Service")
            root_id = service_def_or_name.get("root", "")
            type_key = service_def_or_name.get("type_key", "")
        else:
            service_name = str(service_def_or_name)
            root_id = ""
            type_key = ""

        day_of_week = context.get("day_of_week", 0)
        pascha_offset = context.get("pascha_offset")
        try:
            pascha_offset = int(pascha_offset) if pascha_offset is not None else None
        except (ValueError, TypeError):
            pascha_offset = None

        is_sunday = (day_of_week == 0)
        tone = context.get("tone", 1)
        try:
            tone_roman = self._roman_tone(tone)
        except Exception:
            tone_roman = str(tone)

        rank_val = context.get("rank", 5)
        try:
            from engine.utils.type_utils import parse_rank_integer
            rank_int = parse_rank_integer(rank_val)
        except Exception:
            rank_int = 5

        is_vigil = bool(
            rubrics.get("variables", {}).get("is_vigil") or
            rubrics.get("is_sunday_vigil") or
            context.get("is_vigil") or
            rank_int <= 2
        )

        is_presanctified = bool(
            rubrics.get("variables", {}).get("liturgy_type") == "liturgy_presanctified" or
            rubrics.get("overrides", {}).get("liturgy_type") == "liturgy_presanctified" or
            (hasattr(self.engine, "check_presanctified_trigger") and self.engine.check_presanctified_trigger(context))
        )

        is_vesperal_liturgy = bool(
            "vesperal_merge_logic" in rubrics.get("overrides", {}).get("liturgy_type", "") or
            "vesperal_merge_logic" in rubrics.get("variables", {}).get("liturgy_type", "")
        )

        is_bright_week = (pascha_offset is not None and 0 <= pascha_offset <= 6)
        is_great_lent = (pascha_offset is not None and -48 <= pascha_offset <= -9)
        is_holy_week = (pascha_offset is not None and -8 <= pascha_offset <= -1)

        # ----------------------------------------------------
        # TIER 1: CARD HEADER & BADGES
        # ----------------------------------------------------
        canon_format = self.engine.resolve_canonical_format_number(context)

        # Service Title
        if service_name.lower() in ("vespers", "great vespers", "daily vespers"):
            if is_presanctified:
                s_title = "Vesperal Liturgy of the Presanctified Gifts"
            elif is_vesperal_liturgy:
                s_title = "Vesperal Divine Liturgy"
            elif is_bright_week and pascha_offset == 0:
                s_title = "Paschal Vespers (Agape Vespers)"
            elif is_bright_week:
                s_title = "Bright Week Vespers"
            elif is_sunday or is_vigil or day_of_week == 6:
                s_title = "Great Vespers"
            else:
                s_title = "Daily Vespers"
        elif service_name.lower() in ("matins", "orthros"):
            if is_bright_week:
                s_title = "Bright Matins (Paschal Orthros)"
            elif pascha_offset == -2:
                s_title = "Matins of Great and Holy Friday (Twelve Passion Gospels)"
            elif pascha_offset == -1:
                s_title = "Matins of Great and Holy Saturday (Jerusalem Matins / Lamentations)"
            elif is_sunday:
                s_title = f"Sunday Matins (Orthros) — Tone {tone_roman}"
            elif rank_int <= 3:
                s_title = "Festive Matins (Orthros with Polyeleos)"
            else:
                s_title = "Daily Matins (Orthros)"
        elif service_name.lower() in ("divine liturgy", "liturgy"):
            if is_presanctified:
                s_title = "Liturgy of the Presanctified Gifts"
            elif rubrics.get("variables", {}).get("liturgy_type") == "basil" or pascha_offset in (-3, -1):
                s_title = "Divine Liturgy of St. Basil the Great"
            else:
                s_title = "Divine Liturgy of St. John Chrysostom"
        elif "hour" in service_name.lower():
            if is_bright_week:
                s_title = "Paschal Hours"
            elif pascha_offset == -2:
                s_title = "Royal Hours of Great Friday"
            else:
                s_title = service_name
        elif "compline" in service_name.lower():
            s_title = "Great Compline" if is_great_lent else "Small Compline"
        elif "midnight" in service_name.lower():
            s_title = "Sunday Midnight Office" if is_sunday else "Daily Midnight Office"
        else:
            s_title = service_name

        # Vestment Color Badge
        vestment_res = {}
        try:
            vestment_res = self.engine.resolve_vestment_color(context, rubrics) or {}
        except Exception:
            pass
        color_name = vestment_res.get("color", "bright_gold").replace("_", " ").title()
        alt_color = vestment_res.get("alt", "")
        if alt_color:
            alt_str = f" (or {alt_color.replace('_', ' ').title()})"
        else:
            alt_str = ""
        vestment_badge = f"{color_name}{alt_str}"

        # Fasting Rule Badge
        fasting_res = {}
        try:
            fasting_res = self.engine.resolve_fasting_rule(context, rubrics) or {}
        except Exception:
            pass
        fasting_type = fasting_res.get("type", "normal").replace("_", " ").title()
        fasting_note = fasting_res.get("note", "")
        fasting_badge = f"{fasting_type}" + (f" — {fasting_note}" if fasting_note else "")

        tier_1 = {
            "service_title": s_title,
            "vestment_badge": vestment_badge,
            "fasting_badge": fasting_badge,
            "canonical_format": canon_format,
            "format_badge": f"Format {canon_format:02d}",
        }

        # ----------------------------------------------------
        # TIER 2: OPENING & ENTRANCE CHOREOGRAPHY
        # ----------------------------------------------------
        if "liturgy" in service_name.lower() and not is_presanctified:
            opening_blessing = 'Blessed is the kingdom of the Father, and of the Son, and of the Holy Spirit, now and ever, and forever.'
            opening_psalmody = 'The Three Antiphons (First Antiphon: Psalm 102; Second Antiphon: Psalm 145; Third Antiphon: The Beatitudes)'
            door_state = 'Holy Doors Open at the Little Entrance, Gospel reading, Great Entrance, and Holy Communion'
            entrance_type = 'Little Entrance with the Holy Gospel; Great Entrance with the Holy Gifts'
        elif is_presanctified or (is_vesperal_liturgy and "vespers" in service_name.lower()):
            opening_blessing = 'Blessed is the kingdom of the Father, and of the Son, and of the Holy Spirit, now and ever, and forever.'
            opening_psalmody = 'Psalm 103 (Bless the Lord, O my soul)'
            door_state = 'Holy Doors Open at Entrance, Gospel, and Great Entrance; Closed during Readings and Anaphora'
            entrance_type = 'Entrance with Holy Gospel Book and Censer; Great Entrance with Pre-sanctified Gifts in solemn silence'
        elif is_bright_week:
            opening_blessing = 'Glory to the holy, consubstantial, life-creating, and undivided Trinity, always, now and ever, and forever.'
            opening_psalmody = 'Paschal Troparion "Christ is risen from the dead..." (thrice by celebrant, then with Paschal Verses)'
            door_state = 'Holy Doors and Diaconal Doors remain open throughout the entire service (Ordo §19e)'
            entrance_type = 'Solemn Entrance with Holy Gospel Book and Censer' if "vespers" in service_name.lower() else 'No Entrance'
        elif "vespers" in service_name.lower():
            if is_vigil:
                opening_blessing = 'Glory to the holy, consubstantial, life-creating, and undivided Trinity, always, now and ever, and forever.'
            else:
                opening_blessing = 'Blessed is our God, always, now and ever, and forever.'
            opening_psalmody = 'Psalm 103 (Bless the Lord, O my soul)'
            has_entrance = False
            try:
                has_entrance = bool(self.engine.resolve_entrance_logic(context, rubrics))
            except Exception:
                has_entrance = is_sunday or is_vigil or rank_int <= 3

            if has_entrance:
                entrance_type = 'Entrance with Censer ("Wisdom! Stand aright!")'
                door_state = 'Holy Doors Open for Blessing and Initial Censing; Closed during Kathisma; Opened for Entrance through Prokeimenon'
            else:
                entrance_type = 'No Entrance'
                door_state = 'Holy Doors Closed, Curtain Drawn'
        elif "matins" in service_name.lower():
            if is_vigil:
                opening_blessing = 'Glory to the holy, consubstantial, life-creating, and undivided Trinity, always, now and ever, and forever.'
            else:
                opening_blessing = 'Blessed is our God, always, now and ever, and forever.'
            opening_psalmody = 'The Six Psalms (Psalms 3, 37, 62, 87, 102, 142)'
            door_state = 'Holy Doors Closed; Opened for Polyeleos, Gospel, and Great Doxology' if (is_sunday or rank_int <= 3) else 'Holy Doors Closed, Curtain Drawn'
            entrance_type = 'Entrance with Gospel' if pascha_offset == -2 else 'No Entrance'
        elif "hour" in service_name.lower():
            opening_blessing = 'Blessed is our God, always, now and ever, and forever.'
            opening_psalmody = 'Three Fixed Psalms of the Hour'
            door_state = 'Holy Doors Closed, Curtain Drawn'
            entrance_type = 'No Entrance'
        elif "compline" in service_name.lower():
            opening_blessing = 'Blessed is our God, always, now and ever, and forever.'
            opening_psalmody = 'Fixed Compline Psalms (Psalms 4, 6, 12, 69, 90, 142)'
            door_state = 'Holy Doors Closed, Curtain Drawn'
            entrance_type = 'No Entrance'
        else:
            opening_blessing = 'Blessed is our God, always, now and ever, and forever.'
            opening_psalmody = 'Fixed Service Psalms'
            door_state = 'Holy Doors Closed'
            entrance_type = 'No Entrance'

        tier_2 = {
            "opening_blessing": opening_blessing,
            "opening_psalmody": opening_psalmody,
            "door_state": door_state,
            "entrance_type": entrance_type,
        }

        # ----------------------------------------------------
        # TIER 3: PSALMODY & KATHISMA DETERMINATION
        # ----------------------------------------------------
        kathismata = []
        sessional_hymns = "None"
        omissions = "None"

        if is_bright_week:
            kathismata = []
            omissions = "Kathisma entirely omitted throughout Bright Week (Ordo §19e)"
        elif "vespers" in service_name.lower():
            if day_of_week == 6:  # Saturday evening for Sunday
                kathismata = ["Kathisma 1: Blessed is the man (1st Stasis chanted)"]
                omissions = "Stases 2 and 3 omitted on Saturday evening"
            elif day_of_week == 0:  # Sunday evening
                kathismata = []
                omissions = "Kathisma omitted on Sunday evening (Ordo §31)"
            elif rank_int == 1:  # Great Feast of the Lord
                kathismata = []
                omissions = "Kathisma omitted due to Great Feast of the Lord"
            else:
                kathismata = ["Kathisma according to the weekly Psalter division"]
        elif "matins" in service_name.lower():
            if is_sunday:
                kathismata = ["Kathisma II", "Kathisma III (or seasonal Kathismata)"]
                sessional_hymns = f"Resurrectional Sessionals in Tone {tone_roman} after each Kathisma; Hypakoë in Tone {tone_roman} after Polyeleos"
            elif rank_int <= 3:
                kathismata = ["Kathisma according to Psalter schedule", "Polyeleos (Psalms 134 & 135) with Megalynarion"]
                sessional_hymns = "Sessionals of the Feast / Saint after each Kathisma and after the Polyeleos"
            else:
                kathismata = ["Two Kathismata according to the weekly Psalter schedule"]
                sessional_hymns = "Daily Sessionals from the Octoechos and Menaion"
        elif "hour" in service_name.lower():
            if is_great_lent:
                kathismata = ["Kathisma assigned to the Hour during Great Lent"]
            else:
                kathismata = []
                omissions = "No Kathisma appointed at the Hours outside Great Lent"
        else:
            kathismata = []
            omissions = "None"

        tier_3 = {
            "kathismata_numbers": kathismata,
            "sessional_hymns": sessional_hymns,
            "kathisma_omissions": omissions,
        }

        # ----------------------------------------------------
        # TIER 4: CORE HYMN STACK & PROPORTIONAL RATIOS
        # ----------------------------------------------------
        stichera_dist = {}
        canon_stack = "None"
        praises_dist = "None"
        doxastikon = "None"
        dogmatikon = "None"

        if "vespers" in service_name.lower():
            if is_sunday or day_of_week == 6:
                if rank_int <= 3:
                    stichera_dist = {"octoechos_resurrection": 4, "feast_or_saint": 6, "total": 10}
                    doxastikon = "Glory: Feast / Saint Doxastikon"
                else:
                    stichera_dist = {"octoechos_resurrection": 6, "menaion_saint": 4, "total": 10}
                    doxastikon = "Glory: Saint Doxastikon (or omitted if none appointed)"
                dogmatikon = f"Both now: Dogmatikon of Tone {tone_roman} from the Octoechos"
            elif rank_int <= 3:
                stichera_dist = {"feast_or_saint": 8, "total": 8}
                doxastikon = "Glory: Feast / Saint Doxastikon"
                dogmatikon = "Both now: Feast / Theotokion of the Tone"
            else:
                stichera_dist = {"octoechos": 3, "menaion": 3, "total": 6}
                doxastikon = "Glory: Menaion Saint (if appointed)"
                dogmatikon = "Both now: Octoechos Weekday Theotokion"
        elif "matins" in service_name.lower():
            if is_sunday:
                canon_stack = f"Resurrection Canon (4), Cross-Resurrection (2), Theotokos (2), Menaion (4) — Total: 12 with Katavasia"
                praises_dist = f"Praises on 8: 8 Resurrection Stichera in Tone {tone_roman} (or 4 Resurrection + 4 Feast/Saint)"
                doxastikon = "Glory: Gospel Sticheron (1 of 11 Eothina Stichera)"
                dogmatikon = 'Both now: "Most blessed art thou, O Virgin Theotokos..." in Tone II'
            elif rank_int <= 3:
                canon_stack = "Canon of the Feast / Saint on 8 or 12 with appointed Katavasia"
                praises_dist = "Praises on 4 or 6: Feast / Saint Stichera"
                doxastikon = "Glory: Feast / Saint Doxastikon"
                dogmatikon = "Both now: Theotokion of the Tone"
            else:
                canon_stack = "Canons from Octoechos and Menaion on 12 with Biblical Canticles"
                praises_dist = "Praises read (Daily praises)"
                doxastikon = "Glory: Menaion Saint (if appointed)"
                dogmatikon = "Both now: Octoechos Daily Theotokion"
        elif "liturgy" in service_name.lower() and not is_presanctified:
            stichera_dist = {"antiphon_troparia": 8 if is_sunday else 6}
            doxastikon = "Glory: Saint Kontakion"
            dogmatikon = 'Both now: Steadfast Protectress of Christians ("O Protection of Christians...")'

        tier_4 = {
            "stichera_distribution": stichera_dist,
            "canon_stack": canon_stack,
            "praises_distribution": praises_dist,
            "doxastikon": doxastikon,
            "dogmatikon": dogmatikon,
        }

        # ----------------------------------------------------
        # TIER 5: SCRIPTURE READINGS & LITANIES
        # ----------------------------------------------------
        prokeimena = []
        scripture_readings = []
        litanies = []

        if "vespers" in service_name.lower():
            if day_of_week == 6:  # Saturday evening for Sunday
                prokeimena.append('Tone VI: "The Lord is King, He is robed in majesty." (Verse: "The Lord is robed, He is girded with strength.")')
            elif day_of_week == 0:  # Sunday evening
                prokeimena.append('Tone VIII: "Behold now, bless the Lord, all you servants of the Lord."')
            else:
                prokeimena.append(f"Daily Prokeimenon of the day in appointed Tone")

            if is_vigil or rank_int <= 2:
                scripture_readings.append("Old Testament Paremias (3 readings appointed for the Feast / Saint)")
            else:
                scripture_readings.append("No Old Testament readings appointed")

            litanies = [
                "Great Litany (Litany of Peace)",
                "Litany of Fervent Supplication",
                "Litany of Supplication",
                "Prayer of the Bowing of Heads",
            ]
        elif "matins" in service_name.lower():
            if is_sunday:
                prokeimena.append(f"Sunday Matins Prokeimenon in Tone {tone_roman}")
                scripture_readings.append("Resurrection Gospel (1 of the 11 Matins Gospels in cycle)")
            elif rank_int <= 3:
                prokeimena.append("Festive Matins Prokeimenon")
                scripture_readings.append("Gospel of the Feast / Saint")
            else:
                scripture_readings.append("No Gospel reading appointed at Daily Matins")

            litanies = [
                "Great Litany",
                "Little Litanies (after Kathismata)",
                "Litany of Fervent Supplication",
                "Litany of Supplication",
            ]
        elif "liturgy" in service_name.lower() and not is_presanctified:
            if is_sunday:
                prokeimena.append(f"Prokeimenon of the Sunday in Tone {tone_roman} (plus Saint Prokeimenon if appointed)")
            else:
                prokeimena.append("Prokeimenon of the Day / Saint")
            scripture_readings.append("Epistle reading of the day (Book, Chapter, Verse)")
            scripture_readings.append("Holy Gospel of the day (Book, Chapter, Verse)")
            litanies = [
                "Great Litany",
                "Little Litanies",
                "Litany of Fervent Supplication",
                "Litany of the Catechumens",
                "Litanies of the Faithful",
                "Litany of Supplication",
                "Litany of Thanksgiving",
            ]
        elif is_presanctified:
            prokeimena.append("1st Triodion Prokeimenon; 2nd Triodion Prokeimenon with 'The Light of Christ illumines all!'")
            scripture_readings.append("1st Paremia (Genesis / Exodus)");
            scripture_readings.append("2nd Paremia (Proverbs / Job)")
            litanies = [
                "Great Litany",
                "Litany of Fervent Supplication",
                "Litany of the Catechumens",
                "Litany for those preparing for Holy Illumination (during second half of Great Lent)",
                "Litanies of the Faithful",
                "Litany of Supplication after Great Entrance",
                "Prayer behind the Ambo",
            ]
        else:
            litanies = ["Little Litany / Trisagion Prayers", "Prayer of the Hour", "Dismissal Litany"]

        tier_5 = {
            "prokeimena": prokeimena,
            "scripture_readings": scripture_readings,
            "litanies_sequence": litanies,
        }

        # ----------------------------------------------------
        # TIER 6: DISMISSAL & CONCLUDING APODOSIS
        # ----------------------------------------------------
        if is_sunday:
            troparia_chain = f"Troparion of the Resurrection in Tone {tone_roman} -> Glory: Saint -> Both now: Dismissal Theotokion"
            dismissal_theotokion = f"Resurrectional Dismissal Theotokion of Tone {tone_roman} from the Octoechos"
            benediction = 'Opening: "May Christ our true God, risen from the dead..."; Patron Saint; Saints of the day; All the saints.'
        elif rank_int <= 3:
            troparia_chain = "Troparion of the Feast / Saint -> Glory, Both now: Festal Dismissal Theotokion"
            dismissal_theotokion = "Dismissal Theotokion of the Feast / Saint Tone"
            benediction = 'Opening: "May Christ our true God..."; Feast/Saint commemorated; Patron Saint; All the saints.'
        else:
            troparia_chain = "Troparion of the Saint -> Glory, Both now: Daily Dismissal Theotokion from Octoechos"
            dismissal_theotokion = "Daily Dismissal Theotokion of the Tone"
            benediction = 'Opening: "May Christ our true God..."; Saints of the day; Patron Saint; All the saints.'

        tier_6 = {
            "dismissal_troparia_chain": troparia_chain,
            "dismissal_theotokion": dismissal_theotokion,
            "benediction_commemorations": benediction,
        }

        return {
            "tier_1": tier_1,
            "tier_2": tier_2,
            "tier_3": tier_3,
            "tier_4": tier_4,
            "tier_5": tier_5,
            "tier_6": tier_6,
        }

    def format_service_card(self, card_data):
        """
        Formats a Universal 6-Tier Service Card into standard markdown.
        Strictly enforces tier headers and labels per canonical_maximalist_digest_standard.md.
        """
        if not card_data or not isinstance(card_data, dict):
            return ""

        t1 = card_data.get("tier_1", {})
        t2 = card_data.get("tier_2", {})
        t3 = card_data.get("tier_3", {})
        t4 = card_data.get("tier_4", {})
        t5 = card_data.get("tier_5", {})
        t6 = card_data.get("tier_6", {})

        title = t1.get("service_title", "SERVICE CARD").upper()
        lines = []
        lines.append(f"## {title}")
        lines.append("")

        # TIER 1
        lines.append("### [TIER 1] CARD HEADER & BADGES")
        lines.append(f"- **Service Title**: {t1.get('service_title', '')}")
        lines.append(f"- **Canonical Format**: {t1.get('format_badge', '')}")
        lines.append(f"- **Vestment Badge**: {t1.get('vestment_badge', '')}")
        lines.append(f"- **Fasting Badge**: {t1.get('fasting_badge', '')}")
        lines.append("")

        # TIER 2
        lines.append("### [TIER 2] OPENING & ENTRANCE CHOREOGRAPHY")
        lines.append(f"- **Opening Blessing**: {t2.get('opening_blessing', '')}")
        lines.append(f"- **Opening Psalmody**: {t2.get('opening_psalmody', '')}")
        lines.append(f"- **Sanctuary Doors State**: {t2.get('door_state', '')}")
        lines.append(f"- **Entrance Type**: {t2.get('entrance_type', '')}")
        lines.append("")

        # TIER 3
        lines.append("### [TIER 3] PSALMODY & KATHISMA DETERMINATION")
        k_list = t3.get("kathismata_numbers", [])
        k_str = "; ".join(k_list) if isinstance(k_list, list) and k_list else (str(k_list) if k_list else "None")
        lines.append(f"- **Kathismata**: {k_str}")
        lines.append(f"- **Sessional Hymns**: {t3.get('sessional_hymns', 'None')}")
        lines.append(f"- **Kathisma Omissions**: {t3.get('kathisma_omissions', 'None')}")
        lines.append("")

        # TIER 4
        lines.append("### [TIER 4] CORE HYMN STACK & PROPORTIONAL RATIOS")
        s_dist = t4.get("stichera_distribution", {})
        if isinstance(s_dist, dict) and s_dist:
            s_str = ", ".join(f"{k.replace('_', ' ').title()}: {v}" for k, v in s_dist.items())
        else:
            s_str = str(s_dist) if s_dist else "None"
        lines.append(f"- **Stichera Distribution**: {s_str}")
        lines.append(f"- **Canon Stack**: {t4.get('canon_stack', 'None')}")
        lines.append(f"- **Praises Distribution**: {t4.get('praises_distribution', 'None')}")
        lines.append(f"- **Doxastikon (Glory)**: {t4.get('doxastikon', 'None')}")
        lines.append(f"- **Dogmatikon / Theotokion (Both now)**: {t4.get('dogmatikon', 'None')}")
        lines.append("")

        # TIER 5
        lines.append("### [TIER 5] SCRIPTURE READINGS & LITANIES")
        prok = t5.get("prokeimena", [])
        prok_str = "; ".join(prok) if isinstance(prok, list) and prok else (str(prok) if prok else "None")
        lines.append(f"- **Prokeimena**: {prok_str}")
        readings = t5.get("scripture_readings", [])
        read_str = "; ".join(readings) if isinstance(readings, list) and readings else (str(readings) if readings else "None")
        lines.append(f"- **Scripture Readings**: {read_str}")
        litanies = t5.get("litanies_sequence", [])
        lit_str = " -> ".join(litanies) if isinstance(litanies, list) and litanies else (str(litanies) if litanies else "None")
        lines.append(f"- **Litanies Sequence**: {lit_str}")
        lines.append("")

        # TIER 6
        lines.append("### [TIER 6] DISMISSAL & CONCLUDING APODOSIS")
        lines.append(f"- **Dismissal Troparia Chain**: {t6.get('dismissal_troparia_chain', '')}")
        lines.append(f"- **Dismissal Theotokion**: {t6.get('dismissal_theotokion', '')}")
        lines.append(f"- **Benediction Commemorations**: {t6.get('benediction_commemorations', '')}")
        lines.append("")

        return "\n".join(lines)

    def generate_maximalist_digest(self, context, rubrics):
        """
        Generates a complete Maximalist Typikon Digest featuring the
        Universal 6-Tier Service Card Schema for every active service of the daily cycle.
        """
        digest = []

        # 1. Date Header
        date_str = context.get('date', '')
        try:
            dt = datetime.fromisoformat(date_str).date()
            day_name = dt.strftime('%A').upper()
            month_name = dt.strftime('%B').upper()
            day = dt.day
            suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            formatted_date = f"{day_name}, {month_name} {day}{suffix}, {dt.year}."
        except Exception:
            formatted_date = date_str

        digest.append(f"# TYPICON MAXIMALIST DIGEST: {formatted_date}")

        # Canonical Format Evaluation
        canon_format = self.engine.resolve_canonical_format_number(context)
        digest.append(f"**Canonical General Format**: Format {canon_format:02d} / 26")

        # Tone & Saints
        tone = context.get("tone")
        if tone:
            try:
                tone_roman = self._roman_tone(tone)
            except Exception:
                tone_roman = str(tone)
            digest.append(f"**Tone**: Tone {tone_roman}")

        saints = context.get("saints", [])
        if saints:
            s_names = [s.get("name", "") for s in saints if s.get("name")]
            if s_names:
                digest.append(f"**Commemorations**: {'; '.join(s_names)}")

        digest.append("")

        # 2. Daily Cycle Service Cards
        hours_handled = False
        for service in self.engine.daily_cycle:
            service_name = service.get("name", "")
            root_id = service.get("root", "")

            # Variable / override check
            if service.get("type_key") in rubrics.get("variables", {}):
                root_id = rubrics["variables"][service["type_key"]]
            if service.get("type_key") in rubrics.get("overrides", {}):
                root_id = rubrics["overrides"][service["type_key"]]

            if root_id in ["structure_suppressed", "no_liturgy"]:
                continue

            # Suppression for Compline/Midnight Office during Vigil
            if service_name in ("Compline", "Midnight Office"):
                day = context.get("day_of_week")
                v_type = rubrics.get("overrides", {}).get("vespers_type") or rubrics.get("variables", {}).get("vespers_type") or context.get("vespers_type")
                if day != 0 and v_type == "great_vespers_vigil":
                    continue

            # Group Hours into one unified card
            if "hour" in service_name.lower():
                if hours_handled:
                    continue
                hours_handled = True
                card_data = self.resolve_service_card("Hours (First, Third, Sixth, Ninth Hour)", context, rubrics)
                digest.append(self.format_service_card(card_data))
                continue

            # Vesperal Liturgy suppression
            is_vesperal_liturgy = (
                "vesperal_merge_logic" in rubrics.get("overrides", {}).get("liturgy_type", "") or
                "vesperal_merge_logic" in rubrics.get("variables", {}).get("liturgy_type", "")
            )
            is_presanctified = bool(
                rubrics.get("variables", {}).get("liturgy_type") == "liturgy_presanctified" or
                rubrics.get("overrides", {}).get("liturgy_type") == "liturgy_presanctified" or
                (hasattr(self.engine, "check_presanctified_trigger") and self.engine.check_presanctified_trigger(context))
            )
            if service_name == "Vespers" and (is_vesperal_liturgy or is_presanctified):
                # Vespers is merged into Liturgy
                continue

            card_data = self.resolve_service_card(service, context, rubrics)
            digest.append(self.format_service_card(card_data))

        return "\n".join(digest)
