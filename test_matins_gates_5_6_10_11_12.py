"""
Test Suite for Matins Gates 5, 6, 10, 11, 12
Tests Anabathmoi, Kathisma choice, Eothinon Doxastikon, Doxology type, and Dismissal Troparion
"""

import sys
sys.path.insert(0, 'c:/Users/augus/PycharmProjects/MyFirstGui')

from ruthenian_engine import RuthenianEngine

def test_gate_5_anabathmoi():
    """Test Gate 5: Anabathmoi Selection"""
    print("\n=== Testing Gate 5: Anabathmoi Selection ===")
    engine = RuthenianEngine()
    
    # Test 1: Great Feast - "From my youth"
    context = {
        'rank': 1,
        'feast_id': 'nativity',
        'day_of_week': 4  # Thursday
    }
    result = engine.resolve_anabathmoi(context)
    assert result['type'] == 'festal_anabathmoi'
    assert result['anabathmoi_id'] == 'from_my_youth_tone_4'
    assert result['tone'] == 4
    print("  [PASS] Great Feast uses 'From my youth' (Tone 4)")
    
    # Test 2: Sunday - Anabathmoi of the tone (Tone 1)
    context = {
        'rank': 5,
        'day_of_week': 0,
        'octoechos_week': 1
    }
    result = engine.resolve_anabathmoi(context)
    assert result['type'] == 'sunday_anabathmoi'
    assert result['tone'] == 1
    assert result['anabathmoi_id'] == 'anabathmoi_tone_1'
    print("  [PASS] Sunday (Tone 1) uses Anabathmoi of Tone 1")
    
    # Test 3: Sunday - Anabathmoi Tone 5
    context = {
        'rank': 5,
        'day_of_week': 0,
        'octoechos_week': 5
    }
    result = engine.resolve_anabathmoi(context)
    assert result['tone'] == 5
    assert result['anabathmoi_id'] == 'anabathmoi_tone_5'
    print("  [PASS] Sunday (Tone 5) uses Anabathmoi of Tone 5")
    
    # Test 4: Polyeleos Saint (weekday) - "From my youth"
    context = {
        'rank': 3,
        'saint_id': 'st_nicholas',
        'day_of_week': 4
    }
    result = engine.resolve_anabathmoi(context)
    assert result['type'] == 'polyeleos_anabathmoi'
    assert result['anabathmoi_id'] == 'from_my_youth_tone_4'
    print("  [PASS] Polyeleos Saint (weekday) uses 'From my youth'")
    
    # Test 5: Simple weekday - No Anabathmoi
    context = {
        'rank': 5,
        'day_of_week': 2
    }
    result = engine.resolve_anabathmoi(context)
    assert result['type'] == 'none'
    assert result['anabathmoi_id'] is None
    print("  [PASS] Simple weekday has no Anabathmoi")
    
    print("Gate 5: All Anabathmoi tests passed!")


def test_gate_6_kathisma_choice():
    """Test Gate 6: Kathisma 17 vs Polyeleos Choice"""
    print("\n=== Testing Gate 6: Kathisma 17 vs Polyeleos ===")
    engine = RuthenianEngine()
    
    # Test 1: Simple Sunday - Kathisma 17
    context = {
        'rank': 5,
        'day_of_week': 0,
        'season': 'ordinary'
    }
    result = engine.resolve_kathisma_choice(context)
    assert result['type'] == 'sunday_kathisma_17'
    assert result['kathisma_number'] == 17
    assert result['polyeleos'] == False
    assert 118 in result['psalms']
    print("  [PASS] Simple Sunday uses Kathisma 17 (Psalms 118-133)")
    
    # Test 2: Sunday + Polyeleos - Polyeleos replaces Kathisma 17
    context = {
        'rank': 3,
        'day_of_week': 0,
        'saint_id': 'st_john_chrysostom'
    }
    result = engine.resolve_kathisma_choice(context)
    assert result['type'] == 'polyeleos'
    assert result['kathisma_number'] == 19
    assert result['polyeleos'] == True
    assert result['psalms'] == [134, 135]
    print("  [PASS] Sunday Polyeleos uses Psalms 134-135")
    
    # Test 3: Weekday - Sequential kathisma
    context = {
        'rank': 5,
        'day_of_week': 1,
        'week_number': 1
    }
    result = engine.resolve_kathisma_choice(context)
    assert result['type'] == 'weekday_kathisma'
    assert result['polyeleos'] == False
    print("  [PASS] Weekday uses sequential kathisma")
    
    print("Gate 6: All Kathisma choice tests passed!")


def test_gate_10_eothinon_doxastikon():
    """Test Gate 10: Eothinon Doxastikon (Gospel Sticheron)"""
    print("\n=== Testing Gate 10: Eothinon Doxastikon ===")
    engine = RuthenianEngine()
    
    # Test 1: Sunday Eothinon 1 - Tone 5
    context = {
        'day_of_week': 0,
        'eothinon': 1
    }
    result = engine.resolve_eothinon_doxastikon(context)
    assert result['type'] == 'eothinon_doxastikon'
    assert result['eothinon'] == 1
    assert result['tone'] == 5
    assert result['doxastikon_id'] == 'gospel_sticheron_eothinon_1'
    print("  [PASS] Sunday Eothinon 1 uses Gospel Sticheron Tone 5")
    
    # Test 2: Sunday Eothinon 6 - Tone 7
    context = {
        'day_of_week': 0,
        'eothinon': 6
    }
    result = engine.resolve_eothinon_doxastikon(context)
    assert result['tone'] == 7
    assert result['doxastikon_id'] == 'gospel_sticheron_eothinon_6'
    print("  [PASS] Sunday Eothinon 6 uses Gospel Sticheron Tone 7")
    
    # Test 3: Sunday Eothinon 11 - Tone 2
    context = {
        'day_of_week': 0,
        'eothinon': 11
    }
    result = engine.resolve_eothinon_doxastikon(context)
    assert result['tone'] == 2
    print("  [PASS] Sunday Eothinon 11 uses Gospel Sticheron Tone 2")
    
    # Test 4: Weekday - No Doxastikon
    context = {
        'day_of_week': 3,
        'eothinon': 1
    }
    result = engine.resolve_eothinon_doxastikon(context)
    assert result['type'] == 'none'
    assert result['doxastikon_id'] is None
    print("  [PASS] Weekday has no Eothinon Doxastikon")
    
    print("Gate 10: All Eothinon Doxastikon tests passed!")


def test_gate_11_doxology_type():
    """Test Gate 11: Great vs Small Doxology"""
    print("\n=== Testing Gate 11: Doxology Type ===")
    engine = RuthenianEngine()
    
    # Test 1: Great Feast - Great Doxology
    context = {
        'rank': 1,
        'feast_id': 'theophany'
    }
    result = engine.resolve_doxology_type(context)
    assert result['type'] == 'great_doxology'
    assert result['sung'] == True
    assert result['reason'] == 'Great Feast of the Lord'
    print("  [PASS] Great Feast uses Great Doxology")
    
    # Test 2: Sunday - Great Doxology
    context = {
        'rank': 5,
        'day_of_week': 0
    }
    result = engine.resolve_doxology_type(context)
    assert result['type'] == 'great_doxology'
    assert result['sung'] == True
    assert result['reason'] == 'Sunday Resurrection'
    print("  [PASS] Sunday uses Great Doxology")
    
    # Test 3: Polyeleos Saint - Great Doxology
    context = {
        'rank': 3,
        'saint_id': 'st_basil',
        'day_of_week': 2
    }
    result = engine.resolve_doxology_type(context)
    assert result['type'] == 'great_doxology'
    assert result['sung'] == True
    assert result['reason'] == 'Polyeleos Saint'
    print("  [PASS] Polyeleos Saint uses Great Doxology")
    
    # Test 4: Saint with Doxology (rank 4) - Great Doxology
    context = {
        'rank': 4,
        'saint_id': 'st_andrew',
        'day_of_week': 6
    }
    result = engine.resolve_doxology_type(context)
    assert result['type'] == 'great_doxology'
    assert result['sung'] == True
    assert result['reason'] == 'Saint with Doxology'
    print("  [PASS] Rank 4 Saint uses Great Doxology")
    
    # Test 5: Simple weekday - Small Doxology
    context = {
        'rank': 5,
        'day_of_week': 3
    }
    result = engine.resolve_doxology_type(context)
    assert result['type'] == 'small_doxology'
    assert result['sung'] == False
    assert result['reason'] == 'Simple weekday'
    print("  [PASS] Simple weekday uses Small Doxology")
    
    print("Gate 11: All Doxology tests passed!")


def test_gate_12_dismissal_troparion():
    """Test Gate 12: Matins Dismissal Troparion"""
    print("\n=== Testing Gate 12: Matins Dismissal Troparion ===")
    engine = RuthenianEngine()
    
    # Test 1: Great Feast - Festal troparion
    context = {
        'rank': 1,
        'feast_id': 'ascension',
        'day_of_week': 4
    }
    result = engine.resolve_matins_dismissal_troparion(context)
    assert result['troparia'][0]['type'] == 'festal'
    assert result['glory_both_now'] == 'troparion_ascension'
    print("  [PASS] Great Feast uses festal troparion")
    
    # Test 2: Sunday alone - Resurrectional troparion (Tone 3)
    context = {
        'rank': 5,
        'day_of_week': 0,
        'octoechos_week': 3,
        'saint_id': None
    }
    result = engine.resolve_matins_dismissal_troparion(context)
    assert result['troparia'][0]['type'] == 'resurrectional'
    assert result['troparia'][0]['tone'] == 3
    assert result['glory_both_now'] == 'troparion_resurrection_tone_3'
    print("  [PASS] Sunday alone uses resurrectional troparion (Tone 3)")
    
    # Test 3: Sunday + Saint - Stacking
    context = {
        'rank': 4,
        'day_of_week': 0,
        'octoechos_week': 6,
        'saint_id': 'st_demetrius'
    }
    result = engine.resolve_matins_dismissal_troparion(context)
    assert result['troparia'][0]['type'] == 'resurrectional'
    assert result['troparia'][1]['type'] == 'saint'
    assert result['glory'] == 'troparion_st_demetrius'
    assert result['both_now'] == 'theotokion_tone_6'
    print("  [PASS] Sunday + Saint uses stacking (Resurrectional, Glory, Theotokion)")
    
    # Test 4: Weekday saint - Saint troparion + Theotokion
    context = {
        'rank': 5,
        'day_of_week': 2,
        'saint_id': 'st_george',
        'saint_tone': 4
    }
    result = engine.resolve_matins_dismissal_troparion(context)
    assert result['troparia'][0]['troparion_id'] == 'troparion_st_george'
    assert result['both_now'] == 'theotokion_dismissal_tone_4'
    print("  [PASS] Weekday saint uses troparion + Theotokion")
    
    # Test 5: Simple weekday - None
    context = {
        'rank': 6,
        'day_of_week': 5,
        'saint_id': None
    }
    result = engine.resolve_matins_dismissal_troparion(context)
    assert result['none'] == True
    assert result['troparia'] == []
    print("  [PASS] Simple weekday has no troparion")
    
    print("Gate 12: All Dismissal Troparion tests passed!")


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*60)
    print("MATINS GATES 5, 6, 10, 11, 12 - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    try:
        test_gate_5_anabathmoi()
        test_gate_6_kathisma_choice()
        test_gate_10_eothinon_doxastikon()
        test_gate_11_doxology_type()
        test_gate_12_dismissal_troparion()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("="*60)
        print("\nSummary:")
        print("  Gate 5 (Anabathmoi): 5 tests passed")
        print("  Gate 6 (Kathisma Choice): 3 tests passed")
        print("  Gate 10 (Eothinon Doxastikon): 4 tests passed")
        print("  Gate 11 (Doxology Type): 5 tests passed")
        print("  Gate 12 (Dismissal Troparion): 5 tests passed")
        print("  TOTAL: 22 tests passed")
        
    except AssertionError as e:
        print(f"\n[ERROR] Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
