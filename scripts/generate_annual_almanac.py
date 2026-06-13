#!/usr/bin/env python3
"""
Annual Almanac Generator - Layer 0 of Common/Annual Typikon Optimization
Generates a pre-computed almanac for a given year to speed up engine resolution.
"""

import os
import sys
import json
import argparse
import datetime
import copy

# Add root folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ruthenian_engine import RuthenianEngine

def parse_args():
    parser = argparse.ArgumentParser(description="Generate Annual Liturgical Almanac")
    parser.add_argument("--year", type=int, default=2026, help="Year to generate (e.g. 2026)")
    parser.add_argument("--output-dir", type=str, default="json_db/almanac", help="Output directory")
    return parser.parse_args()

def main():
    args = parse_args()
    year = args.year
    output_dir = args.output_dir
    output_file = os.path.join(output_dir, f"annual_almanac_{year}.json")

    # Clean existing file to force clean generation from live engine logic
    if os.path.exists(output_file):
        print(f"Almanac Gen: Removing existing almanac file {output_file} to ensure clean live generation...")
        try:
            os.remove(output_file)
        except Exception as e:
            print(f"WARNING: Could not remove existing file: {e}")

    print(f"Almanac Gen: Initializing engine for year {year}...")
    engine = RuthenianEngine()

    # Load Lviv Typikon Paradigm Numbers mapping
    map_path = os.path.join("json_db", "lviv_format_map.json")
    if not os.path.exists(map_path):
        print(f"Error: Lviv mapping not found at {map_path}")
        sys.exit(1)

    with open(map_path, "r", encoding="utf-8") as f:
        format_map = json.load(f)

    base_mappings = format_map["base_mappings"]

    days_db = {}
    pascha_date_str = ""

    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)
    delta_days = (end_date - start_date).days + 1

    print(f"Almanac Gen: Precomputing {delta_days} days...")

    for i in range(delta_days):
        current_date = start_date + datetime.timedelta(days=i)
        date_str = current_date.isoformat()

        # Get context (need to deepcopy to prevent cross-day mutation side effects)
        context = engine.get_liturgical_context(current_date)
        
        # Capture Pascha Date
        if context.get("pascha_offset") == 0:
            pascha_date_str = date_str

        # Resolve rubrics and general case
        rubrics = engine.resolve_rubrics(context)
        gc = engine.resolve_general_case(context)
        paradigm_id = gc.get("id") if gc else None

        # Resolve readings using fully enriched context
        enriched_context = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
        readings = engine.resolve_liturgy_readings(enriched_context, rubrics)

        # Calculate Lviv Typikon Paradigm Number
        lviv_paradigm_number = base_mappings.get(paradigm_id) if paradigm_id else None

        # Build day record by copying the base mutated context (preserving integer types for rank)
        day_record = copy.deepcopy(context)
        day_record["paradigm_id"] = paradigm_id
        day_record["lviv_paradigm_number"] = lviv_paradigm_number
        day_record["rubrics_title"] = rubrics.get("title", "")
        day_record["variables"] = rubrics.get("variables", {})
        day_record["overrides"] = rubrics.get("overrides", {})
        day_record["readings"] = readings

        days_db[date_str] = day_record

    # Create final almanac envelope
    almanac_envelope = {
        "file_metadata": {
            "year": year,
            "pascha_date": pascha_date_str,
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "engine_version": "1.2.0"
        },
        "days": days_db
    }

    # Write output
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"annual_almanac_{year}.json")
    print(f"Almanac Gen: Writing output to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(almanac_envelope, f, indent=2, ensure_ascii=False)

    print(f"Almanac Gen: Success! Generated almanac with {len(days_db)} days.")

if __name__ == "__main__":
    main()
