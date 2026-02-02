from ruthenian_engine import RuthenianEngine
from datetime import date
import json
import os

class CantorRenderer:
    def __init__(self):
        self.output = []

    def add_header(self, text, style="main"):
        text = text.upper()
        if style == "main":
            border = "=" * 40
            self.output.append(f"\n{border}")
            self.output.append(f"{text.center(40)}")
            self.output.append(f"{border}\n")
        elif style == "sub":
            self.output.append(f"\n{text.center(40)}")
            self.output.append("-" * 40)
    
    def add_rubric(self, text):
        # Swires Style: Red/Italicized rubric marker
        self.output.append(f"\n   [!] {text}")

    def add_verse_slot(self, number, verse_text, content_desc):
        self.output.append(f"\n{number:<3} {verse_text}...")
        self.output.append(f"    > {content_desc}")

    def render_seasonal_box(self, condition, content):
        # Encyclopedia Style Box
        box_width = 60
        border = f"+{'-' * (box_width - 2)}+"
        self.output.append(f"\n{border}")
        self.output.append(f"| SCENARIO: {condition.upper().ljust(box_width - 14)} |")
        self.output.append(f"{border}")
        for line in content:
            self.output.append(f"| {line.ljust(box_width - 4)} |")
        self.output.append(f"{border}")

    def render_actor_rubric(self, actor, text):
        # Swires Style: Actor Label Indented
        self.output.append(f"\n   {actor.upper()}: {text}")

    def render_canon(self, engine, context, rubrics):
        self.add_header("THE CANON", style="main")
        
        # Intro Rubric (Simulating the block text from screenshot)
        self.add_rubric("The Canon is sung. In current practice, we often omit the Biblical Canticles and sing only the Irmos and Katavasia, reading the Troparia.")
        
        # Default Dolnytsky Structure for Canon
        odes = [1, 3, 4, 5, 6, 7, 8, 9]
        
        for ode in odes:
            self.add_header(f"Ode {ode}", style="sub")
            
            # Simulated Refrain based on Screenshot style
            if ode == 1:
                self.output.append("Refrain: I will sing to the Lord, for He has triumphed gloriously!")
            elif ode == 9:
                self.output.append("Refrain: Magnify, O my soul...")
                
            self.output.append("") # Spacer
            
            # Logic: Get the components (e.g. Resurrection 4, Cross 2)
            # This is hardcoded for prototype, normally comes from engine.resolve_canon()
            components = [("Irmos", "Resurrection (Tone)"), ("Troparia (4)", "Resurrection"), ("Troparia (2)", "Theotokos")]
            if ode == 3 or ode == 6:
                components.append(("Katavasia", "O Open the Mouth (Irmos of Entrance)"))
            elif ode == 9:
                components = [("Magnification", "Verse 1"), ("Irmos", "He is God")]

            for label, source in components:
                 self.output.append(f"   > [{label}]: {source}")
            
            # Post-Ode Rubrics (Little Litany / Kontakion)
            if ode == 3:
                 self.add_rubric("Small Litany. Sessional Hymns (Kathisma).")
            elif ode == 6:
                 self.add_rubric("Small Litany. Kontakion and Ikos.")

    def render_structure(self, engine, context, rubrics):
        self.output = []
        
        # 1. Header
        feast_title = rubrics.get("title", "Service")
        self.add_header(f"CANTOR PROTOTYPE: {feast_title}")
        self.output.append(f"Date: {context['date']}")
        self.output.append(f"Tone: {context.get('tone', 'N/A')}")
        
        # 2. Determine Structure Root (e.g., 'great_vespers_vigil')
        # In a full app, this comes from rubrics['overrides']['vespers_type'] etc.
        # For this prototype, we'll traverse Great Vespers for the demo.
        root_id = "great_vespers_vigil"
        
        # Load the structure definition using Engine's helper (simulated access)
        struct_data = engine._load_json("01h_struct_vespers.json")
        sequence = engine._get_structure_sequence(struct_data, root_id)
        
        if not sequence:
            self.output.append("Error: Structure sequence not found.")
            return "\n".join(self.output)

        self.add_header(f"PROTOTYPE: {root_id.upper().replace('_', ' ')}", style="main")
        
        # 3. Traverse and Render Recursively
        for slot in sequence:
            self.render_slot(engine, context, slot, rubrics)

        return "\n".join(self.output)

    def render_slot(self, engine, context, slot, rubrics):
        slot_id = slot.get("id", "unknown")
        
        # --- RENDER RUBRICS ---
        if "rubric" in slot:
            r = slot["rubric"]
            if "title" in r: self.add_header(r["title"], style="sub")
            if "source_ref" in r: self.output.append(f"   (Source: {r['source_ref']})")
            if "note" in r: self.output.append(f"   [NOTE: {r['note']}]")
            if "roles" in r:
                for role, text in r["roles"].items():
                    self.render_actor_rubric(role, text)

        # --- RENDER CONTENT ---
        content = slot.get("content", {})
        c_type = content.get("type")

        # 1. Recursive Sequence
        if c_type == "sequence":
            for child in content.get("components", []):
                self.render_slot(engine, context, child, rubrics)

        # 2. Conditional Block
        elif c_type == "conditional_block":
            # Simplify logic evaluation for prototype (real engine has 'evaluate_condition')
            logic = content.get("logic", {})
            func = logic.get("function")
            args = logic.get("args", {})
            
            result = False
            # Hardcoded prototype checks
            if func == "check_service_type":
                # Check if the requested type matches context
                req_type = args.get("type")
                if req_type == "vigil" and "vigil" in rubrics.get("variables", {}).get("service_type", ""):
                    result = True
            
            # Recurse
            target_content = content.get("true_content") if result else content.get("false_content")
            if target_content:
                self.render_slot(engine, context, target_content, rubrics)

        # 3. Fixed Group
        elif c_type == "fixed_group":
             for key in content.get("ref_keys", []):
                 # Create a fake slot for the fixed ref
                 self.render_slot(engine, context, {"content": {"type": "fixed_ref", "ref_key": key}}, rubrics)

        # 4. Component Reference
        elif c_type == "component_ref":
             ref_key = content.get("ref_key")
             # Strip 'components.' prefix
             comp_id = ref_key.replace("components.", "")
             
             if hasattr(engine, 'components') and comp_id in engine.components:
                 comp_def = engine.components[comp_id]
                 if "sequence" in comp_def:
                      for child in comp_def["sequence"]:
                           self.render_slot(engine, context, child, rubrics)
             else:
                 self.output.append(f"   [MISSING COMPONENT: {ref_key}]") 

        # 5. Fixed Reference
        elif c_type == "fixed_ref":
            ref_key = content.get('ref_key')
            self._render_text_item(engine, ref_key)

        # 6. Variable Logic
        elif c_type == "variable_logic":
            logic_name = content.get("logic", {}).get("function", "Unknown")
            self._render_variable_item(engine, context, logic_name)

    def _render_text_item(self, engine, ref_key):
        # Normalize and Lookup
        lookup_keys = [ref_key, ref_key.replace("horologion.", "")]
        if "litany_great" in ref_key: lookup_keys.append("litany_peace")
        if "litany_small" in ref_key: lookup_keys.append("litany_peace")
        if "dismissal" in ref_key: lookup_keys.append("dismissal")

        item = None
        for k in lookup_keys:
            if hasattr(engine, 'text_db') and k in engine.text_db:
                item = engine.text_db[k]
                break
        
        if item:
            self.output.append(f"\n   >>> {item.get('title', ref_key)} <<<".upper())
            content = item.get('content', '')
            
            if isinstance(content, dict):
                 # Handle localized dictionary or structured content
                 # Try common language keys: 'en', 'eng', 'english', or 'content'
                 text = content.get('en') or content.get('eng') or content.get('english') or content.get('content') or str(content)
                 for line in text.split('\n'):
                     self.output.append(f"   {line}")
            elif isinstance(content, str):
                for line in content.split('\n'):
                    self.output.append(f"   {line}")
            else:
                 self.output.append(f"   [UNKNOWN CONTENT TYPE: {type(content)}]")
        else:
             self.output.append(f"\n   [MISSING TEXT: {ref_key}]")

    def _render_variable_item(self, engine, context, logic_name):
        # 1. Try to execute as a method on the engine first (Dynamic Logic)
        if hasattr(engine, logic_name):
            method = getattr(engine, logic_name)
            try:
                # Execute the logic function
                result = method(context)
                
                # Case A: Result is a Sequence (Legacy "God is the Lord" style)
                if isinstance(result, dict) and "sequence" in result:
                    self.output.append(f"\n   >>> LOGIC RESOLVED: {result.get('rule_id', 'custom')} (Tone {result.get('tone', '?')}) <<<")
                    sequence = result["sequence"]
                    for item in sequence:
                        # Recursively render the atomic component
                        # We construct a synthetic slot for the item
                        content_key = item.get("content")
                        count = item.get("count", 1)
                        
                        # Handle 'Separator' types (Glory/Both Now)
                        if item.get("type") in ["separator", "combined"]:
                             self._render_fixed_atomic_string(content_key)
                             continue

                        # Fetch the actual text for the content key
                        # This requires the engine to have a resolver for 'troparion_resurrection', etc.
                        for _ in range(count):
                            self._resolve_and_render_atomic_component(engine, context, content_key, result)
                    return "\n".join(self.output)
                
                # Case B: Result is simple text metadata (Legacy)
                elif isinstance(result, dict) and "content" in result and "type" not in result:
                    self._render_text_payload(result)
                    return "\n".join(self.output)

                # Case C: Result is a Structural Slot (Dict with 'type')
                elif isinstance(result, dict) and "type" in result:
                    self.render_slot(engine, context, {"content": result}, {})
                    return "\n".join(self.output)

                # Case D: Result is a List of Structural Slots
                elif isinstance(result, list):
                    for item in result:
                        if isinstance(item, dict):
                            # Treat as content definition
                            self.render_slot(engine, context, {"content": item}, {})
                    return "\n".join(self.output)

            except Exception as e:
                self.output.append(f"   [ERROR EXECUTING LOGIC {logic_name}: {e}]")
                return "\n".join(self.output)

        # 2. Fallback: Try to resolve as a variable reference key
        # (Existing legacy behavior)
        resolved_text = None
        if hasattr(engine, '_resolve_variable_ref'):
             key_candidate = logic_name.replace("resolve_", "")
             # Mappings
             if "stichera_resurrection" in logic_name: key_candidate = "stichera_resurrection"
             if "aposticha" in logic_name:
                 if context.get('pentecostarion_day_key'): key_candidate = "aposticha_pentecostarion"
                 elif context.get('triodion_day_key'): key_candidate = "aposticha_triodion"
                 else: key_candidate = "aposticha_resurrection"
             
             resolved_text = engine._resolve_variable_ref(key_candidate, context)

        if resolved_text:
             self._render_text_payload(resolved_text)
        else:
             self.output.append(f"\n   [VARIABLE PROPERS: {logic_name}]")

        return "\n".join(self.output)

    def _render_fixed_atomic_string(self, key):
        """Helper to render standard fixed strings like Glory/Both Now."""
        map_ = {
            "glory": "Glory to the Father and to the Son and to the Holy Spirit.",
            "both_now": "Now and for ever and ever. Amen.",
            "glory_both_now": "Glory to the Father and to the Son and to the Holy Spirit, now and for ever and ever. Amen."
        }
        text = map_.get(key, f"[{key}]")
        self.output.append(f"   {text}")

    def _resolve_and_render_atomic_component(self, engine, context, key, logic_result):
        """Resolves a specific atomic component from the sequence."""
        # This is where we map abstract keys like 'troparion_resurrection' to actual DB keys
        # We might need to extend RuthenianEngine to handle these specific lookups publically
        # For now, implementing a basic mapping here or calling an internal helper
        
        # Tone override from logic result
        current_tone = logic_result.get("tone", context.get("tone_of_week", 1))
        
        if key == "troparion_resurrection":
            # Construct key: tone_X.matins.troparion_resurrection
            # or rely on engine to resolve it. 
            # Ideally: engine.get_text(f"tone_{current_tone}.troparion.resurrection")
            # But structure might be different. Let's try to query the engine's text_db directly if possible, or use _resolve_variable_ref
            
            # Implementation Strategy: Use _resolve_variable_ref with context modification?
            # Or construct the lookup key manually since we know the schema.
            db_key = f"tone_{current_tone}.troparion.resurrection" 
            text_obj = engine.get_text(db_key)

            # Fallback if assume specific structure
            if not text_obj:
                 # Try Recension 2014 specific path
                 db_key = f"tone_{current_tone}.troparion_resurrection"
                 text_obj = engine.get_text(f"octoechos.{db_key}")

            if not text_obj:
                # Hard fallback for prototype
                text_obj = {"title": f"Resurrection Troparion (Tone {current_tone})", "content": "[Text not found in DB]"}
            
            self._render_text_payload(text_obj)

        elif key == "troparion_saint":
            # Get first saint from context
            saints = context.get("saints", [])
            if saints:
                # For prototype, just rendering a placeholder with saint name
                saint_name = saints[0].get("name", "Unknown Saint")
                self.output.append(f"   [Troparion of {saint_name}]")
            else:
                self.output.append("   [Troparion of Saint]")

        elif key == "theotokion_sunday_by_saint_tone":
             # Needs theotokion tone
             tone = logic_result.get("theotokion_tone", current_tone)
             self.output.append(f"   [Sunday Theotokion (Tone {tone})]")
        
        else:
             self.output.append(f"   [{key}]")

    def _render_text_payload(self, text_obj):
        """Standard rendering of a title/content text object."""
        title = text_obj.get('title', 'Untitled')
        content = text_obj.get('content', '')
        
        # Handle dict content (multilingual)
        if isinstance(content, dict):
            content = content.get("en", content.get("eng", str(content)))

        self.output.append(f"\n   >>> {title} <<<".upper())
        for line in content.split('\n'):
             self.output.append(f"   {line}")

    def render_stichera_countdown(self, engine, context, rubrics):
        # Re-using the logic from previous step, but now integrated into traversal
        self.add_header(f"Lord, I Call (Tone {context.get('tone', '?')})", style="sub")
        self.add_rubric("The Deacon performs the Great Censing.") 
        
        stichera_count = 10 
        
        # Default distribution if not in rubrics
        distribution = rubrics.get("variables", {}).get("vespers_stichera_distribution", [("Resurrection", 10)])
        current_num = stichera_count
        
        # 1. Pre-fetch Resurrection Texts
        res_stichera_text = None
        if hasattr(engine, '_resolve_variable_ref'):
             res_stichera_text = engine._resolve_variable_ref("stichera_resurrection", context)
             
        res_chunks = []
        if res_stichera_text:
             full_c = res_stichera_text.get('content', '')
             res_chunks = [x.strip() for x in full_c.split('\n\n') if x.strip()]

        # 2. Pre-fetch Triodion Texts
        triodion_stichera_text = None
        if hasattr(engine, '_resolve_variable_ref'):
             triodion_stichera_text = engine._resolve_variable_ref("stichera_triodion", context)
             
        triodion_chunks = []
        if triodion_stichera_text:
             full_t = triodion_stichera_text.get('content', '')
             triodion_chunks = [x.strip() for x in full_t.split('\n\n') if x.strip()]
        
        # 3. Pre-fetch Pentecostarion Texts
        pentecostarion_stichera_text = None
        if hasattr(engine, '_resolve_variable_ref'):
             pentecostarion_stichera_text = engine._resolve_variable_ref("stichera_pentecostarion", context)
             
        pentecostarion_chunks = []
        if pentecostarion_stichera_text:
             full_p = pentecostarion_stichera_text.get('content', '')
             pentecostarion_chunks = [x.strip() for x in full_p.split('\n\n') if x.strip()]

        res_chunk_idx = 0
        triodion_chunk_idx = 0
        pentecostarion_chunk_idx = 0

        for pool_name, count in distribution:
            for i in range(count):
                verse_snippet = self._get_verse_snippet(current_num)
                
                content_display = f"[VARIABLE PROPERS]: Stichera {pool_name} (Missing)"
                
                # Logic for Resurrection Pool
                if "Resurrection" in pool_name and res_chunks:
                     if res_chunk_idx < len(res_chunks):
                          content_display = f">>> {res_chunks[res_chunk_idx]} <<<"
                          res_chunk_idx += 1
                     else:
                          content_display = ">>> (Simulated Repeat / excess res stichera) <<<"

                # Logic for Triodion Pool
                elif "Triodion" in pool_name and triodion_chunks:
                     if triodion_chunk_idx < len(triodion_chunks):
                          content_display = f"*** {triodion_chunks[triodion_chunk_idx]} ***"
                          triodion_chunk_idx += 1
                     else:
                          content_display = "*** (Simulated Repeat / excess triodion stichera) ***"

                # Logic for Pentecostarion Pool
                elif "Pentecostarion" in pool_name and pentecostarion_chunks:
                     if pentecostarion_chunk_idx < len(pentecostarion_chunks):
                          content_display = f"^^^ {pentecostarion_chunks[pentecostarion_chunk_idx]} ^^^"
                          pentecostarion_chunk_idx += 1
                     else:
                          content_display = "^^^ (Simulated Repeat / excess pentecostarion stichera) ^^^"
                
                self.add_verse_slot(f"{current_num}.", verse_snippet, content_display)
                current_num -= 1
        
        self.output.append("\nGlory... Now...")
        self.output.append("    > Doxastikon & Theotokion")

    def _get_verse_snippet(self, number):
        # Encyclopedia of fixed verse incipits
        verses = {
            10: "Bring my soul out of prison",
            9: "The righteous are waiting for me",
            8: "Out of the depths I cry to You",
            7: "Let Your ears be attentive",
            6: "If You, O Lord, should take note",
            5: "For Your name's sake, O Lord",
            4: "From the morning watch until night",
            3: "For with the Lord there is mercy",
            2: "Praise the Lord all you nations",
            1: "For great is His mercy to us"
        }
        return verses.get(number, "Verse text...")

def main():
    # Test 1: Stamford (Standard)
    print(">>> Testing Version: STAMFORD <<<")
    engine_stamford = RuthenianEngine(version="stamford")
    renderer = CantorRenderer()
    os.makedirs("cantor_prototypes", exist_ok=True)
    
    scenarios = [
        ("04_dormition_vigil", date(2025, 8, 15)),
        ("02_presanctified", date(2025, 3, 26))
    ]
    
    for name, date_obj in scenarios:
        print(f"Generating {name} (Stamford)...")
        context = engine_stamford.get_liturgical_context(date_obj)
        rubrics = engine_stamford.resolve_rubrics(context)
        text_out = renderer.render_structure(engine_stamford, context, rubrics)
        
        with open(f"cantor_prototypes/{name}_stamford.txt", "w", encoding="utf-8") as f:
            f.write(text_out)

    # Test 2: Other (Empty/Alternative)
    print("\n>>> Testing Version: OTHER <<<")
    engine_other = RuthenianEngine(version="other")
    
    for name, date_obj in scenarios:
        print(f"Generating {name} (Other)...")
        context = engine_other.get_liturgical_context(date_obj)
        rubrics = engine_other.resolve_rubrics(context)
        text_out = renderer.render_structure(engine_other, context, rubrics)
        
        with open(f"cantor_prototypes/{name}_other.txt", "w", encoding="utf-8") as f:
            f.write(text_out)
            
    print("Done. Check 'cantor_prototypes' folder for versioned outputs.")

if __name__ == "__main__":
    main()
