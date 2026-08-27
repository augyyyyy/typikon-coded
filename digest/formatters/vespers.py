class VespersFormatterMixin:
    def _format_paschal_vespers(self, enriched, rubrics):
        day_of_week = enriched.get("day_of_week", 0)
        pascha_off = enriched.get("pascha_offset", 0)
        
        tones = {0: "II", 1: "III", 2: "IV", 3: "V", 4: "VI", 5: "VII", 6: "VIII"}
        tone_str = tones.get(day_of_week, "II")

        prok_map = {
            0: 'Great Prokeimenon (Tone VII): *"What God is great as our God? Thou art the God Who workest wonders!"*',
            1: 'Great Prokeimenon (Tone VII): *"Our God is in heaven and on earth; all that He pleased, He hath done."*',
            2: 'Great Prokeimenon (Tone VII): *"I cried aloud to God, and He heard me."*',
            3: 'Great Prokeimenon (Tone VII): *"O God, give ear to my prayer, and despise not my supplication."*',
            4: 'Great Prokeimenon (Tone VII): *"I will love Thee, O Lord, my strength; the Lord is my support and my refuge."*',
            5: 'Great Prokeimenon (Tone VII): *"Thou hast given an inheritance to those who fear Thy Name, O Lord."*',
            6: 'Prokeimenon (Tone VI): *"The Lord is King, He is robed in majesty."*'
        }
        prok_line = prok_map.get(day_of_week, prok_map[0])

        gospel_block = ""
        if day_of_week == 0:
            gospel_block = (
                "**Holy Gospel (John 20:19–25):** The celebrant, standing before the Holy Doors, reads the Gospel account of Christ appearing to the disciples on the evening of the Resurrection (*\"On the evening of that day, the first day of the week...\"*).\n\n"
            )

        dt_str = str(enriched.get("date", ""))
        is_annunciation = dt_str.endswith("-03-25") or enriched.get("feast_id") == "annunciation" or "annunciation" in str(enriched.get("title", "")).lower()
        
        if is_annunciation and day_of_week == 0:
            lines = [
                "**KYRIOPASCHA (PASCHA WITH ANNUNCIATION) AGAPE VESPERS:**",
                "**Opening:** The celebrant vests in full bright vestments, takes the censer and the Paschal Cross, and intones: *\"Glory to the Holy, Consubstantial, Life-Creating and Undivided Trinity...\"* followed by the Paschal Troparion *\"Christ is risen from the dead...\"* (thrice by clergy, then with the Paschal Verses by the choir).",
                "**At Lord, I Call:** 3 Paschal Stichera, and 3 Feast Stichera of the Annunciation; Glory: Feast of the Annunciation; Both now: Paschal Dogmatikon in Tone II.",
                "**Entrance:** Solemn Entrance with the Holy Gospel Book, censer, and candles; *\"O Joyful Light\"* (*Phos Hilaron*).",
                f"**{prok_line}**",
                gospel_block + "**At the Aposticha:** Paschal Stichera (*\"Let God arise... Today a sacred Pascha is revealed to us...\"*); Glory: Feast of the Annunciation; Both now: *\"This is the day of Resurrection! Let us be illumined by the feast...\"*",
                "**Troparia:** Troparion of Pascha (*\"Christ is risen from the dead...\"*), Troparion of the Annunciation (*\"Today is the fountainhead of our salvation...\"*).",
                "**Paschal Dismissal:** Dialogical Paschal Dismissal with the Cross (*\"Christ is risen from the dead...\"*)."
            ]
            return "\n\n".join(l for l in lines if l.strip())

        lines = [
            "**Opening:** The celebrant vests in full bright vestments, takes the censer and the Paschal Cross, and intones: *\"Glory to the Holy, Consubstantial, Life-Creating and Undivided Trinity...\"* followed by the Paschal Troparion *\"Christ is risen from the dead...\"* (thrice by clergy, then with the Paschal Verses by the choir).",
            f"**At Lord, I Call:** 6 Resurrectional Stichera in Tone {tone_str}; Glory, Both now: Dogmatikon in Tone {tone_str}.",
            "**Entrance:** Solemn Entrance with the Holy Gospel Book, censer, and candles; *\"O Joyful Light\"* (*Phos Hilaron*).",
            f"**{prok_line}**",
            gospel_block + "**At the Aposticha:** 1 Resurrectional Sticheron in Tone " + tone_str + ", followed by the **Paschal Stichera** (*\"Let God arise... Today a sacred Pascha is revealed to us...\"*); Glory, Both now: *\"This is the day of Resurrection! Let us be illumined by the feast...\"*",
            "**Paschal Dismissal:** Dialogical Paschal Dismissal with the Cross (*\"Christ is risen from the dead...\"*)."
        ]
        return "\n\n".join(l for l in lines if l.strip())

    def _format_resolve_passion_vespers_readings(self, res, context):
        if not res:
            return ""
        parts = []
        if "prokeimenon" in res:
            parts.append(f"Prokeimenon: {res['prokeimenon']['text']}")
        for i in (1, 2, 3):
            k = f"paremia_{i}"
            if k in res:
                parts.append(f"Paremia {i}: {res[k]['book']} {res[k]['chapter']}")
        if "epistle" in res:
            parts.append(f"Epistle: {res['epistle']['book']} {res['epistle']['chapter']}")
        if "alleluia" in res:
            parts.append(f"Alleluia: {res['alleluia']['text']}")
        if "gospel" in res:
            parts.append(f"Gospel: {res['gospel']['content']} ({', '.join(res['gospel']['sources'])})")
        return "\n".join(parts)


    def _format_resolve_small_vespers_prokeimenon(self, res, context):
        if not res:
            return ""
        ref_str = self.humanize_key(res.get("ref_key", ""))
        return f"Prokeimenon: {ref_str}"


    def _format_resolve_vespers_stichera(self, res, context):
        if not res:
            return ""
        
        dist = []
        for item in res.get("distribution", []):
            c = item.get('count', item.get('qty', '?'))
            t = item.get('type', '')
            s = self.humanize_key(item.get('source', ''))
            
            # Map type to a human readable description
            saints = context.get("saints", [])
            if t == "saint":
                if saints:
                    name = f"Stichera of {self._clean_name(saints[0].get('name', 'the Saint'))}"
                else:
                    name = "Stichera of the Saint"
            elif t == "saint_1":
                if saints:
                    name = f"Stichera of {self._clean_name(saints[0].get('name', 'the First Saint'))}"
                else:
                    name = "Stichera of the First Saint"
            elif t == "saint_2":
                if len(saints) >= 2:
                    name = f"Stichera of {self._clean_name(saints[1].get('name', 'the Second Saint'))}"
                else:
                    name = "Stichera of the Second Saint"
            elif t in ("current_day", "current_day_stichera"):
                name = "Stichera"
            elif "res" in t.lower():
                name = "Resurrectional Stichera"
            else:
                name = self.humanize_key(t) if t else "Stichera"
                if not name.lower().endswith("stichera"):
                    name = f"{name} Stichera"
            
            dist.append(f"{c} {name} from the {s}")
        parts = []
        if dist:
            if len(dist) == 1:
                joined_dist = dist[0]
            elif len(dist) == 2:
                joined_dist = f"{dist[0]}, and {dist[1]}"
            else:
                joined_dist = ", ".join(dist[:-1]) + f", and {dist[-1]}"
            parts.append(f"**At Lord, I Call:** We sing {joined_dist}")
        glory_val = res.get("glory")
        both_now_val = res.get("both_now")
        
        glory_human = self.humanize_key(glory_val)
        both_now_human = self.humanize_key(both_now_val)
        
        has_glory = glory_human and glory_human.strip().lower() not in ("none", "", "null", "glory", "(no saint doxastikon)", "(no_saint_doxastikon)")
        
        if has_glory:
            parts.append(f"Glory... {glory_human}")
            if both_now_human and both_now_human.strip().lower() not in ("none", "", "null"):
                parts.append(f"Both now... {both_now_human}")
        elif str(glory_val).strip().lower() == "(no_saint_doxastikon)" or str(glory_val).strip().lower() == "(no saint doxastikon)":
            parts.append("Glory... Doxastikon of the Saint")
            if both_now_human and both_now_human.strip().lower() not in ("none", "", "null"):
                parts.append(f"Both now... {both_now_human}")
        else:
            if both_now_human and both_now_human.strip().lower() not in ("none", "", "null"):
                parts.append(f"Glory, Both now... {both_now_human}")
                
        return "; ".join(parts) + "."
        

    def _format_resolve_vespers_prokeimenon(self, res, context):
        if not res:
            return ""
        if isinstance(res, dict):
            tone = res.get("tone") or context.get("tone")
            tone_str = f", Tone {self._roman_tone(tone)}" if tone else ""
            if res.get("type") == "prokeimenon" and res.get("ref_key"):
                return f"Prokeimenon: of the {self.humanize_key(res['ref_key'])}{tone_str}."
            if "text" in res:
                return f"Prokeimenon: of the day{tone_str}."
        
        tone = context.get("tone")
        tone_str = f", Tone {self._roman_tone(tone)}" if tone else ""
        return f"Prokeimenon: of the day{tone_str}."


    def _format_resolve_vespers_entrance(self, res, context):
        if isinstance(res, dict) and res.get("type") == "component_ref":
            return "Entrance with the censer."
        return ""


    def _format_resolve_vespers_readings_logic(self, res, context):
        if not res or not isinstance(res, list):
            return ""
        
        parts = []
        
        # 1. Format the Prokeimenon if present
        for item in res:
            if isinstance(item, dict) and item.get("type") in ("prokeimenon", "sunday_prokeimenon", "daily_prokeimenon", "festal_prokeimenon"):
                p_text = self._format_resolve_prokeimenon(item, context)
                if p_text:
                    parts.append(p_text)
                break
        
        # 2. Format the Readings
        readings = [f"Reading: {r.get('citation', 'Unknown')}" for r in res if r.get('type') == 'ot_reading']
        if readings:
            parts.append("Readings: " + "; ".join(readings) + ".")
            
        return "\n".join(parts)


    def _format_resolve_vespers_troparia_simple(self, res, context):
        if not res or not res.get("components"):
            return ""
            
        is_weekday = 0 < context.get("day_of_week", 0) <= 5
        
        pascha_offset = context.get("pascha_offset")
        is_fore_after = bool(
            context.get("is_fore_or_afterfeast") or
            context.get("is_afterfeast") or
            context.get("triodion_period") in ["forefeast", "afterfeast", "apodosis"] or
            context.get("dolnytsky_rank") in ["forefeast", "afterfeast", "apodosis"] or
            (pascha_offset is not None and 60 <= pascha_offset <= 67)
        )
        d_title = context.get("dolnytsky_title", "").lower()
        d_commem = context.get("dolnytsky_commemoration", "").lower()
        if any(x in d_title or x in d_commem for x in ["forefeast", "afterfeast", "apodosis"]):
            is_fore_after = True

        is_simple = (context.get("rank") in ("rank_simple_6", "rank_simple_4") or context.get("variables", {}).get("rank") in ("rank_simple_6", "rank_simple_4")) and not is_fore_after
        if is_weekday and is_simple:
            is_no_troparion = (context.get("dolnytsky_rank_code") == "[4 NO]" or context.get("variables", {}).get("dolnytsky_rank_code") == "[4 NO]")
            has_saint_trop = any(c.get("type") == "saint" for c in res.get("components", []))
            if is_no_troparion and has_saint_trop:
                is_no_troparion = False
            if is_no_troparion:
                day = context.get("day_of_week", 1)
                if day in (3, 5):
                    wname = "the Cross"
                    wtone = "Tone I"
                elif day == 1:
                    wname = "the Archangels"
                    wtone = "Tone VIII"
                elif day == 2:
                    wname = "the Forerunner"
                    wtone = "Tone II"
                elif day == 4:
                    wname = "the Apostles and St. Nicholas"
                    wtone = "Tone III and Tone IV"
                else:
                    wname = "the day"
                    wtone = "the tone of the week"
                return f"**At the Dismissal Troparia:** We sing the troparion of {wname}; Glory, both now... Dismissal Theotokion in {wtone}."
            else:
                s_name = "Saint"
                saints = context.get("saints", [])
                if saints:
                    s_name_raw = saints[0].get("name", "Saint").strip()
                    s_name = self._clean_name(s_name_raw)
                tone_val = context.get("tone", 1)
                tone_rom = self._roman_tone(tone_val) if isinstance(tone_val, int) else str(tone_val)
                return f"**At the Dismissal Troparia:** Troparion of {s_name}; Glory, both now... Dismissal Theotokion in Tone {tone_rom}."
            
        parts = []
        for c in res["components"]:
            typ = c.get("type", "")
            ref_key = c.get("ref_key", "")
            ref = self.humanize_key(ref_key)
            if "resurrectional" in typ:
                parts.append("the Sunday (resurrectional) troparion in the tone of the week")
            elif typ == "glory":
                parts.append(f"Glory... {ref}")
            elif "both_now" in typ:
                bn_text = "Glory, both now" if typ == "glory_both_now" else "Both now"
                if "theotokion" in ref.lower() or "theotokion" in ref_key.lower() or "day_" in ref_key.lower():
                    parts.append(f"{bn_text}... Theotokion")
                else:
                    parts.append(f"{bn_text}... {ref}")
            else:
                if "Troparion" in ref:
                    name = ref.replace("Troparion", "").strip()
                    if name.lower().startswith("of "):
                        parts.append(f"the troparion {name}" if name else "the troparion")
                    else:
                        parts.append(f"the troparion of the {name}" if name else "the troparion")
                else:
                    if ref.lower().startswith("of "):
                        parts.append(f"the troparion {ref}")
                    else:
                        parts.append(f"the troparion of the {ref}")
        return "**At the Dismissal Troparia:** We sing " + "; ".join(parts) + "."


    def _format_resolve_passion_vespers_readings(self, res, context):
        if not res:
            return ""
        prok = res.get("prokeimenon", {}).get("text", "")
        if self._is_missing(prok):
            prok = "Prokeimenon of Passion Vespers"
            
        paremia_1 = res.get("paremia_1", {})
        if self._is_missing(paremia_1.get("book")) or self._is_missing(paremia_1.get("chapter")):
            p1 = "Reading 1 of Passion Vespers"
        else:
            p1 = f"{paremia_1.get('book')} {paremia_1.get('chapter')}"

        paremia_2 = res.get("paremia_2", {})
        if self._is_missing(paremia_2.get("book")) or self._is_missing(paremia_2.get("chapter")):
            p2 = "Reading 2 of Passion Vespers"
        else:
            p2 = f"{paremia_2.get('book')} {paremia_2.get('chapter')}"

        paremia_3 = res.get("paremia_3", {})
        if self._is_missing(paremia_3.get("book")) or self._is_missing(paremia_3.get("chapter")):
            p3 = "Reading 3 of Passion Vespers"
        else:
            p3 = f"{paremia_3.get('book')} {paremia_3.get('chapter')}"

        epistle_data = res.get("epistle", {})
        if self._is_missing(epistle_data.get("book")) or self._is_missing(epistle_data.get("chapter")):
            epistle = "Epistle of Passion Vespers"
        else:
            epistle = f"{epistle_data.get('book')} {epistle_data.get('chapter')}"

        gospel = res.get("gospel", {}).get("content", "")
        if self._is_missing(gospel):
            gospel = "Gospel reading of Passion Vespers"
            
        g_sources = res.get("gospel", {}).get("sources", [])
        sources = ", ".join(g_sources) if g_sources else "Passion Gospels"
        return (
            f"At Passion Vespers:\n"
            f"  - Prokeimenon: '{prok}'\n"
            f"  - Paremia 1: {p1}\n"
            f"  - Paremia 2: {p2}\n"
            f"  - Paremia 3: {p3}\n"
            f"  - Epistle: {epistle}\n"
            f"  - Gospel: {gospel} (from {sources})"
        )

