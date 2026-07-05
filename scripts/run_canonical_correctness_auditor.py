import os
import sys
import re
import json
from datetime import date, timedelta
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ruthenian_engine import RuthenianEngine

def clean_liturgical_text(text):
    if not text:
        return ""
    return text.replace("**", "").strip()

def emulate_ui_commemorations(dolnytsky_commemoration):
    if not dolnytsky_commemoration or dolnytsky_commemoration == "None":
        return []
    
    cleaned = dolnytsky_commemoration.rstrip(".")
    parts = [p.strip() for p in re.split(
        r'\s+and\s+|\s+&\s+|;|(?<!\bSt)(?<!\bSts)(?<!\bVen)(?<!\bBp)(?<!\bAp)(?<!\bAps)(?<!\bMetr)(?<!\bArchbp)(?<!\bPatr)(?<!\bMart)(?<!\bProp)\.\s+', 
        cleaned, 
        flags=re.IGNORECASE
    ) if p.strip()]
    return parts

class GroundedCanonicalCorrectnessAuditor:
    def __init__(self, year=2026):
        self.year = year
        self.engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
        self.mismatches = []
        self.total_days = 0
        self.last_week_tone = None
        self.last_date = None

    def log_mismatch(self, dt: date, field: str, expected: str, actual: str, severity="ERROR"):
        self.mismatches.append({
            "date": dt.isoformat(),
            "field": field,
            "expected": expected,
            "actual": actual,
            "severity": severity
        })

    def audit_element_recursive(self, expected, actual, path="", dt=None):
        if expected is None and actual is None:
            return
            
        if type(expected) != type(actual):
            if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
                if expected == actual:
                    return
            self.log_mismatch(dt, f"{path} (Type)", type(expected).__name__, type(actual).__name__)
            return
            
        if isinstance(expected, dict):
            for k, v in expected.items():
                sub_path = f"{path}.{k}" if path else k
                if k not in actual:
                    self.log_mismatch(dt, sub_path, f"Has key '{k}'", "Key missing")
                else:
                    self.audit_element_recursive(v, actual[k], sub_path, dt)
        elif isinstance(expected, list):
            if len(expected) != len(actual):
                self.log_mismatch(dt, f"{path} (Length)", f"{len(expected)} elements", f"{len(actual)} elements")
            else:
                for idx, (ev, av) in enumerate(zip(expected, actual)):
                    self.audit_element_recursive(ev, av, f"{path}[{idx}]", dt)
        else:
            if expected != actual:
                if isinstance(expected, str) and isinstance(actual, str):
                    if expected.lower().strip() != actual.lower().strip():
                        self.log_mismatch(dt, path, expected, actual)
                else:
                    self.log_mismatch(dt, path, str(expected), str(actual))

    def get_canonical_expectation(self, dt: date, context: dict, rubrics: dict = None) -> dict:
        from scripts.generate_365_days_audit import get_expected_panel
        
        offset = context.get("pascha_offset")
        panel_expect = get_expected_panel(dt, context, rubrics)
        
        # Base expectation dict
        expect = {
            "period": "normal",
            "season": panel_expect["season"],
            "color": panel_expect["color"]["color"],
            "fasting": panel_expect["fasting"]["type"],
            "prostrations": "Forbidden" if panel_expect["prostrations"]["forbidden"] else "Allowed (Standard Weekday/Lenten bows)",
            "octoechos_suspended": False
        }
        
        d_rank = context.get("dolnytsky_rank") or ""
        d_title = context.get("dolnytsky_title") or ""
        d_commem = context.get("dolnytsky_commemoration") or ""
        full_text = f"{d_title} {d_commem}".lower()
        
        m_rank = context.get("variables", {}).get("menaion_rank", "") or context.get("menaion_rank", "")
        if not m_rank and "rank" in context.get("variables", {}):
            m_rank = context["variables"]["rank"]
            
        period = "normal"
        if d_rank == "LORD" or (isinstance(m_rank, str) and m_rank.startswith("rank_vigil_lord")):
            period = "feast"
        elif d_rank in ["THEOTOKOS", "MOG"] or (isinstance(m_rank, str) and m_rank.startswith("rank_vigil_theotokos")):
            period = "feast"
        elif "apodosis" in full_text:
            period = "apodosis"
        elif "forefeast" in full_text:
            period = "forefeast"
        elif "afterfeast" in full_text or context.get("is_afterfeast"):
            period = "afterfeast"
            
        # Legacy Fallbacks
        if period == "normal":
            if context.get("is_fore_or_afterfeast"):
                period = "forefeast"
            elif context.get("feast_level") == "lord":
                period = "feast"
                
        expect["period"] = period
        
        # Resolve octoechos suspension expectation
        is_lord_or_theotokos_feast = (context.get("feast_level") in ["lord", "theotokos"])
        is_fore_after_apodosis = (period in ["forefeast", "afterfeast", "apodosis"])
        
        # Octoechos is suspended on:
        # - Lord's or Theotokos great feasts
        # - Forefeasts, afterfeasts, apodoses of Lord's/Theotokos feasts on weekdays (but not Sundays, where Octoechos is merged/kept)
        # - Pascha and Bright Week
        # - Pentecost and Pentecost week
        octoechos_suspended = False
        dow = (dt.weekday() + 1) % 7
        if is_lord_or_theotokos_feast:
            octoechos_suspended = True
        elif is_fore_after_apodosis and dow != 0:
            if expect["season"] in ["Nativity", "Theophany", "Meeting", "Transfiguration", "Dormition", "Nativity_Theotokos", "Exaltation_Cross", "Presentation", "Eucharist", "Ascension", "Pentecost"]:
                octoechos_suspended = True
        elif offset is not None:
            if 0 <= offset <= 6:  # Bright Week
                octoechos_suspended = True
            elif 49 <= offset <= 55:  # Pentecost week
                octoechos_suspended = True
                
        expect["octoechos_suspended"] = octoechos_suspended
        return expect

    def traverse_audit_recursive(self, curr_date: date, end_date: date):
        if curr_date > end_date:
            return
            
        self.total_days += 1
        
        try:
            ctx = self.engine.get_liturgical_context(curr_date)
            rubrics = self.engine.resolve_rubrics(ctx)
            fasting = self.engine.resolve_fasting_rule(ctx)
            vestment = self.engine.resolve_vestment_color(ctx, rubrics)
            prostrations = self.engine.resolve_prostrations_rule(ctx)
            
            prostrations_forbidden = prostrations.get("forbidden", False)
        except Exception as e:
            self.log_mismatch(curr_date, "ENGINE_CRASH", "Execution", f"Crashed: {str(e)}")
            self.traverse_audit_recursive(curr_date + timedelta(days=1), end_date)
            return

        from scripts.generate_365_days_audit import get_expected_panel, formatOutlines

        titleVal = self.engine.resolve_service_title(ctx, rubrics)
        commVal = clean_liturgical_text(ctx.get("dolnytsky_commemoration") or "None")
        clergy_variant = self.engine.resolve_clergy_variant(ctx, service="liturgy")
        
        parts = []
        if commVal != "None":
            parts = [p.strip() for p in re.split(
                r';|(?<!\bSt)(?<!\bSts)(?<!\bVen)(?<!\bBp)(?<!\bAp)(?<!\bAps)(?<!\bMetr)(?<!\bArchbp)(?<!\bPatr)(?<!\bMart)(?<!\bProp)\.\s+', 
                commVal, 
                flags=re.IGNORECASE
            ) if p.strip()]
            
        outlinesVal = formatOutlines(rubrics.get("overrides", {}).get("outlines") or rubrics.get("variables", {}).get("outlines") or "Default")

        actual = {
            "period": ctx.get("period", "normal"),
            "color": vestment.get("color", "gold"),
            "fasting": fasting.get("type", "no_fast"),
            "prostrations": "Forbidden" if prostrations_forbidden else "Allowed",
            
            "season": ctx.get("season", "ordinary"),
            "tone": ctx.get("tone"),
            "eothinon_number": ctx.get("eothinon_number"),
            "triodion_book": ctx.get("triodion_book", "N/A"),
            "menaion_book": ctx.get("menaion_book", "N/A"),
            "dolnytsky_rank_code": ctx.get("dolnytsky_rank_code") or ctx.get("fixed_rank_code") or "",
            "menaion_class": ctx.get("menaion_class", ""),
            "paradigm_id": ctx.get("paradigm_id"),
            "rubrics_title": titleVal,
            "commemorations_count": len(parts),
            "primary_commemoration": parts[0] if parts else "None",
            "saint_categories": ctx.get("saint_categories") or [],
            "clergy_variant": {"variant_id": clergy_variant.get("variant_id", "one_deacon")} if clergy_variant else {"variant_id": "one_deacon"},
            "outlines": outlinesVal,
            "vespers_type": rubrics.get("overrides", {}).get("vespers_type") or rubrics.get("variables", {}).get("vespers_type") or "daily_vespers",
            "compline_type": rubrics.get("overrides", {}).get("compline_type") or rubrics.get("variables", {}).get("compline_type") or "small_compline",
            "midnight_type": rubrics.get("overrides", {}).get("midnight_type") or rubrics.get("variables", {}).get("midnight_type") or "midnight_weekday",
            "matins_type": rubrics.get("overrides", {}).get("matins_type") or rubrics.get("variables", {}).get("matins_type") or "matins_weekday",
            "liturgy_type": rubrics.get("overrides", {}).get("liturgy_type") or rubrics.get("variables", {}).get("liturgy_type") or "liturgy_chrysostom"
        }

        panel_expect = get_expected_panel(curr_date, ctx, rubrics, actual)
        expect = self.get_canonical_expectation(curr_date, ctx, rubrics)
        
        mapped_expect = {
            "period": expect["period"],
            "color": panel_expect["color"]["color"],
            "fasting": panel_expect["fasting"]["type"],
            "prostrations": "Forbidden" if panel_expect["prostrations"]["forbidden"] else "Allowed",
            
            "season": panel_expect["season"],
            "tone": panel_expect["tone"],
            "eothinon_number": panel_expect["eothinon_number"],
            "triodion_book": panel_expect["triodion_book"],
            "menaion_book": panel_expect["menaion_book"],
            "dolnytsky_rank_code": panel_expect["dolnytsky_rank_code"],
            "menaion_class": panel_expect["menaion_class"],
            "paradigm_id": panel_expect["paradigm_id"],
            "rubrics_title": panel_expect["rubrics_title"],
            "commemorations_count": panel_expect["commemorations_count"],
            "primary_commemoration": panel_expect["primary_commemoration"],
            "saint_categories": panel_expect["saint_categories"],
            "clergy_variant": panel_expect["clergy_variant"],
            "outlines": panel_expect["outlines"],
            "vespers_type": panel_expect["vespers_type"],
            "compline_type": panel_expect["compline_type"],
            "midnight_type": panel_expect["midnight_type"],
            "matins_type": panel_expect["matins_type"],
            "liturgy_type": panel_expect["liturgy_type"]
        }
        
        # Recursively audit mapped expected vs actual
        self.audit_element_recursive(mapped_expect, actual, path="", dt=curr_date)
        
        # Octoechos suspension check
        if expect["octoechos_suspended"]:
            stichera = ctx.get("variables", {}).get("vespers_stichera_distribution", {})
            has_octoechos_stichera = False
            if isinstance(stichera, dict):
                for key_opt in ["1_saint", "2_saints", "saint_on_6_doxology"]:
                    opt = stichera.get(key_opt, {})
                    if isinstance(opt, dict):
                        for dist in opt.get("distribution", []):
                            if dist.get("source") == "octoechos":
                                has_octoechos_stichera = True
                                
            canons = ctx.get("variables", {}).get("matins_canon_distribution", {})
            has_octoechos_canons = False
            if isinstance(canons, dict):
                for key_opt in ["1_saint", "2_saints", "saint_on_6_doxology"]:
                    opt = canons.get(key_opt, {})
                    if isinstance(opt, dict):
                        for dist in opt.get("distribution", []):
                            if dist.get("source") == "octoechos":
                                has_octoechos_canons = True
                                
            if has_octoechos_stichera and ctx.get("day_of_week") != 0:
                self.log_mismatch(curr_date, "Octoechos Vespers Stichera Leak", "Suspended (0 Octoechos stichera)", "Leaked (Octoechos stichera found in variables)")
            if has_octoechos_canons and ctx.get("day_of_week") != 0:
                self.log_mismatch(curr_date, "Octoechos Matins Canons Leak", "Suspended (0 Octoechos canons)", "Leaked (Octoechos canons found in variables)")

        # Commemorations count check
        comm_val = ctx.get("dolnytsky_commemoration", "None") or "None"
        rendered_parts = emulate_ui_commemorations(comm_val)
        rendered_count = len(rendered_parts)
        backend_saints = ctx.get("saints", [])
        expected_count = len(backend_saints)
        if rendered_count < expected_count:
            self.log_mismatch(curr_date, "UI Commemorations Count", f"Count: {expected_count} ({[s['name'] for s in backend_saints]})", f"Count: {rendered_count} ({rendered_parts})")

        # Tone Continuity Verification (Fortification check)
        tone = ctx.get("tone")
        offset = ctx.get("pascha_offset")
        
        if self.last_date is not None and self.last_date + timedelta(days=1) == curr_date:
            # Python weekday(): 0 = Monday, 6 = Sunday
            is_sunday_transition = (curr_date.weekday() == 6)
            is_bright_week = (offset is not None and 0 <= offset <= 6)
            is_suspended_week = (offset is not None and -8 <= offset <= -1)
            
            if tone is not None:
                if is_sunday_transition:
                    # If it's Sunday, tone should increment by 1 (mod 8) from last week's tone
                    if self.last_week_tone is not None and not is_bright_week and not is_suspended_week:
                        expected_tone = (self.last_week_tone % 8) + 1
                        if tone != expected_tone:
                            self.log_mismatch(
                                curr_date, 
                                "Tone Sunday Increment (Continuity)", 
                                f"Tone {expected_tone}", 
                                f"Tone {tone}"
                            )
                else:
                    # On weekdays, tone must remain constant to prevent mid-week drift
                    if self.last_week_tone is not None and not is_bright_week and not is_suspended_week:
                        if tone != self.last_week_tone:
                            self.log_mismatch(
                                curr_date, 
                                "Tone Weekday Constant (Continuity)", 
                                f"Tone {self.last_week_tone}", 
                                f"Tone {tone}"
                            )
            
        # Update continuity variables
        if tone is not None:
            self.last_week_tone = tone
        self.last_date = curr_date

        # Recurse next day
        self.traverse_audit_recursive(curr_date + timedelta(days=1), end_date)

    def run_audit(self):
        print(f"Starting Independent Grounded Canonical Correctness Audit for {self.year}...")
        
        start_date = date(self.year, 1, 1)
        end_date = date(self.year, 12, 31)
        
        self.traverse_audit_recursive(start_date, end_date)
        
        print("--------------------------------------------------")
        print(f"Audit completed: {self.total_days} days checked.")
        print(f"Mismatches found: {len(self.mismatches)}")
        print("--------------------------------------------------")
        
        report_path_json = PROJECT_ROOT / "audit_results" / "canonical_correctness_report.json"
        report_path_md = PROJECT_ROOT / "audit_results" / "canonical_correctness_report.md"
        
        report_path_json.parent.mkdir(exist_ok=True)
        
        with open(report_path_json, "w", encoding="utf-8") as f:
            json.dump(self.mismatches, f, indent=2)
            
        md_lines = [
            f"# Grounded Canonical Correctness Audit Report ({self.year})",
            "",
            "This report lists all discrepancies between the resolved engine variables and the independent canonical gold standard rules.",
            "",
            f"**Total Days Audited:** {self.total_days}",
            f"**Total Mismatches Found:** {len(self.mismatches)}",
            "",
            "| Date | Field | Expected | Actual | Severity |",
            "|---|---|---|---|---|",
        ]
        
        for m in self.mismatches:
            md_lines.append(f"| {m['date']} | {m['field']} | {m['expected']} | {m['actual']} | {m['severity']} |")
            
        with open(report_path_md, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
            
        print(f"Reports saved to:\n  - {report_path_json}\n  - {report_path_md}")
        return len(self.mismatches)

if __name__ == "__main__":
    auditor = GroundedCanonicalCorrectnessAuditor()
    sys.exit(auditor.run_audit())
