import json
import os

class TypikonDigestGenerator:
    def __init__(self, engine):
        self.engine = engine

    def generate(self, context, rubrics):
        """
        Generates a 'Typikon Style' digest (instructions only, no full text).
        """
        digest = [f"TYPIKON: {context['date']}"]
        digest.append(f"Logic: {rubrics['title']}")
        digest.append("-" * 40)

        self._process_skeleton(digest, context, rubrics)
        
        return "\n".join(digest)

    def _process_skeleton(self, digest, context, rubrics):
        
        def recurse(skeleton, depth=0):
            for slot in skeleton:
                slot_id = slot.get('id', 'anonymous_slot')
                
                # 1. Rubrics (Instructional)
                if "rubric" in slot:
                    r = slot["rubric"]
                    title = r
                    if isinstance(r, dict):
                        title = r.get('title') or r.get('description') or r.get('text')
                        if not title:
                             if "source_ref" in r: title = f"Rubric ({r['source_ref']})"
                             else: title = "Rubric"
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
                                   for item in res.get("distribution", []):
                                        c = item.get('count', item.get('qty', '?'))
                                        s = item.get('source', item.get('type', '')).upper()
                                        digest.append(f"- {c} from {s}")
                                   if "glory" in res: digest.append(f"Glory... {res['glory']}")
                                   if "both_now" in res: digest.append(f"Both Now... {res['both_now']}")
                              except:
                                   digest.append("At 'Lord, I have cried': (Logic Error)")

                # 4. Sequences & Complex Structures
                elif slot_type in ["sequence", "complex_structure"]:
                    if "components" in content:
                        recurse(content["components"], depth + 1)

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
                    ref = content.get('ref_key')
                    if "psalm" in ref: digest.append(f"Psalm: {ref.split('.')[-1]}")
                    elif "litany" in ref: digest.append(f"Litany")
                    elif "hymn" in ref: digest.append(f"Hymn: {ref.split('.')[-1]}")
                
                elif slot_type == "fixed_group":
                    digest.append("Fixed Group:")
                    for k in content.get("ref_keys", []):
                         digest.append(f"- {k.split('.')[-1]}")

                # 7. Slot Variables
                elif slot_type == "slot_variable":
                    sid = content.get("slot_id")
                    val = rubrics.get("overrides", {}).get(sid)
                    if not val: val = rubrics.get("variables", {}).get(sid)
                    if val: digest.append(f"{sid}: {val}")
                    else: digest.append(f"{sid}: (Variable)")

                # 8. Canon Odes
                elif slot_type == "canon_ode":
                    digest.append(f"Ode {content.get('ode')}")
                elif slot_type == "canon_ode_range":
                    digest.append(f"Odes {content.get('range')}")

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

        # Traverse all services
        for service in self.engine.daily_cycle:
            service_name = service["name"]
            digest.append(f"\n=== {service_name.upper()} ===")
            
            # Root ID resolution logic (mirrors engine)
            root_id = service["root"]
            if service["type_key"] in rubrics.get("variables", {}):
                root_id = rubrics["variables"][service["type_key"]]
            if service["type_key"] in rubrics.get("overrides", {}):
                root_id = rubrics["overrides"][service["type_key"]]

            if service_name == "Matins":
                 if context["triodion_period"] == "holy_friday": root_id = "tomb_matins"
                 elif context["triodion_period"] in ["pascha", "bright_week"]: root_id = "bright_matins"
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
                recurse(skeleton)

    def _format_logic_hook(self, func_name, args, context, rubrics):
        if not hasattr(self.engine, func_name): return []

        try:
            enriched_context = {**context, **rubrics.get("variables", {})}
            enriched_context["overrides"] = rubrics.get("overrides", {})
            if rubrics.get("is_sunday_vigil"): enriched_context["is_sunday_vigil"] = True

            func = getattr(self.engine, func_name)
            
            import inspect
            sig = inspect.signature(func)
            call_kwargs = {}
            if "rubrics" in sig.parameters: call_kwargs["rubrics"] = rubrics
            
            if func_name == "resolve_hours_collision" and "hour_num" in args:
                 call_kwargs["hour_num"] = args["hour_num"]

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
                if isinstance(result, list):
                    for r in result:
                        citation = r.get('citation', '')
                        if not citation and "source" in r: citation = r.get('source')
                        lines.append(f"- {citation}")
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

            if "katavasia" in func_name:
                 if isinstance(result, dict): return [f"Katavasia: {result.get('ref_key', 'Unknown')}"]
                 return [f"Katavasia: {result}"]

            if "canon" in func_name:
                 return [f"Canon Logic: {result.get('action', 'Standard')}"]

            return []

        except Exception as e:
            return [f"[Error formatting {func_name}: {e}]"]
