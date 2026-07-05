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


    def __init__(self, base_dir=".", temple_feast_date=None, version="royal_doors", paschalion="gregorian", fixed_recension_path=None, variable_recension_path=None, external_assets_dir=None):
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
        
        self.version_map = {
            "stamford": "stamford_2014",
            "stamford_2014": "stamford_2014",
            "royal_doors": "royal_doors",
            "lviv": "lviv",
            "lviv_2010": "lviv",
            "st_sergius": "st_sergius"
        }
        self.folder_map = {
             "stamford_2014": "stamford",
             "royal_doors": "stamford",
             "lviv": "lviv",
             "st_sergius": "st_sergius"
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
        self.royal_doors_db = {}
        self.stamford_db = {}
        self.text_db = {} 
        
        # Set primary and backup database references
        if self.version_id == "royal_doors":
            self.primary_db = self.royal_doors_db
            self.backup_db = self.stamford_db
        elif self.version_id == "stamford_2014":
            self.primary_db = self.stamford_db
            self.backup_db = {}
        else:
            # Custom version selection (fallback to empty backup, direct loaded text_db primary)
            self.primary_db = self.text_db
            self.backup_db = self.stamford_db

        # 1. Load Royal Doors (Primary) Recension
        rd_dir = "Data/Service Books/Recensions/Royal Doors/JSON/assets"
        self._load_versioned_texts(f"{rd_dir}/text_horologion.json", target_db=self.royal_doors_db)
        self._load_versioned_texts(f"{rd_dir}/text_horologion_supplement.json", target_db=self.royal_doors_db)
        self._load_versioned_texts(f"{rd_dir}/text_menaion.json", target_db=self.royal_doors_db)
        self._load_versioned_texts(f"{rd_dir}/text_eothinon.json", target_db=self.royal_doors_db)
        self._load_versioned_texts(f"{rd_dir}/text_octoechos.json", target_db=self.royal_doors_db)
        self._load_versioned_texts(f"{rd_dir}/text_pentecostarion.json", target_db=self.royal_doors_db)
        self._load_versioned_texts(f"{rd_dir}/text_triodion.json", target_db=self.royal_doors_db)
        self._load_versioned_texts(f"{rd_dir}/text_weekdays.json", target_db=self.royal_doors_db)
        self._load_versioned_texts(f"{rd_dir}/text_theotokia.json", target_db=self.royal_doors_db)
        self._load_versioned_texts(f"{rd_dir}/text_liturgikon.json", target_db=self.royal_doors_db)
        
        # 2. Load Stamford (Backup) Recension
        stam_dir = "Data/Service Books/Recensions/Stamford Divine Office/JSON/assets"
        self._load_versioned_texts(f"{stam_dir}/text_horologion.json", target_db=self.stamford_db)
        self._load_versioned_texts(f"{stam_dir}/text_horologion_supplement.json", target_db=self.stamford_db)
        self._load_versioned_texts(f"{stam_dir}/text_menaion.json", target_db=self.stamford_db)
        self._load_versioned_texts(f"{stam_dir}/text_eothinon.json", target_db=self.stamford_db)
        self._load_versioned_texts(f"{stam_dir}/text_octoechos.json", target_db=self.stamford_db)
        self._load_versioned_texts(f"{stam_dir}/text_pentecostarion.json", target_db=self.stamford_db)
        self._load_versioned_texts(f"{stam_dir}/text_triodion.json", target_db=self.stamford_db)
        self._load_versioned_texts(f"{stam_dir}/text_weekdays.json", target_db=self.stamford_db)
        self._load_versioned_texts(f"{stam_dir}/text_theotokia.json", target_db=self.stamford_db)
        self._load_versioned_texts(f"{stam_dir}/text_liturgikon.json", target_db=self.stamford_db)

        # 3. Load other common/shared texts
        self._load_versioned_texts("json_db/text_pentecostarion_pascha.json")
        self._load_versioned_texts()
        
        # 4. Load General Menaion databases
        self.general_menaion_db = self._load_json("json_db/common/text_general_menaion.json")
        # Overlay Stamford General Menaion (backup)
        stam_common_path = os.path.abspath(os.path.join(self.base_dir, f"{stam_dir}/text_general_menaion.json"))
        if os.path.exists(stam_common_path):
            self.general_menaion_db.update(self._load_json(stam_common_path))
        # Overlay Royal Doors General Menaion (primary)
        rd_common_path = os.path.abspath(os.path.join(self.base_dir, f"{rd_dir}/text_general_menaion.json"))
        if os.path.exists(rd_common_path):
            self.general_menaion_db.update(self._load_json(rd_common_path))
        
        # Load External Assets (Fixed and Variable Recensions)
        if self.fixed_recension_path and os.path.exists(self.fixed_recension_path):
            self._load_external_assets(self.fixed_recension_path, "Fixed")
        if self.variable_recension_path and os.path.exists(self.variable_recension_path):
            self._load_external_assets(self.variable_recension_path, "Variable")
        elif self.external_assets_dir and os.path.exists(self.external_assets_dir):
            # Legacy single-path fallback
            self._load_external_assets(self.external_assets_dir, "Legacy")
            
        # Load Triodion Parsed Data
        self._load_versioned_texts("Data/Service Books/Recensions/Royal Doors/JSON/lenten_triodion.json", target_db=self.royal_doors_db)
        self._load_versioned_texts("Data/Service Books/Recensions/Royal Doors/JSON/floral_triodion.json", target_db=self.royal_doors_db)
        self._load_versioned_texts("Data/Service Books/Recensions/Stamford Divine Office/JSON/lenten_triodion.json", target_db=self.stamford_db)
        self._load_versioned_texts("Data/Service Books/Recensions/Stamford Divine Office/JSON/floral_triodion.json", target_db=self.stamford_db)
        # Primary Source: Dolnytsky Calendar Data (Fixed & Movable)
        # 'lviv' uses the 2010 Lviv Typikon calendar; others use the modern/reformed UGCC calendar
        calendar_file = "json_db/calendar_royal_doors.json" if self.version_id != "lviv" else "json_db/calendar_lviv.json"
        if not os.path.exists(os.path.join(self.base_dir, calendar_file)):
            calendar_file = "json_db/calendar_dolnytsky_split.json"

        self.dolnytsky_fixed = self._load_json(calendar_file)
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
            # Check for version-specific almanac first
            version_almanac = f"annual_almanac_{self.version_id}_{year}.json"
            almanac_path = os.path.join(self.json_db, "almanac", version_almanac)
            
            # Fallback for lviv to the default pre-computed almanac
            if not os.path.exists(almanac_path) and self.version_id == "lviv":
                almanac_path = os.path.join(self.json_db, "almanac", f"annual_almanac_{year}.json")
                
            if os.path.exists(almanac_path):
                try:
                    with open(almanac_path, "r", encoding="utf-8") as f:
                        self._almanacs[year] = json.load(f)
                    print(f"Engine: Loaded pre-computed almanac for year {year} ({os.path.basename(almanac_path)})")
                except Exception as e:
                    print(f"WARNING: Failed to load almanac {almanac_path}: {e}")
                    self._almanacs[year] = None
            else:
                self._almanacs[year] = None
        return self._almanacs[year]
