"""
Ruthenian Engine - EngineCore
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

import json
import os
import re
from datetime import date, timedelta
import copy
import functools

from typikon_digest_generator import TypikonDigestGenerator

def liturgical_source(ordo=None, dolnytsky=None, other=None):
    """
    Strict decorator to enforce explicit grounding of liturgical logic in primary sources.
    - ordo: Citation from Ordo Celebrationis (1996) for physical choreography.
    - dolnytsky: Citation from Dolnytsky Typikon (1899) for variable textual content.
    """
    def decorator(func):
        func.__liturgical_source__ = {
            "ordo": ordo,
            "dolnytsky": dolnytsky,
            "other": other
        }
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


class EngineCore:

    """Mixin providing core methods for RuthenianEngine."""


    def __init__(self, base_dir=".", temple_feast_date=None, version="stamford_2014", paschalion="gregorian", fixed_recension_path=None, variable_recension_path=None, external_assets_dir=None):
        self.base_dir = base_dir
        self.json_db = os.path.join(base_dir, "json_db")
        self.paschalion = paschalion # 'gregorian' or 'julian'
        print(f"Engine: Paschalion -> [{self.paschalion.upper()}]")
        
        # Recension Architecture (Dual-Path)
        self.fixed_recension_path = fixed_recension_path
        self.variable_recension_path = variable_recension_path
        
        # Legacy/Single-Path Backward Compatibility & External Boundary
        self.external_assets_dir = external_assets_dir if external_assets_dir else variable_recension_path

        if self.fixed_recension_path:
             print(f"Engine: Fixed Recension -> [{self.fixed_recension_path}]")
        if self.variable_recension_path:
             print(f"Engine: Variable Recension -> [{self.variable_recension_path}]")
        
        # Identifier Standardization
        self.version_map = {
            "stamford": "stamford_2014",
            "stamford_2014": "stamford_2014",
            "lviv_2018": "lviv_2018",
            "lviv": "lviv_2018",
            "st_sergius": "st_sergius",
            "other": "other_tradition_2025"
        }
        self.folder_map = {
             "stamford_2014": "stamford",
             "lviv_2018": "lviv",
             "st_sergius": "st_sergius",
             "other_tradition_2025": "other"
        }
        
        self.version_id = self.version_map.get(version, version)
        # Default internal folder if no external path provided
        self.content_folder = self.folder_map.get(self.version_id, "stamford")
        
        print(f"Engine Init: Logic=[{self.version_id}] | Internal Content=[json_db/{self.content_folder}]")

        self.temple_feast_date = temple_feast_date
        self.trace_log = []
        self._almanacs = {}
        
        # Instantiate resolver registry for logic safety
        from engine.resolver_registry import ResolverRegistry
        self.resolver_registry = ResolverRegistry(self.base_dir)

        self.assets_map = self._load_json("json_db/03_assets_map.json")
        _comp_data = self._load_json("json_db/00_components.json")
        self.components = _comp_data.get("components", {}) # Unwrapped
        for k, v in _comp_data.items():
            if k.startswith("components."):
                name = k.split("components.", 1)[1]
                if name not in self.components:
                    self.components[name] = v
        self.rank_taxonomy = _comp_data.get("system_definitions", {}).get("rank_taxonomy", {})
        self.scenario_registry = self._load_json("json_db/00_master_scenario_registry.json")
        self.triodion_logic = self._load_json("json_db/02c_logic_triodion.json")
        self.vespers_logic = self._load_json("json_db/04_logic_vespers.json")
        self.small_vespers_logic = self._load_json("json_db/04_logic_small_vespers.json")
        self.matins_logic = self._load_json("json_db/02e_logic_matins.json")
        self.temple_logic = self._load_json("json_db/02d_logic_temple.json")
        self.liturgy_logic = self._load_json("json_db/02f_logic_liturgy.json")
        self.ceremonial_logic = self._load_json("json_db/02g_logic_ceremonial.json")
        self.presanctified_logic = self._load_json("json_db/02g_logic_presanctified.json")
        self.hours_logic = self._load_json("json_db/02h_logic_hours.json")
        self.compline_logic = self._load_json("json_db/02i_logic_compline.json")
        self.hours_structures = {
            1: self._load_json("json_db/01a_struct_hour_1.json"),
            3: self._load_json("json_db/01b_struct_hour_3.json"),
            6: self._load_json("json_db/01c_struct_hour_6.json"),
            9: self._load_json("json_db/01d_struct_hour_9.json")
        }
        self.menaion_logic = {}
        self._load_menaion_files()
        self.midnight_logic = self._load_json("json_db/02j_logic_midnight.json")
        self.god_is_lord_logic = self._load_json("json_db/02c_logic_troparia_god_is_lord.json")
        self.general_cases = self._load_json("json_db/02a_logic_general.json")
        self.collision_db = self._load_json("json_db/02k_logic_collisions.json")
        
        # Load Text Databases (Multi-Layer Strategy)
        self.text_db = {} 
        # The original _load_versioned_texts() and _load_bulk_files() are replaced by the following explicit loads
        # Recension text assets (service book content specific to the tradition)
        # Define recension folder path (decoupled from json_db/)
        recension_dir = "Data/Service Books/Recensions/Stamford Divine Office/JSON/assets"
        self._load_versioned_texts(f"{recension_dir}/text_horologion.json")
        self._load_versioned_texts(f"{recension_dir}/text_horologion_supplement.json")
        self._load_versioned_texts(f"{recension_dir}/text_menaion.json")
        self._load_versioned_texts(f"{recension_dir}/text_eothinon.json")
        self._load_versioned_texts(f"{recension_dir}/text_octoechos.json")
        self._load_versioned_texts(f"{recension_dir}/text_pentecostarion.json")
        self._load_versioned_texts(f"{recension_dir}/text_triodion.json")
        self._load_versioned_texts(f"{recension_dir}/text_weekdays.json")
        self._load_versioned_texts(f"{recension_dir}/text_theotokia.json")
        self._load_versioned_texts("json_db/text_pentecostarion_pascha.json")
        self._load_versioned_texts()
        
        self.general_menaion_db = self._load_json("json_db/common/text_general_menaion.json")
        # Overlay recension-specific General Menaion if available
        recension_menaion_path = f"{recension_dir}/text_general_menaion.json"
        abs_common_path = os.path.abspath(os.path.join(self.base_dir, recension_menaion_path))
        if os.path.exists(abs_common_path):
            recension_common = self._load_json(abs_common_path)
            self.general_menaion_db.update(recension_common)
        
        # Load External Assets (Fixed and Variable Recensions)
        if self.fixed_recension_path and os.path.exists(self.fixed_recension_path):
            self._load_external_assets(self.fixed_recension_path, "Fixed")
        if self.variable_recension_path and os.path.exists(self.variable_recension_path):
            self._load_external_assets(self.variable_recension_path, "Variable")
        elif self.external_assets_dir and os.path.exists(self.external_assets_dir):
            # Legacy single-path fallback
            self._load_external_assets(self.external_assets_dir, "Legacy")
            
        # Load New Triodion Parsed Data
        self._load_versioned_texts("Data/Service Books/Recensions/Stamford Divine Office/JSON/lenten_triodion.json")
        self._load_versioned_texts("Data/Service Books/Recensions/Stamford Divine Office/JSON/floral_triodion.json")
        
        # Primary Source: Dolnytsky Calendar Data (Fixed & Movable)
        self.dolnytsky_fixed = self._load_json("json_db/calendar_dolnytsky_split.json")
        self.dolnytsky_movable = self._load_json("json_db/calendar_dolnytsky_movable.json")
        self.katavasia_seasons = self._load_json("json_db/katavasia_seasons.json")
        
        # Validation
        if not self.dolnytsky_fixed:
             print("WARNING: Failed to load 'calendar_dolnytsky.json'. Fixed calendar overrides disabled.")
        if not self.dolnytsky_movable:
             print("WARNING: Failed to load 'calendar_dolnytsky_movable.json'. Movable calendar overrides disabled.")
        if not self.katavasia_seasons:
             print("WARNING: Failed to load 'katavasia_seasons.json'. Katavasia lookup disabled.")
        
        # Load St. Sergius Unabridged Data (Refined)
        self.st_sergius_db = self._load_json("json_db/st_sergius/octoechos_tone_1_refined.json")
        # Extend to other tones if/when they exist
        
        # Define the Daily Cycle (Standard Sequence)
        self.daily_cycle = [
            {"name": "Vespers", "type_key": "vespers_type", "root": "daily_vespers", "file": "json_db/01h_struct_vespers.json"},
            {"name": "Compline", "type_key": "compline_type", "root": "small_compline", "file": "json_db/01f_struct_compline.json"},
            {"name": "Midnight Office", "type_key": "midnight_type", "root": "midnight_daily", "file": "json_db/01g_struct_midnight.json"},
            {"name": "Matins", "type_key": "matins_type", "root": "daily_matins", "file": "json_db/01i_struct_matins.json"},
            {"name": "First Hour", "type_key": "hours_type_1", "root": "structure_standard", "file": "json_db/01a_struct_hour_1.json"},
            {"name": "Third Hour", "type_key": "hours_type_3", "root": "structure_standard", "file": "json_db/01b_struct_hour_3.json"},
            {"name": "Sixth Hour", "type_key": "hours_type_6", "root": "structure_standard", "file": "json_db/01c_struct_hour_6.json"},
            {"name": "Ninth Hour", "type_key": "hours_type_9", "root": "structure_standard", "file": "json_db/01d_struct_hour_9.json"},
            {"name": "Liturgy", "type_key": "liturgy_type", "root": "liturgy_chrysostom", "file": "json_db/01j_struct_liturgy.json"}
        ]
        # ...


    def log(self, message):
        self.trace_log.append(message)


    def get_debug_report(self):
        return "\n".join(self.trace_log)


    def _get_almanac(self, year):
        if year not in self._almanacs:
            almanac_path = os.path.join(self.json_db, "almanac", f"annual_almanac_{year}.json")
            if os.path.exists(almanac_path):
                try:
                    with open(almanac_path, "r", encoding="utf-8") as f:
                        self._almanacs[year] = json.load(f)
                    print(f"Engine: Loaded pre-computed almanac for year {year}")
                except Exception as e:
                    print(f"WARNING: Failed to load almanac for year {year}: {e}")
                    self._almanacs[year] = None
            else:
                self._almanacs[year] = None
        return self._almanacs[year]
