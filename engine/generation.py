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
                components.append(f"St. {s_name}")
        
        if len(components) <= 1:
            return {"header": components[0] if components else "Service", "components": components}
        
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
             
             # Fallback logic
             rank = context.get("rank", 5)
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
                  if ctype == "paschal_hours": return "Paschal Hours (Compline)"
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
             return "Midnight Office (Daily)"

        # 4. Matins
        if base_name == "Matins":
             if context.get("triodion_period") == "holy_friday": return "Matins of Holy Saturday (Jerusalem Matins)"
             if context.get("triodion_period") == "holy_thursday": return "Matins of Holy Friday (12 Gospels)"
             
             is_lent = context.get("season") == "lent"
             day = context.get("day_of_week")
             rank = context.get("rank", 5)
             
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
             
             is_lent = context.get("season") == "lent"
             day = context.get("day_of_week")
             rank = context.get("rank", 5)
             
             if is_lent and day in [3, 5] and rank > 3: return "Liturgy of the Presanctified Gifts"
             
             if is_lent and day == 0: return "Divine Liturgy of St. Basil the Great"
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
                    if "logic_args" in override:
                        if "content" in sequence[idx] and "logic" in sequence[idx]["content"]:
                             # Safe merge args
                             if "args" not in sequence[idx]["content"]["logic"]: sequence[idx]["content"]["logic"]["args"] = {}
                             sequence[idx]["content"]["logic"]["args"].update(override["logic_args"])
            
            return sequence
        else:
            return copy.deepcopy(structure_def.get("sequence", []))


    def generate_full_booklet(self, context, rubrics):

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

                booklet.append(f"\n--- {service_name.upper()} ({root_id}) ---")

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
                                             booklet.append(f"[{slot.get('id','LINK')}] >>> EXPANDING LINK: {target_id} <<<")
                                             process_sequence(sub_seq, depth + 1)
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
                        booklet.append(f"[{slot_id}] {text}")

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


    def generate_typikon_digest(self, context, rubrics):
        return TypikonDigestGenerator(self).generate(context, rubrics)


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
                                   digest.append(f"At 'Lord, I have cried': {total} stichera")
                                   for item in res.get("distribution", []):
                                        c = item.get('count', item.get('qty', '?'))
                                        s = item.get('source', item.get('type', '')).upper()
                                        digest.append(f"- {c} from {s}")
                                   if "glory" in res: digest.append(f"Glory... {res['glory']}")
                                   if "both_now" in res: digest.append(f"Both Now... {res['both_now']}")
                              except:
                                   digest.append("At 'Lord, I have cried': (Logic Error)")

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


    def _resolve_slot(self, slot, rubrics, context=None):
        # ... (This logic is stable, no changes needed)
        output_lines = []
        if "rubric" in slot:
            r = slot["rubric"];
            if isinstance(r, dict):
                output_lines.append(f"\n   >>> RUBRIC: {r.get('title', '')} <<<")
                if "source_ref" in r: output_lines.append(f"   (Source): {r['source_ref']}")
                if "ordo_ref" in r: output_lines.append(f"   (Ordo): {r['ordo_ref']}")
                if "roles" in r:
                    for role, text in r['roles'].items(): output_lines.append(f"   [{role.upper()}]: {text}")
                output_lines.append("")
            else:
                output_lines.append(f"   RUBRIC: {r}")
        
        content = slot.get("content", {});
        slot_type = content.get("type")
        
        if slot_type == "fixed_ref":
            ref_key = content.get('ref_key')
            if ref_key in self.text_db:
                # Found in Text DB - Return full text
                text_block = self.text_db[ref_key]
                output_lines.append(f"   >>> {text_block.get('title', ref_key)} <<<")
                content_val = text_block.get('content', '')
                if isinstance(content_val, dict):
                     output_lines.append(json.dumps(content_val, indent=2))
                else:
                     output_lines.append(str(content_val))
            else:
                # Fallback
                output_lines.append(f"   {ref_key}")
        elif slot_type == "fixed_group":
            output_lines.append(f"   Group: {', '.join(content.get('ref_keys', []))}")
        elif slot_type == "variable_logic":
            logic = content.get("logic", {})
            func_name = logic.get("function")
            
            if hasattr(self, func_name):
                try:
                    # Execute Logic
                    func = getattr(self, func_name)
                    # Many logic functions require context. 
                    if context:
                        result = func(context, rubrics) if func.__code__.co_argcount > 2 else func(context)
                    else:
                        # Fallback for when context isn't passed (legacy calls)
                        result = f"[PENDING EXECUTION: {func_name}]"

                    if isinstance(result, list):
                        output_lines.append(f"   >>> LOGIC RESULT: {func_name} <<<")
                        for item in result:
                            # Handle different result types (strings vs objects)
                            if isinstance(item, dict):
                                output_lines.append(f"      - {item.get('title', item.get('id', 'Unknown'))}")
                            else:
                                output_lines.append(f"      - {item}")
                    elif isinstance(result, dict):
                         output_lines.append(f"   >>> LOGIC RESULT: {func_name} <<<")
                         output_lines.append(f"      {result.get('title', 'Result Object')}")
                    else:
                        output_lines.append(f"   >>> LOGIC RESULT: {func_name} <<<")
                        output_lines.append(f"      {result}")
                        
                except Exception as e:
                     output_lines.append(f"   [LOGIC ERROR]: {func_name} - {e}")
            else:
                 output_lines.append(f"   [MISSING LOGIC]: {func_name}")
        elif slot_type == "sequence":
             output_lines.append("   Sequence:")
             for comp in content.get("components", []):
                    output_lines.append(f"      - {comp}")
                    
        return "\n".join(output_lines)


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
