class HoursFormatterMixin:
    def _format_qr_hours(self, context, rubrics):
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

        is_simple = (context.get("rank") in ("rank_simple_6", "rank_simple_4") or rubrics.get("variables", {}).get("rank") in ("rank_simple_6", "rank_simple_4")) and not is_fore_after
        if is_weekday and is_simple:
            s_name = "Saint"
            saints = context.get("saints", [])
            if saints:
                s_name_raw = saints[0].get("name", "Saint").strip()
                s_name = self._clean_name(s_name_raw)
            else:
                s_name = "St. Cyril"
            day = context.get("day_of_week", 1)
            if day in (3, 5):
                return f"Troparia: First Hour – Troparion of the Cross; Third Hour – Troparion of {s_name}; Sixth Hour – Troparion of the Temple; Ninth Hour – Troparion of {s_name}. Kontakia: First Hour – Kontakion of the Cross; Third Hour – Kontakion of {s_name}; Sixth Hour – Kontakion of the Temple; Ninth Hour – Kontakion of {s_name}."
            return f"Troparia: First Hour – Day; Third & Ninth Hours – {s_name}; Sixth Hour – Temple. Kontakia: First Hour – Day; Third & Ninth Hours – {s_name}; Sixth Hour – Temple."

        troparia_by_hour = {}
        kontakia_by_hour = {}
        
        for h in [1, 3, 6, 9]:
            h_ctx = {**context, "hour": h}
            try:
                trop_res = self.engine.resolve_hours_troparia(h_ctx, rubrics)
                mode = trop_res.get("mode")
                if mode == "lenten":
                    trop_str = f"Lenten troparion ({self.humanize_key(trop_res.get('content', ''))})"
                else:
                    comps = []
                    saints = context.get("saints", [])
                    for c in trop_res.get("components", []):
                        if c == "trop_resurrection":
                            comps.append("Resurrectional troparion")
                        elif c == "trop_saint":
                            if saints:
                                comps.append(f"troparion of {self._clean_name(saints[0].get('name', 'Saint'))}")
                            else:
                                comps.append("troparion of the Saint")
                        elif c == "trop_saint_2":
                            if len(saints) >= 2:
                                comps.append(f"troparion of {self._clean_name(saints[1].get('name', 'second Saint'))}")
                            else:
                                comps.append("troparion of the second Saint")
                        elif c == "trop_day":
                            comps.append("troparion of the Day")
                        elif c == "trop_temple":
                            comps.append("troparion of the Temple")
                        elif c == "trop_feast":
                            title_lower = context.get("dolnytsky_title", "").lower()
                            lbl = "forefeast" if "forefeast" in title_lower or "prefeast" in title_lower else "afterfeast" if "afterfeast" in title_lower else "feast"
                            comps.append(f"troparion of the {lbl}")
                        elif c in ("glory", "both_now"):
                            pass
                        else:
                            comps.append(self.humanize_key(c))
                    first = comps[0]
                    others = comps[1:]
                    if others:
                        trop_str = f"{first}, Glory... {', '.join(others)}"
                    else:
                        trop_str = first
                troparia_by_hour[h] = trop_str
            except Exception as e:
                troparia_by_hour[h] = f"[ERROR: {e}]"
                
            try:
                kont_res = self.engine.resolve_hours_kontakion(h_ctx, rubrics)
                if isinstance(kont_res, dict):
                    source = kont_res.get("source")
                    if source == "resurrection":
                        kont_str = "Resurrection"
                    elif source == "triodion":
                        kont_str = "Triodion"
                    elif source == "triodion_saint":
                        r_title_lower = rubrics.get("title", "").lower()
                        if "palamas" in r_title_lower:
                            kont_str = "St. Gregory Palamas"
                        elif "john of the ladder" in r_title_lower or "climacus" in r_title_lower:
                            kont_str = "St. John Climacus"
                        else:
                            kont_str = "Saint"
                    elif source == "saint_or_feast":
                        title_lower = context.get("dolnytsky_title", "").lower()
                        lbl = "forefeast" if "forefeast" in title_lower or "prefeast" in title_lower else "afterfeast" if "afterfeast" in title_lower else "feast"
                        kont_str = lbl
                    else:
                        if source == "feast":
                            pascha_offset = context.get("pascha_offset")
                            if pascha_offset is not None and 60 <= pascha_offset <= 67:
                                kont_str = "Kontakion of the Eucharist"
                            else:
                                title = context.get("dolnytsky_title") or "Feast"
                                kont_str = f"Kontakion of the {self.humanize_key(title)}"
                        elif source in ("saints", "saint"):
                            s_list = context.get("saints", [])
                            if s_list:
                                name = self._clean_name(s_list[0].get("name", "Saint")).rstrip('.')
                                kont_str = f"Kontakion of {name}"
                            else:
                                kont_str = "Kontakion of the Saint"
                        elif source == "saints_2":
                            s_list = context.get("saints", [])
                            if len(s_list) >= 2:
                                name = self._clean_name(s_list[1].get("name", "second Saint")).rstrip('.')
                                kont_str = f"Kontakion of {name}"
                            else:
                                kont_str = "Kontakion of the second Saint"
                        else:
                            kont_str = self.humanize_key(source)
                else:
                    kont_str = self.humanize_key(kont_res)
                kontakia_by_hour[h] = kont_str
            except Exception as e:
                kontakia_by_hour[h] = f"[ERROR: {e}]"
                
        # Group Troparia by hours
        trop_to_hours = {}
        for h, t in troparia_by_hour.items():
            trop_to_hours.setdefault(t, []).append(h)
            
        trop_parts = []
        for t, hours in sorted(trop_to_hours.items(), key=lambda x: min(x[1])):
            h_names = [self._hour_ordinal(h) for h in hours]
            if len(h_names) == 4:
                h_str = "all the hours"
            elif len(h_names) == 1:
                h_str = f"the {h_names[0]} Hour"
            elif len(h_names) == 2:
                h_str = f"the {h_names[0]} and {h_names[1]} Hours"
            else:
                h_str = "the " + ", ".join(h_names[:-1]) + f", and {h_names[-1]} Hours"
            trop_parts.append(f"At {h_str}: {t}")
        line1 = "; ".join(trop_parts) + "."
        
        # Group Kontakia by hours
        kont_to_hours = {}
        for h, k in kontakia_by_hour.items():
            kont_to_hours.setdefault(k, []).append(h)
            
        kont_parts = []
        for k, hours in sorted(kont_to_hours.items(), key=lambda x: min(x[1])):
            h_names = [self._hour_ordinal(h) for h in hours]
            if len(h_names) == 4:
                h_str = "all the hours"
            elif len(h_names) == 1:
                h_str = f"the {h_names[0]} Hour"
            elif len(h_names) == 2:
                h_str = f"the {h_names[0]} and {h_names[1]} Hours"
            else:
                h_str = "the " + ", ".join(h_names[:-1]) + f", and {h_names[-1]} Hours"
            kont_parts.append(f"at {h_str} – {k}")
            
        line2 = "Kontakia: " + "; ".join(kont_parts) + "."
        return f"**At the Hours:** {line1}\n{line2}"


    def _format_resolve_hours_collision(self, res, context):
        if not res or not res.get("troparia_sequence"):
            return ""
        seq = res["troparia_sequence"]
        parts = ["At all the hours: We sing the troparia"]
        for t in seq:
            if t.get("type") == "resurrectional":
                parts.append(f"Resurrectional Tone {t.get('tone')}")
            elif t.get("type") == "glory":
                targ = t.get('target', {})
                name = targ.get('name', targ) if isinstance(targ, dict) else targ
                parts.append(f"Glory... {self.humanize_key(name)}")
            elif t.get("type") == "both_now":
                parts.append("Both now... Theotokion")
        kont_winner = self.humanize_key(res.get('kontakion_winner', 'according to the Typikon'))
        return "; ".join(parts) + f". Kontakion: {kont_winner}."


    def _format_resolve_hours_troparia(self, res, context):
        if not res:
            return ""
        mode = res.get("mode")
        if mode == "lenten":
            content = res.get("content", "Lenten Troparion")
            return f"At all the hours: We sing the Lenten troparion: {content}."
        elif mode == "standard":
            mapped = []
            saints = context.get("saints", [])
            for c in res.get("components", []):
                if c == "trop_resurrection":
                    mapped.append("Resurrectional Troparion")
                elif c == "glory":
                    mapped.append("Glory...")
                elif c == "both_now":
                    mapped.append("Both now...")
                elif c == "trop_saint":
                    if saints:
                        mapped.append(f"Troparion of {self.humanize_key(saints[0].get('name', 'Saint'))}")
                    else:
                        mapped.append("Troparion of the Saint")
                elif c == "trop_saint_2":
                    if len(saints) >= 2:
                        mapped.append(f"Troparion of {self.humanize_key(saints[1].get('name', 'second Saint'))}")
                    else:
                        mapped.append("Troparion of the second Saint")
                elif c == "trop_day":
                    mapped.append("Troparion of the Day")
                elif c == "trop_temple":
                    mapped.append("Troparion of the Temple")
                elif c == "trop_feast":
                    mapped.append("Troparion of the Feast")
                else:
                    mapped.append(self.humanize_key(c))
            
            res_str = ""
            for item in mapped:
                if item in ("Glory...", "Both now..."):
                    if res_str and not res_str.endswith(";"):
                        res_str = res_str.rstrip()
                        res_str += "; "
                    res_str += f"{item} "
                else:
                    if res_str and not res_str.endswith(" "):
                        res_str += "; "
                    res_str += item
            return f"At all the hours: We sing the troparia: {res_str}."
        return ""

