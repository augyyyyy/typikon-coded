import json
import os
import re
import copy
from datetime import datetime

class TypikonDigestGenerator:
    def __init__(self, engine):
        self.engine = engine

    def _roman_tone(self, tone):
        try:
            val = int(tone)
            return {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII"}.get(val, str(val))
        except (ValueError, TypeError):
            return str(tone)


    def humanize_key(self, key):
        if not key:
            return ""
        if isinstance(key, dict):
            key = key.get('source', key.get('ref_key', ''))
        key = str(key).strip()
        
        key_lower = key.lower()
        if key_lower == "triodion.doxasticon":
            return "doxasticon from the Triodion"
        if key_lower == "menaion.forefeast.doxasticon":
            return "doxasticon of the forefeast"
        if key_lower == "menaion.feast.doxasticon":
            return "doxasticon of the feast"
        if key_lower in ("dogmatikon_current_tone", "dogmatikon_tone_week") or "dogmatikon" in key_lower:
            return "Dogmatic Theotokion in the tone of the week"
        if key_lower == "menaion.feast.litiya.glory":
            return "doxasticon of the feast"
        if key_lower == "menaion.feast.litiya.both_now":
            return "both now of the feast"
            
        # Strip trailing dot if present to prevent empty split parts
        if key.endswith('.'):
            key = key[:-1]
            
        # Extract the base part (after the last dot)
        parts = key.split('.')
        base = parts[-1] if parts else key
        
        # Tone numbers matching: e.g. tone_1 -> Tone 1
        tone_match = re.search(r'tone_(\d+)', base, re.IGNORECASE)
        if tone_match:
            tone_num = tone_match.group(1)
            base_cleaned = re.sub(r'_?tone_\d+', '', base, flags=re.IGNORECASE)
            if not base_cleaned and len(parts) > 1:
                base_cleaned = ".".join(parts[:-1])
            base_human = self.humanize_key(base_cleaned)
            if base_human:
                return f"{base_human} in Tone {tone_num}"
            else:
                return f"Tone {tone_num}"


        # Eothinon stichera matching: e.g. eothinon_1_stichera -> Gospel Sticheron I
        eothinon_match = re.match(r'eothinon_(\d+)_stichera', base, re.IGNORECASE)
        if eothinon_match:
            num = int(eothinon_match.group(1))
            romans = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
            roman = romans[num] if num < len(romans) else str(num)
            return f"Gospel Sticheron {roman}"
            
        # Eothinon exapostilarion matching
        ex_match = re.match(r'(?:eothinon_)?exapostilarion_(\d+)', base, re.IGNORECASE)
        if ex_match:
            num = int(ex_match.group(1))
            romans = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
            roman = romans[num] if num < len(romans) else str(num)
            return f"Gospel Exapostilarion {roman}"
            
        # Eothinon theotokion matching: matches eothinon_theotokion_x or exapostilarion_theotokion_x
        theo_match = re.match(r'(?:eothinon_|exapostilarion_)?theotokion_(\d+)', base, re.IGNORECASE)
        if theo_match:
            num = int(theo_match.group(1))
            romans = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
            roman = romans[num] if num < len(romans) else str(num)
            return f"Theotokion of Gospel Exapostilarion {roman}"

        mapping = {
            "dogmatikon_current_tone": "Dogmatic Theotokion in the Tone of the week",
            "dogmatikon_tone_week": "Dogmatic Theotokion in the Tone of the week",
            "dogmatikon": "Dogmatic Theotokion",
            "theotokion_daily": "daily Theotokion",
            "open_to_me_the_doors_of_repentance": "Open to me the doors of repentance",
            "on_the_paths_of_salvation": "On the paths of salvation",
            "when_i_think_of_the_many_evil_things_i_have_done": "When I think of the many evil things I have done",
            "saint_doxastikon_if_present": "Doxastikon of the Saint if present",
            "saint_doxastikon": "Doxastikon of the Saint",
            "saint": "Saint",
            "saint_1": "Saint",
            "saint_2": "Saint",
            "forefeast": "Forefeast",
            "afterfeast": "Afterfeast",
            "octoechos": "Octoechos",
            "triodion": "Triodion",
            "menaion": "Menaion",
            "resurrection": "Resurrection",
            "res": "Resurrectional",
            "resurrectional": "Resurrectional",
            "aposticha_theotokion": "Aposticha Theotokion",
            "sidalen": "Sessional Hymn",
            "kathisma": "Kathisma",
            "prokeimenon": "Prokeimenon",
            "psalm_92_lord_is_king": "The Lord is King (Psalm 92)",
            "alleluia": "Alleluia",
            "gospel": "Gospel",
            "epistle": "Epistle",
            "megalynarion": "Megalynarion",
            "canon": "Canon",
            "katavasia": "Katavasia",
            "exapostilarion": "Exapostilarion",
            "praises": "Praises",
            "dismissal": "Dismissal",
            "troparion": "Troparion",
            "kontakion": "Kontakion",
            "beatitudes": "Beatitudes",
            "typika": "Typika",
            "communion_hymn": "Communion Hymn",
            "kinonicon": "Communion Hymn",
            "litya": "Litiya",
            "artoklasia": "Artoklasia",
            "magnification": "Magnification",
            "polyeleos": "Polyeleos",
            "sessional_triodion_set_1": "Sessional Hymns of the Feast from the Triodion",
            "sessional_triodion_set_2": "Sessional Hymns of the Feast from the Triodion",
        }
        
        lower_base = base.lower()
        if lower_base in mapping:
            return mapping[lower_base]
            
        words = base.replace('_', ' ').split()
        capitalized_words = []
        for w in words:
            if w.lower() in ('of', 'the', 'in', 'and', 'to', 'a', 'for', 'with', 'from', 'at'):
                capitalized_words.append(w.lower())
            else:
                capitalized_words.append(w.capitalize())
        return " ".join(capitalized_words)

    def generate(self, context, rubrics, mode="full"):
        if mode == "full":
            return self.generate_full_service(context, rubrics)
        return self.generate_quick_reference(context, rubrics)

    def generate_full_service(self, context, rubrics):
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
        except (ValueError, TypeError):
            formatted_date = date_str
            dt = None

            
        digest.append(f"TYPICON: {formatted_date}")
        
        # 2. Title and Tone
        title = rubrics.get('title', 'NORMAL DAY').upper()
        tone_str = context.get('tone', '')
        if tone_str:
            title += f" - TONE {self._roman_tone(tone_str)}"
        digest.append(title)
        
        # 3. Saints List
        if "saints" in context:
             saints_str = "; ".join(s.get("name", s.get("id", "")) for s in context["saints"])
             if saints_str:
                 digest.append(saints_str)
                 
        # 4. Service Combination Header
        try:
            res = self.engine.resolve_service_combination_header(context, rubrics)
            if res and res.get("components"):
                comps = [c.replace(" from the Octoechos", "") for c in res["components"] 
                         if not c.lower().startswith("st. forefeast") and not c.lower().startswith("st. afterfeast")]
                if comps:
                    header = comps[0]
                    if len(comps) > 1: header += " combined with " + comps[1]
                    for c in comps[2:]: header += ", and that of " + c
                    digest.append(header.capitalize() + ".")
        except Exception as e:
            digest.append(f"[ERROR: resolve_service_combination_header failed - {e}]")

        # 5. Saint Transfer Note
        try:
            res = self.engine.resolve_saint_transfer(context, rubrics)
            if res and res.get("transferred"):
                target = res.get('target', 'a convenient time').replace('_', ' ')
                digest.append(f"The service to {res.get('saint_name', 'the Saint')} is transferred to {target}.")
        except Exception as e:
            digest.append(f"[ERROR: resolve_saint_transfer failed - {e}]")

        # 6. Vestment Colors
        try:
            res = self.engine.resolve_vestment_color(context, rubrics)
            if res and res.get("color"):
                color = res["color"].capitalize()
                alt = f" or {res['alt'].replace('_', ' ')}" if res.get("alt") else ""
                is_dark = res["color"] in ("black", "dark_purple", "purple")
                tone_type = "Dark" if is_dark else "Bright"
                if res["color"] == "gold" and "white" in alt:
                    digest.append(f"Vestment colour: Bright [blue for the forefeast or gold].")
                else:
                    digest.append(f"Vestment colour: {tone_type} ({color}{alt}).")
        except Exception as e:
            digest.append(f"[ERROR: resolve_vestment_color failed - {e}]")
             
        digest.append("")

        # 7. Traverse Daily Cycle
        matins_override = None
        if context.get("triodion_period") == "holy_friday":
            matins_override = "tomb_matins"
        elif context.get("triodion_period") in ["pascha", "bright_week"]:
            matins_override = "bright_matins"
        elif context.get("triodion_period") == "holy_week_weekday" and context.get("day_of_week") in [4, 5]:
            matins_override = "passion_matins"
        elif context.get("triodion_period") == "holy_week_weekday" and context.get("day_of_week") in [1, 2, 3]:
            matins_override = "bridegroom_matins"

        for service in self.engine.daily_cycle:
            context["overrides"] = rubrics.get("overrides", {})
            service_name = service["name"]
            
            # Suppression logic for Vesperal Liturgy & Presanctified
            is_vesperal_liturgy = (
                "vesperal_merge_logic" in rubrics.get("overrides", {}).get("liturgy_type", "") or
                "vesperal_merge_logic" in rubrics.get("variables", {}).get("liturgy_type", "")
            )
            is_presanctified_liturgy = (
                rubrics.get("variables", {}).get("liturgy_type") == "liturgy_presanctified" or 
                rubrics.get("overrides", {}).get("liturgy_type") == "liturgy_presanctified" or
                (hasattr(self.engine, "check_presanctified_trigger") and self.engine.check_presanctified_trigger(context))
            )
            if service_name == "Vespers" and (is_vesperal_liturgy or is_presanctified_liturgy):
                continue

            if service_name == "Vespers":
                try:
                    small_vespers_needed_res = self.engine.resolve_small_vespers_needed(context, rubrics)
                except Exception as e:
                    small_vespers_needed_res = None
                    digest.append(f"[RESOLVE ERROR: resolve_small_vespers_needed: {e}]")
                
                if small_vespers_needed_res and small_vespers_needed_res.get("needed"):
                    struct_data = self.engine._load_json("json_db/01h_struct_vespers.json")
                    skeleton = self.engine._get_structure_sequence(struct_data, "small_vespers")
                    if skeleton:
                        digest.append("=== SMALL VESPERS ===")
                        small_context = context.copy()
                        small_context["is_small_vespers"] = True
                        small_context["active_structure_id"] = "small_vespers"
                        self._process_skeleton(skeleton, small_context, rubrics, digest)
                        digest.append("")

            # Resolve root_id
            root_id = service["root"]
            if service["type_key"] in rubrics.get("variables", {}):
                root_id = rubrics["variables"][service["type_key"]]
            if service["type_key"] in rubrics.get("overrides", {}):
                root_id = rubrics["overrides"][service["type_key"]]

            if root_id == "structure_suppressed":
                continue

            # Apply specific overrides
            if service_name == "Matins" and matins_override:
                root_id = matins_override

            struct_file = service["file"]
            if "hours_type" in service["type_key"]:
                var_hours = rubrics.get("variables", {}).get("hours_type", "")
                is_royal = "royal" in var_hours or (hasattr(self.engine, "check_royal_hours_trigger") and self.engine.check_royal_hours_trigger(context))
                if is_royal:
                    root_id = "structure_royal"
                    struct_file = "json_db/01k_struct_royal_hours.json"
                    
                    hour_map = {
                        "First Hour": 1,
                        "Third Hour": 3,
                        "Sixth Hour": 6,
                        "Ninth Hour": 9
                    }
                    context["hour"] = hour_map.get(service_name, 1)
                elif "lenten" in var_hours:
                    root_id = "structure_lenten"
                elif "paschal" in var_hours:
                    root_id = "structure_paschal"

            if service_name == "Midnight Office":
                 mode_data = self.engine.resolve_midnight_office_mode(context)
                 if "mode" in mode_data:
                     root_id = f"midnight_{mode_data['mode']}"

            # Load the structure sequence
            struct_data = self.engine._load_json(struct_file)
            skeleton = self.engine._get_structure_sequence(struct_data, root_id)

            if not skeleton:
                digest.append(f"=== {service_name.upper()} ===")
                digest.append(f"[ERROR: Structure '{root_id}' not found in {struct_file}]")
                digest.append("")
                continue

            # Print service name header
            expanded_name = self.engine.get_expanded_service_name(service, context).upper()
            digest.append(f"=== {expanded_name} ===")

            # Walk sequence
            service_context = context.copy()
            service_context["active_structure_id"] = root_id
            self._process_skeleton(skeleton, service_context, rubrics, digest)
            digest.append("")

        # Flatten all lines and split by \n
        raw_lines = []
        for item in digest:
            if not item:
                raw_lines.append("")
            elif isinstance(item, str):
                raw_lines.extend(item.splitlines())
            else:
                raw_lines.append(str(item))
                
        formatted_md = []
        for line in raw_lines:
            line_str = line.strip()
            if not line_str:
                formatted_md.append("")
                continue
                
            if line_str.startswith("TYPICON:"):
                if formatted_md and formatted_md[-1] != "":
                    formatted_md.append("")
                formatted_md.append(f"# {line_str}")
                formatted_md.append("")
            elif line_str.startswith("===") and line_str.endswith("==="):
                title = line_str.replace("===", "").strip()
                if formatted_md and formatted_md[-1] != "":
                    formatted_md.append("")
                formatted_md.append(f"## {title}")
                formatted_md.append("")
            elif line_str.startswith("RUBRIC:"):
                rubric_text = line_str.replace("RUBRIC:", "").strip()
                if formatted_md and formatted_md[-1] != "":
                    formatted_md.append("")
                formatted_md.append("> [!NOTE]")
                formatted_md.append(f"> **Rubric**: {rubric_text}")
                formatted_md.append("") # Close the blockquote
            else:
                # Add two spaces at the end of the line to force a line break in Markdown
                formatted_md.append(f"{line_str}  ")
                
        return "\n".join(formatted_md)

    def _get_eothinon_gospel_citation(self, num):
        for key in (f"eothinon.{num}.gospel", f"eothinon.eothinon_{num}_gospel"):
            try:
                asset = self.engine.get_text(key)
                if asset and asset.get("content"):
                    parts = asset["content"].split("\n\n")
                    if parts:
                        return parts[0].strip()
            except Exception:
                pass
        return ""

    def _format_qr_hours(self, context, rubrics):
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
                                comps.append(f"troparion of {self.humanize_key(saints[0].get('name', 'Saint'))}")
                            else:
                                comps.append("troparion of the Saint")
                        elif c == "trop_saint_2":
                            if len(saints) >= 2:
                                comps.append(f"troparion of {self.humanize_key(saints[1].get('name', 'second Saint'))}")
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
                        kont_str = self.humanize_key(source)
                else:
                    kont_str = self.humanize_key(kont_res)
                kontakia_by_hour[h] = kont_str
            except Exception as e:
                kontakia_by_hour[h] = f"[ERROR: {e}]"
                
        unique_troparia = set(troparia_by_hour.values())
        if len(unique_troparia) == 1:
            line1 = f"At all the hours: {list(unique_troparia)[0]}."
        else:
            parts = []
            for h in [1, 3, 6, 9]:
                parts.append(f"at the {self._hour_name(h)} – {troparia_by_hour[h]}")
            line1 = "At the hours: " + "; ".join(parts) + "."
            
        kont_to_hours = {}
        for h, k in kontakia_by_hour.items():
            kont_to_hours.setdefault(k, []).append(h)
            
        kont_parts = []
        for k, hours in sorted(kont_to_hours.items(), key=lambda x: min(x[1])):
            h_names = []
            for h in hours:
                h_names.append(self._hour_ordinal(h))
            if len(h_names) == 1:
                h_str = h_names[0]
            elif len(h_names) == 2:
                h_str = f"{h_names[0]} and {h_names[1]}"
            else:
                h_str = ", ".join(h_names[:-1]) + f" and {h_names[-1]}"
            kont_parts.append(f"at the {h_str} – {k}")
            
        line2 = "Kontakia: " + "; ".join(kont_parts) + "."
        return f"{line1}\n{line2}"

    def _hour_name(self, h):
        return {1: "First Hour", 3: "Third Hour", 6: "Sixth Hour", 9: "Ninth Hour"}.get(h, f"{h}th Hour")

    def _hour_ordinal(self, h):
        return {1: "First", 3: "Third", 6: "Sixth", 9: "Ninth"}.get(h, str(h))

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
            
        lines = []
        for reading in readings_data:
            p = reading.get("prokeimenon", {})
            if p:
                tone = p.get("tone")
                ref = self.humanize_key(p.get("ref_key", ""))
                t_str = f"Tone {self._roman_tone(tone)}" if tone else ""
                ref_clean = ref.replace("Prokimenon", "").strip()
                if ref_clean:
                    lines.append(f"**Prokimenon:**\t{t_str}: \"{ref_clean}...\"")
                else:
                    lines.append(f"**Prokimenon:**\t{t_str}")
                    
            e = reading.get("epistle", {})
            if e:
                ref = self.humanize_key(e.get("ref_key", ""))
                lines.append(f"**Epistle:**\t\t{ref}")
                
            a = reading.get("alleluia", {})
            if a:
                tone = a.get("tone")
                ref = self.humanize_key(a.get("ref_key", ""))
                t_str = f"Tone {self._roman_tone(tone)}" if tone else ""
                lines.append(f"**Alleluia:**\t\t{t_str}")
                
            g = reading.get("gospel", {})
            if g:
                ref = self.humanize_key(g.get("ref_key", ""))
                lines.append(f"**Gospel:**\t\t{ref}")
                
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
                lines.append(f"**Kinonicon:**\t\"{kin_res['text']}\"")
        except Exception as e:
            pass
            
        return "\n".join(lines)

    def generate_quick_reference(self, context, rubrics):
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
        except (ValueError, TypeError):
            formatted_date = date_str
            dt = None
            
        digest.append(f"# TYPICON: {formatted_date}")
        
        # 2. Title and Tone
        title = rubrics.get('title', 'NORMAL DAY').upper()
        tone_str = context.get('tone', '')
        if tone_str:
            title += f" - TONE {self._roman_tone(tone_str)}"
        digest.append(f"## {title}")
        
        # 3. Saints List (including transferred)
        saints = context.get("saints", [])
        transferred_saints = context.get("transferred_saints", [])
        all_saints = list(saints) + list(transferred_saints)
        if all_saints:
            saints_str = "; ".join(s.get("name", s.get("id", "")) for s in all_saints)
            if saints_str:
                digest.append(f"{saints_str}  ")
                
        # 4. Service Combination Header
        try:
            res = self.engine.resolve_service_combination_header(context, rubrics)
            if res and res.get("components"):
                comps = [c.replace(" from the Octoechos", "") for c in res["components"] 
                         if not c.lower().startswith("st. forefeast") and not c.lower().startswith("st. afterfeast")]
                if comps:
                    header = comps[0]
                    if len(comps) > 1: header += " combined with " + comps[1]
                    for c in comps[2:]: header += ", and that of " + c
                    digest.append(f"{header.capitalize()}.  ")
        except Exception as e:
            digest.append(f"[RESOLVE ERROR: resolve_service_combination_header: {e}]  ")
            
        # 5. Saint Transfer Note
        try:
            res = self.engine.resolve_saint_transfer(context, rubrics)
            if res and res.get("transferred"):
                target = res.get('target', 'a convenient time').replace('_', ' ')
                digest.append(f"The service to {res.get('saint_name', 'the Saint')} is transferred to {target}.  ")
        except Exception as e:
            digest.append(f"[RESOLVE ERROR: resolve_saint_transfer: {e}]  ")
            
        # 6. Vestment Colors
        try:
            res = self.engine.resolve_vestment_color(context, rubrics)
            if res and res.get("color"):
                color = res["color"].capitalize()
                alt = f" or {res['alt'].replace('_', ' ')}" if res.get("alt") else ""
                is_dark = res["color"] in ("black", "dark_purple", "purple")
                tone_type = "Dark" if is_dark else "Bright"
                if res["color"] == "gold" and "white" in alt:
                    digest.append(f"**Vestment colour:** Bright [blue for the forefeast or gold].  ")
                else:
                    citation = res.get("citation", "")
                    if "purple" in citation.lower() and "gold" in citation.lower():
                        digest.append(f"**Vestment colour:** Bright [deep gold, or, in some places, gold with purple].  ")
                    else:
                        digest.append(f"**Vestment colour:** {tone_type} [{color}{alt}].  ")
        except Exception as e:
            digest.append(f"[RESOLVE ERROR: resolve_vestment_color: {e}]  ")
            
        digest.append("")
        
        enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
        enriched["overrides"] = rubrics.get("overrides", {})
        if rubrics.get("is_sunday_vigil"):
            enriched["is_sunday_vigil"] = True
            
        active_services = [s["name"] for s in self.engine.daily_cycle]
        
        is_vespers_active = "Vespers" in active_services and rubrics.get("overrides", {}).get("vespers_type") != "structure_suppressed"
        if context.get("day_of_week") == 0:
            is_vespers_active = True
            
        if is_vespers_active:
            digest.append("## GREAT VESPERS")
            
            try:
                res = self.engine.resolve_vespers_stichera(enriched)
                formatted = self._format_resolve_vespers_stichera(res, enriched)
                if formatted:
                    if formatted.startswith("At O Lord, I have cried, we sing"):
                        formatted = "**At O Lord, I have cried…** we sing" + formatted[len("At O Lord, I have cried, we sing"):]
                    elif formatted.startswith("At O Lord, I have cried"):
                        formatted = "**At O Lord, I have cried…**" + formatted[len("At O Lord, I have cried"):]
                    digest.append(f"{formatted}  ")
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: resolve_vespers_stichera: {e}]  ")
                
            try:
                res = self.engine.resolve_litya_content(enriched)
                formatted = self._format_resolve_litya_content(res, enriched)
                if formatted:
                    if formatted.startswith("If Litiya is performed:"):
                        formatted = "**If Litiya is performed:**" + formatted[len("If Litiya is performed:"):]
                    digest.append(f"{formatted}  ")
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: resolve_litya_content: {e}]  ")
                
            try:
                res = self.engine.resolve_aposticha(enriched)
                formatted = self._format_resolve_aposticha(res, enriched)
                if formatted:
                    if formatted.startswith("At the Aposticha, we sing:"):
                        formatted = "**At the Aposticha:** We sing" + formatted[len("At the Aposticha, we sing:"):]
                    elif formatted.startswith("At the Aposticha"):
                        formatted = "**At the Aposticha:**" + formatted[len("At the Aposticha"):]
                    digest.append(f"{formatted}  ")
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: resolve_aposticha: {e}]  ")
                
            try:
                res = self.engine.resolve_vespers_troparia_simple(enriched, rubrics)
                formatted = self._format_resolve_vespers_troparia_simple(res, enriched)
                if formatted:
                    if formatted.startswith("At the Dismissal Troparia, we sing:"):
                        formatted = "**At the Dismissal Troparia:**\nWe sing" + formatted[len("At the Dismissal Troparia, we sing:"):]
                    digest.append(f"{formatted}  ")
                    
                if context.get("day_of_week") == 0:
                    title_lower = title.lower()
                    if "prodigal son" in title_lower:
                        digest.append("Or, if Vigil is served: Rejoice, O Virgin Theotokos... twice; troparion of the forefeast, once.  ")
                    elif "last judgement" in title_lower:
                        digest.append("Or, if Vigil is served: Rejoice, O Virgin Theotokos... twice; troparion of the feast, once.  ")
                    elif "cheesefare" in title_lower:
                        digest.append("Or, if Vigil is served: Rejoice, O Virgin Theotokos... thrice.  ")
                    elif "orthodoxy" in title_lower:
                        digest.append("Or, if Vigil is served: Rejoice, O Virgin Theotokos... twice, troparion from the Triodion, once.  ")
                    elif "palamas" in title_lower:
                        digest.append("Or, if Vigil is served: Rejoice, O Virgin Theotokos... twice, troparion of the Saint, once.  ")
                    elif "cross" in title_lower:
                        digest.append("Or, if Vigil is served: Rejoice, O Virgin Theotokos... twice, troparion of the Cross, once.  ")
                    elif "climacus" in title_lower:
                        digest.append("Or, if Vigil is served: Rejoice, O Virgin Theotokos... twice, troparion of the Saint, once.  ")
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: resolve_vespers_troparia_simple: {e}]  ")
                
            digest.append("")
            
        if "Matins" in active_services and rubrics.get("overrides", {}).get("matins_type") != "structure_suppressed":
            digest.append("## MATINS")
            
            try:
                res = self.engine.resolve_god_is_the_lord(enriched, rubrics)
                formatted = self._format_resolve_god_is_the_lord_troparia(res, enriched)
                if formatted:
                    if formatted.startswith("At The Lord is God, we sing:"):
                        formatted = "**At The Lord is God…** we sing" + formatted[len("At The Lord is God, we sing:"):]
                    digest.append(f"{formatted}  ")
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: resolve_god_is_the_lord: {e}]  ")
                
            if context.get("day_of_week") == 0:
                digest.append("After each cathisma we sing the sessional hymns from the Octoechos.  ")
            else:
                try:
                    res = self.engine.resolve_sidalen_content(enriched)
                    formatted = self._format_resolve_sidalen_content(res, enriched)
                    if formatted:
                        digest.append(f"{formatted}  ")
                except Exception as e:
                    digest.append(f"[RESOLVE ERROR: resolve_sidalen_content: {e}]  ")
                    
            try:
                res = self.engine.resolve_polyeleos_or_kathisma_17(enriched, rubrics)
                formatted = self._format_resolve_polyeleos_or_kathisma_17(res, enriched)
                if formatted:
                    digest.append(f"{formatted}  ")
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: resolve_polyeleos_or_kathisma_17: {e}]  ")
                
            if context.get("day_of_week") == 0:
                t_val = self._roman_tone(context.get("tone", 1))
                digest.append(f"After, the Evlogitaria: the Hypakoë (Tone {t_val}), Hymns of Ascents, Prokeimenon, Let everything that has breath: in the tone of the week.  ")
                
            try:
                res = self.engine.resolve_matins_gospel(enriched)
                if res:
                    eothinon_num = enriched.get("eothinon_number", 1)
                    citation = self._get_eothinon_gospel_citation(eothinon_num)
                    rom_num = self._roman_tone(eothinon_num)
                    cit_str = f": {citation}" if citation else ""
                    digest.append(f"**Matins Gospel {rom_num}**{cit_str}.  ")
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: resolve_matins_gospel: {e}]  ")
                
            try:
                res = self.engine.resolve_post_gospel_stichera(enriched)
                if res and any("open_to_me" in s for s in res):
                    digest.append("After Psalm 50: instead of the usual hymns, we sing: Glory: Open to me the doors of repentance..., Both now: On the paths of salvation... and after the refrain Have mercy on me, O God, the sticheron: When I think of the many evil things I have done.  ")
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: resolve_post_gospel_stichera: {e}]  ")
                
            digest.append("**At the Canon (abbreviated for parish use):**  ")
            
            # Resolve katavasia to use in formatting
            kat_str = ""
            try:
                kat_res = self.engine.resolve_katavasia(enriched)
                if kat_res:
                    kat_str = self._format_resolve_katavasia(kat_res, enriched)
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: resolve_katavasia: {e}]  ")
            
            # Dynamically format the abbreviated parish-use canon details
            for line in self._generate_abbreviated_canon_lines(enriched, kat_str):
                digest.append(f"  {line}  ")
                
            try:
                canon_res = self.engine.resolve_canon_stack(enriched)
                dist = canon_res.get("distribution", [])
                parts = []
                for item in dist:
                    src = self.humanize_key(item.get("source", ""))
                    qty = item.get("qty", item.get("count", 0))
                    typ = item.get("type", "")
                    name = src
                    if src.lower() == "octoechos" and typ:
                        name = self.humanize_key(typ)
                    if name.lower() == "forefeast":
                        name = "Menaion"
                    extra = " (including the irmos)" if item.get("irmos") else ""
                    parts.append(f"{name} - {qty}{extra}")
                
                # Format Katavasia for suffix
                kat_suffix = ""
                try:
                    kat_res = self.engine.resolve_katavasia(enriched)
                    if kat_res:
                        kat_text = kat_res.get("text", "")
                        if "encounter" in kat_res.get("id", "").lower() or "meeting" in kat_res.get("id", "").lower():
                            kat_suffix = "  Catabasia of the Encounter."
                        elif kat_text:
                            tone_roman = self._roman_tone(kat_res.get("tone", 4))
                            kat_suffix = f"  Catabasia Tone {tone_roman} \"{kat_text} . . . \"."
                except Exception as e_kat:
                    kat_suffix = f"  [RESOLVE ERROR: resolve_katavasia: {e_kat}]"
                
                full_order_str = f"Full order of the canon (according to the typicon): {', '.join(parts)}.{kat_suffix}"
                digest.append(f"{full_order_str}  ")
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: resolve_canon_stack: {e}]  ")
                
            digest.append(self._format_canon_interludes_ode_3(enriched))
            digest.append(self._format_canon_interludes_ode_6(enriched))
                
            try:
                res = self.engine.resolve_magnificat(enriched, rubrics)
                if res and res.get("type") == "suppressed_magnificat":
                    digest.append("After Ode VIII: we do not sing the Magnificat.  ")
                else:
                    digest.append("After Ode VIII: we sing the Magnificat.  ")
            except Exception as e:
                digest.append("After Ode VIII: we sing the Magnificat.  ")
                
            if context.get("day_of_week") == 0:
                t_val = self._roman_tone(context.get("tone", 1))
                digest.append(f"Holy is the Lord... Tone {t_val}.  ")
                
            try:
                res = self.engine.resolve_exapostilarion_matins(enriched)
                formatted = self._format_resolve_exapostilarion_matins(res, enriched)
                if formatted:
                    if formatted.startswith("Exapostilarion:"):
                        formatted = "**Exapostilarion** -" + formatted[len("Exapostilarion:"):]
                    digest.append(f"{formatted}  ")
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: resolve_exapostilarion_matins: {e}]  ")
                
            try:
                res = self.engine.resolve_praises_stichera(enriched)
                formatted = self._format_resolve_praises_stichera(res, enriched)
                if formatted:
                    if formatted.startswith("At the Praises, we sing "):
                        formatted = "**At the Praises:** We sing " + formatted[len("At the Praises, we sing "):]
                    elif formatted.startswith("At the Praises"):
                        formatted = "**At the Praises:**" + formatted[len("At the Praises"):]
                    digest.append(f"{formatted}  ")
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: resolve_praises_stichera: {e}]  ")
                
            if context.get("day_of_week") == 0:
                try:
                    eothinon_num = enriched.get("eothinon_number", 1)
                    rom_num = self._roman_tone(eothinon_num)
                    digest.append(f"After the Dismissal of Matins: Glory... both now... Gospel Sticheron {rom_num}.  ")
                except Exception as e:
                    digest.append(f"[RESOLVE ERROR: gospel_sticheron_formatting: {e}]  ")
                    
            digest.append("")
            
        if "First Hour" in active_services or "Third Hour" in active_services:
            digest.append("## HOURS")
            try:
                hours_str = self._format_qr_hours(enriched, rubrics)
                digest.append(hours_str)
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: hours summary failed - {e}]  ")
            digest.append("")
            
        is_liturgy_active = ("Divine Liturgy" in active_services or "Liturgy" in active_services) and rubrics.get("overrides", {}).get("liturgy_type") != "structure_suppressed"
        if is_liturgy_active:
            lit_type = rubrics.get("overrides", {}).get("liturgy_type") or rubrics.get("variables", {}).get("liturgy_type", "")
            if "basil" in lit_type.lower():
                digest.append("## DIVINE LITURGY OF SAINT BASIL THE GREAT")
            else:
                digest.append("## DIVINE LITURGY")
                
            try:
                antiphons_res = self.engine.resolve_liturgy_antiphons(enriched, rubrics)
                beatitudes_res = self.engine.resolve_beatitudes(enriched)
                
                stichera_parts = []
                total_qty = 0
                if beatitudes_res and beatitudes_res.get("stichera"):
                    for s in beatitudes_res["stichera"]:
                        src = s.get("source", "")
                        qty = s.get("count", 0)
                        total_qty += qty
                        
                        src_str = self.humanize_key(src)
                        if src.lower() == "octoechos":
                            src_str = "Octoechos"
                        elif src.lower() == "triodion":
                            src_str = "Triodion"
                        elif src.lower() == "menaion":
                            title_lower = title.lower()
                            if "forefeast" in title_lower:
                                src_str = "forefeast"
                            else:
                                src_str = "Menaion"
                        stichera_parts.append(f"{src_str} - {qty}")
                        
                if total_qty > 0:
                    beat_str = f"Beatitudes on {total_qty}: {'; '.join(stichera_parts)}."
                else:
                    beat_str = "Beatitudes."
                    
                if antiphons_res and antiphons_res.get("type") == "festal_antiphons":
                    digest.append("Festal Antiphons.  ")
                else:
                    digest.append(f"Psalms of Typica; {beat_str}  ")
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: liturgy_antiphons_or_beatitudes: {e}]  ")
                
            try:
                res = self.engine.resolve_liturgy_hymns(enriched, rubrics)
                formatted = self._format_resolve_liturgy_hymns(res, enriched)
                if formatted:
                    if formatted.startswith("Troparia and Kontakia:"):
                        formatted = "**Troparia and Kontakia:**" + formatted[len("Troparia and Kontakia:"):]
                    digest.append(f"{formatted}  ")
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: resolve_liturgy_hymns: {e}]  ")
                
            try:
                readings_str = self._format_qr_readings(enriched, rubrics)
                if readings_str:
                    digest.append(readings_str)
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: readings_formatting: {e}]  ")
                
            digest.append("")
            
        collision_rule = self.engine.check_collision(context)
        if collision_rule and "rubric" in collision_rule and "notes" in collision_rule["rubric"]:
            notes = collision_rule["rubric"]["notes"]
            if notes:
                digest.append("## NOTES & FOOTNOTES")
                if isinstance(notes, list):
                    for idx, note in enumerate(notes):
                        digest.append(f"{idx+1}. {note}  ")
                else:
                    digest.append(f"{notes}  ")
                    
        formatted_md = []
        for line in digest:
            if line is None:
                formatted_md.append("")
            elif isinstance(line, str):
                formatted_md.extend(line.splitlines())
            else:
                formatted_md.append(str(line))
                
        return "\n".join(formatted_md)

    def _apply_link_overrides(self, sequence, overrides):
        seq = copy.deepcopy(sequence)
        for override in overrides:
            target_id = override.get("target_id")
            action = override.get("action")
            
            indices = [i for i, slot in enumerate(seq) if slot.get("id") == target_id]
            if not indices:
                continue
            idx = indices[0]

            if action == "replace":
                seq[idx] = override.get("new_component")
            elif action == "delete":
                del seq[idx]
            elif action == "insert_after":
                seq.insert(idx + 1, override.get("new_component"))
            elif action == "insert_before":
                seq.insert(idx, override.get("new_component"))
            elif action == "modify":
                if "rubric" in override:
                    seq[idx]["rubric"] = override["rubric"]
                if "content" in override:
                    seq[idx]["content"] = override["content"]
                if "logic_args" in override:
                    if "content" in seq[idx] and "logic" in seq[idx]["content"]:
                         if "args" not in seq[idx]["content"]["logic"]:
                             seq[idx]["content"]["logic"]["args"] = {}
                         seq[idx]["content"]["logic"]["args"].update(override["logic_args"])
        return seq

    def _process_skeleton(self, skeleton, context, rubrics, digest):
        for slot in skeleton:
            # Output matins canon description if defined
            if slot.get("id") in ("canon_pascha", "canon_block") and rubrics.get("variables", {}).get("matins_canon_description"):
                digest.append(f"At the Canon: {rubrics['variables']['matins_canon_description']}")

            # 1. Print rubric info if any
            if "rubric" in slot:
                r = slot["rubric"]
                title = ""
                if isinstance(r, dict):
                    title = r.get('title') or r.get('description') or r.get('text')
                    if not title:
                         if "source_ref" in r:
                             title = f"Rubric ({r['source_ref']})"
                         else:
                             title = "Rubric"
                    if "ordo_ref" in r:
                         title = f"{title} [Ordo {r['ordo_ref']}]"
                else:
                    title = str(r)
                if title:
                    digest.append(f"RUBRIC: {title}")

            content = slot.get("content", {})
            if not content and "type" in slot:
                content = slot
            slot_type = content.get("type")

            enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}

            if slot_type == "variable_logic":
                logic = content.get("logic", {})
                func_name = logic.get("function")
                args = logic.get("args", {})
                self._format_logic_hook(func_name, args, context, rubrics, digest)
                
            elif slot_type == "generator":
                method = content.get("generator_method")
                args = content.get("args", {})
                self._format_generator_hook(method, args, context, rubrics, digest)
                
            elif slot_type == "sequence" or slot_type == "complex_structure":
                if "components" in content:
                    self._process_skeleton(content["components"], context, rubrics, digest)
                    
            elif slot_type == "slot_variable":
                slot_id = content.get("slot_id")
                # Handle liturgy readings slot variables
                if slot_id in ("liturgy_prokeimenon", "liturgy_epistle", "liturgy_alleluia", "liturgy_gospel"):
                    try:
                        res = self.engine.resolve_liturgy_readings(enriched, rubrics)
                        if res and res.get("readings"):
                            for r in res["readings"]:
                                if slot_id == "liturgy_prokeimenon" and "prokeimenon" in r:
                                    p = r["prokeimenon"]
                                    ref_str = self.humanize_key(p.get("ref_key", ""))
                                    if "Tone" in ref_str:
                                        digest.append(f"Prokimenon: {ref_str}")
                                    else:
                                        tone_str = f" Tone {p.get('tone')}" if p.get("tone") else ""
                                        digest.append(f"Prokimenon: {ref_str}{tone_str}")
                                elif slot_id == "liturgy_epistle" and "epistle" in r:
                                    e = r["epistle"]
                                    ref_str = self.humanize_key(e.get("ref_key", ""))
                                    digest.append(f"Epistle: {ref_str}")
                                elif slot_id == "liturgy_alleluia" and "alleluia" in r:
                                    try:
                                        all_res = r["alleluia"]
                                        if all_res:
                                            formatted = self._format_resolve_liturgy_alleluia(all_res, enriched)
                                            if formatted:
                                                digest.append(formatted)
                                    except Exception as e_all:
                                        digest.append(f"[ERROR: resolve_liturgy_alleluia failed - {e_all}]")
                                elif slot_id == "liturgy_gospel" and "gospel" in r:
                                    g = r["gospel"]
                                    ref_str = self.humanize_key(g.get("ref_key", ""))
                                    digest.append(f"Gospel: {ref_str}")
                    except Exception as e:
                        digest.append(f"[ERROR: Resolving liturgy readings failed - {e}]")
                elif "kontakion" in str(slot_id):
                    try:
                        hour = content.get("hour") or slot.get("hour")
                        if not hour and "hour_" in str(slot_id):
                            match = re.search(r'hour_(\d+)', str(slot_id))
                            if match:
                                hour = int(match.group(1))
                        if not hour:
                            hour = 1
                        enriched_hour = {**enriched, "hour": hour}
                        res = self.engine.resolve_hours_kontakion(enriched_hour, rubrics)
                        if res:
                            source = res.get("source", "saint_or_feast")
                            if source in ("resurrection", "triodion"):
                                if enriched_hour.get("triodion_period") or source == "triodion":
                                    triodion_id = enriched_hour.get("triodion_id") or "triodion"
                                    digest.append(f"Kontakion: from the Triodion ({self.humanize_key(triodion_id)})")
                                else:
                                    tone = enriched_hour.get("tone", 1)
                                    digest.append(f"Kontakion: of the Resurrection in Tone {tone}")
                            elif source == "triodion_saint":
                                r_title_lower = rubrics.get("title", "").lower()
                                if "palamas" in r_title_lower:
                                    digest.append("Kontakion: of the Saint (St. Gregory Palamas)")
                                elif "john of the ladder" in r_title_lower or "climacus" in r_title_lower:
                                    digest.append("Kontakion: of the Saint (St. John Climacus)")
                                else:
                                    digest.append("Kontakion: of the Saint")
                            elif source == "day":
                                digest.append("Kontakion: of the Day")
                            elif source == "temple":
                                digest.append("Kontakion: of the Temple")
                            elif source == "feast":
                                if enriched_hour.get("feast_id"):
                                    digest.append(f"Kontakion: of the Feast ({self.humanize_key(enriched_hour['feast_id'])})")
                                else:
                                    digest.append("Kontakion: of the Feast")
                            elif source == "saints":
                                if enriched_hour.get("saints"):
                                    digest.append(f"Kontakion: of {self.humanize_key(enriched_hour['saints'][0].get('name', 'Saint'))}")
                                else:
                                    digest.append("Kontakion: of the Saint")
                            elif source == "saints_2":
                                if len(enriched_hour.get("saints", [])) >= 2:
                                    digest.append(f"Kontakion: of {self.humanize_key(enriched_hour['saints'][1].get('name', 'second Saint'))}")
                                else:
                                    digest.append("Kontakion: of the second Saint")
                            else:
                                if enriched_hour.get("feast_id"):
                                    digest.append(f"Kontakion: of the Feast ({self.humanize_key(enriched_hour['feast_id'])})")
                                elif enriched_hour.get("is_forefeast") or enriched_hour.get("is_afterfeast"):
                                    digest.append("Kontakion: of the Forefeast")
                                elif enriched_hour.get("saints"):
                                    s_names = [self.humanize_key(s.get("name", "Saint")) for s in enriched_hour["saints"]]
                                    digest.append(f"Kontakion: of {', '.join(s_names)}")
                                else:
                                    digest.append("Kontakion: of the Temple")
                    except Exception as e:
                        digest.append(f"[ERROR: Resolving hour kontakion failed - {e}]")

            elif slot_type == "canon_ode":
                ode_val = content.get("ode") or slot.get("ode")
                if ode_val == 1:
                    try:
                        res = self.engine.resolve_canon_structure(1, enriched)
                        formatted = self._format_resolve_canon_structure(res, enriched)
                        if formatted:
                            digest.append(formatted)
                    except Exception as e:
                        digest.append(f"[ERROR: resolve_canon_structure failed - {str(e)}]")

            elif slot_type == "conditional_block":
                logic = content.get("logic", {})
                func_name = logic.get("function")
                args = logic.get("args", {})
                
                result = False
                if hasattr(self.engine, func_name):
                    try:
                        func = getattr(self.engine, func_name)
                        import inspect
                        sig = inspect.signature(func)
                        call_kwargs = {}
                        if "rubrics" in sig.parameters:
                            call_kwargs["rubrics"] = rubrics
                            
                        normalized_args = {}
                        for k, v in args.items():
                            if k == "pos":
                                normalized_args["position"] = v
                            elif k == "num":
                                normalized_args["num"] = v
                            else:
                                normalized_args[k] = v
                                
                        for param_name in sig.parameters:
                            if param_name in normalized_args:
                                call_kwargs[param_name] = normalized_args[param_name]
                                
                        params = list(sig.parameters.values())
                        has_context = len(params) > 0
                        
                        if has_context:
                            result = func(enriched, **call_kwargs)
                        else:
                            result = func()
                    except Exception as e:
                        digest.append(f"[ERROR: Evaluating conditional {func_name} failed - {e}]")
                else:
                    digest.append(f"[ERROR: Missing condition helper {func_name}]")
                
                # Recurse
                target_content = content.get("true_content") if result else content.get("false_content")
                if target_content:
                    if isinstance(target_content, list):
                        self._process_skeleton(target_content, context, rubrics, digest)
                    elif isinstance(target_content, dict):
                        self._process_skeleton([target_content], context, rubrics, digest)
                    
            elif slot_type == "structure_ref":
                target_file = content.get("file")
                root_id = content.get("root_id")
                if target_file and root_id:
                    try:
                        linked_data = self.engine._load_json(target_file)
                        sub_skeleton = self.engine._get_structure_sequence(linked_data, root_id)
                        if sub_skeleton:
                            self._process_skeleton(sub_skeleton, context, rubrics, digest)
                        else:
                            digest.append(f"[ERROR: Structure ref '{root_id}' not found in {target_file}]")
                    except Exception as e:
                        digest.append(f"[ERROR: Loading Structure Ref {root_id} from {target_file} failed - {e}]")

            elif slot_type == "fixed_ref":
                ref = content.get('ref_key')
                self._format_fixed_ref(ref, digest)
                
            elif slot_type == "fixed_group":
                ref_keys = content.get('ref_keys', [])
                for ref in ref_keys:
                    self._format_fixed_ref(ref, digest)
                
            elif slot_type == "link":
                target_id = slot.get('target_id')
                target_file = slot.get('target_file')
                if target_file and target_id:
                    full_path = os.path.join(self.engine.json_db, target_file)
                    if not os.path.exists(full_path):
                        full_path = target_file
                    if os.path.exists(full_path):
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                linked_data = json.load(f)
                            sub_skeleton = self.engine._get_structure_sequence(linked_data, target_id)
                            if sub_skeleton:
                                if "start_at_component" in slot:
                                    start_id = slot["start_at_component"]
                                    start_idx = next((i for i, s in enumerate(sub_skeleton) if s.get("id") == start_id), -1)
                                    if start_idx != -1:
                                        sub_skeleton = sub_skeleton[start_idx:]
                                if "stop_after_component" in slot:
                                    stop_id = slot["stop_after_component"]
                                    stop_idx = next((i for i, s in enumerate(sub_skeleton) if s.get("id") == stop_id), -1)
                                    if stop_idx != -1:
                                        sub_skeleton = sub_skeleton[:stop_idx + 1]
                                if "overrides" in slot:
                                    sub_skeleton = self._apply_link_overrides(sub_skeleton, slot["overrides"])
                                self._process_skeleton(sub_skeleton, context, rubrics, digest)
                        except Exception as e:
                            digest.append(f"[ERROR: Loading Link {target_id} failed - {e}]")

            elif slot_type == "component_ref":
                ref_key = content.get("ref_key")
                if ref_key:
                    comp_name = ref_key
                    if comp_name.startswith("components."):
                        comp_name = comp_name.split("components.", 1)[1]
                    comp = self.engine.components.get(comp_name)
                    if comp:
                        seq = comp.get("sequence") or comp.get("components")
                        if seq:
                            self._process_skeleton(seq, context, rubrics, digest)
                        else:
                            self._format_fixed_ref(ref_key, digest)
                    else:
                        digest.append(f"[ERROR: Component {ref_key} not found]")

            # Support sequence/sub-structures nested directly in the slot itself
            if "sequence" in slot:
                self._process_skeleton(slot["sequence"], context, rubrics, digest)

    def _format_fixed_ref(self, ref, digest):
        if not ref:
            return
        if ref in self.engine.text_db:
            title = self.engine.text_db[ref].get("title", ref)
        else:
            title = ref.split('.')[-1].replace('_', ' ').capitalize()
        
        # Avoid technical strings for litanies
        if "litany" in ref.lower():
            if "great" in ref.lower():
                digest.append("Great Litany")
            elif "small" in ref.lower():
                digest.append("Small Litany")
            else:
                digest.append("Litany")
        else:
            digest.append(self.humanize_key(title))

    def _format_logic_hook(self, func_name, args, context, rubrics, digest):
        redirects = {
            "resolve_alleluia": "resolve_liturgy_alleluia",
            "resolve_megalynarion": "resolve_liturgy_megalynarion",
            "resolve_liturgy_readings_logic": "resolve_liturgy_readings",
            "resolve_megalynaria": "resolve_angelic_council"
        }
        actual_func_name = redirects.get(func_name, func_name)
        
        # Resolver registry validation for context safety
        active_structure = context.get("active_structure_id")
        if hasattr(self.engine, "resolver_registry"):
            if not self.engine.resolver_registry.is_allowed(active_structure, actual_func_name):
                digest.append(f"[ERROR: Logic resolver {actual_func_name} is not permitted in structure {active_structure}]")
                return
        
        if not hasattr(self.engine, actual_func_name):
            # Known internal checking hooks that do not yield instructions
            if actual_func_name in ("check_service_type", "check_gospel_service", "resolve_kathisma_choice", "resolve_canon_ode_troparion"):
                return
            digest.append(f"[ERROR: Missing logic resolver method {actual_func_name}]")
            return
            
        try:
            enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
            enriched["overrides"] = rubrics.get("overrides", {})
            if rubrics.get("is_sunday_vigil"):
                enriched["is_sunday_vigil"] = True
                
            func = getattr(self.engine, actual_func_name)
            
            import inspect
            sig = inspect.signature(func)
            call_kwargs = {}
            if "rubrics" in sig.parameters:
                call_kwargs["rubrics"] = rubrics
                
            # Normalize common key mismatches between JSON structures and Python engine
            normalized_args = {}
            for k, v in args.items():
                if k == "pos":
                    normalized_args["position"] = v
                elif k == "num":
                    normalized_args["num"] = v
                else:
                    normalized_args[k] = v
                    
            # Dynamically pass parameters matching function signature
            for param_name in sig.parameters:
                if param_name in normalized_args:
                    call_kwargs[param_name] = normalized_args[param_name]
                
            params = list(sig.parameters.values())
            has_context = len(params) > 0
            
            if has_context:
                result = func(enriched, **call_kwargs)
            else:
                result = func()
                
            formatted_text = self._format_result(actual_func_name, result, enriched)
            if formatted_text:
                digest.append(formatted_text)
                
        except Exception as e:
            digest.append(f"[ERROR: {actual_func_name} failed - {str(e)}]")

    def _format_generator_hook(self, method, args, context, rubrics, digest):
        if method == "generate_stichera_sequence":
            try:
                enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
                enriched["overrides"] = rubrics.get("overrides", {})
                if rubrics.get("is_sunday_vigil"):
                    enriched["is_sunday_vigil"] = True
                res = self.engine.resolve_vespers_stichera(enriched)
                formatted = self._format_resolve_vespers_stichera(res, enriched)
                if formatted:
                    digest.append(formatted)
            except Exception as e:
                digest.append(f"[ERROR: generate_stichera_sequence failed - {str(e)}]")
        elif method == "generate_hour_troparia":
            try:
                enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
                enriched["overrides"] = rubrics.get("overrides", {})
                hour = args.get("hour", 1)
                enriched["hour"] = hour
                res = self.engine.resolve_hours_troparia(enriched, rubrics)
                formatted = self._format_resolve_hours_troparia(res, enriched)
                if formatted:
                    digest.append(formatted)
            except Exception as e:
                digest.append(f"[ERROR: generate_hour_troparia failed - {str(e)}]")
        else:
            digest.append(f"[ERROR: Unknown generator method {method}]")

    def _format_result(self, func_name, result, context):
        if not result:
            return ""
        formatter_name = f"_format_{func_name}"
        if hasattr(self, formatter_name):
            formatter = getattr(self, formatter_name)
            return formatter(result, context)
        if isinstance(result, dict) and result.get("type") in ("component_ref", "fixed_ref", "fixed_group", "sequence", "complex_structure"):
            temp_digest = []
            self._process_skeleton([result], context, {}, temp_digest)
            return "\n".join(temp_digest)
        return self._format_generic(func_name, result, context)

    # --- Logic Resolvers Formatters ---

    def _format_resolve_gradual(self, res, context):
        if not res:
            return ""
        anabathmoi = self.humanize_key(res.get("anabathmoi", ""))
        return f"Gradual (Anabathmoi): {anabathmoi}."

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

    def _format_resolve_lenten_prokeimenon(self, res, context):
        if not res:
            return ""
        if res.get("type") == "prokeimenon":
            return f"Prokeimenon: {self.humanize_key(res.get('ref_key'))}"
        parts = []
        for comp in res.get("components", []):
            if comp.get("type") == "prokeimenon":
                parts.append(f"Prokimenon: {self.humanize_key(comp.get('ref_key'))}")
            elif comp.get("type") == "reading":
                parts.append(f"Reading from {comp.get('source', '').capitalize()}")
        return "\n".join(parts)

    def _format_resolve_lenten_ending(self, res, context):
        if not res:
            return ""
        parts = []
        for comp in res.get("components", []):
            c_type = comp.get("type")
            if c_type == "lenten_troparia_block":
                troparia = []
                for t in comp.get("components", []):
                    name = self.humanize_key(t.get("ref_key"))
                    if t.get("prostration"):
                        troparia.append(f"{name} (with prostration)")
                    else:
                        troparia.append(name)
                parts.append(f"Lenten Troparia: {'; '.join(troparia)}")
            elif c_type == "fixed_ref":
                parts.append(self.humanize_key(comp.get("ref_key")))
            elif c_type == "prayer_ephrem":
                count = comp.get("prostration_count", 0)
                parts.append(f"Prayer of St. Ephrem ({count} prostrations)")
            elif c_type == "come_let_us_worship":
                parts.append("Come, let us worship (with final prostrations)")
        return "\n".join(parts)

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

    def _format_resolve_lenten_sessional(self, res, context):
        if not res:
            return ""
        return res.get("rubric_note", "")

    def _format_resolve_lenten_triodic_canon(self, res, context):
        if not res:
            return ""
        return f"Lenten Canon: {res.get('action')}"

    def _format_resolve_lenten_exapostilarion(self, res, context):
        if not res:
            return ""
        return res.get("rubric_note", "")

    def _format_resolve_lenten_aposticha(self, res, context):
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



    def _format_resolve_vigil_polyeleos(self, res, context):
        if not res:
            return ""
        parts = []
        for comp in res.get("components", []):
            note = comp.get("note") or self.humanize_key(comp.get("ref_key", ""))
            parts.append(note)
        return f"Polyeleos: {', '.join(parts)}"

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

    def _format_resolve_great_canon_portion(self, res, context):
        if not res:
            return ""
        return f"Great Canon Portion: Part {res.get('part')}"

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

    def _format_resolve_canon_ode_troparion(self, res, context):
        if not res:
            return ""
        return f"Canon Ode Troparion (Ode {res.get('ode')}, {res.get('position')}): {self.humanize_key(res.get('ref_key'))}"

    def _format_resolve_bridegroom_canon_type(self, res, context):
        if not res:
            return ""
        return f"Bridegroom Canon: {res.get('rubric_note')}"

    def _format_resolve_bridegroom_aposticha(self, res, context):
        if not res:
            return ""
        return f"Bridegroom Aposticha: {res.get('rubric_note')}"

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

    def _format_resolve_encomia_station(self, res, context):
        if not res:
            return ""
        return res.get("rubric_note", "")

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

    def _format_resolve_fasting_rule(self, res, context):
        if not res:
            return ""
        return f"Fasting Rule: {res.get('rule')} ({res.get('note', '')})"

    def _format_resolve_vestment_color(self, res, context):
        if not res:
            return ""
        return f"Vestment Color: {res.get('color')} ({res.get('note', '')})"

    def _format_resolve_prostration_annotation(self, res, context):
        if not res:
            return ""
        return f"Prostrations: {res.get('annotation') or res.get('note')}"

    def _format_resolve_censing_annotation(self, res, context):
        if not res:
            return ""
        p = res.get('protocol')
        if p and isinstance(p, dict):
            return f"Censing: {p.get('description') or res.get('note')}"
        return f"Censing: {res.get('note')}"

    def _format_resolve_door_state(self, res, context):
        if not res:
            return ""
        state_str = str(res.get('state', '')).capitalize()
        return f"Royal Doors: {state_str} ({res.get('note')})"

    def _format_resolve_curtain_state(self, res, context):
        if not res:
            return ""
        state_str = str(res.get('state', '')).capitalize()
        return f"Sanctuary Curtain: {state_str} ({res.get('note')})"

    def _format_resolve_vestment_set(self, res, context):
        if not res:
            return ""
        return f"Vestment Set: {res.get('set_type')} ({res.get('note')})"

    def _format_resolve_clergy_variant(self, res, context):
        if not res:
            return ""
        return f"Clergy Variant: {res.get('variant')} ({res.get('note')})"

    def _format_resolve_bow_type(self, res, context):
        if not res:
            return ""
        return f"Bow: {res.get('bow_type')} ({res.get('note')})"

    def _format_resolve_hand_position(self, res, context):
        if not res:
            return ""
        return f"Hand Position: {res.get('position')} ({res.get('note')})"

    def _format_resolve_role_view(self, res, context):
        if not res:
            return ""
        return f"Role View: {res.get('view_summary') or str(res)}"

    def _format_resolve_cantor_signal(self, res, context):
        if not res:
            return ""
        return f"Cantor Signal: {res.get('signal') or res.get('note')}"


    def _format_generic(self, func_name, result, context):
        if result is None:
            return ""
        if isinstance(result, str):
            return f"{self.humanize_key(func_name)}: {result}"
        if isinstance(result, list):
            items = []
            for item in result:
                if isinstance(item, dict):
                    citation = item.get("citation") or item.get("title") or item.get("id") or item.get("ref_key")
                    if citation:
                        items.append(self.humanize_key(citation))
                    else:
                        items.append(str(item))
                else:
                    items.append(self.humanize_key(str(item)))
            return f"{self.humanize_key(func_name)}: {'; '.join(items)}"
        if isinstance(result, dict):
            title = result.get("title") or result.get("text") or result.get("citation")
            if title:
                return f"{self.humanize_key(func_name)}: {title}"
            if "components" in result:
                comps = [self.humanize_key(c) for c in result["components"]]
                return f"{self.humanize_key(func_name)}: {'; '.join(comps)}"
            return f"{self.humanize_key(func_name)}: {result}"
        return f"{self.humanize_key(func_name)}: {str(result)}"

    # --- Specific Formatters ---

    def _format_resolve_small_vespers_prokeimenon(self, res, context):
        if not res:
            return ""
        ref_str = self.humanize_key(res.get("ref_key", ""))
        return f"Prokimenon: {ref_str}"

    def _format_resolve_vespers_stichera(self, res, context):
        if not res:
            return ""
        dist = []
        for item in res.get("distribution", []):
            c = item.get('count', item.get('qty', '?'))
            t = item.get('type', '')
            s = self.humanize_key(item.get('source', ''))
            name = self.humanize_key(t) if t else "Stichera"
            if "res" in t.lower():
                name = "resurrectional stichera"
            dist.append(f"{c} {name} from the {s}")
        parts = []
        if dist:
            parts.append(f"At O Lord, I have cried, we sing {', '.join(dist)}")
        glory_val = res.get("glory")
        if glory_val and str(glory_val).strip().lower() not in ("none", "", "null", "(no saint doxastikon)"):
            parts.append(f"Glory... {self.humanize_key(glory_val)}")
        both_now_val = res.get("both_now")
        if both_now_val and str(both_now_val).strip().lower() not in ("none", "", "null"):
            parts.append(f"Both now... {self.humanize_key(both_now_val)}")
        return "; ".join(parts) + "."

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
                p_type = item.get("type")
                tone = item.get("tone")
                tone_roman = self._roman_tone(tone) if isinstance(tone, int) else str(tone)
                text = item.get("text") or item.get("content")
                
                if p_type == "prokeimenon" and item.get("ref_key") == "prokeimenon.saturday_evening":
                    parts.append("Prokeimenon: The Lord is King (Tone VI).")
                elif p_type == "sunday_prokeimenon":
                    parts.append(f"Prokeimenon: {text} (Tone {tone_roman}).")
                elif p_type == "festal_prokeimenon":
                    parts.append(f"Prokeimenon: Festal prokeimenon in Tone {tone_roman}.")
                elif p_type == "daily_prokeimenon":
                    day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                    day_idx = item.get("day_of_week", 0)
                    day_str = day_names[day_idx]
                    parts.append(f"Prokeimenon: Daily prokeimenon for {day_str} evening in Tone {tone_roman}.")
                else:
                    parts.append(f"Prokeimenon: {text or 'sung according to the Typikon'} (Tone {tone_roman}).")
                break
        
        # 2. Format the Readings
        readings = [f"Reading: {r.get('citation', 'Unknown')}" for r in res if r.get('type') == 'ot_reading']
        if readings:
            parts.append("Readings: " + "; ".join(readings) + ".")
            
        return "\n".join(parts)

    def _format_resolve_presanctified_transfer(self, res, context):
        if not res:
            return ""
        action = res.get("transfer_action", {})
        priest = action.get("priest_action", "")
        deacon = action.get("deacon_action", "")
        covering = action.get("covering", "")
        
        parts = [
            f"At the Kathisma: {res.get('rubric', {}).get('note', '')}",
            f"During the Kathisma: {priest}",
            f"The deacon: {deacon}",
            f"After placement: {covering}"
        ]
        if "special_note" in action:
            parts.append(action["special_note"])
        return "; ".join(parts) + "."

    def _format_resolve_presanctified_entrance(self, res, context):
        if not res:
            return ""
        ent_type = res.get("entrance_type", "censer")
        rub = res.get("rubric", {})
        title = rub.get("title", "Entrance")
        
        if ent_type == "gospel":
            gospel_ref = self.humanize_key(res.get("gospel_ref", ""))
            return f"Entrance: {title} with the Gospel book (Gospel: {gospel_ref})."
        
        roles = rub.get("roles", {})
        deacon_role = roles.get("deacon", "")
        priest_role = roles.get("priest", "")
        
        parts = [f"Entrance: {title} with the censer"]
        if deacon_role:
            parts.append(f"Deacon: {deacon_role}")
        if priest_role:
            parts.append(f"Priest: {priest_role}")
        return "; ".join(parts) + "."

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
        if glory_val and str(glory_val).strip().lower() not in ("none", "", "null", "(no saint doxastikon)"):
            parts.append(f"Glory... {self.humanize_key(glory_val)}")
        both_now_val = res.get("both_now")
        if both_now_val and str(both_now_val).strip().lower() not in ("none", "", "null"):
            parts.append(f"Both now... {self.humanize_key(both_now_val)}")
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
                item_id = self.humanize_key(item.get("id", "Stichera"))
                key = (source, item_id)
                counts[key] = counts.get(key, 0) + item.get("count", 1)
                
        for (source, item_id), c in counts.items():
            stichera_parts.append(f"{c} {item_id} from the {source}")
            
        parts = []
        if stichera_parts:
            parts.append(f"At the Aposticha, we sing: {', '.join(stichera_parts)}")
        else:
            parts.append("At the Aposticha, we sing the Aposticha")
            
        if glory:
            parts.append(f"Glory... {self.humanize_key(glory)}")
        if both_now:
            parts.append(f"Both now... {self.humanize_key(both_now)}")
        if glory_both_now:
            parts.append(f"Glory, both now... {self.humanize_key(glory_both_now)}")
            
        return "; ".join(parts) + "."

    def _format_resolve_vespers_troparia_simple(self, res, context):
        if not res or not res.get("components"):
            return ""
        parts = []
        for c in res["components"]:
            typ = c.get("type", "")
            ref = self.humanize_key(c.get("ref_key", ""))
            if "resurrectional" in typ:
                parts.append("We sing the Sunday (resurrectional) troparion in the tone of the week")
            elif typ == "glory":
                parts.append(f"Glory... {ref}")
            elif typ == "both_now":
                parts.append(f"Both now... {ref}")
            elif typ == "glory_both_now":
                parts.append(f"Glory, both now... {ref}")
            else:
                parts.append(f"Troparion of the {ref}")
        return "At the Dismissal Troparia, we sing: " + "; ".join(parts) + "."

    def _format_resolve_god_is_the_lord_troparia(self, res, context):
        if not res or not res.get("sequence"):
            return ""
        
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
                    parts.append(f"troparion of {self.humanize_key(name)},{count_str}")
                else:
                    parts.append(f"troparion of the saint,{count_str}")
            elif "theotokion" in content:
                parts.append(f"theotokion,{count_str}")
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
            
        return "At The Lord is God, we sing: " + result_str

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

    def _format_resolve_polyeleos_or_kathisma_17(self, res, context):
        if not res:
            return ""
        typ = res.get("type")
        if typ == "polyeleos":
            add_text = ""
            if context.get("matins_polyeleos_add") == "psalm_136_waters_of_babylon":
                add_text = ", and we add Psalm 136 (By the waters of Babylon)"
            return f"We sing the Polyeleos{add_text}. Magnification: sung if prescribed."
        elif typ == "kathisma_17":
            return "We sing the 17th Kathisma (Psalm 118)."
        return ""

    def _format_resolve_matins_gospel(self, res, context):
        if not res:
            return ""
        title = res.get("title") or res.get("reading_key") or "Matins Gospel"
        return f"Matins Gospel: {title}."

    def _format_resolve_post_gospel_stichera(self, res, context):
        if not res or not isinstance(res, list):
            return ""
        refs = [self.humanize_key(r) for r in res]
        return f"Psalm 50 and Post-Gospel Stichera: {', '.join(refs)}."

    def _format_resolve_canon_structure(self, res, context):
        if not res:
            return ""
        parts = []
        for item in res:
            src = self.humanize_key(item.get('source', 'Unknown'))
            cnt = item.get('count', item.get('qty', '?'))
            extra = " (including the irmos)" if item.get('irmos') else ""
            parts.append(f"{src} - {cnt}{extra}")
        return f"At the Canon: Full order of the canon (according to the typicon): {', '.join(parts)}."

    def _format_resolve_katavasia(self, res, context):
        if not res:
            return ""
        if isinstance(res, dict):
            key = res.get("id") or res.get("katavasia_id") or ""
            tone = res.get("tone")
            tone_str = f" (Tone {tone})" if tone else ""
            return f"Catabasia: {self.humanize_key(key)}{tone_str}."
        return f"Catabasia: {self.humanize_key(res)}."

    def _format_resolve_canon_insertion(self, res, context):
        if not res:
            return ""
        formatted = []
        for item in res:
            formatted.append(self.humanize_key(item))
        return f"Canon Insertion: {', '.join(formatted)}."

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
                if "glory" in ref.lower():
                    glory.append(self.humanize_key(ref))
                elif "both_now" in ref.lower():
                    both_now.append(self.humanize_key(ref))
                elif "psalms_praises" in ref.lower():
                    pass
                else:
                    other_refs.append(self.humanize_key(ref))
                    
        if total == 0 and len(res) > 0:
            for item in res:
                if item.get("type") == "sticheron" or "praises" in str(item.get("addr", "")):
                    total += 1
            if total > 0:
                stichera_counts["Octoechos"] = total

        dist_str = ", and ".join(f"{qty} from the {source}" for source, qty in stichera_counts.items())
        
        parts = []
        if total > 0:
            parts.append(f"At the Praises, we sing {total} stichera: {dist_str}")
        else:
            parts.append("At the Praises, we sing the praises stichera")
            
        if glory:
            parts.append(f"Glory... {', '.join(glory)}")
        if both_now:
            parts.append(f"Both now... {', '.join(both_now)}")
        if other_refs:
            parts.append(f"Other: {', '.join(other_refs)}")
            
        return "; ".join(parts) + "."

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

    def _format_resolve_liturgy_antiphons(self, res, context):
        if res and res.get("type") == "festal_antiphons":
            return "Festal Antiphons."
        return "Psalms of Typica; Beatitudes."

    def _format_resolve_prokeimenon(self, res, context):
        if not res:
            return ""
        return f"Prokeimenon: {res.get('text', 'sung according to the Typikon')} (Tone {res.get('tone', '')})."

    def _format_resolve_liturgy_alleluia(self, res, context):
        if not res:
            return ""
        return f"Alleluia: sung in Tone {res.get('tone', '')}."

    def _format_resolve_liturgy_megalynarion(self, res, context):
        if not res:
            return ""
        if res.get("text"):
            return f"Instead of 'It is truly proper': {res.get('text')}."
        elif res.get("type") == "irmos_ode_9" or res.get("ref_key") == "festal_zadostoinyk" or res.get("type") == "variable":
            return "Instead of 'It is truly proper', we sing the Irmos of Ode 9 of the Canon."
        return ""

    def _format_resolve_communion_hymn(self, res, context):
        if not res or not res.get("text"):
            return ""
        return f"Communion Hymn: {res.get('text')}."

    def _format_resolve_liturgy_hymns(self, res, context):
        if not res or not res.get("components"):
            return ""
        parts = ["Troparia and Kontakia:"]
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
        parts = []
        for idx, reading in enumerate(res["readings"]):
            r_parts = []
            
            p = reading.get("prokeimenon", {})
            if p:
                tone_str = f" Tone {p.get('tone')}" if p.get("tone") else ""
                ref_str = self.humanize_key(p.get("ref_key", ""))
                r_parts.append(f"Prokimenon: {ref_str}{tone_str}")
                
            e = reading.get("epistle", {})
            if e:
                ref_str = self.humanize_key(e.get("ref_key", ""))
                r_parts.append(f"Epistle: {ref_str}")
                
            a = reading.get("alleluia", {})
            if a:
                tone_str = f" Tone {a.get('tone')}" if a.get('tone') else ""
                ref_str = self.humanize_key(a.get("ref_key", ""))
                r_parts.append(f"Alleluia: {ref_str}{tone_str}")
                
            g = reading.get("gospel", {})
            if g:
                ref_str = self.humanize_key(g.get("ref_key", ""))
                r_parts.append(f"Gospel: {ref_str}")
                
            parts.append("; ".join(r_parts))
            
        return "\n".join(parts)

    def _format_resolve_kathisma(self, res, context):
        if not res: return ""
        if res.get('type') == 'lenten_hours':
            return f"We read Kathisma {res.get('kathisma_number')}."
        return f"We read {self.humanize_key(res.get('id', 'Kathisma'))}."

    def _format_resolve_sessional(self, res, context):
        if not res: return ""
        return f"Sessional Hymns: {self.humanize_key(res.get('id', 'Sessional'))}."

    def _format_resolve_kathisma_choice(self, res, context):
        if not res: return ""
        if res.get('type') == 'polyeleos':
            add_txt = ", and we add Psalm 136 (By the waters of Babylon)" if context.get("matins_polyeleos_add") else ""
            return f"We sing the Polyeleos{add_txt}."
        return f"We read {self.humanize_key(res.get('id', 'Kathisma 17'))}."

    def _format_resolve_hypakoe(self, res, context):
        if not res: return ""
        return f"Hypakoe: {self.humanize_key(res.get('id', 'Hypakoe'))}."

    def _format_resolve_anabathmoi(self, res, context):
        if not res: return ""
        return f"Anabathmoi (Hymns of Ascents): {self.humanize_key(res.get('id', 'Anabathmoi'))}."

    def _format_resolve_doxology_type(self, res, context):
        if not res: return ""
        return f"Doxology: {res.get('rubric_note', 'Great Doxology')}."

    def _format_resolve_compline_canon(self, res, context):
        if not res: return ""
        return f"Canon: {self.humanize_key(res.get('subject', ''))} from the {self.humanize_key(res.get('book', 'Octoechos'))}."

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
                parts.append("Troparion of the Temple")
                continue
                
            if ref_key == "horologion.troparion.god_of_our_fathers_block":
                parts.append("Troparion 'O God of our fathers' block")
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
                parts.append("Troparion of the weekday")
                continue
                
            if ref_key == "horologion.troparion_saint_if_any":
                parts.append("Troparion of the Saint (if any)")
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

    def _format_resolve_compline_troparia(self, res, context):
        if not res: return ""
        if isinstance(res, dict) and res.get("type") == "troparia_stack":
            comps = self._format_troparia_stack_components(res.get("components", []), context)
            return f"Troparia: {comps}."
        return f"Troparia: {self.humanize_key(res)}."

    def _format_resolve_triadic_canon(self, res, context):
        if not res: return ""
        return f"Triadic Canon: {self.humanize_key(res.get('ref_key', ''))}."

    def _format_resolve_midnight_troparia(self, res, context):
        if not res: return ""
        if isinstance(res, dict) and res.get("type") == "troparia_stack":
            comps = self._format_troparia_stack_components(res.get("components", []), context)
            return f"Midnight Troparia: {comps}."
        return f"Midnight Troparia: {self.humanize_key(res)}."

    def _format_resolve_midnight_prayer(self, res, context):
        if not res: return ""
        return f"Prayer: {self.humanize_key(res.get('ref_key', ''))}."

    def _format_resolve_trisagion_type(self, res, context):
        if not res:
            return "Trisagion: Holy God, Holy Mighty, Holy Immortal, have mercy on us."

        if isinstance(res, str): 
            return f"Trisagion: {res}"
        if isinstance(res, dict):
            if res.get("type") == "replacement" and res.get("text"):
                return f"Instead of the Trisagion, we sing: {res.get('text')}"
            if res.get("ref_key"):
                return f"Trisagion: {self.humanize_key(res.get('ref_key'))}."
        return "Trisagion: Holy God, Holy Mighty, Holy Immortal, have mercy on us."

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

    def _format_resolve_royal_readings(self, res, context):
        if not res: return ""
        components = res.get("components", [])
        parts = []
        for c in components:
            ref = c.get("ref_key", "")
            parts.append(self.humanize_key(ref))
        return f"Royal Readings: {'; '.join(parts)}."

    def _format_resolve_royal_kontakion(self, res, context):
        if not res: return ""
        return f"Royal Kontakion: {self.humanize_key(res.get('ref_key', ''))}."

    def _format_resolve_artoklasia(self, res, context):
        if not res: return ""
        return "Blessing of the loaves (Artoklasia)."

    def _format_resolve_cherubic_hymn(self, res, context):
        if not res: return ""
        return f"Cherubic Hymn: {self.humanize_key(res.get('ref_key', 'Cherubic Hymn'))}."

    def _format_resolve_liturgy_dismissal(self, res, context):
        if not res: return ""
        return f"Dismissal: {res.get('content', 'May Christ our true God...')}"

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

    def _format_resolve_magnificat(self, res, context):
        if not res:
            return ""
        typ = res.get("type")
        if typ == "paschal_magnificat":
            return "At Ode IX, we sing the Paschal magnification: 'The Angel cried out...'."
        elif typ == "festal_magnificat":
            return "At Ode IX, we sing the Festal magnification and the Irmos of Ode IX of the Feast."
        elif typ == "suppressed_magnificat":
            return "At Ode IX, we do not sing the Magnificat, but immediately the Irmos of Ode IX of the Canon."
        elif typ in ("sunday_magnificat", "festal_with_more_honorable"):
            return "At Ode IX, we sing the Magnificat ('My soul magnifies the Lord...') and the refrains ('More honorable than the Cherubim...')."
        return "At Ode IX, we sing the Magnificat ('My soul magnifies the Lord...') and the refrains ('More honorable than the Cherubim...')."

    def _format_resolve_post_ode9_hymn(self, res, context):
        if not res:
            return ""
        typ = res.get("type")
        if typ == "holy_is_the_lord":
            return "Holy is the Lord our God (3x)."
        elif typ == "it_is_truly_meet":
            return "It is truly proper (Axion Estin)."
        elif typ == "paschal_troparion":
            return "Paschal Troparion refrains."
        elif typ == "zadostojnyk":
            return "Zadostoinyk (Feast Irmos)."
        return ""

    def _format_resolve_god_is_with_us(self, res, context):
        if not res: return ""
        mode = self.humanize_key(res.get("mode", ""))
        return f"We sing 'God is with us': in {mode}."

    def _format_resolve_compline_lord_of_hosts(self, res, context):
        if not res: return ""
        ref = res.get("ref_key", "")
        if ref == "lord_of_hosts_tone_6":
            return "Lord of Hosts: We sing 'Lord of hosts, be with us...' in Tone 6."
        return f"Lord of Hosts: We read the Kontakion of the Feast."

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

    def _format_resolve_royal_readings(self, res, context):
        if not res: return ""
        components = res.get("components", [])
        parts = []
        for c in components:
            ref = c.get("ref_key", "")
            parts.append(self.humanize_key(ref))
        return f"Royal Readings: {'; '.join(parts)}."

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
        parts = []
        for t in troparia:
            t_type = t.get("type", "")
            t_id = t.get("troparion_id", "")
            tone = t.get("tone")
            if t_type == "resurrectional":
                if tone is not None:
                    if tone % 2 == 1:
                        parts.append(f"Sunday Dismissal Troparion 'Today salvation has come to the world' in Tone {tone}")
                    else:
                        parts.append(f"Sunday Dismissal Troparion 'Having risen from the tomb' in Tone {tone}")
                else:
                    parts.append("Sunday Dismissal Troparion")
            elif t_type == "festal":
                parts.append(f"Troparion of the Feast in Tone {tone}")
            elif t_type == "saint":
                saint_name = self.humanize_key(t_id.replace("troparion_", ""))
                parts.append(f"Troparion of {saint_name}")
            else:
                parts.append(f"Troparion {self.humanize_key(t_id)}")
        
        return "At the Dismissal Troparion, we sing: " + "; ".join(parts) + "."

    def _format_resolve_dismissal_theotokion(self, res, context):
        if not res:
            return ""
        ref_key = res.get("ref_key", "")
        rubric_note = res.get("rubric_note") or "Dismissal Theotokion"
        
        # Check if the text is in the text database
        if ref_key and ref_key in self.engine.text_db:
            content = self.engine.text_db[ref_key]
            title = content.get("title")
            if title:
                return f"{rubric_note}: {title}."
                
        # Fallback to a nice humanized key
        if "theotokion_dismissal" in ref_key:
            parts = ref_key.split('.')
            tone_part = ""
            day_part = ""
            for p in parts:
                if "tone" in p:
                    tone_part = p.replace("tone_", "Tone ")
                elif p in ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"):
                    day_part = p.capitalize()
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
            if rubric_note:
                return f"RUBRIC: {rubric_note}\nWe sing: {'; '.join(parts)}."
            else:
                return f"We sing: {'; '.join(parts)}."
        return ""

    def _format_resolve_post_communion_hymn(self, res, context):
        if not res:
            return ""
        hymn_text = res.get("hymn")
        ref_key = res.get("ref_key")
        if hymn_text:
            return f"Post-Communion Hymn: '{hymn_text}' ({self.humanize_key(ref_key)})"
        elif ref_key:
            return f"Post-Communion Hymn: {self.humanize_key(ref_key)}"
        return ""

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

    def _format_resolve_lenten_prokeimenon(self, res, context):
        if not res:
            return ""
        if res.get("type") == "sequence":
            parts = []
            for comp in res.get("components", []):
                c_type = comp.get("type")
                if c_type == "prokeimenon":
                    parts.append(f"Prokeimenon ({self.humanize_key(comp.get('ref_key', ''))})")
                elif c_type == "reading":
                    parts.append(f"Reading from {comp.get('source', '').capitalize()}")
            return "At the readings: " + " then ".join(parts) + "."
        else:
            ref = res.get("ref_key", "")
            return f"Prokeimenon: {self.humanize_key(ref)}."

    def _format_resolve_lenten_ending(self, res, context):
        if not res:
            return ""
        parts = []
        for comp in res.get("components", []):
            c_type = comp.get("type")
            if c_type == "lenten_troparia_block":
                block_parts = []
                for sub in comp.get("components", []):
                    ref = sub.get("ref_key", "")
                    prost = " with a great prostration" if sub.get("prostration") else ""
                    block_parts.append(f"{self.humanize_key(ref)}{prost}")
                parts.append("Lenten Troparia: " + "; ".join(block_parts))
            elif c_type == "fixed_ref":
                parts.append(self.humanize_key(comp.get("ref_key", "")))
            elif c_type == "prayer_ephrem":
                ref = comp.get("ref_key", "")
                cnt = comp.get("prostration_count", 0)
                parts.append(f"Prayer of St. Ephrem ({self.humanize_key(ref)}) with {cnt} prostrations")
            elif c_type == "come_let_us_worship":
                parts.append("Come let us worship (3x) with prostrations")
            else:
                parts.append(self.humanize_key(str(comp)))
        return "At the Lenten Ending:\n" + "\n".join(f"  - {p}" for p in parts)

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

    def _format_resolve_lenten_sessional(self, res, context):
        if not res:
            return ""
        ref = res.get("ref_key", "")
        rubric = res.get("rubric_note", "")
        return f"Lenten Sessional: {self.humanize_key(ref)} ({rubric})"

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

    def _format_resolve_lenten_aposticha(self, res, context):
        if not res:
            return ""
        stichera = [self.humanize_key(s.get("ref", "")) for s in res.get("stichera", [])]
        glory = self.humanize_key(res.get("glory", {}).get("ref", ""))
        now = self.humanize_key(res.get("now", {}).get("ref", ""))
        rubric = res.get("rubric_note", "")
        return f"Lenten Aposticha: {'; '.join(stichera)}. Glory: {glory}. Both now: {now}. ({rubric})"

    def _format_resolve_post_doxology_event(self, res, context):
        if not res:
            return ""
        ref = res.get("ref_key", "")
        return f"Post-Doxology Event: {self.humanize_key(ref)}."

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

    def _format_resolve_artoklasia(self, res, context):
        if not res or not res.get("included"):
            return ""
        troparia_parts = []
        for t in res.get("troparia", []):
            ref = t.get("ref_key", "")
            cnt = t.get("count", 1)
            source = t.get("source", "")
            troparia_parts.append(f"{self.humanize_key(ref)} ({source}) x{cnt}")
        troparia_str = ", ".join(troparia_parts)
        roles = res.get("roles", {})
        priest_action = roles.get("priest", "")
        deacon_action = roles.get("deacon", "")
        choir_action = roles.get("choir", "")
        return (
            f"At the Blessing of Loaves (Artoklasia):\n"
            f"  - Rubric: {res.get('rubric', '')} (Ordo {res.get('ordo_ref', '')}).\n"
            f"  - Troparia to sing: {troparia_str}.\n"
            f"  - Priest action: {priest_action}\n"
            f"  - Deacon action: {deacon_action}\n"
            f"  - Choir action: {choir_action}"
        )

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

    def _format_resolve_passion_vespers_readings(self, res, context):
        if not res:
            return ""
        prok = res.get("prokeimenon", {}).get("text", "")
        p1 = f"{res.get('paremia_1', {}).get('book')} {res.get('paremia_1', {}).get('chapter')}"
        p2 = f"{res.get('paremia_2', {}).get('book')} {res.get('paremia_2', {}).get('chapter')}"
        p3 = f"{res.get('paremia_3', {}).get('book')} {res.get('paremia_3', {}).get('chapter')}"
        epistle = f"{res.get('epistle', {}).get('book')} {res.get('epistle', {}).get('chapter')}"
        gospel = res.get("gospel", {}).get("content", "")
        sources = ", ".join(res.get("gospel", {}).get("sources", []))
        return (
            f"At Passion Vespers:\n"
            f"  - Prokeimenon: '{prok}'\n"
            f"  - Paremia 1: {p1}\n"
            f"  - Paremia 2: {p2}\n"
            f"  - Paremia 3: {p3}\n"
            f"  - Epistle: {epistle}\n"
            f"  - Gospel: {gospel} (from {sources})"
        )

    def _format_resolve_great_canon_portion(self, res, context):
        if not res:
            return ""
        part = res.get("part", 1)
        part_names = {1: "First (Monday)", 2: "Second (Tuesday)", 3: "Third (Wednesday)", 4: "Fourth (Thursday)"}
        name = part_names.get(part, f"Part {part}")
        return f"At Great Compline: We read the Great Canon of St. Andrew, {name} Portion."

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

    def _format_resolve_canon_ode_troparion(self, res, context):
        if not res:
            return ""
        ode = res.get("ode")
        pos = res.get("position", "")
        ref = res.get("ref_key", "")
        return f"At Ode {ode} ({self.humanize_key(pos)}): {self.humanize_key(ref)}."

    def _format_resolve_bridegroom_canon_type(self, res, context):
        if not res:
            return ""
        name = res.get("canon_name", "")
        note = res.get("rubric_note", "")
        return f"Bridegroom Canon ({self.humanize_key(name)}): {note}."

    def _format_resolve_bridegroom_aposticha(self, res, context):
        if not res:
            return ""
        note = res.get("rubric_note", "")
        return f"Bridegroom Aposticha: {note}."

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

    def _format_resolve_encomia_station(self, res, context):
        if not res:
            return ""
        note = res.get("rubric_note", "")
        return f"Lamentations at the Tomb: {note}."

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

    def _format_resolve_fasting_rule(self, res, context):
        if not res:
            return ""
        note = res.get("note", "")
        cit = res.get("citation", "")
        cit_str = f" ({cit})" if cit else ""
        return f"Fasting Rule: {note}{cit_str}."

    def _format_resolve_vestment_color(self, res, context):
        if not res:
            return ""
        color = res.get("color", "")
        alt = res.get("alt", "")
        alt_str = f" or {alt}" if alt else ""
        cit = res.get("citation", "")
        cit_str = f" ({cit})" if cit else ""
        return f"Vestment colour: {color.capitalize()}{alt_str}{cit_str}."

    def _format_resolve_prostration_annotation(self, res, context):
        if not res or res.get("forbidden"):
            reason = res.get("reason", "") if res else ""
            return f"Prostrations: Forbidden{f' ({reason})' if reason else ''}."
        ann = res.get("annotation")
        if not ann:
            return ""
        return f"Prostrations: {ann.get('note', '')}."

    def _format_resolve_censing_annotation(self, res, context):
        if not res or not res.get("has_censing"):
            return ""
        prot = res.get("protocol", {})
        desc = prot.get("description", "")
        cit = prot.get("citation", "")
        cit_str = f" ({cit})" if cit else ""
        return f"Censing: {desc}{cit_str}."

    def _format_resolve_door_state(self, res, context):
        if not res:
            return ""
        state = res.get("state", "")
        note = res.get("note", "")
        ref = res.get("ordo_ref", "")
        ref_str = f" (Ordo {ref})" if ref else ""
        return f"Royal Doors: {state.upper()} - {note}{ref_str}."

    def _format_resolve_curtain_state(self, res, context):
        if not res:
            return ""
        state = res.get("state", "")
        note = res.get("note", "")
        ref = res.get("ordo_ref", "")
        ref_str = f" (Ordo {ref})" if ref else ""
        note_str = f" - {note}" if note else ""
        return f"Curtain: {state.upper()}{note_str}{ref_str}."

    def _format_resolve_vestment_set(self, res, context):
        if not res:
            return ""
        vest = ", ".join(res.get("vestments", []))
        note = res.get("note", "")
        note_str = f" - {note}" if note else ""
        ref = res.get("ordo_ref", "")
        ref_str = f" (Ordo {ref})" if ref else ""
        return f"Vestments ({res.get('clergy_type', '')}): {vest}{note_str}{ref_str}."

    def _format_resolve_clergy_variant(self, res, context):
        if not res:
            return ""
        label = res.get("label", "")
        r_range = res.get("ordo_range", "")
        ref = res.get("ordo_ref", "")
        ref_str = f" ({ref})" if ref else ""
        range_str = f" (Range: {r_range})" if r_range else ""
        return f"Clergy variant: {label}{ref_str}{range_str}."

    def _format_resolve_bow_type(self, res, context):
        if not res:
            return ""
        if res.get("forbidden"):
            return f"Bows/Prostrations: Forbidden ({res.get('reason', '')})."
        bt = res.get("bow_type", "")
        cnt = res.get("count", 1)
        note = res.get("note", "")
        note_str = f" - {note}" if note else ""
        ref = res.get("ordo_ref", "")
        ref_str = f" (Ordo {ref})" if ref else ""
        return f"Bow: {bt} x{cnt}{note_str}{ref_str}."

    def _format_resolve_hand_position(self, res, context):
        if not res:
            return ""
        desc = res.get("description", "")
        ref = res.get("ordo_ref", "")
        ref_str = f" (Ordo {ref})" if ref else ""
        return f"Hand Position: {desc}{ref_str}."

    def _format_resolve_role_view(self, res, context):
        return str(res)

    def _format_resolve_cantor_signal(self, res, context):
        return str(res)

    def _get_canon_refrain(self, source, context, canon_num=1):
        offset = context.get("pascha_offset")
        if offset == -70:
            if source == "octoechos":
                return "Glory to Your holy resurrection, O Lord!"
            elif source == "triodion":
                return "Have mercy on me, O God, have mercy on me!"
        elif offset == -63:
            if source == "octoechos":
                return "Glory to Your holy resurrection, O Lord!"
            elif source == "triodion":
                return "Have mercy on me, O God, have mercy on me!"
        elif offset == -56:
            if source == "octoechos":
                return "Glory to Your holy resurrection, O Lord!"
            elif source == "triodion":
                return "Have mercy on me, O God, have mercy on me!"
        elif offset == -49:
            if source == "triodion":
                return "Glory to You, O God, glory to You!"
        elif offset == -42:
            if source == "triodion":
                if canon_num == 1:
                    return "Glory to You, O God, glory to You!"
                else:
                    return "Holy hierarch Gregory pray to God for us!"
        elif offset == -35:
            if source == "triodion":
                return "Glory to Your precious Cross, O Lord!"
        elif offset == -28:
            if source == "octoechos":
                return "Glory to Your, holy Resurrection, O Lord!"
            elif source == "triodion":
                if canon_num == 1:
                    return "Have mercy on me, O God, have mercy on me!"
                else:
                    return "Venerable father John, pray to God for us!"
        elif offset == -8:
            if source == "triodion":
                return "Glory to You, O God, glory to You!"
        
        # Fallbacks
        if source == "octoechos":
            return "Glory to Your holy resurrection, O Lord!"
        elif source == "triodion":
            return "Glory to You, O God, glory to You!"
        elif source == "menaion":
            saints = context.get("saints", [])
            if saints:
                name = saints[0].get("name", "Saint")
                return f"Holy {name}, pray to God for us!"
            return "Holy Saint of God, pray to God for us!"
        return "Glory to You, O God, glory to You!"

    def _generate_abbreviated_canon_lines(self, context, katavasia_str):
        offset = context.get("pascha_offset")
        lines = []
        
        if offset in (-70, -63, -56, -49, -42, -35, -28):
            lines.append("At each ode, the irmos of the resurrection from the Octoechos.")
        elif offset == -8:
            pass
        else:
            if context.get("day_of_week") == 0:
                lines.append("At each ode, the irmos of the resurrection from the Octoechos.")
            else:
                lines.append("At each ode, the irmos from the Octoechos.")

        if offset == -70:
            lines.append("1 troparion of the resurrection.  ℟. Glory to Your holy resurrection, O Lord!")
            lines.append("1 troparion from the Triodion.  ℟.  Have mercy on me, O God, have mercy on me!")
            lines.append("Glory... both now... forefeast (from the Menaion).")
        elif offset == -63:
            lines.append("1 troparion of the resurrection.  ℟. Glory to Your holy resurrection, O Lord!")
            lines.append("1 troparion from the Triodion.  ℟.  Have mercy on me, O God, have mercy on me!")
            lines.append("Glory... both now... feast (from the Menaion).")
        elif offset == -56:
            lines.append("1 troparion of the resurrection.  ℟. Glory to Your holy resurrection, O Lord!")
            lines.append("2 troparia from the Triodion.  ℟.  Have mercy on me, O God, have mercy on me!")
            lines.append("Glory... both now... Triodion.")
        elif offset == -49:
            lines.append("2 troparia from the Triodion.  ℟.  Glory to You, O God, glory to You!")
            lines.append("Glory... both now... Triodion.")
        elif offset == -42:
            lines.append("2 troparia from canon I in the Triodion.  ℟.  Glory to You, O God, glory to You!")
            lines.append("1 troparia from canon II in the Triodion.  ℟.  Holy hierarch Gregory pray to God for us!")
            lines.append("Glory... both now... Triodion.")
        elif offset == -35:
            lines.append("3 troparia from canon of the Triodion.  ℟.  Glory to Your precious Cross, O Lord!")
            lines.append("Glory... both now... Triodion.")
        elif offset == -28:
            lines.append("1 troparion: canon of the Resurrection.  ℟.  Glory to Your, holy Resurrection, O Lord!")
            lines.append("1 troparion: Triodion canon I.  ℟.  Have mercy on me, O God, have mercy on me!")
            lines.append("1 troparion: Triodion canon II.  ℟.  Venerable father John, pray to God for us!.")
            lines.append("Glory... both now... Triodion.")
        elif offset == -8:
            lines.append("At each ode: 2 troparia from the first canon.  ℟. Glory to You, O God, glory to You!")
            lines.append("2 troparia from the second canon.  ℟. Glory to You, O God, glory to You!")
            lines.append("Glory... both now... second canon.")
        else:
            if context.get("day_of_week") == 0:
                lines.append("1 troparion of the resurrection.  ℟. Glory to Your holy resurrection, O Lord!")
                saints = context.get("saints", [])
                if saints:
                    name = saints[0].get("name", "Saint")
                    lines.append(f"1 troparion of the Saint.  ℟. Holy {name}, pray to God for us!")
                lines.append("Glory... both now... Theotokion.")
            else:
                lines.append("At each ode: Irmos, troparia with refrains, Glory... both now.")

        if katavasia_str:
            kat_line = katavasia_str
            if kat_line.startswith("Catabasia: "):
                kat_line = kat_line[len("Catabasia: "):]
            if "encounter" in katavasia_str.lower() or "meeting" in katavasia_str.lower():
                lines.append("Catabasia of the Encounter.")
            else:
                lines.append(katavasia_str)

        return lines

    def _format_canon_interludes_ode_3(self, context):
        offset = context.get("pascha_offset")
        if offset == -70:
            return "After Ode III: kontakion and ikos of the forefeast (found after Ode VI in the Menaion) and the sessional hymns from the Triodion (found after Ode III), Glory, both now... forefeast.  "
        elif offset == -63:
            return "After Ode III: kontakion and ikos of the feast, and the sessional hymns from the Triodion (found after Ode III), Glory, both now... feast.  "
        elif offset in (-56, -49, -42, -35, -28):
            return "After Ode III: Sessional hymns from the Triodion (found after Ode III).  "
        
        is_sunday = context.get("day_of_week") == 0
        if is_sunday:
            tone = context.get("octoechos_tone", context.get("tone", 1))
            tone_rom = self._roman_tone(tone)
            return f"After Ode III: Hypakoe in Tone {tone_rom}; Glory... both now... Theotokion.  "
        else:
            return "After Ode III: Sessional hymns; Glory... both now... Theotokion.  "

    def _format_canon_interludes_ode_6(self, context):
        offset = context.get("pascha_offset")
        if offset == -35:
            return "After Ode VI: kontakion and ikos of the Cross, from the Triodion, in Tone VII.  "
        elif offset in (-70, -63, -56, -49, -42, -28, -8):
            return "After Ode VI: kontakion and ikos from the Triodion are sung.  "
        
        is_sunday = context.get("day_of_week") == 0
        if is_sunday:
            tone = context.get("octoechos_tone", context.get("tone", 1))
            tone_rom = self._roman_tone(tone)
            return f"After Ode VI: Resurrection Kontakion and Ikos in Tone {tone_rom}.  "
        else:
            return "After Ode VI: Kontakion and Ikos.  "



