from datetime import date
from ruthenian_engine import RuthenianEngine

def test_royal_doors_calendar_resolutions():
    """Verify that the royal_doors recension resolves the modern reformed calendar."""
    engine = RuthenianEngine(version="royal_doors")
    
    # 1. July 5, 2026: Should be Athanasius of Athos (rank_polyeleos)
    ctx_july_5 = engine.get_liturgical_context(date(2026, 7, 5))
    assert ctx_july_5["dolnytsky_rank"] == "POLYELEOS"
    assert "athanasius" in ctx_july_5["saints"][0]["id"]
    
    # 2. July 6, 2026: Should be Sisoes the Great (rank_simple / [4 TR])
    ctx_july_6 = engine.get_liturgical_context(date(2026, 7, 6))
    assert ctx_july_6["dolnytsky_rank"] == "SIMPLE"
    assert "Sisoes" in ctx_july_6["dolnytsky_commemoration"]
    
    # 3. May 11, 2026: Should be Cyril and Methodius (rank_polyeleos)
    ctx_may_11 = engine.get_liturgical_context(date(2026, 5, 11))
    assert ctx_may_11["dolnytsky_rank"] == "POLYELEOS"
    assert "Cyril" in ctx_may_11["dolnytsky_commemoration"]


def test_lviv_2010_calendar_resolutions():
    """Verify that the lviv recension resolves the 2010 Lviv Typikon calendar."""
    engine = RuthenianEngine(version="lviv")
    
    # 1. July 5, 2026: Should be Cyril and Methodius (rank_polyeleos)
    ctx_july_5 = engine.get_liturgical_context(date(2026, 7, 5))
    assert ctx_july_5["dolnytsky_rank"] == "POLYELEOS"
    assert "Cyril" in ctx_july_5["dolnytsky_commemoration"]
    
    # 2. July 6, 2026: Should be Athanasius of Athos (rank_polyeleos)
    ctx_july_6 = engine.get_liturgical_context(date(2026, 7, 6))
    assert ctx_july_6["dolnytsky_rank"] == "POLYELEOS"
    assert "Athanasius" in ctx_july_6["dolnytsky_commemoration"]
    
    # 3. May 11, 2026: Should be Mocius (rank_simple / [4 A+G])
    ctx_may_11 = engine.get_liturgical_context(date(2026, 5, 11))
    assert ctx_may_11["dolnytsky_rank"] == "SIMPLE"
    assert "Mocius" in ctx_may_11["dolnytsky_commemoration"]
