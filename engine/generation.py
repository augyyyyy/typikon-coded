"""
Ruthenian Engine - GenerationMixin
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

import json
import os
import re
from datetime import date, timedelta
import copy

from typikon_digest_generator import TypikonDigestGenerator
from engine.utils.type_utils import parse_rank_integer


class GenerationMixin:

    """Mixin providing generation methods for RuthenianEngine."""


    def resolve_service_combination_header(self, context, rubrics=None):
        """
        NEW-4: Generates the Dolnytsky-style header describing how services combine.
        
        E.g.: "Sunday service combined with the Triodion, and that of the forefeast"
        Citation: Dolnytsky Part 2 — Headers of all 20 Paradigms
        """
        components = []
        day_of_week = context.get("day_of_week", 0)
        season = context.get("season_id", "")
        d_title = context.get("dolnytsky_title", "")
        full_text = f"{d_title}".lower()
        
        # Base service
        if day_of_week == 0:
            components.append("Sunday service from the Octoechos")
        elif day_of_week == 6:
            components.append("Saturday service")
        else:
            day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
            components.append(f"{day_names.get(day_of_week, 'Weekday')} service")
        
        # Triodion overlay
        if season in ("triodion", "pentecostarion"):
            components.append("the Triodion")
        
        # Forefeast/Afterfeast
        if "forefeast" in full_text:
            components.append("the forefeast")
        elif "afterfeast" in full_text:
            components.append("the afterfeast")
        
        # Saint
        saints = context.get("saints", [])
        if saints:
            s_name = saints[0].get("name", saints[0].get("id", ""))
            if s_name:
                s_name_cleaned = s_name.strip()
                if s_name_cleaned.lower().startswith("st."):
                    components.append(s_name_cleaned)
                elif s_name_cleaned.lower().startswith("st "):
                    components.append("St. " + s_name_cleaned[3:])
                else:
                    components.append(f"St. {s_name_cleaned}")
        
        if len(components) <= 1:
            return {"header": components[0] if components else "Service", "components": components}
        
        # Check if it's just a simple weekday + saint (no Triodion, no fore/afterfeast)
        is_weekday = 0 < day_of_week <= 5
        has_triodion = season in ("triodion", "pentecostarion")
        has_feast_period = "forefeast" in full_text or "afterfeast" in full_text
        if is_weekday and not has_triodion and not has_feast_period and len(components) == 2 and saints:
            s_name = saints[0].get("name", saints[0].get("id", ""))
            s_name_cleaned = s_name.strip().rstrip('.')
            titles = ["hieromartyr", "protomartyr", "great martyr", "greatmartyr", "venerable", "martyr", "apostle", "archbishop", "bishop", "hierodeacon", "righteous", "prophet"]
            s_name_lower = s_name_cleaned.lower()
            if s_name_lower.startswith("st. ") or s_name_lower.startswith("st "):
                rest = s_name_cleaned[4:].strip() if s_name_lower.startswith("st. ") else s_name_cleaned[3:].strip()
                if any(t in rest.lower() for t in titles):
                    s_name_cleaned = rest
            header = f"Service of {s_name_cleaned}"
        else:
            header = components[0] + " combined with " + ", and that of ".join(components[1:])
            
        return {"header": header, "components": components}


    def get_expanded_service_name(self, service_def, context):
        """
        Returns the expanded service name (e.g., "Great Vespers", "Lenten Matins").
        Used for Report Generation headers.
        """
        base_name = service_def["name"]
        
        # 1. Vespers
        if base_name == "Vespers":
             # Check explicit type in logic/context
             even_type = self.resolve_evening_service_type(context)
             if even_type == "great_vespers": return "Great Vespers"
             elif even_type == "great_vespers_vigil": return "Great Vespers" # or "Great Vespers with Vigil"
             elif even_type == "great_vespers_simple": return "Great Vespers"
             elif even_type == "vesperal_liturgy_basil": return "Vesperal Liturgy of St. Basil"
             elif even_type == "vesperal_liturgy_chrysostom": return "Vesperal Liturgy of St. John Chrysostom"
             elif even_type == "paschal_vespers": return "Paschal Vespers"
             
             # Fallback logic
             rank = parse_rank_integer(context.get("rank", 5))
             is_lent = context.get("season") == "lent"
             day = context.get("day_of_week")
             
             if is_lent and day in [0,1,2,3,4]: # Sun-Thu eve
                  return "Daily Vespers (Lenten)" # Was returning "Great Vespers"? Correction: Weekday Lenten is Daily-ish.
             
             # Fallback
             return "Daily Vespers"
                  
        # 2. Compline
        if base_name == "Compline":
             if hasattr(self, "resolve_compline_type"):
                  ctype = self.resolve_compline_type(context)
                  if ctype == "paschal_hours": return "Paschal Hours"
                  elif ctype == "great_compline": return "Great Compline"
                  return "Small Compline"
                  if day == 5: return "Great Vespers" # Fri Eve
                  return "Lenten Vespers"
             
             if rank <= 3 or context.get("is_vigil"): return "Great Vespers"
             if day == 6: return "Great Vespers" # Sat Eve for Sun
             
             return "Daily Vespers"

        # 2. Compline
        if base_name == "Compline":
             is_lent = context.get("season") == "lent"
             day = context.get("day_of_week")
             # Mon-Thu Evening (Day 1-4)
             if is_lent and day in [1,2,3,4]: return "Great Compline"
             return "Small Compline"

        # 3. Midnight Office
        if base_name == "Midnight Office":
             day = context.get("day_of_week")
             if day == 0: return "Midnight Office (Sunday)"
             if day == 6: return "Midnight Office (Saturday)"
             
             mode_data = self.resolve_midnight_office_mode(context)
             if mode_data.get("mode") == "feast":
                  return "Midnight Office"
             return "Midnight Office (Daily)"

        # 4. Matins
        if base_name == "Matins":
             if context.get("triodion_period") == "holy_friday": return "Matins of Holy Saturday (Jerusalem Matins)"
             if context.get("triodion_period") == "holy_thursday": return "Matins of Holy Friday (12 Gospels)"
             
             is_lent = context.get("season") == "lent"
             day = context.get("day_of_week")
             rank = parse_rank_integer(context.get("rank", 5))
             
             if is_lent and day in [1,2,3,4,5] and rank > 3: 
                  return "Lenten Matins (Alleluia)"
             if day == 0: return "Sunday Matins"
             if rank <= 3 or context.get("is_vigil"): return "Festal Matins"
             
             return "Daily Matins"

        # 5. Hours
        if "Hour" in base_name:
             if self.check_royal_hours_trigger(context):
                  return base_name.replace("Hour", "Royal Hour")
             
             is_lent = context.get("season") == "lent"
             day = context.get("day_of_week")
             if is_lent and day in [1,2,3,4,5]: return f"Lenten {base_name}"
             
             return base_name

        # 6. Liturgy
        if base_name == "Liturgy":
             if context.get("is_aliturgical"): return "Typika (Aliturgical)"
             
             # Check explicit type first
             even_type = context.get("overrides", {}).get("liturgy_type") or context.get("variables", {}).get("liturgy_type") or context.get("liturgy_type")
             if even_type == "vesperal_merge_logic": return "Vesperal Divine Liturgy of St. Basil the Great"
             if even_type == "liturgy_chrysostom_vesperal": return "Vesperal Divine Liturgy of St. John Chrysostom"
             if even_type == "liturgy_presanctified": return "Liturgy of the Presanctified Gifts"
             
             is_lent = context.get("season") == "lent"
             day = context.get("day_of_week")
             rank = parse_rank_integer(context.get("rank", 5))
             
             if is_lent and day in [3, 5] and rank > 3: return "Liturgy of the Presanctified Gifts"
             
             if is_lent and day == 0 and context.get("pascha_offset", 0) <= -8: return "Divine Liturgy of St. Basil the Great"
             if context.get("date", "").endswith("-01-01"): return "Divine Liturgy of St. Basil the Great"
             
             return "Divine Liturgy of St. John Chrysostom"

        return base_name


    def _get_structure_sequence(self, struct_data, root_id):
        """
        Recursively resolves the sequence of a structure, handling inheritance and overrides.
        """
        structure_def = struct_data.get("structures", {}).get(root_id)
        if not structure_def:
            return None

        # Base Sequence
        if "inherits_from" in structure_def and structure_def["inherits_from"]:
            parent_id = structure_def["inherits_from"]
            sequence = self._get_structure_sequence(struct_data, parent_id)
            if sequence is None: return None # Parent not found
            
            # Apply Overrides
            for override in structure_def.get("overrides", []):
                target_id = override.get("target_id")
                action = override.get("action")
                
                # Find index of target
                indices = [i for i, slot in enumerate(sequence) if slot.get("id") == target_id]
                if not indices: continue
                idx = indices[0] # Handle first match for now

                if action == "replace":
                    sequence[idx] = override.get("new_component")
                elif action == "delete":
                    del sequence[idx]
                elif action == "insert_after":
                    sequence.insert(idx + 1, override.get("new_component"))
                elif action == "insert_before":
                    sequence.insert(idx, override.get("new_component"))
                elif action == "modify":
                    # Merge logic/rubric into existing slot
                    if "rubric" in override: sequence[idx]["rubric"] = override["rubric"]
                    if "content" in override: sequence[idx]["content"] = override["content"]
                    if "logic_args" in override:
                        if "content" in sequence[idx] and "logic" in sequence[idx]["content"]:
                             # Safe merge args
                             if "args" not in sequence[idx]["content"]["logic"]: sequence[idx]["content"]["logic"]["args"] = {}
                             sequence[idx]["content"]["logic"]["args"].update(override["logic_args"])
            
            return sequence
        else:
            return copy.deepcopy(structure_def.get("sequence", []))

    def generate_full_booklet(self, context, rubrics, include_ceremonial=False):

            context["include_ceremonial"] = include_ceremonial
            booklet = [f"DATE: {context['date']}\nFEAST: {rubrics['title']}\n"]

            # Determine Matins override first
            matins_override = None
            if context["triodion_period"] == "holy_friday":
                matins_override = "tomb_matins"  # Great Saturday Matins (Encomia)
            elif context["triodion_period"] in ["pascha", "bright_week"]:
                matins_override = "bright_matins"
            elif context["triodion_period"] == "holy_week_weekday" and context.get("day_of_week") in [4, 5]:
                # Holy Thursday night = Passion Matins (12 Gospels), actually celebrated Thursday evening
                # day_of_week==4 is Thursday in 0=Sun convention
                matins_override = "passion_matins"
            elif context["triodion_period"] == "holy_week_weekday" and context.get("day_of_week") in [1, 2, 3]:
                # Holy Monday (1), Tuesday (2), Wednesday (3) = Bridegroom Matins
                matins_override = "bridegroom_matins"

            for service in self.daily_cycle:
                service_name = service["name"]

                # Suppression logic for Compline and Midnight Office during Weekday Vigil
                if service_name in ("Compline", "Midnight Office"):
                    day = context.get("day_of_week")
                    v_type = rubrics.get("overrides", {}).get("vespers_type") or rubrics.get("variables", {}).get("vespers_type") or context.get("vespers_type")
                    if day != 0 and v_type == "great_vespers_vigil":
                        continue

                # Suppression logic for Vesperal Liturgy
                if service_name == "Vespers" and "vesperal_merge_logic" in rubrics.get("overrides", {}).get(
                        "liturgy_type", ""):
                    booklet.append(
                        f"\n--- {service_name.upper()} ---\nNOTE: Vespers is combined with the Divine Liturgy below.")
                    continue

                # Get base root_id
                # Check variables first (standard logic), then overrides (higher priority), then default
                root_id = service["root"]
                if service["type_key"] in rubrics.get("variables", {}):
                    root_id = rubrics["variables"][service["type_key"]]
                
                if service["type_key"] in rubrics.get("overrides", {}):
                    root_id = rubrics["overrides"][service["type_key"]]

                # Apply specific overrides
                if service_name == "Matins" and matins_override:
                    root_id = matins_override

                if "hours_type" in service["type_key"]:
                    var_hours = rubrics.get("variables", {}).get("hours_type", "");
                    if "royal" in var_hours:
                        root_id = "structure_royal";
                    elif "lenten" in var_hours:
                        root_id = "structure_lenten";
                    elif "paschal" in var_hours:
                        root_id = "structure_paschal"

                if service_name == "Midnight Office":
                     mode_data = self.resolve_midnight_office_mode(context)
                     if "mode" in mode_data:
                          # Map "sunday" -> "midnight_sunday"
                          root_id = f"midnight_{mode_data['mode']}"

                if include_ceremonial:
                    booklet.append(f"\n--- {service_name.upper()} ({root_id}) ---")
                else:
                    booklet.append(f"\n--- {service_name.upper()} ---")

                struct_data = self._load_json(service["file"])
                # Use new inheritance helper
                skeleton = self._get_structure_sequence(struct_data, root_id)

                if not skeleton:
                    booklet.append(f"ERROR: Structure '{root_id}' not found in {service['file']}")
                    continue

                def process_sequence(sequence, depth=0):
                    for slot in sequence:
                        # Normalize type/content
                        content = slot.get("content", {})
                        if not content and "type" in slot: content = slot
                        slot_type = content.get("type")

                        if slot_type == 'link':
                            target_id = content.get('target_id')
                            target_file = content.get('target_file')
                             
                            if target_file and target_id:
                                # Resolve path
                                full_path = os.path.join(self.json_db, target_file)
                                if not os.path.exists(full_path): full_path = target_file
                                
                                if os.path.exists(full_path):
                                     try:
                                         with open(full_path, 'r', encoding='utf-8') as f:
                                             linked_data = json.load(f)
                                         # Get sequence (handles inheritance too)
                                         sub_seq = self._get_structure_sequence(linked_data, target_id)
                                         if sub_seq:
                                             if include_ceremonial:
                                                 booklet.append(f"[{slot.get('id','LINK')}] >>> EXPANDING LINK: {target_id} <<<")
                                             process_sequence(sub_seq, depth + 1)
                                             if include_ceremonial:
                                                 booklet.append(f"[{slot.get('id','LINK')}] <<< END LINK <<<")
                                         else:
                                             booklet.append(f"[{slot.get('id','LINK')}] ERROR: Link target '{target_id}' not found.")
                                     except Exception as e:
                                         booklet.append(f"[{slot.get('id','LINK')}] ERROR Loading Link: {e}")
                            else:
                                 booklet.append(f"[{slot.get('id','LINK')}] ERROR: Invalid Link Definition")
                            continue

                        slot_id = slot.get('id', 'UNKNOWN_ID')
                        if slot_id == 'UNKNOWN_ID':
                            print(f"WARNING: Slot missing ID in {service_name}: {slot}")
                        
                        text = self._resolve_slot(slot, rubrics, context)
                        if text and text.strip():
                            booklet.append(text)
                            
                        # Recurse into nested sequence if it exists
                        nested_seq = slot.get("sequence") or content.get("sequence")
                        if nested_seq and isinstance(nested_seq, list) and slot_type != "sequence":
                            process_sequence(nested_seq, depth + 1)

                process_sequence(skeleton)

            return "\n".join(booklet)


    def generate_rubrical_abstract(self, context, rubrics):
        """
        Generates a structural abstract focusing ONLY on Logic Hooks and Rubrics.
        """
        abstract = [f"RUBRICAL ABSTRACT: {context['date']}", f"Logic: {rubrics['title']}"]
        
        # TOP LEVEL LOGIC TRACE
        if "_trace" in rubrics and rubrics["_trace"]:
             abstract.append("")
             abstract.append(f"[TRACE] === SERVICE DECISION LOGIC ===")
             for line in rubrics["_trace"]:
                  abstract.append(f"[TRACE] {line}")
             abstract.append("")
        else:
             abstract.append("")
        return "\n".join(abstract)


    def generate_typikon_digest(self, context, rubrics, mode="full"):
        raw_output = TypikonDigestGenerator(self).generate(context, rubrics, mode=mode)
        return self._sanitize_digest_output(raw_output)

    def _sanitize_digest_output(self, text):
        if not text:
            return ""
        lines = text.splitlines()
        clean_lines = []
        for line in lines:
            line_strip = line.strip()
            
            # Skip useless developer rubrics
            if line_strip.lower() in [
                "rubric: rubric", "rubric: description", "rubric:",
                "> **rubric**: rubric", "> **rubric**: description", "> **rubric**:"
            ]:
                continue
                
            # Skip lines that look like file/line paths or parser reference logs
            if ".txt:l" in line_strip.lower() or ".json" in line_strip.lower():
                continue
                
            # Sanitize internal keys / raw variables
            sanitized_line = line
            
            # Replace Tone_X or Tone_x with Roman numerals
            def roman_replace(match):
                num = int(match.group(1))
                roman = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII'}.get(num, str(num))
                return f"Tone {roman}"
            sanitized_line = re.sub(r'\bTone[_\s]+([1-8])\b', roman_replace, sanitized_line, flags=re.IGNORECASE)
            
            # Replace generic internal keys like Eothinon_1_theotokion, saint_1, etc.
            # Convert snake_case identifiers to title case/human readable text
            def key_replace(match):
                key = match.group(0)
                if "_" in key:
                    parts = key.split("_")
                    return " ".join(p.capitalize() for p in parts)
                return key
            sanitized_line = re.sub(r'\b[a-zA-Z]+_[a-zA-Z0-9_]+\b', key_replace, sanitized_line)
            sanitized_line = re.sub(r'(?<!\.)\.\.(?!\.)', '.', sanitized_line)
            
            clean_lines.append(sanitized_line)
            
        return "\n".join(clean_lines)


    def _legacy_generate_typikon_digest(self, context, rubrics):
        """
        Generates a 'Typikon Style' digest (instructions only, no full text).
        """
        digest = [f"TYPIKON: {context['date']}"]
        digest.append(f"Logic: {rubrics['title']}")
        digest.append("-" * 40)

        def process_skeleton(skeleton, depth=0):
            indent = "" 
            
            for slot in skeleton:
                slot_id = slot.get('id', 'anonymous_slot')
                
                # 1. Rubrics (Instructional)
                if "rubric" in slot:
                    r = slot["rubric"]
                    title = r
                    if isinstance(r, dict):
                        # Try commonly used keys
                        title = r.get('title') or r.get('description') or r.get('text')
                        if not title:
                             # Summarize sources if present
                             if "source_ref" in r: title = f"Rubric ({r['source_ref']})"
                             else: title = "Rubric"
                        if "ordo_ref" in r:
                             title = f"{title} [Ordo {r['ordo_ref']}]"
                    digest.append(f"RUBRIC: {title}")

                content = slot.get("content", {})
                if not content and "type" in slot: content = slot
                slot_type = content.get("type")
                
                # 2. Variable Logic
                if slot_type == "variable_logic":
                    func_name = content["logic"].get("function")
                    args = content["logic"].get("args", {})
                    lines = self._format_logic_hook(func_name, args, context, rubrics)
                    digest.extend(lines)

                # 3. Generators
                elif slot_type == "generator":
                    method = content.get("generator_method")
                    args = content.get("args", {})
                    # Special handling for Stichera to get counts
                    if method == "generate_stichera_sequence":
                         enriched_context = {**context, **rubrics.get("variables", {})}
                         enriched_context["overrides"] = rubrics.get("overrides", {})
                         if rubrics.get("is_sunday_vigil"): enriched_context["is_sunday_vigil"] = True

                         # Use the 'resolve_' logic directly to get metadata
                         # This assumes the generator wrapper logic is similar
                         if "vespers" in args.get('slot_id', ''):
                              try:
                                   res = self.resolve_vespers_stichera(enriched_context)
                                   # Format info
                                   total = res.get("total_count", 0)
                                   digest.append(f"At 'Lord, I Call': {total} stichera")
                                   for item in res.get("distribution", []):
                                        c = item.get('count', item.get('qty', '?'))
                                        s = item.get('source', item.get('type', '')).upper()
                                        digest.append(f"- {c} from {s}")
                                   if "glory" in res: digest.append(f"Glory... {res['glory']}")
                                   if "both_now" in res: digest.append(f"Both Now... {res['both_now']}")
                              except:
                                   digest.append("At 'Lord, I Call': (Logic Error)")

                # 4. Sequences (Recurse)
                elif slot_type == "sequence":
                    if "components" in content:
                        process_skeleton(content["components"], depth + 1)
                
                # 5. Fixed Content
                elif slot_type == "fixed_ref":
                    ref = content.get('ref_key')
                    if "psalm" in ref: digest.append(f"Psalm: {ref.split('.')[-1]}")
                    elif "litany" in ref: digest.append(f"Litany")
                    elif "hymn" in ref: digest.append(f"Hymn: {ref.split('.')[-1]}")

                # 6. Links (Recurse)
                elif slot_type == "link":
                    target = slot.get('target_id')
                    target_file = slot.get('target_file')
                    if target_file and target:
                         import os
                         full_path = os.path.join(self.json_db, target_file)
                         if not os.path.exists(full_path): full_path = target_file
                         if os.path.exists(full_path):
                             try:
                                 with open(full_path, 'r', encoding='utf-8') as f: linked_data = json.load(f)
                                 sub_skeleton = self._get_structure_sequence(linked_data, target)
                                 if sub_skeleton: process_skeleton(sub_skeleton, depth + 1)
                             except: pass

        for service in self.daily_cycle:
            service_name = service["name"]

            # Suppression logic for Compline and Midnight Office during Weekday Vigil
            if service_name in ("Compline", "Midnight Office"):
                day = context.get("day_of_week")
                v_type = rubrics.get("overrides", {}).get("vespers_type") or rubrics.get("variables", {}).get("vespers_type") or context.get("vespers_type")
                if day != 0 and v_type == "great_vespers_vigil":
                    continue

            digest.append(f"\n=== {service_name.upper()} ===")
            
            # Root ID resolution
            root_id = service["root"]
            if service["type_key"] in rubrics.get("variables", {}):
                root_id = rubrics["variables"][service["type_key"]]
            if service["type_key"] in rubrics.get("overrides", {}):
                root_id = rubrics["overrides"][service["type_key"]]

            # Apply Matins/Midnight/Hours overrides similar to generate_full_booklet
            if service_name == "Matins":
                 if context["triodion_period"] == "holy_friday": root_id = "tomb_matins"
                 elif context["triodion_period"] in ["pascha", "bright_week"]: root_id = "bright_matins"
            elif service_name == "Midnight Office":
                 mode_data = self.resolve_midnight_office_mode(context)
                 if "mode" in mode_data: root_id = f"midnight_{mode_data['mode']}"
            elif "hours_type" in service["type_key"]:
                 var_hours = rubrics.get("variables", {}).get("hours_type", "")
                 if "royal" in var_hours: root_id = "structure_royal"
                 elif "lenten" in var_hours: root_id = "structure_lenten"
                 elif "paschal" in var_hours: root_id = "structure_paschal"

            struct_data = self._load_json(service["file"])
            skeleton = self._get_structure_sequence(struct_data, root_id)
            if skeleton:
                process_skeleton(skeleton)

        return "\n".join(digest)


    def _format_logic_hook(self, func_name, args, context, rubrics):
        """
        Executes logic and returns a list of formatted strings for the Typikon digest.
        """
        if not hasattr(self, func_name): return []

        try:
            # Prepare Context
            enriched_context = {**context, **rubrics.get("variables", {})}
            enriched_context["overrides"] = rubrics.get("overrides", {})
            if rubrics.get("is_sunday_vigil"): enriched_context["is_sunday_vigil"] = True

            # Get Function
            func = getattr(self, func_name)
            
            # Inspect Args
            import inspect
            sig = inspect.signature(func)
            call_kwargs = {}
            if "rubrics" in sig.parameters: call_kwargs["rubrics"] = rubrics
            
            # Special Args (hours)
            if func_name == "resolve_hours_collision" and "hour_num" in args:
                 call_kwargs["hour_num"] = args["hour_num"]

            # Execute
            result = func(enriched_context, **call_kwargs)

            # --- FORMATTING RULES ---
            
            # 1. Prokeimenon
            if func_name == "resolve_prokeimenon" or "prokeimenon" in func_name:
                lines = []
                if isinstance(result, dict): result = [result]
                for p in result:
                     if isinstance(p, dict):
                         ref = p.get('ref_key', p.get('source', 'Unknown'))
                         lines.append(f"Prokeimenon: {ref.split('.')[-1]}")
                return lines

            # 2. God is the Lord / Alleluia
            if func_name == "resolve_god_is_the_lord_troparia":
                if result.get("gradual_type") == "alleluia":
                    return ["At God is the Lord: Alleluia is sung."]
                else:
                    lines = [f"At God is the Lord (Tone {result.get('tone')}):"]
                    for t in result.get("sequence", []):
                        lines.append(f"- {t.get('content', t.get('type'))}")
                    return lines

            # 3. Readings
            if "readings" in func_name:
                lines = ["Readings:"]
                if isinstance(result, list):
                    for r in result:
                        citation = r.get('citation', '')
                        if not citation and "source" in r: citation = r.get('source')
                        lines.append(f"- {citation}")
                return lines

            # 4. Troparia (Generic)
            if "troparia" in func_name:
                lines = ["Troparia:"]
                if isinstance(result, dict):
                    if "components" in result:
                        for c in result["components"]:
                             lines.append(f"- {c.get('id', c.get('type'))}")
                    elif "sequence" in result:
                        for c in result["sequence"]:
                             lines.append(f"- {c.get('content', c.get('type'))}")
                    elif "troparia_sequence" in result: # Hours collision result
                        for c in result["troparia_sequence"]:
                             lines.append(f"- {c.get('target', c.get('name'))}")
                return lines
                
            return []

        except Exception as e:
            return [f"[Error formatting {func_name}: {e}]"]


    def _expand_abstract_logic(self, func_name, args, context, rubrics):
        """
        Executes logic hooks specifically for the Abstract view to show 'What happened'.
        """
        if not hasattr(self, func_name):
            return [f"      [Logic Missing: {func_name}]"]

        try:
            # CRITICAL: Merge rubrics variables into context so inner functions access menaion_rank, etc.
            enriched_context = {**context, **rubrics.get("variables", {})}
            # Also add overrides to context for direct access
            enriched_context["overrides"] = rubrics.get("overrides", {})
            # FIX: Copy is_sunday_vigil flag from rubrics for Saturday Vigil stichera/doxology resolution
            if rubrics.get("is_sunday_vigil"):
                enriched_context["is_sunday_vigil"] = True
            
            # Execute the logic
            func = getattr(self, func_name)
            
            # Smart Argument Injection
            # If args dict provided, try to pass as kwargs if function accepts them
            import inspect
            sig = inspect.signature(func)
            
            call_kwargs = {}
            if "rubrics" in sig.parameters:
                call_kwargs["rubrics"] = rubrics
            
            # Merge JSON args into call arguments
            # Special handling for known signatures
            if func_name == "resolve_hours_collision" and "hour_num" in args:
                 call_kwargs["hour_num"] = args["hour_num"]
            
            result = func(enriched_context, **call_kwargs)
                 
            output = []
            
            # Formatter for specific types
            meta = self._extract_logic_metadata(func_name)
            reason = self._explain_logic_decision(func_name, enriched_context, result)
            
            # Simple metadata block for ALL expansions
            # We add a "TRACE" prefix line which the generator can choose to render or hidden
            output.append(f"      [TRACE] Citation: {meta['citation']}")
            output.append(f"      [TRACE] Reason: {reason}")
            
            if func_name == "resolve_vespers_stichera":
                 # This returns the distribution dict
                 total = result.get("total_count", result.get("total", 0))
                 dist = result.get("distribution", result.get("counts", []))
                 output.append(f"      Total: {total} Stichera")
                 for item in dist:
                     c = item.get('count', item.get('qty', '?'))
                     src = item.get('source', item.get('type', 'Unknown')).upper()
                     output.append(f"      - {c} from {src}")
                 if "glory" in result: output.append(f"      Glory: {result['glory']}")
                 if "both_now" in result: output.append(f"      Both Now: {result['both_now']}")
                 return output

            if func_name == "resolve_hours_collision":
                 output.append(f"      Hour: {result.get('hour_number')}")
                 output.append("      Troparia Sequence:")
                 for t in result.get("troparia_sequence", []):
                      output.append(f"        - {t.get('type')} ({t.get('target', t.get('name', ''))})")
                 output.append(f"      Kontakion: {result.get('kontakion_winner')}")
                 return output

            if isinstance(result, list):
                # Check if it's a list of components/dicts
                for idx, item in enumerate(result):
                    if isinstance(item, dict):
                        # Try to find a human readable label
                        label = item.get("type", "item")
                        if "ref_key" in item: label += f" ({item['ref_key']})"
                        elif "source" in item: label += f" ({item['source']})"
                        output.append(f"      {idx+1}. {label}")
                    else:
                        output.append(f"      {idx+1}. {item}")
                        
            elif isinstance(result, dict):
                 # Flatten simple dicts
                 if "type" in result: output.append(f"      Type: {result['type']}")
                 if "gradual_type" in result: output.append(f"      Type: {result['gradual_type'].upper()}")
                 if "mode" in result: output.append(f"      Mode: {result['mode']}")
                 if "ref_key" in result: output.append(f"      Ref: {result['ref_key']}")
                 
                 # Components list
                 if "components" in result:
                      output.append("      Components:")
                      for sub in result["components"]:
                           output.append(f"        - {sub}")
                 elif "sequence" in result:
                      output.append("      Sequence:")
                      for sub in result["sequence"]:
                           output.append(f"        - {sub}")
                           
            else:
                output.append(f"      Result: {result}")
                
            return output
            
        except Exception as e:
            return [f"      [Expansion Error: {e}]"]


    def _expand_abstract_generator(self, method, args, context, rubrics):
        """
        Simulates generator execution for Abstract view.
        """
        output = []
        
        if method == "generate_stichera_sequence":
             # We piggyback on resolve_vespers_stichera logic usually
             # But slot_id gives a hint.
             slot_id = args.get("slot_id", "")
             
             if "vespers" in slot_id:
                  # Force call to resolver
                  return self._expand_abstract_logic("resolve_vespers_stichera", {}, context, rubrics)
                  
        if method == "generate_antiphons":
             return self._expand_abstract_logic("resolve_liturgy_antiphons", {}, context, rubrics)

        if method == "generate_hour_troparia":
             # Use resolve_hours_collision logic
             hour = args.get("hour", 1)
             return self._expand_abstract_logic("resolve_hours_collision", {"hour_num": hour}, context, rubrics)
             
        output.append(f"      (Generator logic for {method} not specificed)")
        return output

    def _get_humanized_title(self, item, ref_key):
        if not ref_key:
            return ""
        title = None
        if item and isinstance(item, dict):
            title = item.get("title")
        if not title or title == ref_key or "." in str(title) or "_" in str(title):
            last_part = ref_key.split(".")[-1]
            title = last_part.replace("_", " ").strip().title()
        return title

    def _resolve_slot(self, slot, rubrics, context=None):
        # Check ceremonial filtering
        include_ceremonial = False
        if context:
            include_ceremonial = context.get("include_ceremonial", False)
            
        slot_id = slot.get("id", "")
        content = slot.get("content", {})
        if not content and "type" in slot:
            content = slot
        slot_type = content.get("type")
        
        ceremonial_slot_ids = {
            "vesting_rite", "opening_vigil", "censing_psalm_103", 
            "censing_lord_i_have_cried", "censing_entrance", 
            "doors_entrance", "resolve_door_state", "fasting_rule"
        }
        
        ceremonial_functions = {
            "resolve_vestment_set", "resolve_censing_annotation", 
            "resolve_door_state", "resolve_clergy_variant", "resolve_fasting_rule"
        }
        
        func_name = None
        if slot_type == "variable_logic":
            func_name = content.get("logic", {}).get("function")
            
        if not include_ceremonial:
            if slot_id in ceremonial_slot_ids or func_name in ceremonial_functions:
                return ""  # Suppress this slot entirely!
                
        # 1. Format Rubric if present (Instructional directions)
        output_lines = []
        if "rubric" in slot:
            r = slot["rubric"]
            if isinstance(r, dict):
                title = r.get("title", "")
                sources = []
                if "source_ref" in r:
                    sources.append(r["source_ref"])
                if "ordo_ref" in r:
                    sources.append(f"Ordo {r['ordo_ref']}")
                citation_html = ""
                if sources:
                    cit_str = ", ".join(sources)
                    citation_html = f' <sup class="citation-sup" title="Citation: {cit_str}">{cit_str}</sup>'
                
                if title:
                    output_lines.append(f'<span class="rubric">{title}{citation_html}</span>')
                elif citation_html:
                    output_lines.append(f'<p>{citation_html}</p>')
                
                # Add role-based dialogue
                if "roles" in r:
                    for role, text in r["roles"].items():
                        # Skip minor sanctuary clergy instructions if include_ceremonial is False
                        if not include_ceremonial and role.lower() in ("priest", "deacon", "subdeacon") and slot_id in ceremonial_slot_ids:
                            continue
                        output_lines.append(f'<p><span class="actor">{role.upper()}</span> {text}</p>')
            else:
                output_lines.append(f'<span class="rubric">{r}</span>')
                 
        # 2. Resolve and Hydrate Content
        if slot_type == "fixed_ref":
            ref_key = content.get("ref_key")
            item = self.get_text(ref_key, context=context)
            if item:
                title = self._get_humanized_title(item, ref_key)
                text_val = item.get("content", "")
                cit_html = ""
                if "source" in item:
                    cit_html = f' <sup class="citation-sup" title="Source: {item["source"]}">{item["source"]}</sup>'
                output_lines.append(f'<div class="title-medium">{title}{cit_html}</div>')
                for p_text in text_val.split("\n"):
                    p_text = p_text.strip()
                    if p_text:
                        output_lines.append(f'<p>{p_text}</p>')
            else:
                humanized = ref_key.split(".")[-1].replace("_", " ").title()
                output_lines.append(f'<p class="rubric">[Missing text: {humanized} ({ref_key})]</p>')
                 
        elif slot_type == "fixed_group":
            for ref_key in content.get("ref_keys", []):
                item = self.get_text(ref_key, context=context)
                if item:
                    title = self._get_humanized_title(item, ref_key)
                    text_val = item.get("content", "")
                    cit_html = ""
                    if "source" in item:
                        cit_html = f' <sup class="citation-sup" title="Source: {item["source"]}">{item["source"]}</sup>'
                    output_lines.append(f'<div class="title-medium">{title}{cit_html}</div>')
                    for p_text in text_val.split("\n"):
                        p_text = p_text.strip()
                        if p_text:
                            output_lines.append(f'<p>{p_text}</p>')
                else:
                    humanized = ref_key.split(".")[-1].replace("_", " ").title()
                    output_lines.append(f'<p class="rubric">[Missing text: {humanized} ({ref_key})]</p>')
                     
        elif slot_type == "variable_logic":
            # Execute the logic method
            if hasattr(self, func_name):
                try:
                     func = getattr(self, func_name)
                     if context:
                         import inspect
                         sig = inspect.signature(func)
                         call_kwargs = {}
                         
                         # Enrich context
                         enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
                         enriched["overrides"] = rubrics.get("overrides", {})
                         if rubrics.get("is_sunday_vigil"):
                             enriched["is_sunday_vigil"] = True
                             
                         args = content.get("logic", {}).get("args", {})
                         normalized_args = {}
                         for k, v in args.items():
                             if k == "pos":
                                 normalized_args["position"] = v
                             elif k == "num":
                                 normalized_args["num"] = v
                             else:
                                 normalized_args[k] = v
                                 
                         if "rubrics" in sig.parameters:
                             call_kwargs["rubrics"] = rubrics
                             
                         for param_name in sig.parameters:
                             if param_name in normalized_args:
                                 call_kwargs[param_name] = normalized_args[param_name]
                                 
                         params = list(sig.parameters.values())
                         has_context = len(params) > 0
                         if has_context:
                             result = func(enriched, **call_kwargs)
                         else:
                             result = func()
                     else:
                         result = f"[Pending execution: {func_name}]"
                         
                     # Hydrate and Format the logic result
                     hydrated = self._hydrate_and_format_logic_result(result, func_name, context, rubrics)
                     if hydrated:
                         output_lines.append(hydrated)
                         
                except Exception as e:
                     output_lines.append(f'<p class="rubric">[Logic Error: {func_name} - {e}]</p>')
            else:
                 output_lines.append(f'<p class="rubric">[Missing Logic Resolver: {func_name}]</p>')
                 
        elif slot_type == "generator":
            generator_method = content.get("generator_method")
            args = content.get("args", {})
            if generator_method == "generate_stichera_sequence":
                try:
                     res = self.resolve_vespers_stichera(context)
                     hydrated = self._hydrate_and_format_logic_result(res, "resolve_vespers_stichera", context)
                     if hydrated:
                         output_lines.append(hydrated)
                except Exception as e:
                     output_lines.append(f'<p class="rubric">[Generator Error: {generator_method} - {e}]</p>')
            elif generator_method == "generate_antiphons":
                try:
                     res = self.resolve_liturgy_antiphons(context, rubrics)
                     hydrated = self._hydrate_and_format_logic_result(res, "resolve_liturgy_antiphons", context)
                     if hydrated:
                         output_lines.append(hydrated)
                except Exception as e:
                     output_lines.append(f'<p class="rubric">[Generator Error: {generator_method} - {e}]</p>')
            elif generator_method == "generate_hour_troparia":
                try:
                     hour_num = args.get("hour", 1)
                     res = self.resolve_hours_collision(context, hour_num=hour_num)
                     hydrated = self._hydrate_and_format_logic_result(res, "resolve_hours_collision", context)
                     if hydrated:
                         output_lines.append(hydrated)
                except Exception as e:
                     output_lines.append(f'<p class="rubric">[Generator Error: {generator_method} - {e}]</p>')
            else:
                 output_lines.append(f'<p class="rubric">[Generator: {generator_method} (not fully formatted)]</p>')
                 
        elif slot_type == "slot_variable":
            slot_id = content.get("slot_id") or content.get("id") or slot.get("slot_id") or slot.get("id")
            
            # Extract month and day
            dt = context.get("date")
            if isinstance(dt, str):
                parts = dt.split("-")
                month = parts[1]
                day = parts[2]
            elif hasattr(dt, "month") and hasattr(dt, "day"):
                month = f"{dt.month:02d}"
                day = f"{dt.day:02d}"
            else:
                month = context.get("month", "01")
                day = context.get("day", "01")
                
            # Enrich context
            enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
            enriched["overrides"] = rubrics.get("overrides", {})
            if rubrics.get("is_sunday_vigil"):
                enriched["is_sunday_vigil"] = True
            
            if slot_id in ("liturgy_prokeimenon", "liturgy_epistle", "liturgy_alleluia", "liturgy_gospel", "prokeimenon", "epistle", "alleluia", "gospel"):
                try:
                    res = self.resolve_liturgy_readings(enriched, rubrics)
                    if res and "readings" in res:
                        # Iterate through each reading set
                        for r_set in res["readings"]:
                            if not isinstance(r_set, dict):
                                continue
                            
                            # Determine what part of the reading set we need
                            part_key = None
                            if "prokeimenon" in slot_id:
                                part_key = "prokeimenon"
                            elif "epistle" in slot_id:
                                part_key = "epistle"
                            elif "alleluia" in slot_id:
                                part_key = "alleluia"
                            elif "gospel" in slot_id:
                                part_key = "gospel"
                                
                            if part_key and part_key in r_set:
                                pk = r_set[part_key]
                                ref_key = pk.get("ref_key", "")
                                text_val = pk.get("text") or pk.get("content") or ""
                                tone = pk.get("tone")
                                
                                # Check if text_val is a placeholder or empty, and fetch from text_db
                                if ref_key and (not text_val or "[missing" in str(text_val).lower() or "[stub" in str(text_val).lower()):
                                    text_item = self.get_text(ref_key, context=context)
                                    if text_item:
                                        text_val = text_item.get("content", "")
                                        if not tone:
                                            tone = text_item.get("tone")
                                            
                                # If text_val is still empty and ref_key is present, use humanized key as fallback
                                if not text_val and ref_key:
                                    text_val = f"[{ref_key.split('.')[-1].replace('_', ' ').title()} (Missing)]"
                                
                                # Format output
                                part_title = part_key.title()
                                tone_str = f" (Tone {tone})" if tone else ""
                                
                                if part_key == "prokeimenon":
                                    output_lines.append(f'<p><strong>Prokeimenon</strong>{tone_str}: {text_val}</p>')
                                elif part_key == "alleluia":
                                    output_lines.append(f'<p><strong>Alleluia</strong>{tone_str}: {text_val}</p>')
                                else:
                                    # Epistle or Gospel
                                    clean_title = ref_key.split(".")[-1].replace("_", " ").title() if ref_key else part_title
                                    output_lines.append(f'<p><strong>{part_title}</strong> ({clean_title}): {text_val}</p>')
                except Exception as e:
                    output_lines.append(f'<p class="rubric">[Logic Error: resolve_liturgy_readings - {e}]</p>')
                    
            elif "kontakion" in str(slot_id):
                # Call resolve_hours_kontakion
                hour_num = content.get("hour")
                if not hour_num and slot_id and "hour_" in str(slot_id):
                    parts = str(slot_id).split("_")
                    if len(parts) >= 2:
                        try:
                            hour_num = int(parts[1])
                        except ValueError:
                            pass
                if not hour_num:
                    hour_num = 1
                enriched["hour"] = hour_num
                try:
                    res = self.resolve_hours_kontakion(enriched, rubrics)
                    if res:
                        source = res.get("source", "saint_or_feast")
                        # Look up target key based on source
                        ref_key = None
                        if source == "feast":
                            ref_key = f"menaion.{month}{day}.vespers.kontakion"
                        elif source == "saints":
                            s_id = "saint"
                            if enriched.get("saints"):
                                s_id = enriched["saints"][0].get("id", "saint")
                            ref_key = f"menaion.{s_id}.matins.kontakion"
                            
                        text_val = None
                        if ref_key:
                            text_item = self.get_text(ref_key, context=context)
                            if text_item:
                                text_val = text_item.get("content")
                                
                        if not text_val:
                            # generic text
                            text_val = f"Kontakion of the {source.title()}"
                            
                        output_lines.append(f'<p><strong>Kontakion</strong>: {text_val}</p>')
                except Exception as e:
                    output_lines.append(f'<p class="rubric">[Logic Error: resolve_hours_kontakion - {e}]</p>')

        elif slot_type == "conditional_block":
            logic_data = content.get("logic", {})
            func_name = logic_data.get("function")
            if func_name and hasattr(self, func_name):
                try:
                    func = getattr(self, func_name)
                    import inspect
                    sig = inspect.signature(func)
                    
                    enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
                    enriched["overrides"] = rubrics.get("overrides", {})
                    
                    call_kwargs = {}
                    args_data = logic_data.get("args", {})
                    if isinstance(args_data, dict):
                        for k, v in args_data.items():
                            if k in sig.parameters:
                                call_kwargs[k] = v
                                
                    if "rubrics" in sig.parameters:
                        call_kwargs["rubrics"] = rubrics
                    
                    params = list(sig.parameters.values())
                    has_context = len(params) > 0
                    
                    result = func(enriched, **call_kwargs) if has_context else func()
                    
                    sub_slot = content.get("true_content") if result else content.get("false_content")
                    if sub_slot:
                        sub_type = sub_slot.get("type")
                        if sub_type == "structure_ref":
                            target_file = sub_slot.get("file")
                            target_id = sub_slot.get("root_id")
                            if target_file and target_id:
                                full_path = os.path.join(self.json_db, target_file)
                                if not os.path.exists(full_path):
                                    full_path = target_file
                                if os.path.exists(full_path):
                                    with open(full_path, 'r', encoding='utf-8') as f:
                                        linked_data = json.load(f)
                                    sub_seq = self._get_structure_sequence(linked_data, target_id)
                                    if sub_seq:
                                        for seq_slot in sub_seq:
                                            txt = self._resolve_slot(seq_slot, rubrics, context)
                                            if txt and txt.strip():
                                                output_lines.append(txt)
                        else:
                            txt = self._resolve_slot(sub_slot, rubrics, context)
                            if txt and txt.strip():
                                output_lines.append(txt)
                except Exception as e:
                    output_lines.append(f'<p class="rubric">[Conditional Block Error: {func_name} - {e}]</p>')
            else:
                output_lines.append(f'<p class="rubric">[Missing Conditional Logic: {func_name}]</p>')

        elif slot_type == "sequence":
             for comp in content.get("components", []):
                 txt = self._resolve_slot(comp, rubrics, context)
                 if txt and txt.strip():
                     output_lines.append(txt)
                 
        return "\n\n".join(output_lines)
    def _split_and_wrap(self, html_prefix, content):
        if not content:
            return []
        # Support both string and dictionary structures if they leak into content
        if isinstance(content, dict):
            content = content.get("content", "") or content.get("text", "")
        content_str = str(content)
        lines = [line.strip() for line in content_str.split("\n") if line.strip()]
        if not lines:
            return []
        res = [f'<p>{html_prefix}{lines[0]}</p>']
        for line in lines[1:]:
            res.append(f'<p>{line}</p>')
        return res

    def _hydrate_and_format_logic_result(self, result, func_name, context, rubrics=None):
        if not result:
            return ""
            
        output = []
        
        # Case 1: Result is a canon block
        if isinstance(result, dict) and result.get("type") == "canon_block":
            return self._format_canon_block(result, context)
            
        # Case 2: Result is a dictionary representing a structured chant group (like stichera or aposticha)
        elif isinstance(result, dict) and ("items" in result or "components" in result):
            items = result.get("items") or result.get("components") or []
            
            title = result.get("type", "Stichera").title()
            tone = result.get("tone") or (context.get("tone") if context else None)
            tone_str = f" (Tone {tone})" if tone else ""
            output.append(f'<div class="title-medium">{title}{tone_str}</div>')
            
            for idx, item_key in enumerate(items):
                ref_key = item_key
                if isinstance(item_key, dict):
                    ref_key = item_key.get("id")
                    if not ref_key and "type" in item_key:
                        ref_key = self._resolve_logical_chant_key(item_key, context, rubrics)
                    
                if not ref_key:
                    continue
                    
                # Fetch text
                text_item = self.get_text(ref_key, context=context)
                if text_item:
                    content = text_item.get("content", "")
                    h_title = text_item.get("title") or ref_key.split(".")[-1].replace("_", " ").title()
                    item_label = f"{h_title} {idx+1}" if len(items) > 1 else h_title
                    html_prefix = f"<strong>{item_label}</strong>: "
                    output.extend(self._split_and_wrap(html_prefix, content))
                else:
                    humanized = ref_key.split(".")[-1].replace("_", " ").title()
                    output.append(f'<p class="rubric">[Missing text: {humanized} ({ref_key})]</p>')
                    
            # Handle Glory
            glory_key = result.get("glory")
            if glory_key and glory_key != "(No Saint Doxastikon)":
                text_item = self.get_text(glory_key, context=context)
                if text_item:
                    html_prefix = "<strong>Glory</strong>: "
                    output.extend(self._split_and_wrap(html_prefix, text_item.get("content", "")))
                    
            # Handle Both Now
            both_now_key = result.get("both_now")
            if both_now_key and both_now_key != "None":
                text_item = self.get_text(both_now_key, context=context)
                if text_item:
                    html_prefix = "<strong>Both now</strong>: "
                    output.extend(self._split_and_wrap(html_prefix, text_item.get("content", "")))
                    
            return "\n\n".join(output)
            
        # Case 3: Result is a list of objects (like readings)
        elif isinstance(result, list):
            for res_item in result:
                if isinstance(res_item, dict):
                    ref_key = res_item.get("ref_key", "")
                    content_val = res_item.get("content", "")
                    title = res_item.get("title")
                    
                    if res_item.get("type") == "stichera_block":
                        title = f"Stichera Block ({res_item.get('source', '').capitalize()})"
                        content_val = res_item.get("note", "")
                    
                    if ref_key and (not content_val or not title):
                        text_item = self.get_text(ref_key, context=context)
                        if text_item:
                            if not content_val:
                                content_val = text_item.get("content", "")
                            if not title:
                                title = text_item.get("title") or self._get_humanized_title(text_item, ref_key)
                                
                    title = title or res_item.get("type", "Item").title()
                    
                    source_name = ""
                    if ref_key:
                        text_item = self.get_text(ref_key, context=context)
                        if text_item and text_item.get("source"):
                            source_name = text_item["source"]
                    cit_str = f' <sup class="citation-sup" title="Source: {source_name}">{source_name}</sup>' if source_name else ""
                    
                    output.append(f'<div class="title-medium">{title}{cit_str}</div>')
                    for p_text in content_val.split("\n"):
                        p_text = p_text.strip()
                        if p_text:
                            output.append(f'<p>{p_text}</p>')
                else:
                    output.append(f'<p>{str(res_item)}</p>')
            return "\n\n".join(output)

        # Case 3.5: Result is a readings container (like liturgy_readings)
        elif isinstance(result, dict) and "readings" in result:
            readings_list = result["readings"]
            for r_set in readings_list:
                if isinstance(r_set, dict):
                    # Prokeimenon
                    pk = r_set.get("prokeimenon", {})
                    if pk:
                        ref_key = pk.get("ref_key", "")
                        if ref_key:
                            text_item = self.get_text(ref_key, context=context)
                            if text_item:
                                html_prefix = f'<strong>Prokeimenon</strong> (Tone {text_item.get("tone", pk.get("tone", "?"))}): '
                                output.extend(self._split_and_wrap(html_prefix, text_item.get("content", "")))
                            else:
                                output.append(f'<p class="rubric">[Missing Prokeimenon: {ref_key}]</p>')
                    
                    # Epistle
                    ep = r_set.get("epistle", {})
                    if ep:
                        ref_key = ep.get("ref_key", "")
                        if ref_key:
                            text_item = self.get_text(ref_key, context=context)
                            if text_item:
                                title = text_item.get("title") or ref_key.split(".")[-1].replace("_", " ").title()
                                html_prefix = f'<strong>Epistle</strong> ({title}): '
                                output.extend(self._split_and_wrap(html_prefix, text_item.get("content", "")))
                            else:
                                output.append(f'<p class="rubric">[Missing Epistle: {ref_key}]</p>')
                    
                    # Alleluia
                    al = r_set.get("alleluia", {})
                    if al:
                        ref_key = al.get("ref_key", "")
                        if ref_key:
                            text_item = self.get_text(ref_key, context=context)
                            if text_item:
                                html_prefix = f'<strong>Alleluia</strong> (Tone {text_item.get("tone", al.get("tone", "?"))}): '
                                output.extend(self._split_and_wrap(html_prefix, text_item.get("content", "")))
                            else:
                                output.append(f'<p class="rubric">[Missing Alleluia: {ref_key}]</p>')
                    
                    # Gospel
                    gs = r_set.get("gospel", {})
                    if gs:
                        ref_key = gs.get("ref_key", "")
                        if ref_key:
                            text_item = self.get_text(ref_key, context=context)
                            if text_item:
                                title = text_item.get("title") or ref_key.split(".")[-1].replace("_", " ").title()
                                html_prefix = f'<strong>Gospel</strong> ({title}): '
                                output.extend(self._split_and_wrap(html_prefix, text_item.get("content", "")))
                            else:
                                output.append(f'<p class="rubric">[Missing Gospel: {ref_key}]</p>')
                else:
                    output.append(f'<p>{str(r_set)}</p>')
            return "\n\n".join(output)
            
        # Case 4: Result has 'sequence' or 'troparia_sequence' (like troparia/kontakia stacking)
        elif isinstance(result, dict) and ("sequence" in result or "troparia_sequence" in result):
            tone = result.get('tone', '?')
            tone_str = f" (Tone {tone})" if tone != '?' else ""
            output.append(f'<div class="title-medium">Troparia & Kontakia{tone_str}</div>')
            
            seq_items = result.get("sequence") or result.get("troparia_sequence") or []
            kontakion_winner = result.get("kontakion_winner")
            
            for item in seq_items:
                content_key = item.get("content") or item.get("target") or item.get("id")
                if content_key:
                    text_item = self.get_text(content_key, context=context)
                    if text_item:
                        title = text_item.get('title') or content_key.split(".")[-1].replace("_", " ").title()
                        html_prefix = f'<strong>{title}</strong>: '
                        output.extend(self._split_and_wrap(html_prefix, text_item.get("content", "")))
                    else:
                        humanized = content_key.split(".")[-1].replace("_", " ").title()
                        output.append(f'<p class="rubric">[Missing text: {humanized} ({content_key})]</p>')
                        
            if kontakion_winner:
                text_item = self.get_text(kontakion_winner, context=context)
                if text_item:
                    title = text_item.get('title') or kontakion_winner.split(".")[-1].replace("_", " ").title()
                    html_prefix = f'<strong>{title}</strong>: '
                    output.extend(self._split_and_wrap(html_prefix, text_item.get("content", "")))
                else:
                    humanized = kontakion_winner.split(".")[-1].replace("_", " ").title()
                    output.append(f'<p class="rubric">[Missing text: {humanized} ({kontakion_winner})]</p>')
            return "\n\n".join(output)

        # Case 4.1: Result is Litiya content structure
        elif isinstance(result, dict) and result.get("prayer") == "horologion.litiya_prayer":
            output.append('<div class="title-large">Litiya</div>')
            
            # Format stichera
            stichera_groups = result.get("stichera", [])
            for group in stichera_groups:
                menaion_key = context.get("menaion_key", "")
                target_key = f"{menaion_key}.vespers.litiya" if menaion_key else "litiya_menaion"
                
                text_item = self.get_text(target_key, context=context)
                if text_item:
                    html_prefix = "<strong>Litiya Stichera</strong>: "
                    output.extend(self._split_and_wrap(html_prefix, text_item.get("content", "")))
                else:
                    output.append(f'<p class="rubric">[Missing Litiya Stichera: {target_key}]</p>')
            
            # Format Glory / Both Now
            glory = result.get("glory")
            both_now = result.get("both_now")
            if glory:
                if "glory" in glory:
                    menaion_key = context.get("menaion_key", "")
                    glory_key = f"{menaion_key}.vespers.doxastichon_litiya" if menaion_key else glory
                else:
                    glory_key = glory
                
                text_item = self.get_text(glory_key, context=context)
                if text_item:
                    html_prefix = "<strong>Glory</strong>: "
                    output.extend(self._split_and_wrap(html_prefix, text_item.get("content", "")))
            
            if both_now:
                if "both_now" in both_now:
                    menaion_key = context.get("menaion_key", "")
                    both_now_key = f"{menaion_key}.vespers.theotokion_litiya" if menaion_key else both_now
                else:
                    both_now_key = both_now
                
                text_item = self.get_text(both_now_key, context=context)
                if text_item:
                    html_prefix = "<strong>Both now</strong>: "
                    output.extend(self._split_and_wrap(html_prefix, text_item.get("content", "")))
            
            # Format Litiya Prayer
            prayer_key = result.get("prayer", "horologion.litiya_prayer")
            text_item = self.get_text(prayer_key, context=context)
            if text_item:
                title = text_item.get("title", "Litiya Prayers")
                output.append(f'<div class="title-medium">{title}</div>')
                output.extend(self._split_and_wrap("", text_item.get("content", "")))
            else:
                output.append(f'<p class="rubric">[Missing Litiya Prayers: {prayer_key}]</p>')
                
            return "\n\n".join(output)

        # Case 4.2: Result is Artoklasia content structure
        elif isinstance(result, dict) and result.get("prayer") == "horologion.artoklasia_prayer":
            output.append('<div class="title-large">Blessing of Loaves (Artoklasia)</div>')
            
            # Rubric
            rubric_str = result.get("rubric", "")
            ordo = result.get("ordo_ref", "")
            cit_str = f' <sup class="citation-sup" title="Ordo: {ordo}">{ordo}</sup>' if ordo else ""
            if rubric_str:
                output.append(f'<p class="rubric">{rubric_str}{cit_str}</p>')
                
            # Roles instructions
            roles = result.get("roles", {})
            for role, text in roles.items():
                output.extend(self._split_and_wrap(f'<span class="actor">{role.upper()}</span> ', text))
                
            # Troparia instruction
            troparia_config = result.get("troparia", [])
            for t_item in troparia_config:
                ref = t_item.get("ref_key")
                count = t_item.get("count", 1)
                text_item = self.get_text(ref, context=context)
                if text_item:
                    title = text_item.get("title") or ref.split(".")[-1].replace("_", " ").title()
                    html_prefix = f"<strong>{title} (x{count})</strong>: "
                    output.extend(self._split_and_wrap(html_prefix, text_item.get('content', '')))
                else:
                    title = ref.split(".")[-1].replace("_", " ").title()
                    output.append(f'<p class="rubric"><strong>{title} (x{count})</strong>: [Missing: {ref}]</p>')
            
            if not troparia_config and "troparion" in result:
                t_item = result["troparion"]
                ref = t_item.get("key")
                count = t_item.get("count", 1)
                text_item = self.get_text(ref, context=context)
                if text_item:
                    title = text_item.get("title") or ref.split(".")[-1].replace("_", " ").title()
                    html_prefix = f"<strong>{title} (x{count})</strong>: "
                    output.extend(self._split_and_wrap(html_prefix, text_item.get('content', '')))
            
            # Artoklasia Prayer
            prayer_key = result.get("prayer")
            text_item = self.get_text(prayer_key, context=context)
            if text_item:
                title = text_item.get("title", "Artoklasia Prayer")
                output.append(f'<div class="title-medium">{title}</div>')
                output.extend(self._split_and_wrap("", text_item.get("content", "")))
            else:
                output.append(f'<p class="rubric">[Missing Artoklasia Prayer: {prayer_key}]</p>')
                
            return "\n\n".join(output)

        # Case 4.3: Result is a Psalms / Kathisma / Polyeleos block
        elif isinstance(result, dict) and result.get("type") in ("psalms", "kathisma", "polyeleos"):
            k_id = result.get("id", "")
            if result.get("type") == "polyeleos":
                k_id = "horologion.polyeleos"
            k_num = result.get("kathisma_number", k_id.split("_")[-1] if "_" in k_id else "")
            title = f"Kathisma {k_num}" if k_num else "Kathisma"
            
            text_item = self.get_text(k_id, context=context) or self.get_text(f"horologion.{k_id}", context=context)
            content_val = ""
            if text_item and not text_item.get("is_missing"):
                title = text_item.get("title") or title
                content_val = text_item.get("content", "")
            else:
                content_val = f"[Read Kathisma {k_num} from the Psalter]" if k_num else f"[Read {k_id.replace('_', ' ').title()} from the Psalter]"
                
            output.append(f'<div class="title-medium">{title}</div>')
            if content_val:
                for p_text in content_val.split("\n"):
                    p_text = p_text.strip()
                    if p_text:
                        output.append(f'<p>{p_text}</p>')
            return "\n\n".join(output)

        # Case 4.4: Result is a Sessional Hymn / group
        elif isinstance(result, dict) and result.get("type") in ("sessional", "sessional_group"):
            s_id = result.get("id", "")
            title = "Sessional Hymns"
            
            text_item = self.get_text(s_id, context=context) or self.get_text(f"horologion.{s_id}", context=context)
            content_val = ""
            if text_item and not text_item.get("is_missing"):
                title = text_item.get("title") or title
                content_val = text_item.get("content", "")
            else:
                humanized = s_id.replace("_", " ").title()
                content_val = f"[Sessional Hymns: {humanized}]"
                
            output.append(f'<div class="title-medium">{title}</div>')
            if content_val:
                for p_text in content_val.split("\n"):
                    p_text = p_text.strip()
                    if p_text:
                        output.append(f'<p>{p_text}</p>')
            return "\n\n".join(output)

        # Case 4.5: Result is a Fixed Reference block
        elif isinstance(result, dict) and result.get("type") == "fixed_ref":
            ref_key = result.get("ref_key")
            item = self.get_text(ref_key, context=context)
            if item:
                title = self._get_humanized_title(item, ref_key)
                text_val = item.get("content", "")
                cit_html = ""
                if "source" in item:
                    cit_html = f' <sup class="citation-sup" title="Source: {item["source"]}">{item["source"]}</sup>'
                output.append(f'<div class="title-medium">{title}{cit_html}</div>')
                for p_text in text_val.split("\n"):
                    p_text = p_text.strip()
                    if p_text:
                        output.append(f'<p>{p_text}</p>')
            else:
                humanized = ref_key.split(".")[-1].replace("_", " ").title()
                output.append(f'<p class="rubric">[Missing text: {humanized} ({ref_key})]</p>')
            return "\n\n".join(output)

        # Case 4.6: Result is a Prayer block
        elif isinstance(result, dict) and result.get("type") == "prayer":
            ref_key = result.get("ref_key")
            item = self.get_text(ref_key, context=context)
            if item:
                title = self._get_humanized_title(item, ref_key)
                text_val = item.get("content", "")
                output.append(f'<div class="title-medium">{title}</div>')
                for p_text in text_val.split("\n"):
                    p_text = p_text.strip()
                    if p_text:
                        output.append(f'<p>{p_text}</p>')
            else:
                humanized = ref_key.split(".")[-1].replace("_", " ").title()
                output.append(f'<p class="rubric">[Missing prayer: {humanized} ({ref_key})]</p>')
            return "\n\n".join(output)

        # Case 4.7: Result is a Daily Prokeimenon
        elif isinstance(result, dict) and result.get("type") == "daily_prokeimenon":
            tone = result.get("tone")
            text = result.get("text", "")
            verse = result.get("verse", "")
            output.append(f'<div class="title-medium">Daily Prokeimenon (Tone {tone})</div>')
            output.append(f'<p>{text}</p>')
            if verse:
                output.append(f'<p><span class="rubric">Verse:</span> {verse}</p>')
            return "\n\n".join(output)

        # Case 4.8: Result is a Canon descriptor
        elif isinstance(result, dict) and result.get("type") == "canon":
            subject = result.get("subject", "").capitalize()
            book = result.get("book", "").capitalize()
            output.append(f'<p class="rubric">[Canon to the {subject} ({book})]</p>')
            return "\n\n".join(output)

        # Case 4.9: Result is a Weekday Dismissal Theotokion / Stavrotheotokion
        elif isinstance(result, dict) and result.get("type") in ("weekday_dismissal_theotokion", "weekday_dismissal_stavrotheotokion"):
            ref_key = result.get("ref_key")
            item = self.get_text(ref_key, context=context)
            if item:
                title = item.get("title") or "Theotokion"
                text_val = item.get("content", "")
                output.append(f'<div class="title-medium">{title}</div>')
                for p_text in text_val.split("\n"):
                    p_text = p_text.strip()
                    if p_text:
                        output.append(f'<p>{p_text}</p>')
            else:
                humanized = ref_key.split(".")[-1].replace("_", " ").title()
                output.append(f'<p class="rubric">[Missing Theotokion: {humanized} ({ref_key})]</p>')
            return "\n\n".join(output)

        # Case 4.10: Result is a Standard structured text
        elif isinstance(result, dict) and result.get("type") == "standard":
            ref_key = result.get("ref_key", "")
            text = result.get("text", "")
            title = result.get("title", ref_key.split(".")[-1].replace("_", " ").title() if ref_key else "Prayer")
            output.append(f'<div class="title-medium">{title}</div>')
            for p_text in text.split("\n"):
                p_text = p_text.strip()
                if p_text:
                    output.append(f'<p>{p_text}</p>')
            return "\n\n".join(output)

        # Case 4.11: Result is a dynamic Generator block
        elif isinstance(result, dict) and result.get("type") == "generator":
            method = result.get("generator_method")
            args = result.get("args", {})
            if method == "generate_antiphons":
                res = self.resolve_liturgy_antiphons(context, rubrics)
                return self._hydrate_and_format_logic_result(res, "resolve_liturgy_antiphons", context, rubrics)
            elif method == "generate_hour_troparia":
                hour_num = args.get("hour", 1)
                res = self.resolve_hours_collision(context, hour_num=hour_num)
                return self._hydrate_and_format_logic_result(res, "resolve_hours_collision", context, rubrics)
            return f'<p class="rubric">[Generator: {method} ({str(args)})]</p>'

        # Case 4.12: Result has troparia/kontakia lists
        elif isinstance(result, dict) and ("troparia" in result or "kontakia" in result):
            troparia = result.get("troparia", [])
            for item in troparia:
                t_id = item.get("troparion_id") or item.get("id") or item.get("ref_key")
                tone = item.get("tone", "")
                tone_str = f" (Tone {tone})" if tone else ""
                if t_id:
                    text_item = self.get_text(t_id, context=context)
                    if text_item:
                        title = text_item.get("title") or t_id.split(".")[-1].replace("_", " ").title()
                        html_prefix = f'<strong>{title}{tone_str}</strong>: '
                        output.extend(self._split_and_wrap(html_prefix, text_item.get("content", "")))
                    else:
                        humanized = t_id.split(".")[-1].replace("_", " ").title()
                        output.append(f'<p class="rubric">[Missing Troparion: {humanized} ({t_id})]</p>')
                        
            kontakia = result.get("kontakia", [])
            for item in kontakia:
                k_id = item.get("kontakion_id") or item.get("id") or item.get("ref_key")
                tone = item.get("tone", "")
                tone_str = f" (Tone {tone})" if tone else ""
                if k_id:
                    text_item = self.get_text(k_id, context=context)
                    if text_item:
                        title = text_item.get("title") or k_id.split(".")[-1].replace("_", " ").title()
                        html_prefix = f'<strong>{title}{tone_str}</strong>: '
                        output.extend(self._split_and_wrap(html_prefix, text_item.get("content", "")))
                    else:
                        humanized = k_id.split(".")[-1].replace("_", " ").title()
                        output.append(f'<p class="rubric">[Missing Kontakion: {humanized} ({k_id})]</p>')
            return "\n\n".join(output)

        # Case 4.13: Result is a Communion Hymn dict
        elif isinstance(result, dict) and result.get("type") == "communion_hymn":
            text = result.get("text") or ""
            ref_key = result.get("ref_key")
            source_name = ""
            if ref_key:
                text_item = self.get_text(ref_key, context=context)
                if text_item and text_item.get("source"):
                    source_name = text_item["source"]
            cit_str = f' <sup class="citation-sup" title="Source: {source_name}">{source_name}</sup>' if source_name else ""
            html_prefix = f"<strong>Communion Hymn</strong>{cit_str}: "
            output.extend(self._split_and_wrap(html_prefix, text))
            return "\n\n".join(output)

        # Case 4.14: Result is a Post-Communion Hymn dict
        elif isinstance(result, dict) and result.get("type") == "post_communion":
            hymn = result.get("hymn") or ""
            ref_key = result.get("ref_key")
            source_name = ""
            if ref_key:
                text_item = self.get_text(ref_key, context=context)
                if text_item and text_item.get("source"):
                    source_name = text_item["source"]
            cit_str = f' <sup class="citation-sup" title="Source: {source_name}">{source_name}</sup>' if source_name else ""
            html_prefix = f"<strong>Post-Communion Hymn</strong>{cit_str}: "
            output.extend(self._split_and_wrap(html_prefix, hymn))
            return "\n\n".join(output)

        # Case 5: Result has 'vestments' (ceremonial vesting set)
        elif isinstance(result, dict) and "vestments" in result:
            v_list = result.get("vestments", [])
            note = result.get("note", "")
            ordo = result.get("ordo_ref", "")
            roles_str = ", ".join(v.capitalize() for v in v_list)
            cit_str = f' <sup class="citation-sup" title="Ordo: {ordo}">{ordo}</sup>' if ordo else ""
            output.append(f'<span class="rubric">VESTMENT SET: Vests in {roles_str}. {note}{cit_str}</span>')
            return "\n\n".join(output)
            
        # Case 6: Standard dictionary with 'content' (like fasting rule)
        elif isinstance(result, dict) and "content" in result:
            output.append(f'<p>{result["content"]}</p>')
            return "\n\n".join(output)
            
        # Case 7: Standard dictionary with 'note' (like fasting rule or clergy variant)
        elif isinstance(result, dict) and "note" in result:
            output.append(f'<p>{result["note"]}</p>')
            return "\n\n".join(output)
            
        # Case 8: Simple string or fallback
        else:
            res_str = str(result)
            if not res_str.startswith("<"):
                return f'<p>{res_str}</p>'
            return res_str

    def _format_canon_block(self, result, context):
        output = []
        output.append('<div class="title-large">The Canon</div>')
        
        dist_str = ", ".join(f"{d.get('source','').capitalize()} ({d.get('qty',0)})" for d in result.get("distribution", []))
        output.append(f'<p class="rubric">Structure: {dist_str} | Total: {result.get("total_count", 0)} Odes</p>')
        
        for o in result.get("odes", []):
            if "ode" in o:
                num = o["ode"]
                output.append(f'<div class="title-medium">Ode {num}</div>')
                
                for d in o.get("distribution", []):
                    source = d.get("source")
                    qty = d.get("qty", 0)
                    is_irmos = d.get("irmos", False)
                    
                    tone = context.get("tone", 1) if context else 1
                    s_id = "saint"
                    if context and context.get("saints"):
                        s_id = context["saints"][0].get("id", "saint")
                        
                    if is_irmos:
                        irmos_key = f"octoechos.tone_{tone}.canon.ode_{num}.irmos" if source == "octoechos" else f"menaion.{s_id}.canon.ode_{num}.irmos"
                        irmos_item = self.get_text(irmos_key, context=context)
                        if irmos_item and not irmos_item.get("is_missing"):
                            output.append(f'<p><strong>(Irmos)</strong> {irmos_item.get("content")}</p>')
                        else:
                            output.append(f'<p class="rubric"><strong>(Irmos - Tone {tone})</strong> [Sing Irmos of {source.capitalize()} Ode {num}]</p>')
                            
                    troparia_key = f"octoechos.tone_{tone}.canon.ode_{num}.troparia" if source == "octoechos" else f"menaion.{s_id}.canon.ode_{num}.troparia"
                    troparia_item = self.get_text(troparia_key, context=context)
                    if troparia_item and not troparia_item.get("is_missing"):
                        output.append(f'<p>{troparia_item.get("content")}</p>')
                    else:
                        output.append(f'<p class="rubric">[Troparia of {source.capitalize()} ({qty}x) - Tone {tone}]</p>')
            else:
                i_type = o.get("type", "")
                if i_type == "kathisma":
                    output.append('<div class="title-medium">Sessional Hymns (Kathisma)</div>')
                    for item in o.get("components", []):
                        ref_key = item.get("id")
                        text_item = self.get_text(ref_key, context=context)
                        if text_item and not text_item.get("is_missing"):
                            title = self._get_humanized_title(text_item, ref_key)
                            output.append(f'<p><strong>{title}</strong>: {text_item.get("content")}</p>')
                        else:
                            output.append(f'<p class="rubric">[Sessional Hymn ({ref_key})]</p>')
                elif i_type == "kontakion":
                    output.append('<div class="title-medium">Kontakion & Ikos</div>')
                    for item in o.get("components", []):
                        ref_key = item.get("id")
                        text_item = self.get_text(ref_key, context=context)
                        if text_item and not text_item.get("is_missing"):
                            title = self._get_humanized_title(text_item, ref_key)
                            output.append(f'<p><strong>{title}</strong>: {text_item.get("content")}</p>')
                        else:
                            output.append(f'<p class="rubric">[Kontakion/Ikos ({ref_key})]</p>')
                            
        return "\n\n".join(output)

    def _extract_logic_metadata(self, func_name):
        """
        Extracts citations and logic descriptions from function docstrings.
        """
        if not hasattr(self, func_name):
            return {"citation": "Unknown", "description": "No documentation"}
            
        func = getattr(self, func_name)
        doc = func.__doc__
        if not doc:
            return {"citation": "None", "description": "No docstring provided"}
            
        lines = [l.strip() for l in doc.split('\n') if l.strip()]
        
        citation = "Internal Logic"
        description = lines[0] if lines else "Logic Handler"
        
        for line in lines:
            lower_line = line.lower()
            if "citation:" in lower_line or "ref:" in lower_line or "source:" in lower_line:
                citation = line.replace("Citation:", "").replace("Ref:", "").replace("Source:", "").replace("Logic Source:", "").strip()
                break
                
        return {"citation": citation, "description": description}


    def _explain_logic_decision(self, func_name, context, result):
        """
        Generates a human-readable explanation for WHY a result was chosen.
        """
        explanation = "Standard execution path."
        
        # 1. Midnight Office Mode
        if func_name == "resolve_midnight_office_mode":
            day = context.get("day_of_week")
            if day == 0: explanation = "Day is Sunday (0), so Triadic Canon replaces Ps 118."
            elif day == 6: explanation = "Day is Saturday (6), so Kathisma 9 replaces Ps 118."
            else: explanation = "Weekday (Mon-Fri), standard Ps 118."
            
        # 2. Lenten Triodic Canon
        elif func_name == "resolve_lenten_triodic_canon":
            day = context.get("day_of_week")
            explanation = f"Day is {day}. Triodic Odes for this day trigger specific Menaion/Triodion balance."

        # 3. Prokeimenon
        elif func_name == "resolve_prokeimenon":
            rank = self.calculate_rank(context)
            if rank == 1: explanation = f"Great Feast (Rank 1): '{context.get('menaion_rank', 'feast')}' overrides everything."
            elif context.get("day_of_week") == 0: explanation = "Sunday Resurrectional Cycle (Eothinon)."
            else: explanation = "Weekday cycle."
            
        # 4. Vespers Stichera
        elif func_name == "resolve_vespers_stichera":
            rank = self.calculate_rank(context)
            day = context.get("day_of_week")
            if rank == 1: explanation = f"Great Feast (Rank 1): Festal stichera from Menaion."
            elif day == 0 or rank <= 2: explanation = "Sunday/Vigil: 10 Stichera (Resurrection priority)."
            else: explanation = f"Weekday (Rank {rank}): Standard distribution."

        # 5. Aposticha
        elif func_name == "resolve_aposticha":
            day = context.get("day_of_week")
            if day == 0: explanation = "Sunday: Resurrectional Aposticha (Octoechos)."
            else: explanation = "Weekday: Standard Aposticha from Octoechos."

        # 6. Troparia (Vespers/Matins general)
        elif "troparia" in func_name and "hour" not in func_name:
            if isinstance(result, dict) and result.get("gradual_type") == "alleluia":
                 explanation = "Lenten/Aliturgical: Alleluia replaces God is the Lord."
            else:
                day = context.get("day_of_week")
                is_sunday = day == 0 or context.get("is_sunday_vigil")
                if is_sunday: explanation = "Sunday: Resurrectional Troparion + Theotokion."
                else: explanation = "Weekday: Troparion of the Day/Saint."

        # 7. Hours Troparia
        elif func_name == "generate_hour_troparia" or func_name == "resolve_hours_collision":
            paradigm = context.get("paradigm", "weekday")
            is_sunday = "sunday" in paradigm or context.get("day_of_week") == 0 or context.get("is_sunday_vigil")
            if is_sunday:
                 explanation = "Sunday: Resurrectional Troparion takes precedence at all Hours."
            else:
                 explanation = "Weekday: Saint Troparion (if present) or Day Troparion."

        # 8. Kathisma
        elif func_name == "resolve_kathisma":
            # Kathisma logic is complex (Psalter cycle)
            day = context.get("day_of_week")
            num = context.get("kathisma_session_id", "?") # Not passed effectively, usually args
            explanation = f"Psalter Cycle for Day {day}: Standard rotation."

        # 9. Liturgy Antiphons
        elif func_name == "resolve_liturgy_antiphons":
            paradigm = context.get("paradigm", "")
            if paradigm == "p_feast_lord": explanation = "Great Feast: Festal Antiphons (Psalms 91, 92, 94 etc)."
            elif context.get("day_of_week") == 0: explanation = "Sunday: Typical Psalms (102, 145) + Beatitudes."
            else: explanation = "Weekday: Appointed Antiphons or Typical Psalms."

        # 10. Liturgy Hymns (Entrance)
        elif func_name == "resolve_liturgy_hymns":
            explanation = "Temple Priority Logic: Sunday + Temple + Saint (Standard Order)."

        return explanation


    def _resolve_logical_chant_key(self, item_key, context, rubrics=None):
        if not isinstance(item_key, dict):
            return item_key
            
        c_type = item_key.get("type")
        source = item_key.get("source")
        
        # Check if id is explicitly provided
        if item_key.get("id"):
            return item_key["id"]
        if item_key.get("ref_key"):
            return item_key["ref_key"]
            
        # Get date details from context
        dt = context.get("date")
        if isinstance(dt, str):
            parts = dt.split("-")
            month = parts[1]
            day = parts[2]
        elif hasattr(dt, "month") and hasattr(dt, "day"):
            month = f"{dt.month:02d}"
            day = f"{dt.day:02d}"
        else:
            month = context.get("month", "01")
            day = context.get("day", "01")
            
        menaion_key = f"menaion.{month}{day}"
        tone = context.get("tone", 1)
        
        if c_type == "glory" or source == "glory":
            return "horologion.glory"
        if c_type == "both_now" or source == "both_now":
            return "horologion.both_now"
        if c_type == "glory_both_now" or source == "glory_both_now":
            return "horologion.glory_both_now"
            
        if source == "feast":
            if c_type == "troparion":
                return f"{menaion_key}.vespers.troparion"
            elif c_type == "kontakion":
                return f"{menaion_key}.vespers.kontakion"
        elif source == "menaion_saint":
            if month == "01" and day == "01":
                if c_type == "troparion":
                    return f"{menaion_key}.vespers.troparion_basil"
                elif c_type == "kontakion":
                    return f"{menaion_key}.matins.kontakion_basil"
            else:
                if c_type == "troparion":
                    return f"{menaion_key}.vespers.troparion"
                elif c_type == "kontakion":
                    return f"{menaion_key}.vespers.kontakion"
        elif source == "resurrection":
            if c_type == "troparion":
                return f"tone_{tone}.troparion.resurrection"
            elif c_type == "kontakion":
                return f"tone_{tone}.kontakion.resurrection"
        elif source == "temple":
            return f"general.temple.{c_type}"
        elif source == "cross":
            return f"weekday.wednesday.{c_type}"
            
        return f"{c_type}_{source}"
