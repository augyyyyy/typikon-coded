
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
    Generates a skeleton for Festal Matins (Transfiguration) to audit against Dolnytsky.
    Target: August 6 (Transfiguration).
    """
    logging.basicConfig(level=logging.INFO)
    
    engine = RuthenianEngine("Let's Audit")
    renderer = CantorRenderer()
    
    # Context for Transfiguration (Feast of the Lord)
    # Aug 6
    context = {
        "date": "2026-08-06", 
        "day_of_week": 3, # Thursday (Example)
        "service_type": "great_matins", 
        "tone": 7, # Transfiguration uses specific tones, but logic should override
        "period": "pentecostarion", # Technically outside, but logic handles fixed feasts
        "feast_level": "lord",
        "is_feast": True,
        "mode": "text_only",
        "components_mask": ["matins"]
    }
    
    print(f"--- GENERATING SKELETON FOR FESTAL MATINS (Transfiguration) ---")
    
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

    # Root for Great Matins is 'great_matins'
    root_id = "great_matins"
    
    # 2. Get Sequence
    sequence = engine._get_structure_sequence(struct_data, root_id)
    
    if not sequence:
        print(f"Error: Sequence for {root_id} not found.")
        return

    # 3. Render Skeleton Loop
    c_rubrics = {"title": "Festal Matins (Transfiguration)"}
    renderer.add_header("FESTAL MATINS SKELETON", style="main")
    
    for slot in sequence:
        renderer.render_slot(engine, context, slot, c_rubrics)
    
    # 4. Save
    output_path = os.path.join("cantor_prototypes", "skeleton_festal_matins.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(renderer.output))
        
    print(f"Skeleton saved to {output_path}")

if __name__ == "__main__":
    run_audit()
