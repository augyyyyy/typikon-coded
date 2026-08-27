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
                    txt = p.get("text") or p.get("content")
                    if txt and not self._is_missing(txt):
                        return True
                    ref_key = p.get("ref_key", "")
                    if ref_key and ref_key in self.engine.text_db:
                        entry = self.engine.text_db[ref_key]
                        if not self._is_missing(entry):
                            entry_txt = entry.get("text") or entry.get("content")
                            if entry_txt and not self._is_missing(entry_txt):
                                return True
            return False
            
        hydrated_any = any(is_hydrated(r) for r in readings_data)
        if hydrated_any:
            readings_data = [r for r in readings_data if is_hydrated(r)]
            
        lines = [self._format_resolve_liturgy_readings({"readings": readings_data}, context)]
        
        try:
            meg_res = self.engine.resolve_liturgy_megalynarion(context, rubrics)
            if meg_res:
                formatted_meg = self._format_resolve_liturgy_megalynarion(meg_res, context)
                if formatted_meg:
                    clean_meg = formatted_meg.replace("Instead of 'It is truly proper':", "").strip()
                    lines.append(f"**Instead of 'It is truly proper':** {clean_meg}")
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
                p_text = r.get("text") or self.humanize_key(r.get("ref_key", ""))
                parts.append(f"Paremia ({r.get('book', 'OT')}): {p_text}")
            elif r_type == "exclamation":
                parts.append(f"Exclamation: {r.get('text', '')} (Posture: {r.get('rubric', {}).get('response', '')})")
                
        if res.get("has_feast_readings"):
            fr = res.get("feast_readings", {})
            parts_fr = []
            if fr.get("epistle"):
                ep_text = fr["epistle"].get("text") or self.humanize_key(fr["epistle"].get("ref_key", ""))
                parts_fr.append(f"Epistle: {ep_text}")
            if fr.get("gospel"):
                gosp_text = fr["gospel"].get("text") or self.humanize_key(fr["gospel"].get("ref_key", ""))
                parts_fr.append(f"Gospel: {gosp_text}")
            if parts_fr:
                parts.append(f"Feast Readings – {', '.join(parts_fr)}")
            
        return "**At the Paremias:**  \n" + "  \n".join(f"  - {p}" for p in parts)


    def _format_resolve_vesperal_liturgy_readings(self, res, context):
        if not res:
            return ""
        data = res.get("data")
        if not data and isinstance(res, dict):
            paremias = []
            ep_prok = None
            ep = None
            all_data = None
            gosp = None
            for comp in res.get("components", []):
                c_type = comp.get("type")
                c_data = comp.get("data")
                if c_type == "reading" and comp.get("source") == "paremia" and c_data:
                    paremias.append(c_data)
                elif c_type == "prokeimenon" and c_data:
                    ep_prok = c_data
                elif c_type == "reading" and comp.get("source") == "epistle" and c_data:
                    ep = c_data
                elif c_type == "alleluia" and c_data:
                    all_data = c_data
                elif c_type == "reading" and comp.get("source") == "gospel" and c_data:
                    gosp = c_data
            if paremias or ep or gosp:
                data = {
                    "paremias": paremias,
                    "epistle_prokeimenon": ep_prok,
                    "epistle": ep,
                    "alleluia": all_data,
                    "gospel": gosp
                }
        if data and isinstance(data, dict):
            lines = []
            title = context.get("title") or "Vesperal Liturgy"
            lines.append(f"**Vesperal Liturgy Readings & Propers ({title} - St. Basil the Great):**")
            
            # Prokeimenon
            prok = data.get("prokeimenon")
            if prok:
                lines.append(f"**Prokeimenon (Tone {self._roman_tone(prok.get('tone'))}):**\n> \"{prok.get('text')}\"  \n> *Verse:* {prok.get('verse')}")
                
            # Paremias
            paremias = data.get("paremias", [])
            if paremias:
                p_lines = []
                for p in paremias:
                    p_num = p.get("number")
                    p_book = p.get("book")
                    p_ch = p.get("chapter")
                    p_title = p.get("title", "")
                    p_prok = p.get("prokeimenon")
                    
                    p_str = f"{p_num}. **{p_book} {p_ch}** ({p_title})"
                    if p_prok:
                        p_str += f"  \n   *Prokeimenon (Tone {self._roman_tone(p_prok.get('tone'))}):* \"{p_prok.get('text')}\""
                    p_lines.append(p_str)
                lines.append("**Old Testament Paremias:**\n" + "\n".join(p_lines))
                
            # Epistle Prokeimenon
            ep_prok = data.get("epistle_prokeimenon")
            if ep_prok:
                lines.append(f"**Prokeimenon of the Apostol (Tone {self._roman_tone(ep_prok.get('tone'))}):**\n> \"{ep_prok.get('text')}\"  \n> *Verse:* {ep_prok.get('verse')}")
                
            # Epistle
            ep = data.get("epistle")
            if ep:
                lines.append(f"**Epistle:**\n> **{ep.get('book')} §{ep.get('pericope')} [{ep.get('chapter')}]**  \n> *Incipit:* \"{ep.get('incipit')}\"")
                
            # Alleluia or Alleluia replacement
            all_rep = data.get("alleluia_replace")
            if all_rep:
                verses_str = "\n> ".join(f"*Verse {i+1}:* {v}" for i, v in enumerate(all_rep.get("verses", [])))
                lines.append(f"**Instead of the Alleluia:**\n> {all_rep.get('text')}\n> {verses_str}\n> *Rubric:* {all_rep.get('rubric', '')}")
            else:
                all_data = data.get("alleluia")
                if all_data:
                    verses_str = "; ".join(all_data.get("verses", []))
                    lines.append(f"**Alleluia (Tone {self._roman_tone(all_data.get('tone'))}):**\n> \"{verses_str}\"")
                    
            # Gospel
            gosp = data.get("gospel")
            if gosp:
                lines.append(f"**Holy Gospel:**\n> **{gosp.get('book')} §{gosp.get('pericope')} [{gosp.get('chapter')}]**  \n> *Incipit:* \"{gosp.get('incipit')}\"")
                
            # Cherubikon replacement
            cherub = data.get("cherubic_hymn_replace")
            if cherub:
                lines.append(f"**Instead of the Cherubic Hymn (also after the transfer of the Holy Gifts):**\n> \"{cherub}\"")
                
            # Zadostoinyk
            zad = data.get("zadostoinyk")
            if zad:
                lines.append(f"**Instead of 'It is truly right' (Zadostoinyk - Irmos of Ode IX):**\n> \"{zad}\"")
                
            # Koinonikon
            koin = data.get("koinonikon")
            if koin:
                lines.append(f"**Communion Hymn (Koinonikon):**\n> \"{koin}\"")
                
            # Post-communion replacement
            post_c = data.get("post_communion_replace")
            if post_c:
                lines.append(f"**Post-Communion Hymn (instead of 'We have seen the true light' and 'Let our mouths be filled'):**\n> \"{post_c}\"")
                
            # Reserve Lamb note
            res_note = data.get("reserve_lamb_note")
            if res_note:
                lines.append(f"> [!NOTE]\n> **Reserve Lamb Rubric**: {res_note}")
                
            return "\n\n".join(lines)

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
        return f"**Vesperal Liturgy Readings ({vesperal_id}):**  \n" + "  \n".join(f"  - {p}" for p in parts)


    def _format_resolve_liturgy_antiphons(self, res, context):
        pascha_off = context.get("pascha_offset")
        strategy = res.get("args", {}).get("strategy") or res.get("strategy") if res else None
        if res and (res.get("type") == "festal_antiphons" or strategy == "festal_antiphons" or (pascha_off is not None and 0 <= pascha_off <= 6)):
            if pascha_off is not None and 0 <= pascha_off <= 6:
                return (
                    "**Festal Antiphons of Pascha:**\n"
                    "  - **1st Antiphon (Psalm 65):** *\"Shout joyfully to the Lord, all the earth...\"* Refrain: *\"Through the prayers of the Mother of God, O Savior, save us.\"*\n"
                    "  - **2nd Antiphon (Psalm 66):** *\"May God be merciful to us and bless us...\"* Refrain: *\"Save us, O Son of God, risen from the dead, who sing to Thee: Alleluia.\"*\n"
                    "  - **3rd Antiphon (Psalm 67):** *\"Let God arise, and let His enemies be scattered...\"* Refrain: *\"Christ is risen from the dead, trampling down death by death, and upon those in the tombs bestowing life.\"*\n"
                    "**Entrance Hymn (Isodikon):** *\"In the churches bless God, the Lord from the fountains of Israel. Save us, O Son of God, risen from the dead, who sing to Thee: Alleluia.\"*"
                )
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
            return "**Typika & Beatitudes:** Psalms of Typica; Beatitudes on 6: 3 from the Octoechos, 3 from Ode III of the Saint."
        return "**Typika & Beatitudes:** Psalms of Typica; Beatitudes."


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
        pascha_off = context.get("pascha_offset")
        if pascha_off is not None and 0 <= pascha_off <= 38:
            return "**Instead of 'It is truly proper' (Zadostoinyk):**  \n> *\"The angel cried to the Lady Full of Grace: Rejoice, O Pure Virgin! And again I say: Rejoice! Thy Son is risen from His three days in the tomb, and has raised all the dead: O you people, be glad! Shine, shine, O New Jerusalem, for the glory of the Lord has shone upon thee. Exult now and be glad, O Zion, and thou, O pure Mother of God, rejoice in the resurrection of Thy Son.\"*"
        if res.get("text"):
            text = res.get("text")
            if self._is_missing(text):
                text = None
            if text:
                if not text.startswith('*') and not text.endswith('*') and len(text) > 2:
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
                    txt = p.get("text") or p.get("content")
                    if txt and not self._is_missing(txt):
                        return True
                    ref_key = p.get("ref_key", "")
                    if ref_key and ref_key in self.engine.text_db:
                        entry = self.engine.text_db[ref_key]
                        if not self._is_missing(entry):
                            entry_txt = entry.get("text") or entry.get("content")
                            if entry_txt and not self._is_missing(entry_txt):
                                return True
            return False
        # Keep all reading slots (even if unhydrated) to ensure placeholders are displayed
        # for saints' readings on double-reading days.
        readings = res["readings"]
        
        def get_ref_label(ref_key, fallback_default):
            if not ref_key:
                return f"*{fallback_default}*"
            if ref_key.startswith("menaion."):
                name = "Saint"
                if context.get("feast_level") in ("lord", "theotokos") or context.get("is_fore_or_afterfeast"):
                    name = context.get("title") or "the Feast"
                else:
                    s_list = context.get("saints", [])
                    for s in s_list:
                        s_id = s.get("id", "")
                        if s_id and s_id in ref_key:
                            name = s.get("name", "Saint")
                            break
                if name == "Saint":
                    s_title = context.get("title") or context.get("dolnytsky_title") or context.get("feast_title")
                    if s_title:
                        name = s_title
                    else:
                        parts = ref_key.split('.')
                        if len(parts) >= 3:
                            name = self.humanize_key(parts[2])
                        else:
                            name = "the Saint"
                name_human = self.humanize_key(name)
                if name_human.startswith("Menaion.") or name_human.startswith("Menaion "):
                    name_human = context.get("title") or "the Saint"
                return f"*of {name_human}*"
            
            ref_str = self.humanize_key(ref_key)
            if not ref_str or ref_str.lower() in (fallback_default.lower(), f"{fallback_default.lower()}_daily"):
                return "*of the day*"
            
            ref_clean = ref_str.replace("Prokimenon", "").replace("Prokeimenon", "").replace("Epistle", "").replace("Alleluia", "").replace("Gospel", "").strip()
            return f"*{ref_clean}*"
            
        parts = []
        for idx, reading in enumerate(readings):
            r_parts = []
            r_parts.append('<div class="readings-group">')
            
            p = reading.get("prokeimenon", {})
            if p:
                tone = p.get("tone")
                tone_roman = self._roman_tone(tone)
                tone_str = f"Tone {tone_roman}" if tone_roman else ""
                text = p.get("text") or p.get("content")
                if self._is_missing(text):
                    text = None
                if text:
                    text_clean = text.strip('"').rstrip('.')
                    val = f'{text_clean} ({tone_str})' if tone_str else text_clean
                else:
                    ref_key = p.get("ref_key", "")
                    val = get_ref_label(ref_key, "Prokeimenon").replace("*", "")
                    if tone_roman:
                        val += f" (Tone {tone_roman})"
                
                label = "Prokeimenon (Feast)" if len(readings) > 1 and idx == 0 else "Prokeimenon (Saint)" if len(readings) > 1 else "Prokeimenon"
                r_parts.append(f'<span class="readings-label">{label}:</span><span class="readings-value">{val}</span>')
                
            e = reading.get("epistle", {})
            if e:
                text = e.get("text") or e.get("content")
                if self._is_missing(text):
                    text = None
                if not text and e.get("ref_key"):
                    scripture_val = self._format_scripture_key(e["ref_key"])
                    if scripture_val and scripture_val != self.humanize_key(e["ref_key"]):
                        text = scripture_val
                if text:
                    val = text
                else:
                    ref_key = e.get("ref_key", "")
                    val = get_ref_label(ref_key, "Epistle").replace("*", "")
                
                label = "Epistles" if len(readings) > 1 and idx == 0 else "Epistle" if len(readings) > 1 else "Epistle"
                r_parts.append(f'<span class="readings-label">{label}:</span><span class="readings-value">{val}</span>')
                
            a = reading.get("alleluia", {})
            if a:
                tone = a.get("tone")
                tone_roman = self._roman_tone(tone)
                tone_str = f"Tone {tone_roman}" if tone_roman else ""
                text = a.get("text") or a.get("content")
                if self._is_missing(text):
                    text = None
                verses = a.get("verses", [])
                
                if text:
                    val = f'sung in {tone_str} with verses: "{text}"' if tone_str else f'with verses: "{text}"'
                elif verses:
                    vs_str = "; ".join(verses)
                    val = f'sung in {tone_str} with verses: "{vs_str}"' if tone_str else f'with verses: "{vs_str}"'
                elif is_weekday and is_simple:
                    val = f"{tone_str}: 'Alleluia, Alleluia, Alleluia, glory to Thee, O God.'" if tone_str else "'Alleluia, Alleluia, Alleluia, glory to Thee, O God.'"
                else:
                    ref_key = a.get("ref_key", "")
                    val = get_ref_label(ref_key, "Alleluia").replace("*", "")
                    if tone_roman:
                        val += f" (Tone {tone_roman})"
                
                label = "Alleluia (Feast)" if len(readings) > 1 and idx == 0 else "Alleluia (Saint)" if len(readings) > 1 else "Alleluia"
                r_parts.append(f'<span class="readings-label">{label}:</span><span class="readings-value">{val}</span>')
                
            g = reading.get("gospel", {})
            if g:
                text = g.get("text") or g.get("content")
                if self._is_missing(text):
                    text = None
                if not text and g.get("ref_key"):
                    scripture_val = self._format_scripture_key(g["ref_key"])
                    if scripture_val and scripture_val != self.humanize_key(g["ref_key"]):
                        text = scripture_val
                if text:
                    val = text
                else:
                    ref_key = g.get("ref_key", "")
                    val = get_ref_label(ref_key, "Gospel").replace("*", "")
                
                label = "Gospels" if len(readings) > 1 and idx == 0 else "Gospel" if len(readings) > 1 else "Gospel"
                r_parts.append(f'<span class="readings-label">{label}:</span><span class="readings-value">{val}</span>')
                
            c = reading.get("communion_hymn", {})
            if c:
                text = c.get("text") or c.get("content")
                if self._is_missing(text):
                    text = None
                if text:
                    cleaned_text = self._clean_hymn_text(text)
                    val = cleaned_text
                else:
                    ref_str = self.humanize_key(c.get("ref_key", ""))
                    val = ref_str
                
                label = "Communion Hymn (Feast)" if len(readings) > 1 and idx == 0 else "Communion Hymn (Saint)" if len(readings) > 1 else "Communion Hymn"
                r_parts.append(f'<span class="readings-label">{label}:</span><span class="readings-value">{val}</span>')
                
            r_parts.append('</div>')
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
        return f"**Dismissal:** {content}"


    def _format_resolve_royal_readings(self, res, context):
        if not res: return ""
        components = res.get("components", [])
        parts = []
        for c in components:
            ref = c.get("ref_key", "")
            parts.append(self.humanize_key(ref))
        return f"Royal Readings: {'; '.join(parts)}."


    def _format_resolve_post_communion_hymn(self, res, context):
        if context.get("variables", {}).get("post_communion_replace") or context.get("post_communion_replace"):
            return ""
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
        text = res.get("text", "")
        rub = res.get("rubric", "")
        rub_str = f" ({rub})" if rub else ""
        if text:
            return f"**Megalynarion:** *\"{text}\"*{rub_str}"
        return f"**Megalynarion:** {self.humanize_key(ref)}{rub_str}"

