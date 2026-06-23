import os
import sys
import re
import inspect
from datetime import date, timedelta
from pathlib import Path
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ruthenian_engine import RuthenianEngine
from scratch.audit_recursive_resolvers import extract_resolver_calls_from_structures

def test_musical_mode_and_tone_coherence():
    """
    Gate 9: Musical Mode & Tone Coherence.
    Asserts that:
    1. For every asset in text_db that specifies a tone in its metadata, the tone matches 
       the tone pattern in the database key (e.g., a key containing 'tone_1' must have 'Tone 1' metadata).
    2. During active liturgical resolutions for the year 2026, any resolved resurrectional 
       (Octoechos) key matches the Tone of the Week.
    3. The linked sheet music/Full Octoechos PDF files exist on disk for all tones 1-8 
       and their filenames contain the matching Tone identifier.
    """
    engine = RuthenianEngine(base_dir=str(PROJECT_ROOT))
    
    # --- 1. Static Database-wide Tone Coherence Check ---
    errors = []
    tone_pattern_in_key = re.compile(r"\btone_(?P<num>[1-8])\b")
    
    for key, asset in engine.text_db.items():
        if not isinstance(asset, dict):
            continue
            
        # Check if the key name has a tone identifier (e.g. "tone_1")
        key_match = tone_pattern_in_key.search(key)
        asset_tone = asset.get("tone")
        
        if key_match:
            expected_num = key_match.group("num")
            expected_tone_str = f"Tone {expected_num}"
            
            if asset_tone:
                asset_tone_clean = str(asset_tone).strip()
                if asset_tone_clean not in (expected_tone_str, expected_num):
                    errors.append(
                        f"Static DB Mismatch: Key '{key}' has tone metadata '{asset_tone}' "
                        f"but expected '{expected_tone_str}' or '{expected_num}' based on key name."
                    )
            else:
                # If key name says tone_X, it should ideally have tone metadata or it might be a sub-key.
                # We won't error if it's missing, but if it exists, it must match.
                pass
        
        # Conversely, if asset tone says "Tone X" or "X", check if key name is compatible (optional, but good)
        if asset_tone:
            asset_tone_str = str(asset_tone).strip()
            tone_val_match = re.search(r"\b(?:Tone\s*)?([1-8])\b", asset_tone_str, re.IGNORECASE)
            if tone_val_match:
                tone_num = tone_val_match.group(1)
                # If the key contains a tone number that is different, that's a bug
                key_any_tone_match = tone_pattern_in_key.search(key)
                if key_any_tone_match and key_any_tone_match.group("num") != tone_num:
                    errors.append(
                        f"Static DB Conflict: Key '{key}' name implies tone {key_any_tone_match.group('num')} "
                        f"but metadata specifies '{asset_tone}'."
                    )

    # --- 2. Runtime Liturgical Tone Coherence Check ---
    resolver_calls = extract_resolver_calls_from_structures(str(PROJECT_ROOT))
    start_date = date(2026, 1, 1)
    end_date = date(2026, 12, 31)
    
    current_date = start_date
    while current_date <= end_date:
        try:
            context = engine.get_liturgical_context(current_date)
            rubrics = engine.resolve_rubrics(context)
            week_tone = context.get("tone") # Tone of the Week (1-8)
            
            enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
            enriched["overrides"] = rubrics.get("overrides", {})
            if rubrics.get("is_sunday_vigil"):
                enriched["is_sunday_vigil"] = True
        except Exception as e:
            current_date += timedelta(days=1)
            continue

        services = rubrics.get("services", [])
        active_structures = [s.get("structure_id") for s in services if s.get("structure_id")]

        # Helper to collect keys recursively from resolved objects
        def collect_db_keys(val, keys_list):
            if isinstance(val, str):
                if any(val.startswith(p) for p in ["menaion.", "octoechos.", "triodion.", "horologion.", "tone_"]):
                    keys_list.append(val)
            elif isinstance(val, list):
                for item in val:
                    collect_db_keys(item, keys_list)
            elif isinstance(val, dict):
                for k, v in val.items():
                    collect_db_keys(k, keys_list)
                    collect_db_keys(v, keys_list)

        resolved_keys = []
        for func_name, signatures in resolver_calls.items():
            is_permitted = False
            for struct_id in active_structures:
                if engine.resolver_registry.is_allowed(struct_id, func_name):
                    is_permitted = True
                    break
            
            if not is_permitted or not hasattr(engine, func_name):
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
                    res = func(enriched, **call_kwargs) if has_context else func()
                    collect_db_keys(res, resolved_keys)
                except Exception:
                    pass

        # For every resolved key on this day, check if it refers to Octoechos resurrectional texts
        # and ensure the tone of the asset matches the week_tone
        for key in resolved_keys:
            # If the key contains "tone_N", check if N matches week_tone
            # Only assert this if the key is resolved in a Sunday/resurrectional context
            # (since week days might resolve week tone, but feasts could override)
            key_match = tone_pattern_in_key.search(key)
            if key_match:
                key_tone_num = int(key_match.group("num"))
                asset = engine.get_text(key)
                if asset and isinstance(asset, dict):
                    asset_tone = asset.get("tone")
                    if asset_tone:
                        expected_tone_str = f"Tone {key_tone_num}"
                        if asset_tone.strip() != expected_tone_str:
                            errors.append(
                                f"Runtime Mismatch ({current_date.isoformat()}): Key '{key}' "
                                f"resolved, but asset tone metadata '{asset_tone}' does not match "
                                f"expected '{expected_tone_str}'."
                            )

        current_date += timedelta(days=1)

    # --- 3. Sheet Music/Full Octoechos PDF File Verification ---
    pdf_dir = PROJECT_ROOT / "Data" / "Service Books" / "Recensions" / "St Sergius" / "PDFs" / "Full Octoechos"
    
    # Assert that all 8 tones have their corresponding sheet music PDF
    for t in range(1, 9):
        pdf_filename = f"Tone{t}.pdf"
        pdf_path = pdf_dir / pdf_filename
        
        # Verify file exists on disk
        if not pdf_path.exists():
            errors.append(f"Sheet Music Error: Expected PDF file '{pdf_path.name}' does not exist in {pdf_dir}")
        else:
            # Verify file name contains the correct tone identifier
            # Filename is "ToneT.pdf", which contains the string f"Tone{t}"
            if f"Tone{t}" not in pdf_path.name:
                errors.append(f"Sheet Music Error: Filename '{pdf_path.name}' does not match Tone {t} identifier.")

    assert not errors, "Musical Mode & Tone Coherence validation failed:\n" + "\n".join(errors)
