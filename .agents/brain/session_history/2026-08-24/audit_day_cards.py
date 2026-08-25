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
        rubrics = self.engine.resolve_rubrics(ctx)
        digest = self.engine.generate_typikon_digest(ctx, rubrics)
        
        cards_results = {
            "card_1_general_info": self._audit_card_1_general_info(ctx, rubrics, digest),
            "card_2_vespers": self._audit_card_2_vespers(ctx, rubrics, digest),
            "card_3_compline": self._audit_card_3_compline(ctx, rubrics, digest),
            "card_4_midnight_office": self._audit_card_4_midnight_office(ctx, rubrics, digest),
            "card_5_matins": self._audit_card_5_matins(ctx, rubrics, digest),
            "card_6_hours": self._audit_card_6_hours(ctx, rubrics, digest),
            "card_7_liturgy": self._audit_card_7_liturgy(ctx, rubrics, digest),
        }
        
        all_passed = all(c["status"] == "PASS" for c in cards_results.values())
        
        return {
            "date": target_date.isoformat(),
            "overall_status": "PASS" if all_passed else "FAIL",
            "cards_passed": sum(1 for c in cards_results.values() if c["status"] == "PASS"),
            "total_cards": len(cards_results),
            "cards": cards_results
        }

    def _audit_card_1_general_info(self, ctx, rubrics, digest) -> dict:
        discrepancies = []
        # Check required metadata
        if not ctx.get("date"):
            discrepancies.append("Missing date in context")
        if not ctx.get("tone"):
            discrepancies.append("Missing Tone of the Week")
        if "TYPICON:" not in digest:
            discrepancies.append("Missing TYPICON header in digest output")
        if "Vestment colour:" not in digest and "VESTMENT:" not in digest:
            discrepancies.append("Missing Vestment specification in General Info")
            
        return {
            "name": "General Info",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def _audit_card_2_vespers(self, ctx, rubrics, digest) -> dict:
        discrepancies = []
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

    def _audit_card_3_compline(self, ctx, rubrics, digest) -> dict:
        discrepancies = []
        if "COMPLINE" not in digest:
            discrepancies.append("Compline card missing from digest output")
        return {
            "name": "Small/Great Compline",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def _audit_card_4_midnight_office(self, ctx, rubrics, digest) -> dict:
        discrepancies = []
        if "MIDNIGHT OFFICE" not in digest:
            discrepancies.append("Midnight Office card missing from digest output")
        return {
            "name": "Midnight Office",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def _audit_card_5_matins(self, ctx, rubrics, digest) -> dict:
        discrepancies = []
        if "MATINS" not in digest:
            discrepancies.append("Matins card missing from digest output")
        if "Kathisma" not in digest and "kathisma" not in digest:
            discrepancies.append("Matins Kathismata reading missing from digest")
        if "Canon" not in digest:
            discrepancies.append("Matins Canon order missing from digest")
            
        return {
            "name": "Daily/Great Matins",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def _audit_card_6_hours(self, ctx, rubrics, digest) -> dict:
        discrepancies = []
        if "HOURS" not in digest:
            discrepancies.append("The Hours card missing from digest output")
        return {
            "name": "The Hours",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def _audit_card_7_liturgy(self, ctx, rubrics, digest) -> dict:
        discrepancies = []
        if "LITURGY" not in digest:
            discrepancies.append("Divine Liturgy card missing from digest output")
        if "Troparia and Kontakia" not in digest:
            discrepancies.append("Liturgy Troparia & Kontakia sequence missing from digest")
            
        return {
            "name": "Divine Liturgy",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }


def main():
    parser = argparse.ArgumentParser(description="Audit all 7 cards for a given liturgical date.")
    parser.add_argument("date", nargs="?", default="2026-08-24", help="Target date in YYYY-MM-DD format")
    args = parser.parse_args()
    
    target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    auditor = DayCardsAuditor()
    report = auditor.audit_day(target_date)
    
    print(f"\n=======================================================")
    print(f" 7-CARD DAY AUDIT REPORT: {report['date']}")
    print(f" Overall Status: {report['overall_status']} ({report['cards_passed']}/{report['total_cards']} cards passed)")
    print(f"=======================================================")
    
    for card_id, res in report["cards"].items():
        symbol = "✅ PASS" if res["status"] == "PASS" else "❌ FAIL"
        print(f"[{symbol}] {res['name']}")
        for d in res["discrepancies"]:
            print(f"       ⚠️  {d}")
            
    print(f"=======================================================\n")
    
    if report["overall_status"] != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
