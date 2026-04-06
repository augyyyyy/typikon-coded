import json
import os
from datetime import datetime, timedelta

class TypikonDigestGenerator:
    def __init__(self, engine):
        self.engine = engine

    def generate(self, context, rubrics):
        """
        Generates a 'Typikon Style' digest (instructions only, no full text).
        Uses a 'Calendar Sandwich' model for Civil-Liturgical alignment:
        1. Vespers & Compline of the Date (served previous evening)
           EXCEPTION: On Lenten weekdays Vespers closes the *current* day (after the 9th Hour)
        2. Midnight Office, Matins, Hours of the Date (morning/daytime)
        3. Vespers position depends on period (see _build_service_order)
        4. Evening: Great Compline (Lenten weekdays) or Presanctified/Liturgy
        """
        digest = [f"# TYPIKON: {context['date']}"]
        digest.append(f"**Logic:** {rubrics['title']}\n")

        # Instance Data Table
        digest.append("## 2026 Instance Data")
        digest.append("| Variable | Value |")
        digest.append("|---|---|")
        digest.append(f"| Civil Date | {context.get('date', '')} |")
        season_str = context.get('season', '')
        if context.get('triodion_period'):
             season_str += f" ({context['triodion_period']})"
        digest.append(f"| Season / Period | {season_str} |")
        digest.append(f"| Octoechos Tone | {context.get('tone', '')} |")
        digest.append(f"| Rank | {context.get('rank', '')} |")
        if "saints" in context:
             saints_str = ", ".join(s.get("name", s.get("id", "")) for s in context["saints"])
             digest.append(f"| Saints | {saints_str} |")
        digest.append("")

        # A. Late Service Calculation (needed early to handle morning suppression)
        late_service = context.get("late_service_type")
        is_lenten_weekday = self._is_lenten_weekday(context)
        is_presanctified = (late_service == "presanctified_vespers")
        is_vesperal = (rubrics.get("overrides", {}).get("liturgy_type", "") == "vesperal_merge_logic")

        # Build a lookup dict for services by name
        svc_by_name = {s["name"]: s for s in self.engine.daily_cycle}

        # ------------------------------------------------------------------
        # B. PREVIOUS EVENING (Vespers & Compline)
        # On a standard day, Vespers of the current feast was sung the evening
        # before this civil date. This is the normal Byzantine day-start.
        # EXCEPTION: On Lenten weekdays, Vespers belongs to the CURRENT civil
        # day's midday block (after the 9th Hour), so we skip previous-evening
        # Vespers and instead render a note about the prior evening's services.
        # ------------------------------------------------------------------
        if is_lenten_weekday:
            digest.append("\n--- PREVIOUS EVENING ---")
            digest.append("Great Compline (of the previous day's evening block)")
        else:
            try:
                date_str = context.get("date")
                if isinstance(date_str, str):
                    target_dt = datetime.fromisoformat(date_str).date()
                else:
                    target_dt = date_str

                prev_dt = target_dt - timedelta(days=1)
                context_prev = self.engine.get_liturgical_context(prev_dt)
                rubrics_prev = self.engine.resolve_rubrics(context_prev)

                for service in self.engine.daily_cycle:
                    if service["name"] in ["Vespers", "Compline"]:
                        self._render_service_block(digest, service, context_prev, rubrics_prev)
            except Exception as e:
                digest.append(f"[Error loading Previous Evening context: {e}]")

        # ------------------------------------------------------------------
        # C. MORNING & DAYTIME (Midnight → Matins → Hours)
        # ------------------------------------------------------------------
        morning_services = ["Midnight Office", "Matins",
                            "First Hour", "Third Hour", "Sixth Hour", "Ninth Hour"]
        for name in morning_services:
            if name in svc_by_name:
                self._render_service_block(digest, svc_by_name[name], context, rubrics)

        # ------------------------------------------------------------------
        # D. MIDDAY / VESPERS POSITION
        # Lenten weekday: Vespers is appended here, fused after the 9th Hour.
        # Presanctified day: Vespers is merged into the evening Presanctified.
        # Vesperal Liturgy day: Vespers is fused with the evening Liturgy.
        # Standard day: Liturgy follows the Hours; Vespers was already rendered
        #               in section B (previous evening).
        # ------------------------------------------------------------------
        if is_lenten_weekday:
            # Vespers closes the midday block on Lenten weekdays
            digest.append("\n--- MIDDAY BLOCK: 3rd + 6th + 9th Hours + Typika + Vespers combined ---")
            if "Vespers" in svc_by_name:
                self._render_service_block(digest, svc_by_name["Vespers"], context, rubrics)
            # Evening: Great Compline (not the standard small compline)
            if "Compline" in svc_by_name:
                self._render_service_block(digest, svc_by_name["Compline"], context, rubrics)
        elif is_presanctified:
            # Liturgy slot is skipped; Presanctified rendered separately below
            pass
        elif is_vesperal:
            # Vespers is fused with the Liturgy — render just the Liturgy (which contains Vespers)
            if "Liturgy" in svc_by_name:
                self._render_service_block(digest, svc_by_name["Liturgy"], context, rubrics)
        else:
            # Standard: Liturgy follows the Hours
            if "Liturgy" in svc_by_name:
                self._render_service_block(digest, svc_by_name["Liturgy"], context, rubrics)

        # ------------------------------------------------------------------
        # E. CURRENT EVENING (Presanctified or Aliturgical marker)
        # ------------------------------------------------------------------
        if is_presanctified:
            digest.append("\n## LITURGY OF THE PRESANCTIFIED GIFTS")
            struct_data = self.engine._load_json("json_db/01j_struct_liturgy.json")
            skeleton = self.engine._get_structure_sequence(struct_data, "liturgy_presanctified")
            if skeleton:
                self._process_skeleton(digest, context, rubrics, skeleton)
            else:
                digest.append("  [Presanctified structure not resolved — check liturgy JSON]")
        elif late_service == "aliturgical":
            digest.append("\n## ALITURGICAL (NO LITURGY)")

        return "\n".join(digest)

    def _is_lenten_weekday(self, context):
        """True if this is a Mon-Fri weekday during Great Lent (not Holy Week)."""
        season = context.get("season", "")
        period = context.get("triodion_period", "")
        day = context.get("day_of_week", -1)  # 0=Sun, 6=Sat
        # Holy Week weekdays are handled as separate cases, not generic lenten_weekday
        holy_week_periods = ("holy_thursday", "holy_friday", "holy_saturday",
                             "holy_week_weekday")
        if period in holy_week_periods:
            return False
        return season == "lent" and day in [1, 2, 3, 4, 5]

    def _render_service_block(self, digest, service, context, rubrics):
        """Helper to render a single service within the digest."""
        service_name = service["name"]
        
        # Expanded Name (e.g. "Great Vespers")
        if hasattr(self.engine, "get_expanded_service_name"):
             service_name = self.engine.get_expanded_service_name(service, context)

        digest.append(f"\n## {service_name.upper()}")
        
        # Root ID resolution logic (mirrors engine)
        root_id = service["root"]
        if service["type_key"] in rubrics.get("variables", {}):
            root_id = rubrics["variables"][service["type_key"]]
        if service["type_key"] in rubrics.get("overrides", {}):
            root_id = rubrics["overrides"][service["type_key"]]

        # Specific Overrides
        if service_name == "Matins":
             if context.get("triodion_period") == "holy_friday": root_id = "tomb_matins"
             elif context.get("triodion_period") in ["pascha", "bright_week"]: root_id = "bright_matins"
             elif context.get("triodion_period") == "holy_week_weekday" and context.get("day_of_week") in [4, 5]:
                  root_id = "passion_matins"  # Holy Thursday night: 12 Gospels
             elif context.get("triodion_period") == "holy_week_weekday" and context.get("day_of_week") in [1, 2, 3]:
                  root_id = "bridegroom_matins"  # Holy Mon/Tue/Wed: Bridegroom
        
        elif service["name"] == "Compline":
             if hasattr(self.engine, "resolve_compline_type"):
                  ctype = self.engine.resolve_compline_type(context)
                  if ctype == "paschal_hours": root_id = "structure_paschal"
                  # Fix: JSON uses 'great_compline_lenten', not 'structure_great_compline'
                  elif ctype == "great_compline": root_id = "great_compline_lenten"

        elif service_name == "Midnight Office":
             mode_data = self.engine.resolve_midnight_office_mode(context)
             if "mode" in mode_data: root_id = f"midnight_{mode_data['mode']}"
             
        elif "hours_type" in service["type_key"]:
             var_hours = rubrics.get("variables", {}).get("hours_type", "")
             if "royal" in var_hours: root_id = "structure_royal"
             elif "lenten" in var_hours: root_id = "structure_lenten"
             elif "paschal" in var_hours: root_id = "structure_paschal"

        struct_data = self.engine._load_json(service["file"])
        skeleton = self.engine._get_structure_sequence(struct_data, root_id)
        if skeleton:
            self._process_skeleton(digest, context, rubrics, skeleton)
        else:
            # Every service always has fixed Horologion content; a missing skeleton
            # means a root_id mismatch or missing JSON structure — flag it clearly.
            digest.append(f"  [Fixed Horologion content] (structure '{root_id}' not found in {service['file']})")  # noqa

    def _process_skeleton(self, digest, context, rubrics, skeleton):
        
        def recurse(skeleton, depth=0):
            for slot in skeleton:
                slot_id = slot.get('id', 'anonymous_slot')
                
                # 1. Rubrics (Instructional)
                if "rubric" in slot:
                    r = slot["rubric"]
                    title = r
                    source_ref = ""
                    if isinstance(r, dict):
                        title = r.get('title') or r.get('description') or r.get('text')
                        source_ref = r.get('source_ref', '')
                    
                    if source_ref:
                         digest.append(f"> **Primary Source ({source_ref}):** *{title}*")
                    else:
                         digest.append(f"> *Rubric:* {title}")

                content = slot.get("content", {})
                if not content and "type" in slot: content = slot
                
                # Implicit Sequence Handle
                if not content and "sequence" in slot:
                     content = slot
                     content["type"] = "sequence"
                
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
                    # Special handling for Stichera
                    if method == "generate_stichera_sequence":
                         enriched_context = {**context, **rubrics.get("variables", {})}
                         enriched_context["overrides"] = rubrics.get("overrides", {})
                         if rubrics.get("is_sunday_vigil"): enriched_context["is_sunday_vigil"] = True

                         if "vespers" in args.get('slot_id', ''):
                              try:
                                   res = self.engine.resolve_vespers_stichera(enriched_context)
                                   total = res.get("total_count", 0)
                                   digest.append(f"At 'Lord, I have cried': {total} stichera")
                                   
                                   # New: Expanded Items
                                   if "items" in res and res["items"]:
                                       for item in res["items"]:
                                            digest.append(f"- {item}")
                                   else:
                                       # Fallback to distribution summary
                                       for item in res.get("distribution", []):
                                            c = item.get('count', item.get('qty', '?'))
                                            s = item.get('source', item.get('type', '')).upper()
                                            digest.append(f"- {c} from {s}")
                                   
                                   if "glory" in res: digest.append(f"Glory... {res['glory']}")
                                   if "both_now" in res: digest.append(f"Both Now... {res['both_now']}")
                              except Exception as e:
                                   digest.append(f"At 'Lord, I have cried': (Logic Error: {e})")

                # 4. Sequences & Complex Structures
                elif slot_type in ["sequence", "complex_structure"]:
                    if "components" in content:
                        recurse(content["components"], depth + 1)
                    elif "sequence" in content:
                        recurse(content["sequence"], depth + 1)

                # 5. Conditional Blocks
                elif slot_type == "conditional_block":
                    logic = content.get("logic", {})
                    func = logic.get("function")
                    args = logic.get("args", {})
                    
                    active_content = None
                    try:
                         enriched_context = {**context, **rubrics.get("variables", {})}
                         if rubrics.get("is_sunday_vigil"): enriched_context["type"] = "vigil"

                         method = getattr(self.engine, func)
                         if method(enriched_context, **args): active_content = content.get("true_content")
                         else: active_content = content.get("false_content")
                    except:
                         digest.append(f"[Conditional Block: {func}]")
                    
                    if active_content:
                         if isinstance(active_content, dict): active_content = [active_content]
                         recurse(active_content, depth + 1)

                # 6. Fixed Content & Groups
                elif slot_type == "fixed_ref":
                    ref = content.get('ref_key', '')
                    title = ref.split('.')[-1].replace('_', ' ').title()
                    
                    if "psalm" in ref: digest.append(f"**Psalm:** {title}")
                    elif "litany" in ref: digest.append(f"**Litany:** {title}")
                    elif "hymn" in ref: digest.append(f"**Hymn:** {title}")
                    else: digest.append(f"**Priest/Reader:** {title}")
                
                elif slot_type == "component_ref":
                    ref_key = content.get("ref_key")
                    name = ref_key.split('.')[-1].replace('_', ' ').title()
                    digest.append(f"[{name}]")
                    
                    # Try to expand component content
                    try:
                        # 1. Check if it's a known component file (e.g. 03_common_components.json)
                        # We can try to load a default list of component files or search logic.
                        # For now, let's assume components are in '03_common_components.json' or similar.
                        # A better way finds the file dynamically or uses engine.text_db if loaded?
                        # But text_db is text, not structure. 
                        # We need the structure definition. 
                        
                        # HACK: Hardcoded check for known component files in json_db
                        comp_files = ["00_components.json", "03_components_common.json", "03_components_vespers.json", "03_components_matins.json"]
                        found_comp = None
                        
                        for cf in comp_files:
                             # Check versioned dir first
                             paths_to_check = [
                                 os.path.join(self.engine.json_db, cf),
                                 os.path.join(os.path.dirname(self.engine.json_db), cf)
                             ]
                             
                             path = None
                             for p in paths_to_check:
                                 if os.path.exists(p):
                                      path = p
                                      break
                             
                             if path:
                                  with open(path, 'r', encoding='utf-8') as f:
                                       data = json.load(f)
                                       # Look for the component ID (ref_key usually 'components.entrance_great')
                                       comp_id = ref_key.split('.')[-1]
                                       
                                       # Recursively search for 'id': comp_id in the file?
                                       # Or is the file a dictionary of components?
                                       # Update 2026-02-10: 00_components.json has "components": { "key": {...} }
                                       
                                       if isinstance(data, dict):
                                            if "components" in data:
                                                 # Look in "components" dict
                                                 # Try direct key match "entrance_great"
                                                 if comp_id in data["components"]:
                                                      found_comp = data["components"][comp_id]
                                                 # Or loop?
                                            
                                            # Also check root if structure differs
                                            if not found_comp and comp_id in data:
                                                 found_comp = data[comp_id]

                                       # Legacy list support
                                       elif isinstance(data, list):
                                            for item in data:
                                                 if item.get("id") == comp_id:
                                                      found_comp = item
                                                      break
                                       if found_comp: break
                        
                        if found_comp:
                             # It's a structure slot! Recurse.
                             
                             # Case A: Explicit Content Wrapper
                             if "content" in found_comp:
                                  c = found_comp["content"]
                                  if isinstance(c, list): recurse(c, depth + 1)
                                  elif isinstance(c, dict) and "sequence" in c: recurse(c["sequence"], depth + 1)
                                  elif isinstance(c, dict): recurse([found_comp], depth + 1) # Encapsulated
                             
                             # Case B: Direct Sequence (Common in 00_components.json)
                             elif "sequence" in found_comp:
                                  recurse(found_comp["sequence"], depth + 1)
                                  
                    except Exception as e:
                         pass # Fail silently, just show header
                
                elif slot_type == "fixed_group":
                    digest.append("**Fixed Group:**")
                    for k in content.get("ref_keys", []):
                         title = k.split('.')[-1].replace('_', ' ').title()
                         digest.append(f"- *{title}*")

                # 7. Slot Variables
                elif slot_type == "slot_variable":
                    sid = content.get("slot_id")
                    val = rubrics.get("overrides", {}).get(sid)
                    if not val: val = rubrics.get("variables", {}).get(sid)
                    if val: digest.append(f"{sid}: {val}")
                    else: digest.append(f"{sid}: (Variable)")

                # 8. Canon Odes (Enhanced)
                elif slot_type == "canon_ode":
                    ode = content.get('ode')
                    digest.append(f"Ode {ode}")
                    
                    # A. Structure (Troparia Counts)
                    if hasattr(self.engine, "resolve_canon_structure"):
                        try:
                             structure = self.engine.resolve_canon_structure(ode, context)
                             if structure:
                                 parts = []
                                 for item in structure:
                                     src = item.get('source', 'Unknown').capitalize()
                                     cnt = item.get('count', item.get('qty', '?'))
                                     extra = ""
                                     if item.get('irmos'): extra = " (including irmos)"
                                     parts.append(f"{src} - {cnt}{extra}")
                                 digest.append(f"  Structure: {', '.join(parts)}")
                        except Exception as e:
                             digest.append(f"  [Error resolving structure: {e}]")

                    # B. Katavasia
                    # Note: Katavasia logic is often separate in the skeleton, checking if omitted here
                    # If the skeleton handles it via 'variable_logic' -> 'resolve_katavasia', we skip it here.
                    # But if we want it grouped:
                    # (Skipping here to rely on skeleton slots, or we can force it if missing)

                # 9. Links
                elif slot_type == "link":
                    target = slot.get('target_id')
                    target_file = slot.get('target_file')
                    if target_file and target:
                         full_path = os.path.join(self.engine.json_db, target_file)
                         if not os.path.exists(full_path): full_path = target_file
                         if os.path.exists(full_path):
                             try:
                                 with open(full_path, 'r', encoding='utf-8') as f: linked_data = json.load(f)
                                 sub_skeleton = self.engine._get_structure_sequence(linked_data, target)
                                 if sub_skeleton: recurse(sub_skeleton, depth + 1)
                             except: pass

        # Start recursion
        recurse(skeleton)


    def _format_logic_hook(self, func_name, args, context, rubrics):
        if not hasattr(self.engine, func_name): return []

        try:
            enriched_context = {**context, **rubrics.get("variables", {})}
            enriched_context["overrides"] = rubrics.get("overrides", {})
            if rubrics.get("is_sunday_vigil"): enriched_context["is_sunday_vigil"] = True
            # Ensure rank is always int (can leak in as string from rubrics variables)
            if "rank" in enriched_context:
                try: enriched_context["rank"] = int(enriched_context["rank"])
                except (ValueError, TypeError): enriched_context["rank"] = 5

            func = getattr(self.engine, func_name)
            
            import inspect
            sig = inspect.signature(func)
            call_kwargs = {}
            if "rubrics" in sig.parameters: call_kwargs["rubrics"] = rubrics
            
            # Forward any args from the JSON definition that match function parameters
            # This handles `hour`, `hour_num`, `service`, etc.
            for arg_key, arg_val in args.items():
                if arg_key in sig.parameters and arg_key not in call_kwargs:
                    call_kwargs[arg_key] = arg_val

            result = func(enriched_context, **call_kwargs)

            # Formatting Rules
            if func_name == "resolve_prokeimenon" or "prokeimenon" in func_name:
                lines = []
                if isinstance(result, dict): result = [result]
                for p in result:
                     if isinstance(p, dict):
                         ref = p.get('ref_key', p.get('source', 'Unknown'))
                         lines.append(f"Prokeimenon: {ref.split('.')[-1]}")
                return lines

            if func_name == "resolve_god_is_the_lord_troparia":
                if result.get("gradual_type") == "alleluia":
                    return ["At God is the Lord: Alleluia is sung."]
                else:
                    lines = [f"At God is the Lord (Tone {result.get('tone')}):"]
                    for t in result.get("sequence", []):
                        lines.append(f"- {t.get('content', t.get('type'))}")
                    return lines

            if "readings" in func_name:
                lines = ["Readings:"]
                has_content = False
                if isinstance(result, list):
                    for r in result:
                        if not r: continue
                        has_content = True
                        
                        # Check if it's a Prokeimenon dictionary mixed in
                        if isinstance(r, dict) and r.get("type") == "prokeimenon":
                             ref = r.get('ref_key', r.get('content', 'Unknown'))
                             lines.append(f"Prokeimenon: {ref}")
                        else:
                             citation = r.get('citation', '')
                             if not citation and "source" in r: citation = r.get('source')
                             lines.append(f"- {citation}")
                
                if not has_content: return []
                return lines

            if "aposticha" in func_name:
                lines = ["Aposticha:"]
                if isinstance(result, dict):
                    components = result.get("components", result.get("stichera", []))
                    for c in components:
                         s = c.get("source", "Unknown").upper()
                         t = c.get("id", c.get("type", c.get("ref", "")))
                         count = c.get("count", 1)
                         lines.append(f"- {count} x {s} ({t})")
                    
                    if "glory" in result:
                         ref = result["glory"].get("id", result["glory"].get("ref", "Unknown"))
                         lines.append(f"- Glory... {ref}")
                    if "now" in result:
                         ref = result["now"].get("id", result["now"].get("ref", "Unknown"))
                         lines.append(f"- Both Now... {ref}")
                return lines

            if "troparia" in func_name or "hymns" in func_name:
                lines = [f"Hymns ({func_name}):"]
                if isinstance(result, dict):
                    if "components" in result:
                        for c in result["components"]: lines.append(f"- {c.get('id', c.get('type'))}")
                    elif "sequence" in result:
                        for c in result["sequence"]: lines.append(f"- {c.get('content', c.get('type'))}")
                    elif "troparia" in result and isinstance(result["troparia"], list):
                         for t in result["troparia"]: lines.append(f"- Troparion: {t.get('id', t.get('ref_key'))}")
                    elif "kontakia" in result and isinstance(result["kontakia"], list):
                         for k in result["kontakia"]: lines.append(f"- Kontakion: {k.get('id', k.get('ref_key'))}")

                if isinstance(result, list): 
                     for r in result:
                          if isinstance(r, dict): lines.append(f"- {r.get('id') or r.get('ref_key')}")
                return lines

            if isinstance(result, dict) and result.get("type") == "sequence":
                 lines = []
                 for c in result.get("components", []):
                      if c.get("type") == "fixed_ref":
                           lines.append(f"- {c.get('ref_key')}")
                 return lines

            if "katavasia" in func_name:
                 if isinstance(result, dict):
                     name = result.get('katavasia_id', result.get('text', result.get('ref_key', 'Unknown')))
                     return [f"Katavasia: {name}"]
                 return [f"Katavasia: {result}"]

            if "canon" in func_name and "insertion" in func_name:
                 # canon_insertion returns a list of interlude components
                 if isinstance(result, list):
                     lines = []
                     for item in result:
                         if isinstance(item, dict):
                             lines.append(f"  Interlude: {item.get('type', '')} - {item.get('id', item.get('ref_key', ''))}")
                     return lines if lines else []
                 elif isinstance(result, dict):
                     return [f"Canon Interlude: {result.get('action', result.get('type', 'Standard'))}"]
                 return []

            if "canon" in func_name:
                 if isinstance(result, dict):
                     return [f"Canon Logic: {result.get('action', 'Standard')}"]
                 elif isinstance(result, list):
                     return [f"Canon Logic: {len(result)} components"]
                 return []
            return []

        except Exception as e:
            return [f"[Error formatting {func_name}: {e}]"]
