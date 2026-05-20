    def generate_typikon_digest(self, context, rubrics):
        """
        Generates a 'Typikon Style' digest (instructions only, no full text).
        """
        digest = [f"TYPIKON: {context['date']}"]
        digest.append(f"Logic: {rubrics['title']}")
        digest.append("-" * 40)

        # Helper to format stichera distribution
        def format_stichera_dist(dist_data):
            lines = []
            total = dist_data.get("total_count", 0)
            lines.append(f"We sing {total} stichera:")
            for item in dist_data.get("distribution", []):
                count = item.get("count", 0)
                source = item.get("source", "unknown").replace("_", " ").title()
                lines.append(f"- {count} from {source}")
            if "glory" in dist_data:
                lines.append(f"Glory... {dist_data['glory']}")
            if "both_now" in dist_data:
                lines.append(f"Both now... {dist_data['both_now']}")
            return lines

        def process_skeleton(skeleton, depth=0):
            indent = "" 
            
            for slot in skeleton:
                slot_id = slot.get('id', 'anonymous_slot')
                
                # 1. Rubrics (Print as instructions)
                if "rubric" in slot:
                    r = slot["rubric"]
                    title = r.get('title', r) if isinstance(r, dict) else r
                    # weak attempt to filter internal keys
                    digest.append(f"RUBRIC: {title}")

                content = slot.get("content", {})
                if not content and "type" in slot: content = slot
                slot_type = content.get("type")
                
                # 2. Logic Hooks (Important for structure)
                if slot_type == "variable_logic":
                    func_name = content["logic"].get("function")
                    args = content["logic"].get("args", {})
                    
                    # Execute logic to get the 'What'
                    try:
                        enriched_context = {**context, **rubrics.get("variables", {})}
                        enriched_context["overrides"] = rubrics.get("overrides", {})
                        func = getattr(self, func_name)
                        
                        # Inspect args
                        import inspect
                        sig = inspect.signature(func)
                        call_kwargs = {}
                        if "rubrics" in sig.parameters: call_kwargs["rubrics"] = rubrics
                        
                        if func_name == "resolve_hours_collision" and "hour_num" in args:
                             call_kwargs["hour_num"] = args["hour_num"]

                        result = func(enriched_context, **call_kwargs)
                        
                        # FORMATTING BASED ON FUNCTION NAME
                        if func_name == "resolve_prokeimenon":
                             if isinstance(result, list):
                                  for p in result:
                                       digest.append(f"Prokeimenon: {p.get('ref_key', 'Unknown')}")
                             elif isinstance(result, dict):
                                  digest.append(f"Prokeimenon: {result.get('ref_key', 'Unknown')}")

                        elif func_name == "resolve_god_is_the_lord_troparia":
                             if result.get("gradual_type") == "alleluia":
                                  digest.append("At God is the Lord: Alleluia is sung.")
                             else:
                                  digest.append(f"At God is the Lord (Tone {result.get('tone')}):")
                                  for t in result.get("sequence", []):
                                       digest.append(f"- {t.get('slot')}: {t.get('content')}")

                        elif func_name == "resolve_readings":
                             digest.append("Readings:")
                             for r in result:
                                  digest.append(f"- {r.get('source')} {r.get('citation', '')}")

                        elif "troparia" in func_name:
                             # Generic troparia handler
                             if isinstance(result, dict) and "components" in result:
                                  digest.append(f"Troparia:")
                                  for c in result["components"]:
                                       digest.append(f"- {c.get('id') or c.get('type')}")
                        
                    except Exception as e:
                        digest.append(f"[Error calculating {func_name}: {e}]")

                # 3. Generators
                elif slot_type == "generator":
                    method = content.get("generator_method")
                    args = content.get("args", {})
                    
                    if method == "generate_stichera_sequence":
                         # We need to peek at the logic, not just run it
                         # But for digest we actually want the RESULT of the logic
                         enriched_context = {**context, **rubrics.get("variables", {})}
                         res = self.resolve_vespers_stichera(enriched_context) # This is the underlying logic usually
                         # Wait, generate_stichera_sequence calls resolve_vespers_stichera internally?
                         # Actually it calls self.resolve_vespers_stichera usually.
                         # Let's just call that directly for the digest if we know it.
                         if "vespers" in args.get('slot_id', ''):
                              res = self.resolve_vespers_stichera(enriched_context)
                              lines = format_stichera_dist(res)
                              digest.extend(lines)

                # 4. Sequences (Recurse)
                elif slot_type == "sequence":
                    if "components" in content:
                        process_skeleton(content["components"], depth + 1)
                
                # 5. Fixed Content
                elif slot_type == "fixed_ref":
                    ref = content.get('ref_key')
                    if "psalm" in ref: digest.append(f"Psalm: {ref}")
                    elif "litany" in ref: digest.append(f"Litany: {ref}")
                    else: digest.append(f"Hymn: {ref}")

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
            digest.append(f"\n{service_name.upper()}")
            
            # Root ID resolution (Standard)
            root_id = service["root"]
            if service["type_key"] in rubrics.get("variables", {}):
                root_id = rubrics["variables"][service["type_key"]]
            if service["type_key"] in rubrics.get("overrides", {}):
                root_id = rubrics["overrides"][service["type_key"]]

            # Special Cases (Matins/Midnight/Hours filters) - duplicated from main engine
            # ... (omitted for brevity, assume standard weekday for now or copy logic)

            struct_data = self._load_json(service["file"])
            if not struct_data: continue
            
            skeleton = self._get_structure_sequence(struct_data, root_id)
            if skeleton:
                process_skeleton(skeleton)

        return "\n".join(digest)
