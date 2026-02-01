"""
Integration Test Suite for Matins Engine
Verifies that the new dynamic JSON structure correctly calls the Python logic gates.
"""

import sys
import json
from datetime import date
sys.path.insert(0, 'c:/Users/augus/PycharmProjects/MyFirstGui')

from ruthenian_engine import RuthenianEngine

def test_integration_sunday_publican_pharisee():
    """
    Test Case 1: Sunday of Publican and Pharisee (Triodion Begins)
    Date: Feb 1, 2026
    Expectations:
    - Gate 6: Polyeleos (Psalm 135) or Kathisma 17? (Usually Polyeleos in Triodion?)
      Actually, Triodion Sundays usually have Polyeleos.
    - Gate 5: Anabathmoi (Tone 1, as Publican is Week 1 of Triodion... wait, no.
      Feb 1 2026 is Sunday of Prodigal Son actually?
      Pascha 2026 is April 12.
      Lent begins Feb 23.
      Meatfare Feb 15.
      Publican Jan 25.
      Prodigal Feb 1.
      So Feb 1 is Prodigal Son. Tone 2 (seq from Jan 25 Tone 1).
      
    Let's stick to checking if the resolution functions are CALLED and return valid structures.
    """
    print("\n=== Integration Test: Sunday of Prodigal Son (Feb 1, 2026) ===")
    engine = RuthenianEngine()
    
    # Context mimicking what the engine would build
    context = {
        'date': date(2026, 2, 1),
        'day_of_week': 0, # Sunday
        'rank': 5, # Sunday (Resurrection)
        'tone': 2,
        'eothinon': 2,
        'season': 'triodion', # Prodigal Son is in Triodion period
        'feast_id': 'prodigal_son'
    }
    
    # 1. Test Gate 6 (Kathisma/Polyeleos)
    print("Checking Gate 6 (Kathisma Choice)...")
    k_choice = engine.resolve_kathisma_choice(context)
    print(f"  Result: {k_choice['type']}")
    # On Prodigal Son, we usually sing Polyeleos "By the waters of Babylon" (Ps 136) too
    # But for now, ensuring it returns 'polyeleos' or 'kathisma' is enough integration proof.
    assert k_choice['type'] in ['sunday_kathisma_17', 'polyeleos']
    
    # 2. Test Gate 7 (Katavasia)
    print("Checking Gate 7 (Katavasia)...")
    katavasia = engine.resolve_katavasia(context)
    print(f"  Result: {katavasia['type']} ({katavasia.get('katavasia_id')})")
    # Should probably be Triodion or General?
    # Prodigal son might just use general or specific
    assert 'katavasia' in katavasia['type']
    
    # 3. Test Gate 8 (Magnificat)
    print("Checking Gate 8 (Magnificat)...")
    magnificat = engine.resolve_magnificat(context)
    print(f"  Result: {magnificat['type']}")
    # Sunday -> "More honorable" (unless feast overrides)
    assert magnificat['type'] == 'sunday_magnificat' or magnificat['type'] == 'default_magnificat'
    
    # 4. Test Gate 12 (Dismissal)
    print("Checking Gate 12 (Dismissal Troparion)...")
    dismissal = engine.resolve_matins_dismissal_troparion(context)
    print(f"  Result Keys: {dismissal.keys()}")
    assert 'troparia' in dismissal
    
    print("  [PASS] Logic gates returned valid structures.")

def test_integration_great_feast_meeting():
    """
    Test Case 2: Meeting of the Lord (Feb 2, 2026)
    Expectations:
    - Festal Anabathmoi
    - Festal Katavasia (all odes)
    - Festal Magnificat (no Axion Estin)
    """
    print("\n=== Integration Test: Meeting of the Lord (Feb 2, 2026) ===")
    engine = RuthenianEngine()
    
    context = {
        'date': date(2026, 2, 2),
        'day_of_week': 1, # Monday
        'rank': 1, # Great Feast
        'feast_id': 'meeting',
        'season': 'meeting_season'
    }
    
    # Gate 7: Feast -> All Odes
    print("Checking Gate 7 (Katavasia)...")
    kat = engine.resolve_katavasia(context)
    print(f"  Result: {kat['type']} (Odes: {kat.get('after_odes')})")
    assert kat['type'] == 'festal_katavasia'
    assert len(kat['after_odes']) == 9
    
    # Gate 8: Magnificat -> Festal Irmos
    print("Checking Gate 8 (Magnificat)...")
    mag = engine.resolve_magnificat(context)
    print(f"  Result: {mag['type']}")
    assert mag['type'] == 'festal_magnificat'
    assert mag['axion_estin'] is False

    print("  [PASS] Meeting of the Lord gates correct.")

if __name__ == "__main__":
    try:
        test_integration_sunday_publican_pharisee()
        test_integration_great_feast_meeting()
        print("\nINTEGRATION TESTS PASSED")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise
