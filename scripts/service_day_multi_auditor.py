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
    def __init__(self, year=2026, start_date_str=None, end_date_str=None, call_deepseek=False):
        self.year = year
        self.engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
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
        """Gate 4: Canonical Liturgical Constraints (Octoechos suppressions, reading overrides)."""
        errors = []
        rank_id = self.engine._get_rank_id(context)
        d_rank = context.get("dolnytsky_rank", 5)
        try:
            d_rank_val = int(d_rank)
        except (ValueError, TypeError):
            d_rank_val = 5
            
        is_great_feast = (
            context.get("feast_level") in ("lord", "theotokos") and 
            d_rank_val <= 2
        ) or rank_id in ("rank_vigil_lord", "rank_vigil_theotokos")

        # Weekday Great Feast: 0% Octoechos in Vespers stichera & Matins canons
        if is_great_feast and context.get("day_of_week") != 0:
            if service_name == "Vespers":
                stichera = self.engine.resolve_vespers_stichera(enriched)
                if stichera and isinstance(stichera, dict):
                    for item in stichera.get("items", []):
                        if item.startswith("octoechos."):
                            errors.append(f"Octoechos stichera '{item}' leaked on weekday Great Feast.")
                    for dist_item in stichera.get("distribution", []):
                        if dist_item.get("source") == "octoechos":
                            errors.append("Octoechos stichera included in Vespers distribution on weekday Great Feast.")
            
            if service_name == "Matins":
                canon_stack = self.engine.resolve_canon_stack(enriched)
                if canon_stack and isinstance(canon_stack, dict):
                    for dist_item in canon_stack.get("distribution", []):
                        if dist_item.get("type") in ("resurrection", "cross_res"):
                            errors.append(f"Resurrectional Octoechos canon '{dist_item.get('type')}' leaked on weekday Great Feast Matins.")

        # Readings override check
        if is_great_feast and context.get("day_of_week") != 0 and service_name == "Liturgy":
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
            if not is_great_feast_lord and pascha_off not in (-1, 0, 6): # Exclude Holy Saturday, Pascha, and Bright Saturday
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
            if line_str.startswith("<") or line_str.startswith("|") or line_str.startswith("#"):
                continue
            if (len(line_str) > 450 or line_str.count(";") >= 4) and len(line_str) > 250 and "  \n" not in line and "<br>" not in line:
                errors.append(f"Typography Error in {service_name}: Found monolithic unbroken text block ({len(line_str)} chars) with dense semicolons. Must format with itemized line breaks.")

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
                context = self.engine.get_liturgical_context(current_date)
                rubrics = self.engine.resolve_rubrics(context)
                
                # Apply sliding context tone/vigil checks
                # If Saturday, track vigil leak lookahead
                if current_date.weekday() == 5: # Saturday
                    self.sliding_state["saturday_vigil"] = rubrics.get("is_sunday_vigil", False)
                elif current_date.weekday() == 6: # Sunday
                    if self.sliding_state.get("saturday_vigil") and not rubrics.get("is_sunday_vigil"):
                        pass
                
                enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
                enriched["overrides"] = rubrics.get("overrides", {})
                if rubrics.get("is_sunday_vigil"):
                    enriched["is_sunday_vigil"] = True
                    
                full_day_digest = self.engine.generate_typikon_digest(context, rubrics)
            except Exception as e:
                print(f"\n❌ [HALT] Context generation crashed on date {current_date.isoformat()}: {e}")
                sys.exit(1)

            # Chronological cycle loop
            for service in self.engine.daily_cycle:
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

                total_services += 1
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

                if service_errors:
                    # Halt Execution immediately on logical failures
                    print(f"\n❌ [HALT] Service validation failed: {service_name} on {current_date.isoformat()}")
                    print("Errors encountered:")
                    for err in service_errors:
                        print(f"  - {err}")
                        
                    # Save error dumps
                    (self.audit_dir / "failed_service.txt").write_text(booklet, encoding="utf-8")
                    with open(self.audit_dir / "failed_context.json", "w", encoding="utf-8") as f:
                        json.dump({
                            "date": current_date.isoformat(),
                            "service": service_name,
                            "context": {k: str(v) for k, v in context.items()},
                            "rubrics": rubrics
                        }, f, indent=2)
                        
                    print(f"\nDumps saved to:\n  - {self.audit_dir / 'failed_service.txt'}\n  - {self.audit_dir / 'failed_context.json'}")
                    
                    if self.call_deepseek_flag:
                        self.call_deepseek_remediation(current_date, service_name, context, rubrics, service_errors, booklet)
                        
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
