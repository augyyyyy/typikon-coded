"""
Ruthenian Engine - TextDBMixin
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

import json
import os
import re
from datetime import date, timedelta
import copy

LEGACY_KEY_ALIASES = {
    # Vespers
    "horologion.litany_great": "horologion.vespers.great_litany",
    "horologion.litany_fervent": "horologion.vespers.fervent_litany",
    "horologion.litany_supplication": "horologion.vespers.supplication_litany",
    "horologion.litany_small": "horologion.common.small_litany",
    "horologion.psalm_103": "horologion.vespers.psalm_103",
    "horologion.psalm_140": "horologion.vespers.psalm_140",
    "horologion.psalm_141": "horologion.vespers.psalm_141",
    "horologion.psalm_142": "horologion.matins.psalm_142",
    "horologion.psalm_129": "horologion.vespers.psalm_129",
    "horologion.psalm_116": "horologion.vespers.psalm_116",
    "horologion.o_gladsome_light_read": "horologion.vespers.phos_hilaron_read",
    "horologion.vouchsafe_o_lord": "horologion.vespers.vouchsafe_o_lord",
    "horologion.nunc_dimittis": "horologion.vespers.nunc_dimittis",
    "horologion.psalm_33": "horologion.vespers.psalm_33",
    "horologion.it_is_a_good_thing": "horologion.vespers.it_is_a_good_thing",

    # Matins
    "horologion.hexapsalmos": "horologion.matins.hexapsalmos",
    "horologion.six_psalms": "horologion.matins.six_psalms",
    "horologion.god_is_the_lord_verses": "horologion.matins.god_is_the_lord_verses",
    "horologion.polyeleos": "horologion.matins.polyeleos",
    "horologion.praises_psalms": "horologion.matins.praises_psalms",
    "horologion.doxology_great": "horologion.matins.great_doxology",
    "horologion.doxology_small_read": "horologion.matins.small_doxology_read",
    "horologion.invitatory_3x": "horologion.matins.invitatory_3x",
    "horologion.o_lord_open_lips": "horologion.matins.open_lips",
    "horologion.glory_to_god_highest": "horologion.matins.glory_to_god_highest",
    "horologion.glory_to_holy": "horologion.matins.glory_to_holy",
    "horologion.blessing_vigil": "horologion.matins.blessing_vigil",
    "horologion.vigil_bridge_blessing": "horologion.matins.vigil_bridge_blessing",

    # Compline
    "horologion.prayer_compline_spotless": "horologion.compline.prayer_spotless",
    "horologion.prayer_compline_grant_us": "horologion.compline.prayer_grant_us",
    "horologion.prayer_manasses": "horologion.compline.prayer_manasseh",
    "horologion.troparia_compline_day_passed": "horologion.compline.troparia_day_passed",
    "horologion.dismissal_great_compline_standard": "horologion.compline.dismissal_great_standard",
    "horologion.litany_final_compline": "horologion.compline.final_litany",
    "horologion.psalm_4": "horologion.compline.psalm_4",
    "horologion.psalm_6": "horologion.compline.psalm_6",
    "horologion.psalm_12": "horologion.compline.psalm_12",
    "horologion.psalm_24": "horologion.compline.psalm_24",
    "horologion.psalm_30": "horologion.compline.psalm_30",
    "horologion.psalm_90": "horologion.compline.psalm_90",

    # Hours
    "horologion.prayer_hour_1_christ_true_light": "horologion.hours.hour_1.prayer_christ_true_light",
    "horologion.prayer_the_first_hour": "horologion.hours.hour_1.ordinary_prayer",
    "horologion.verses_hour_1_order_my_steps": "horologion.hours.hour_1.verses_order_steps",
    "horologion.prayer_the_third_hour": "horologion.hours.hour_3.ordinary_prayer",
    "horologion.verses_hour_3_blessed_is_the_lord": "horologion.hours.hour_3.verses_blessed_is_lord",
    "horologion.prayer_hour_3_mardari": "horologion.hours.hour_3.prayer_mardari",
    "horologion.prayer_hour_6_god_and_lord_of_hosts": "horologion.hours.hour_6.prayer_lord_of_hosts",
    "horologion.prayer_the_sixth_hour": "horologion.hours.hour_6.ordinary_prayer",
    "horologion.verses_hour_6_compassions_quickly": "horologion.hours.hour_6.verses_compassions_quickly",
    "horologion.prayer_hour_9_master_lord": "horologion.hours.hour_9.prayer_master_lord",
    "horologion.prayer_the_ninth_hour": "horologion.hours.hour_9.ordinary_prayer",
    "horologion.verses_hour_9_forsake_not": "horologion.hours.hour_9.verses_forsake_not",
    "horologion.prayer_hours_thou_who": "horologion.hours.prayer_thou_who_at_all_times",

    # Common Ordinaries
    "horologion.creed": "horologion.common.creed",
    "horologion.axion_estin": "horologion.common.axion_estin",
    "horologion.blessed_be_name_3x": "horologion.common.blessed_be_name_3x",
    "horologion.lord_have_mercy_3x": "horologion.common.lord_have_mercy_3x",
    "horologion.lord_have_mercy_12": "horologion.common.lord_have_mercy_12",
    "horologion.lord_have_mercy_40": "horologion.common.lord_have_mercy_40",
    "horologion.remit_pardon": "horologion.common.remit_pardon",
    "horologion.blessing_common": "horologion.common.blessing",
    "horologion.our_father": "horologion.common.our_father",
    "horologion.trisagion_block": "horologion.common.trisagion_block",
}


def humanize_key(key):
    """
    Format a database key into a human-readable title for cantor / UI displays.
    """
    if not key:
        return ""
    if isinstance(key, dict):
        key = key.get("title") or key.get("source") or key.get("ref_key", "")
    key = str(key).strip()

    # Extract the relevant suffix
    parts = key.split(".")
    suffix = parts[-1]
    return suffix.replace("_", " ").title()


class TextDBMixin:

    """Mixin providing text db methods for RuthenianEngine."""


    def _load_json(self, path_to_json):
        try:
            if os.path.isabs(path_to_json):
                abs_path = path_to_json
            else:
                abs_path = os.path.abspath(os.path.join(self.base_dir, path_to_json))
                
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


    def _load_versioned_texts(self, specific_path=None, target_db=None):
        """
        Load texts from asset-based directory structure OR specific file.
        Recursively scans assets/stamford/ directory if no path provided.
        """
        if target_db is None:
            target_db = self.text_db

        if specific_path:
             # Direct load mode
             if os.path.isabs(specific_path):
                 abs_path = specific_path
             else:
                 abs_path = os.path.abspath(os.path.join(self.base_dir, specific_path))
                 
             if os.path.exists(abs_path):
                 try:
                     with open(abs_path, 'r', encoding='utf-8') as f:
                         data = json.load(f)
                         
                     if isinstance(data, dict):
                         target_db.update(data)
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
                        
                        target_db[asset_id] = asset_data
                        count += 1
                    except Exception as e:
                        print(f"Error loading {asset_path}: {e}")
        
        print(f"Engine: Loaded {count} assets from {assets_base}")





    def get_text(self, text_id, logic_requirement=None, context=None):
        """
        Public accessor for text_db.
        Implements hierarchical fallback:
          1. Selected Recension DB (e.g. st_sergius_db, lviv_db if present)
          2. Stamford base recension (self.text_db)
          3. General Menaion fallback (self.general_menaion_db)
          4. Humanized missing placeholder
        """
        item = None
        recension = context.get("recension") if context else None

        def db_get(db, key):
            if not db:
                return None
            val = db.get(key)
            if not val:
                for legacy, new_alias in LEGACY_KEY_ALIASES.items():
                    if new_alias == key:
                        val = db.get(legacy)
                        if val:
                            break
            if not val and key in LEGACY_KEY_ALIASES:
                val = db.get(LEGACY_KEY_ALIASES[key])
            return val

        language = context.get("language", "en") if context else "en"

        # Parse Year from Date
        year = None
        if context and "date" in context:
            dt = context["date"]
            if hasattr(dt, "year"):
                year = dt.year
            elif isinstance(dt, str) and len(dt) >= 4:
                try:
                    year = int(dt[:4])
                except Exception:
                    pass

        # Helper: Compile sequential indexed stichera or doxology suffixes
        def compile_sequential_text(db, base_id, source_name):
            indexed_items = []
            idx = 1
            while True:
                test_id = f"{base_id}_{idx}"
                cand = db_get(db, test_id)
                if not cand:
                    break
                indexed_items.append(copy.deepcopy(cand))
                idx += 1
            
            for suffix in ["_glory", "_both_now", "_glory_both_now"]:
                cand = db_get(db, f"{base_id}{suffix}")
                if cand:
                    indexed_items.append(copy.deepcopy(cand))
            
            if indexed_items:
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
                
                return {
                    "id": base_id,
                    "content": "\n\n".join(content_parts),
                    "_segments": segments,
                    "_verses": verses,
                    "source": source_name
                }
            return None

        # Helper: Look up key in specified recension database
        def lookup_recension(target_rec):
            # Enforce language boundaries to prevent language collision bug
            if language == "en" and target_rec in ["stamford_printed", "stamford_web_2026"]:
                return None
            if language == "uk" and target_rec in ["sheptytsky_printed", "royal_doors_web"]:
                return None

            db_attr = f"{target_rec}_db"
            if not hasattr(self, db_attr):
                return None
            db = getattr(self, db_attr)
            if not db:
                return None
            
            res = db_get(db, text_id)
            if res:
                return copy.deepcopy(res)
            
            # Suffix/Sequential compilation lookup
            src_name = target_rec.replace("_", " ").title()
            return compile_sequential_text(db, text_id, src_name)

        # 0. Recension Database Lookup
        if recension:
            # 0.1 Daily Office Translation Drift Lookup for royal_doors_web
            if recension == "royal_doors_web" and language == "en" and year and hasattr(self, "royal_doors_drift_db") and self.royal_doors_drift_db:
                dt = context.get("date")
                mm_dd = None
                if dt:
                    if hasattr(dt, "month") and hasattr(dt, "day"):
                        mm_dd = f"{dt.month:02d}_{dt.day:02d}"
                    elif isinstance(dt, str) and len(dt) >= 10:
                        parts = dt.split("-")
                        if len(parts) >= 3:
                            try:
                                mm_dd = f"{int(parts[1]):02d}_{int(parts[2]):02d}"
                            except Exception:
                                pass
                
                if mm_dd:
                    parts = text_id.split(".")
                    if len(parts) >= 3:
                        element_key = ".".join(parts[2:])
                        pairs = self.royal_doors_drift_db.get((mm_dd, element_key))
                        if pairs:
                            for pair in pairs:
                                if year in pair.get("years1", []):
                                    item = {
                                        "id": text_id,
                                        "content": pair.get("text1", ""),
                                        "source": f"Royal Doors Web Drift ({year})"
                                    }
                                    break
                                elif year in pair.get("years2", []):
                                    item = {
                                        "id": text_id,
                                        "content": pair.get("text2", ""),
                                        "source": f"Royal Doors Web Drift ({year})"
                                    }
                                    break

            # 0.2 Primary Recension Lookup
            if not item:
                item = lookup_recension(recension)

            # 0.3 Language-Safe Fallback Chain resolution
            if not item:
                if language == "en":
                    fallback_chain = {
                        "stamford_printed": ["sheptytsky_printed", "royal_doors_web"],
                        "stamford_web_2026": ["sheptytsky_printed", "royal_doors_web"],
                        "sheptytsky_printed": ["royal_doors_web"],
                        "royal_doors_web": []
                    }.get(recension, [])
                else:
                    fallback_chain = {
                        "sheptytsky_printed": ["stamford_printed", "stamford_web_2026"],
                        "royal_doors_web": ["stamford_printed", "stamford_web_2026"],
                        "stamford_printed": ["stamford_web_2026"],
                        "stamford_web_2026": []
                    }.get(recension, [])

                for fb_rec in fallback_chain:
                    item = lookup_recension(fb_rec)
                    if item:
                        warn_msg = f"WARNING: Key '{text_id}' missing in '{recension}' for language '{language}'. Falling back to '{fb_rec}'."
                        if hasattr(self, "log"):
                            self.log(warn_msg)
                        elif hasattr(self, "trace_log"):
                            self.trace_log.append(warn_msg)
                        else:
                            print(warn_msg)
                        break

            # 0.4 Special historical St. Sergius lookup (fallback compat)
            if not item and recension == "st_sergius" and hasattr(self, "st_sergius_db") and self.st_sergius_db:
                item = compile_sequential_text(self.st_sergius_db, text_id, "St. Sergius Unabridged (consolidated)")
        
        # 1. Primary selected recension lookup
        if not item and hasattr(self, "primary_db") and self.primary_db is not None:
            item = db_get(self.primary_db, text_id)

        # 1.1 Backup recension lookup (if different from primary)
        if not item and hasattr(self, "backup_db") and self.backup_db:
            item = db_get(self.backup_db, text_id)

        # 1.2 Legacy/direct text_db lookup
        if not item:
            item = db_get(self.text_db, text_id)

        # 1.5 Dynamic Variable Resolution
        if not item and context:
            resolved_val = self._resolve_variable_ref(text_id, context)
            if resolved_val:
                if isinstance(resolved_val, dict):
                    item = resolved_val
                elif isinstance(resolved_val, str) and resolved_val != text_id:
                    item = self.get_text(resolved_val, logic_requirement, context)

        if item:
            # Deep copy to avoid mutation
            item = copy.deepcopy(item)
            
            # 1.1 Content Processing
            if isinstance(item, dict) and "content" in item:
                raw_text = item["content"]
                if isinstance(raw_text, dict):
                    if "text" in raw_text:
                        inner = raw_text["text"]
                        if isinstance(inner, dict):
                            raw_text = inner.get("en") or next(iter(inner.values())) if inner else ""
                        else:
                            raw_text = str(inner)
                    else:
                        raw_text = raw_text.get("en") or next(iter(raw_text.values())) if raw_text else ""
                raw_text = str(raw_text)
                
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

        # 3. Missing Handler (Human-readable clean placeholder)
        humanized = text_id.split(".")[-1].replace("_", " ").title()
        req_str = f" | Required by: {logic_requirement}" if logic_requirement else ""
        rec_name = recension.replace("_", " ").title() if recension else "Stamford"
        return {
            "title": humanized,
            "content": f"[{humanized} (Missing in {rec_name}{req_str})]",
            "source": "System Logic",
            "is_missing": True
        }

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
                  
             # Look up root in primary_db, backup_db, or text_db
             root = None
             if text_key:
                 root = (self.primary_db.get(text_key) if hasattr(self, "primary_db") and self.primary_db is not None else None) or (self.backup_db.get(text_key) if hasattr(self, "backup_db") and self.backup_db else None) or self.text_db.get(text_key)
             
             if root:
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
             
             if target_key:
                  return self.get_text(target_key, context=context)

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
             if concrete_key:
                  return self.get_text(concrete_key, context=context)
        
        # Assets Map Fallback Check
        if hasattr(self, "assets_map") and self.assets_map:
            for domain, domain_data in self.assets_map.get("asset_domains", {}).items():
                domain_map = domain_data.get("map", {})
                if ref_key in domain_map:
                    mapped_path = domain_map[ref_key]
                    if domain == "menaion":
                        parts = mapped_path.split("/")
                        if len(parts) >= 3:
                            month = parts[0]
                            day = parts[1]
                            filename = parts[2].replace(".json", "")
                            section = "vespers" if filename in ("litiya", "stichera_vespers", "stichera_vespers_great", "aposticha") else "matins"
                            concrete_key = f"menaion.{month}{day}.{section}.{filename}"
                            exists = (hasattr(self, "primary_db") and self.primary_db is not None and concrete_key in self.primary_db) or (hasattr(self, "backup_db") and self.backup_db and concrete_key in self.backup_db) or concrete_key in self.text_db
                            if exists:
                                return self.get_text(concrete_key, context=context)
        
        return None


    def _load_menaion_files(self):
        if not os.path.exists(self.json_db): return
        
        # 1. Load common logic files
        files = sorted([f for f in os.listdir(self.json_db) if f.startswith("02b_") and "index" not in f])
        for f in files:
            data = self._load_json(os.path.join(self.json_db, f))
            if "month_settings" in data:
                self.menaion_logic[data["month_settings"]["month_id"]] = data["month_settings"]
                
        # 2. Load version-specific logic overrides (deep merge by month_id)
        version_id = getattr(self, "version_id", None)
        if version_id:
            version_dir = os.path.join(self.json_db, version_id)
            if os.path.exists(version_dir):
                version_files = sorted([f for f in os.listdir(version_dir) if f.startswith("02b_") and "index" not in f])
                for f in version_files:
                    data = self._load_json(os.path.join(version_dir, f))
                    if "month_settings" in data:
                        month_id = data["month_settings"]["month_id"]
                        if month_id in self.menaion_logic:
                            # Merge days
                            if "days" in data["month_settings"]:
                                if "days" not in self.menaion_logic[month_id]:
                                    self.menaion_logic[month_id]["days"] = {}
                                self.menaion_logic[month_id]["days"].update(data["month_settings"]["days"])
                            # Merge floating rules
                            if "floating_rules" in data["month_settings"]:
                                if "floating_rules" not in self.menaion_logic[month_id]:
                                    self.menaion_logic[month_id]["floating_rules"] = {}
                                self.menaion_logic[month_id]["floating_rules"].update(data["month_settings"]["floating_rules"])
                        else:
                            self.menaion_logic[month_id] = data["month_settings"]


class TextDB:
    """
    Convenience wrapper providing TextDB access using the Ruthenian Engine.
    """
    def __new__(cls, *args, **kwargs):
        from engine import RuthenianEngine
        return RuthenianEngine(*args, **kwargs)

