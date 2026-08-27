import re

class CommonFormatterMixin:
    def _format_resolve_gradual(self, res, context):
        # Suppressed to avoid duplicate printing with resolve_anabathmoi
        return ""


    def _format_resolve_alleluia_vs_god_is_lord(self, res, context):
        if not res:
            return ""
        if res.get("type") == "god_is_the_lord":
            return self._format_resolve_god_is_the_lord_troparia(res, context)
        parts = []
        for comp in res.get("components", []):
            if comp.get("type") == "hymn":
                parts.append(f"Trinity Hymn: {self.humanize_key(comp.get('ref_key'))}")
        return "\n".join(parts)


    def _format_resolve_trinity_hymns(self, res, context):
        if not res:
            return ""
        return f"Trinity Hymns: {res.get('rubric_note', '')}"


    def _format_resolve_vigil_troparion(self, res, context):
        if not res:
            return ""
        return f"Troparion: {self.humanize_key(res.get('ref_key'))}"


    def _format_resolve_vigil_kontakion(self, res, context):
        if not res:
            return ""
        return f"Kontakion: {self.humanize_key(res.get('ref_key'))}"


    def _format_resolve_vigil_opening(self, res, context):
        if not res:
            return ""
        if isinstance(res, dict) and res.get("type") == "fixed_ref":
            temp = []
            self._format_fixed_ref(res.get("ref_key"), temp)
            return "\n".join(temp)
        return str(res)




    def _format_resolve_prophecy_reading(self, res, context):
        if not res or res.get("type") == "none":
            return ""
        return f"Prophecy Reading (Hour 6): Reading {res.get('reading_id')} (from {res.get('book')})"


    def _format_resolve_prophecy_prok_1(self, res, context):
        if not res:
            return ""
        return f"First Prokeimenon (Hour 6): {self.humanize_key(res.get('prokeimenon_id'))}"


    def _format_resolve_prophecy_prok_2(self, res, context):
        if not res:
            return ""
        return f"Second Prokeimenon (Hour 6): {self.humanize_key(res.get('prokeimenon_id'))}"


    def _format_resolve_psalm_50_intercession(self, res, context):
        if not res:
            return ""
        parts = []
        if "glory" in res:
            parts.append(f"Glory: {res['glory']['text']}")
        if "both_now" in res:
            parts.append(f"Both Now: {res['both_now']['text']}")
        if "sticheron" in res:
            parts.append(f"Sticheron: {res['sticheron']['text']}")
        return "\n".join(parts)


    def _format_resolve_fasting_rule(self, res, context):
        if not res:
            return ""
        return f"Fasting Rule: {res.get('rule')} ({res.get('note', '')})"


    def _format_resolve_prostration_annotation(self, res, context):
        if not res:
            return ""
        return f"Prostrations: {res.get('annotation') or res.get('note')}"


    def _format_resolve_clergy_variant(self, res, context):
        if not res:
            return ""
        return f"Clergy Variant: {res.get('variant')} ({res.get('note')})"


    def _format_resolve_photizomenoi_litany(self, res, context):
        if not res or not res.get("components"):
            return ""
        parts = []
        for c in res["components"]:
            parts.append(self.humanize_key(c.get("ref_key", "")))
        return "Litanies: " + "; ".join(parts) + "."


    def _format_resolve_litya_content(self, res, context):
        if not res or res.get("included") is False or res.get("type") == "suppressed":
            return ""
        dist = []
        for item in res.get("stichera", []):
            c = item.get('count', item.get('qty', '?'))
            t = item.get('type', '')
            s = self.humanize_key(item.get('source', ''))
            name = self.humanize_key(t) if t else "Stichera"
            if "saint" in t.lower():
                name = "stichera of the saint"
            elif "feast" in t.lower():
                name = "stichera of the feast"
            dist.append(f"{c} {name} from the {s}")
            
        parts = []
        if dist:
            parts.append(f"We sing the Litiya stichera: {', '.join(dist)}")
        glory_val = res.get("glory")
        glory_human = self.humanize_key(glory_val)
        if glory_human and glory_human.strip().lower() not in ("none", "", "null", "glory", "(no saint doxastikon)", "(no_saint_doxastikon)"):
            parts.append(f"Glory... {glory_human}")
        both_now_val = res.get("both_now")
        both_now_human = self.humanize_key(both_now_val)
        if both_now_human and both_now_human.strip().lower() not in ("none", "", "null"):
            parts.append(f"Both now... {both_now_human}")
        return "; ".join(parts) + "."


    def _format_resolve_aposticha(self, res, context):
        if not res or not res.get("components"):
            return ""
        stichera_parts = []
        glory = None
        both_now = None
        glory_both_now = None
        
        counts = {}
        for item in res["components"]:
            t = item.get("type", "stichera")
            if t == "glory":
                glory = item.get("id")
            elif t == "both_now":
                both_now = item.get("id")
            elif t == "glory_both_now":
                glory_both_now = item.get("id")
            else:
                source = self.humanize_key(item.get("source", ""))
                raw_id = item.get("id", "Stichera")
                
                # Strip numeric suffix for grouping (e.g., aposticha_resurrection_1 -> aposticha_resurrection)
                base_id = re.sub(r'_\d+$', '', raw_id)
                key = (source, base_id)
                counts[key] = counts.get(key, 0) + item.get("count", 1)
                
        for (source, base_id), c in counts.items():
            if "resurrection" in base_id.lower() and "octoechos" in source.lower():
                stichera_parts.append(f"the resurrectional aposticha in the tone of the week, from the Octoechos")
            else:
                name = self.humanize_key(base_id)
                if c > 1:
                    stichera_parts.append(f"{c} {name} from the {source}")
                else:
                    stichera_parts.append(f"{name} from the {source}")
            
        parts = []
        if stichera_parts:
            parts.append(f"We sing {', '.join(stichera_parts)}")
        else:
            parts.append("We sing the Aposticha")
            
        glory_human = self.humanize_key(glory)
        both_now_human = self.humanize_key(both_now)
        glory_both_now_human = self.humanize_key(glory_both_now)
        
        has_glory = glory_human and glory_human.strip().lower() not in ("none", "", "null", "glory", "(no saint doxastikon)", "(no_saint_doxastikon)")
        
        if has_glory:
            parts.append(f"Glory... {glory_human}")
            if both_now_human and both_now_human.strip().lower() not in ("none", "", "null"):
                parts.append(f"Both now... {both_now_human}")
        else:
            if both_now_human and both_now_human.strip().lower() not in ("none", "", "null"):
                parts.append(f"Glory, both now... {both_now_human}")
                
        if glory_both_now_human and glory_both_now_human.strip().lower() not in ("none", "", "null"):
            parts.append(f"Glory, both now... {glory_both_now_human}")
            
        return "**At the Aposticha:** " + "; ".join(parts) + "."


    def _format_resolve_god_is_the_lord_troparia(self, res, context):
        if not res or not res.get("sequence"):
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
                return f"**God is the Lord:** We sing the troparion of {wname}, twice; Glory, both now... Dismissal Theotokion in {wtone}."
            else:
                sname = "the Saint"
                saints = context.get("saints", [])
                if saints:
                    sname = self._clean_name(saints[0].get("name", "the Saint"))
                return f"**God is the Lord:** We sing the troparion of {sname}, twice; Glory, both now... Dismissal Theotokion in the tone of the Saint's troparion and of the day of the week."
        
        parts = []
        for t in res["sequence"]:
            content = t.get("content", "")
            count = t.get("count", 1)
            count_str = " once" if count == 1 else " twice" if count == 2 else f" {count} times"
            
            if content == "troparion_resurrection":
                parts.append(f"the Sunday (resurrectional) troparion,{count_str}")
            elif content in ("glory", "both_now", "glory_both_now"):
                if content == "glory_both_now":
                    parts.append("Glory, both now.")
                else:
                    lbl = content.replace('_', ' ')
                    parts.append(lbl.capitalize() + ".")
            elif content == "troparion_feast":
                title_lower = context.get("dolnytsky_title", "").lower()
                feast_label = "forefeast" if "forefeast" in title_lower or "prefeast" in title_lower else "afterfeast" if "afterfeast" in title_lower else "feast"
                parts.append(f"troparion of the {feast_label},{count_str}")
            elif content in ("troparion_saint", "troparion_saint_1", "troparion_saint_2"):
                saints = context.get("saints", [])
                idx = 1 if "2" in content else 0
                if idx < len(saints):
                    name = saints[idx].get("name", "saint")
                    parts.append(f"troparion of {self._clean_name(name)},{count_str}")
                else:
                    parts.append(f"troparion of the saint,{count_str}")
            elif "theotokion" in content:
                parts.append(f"Theotokion,{count_str}")
            elif content == "trinity_hymns":
                parts.append(f"Trinity hymns in Tone {t.get('tone', 1)}")
            else:
                parts.append(f"{self.humanize_key(content)},{count_str}")
                
        result_str = ""
        for p in parts:
            if p.endswith("."):
                if result_str:
                    if result_str.endswith("; "):
                        result_str = result_str[:-2]
                    result_str += "; " + p + " "
                else:
                    result_str += p + " "
            else:
                result_str += p + "; "
                
        if result_str.endswith("; "):
            result_str = result_str[:-2]
        if result_str.endswith(" "):
            result_str = result_str[:-1]
        if not result_str.endswith("."):
            result_str += "."
            
        return "**God is the Lord:** We sing: " + result_str


    def _format_resolve_sidalen_content(self, res, context):
        if not res:
            return ""
        parts = []
        if res.get("sidalen_1"):
            parts.append("1st Kathisma sessional hymns.")
        if res.get("sidalen_2"):
            parts.append("2nd Kathisma sessional hymns.")
        if res.get("sidalen_3"):
            parts.append("3rd Kathisma sessional hymns.")
        if parts:
            return "After each cathisma we sing the sessional hymns: " + " ".join(parts)
        return ""


    def _format_resolve_post_gospel_stichera(self, res, context):
        if not res or not isinstance(res, list):
            return ""
        refs = [self.humanize_key(r) for r in res]
        return f"Psalm 50 and Post-Gospel Stichera: {', '.join(refs)}."


    def _format_resolve_prokeimenon(self, res, context):
        if not res:
            return ""
        
        # Tone extraction
        tone = res.get('tone')
        if tone is None:
            ref_key = res.get("ref_key", "")
            if "saturday_evening" in ref_key:
                tone = 6
            elif "great_prokeimenon_sunday_lent" in ref_key:
                tone = 8
            elif "great_prokeimenon_bright_week_tone_8" in ref_key:
                tone = 8
            elif "great_prokeimenon_bright_week_tone_7" in ref_key:
                tone = 7
        
        tone_roman = self._roman_tone(tone) if isinstance(tone, int) else str(tone) if tone else ""
        
        # Text extraction
        text = res.get('text') or res.get('content')
        if not text and res.get('prokeimenon_id'):
            text = res.get('prokeimenon_id').replace('_', ' ')
            
        ref_key = res.get("ref_key", "")
        variant = res.get("variant", "")
        res_type = res.get("type", "")
        
        if "saturday_evening" in ref_key or (context.get("day_of_week") == 6 and not variant):
            p_title = "Prokeimenon of Saturday Evening (Sunday prep)"
        elif variant == "great" or "great_prokeimenon" in ref_key:
            p_title = "Great Prokeimenon"
        elif res_type == "daily_prokeimenon":
            day_name = {
                0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday",
                4: "Thursday", 5: "Friday", 6: "Saturday"
            }.get(context.get("day_of_week", 4), "Thursday")
            p_title = f"Daily Prokeimenon ({day_name} of the Octoechos)"
        elif res_type == "festal_prokeimenon":
            p_title = "Festal Prokeimenon"
        else:
            p_title = "Prokeimenon"

        tone_str = f"Tone {tone_roman}" if tone_roman else ""
        
        # verses
        verses = []
        
        # Dynamic lookup from Horologion asset horologion.psalm_116
        psalm_116 = self.engine.get_text("horologion.psalm_116")
        content_116 = psalm_116.get("content", "") if psalm_116 and not self._is_missing(psalm_116) else ""
        if self._is_missing(content_116):
            content_116 = ""
        
        day_headers = {
            0: "On Sunday Evening:",
            1: "On Monday Evening:",
            2: "On Tuesday Evening:",
            3: "On Wednesday Evening:",
            4: "On Thursday Evening:",
            5: "On Friday Evening:",
            6: "On Saturday Evening:",
        }
        
        # 1. Saturday Evening / Daily Prokeimenon dynamic lookup
        day_header = None
        if "saturday_evening" in ref_key or (context.get("day_of_week") == 6 and not variant):
            day_header = "On Saturday Evening:"
        elif res_type == "daily_prokeimenon" and context.get("day_of_week") is not None:
            day_header = day_headers.get(context.get("day_of_week"))
            
        if day_header and content_116:
            # Parse daily prokeimenon refrain and verses from psalm_116
            lines = content_116.split('\n')
            found = False
            refrain = ""
            parsed_verses = []
            for line in lines:
                line_strip = line.strip()
                if not line_strip:
                    continue
                if found:
                    if (line_strip.startswith("On ") and "Evening:" in line_strip) or \
                       line_strip.startswith("During the Great Fast") or \
                       line_strip.startswith("The Great Prokimena"):
                        break
                    if not refrain:
                        refrain = line_strip.replace('*', '').replace('  ', ' ').strip()
                    elif line_strip.startswith("Verse:"):
                        v_text = line_strip[len("Verse:"):].replace('*', '').replace('  ', ' ').strip()
                        parsed_verses.append(v_text)
                elif line_strip.startswith(day_header):
                    found = True
            
            if refrain:
                text = refrain
                verses = parsed_verses

        # 2. Great Lenten Sunday Prokeimenon dynamic lookup from horologion.psalm_68
        elif "great_prokeimenon_sunday_lent" in ref_key:
            psalm_68 = self.engine.get_text("horologion.psalm_68")
            content_68 = psalm_68.get("content", "") if psalm_68 and not self._is_missing(psalm_68) else ""
            if self._is_missing(content_68):
                content_68 = ""
            if content_68:
                lines = content_68.split('\n')
                refrain = ""
                parsed_verses = []
                for line in lines:
                    line_strip = line.strip()
                    if not line_strip:
                        continue
                    if line_strip.startswith("If there are readings"):
                        break
                    if line_strip.startswith("Verse:"):
                        v_text = line_strip[len("Verse:"):].replace('*', '').replace('  ', ' ').strip()
                        parsed_verses.append(v_text)
                    elif not refrain:
                        refrain = line_strip.replace('*', '').replace('  ', ' ').strip()
                if refrain:
                    text = refrain
                    verses = parsed_verses
            else:
                # Fallback if psalm_68 is empty/missing
                text = "Turn not away Your face from Your servant, for I am in distress; answer me quickly; draw near to my soul and redeem it."
                verses = [
                    "Let Your salvation, O God, protect me.",
                    "Let the poor see and rejoice.",
                    "Seek God, and your soul shall live."
                ]
                
        # 3. Fallbacks for other special/Great Prokeimena
        elif "great_prokeimenon_feast_evening" in ref_key or "great_prokeimenon_bright_week" in ref_key:
            if tone == 7:
                text = "Who is so great a God as our God? You are the God Who works wonders."
                verses = [
                    "You made Your power known among the peoples.",
                    "And I said: Now have I begun; this change is of the right hand of the Most High.",
                    "I remembered the works of the Lord; for I will remember Your wonders from the beginning."
                ]
            elif tone == 8:
                text = "Who is so great a God as our God? You are the God Who works wonders."
                verses = [
                    "When Israel went out of Egypt, the house of Jacob from a people of foreign tongue.",
                    "The sea saw it and fled; Jordan was turned back."
                ]
                
        if text:
            text_clean = text.replace('*', '').replace('  ', ' ').strip('"').rstrip('.')
            html = f'<span class="rubric">{p_title}'
            if tone_str:
                html += f', {tone_str}'
            html += f':</span> <span class="sung-text">"{text_clean}"</span>'
            
            if verses:
                for v in verses:
                    html += f'\n<blockquote class="verse"><span class="rubric">Stichos:</span> <span class="sung-text">{v}</span></blockquote>'
            return html
            
        fallback_text = text or 'sung according to the Typikon'
        if fallback_text and not fallback_text.startswith('*') and not fallback_text.endswith('*') and len(fallback_text) > 2:
            fallback_text = f"*{fallback_text}*"
            
        html = f'<span class="rubric">{p_title}'
        if tone_str:
            html += f' ({tone_str})'
        html += f':</span> <span class="sung-text">{fallback_text}</span>'
        return html


    def _format_resolve_sessional(self, res, context):
        if not res: return ""
        val = res.get('id', 'Sessional')
        val_lower = val.lower()
        if "octoechos" in val_lower or "sidalen_res" in val_lower or "res" in val_lower:
            if "sunday" in val_lower or "res" in val_lower or "resurrection" in val_lower:
                return "We sing the resurrectional sessional hymns in the tone of the week, from the Octoechos."
            return "We sing the sessional hymns from the Octoechos."
        if "triodion" in val.lower():
            return "We sing the sessional hymns from the Triodion."
        if "menaion" in val.lower() or "saint" in val.lower():
            categories = context.get("saint_categories", [])
            if categories:
                cat = categories[0]
                mapping = {
                    "Prophet": "Holy Prophet",
                    "Prophets": "Holy Prophets",
                    "Apostle": "Holy Apostle",
                    "Apostles": "Holy Apostles",
                    "Martyr": "Holy Martyr",
                    "Martyrs": "Holy Martyrs",
                    "Hieromartyr": "Holy Hieromartyr",
                    "Hieromartyrs": "Holy Hieromartyrs",
                    "Venerable Martyr": "Holy Venerable Martyr",
                    "Venerable Martyrs": "Holy Venerable Martyrs",
                    "Venerable Woman": "Venerable Mother",
                    "Venerable Women": "Venerable Mothers",
                    "Venerable": "Venerable Father",
                    "Venerables": "Venerable Fathers",
                    "Hierarch": "Holy Hierarch",
                    "Hierarchs": "Holy Hierarchs",
                    "Unmercenary": "Holy Unmercenary",
                    "Unmercenaries": "Holy Unmercenaries",
                    "Holy Fathers": "Holy Fathers",
                    "Angels": "Holy Angels",
                    "Woman Martyr": "Holy Woman Martyr",
                    "Women Martyrs": "Holy Women Martyrs",
                    "Fool for Christ": "Holy Fool for Christ",
                    "Fools for Christ": "Holy Fools for Christ",
                }
                term = mapping.get(cat, "Saint")
                return f"We sing the sessional hymns of the {term}."
            return "We sing the sessional hymns of the Saint."
        return f"Sessional Hymns: {self.humanize_key(val)}."


    def _format_resolve_hypakoe(self, res, context):
        if not res: return ""
        return f"Hypakoe: {self.humanize_key(res.get('id', 'Hypakoe'))}."


    def _format_troparia_stack_components(self, components, context):
        parts = []
        for c in components:
            if not isinstance(c, dict):
                parts.append(self.humanize_key(str(c)))
                continue
                
            ref_key = c.get("ref_key") or c.get("id") or ""
            tone = c.get("tone")
            tone_str = f" in Tone {tone}" if tone else ""
            
            if "weekday.day_" in ref_key:
                day_match = re.search(r'day_(\d+)', ref_key)
                if day_match:
                    day_num = int(day_match.group(1))
                    if day_num in (3, 5):
                        parts.append("Troparion of the Cross (first place, Wednesday/Friday)")
                    else:
                        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                        day_name = days[day_num]
                        parts.append(f"{day_name} Troparion from the Octoechos")
                    continue
            
            if "resurrection.tone_" in ref_key:
                tone_match = re.search(r'tone_(\d+)', ref_key)
                if tone_match:
                    t_num = tone_match.group(1)
                    parts.append(f"Resurrectional Troparion in Tone {t_num}")
                    continue
            
            if ref_key == "temple.troparion" or ref_key == "horologion.troparion_temple":
                day_num = context.get("day_of_week", 1)
                temple_type = context.get("temple_type", "saint")
                if day_num in (3, 5) and temple_type not in ("lord", "theotokos"):
                    # Omit Temple troparion on Wednesday/Friday if it is of a Saint
                    continue
                parts.append("Troparion of the Temple")
                continue
                
            if ref_key == "horologion.troparion.god_of_our_fathers_block":
                parts.append('*"O God of our fathers..."* and the following three troparia')
                continue
                
            if ref_key == "horologion.hypakoe_sunday":
                t_val = tone or context.get("tone", 1)
                parts.append(f"Sunday Hypakoe in Tone {t_val}")
                continue
                
            if ref_key == "horologion.troparion_uncreated_nature":
                parts.append("Troparion 'Uncreated Nature'")
                continue
                
            if ref_key == "horologion.troparion_behold_the_bridegroom":
                parts.append("Troparion 'Behold, the Bridegroom'")
                continue
                
            if ref_key == "horologion.troparion_behold_the_bridegroom_glory":
                parts.append("Glory... 'Behold, the Bridegroom' (Glory)")
                continue
                
            if ref_key == "horologion.troparion_behold_the_bridegroom_theotokion":
                parts.append("Both now... 'Behold, the Bridegroom' (Theotokion)")
                continue
                
            if ref_key == "horologion.troparion_day_of_week":
                day_names = {
                    1: "Troparion of the Archangels",
                    2: "Troparion of the Forerunner",
                    3: "Troparion of the Cross",
                    4: "Troparion of the Apostles and St. Nicholas",
                    5: "Troparion of the Cross",
                    6: "Troparion of All Saints",
                    0: "Resurrectional Troparion"
                }
                d_num = context.get("day_of_week", 1)
                parts.append(day_names.get(d_num, "Troparion of the weekday"))
                continue
                
            if ref_key == "horologion.troparion_saint_if_any":
                saints = context.get("saints", [])
                if saints:
                    s_name = self._clean_name(saints[0].get("name", "the Saint"))
                    parts.append(f"Troparion of {s_name}")
                else:
                    parts.append("Troparion of the Saint")
                continue
                
            if ref_key == "horologion.theotokion_daily":
                parts.append("daily Theotokion")
                continue
            
            if ref_key in self.engine.text_db:
                val = self.engine.text_db[ref_key]
                title = val.get("title") or val.get("metadata", {}).get("title") if isinstance(val, dict) else ref_key
                parts.append(self.humanize_key(title) + tone_str)
            else:
                parts.append(self.humanize_key(ref_key) + tone_str)
                
        return ", ".join(parts)


    def _format_resolve_midnight_troparia(self, res, context):
        if not res: return ""
        if isinstance(res, dict) and res.get("type") == "troparia_stack":
            components = res.get("components", [])
            if len(components) == 2 and "After the 1st Trisagion" in str(components[0].get("id", "")):
                t1 = components[0].get("id")
                t2 = components[1].get("id")
                return f"**Troparia:**  \n{t1}.  \n{t2}."
            comps = self._format_troparia_stack_components(components, context)
            return f"**Troparia:** {comps}."
        return f"**Troparia:** {self.humanize_key(res)}."


    def _format_resolve_midnight_prayer(self, res, context):
        if not res: return ""
        ref = res.get('ref_key', '')
        if ref == "horologion.prayer_mardarius":
            return "**Prayer:** Prayer of St. Mardarius (*\"O Lord God, Father Almighty...\"*)."
        return f"**Prayer:** {self.humanize_key(ref)}."


    def _format_resolve_royal_psalms(self, res, context):
        if not res: return ""
        meta = res.get("source_metadata", {})
        hour = meta.get("hour", 1)
        feast = self.humanize_key(meta.get("feast", ""))
        psalms = [self.humanize_key(p) for p in res.get('ref_keys', [])]
        return f"Royal Psalms for {feast} Hour {hour}: {', '.join(psalms)}."


    def _format_resolve_royal_stichera(self, res, context):
        if not res: return ""
        meta = res.get("source_metadata", {})
        hour = meta.get("hour", 1)
        components = res.get("components", [])
        parts = []
        for c in components:
            ref = c.get("ref_key", "")
            parts.append(self.humanize_key(ref))
        return f"Royal Stichera for Hour {hour}: {'; '.join(parts)}."


    def _format_resolve_royal_kontakion(self, res, context):
        if not res: return ""
        return f"Royal Kontakion: {self.humanize_key(res.get('ref_key', ''))}."


    def _format_resolve_artoklasia(self, res, context):
        if not res:
            return ""
        if "action" in res:
            action = res.get("action", "")
            ref = res.get("ordo_ref", "")
            ref_str = f" [{ref}]" if ref else ""
            return f"Artoklasia{ref_str}: {action}"
            
        if not res.get("included"):
            return ""
        troparia_parts = []
        for t in res.get("troparia", []):
            ref = t.get("ref_key", "")
            cnt = t.get("count", 1)
            troparia_parts.append(f"{self.humanize_key(ref)} x{cnt}")
        troparia_str = ", ".join(troparia_parts)
        return f"At the Blessing of Loaves (Artoklasia): we sing {troparia_str}."


    def _format_resolve_post_ode9_hymn(self, res, context):
        if not res:
            return ""
        typ = res.get("type")
        if typ == "holy_is_the_lord":
            return "Holy is the Lord our God (3x)."
        elif typ == "it_is_truly_meet":
            return "It is truly meet (Axion Estin)."
        elif typ == "paschal_troparion":
            return "Paschal Troparion refrains."
        elif typ == "zadostojnyk":
            return "Zadostoinyk (Feast Heirmos)."
        return ""


    def _format_resolve_god_is_with_us(self, res, context):
        if not res: return ""
        mode = self.humanize_key(res.get("mode", ""))
        return f"We sing 'God is with us': in {mode}."


    def _format_resolve_typika_kontakia(self, res, context):
        if not res: return ""
        order = res.get("order", [])
        formatted_order = [self.humanize_key(item) for item in order]
        return f"Typika Kontakia (order of singing): {'; '.join(formatted_order)}."


    def _format_resolve_royal_psalms(self, res, context):
        if not res: return ""
        meta = res.get("source_metadata", {})
        hour = meta.get("hour", 1)
        feast = self.humanize_key(meta.get("feast", ""))
        psalms = [self.humanize_key(p) for p in res.get("ref_keys", [])]
        return f"Royal Psalms for {feast} Hour {hour}: {', '.join(psalms)}."


    def _format_resolve_royal_stichera(self, res, context):
        if not res: return ""
        meta = res.get("source_metadata", {})
        hour = meta.get("hour", 1)
        components = res.get("components", [])
        parts = []
        for c in components:
            ref = c.get("ref_key", "")
            parts.append(self.humanize_key(ref))
        return f"Royal Stichera for Hour {hour}: {'; '.join(parts)}."


    def _format_resolve_dismissal_theotokion(self, res, context):
        is_weekday = 0 < context.get("day_of_week", 0) <= 5
        is_simple = context.get("rank") in ("rank_simple_6", "rank_simple_4") or context.get("variables", {}).get("rank") in ("rank_simple_6", "rank_simple_4")
        if is_weekday and is_simple:
            return ""
        if not res:
            return ""
        ref_key = res.get("ref_key", "")
        rubric_note = res.get("rubric_note") or "Dismissal Theotokion"
        
        if "Resurrectional Theotokion in Tone of Saint" in rubric_note or "Resurrectional Theotokion (Tone" in rubric_note:
            match = re.search(r'Tone\s+(\d+|[IVXLCDM]+)', rubric_note, re.IGNORECASE)
            if match:
                t_val = match.group(1)
                if t_val.isdigit():
                    t_val = self._roman_tone(int(t_val))
                return f"Resurrectional Theotokion in Tone {t_val}."
            return "Resurrectional Theotokion."
            
        if ref_key and ref_key in self.engine.text_db:
            content = self.engine.text_db[ref_key]
            title = content.get("title")
            if title:
                return f"{rubric_note}: {title}."
                
        if "theotokion_dismissal" in ref_key:
            parts = ref_key.split('.')
            tone_part = ""
            day_part = ""
            for p in parts:
                if "tone" in p:
                    tone_part = p.replace("tone_", "Tone ")
                elif p in ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"):
                    day_part = p.capitalize()
            if rubric_note.lower().strip() == "dismissal theotokion":
                return f"Dismissal Theotokion for {day_part} in {tone_part}."
            return f"{rubric_note}: Dismissal Theotokion for {day_part} in {tone_part}."
            
        return f"{rubric_note}: {self.humanize_key(ref_key)}."


    def _format_resolve_gospel_sticheron_placement(self, res, context):
        if not res or res.get("type") == "none":
            return ""
        
        rubric_note = res.get("rubric", {}).get("note", "")
        parts = []
        for comp in res.get("components", []):
            if comp.get("type") == "stichera_group":
                for s in comp.get("stichera", []):
                    pos = s.get("position", "")
                    ref = s.get("ref_key", "")
                    tone = s.get("tone")
                    
                    human_ref = self.humanize_key(ref)
                    if tone is not None:
                        human_ref = f"{human_ref} in Tone {tone}"
                        
                    if pos == "glory":
                        parts.append(f"Glory... {human_ref}")
                    elif pos == "both_now":
                        parts.append(f"Both now... {human_ref}")
                    elif pos == "glory_both_now":
                        parts.append(f"Glory, both now... {human_ref}")
                    else:
                        parts.append(human_ref)
                        
        if parts:
            return f"We sing: {'; '.join(parts)}."
        return ""


    def _format_resolve_alleluia_vs_god_is_lord(self, res, context):
        if not res:
            return ""
        if res.get("type") == "sequence":
            parts = []
            for comp in res.get("components", []):
                ref = comp.get("ref_key", "")
                tone = comp.get("tone")
                ending = comp.get("ending_variable", "")
                ending_str = f" with ending for {ending}" if ending else ""
                parts.append(f"{self.humanize_key(ref)} in Tone {tone}{ending_str}")
            return "Instead of 'God is the Lord', we sing Alleluia and Trinity Hymns:\n" + "\n".join(f"  - {p}" for p in parts)
        return self._format_resolve_god_is_the_lord_troparia(res, context)


    def _format_resolve_trinity_hymns(self, res, context):
        if not res:
            return ""
        tone = res.get("tone")
        rubric = res.get("rubric_note", "")
        hymns_list = []
        for h in res.get("hymns", []):
            pos = h.get("position")
            ref = h.get("ref")
            comm = h.get("commemoration", "")
            hymns_list.append(f"Hymn {pos} ({self.humanize_key(comm)}): {self.humanize_key(ref)}")
        return f"Trinity Hymns (Tone {tone}):\n" + "\n".join(f"  - {h}" for h in hymns_list) + f"\n({rubric})"


    def _format_resolve_vigil_troparion(self, res, context):
        if not res:
            return ""
        ref = res.get("ref_key", "")
        source = res.get("source", "")
        return f"Vigil Troparion (from {source}): {self.humanize_key(ref)}."


    def _format_resolve_vigil_kontakion(self, res, context):
        if not res:
            return ""
        ref = res.get("ref_key", "")
        source = res.get("source", "")
        return f"Vigil Kontakion (from {source}): {self.humanize_key(ref)}."


    def _format_resolve_vigil_opening(self, res, context):
        if not res:
            return ""
        ref = res.get("ref_key", "")
        return f"Vigil Opening: {self.humanize_key(ref)}."




    def _format_resolve_prophecy_reading(self, res, context):
        if not res or res.get("type") == "none":
            return ""
        reading_id = res.get("reading_id", "")
        book = res.get("book", "")
        return f"Prophecy Reading: from {book} ({self.humanize_key(reading_id)})."


    def _format_resolve_prophecy_prok_1(self, res, context):
        if not res:
            return ""
        prok_id = res.get("prokeimenon_id", "")
        return f"First Prokeimenon of the 6th Hour: {self.humanize_key(prok_id)}."


    def _format_resolve_prophecy_prok_2(self, res, context):
        if not res:
            return ""
        prok_id = res.get("prokeimenon_id", "")
        return f"Second Prokeimenon of the 6th Hour: {self.humanize_key(prok_id)}."


    def _format_resolve_psalm_50_intercession(self, res, context):
        if not res:
            return ""
        g = res.get("glory", {})
        bn = res.get("both_now", {})
        s = res.get("sticheron", {})
        return (
            f"After Psalm 50, we sing the Intercession Hymns:\n"
            f"  - Glory: '{g.get('text')}' ({self.humanize_key(g.get('ref_key', ''))})\n"
            f"  - Both now: '{bn.get('text')}' ({self.humanize_key(bn.get('ref_key', ''))})\n"
            f"  - Sticheron: '{s.get('text')}' ({self.humanize_key(s.get('ref_key', ''))})"
        )


    def _format_resolve_fasting_rule(self, res, context):
        if not res:
            return ""
        note = res.get("note", "")
        return f"Fasting Rule: {note}."


    def _format_resolve_prostration_annotation(self, res, context):
        if not res or res.get("forbidden"):
            reason = res.get("reason", "") if res else ""
            return f"Prostrations: Forbidden{f' ({reason})' if reason else ''}."
        ann = res.get("annotation")
        if not ann:
            return ""
        return f"Prostrations: {ann.get('note', '')}."


    def _format_resolve_clergy_variant(self, res, context):
        if not res:
            return ""
        label = res.get("label", "")
        r_range = res.get("ordo_range", "")
        range_str = f" (Range: {r_range})" if r_range else ""
        return f"Clergy variant: {label}{range_str}."

