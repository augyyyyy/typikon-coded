from ruthenian_engine import RuthenianEngine
import datetime

def test_ingestion():
    engine = RuthenianEngine(version="stamford_2014")
    
    print("--- 1. Testing Weekday Troparia (Monday) ---")
    # Monday = Angels. Key: weekday.monday.troparion
    # Text start: "Princes of the heavenly hosts"
    text = engine.get_text("weekday.monday.troparion")
    if text and "Princes of the heavenly hosts" in text["content"]:
        print("[PASS] Weekday Monday Troparion found.")
    else:
        print(f"[FAIL] Weekday Monday Troparion missing or wrong. Got: {text}")

    print("\n--- 2. Testing Theotokia (Tone 1 Resurrectional) ---")
    # Key: theotokion.tone_1.resurrectional
    # Text start: "O holy tabernacle"
    text = engine.get_text("theotokion.tone_1.resurrectional")
    if text and "O holy tabernacle" in text["content"]:
        print("[PASS] Theotokion Tone 1 Resurrectional found.")
    else:
        print(f"[FAIL] Theotokia missing or wrong. Got: {text}")

    print("\n--- 3. Testing General Menaion Fallback (St. Timothy) ---")
    # Mock context for St. Timothy (Apostle)
    ctx = {
        "saint_class": "Apostle",
        "st_name": "Timothy"
    }
    # Direct lookup of the fallback logic via get_text specific flow (simulated)
    # The get_text logic does: if logic_requirement provided -> check fallback. 
    # Or strict lookup of general key. 
    
    # Let's test the Engine's direct access to the general DB first
    gen_text = engine.general_menaion_db.get("general.apostle.troparion")
    if gen_text and "Holy apostle" in gen_text["content"] and gen_text.get("source") == "Stamford":
        print("[PASS] General Menaion DB loaded with Stamford source.")
    else:
        print(f"[FAIL] General Menaion DB not overlaid correcty. Got: {gen_text}")
        
    # Now test the fallback mechanism via a FAILING key
    # text_id="menaion.01_22.troparion" (which doesn't exist)
    # context={"saint_class": "Apostle", "st_name": "Timothy"}
    
    fallback = engine.get_text("menaion.01_22.troparion", context=ctx)
    if fallback and "Holy apostle Timothy" in fallback["content"]:
        print("[PASS] Fallback mechanism correctly rendered 'Timothy'.")
    else:
        print(f"[FAIL] Fallback mechanism failed. Got: {fallback}")

    print("\n--- 4. Testing Triodion (Publican and Pharisee) ---")
    # key: triodion.publican_pharisee.kontakion
    # Text: "Let us bring to the Lord the sighs"
    tri_text = engine.get_text("triodion.publican_pharisee.kontakion")
    if tri_text and "sighs of the publican" in tri_text["content"]:
        print("[PASS] Triodion Publican/Pharisee Kontakion found.")
    else:
        print(f"[FAIL] Triodion missing. Got: {tri_text}")

if __name__ == "__main__":
    test_ingestion()
