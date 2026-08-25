#!/usr/bin/env python
"""
Automated 7-Card Day Auditor for Typikon Coded.
Audits every individual card for a given date against the 2010 Lviv Dolnytsky Typikon.
A day evaluates to PASS if and only if all 7 cards evaluate to PASS.
"""

import sys
import argparse
from datetime import date, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ruthenian_engine import RuthenianEngine
from typikon_digest_generator import TypikonDigestGenerator


class DayCardsAuditor:
    def __init__(self):
        self.engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
        self.digest_gen = TypikonDigestGenerator(self.engine)

    def audit_day(self, target_date: date) -> dict:
        ctx = self.engine.get_liturgical_context(target_date)
        resolved_case = self.engine.resolve_general_case(ctx)
        case_id = resolved_case.get("id", "UNKNOWN_CASE") if resolved_case else "UNKNOWN_CASE"
        rubrics = self.engine.resolve_rubrics(ctx)
        digest = self.engine.generate_typikon_digest(ctx, rubrics)
        
        cards_results = {
            "card_1_general_info": self._audit_card_1_general_info(ctx, rubrics, digest, case_id),
            "card_2_vespers": self._audit_card_2_vespers(ctx, rubrics, digest, case_id),
            "card_3_compline": self._audit_card_3_compline(ctx, rubrics, digest, case_id),
            "card_4_midnight_office": self._audit_card_4_midnight_office(ctx, rubrics, digest, case_id),
            "card_5_matins": self._audit_card_5_matins(ctx, rubrics, digest, case_id),
            "card_6_hours": self._audit_card_6_hours(ctx, rubrics, digest, case_id),
            "card_7_liturgy": self._audit_card_7_liturgy(ctx, rubrics, digest, case_id),
        }
        
        all_passed = all(c["status"] == "PASS" for c in cards_results.values())
        
        return {
            "date": target_date.isoformat(),
            "case_id": case_id,
            "overall_status": "PASS" if all_passed else "FAIL",
            "cards_passed": sum(1 for c in cards_results.values() if c["status"] == "PASS"),
            "total_cards": len(cards_results),
            "cards": cards_results
        }

    def _audit_card_1_general_info(self, ctx, rubrics, digest, case_id) -> dict:
        discrepancies = []
        if not ctx.get("date"):
            discrepancies.append("Missing date in context")
        # Citation: Dolnytsky Part IV — Lazarus Saturday (-8), Holy Week (-7 to -1), and Bright Week (0 to 6) suspend the Octoechos Tone
        pascha_offset = ctx.get("pascha_offset")
        is_tone_suspended = pascha_offset is not None and (-8 <= pascha_offset <= 6)
        if not is_tone_suspended and not ctx.get("tone"):
            discrepancies.append("Missing Tone of the Week on Octoechos day")
        if "TYPICON:" not in digest:
            discrepancies.append("Missing TYPICON header in digest output")
        if "Vestment colour:" not in digest and "VESTMENT:" not in digest:
            discrepancies.append("Missing Vestment specification in General Info")
            
        return {
            "name": "General Info",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def _audit_card_2_vespers(self, ctx, rubrics, digest, case_id) -> dict:
        discrepancies = []
        pascha_offset = ctx.get("pascha_offset")
        is_pascha = pascha_offset == 0
        is_vespers_in_digest = "VESPERS" in digest or "Vespers" in digest
        if is_vespers_in_digest and not is_pascha:
            enriched = {**ctx, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
            stichera_res = self.engine.resolve_vespers_stichera(enriched)
            
            if stichera_res and stichera_res.get("total_count", 0) > 0:
                dist = stichera_res.get("distribution", [])
                if not dist:
                    discrepancies.append("Resolver returned empty distribution list for active stichera")
                if "At Lord, I Call" not in digest and "At O Lord, I have cried" not in digest:
                    discrepancies.append("Lord, I Call stichera block missing from Vespers digest")
                    
            # Prokeimenon check
            if "Prokeimenon" not in digest:
                discrepancies.append("Vespers prokeimenon missing from digest")
            
        return {
            "name": "Daily/Great Vespers",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def _audit_card_3_compline(self, ctx, rubrics, digest, case_id) -> dict:
        discrepancies = []
        pascha_offset = ctx.get("pascha_offset")
        is_bright_week = pascha_offset is not None and (0 <= pascha_offset <= 6)
        is_vigil = (
            ctx.get("is_vigil") or 
            rubrics.get("variables", {}).get("is_vigil") or 
            case_id in ("CASE_07", "CASE_08", "CASE_09", "CASE_10", "CASE_11", "CASE_12", "CASE_13", "CASE_14", "CASE_15", "CASE_16", "CASE_17", "CASE_18", "ascension", "monday_holy_spirit", "feast_of_eucharist", "pascha") or
            is_bright_week
        )
        # Citation: Dolnytsky Part I & V — On Vigil days and throughout Bright Week, Compline is omitted/replaced by Paschal Hours
        if not is_vigil and "COMPLINE" not in digest:
            discrepancies.append("Compline card missing from digest output on non-Vigil day")
        return {
            "name": "Small/Great Compline",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def _audit_card_4_midnight_office(self, ctx, rubrics, digest, case_id) -> dict:
        discrepancies = []
        pascha_offset = ctx.get("pascha_offset")
        is_bright_week = pascha_offset is not None and (0 <= pascha_offset <= 6)
        is_vigil = (
            ctx.get("is_vigil") or 
            rubrics.get("variables", {}).get("is_vigil") or 
            case_id in ("CASE_07", "CASE_08", "CASE_09", "CASE_10", "CASE_11", "CASE_12", "CASE_13", "CASE_14", "CASE_15", "CASE_16", "CASE_17", "CASE_18", "ascension", "monday_holy_spirit", "feast_of_eucharist", "pascha") or
            is_bright_week
        )
        # Citation: Dolnytsky Part I & V — On Vigil days and throughout Bright Week, Midnight Office is omitted
        if not is_vigil and "MIDNIGHT OFFICE" not in digest:
            discrepancies.append("Midnight Office card missing from digest output on non-Vigil day")
        return {
            "name": "Midnight Office",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def _audit_card_5_matins(self, ctx, rubrics, digest, case_id) -> dict:
        discrepancies = []
        if "MATINS" not in digest:
            discrepancies.append("Matins card missing from digest output")
        pascha_offset = ctx.get("pascha_offset")
        is_kathisma_transformed = pascha_offset is not None and (pascha_offset in (-3, -2, -1, 0) or (0 <= pascha_offset <= 6))
        # Citation: Dolnytsky Part IV & V — Passion Matins, Jerusalem Matins, and Paschal Matins replace ordinary Kathismata with Gospels, Lamentations, or Paschal Canon
        if not is_kathisma_transformed and "Kathisma" not in digest and "kathisma" not in digest:
            discrepancies.append("Matins Kathismata reading missing from digest")
        if "Canon" not in digest and not is_kathisma_transformed:
            discrepancies.append("Matins Canon order missing from digest")
            
        return {
            "name": "Daily/Great Matins",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def _audit_card_6_hours(self, ctx, rubrics, digest, case_id) -> dict:
        discrepancies = []
        if "HOURS" not in digest and "Hours" not in digest:
            discrepancies.append("The Hours card missing from digest output")
        return {
            "name": "The Hours",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def _audit_card_7_liturgy(self, ctx, rubrics, digest, case_id) -> dict:
        discrepancies = []
        # Citation: Dolnytsky Part IV — Clean Monday/Tuesday, non-Presanctified Lenten weekdays, and Great Friday are strictly aliturgical
        pascha_offset = ctx.get("pascha_offset")
        is_lent = (
            ctx.get("is_lent") or 
            ctx.get("season") == "lent" or 
            ctx.get("triodion_period") in ("lent", "clean_week", "great_lent") or
            (pascha_offset is not None and -48 <= pascha_offset <= -7)
        )
        is_aliturgical = (
            ctx.get("is_aliturgical") or 
            rubrics.get("variables", {}).get("is_aliturgical") or 
            rubrics.get("variables", {}).get("liturgy_type") == "none" or
            (is_lent and ctx.get("day_of_week") in (1, 2, 4) and not ctx.get("is_presanctified")) or
            pascha_offset == -2 # Great and Holy Friday
        )
        is_vesperal = "VESPERAL" in digest or "Vesperal" in digest or "vesperal_merge_logic" in str(rubrics)
        if not is_aliturgical:
            if "LITURGY" not in digest and not is_vesperal:
                discrepancies.append("Divine Liturgy card missing from digest output on Eucharistic day")
            if "Troparia and Kontakia" not in digest and "Presanctified" not in digest and "PRESANCTIFIED" not in digest and not is_vesperal:
                discrepancies.append("Liturgy Troparia & Kontakia sequence missing from digest")
            
        return {
            "name": "Divine Liturgy",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }


def main():
    parser = argparse.ArgumentParser(description="Audit all 7 cards for a given date or full year.")
    parser.add_argument("date", nargs="?", default=None, help="Target date in YYYY-MM-DD format")
    parser.add_argument("--all-year", action="store_true", help="Run full 365-day exhaustive card sweep for 2026")
    parser.add_argument("--year", type=int, default=2026, help="Year to sweep (default: 2026)")
    args = parser.parse_args()
    
    auditor = DayCardsAuditor()
    
    if args.all_year:
        start_d = date(args.year, 1, 1)
        end_d = date(args.year, 12, 31)
        total_days = (end_d - start_d).days + 1
        passed_days = 0
        failed_days = []
        
        print(f"\n=======================================================")
        print(f" EXHAUSTIVE 365-DAY 7-CARD AUDIT SWEEP: {args.year}")
        print(f" Total Days to Audit: {total_days} (2,555 Total Cards)")
        print(f"=======================================================")
        
        curr = start_d
        while curr <= end_d:
            report = auditor.audit_day(curr)
            if report["overall_status"] == "PASS":
                passed_days += 1
            else:
                failed_days.append(report)
            curr += timedelta(days=1)
            
        print(f" Passed Days: {passed_days}/{total_days} ({passed_days/total_days*100:.1f}%)")
        print(f" Failed Days: {len(failed_days)}/{total_days}")
        print(f"=======================================================\n")
        
        if failed_days:
            print("First 5 Failures:")
            for f in failed_days[:5]:
                print(f"  * {f['date']} [{f['case_id']}]: {f['cards_passed']}/{f['total_cards']} cards passed")
                for c_id, c in f["cards"].items():
                    if c["status"] != "PASS":
                        print(f"      - {c['name']}: {', '.join(c['discrepancies'])}")
            sys.exit(1)
        else:
            print("SUCCESS: 100% of all 365 days (2,555 cards) evaluated to PASS!")
            sys.exit(0)
            
    target_date_str = args.date or "2026-08-24"
    target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    report = auditor.audit_day(target_date)
    
    print(f"\n=======================================================")
    print(f" 7-CARD DAY AUDIT REPORT: {report['date']} [{report['case_id']}]")
    print(f" Overall Status: {report['overall_status']} ({report['cards_passed']}/{report['total_cards']} cards passed)")
    print(f"=======================================================")
    
    for card_id, res in report["cards"].items():
        symbol = "PASS" if res["status"] == "PASS" else "FAIL"
        print(f"[{symbol}] {res['name']}")
        for d in res["discrepancies"]:
            print(f"       * {d}")
            
    print(f"=======================================================\n")
    
    if report["overall_status"] != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    from datetime import timedelta
    main()
