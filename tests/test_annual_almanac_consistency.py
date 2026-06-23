import os
import json
import datetime
import unittest
import copy
from ruthenian_engine import RuthenianEngine

class TestAnnualAlmanacConsistency(unittest.TestCase):
    def test_almanac_consistency_2026(self):
        # 1. Load the almanac JSON
        almanac_path = os.path.join("json_db", "almanac", "annual_almanac_2026.json")
        self.assertTrue(os.path.exists(almanac_path), f"Almanac file not found at {almanac_path}")
        
        # Freshness Check: Enforce almanac is newer than engine source edits
        import glob
        engine_files = (
            glob.glob(os.path.join("engine", "*.py")) + 
            glob.glob(os.path.join("engine", "resolvers", "*.py"))
        )
        self.assertTrue(len(engine_files) > 0, "No engine source files found to check mtime.")
        max_engine_mtime = max(os.path.getmtime(f) for f in engine_files)
        almanac_mtime = os.path.getmtime(almanac_path)
        
        self.assertGreaterEqual(
            almanac_mtime, max_engine_mtime,
            f"Almanac cache is stale! (Mtime: {datetime.datetime.fromtimestamp(almanac_mtime)} vs "
            f"Engine Mtime: {datetime.datetime.fromtimestamp(max_engine_mtime)}). "
            f"Please run 'python scripts/generate_annual_almanac.py' to regenerate it."
        )
        
        with open(almanac_path, "r", encoding="utf-8") as f:
            almanac = json.load(f)
            
        # Load the Lviv paradigm mapping
        map_path = os.path.join("json_db", "lviv_format_map.json")
        with open(map_path, "r", encoding="utf-8") as f:
            format_map = json.load(f)
            
        # 2. Instantiate a clean engine and stub out almanac loading to force live computation
        live_engine = RuthenianEngine()
        # Override _get_almanac to return None, forcing live calculation
        live_engine._get_almanac = lambda *args, **kwargs: None
        
        # 3. Instantiate an engine WITH almanac active to test the almanac fast path
        almanac_engine = RuthenianEngine()
        self.assertIsNotNone(almanac_engine._get_almanac(2026), "Almanac engine should successfully load the almanac")

        # 4. Compare every day
        days = almanac["days"]
        print(f"Comparing {len(days)} days for consistency...")
        
        # We check specific fields to make sure no regressions occur between live and almanac engines
        for date_str, expected in days.items():
            dt = datetime.date.fromisoformat(date_str)
            
            # Get live context, rubrics, and paradigm ID
            live_ctx = live_engine.get_liturgical_context(dt)
            live_rubrics = live_engine.resolve_rubrics(live_ctx)
            
            # Enrich live context to match digest and almanac generator behaviour
            enriched_live_ctx = {**live_ctx, **live_rubrics.get("variables", {}), "variables": live_rubrics.get("variables", {})}
            live_readings = live_engine.resolve_liturgy_readings(enriched_live_ctx, live_rubrics)
            
            live_gc = live_engine.resolve_general_case(live_ctx)
            live_paradigm_id = live_gc.get("id") if live_gc else None
            
            # Get almanac-engine context, rubrics, readings
            alm_ctx = almanac_engine.get_liturgical_context(dt)
            alm_rubrics = almanac_engine.resolve_rubrics(alm_ctx)
            # alm_ctx is already enriched, but we can pass it directly
            alm_readings = almanac_engine.resolve_liturgy_readings(alm_ctx, alm_rubrics)
            
            # 5. Assertions
            self.assertTrue(alm_ctx.get("_almanac_used"), f"Almanac fast path should be marked active on {date_str}")
            
            # Check context fields
            for key in ["day_of_week", "tone", "season_id", "season", "pascha_offset", "dolnytsky_rank", "dolnytsky_title", "feast_id", "feast_level"]:
                self.assertEqual(
                    alm_ctx.get(key), live_ctx.get(key),
                    f"Context mismatch for key '{key}' on {date_str} (Almanac: {alm_ctx.get(key)} vs Live: {live_ctx.get(key)})"
                )
                
            # Check paradigm ID
            self.assertEqual(
                expected.get("paradigm_id"), live_paradigm_id,
                f"Paradigm ID mismatch on {date_str} (Almanac: {expected.get('paradigm_id')} vs Live: {live_paradigm_id})"
            )
            
            # Check Lviv paradigm number
            expected_num = format_map["base_mappings"].get(live_paradigm_id) if live_paradigm_id else None
            self.assertEqual(
                alm_ctx.get("lviv_paradigm_number"), expected_num,
                f"Lviv paradigm number mismatch on {date_str} (Almanac: {alm_ctx.get('lviv_paradigm_number')} vs Expected: {expected_num})"
            )
            
            # Check rubrics title, variables & overrides
            self.assertEqual(
                alm_rubrics.get("title"), live_rubrics.get("title"),
                f"Title mismatch on {date_str} (Almanac: {alm_rubrics.get('title')} vs Live: {live_rubrics.get('title')})"
            )
            
            self.assertEqual(
                alm_rubrics.get("variables"), live_rubrics.get("variables"),
                f"Variables mismatch on {date_str}\nAlmanac: {alm_rubrics.get('variables')}\nLive: {live_rubrics.get('variables')}"
            )
            
            self.assertEqual(
                alm_rubrics.get("overrides"), live_rubrics.get("overrides"),
                f"Overrides mismatch on {date_str}\nAlmanac: {alm_rubrics.get('overrides')}\nLive: {live_rubrics.get('overrides')}"
            )
            
            # Check readings
            self.assertEqual(
                alm_readings, live_readings,
                f"Readings mismatch on {date_str}\nAlmanac: {alm_readings}\nLive: {live_readings}"
            )

if __name__ == "__main__":
    unittest.main()
