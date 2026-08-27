import json
import pytest
from datetime import date, timedelta
from pathlib import Path
from ruthenian_engine import RuthenianEngine

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class TestParadigmCoverage365:
    @classmethod
    def setup_class(cls):
        cls.engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
        
        # Load 02a_logic_general.json
        with open(PROJECT_ROOT / "json_db" / "02a_logic_general.json", encoding="utf-8") as f:
            cls.general_cases_db = json.load(f).get("logic_definitions", {})

        # Load 02c_logic_triodion.json
        with open(PROJECT_ROOT / "json_db" / "02c_logic_triodion.json", encoding="utf-8") as f:
            cls.triodion_db = json.load(f).get("logic_map", {})

    def test_all_365_days_paradigm_compliance(self):
        start_date = date(2026, 1, 1)
        end_date = date(2026, 12, 31)
        current_date = start_date
        
        discrepancies = []
        evaluated_days = 0

        while current_date <= end_date:
            evaluated_days += 1
            dt_str = current_date.isoformat()
            
            try:
                # 1. Liturgical Context & Rubrics
                ctx = self.engine.get_liturgical_context(current_date)
                rubrics = self.engine.resolve_rubrics(ctx)
                
                day_of_week = ctx.get("day_of_week", 0)
                is_sunday = (day_of_week == 0)
                pascha_off = ctx.get("pascha_offset")
                is_triodion_pentecost = (pascha_off is not None and -70 <= pascha_off <= 68)

                # 2. General Case Resolution
                gc = self.engine.resolve_general_case(ctx)
                paradigm_id = gc.get("id") if gc else None
                
                # Check 1: Paradigm must not be None
                if not paradigm_id:
                    discrepancies.append(f"{dt_str}: No paradigm_id resolved by resolve_general_case")
                    current_date += timedelta(days=1)
                    continue

                # Check 2: Verify paradigm_id validity (CASE_01..CASE_20 or known triodion keys)
                if not (paradigm_id.startswith("CASE_") or paradigm_id in self.triodion_db or paradigm_id in ("pascha", "ascension", "pentecost")):
                    discrepancies.append(f"{dt_str}: Unrecognized paradigm_id '{paradigm_id}'")

                # Check 3: Sunday Paradigms must be Sunday Cases
                SUNDAY_CASES = {"CASE_01", "CASE_04", "CASE_06", "CASE_08", "CASE_10", "CASE_11", "CASE_13", "CASE_15", "CASE_17", "CASE_19"}
                if is_sunday and not is_triodion_pentecost:
                    if paradigm_id not in SUNDAY_CASES:
                        discrepancies.append(f"{dt_str}: Sunday resolved to non-Sunday paradigm '{paradigm_id}'")

                # Check 4: Saturday Paradigms (non-festal, non-triodion)
                SATURDAY_CASES = {"CASE_03", "CASE_05", "CASE_07", "CASE_09", "CASE_10", "CASE_12", "CASE_14", "CASE_16", "CASE_18", "CASE_20"}
                if day_of_week == 6 and not is_triodion_pentecost:
                    if paradigm_id not in SATURDAY_CASES:
                        discrepancies.append(f"{dt_str}: Saturday resolved to non-Saturday paradigm '{paradigm_id}'")

                # Check 5: Stichera Distribution Invariant
                stich = self.engine.resolve_vespers_stichera(ctx)
                total_stichera = stich.get("total_count", 0)
                if is_sunday:
                    if total_stichera not in (10, 8, 6):
                        discrepancies.append(f"{dt_str}: Sunday Vespers stichera count is {total_stichera} (expected 10, 8, or 6)")
                elif day_of_week != 0 and not is_triodion_pentecost:
                    if total_stichera not in (6, 8, 10):
                        discrepancies.append(f"{dt_str}: Weekday Vespers stichera count is {total_stichera} (expected 6, 8, or 10)")

                # Check 6: Canon Stack Total Count Invariant
                canon = self.engine.resolve_canon_stack(ctx)
                total_canon = canon.get("total_count", 0)
                if total_canon not in (14, 12, 10, 8, 6, 4):
                    discrepancies.append(f"{dt_str}: Matins Canon total count is {total_canon} (expected standard Byzantine count 14, 12, 10, 8, 6, or 4)")

                # Check 7: Deep Case Invariants
                # A. Great Feasts of the Lord (CASE_10)
                if paradigm_id == "CASE_10":
                    if not ctx.get("is_feast_of_the_lord") and ctx.get("feast_level") != "lord" and ctx.get("dolnytsky_rank") != "LORD":
                        discrepancies.append(f"{dt_str}: CASE_10 triggered without Lord feast flag")

                # B. Great Feasts of the Theotokos (CASE_11, CASE_12)
                if paradigm_id in ("CASE_11", "CASE_12"):
                    if not ctx.get("is_feast_of_theotokos") and ctx.get("feast_level") != "theotokos" and ctx.get("dolnytsky_rank") not in ("THEOTOKOS", "MOG"):
                        discrepancies.append(f"{dt_str}: {paradigm_id} triggered without Theotokos feast flag")

                # C. Sunday Polyeleos (CASE_04)
                if paradigm_id == "CASE_04":
                    m_rank = str(ctx.get("variables", {}).get("menaion_rank") or ctx.get("menaion_rank") or ctx.get("dolnytsky_rank") or "")
                    if "polyeleos" not in m_rank.lower() and "pol" not in m_rank.lower():
                        discrepancies.append(f"{dt_str}: CASE_04 triggered without Polyeleos rank (got: '{m_rank}')")

                # Check 8: Typikon Digest Right-Panel Generation Invariants
                digest = self.engine.generate_typikon_digest(ctx, rubrics)
                if "[ERROR:" in digest:
                    discrepancies.append(f"{dt_str}: Digest contains '[ERROR:'")
                if "[RESOLVE ERROR" in digest:
                    discrepancies.append(f"{dt_str}: Digest contains '[RESOLVE ERROR'")
                if "{'" in digest:
                    discrepancies.append(f"{dt_str}: Digest contains raw Python dict dump")

            except Exception as e:
                discrepancies.append(f"{dt_str}: Crash during paradigm evaluation: {str(e)}")

            current_date += timedelta(days=1)

        assert evaluated_days == 365, f"Expected 365 days evaluated, got {evaluated_days}"
        assert not discrepancies, f"Found {len(discrepancies)} paradigm compliance violations across 365 days:\n" + "\n".join(f"  - {d}" for d in discrepancies[:30])
