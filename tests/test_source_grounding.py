import pytest
import inspect
from engine.resolvers.matins import MatinsMixin
from engine.resolvers.liturgy import LiturgyMixin
from engine.resolvers.vespers import VespersMixin
from engine.resolvers.hours import HoursMixin

# For now, we only enforce on specific Mixins as we migrate the missing functions.
# Eventually this should cover the entire RuthenianEngine.

class TestSourceGrounding:
    
    def test_resolvers_are_grounded(self):
        """
        Ensures that every new 'resolve_' function added has the @liturgical_source decorator.
        """
        # Get all methods across multiple mixins
        methods = []
        methods.extend(inspect.getmembers(MatinsMixin, predicate=inspect.isfunction))
        methods.extend(inspect.getmembers(LiturgyMixin, predicate=inspect.isfunction))
        methods.extend(inspect.getmembers(VespersMixin, predicate=inspect.isfunction))
        methods.extend(inspect.getmembers(HoursMixin, predicate=inspect.isfunction))
        
        missing_decorators = []
        missing_ordo = []
        
        # The 11 Matins functions + 5 Phase 2 functions + 14 Retroactive functions
        strictly_enforced_functions = [
            'resolve_service_type',
            'resolve_god_is_lord_tone',
            'calculate_canon_ratios',
            'resolve_canon_combination',
            'get_katavasia',
            'get_eothinon_exapostilarion',
            'resolve_praises',
            'get_eothinon_doxastikon',
            'resolve_doxology',
            'resolve_dismissal',
            'resolve_dismissal_troparion',
            # Phase 2 additions
            'resolve_vesperal_liturgy_readings',
            'resolve_beatitudes',
            'resolve_12_passion_gospels',
            'resolve_passion_vespers_readings',
            'resolve_typika_kontakia',
            # Phase 2 Retroactive (Royal Hours)
            'resolve_royal_psalms',
            'resolve_royal_stichera',
            'resolve_royal_readings',
            'resolve_royal_troparia',
            'resolve_royal_kontakion',
            'check_royal_hours_trigger',
            # Phase 2 Retroactive (Liturgy)
            'resolve_trisagion_type',
            'resolve_basil_megalynarion',
            'resolve_communion_hymn',
            'resolve_post_communion_hymn',
            'resolve_liturgy_readings',
            'resolve_reading_ot',
            'resolve_reading_epistle',
            'resolve_reading_gospel'
        ]
        
        for name, func in methods:
            if name in strictly_enforced_functions:
                # Must have the decorator
                if not hasattr(func, '__liturgical_source__'):
                    missing_decorators.append(name)
                else:
                    source_meta = func.__liturgical_source__
                    # If the function name implies physical choreography/structure, it MUST have an Ordo citation
                    if name in ['resolve_doxology', 'resolve_dismissal', 'resolve_12_passion_gospels']:
                        if not source_meta.get('ordo'):
                            missing_ordo.append(name)
                            
        assert not missing_decorators, f"STRICT MODE FAIL: The following functions lack the @liturgical_source decorator: {list(set(missing_decorators))}"
        assert not missing_ordo, f"STRICT MODE FAIL: The following physical/choreographic functions lack an Ordo Celebrationis citation: {list(set(missing_ordo))}"


    def test_no_hardcoded_verses_in_formatter(self):
        """
        Verify that no hardcoded Elizabethan/arbitrary prokeimena verses exist in digest/formatters/common.py,
        and that it relies on dynamic lookups from the Horologion assets instead.
        """
        import os
        formatter_path = os.path.join("digest", "formatters", "common.py")
        with open(formatter_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # These legacy/Elizabethan strings should not be in the file anymore
        banned_strings = [
            "hath girded Himself",
            "Holiness becometh Thy house",
            "Hearken unto my soul",
            "Thy salvation, O God, shall uphold me",
            "Let the poor see and be glad",
            "Thou hast made Thy power known",
            "barbarous people",
            "Thy wonders from the beginning"
        ]
        
        found_banned = [s for s in banned_strings if s in content]
        assert not found_banned, f"Audit Fail: Hardcoded legacy prokeimena verses found in {formatter_path}: {found_banned}"

        # Check that psalm_116 and psalm_68 lookups are present
        assert "horologion.psalm_116" in content, "Audit Fail: horologion.psalm_116 lookup is missing in common.py"
        assert "horologion.psalm_68" in content, "Audit Fail: horologion.psalm_68 lookup is missing in common.py"

        # Check that sessional formatter maps saint categories
        assert "saint_categories" in content, "Audit Fail: saint_categories lookup is missing in sessional formatter"
        assert "Venerable Woman" in content, "Audit Fail: Venerable Woman mapping is missing in sessional formatter"
        assert "Venerable Mother" in content, "Audit Fail: Venerable Mother mapping is missing in sessional formatter"
