import json
import os
from ruthenian_engine import RuthenianEngine

def verify_db_keys():
    engine = RuthenianEngine(base_dir=r"c:\Users\augus\PycharmProjects\MyFirstGui")
    print(f"Total Text Items: {len(engine.text_db)}")
    
    # Check for Tone 1 Stichera
    key = "tone_1.sat_vespers.stichera_lord_i_call"
    if key in engine.text_db:
        print(f"Found: {key}")
        print(engine.text_db[key]['content'][:50] + "...")
    else:
        print(f"MISSING: {key}")
        
    # Check for Eothinon 1
    key = "eothinon_1_gospel"
    if key in engine.text_db:
        print(f"Found: {key}")
    else:
        print(f"MISSING: {key}")

if __name__ == "__main__":
    verify_db_keys()
