
import sys
import os
import json
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ruthenian_engine import RuthenianEngine
from generate_cantor_prototype import CantorRenderer

def run_audit():
    """
    Generates a skeleton for Paschal Matins (Resurrection Sunday).
    Target: Pascha.
    """
    logging.basicConfig(level=logging.INFO)
    
    engine = RuthenianEngine("Let's Audit")
    renderer = CantorRenderer()
    
    # Context for Pascha
    context = {
        "date": "2026-04-05", # Pascha 2026
        "day_of_week": 0, 
        "service_type": "bright_matins", # Explicit
        "tone": 1, 
        "period": "pentecostarion",
        "is_pascha": True,
        "feast_level": "lord",
        "mode": "text_only",
        "components_mask": ["matins"]
    }
    
    print(f"--- GENERATING SKELETON FOR PASCHAL MATINS ---")
    
    # 1. Load Structure Manually (Debug Mode)
    json_rel_path = "json_db/01i_struct_matins.json"
    print(f"DEBUG: Loading JSON from relative path: {json_rel_path}")
    
    struct_data = {}
    try:
        with open(json_rel_path, 'r', encoding='utf-8') as f:
            struct_data = json.load(f)
    except Exception as e:
        print(f"DEBUG: JSON Load Failed: {e}")
        return

    # Root for Paschal Matins is 'bright_matins'
    root_id = "bright_matins"
    
    # 2. Get Sequence
    sequence = engine._get_structure_sequence(struct_data, root_id)
    
    if not sequence:
        print(f"Error: Sequence for {root_id} not found.")
        return

    # 3. Render Skeleton Loop
    c_rubrics = {"title": "Paschal Matins"}
    renderer.add_header("PASCHAL MATINS SKELETON", style="main")
    
    for slot in sequence:
        renderer.render_slot(engine, context, slot, c_rubrics)
    
    # 4. Save
    output_path = os.path.join("cantor_prototypes", "skeleton_paschal_matins.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(renderer.output))
        
    print(f"Skeleton saved to {output_path}")

if __name__ == "__main__":
    run_audit()
