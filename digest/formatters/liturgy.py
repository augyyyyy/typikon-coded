class LiturgyFormatterMixin:
    def _format_qr_readings(self, context, rubrics):
        try:
            res = self.engine.resolve_liturgy_readings(context, rubrics)
        except Exception as e:
            return f"[ERROR: resolve_liturgy_readings failed - {e}]"
            
        readings_data = res.get("readings")
        if not readings_data:
            return ""
            
        if isinstance(readings_data, str):
            return f"**Readings:** {self.humanize_key(readings_data)}"
            
        # Check hydration of each reading block
        def is_hydrated(reading):
            for k in ["prokeimenon", "epistle", "alleluia", "gospel", "communion_hymn"]:
                p = reading.get(k, {})
                if p:
                    if p.get("text") or p.get("content"):
                        return True
                    ref_key = p.get("ref_key", "")
                    if ref_key and ref_key in self.engine.text_db:
                        entry = self.engine.text_db[ref_key]
                        if entry.get("text") or entry.get("content") or entry.get("title"):
                            return True
            return False
            
        hydrated_any = any(is_hydrated(r) for r in readings_data)
        if hydrated_any:
            readings_data = [r for r in readings_data if is_hydrated(r)]
            
        prokeimena_lines = []
        epistle_lines = []
        alleluia_lines = []
        gospel_lines = []
        
        for idx, reading in enumerate(readings_data):
            p = reading.get("prokeimenon", {})
            if p:
                tone = p.get("tone")
                t_str = f"Tone {self._roman_tone(tone)}" if tone else ""
                text = p.get("text") or p.get("content")
                if len(readings_data) > 1:
                    label = "Prokeimenon (Feast - sung twice)" if idx == 0 else "Prokeimenon (Saint - sung once, without verse)"
                else:
                    label = "Prokeimenon"
                if text:
                    text_clean = text.strip('"').rstrip('.')
                    p_str = f"**{label}:** {t_str}: \"{text_clean}\"".replace(" :", ":").replace("::", ":").strip()
                else:
                    ref = self.humanize_key(p.get("ref_key", ""))
                    ref_clean = ref.replace("Prokimenon", "").replace("Prokeimenon", "").strip()
                    ref_key_lower = p.get("ref_key", "").lower()
                    if not ref_clean or ref_clean.lower() in ("prokeimenon", "prokeimenon_daily") or "day_" in ref_key_lower or "day " in ref_clean.lower():
                        p_str = f"**{label}:** of the day{', ' + t_str if t_str else ''}."
                    else:
                        p_str = f"**{label}:** {t_str}: \"{ref_clean}...\"".replace(" :", ":").replace("::", ":").strip()
                prokeimena_lines.append(p_str)
                    
            e = reading.get("epistle", {})
            if e:
                text = e.get("text") or e.get("content")
                if text:
                    ref = text
                else:
                    ref = self.humanize_key(e.get("ref_key", ""))
                    ref_key_lower = e.get("ref_key", "").lower()
                    if not ref or ref.lower() in ("epistle", "epistle_daily", "apostol.weekday", "weekday") or "day_" in ref_key_lower or "day " in ref.lower():
                        ref = "of the day"
                epistle_lines.append(f"**Epistle:** {ref}")
                
            a = reading.get("alleluia", {})
            if a:
                tone = a.get("tone") or (p.get("tone") if p else None)
                t_str = f"Tone {self._roman_tone(tone)}" if tone else ""
                is_weekday = 0 < context.get("day_of_week", 0) <= 5
                is_simple = context.get("rank") in ("rank_simple_6", "rank_simple_4") or context.get("variables", {}).get("rank") in ("rank_simple_6", "rank_simple_4")
                if is_weekday and is_simple:
                    a_str = f"**Alleluia:** {t_str}, with verses of the day." if t_str else "**Alleluia:** with verses of the day."
                else:
                    text = a.get("text") or a.get("content")
                    if text:
                        a_str = f"**Alleluia:** {t_str}, with verses: \"{text}\"."
                    else:
                        verses = a.get("verses")
                        if verses:
                            vs_str = "; ".join(verses)
                            v_str = f", with verses: \"{vs_str}\""
                            a_str = f"**Alleluia:** {t_str}{v_str}."
                        else:
                            ref = self.humanize_key(a.get("ref_key", ""))
                            ref_clean = ref.replace("Alleluia", "").strip()
                            ref_key_lower = a.get("ref_key", "").lower()
                            if not ref_clean or ref_clean.lower() in ("alleluia", "alleluia_daily") or "day_" in ref_key_lower or "day " in ref_clean.lower() or ref_clean.lower() == "weekday":
                                a_str = f"**Alleluia:** of the day{', ' + t_str if t_str else ''}."
                            else:
                                a_str = f"**Alleluia:** {t_str}".strip()
                alleluia_lines.append(a_str)
                
            g = reading.get("gospel", {})
            if g:
                text = g.get("text") or g.get("content")
                if text:
                    ref = text
                else:
                    ref = self.humanize_key(g.get("ref_key", ""))
                    ref_key_lower = g.get("ref_key", "").lower()
                    if not ref or ref.lower() in ("gospel", "gospel_daily", "evangelion.weekday", "weekday") or "day_" in ref_key_lower or "day " in ref.lower():
                        ref = "of the day"
                gospel_lines.append(f"**Gospel:** {ref}")
                
        lines = prokeimena_lines + epistle_lines + alleluia_lines + gospel_lines
                
        try:
            meg_res = self.engine.resolve_liturgy_megalynarion(context, rubrics)
            if meg_res:
                formatted_meg = self._format_resolve_liturgy_megalynarion(meg_res, context)
                if formatted_meg:
                    clean_meg = formatted_meg.replace("Instead of 'It is truly proper':", "").strip()
                    lines.append(f"**Instead of 'It is truly proper':** {clean_meg}")
        except Exception as e:
            pass
            
        try:
            kin_res = self.engine.resolve_communion_hymn(context, rubrics)
            if kin_res and kin_res.get("text"):
                lines.append(f"**Communion Hymn:** \"{kin_res['text']}\"")
        except Exception as e:
            pass
            
        return "\n".join(lines)


    def _format_resolve_beatitudes(self, res, context):
        if not res:
            return ""
        note = res.get("note", "Beatitudes")
        stichera_parts = []
        for s in res.get("stichera", []):
            stichera_parts.append(f"{s.get('count')} from {self.humanize_key(s.get('source'))}")
        if stichera_parts:
            return f"Beatitudes: {note} ({', '.join(stichera_parts)})"
        return f"Beatitudes: {note}"


    def _format_resolve_basil_megalynarion(self, res, context):
        if not res:
            return ""
        rubric = res.get("rubric")
        if rubric:
            return f"Basil Megalynarion: {rubric} ({self.humanize_key(res.get('ref_key'))})"
        text = res.get("text")
        if text:
            return f"Basil Megalynarion: {text}"
        return f"Basil Megalynarion: {self.humanize_key(res.get('ref_key'))}"


    def _format_resolve_presanctified_readings(self, res, context):
        if not res:
            return ""
        parts = []
        for r in res.get("sequence", []):
            r_type = r.get("type")
            if r_type == "prokeimenon":
                parts.append(f"Prokeimenon: {self.humanize_key(r.get('ref_key', ''))}")
            elif r_type == "paremia":
                parts.append(f"Paremia ({r.get('book', 'OT')}): {self.humanize_key(r.get('ref_key', ''))}")
            elif r_type == "exclamation":
                parts.append(f"Exclamation: {r.get('text', '')} (Posture: {r.get('rubric', {}).get('response', '')})")
                
        if res.get("has_feast_readings"):
            fr = res.get("feast_readings", {})
            ep = self.humanize_key(fr.get("epistle", {}).get("ref_key", ""))
            gosp = self.humanize_key(fr.get("gospel", {}).get("ref_key", ""))
            parts.append(f"Feast Readings - Epistle: {ep}, Gospel: {gosp}")
            
        return "At the Paremias: " + "; ".join(parts) + "."


    def _format_resolve_vesperal_liturgy_readings(self, res, context):
        if not res:
            return ""
        parts = []
        for comp in res.get("components", []):
            c_type = comp.get("type")
            ref_key = comp.get("ref_key", "")
            if c_type == "reading":
                source = comp.get("source", "")
                parts.append(f"{source.capitalize()}: {self.humanize_key(ref_key)}")
            elif c_type == "prokeimenon":
                parts.append(f"Prokeimenon: {self.humanize_key(ref_key)}")
            elif c_type == "alleluia":
                parts.append(f"Alleluia: {self.humanize_key(ref_key)}")
        
        meta = res.get("source_metadata", {})
        vesperal_id = self.humanize_key(meta.get("vesperal_id", ""))
        return f"Vesperal Liturgy Readings ({vesperal_id}): " + "; ".join(parts) + "."


    def _format_resolve_liturgy_antiphons(self, res, context):
        if res and res.get("type") == "festal_antiphons":
            return "Festal Antiphons."
        
        try:
            beat_res = self.engine.resolve_beatitudes(context)
            if beat_res and beat_res.get("stichera"):
                parts = []
                for s in beat_res["stichera"]:
                    src = s.get("source", "")
                    cnt = s.get("count", 0)
                    parts.append(f"{self.humanize_key(src)} - {cnt}")
                if parts:
                    total_qty = sum(s.get("count", 0) for s in beat_res["stichera"])
                    return f"Psalms of Typica; Beatitudes on {total_qty}: {', '.join(parts)}."
        except Exception:
            pass

        is_weekday = 0 < context.get("day_of_week", 0) <= 5
        is_simple = context.get("rank") in ("rank_simple_6", "rank_simple_4") or context.get("variables", {}).get("rank") in ("rank_simple_6", "rank_simple_4")
        if is_weekday and is_simple:
            return "Psalms of Typica; Beatitudes on 6: 3 from the Octoechos, 3 from Ode III of the Saint."
        return "Psalms of Typica; Beatitudes."


    def _format_resolve_liturgy_alleluia(self, res, context):
        if not res:
            return ""
        tone = res.get("tone")
        if tone is None or str(tone).lower() == "none":
            return ""
        tone_roman = self._roman_tone(tone) if isinstance(tone, int) else str(tone)
        tone_str = f"Tone {tone_roman}" if tone_roman else ""
        
        verses = res.get("verses", [])
        if verses:
            vs_str = "; ".join(verses)
            return f"**Alleluia:**  \n> {tone_str}: \"{vs_str}\"."
            
        is_weekday = 0 < context.get("day_of_week", 0) <= 5
        is_simple = context.get("rank") in ("rank_simple_6", "rank_simple_4") or context.get("variables", {}).get("rank") in ("rank_simple_6", "rank_simple_4")
        if is_weekday and is_simple:
            return f"**Alleluia:**  \n> {tone_str}, with verses of the day."
            
        return f"**Alleluia:**  \n> sung in Tone {tone_roman}."


    def _format_resolve_liturgy_megalynarion(self, res, context):
        if not res:
            return ""
        if res.get("text"):
            text = res.get("text")
            if text and not text.startswith('*') and not text.endswith('*') and len(text) > 2:
                text = f"*{text}*"
            return f"**Instead of 'It is truly proper':**  \n> {text}."
        elif res.get("type") == "irmos_ode_9" or res.get("ref_key") == "festal_zadostoinyk" or res.get("type") == "variable":
            return "**Instead of 'It is truly proper':**  \n> we sing the Heirmos of Ode 9 of the Canon."
        return ""


    def _format_resolve_communion_hymn(self, res, context):
        is_weekday = 0 < context.get("day_of_week", 0) <= 5
        is_simple = context.get("rank") in ("rank_simple_6", "rank_simple_4") or context.get("variables", {}).get("rank") in ("rank_simple_6", "rank_simple_4")
        if is_weekday and is_simple:
            return ""
        if not res or not res.get("text"):
            return ""
        text = res.get('text')
        cleaned_text = self._clean_hymn_text(text)
        return f"**Communion Hymn:**  \n> {cleaned_text}"


    def _format_resolve_liturgy_hymns(self, res, context):
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
            day = context.get("day_of_week", 1)
            day_troparia = {
                1: "Troparion of the Angels.",
                2: "Troparion of the Forerunner.",
                3: "Troparion of the Cross.",
                4: "Troparion of the Apostles; Troparion of St. Nicholas.",
                5: "Troparion of the Cross."
            }
            day_kontakia = {
                1: "Kontakion of the Angels.",
                2: "Kontakion of the Forerunner.",
                3: "Kontakion of the Cross.",
                4: "Kontakion of the Apostles; Kontakion of St. Nicholas.",
                5: "Kontakion of the Cross."
            }
            sname = "the Saint"
            saints = context.get("saints", [])
            if saints:
                sname = self._clean_name(saints[0].get("name", "the Saint"))
            
            rank_id = context.get("rank") or context.get("variables", {}).get("rank")
            temple_type = context.get("temple_type", "saint")
            if day in (3, 5) and (rank_id in ("rank_simple_6", "rank_simple_4") or temple_type in ("lord", "theotokos")):
                parts = [
                    "**Troparia and Kontakia:**",
                    "Troparion of the Cross."
                ]
                if temple_type == "theotokos":
                    parts.append("Troparion of the Temple.")
                parts.extend([
                    f"Troparion of {sname}.",
                    f"Glory... Kontakion of {sname}.",
                    "Both now... Kontakion of the Cross."
                ])
            else:
                temple_part = "Theotokion 'Steadfast Protectress of Christians'."
                if res and res.get("components"):
                    for c in res["components"]:
                        if c.get("source") == "temple" and c.get("type") == "kontakion":
                            temple_part = "Kontakion of the Temple."
                            break
                        elif "steadfast" in str(c.get("source", "")).lower() or "steadfast" in str(c.get("key", "")).lower():
                            temple_part = "Theotokion 'Steadfast Protectress of Christians'."
                            break
                
                parts = [
                    "**Troparia and Kontakia:**",
                    day_troparia.get(day, "Troparion of the Day."),
                    f"Troparion of {sname}.",
                    day_kontakia.get(day, "Kontakion of the Day."),
                    f"Glory... Kontakion of {sname}.",
                    f"Both now... {temple_part}"
                ]
            return "\n".join(parts)
            
        parts = ["**Troparia and Kontakia:**"]
        tone = context.get("tone")
        tone_str = f" in Tone {tone}" if tone else ""
        
        for c in res["components"]:
            typ = c.get("type", "").capitalize()
            source = c.get("source") or c.get("ref_key") or "hymn"
            
            # Helper to prepend Glory/Both now/etc.
            prefix = ""
            if c.get("glory") or c.get("type") == "glory":
                prefix = "Glory... "
            elif c.get("both_now") or c.get("type") == "both_now":
                prefix = "Both now... "
            elif c.get("glory_both_now") or c.get("type") == "glory_both_now":
                prefix = "Glory, both now... "
                
            if source == "resurrection_tone":
                parts.append(f"{prefix}{typ} of the Resurrection{tone_str}.")
            elif source == "temple":
                parts.append(f"{prefix}{typ} of the Temple.")
            elif source == "menaion_saint":
                saints = context.get("saints", [])
                if saints:
                    if typ.lower() == "kontakion" and len(saints) > 1 and (c.get("glory") or c.get("type") == "glory"):
                        for s in saints[:-1]:
                            name = self.humanize_key(s.get("name", "Saint"))
                            parts.append(f"{typ} of {name}.")
                        last_saint = saints[-1]
                        name = self.humanize_key(last_saint.get("name", "Saint"))
                        parts.append(f"{prefix}{typ} of {name}.")
                    else:
                        for s in saints:
                            name = self.humanize_key(s.get("name", "Saint"))
                            parts.append(f"{prefix}{typ} of {name}.")
                else:
                    parts.append(f"{prefix}{typ} of the Saint.")
            elif source in ("steadfast_protectress", "fixed_theotokion") or "steadfast" in str(source).lower():
                parts.append(f"{prefix}Kontakion 'Steadfast Protectress of Christians'.")
            elif "to_you_mother_of_god" in str(source).lower() or "to_you_o_mother" in str(source).lower():
                parts.append(f"{prefix}Theotokion 'To you, O Mother of God...'.")
            else:
                parts.append(f"{prefix}{typ} of the {self.humanize_key(source)}.")
                
        return "\n".join(parts)


    def _format_resolve_liturgy_readings(self, res, context):
        if not res or not res.get("readings"):
            return ""
        is_weekday = 0 < context.get("day_of_week", 0) <= 5
        is_simple = context.get("rank") in ("rank_simple_6", "rank_simple_4") or context.get("variables", {}).get("rank") in ("rank_simple_6", "rank_simple_4")
        
        # Check hydration of each reading block
        readings = res["readings"]
        
        def is_hydrated(reading):
            for k in ["prokeimenon", "epistle", "alleluia", "gospel", "communion_hymn"]:
                p = reading.get(k, {})
                if p:
                    if p.get("text") or p.get("content"):
                        return True
        # Keep all reading slots (even if unhydrated) to ensure placeholders are displayed
        # for saints' readings on double-reading days.
        readings = res["readings"]
        
        def get_ref_label(ref_key, fallback_default):
            if not ref_key:
                return f"*{fallback_default}*"
            if ref_key.startswith("menaion."):
                name = "Saint"
                s_list = context.get("saints", [])
                for s in s_list:
                    s_id = s.get("id", "")
                    if s_id and s_id in ref_key:
                        name = s.get("name", "Saint")
                        break
                if name == "Saint":
                    parts = ref_key.split('.')
                    if len(parts) >= 3:
                        name = self.humanize_key(parts[2])
                name_human = self.humanize_key(name)
                return f"*of {name_human}*"
            
            ref_str = self.humanize_key(ref_key)
            if not ref_str or ref_str.lower() in (fallback_default.lower(), f"{fallback_default.lower()}_daily"):
                return "*of the day*"
            
            ref_clean = ref_str.replace("Prokimenon", "").replace("Prokeimenon", "").replace("Epistle", "").replace("Alleluia", "").replace("Gospel", "").strip()
            return f"*{ref_clean}*"
            
        parts = []
        for idx, reading in enumerate(readings):
            r_parts = []
            
            p = reading.get("prokeimenon", {})
            if p:
                tone = p.get("tone")
                tone_roman = self._roman_tone(tone)
                tone_str = f"Tone {tone_roman}" if tone_roman else ""
                text = p.get("text") or p.get("content")
                if len(readings) > 1:
                    label = "Prokeimenon (Feast - sung twice)" if idx == 0 else "Prokeimenon (Saint - sung once, without verse)"
                else:
                    label = "Prokeimenon"
                if text:
                    text_clean = text.strip('"').rstrip('.')
                    r_parts.append(f"**{label}:** {tone_str}: \"{text_clean}\"")
                else:
                    ref_key = p.get("ref_key", "")
                    val = get_ref_label(ref_key, "Prokeimenon")
                    if val == "*of the day*":
                        r_parts.append(f"**{label}:** {val}{', Tone ' + tone_roman if tone_roman else ''}")
                    else:
                        r_parts.append(f"**{label}:** {val} (Tone {tone_roman})" if tone_roman else f"**{label}:** {val}")
                
            e = reading.get("epistle", {})
            if e:
                text = e.get("text") or e.get("content")
                if text:
                    if is_weekday and is_simple:
                        r_parts.append(f"**Epistle:** of the day ({text})")
                    else:
                        r_parts.append(f"**Epistle:** {text}")
                else:
                    ref_key = e.get("ref_key", "")
                    val = get_ref_label(ref_key, "Epistle")
                    r_parts.append(f"**Epistle:** {val}")
                
            a = reading.get("alleluia", {})
            if a:
                tone = a.get("tone")
                tone_roman = self._roman_tone(tone)
                tone_str = f"Tone {tone_roman}" if tone_roman else ""
                text = a.get("text") or a.get("content")
                verses = a.get("verses", [])
                
                if is_weekday and is_simple:
                    r_parts.append(f"**Alleluia:** {tone_str}: 'Alleluia, Alleluia, Alleluia, glory to Thee, O God.'")
                elif text:
                    r_parts.append(f"**Alleluia:** {tone_str}, with verses: \"{text}\"" if tone_str else f"**Alleluia:** with verses: \"{text}\"")
                elif verses:
                    vs_str = "; ".join(verses)
                    r_parts.append(f"**Alleluia:** {tone_str}, with verses: \"{vs_str}\"" if tone_str else f"**Alleluia:** with verses: \"{vs_str}\"")
                else:
                    ref_key = a.get("ref_key", "")
                    val = get_ref_label(ref_key, "Alleluia")
                    if val == "*of the day*":
                        r_parts.append(f"**Alleluia:** {val}{', Tone ' + tone_roman if tone_roman else ''}")
                    else:
                        r_parts.append(f"**Alleluia:** {val} (Tone {tone_roman})" if tone_roman else f"**Alleluia:** {val}")
                
            g = reading.get("gospel", {})
            if g:
                text = g.get("text") or g.get("content")
                if text:
                    if is_weekday and is_simple:
                        r_parts.append(f"**Gospel:** of the day ({text})")
                    else:
                        r_parts.append(f"**Gospel:** {text}")
                else:
                    ref_key = g.get("ref_key", "")
                    val = get_ref_label(ref_key, "Gospel")
                    r_parts.append(f"**Gospel:** {val}")
 
            c = reading.get("communion_hymn", {})
            if c:
                text = c.get("text") or c.get("content")
                if text:
                    cleaned_text = self._clean_hymn_text(text)
                    if is_weekday and is_simple:
                        r_parts.append(f"**Communion Hymn:** of the day: {cleaned_text}")
                    else:
                        r_parts.append(f"**Communion Hymn:** {cleaned_text}")
                else:
                    ref_str = self.humanize_key(c.get("ref_key", ""))
                    if is_weekday and is_simple:
                        r_parts.append(f"**Communion Hymn:** of the day: {ref_str}")
                    else:
                        r_parts.append(f"**Communion Hymn:** {ref_str}")
                
            parts.append("\n".join(r_parts))
            
        if len(readings) > 1:
            parts.append("*Note: The second Prokeimenon is taken once without a verse; the second Alleluia has only its first verse; the second Epistle and Gospel are read without announcing their heading.*")
            
        return "\n".join(parts)


    def _format_resolve_trisagion_type(self, res, context):
        if not res:
            return ""

        if isinstance(res, str): 
            if res.lower() in ("standard", "trisagion", "trisagion_standard"):
                return ""
            return f"**Trisagion:** {res}"
        if isinstance(res, dict):
            if res.get("type") == "standard":
                return ""
            if res.get("type") == "replacement" and res.get("text"):
                return f"Instead of the Trisagion, we sing: *{res.get('text')}*"
            ref_key = res.get("ref_key", "")
            if ref_key:
                if "trisagion_our_father" in ref_key or "standard" in ref_key.lower() or ref_key == "trisagion" or "horologion.trisagion" in ref_key:
                    return ""
                return f"**Trisagion:** *{self.humanize_key(ref_key)}*."
        return ""


    def _format_resolve_royal_readings(self, res, context):
        if not res: return ""
        components = res.get("components", [])
        parts = []
        for c in components:
            ref = c.get("ref_key", "")
            parts.append(self.humanize_key(ref))
        return f"Royal Readings: {'; '.join(parts)}."


    def _format_resolve_cherubic_hymn(self, res, context):
        if not res: return ""
        ref_key = res.get('ref_key', '')
        if not ref_key or "standard" in ref_key.lower() or ref_key == "cherubic_hymn":
            return ""
        return f"**Cherubic Hymn:** *{self.humanize_key(ref_key)}*."


    def _format_resolve_liturgy_dismissal(self, res, context):
        is_weekday = 0 < context.get("day_of_week", 0) <= 5
        is_simple = context.get("rank") in ("rank_simple_6", "rank_simple_4") or context.get("variables", {}).get("rank") in ("rank_simple_6", "rank_simple_4")
        if self.mode == "quick" and is_weekday and is_simple:
            return ""
        if not res: return ""
        content = res.get('content', 'May Christ our true God...')
        if content and not content.endswith('...') and not content.endswith('.'):
            content += "..."
        return f"Dismissal: {content}"


    def _format_resolve_royal_readings(self, res, context):
        if not res: return ""
        components = res.get("components", [])
        parts = []
        for c in components:
            ref = c.get("ref_key", "")
            parts.append(self.humanize_key(ref))
        return f"Royal Readings: {'; '.join(parts)}."


    def _format_resolve_post_communion_hymn(self, res, context):
        is_weekday = 0 < context.get("day_of_week", 0) <= 5
        is_simple = context.get("rank") in ("rank_simple_6", "rank_simple_4") or context.get("variables", {}).get("rank") in ("rank_simple_6", "rank_simple_4")
        if self.mode == "quick" and is_weekday and is_simple:
            return ""
        if not res:
            return ""
        hymn_text = res.get("hymn")
        ref_key = res.get("ref_key")
        if hymn_text:
            return f"**Post-Communion Hymn:** \"{hymn_text}\""
        elif ref_key:
            return f"**Post-Communion Hymn:** {self.humanize_key(ref_key)}"
        return ""


    def _format_resolve_beatitudes(self, res, context):
        if not res:
            return ""
        note = res.get("note", "")
        if res.get("type") == "beatitudes":
            stichera = []
            for s in res.get("stichera", []):
                src = s.get("source", "")
                cnt = s.get("count", 0)
                stichera.append(f"{cnt} from {src}")
            return f"At the Beatitudes: {', '.join(stichera)} ({note})."
        return f"At the Beatitudes: {note}."


    def _format_resolve_basil_megalynarion(self, res, context):
        if not res:
            return ""
        source = res.get("source", "")
        ref = res.get("ref_key", "")
        rub = res.get("rubric", "")
        rub_str = f" ({rub})" if rub else ""
        return f"Megalynarion at St. Basil Liturgy (from {source}): {self.humanize_key(ref)}{rub_str}."

