from ruthenian_engine import RuthenianEngine
from datetime import date
import json
import os

class CantorRenderer:
    def __init__(self):
        self.output = []

    def add_header(self, text, style="main"):
        if style == "main":
            self.output.append(f"\n{'='*40}")
            self.output.append(f"{text.upper().center(40)}")
            self.output.append(f"{'='*40}\n")
        elif style == "sub":
            self.output.append(f"\n{text}")
            self.output.append("-" * len(text))
    
    def add_rubric(self, text):
        # Simulating the "Red Text" from screenshots with a distinct marker
        self.output.append(f"\n   [!] RUBRIC: {text}")

    def add_verse_slot(self, number, verse_text, content_desc):
        self.output.append(f"\n{number:<3} {verse_text}...")
        self.output.append(f"    > {content_desc}")

    def render_seasonal_box(self, condition, content):
        # Mimics the boxed seasonal logic from screenshots
        box_width = 60
        self.output.append(f"\n+{'-' * (box_width - 2)}+")
        self.output.append(f"| {condition.upper().ljust(box_width - 4)} |")
        self.output.append(f"+{'-' * (box_width - 2)}+")
        for line in content:
            self.output.append(f"| {line.ljust(box_width - 4)} |")
        self.output.append(f"+{'-' * (box_width - 2)}+")

    def render_actor_rubric(self, actor, text):
        # Mimics the Red Actor text (DEACON: Text)
        self.output.append(f"\n   [{actor.upper()}]: {text}")

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

        self.add_header("GREAT VESPERS", style="main")
        
        # 3. Traverse and Render
        for slot in sequence:
            slot_id = slot.get("id", "unknown")
            
            # --- RENDER RUBRICS (The "Red Text") ---
            if "rubric" in slot:
                r = slot["rubric"]
                # Title -> Sub-header
                if "title" in r:
                    self.add_header(r["title"], style="sub")
                
                # Source Ref -> Tiny rubric
                if "source_ref" in r:
                    self.output.append(f"   (Source: {r['source_ref']})")

                # Roles -> Actor Dialogue (The red text lines)
                if "roles" in r:
                    for role, text in r["roles"].items():
                        self.render_actor_rubric(role, text)

            # --- RENDER CONTENT ---
            # Special Handling for specific IDs (The "Visual Logic")
            if slot_id == "opening_vigil":
                # In real life, we would call engine.resolve_seasonal_opening(context)
                # Here we mimic the result of that logic for the box view
                if "pascha" in context["triodion_period"]:
                    self.render_seasonal_box("Paschal Season", ["Christ is Risen (3x)", "Let God Arise..."])
                else:
                    self.render_seasonal_box("Standard / Lent", ["Glory to the Holy, Consubstantial...", "Come, let us worship (3x)"])
            
            elif slot_id == "lord_i_have_cried_10":
                # Render the Stichera Countdown
                self.render_stichera_countdown(engine, context, rubrics)
                
            elif slot_id == "canon_block":
                # Only render canon if applicable
                if "matins" in rubrics.get("variables", {}).get("matins_type", "great_matins") or "vigil" in rubrics.get("title", "").lower():
                    self.render_canon(engine, context, rubrics)

            else:
                # Generic Content Fallback
                content = slot.get("content", {})
                c_type = content.get("type")
                if c_type == "fixed_ref":
                    ref_key = content.get('ref_key')
                    
                    # Normalize and Lookup
                    lookup_keys = [ref_key, ref_key.replace("horologion.", "")]
                    
                    # Aliases
                    if "litany_great" in ref_key: lookup_keys.append("litany_peace")
                    if "litany_small" in ref_key: lookup_keys.append("litany_peace") # Reuse for now
                    if "dismissal" in ref_key: lookup_keys.append("dismissal")

                    item = None
                    for k in lookup_keys:
                        if hasattr(engine, 'text_db') and k in engine.text_db:
                            item = engine.text_db[k]
                            break
                    
                    if item:
                        self.output.append(f"\n   >>> {item.get('title', ref_key)} <<<".upper())
                        text_lines = item.get('content', '').split('\n')
                        for line in text_lines:
                             # Truncate very long texts for prototype? No, user wants full text.
                             self.output.append(f"   {line}")
                    else:
                         self.output.append(f"\n   [MISSING TEXT: {ref_key}] (Not found in Horologion)")

                elif c_type == "variable_logic":
                    logic_name = content.get("logic", {}).get("function", "Unknown Logic")
                    
                    # Try to resolve text content via Engine (Octoechos/Eothinon)
                    resolved_text = None
                    if hasattr(engine, '_resolve_variable_ref'):
                         # Strip "resolve_" to get the key candidate
                         key_candidate = logic_name.replace("resolve_", "")
                         # Helper logic to match simpler keys if needed
                         if "stichera_resurrection" in logic_name: key_candidate = "stichera_resurrection"
                         if "aposticha" in logic_name:
                             if context.get('pentecostarion_day_key'):
                                 key_candidate = "aposticha_pentecostarion"
                             elif context.get('triodion_day_key'):
                                 key_candidate = "aposticha_triodion"
                             else:
                                 key_candidate = "aposticha_resurrection"
                         if "troparia_resurrection" in logic_name: key_candidate = "troparion_resurrection"
                         if "sessional_resurrection" in logic_name: key_candidate = "sessional_resurrection_1" # Hack for now
                         
                         resolved_text = engine._resolve_variable_ref(key_candidate, context)

                    if resolved_text:
                         self.output.append(f"\n   >>> {resolved_text.get('title', logic_name)} <<<".upper())
                         text_lines = resolved_text.get('content', '').split('\n')
                         for line in text_lines:
                              self.output.append(f"   {line}")
                    else:
                         self.output.append(f"\n   [VARIABLE PROPERS: {logic_name}]")
                         self.output.append("   (Text not yet integrated or Missing from Octoechos)")

        return "\n".join(self.output)

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
