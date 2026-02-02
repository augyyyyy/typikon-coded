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
        self.output.append(f"\n   [STRUCTURE: {ref_key.upper()}]")

    def _render_text_payload(self, text_obj):
        if isinstance(text_obj, dict):
            title = text_obj.get("title", "Unknown Text")
            self.output.append(f"   [CONTENT: {title}]")
        else:
            self.output.append(f"   [CONTENT: {str(text_obj)[:50]}...]")

    def _render_variable_item(self, engine, context, logic_name):
        self.output.append(f"\n   [LOGIC START: {logic_name}]")
        try:
            result = super()._render_variable_item(engine, context, logic_name)
        except Exception as e:
            self.output.append(f"   [LOGIC ERROR: {e}]")
            result = None
        self.output.append(f"   [LOGIC END: {logic_name}]")
        return result

    def _render_fixed_atomic_string(self, key):
         self.output.append(f"   [ATOMIC: {key}]")

    def _resolve_and_render_atomic_component(self, engine, context, key, logic_result):
        tone = logic_result.get("tone", "?")
        self.output.append(f"      -> [COMPONENT: {key} (Tone {tone})]")

def run_audit(label, date_str, expected_type):
    print(f"\n--- Auditing {label} [{date_str}] ---")
    engine = RuthenianEngine(base_dir=".")
    
    parts = date_str.split("-")
    test_date = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
    
    context = engine.get_liturgical_context(test_date)
    
    # Prime the scenario logic
    scenario_id = engine.identify_scenario(context)
    
    # Force tone if missing
    if 'tone' not in context:
        context['tone'] = 1
        context['tone_of_week'] = 1
        
    print(f"Scenario: {context.get('scenario_description')} | Season: {context.get('season')} | Tone: {context.get('tone')}")
    
    # Load Structure
    json_path = "json_db/01i_struct_matins.json"
    if not os.path.exists(json_path):
        print(f"CRITICAL ERROR: Structure file missing.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        struct_data = json.load(f)

    # Resolve Sequence
    sequence = engine._get_structure_sequence(struct_data, "great_matins")
    
    renderer = StructuralRenderer()
    renderer.output.append(f"=== MATINS SKELETON: {label.upper()} ({date_str}) ===\n")
    
    for slot in sequence:
        slot_id = slot.get("id", "unknown")
        renderer.output.append(f"\n>> {slot_id.upper()} <<")
        renderer.render_slot(engine, context, slot, struct_data)

    out_name = f"cantor_prototypes/skeleton_{label.lower().replace(' ', '_')}.txt"
    os.makedirs(os.path.dirname(out_name), exist_ok=True)
    with open(out_name, "w", encoding="utf-8") as f:
        f.write("\n".join(renderer.output))
    print(f"Saved to {out_name}")

if __name__ == "__main__":
    # 1. Sunday Matins (Standard)
    run_audit("Sunday Matins", "2026-01-04", "Sunday") # Tone 6
    
    # 2. Daily Matins (Weekday)
    # Jan 7, 2026 is Wednesday after Theophany (Post-feast)
    # Let's pick a generic non-feast Wednesday: Jan 21, 2026 (St. Maximus Confessor?)
    # Jan 21 is Wed.
    run_audit("Daily Matins", "2026-01-21", "Weekday")
    
    # 3. Lenten Matins
    # Lent 2026 starts Feb 16. Feb 18 is Wednesday.
    run_audit("Lenten Matins", "2026-02-18", "Lent")
