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
        comps = []
        for c in res["components"]:
            if isinstance(c, dict):
                ref = c.get("ref_key") or c.get("source") or ""
                chorus = c.get("chorus")
                if chorus:
                    comps.append(f'"{ref}" ({chorus})')
                elif ref:
                    comps.append(self.humanize_key(ref))
            else:
                comps.append(self.humanize_key(c))
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
        subj = self.humanize_key(res.get('subject', ''))
        if subj.lower() == "theotokos":
            subj = "To the Theotokos"
        return f"**Canon:** {subj} from the {self.humanize_key(res.get('book', 'Octoechos'))}."


    def _format_resolve_triadic_canon(self, res, context):
        if not res: return ""
        return f"Triadic Canon: {self.humanize_key(res.get('ref_key', ''))}."


    def _format_resolve_magnificat(self, res, context):
        if not res:
            return ""
        typ = res.get("type")
        if typ == "paschal_magnificat":
            return "**At Ode IX:** We sing the Paschal magnification: 'The Angel cried out...'."
        elif typ == "festal_magnificat":
            return "**At Ode IX:** We sing the Festal magnification and the Heirmos of Ode IX of the Feast."
        elif typ == "suppressed_magnificat":
            return "**At Ode IX:** We do not sing the Magnification, but immediately the Heirmos of Ode IX of the Canon."
        elif typ in ("sunday_magnificat", "festal_with_more_honorable"):
            return "**At Ode IX:** We sing the Magnification ('My soul magnifies the Lord...') and the refrains ('More honorable than the Cherubim...')."
        return "**At Ode IX:** We sing the Magnification ('My soul magnifies the Lord...') and the refrains ('More honorable than the Cherubim...')."


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
        if num == 1:
            return "At Vespers, Kathisma 1 ('Blessed is the man') is read."
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
        if "cross" in ref.lower() or "elevation" in ref.lower() or "exaltation" in ref.lower():
            return (
                "**Ceremony of the Elevation of the Precious and Life-Giving Cross:**\n"
                "After the Great Doxology (sung), the celebrant carries the Precious Cross in solemn procession to the center of the temple, chanting *\"Wisdom! Stand aright!\"*\n"
                "The priest elevates the Cross towards the four cardinal directions (East, West, South, North, and East again), while the choir sings *\"Lord, have mercy\"* 100 times for each station (500 times total).\n"
                "**Veneration of the Cross:** Celebrant and faithful venerate the Cross while singing the hymn *\"Before Your Cross, we bow down in worship, O Master, and Your holy Resurrection we glorify\"* (thrice)."
            )
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

    def _format_bridegroom_matins(self, enriched, rubrics):
        pascha_off = enriched.get("pascha_offset")
        day_names = {-6: "Great and Holy Monday", -5: "Great and Holy Tuesday", -4: "Great and Holy Wednesday"}
        day_str = day_names.get(pascha_off, "Holy Week")
        
        gospel_pericopes = {
            -6: "**Matthew §84 [21:18–43]** (The Cursing of the Fig Tree and Parable of the Wicked Vinedressers)",
            -5: "**Matthew §90 [22:15–23:39]** (Tribute to Caesar, Resurrection, and Seven Woes against the Pharisees)",
            -4: "**John §41 [12:17–50]** (The Greeks seek Jesus and the Son of Man glorified)"
        }
        gospel_str = gospel_pericopes.get(pascha_off, "**Holy Gospel of the Day**")
        
        lines = [
            "*At Alleluia:* We sing Alleluia in Tone VIII, with the special melody of the Bridegroom Troparion.",
            "**Dismissal Troparia at Alleluia:** Troparion *\"Behold, the Bridegroom comes at midnight, and blessed is the servant whom He shall find watchful...\"* (thrice, slowly in Tone VIII).",
            "**Kathismata:** Kathismata 4, 5, and 6 (Monday); 9, 10, and 11 (Tuesday); 14, 15, and 16 (Wednesday) are read. After each Kathisma, Sessional Hymns from the Holy Week Triodion.",
            f"**Holy Gospel:** {gospel_str}; then Psalm 50 and immediately the Canon.",
            f"**At the Canon:** Triode / Diode of {day_str} from the Holy Week Triodion. Heirmoi twice, Troparia on 12. Katavasia: Heirmos of the canon. (Menaion is suppressed).",
            "**After Ode III:** Sessional Hymn from the Triodion.",
            "**After Ode VI:** Kontakion and Ikos from the Triodion.",
            "**At Ode IX:** The Magnification is suppressed; instead we sing immediately the Heirmos of Ode IX. (Priest censes as at Great Matins).",
            "**Exaposteilarion (The Bridal Chamber):** *\"Thy bridal chamber I see adorned, O my Savior, and I have no wedding garment that I may enter there. O Giver of Light, enlighten the vesture of my soul and save me.\"* (thrice in Tone III).",
            "**At the Praises:** We sing 4 Stichera from the Holy Week Triodion; Small Doxology (read).",
            "**At the Aposticha:** We sing the Aposticha from the Holy Week Triodion with specific verses.",
            "**At the Dismissal Troparia:** After 'It is a good thing' and the Trisagion prayers, Troparion *\"Behold, the Bridegroom comes at midnight...\"* (once). Prayer of St. Ephrem with 4 great prostrations. 1st Hour follows immediately without dismissal."
        ]
        return "\n\n".join(lines)

    def _format_holy_thursday_matins(self, enriched, rubrics):
        lines = [
            "*At Alleluia:* We sing Alleluia in Tone VIII, with the special melody of the Troparion.",
            "**Dismissal Troparia at Alleluia:** Troparion *\"When the glorious disciples were enlightened at the washing of the feet...\"* (twice); Glory, Both now: once more the same.",
            "There are no Kathismata or Sessional Hymns, but immediately the Holy Gospel: **Luke §108 [22:39–23:1]**; then Psalm 50 and immediately the Canon.",
            "**At the Canon:** Canon of St. Cosmas on 6: Heirmoi twice, Troparia on 6 with the refrain *\"Glory to Thee, our God, glory to Thee\"*. Katavasia after each ode: Heirmos of the same canon once, both choirs together.",
            "**After Ode III:** Sessional hymn from the Triodion.",
            "**After Ode VI:** Kontakion and Ikos of Great and Holy Thursday.",
            "**At Ode IX:** The Magnification is suppressed; instead we sing immediately the Heirmos of Ode IX (*\"Come, O faithful, let us enjoy the Master's hospitality and the table of immortality in the upper room...\"*).",
            "**Exaposteilarion:** *\"Thy bridal chamber I see adorned, O my Savior, and I have no wedding garment that I may enter there. O Giver of Light, enlighten the vesture of my soul and save me.\"* (twice); Glory, Both now: once more the same.",
            "**At the Praises:** We sing 4 Stichera from the Triodion; Small Doxology (read).",
            "**At the Aposticha:** We sing the Aposticha from the Triodion with specific verses.",
            "**At the Dismissal Troparia:** Troparion *\"When the glorious disciples were enlightened at the washing of the feet\"* (without Theotokion). 1st Hour follows."
        ]
        return "\n\n".join(lines)

    def _format_holy_friday_matins(self, enriched, rubrics):
        lines = [
            "*At Alleluia:* Troparion *\"When the glorious disciples\"* (thrice, Tone VIII).",
            "**The Twelve Passion Gospels (The Twelve Holy Gospels of the Passion)** are read throughout the service, interspersed with the 15 Antiphons and Sidalny:",
            "  1. **John 13:31–18:1** (Christ's farewell discourse to His disciples)",
            "  2. **John 18:1–28** (The betrayal in Gethsemane and interrogation before Annas)",
            "  3. **Matthew 26:57–75** (Christ before Caiaphas and Peter's denial)",
            "  4. **John 18:28–19:16** (Christ before Pontius Pilate)",
            "  5. **Matthew 27:3–32** (The death of Judas and the Crown of Thorns)",
            "  6. **Mark 15:16–32** (The Crucifixion at Golgotha)",
            "  7. **Matthew 27:33–54** (Christ gives up His spirit on the Cross)",
            "  8. **Luke 23:32–49** (The repentance of the Wise Thief)",
            "  9. **John 19:25–37** (The Mother of God at the Cross and the Piercing with the Lance)",
            "  10. **Mark 15:43–47** (Joseph of Arimathea asks for the Body of Jesus)",
            "  11. **John 19:38–42** (The Burial of Christ by Joseph and Nicodemus)",
            "  12. **Matthew 27:62–66** (The Guard set at the Sepulchre)",
            "**The Beatitudes** with 8 Troparia; Canon of Holy Friday (Triode by St. Cosmas); Exaposteilarion: *\"The wise thief in a single moment...\"* (3x); Praises on 4; Aposticha; Dismissal of Holy Friday."
        ]
        return "\n\n".join(lines)

    def _format_holy_saturday_matins(self, enriched, rubrics):
        lines = [
            "*At God is the Lord in Tone II:* Troparia *\"The noble Joseph\"*, Glory... *\"When Thou didst descend unto death\"*, Both now... *\"The angel stood by the tomb\"*.",
            "**Station at Psalm 118 with the Three Stases of the Lamentations (Encomia)** sung before the Holy Shroud (Epitaphios / Plashchanytsia):",
            "  - 1st Stasis: *\"In a grave they laid Thee, O my Life and Christ...\"*",
            "  - 2nd Stasis: *\"Right it is to praise Thee, Giver of Life...\"*",
            "  - 3rd Stasis: *\"Every generation, O my Christ, offers praises to Thy burial...\"*",
            "**Evlogitaria of the Resurrection:** *\"Blessed are You, O Lord, teach me Your statutes... The angelic council was amazed\"*.",
            "**Canon of Holy Saturday:** *\"Do not weep for Me, O Mother\"* (Tone VI). Katavasia: Heirmos of the same canon.",
            "**At the Praises:** Stichera on 4 from the Triodion.",
            "**Great Doxology (sung):** Procession of the Holy Shroud (Plashchanytsia) around the church while singing the Trisagion.",
            "**Readings after the Procession:**",
            "  - *Prokeimenon (Tone 4):* \"Arise, O Lord, help us and redeem us for Your name's sake.\"",
            "  - *Paremia:* **Ezekiel 37:1–14** (The Vision of the Dry Bones)",
            "  - *Epistle:* **1 Corinthians 5:6–8; Galatians 3:13–14** (Christ our Passover is sacrificed for us)",
            "  - *Alleluia (Tone 5):* \"Let God arise, and let His enemies be scattered.\"",
            "  - *Gospel:* **Matthew 27:62–66** (The Setting of the Guard at the Sepulchre)"
        ]
        return "\n\n".join(lines)

    def _format_paschal_matins(self, enriched, rubrics):
        canon_line = "**Paschal Canon of St. John of Damascus (Tone I):** *\"This is the day of Resurrection, let us be illumined, O people...\"* Katavasia: Heirmos of the same ode. At each ode, the priest censes with the Paschal greeting *\"Christ is risen!\"*"
        if str(enriched.get("date", "")).endswith("-03-25") or enriched.get("scenario_id") == "collision_annunciation_pascha_sunday" or enriched.get("feast_id") == "annunciation" or "annunciation" in str(enriched.get("title", "")).lower():
            canon_line = "**At the Canon:** Paschal Canon with irmos on 8 and of the Annunciation with irmos on 8. Katavasia: Heirmos of the Paschal Canon."

        lines = [
            "**Paschal Procession:** The clergy and faithful circle the church with candles, chanting *\"Thy Resurrection, O Christ our Savior, angels hymn in the heavens...\"*",
            "**Opening of Matins:** At the church doors: *\"Glory to the Holy, Consubstantial, Life-Creating and Undivided Trinity...\"* and the Paschal Troparion *\"Christ is risen from the dead, trampling down death by death, and upon those in the tombs bestowing life\"* (thrice by clergy, then by choir with the Paschal Verses *\"Let God arise...\"*).",
            canon_line,
            "**Hypakoe (Tone IV):** *\"When they who were with Mary came, anticipating the dawn, and found the stone rolled away from the tomb...\"*",
            "**Kontakion & Ikos (Tone VIII):** *\"Though You went down into the tomb, O Immortal One, yet You destroyed the power of Hades...\"*",
            "**Exaposteilarion (thrice):** *\"Having fallen asleep in the flesh as a mortal, O King and Lord, on the third day You rose again...\"*",
            "**At the Praises:** 4 Stichera of the Resurrection in Tone I, followed by the **Paschal Stichera** (*\"Let God arise... Today a sacred Pascha is revealed to us...\"*).",
            "**Paschal Homily of St. John Chrysostom** read by the celebrant (*\"If any man be devout and love God, let him enjoy this fair and radiant triumphal feast...\"*)."
        ]
        return "\n\n".join(lines)



