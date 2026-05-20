import os

code = '''
    def resolve_aposticha(self, context, rubrics=None):
        """
        Resolves Aposticha (Stichera at the Aposticha) for Vespers and Matins.
        Driven entirely by the 02a_logic_general.json paradigm rules, eliminating hardcoding.
        Citation: Dolnytsky Part II Lines 86, 170, 196, 226, 246, etc.
        """
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
                components.append({
                    "source": source,
                    "id": item_id,
                    "count": 1
                })
        
        # Glory / Both Now
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
            
        # Fallback if config is missing due to missing paradigm mapping
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
'''

with open(r'E:\Google Antigravity\Projects\Typikon Coded\ruthenian_engine.py', 'a', encoding='utf-8') as f:
    f.write(code)
