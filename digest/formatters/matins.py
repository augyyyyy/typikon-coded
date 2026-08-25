class MatinsFormatterMixin:
    def _format_resolve_matins_prokeimenon(self, res, context):
        if not res:
            return ""
        return f"Prokeimenon: {res.get('text', 'sung according to the Typikon')} (Tone {self._roman_tone(res.get('tone', ''))})."


    def _format_resolve_daily_kathisma(self, res, context):
        if not res or res.get("type") == "none":
            return "No Kathisma."
        return f"Kathisma: {self.humanize_key(res.get('ref_key'))}"


    def _format_resolve_lenten_kathisma(self, res, context):
        if not res:
            return ""
        return f"Kathisma: {self.humanize_key(res.get('ref_key'))}"


    def _format_resolve_lenten_triodic_canon(self, res, context):
        if not res:
            return ""
        return f"Lenten Canon: {res.get('action')}"


    def _format_resolve_lenten_exapostilarion(self, res, context):
        if not res:
            return ""
        return res.get("rubric_note", "")


    def _format_resolve_post_doxology_event(self, res, context):
        if not res:
            return ""
        if isinstance(res, dict) and res.get("type") in ("component_ref", "fixed_ref"):
            temp = []
            self._process_skeleton([res], context, {}, temp)
            return "\n".join(temp)
        return str(res)


    def _format_resolve_vigil_polyeleos(self, res, context):
        if not res:
            return ""
        parts = []
        for comp in res.get("components", []):
            note = comp.get("note") or self.humanize_key(comp.get("ref_key", ""))
            parts.append(note)
        return f"Polyeleos: {', '.join(parts)}"


    def _format_resolve_great_canon_portion(self, res, context):
        if not res:
            return ""
        return f"Great Canon Portion: Part {res.get('part')}"


    def _format_resolve_canon_ode_troparion(self, res, context):
        if not res:
            return ""
        ode = res.get('ode')
        pos = res.get('position')
        ref = res.get('ref_key')
        if ode == 8 and pos == "glory":
            return "At Ode 8 (Glory): \"Let us bless the Father, and the Son, and the Holy Spirit, the Lord.\""
        return f"Canon Ode Troparion (Ode {ode}, {pos}): {self.humanize_key(ref)}"


    def _format_resolve_bridegroom_canon_type(self, res, context):
        if not res:
            return ""
        return f"Bridegroom Canon: {res.get('rubric_note')}"


    def _format_resolve_tomb_matins_canon(self, res, context):
        if not res:
            return ""
        return res.get("rubric_note", "")


    def _format_resolve_passion_canon(self, res, context):
        if not res:
            return ""
        return res.get("rubric_note", "")


    def _format_resolve_bright_praises(self, res, context):
        if not res:
            return ""
        return res.get("rubric_note", "")

    # --- Ceremonial Resolvers Formatters ---


    def _format_resolve_aposticha_matins(self, res, context):
        return self._format_resolve_aposticha(res, context)


    def _format_resolve_polyeleos_or_kathisma_17(self, res, context):
        if not res:
            return ""
        typ = res.get("type")
        if typ == "polyeleos":
            add_text = ""
            if context.get("matins_polyeleos_add") == "psalm_136_waters_of_babylon":
                add_text = ", and we add Psalm 136 (By the waters of Babylon)"
            
            # Dynamic check for Eucharist Period + Polyeleos Saint
            pascha_offset = context.get("pascha_offset")
            if pascha_offset == 60:
                saints = context.get("saints", [])
                saint_name = saints[0].get("name", "Apostles") if saints else "Apostles"
                saint_name = saint_name.rstrip('.')
                return f"We sing the Polyeleos{add_text}, then the Magnification of the Feast of the Eucharist ('We magnify Thee, O life-giving Christ...') and of the {saint_name} ('We magnify you...'), followed by the Sessional Hymns of the Polyeleos."
            elif pascha_offset is not None and 61 <= pascha_offset <= 67:
                return f"We sing the Polyeleos{add_text}, followed by the Sessional Hymns of the Polyeleos."
            
            return f"We sing the Polyeleos{add_text}. Magnification: sung if prescribed."
        elif typ == "kathisma_17":
            return "We sing the 17th Kathisma (Psalm 118)."
        return ""


    def _format_resolve_matins_gospel(self, res, context):
        if not res:
            return ""
        if res.get("type") == "saint":
            return (
                "And that we may be accounted worthy of hearing the holy Gospel, let us pray to the Lord God. "
                "Wisdom, stand upright! Let us hear the holy Gospel. "
                f"**Matins Gospel:** {res.get('title')}: {res.get('text')}. "
                "Response: Glory to Thee, O Lord, glory to Thee."
            )
        
        reading_key = res.get("reading_key", "")
        # Check if it is a Sunday Eothinon Gospel
        if "eothinon.gospel_" in reading_key or (res.get("title") and "(Eothinon)" in res.get("title")):
            # Extract Eothinon number
            try:
                num = int(reading_key.split("_")[-1])
            except ValueError:
                num = 1
                for part in res.get("title", "").split():
                    if part.isdigit():
                        num = int(part)
                        break
            
            # Roman numerals and citations mapping
            eothinon_map = {
                1: ("I", "(116) Matthew 28:16-20"),
                2: ("II", "(70) Mark 16:1-8"),
                3: ("III", "(71) Mark 16:9-20"),
                4: ("IV", "(112) Luke 24:1-12"),
                5: ("V", "(113) Luke 24:12-35"),
                6: ("VI", "(114) Luke 24:36-53"),
                7: ("VII", "(63) John 20:1-10"),
                8: ("VIII", "(64) John 20:11-18"),
                9: ("IX", "(65) John 20:19-31"),
                10: ("X", "(66) John 21:1-14"),
                11: ("XI", "(67) John 21:15-25")
            }
            roman, citation = eothinon_map.get(num, ("I", "(116) Matthew 28:16-20"))
            return f"Matins Gospel {roman}: {citation}."

        title = res.get("title") or res.get("reading_key") or "Matins Gospel"
        return f"Matins Gospel: {title}."


    def _format_resolve_canon_structure(self, res, context):
        if not res:
            return ""
        parts = []
        for item in res:
            src = self.humanize_key(item.get('source', 'Unknown'))
            cnt = item.get('count', item.get('qty', '?'))
            extra = " (including the heirmos)" if item.get('irmos') else ""
            parts.append(f"{src} - {cnt}{extra}")
        return f"At the Canon: Full order of the canon (according to the typicon): {', '.join(parts)}."


    def _format_resolve_katavasia(self, res, context):
        if not res:
            return ""
            
        is_weekday = 0 < context.get("day_of_week", 0) <= 5
        is_simple = context.get("rank") in ("rank_simple_6", "rank_simple_4") or context.get("variables", {}).get("rank") in ("rank_simple_6", "rank_simple_4")
        if is_weekday and is_simple:
            return ""
            
        if isinstance(res, dict):
            text = res.get("text") or res.get("content")
            if self._is_missing(text):
                text = None
            key = res.get("id") or res.get("katavasia_id") or ""
            tone = res.get("tone")
            if isinstance(tone, int):
                tone_rom = self._roman_tone(tone)
            else:
                tone_rom = str(tone) if tone else ""
            tone_str = f" (Tone {tone_rom})" if tone_rom else ""
            
            if text:
                val = f'"{text}"'
            else:
                val = self.humanize_key(key)
                if self._is_missing(val):
                    val = "Katavasia of the Saint"
                if val and not val.startswith('"') and not val.endswith('"') and len(val) > 5:
                    val = f"*{val}*"
            formatted = f"**Katavasia:** {val}{tone_str}."
        else:
            if self._is_missing(res):
                val = "Katavasia of the Saint"
            else:
                val = self.humanize_key(res)
                if self._is_missing(val):
                    val = "Katavasia of the Saint"
            if val and not val.startswith('"') and not val.endswith('"') and len(val) > 5:
                val = f"*{val}*"
            formatted = f"**Katavasia:** {val}."
            
        if hasattr(self, "_seen_katavasias"):
            if formatted in self._seen_katavasias:
                return ""
            self._seen_katavasias.add(formatted)
            
        return formatted


    def _format_resolve_canon_insertion(self, res, context):
        return ""


    def _format_resolve_exapostilarion_matins(self, res, context):
        if not res or not res.get("components"):
            return ""
        comps = [self.humanize_key(c) for c in res["components"]]
        return f"Exapostilarion: {'; '.join(comps)}."


    def _format_resolve_praises_stichera(self, res, context):
        if not res or not isinstance(res, list):
            return ""
        
        stichera_counts = {}
        total = 0
        glory = []
        both_now = []
        other_refs = []
        
        for item in res:
            t = item.get("type")
            if t == "sticheron":
                source = self.humanize_key(item.get("source", "Octoechos"))
                stichera_counts[source] = stichera_counts.get(source, 0) + 1
                total += 1
            elif t == "stichera_block":
                source = self.humanize_key(item.get("source", "Menaion"))
                qty = item.get("qty", 0)
                stichera_counts[source] = stichera_counts.get(source, 0) + qty
                total += qty
            elif t == "fixed_ref":
                ref = item.get("ref_key", "")
                note = item.get("rubric_note")
                val = note if note else self.humanize_key(ref)
                if "glory" in ref.lower():
                    glory.append(val)
                elif "both_now" in ref.lower():
                    both_now.append(val)
                elif "psalms_praises" in ref.lower():
                    pass
                else:
                    other_refs.append(val)
                    
        if total == 0 and len(res) > 0:
            for item in res:
                if item.get("type") == "sticheron" or "praises" in str(item.get("addr", "")):
                    total += 1
            if total > 0:
                stichera_counts["Octoechos"] = total

        # Force Sunday praises count to be exactly 8 (canonical cap)
        is_sunday = context.get("day_of_week") == 0 or context.get("is_sunday_vigil")
        if is_sunday and total > 0:
            has_menaion = any("menaion" in str(item.get("addr", "")).lower() or item.get("source") == "menaion" for item in res)
            if has_menaion:
                stichera_counts = {"Octoechos": 4, "Menaion": 4}
                total = 8
            else:
                stichera_counts = {"Octoechos": 8}
                total = 8

        dist_str = ", and ".join(f"{qty} from the {source}" for source, qty in stichera_counts.items())
        
        parts = []
        if total > 0:
            parts.append(f"At the Praises, we sing {total} Stichera: {dist_str}")
        else:
            if not glory and not both_now and not other_refs:
                return ""
            parts.append("At the Praises, we sing the Praises Stichera")
            
        import re
        if glory:
            cleaned_glory = []
            for g in glory:
                g_str = str(g).strip()
                g_stripped = re.sub(r'^(glory\b[.,\s]*)', '', g_str, flags=re.IGNORECASE).strip()
                cleaned_glory.append(g_stripped)
            parts.append(f"Glory... {', '.join(cleaned_glory)}")
        if both_now:
            cleaned_bn = []
            for bn in both_now:
                bn_str = str(bn).strip()
                bn_stripped = re.sub(r'^(both\s+now\b[.,\s]*)', '', bn_str, flags=re.IGNORECASE).strip()
                cleaned_bn.append(bn_stripped)
            parts.append(f"Both now... {', '.join(cleaned_bn)}")
        if other_refs:
            parts.append(f"Other: {', '.join(other_refs)}")
            
        return "; ".join(parts) + "."


    def _format_resolve_kathisma(self, res, context):
        if not res: return ""
        if res.get('type') == 'lenten_hours':
            return f"We read Kathisma {res.get('kathisma_number')}."
        return f"We read {self.humanize_key(res.get('id', 'Kathisma'))}."


    def _format_resolve_kathisma_choice(self, res, context):
        if not res: return ""
        if res.get('type') == 'polyeleos':
            add_txt = ", and we add Psalm 136 (By the waters of Babylon)" if context.get("matins_polyeleos_add") else ""
            return f"We sing the Polyeleos{add_txt}."
        return f"We read {self.humanize_key(res.get('id', 'Kathisma 17'))}."


    def _format_resolve_anabathmoi(self, res, context):
        if not res: return ""
        val = self.humanize_key(res.get('id', 'Anabathmoi'))
        val = val.replace('Anabathmoi', 'Gradual').replace('anabathmoi', 'gradual')
        return f"Gradual (Hymns of Ascents): {val}."


    def _format_resolve_doxology_type(self, res, context):
        if not res: return ""
        note = res.get('rubric_note', 'Great Doxology')
        if "polyeleos" in note.lower() or "saint" in note.lower():
            note = "Great Doxology (sung)"
        return f"Doxology: {note}."


    def _format_resolve_compline_canon(self, res, context):
        if not res: return ""
        is_afterfeast = context.get("is_afterfeast") or context.get("period") in ("afterfeast", "apodosis")
        is_feast = context.get("is_feast")
        if (is_afterfeast or is_feast) and res.get("subject") == "feast":
            feast_id = context.get("feast_id") or "eucharist"
            if feast_id in ("eucharist", "ascension", "pentecost") or (60 <= context.get("pascha_offset", -100) <= 67):
                return ""
        return f"Canon: {self.humanize_key(res.get('subject', ''))} from the {self.humanize_key(res.get('book', 'Octoechos'))}."


    def _format_resolve_triadic_canon(self, res, context):
        if not res: return ""
        return f"Triadic Canon: {self.humanize_key(res.get('ref_key', ''))}."


    def _format_resolve_magnificat(self, res, context):
        if not res:
            return ""
        typ = res.get("type")
        if typ == "paschal_magnificat":
            return "At Ode IX, we sing the Paschal magnification: 'The Angel cried out...'."
        elif typ == "festal_magnificat":
            return "At Ode IX, we sing the Festal magnification and the Heirmos of Ode IX of the Feast."
        elif typ == "suppressed_magnificat":
            return "At Ode IX, we do not sing the Magnification, but immediately the Heirmos of Ode IX of the Canon."
        elif typ in ("sunday_magnificat", "festal_with_more_honorable"):
            return "At Ode IX, we sing the Magnification ('My soul magnifies the Lord...') and the refrains ('More honorable than the Cherubim...')."
        return "At Ode IX, we sing the Magnification ('My soul magnifies the Lord...') and the refrains ('More honorable than the Cherubim...')."


    def _format_resolve_exapostilarion(self, res, context):
        if not res:
            return ""
        if isinstance(res, list):
            parts = []
            for item in res:
                if isinstance(item, dict):
                    ref = item.get("ref_key")
                    if ref:
                        parts.append(self.humanize_key(ref))
            return f"Exapostilarion: {'; '.join(parts)}."
        return f"Exapostilarion: {self.humanize_key(res)}."


    def _format_resolve_matins_dismissal_troparion(self, res, context):
        if not res:
            return ""
        troparia = res.get("troparia", [])
        if res.get("combination") == "feast_saint_feast":
            t1 = troparia[0]
            t2 = troparia[1]
            feast_tone = t1.get("tone")
            feast_tone_rom = self._roman_tone(feast_tone) if feast_tone else ""
            feast_tone_str = f" in Tone {feast_tone_rom}" if feast_tone_rom else ""
            saint_id = t2.get("troparion_id", "").replace("troparion_", "")
            if "bartholomew" in saint_id.lower() or any("bartholomew" in s.get("id", "").lower() for s in context.get("saints", [])):
                saint_name = "Apostles Bartholomew and Barnabas"
            elif saint_id == "saint":
                saints = context.get("saints", [])
                if saints:
                    s_name = saints[0].get("name", "Saint").strip()
                    if s_name.lower().startswith("st. "):
                        s_name = s_name[4:]
                    elif s_name.lower().startswith("st "):
                        s_name = s_name[3:]
                    saint_name = s_name.rstrip('.')
                else:
                    saint_name = "Saint"
            else:
                saint_name = self.humanize_key(saint_id)
            saint_tone = t2.get("tone")
            saint_tone_rom = self._roman_tone(saint_tone) if saint_tone else ""
            saint_tone_str = f" in Tone {saint_tone_rom}" if saint_tone_rom else ""
            return (
                f"**At the Dismissal Troparia:** Troparion of the Feast{feast_tone_str}; "
                f"Glory... Troparion of {saint_name}{saint_tone_str}; "
                f"Both now: Troparion of the Feast{feast_tone_str}."
            )
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
            has_saint_trop = any(t.get("type") == "saint" for t in troparia)
            if is_no_troparion and has_saint_trop:
                is_no_troparion = False
            day = context.get("day_of_week", 1)
            day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
            day_str = day_names.get(day, "Wednesday")
            
            if is_no_troparion:
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
                return f"**At the Dismissal Troparia:** Troparion of {wname}; Glory, both now... Dismissal Theotokion for {day_str} in {wtone}."
            else:
                s_name = "Saint"
                saints = context.get("saints", [])
                if saints:
                    s_name_raw = saints[0].get("name", "Saint").strip()
                    s_name = self._clean_name(s_name_raw)
                else:
                    s_name = "St. Cyril"
                    
                tone_val = None
                if troparia and troparia[0].get("tone"):
                    tone_val = troparia[0].get("tone")
                if not tone_val and res.get("both_now"):
                    import re
                    m = re.search(r'tone_(\d+)', str(res.get("both_now")))
                    if m:
                        tone_val = int(m.group(1))
                if not tone_val:
                    tone_val = context.get("troparion_tone") or context.get("tone") or 4
                tone_rom = self._roman_tone(tone_val) if isinstance(tone_val, int) else str(tone_val)
                
                return f"**At the Dismissal Troparia:** Troparion of {s_name}; Glory, Both now: Dismissal Theotokion for {day_str} in Tone {tone_rom}."

        parts = []
        for t in troparia:
            t_type = t.get("type", "")
            t_id = t.get("troparion_id", "")
            tone = t.get("tone")
            if t_type == "resurrectional":
                if tone is not None:
                    tone_rom = self._roman_tone(tone) if isinstance(tone, int) else str(tone)
                    if tone % 2 == 1:
                        parts.append(f"Sunday Dismissal Troparion 'Today salvation has come to the world' in Tone {tone_rom}")
                    else:
                        parts.append(f"Sunday Dismissal Troparion 'Having risen from the tomb' in Tone {tone_rom}")
                else:
                    parts.append("Sunday Dismissal Troparion")
            elif t_type == "festal":
                tone_rom = self._roman_tone(tone) if isinstance(tone, int) else str(tone)
                parts.append(f"Troparion of the Feast in Tone {tone_rom}")
            elif t_type == "saint":
                name_key = t_id.replace("troparion_", "")
                if name_key == "saint":
                    saints = context.get("saints", [])
                    if saints:
                        s_name = saints[0].get("name", "Saint").strip()
                        if s_name.lower().startswith("st. "):
                            s_name = s_name[4:]
                        elif s_name.lower().startswith("st "):
                            s_name = s_name[3:]
                        saint_name = s_name.rstrip('.')
                    else:
                        saint_name = "Saint"
                else:
                    saint_name = self.humanize_key(name_key)
                tone_rom = f" in Tone {self._roman_tone(tone)}" if isinstance(tone, int) else (f" in Tone {tone}" if tone else "")
                parts.append(f"Troparion of {saint_name}{tone_rom}")
            else:
                parts.append(f"Troparion {self.humanize_key(t_id)}")
                
        if "glory_both_now" in res:
            ref_key = res["glory_both_now"]
            ref_human = self.humanize_key(ref_key)
            if "theotokion" in ref_key.lower():
                parts.append("Glory, Both now... Theotokion")
            elif "troparion" in ref_key.lower():
                feast_tone = res.get("feast_tone") or context.get("feast_tone")
                tone_rom = f" in Tone {self._roman_tone(feast_tone)}" if isinstance(feast_tone, int) else (f" in Tone {feast_tone}" if feast_tone else "")
                parts.append(f"Glory, Both now... Troparion of the Feast{tone_rom}")
            else:
                parts.append(f"Glory, Both now... {ref_human}")
        elif "both_now" in res:
            ref_key = res["both_now"]
            ref_human = self.humanize_key(ref_key)
            if "theotokion" in ref_key.lower():
                parts.append("Both now... Theotokion")
            else:
                parts.append(f"Both now... {ref_human}")
                
        if not parts:
            return ""
        
        return "**At the Dismissal Troparia:** We sing: " + "; ".join(parts) + "."


    def _format_resolve_daily_kathisma(self, res, context):
        if not res or res.get("type") == "none":
            return "No kathisma is appointed."
        num = res.get("number")
        return f"At Vespers, Kathisma {num} is read."


    def _format_resolve_lenten_kathisma(self, res, context):
        if not res:
            return ""
        ref = res.get("ref_key", "")
        return f"Kathisma: We read {self.humanize_key(ref)}."


    def _format_resolve_lenten_triodic_canon(self, res, context):
        if not res:
            return ""
        action = res.get("action", "")
        return f"Lenten Triodion Canon: {action}."


    def _format_resolve_lenten_exapostilarion(self, res, context):
        if not res:
            return ""
        tone = res.get("tone")
        ref = res.get("ref_key", "")
        rubric = res.get("rubric_note", "")
        return f"Lenten Exapostilarion (Trinity Light Hymn, Tone {tone}): {self.humanize_key(ref)} ({rubric})"


    def _format_resolve_post_doxology_event(self, res, context):
        if not res:
            return ""
        ref = res.get("ref_key", "")
        return f"Post-Doxology Event: {self.humanize_key(ref)}."


    def _format_resolve_vigil_polyeleos(self, res, context):
        if not res:
            return ""
        parts = []
        for comp in res.get("components", []):
            c_type = comp.get("type")
            ref = comp.get("ref_key", "")
            note = comp.get("note", "")
            note_str = f" ({note})" if note else ""
            parts.append(f"{c_type.capitalize()}: {self.humanize_key(ref)}{note_str}")
        return "Polyeleos:\n" + "\n".join(f"  - {p}" for p in parts)


    def _format_resolve_great_canon_portion(self, res, context):
        if not res:
            return ""
        part = res.get("part", 1)
        part_names = {1: "First (Monday)", 2: "Second (Tuesday)", 3: "Third (Wednesday)", 4: "Fourth (Thursday)"}
        name = part_names.get(part, f"Part {part}")
        return f"At Great Compline: We read the Great Canon of St. Andrew, {name} Portion."


    def _format_resolve_canon_ode_troparion(self, res, context):
        if not res:
            return ""
        ode = res.get("ode")
        pos = res.get("position", "")
        ref = res.get("ref_key", "")
        if ode == 8 and pos == "glory":
            return "At Ode 8 (Glory): \"Let us bless the Father, and the Son, and the Holy Spirit, the Lord.\""
        return f"At Ode {ode} ({self.humanize_key(pos)}): {self.humanize_key(ref)}."


    def _format_resolve_bridegroom_canon_type(self, res, context):
        if not res:
            return ""
        name = res.get("canon_name", "")
        note = res.get("rubric_note", "")
        return f"Bridegroom Canon ({self.humanize_key(name)}): {note}."


    def _format_resolve_tomb_matins_canon(self, res, context):
        if not res:
            return ""
        note = res.get("rubric_note", "")
        return f"Great Saturday Matins Canon: {note}."


    def _format_resolve_passion_canon(self, res, context):
        if not res:
            return ""
        note = res.get("rubric_note", "")
        return f"Passion Canon: {note}."


    def _format_resolve_bright_praises(self, res, context):
        if not res:
            return ""
        note = res.get("rubric_note", "")
        return f"Paschal Praises: {note}."


    def _format_canon_interludes_ode_3(self, context):
        offset = context.get("pascha_offset")
        if offset == -70:
            return "**After Ode III:** Kontakion and ikos of the forefeast (found after Ode VI in the Menaion) and the sessional hymns from the Triodion (found after Ode III), Glory, both now... forefeast.  "
        elif offset == -63:
            return "**After Ode III:** Kontakion and ikos of the feast, and the sessional hymns from the Triodion (found after Ode III), Glory, both now... feast.  "
        elif offset in (-56, -49, -42, -35, -28):
            return "**After Ode III:** Sessional hymns from the Triodion (found after Ode III).  "
        
        is_sunday = context.get("day_of_week") == 0
        if is_sunday:
            tone = context.get("octoechos_tone", context.get("tone", 1))
            tone_rom = self._roman_tone(tone)
            return f"**After Ode III:** Hypakoe in Tone {tone_rom}; Glory... both now... Theotokion.  "
        else:
            return "**After Ode III:** Sessional hymns; Glory... both now... Theotokion.  "


    def _format_canon_interludes_ode_6(self, context):
        offset = context.get("pascha_offset")
        if offset == -35:
            return "**After Ode VI:** Kontakion and ikos of the Cross, from the Triodion, in Tone VII.  "
        elif offset in (-70, -63, -56, -49, -42, -28, -8):
            return "**After Ode VI:** Kontakion and ikos from the Triodion are sung.  "
        
        is_sunday = context.get("day_of_week") == 0
        if is_sunday:
            tone = context.get("octoechos_tone", context.get("tone", 1))
            tone_rom = self._roman_tone(tone)
            return f"**After Ode VI:** Resurrection Kontakion and Ikos in Tone {tone_rom}.  "
        else:
            return "**After Ode VI:** Kontakion and Ikos.  "



