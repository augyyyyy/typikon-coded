"""
Test Suite for Matins Gates 7-8
Tests Katavasia selection and Magnificat at Ode 9
"""

import sys
sys.path.insert(0, 'c:/Users/augus/PycharmProjects/MyFirstGui')

from ruthenian_engine import RuthenianEngine

def test_gate_7_katavasia():
    """Test Gate 7: Katavasia Selection"""
    print("\n=== Testing Gate 7: Katavasia Selection ===")
    engine = RuthenianEngine()
    
    # Test 1: Great Feast - Katavasia after EVERY ode
    context = {
        'rank': 1,
        'feast_id': 'nativity',
        'season': 'ordinary'
    }
    result = engine.resolve_katavasia(context)
    assert result['type'] == 'festal_katavasia'
    assert result['after_odes'] == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert result['frequency'] == 'after_each_ode'
    print("  [PASS] Great Feast uses festal Katavasia after all 9 odes")
    
    # Test 2: Pascha - Paschal Katavasia every ode
    context = {
        'rank': 5,
        'season': 'pascha',
        'day_of_week': 0
    }
    result = engine.resolve_katavasia(context)
    assert result['type'] == 'paschal_katavasia'
    assert result['katavasia_id'] == 'katavasia_pascha'
    assert result['after_odes'] == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    print("  [PASS] Pascha uses Paschal Katavasia after all 9 odes")
    
    # Test 3: Polyeleos Saint - Limited odes (3, 6, 8, 9)
    context = {
        'rank': 3,
        'saint_id': 'st_nicholas',
        'season': 'ordinary',
        'day_of_week': 4
    }
    result = engine.resolve_katavasia(context)
    assert result['type'] == 'polyeleos_katavasia'
    assert result['after_odes'] == [3, 6, 8, 9]
    assert result['frequency'] == 'limited_odes'
    print("  [PASS] Polyeleos uses irmos of last canon after odes 3, 6, 8, 9")
    
    # Test 4: Meatfare Sunday - Triodion Katavasia all odes
    context = {
        'rank': 5,
        'feast_id': 'meatfare_sunday',
        'season': 'triodion',
        'day_of_week': 0
    }
    result = engine.resolve_katavasia(context)
    assert result['type'] == 'triodion_katavasia'
    assert result['after_odes'] == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    print("  [PASS] Meatfare Sunday uses Triodion Katavasia after all odes")
    
    # Test 5: Lenten weekday - Limited odes only
    context = {
        'rank': 5,
        'season': 'great_lent',
        'day_of_week': 2  # Tuesday
    }
    result = engine.resolve_katavasia(context)
    assert result['type'] == 'lenten_katavasia'
    assert result['after_odes'] == [3, 6, 8, 9]
    print("  [PASS] Lenten weekday uses limited odes (3, 6, 8, 9)")
    
    # Test 6: Meeting season - Festal Katavasia
    context = {
        'rank': 5,
        'season': 'meeting_season',
        'day_of_week': 3
    }
    result = engine.resolve_katavasia(context)
    assert result['type'] == 'festal_katavasia'
    assert result['katavasia_id'] == 'katavasia_meeting'
    assert result['after_odes'] == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    print("  [PASS] Meeting season uses Meeting Katavasia after all odes")
    
    # Test 7: Simple weekday - "I will open my mouth"
    context = {
        'rank': 5,
        'season': 'ordinary',
        'day_of_week': 3
    }
    result = engine.resolve_katavasia(context)
    assert result['type'] == 'general_katavasia'
    assert result['katavasia_id'] == 'i_will_open_my_mouth'
    assert result['after_odes'] == [3, 6, 8, 9]
    assert 'I will open my mouth' in result['text']
    print("  [PASS] Simple weekday uses 'I will open my mouth' after odes 3, 6, 8, 9")
    
    print("Gate 7: All Katavasia tests passed!")


def test_gate_8_magnificat():
    """Test Gate 8: Magnificat at Ode 9"""
    print("\n=== Testing Gate 8: Magnificat at Ode 9 ===")
    engine = RuthenianEngine()
    
    # Test 1: Pascha - "Angel cried out" (no Axion Estin)
    context = {
        'rank': 5,
        'season': 'pascha',
        'day_of_week': 0
    }
    result = engine.resolve_magnificat(context)
    assert result['type'] == 'paschal_magnificat'
    assert result['axion_estin'] == False
    assert result['magnificat_id'] == 'angel_cried_out'
    print("  [PASS] Pascha uses 'Angel cried out' (no 'It is truly meet')")
    
    # Test 2: Theophany (Great Feast) - Festal irmos replaces Axion
    context = {
        'rank': 1,
        'feast_id': 'theophany',
        'season': 'ordinary'
    }
    result = engine.resolve_magnificat(context)
    assert result['type'] == 'festal_magnificat'
    assert result['axion_estin'] == False
    assert result['more_honorable'] == False
    print("  [PASS] Theophany uses festal irmos instead of 'It is truly meet'")
    
    # Test 3: Ascension (Great Feast) - More honorable + festal irmos
    context = {
        'rank': 1,
        'feast_id': 'ascension',
        'season': 'ordinary'
    }
    result = engine.resolve_magnificat(context)
    assert result['type'] == 'festal_with_more_honorable'
    assert result['axion_estin'] == False
    assert result['more_honorable'] == True
    print("  [PASS] Ascension uses 'More honorable' + festal irmos")
    
    # Test 4: Sunday - Irmos replaces Axion (Tone 6)
    context = {
        'rank': 5,
        'day_of_week': 0,
        'octoechos_week': 6,
        'eothinon': 5
    }
    result = engine.resolve_magnificat(context)
    assert result['type'] == 'sunday_magnificat'
    assert result['axion_estin'] == False
    assert result['tone'] == 6
    assert 'irmos_ode_9_tone_6' in result['magnificat_id']
    print("  [PASS] Sunday uses irmos of Tone 6 instead of 'It is truly meet'")
    
    # Test 5: Polyeleos Saint - Irmos of last canon
    context = {
        'rank': 3,
        'saint_id': 'st_basil',
        'day_of_week': 2
    }
    result = engine.resolve_magnificat(context)
    assert result['type'] == 'polyeleos_magnificat'
    assert result['axion_estin'] == False
    print("  [PASS] Polyeleos uses irmos of last canon instead of Axion")
    
    # Test 6: Simple weekday - "It is truly meet"
    context = {
        'rank': 5,
        'day_of_week': 4,
        'season': 'ordinary'
    }
    result = engine.resolve_magnificat(context)
    assert result['type'] == 'default_magnificat'
    assert result['axion_estin'] == True
    assert result['magnificat_id'] == 'it_is_truly_meet'
    print("  [PASS] Simple weekday uses 'It is truly meet'")
    
    print("Gate 8: All Magnificat tests passed!")


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*60)
    print("MATINS GATES 7-8 - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    try:
        test_gate_7_katavasia()
        test_gate_8_magnificat()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("="*60)
        print("\nSummary:")
        print("  Gate 7 (Katavasia): 7 tests passed")
        print("  Gate 8 (Magnificat): 6 tests passed")
        print("  TOTAL: 13 tests passed")
        
    except AssertionError as e:
        print(f"\n[ERROR] Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
