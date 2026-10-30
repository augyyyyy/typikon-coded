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

EXTENDED_KEY_ALIASES = {
    "components.prothesis_rite": "liturgikon.prothesis_rite",
    "components.great_entrance_rite": "liturgikon.great_entrance_rite",
    "components.communion_rite": "liturgikon.communion_rite",
    "prothesis_rite": "liturgikon.prothesis_rite",
    "great_entrance_rite": "liturgikon.great_entrance_rite",
    "communion_rite": "liturgikon.communion_rite",
    "typical_psalms": "liturgikon.antiphons.typical_psalms",
    "weekday_antiphons": "liturgikon.antiphons.weekday_antiphons",
    "festal_antiphons": "liturgikon.antiphons.festal_antiphons",
    "horologion.only_begotten": "horologion.common.only_begotten",
    "only_begotten": "horologion.common.only_begotten",
    "trisagion_standard": "liturgikon.trisagion_standard",
    "horologion.trisagion": "liturgikon.trisagion_standard",
    "as_many_as_baptized": "liturgikon.as_many_as_baptized",
    "as_many_baptized": "liturgikon.as_many_as_baptized",
    "before_thy_cross": "liturgikon.before_thy_cross",
    "cherubic_hymn_standard": "liturgikon.cherubic_hymn_standard",
    "cherubic_hymn_holy_thursday": "liturgikon.cherubic_hymn_holy_thursday",
    "cherubic_hymn_holy_saturday": "liturgikon.cherubic_hymn_holy_saturday",
    "cherubic_hymn_presanctified": "liturgikon.cherubic_hymn_presanctified",
    "anaphora_chrysostom": "liturgikon.anaphora_chrysostom",
    "anaphora_basil": "liturgikon.anaphora_basil",
    "ambo_prayer": "liturgikon.ambo_prayer",
    "blessing_kingdom": "liturgikon.blessing_kingdom",
    "litanies_catechumens": "liturgikon.litanies_catechumens",
    "in_thee_rejoiceth": "liturgikon.in_thee_rejoiceth",
    "horologion.in_thee_rejoiceth": "liturgikon.in_thee_rejoiceth",
    "paschal_zadostoinyk": "liturgikon.paschal_zadostoinyk",
    "we_have_seen_true_light": "liturgikon.we_have_seen_true_light",
    "horologion.psalm_50": "horologion.matins.psalm_50",
    "horologion.magnificat": "horologion.matins.magnificat",
    "horologion.dismissal_full": "horologion.common.dismissal_full",
    "horologion.dismissal_great": "horologion.common.dismissal_great",
    "horologion.dismissal_small": "horologion.common.dismissal_small",
    "triodion.presanctified.opening": "liturgikon.blessing_kingdom",
    "triodion.let_my_prayer_arise": "liturgikon.let_my_prayer_arise",
    "triodion.now_the_powers": "liturgikon.cherubic_hymn_presanctified",
    "triodion.communion_presanctified": "liturgikon.communion.presanctified",
    "triodion.dismissal_presanctified": "liturgikon.dismissal_presanctified",
    "liturgikon.litanies_catechumens_presanctified": "liturgikon.litanies_catechumens",
    "horologion.litany_before_communion": "liturgikon.litany_before_communion",
}

ATOMIC_CORPUS_HUB_ALIASES = {
    "horologion.common.creed": "ORD.PRIM.CREED",
    "horologion.common.axion_estin": "ORD.PRIM.MORE_HONORABLE",
    "horologion.common.our_father": "ORD.PRIM.OUR_FATHER",
    "horologion.common.lord_have_mercy_3x": "ORD.PRIM.KYRIES_THREEFOLD",
    "horologion.common.lord_have_mercy_12": "ORD.PRIM.KYRIES_TWELVEFOLD",
    "horologion.common.blessing": "ORD.PRIM.INITIAL_BLESSING",
    "horologion.common.trisagion_block": "ORD.PRIM.TRISAGION",
    "horologion.matins.blessing_vigil": "HOR.PRIM.CONSUBSTANTIAL_BLESSING",
    "horologion.matins.glory_to_holy": "HOR.PRIM.CONSUBSTANTIAL_BLESSING",
    "horologion.glory_to_holy": "HOR.PRIM.CONSUBSTANTIAL_BLESSING",
    "horologion.matins.great_doxology": "HOR.PRIM.GREAT_DOXOLOGY",
    "horologion.matins.small_doxology_read": "ORD.PRIM.SMALL_DOXOLOGY",
    "horologion.matins.hexapsalmos": "HOR.PRIM.HEXAPSALMOS",
    "horologion.matins.six_psalms": "HOR.PRIM.HEXAPSALMOS",
    "horologion.matins.praises_psalms": "HOR.PRIM.PRAISES_PSALMS",
    "horologion.matins.invitatory_3x": "HOR.COMMON.INVITATORY_3X",
    "horologion.vespers.nunc_dimittis": "HOR.VESP.NUNC_DIMITTIS",
    "horologion.vespers.phos_hilaron_read": "HOR.VESP.PHOS_HILARON",
    "horologion.vespers.vouchsafe_o_lord": "HOR.VESP.VOUCHSAFE_O_LORD",
    "horologion.vespers.psalm_33": "HOR.VESP.PSALM_33",
    "horologion.dismissal_full": "ORD.PRIM.DAILY_MAJOR_DISMISSAL",
    "horologion.dismissal_great": "ORD.PRIM.DAILY_MAJOR_DISMISSAL",
    "horologion.dismissal_small": "ORD.PRIM.MINOR_DISMISSAL",
    "horologion.common.dismissal_full": "ORD.PRIM.DAILY_MAJOR_DISMISSAL",
    "horologion.common.dismissal_great": "ORD.PRIM.DAILY_MAJOR_DISMISSAL",
    "horologion.common.dismissal_small": "ORD.PRIM.MINOR_DISMISSAL",
    "horologion.only_begotten": "LIT.PRIM.O_MONOGENES",
    "horologion.common.only_begotten": "LIT.PRIM.O_MONOGENES",
    "only_begotten": "LIT.PRIM.O_MONOGENES",
    "horologion.protection_christians": "ORD.PRIM.STEADFAST_PROTECTRESS",
    "liturgikon.ambo_prayer": "LIT.PRIM.AMBO_PRAYER",
    "liturgikon.blessing_kingdom": "LIT.PRIM.KINGDOM_BLESSING",
    "liturgikon.litanies_catechumens": "LIT.PRIM.LITANY_OF_CATECHUMENS",
    "triodion.presanctified.opening": "LIT.PRIM.KINGDOM_BLESSING",
    "liturgikon.litanies_catechumens_presanctified": "LIT.PRIM.LITANY_OF_CATECHUMENS",
    "triodion.now_the_powers": "PROP.TRIOD.CHERUBIC_PRESANCTIFIED",
    "liturgikon.cherubic_hymn_presanctified": "PROP.TRIOD.CHERUBIC_PRESANCTIFIED",
    "cherubic_hymn_presanctified": "PROP.TRIOD.CHERUBIC_PRESANCTIFIED",
    "menaion.0908.troparion": "MEN.0908.TROPARION.APOLYTIKION",
    "menaion.09_08.troparion": "MEN.0908.TROPARION.APOLYTIKION",
    "menaion.0908.liturgy.troparion": "MEN.0908.TROPARION.APOLYTIKION",
    "octoechos.dogmatikon_tone_2": "OCT.T2.SAT_VESP.LIC.DOGMATIKON",
    "tone_2.sat_vespers.dogmatikon": "OCT.T2.SAT_VESP.LIC.DOGMATIKON",
    "tone_2.sat_vespers.stichera_resurrection_1": "OCT.T2.SAT_VESP.LIC.STICHERON_1",
    "tone_3.sat_vespers.stichera_resurrection_1": "OCT.T3.SAT_VESP.LIC.STICHERON_1",
}

_JSON_FILE_CACHE = {}
_ASSETS_DIR_CACHE = {}
_ATOMIC_CORPUS_CACHE = {}

RECENSION_DISPLAY_LABELS = {
    "royal_doors": "Royal Doors",
    "royal_doors_web": "Royal Doors",
    "stamford_2014": "Stamford 2014",
    "stamford": "Stamford 2014",
    "st_sergius": "St. Sergius",
    "sheptytsky_2021": "Sheptytsky 2021",
    "sheptytsky_printed": "Sheptytsky 2021",
    "lviv": "Lviv",
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
    special_map = {
        "prayer_holy_trinity_all_creating": "Prayer to the Most Holy Trinity",
        "prayer_eustratius": "Prayer of St. Eustratius",
        "prayer_mardarius": "Prayer of St. Mardarius",
        "prayer_first": "First Prayer of the Midnight Office",
        "prayer_second": "Second Prayer of the Midnight Office",
        "fathers_seventh_council": "the Holy Fathers of the Seventh Ecumenical Council",
    }
    if suffix.lower() in special_map:
        return special_map[suffix.lower()]
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
            stat = os.stat(abs_path)
            cache_key = (abs_path, stat.st_mtime)
            if cache_key not in _JSON_FILE_CACHE:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    _JSON_FILE_CACHE[cache_key] = json.load(f)
            cached = _JSON_FILE_CACHE[cache_key]
            # Deep-copy small mutable logic files (< 256 KB); shallow-copy large asset dictionaries
            if stat.st_size < 262144:
                return copy.deepcopy(cached)
            return dict(cached) if isinstance(cached, dict) else list(cached)
        except Exception as e:
            print(f"ERROR loading JSON {path_to_json}: {e}")
            return {}


    def _load_text_db(self, filename):
        # Look in the mapped content folder
        path = os.path.join(self.json_db, self.content_folder, filename)
        if not os.path.exists(path):
             return {}
        return self._load_json(path)


    def _load_recension_book_shards(self, rec_dir, combined_db, ordinaries_db, propers_db, recension_key):
        """
        Loads modular per-book JSON shards from a recension assets directory (`rec_dir`).
        Preserves canonical load order first (so supplements overlay base files), then auto-discovers
        any additional `text_*.json` shards in the directory, classifying each shard into
        `ordinaries` (Horologion / Liturgikon) vs. `propers` (Octoechos / Menaion / Triodion / Pentecostarion).
        """
        abs_dir = os.path.abspath(os.path.join(self.base_dir, rec_dir))
        if not os.path.exists(abs_dir):
            return
        canonical_order = [
            "text_horologion.json",
            "text_horologion_supplement.json",
            "text_liturgikon.json",
            "text_menaion.json",
            "text_eothinon.json",
            "text_octoechos.json",
            "text_pentecostarion.json",
            "text_triodion.json",
            "text_lenten_triodion.json",
            "text_floral_triodion.json",
            "text_weekdays.json",
            "text_theotokia.json",
        ]
        existing_files = [
            f for f in sorted(os.listdir(abs_dir))
            if f.endswith(".json") and f != "text_general_menaion.json"
        ]
        ordered_files = [f for f in canonical_order if f in existing_files] + [
            f for f in existing_files if f not in canonical_order
        ]
        shard_registry = self.recension_book_shards.setdefault(recension_key, {})
        for fname in ordered_files:
            rel_path = f"{rec_dir}/{fname}"
            data = self._load_json(rel_path)
            if not isinstance(data, dict):
                continue
            combined_db.update(data)
            lower_name = fname.lower()
            is_ordinary = ("horologion" in lower_name) or ("liturgikon" in lower_name)
            domain = "ordinaries" if is_ordinary else "propers"
            if is_ordinary:
                ordinaries_db.update(data)
            else:
                propers_db.update(data)
            book_key = fname.replace("text_", "").replace(".json", "")
            shard_registry[book_key] = {
                "domain": domain,
                "file": fname,
                "count": len(data),
            }


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
             data = self._load_json(specific_path)
             if isinstance(data, dict):
                 target_db.update(data)
             return

        assets_base = os.path.abspath(os.path.join(self.base_dir, "assets", self.content_folder))
        if not os.path.exists(assets_base):
            print(f"Warning: Assets directory not found: {assets_base}")
            return

        if assets_base in _ASSETS_DIR_CACHE:
            cached_assets = _ASSETS_DIR_CACHE[assets_base]
            target_db.update(cached_assets)
            print(f"Engine: Loaded {len(cached_assets)} assets from {assets_base}")
            return

        # Load ID map first
        id_map_path = os.path.join(assets_base, "_id_map.json")
        id_map = {}
        if os.path.exists(id_map_path):
            with open(id_map_path, 'r', encoding='utf-8') as f:
                id_map = json.load(f)
        
        # Recursively load all JSON assets
        loaded_assets = {}
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
                        
                        loaded_assets[asset_id] = asset_data
                        count += 1
                    except Exception as e:
                        print(f"Error loading {asset_path}: {e}")
        _ASSETS_DIR_CACHE[assets_base] = loaded_assets
        target_db.update(loaded_assets)
        print(f"Engine: Loaded {count} assets from {assets_base}")


    def _load_atomic_corpus(self):
        """
        Loads the 4-Shard Unified Atomic Key-Value Liturgical Corpus
        (../Shared_Lexicon/atomic_corpus/master_liturgical_corpus.json)
        into self.atomic_corpus_db and self.atomic_corpus_aliases.
        """
        self.atomic_corpus_db = {}
        self.atomic_corpus_aliases = {}
        corpus_path = os.path.abspath(
            os.path.join(self.base_dir, "..", "Shared_Lexicon", "atomic_corpus", "master_liturgical_corpus.json")
        )
        if not os.path.exists(corpus_path):
            return
        try:
            stat = os.stat(corpus_path)
            cache_key = (corpus_path, stat.st_mtime)
            if cache_key in _ATOMIC_CORPUS_CACHE:
                cached_db, cached_aliases = _ATOMIC_CORPUS_CACHE[cache_key]
                self.atomic_corpus_db = dict(cached_db)
                self.atomic_corpus_aliases = dict(cached_aliases)
                return

            with open(corpus_path, "r", encoding="utf-8") as f:
                master_data = json.load(f)
            entries = master_data.get("entries", {})
            for sid, entry in entries.items():
                canon = entry.get("canonical_text", {})
                text_val = canon.get("text") if canon.get("text") is not None else (canon.get("gap_marker") or "")
                record = {
                    "id": sid,
                    "structural_id": sid,
                    "content": text_val,
                    "slavonic_incipit": entry.get("slavonic_incipit"),
                    "greek_incipit": entry.get("greek_incipit"),
                    "codex_domain": entry.get("codex_domain"),
                    "corpus_division": entry.get("corpus_division"),
                    "tone": entry.get("tone"),
                    "gap_marker": canon.get("gap_marker"),
                    "provenance": canon.get("provenance"),
                    "recension_witnesses": entry.get("recension_witnesses", {}),
                    "source": f"Shared Atomic Corpus ({entry.get('corpus_division', 'MASTER')})",
                }
                self.atomic_corpus_db[sid] = record
                rationale = entry.get("adjudication_rationale") or {}
                for alias in rationale.get("hub_key_aliases", []):
                    self.atomic_corpus_aliases[alias] = sid
            for hub_key, sid in ATOMIC_CORPUS_HUB_ALIASES.items():
                if sid in self.atomic_corpus_db:
                    self.atomic_corpus_aliases.setdefault(hub_key, sid)
            for legacy_key, new_key in LEGACY_KEY_ALIASES.items():
                if new_key in self.atomic_corpus_aliases:
                    self.atomic_corpus_aliases.setdefault(legacy_key, self.atomic_corpus_aliases[new_key])
            for ext_key, new_key in EXTENDED_KEY_ALIASES.items():
                if new_key in self.atomic_corpus_aliases:
                    self.atomic_corpus_aliases.setdefault(ext_key, self.atomic_corpus_aliases[new_key])
            for skip_alias in (
                "horologion.litany_great",
                "horologion.vespers.great_litany",
                "horologion.litany_fervent",
                "horologion.vespers.fervent_litany",
                "menaion.0914.troparion",
                "menaion.09_14.troparion",
                "menaion.0914.liturgy.troparion",
                "menaion.0914.vespers.troparion",
            ):
                self.atomic_corpus_aliases.pop(skip_alias, None)
            _ATOMIC_CORPUS_CACHE[cache_key] = (dict(self.atomic_corpus_db), dict(self.atomic_corpus_aliases))
        except Exception as e:
            print(f"Warning: Failed to load Shared Atomic Corpus at {corpus_path}: {e}")

    @staticmethod
    def _is_stub_record(val) -> bool:
        """Returns True if a text database entry contains an unhydrated '[STUB]' placeholder or '[GAP' marker."""
        if not val:
            return False
        if isinstance(val, dict):
            raw = val.get("content", val.get("text", ""))
            if isinstance(raw, dict):
                raw = raw.get("text", raw.get("en", ""))
            raw_str = str(raw)
        else:
            raw_str = str(val)
        return bool(re.search(r'(\[STUB\]|\bSTUB:|\[GAP_|\[UNPOPULATED)', raw_str, re.IGNORECASE))

    @staticmethod
    def _is_unpopulated_gap(val) -> bool:
        """Returns True only if a record is empty or an unpopulated '[GAP_...]' marker without text."""
        if not val:
            return True
        if isinstance(val, dict):
            raw = val.get("content", val.get("text", ""))
            if isinstance(raw, dict):
                raw = raw.get("text", raw.get("en", ""))
            raw_str = str(raw).strip()
        else:
            raw_str = str(val).strip()
        if not raw_str:
            return True
        return bool(re.search(r'(\[GAP_|\[UNPOPULATED)', raw_str, re.IGNORECASE))

    @staticmethod
    def _normalize_ugcc_text(text: str) -> str:
        """
        Normalizes raw text at the engine/output boundary to UGCC Royal Doors standards
        without mutating diplomatic witness JSON files on disk:
        - Strips '[STUB]' and 'STUB:' markers
        - Replaces 'prokimenon'/'prokimena' -> 'Prokeimenon'/'Prokeimena' (case-preserving)
        - Replaces 'anabathmoi' -> 'Gradual' (case-preserving)
        """
        if not text or not isinstance(text, str):
            return text
        text = re.sub(r'\[STUB\]\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\bSTUB:\s*', '', text, flags=re.IGNORECASE)

        def _repl_prok(m):
            word = m.group(0)
            suffix = "a" if word.lower().endswith("a") else "on"
            if word.isupper():
                return f"PROKEIMEN{suffix.upper()}"
            if word[0].isupper():
                return f"Prokeimen{suffix}"
            return f"prokeimen{suffix}"

        text = re.sub(r'\bprokimen(?:on|a)\b', _repl_prok, text, flags=re.IGNORECASE)

        def _repl_anab(m):
            word = m.group(0)
            if word.isupper():
                return "GRADUAL"
            if word[0].isupper():
                return "Gradual"
            return "gradual"

        text = re.sub(r'\banabathmoi\b', _repl_anab, text, flags=re.IGNORECASE)
        return text.strip() if text.startswith(" ") else text

    def _classify_key_domain(self, text_id: str) -> str:
        """
        Classifies a liturgical key into 'ordinaries' (Horologion / Liturgikon / Ordinarium)
        vs. 'propers' (Octoechos / Menaion / Triodion / Pentecostarion / General Menaion),
        consulting the loaded per-book domain shard dictionaries first.
        """
        if not text_id:
            return "propers"
        raw_tid = str(text_id).strip()
        tid = raw_tid
        if tid in LEGACY_KEY_ALIASES:
            tid = LEGACY_KEY_ALIASES[tid]
        if tid in EXTENDED_KEY_ALIASES:
            tid = EXTENDED_KEY_ALIASES[tid]

        ord_dbs = (
            getattr(self, "royal_doors_ordinaries_db", None),
            getattr(self, "stamford_ordinaries_db", None),
            getattr(self, "st_sergius_ordinaries_db", None),
            getattr(self, "sheptytsky_ordinaries_db", None),
        )
        prop_dbs = (
            getattr(self, "royal_doors_propers_db", None),
            getattr(self, "stamford_propers_db", None),
            getattr(self, "st_sergius_propers_db", None),
            getattr(self, "sheptytsky_propers_db", None),
        )
        in_ord = any(isinstance(d, dict) and (tid in d or raw_tid in d) for d in ord_dbs if d)
        in_prop = any(isinstance(d, dict) and (tid in d or raw_tid in d) for d in prop_dbs if d)
        if in_ord:
            return "ordinaries"
        if in_prop:
            return "propers"

        if tid.startswith(("horologion.", "liturgikon.", "ORD.", "HOR.", "LIT.", "components.")):
            return "ordinaries"
        return "propers"

    def _resolve_from_atomic_corpus(self, text_id: str, target_rec: str):
        """
        Resolves a differentiated recension witness from the 4-Shard Shared Atomic Corpus
        (`self.atomic_corpus_db`) if present and non-stubbed for `target_rec`.
        """
        if not hasattr(self, "atomic_corpus_db") or not self.atomic_corpus_db:
            return None
        canon_id = LEGACY_KEY_ALIASES.get(text_id, EXTENDED_KEY_ALIASES.get(text_id, text_id))
        sid = None
        is_direct_sid = False
        if text_id in self.atomic_corpus_db:
            sid = text_id
            is_direct_sid = True
        elif canon_id in self.atomic_corpus_db:
            sid = canon_id
            is_direct_sid = True
        elif hasattr(self, "atomic_corpus_aliases"):
            sid = self.atomic_corpus_aliases.get(text_id) or self.atomic_corpus_aliases.get(canon_id)
        if not sid:
            return None
        entry_rec = self.atomic_corpus_db.get(sid)
        if not entry_rec:
            return None

        witnesses = entry_rec.get("recension_witnesses") or {}
        norm_rec = (target_rec or "royal_doors").lower()
        is_explicit_hub_alias = (text_id in ATOMIC_CORPUS_HUB_ALIASES) or (canon_id in ATOMIC_CORPUS_HUB_ALIASES)

        if is_direct_sid or entry_rec.get("gap_marker") or norm_rec in ("royal_doors", "lviv", "atomic_corpus"):
            raw_text = entry_rec.get("content")
            if raw_text and (entry_rec.get("gap_marker") or not self._is_stub_record(raw_text)):
                out = copy.deepcopy(entry_rec)
                out["id"] = text_id
                out["content"] = raw_text
                out["recension_resolved"] = "royal_doors" if norm_rec not in ("lviv", "stamford_2014", "stamford") else ("lviv" if norm_rec == "lviv" else "stamford_2014")
                return out
            return None

        if norm_rec in ("stamford_2014", "stamford"):
            if is_explicit_hub_alias:
                raw_text = entry_rec.get("content")
                if raw_text and not self._is_stub_record(raw_text):
                    out = copy.deepcopy(entry_rec)
                    out["id"] = text_id
                    out["content"] = raw_text
                    out["recension_resolved"] = "stamford_2014"
                    return out
            for w_key in ("stamford_2014", "stamford_or_1988_source"):
                w_obj = witnesses.get(w_key)
                if isinstance(w_obj, dict) and w_obj.get("text") and not self._is_stub_record(w_obj.get("text")):
                    out = copy.deepcopy(entry_rec)
                    out["id"] = text_id
                    out["content"] = w_obj["text"]
                    w_src = w_obj.get("source") or "Stamford 2014"
                    out["source"] = w_src if "Shared Atomic Corpus" in w_src else f"{w_src} (Shared Atomic Corpus)"
                    out["recension_resolved"] = "stamford_2014"
                    return out
            return None

        if norm_rec == "st_sergius":
            w_obj = witnesses.get("st_sergius")
            if isinstance(w_obj, dict) and w_obj.get("text") and not self._is_stub_record(w_obj.get("text")):
                out = copy.deepcopy(entry_rec)
                out["id"] = text_id
                out["content"] = w_obj["text"]
                w_src = w_obj.get("source") or "St. Sergius"
                out["source"] = w_src if "Shared Atomic Corpus" in w_src else f"{w_src} (Shared Atomic Corpus)"
                out["recension_resolved"] = "st_sergius"
                return out
            return None

        if norm_rec in ("sheptytsky_2021", "sheptytsky", "sheptytsky_printed"):
            w_obj = witnesses.get("sheptytsky_2021")
            if isinstance(w_obj, dict) and w_obj.get("text") and not self._is_stub_record(w_obj.get("text")):
                out = copy.deepcopy(entry_rec)
                out["id"] = text_id
                out["content"] = w_obj["text"]
                out["source"] = w_obj.get("source") or "Sheptytsky Institute Academic Translation"
                out["recension_resolved"] = "sheptytsky_2021"
                return out
            return None

        return None

    def _expand_st_sergius_candidate_keys(self, text_id: str) -> list:
        """
        Maps standard engine keys (`tone_1.sat_vespers.stichera_resurrection`,
        `octoechos.tone_1.saturday_vespers.stichera_resurrection_1`,
        `menaion.09_08.vespers.stichera_lord_i_call`, etc.) to St. Sergius corpus key conventions.
        """
        cands = [text_id]
        canon = LEGACY_KEY_ALIASES.get(text_id, EXTENDED_KEY_ALIASES.get(text_id, text_id))
        if canon not in cands:
            cands.append(canon)

        # Tone mapping: support both 3-part and 4-part tone keys
        m_tone = re.match(
            r"^(?:octoechos\.)?tone_(\d+)\.(?:sunday\.)?([a-z0-9_]+)\.([a-z0-9_]+)$",
            text_id,
        )
        if m_tone:
            t_num, svc, slot = m_tone.groups()
            svc_map = {
                "sat_vespers": "vespers",
                "saturday_vespers": "vespers",
                "vespers": "vespers",
                "sun_matins": "matins",
                "sunday_matins": "matins",
                "matins": "matins",
                "liturgy": "liturgy",
            }
            s_norm = svc_map.get(svc, svc)

            # Check for numbered resurrection stichera (1..7)
            m_stich_num = re.match(r"^(?:stichera_resurrection|stichera_lord_i_call)_v?(\d+)$", slot)
            if m_stich_num:
                n = int(m_stich_num.group(1))
                if n <= 3:
                    cands.append(f"tone_{t_num}.sat_vespers_great.stichera_lord_i_call_{n}")
                elif n == 4:
                    cands.append(f"tone_{t_num}.sat_vespers_great.stichera_lord_i_call_anatolius")
                else:
                    cands.append(f"tone_{t_num}.sat_vespers_great.stichera_lord_i_call_anatolius_{n - 3}")

            slot_variants = [slot]
            if slot in ("stichera_resurrection", "stichera_lord_i_call"):
                slot_variants = ["stichera_lord_i_call_1", "stichera_lord_i_call", "stichera_resurrection"]
            elif slot in ("stichera_aposticha", "aposticha_resurrection", "aposticha"):
                slot_variants = ["stichera_aposticha_1", "aposticha", "stichera_aposticha"]
            elif slot in ("troparia", "troparion_resurrection", "troparion"):
                slot_variants = ["troparion_1", "troparion", "troparia"]
            elif slot in ("theotokion", "dogmatikon"):
                slot_variants = ["stichera_lord_i_call_dogmatic", "dogmatikon", "theotokion"]
            for sv in slot_variants:
                cands.append(f"tone_{t_num}.sat_vespers_great.{sv}")
                cands.append(f"octoechos.tone_{t_num}.{s_norm}.{sv}")
                cands.append(f"tone_{t_num}.{svc}.{sv}")

        # Menaion mapping: menaion.0908.* <-> menaion.09_08.*
        m_men = re.match(r"^menaion\.(\d{2})_?(\d{2})\.(.+)$", text_id)
        if m_men:
            mm, dd, rest = m_men.groups()
            cands.append(f"menaion.{mm}_{dd}.{rest}")
            cands.append(f"menaion.{mm}{dd}.{rest}")
            if rest in ("vespers.stichera_lord_i_call", "stichera_lord_i_call"):
                cands.append(f"menaion.{mm}_{dd}.sat_vespers_great.stichera_lord_i_call_1")
                cands.append(f"menaion.{mm}_{dd}.vespers.stichera_lord_i_call_1")
            if "." not in rest:
                cands.append(f"menaion.{mm}_{dd}.vespers.{rest}")
                cands.append(f"menaion.{mm}_{dd}.sat_vespers_great.{rest}_1")
                cands.append(f"menaion.{mm}_{dd}.liturgy.{rest}")
                cands.append(f"menaion.{mm}_{dd}.matins.{rest}")

        seen = set()
        dedup = []
        for k in cands:
            if k not in seen:
                seen.add(k)
                dedup.append(k)
        return dedup

    def _expand_symbolic_slot_key(self, text_id: str, context: dict) -> list:
        """
        Expands symbolic resolver slot keys (e.g., `troparion_resurrection`, `theotokion_resurrection`,
        `troparion_day_of_week`, `theotokion_daily`, `troparion_feast`, `kontakion_feast`)
        into concrete corpus keys using `context`.
        """
        if not context or not text_id:
            return []
        tone = context.get("tone") or 1
        dow = context.get("day_of_week")
        day_names = {0: "sunday", 1: "monday", 2: "tuesday", 3: "wednesday", 4: "thursday", 5: "friday", 6: "saturday"}
        day_name = day_names.get(dow, "monday")

        dt = context.get("date")
        mm_dd = None
        mmdd = None
        if dt:
            if hasattr(dt, "month") and hasattr(dt, "day"):
                mm_dd = f"{dt.month:02d}_{dt.day:02d}"
                mmdd = f"{dt.month:02d}{dt.day:02d}"
            elif isinstance(dt, str) and len(dt) >= 10:
                parts = dt.split("-")
                if len(parts) >= 3:
                    try:
                        mm_dd = f"{int(parts[1]):02d}_{int(parts[2]):02d}"
                        mmdd = f"{int(parts[1]):02d}{int(parts[2]):02d}"
                    except Exception:
                        pass

        expanded = []
        if text_id in ("troparion_resurrection", "resurrection_troparion"):
            expanded.extend([
                f"tone_{tone}.sat_vespers.troparia",
                f"octoechos.tone_{tone}.vespers.troparion",
                f"octoechos.troparion_tone_{tone}",
            ])
        elif text_id in (
            "theotokion_resurrection",
            "theotokion_dismissal_resurrection",
            "theotokion_sunday_by_tone",
            "theotokion_aposticha_sunday_in_tone_of_doxastikon",
            "theotokion_aposticha_sunday_in_tone_of_doxastikon_else_current_tone",
            "theotokion_after_doxastikon",
            "theotokion_horologion_or_octoechos",
        ):
            expanded.extend([
                f"theotokia.dismissal_sunday_tone_{tone}",
                f"tone_{tone}.sat_vespers.theotokion",
                f"octoechos.dogmatikon_tone_{tone}",
            ])
        elif text_id in ("theotokion_daily", "theotokion_weekday"):
            expanded.extend([
                f"theotokia.dismissal_weekday_{day_name}",
                f"tone_{tone}.sat_vespers.theotokion",
            ])
        elif text_id == "troparion_day_of_week":
            expanded.append(f"weekdays.{day_name}.troparion")
        elif text_id == "kontakion_day_of_week":
            expanded.append(f"weekdays.{day_name}.kontakion")
        elif text_id in ("troparion_feast", "trop_feast", "troparion_saint", "trop_saint", "troparion_saint_if_any", "troparion_forefeast", "trop_forefeast"):
            if mm_dd:
                expanded.extend([
                    f"menaion.{mm_dd}.troparion",
                    f"menaion.{mmdd}.troparion",
                    f"menaion.{mmdd}.liturgy.troparion",
                    f"menaion.{mm_dd}.vespers.troparion",
                ])
        elif text_id in ("kontakion_feast", "kont_feast", "kontakion_saint", "kont_saint", "kontakion_saint_if_any", "kontakion_forefeast", "kont_forefeast"):
            if mm_dd:
                expanded.extend([
                    f"menaion.{mm_dd}.kontakion",
                    f"menaion.{mmdd}.kontakion",
                    f"menaion.{mmdd}.liturgy.kontakion",
                    f"menaion.{mm_dd}.matins.kontakion",
                ])
        elif text_id in ("stichera_feast", "stichera_saint", "stichera_forefeast", "stichera_afterfeast"):
            if mm_dd:
                expanded.extend([
                    f"menaion.{mm_dd}.vespers.stichera_lord_i_call",
                    f"menaion.{mm_dd}.stichera_vespers",
                    f"menaion.{mmdd}.vespers.stichera_vespers",
                ])
        elif text_id in ("doxastikon_feast", "feast_doxastikon", "doxastikon_saint", "saint_doxastikon", "doxastikon_forefeast"):
            if mm_dd:
                expanded.extend([
                    f"menaion.{mm_dd}.vespers.stichera_lord_i_call_glory",
                    f"menaion.{mm_dd}.vespers.doxastikon",
                    f"menaion.{mmdd}.vespers.doxastikon",
                ])
        elif text_id in ("aposticha_feast", "aposticha_saint", "aposticha_forefeast", "aposticha_afterfeast"):
            if mm_dd:
                expanded.extend([
                    f"menaion.{mm_dd}.vespers.aposticha",
                    f"menaion.{mmdd}.vespers.aposticha",
                ])
        return expanded

    @staticmethod
    def _resolve_cantorial_directive(text_id: str, context: dict = None):
        """
        Distinguishes Psalter Kathisma references (`horologion.kathisma_1..20`, `kathisma_1..20`)
        and Biblical Lectionary pericope citations (`wisdom_3_1_9`, `isaiah_*`, `proverbs_*`, etc.)
        from true unpopulated hymn/prayer corpus gaps, returning a clean cantorial rubric directive.
        """
        if not text_id:
            return None
        tid = str(text_id).strip().lower()
        tail = tid.split(".")[-1]

        # 1. Psalter Kathisma Directives
        m_kath = re.match(r"^(?:horologion\.)?kathisma_(\d+)$", tid)
        if m_kath:
            k_num = int(m_kath.group(1))
            psalm_ranges = {
                1: "Psalms 1–8", 2: "Psalms 9–16", 3: "Psalms 17–23", 4: "Psalms 24–31",
                5: "Psalms 32–36", 6: "Psalms 37–45", 7: "Psalms 46–54", 8: "Psalms 55–63",
                9: "Psalms 64–69", 10: "Psalms 70–76", 11: "Psalms 77–84", 12: "Psalms 85–90",
                13: "Psalms 91–100", 14: "Psalms 101–104", 15: "Psalms 105–108", 16: "Psalms 109–117",
                17: "Psalm 118", 18: "Psalms 119–133 (Songs of Ascent)", 19: "Psalms 134–142", 20: "Psalms 143–150",
            }
            p_range = psalm_ranges.get(k_num, f"Kathisma {k_num}")
            return {
                "id": text_id,
                "title": f"Kathisma {k_num} ({p_range})",
                "rubric": f"Cantorial Directive — Psalter Kathisma {k_num} ({p_range})",
                "content": f"Read Kathisma {k_num} ({p_range}) from the Psalter (3 Stases with Small Litanies as prescribed by the Typikon).",
                "source": "Psalter Rubric Directive",
                "is_cantorial_directive": True,
                "is_missing": False,
            }
        if tail == "kathisma_psalm":
            return {
                "id": text_id,
                "title": "Appointed Kathisma of the Psalter",
                "rubric": "Cantorial Directive — Psalter Kathisma",
                "content": "Read the appointed Kathisma from the Psalter according to the day of the week and season.",
                "source": "Psalter Rubric Directive",
                "is_cantorial_directive": True,
                "is_missing": False,
            }

        # 2. Biblical Pericope / Prophetologion / Lectionary References
        biblical_books = {
            "genesis": "Genesis",
            "exodus": "Exodus",
            "leviticus": "Leviticus",
            "numbers": "Numbers",
            "deuteronomy": "Deuteronomy",
            "joshua": "Joshua",
            "judges": "Judges",
            "1_kings": "1 Kings (3 Kingdoms)",
            "2_kings": "2 Kings (4 Kingdoms)",
            "1_chronicles": "1 Chronicles",
            "2_chronicles": "2 Chronicles",
            "job": "Job",
            "proverbs": "Proverbs",
            "wisdom": "Wisdom of Solomon",
            "isaiah": "the Prophecy of Isaiah",
            "jeremiah": "the Prophecy of Jeremiah",
            "ezekiel": "the Prophecy of Ezekiel",
            "daniel": "the Prophecy of Daniel",
            "joel": "the Prophecy of Joel",
            "jonah": "the Prophecy of Jonah",
            "micah": "the Prophecy of Micah",
            "zephaniah": "the Prophecy of Zephaniah",
            "zechariah": "the Prophecy of Zechariah",
            "malachi": "the Prophecy of Malachi",
            "acts": "the Acts of the Apostles",
            "romans": "St. Paul's Epistle to the Romans",
            "1_corinthians": "St. Paul's First Epistle to the Corinthians",
            "2_corinthians": "St. Paul's Second Epistle to the Corinthians",
            "galatians": "St. Paul's Epistle to the Galatians",
            "ephesians": "St. Paul's Epistle to the Ephesians",
            "philippians": "St. Paul's Epistle to the Philippians",
            "colossians": "St. Paul's Epistle to the Colossians",
            "1_thessalonians": "St. Paul's First Epistle to the Thessalonians",
            "2_thessalonians": "St. Paul's Second Epistle to the Thessalonians",
            "1_timothy": "St. Paul's First Epistle to Timothy",
            "2_timothy": "St. Paul's Second Epistle to Timothy",
            "titus": "St. Paul's Epistle to Titus",
            "hebrews": "the Epistle to the Hebrews",
            "james": "the Universal Epistle of St. James",
            "1_peter": "the First Universal Epistle of St. Peter",
            "2_peter": "the Second Universal Epistle of St. Peter",
            "1_john": "the First Universal Epistle of St. John",
            "jude": "the Universal Epistle of St. Jude",
            "matthew": "the Holy Gospel according to St. Matthew",
            "mark": "the Holy Gospel according to St. Mark",
            "luke": "the Holy Gospel according to St. Luke",
            "john": "the Holy Gospel according to St. John",
        }
        for prefix, book_title in biblical_books.items():
            if tail == prefix or tail.startswith(f"{prefix}_"):
                rest = tail[len(prefix):].strip("_")
                nums = [p for p in rest.split("_") if p.isdigit()]
                if len(nums) == 3:
                    ref_cite = f" ({nums[0]}:{nums[1]}–{nums[2]})"
                elif len(nums) == 4:
                    ref_cite = f" ({nums[0]}:{nums[1]}–{nums[2]}:{nums[3]})"
                elif len(nums) == 2:
                    ref_cite = f" ({nums[0]}:{nums[1]})"
                elif len(nums) == 1:
                    ref_cite = f" {nums[0]}"
                elif rest:
                    ref_cite = f" ({rest.replace('_', ' ').title()})"
                else:
                    ref_cite = ""
                return {
                    "id": text_id,
                    "title": f"Reading from {book_title}{ref_cite}",
                    "rubric": f"Lectionary Directive — {book_title}{ref_cite}",
                    "content": f"Reading from {book_title}{ref_cite} from the Lectionary / Prophetologion.",
                    "source": "Lectionary Rubric Directive",
                    "is_cantorial_directive": True,
                    "is_missing": False,
                }

        # 3. Lenten Triodion / Prophetologion Lectionary Keys (e.g., triodion.genesis.week_1.day_3, menaion.*.readings_1)
        m_lenten_lec = re.match(
            r"^triodion\.(genesis|exodus|job|proverbs|isaiah|wisdom|ezekiel|jeremiah)\.week_(\d+)\.day_(\d+)$",
            tid,
        )
        if m_lenten_lec:
            b_key, wk, dy = m_lenten_lec.groups()
            book_title = biblical_books.get(b_key, b_key.title())
            day_names = {
                "0": "Sunday", "1": "Monday", "2": "Tuesday", "3": "Wednesday",
                "4": "Thursday", "5": "Friday", "6": "Saturday", "7": "Sunday",
            }
            day_label = day_names.get(dy, f"Day {dy}")
            ref_cite = f" (Week {wk} of Great Lent, {day_label})"
            return {
                "id": text_id,
                "title": f"Reading from {book_title}{ref_cite}",
                "rubric": f"Prophetologion Directive — {book_title}{ref_cite}",
                "content": f"Reading from {book_title}{ref_cite} from the Lenten Prophetologion.",
                "source": "Lectionary Rubric Directive",
                "is_cantorial_directive": True,
                "is_missing": False,
            }

        m_paremia = re.match(r"^(?:([a-z0-9_]+)_)?(?:readings|paremia)_(\d+)$", tail)
        if m_paremia:
            prefix_label, num_str = m_paremia.groups()
            ord_label = f"Paremia Reading {num_str}"
            if prefix_label:
                clean_prefix = prefix_label.replace("_", " ").title()
                ord_label = f"{clean_prefix} Readings {num_str} ({ord_label})"
            return {
                "id": text_id,
                "title": ord_label,
                "rubric": f"Lectionary Directive — {ord_label}",
                "content": f"Read {ord_label} appointed for the Feast/Saint from the Lectionary / Prophetologion.",
                "source": "Lectionary Rubric Directive",
                "is_cantorial_directive": True,
                "is_missing": False,
            }

        return None


    def get_text(self, text_id, logic_requirement=None, context=None):
        """
        Public accessor for text_db.
        Implements domain-aware recension resolution ('ordinaries' vs. 'propers') and deterministic fallback:
          0. Custom in-memory overlay (`context['custom_overlay']`)
          1. Selected Active Recension for domain (via Shared Atomic Corpus witness + modular recension DB)
          2. Deterministic Fallback Chain (unless `strict_corpus_mode` is True):
             Selected Recension -> Royal Doors -> Stamford 2014 -> General Menaion (for minor saints)
          3. Psalter / Biblical Lectionary Cantorial Directive handler
          4. Structured Unresolved Canonical Gap (`is_missing=True`, `canonical_gap_badge`)
        """
        item = None
        explicit_recension = context.get("recension") if context else None
        strict_mode = bool(
            (context and context.get("strict_corpus_mode"))
            or getattr(self, "strict_corpus_mode", False)
        )
        domain = self._classify_key_domain(text_id)

        # Determine active target recension for this key's domain (Ordinaries vs. Propers)
        if context and domain == "ordinaries" and context.get("ordinaries_recension"):
            active_rec = self.version_map.get(context["ordinaries_recension"], context["ordinaries_recension"])
        elif context and domain == "propers" and context.get("propers_recension"):
            active_rec = self.version_map.get(context["propers_recension"], context["propers_recension"])
        elif explicit_recension:
            # If split recensions are configured on the engine and context.recension is just the default version_id,
            # respect the engine's domain split
            ord_eng = getattr(self, "ordinaries_recension", getattr(self, "version_id", "royal_doors"))
            prop_eng = getattr(self, "propers_recension", getattr(self, "version_id", "royal_doors"))
            if ord_eng != prop_eng and explicit_recension == getattr(self, "version_id", None):
                active_rec = ord_eng if domain == "ordinaries" else prop_eng
            else:
                active_rec = self.version_map.get(explicit_recension, explicit_recension) if hasattr(self, "version_map") else explicit_recension
        else:
            if domain == "ordinaries":
                active_rec = getattr(self, "ordinaries_recension", getattr(self, "version_id", "royal_doors"))
            else:
                active_rec = getattr(self, "propers_recension", getattr(self, "version_id", "royal_doors"))

        def db_get(db, key):
            if not db:
                return None
            val = db.get(key)
            if not val and key in LEGACY_KEY_ALIASES:
                val = db.get(LEGACY_KEY_ALIASES[key])
            if not val and key in EXTENDED_KEY_ALIASES:
                val = db.get(EXTENDED_KEY_ALIASES[key])
            if not val:
                for legacy, new_alias in LEGACY_KEY_ALIASES.items():
                    if new_alias == key:
                        val = db.get(legacy)
                        if val:
                            break
            if not val:
                for ext_k, new_alias in EXTENDED_KEY_ALIASES.items():
                    if new_alias == key:
                        val = db.get(ext_k)
                        if val:
                            break
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
                    if isinstance(part, dict):
                        part = part.get("en") or part.get("text") or ""
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

        # Helper: Look up key in a specific recension tier (Atomic Corpus Witness + Modular Shards)
        def lookup_in_recension_tier(target_rec, candidate_key):
            # Enforce language boundaries to prevent language collision bug on legacy comparison DBs
            if language == "en" and target_rec in ["stamford_printed", "stamford_web_2026"]:
                return None
            if language == "uk" and target_rec in ["sheptytsky_printed", "royal_doors_web"]:
                return None

            # 1. Legacy web/printed comparison DBs (when explicitly requested)
            if target_rec in ("sheptytsky_printed", "stamford_printed", "royal_doors_web", "stamford_web_2026"):
                if target_rec == "royal_doors_web" and language == "en" and year and hasattr(self, "royal_doors_drift_db") and self.royal_doors_drift_db:
                    dt = context.get("date") if context else None
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
                        parts = candidate_key.split(".")
                        if len(parts) >= 3:
                            element_key = ".".join(parts[2:])
                            pairs = self.royal_doors_drift_db.get((mm_dd, element_key))
                            if pairs:
                                for pair in pairs:
                                    if year in pair.get("years1", []):
                                        return {
                                            "id": candidate_key,
                                            "content": pair.get("text1", ""),
                                            "source": f"Royal Doors Web Drift ({year})"
                                        }
                                    elif year in pair.get("years2", []):
                                        return {
                                            "id": candidate_key,
                                            "content": pair.get("text2", ""),
                                            "source": f"Royal Doors Web Drift ({year})"
                                        }
                db_attr = f"{target_rec}_db"
                db = getattr(self, db_attr, None)
                if db:
                    res = db_get(db, candidate_key)
                    if res and not self._is_stub_record(res):
                        return copy.deepcopy(res)
                    seq = compile_sequential_text(db, candidate_key, target_rec.replace("_", " ").title())
                    if seq:
                        return seq
                return None

            # 2. Primary Modular Recensions: royal_doors, stamford_2014, st_sergius, sheptytsky_2021, lviv
            if target_rec == "royal_doors":
                canon_k = LEGACY_KEY_ALIASES.get(candidate_key, EXTENDED_KEY_ALIASES.get(candidate_key, candidate_key))
                is_hub_alias = (candidate_key in ATOMIC_CORPUS_HUB_ALIASES) or (canon_k in ATOMIC_CORPUS_HUB_ALIASES) or (hasattr(self, "atomic_corpus_aliases") and (candidate_key in self.atomic_corpus_aliases or canon_k in self.atomic_corpus_aliases))
                rd_domain_db = getattr(self, f"royal_doors_{domain}_db", None)
                rd_direct = (db_get(self.royal_doors_db, candidate_key) if hasattr(self, "royal_doors_db") else None) or (db_get(rd_domain_db, candidate_key) if rd_domain_db else None)
                if rd_direct and not self._is_stub_record(rd_direct) and not is_hub_alias:
                    return copy.deepcopy(rd_direct)
                atom_res = self._resolve_from_atomic_corpus(candidate_key, "royal_doors")
                if atom_res:
                    return atom_res
                if rd_direct and not self._is_unpopulated_gap(rd_direct):
                    return copy.deepcopy(rd_direct)
                if hasattr(self, "royal_doors_db") and self.royal_doors_db:
                    seq = compile_sequential_text(self.royal_doors_db, candidate_key, "Royal Doors")
                    if seq:
                        return seq
                if rd_domain_db:
                    seq_dom = compile_sequential_text(rd_domain_db, candidate_key, "Royal Doors")
                    if seq_dom:
                        return seq_dom
                if hasattr(self, "royal_doors_web_db") and self.royal_doors_web_db and language == "en":
                    web_res = db_get(self.royal_doors_web_db, candidate_key)
                    if web_res and not self._is_unpopulated_gap(web_res):
                        return copy.deepcopy(web_res)
                return None

            if target_rec in ("stamford_2014", "stamford"):
                canon_k = LEGACY_KEY_ALIASES.get(candidate_key, EXTENDED_KEY_ALIASES.get(candidate_key, candidate_key))
                is_hub_alias = (candidate_key in ATOMIC_CORPUS_HUB_ALIASES) or (canon_k in ATOMIC_CORPUS_HUB_ALIASES) or (hasattr(self, "atomic_corpus_aliases") and (candidate_key in self.atomic_corpus_aliases or canon_k in self.atomic_corpus_aliases))
                st_domain_db = getattr(self, f"stamford_{domain}_db", None)
                st_direct = (db_get(self.stamford_db, candidate_key) if hasattr(self, "stamford_db") else None) or (db_get(st_domain_db, candidate_key) if st_domain_db else None)
                if st_direct and not self._is_stub_record(st_direct) and not is_hub_alias:
                    return copy.deepcopy(st_direct)
                atom_res = self._resolve_from_atomic_corpus(candidate_key, "stamford_2014")
                if atom_res:
                    return atom_res
                if st_direct and not self._is_unpopulated_gap(st_direct):
                    return copy.deepcopy(st_direct)
                if hasattr(self, "stamford_db") and self.stamford_db:
                    seq = compile_sequential_text(self.stamford_db, candidate_key, "Stamford 2014")
                    if seq:
                        return seq
                if st_domain_db:
                    seq_dom = compile_sequential_text(st_domain_db, candidate_key, "Stamford 2014")
                    if seq_dom:
                        return seq_dom
                if hasattr(self, "text_db") and self.text_db:
                    t_res = db_get(self.text_db, candidate_key)
                    if t_res and not self._is_unpopulated_gap(t_res):
                        return copy.deepcopy(t_res)
                    seq_t = compile_sequential_text(self.text_db, candidate_key, "Stamford 2014")
                    if seq_t:
                        return seq_t
                return None

            if target_rec == "st_sergius":
                if hasattr(self, "st_sergius_db") and self.st_sergius_db:
                    direct_ss = db_get(self.st_sergius_db, candidate_key)
                    if direct_ss and not self._is_unpopulated_gap(direct_ss):
                        return copy.deepcopy(direct_ss)
                ss_domain_db = getattr(self, f"st_sergius_{domain}_db", None)
                if ss_domain_db:
                    direct_dom = db_get(ss_domain_db, candidate_key)
                    if direct_dom and not self._is_unpopulated_gap(direct_dom):
                        return copy.deepcopy(direct_dom)
                atom_res = self._resolve_from_atomic_corpus(candidate_key, "st_sergius")
                if atom_res:
                    return atom_res
                if hasattr(self, "st_sergius_db") and self.st_sergius_db:
                    for ss_key in self._expand_st_sergius_candidate_keys(candidate_key):
                        cand = db_get(self.st_sergius_db, ss_key)
                        if cand and not self._is_unpopulated_gap(cand):
                            return copy.deepcopy(cand)
                        seq = compile_sequential_text(self.st_sergius_db, ss_key, "St. Sergius Unabridged")
                        if seq:
                            return seq
                return None

            if target_rec == "sheptytsky_2021":
                sh_domain_db = getattr(self, f"sheptytsky_{domain}_db", None)
                if sh_domain_db:
                    direct_sh = db_get(sh_domain_db, candidate_key)
                    if direct_sh and not self._is_unpopulated_gap(direct_sh):
                        return copy.deepcopy(direct_sh)
                atom_res = self._resolve_from_atomic_corpus(candidate_key, "sheptytsky_2021")
                if atom_res:
                    return atom_res
                if hasattr(self, "sheptytsky_printed_db") and self.sheptytsky_printed_db and language == "en":
                    sh_res = db_get(self.sheptytsky_printed_db, candidate_key)
                    if sh_res and not self._is_unpopulated_gap(sh_res):
                        return copy.deepcopy(sh_res)
                    m_men = re.match(r"^menaion\.(\d{2})_?(\d{2})\.(?:.*?\.)?([a-z0-9_]+)$", candidate_key)
                    if m_men:
                        mm, dd, elem = m_men.groups()
                        for sh_k in (
                            f"menaion.{mm}{dd}.liturgy.{elem}",
                            f"menaion.{mm}{dd}.vespers.{elem}",
                            f"menaion.{mm}{dd}.matins.{elem}",
                            f"menaion.{mm}{dd}.{elem}",
                        ):
                            sh_res = db_get(self.sheptytsky_printed_db, sh_k)
                            if sh_res and not self._is_unpopulated_gap(sh_res):
                                return copy.deepcopy(sh_res)
                return None

            if target_rec in ("lviv", "atomic_corpus"):
                if hasattr(self, "text_db") and self.text_db:
                    t_res = db_get(self.text_db, candidate_key)
                    if t_res and not self._is_unpopulated_gap(t_res):
                        return copy.deepcopy(t_res)
                atom_res = self._resolve_from_atomic_corpus(candidate_key, target_rec)
                if atom_res:
                    return atom_res
                return None

            # Generic custom `<target_rec>_db` attribute lookup
            db_attr = f"{target_rec}_db"
            db = getattr(self, db_attr, None)
            if db:
                res = db_get(db, candidate_key)
                if res and not self._is_unpopulated_gap(res):
                    return copy.deepcopy(res)
                return compile_sequential_text(db, candidate_key, target_rec.replace("_", " ").title())
            return None

        # -1. Explicit Custom In-Memory Overlay Lookup (Highest Priority)
        if context and not item:
            custom_overlay = context.get("custom_overlay") or context.get("overlay_db")
            if isinstance(custom_overlay, dict):
                cand = db_get(custom_overlay, text_id)
                if cand:
                    if isinstance(cand, str):
                        item = {"id": text_id, "content": cand, "source": "Custom Overlay"}
                    else:
                        item = copy.deepcopy(cand)
                if not item:
                    item = compile_sequential_text(custom_overlay, text_id, "Custom Overlay")

        # 0. Primary Active Recension Lookup (including symbolic key expansion if needed)
        candidate_keys = [text_id] + self._expand_symbolic_slot_key(text_id, context)
        resolved_recension = None

        if not item:
            for c_key in candidate_keys:
                item = lookup_in_recension_tier(active_rec, c_key)
                if item:
                    resolved_recension = active_rec
                    break

        # 1. Deterministic Fallback Chain (disabled when strict_corpus_mode is True)
        if not item and not strict_mode:
            if active_rec in ("stamford_printed", "stamford_web_2026", "sheptytsky_printed", "royal_doors_web"):
                if language == "en":
                    fallback_chain = {
                        "stamford_printed": ["sheptytsky_printed", "royal_doors_web"],
                        "stamford_web_2026": ["sheptytsky_printed", "royal_doors_web"],
                        "sheptytsky_printed": ["royal_doors_web"],
                        "royal_doors_web": []
                    }.get(active_rec, [])
                else:
                    fallback_chain = {
                        "sheptytsky_printed": ["stamford_printed", "stamford_web_2026"],
                        "royal_doors_web": ["stamford_printed", "stamford_web_2026"],
                        "stamford_printed": ["stamford_web_2026"],
                        "stamford_web_2026": []
                    }.get(active_rec, [])

                for fb_rec in fallback_chain:
                    for c_key in candidate_keys:
                        item = lookup_in_recension_tier(fb_rec, c_key)
                        if item:
                            resolved_recension = fb_rec
                            warn_msg = f"WARNING: Key '{text_id}' missing in '{active_rec}' for language '{language}'. Falling back to '{fb_rec}'."
                            if hasattr(self, "log"):
                                self.log(warn_msg)
                            elif hasattr(self, "trace_log"):
                                self.trace_log.append(warn_msg)
                            else:
                                print(warn_msg)
                            break
                    if item:
                        break

            # Standard Fallback Chain: Selected Recension -> Royal Doors -> Stamford 2014
            if not item:
                std_fallbacks = []
                for fb_cand in ("royal_doors", "stamford_2014"):
                    if fb_cand != active_rec:
                        std_fallbacks.append(fb_cand)
                for fb_rec in std_fallbacks:
                    for c_key in candidate_keys:
                        item = lookup_in_recension_tier(fb_rec, c_key)
                        if item:
                            resolved_recension = fb_rec
                            break
                    if item:
                        break

            # Legacy/direct text_db & propers_web_db fallback
            if not item and hasattr(self, "text_db") and self.text_db:
                for c_key in candidate_keys:
                    item = db_get(self.text_db, c_key)
                    if item and not self._is_unpopulated_gap(item):
                        resolved_recension = "stamford_2014"
                        break
                    item = None

            if not item and hasattr(self, "propers_web_db") and self.propers_web_db:
                for c_key in candidate_keys:
                    item = db_get(self.propers_web_db, c_key)
                    if not item:
                        m = re.match(r'menaion\.([a-z]{3})_(\d{2})\.(?:.*?\.)?([a-z_]+)$', c_key)
                        if m:
                            months = {'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06', 'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'}
                            mo_str, day_str, elem = m.groups()
                            mo_num = months.get(mo_str)
                            if mo_num:
                                for cand_k in [
                                    f'menaion.{mo_num}{day_str}.liturgy.{elem}_{language}',
                                    f'menaion.{mo_num}{day_str}.vespers.{elem}_{language}',
                                    f'menaion.{mo_num}{day_str}.matins.{elem}_{language}',
                                    f'menaion.{mo_num}{day_str}.{elem}_{language}',
                                    f'menaion.{mo_num}{day_str}.liturgy.{elem}_en',
                                    f'menaion.{mo_num}{day_str}.{elem}_en'
                                ]:
                                    item = db_get(self.propers_web_db, cand_k)
                                    if item:
                                        resolved_recension = "royal_doors"
                                        break
                    if item:
                        break

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
            if isinstance(item, str):
                item = {"id": text_id, "content": item, "source": "System Logic"}
            
            # Attach fallback provenance pill when resolved from a fallback recension
            if (
                resolved_recension
                and active_rec
                and resolved_recension != active_rec
                and active_rec not in ("lviv", "royal_doors_web", "sheptytsky_printed", "stamford_printed", "stamford_web_2026")
            ):
                fb_label = RECENSION_DISPLAY_LABELS.get(resolved_recension, resolved_recension.replace("_", " ").title())
                item["is_fallback"] = True
                item["requested_recension"] = active_rec
                item["recension_resolved"] = resolved_recension
                item["provenance_pill"] = f"[Fallback: {fb_label}]"
            elif resolved_recension:
                item.setdefault("recension_resolved", resolved_recension)
                item.setdefault("is_fallback", False)

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
                raw_text = self._normalize_ugcc_text(str(raw_text))
                
                # Sanitization: Strip instructions in () or ending in :
                # e.g. "(Spec. Mel.: ...):" -> moved to metadata
                rubric_matches = re.findall(r'\((.*?)\):?', raw_text)
                if rubric_matches:
                    item["_rubrics"] = item.get("_rubrics", []) + [self._normalize_ugcc_text(r) for r in rubric_matches]
                    # Remove from spoken text
                    clean_content = re.sub(r'\(.*?\):?', '', raw_text).strip()
                else:
                    clean_content = raw_text

                # Musical Syntax: Handle * and **
                # Store segments for musical phrasing
                item["_segments"] = [s.strip() for s in clean_content.split("*") if s.strip()]
                item["content"] = self._normalize_ugcc_text(clean_content.replace("*", "").replace("  ", " ")) # Spoken text
            if isinstance(item, dict):
                if "title" in item and isinstance(item["title"], str):
                    item["title"] = self._normalize_ugcc_text(item["title"])
                if "rubric" in item and isinstance(item["rubric"], str):
                    item["rubric"] = self._normalize_ugcc_text(item["rubric"])
                
            return item
        
        # 2. General Menaion Fallback (when not in strict_corpus_mode)
        if not strict_mode and self.general_menaion_db:
            saint_class_str = ""
            st_name = "Saint"
            if context:
                saint_class_str = context.get("saint_class", "") or ""
                st_name = context.get("st_name") or context.get("feast_title") or "Saint"
                if not saint_class_str and isinstance(context.get("dolnytsky_data"), dict):
                    dd = context["dolnytsky_data"]
                    saint_class_str = dd.get("category") or dd.get("saint_class") or ""
                    st_name = dd.get("title") or st_name

            if saint_class_str:
                key_parts = text_id.split(".")
                suffix = key_parts[-1]
                if suffix in ("troparion_saint", "trop_saint", "troparion_feast", "trop_feast", "troparion_saint_if_any"):
                    suffix = "troparion"
                elif suffix in ("kontakion_saint", "kont_saint", "kontakion_feast", "kont_feast", "kontakion_saint_if_any"):
                    suffix = "kontakion"
                elif len(key_parts) > 2 and "stichera" in key_parts[-2]:
                    suffix = f"{key_parts[-2]}.{suffix}"

                saint_classes = saint_class_str.split(",")
                for st_class in saint_classes:
                    st_class = st_class.strip().lower()
                    if not st_class:
                        continue
                    generic_id = f"general.{st_class}.{suffix}"
                    
                    fallback_item = self.general_menaion_db.get(generic_id)
                    if fallback_item:
                        rendered_item = copy.deepcopy(fallback_item)
                        if "content" in rendered_item and isinstance(rendered_item["content"], str):
                            rendered_item["content"] = rendered_item["content"].replace("{{name}}", st_name)
                        cat_label = st_class.replace("_", " ").title()
                        rendered_item["_source"] = f"General Menaion ({st_class})"
                        rendered_item["is_fallback"] = True
                        rendered_item["provenance_pill"] = f"[General Menaion: {cat_label}]"
                        return rendered_item

        # 3. Psalter Kathisma & Biblical Lectionary Cantorial Directive Handler
        directive_item = self._resolve_cantorial_directive(text_id, context)
        if directive_item:
            return directive_item

        # 4. Missing Handler (Human-readable clean placeholder + structured SGC-04 gap metadata)
        humanized = self.canonical_humanize_key(text_id)
        req_str = f" | Required by: {logic_requirement}" if logic_requirement else ""
        if explicit_recension and not (
            getattr(self, "ordinaries_recension", None) != getattr(self, "propers_recension", None)
            and explicit_recension == getattr(self, "version_id", None)
        ):
            rec_name = explicit_recension.replace("_", " ").title()
        elif active_rec:
            rec_name = RECENSION_DISPLAY_LABELS.get(active_rec, active_rec.replace("_", " ").title())
        else:
            rec_name = getattr(self, "version_id", "royal_doors").replace("_", " ").title()
        return {
            "title": humanized,
            "content": f"[{humanized} (Missing in {rec_name}{req_str})]",
            "source": "System Logic",
            "is_missing": True,
            "canonical_gap_key": text_id,
            "canonical_gap_badge": f"[UNRESOLVED_CANONICAL_GAP: {text_id}]"
        }

    @staticmethod
    def canonical_humanize_key(key: str) -> str:
        """Canonically humanizes internal chant keys and identifiers to standard liturgical English."""
        if not key:
            return ""
        m_wk_dy = re.match(r"^([a-z0-9_]+)\.([a-z0-9_]+)\.week_(\d+)\.day_(\d+)$", key.lower())
        if m_wk_dy:
            book_part, item_part, wk, dy = m_wk_dy.groups()
            return f"{book_part.replace('_', ' ').title()} {item_part.replace('_', ' ').title()} (Week {wk}, Day {dy})"

        raw_base = key.split(".")[-1].lower()
        base = re.sub(r'_\d+$', '', raw_base)
        
        canon_map = {
            "aposticha_feast": "Stichera of the Feast",
            "aposticha_forefeast": "Stichera of the Forefeast",
            "aposticha_afterfeast": "Stichera of the Feast",
            "aposticha_saint": "Stichera of the Saint",
            "aposticha_theotokos": "Stichera of the Theotokos",
            "aposticha_resurrection": "Stichera of the Resurrection",
            "aposticha_daily": "Daily Aposticha",
            "stichera_feast": "Stichera of the Feast",
            "stichera_forefeast": "Stichera of the Forefeast",
            "stichera_afterfeast": "Stichera of the Feast",
            "stichera_saint": "Stichera of the Saint",
            "stichera_theotokos": "Stichera of the Theotokos",
            "stichera_resurrection": "Stichera of the Resurrection",
            "doxastikon_saint": "Doxastikon of the Saint",
            "doxastikon_feast": "Doxastikon of the Feast",
            "doxastikon_forefeast": "Doxastikon of the Forefeast",
            "theotokion_feast": "Theotokion of the Feast",
            "theotokion_forefeast": "Theotokion of the Forefeast",
            "theotokion_afterfeast": "Theotokion of the Feast",
            "theotokion_saint": "Theotokion of the Saint",
            "theotokion_resurrection": "Theotokion of the Resurrection",
            "feast_theotokion": "Theotokion of the Feast",
            "forefeast_theotokion": "Theotokion of the Forefeast",
            "afterfeast_theotokion": "Theotokion of the Feast",
            "saint_doxastikon": "Doxastikon of the Saint",
            "feast_doxastikon": "Doxastikon of the Feast",
            "trop_feast": "Troparion of the Feast",
            "troparion_feast": "Troparion of the Feast",
            "trop_forefeast": "Troparion of the Forefeast",
            "troparion_forefeast": "Troparion of the Forefeast",
            "trop_saint": "Troparion of the Saint",
            "troparion_saint": "Troparion of the Saint",
            "kont_feast": "Kontakion of the Feast",
            "kontakion_feast": "Kontakion of the Feast",
            "kont_saint": "Kontakion of the Saint",
            "kontakion_saint": "Kontakion of the Saint",
            "troparion_saint_if_any": "Troparion of the Saint",
            "troparion_day_of_week": "Troparion of the Day",
            "troparion_temple": "Troparion of the Temple",
            "theotokion_daily": "Daily Theotokion",
            "kontakion_saint_if_any": "Kontakion of the Saint",
            "kontakion_day_of_week": "Kontakion of the Day",
            "kontakion_temple": "Kontakion of the Temple",
            "prayer_holy_trinity_all_creating": "Prayer to the Most Holy Trinity",
            "prayer_eustratius": "Prayer of St. Eustratius",
            "prayer_mardarius": "Prayer of St. Mardarius",
            "prayer_first": "First Prayer of the Midnight Office",
            "prayer_second": "Second Prayer of the Midnight Office",
            "theotokion_aposticha_sunday_in_tone_of_doxastikon": "Theotokion from the Octoechos in the tone of the Doxastikon",
            "theotokion_aposticha_sunday_in_tone_of_doxastikon_else_current_tone": "Theotokion from the Octoechos in the tone of the Doxastikon",
            "theotokion_after_doxastikon": "Theotokion from the Octoechos in the tone of the Doxastikon",
            "theotokion_horologion_or_octoechos": "Theotokion from the Horologion or Octoechos",
        }
        if base in canon_map:
            return canon_map[base]
            
        m = re.match(r"^(aposticha|stichera|doxastikon|theotokion|troparion|kontakion|sessional|exapostilarion)_(feast|forefeast|afterfeast|saint|theotokos|resurrection|temple|cross|day)$", base)
        if m:
            h_type, subj = m.groups()
            h_clean = "Stichera" if h_type == "aposticha" else h_type.capitalize()
            return f"{h_clean} of the {subj.capitalize()}"

        m_rev = re.match(r"^(feast|forefeast|afterfeast|saint|theotokos|resurrection)_(doxastikon|theotokion|troparion|kontakion|sessional|exapostilarion|stichera|aposticha)$", base)
        if m_rev:
            subj, h_type = m_rev.groups()
            h_clean = "Stichera" if h_type == "aposticha" else h_type.capitalize()
            return f"{h_clean} of the {subj.capitalize()}"
            
        m_trop = re.match(r"^(trop|kont)_(feast|forefeast|afterfeast|saint|theotokos|resurrection|temple|cross|day)$", base)
        if m_trop:
            h_type, subj = m_trop.groups()
            h_clean = "Troparion" if h_type == "trop" else "Kontakion"
            return f"{h_clean} of the {subj.capitalize()}"
            
        return base.replace("_", " ").title()

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

