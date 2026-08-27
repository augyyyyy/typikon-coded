import os
import json
from typing import Dict, List, Any, Optional

class FootnoteResolverMixin:
    """Mixin providing synodal footnote indexing and dynamic context matching."""
    _synodal_footnotes_cache: Optional[Dict[str, Any]] = None

    def _ensure_footnotes_loaded(self) -> Dict[str, Any]:
        if self._synodal_footnotes_cache is None:
            base_dir = getattr(self, "base_dir", ".")
            json_path = os.path.join(base_dir, "json_db", "synodal_footnotes.json")
            if not os.path.exists(json_path):
                parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                json_path = os.path.join(parent_dir, "json_db", "synodal_footnotes.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    self._synodal_footnotes_cache = json.load(f)
            else:
                self._synodal_footnotes_cache = {}
        return self._synodal_footnotes_cache

    def get_footnote_by_id(self, footnote_id: str) -> Optional[Dict[str, Any]]:
        db = self._ensure_footnotes_loaded()
        clean_id = str(footnote_id).replace("footnote_", "").strip()
        return db.get(clean_id)

    def resolve_synodal_footnotes(self, context: Dict[str, Any], rubrics: Optional[Dict[str, Any]] = None, service_name: Optional[str] = None, include_academic: bool = False) -> List[Dict[str, Any]]:
        db = self._ensure_footnotes_loaded()
        if not db:
            return []
        menaion_key = context.get("menaion_key", "")
        season = context.get("season", "")
        resolved = []
        seen_ids = set()
        for fn_id, entry in db.items():
            if not include_academic and entry.get("category") == "historical_apparatus":
                continue
            entry_services = entry.get("services", [])
            if service_name:
                service_clean = service_name.replace("Divine ", "").replace("Great ", "").replace("Daily ", "").replace("Small ", "").strip()
                if entry_services and "General" not in entry_services:
                    if not any(s in service_name or service_clean in s for s in entry_services):
                        continue
            triggers = entry.get("triggers", {})
            menaion_triggers = triggers.get("menaion_keys", [])
            matched = False
            if menaion_key and menaion_triggers:
                if menaion_key in menaion_triggers:
                    matched = True
            season_trigger = triggers.get("season")
            if season_trigger:
                if season_trigger == "triodion" and (season in ("lent", "triodion", "holy_week") or context.get("season_id") == "triodion"):
                    matched = True
                elif season_trigger == "pascha" and (season in ("bright_week", "pascha") or context.get("season_id") == "pascha"):
                    matched = True
                elif season_trigger == "pentecostarion" and (season == "pentecostarion" or context.get("season_id") == "pentecostarion"):
                    matched = True
            comp_triggers = triggers.get("components", [])
            if comp_triggers:
                if "censing_initial" in comp_triggers and service_name in ("Vespers", "Great Vespers", "Matins"):
                    matched = True
                if "liturgy_antiphons" in comp_triggers and service_name in ("Liturgy", "DivineLiturgy"):
                    matched = True
                if "kathismata_litanies" in comp_triggers and service_name in ("Matins", "Daily Matins"):
                    matched = True
                if "polyeleos_troparia" in comp_triggers and (rubrics and rubrics.get("variables", {}).get("has_polyeleos")):
                    matched = True
            if matched and fn_id not in seen_ids:
                seen_ids.add(fn_id)
                resolved.append(entry)
        def sort_key(e):
            num_str = e.get("number", "0")
            clean_num = "".join(c for c in num_str if c.isdigit())
            return int(clean_num) if clean_num else 9999
        resolved.sort(key=sort_key)
        return resolved
