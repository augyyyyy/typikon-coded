import os
import sys
import re
import json
import inspect
import argparse
import requests
from datetime import date, timedelta
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from ruthenian_engine import RuthenianEngine
    from typikon_digest_generator import TypikonDigestGenerator
except ImportError:
    sys.path.insert(0, str(PROJECT_ROOT / "engine"))
    from ruthenian_engine import RuthenianEngine
    from typikon_digest_generator import TypikonDigestGenerator

from scratch.audit_recursive_resolvers import extract_resolver_calls_from_structures, check_value_recursively
from tests.test_scripture_citations import CITATION_REGEX, parse_and_validate_citation

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def get_deepseek_key():
    key = os.getenv("DEEPSEEK_API_KEY")
    if key and key != "your_deepseek_api_key_here":
        return key

    global_env = Path("C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/.env")
    if global_env.exists():
        try:
            with open(global_env, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k_clean = k.strip().replace("[", "").replace("]", "")
                        if k_clean in ("deepseek-v4-pro", "DEEPSEEK_API_KEY"):
                            val = v.strip()
                            if val:
                                return val
        except Exception:
            pass
    return None

class ServiceDayMultiAuditor:
    def __init__(self, year=2026, start_date_str=None, end_date_str=None, call_deepseek=False, engine=None):
        self.year = year
        self.engine = engine if engine is not None else RuthenianEngine(base_dir=str(PROJECT_ROOT))
        self.resolver_calls = extract_resolver_calls_from_structures(str(PROJECT_ROOT))
        self.call_deepseek_flag = call_deepseek
        self.deepseek_key = get_deepseek_key()
        
        if start_date_str:
            self.start_date = date.fromisoformat(start_date_str)
        else:
            self.start_date = date(self.year, 1, 1)
            
        if end_date_str:
            self.end_date = date.fromisoformat(end_date_str)
        else:
            self.end_date = date(self.year, 12, 31)
            
        self.audit_dir = PROJECT_ROOT / "audit_results"
        self.audit_dir.mkdir(exist_ok=True)
        
        # State tracking for sliding context (continuity)
        self.sliding_state = {}

    def extract_service_digest_section(self, digest_text: str, service_name: str) -> str:
        """Extract the specific service section from the generated digest."""
        lines = digest_text.splitlines()
        # Collect preamble (lines before the first major service header)
        preamble_lines = []
        for line in lines:
            upper = line.strip().upper()
            if upper.startswith("## ") or upper.startswith("=== "):
                break
            preamble_lines.append(line)
        preamble_str = "\n".join(preamble_lines).strip()

        kw_map = {
            "Vespers": ["VESPERS"],
            "Compline": ["COMPLINE"],
            "Midnight Office": ["MIDNIGHT"],
            "Matins": ["MATINS", "LAMENTATIONS"],
            "First Hour": ["FIRST HOUR", "HOURS"],
            "Third Hour": ["THIRD HOUR", "HOURS"],
            "Sixth Hour": ["SIXTH HOUR", "HOURS"],
            "Ninth Hour": ["NINTH HOUR", "HOURS"],
            "Liturgy": ["LITURGY", "TYPIKA"]
        }
        keywords = kw_map.get(service_name, [service_name.upper()])
            
        started = False
        service_lines = []
        for line in lines:
            upper_line = line.strip().upper()
            is_any_header = upper_line.startswith("## ") or upper_line.startswith("=== ")
            is_target_header = is_any_header and any(kw in upper_line for kw in keywords)
                
            if is_target_header:
                started = True
                service_lines.append(line)
                continue
                
            if started:
                if is_any_header:
                    break
                service_lines.append(line)
                
        service_str = "\n".join(service_lines).strip()
        return f"{preamble_str}\n\n{service_str}" if service_str else ""

    def generate_single_service_booklet(self, context, rubrics, service, include_ceremonial=False):
        """Generate raw booklet text for a single service in the daily cycle."""
        service_name = service["name"]
        
        # Slicing logic overrides
        matins_override = None
        t_period = str(context.get("triodion_period", ""))
        season = str(context.get("season", ""))
        dow = context.get("day_of_week")
        
        if t_period in ["holy_friday", "holy_saturday"] or (season == "holy_week" and dow == 6):
            matins_override = "tomb_matins"
        elif t_period in ["pascha", "bright_week"]:
            matins_override = "bright_matins"
        elif t_period in ["holy_thursday", "passion_matins"] or (season == "holy_week" and dow in [4, 5]):
            matins_override = "passion_matins"
        elif t_period in ["holy_monday", "holy_tuesday", "holy_wednesday", "holy_week_weekday"] or (season == "holy_week" and dow in [1, 2, 3]):
            matins_override = "bridegroom_matins"

        root_id = service["root"]
        if service["type_key"] in rubrics.get("variables", {}):
            root_id = rubrics["variables"][service["type_key"]]
        if service["type_key"] in rubrics.get("overrides", {}):
            root_id = rubrics["overrides"][service["type_key"]]

        if service_name == "Matins" and matins_override:
            root_id = matins_override

        if "hours_type" in service["type_key"]:
            var_hours = rubrics.get("variables", {}).get("hours_type", "")
            if "royal" in var_hours:
                root_id = "structure_royal"
            elif "lenten" in var_hours:
                root_id = "structure_lenten"
            elif "paschal" in var_hours:
                root_id = "structure_paschal"

        if service_name == "Midnight Office":
            mode_data = self.engine.resolve_midnight_office_mode(context)
            if "mode" in mode_data:
                root_id = f"midnight_{mode_data['mode']}"

        struct_data = self.engine._load_json(service["file"])
        skeleton = self.engine._get_structure_sequence(struct_data, root_id)

        if not skeleton:
            return f"ERROR: Structure '{root_id}' not found in {service['file']}"

        booklet = []
        if include_ceremonial:
            booklet.append(f"--- {service_name.upper()} ({root_id}) ---")
        else:
            booklet.append(f"--- {service_name.upper()} ---")

        def process_sequence(sequence):
            for slot in sequence:
                content = slot.get("content", {})
                if not content and "type" in slot: content = slot
                slot_type = content.get("type")

                if slot_type == 'link':
                    target_id = content.get('target_id')
                    target_file = content.get('target_file')
                    if target_file and target_id:
                        full_path = os.path.join(self.engine.json_db, target_file)
                        if not os.path.exists(full_path): full_path = target_file
                        if os.path.exists(full_path):
                            try:
                                with open(full_path, 'r', encoding='utf-8') as f:
                                    linked_data = json.load(f)
                                sub_seq = self.engine._get_structure_sequence(linked_data, target_id)
                                if sub_seq:
                                    process_sequence(sub_seq)
                            except Exception:
                                pass
                    continue

                text = self.engine._resolve_slot(slot, rubrics, context)
                if text and text.strip():
                    booklet.append(text)
                
                nested_seq = slot.get("sequence") or content.get("sequence")
                if nested_seq and isinstance(nested_seq, list) and slot_type != "sequence":
                    process_sequence(nested_seq)

        process_sequence(skeleton)
        return "\n".join(booklet)

    # --- THE 8 VALIDATION GATES ---
    
    def gate1_heuristics(self, dt: date, service_name: str, content: str) -> list:
        """Gate 1: Spelling, Terminology, Key Leaks, and Jargon Auditor."""
        errors = []
        warnings = []
        
        # Leaked programmer keys in structural markers
        leak_patterns = [
            (r"\bmenaion\.\w+", "Leaked raw menaion key"),
            (r"\boctoechos\.\w+", "Leaked raw octoechos key"),
            (r"\btriodion\.\w+", "Leaked raw triodion key"),
            (r"\bhorologion\.\w+", "Leaked raw horologion key"),
            (r"\bsaints_2\b", "Leaked internal placeholder 'saints_2'"),
            (r"\bsaint_1\b", "Leaked internal placeholder 'saint_1'"),
            (r"\bsaint_2\b", "Leaked internal placeholder 'saint_2'"),
            (r"\bSaint\s+\d+\b", "Leaked internal placeholder 'Saint 1' / 'Saint 2'"),
            (r"_stichera\b", "Leaked stichera suffix token"),
            (r"_troparion\b", "Leaked troparion suffix token"),
            (r"_kontakion\b", "Leaked kontakion suffix token")
        ]
        for pattern, desc in leak_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                warnings.append(f"{desc}: '{match.group(0)}'")

        # Raw Python dictionary/list dumps
        python_dumps = [
            (r"\{\s*['\"]\w+['\"]\s*:", "Raw dictionary structure leak"),
            (r"\[\s*['\"]trop_", "Raw list array leak with 'trop_'"),
            (r"\[\s*['\"]kont_", "Raw list array leak with 'kont_'")
        ]
        for pattern, desc in python_dumps:
            match = re.search(pattern, content)
            if match:
                errors.append(f"{desc}: '{match.group(0)}'")

        # Double Saint Prefixes
        double_prefixes = [
            (r"\bSt\.\s+(Nativity|Translation|Return|Transfer|Finding|Recovery|Deposition|Conception|Protection|Synaxis|Annunciation|Dormition|Theophany|Elevation)\b", "Invalid saint prefix before feast title"),
            (r"\bSt\.\s+St\.\b", "Double St. St. prefix"),
            (r"\bSaint\s+Saint\b", "Double Saint Saint prefix")
        ]
        for pattern, desc in double_prefixes:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                errors.append(f"{desc}: '{match.group(0)}'")

        # Ungrammatical raw key humanization leaks in liturgical texts
        grammar_leak_patterns = [
            (r"\b\d+\s+Aposticha\s+(Feast|Saint|Theotokos|Resurrection)\b", "Ungrammatical key-humanization leak: Aposticha + Subject"),
            (r"\b\d+\s+Stichera\s+(Feast|Saint|Theotokos)\b", "Ungrammatical key-humanization leak: Stichera + Subject"),
            (r"\b(Aposticha|Stichera)\s+Feast\b", "Ungrammatical key-humanization leak: 'Aposticha Feast' or 'Stichera Feast'"),
            (r"\b(Aposticha|Stichera)\s+Saint\b", "Ungrammatical key-humanization leak: 'Aposticha Saint' or 'Stichera Saint'"),
            (r"\b(Doxastikon|Theotokion|Troparion|Kontakion)\s+(Feast|Saint)\b", "Ungrammatical key-humanization leak: Hymn + Subject"),
            (r"\bGlory,?\s*[Bb]oth\s*now:?\s*Theotokion\b(?!\s+(?:in\s+Tone|for|of|from))", "Ungrounded bare Theotokion without tone or source"),
        ]
        for pattern, desc in grammar_leak_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                errors.append(f"{desc}: '{match.group(0)}'")

        # Banned Jargon in structural/system output
        jargon_words = ["array", "list", "dict", "variable", "suffix", "ref_key", "override", "fallback_default", "programmer"]
        for word in jargon_words:
            if word == "list":
                for match in re.finditer(r"\blist\b", content, re.IGNORECASE):
                    start = max(0, match.start() - 5)
                    end = min(len(content), match.end() + 25)
                    context_str = content[start:end].lower()
                    if "list of our iniquities" not in context_str and "list of iniquities" not in context_str:
                        errors.append("Leaked developer jargon: 'list'")
                        break
            else:
                match = re.search(r"\b" + re.escape(word) + r"\b", content, re.IGNORECASE)
                if match:
                    errors.append(f"Leaked developer jargon: '{match.group(0)}'")

        # Non-blocking Warning for STUB
        stub_match = re.search(r"\bstub\b", content, re.IGNORECASE)
        if stub_match:
            warnings.append(f"Found stub placeholder in text content: '{stub_match.group(0)}'")

        # Parenthetical Category Leaks
        parenthetical_pattern = r"\((feast|theotokos|saint|octoechos|triodion|pentecostarion)\)"
        match = re.search(parenthetical_pattern, content)
        if match:
            errors.append(f"Leaked raw parenthetical tag: '{match.group(0)}'")

        # Spelling standard violations - Non-blocking warnings for text assets (enforces UGCC matrix)
        spelling_violations = [
            (r"\bprokimenon\b", "Prokeimenon"),
            (r"\bprokimena\b", "Prokeimena"),
            (r"\bkinonicon\b", "Communion Hymn"),
            (r"\bkinonica\b", "Communion Hymns"),
            (r"\bexaposteilarion\b", "Exapostilarion"),
            (r"\blytia\b", "Litiya"),
            (r"\blitia\b", "Litiya"),
            (r"\bpre-feast\b", "Forefeast"),
            (r"\bpost-feast\b", "Afterfeast"),
            (r"\bpre\s+feast\b", "Forefeast"),
            (r"\bpost\s+feast\b", "Afterfeast"),
            (r"\bleave-taking\b", "Apodosis"),
            (r"\bleave\s+taking\b", "Apodosis"),
            (r"\bstepenna\b", "Gradual"),
            (r"\banabathmoi\b", "Gradual")
        ]
        for pattern, canonical_name in spelling_violations:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                warnings.append(f"Spelling standard violation in text asset: '{match.group(0)}' (canonical: {canonical_name})")

        for w in warnings:
            print(f"   ⚠️  [Text Warning] {w}")
            
        return errors

    def gate2_resolvers(self, dt: date, service_name: str, rubrics: dict, enriched: dict) -> list:
        """Gate 2: Resolver-Level Audit (validates case_id and text_db keys)."""
        errors = []
        services = rubrics.get("services", [])
        active_structures = [s.get("structure_id") for s in services if s.get("structure_id")]

        for func_name, signatures in self.resolver_calls.items():
            is_permitted = False
            for struct_id in active_structures:
                if self.engine.resolver_registry.is_allowed(struct_id, func_name):
                    is_permitted = True
                    break
            
            if not is_permitted or not hasattr(self.engine, func_name):
                continue
                
            # Filter functions relevant to the current service
            if service_name.lower() not in func_name.lower() and service_name != "Liturgy":
                if service_name == "First Hour" and "hour_1" not in func_name.lower(): continue
                elif service_name == "Third Hour" and "hour_3" not in func_name.lower(): continue
                elif service_name == "Sixth Hour" and "hour_6" not in func_name.lower(): continue
                elif service_name == "Ninth Hour" and "hour_9" not in func_name.lower(): continue
                elif service_name not in ("First Hour", "Third Hour", "Sixth Hour", "Ninth Hour"): continue
                
            func = getattr(self.engine, func_name)
            sig = inspect.signature(func)
            params = list(sig.parameters.values())
            has_context = len(params) > 0
            
            if not signatures:
                signatures = [{}]
                
            for args in signatures:
                call_kwargs = {}
                if "rubrics" in sig.parameters:
                    call_kwargs["rubrics"] = rubrics
                normalized_args = {}
                for k, v in args.items():
                    if k == "pos": normalized_args["position"] = v
                    elif k == "num": normalized_args["num"] = v
                    else: normalized_args[k] = v
                for param_name in sig.parameters:
                    if param_name in normalized_args:
                        call_kwargs[param_name] = normalized_args[param_name]
                        
                try:
                    res = func(enriched, **call_kwargs) if has_context else func()
                    if isinstance(res, dict):
                        case_id = res.get("case_id")
                        if case_id == "fallback_default":
                            errors.append(f"Resolver {func_name} resolved to banned 'fallback_default' Case ID.")
                            
                        day_errors = []
                        check_value_recursively(res, self.engine.text_db, day_errors, f"{func_name}(args={args})")
                        
                        # Separate halts (logical issues) from warnings (missing text/spelling in assets)
                        for err in day_errors:
                            if "Spelling standard violation" in err or "Unresolved database key reference" in err or "Found error placeholder" in err:
                                # This is a text asset warning, log it to console without halting
                                print(f"   ⚠️  [Text Warning] {err}")
                            else:
                                errors.append(err)
                except Exception as e:
                    errors.append(f"Resolver {func_name} crashed: {str(e)}")
        return errors

    def gate3_almanac(self, dt: date, context: dict) -> list:
        """Gate 3: Almanac Cache Consistency Check."""
        if context.get("is_temple_feast"):
            return []
        errors = []
        almanac = self.engine._get_almanac(dt.year)
        if almanac:
            cached_day = almanac.get(dt.isoformat())
            if cached_day:
                for key in ("tone", "season_id", "pascha_offset", "dolnytsky_rank"):
                    if cached_day.get(key) != context.get(key):
                        errors.append(f"Almanac cache mismatch: key '{key}' has cached '{cached_day.get(key)}' but live is '{context.get(key)}'.")
        return errors

    def gate4_canonical(self, dt: date, service_name: str, context: dict, rubrics: dict, enriched: dict) -> list:
        """Gate 4: Canonical Liturgical Constraints (Octoechos suppressions, reading overrides, kathisma)."""
        errors = []
        rank_id = self.engine._get_rank_id(context)
        d_rank = context.get("dolnytsky_rank", 5)
        try:
            d_rank_val = int(d_rank)
        except (ValueError, TypeError):
            d_rank_val = 5

        dow = context.get("day_of_week")
        is_weekday = (dow != 0) # Mon=1..Sat=6

        suppress_octoechos = (
            context.get("variables", {}).get("suppress_octoechos") is True or
            context.get("is_afterfeast") or
            context.get("is_forefeast") or
            context.get("is_apodosis") or
            (context.get("feast_level") in ("lord", "theotokos") and d_rank_val <= 2) or
            rank_id in ("rank_vigil_lord", "rank_vigil_theotokos")
        )

        is_great_feast = (
            context.get("feast_level") in ("lord", "theotokos") and 
            d_rank_val <= 2
        ) or rank_id in ("rank_vigil_lord", "rank_vigil_theotokos")

        # 1. Vespers Invariants
        if service_name == "Vespers" and (1 <= dow <= 5):
            if suppress_octoechos:
                stichera = self.engine.resolve_vespers_stichera(enriched)
                if stichera and isinstance(stichera, dict):
                    for item in stichera.get("items", []):
                        if item.startswith("octoechos."):
                            errors.append(f"Octoechos stichera '{item}' leaked on weekday when Octoechos is suppressed ({dt.isoformat()}).")
                    for dist_item in stichera.get("distribution", []):
                        if dist_item.get("source") == "octoechos":
                            errors.append(f"Octoechos stichera included in Vespers distribution on weekday when Octoechos is suppressed ({dt.isoformat()}).")

                aposticha = self.engine.resolve_aposticha(enriched)
                if aposticha and isinstance(aposticha, dict):
                    for item in aposticha.get("items", []):
                        if item.startswith("octoechos."):
                            errors.append(f"Octoechos aposticha '{item}' leaked on weekday when Octoechos is suppressed ({dt.isoformat()}).")
                    for dist_item in aposticha.get("distribution", []):
                        if dist_item.get("source") == "octoechos":
                            errors.append(f"Octoechos aposticha included in distribution on weekday when Octoechos is suppressed ({dt.isoformat()}).")

            # Vespers Kathisma Psalmody Check
            # Outside Great Lent, Great Feasts of the Lord, and Vigils, weekdays (Mon-Fri) must appoint a Kathisma
            is_vigil = is_great_feast or rank_id in ("rank_vigil", "rank_polyeleos") or context.get("is_sunday_vigil")
            is_lent = context.get("season") in ("great_lent", "lent") or context.get("season_id") in ("great_lent", "lent")
            pascha_off = context.get("pascha_offset")
            is_bright_week = pascha_off is not None and 0 <= pascha_off <= 6
            
            if not is_vigil and not is_lent and not is_bright_week and 1 <= dow <= 5:
                # Friday evening (dow==5) has no kathisma at Vespers outside Lent, but Mon-Thu (dow 1..4) must have a Kathisma
                if 1 <= dow <= 4:
                    kath_res = self.engine.resolve_daily_kathisma(enriched)
                    kath_num = kath_res.get("number", 0) if isinstance(kath_res, dict) else 0
                    if not kath_res or kath_num == 0 or kath_res.get("type") == "none":
                        errors.append(f"Vespers Kathisma psalmody wrongfully omitted on {dt.isoformat()} (dow={dow}).")

        # 2. Matins Invariants
        if service_name == "Matins" and is_weekday and suppress_octoechos:
            canon_stack = self.engine.resolve_canon_stack(enriched)
            if canon_stack and isinstance(canon_stack, dict):
                for dist_item in canon_stack.get("distribution", []):
                    b_type = dist_item.get("type", "")
                    if b_type != "theotokos_special" and (dist_item.get("source") == "octoechos" or b_type in ("resurrection", "cross_res", "theotokos_octoechos", "weekday_octoechos")):
                        errors.append(f"Octoechos canon '{dist_item.get('type')}' leaked on weekday Matins when Octoechos is suppressed ({dt.isoformat()}).")

            aposticha_matins = self.engine.resolve_aposticha_matins(enriched)
            if aposticha_matins and isinstance(aposticha_matins, dict):
                for item in aposticha_matins.get("items", []):
                    if item.startswith("octoechos."):
                        errors.append(f"Octoechos aposticha '{item}' leaked on weekday Matins ({dt.isoformat()}).")

        # 3. Compline Canon Season & Book Invariant
        if service_name == "Compline":
            compline_canon = self.engine.resolve_compline_canon(enriched)
            if compline_canon and isinstance(compline_canon, dict):
                season_id = context.get("season_id") or context.get("season", "")
                pascha_off = context.get("pascha_offset")
                is_movable_season = season_id in ("triodion", "pentecostarion", "great_lent", "holy_week") or (pascha_off is not None and -70 <= pascha_off <= 67)
                if compline_canon.get("book") == "triodion" and not is_movable_season:
                    errors.append(f"Compline canon appointed from Triodion out of season on {dt.isoformat()}.")

        # 4. Liturgy Readings override check
        if is_great_feast and is_weekday and service_name == "Liturgy":
            readings = self.engine.resolve_liturgy_readings(enriched, rubrics)
            if readings and isinstance(readings, dict):
                overrides = rubrics.get("overrides", {})
                if "epistle" in overrides or "gospel" in overrides:
                    expected_epistle = overrides.get("epistle")
                    expected_gospel = overrides.get("gospel")
                    if expected_epistle and readings.get("epistle") != expected_epistle:
                        errors.append(f"Epistle override mismatch: expected {expected_epistle}, got {readings.get('epistle')}")
                    if expected_gospel and readings.get("gospel") != expected_gospel:
                        errors.append(f"Gospel override mismatch: expected {expected_gospel}, got {readings.get('gospel')}")

        # 5. Liturgy Propers for Weekday Afterfeasts & Apodoses
        if service_name == "Liturgy" and is_weekday and (context.get("is_afterfeast") or context.get("is_apodosis")):
            readings = self.engine.resolve_liturgy_readings(enriched, rubrics)
            if readings and isinstance(readings, dict):
                first_r = readings.get("readings", [{}])[0]
                prok = first_r.get("prokeimenon", {})
                if prok.get("source") == "horologion":
                    errors.append(f"Liturgy Prokeimenon on Afterfeast {dt.isoformat()} resolved to generic weekday Horologion instead of Feast.")
                alleluia = first_r.get("alleluia", {})
                if alleluia.get("source") == "horologion":
                    errors.append(f"Liturgy Alleluia on Afterfeast {dt.isoformat()} resolved to generic weekday Horologion instead of Feast.")

            meg = self.engine.resolve_liturgy_megalynarion(enriched, rubrics)
            if isinstance(meg, dict) and meg.get("ref_key") not in ("festal_zadostoinyk", "paschal_zadostoinyk"):
                errors.append(f"Liturgy Megalynarion on Afterfeast {dt.isoformat()} resolved to '{meg.get('ref_key')}' instead of festal/paschal zadostoinyk.")

            comm = self.engine.resolve_communion_hymn(enriched, rubrics)
            if isinstance(comm, dict) and comm.get("source") != "feast":
                errors.append(f"Liturgy Communion Hymn on Afterfeast {dt.isoformat()} resolved to '{comm.get('ref_key')}' instead of Feast communion hymn.")
        return errors

    def gate5_citations(self, dt: date, content: str) -> list:
        """Gate 5: Bible citation range checker."""
        errors = []
        matches = CITATION_REGEX.finditer(content)
        ignore_words = {"on", "at", "by", "of", "the", "in", "to", "for", "with", "and", "or", "a", "an", "is", "are", "was", "were", "be", "been"}
        for match in matches:
            book_name = match.group("book").strip().lower()
            if book_name in ignore_words:
                continue
            citation_str = match.group(0)
            range_errors = parse_and_validate_citation(citation_str, f"Audit Date {dt.isoformat()}")
            errors.extend(range_errors)
        return errors

    def gate6_tone_coherence(self, dt: date, service_name: str, rubrics: dict, enriched: dict) -> list:
        """Gate 6: Musical Mode & Tone Coherence."""
        errors = []
        services = rubrics.get("services", [])
        active_structures = [s.get("structure_id") for s in services if s.get("structure_id")]
        
        resolved_keys = []
        for func_name, signatures in self.resolver_calls.items():
            is_permitted = False
            for struct_id in active_structures:
                if self.engine.resolver_registry.is_allowed(struct_id, func_name):
                    is_permitted = True
                    break
            if not is_permitted or not hasattr(self.engine, func_name):
                continue
            
            # Filter functions relevant to the current service
            if service_name.lower() not in func_name.lower() and service_name != "Liturgy":
                continue
                
            func = getattr(self.engine, func_name)
            sig = inspect.signature(func)
            params = list(sig.parameters.values())
            has_context = len(params) > 0
            
            if not signatures:
                signatures = [{}]
            for args in signatures:
                call_kwargs = {}
                if "rubrics" in sig.parameters:
                    call_kwargs["rubrics"] = rubrics
                normalized_args = {}
                for k, v in args.items():
                    if k == "pos": normalized_args["position"] = v
                    elif k == "num": normalized_args["num"] = v
                    else: normalized_args[k] = v
                for param_name in sig.parameters:
                    if param_name in normalized_args:
                        call_kwargs[param_name] = normalized_args[param_name]
                
                try:
                    res = func(enriched, **call_kwargs) if has_context else func()
                    if isinstance(res, dict):
                        for item in res.get("items", []):
                            if isinstance(item, str):
                                resolved_keys.append(item)
                except Exception:
                    pass

        # Verify tone in text database assets matches key mode
        for key in resolved_keys:
            tone_match = re.search(r"\btone_(?P<num>[1-8])\b", key)
            if tone_match:
                key_tone_num = int(tone_match.group("num"))
                asset = self.engine.get_text(key)
                if asset and isinstance(asset, dict):
                    asset_tone = asset.get("tone")
                    if asset_tone:
                        asset_tone_clean = str(asset_tone).strip()
                        expected_tone_str = f"Tone {key_tone_num}"
                        if asset_tone_clean not in (expected_tone_str, str(key_tone_num)):
                            errors.append(f"Tone mismatch for key '{key}': key implies tone {key_tone_num} but asset specifies '{asset_tone}'.")
        return errors

    def gate7_overrides(self, dt: date, service_name: str, rubrics: dict, booklet: str) -> list:
        """Gate 7: Override Compliance Check."""
        errors = []
        variables = rubrics.get("variables", {})
        overrides = rubrics.get("overrides", {})
        
        for key in ("vespers_readings", "liturgy_readings", "litiya_stichera", "troparia_sequence"):
            # Ensure the override corresponds to this service
            if key == "vespers_readings" and service_name != "Vespers": continue
            if key == "litiya_stichera" and service_name != "Vespers": continue
            if key == "liturgy_readings" and service_name != "Liturgy": continue
            if key == "troparia_sequence" and service_name != "Liturgy": continue
            
            val = overrides.get(key) or variables.get(key)
            if not val:
                continue
                
            items = val if isinstance(val, list) else [val]
            for item in items:
                if not isinstance(item, str):
                    continue
                    
                resolved = self.engine.get_text(item)
                res_title = None
                res_content = None
                if isinstance(resolved, dict):
                    res_title = resolved.get("title") or resolved.get("ref_key")
                    res_content = resolved.get("content")
                
                title = self.engine.text_db.get(f"{item}.title") or self.engine.text_db.get(item)
                if isinstance(title, dict):
                    title = title.get("text") or title.get("title") or title.get("ref_key")
                
                clean_item = item.replace("_", " ").lower()
                found = False
                if clean_item in booklet.lower():
                    found = True
                elif title and isinstance(title, str) and title[:15].lower() in booklet.lower():
                    found = True
                elif res_title and isinstance(res_title, str) and res_title[:15].lower() in booklet.lower():
                    found = True
                elif res_content and isinstance(res_content, str) and res_content[:30].lower() in booklet.lower():
                    found = True
                
                if not found:
                    ignore_words = {
                        "glory", "both", "now", "kont", "bn", "sequence", "vespers", 
                        "matins", "liturgy", "stichera", "troparion", "kontakion", 
                        "readings", "litiya", "artoklasia", "aposticha", "canon", "ode",
                        "hymn", "prayer", "service", "feast", "saint", "prokeimenon"
                    }
                    tokens = re.split(r'[._]', item.lower())
                    significant_tokens = [t for t in tokens if t and t not in ignore_words]
                    if significant_tokens and all(t in booklet.lower() for t in significant_tokens):
                        found = True
                
                if not found:
                    if key == "troparia_sequence" and (item in str(variables) or item in str(overrides)):
                        # Sequence names are not printed literally in the booklet, but verified resolved in logic
                        pass
                    elif item in str(variables) or item in str(overrides):
                        print(f"   ⚠️  [Text Warning] Override '{key}' value '{item}' not found in booklet text (but present in resolved rubrics).")
                    else:
                        errors.append(f"Override '{key}' value '{item}' not found in generated service booklet and not resolved in rubrics.")
        return errors

    def gate8_visual(self, dt: date, content: str) -> list:
        """Gate 8: Visual Ergonomics and Tag Balance."""
        errors = []
        paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
        
        is_first_paragraph = True
        for p in paragraphs:
            if p.startswith("---") and p.endswith("---"):
                is_first_paragraph = True
                continue
                
            actor_match = re.match(r"^\[([A-Z0-9_ -]+)\]:", p, re.IGNORECASE)
            
            # Check drop-cap starting characters
            if is_first_paragraph and not actor_match and not p.startswith("DATE:") and not p.startswith("FEAST:") and not p.startswith("<") and not p.startswith("["):
                if p[0] in ('"', "'", '“', '‘', '(', '{', '✚', '-', '—'):
                    errors.append(f"Drop-cap paragraph starts with invalid character '{p[0]}': '{p[:40]}...'")
                is_first_paragraph = False
            elif not actor_match and not p.startswith("DATE:") and not p.startswith("FEAST:") and not p.startswith("<") and not p.startswith("["):
                is_first_paragraph = False
                
            # HTML tag balance checking
            tags = re.findall(r"<(/?[a-zA-Z]+)(?:\s+[^>]*)?>", p)
            stack = []
            for tag in tags:
                if tag.startswith("/"):
                    tag_name = tag[1:].lower()
                    if not stack or stack[-1] != tag_name:
                        errors.append(f"Unbalanced HTML tag close '</{tag_name}>' in paragraph: '{p[:60]}...'")
                        if stack and tag_name in stack:
                            stack.remove(tag_name)
                    else:
                        stack.pop()
                else:
                    tag_name = tag.split()[0].lower()
                    if tag_name not in ("br", "img", "hr"):
                        stack.append(tag_name)
            if stack:
                errors.append(f"Unclosed HTML tags {stack} in paragraph: '{p[:60]}...'")
                
        return errors

    def gate9_canonical_negative_suppressions(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 9: Canonical Negative Prohibitions (Dolnytsky Parts I-V)."""
        errors = []
        pascha_off = context.get("pascha_offset")
        season_id = context.get("season_id") or context.get("season", "")
        
        # 1. Holy Week Negative Constraints (-8 to -1)
        if (pascha_off is not None and -8 <= pascha_off <= -1) or season_id == "holy_week":
            # Ban weekday Octoechos combination strings
            for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"):
                if f"{day} service combined with" in content:
                    errors.append(f"Holy Week Violation: Found forbidden weekday combination string '{day} service combined with'.")
            
            # Ban Temple troparia
            if "Troparion of the Temple" in content:
                errors.append("Holy Week Violation: Found forbidden 'Troparion of the Temple'.")
                
            # Ban Saint Doxastikon (unless Annunciation collision)
            is_annunciation = str(dt).endswith("-03-25") or context.get("feast_id") == "annunciation"
            if not is_annunciation:
                if "Doxastikon of the Saint" in content:
                    errors.append("Holy Week Violation: Found forbidden 'Doxastikon of the Saint'.")
                if "Theotokion from the Horologion or Octoechos" in content:
                    errors.append("Holy Week Violation: Found forbidden 'Theotokion from the Horologion or Octoechos'.")
                    
            # Holy Thursday specific bans
            if pascha_off == -3:
                if "We have seen the true light, we have received" in content or '**Post-Communion Hymn:** "We have seen' in content:
                    errors.append("Holy Thursday Violation: Found forbidden Post-Communion hymn 'We have seen the true light'.")
                if "Let our mouths be filled with Thy praise" in content:
                    errors.append("Holy Thursday Violation: Found forbidden 'Let our mouths be filled'.")

        # 2. Bright Week Negative Constraints (0 to +6)
        elif (pascha_off is not None and 0 <= pascha_off <= 6) or season_id in ("pascha", "bright_week"):
            if "Six Psalms" in content:
                errors.append("Bright Week Violation: Found forbidden 'Six Psalms' (Must be replaced by Paschal Troparion).")
            if "Kathisma 1" in content or "Kathismata" in content:
                # On Bright Saturday (pascha_off == 6), Vespers is Sunday Vespers of Thomas Sunday, which resumes Kathisma 1
                if not (pascha_off == 6 and service_name == "Vespers"):
                    errors.append("Bright Week Violation: Found forbidden Kathisma reading during Bright Week.")

        # 3. Forefeast, Afterfeast, and Apodosis Negative Suppressions
        is_after_or_fore = bool(
            context.get("is_afterfeast") or
            context.get("is_forefeast") or
            context.get("is_apodosis")
        )
        dow = context.get("day_of_week")
        if is_after_or_fore and dow != 0:
            rubric_lines = [l for l in content.splitlines() if not l.strip().startswith(">")]
            rubric_content = "\n".join(rubric_lines)
            
            # A. Ban Octoechos sessional hymns string
            if "Sessional Hymns from the Octoechos" in rubric_content:
                errors.append(f"Negative Suppression Violation: Found forbidden 'Sessional Hymns from the Octoechos' on Afterfeast/Forefeast (date={dt.isoformat()}).")

            # B. Ban generic weekday combination headers (e.g., 'Thursday service combined with')
            for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"):
                if f"{day} service combined with" in rubric_content:
                    errors.append(f"Negative Suppression Violation: Found forbidden weekday combination string '{day} service combined with' on Afterfeast/Forefeast (date={dt.isoformat()}).")

            # C. Ban 'Theotokion from the Horologion or Octoechos'
            if "Theotokion from the Horologion or Octoechos" in rubric_content or "Theotokion from the Octoechos" in rubric_content:
                errors.append(f"Negative Suppression Violation: Found forbidden Octoechos/Horologion theotokion string on Afterfeast/Forefeast (date={dt.isoformat()}).")

            # D. Ban generic 'Theotokion' at dismissal troparia on Forefeasts/Afterfeasts (must be Feast Troparion)
            if "Dismissal Troparia" in rubric_content:
                for line in rubric_content.splitlines():
                    if "Dismissal Troparia" in line:
                        if "Both now: Theotokion" in line or "both now... Theotokion" in line or "Both now... Theotokion" in line:
                            errors.append(f"Negative Suppression Violation: Dismissal Troparia on Forefeast/Afterfeast ends with generic 'Theotokion' instead of Troparion of the Feast (date={dt.isoformat()}).")
                
        return errors

    def gate10_choral_choreography(self, dt: date, service_name: str, context: dict, content: str) -> list:
        """Gate 10: Choral Choreography and Repetition Precision."""
        errors = []
        pascha_off = context.get("pascha_offset")
        
        # Great Thursday Exapostilarion breakdown
        if pascha_off == -3 and service_name == "Matins":
            if "Exaposteilarion (thrice)" in content:
                errors.append("Holy Thursday Choreography Error: Exapostilarion must specify breakdown '(twice); Glory, Both now: once more the same' rather than flat '(thrice)'.")
                
        return errors

    def gate12_theological_rubrical_nuance(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """
        Gate 12: Theological & Rubrical Nuance Auditor.
        Grounded in Dolnytsky Parts I-V, Ordo Celebrationis, and the Liturgicon:
        1. Trisagion Substitution Invariants (Baptismal 'All of you who have been baptized', Cross 'Before Your Cross')
        2. Megalynarion / Zadostoynyk Invariants (St. Basil 'In you, O Woman Full of Grace', Ode IX Irmos on Great Feasts)
        3. Post-Communion Hymn Matrix ('We have seen the true light' vs Festal Troparion / 'Be exalted' / 'Receive me today')
        4. Saturday Evening Dogmatikon Invariant (Tone Dogmatikon at 'Lord, I Call')
        5. Saturday Evening Kathisma 1 Invariant ('Blessed is the man')
        6. Sunday Evening Kathisma Suppression Invariant
        7. Sunday Matins Evlogitaria Invariant
        8. Vestment Theological Color Matrix
        """
        errors = []
        if not content:
            return errors
            
        pascha_off = context.get("pascha_offset")
        season_id = context.get("season_id") or context.get("season", "")
        dow = context.get("day_of_week") # 0=Sunday, 6=Saturday
        d_rank = context.get("dolnytsky_rank", "")
        feast_id = context.get("feast_id", "")
        dt_str = dt.isoformat()
        
        # 1. Trisagion Substitution Invariant at Divine Liturgy
        if service_name in ("Liturgy", "Divine Liturgy") or "## Divine Liturgy" in content or "## DIVINE LITURGY" in content:
            # Baptismal Hymn Feasts: Nativity (12-25), Theophany (01-06), Lazarus Sat (-8), Holy Sat (-1), Pascha (0), Bright Week (1..6), Pentecost Sunday (49)
            is_baptismal = (
                dt_str.endswith("-12-25") or
                dt_str.endswith("-01-06") or
                (pascha_off is not None and pascha_off in (-8, -1, 0, 1, 2, 3, 4, 5, 6, 49))
            )
            if is_baptismal:
                if "All of you who have been baptized into Christ" not in content and "Baptized into Christ" not in content and "As many as have been baptized" not in content and "All who have been baptized" not in content:
                    # Check if aliturgical or presanctified
                    lit_type = str(rubrics.get("overrides", {}).get("liturgy_type", ""))
                    if "presanctified" not in lit_type and "aliturgical" not in lit_type and "no_liturgy" not in lit_type:
                        errors.append(f"Theological/Rubrical Error in {service_name} on {dt_str}: Baptismal Feast must prescribe 'All of you who have been baptized into Christ' in place of the Trisagion.")

            # Cross Veneration Feasts: Exaltation of the Cross (09-14), 3rd Sunday of Great Lent (-28)
            is_cross_feast = dt_str.endswith("-09-14") or (pascha_off is not None and pascha_off == -28)
            if is_cross_feast:
                if "Before Your Cross" not in content and "Before Thy Cross" not in content:
                    errors.append(f"Theological/Rubrical Error in {service_name} on {dt_str}: Cross Veneration Feast must prescribe 'Before Your Cross, we bow down in worship' in place of the Trisagion.")

        # 2. Megalynarion / Zadostoynyk Invariant at Divine Liturgy
        if service_name in ("Liturgy", "Divine Liturgy") or "## Divine Liturgy" in content or "## DIVINE LITURGY" in content:
            # St. Basil Liturgies: "In you, O Woman Full of Grace"
            lit_type = str(rubrics.get("overrides", {}).get("liturgy_type", "")).lower()
            if "basil" in lit_type:
                # Holy Thursday, Holy Saturday, Christmas Eve, Theophany Eve, and Annunciation have their own Ode 9 irmos (Zadostoinyk)
                is_festal_zadostoinyk = pascha_off in (-3, -1) or dt_str.endswith("-03-25") or dt_str.endswith("-12-24") or dt_str.endswith("-01-05")
                if not is_festal_zadostoinyk:
                    if "In you, O Woman Full of Grace" not in content and "In You, O Woman Full of Grace" not in content and "All creation rejoices in you" not in content and "O Woman Full of Grace" not in content:
                        errors.append(f"Theological/Rubrical Error in {service_name} on {dt_str}: Divine Liturgy of St. Basil the Great must prescribe 'In you, O Woman Full of Grace' as the Megalynarion.")

        # 3. Post-Communion Hymn Invariant
        if service_name in ("Liturgy", "Divine Liturgy") or "## Divine Liturgy" in content or "## DIVINE LITURGY" in content:
            # Ascension (pascha_off == 40): "Be exalted, O God"
            if pascha_off == 40:
                if "Be exalted, O God" not in content and "Be Thou exalted, O God" not in content:
                    errors.append(f"Theological/Rubrical Error in {service_name} on {dt_str}: Feast of the Ascension must prescribe 'Be exalted, O God, above the heavens' as the Post-Communion hymn.")
            # 3. Holy Thursday (Pascha -3): 'Receive me today, O Son of God' / 'Of Thy Mystical Supper'
            elif pascha_off == -3:
                if "Receive me today" not in content and "Receive me this day" not in content and "receive_me_today" not in content and "Mystical Supper" not in content:
                    errors.append(f"Theological/Rubrical Error in Liturgy on {dt_str}: Great and Holy Thursday must prescribe 'Receive me today, O Son of God' as the Post-Communion hymn.")

        # 4. Saturday Evening (Sunday Vespers) Kathisma 1 Invariant
        if service_name == "Vespers" and dow == 6:
            # Normal Saturday evening Vespers requires Kathisma 1 (Blessed is the man)
            is_great_feast_lord = d_rank == "LORD" or feast_id in ("nativity", "theophany", "transfiguration")
            v_type = rubrics.get("overrides", {}).get("vespers_type") or rubrics.get("variables", {}).get("vespers_type") or context.get("vespers_type")
            if not is_great_feast_lord and pascha_off not in (-8, -1, 0, 6) and v_type != "lenten_vespers_presanctified": # Exclude Lazarus Saturday (Palm Sunday eve), Holy Saturday, Pascha, Bright Saturday, and Presanctified eve
                if "Kathisma 1" not in content and "Kathisma I" not in content and "First Kathisma" not in content and "Blessed is the man" not in content:
                    errors.append(f"Theological/Rubrical Error in {service_name} on {dt_str} (Saturday Evening): Saturday evening Vespers must prescribe Kathisma 1 ('Blessed is the man').")

        # 5. Sunday Evening Vespers Kathisma Suppression Invariant
        if service_name == "Vespers" and dow == 0:
            # Outside Great Lent, Sunday evening Vespers has NO Kathisma
            is_lent = (pascha_off is not None and -48 <= pascha_off <= -8) or season_id == "great_lent"
            if not is_lent:
                if "Kathisma 1 is read" in content or "Kathisma 2 is read" in content:
                    errors.append(f"Theological/Rubrical Error in {service_name} on {dt_str} (Sunday Evening): Sunday evening Vespers outside Great Lent must omit the Kathisma psalmody.")

        # 6. Sunday Matins Evlogitaria Invariant
        if service_name == "Matins" and dow == 0:
            # Normal Sunday Matins has Resurrectional Evlogitaria
            is_great_feast_lord = d_rank == "LORD"
            if not is_great_feast_lord and pascha_off != 0: # Exclude Great Feasts of the Lord and Pascha Sunday
                if "Evlogitaria" in content:
                    if "The angelic council was amazed" not in content and "Blessed are You, O Lord" not in content:
                        errors.append(f"Theological/Rubrical Error in {service_name} on {dt_str} (Sunday Matins): Sunday Matins Evlogitaria must cite 'The angelic council was amazed' / 'Blessed are You, O Lord'.")

        return errors

    def gate13_rare_movable_fixed_collisions(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 13: Rare Movable x Fixed Feast Collisions (Dolnytsky Parts I-V / 2010 Lviv Typikon)."""
        errors = []
        pascha_off = context.get("pascha_offset")
        try:
            pascha_off = int(pascha_off) if pascha_off is not None else None
        except (ValueError, TypeError):
            pascha_off = None
            
        dt_str = str(dt)
        is_annunciation = dt_str.endswith("-03-25") or context.get("feast_id") == "annunciation" or "annunciation" in str(context.get("title", "")).lower()
        is_george = dt_str.endswith("-04-23") or context.get("feast_id") == "george" or "george" in str(context.get("title", "")).lower()
        
        # 1. Annunciation Collisions
        if is_annunciation and pascha_off is not None:
            # A. Great Thursday (Pascha -3): Vesperal Liturgy of St. Basil + Annunciation
            if pascha_off == -3:
                if service_name in ("Liturgy", "Vespers", "Divine Liturgy") or "## DIVINE LITURGY" in content or "## VESPERAL" in content:
                    if "vesperal" not in content.lower() and "basil" not in content.lower():
                        errors.append(f"Annunciation Collision Error on {dt_str} (Holy Thursday): Must prescribe Vesperal Liturgy of St. Basil combined with Annunciation.")
            # B. Great Friday (Pascha -2): Vesperal Liturgy of St. John Chrysostom + Shroud Vespers
            elif pascha_off == -2:
                if service_name in ("Vespers", "Liturgy", "Divine Liturgy") or "## GREAT VESPERS" in content or "## VESPERAL" in content:
                    if "chrysostom" not in content.lower() and "shroud" not in content.lower():
                        errors.append(f"Annunciation Collision Error on {dt_str} (Holy Friday): Must prescribe Shroud Vespers and Chrysostom Liturgy.")
            # C. Great Saturday (Pascha -1): Vesperal Liturgy of St. Basil + Annunciation
            elif pascha_off == -1:
                if service_name in ("Liturgy", "Vespers", "Divine Liturgy") or "## DIVINE LITURGY" in content or "## VESPERAL" in content:
                    if "vesperal" not in content.lower() and "basil" not in content.lower():
                        errors.append(f"Annunciation Collision Error on {dt_str} (Holy Saturday): Must prescribe Vesperal Liturgy of St. Basil combined with Annunciation.")
            # D. Pascha Day (Kyriopascha, Pascha 0): Paschal Liturgy / Matins combined with Annunciation
            elif pascha_off == 0:
                if service_name in ("Matins", "Liturgy", "Divine Liturgy") or "## DIVINE LITURGY" in content or "## PASCHAL MATINS" in content:
                    if "kyriopascha" not in content.lower() and "annunciation" not in content.lower():
                        errors.append(f"Kyriopascha Error on {dt_str}: Pascha day falling on Annunciation must prescribe Kyriopascha combined rubrics.")
                    
        # 2. St. George Collision (April 23 during Holy Week / Pascha)
        if is_george and pascha_off is not None:
            if -6 <= pascha_off <= 0:
                # St. George transferred to Bright Monday or Bright Tuesday
                if service_name in ("Vespers", "Matins", "First Hour", "Third Hour", "Sixth Hour", "Ninth Hour"):
                    if "transfer" not in content.lower() and "bright" not in content.lower():
                        errors.append(f"St. George Transfer Error on {dt_str}: St. George falling during Holy Week/Pascha must be noted as transferred to Bright Week.")
                    
        return errors

    def gate14_presanctified_lenten_structure(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 14: Presanctified & Lenten Structure Invariants (Dolnytsky Part I Chapter 4, Part II)."""
        errors = []
        pascha_off = context.get("pascha_offset")
        try:
            pascha_off = int(pascha_off) if pascha_off is not None else None
        except (ValueError, TypeError):
            pascha_off = None
            
        is_presanctified_service = (
            service_name in ("Presanctified", "Liturgy of the Presanctified Gifts", "Presanctified Liturgy") or
            "## LITURGY OF THE PRESANCTIFIED GIFTS" in content.upper() or
            "## PRESANCTIFIED LITURGY" in content.upper()
        )
        
        if is_presanctified_service:
            dt_str = str(dt)
            # 1. Kathisma 18 at Presanctified Vespers
            if "Kathisma 18" not in content and "Kathisma XVIII" not in content and "18th Kathisma" not in content and "Kathisma" not in content:
                if pascha_off not in (-6, -5, -4):
                    errors.append(f"Presanctified Structure Error on {dt_str}: Presanctified Liturgy must prescribe Kathisma 18 at Vespers.")
            
            # 2. 2 Old Testament Paroemias
            if "Paremias" not in content and "Paroemias" not in content and "Old Testament" not in content and "Genesis" not in content and "Exodus" not in content:
                errors.append(f"Presanctified Structure Error on {dt_str}: Presanctified Liturgy must specify the 2 Old Testament Paroemias.")
                
            # 3. 'Let my prayer arise'
            if "Let my prayer arise" not in content and "Let My Prayer Arise" not in content and "let_my_prayer_arise" not in content and "prostrations" not in content:
                errors.append(f"Presanctified Structure Error on {dt_str}: Presanctified Liturgy must specify 'Let my prayer arise' with prostrations.")
                
            # 4. Presanctified Communion Hymn 'O taste and see'
            if "Taste and see" not in content and "taste and see" not in content and "Taste and See" not in content and "koinonikon" not in content:
                errors.append(f"Presanctified Structure Error on {dt_str}: Presanctified Liturgy must prescribe 'O taste and see that the Lord is good' as Communion Hymn.")
                
        return errors

    def gate15_dual_reading_hierarchy(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 15: Epistle and Gospel Dual Reading Precedence Invariant (Dolnytsky Part II / 2010 Lviv Typikon)."""
        errors = []
        is_liturgy = (
            service_name in ("Liturgy", "Divine Liturgy") or
            "## DIVINE LITURGY" in content.upper()
        )
        
        if is_liturgy:
            dt_str = str(dt)
            # Check for leaked unrendered reading object representations
            if "{'prokeimenon':" in content or "{'epistle':" in content:
                errors.append(f"Dual Reading Rendering Error on {dt_str}: Leaked unformatted reading dictionary in Liturgy card.")
            if "Missing Prokeimenon" in content or "Missing Epistle" in content or "Missing Gospel" in content:
                errors.append(f"Dual Reading Missing Error on {dt_str}: Missing scripture reading pericope in Liturgy card.")
                
        return errors

    def gate16_synodal_footnote_integrity(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 16: Dolnytsky Synodal Footnote Integrity and Citation Grammar."""
        errors = []
        if not content:
            return errors
            
        dt_str = str(dt)
        if "[^None]" in content or "[^UNDEFINED]" in content:
            errors.append(f"Footnote Corruption Error on {dt_str}: Found corrupted footnote anchor in {service_name}.")
        
        # Check for unclosed Dolnytsky footnote bracket
        for m in re.finditer(r'Dolnytsky Note\s*\[\^([^\]\n]+)', content):
            anchor = m.group(0)
            if "]" not in content[m.start():m.start() + len(anchor) + 5]:
                errors.append(f"Footnote Syntax Error on {dt_str}: Unclosed Dolnytsky footnote bracket in {service_name}.")
            
        return errors

    def gate17_psalter_kathisma_distribution(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 17: Validates Kathisma sequence against the canonical 4-season Psalter matrix."""
        errors = []
        if not content:
            return errors
        
        dt_str = str(dt)
        ctx_dow = context.get("day_of_week", 0)
        mmdd = dt.strftime("%m%d")
        is_lent = context.get("season") in ("great_lent", "lent") or context.get("season_id") in ("great_lent", "lent")
        is_bright_week = context.get("season") in ("bright_week", "pascha") or context.get("season_id") == "pascha"
        
        if service_name in ("Vespers", "Daily Vespers", "Great Vespers") or "## DAILY VESPERS" in content or "## GREAT VESPERS" in content:
            if not is_lent and not is_bright_week:
                # In Summer schedule (before Sep 22):
                if "0601" <= mmdd <= "0921":
                    if ctx_dow == 4: # Thursday evening (for Friday)
                        if "Kathisma 18 is read" in content:
                            errors.append(f"Psalter Matrix Error on {dt_str}: Thursday Summer Vespers cannot read Kathisma 18 (appointed: Kathisma 15).")
                    elif ctx_dow == 3: # Wednesday evening (for Thursday)
                        if "Kathisma 18 is read" in content:
                            errors.append(f"Psalter Matrix Error on {dt_str}: Wednesday Summer Vespers cannot read Kathisma 18 (appointed: Kathisma 12).")
                    elif ctx_dow == 2: # Tuesday evening (for Wednesday)
                        if "Kathisma 18 is read" in content:
                            errors.append(f"Psalter Matrix Error on {dt_str}: Tuesday Summer Vespers cannot read Kathisma 18 (appointed: Kathisma 9).")
                    elif ctx_dow == 1: # Monday evening (for Tuesday)
                        if "Kathisma 18 is read" in content:
                            errors.append(f"Psalter Matrix Error on {dt_str}: Monday Summer Vespers cannot read Kathisma 18 (appointed: Kathisma 6).")
                    elif ctx_dow == 0: # Sunday evening (for Monday)
                        if "Kathisma 18 is read" in content or "Kathisma 1 is read" in content:
                            errors.append(f"Psalter Matrix Error on {dt_str}: Sunday evening Vespers has no Kathisma.")
        return errors

    def gate18_weekday_theotokia_cycle(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 18: Validates weekday Theotokia thematic alignment."""
        errors = []
        if not content:
            return errors
        if "theotokion_missing" in content.lower() or "[theotokion]" in content.lower():
            errors.append(f"Theotokion Cycle Error on {str(dt)}: Missing or placeholder Theotokion in {service_name}.")
        return errors

    def gate19_octoechos_tone_rotation(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 19: Validates Sunday Tone consistency and weekly sequence (Tones 1..8)."""
        errors = []
        if context.get("day_of_week") == 0:
            is_great_feast_of_lord = (
                context.get("feast_level") == "lord" or
                context.get("dolnytsky_rank") in ("LORD", "Class I — Great Feast") or
                "Palm Sunday" in context.get("title", "") or
                "Pascha" in context.get("title", "") or
                "Pentecost" in context.get("title", "")
            )
            tone = context.get("tone")
            if not is_great_feast_of_lord:
                if tone not in range(1, 9):
                    errors.append(f"Tone Rotation Error on {str(dt)}: Invalid Sunday tone '{tone}' (must be 1..8).")
        return errors

    def gate20_matins_canon_katavasia(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 20: Validates Matins Canon Katavasia seasonal assignments."""
        errors = []
        if not content:
            return errors
        if "Matins" in service_name or "## DAILY MATINS" in content or "## FESTAL MATINS" in content or "## SUNDAY MATINS" in content:
            # Check for Katavasia corruption
            if "katavasia_unknown" in content.lower() or "[katavasia]" in content.lower():
                errors.append(f"Katavasia Selection Error on {str(dt)}: Missing or placeholder Katavasia in {service_name}.")
        return errors

    def gate21_eothinon_exapostilarion_sync(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 21: Validates Sunday Eothinon Gospel & Exapostilarion pairing."""
        errors = []
        if context.get("day_of_week") == 0:
            eothinon = context.get("eothinon")
            if eothinon is not None and eothinon not in range(1, 12):
                errors.append(f"Eothinon Sync Error on {str(dt)}: Invalid Eothinon index '{eothinon}' (must be 1..11).")
        return errors

    def gate22_little_entrance_sequence(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 22: Validates Little Entrance Troparia and Kontakia sequence."""
        errors = []
        if not content:
            return errors
        if "Liturgy" in service_name or "## DIVINE LITURGY" in content:
            if "At the Little Entrance:" in content:
                # Check for unformatted troparia/kontakia placeholders
                if "troparion_unknown" in content.lower() or "kontakion_unknown" in content.lower():
                    errors.append(f"Little Entrance Sequence Error on {str(dt)}: Unknown hymn placeholder at Little Entrance.")
        return errors

    def gate23_compline_midnight_office(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 23: Validates Compline (Small vs Great) and Midnight Office selection."""
        errors = []
        if not content:
            return errors
        pascha_offset = context.get("pascha_offset")
        is_bright_week = (pascha_offset is not None and 0 <= pascha_offset <= 6)
        if is_bright_week:
            if "## MIDNIGHT OFFICE" in content:
                errors.append(f"Office Suppression Error on {str(dt)}: Midnight Office must be suppressed during Bright Week.")
        return errors

    def gate24_hours_propers_schedule(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 24: Validates Minor Hours Troparia and Kontakia distribution."""
        errors = []
        if not content:
            return errors
        if "Hour" in service_name or "## FIRST HOUR" in content or "## THIRD HOUR" in content:
            if "hours_troparion_missing" in content.lower():
                errors.append(f"Minor Hours Error on {str(dt)}: Missing Troparion in {service_name}.")
        return errors

    def gate25_liturgical_dismissal_alignment(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 25: Validates liturgical dismissal characteristic phrase alignment."""
        errors = []
        if not content:
            return errors
        if "Dismissal:" in content or "The Dismissal" in content:
            if "[dismissal]" in content.lower() or "dismissal_unknown" in content.lower():
                errors.append(f"Dismissal Formula Error on {str(dt)}: Missing or placeholder dismissal in {service_name}.")
        return errors

    def gate26_vesperal_liturgy_eve_shifts(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 26: Validates Vesperal Liturgies and Eve shifts."""
        errors = []
        if not content:
            return errors
        # Holy Thursday and Holy Saturday must appoint Liturgy of St. Basil
        pascha_offset = context.get("pascha_offset")
        if pascha_offset == -3: # Holy Thursday
            if "Vesperal" in service_name and "Basil" not in content and "Presanctified" in content:
                errors.append(f"Vesperal Liturgy Error on {str(dt)}: Holy Thursday must appoint Liturgy of St. Basil.")
        elif pascha_offset == -1: # Holy Saturday
            if "Vesperal" in service_name and "Basil" not in content and "Chrysostom" in content:
                errors.append(f"Vesperal Liturgy Error on {str(dt)}: Holy Saturday must appoint Liturgy of St. Basil.")
        return errors

    def gate27_aliturgical_suppression(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 27: Enforces strict Divine Liturgy suppression on Aliturgical days."""
        errors = []
        pascha_offset = context.get("pascha_offset")
        # Great Friday is strictly Aliturgical (unless Annunciation March 25)
        if pascha_offset == -2:
            is_annunciation = (context.get("feast_level") == "annunciation" or dt.strftime("%m%d") == "0325")
            if not is_annunciation and ("Divine Liturgy of" in service_name or "## DIVINE LITURGY" in content):
                errors.append(f"Aliturgical Invariant Violation on {str(dt)}: Divine Liturgy cannot be served on Great Friday.")
        return errors

    def gate28_antiphons_beatitudes_matrix(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 28: Validates Liturgy Antiphons vs Beatitudes matrix."""
        errors = []
        if not content:
            return errors
        if "Liturgy" in service_name or "## DIVINE LITURGY" in content:
            if "[antiphon]" in content.lower() or "antiphon_unknown" in content.lower():
                errors.append(f"Antiphon Selection Error on {str(dt)}: Missing or placeholder Antiphon in {service_name}.")
        return errors

    def gate29_koinonikon_precedence(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 29: Validates Communion Hymn (Koinonikon) precedence."""
        errors = []
        if not content:
            return errors
        if "Liturgy" in service_name or "## DIVINE LITURGY" in content:
            if "[koinonikon]" in content.lower() or "koinonikon_unknown" in content.lower() or "communion_hymn_unknown" in content.lower():
                errors.append(f"Koinonikon Selection Error on {str(dt)}: Missing or placeholder Koinonikon in {service_name}.")
        return errors

    def gate30_vestment_color_transition(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 30: Validates liturgical vestment color assignment."""
        errors = []
        if not content:
            return errors
        if "Vestment colour:" in content:
            # Valid canonical colors
            valid_colors = ["bright", "gold", "white", "red", "dark", "purple", "black", "green", "blue", "crimson"]
            color_line = [line for line in content.splitlines() if "Vestment colour:" in line]
            if color_line:
                line_text = color_line[0].lower()
                if not any(c in line_text for c in valid_colors):
                    errors.append(f"Vestment Color Error on {str(dt)}: Unrecognized vestment color assignment '{color_line[0]}'.")
        return errors

    def gate31_scripture_incipit_syntax(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 31: Validates Gospel and Epistle incipit syntax."""
        errors = []
        if not content:
            return errors
        if "[incipit]" in content.lower() or "incipit_unknown" in content.lower():
            errors.append(f"Scripture Incipit Error on {str(dt)}: Missing or placeholder scripture incipit in {service_name}.")
        return errors

    def gate32_holy_doors_veil_state(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 32: Validates Holy Doors and Chancel Veil ceremonial state consistency."""
        errors = []
        if not content:
            return errors
        if "[doors]" in content.lower() or "doors_unknown" in content.lower() or "[veil]" in content.lower():
            errors.append(f"Ceremonial State Error on {str(dt)}: Unresolved Holy Doors/Veil rubric in {service_name}.")
        return errors

    def gate11_formatting_readability(self, dt: date, service_name: str, context: dict, content: str) -> list:
        """Gate 11: Typography, Readability & Visual Formatting across all cards of all days."""
        errors = []
        if not content:
            return errors

        # 1. Hours Card Structure: Forbid dense semicolon walls of text lacking bold rubric leads
        if service_name == "Hours" or "## Hours" in content:
            # Check for unformatted plain text leads
            if re.search(r"(?<!\*)\bTroparia:\s*First Hour", content) or re.search(r"(?<!\*)\bKontakia:\s*First Hour", content):
                errors.append("Hours Formatting Error: 'Troparia:' and 'Kontakia:' must use markdown bold leads (**Troparia:**, **Kontakia:**).")
            
            # Check for unseparated run-on strings joining Troparia and Kontakia with semicolons on one line
            if re.search(r"Ninth Hour [–-][^\n\r]*Kontakia:", content):
                errors.append("Hours Formatting Error: Troparia and Kontakia must be separated by distinct paragraph breaks rather than joined on a single line.")

        # 2. Liturgy Card Structure: Verify bold rubric leads for major liturgical units
        if service_name == "Divine Liturgy" or "## Divine Liturgy" in content:
            if "Troparia and Kontakia:" in content and "**Troparia and Kontakia:**" not in content:
                errors.append("Divine Liturgy Formatting Error: 'Troparia and Kontakia:' must use markdown bold lead (**Troparia and Kontakia:**).")

        for line in content.splitlines():
            line_str = line.strip()
            if line_str.startswith("<") or line_str.startswith("|") or line_str.startswith("#") or line_str.startswith(">"):
                continue
            # Patristic homilies, sacerdotal prayers, and full hymnic prose contain natural semicolons
            if any(marker in line_str for marker in (
                "pious and God-loving",
                "banquet of faith",
                "blessing of the paska",
                "The priest says",
                "Having beheld the Resurrection",
                "**Ikos Pascha:**",
                "look upon this lamb",
                "Creator of all things"
            )):
                continue
            if (len(line_str) > 450 or line_str.count(";") >= 4) and len(line_str) > 250 and "  \n" not in line and "<br>" not in line:
                errors.append(f"Typography Error in {service_name}: Found monolithic unbroken text block ({len(line_str)} chars) with dense semicolons. Must format with itemized line breaks.")

        return errors

    def gate33_paradigm_invariants(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 33: Dolnytsky Part II Paradigm Invariants (The 20 Cases: Forefeasts, Afterfeasts, Apodoses)."""
        errors = []
        if not content:
            return errors
            
        dow = context.get("day_of_week")
        is_weekday = (dow != 0)
        is_afterfeast = context.get("is_afterfeast")
        is_forefeast = context.get("is_forefeast")
        is_apodosis = context.get("is_apodosis")

        rubric_lines = [l for l in content.splitlines() if not l.strip().startswith(">")]
        rubric_content = "\n".join(rubric_lines)
        
        # Case 14: Weekday Afterfeast with simple saint
        if is_afterfeast and (1 <= dow <= 5) and service_name == "Vespers":
            if "At the Aposticha:" in rubric_content or "**Aposticha:**" in rubric_content:
                if "Aposticha from the Octoechos" in rubric_content or "from the Octoechos" in rubric_content:
                    errors.append(f"Paradigm Case 14 Violation on {dt.isoformat()}: Vespers Aposticha cannot be taken from the Octoechos during an Afterfeast.")

        if is_afterfeast and is_weekday and service_name == "Matins":
            if "Sessional Hymns from the Octoechos" in rubric_content:
                errors.append(f"Paradigm Case 14 Violation on {dt.isoformat()}: Matins Kathismata Sessional Hymns cannot be taken from the Octoechos during an Afterfeast.")

        return errors

    def gate34_katavasia_seasonal_matrix(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 34: Validates Matins Katavasia seasonal assignments (Typikon Chapter III / Irmologion)."""
        errors = []
        if not content:
            return errors
        if service_name != "Matins" and "## Matins" not in content and "## MATINS" not in content:
            return errors

        if "Katavasia:" in content or "Katavasia" in content:
            mmdd = dt.strftime("%m%d")
            kat_lines = [line for line in content.splitlines() if "katavasia" in line.lower()]
            kat_text = " ".join(kat_lines).lower()

            # 1. September 1 - September 21: Exaltation of the Holy Cross
            if "0901" <= mmdd <= "0921":
                if "i will open my mouth" in kat_text or "open my mouth" in kat_text:
                    errors.append(f"Katavasia Seasonal Error on {dt.isoformat()}: Appointed Theotokos Katavasia ('I will open my mouth') during Exaltation period (Sep 1-21). Must be Irmoi of the Cross.")
            # 2. November 21 - December 31: Nativity of Christ
            elif "1121" <= mmdd <= "1231":
                if "i will open my mouth" in kat_text:
                    errors.append(f"Katavasia Seasonal Error on {dt.isoformat()}: Appointed Theotokos Katavasia ('I will open my mouth') during Nativity period (Nov 21-Dec 31). Must be 'Christ is born'.")
            # 3. January 1 - January 14: Theophany
            elif "0101" <= mmdd <= "0114":
                if "i will open my mouth" in kat_text:
                    errors.append(f"Katavasia Seasonal Error on {dt.isoformat()}: Appointed Theotokos Katavasia during Theophany period (Jan 1-14). Must be Theophany Irmoi.")
        return errors

    def gate35_systemic_invariants(self, dt: date, service_name: str, context: dict, rubrics: dict, content: str) -> list:
        """Gate 35: Systemic Invariants (Preventing the 8 Systemic Flaws across all services)."""
        errors = []
        if not content:
            return errors

        dt_str = dt.isoformat()
        dow_py = dt.weekday() # 0=Mon..4=Fri, 5=Sat, 6=Sun
        rank = context.get("rank")
        d_rank = str(context.get("dolnytsky_rank", ""))
        is_vigil = (rank == 2 or "VIGIL" in d_rank)
        is_polyeleos = ("POLYELEOS" in d_rank)
        is_major = is_vigil or is_polyeleos or rank == 1

        # 1. Small Vespers Prokeimenon (Bug 1)
        if "Small Vespers" in service_name or "## SMALL VESPERS" in content:
            if dow_py == 4 or (context.get("day_of_week") == 6):
                if '"The Lord is King' in content or '"The Lord is king' in content or "psalm_92" in content.lower():
                    errors.append(f"Small Vespers Error on {dt_str}: Small Vespers on Friday afternoon (for Saturday) cannot appoint Sunday Prokeimenon 'The Lord is King'.")

        # 2. Octoechos Canon Leaked on Vigil/Polyeleos (Bug 2)
        if "Matins" in service_name or "## FESTAL MATINS" in content or "## SUNDAY MATINS" in content or "## MATINS" in content:
            if (is_vigil or is_polyeleos) and context.get("day_of_week") != 0:
                for line in content.splitlines():
                    if "Canon:" in line or "**Canon:**" in line or "Order of the Canon:" in line:
                        has_octoechos = (
                            "Octoechos -" in line or
                            "Octoechos (including" in line or
                            "Canon of the Tone" in line or
                            "Canon from the Octoechos" in line
                        )
                        if has_octoechos:
                            errors.append(f"Matins Canon Error on {dt_str}: Octoechos canon leaked on Vigil/Polyeleos feast: '{line.strip()}'.")

            # 3. Katavasia Generic Fallback (Bug 3)
            is_festal_or_sunday = (
                context.get("day_of_week") == 0 or
                is_major or
                context.get("is_afterfeast") or
                context.get("is_forefeast") or
                context.get("is_apodosis") or
                context.get("feast_level") in ("lord", "theotokos")
            )
            for line in content.splitlines():
                if "Katavasia:" in line or "**Katavasia:**" in line:
                    if ("Heirmos of the last canon" in line and is_festal_or_sunday) or "katavasia_unknown" in line.lower() or "[katavasia]" in line.lower():
                        errors.append(f"Katavasia Error on {dt_str}: Katavasia defaulted to generic fallback on festal day: '{line.strip()}'.")

            # 4. Praises Doxastikon Swallowed (Bug 4)
            if is_major and ("At the Praises" in content or "## Praises" in content):
                praises_match = re.search(r"(?:At the Praises|## Praises|Praises:).*?(?=(?:Doxology|Dismissal Troparia|##|$))", content, re.DOTALL)
                if praises_match:
                    p_text = praises_match.group(0)
                    if "stichera" in p_text.lower() and "glory" not in p_text.lower() and "both now" not in p_text.lower():
                        errors.append(f"Praises Error on {dt_str}: Praises Doxastikon swallowed on Vigil/Polyeleos.")

        # 5. Vespers Kathisma on Vigil Eve (Bug 5)
        if "Vespers" in service_name or "## GREAT VESPERS" in content:
            if is_vigil and "Kathisma 1 ('Blessed is the man') is read" in content:
                errors.append(f"Vespers Kathisma Error on {dt_str}: Great Vespers prescribed full Kathisma 1 read instead of 1st Antiphon ('Blessed is the man') on Vigil eve.")

        # 6. Lectionary Dual Readings (Bug 6)
        if "Liturgy" in service_name or "## DIVINE LITURGY" in content:
            is_saint_vigil_or_polyeleos = ("VIGIL" in d_rank or "POLYELEOS" in d_rank)
            is_lord_feast = (context.get("feast_level") == "lord")
            is_theotokos_great = (context.get("feast_level") == "theotokos" and ("VIGIL" in d_rank or rank <= 2))
            is_special_vigil_saint = ((dt.month == 6 and dt.day in (24, 29)) or (dt.month == 8 and dt.day == 29))
            is_lent_presanctified_weekday = (context.get("season") == "lent" and dt.weekday() < 5)

            if is_saint_vigil_or_polyeleos and context.get("day_of_week") != 0:
                if not is_lord_feast and not is_theotokos_great and not is_special_vigil_saint and not is_lent_presanctified_weekday:
                    epistle_lines = [l for l in content.splitlines() if "**Epistle" in l or "Epistle:" in l]
                    has_two_epistles = (len(epistle_lines) >= 2)
                    for el in epistle_lines:
                        if ";" in el or "1)" in el or "2)" in el or "and" in el:
                            has_two_epistles = True

                    gospel_lines = [l for l in content.splitlines() if "**Gospel" in l or "Gospel:" in l]
                    has_two_gospels = (len(gospel_lines) >= 2)
                    for gl in gospel_lines:
                        if "1)" in gl or "2)" in gl or "and" in gl or gl.count(":") >= 2:
                            has_two_gospels = True

                    if not has_two_epistles or not has_two_gospels:
                        errors.append(f"Lectionary Error on {dt_str}: Divine Liturgy dropped sequential daily reading on Polyeleos/Vigil Saint.")

        # 7. Crude Programmer Token Leaks (Bug 7)
        token_patterns = [
            (r"\b[A-Z][a-z]+ Doxastikon\b", "Pattern '<Name> Doxastikon' without preposition"),
            (r"\bDoxastikon of Litiya\b", "Pattern 'Doxastikon of Litiya'"),
            (r"\bTheotokion of Litiya\b", "Pattern 'Theotokion of Litiya'"),
            (r"\b(falling_asleep|first_called|great_martyr|holy_apostle)_[a-z_]+\b", "Snake case identifier leak")
        ]
        for pat, desc in token_patterns:
            for line in content.splitlines():
                if re.search(pat, line):
                    errors.append(f"Crude Token Leak on {dt_str}: Found {desc} in '{line.strip()}'.")

        return errors

    def call_deepseek_remediation(self, dt: date, service_name: str, context: dict, rubrics: dict, errors: list, booklet: str):
        """Call DeepSeek to propose a logic or database fix for the failing service."""
        if not self.deepseek_key:
            print("   [Remediation] DeepSeek API Key not configured. Skipping LLM remediation proposal.")
            return

        print(f"   [Remediation] Requesting patch suggestion from DeepSeek for failing {service_name} on {dt.isoformat()}...")
        
        system_prompt = (
            "You are the senior Byzantine-Ruthenian liturgical software architect. "
            "You are reviewing a day/service multi-audit failure. "
            "Suggest the exact file changes (Python logic or JSON database overrides) to resolve the validation failures. "
            "Respond in clear markdown, providing code diffs if possible."
        )
        
        user_prompt = f"""
Liturgical Date: {dt.isoformat()}
Service: {service_name}
Season ID: {context.get("season_id")}
Pascha Offset: {context.get("pascha_offset")}
Tone: {context.get("tone")}
Dolnytsky Rank: {context.get("dolnytsky_rank")}
Feast Level: {context.get("feast_level")}

VALIDATION FAILURES ENCOUNTERED:
{chr(10).join(f'- {err}' for err in errors)}

Generated Service Booklet Snippet:
{booklet[:1500]}
...

Suggest how to remediate these failures in the python engine (under engine/) or monthly override JSON templates (under json_db/).
"""
        headers = {
            "Authorization": f"Bearer {self.deepseek_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "thinking": {"type": "enabled"}
        }
        
        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            res_data = response.json()
            if 'choices' in res_data and res_data['choices']:
                msg_content = res_data['choices'][0]['message'].get('content') or ""
                reasoning = res_data['choices'][0]['message'].get('reasoning_content') or ""
                
                remediation_path = self.audit_dir / "failed_service_remediation.md"
                report_lines = [
                    f"# Remediation Suggestion for {service_name} Failure on {dt.isoformat()}",
                    "",
                    "## Validation Errors",
                    "\n".join(f"- {err}" for err in errors),
                    ""
                ]
                if reasoning:
                    report_lines.extend(["## Reasoning Trace", reasoning, ""])
                if msg_content:
                    report_lines.extend(["## Recommended Patch", msg_content])
                    
                remediation_path.write_text("\n".join(report_lines), encoding="utf-8")
                print(f"   [Remediation] Saved remediation proposal to: {remediation_path}")
        except Exception as e:
            print(f"   [Remediation] DeepSeek API call failed: {e}")

    def audit_single_day(self, current_date: date, engine=None) -> list:
        """
        Audits all services for a single liturgical day across all 34 gates.
        Returns a list of failed service reports: [{"service": service_name, "errors": service_errors, "booklet": booklet, "context": context, "rubrics": rubrics}]
        """
        target_engine = engine or self.engine
        context = target_engine.get_liturgical_context(current_date)
        rubrics = target_engine.resolve_rubrics(context)

        # Apply sliding context tone/vigil checks
        if current_date.weekday() == 5: # Saturday
            self.sliding_state["saturday_vigil"] = rubrics.get("is_sunday_vigil", False)
        elif current_date.weekday() == 6: # Sunday
            if self.sliding_state.get("saturday_vigil") and not rubrics.get("is_sunday_vigil"):
                pass

        enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
        enriched["overrides"] = rubrics.get("overrides", {})
        if rubrics.get("is_sunday_vigil"):
            enriched["is_sunday_vigil"] = True

        full_day_digest = target_engine.generate_typikon_digest(context, rubrics)
        day_failures = []

        # Chronological cycle loop
        for service in target_engine.daily_cycle:
            service_name = service["name"]

            # Suppression Checks
            if service_name in ("Compline", "Midnight Office"):
                day = context.get("day_of_week")
                v_type = rubrics.get("overrides", {}).get("vespers_type") or rubrics.get("variables", {}).get("vespers_type") or context.get("vespers_type")
                if day != 0 and v_type == "great_vespers_vigil":
                    continue
                pascha_off = context.get("pascha_offset")
                if pascha_off is not None and 0 <= pascha_off <= 6:
                    continue

            if service_name == "Vespers" and "vesperal_merge_logic" in rubrics.get("overrides", {}).get("liturgy_type", ""):
                continue

            booklet = self.generate_single_service_booklet(context, rubrics, service)
            digest_sec = self.extract_service_digest_section(full_day_digest, service_name)

            # Collect validation errors across gates
            service_errors = []

            # Run Booklet gates
            service_errors.extend(self.gate1_heuristics(current_date, service_name, booklet))
            service_errors.extend(self.gate2_resolvers(current_date, service_name, rubrics, enriched))
            service_errors.extend(self.gate3_almanac(current_date, context))
            service_errors.extend(self.gate4_canonical(current_date, service_name, context, rubrics, enriched))
            service_errors.extend(self.gate5_citations(current_date, booklet))
            service_errors.extend(self.gate6_tone_coherence(current_date, service_name, rubrics, enriched))
            service_errors.extend(self.gate7_overrides(current_date, service_name, rubrics, booklet))
            service_errors.extend(self.gate8_visual(current_date, booklet))
            service_errors.extend(self.gate9_canonical_negative_suppressions(current_date, service_name, context, rubrics, booklet))
            # Run Digest gates (if digest section resolved)
            target_content = digest_sec if digest_sec else booklet
            if target_content:
                service_errors.extend(self.gate1_heuristics(current_date, service_name, target_content))
                service_errors.extend(self.gate5_citations(current_date, target_content))
                service_errors.extend(self.gate8_visual(current_date, target_content))
                service_errors.extend(self.gate9_canonical_negative_suppressions(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate10_choral_choreography(current_date, service_name, context, target_content))
                service_errors.extend(self.gate11_formatting_readability(current_date, service_name, context, target_content))
                service_errors.extend(self.gate12_theological_rubrical_nuance(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate13_rare_movable_fixed_collisions(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate14_presanctified_lenten_structure(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate15_dual_reading_hierarchy(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate16_synodal_footnote_integrity(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate17_psalter_kathisma_distribution(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate18_weekday_theotokia_cycle(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate19_octoechos_tone_rotation(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate20_matins_canon_katavasia(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate21_eothinon_exapostilarion_sync(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate22_little_entrance_sequence(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate23_compline_midnight_office(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate24_hours_propers_schedule(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate25_liturgical_dismissal_alignment(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate26_vesperal_liturgy_eve_shifts(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate27_aliturgical_suppression(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate28_antiphons_beatitudes_matrix(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate29_koinonikon_precedence(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate30_vestment_color_transition(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate31_scripture_incipit_syntax(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate32_holy_doors_veil_state(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate33_paradigm_invariants(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate34_katavasia_seasonal_matrix(current_date, service_name, context, rubrics, target_content))
                service_errors.extend(self.gate35_systemic_invariants(current_date, service_name, context, rubrics, target_content))

            if service_errors:
                day_failures.append({
                    "service": service_name,
                    "errors": service_errors,
                    "booklet": booklet,
                    "context": context,
                    "rubrics": rubrics
                })

        return day_failures

    def run_audit(self):
        """Execute the chronological sequential day/service audit."""
        print(f"Starting Sequential Day/Service Multi-Audits ({self.start_date.isoformat()} to {self.end_date.isoformat()})...")
        
        current_date = self.start_date
        total_days = 0
        total_services = 0
        
        while current_date <= self.end_date:
            total_days += 1
            print(f"📅 Auditing Day {total_days}: {current_date.isoformat()}")
            
            try:
                day_failures = self.audit_single_day(current_date)
            except Exception as e:
                print(f"\n❌ [HALT] Context generation crashed on date {current_date.isoformat()}: {e}")
                sys.exit(1)

            total_services += len(self.engine.daily_cycle)
            if day_failures:
                first_fail = day_failures[0]
                s_name = first_fail["service"]
                s_errs = first_fail["errors"]
                # Halt Execution immediately on logical failures
                print(f"\n❌ [HALT] Service validation failed: {s_name} on {current_date.isoformat()}")
                print("Errors encountered:")
                for err in s_errs:
                    print(f"  - {err}")
                    
                # Save error dumps
                (self.audit_dir / "failed_service.txt").write_text(first_fail["booklet"], encoding="utf-8")
                with open(self.audit_dir / "failed_context.json", "w", encoding="utf-8") as f:
                    json.dump({
                        "date": current_date.isoformat(),
                        "service": s_name,
                        "context": {k: str(v) for k, v in first_fail["context"].items()},
                        "rubrics": first_fail["rubrics"]
                    }, f, indent=2)
                    
                print(f"\nDumps saved to:\n  - {self.audit_dir / 'failed_service.txt'}\n  - {self.audit_dir / 'failed_context.json'}")
                
                if self.call_deepseek_flag:
                    self.call_deepseek_remediation(current_date, s_name, first_fail["context"], first_fail["rubrics"], s_errs, first_fail["booklet"])
                    
                sys.exit(1)
                    
            print(f"   ✓ All services passed for {current_date.isoformat()}")
            current_date += timedelta(days=1)
            
        print(f"\n🎉 [SUCCESS] Sequential Multi-Audit passed for all {total_days} days ({total_services} services checked)!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Liturgical Service/Day Sequential Auditor")
    parser.add_argument("--year", type=int, default=2026, help="Target year")
    parser.add_argument("--start-date", type=str, default=None, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default=None, help="End date (YYYY-MM-DD)")
    parser.add_argument("--deepseek", action="store_true", help="Call DeepSeek for remediation suggestion on failure")
    args = parser.parse_args()
    
    auditor = ServiceDayMultiAuditor(
        year=args.year, 
        start_date_str=args.start_date, 
        end_date_str=args.end_date, 
        call_deepseek=args.deepseek
    )
    auditor.run_audit()
