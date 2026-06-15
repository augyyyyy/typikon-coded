import os
import sys
import re
import json
import inspect
from datetime import date, timedelta
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(os.getcwd()).resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from ruthenian_engine import RuthenianEngine

def extract_resolver_calls_from_structures(base_dir):
    """
    Scans json_db for structure definitions and components to extract
    all actual logic resolver functions along with the arguments used in the JSON.
    Returns a dict mapping func_name -> list of arg_dicts.
    """
    resolver_calls = {}
    json_dir = os.path.join(base_dir, "json_db")
    
    # Load components from 00_components.json
    components = {}
    comp_file = os.path.join(json_dir, "00_components.json")
    if os.path.exists(comp_file):
        try:
            with open(comp_file, 'r', encoding='utf-8') as f:
                cdata = json.load(f)
                components = cdata.get("components", {})
                for k, v in cdata.items():
                    if k.startswith("components."):
                        name = k.split("components.", 1)[1]
                        if name not in components:
                            components[name] = v
        except Exception:
            pass

    def scan_item(item):
        if not isinstance(item, dict):
            return
        
        # Check variable_logic
        content = item.get("content", {})
        if not content and "type" in item:
            content = item
            
        slot_type = content.get("type")
        if slot_type == "variable_logic":
            logic = content.get("logic", {})
            func_name = logic.get("function")
            args = logic.get("args", {})
            if func_name:
                if func_name not in resolver_calls:
                    resolver_calls[func_name] = []
                # Store unique argument signatures
                if args not in resolver_calls[func_name]:
                    resolver_calls[func_name].append(args)
                    
        # Check generator
        elif slot_type == "generator":
            generator_method = content.get("generator_method")
            args = content.get("args", {})
            if generator_method:
                # Generators map to resolvers in engine
                resolver_mapping = {
                    "generate_stichera_sequence": "resolve_vespers_stichera",
                    "generate_antiphons": "resolve_liturgy_antiphons",
                    "generate_hour_troparia": "resolve_hours_collision"
                }
                mapped_func = resolver_mapping.get(generator_method)
                if mapped_func:
                    if mapped_func not in resolver_calls:
                        resolver_calls[mapped_func] = []
                    if args not in resolver_calls[mapped_func]:
                        resolver_calls[mapped_func].append(args)
        
        # Check components list
        if "components" in item:
            for comp in item["components"]:
                scan_item(comp)
        if "components" in content:
            for comp in content["components"]:
                scan_item(comp)
                
        # Check conditionals
        tc = content.get("true_content")
        if tc: scan_item(tc)
        fc = content.get("false_content")
        if fc: scan_item(fc)
        
        # Check sequence
        for seq_item in item.get("sequence", []):
            scan_item(seq_item)
            
        # Check overrides
        for ov in item.get("overrides", []):
            new_comp = ov.get("new_component", {})
            if new_comp:
                scan_item(new_comp)

    # 1. Scan 00_components.json
    for cname, cdata in components.items():
        scan_item(cdata)

    # 2. Scan all structure files
    struct_files = Path(json_dir).glob("01*_struct_*.json")
    for filepath in struct_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                structs = data.get("structures", {})
                for sid, sdata in structs.items():
                    scan_item(sdata)
        except Exception:
            pass
            
    return resolver_calls

def check_value_recursively(value, text_db, errors, context_info=""):
    """
    Recursively inspects a resolver's output to check for spelling standards,
    placeholder errors, and db key existence.
    """
    if value is None:
        return

    if isinstance(value, str):
        # 1. Check spelling standard violations (current UGCC norm)
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
            if re.search(pattern, value, re.IGNORECASE):
                errors.append(f"{context_info}: Spelling standard violation: '{value}' contains forbidden word mapped to {name}")

        # 2. Check for unresolved DB keys and verify existence in text_db
        db_key_patterns = [
            r"^menaion\.\w+",
            r"^octoechos\.\w+",
            r"^triodion\.\w+",
            r"^horologion\.\w+"
        ]
        if value not in ("(No Saint Doxastikon)", "None", ""):
            for pattern in db_key_patterns:
                if re.match(pattern, value):
                    # Strip common dynamic suffixes to find the base key in text_db
                    clean_key = value
                    suffixes_to_remove = [
                        r"\.title$", r"\.glory$", r"\.both_now$", r"\.troparion$",
                        r"\.kontakion$", r"\.stichera_\d+$", r"\.aposticha_\d+$",
                        r"\.magnification$", r"\.hymn$", r"\.prokeimenon$",
                        r"\.communion_hymn$"
                    ]
                    for suff in suffixes_to_remove:
                        clean_key = re.sub(suff, "", clean_key)
                    
                    # Verify if the exact or stripped key exists
                    if value not in text_db and clean_key not in text_db:
                        # Some special cases might be valid dynamically, but let's log them
                        errors.append(f"{context_info}: Unresolved database key reference '{value}' (base: '{clean_key}') does not exist in text_db")

        # 3. Check for error/placeholder markers
        error_patterns = [
            r"\[ERROR:",
            r"\[RESOLVE:",
            r"\[CHECK:",
            r"\[MISSING",
            r"Missing in Stamford"
        ]
        for pattern in error_patterns:
            if re.search(pattern, value):
                errors.append(f"{context_info}: Found error placeholder '{value}'")

    elif isinstance(value, list):
        for i, item in enumerate(value):
            check_value_recursively(item, text_db, errors, f"{context_info}[{i}]")

    elif isinstance(value, dict):
        for k, v in value.items():
            check_value_recursively(k, text_db, errors, f"{context_info}.keys({k})")
            check_value_recursively(v, text_db, errors, f"{context_info}.{k}")

def run_recursive_resolver_audit(engine, target_date, resolver_calls):
    """
    Invokes all logic resolvers for a given date context, recursively auditing outputs.
    """
    errors = []
    try:
        context = engine.get_liturgical_context(target_date)
        rubrics = engine.resolve_rubrics(context)
        enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
        enriched["overrides"] = rubrics.get("overrides", {})
        if rubrics.get("is_sunday_vigil"):
            enriched["is_sunday_vigil"] = True
    except Exception as e:
        return [f"Context generation failed: {str(e)}"]

    # Determine active service structures for the day
    services = rubrics.get("services", [])
    active_structures = [s.get("structure_id") for s in services if s.get("structure_id")]
    
    # Loop over all resolvers found in the database
    for func_name, signatures in resolver_calls.items():
        # Optimization/Safety: Only execute resolvers permitted for the active structures
        is_permitted = False
        for struct_id in active_structures:
            if engine.resolver_registry.is_allowed(struct_id, func_name):
                is_permitted = True
                break
                
        # If no active structure permits it, we skip running it for this day
        if not is_permitted:
            continue
            
        if not hasattr(engine, func_name):
            errors.append(f"Resolver {func_name} is permitted but not implemented in engine.")
            continue
            
        func = getattr(engine, func_name)
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        has_context = len(params) > 0
        
        # If there are no signatures (args) defined, run once with empty args
        if not signatures:
            signatures = [{}]
            
        for args in signatures:
            call_kwargs = {}
            if "rubrics" in sig.parameters:
                call_kwargs["rubrics"] = rubrics
                
            # Normalize arguments
            normalized_args = {}
            for k, v in args.items():
                if k == "pos":
                    normalized_args["position"] = v
                elif k == "num":
                    normalized_args["num"] = v
                else:
                    normalized_args[k] = v
                    
            for param_name in sig.parameters:
                if param_name in normalized_args:
                    call_kwargs[param_name] = normalized_args[param_name]
                    
            try:
                if has_context:
                    res = func(enriched, **call_kwargs)
                else:
                    res = func()
                    
                # Audit the returned intermediate object
                check_value_recursively(res, engine.text_db, errors, f"{func_name}(args={args})")
            except Exception as e:
                errors.append(f"Resolver {func_name}(args={args}) crashed: {str(e)}")
                
    return errors

def main():
    print("======================================================================")
    print("      DEVELOPING PROTO-PASS 3: RECURSIVE RESOLVER-LEVEL AUDIT         ")
    print("======================================================================")
    
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    
    print("Scanning database for logic resolver signatures...")
    resolver_calls = extract_resolver_calls_from_structures(str(PROJECT_ROOT))
    print(f"Extracted {len(resolver_calls)} distinct resolver functions from structures.")
    
    start_date = date(2026, 1, 1)
    end_date = date(2026, 1, 31)
    
    current_date = start_date
    total_days = 0
    passed_days = 0
    all_errors = {}
    
    print("\nAuditing January 2026 at the resolver level:")
    while current_date <= end_date:
        total_days += 1
        errors = run_recursive_resolver_audit(engine, current_date, resolver_calls)
        if errors:
            print(f"[-] {current_date.isoformat()} -> FAIL ({len(errors)} errors)")
            for err in errors[:5]:  # show first 5 errors
                print(f"    * {err}")
            if len(errors) > 5:
                print(f"    * ... and {len(errors) - 5} more errors")
            all_errors[current_date.isoformat()] = errors
        else:
            print(f"[+] {current_date.isoformat()} -> PASS")
            passed_days += 1
        current_date += timedelta(days=1)
        
    print("======================================================================")
    print("                         AUDIT SUMMARY                                ")
    print("======================================================================")
    print(f"Total January Days Audited: {total_days}")
    print(f"Passed January Days:        {passed_days}")
    print(f"Failed January Days:        {len(all_errors)}")
    
    if len(all_errors) > 0:
        print("\nCompliance Status: FAIL (Resolver level audit has errors)")
        sys.exit(1)
    else:
        print("\nCompliance Status: SUCCESS (All resolvers passed on all days!)")
        sys.exit(0)

if __name__ == "__main__":
    main()
