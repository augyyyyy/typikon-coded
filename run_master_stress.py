import json
from ruthenian_engine import RuthenianEngine

def run_stress_test():
    engine = RuthenianEngine(".")
    print("=== MASTER STRESS TEST: DIVINE LITURGY ===")
    
    # SCENARIO A: Sunday Tone 4 + Rank 3 Saint (Polyeleos)
    print("\n[SCENARIO A] Sunday Tone 4 + Saint (Rank 3)")
    ctx_a = {
        "date": "2025-02-02", "day_of_week": 0, "rank": 3, 
        "tone": 4, "title": "Sunday", "saturday_before": False
    }
    rubrics_a = {}
    antiphons_a = engine.resolve_liturgy_antiphons(ctx_a, rubrics_a)
    hymns_a = engine.resolve_liturgy_hymns(ctx_a, rubrics_a)
    print(f"Antiphons: {antiphons_a['args']['strategy']}")
    print(f"Hymn Stack: {[h['source'] for h in hymns_a['components']]}")
    
    # SCENARIO B: Theophany (Jan 6) on Tuesday
    print("\n[SCENARIO B] Theophany (Great Feast) on Tuesday")
    ctx_b = {
        "date": "2026-01-06", "day_of_week": 2, "rank": 1, 
        "tone": 0, "title": "Theophany", "saturday_before": False
    }
    rubrics_b = {}
    antiphons_b = engine.resolve_liturgy_antiphons(ctx_b, rubrics_b)
    trisagion_b = engine.resolve_trisagion_type(ctx_b, rubrics_b)
    megalynarion_b = engine.resolve_liturgy_megalynarion(ctx_b, rubrics_b)
    
    print(f"Antiphons: {antiphons_b['args']['strategy']}")
    print(f"Trisagion: {trisagion_b.get('ref_key')}")
    print(f"Megalynarion: {megalynarion_b.get('ref_key', megalynarion_b.get('note'))}")

    # SCENARIO C: Great Thursday
    print("\n[SCENARIO C] Great Thursday")
    ctx_c = {
        "date": "2026-04-09", "day_of_week": 4, "rank": 1, 
        "tone": 0, "title": "Great Thursday", "saturday_before": False,
        "liturgy_type": "basil", "is_great_thursday": True
    }
    rubrics_c = {}
    cherubic_c = engine.resolve_cherubic_hymn(ctx_c, rubrics_c)
    megalynarion_c = engine.resolve_liturgy_megalynarion(ctx_c, rubrics_c)
    
    print(f"Cherubic: {cherubic_c.get('ref_key')}")
    print(f"Megalynarion: {megalynarion_c.get('ref_key')}")

if __name__ == "__main__":
    run_stress_test()
