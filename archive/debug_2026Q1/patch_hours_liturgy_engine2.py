import ast

def patch_methods(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    new_methods = """
    def resolve_hours_troparia(self, context, rubrics=None):
        paradigm = context.get("paradigm", "case_01_sunday_simple")
        variables = self._lookup_paradigm_variables(paradigm)
        dist = variables.get("hours_distribution", {})
        
        trop_rules = dist.get("troparion", "day")
        glory_rules = dist.get("glory", "none")
        
        components = [{"type": "troparion", "source": trop_rules}]
        if glory_rules != "none":
            components.append({"type": "glory_troparion", "source": glory_rules})
            
        return {"mode": "standard", "components": components}

    def resolve_hours_kontakion(self, context, rubrics=None):
        paradigm = context.get("paradigm", "case_01_sunday_simple")
        variables = self._lookup_paradigm_variables(paradigm)
        dist = variables.get("hours_distribution", {})
        kontakion_rules = dist.get("kontakion", "day")
        
        return {"type": "kontakion", "source": kontakion_rules}
        
    def resolve_liturgy_antiphons(self, context, rubrics=None):
        paradigm = context.get("paradigm", "case_01_sunday_simple")
        variables = self._lookup_paradigm_variables(paradigm)
        dist = variables.get("liturgy_distribution", {})
        antiphons = dist.get("antiphons", "daily")
        
        return {"type": "liturgy_antiphons", "strategy": antiphons}

    def resolve_liturgy_hymns(self, context, rubrics=None):
        paradigm = context.get("paradigm", "case_01_sunday_simple")
        variables = self._lookup_paradigm_variables(paradigm)
        dist = variables.get("liturgy_distribution", {})
        
        troparia = dist.get("troparia", ["day"])
        kontakia = dist.get("kontakia", ["day_glory", "bothnow_theotokion"])
        
        return {
             "type": "liturgy_hymns",
             "troparia_sequence": troparia,
             "kontakia_sequence": kontakia
        }
        
    def resolve_aposticha(self, context, rubrics=None):
        paradigm = context.get("paradigm", "case_01_sunday_simple")
        variables = self._lookup_paradigm_variables(paradigm)
        
        distribution_config = variables.get("aposticha_distribution", {})
        total_count = distribution_config.get("total_count", 0)
        distribution = distribution_config.get("distribution", [])
        
        components = []
        for group in distribution:
            source = group.get("source")
            b_type = group.get("type", "resurrection")
            qty = group.get("qty", 1)
            
            for i in range(1, qty + 1):
                item_id = f"aposticha_{b_type}_{i}"
                components.append({"source": source, "id": item_id, "count": 1})
        
        glory_type = distribution_config.get("glory", "none")
        if glory_type != "none":
            components.append({
                "source": "menaion" if "saint" in glory_type or "feast" in glory_type else "octoechos",
                "id": glory_type,
                "type": "glory"
            })
            
        both_now_type = distribution_config.get("both_now", "aposticha_theotokion")
        if both_now_type != "none":
            components.append({
                 "source": "menaion" if "forefeast" in both_now_type or "feast" in both_now_type or "afterfeast" in both_now_type else "octoechos",
                 "id": both_now_type,
                 "type": "both_now" if glory_type != "none" else "glory_both_now"
            })
            
        if not components:
             day = context.get("day_of_week", 0)
             if day == 0:
                  tone = context.get("tone", 1)
                  components = [
                       {"source": "octoechos", "id": f"aposticha_resurrection_tone_{tone}", "count": 1},
                       {"source": "octoechos", "id": f"aposticha_theotokion_tone_{tone}", "type": "glory_both_now"}
                  ]
             else:
                  components = [
                       {"source": "octoechos", "id": "aposticha_daily", "count": 3},
                       {"source": "octoechos", "id": "aposticha_theotokion", "type": "glory_both_now"}
                  ]
                  
        return {
            "type": "aposticha",
            "components": components
        }
"""

    tree = ast.parse(source)
    methods_to_replace = ["resolve_hours_troparia", "resolve_hours_kontakion", "resolve_liturgy_antiphons", "resolve_liturgy_hymns"]
    
    ranges = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in methods_to_replace:
            ranges.append((node.lineno, node.end_lineno))
            
    ranges.sort(key=lambda x: x[0], reverse=True)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    lines_copy = list(lines)
    for start, end in ranges:
        del lines_copy[start-1:end]
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines_copy)
        f.write(new_methods)
        
    print("Methods patched safely.")

patch_methods(r'E:\Google Antigravity\Projects\Typikon Coded\ruthenian_engine.py')
