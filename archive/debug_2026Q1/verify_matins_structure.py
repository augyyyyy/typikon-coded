import sys
import os
import datetime
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ruthenian_engine import RuthenianEngine
from generate_cantor_prototype import CantorRenderer

class StructuralRenderer(CantorRenderer):
    """
    Subclass that overrides text rendering to showing only structural markers.
    """
    def _render_text_item(self, engine, ref_key):
        # Override to just show the slot/key
        self.output.append(f"\n   [STRUCTURE: {ref_key.upper()}]")
        # Do NOT render content

    def _render_text_payload(self, text_obj):
        # Override to just show the title or type
        if isinstance(text_obj, dict):
            title = text_obj.get("title", "Unknown Text")
            source = text_obj.get("source", "Unknown Source")
            self.output.append(f"   [CONTENT: {title} | Source: {source}]")
        else:
            self.output.append(f"   [CONTENT: {str(text_obj)[:50]}...]")

    def _render_variable_item(self, engine, context, logic_name):
        # Wrap the parent logic to show what rule fired, but suppress inner text
        self.output.append(f"\n   [LOGIC START: {logic_name}]")
        result = super()._render_variable_item(engine, context, logic_name)
        # The parent renderer might append text to self.output, which we want to avoid if possible.
        # Actually, super() calls _render_text_payload or _render_fixed_atomic_string
        # We need to ensure those methods in THIS class are used.
        # Since they are instance methods, they should be.
        self.output.append(f"   [LOGIC END: {logic_name}]")
        return result

    def _render_fixed_atomic_string(self, key):
         self.output.append(f"   [ATOMIC: {key}]")

    def _resolve_and_render_atomic_component(self, engine, context, key, logic_result):
        # Show what component is being requested, but don't dump the text
        tone = logic_result.get("tone", "?")
        self.output.append(f"      -> [COMPONENT: {key} (Tone {tone})]")

def main():
    print("Initializing Engine for Matins Structural Verification...")
    engine = RuthenianEngine(base_dir=".")
    
    # Test Date: Jan 4, 2026 (Sunday)
    test_date = datetime.date(2026, 1, 4)
    print(f"Testing Date: {test_date}")
    
    context = engine.get_liturgical_context(test_date)
    scenario_id = engine.identify_scenario(context)
    print(f"Scenario ID: {scenario_id}")
    
    # Mock Tone if needed
    if 'tone' not in context:
        context['tone'] = 6
        context['tone_of_week'] = 6
    
    print(f"Context Info: {context.get('scenario_description', 'normal')} | Tone: {context.get('tone')}")

    # Load Structure
    print("Loading Matins Structure...")
    # NOTE: We need to access the engine's loaded structure directly or via a public method if available.
    # RuthenianEngine loads matins logic into self.matins_logic
    # But usually we render a specific "rubric" file or top-level key.
    
    # Looking at verify_matins_output.py, we need the structure.
    # Assuming standard daily matins structure for now, or determining from logic.
    structure = engine.matins_logic # This is the full logic file content
    
    # We need the ordered sequence of events.
    # Usually this is defined in a 'structure' file (e.g. 01i_struct_matins.json)
    import json
    json_path = "json_db/01i_struct_matins.json"
    
    if not os.path.exists(json_path):
        print(f"CRITICAL ERROR: File not found at {os.path.abspath(json_path)}")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            struct_data = json.load(f)
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to parse JSON: {e}")
        return

    rubrics = struct_data # For compatibility with render_slot if it expects dict
    
    # Traverse top-level slots
    sequence = engine._get_structure_sequence(struct_data, "great_matins")
    
    if not sequence:
         print("ERROR: Could not resolve sequence for 'great_matins'")
         return
         
    print(f"Resolved Sequence: {len(sequence)} high-level slots")

    # Use our Structural Renderer
    renderer = StructuralRenderer()

    print("Rendering Structure...")
    renderer.output.append("=== MATINS STRUCTURE SKELETON ===\n")
    
    for slot in sequence:
        slot_id = slot.get("id", "unknown")
        renderer.output.append(f"\n>> {slot_id.upper()} <<")
        renderer.render_slot(engine, context, slot, rubrics)

    # Output
    out_path = "cantor_prototypes/matins_structure_skeleton.txt"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(renderer.output))
        
    print(f"Saved structure skeleton to {out_path}")

if __name__ == "__main__":
    main()
