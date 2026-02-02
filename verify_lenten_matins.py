
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
    Generates a skeleton for Lenten Matins (Weekday) to audit against Dolnytsky.
    Target: First Monday of Great Lent (Clean Monday).
    """
    logging.basicConfig(level=logging.INFO)
    
    engine = RuthenianEngine("Let's Audit")
    renderer = CantorRenderer()
    
    # Context for Clean Monday (Lenten Weekday)
    # 2026-02-16 is Clean Monday (Gregorian for 2026 check? Or just hypothetical)
    # Let's force strict inputs to ensure Lenten logic triggers.
    context = {
        "date": "2026-02-16", # Clean Monday
        "day_of_week": 1, # Monday
        "service_type": "lenten_matins", # Explicit type to help logic
        "tone": 1, 
        "period": "triodion",
        "is_lent": True,
        "mode": "text_only",
        "components_mask": ["matins"]
    }
    
    print(f"--- GENERATING SKELETON FOR LENTEN MATINS (Clean Monday) ---")
    
    print(f"--- GENERATING SKELETON FOR LENTEN MATINS (Clean Monday) ---")
    
    # 1. Load Structure Manualy
    # 1. Load Structure Manually (Debug Mode)
    json_rel_path = "json_db/01i_struct_matins.json"
    print(f"DEBUG: Loading JSON from relative path: {json_rel_path}")
    print(f"DEBUG: CWD: {os.getcwd()}")
    
    struct_data = {}
    try:
        with open(json_rel_path, 'r', encoding='utf-8') as f:
            struct_data = json.load(f)
        print("DEBUG: JSON Load Success")
    except Exception as e:
        print(f"DEBUG: JSON Load Failed: {e}")
        return

    root_id = "lenten_matins_weekday"
    
    # DEBUG
    print(f"Loaded keys: {list(struct_data.get('structures', {}).keys())}")

    # 2. Get Sequence
    # RuthenianEngine._get_structure_sequence might need access. 
    # If it's private, we access it via engine or reimplement lookup.
    # Looking at prototype, it accesses engine._get_structure_sequence.
    sequence = engine._get_structure_sequence(struct_data, root_id)
    
    if not sequence:
        print(f"Error: Sequence for {root_id} not found.")
        return

    # 3. Render Skeleton Loop
    c_rubrics = {"title": "Lenten Matins (Clean Monday)"}
    renderer.add_header("LENTEN MATINS SKELETON", style="main")
    
    for slot in sequence:
        renderer.render_slot(engine, context, slot, c_rubrics)
    
    # 4. Save
    output_path = os.path.join("cantor_prototypes", "skeleton_lenten_matins.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(renderer.output))
        
    print(f"Skeleton saved to {output_path}")

if __name__ == "__main__":
    run_audit()
