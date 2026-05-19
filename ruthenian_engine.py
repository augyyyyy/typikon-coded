"""
Ruthenian Engine — Backward Compatibility Shim
===============================================

This module re-exports the RuthenianEngine class from the modular engine/ package.
All existing code that imports `from ruthenian_engine import RuthenianEngine` will
continue to work unchanged.

The actual implementation lives in engine/ as domain-specific mixin modules.
"""

from engine import RuthenianEngine

__all__ = ['RuthenianEngine']
