import os
import sys
import re
import json
import inspect
from datetime import date, timedelta
from pathlib import Path
import pytest
from jsonschema import validate, ValidationError

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ruthenian_engine import RuthenianEngine
from scratch.audit_recursive_resolvers import extract_resolver_calls_from_structures, check_value_recursively

# Load JSON schemas for validation
SCHEMAS_DIR = PROJECT_ROOT / "schemas" / "resolver_outputs"
with open(SCHEMAS_DIR / "vespers_stichera.schema.json", "r", encoding="utf-8") as f:
    VESPERS_STICHERA_SCHEMA = json.load(f)

with open(SCHEMAS_DIR / "canon_stack.schema.json", "r", encoding="utf-8") as f:
    CANON_STACK_SCHEMA = json.load(f)


def test_resolver_outputs_compliance():
    """
    Rigorously runs all logic resolvers across all 365 days of 2026,
    asserting output type schema safety, key resolution existence,
    and banning the 'fallback_default' Case ID.
    """
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    resolver_calls = extract_resolver_calls_from_structures(str(PROJECT_ROOT))
    assert len(resolver_calls) > 0, "No logic resolvers were extracted from service structures!"
    
    start_date = date(2026, 1, 1)
    end_date = date(2026, 12, 31)
    
    current_date = start_date
    total_days_checked = 0
    all_errors = {}
    
    while current_date <= end_date:
        total_days_checked += 1
        # Resolve date contexts
        try:
            context = engine.get_liturgical_context(current_date)
            rubrics = engine.resolve_rubrics(context)
            enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
            enriched["overrides"] = rubrics.get("overrides", {})
            if rubrics.get("is_sunday_vigil"):
                enriched["is_sunday_vigil"] = True
        except Exception as e:
            all_errors[current_date.isoformat()] = [f"Context generation crashed: {str(e)}"]
            current_date += timedelta(days=1)
            continue

        services = rubrics.get("services", [])
        active_structures = [s.get("structure_id") for s in services if s.get("structure_id")]
        day_errors = []

        for func_name, signatures in resolver_calls.items():
            # Check if this resolver is allowed for any active structure on this day
            is_permitted = False
            for struct_id in active_structures:
                if engine.resolver_registry.is_allowed(struct_id, func_name):
                    is_permitted = True
                    break
            
            if not is_permitted:
                continue
                
            if not hasattr(engine, func_name):
                day_errors.append(f"Resolver {func_name} is permitted but not implemented in engine.")
                continue
                
            func = getattr(engine, func_name)
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
                        
                    # 1. Ban fallback_default Case ID in returned results
                    if isinstance(res, dict):
                        case_id = res.get("case_id")
                        if case_id == "fallback_default":
                            day_errors.append(f"{func_name}(args={args}): Resolved to banned 'fallback_default' Case ID.")
                        
                        # 2. Validate against output schemas
                        if "vespers_stichera" in func_name or "vespers_stichera" in str(res.get("distribution")):
                            try:
                                validate(instance=res, schema=VESPERS_STICHERA_SCHEMA)
                            except ValidationError as ve:
                                day_errors.append(f"{func_name}(args={args}): Schema validation error: {ve.message}")
                                
                        elif "canon_stack" in func_name or ("total_count" in res and "distribution" in res and "qty" in str(res.get("distribution"))):
                            try:
                                validate(instance=res, schema=CANON_STACK_SCHEMA)
                            except ValidationError as ve:
                                day_errors.append(f"{func_name}(args={args}): Schema validation error: {ve.message}")

                    # 3. Recursively check database key resolutions and placeholders
                    check_value_recursively(res, engine.text_db, day_errors, f"{func_name}(args={args})")
                    
                except Exception as e:
                    day_errors.append(f"Resolver {func_name}(args={args}) crashed: {str(e)}")
                    
        if day_errors:
            all_errors[current_date.isoformat()] = day_errors
            
        current_date += timedelta(days=1)
        
    assert not all_errors, f"Resolver compliance errors detected:\n" + "\n".join(
        f"  - {dt}:\n" + "\n".join(f"    * {err}" for err in errs) for dt, errs in all_errors.items()
    )
    assert total_days_checked == 365, f"Expected to check 365 days, checked {total_days_checked}"
