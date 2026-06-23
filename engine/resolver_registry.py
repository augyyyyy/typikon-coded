import json
import os
import glob

class ResolverRegistry:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.registry = {}
        self.build_registry()

    def build_registry(self):
        """
        Dynamically scans all service structure JSON files to compile
        the list of allowed logic resolvers for each structure ID.
        """
        struct_files = glob.glob(os.path.join(self.base_dir, "json_db", "01*_struct_*.json"))
        
        all_structures = {}
        for filepath in struct_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    structs = data.get("structures", {})
                    for sid, sdata in structs.items():
                        all_structures[sid] = sdata
            except Exception:
                pass

        # Load components from 00_components.json
        self.components = {}
        comp_file = os.path.join(self.base_dir, "json_db", "00_components.json")
        if os.path.exists(comp_file):
            try:
                with open(comp_file, 'r', encoding='utf-8') as f:
                    cdata = json.load(f)
                    self.components = cdata.get("components", {})
                    # Also unwrap keys starting with components, but do not overwrite real ones with stubs
                    for k, v in cdata.items():
                        if k.startswith("components."):
                            name = k.split("components.", 1)[1]
                            if name not in self.components or (isinstance(v, dict) and not v.get("_stub")):
                                self.components[name] = v
            except Exception:
                pass

        # Recursively resolve permitted functions per structure ID
        for sid in all_structures:
            self.registry[sid] = self._resolve_allowed_resolvers(sid, all_structures)

    def _resolve_allowed_resolvers(self, sid, all_structures, visited=None):
        if visited is None:
            visited = set()
            
        if sid in visited:
            return set()
        visited.add(sid)
        
        allowed = set()
        sdata = all_structures.get(sid, {})
        
        # 1. Handle inherits_from (recursive inheritance resolution)
        parent = sdata.get("inherits_from")
        if parent and parent in all_structures:
            allowed.update(self._resolve_allowed_resolvers(parent, all_structures, visited))
            
        # Helper to extract resolver functions
        def extract_funcs(item):
            funcs = set()
            if not isinstance(item, dict):
                return funcs
                
            objs_to_check = [item]
            content = item.get("content")
            if isinstance(content, dict):
                objs_to_check.append(content)
                
            for obj in objs_to_check:
                if obj.get("type") == "variable_logic":
                    logic = obj.get("logic", {})
                    if isinstance(logic, dict) and "function" in logic:
                        funcs.add(logic["function"])
                elif obj.get("type") == "generator":
                    gen_method = obj.get("generator_method")
                    resolver_mapping = {
                        "generate_stichera_sequence": "resolve_vespers_stichera",
                        "generate_antiphons": "resolve_liturgy_antiphons",
                        "generate_hour_troparia": "resolve_hours_collision"
                    }
                    mapped_func = resolver_mapping.get(gen_method)
                    if mapped_func:
                        funcs.add(mapped_func)
                
                # Check nested components
                if "components" in obj:
                    for comp in obj["components"]:
                        funcs.update(extract_funcs(comp))

                # Check conditional content
                tc = obj.get("true_content")
                if tc:
                    funcs.update(extract_funcs(tc))
                fc = obj.get("false_content")
                if fc:
                    funcs.update(extract_funcs(fc))
                        
            # Check nested sequences
            for seq_item in item.get("sequence", []):
                funcs.update(extract_funcs(seq_item))
                
            # Check overrides within sequence items
            for ov in item.get("overrides", []):
                new_comp = ov.get("new_component", {})
                if new_comp:
                    funcs.update(extract_funcs(new_comp))
                    
            return funcs

        # Helper to check linked structures, component refs, and structure refs
        def check_relations(item):
            links = set()
            comp_refs = set()
            struct_refs = set()
            if not isinstance(item, dict):
                return links, comp_refs, struct_refs
                
            objs_to_check = [item]
            content = item.get("content")
            if isinstance(content, dict):
                objs_to_check.append(content)
                
            for obj in objs_to_check:
                typ = obj.get("type")
                if typ == "link":
                    tid = obj.get("target_id")
                    if tid:
                        links.add(tid)
                elif typ == "component_ref":
                    ref_key = obj.get("ref_key")
                    if ref_key:
                        name = ref_key
                        if name.startswith("components."):
                            name = name.split("components.", 1)[1]
                        comp_refs.add(name)
                elif typ == "structure_ref":
                    root_id = obj.get("root_id")
                    if root_id:
                        struct_refs.add(root_id)
                        
                if "components" in obj:
                    for comp in obj["components"]:
                        l, c, s = check_relations(comp)
                        links.update(l)
                        comp_refs.update(c)
                        struct_refs.update(s)

                # Check conditional blocks
                tc = obj.get("true_content")
                if tc:
                    l, c, s = check_relations(tc)
                    links.update(l)
                    comp_refs.update(c)
                    struct_refs.update(s)
                fc = obj.get("false_content")
                if fc:
                    l, c, s = check_relations(fc)
                    links.update(l)
                    comp_refs.update(c)
                    struct_refs.update(s)
                        
            for seq_item in item.get("sequence", []):
                l, c, s = check_relations(seq_item)
                links.update(l)
                comp_refs.update(c)
                struct_refs.update(s)
                
            for ov in item.get("overrides", []):
                new_comp = ov.get("new_component", {})
                if new_comp:
                    l, c, s = check_relations(new_comp)
                    links.update(l)
                    comp_refs.update(c)
                    struct_refs.update(s)
                    
            return links, comp_refs, struct_refs

        # 2. Scan standard sequence for resolvers and relations
        linked_sids = set()
        comp_names = set()
        struct_sids = set()
        for item in sdata.get("sequence", []):
            allowed.update(extract_funcs(item))
            l, c, s = check_relations(item)
            linked_sids.update(l)
            comp_names.update(c)
            struct_sids.update(s)
            
        # 3. Scan root-level overrides for resolvers and relations
        for override in sdata.get("overrides", []):
            allowed.update(extract_funcs(override))
            l, c, s = check_relations(override)
            linked_sids.update(l)
            comp_names.update(c)
            struct_sids.update(s)
            new_comp = override.get("new_component", {})
            if new_comp:
                allowed.update(extract_funcs(new_comp))
                l, c, s = check_relations(new_comp)
                linked_sids.update(l)
                comp_names.update(c)
                struct_sids.update(s)

        # Helper to resolve all resolvers from a set of component names recursively
        def resolve_components(names, visited_comps=None):
            if visited_comps is None:
                visited_comps = set()
            funcs = set()
            for cname in names:
                if cname in visited_comps:
                    continue
                visited_comps.add(cname)
                comp_data = self.components.get(cname, {})
                if comp_data:
                    funcs.update(extract_funcs(comp_data))
                    l, c, s = check_relations(comp_data)
                    funcs.update(resolve_components(c, visited_comps))
                    linked_sids.update(l)
                    struct_sids.update(s)
            return funcs

        allowed.update(resolve_components(comp_names))
            
        # 4. Recursively pull resolvers from referenced structures
        for struct_sid in struct_sids:
            if struct_sid in all_structures:
                allowed.update(self._resolve_allowed_resolvers(struct_sid, all_structures, visited))

        # 5. Recursively pull resolvers from linked structures
        for linked_sid in linked_sids:
            if linked_sid in all_structures:
                allowed.update(self._resolve_allowed_resolvers(linked_sid, all_structures, visited))
                
        return allowed

    def is_allowed(self, structure_id, func_name):
        """
        Validates if func_name is legally allowed to execute under structure_id.
        """
        redirects = {
            "resolve_alleluia": "resolve_liturgy_alleluia",
            "resolve_megalynarion": "resolve_liturgy_megalynarion",
            "resolve_liturgy_readings_logic": "resolve_liturgy_readings",
            "resolve_megalynaria": "resolve_angelic_council"
        }
        actual_name = redirects.get(func_name, func_name)
        
        # If structure is not specified or unknown, bypass check
        if not structure_id or structure_id not in self.registry:
            return True
            
        allowed_set = self.registry[structure_id]
        
        # Universal helper checks and dismissals are always allowed
        common_allowed = {
            "check_day_range",
            "check_gospel_service",
            "check_litiya_trigger",
            "check_service_continuity",
            "check_service_type",
            "resolve_kathisma_choice",
            "resolve_canon_ode_troparion",
            "resolve_dismissal_universal"
        }
        if actual_name in common_allowed:
            return True
            
        return actual_name in allowed_set
