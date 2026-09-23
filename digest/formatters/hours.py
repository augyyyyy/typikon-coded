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
                return (
                    f"**Troparia:**  \n"
                    f"First Hour – Troparion of the Cross.  \n"
                    f"Third Hour – Troparion of {s_name}.  \n"
                    f"Sixth Hour – Troparion of the Temple.  \n"
                    f"Ninth Hour – Troparion of {s_name}.  \n\n"
                    f"**Kontakia:**  \n"
                    f"First Hour – Kontakion of the Cross.  \n"
                    f"Third Hour – Kontakion of {s_name}.  \n"
                    f"Sixth Hour – Kontakion of the Temple.  \n"
                    f"Ninth Hour – Kontakion of {s_name}."
                )
            return (
                f"**Troparia:**  \n"
                f"First Hour – Troparion of the Day.  \n"
                f"Third & Ninth Hours – Troparion of {s_name}.  \n"
                f"Sixth Hour – Troparion of the Temple.  \n\n"
                f"**Kontakia:**  \n"
                f"First Hour – Kontakion of the Day.  \n"
                f"Third & Ninth Hours – Kontakion of {s_name}.  \n"
                f"Sixth Hour – Kontakion of the Temple."
            )

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
                            sname = self._get_saint_display_name(context, 0, form="full")
                            comps.append(f"troparion of {sname}")
                        elif c == "trop_saint_2":
                            sname2 = self._get_saint_display_name(context, 1, form="full")
                            comps.append(f"troparion of {sname2}")
                        elif c == "trop_day":
                            comps.append("troparion of the Day")
                        elif c == "trop_temple":
                            comps.append("troparion of the Temple")
                        elif c == "trop_feast":
                            fname = self._get_feast_display_name(context, form="short")
                            comps.append(f"troparion of {fname}")
                        elif c in ("glory", "both_now"):
                            pass
                        else:
                            comps.append(self.humanize_key(c, context))
                    first = comps[0]
                    others = comps[1:]
                    if others:
                        trop_str = f"{first}; Glory... {', '.join(others)}"
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
                        kont_str = "Resurrectional kontakion"
                    elif source == "triodion":
                        kont_str = "Kontakion of the Triodion"
                    elif source == "triodion_saint":
                        r_title_lower = rubrics.get("title", "").lower()
                        if "palamas" in r_title_lower:
                            kont_str = "Kontakion of St. Gregory Palamas"
                        elif "john of the ladder" in r_title_lower or "climacus" in r_title_lower:
                            kont_str = "Kontakion of St. John Climacus"
                        else:
                            sname = self._get_saint_display_name(context, 0, form="full")
                            kont_str = f"Kontakion of {sname}"
                    elif source == "saint_or_feast":
                        fname = self._get_feast_display_name(context, form="short")
                        kont_str = f"Kontakion of {fname}"
                    else:
                        if source == "feast":
                            fname = self._get_feast_display_name(context, form="short")
                            kont_str = f"Kontakion of {fname}"
                        elif source in ("saints", "saint"):
                            sname = self._get_saint_display_name(context, 0, form="full")
                            kont_str = f"Kontakion of {sname}"
                        elif source == "saints_2":
                            sname = self._get_saint_display_name(context, 1, form="full")
                            kont_str = f"Kontakion of {sname}"
                            s_list = context.get("saints", [])
                            if len(s_list) >= 2:
                                name = self._clean_name(s_list[1].get("name", "second Saint")).rstrip('.')
                                kont_str = f"Kontakion of {name}"
                            else:
                                kont_str = "Kontakion of the second Saint"
                        else:
                            kont_str = f"Kontakion of {self.humanize_key(source)}"
                else:
                    kont_str = f"Kontakion of the {self.humanize_key(kont_res)}"
                kontakia_by_hour[h] = kont_str
            except Exception as e:
                kontakia_by_hour[h] = f"[ERROR: {e}]"
                
        # Group Troparia by hours
        trop_to_hours = {}
        for h, t in troparia_by_hour.items():
            trop_to_hours.setdefault(t, []).append(h)
            
        trop_lines = []
        for t, hours in sorted(trop_to_hours.items(), key=lambda x: min(x[1])):
            h_names = [self._hour_ordinal(h) for h in hours]
            if len(h_names) == 4:
                h_str = "All Hours"
            elif len(h_names) == 1:
                h_str = f"{h_names[0]} Hour"
            elif len(h_names) == 2:
                h_str = f"{h_names[0]} & {h_names[1]} Hours"
            else:
                h_str = ", ".join(h_names[:-1]) + f" & {h_names[-1]} Hours"
            trop_lines.append(f"{h_str} – {t}.")
        
        # Group Kontakia by hours
        kont_to_hours = {}
        for h, k in kontakia_by_hour.items():
            kont_to_hours.setdefault(k, []).append(h)
            
        kont_lines = []
        for k, hours in sorted(kont_to_hours.items(), key=lambda x: min(x[1])):
            h_names = [self._hour_ordinal(h) for h in hours]
            if len(h_names) == 4:
                h_str = "All Hours"
            elif len(h_names) == 1:
                h_str = f"{h_names[0]} Hour"
            elif len(h_names) == 2:
                h_str = f"{h_names[0]} & {h_names[1]} Hours"
            else:
                h_str = ", ".join(h_names[:-1]) + f" & {h_names[-1]} Hours"
            kont_lines.append(f"{h_str} – {k}.")
            
        trop_block = "**Troparia:**  \n" + "  \n".join(trop_lines)
        kont_block = "**Kontakia:**  \n" + "  \n".join(kont_lines)
        return f"{trop_block}\n\n{kont_block}"


    def _format_resolve_hours_collision(self, res, context):
        if not res or not res.get("troparia_sequence"):
            return ""
        seq = res["troparia_sequence"]
        parts = []
        for t in seq:
            if t.get("type") == "resurrectional":
                parts.append(f"Resurrectional (Tone {t.get('tone')})")
            elif t.get("type") == "glory":
                targ = t.get('target', {})
                name = targ.get('name', targ) if isinstance(targ, dict) else targ
                parts.append(f"Glory... Troparion of {self.humanize_key(name)}")
            elif t.get("type") == "both_now":
                parts.append("Both now... Theotokion of the Hour")
        kont_winner = self.humanize_key(res.get('kontakion_winner', 'according to the Typikon'))
        return f"**Troparia (at all the Hours):**  \n" + "  \n".join(parts) + f"\n\n**Kontakion:**  \n{kont_winner}."


    def _format_resolve_hours_troparia(self, res, context):
        if not res:
            return ""
        mode = res.get("mode")
        if mode == "lenten":
            content = res.get("content", "Lenten Troparion")
            return f"**Troparia (at all the Hours):**  \nLenten troparion ({content})."
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
                    sname = self._get_saint_display_name(context, 0, form="full")
                    mapped.append(f"Troparion of {sname}")
                elif c == "trop_saint_2":
                    sname2 = self._get_saint_display_name(context, 1, form="full")
                    mapped.append(f"Troparion of {sname2}")
                elif c == "trop_day":
                    mapped.append("Troparion of the Day")
                elif c == "trop_temple":
                    mapped.append("Troparion of the Temple")
                elif c == "trop_feast":
                    fname = self._get_feast_display_name(context, form="full")
                    mapped.append(f"Troparion of {fname}")
                else:
                    mapped.append(self.humanize_key(c))
            
            res_str = "  \n".join(mapped)
            return f"**Troparia (at all the Hours):**  \n{res_str}"
        return ""

