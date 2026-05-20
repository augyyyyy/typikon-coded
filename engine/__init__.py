"""
Ruthenian Typikon Engine — Modular Architecture
================================================

This package provides the RuthenianEngine class, composed from domain-specific
mixin modules. The public API is identical to the original monolithic class.

Usage:
    from engine import RuthenianEngine
"""

from engine.core import EngineCore
from engine.text_db import TextDBMixin
from engine.calendar import CalendarMixin
from engine.rubrics import RubricsMixin
from engine.generation import GenerationMixin
from engine.resolvers.vespers import VespersMixin
from engine.resolvers.matins import MatinsMixin
from engine.resolvers.liturgy import LiturgyMixin
from engine.resolvers.hours import HoursMixin
from engine.resolvers.compline import ComplineMixin
from engine.resolvers.lenten import LentenMixin
from engine.resolvers.paschal import PaschalMixin
from engine.resolvers.ceremonial import CeremonialMixin
from engine.resolvers.common import CommonResolverMixin


class RuthenianEngine(
    EngineCore,
    TextDBMixin,
    CalendarMixin,
    RubricsMixin,
    GenerationMixin,
    VespersMixin,
    MatinsMixin,
    LiturgyMixin,
    HoursMixin,
    ComplineMixin,
    LentenMixin,
    PaschalMixin,
    CeremonialMixin,
    CommonResolverMixin,
):
    """
    Ruthenian Typikon Engine — Byzantine Rite liturgical constraint-logic engine.
    
    Dynamically generates service texts according to the Lviv (Dolnytsky) Typikon (2010).
    This class composes all functionality from domain-specific mixin modules.
    
    Entry points:
        - get_liturgical_context(date) -> context dict
        - generate_full_booklet(date) -> service booklet
        - generate_typikon_digest(date) -> digest output
    """
    pass
