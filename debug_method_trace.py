"""
Debug script to trace method resolution
"""

import sys
sys.path.insert(0, 'c:/Users/augus/PycharmProjects/MyFirstGui')

from ruthenian_engine import RuthenianEngine
import inspect

engine = RuthenianEngine()

# Get the method object
method = getattr(engine, 'resolve_matins_dismissal_troparion')

print(f"Method: {method}")
print(f"Source file: {inspect.getfile(method)}")
print(f"Line number: {inspect.getsourcelines(method)[1]}")
print(f"\nFirst 20 lines of source:")
print("".join(inspect.getsourcelines(method)[0][:20]))
