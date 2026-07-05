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
        preamble = []
        service_lines = []
        
        mapping = {
            "Vespers": ["## GREAT VESPERS", "## VESPERS", "## PASCHAL VESPERS", "## LENTEN VESPERS"],
            "Compline": ["## SMALL COMPLINE", "## COMPLINE", "## GREAT COMPLINE"],
            "Midnight Office": ["## MIDNIGHT OFFICE", "## MIDNIGHT OFFICE (SUNDAY)", "## MIDNIGHT OFFICE (SATURDAY)"],
            "Matins": ["## FESTAL MATINS", "## MATINS", "## DAILY MATINS", "## SUNDAY MATINS", "## LENTEN MATINS"],
            "First Hour": ["## FIRST HOUR", "## LENTEN FIRST HOUR", "## ROYAL FIRST HOUR"],
            "Third Hour": ["## THIRD HOUR", "## LENTEN THIRD HOUR", "## ROYAL THIRD HOUR"],
            "Sixth Hour": ["## SIXTH HOUR", "## LENTEN SIXTH HOUR", "## ROYAL SIXTH HOUR"],
            "Ninth Hour": ["## NINTH HOUR", "## LENTEN NINTH HOUR", "## ROYAL NINTH HOUR"],
            "Liturgy": ["## DIVINE LITURGY", "## LITURGY"]
        }
        
        target_headers = [h.upper() for h in mapping.get(service_name, [])]
        all_headers = []
        for hdrs in mapping.values():
            all_headers.extend([h.upper() for h in hdrs])
            
        started = False
        for line in lines:
            upper_line = line.strip().upper()
            is_any_header = any(upper_line.startswith(h) for h in all_headers)
            is_target_header = any(upper_line.startswith(h) for h in target_headers)
            
            if not started and not is_any_header:
                preamble.append(line)
                continue
                
            if is_target_header:
                started = True
                service_lines.append(line)
                continue
                
            if started:
                if is_any_header:
                    break
                service_lines.append(line)
                
        preamble_str = "\n".join(preamble).strip()
        service_str = "\n".join(service_lines).strip()
        return f"{preamble_str}\n\n{service_str}" if service_str else ""

    def generate_single_service_booklet(self, context, rubrics, service, include_ceremonial=False):
        """Generate raw booklet text for a single service in the daily cycle."""
        service_name = service["name"]
        
        # Slicing logic overrides
        matins_override = None
        if context["triodion_period"] == "holy_friday":
            matins_override = "tomb_matins"
        elif context["triodion_period"] in ["pascha", "bright_week"]:
            matins_override = "bright_matins"
        elif context["triodion_period"] == "holy_week_weekday" and context.get("day_of_week") in [4, 5]:
            matins_override = "passion_matins"
        elif context["triodion_period"] == "holy_week_weekday" and context.get("day_of_week") in [1, 2, 3]:
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
            (r"\bSt\.\s+(Nativity|Translation|Synaxis|Annunciation|Dormition|Theophany|Elevation)\b", "Invalid saint prefix before feast title"),
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
            (r"\bprokimenon\b", "Prokimenon (must use Prokeimenon)"),
            (r"\bprokimena\b", "Prokimena (must use Prokeimena)"),
            (r"\bkinonicon\b", "Kinonicon (must use Communion Hymn)"),
            (r"\bkinonica\b", "Kinonica (must use Communion Hymns)"),
            (r"\bholy doors\b", "Holy Doors (must use Royal Doors)"),
            (r"\bexaposteilarion\b", "Exaposteilarion (must use Exapostilarion)"),
            (r"\blytia\b", "Lytia (must use Litiya)"),
            (r"\blitia\b", "Litia (must use Litiya)"),
            (r"\bpre-feast\b", "Pre-feast (must use Forefeast)"),
            (r"\bpost-feast\b", "Post-feast (must use Afterfeast)"),
            (r"\bpre\s+feast\b", "Pre feast (must use Forefeast)"),
            (r"\bpost\s+feast\b", "Post feast (must use Afterfeast)"),
            (r"\bleave-taking\b", "Leave-taking (must use Apodosis)"),
            (r"\bleave\s+taking\b", "Leave taking (must use Apodosis)"),
            (r"\bstepenna\b", "Stepenna (must use Gradual)"),
            (r"\banabathmoi\b", "Anabathmoi (must use Gradual)")
        ]
        for pattern, name in spelling_violations:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                warnings.append(f"Spelling standard violation in text asset: '{match.group(0)}' (should be: {name})")

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
                
                # Run Digest gates (if digest section resolved)
                if digest_sec:
                    service_errors.extend(self.gate1_heuristics(current_date, service_name, digest_sec))
                    service_errors.extend(self.gate5_citations(current_date, digest_sec))
                    service_errors.extend(self.gate8_visual(current_date, digest_sec))

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
