"""
Automated 5-Sub-Section Liturgical Context Panel Auditor

Validates the Left Panel ("LITURGICAL CONTEXT") on the Cantor Dashboard:
  - Sub-Section 1: Calendar Instance (Date, Season, Tone, Eothinon, Fasting, Katavasia)
  - Sub-Section 2: Source Books & Classification (Menaion, Triodion)
  - Sub-Section 3: Commemoration & Class (Rank Code, Class, Rubrics Case, Temporal Purity)
  - Sub-Section 4: Ceremonial Settings (Color, Prostrations, Clergy Variant)
  - Sub-Section 5: Rubrics Outcomes (Selected Outlines)

Canonical Authority:
  - Dolnytsky Typikon Parts I–V
  - Ordo Celebrationis §12–§45
  - Particular Law of the UGCC (Can. 115)
"""

import sys
import os
from datetime import date, timedelta

# Dynamic Path Resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ruthenian_engine import RuthenianEngine


class LiturgicalContextAuditor:
    def __init__(self):
        self.engine = RuthenianEngine()

    def audit_context(self, target_date: date) -> dict:
        ctx = self.engine.get_liturgical_context(target_date)
        rubrics = self.engine.resolve_rubrics(ctx)
        fasting = self.engine.resolve_fasting_rule(ctx)
        vestment = self.engine.resolve_vestment_color(ctx, rubrics)
        prostrations = self.engine.resolve_prostrations_rule(ctx)
        clergy_variant = self.engine.resolve_clergy_variant(ctx, service="liturgy")
        katavasia = self.engine.resolve_katavasia(ctx)
        service_title = self.engine.resolve_service_title(ctx, rubrics)

        # Enriched context
        enriched = {**ctx, "service_title": service_title}

        sections = {
            "section_1_calendar_instance": self._audit_section_1_calendar(enriched, rubrics, fasting, katavasia),
            "section_2_source_books": self._audit_section_2_source_books(enriched, rubrics),
            "section_3_commemoration_class": self._audit_section_3_commemoration_class(enriched, rubrics),
            "section_4_ceremonial_settings": self._audit_section_4_ceremonial(enriched, rubrics, vestment, prostrations, clergy_variant),
            "section_5_rubrics_outcomes": self._audit_section_5_rubrics_outcomes(enriched, rubrics)
        }

        all_passed = all(s["status"] == "PASS" for s in sections.values())

        return {
            "date": target_date.isoformat(),
            "overall_status": "PASS" if all_passed else "FAIL",
            "sections": sections
        }

    def _audit_section_1_calendar(self, ctx, rubrics, fasting, katavasia) -> dict:
        discrepancies = []
        # Date Invariant
        if not ctx.get("date"):
            discrepancies.append("Missing civil date")

        # Season Invariant
        if not ctx.get("season"):
            discrepancies.append("Missing liturgical season")

        # Eothinon Invariant: Eothinon Gospel ONLY on Sunday
        day_of_week = ctx.get("day_of_week", 0)
        eoth = ctx.get("eothinon_number")
        if day_of_week != 0 and eoth is not None:
            discrepancies.append(f"Eothinon Gospel ({eoth}) present on non-Sunday (Day {day_of_week})")
        elif day_of_week == 0 and eoth is None:
            # Check if Pascha or Pentecost Sunday where standard Eothinon cycle gives way to festal Gospel
            p_offset = ctx.get("pascha_offset")
            if p_offset not in (0, 49):
                discrepancies.append("Missing Eothinon Gospel on Sunday")

        # Tone Invariant: Tone required on Octoechos days (None on Holy Week / Bright Week)
        p_offset = ctx.get("pascha_offset")
        is_tone_suspended = p_offset is not None and (-8 <= p_offset <= 6)
        if not is_tone_suspended and not ctx.get("tone"):
            discrepancies.append("Missing Octoechos Tone on non-suspended day")

        # Fasting Invariant
        if not fasting or not fasting.get("type"):
            discrepancies.append("Missing fasting discipline specification")

        return {
            "name": "Calendar Instance",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def _audit_section_2_source_books(self, ctx, rubrics) -> dict:
        discrepancies = []
        # Menaion Invariant
        if not ctx.get("menaion_book"):
            discrepancies.append("Missing Menaion book reference")

        # Triodion Invariant
        season_id = ctx.get("season_id")
        p_offset = ctx.get("pascha_offset")
        is_triodion_period = season_id in ("triodion", "pentecostarion") or (p_offset is not None and (-70 <= p_offset <= 56))
        triodion_book = ctx.get("triodion_book")
        if is_triodion_period and (not triodion_book or triodion_book == "N/A"):
            discrepancies.append("Missing Triodion/Pentecostarion book during movable cycle")

        return {
            "name": "Source Books & Classification",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def _audit_section_3_commemoration_class(self, ctx, rubrics) -> dict:
        discrepancies = []
        day_of_week = ctx.get("day_of_week", 0)
        
        # 1. Temporal Purity: Check for day-mismatch in titles and commemorations
        comm = ctx.get("dolnytsky_commemoration", "")
        title = ctx.get("dolnytsky_title", "")
        s_title = ctx.get("service_title", "")
        saints = ctx.get("saints", [])
        saint_names = " ".join(s.get("name", "") for s in saints)

        all_text = f"{comm} {title} {s_title} {saint_names}"

        if day_of_week != 0 and "(on sunday)" in all_text.lower():
            discrepancies.append("Temporal Clashing: '(On Sunday)' text present on non-Sunday")
        if day_of_week != 6 and "(on saturday)" in all_text.lower():
            discrepancies.append("Temporal Clashing: '(On Saturday)' text present on non-Saturday")
        if day_of_week == 0 and "(on weekday)" in all_text.lower():
            discrepancies.append("Temporal Clashing: '(On Weekday)' text present on Sunday")

        # 2. Paradigm Invariant: Sunday vs Non-Sunday vs Specific Saturday/Weekday
        paradigm = ctx.get("paradigm_id") or rubrics.get("variables", {}).get("paradigm_id") or ""
        sunday_only_cases = ("CASE_01", "CASE_04", "CASE_06", "CASE_08", "CASE_11", "CASE_13", "CASE_15", "CASE_17", "CASE_19", "CASE_21")
        weekday_only_cases = ("CASE_02",)
        saturday_only_cases = ("CASE_03", "CASE_22")

        if day_of_week == 0:
            if paradigm in weekday_only_cases or paradigm in saturday_only_cases:
                discrepancies.append(f"Paradigm Misalignment: Non-Sunday paradigm ({paradigm}) resolved on Sunday")
        elif day_of_week == 6:
            if paradigm in sunday_only_cases:
                discrepancies.append(f"Paradigm Misalignment: Sunday paradigm ({paradigm}) resolved on Saturday")
            elif paradigm in weekday_only_cases:
                discrepancies.append(f"Paradigm Misalignment: Weekday-only paradigm ({paradigm}) resolved on Saturday")
        elif 1 <= day_of_week <= 5:
            if paradigm in sunday_only_cases:
                discrepancies.append(f"Paradigm Misalignment: Sunday paradigm ({paradigm}) resolved on Weekday")
            elif paradigm in saturday_only_cases:
                discrepancies.append(f"Paradigm Misalignment: Saturday-only paradigm ({paradigm}) resolved on Weekday")

        # 3. Rank Code Invariant
        code = ctx.get("fixed_rank_code") or ctx.get("dolnytsky_rank_code") or ""
        valid_codes = ["[LORD]", "[MOG]", "[VIGIL]", "[POL]", "[GT DOX]", "[6 SM]", "[4 A+G]", "[4 NO]", "[4 TR]"]
        if code and code not in valid_codes:
            discrepancies.append(f"Invalid rank code format: '{code}'")

        return {
            "name": "Commemoration & Class",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def _audit_section_4_ceremonial(self, ctx, rubrics, vestment, prostrations, clergy_variant) -> dict:
        discrepancies = []
        # Vestment Invariant
        if not vestment or not vestment.get("color"):
            discrepancies.append("Missing liturgical vestment color")

        # Prostrations Invariant: Forbidden on Sundays and during Paschal season
        day_of_week = ctx.get("day_of_week", 0)
        p_offset = ctx.get("pascha_offset")
        is_pascha_season = p_offset is not None and (0 <= p_offset <= 48)
        if (day_of_week == 0 or is_pascha_season) and not prostrations.get("forbidden", False):
            discrepancies.append("Prostrations incorrectly allowed on Sunday / Paschal season (Ordo §12)")

        # Clergy Variant Invariant
        if not clergy_variant or not clergy_variant.get("label"):
            discrepancies.append("Missing clergy variant specification")

        return {
            "name": "Ceremonial Settings",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def _audit_section_5_rubrics_outcomes(self, ctx, rubrics) -> dict:
        discrepancies = []
        if not rubrics or not isinstance(rubrics, dict):
            discrepancies.append("Missing rubrics resolution outcome")
        elif "variables" not in rubrics or not isinstance(rubrics["variables"], dict):
            discrepancies.append("Missing rubrics variables dictionary")

        return {
            "name": "Rubrics Outcomes",
            "status": "PASS" if not discrepancies else "FAIL",
            "discrepancies": discrepancies
        }

    def sweep_year(self, year: int = 2026) -> dict:
        curr = date(year, 1, 1)
        end = date(year, 12, 31)
        passed = 0
        failed = []

        while curr <= end:
            res = self.audit_context(curr)
            if res["overall_status"] == "PASS":
                passed += 1
            else:
                failed.append(res)
            curr += timedelta(days=1)

        return {
            "total_days": 365,
            "passed_count": passed,
            "failed_count": len(failed),
            "pass_rate_pct": (passed / 365.0) * 100.0,
            "failures": failed
        }


if __name__ == "__main__":
    auditor = LiturgicalContextAuditor()
    if len(sys.argv) > 1 and sys.argv[1] == "--all-year":
        res = auditor.sweep_year(2026)
        print("=======================================================")
        print(f" EXHAUSTIVE 365-DAY LITURGICAL CONTEXT AUDIT: 2026")
        print(f" Passed Days: {res['passed_count']}/{res['total_days']} ({res['pass_rate_pct']:.1f}%)")
        print(f" Failed Days: {res['failed_count']}/{res['total_days']}")
        print("=======================================================")
        if res["failures"]:
            print("\nFirst 10 Failures:")
            for f in res["failures"][:10]:
                print(f"  * {f['date']}:")
                for s_id, s in f["sections"].items():
                    if s["status"] != "PASS":
                        print(f"      - {s['name']}: {', '.join(s['discrepancies'])}")
            sys.exit(1)
        else:
            print("\nSUCCESS: 100% of all 365 days evaluated to PASS!")
            sys.exit(0)
    else:
        target_str = sys.argv[1] if len(sys.argv) > 1 else "2026-08-29"
        target_date = date.fromisoformat(target_str)
        res = auditor.audit_context(target_date)
        print(f"AUDIT REPORT FOR {res['date']}: [{res['overall_status']}]")
        for s_id, s in res["sections"].items():
            status_symbol = "PASS" if s["status"] == "PASS" else "FAIL"
            print(f"  [{status_symbol}] {s['name']}")
            for d in s["discrepancies"]:
                print(f"      - {d}")
        sys.exit(0 if res["overall_status"] == "PASS" else 1)
