"""
Ruthenian Engine - TextDBMixin
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

import json
import os
import re
from datetime import date, timedelta
import copy


class TextDBMixin:

    """Mixin providing text db methods for RuthenianEngine."""


    def _load_json(self, path_to_json):
        try:
            abs_path = os.path.abspath(path_to_json)
            if not os.path.exists(abs_path):
                 return {}
            with open(abs_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"ERROR loading JSON {path_to_json}: {e}")
            return {}


    def _load_text_db(self, filename):
        # Look in the mapped content folder
        path = os.path.join(self.json_db, self.content_folder, filename)
        if not os.path.exists(path):
             return {}
        try:
            with open(path, 'r', encoding='utf-8') as f: return json.load(f)
        except Exception as e:
            print(f"ERROR loading {filename}: {e}")
            return {}


    def _load_external_assets(self, asset_path, label="External"):
        """
        Recursively loads all JSON files in the specified directory and merges them into text_db.
        This allows external assets (Fixed or Variable recensions) to override or supplement internal ones.
        
        Args:
            asset_path: Path to the directory containing JSON assets.
            label: A label for logging purposes (e.g., "Fixed", "Variable").
        """
        print(f"Engine: Scanning {label} Recension assets at [{asset_path}]...")
        count = 0
        for root, dirs, files in os.walk(asset_path):
            for file in files:
                if file.endswith(".json"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # If it's a bulk file (dict of ID -> Asset), update all
                            if isinstance(data, dict):
                                # Check if it's a single asset (has "id" and "content") or a collection
                                if "id" in data and "content" in data:
                                    self.text_db[data["id"]] = data
                                    count += 1
                                else:
                                    # Assume collection key->value
                                    self.text_db.update(data)
                                    count += len(data)
                    except Exception as e:
                        print(f"Error loading {label} asset {file}: {e}")
        print(f"Engine: Loaded {count} {label} Recension assets.")


    def _load_versioned_texts(self, specific_path=None):
        """
        Load texts from asset-based directory structure OR specific file.
        Recursively scans assets/stamford/ directory if no path provided.
        """
        if specific_path:
             # Direct load mode
             abs_path = os.path.abspath(specific_path)
             if os.path.exists(abs_path):
                 try:
                     with open(abs_path, 'r', encoding='utf-8') as f:
                         data = json.load(f)
                         
                     if isinstance(data, dict):
                         self.text_db.update(data)
                         # print(f"Engine: Loaded {len(data)} items from {specific_path}")
                 except Exception as e:
                     print(f"Engine: Error loading {specific_path}: {e}")
             else:
                 pass
                 # print(f"Warning: File not found {specific_path}")
             return

        # Load ID map first
        id_map_path = os.path.join(self.base_dir, "assets", self.content_folder, "_id_map.json")
        id_map = {}
        if os.path.exists(id_map_path):
            with open(id_map_path, 'r', encoding='utf-8') as f:
                id_map = json.load(f)
        
        # Scan assets directory
        assets_base = os.path.join(self.base_dir, "assets", self.content_folder)
        
        if not os.path.exists(assets_base):
            print(f"Warning: Assets directory not found: {assets_base}")
            return
        
        # Recursively load all JSON assets
        count = 0
        for root, dirs, files in os.walk(assets_base):
            for file in files:
                if file.endswith('.json') and file != '_id_map.json':
                    asset_path = os.path.join(root, file)
                    try:
                        with open(asset_path, 'r', encoding='utf-8') as f:
                            asset_data = json.load(f)
                        
                        # Get original ID from asset or from ID map
                        if isinstance(asset_data, dict) and '_original_id' in asset_data:
                            asset_id = asset_data['_original_id']
                        else:
                            # Fallback: use filename hash to lookup in ID map
                            file_hash = os.path.splitext(file)[0]
                            asset_id = id_map.get(file_hash, file_hash)
                        
                        self.text_db[asset_id] = asset_data
                        count += 1
                    except Exception as e:
                        print(f"Error loading {asset_path}: {e}")
        
        print(f"Engine: Loaded {count} assets from {assets_base}")





    def get_text(self, text_id, logic_requirement=None, context=None):
        """
        Public accessor for text_db.
        If logic_requirement is provided and text is missing, attempts fallback to General Menaion 
        before returning a structured MISSING asset.
        """
        item = None
        # 0. Recension Priority (e.g. St. Sergius Unabridged)
        if context and context.get("recension") == "st_sergius":
            # Attempt lookup in St. Sergius DB
            serge_item = self.st_sergius_db.get(text_id)
            if serge_item:
                item = copy.deepcopy(serge_item)
            else:
                # Check for indexed variants (e.g. key_1, key_2...)
                # and special suffixes (glory, both_now)
                indexed_items = []
                idx = 1
                while True:
                    test_id = f"{text_id}_{idx}"
                    cand = self.st_sergius_db.get(test_id)
                    if not cand: break
                    indexed_items.append(cand)
                    idx += 1
                
                # Special suffixes
                for suffix in ["_glory", "_both_now", "_glory_both_now"]:
                    cand = self.st_sergius_db.get(f"{text_id}{suffix}")
                    if cand:
                        indexed_items.append(cand)

                if indexed_items:
                    # Construct a virtual asset
                    content_parts = []
                    segments = []
                    verses = []
                    for it in indexed_items:
                        part = it.get("content", "")
                        if "verse" in it:
                            v = it['verse']
                            part = f"Verse: {v}\n{part}"
                            verses.append(v)
                        else:
                            verses.append(None)
                        content_parts.append(part)
                        segments.append(it.get("content", ""))
                    
                    item = {
                        "id": text_id,
                        "content": "\n\n".join(content_parts),
                        "_segments": segments,
                        "_verses": verses,
                        "source": "St. Sergius Unabridged (consolidated)"
                    }
        
        # 1. Primary Lookup (if not already found in st_sergius_db)
        if not item:
            item = self.text_db.get(text_id)

        if item:
            # Deep copy to avoid mutation
            item = copy.deepcopy(item)
            
            # 1.1 Content Processing
            if isinstance(item, dict) and "content" in item:
                raw_text = item["content"]
                
                # Sanitization: Strip instructions in () or ending in :
                # e.g. "(Spec. Mel.: ...):" -> moved to metadata
                rubric_matches = re.findall(r'\((.*?)\):?', raw_text)
                if rubric_matches:
                    item["_rubrics"] = item.get("_rubrics", []) + rubric_matches
                    # Remove from spoken text
                    clean_content = re.sub(r'\(.*?\):?', '', raw_text).strip()
                else:
                    clean_content = raw_text
                    
                # Musical Syntax: Handle * and **
                # Store segments for musical phrasing
                item["_segments"] = [s.strip() for s in clean_content.split("*") if s.strip()]
                item["content"] = clean_content.replace("*", "").replace("  ", " ") # Spoken text
                
            return item
        
        # 2. General Menaion Fallback
        if context and "saint_class" in context and self.general_menaion_db:
            # Map standard key to generic key, e.g., "menaion.01_22.troparion" -> "general.apostle.troparion"
            # Helper to extract the suffix (e.g. 'troparion', 'kontakion', 'stichera_vespers')
            key_parts = text_id.split(".")
            suffix = key_parts[-1]
            if len(key_parts) > 2 and "stichera" in key_parts[-2]:
                 suffix = f"{key_parts[-2]}.{suffix}" # e.g. "stichera_vespers.lord_i_call"

            saint_classes = context.get("saint_class", "").split(",")
            for st_class in saint_classes:
                st_class = st_class.strip().lower()
                generic_id = f"general.{st_class}.{suffix}"
                
                fallback_item = self.general_menaion_db.get(generic_id)
                if fallback_item:
                    # Deep Copy to avoid mutating the master DB
                    rendered_item = copy.deepcopy(fallback_item)
                    
                    # Template Rendering
                    st_name = context.get("st_name", "Saint")
                    if "content" in rendered_item and isinstance(rendered_item["content"], str):
                        rendered_item["content"] = rendered_item["content"].replace("{{name}}", st_name)
                    
                    # Add Metadata about Fallback source
                    rendered_item["_source"] = f"General Menaion ({st_class})"
                    return rendered_item

        # 3. Missing Handler
        if logic_requirement:
            return {
                "title": "Missing Component",
                "content": f"[MISSING_COMPONENT: {text_id} | REQUIRED_BY: {logic_requirement}]",
                "source": "System Logic",
                "is_missing": True
            }
        
        return None

    # --- Phase 8: Advanced Collision Logic (Double Feasts) ---


    def _find_fuzzy_key(self, container, prefix):
        """Helper to find a key in container starting with prefix."""
        if not isinstance(container, dict):
            return None
        for k in container.keys():
            if k.startswith(prefix):
                return k
        return None


    def _resolve_variable_ref(self, ref_key, context):
        """
        Resolves a dynamic reference like 'stichera_resurrection' to a concrete key 
        like 'tone_1.sat_vespers.stichera_lord_i_call' based on context.
        """
        tone = context.get('tone', 1)
        
        # Mapping table for abstract variable_refs -> concrete DB keys
        mapping = {
            "stichera_resurrection": f"tone_{tone}.sat_vespers.stichera_lord_i_call",
            "aposticha_resurrection": f"tone_{tone}.sat_vespers.stichera_aposticha",
            "troparion_resurrection": f"tone_{tone}.sat_vespers.troparia",
            "sessional_resurrection_1": f"tone_{tone}.sun_matins.sessionals",
            "stichera_praises": f"tone_{tone}.sun_matins.stichera_praises",
        }
        
        # Eothinon mapping
        eothinon_id = context.get('eothinon_gospel', 1)
        mapping.update({
            "eothinon_gospel": f"eothinon_{eothinon_id}_gospel",
            "eothinon_hymn": f"eothinon_{eothinon_id}_stichera", 
            "exapostilarion_resurrection": f"eothinon_{eothinon_id}_exapostilarion",
        })

        # Triodion Mapping
        triodion_key = context.get('triodion_day_key') 
        if triodion_key:
             # Look up the text_key from logic
             logic_entry = self.triodion_logic.get('logic_map', {}).get(triodion_key, {})
             # Try top-level then variables
             text_key = logic_entry.get('text_key')
             if not text_key:
                  text_key = logic_entry.get('variables', {}).get('text_key')
                  
             if text_key and text_key in self.text_db:
                  root = self.text_db[text_key]
                  
                  # Resolver Helper
                  def get_triodion_content(service_prefix, section_prefix):
                      service_key = self._find_fuzzy_key(root, service_prefix)
                      if service_key:
                          section_key = self._find_fuzzy_key(root[service_key], section_prefix)
                          if section_key:
                              return root[service_key][section_key]
                      return None

                  # Map Dynamic Keys
                  result = None
                  if ref_key == "stichera_triodion":
                      result = get_triodion_content("saturday_vespers", "stichera_at_o_lord")
                  elif ref_key == "aposticha_triodion":
                      result = get_triodion_content("saturday_vespers", "aposticha")
                  elif ref_key == "canon_triodion":
                      result = get_triodion_content("sunday_matins", "ode_9")
                  elif ref_key == "exapostilarion_triodion":
                      result = get_triodion_content("sunday_matins", "exapostilarion")
                  elif ref_key == "stichera_praises_triodion":
                      result = get_triodion_content("sunday_matins", "stichera_at_the_praises")
                  elif ref_key == "sessional_triodion":
                       # Try Matins Sessional
                       result = get_triodion_content("sunday_matins", "sessional")

                  if result is not None:
                      if isinstance(result, list):
                          return {"content": "\n\n".join(result), "title": "Triodion Prop"}
                      return result

        # Menaion Mapping (Flattened Keys)
        menaion_key = context.get('menaion_key')
        if menaion_key:
             target_key = None
             if ref_key == "stichera_menaion":
                  target_key = f"{menaion_key}.vespers.stichera_lord_i_call"
             elif ref_key == "aposticha_menaion":
                  target_key = f"{menaion_key}.vespers.aposticha"
             elif ref_key == "litiya_menaion":
                  target_key = f"{menaion_key}.vespers.litiya"
             elif ref_key == "sessional_menaion":
                  target_key = f"{menaion_key}.matins.sessional"
             elif ref_key == "exapostilarion_menaion":
                  target_key = f"{menaion_key}.matins.exapostilarion"
             elif ref_key == "stichera_praises_menaion":
                  target_key = f"{menaion_key}.matins.stichera_praises"
             elif ref_key == "canon_menaion":
                  target_key = f"{menaion_key}.matins.canon"
             
             if target_key and target_key in self.text_db:
                  return self.text_db[target_key]

        # Pentecostarion Mapping
        pentecostarion_key = context.get('pentecostarion_day_key')
        if pentecostarion_key:
             mapping.update({
                  "stichera_pentecostarion": f"{pentecostarion_key}.sat_vespers.stichera_vespers",
                  "aposticha_pentecostarion": f"{pentecostarion_key}.sat_vespers.aposticha",
                  "canon_pentecostarion": f"{pentecostarion_key}.sun_matins.canon",
                  "exapostilarion_pentecostarion": f"{pentecostarion_key}.sun_matins.exapostilarion",
                  "stichera_praises_pentecostarion": f"{pentecostarion_key}.sun_matins.stichera_praises",
             })

        # Special Logic Keys
        if ref_key == "vespers_readings_logic":
             if context.get('pentecostarion_day_key') == 'thomas_sunday':
                  return {"title": "Readings", "content": "Prokimenon (Saturday). There are no readings."}

        if ref_key in mapping:
             concrete_key = mapping[ref_key]
             if concrete_key in self.text_db:
                  return self.text_db[concrete_key]
        
        return None


    def _load_menaion_files(self):
        if not os.path.exists(self.json_db): return
        files = sorted([f for f in os.listdir(self.json_db) if f.startswith("02b_") and "index" not in f])
        for f in files:
            data = self._load_json(os.path.join(self.json_db, f))
            if "month_settings" in data:
                self.menaion_logic[data["month_settings"]["month_id"]] = data["month_settings"]
