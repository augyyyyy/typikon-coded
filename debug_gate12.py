"""
Quick debug script to check what resolve_matins_dismissal_troparion returns
"""

import sys
sys.path.insert(0, 'c:/Users/augus/PycharmProjects/MyFirstGui')

from ruthenian_engine import RuthenianEngine

engine = RuthenianEngine()

# Test 1: Great Feast
context = {
    'rank': 1,
    'feast_id': 'ascension',
    'day_of_week': 4
}

print("Testing Great Feast context:")
print(context)
result = engine.resolve_matins_dismissal_troparion(context)
print("\nResult:")
print(result)
print(f"\nType: {type(result)}")
print(f"Keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
