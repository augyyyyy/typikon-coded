"""
Ruthenian Engine - RegionalChantMixin
=====================================
Integrates regional chant variations, neume rules, and hexachord solmization guidelines
into the Byzantine/Ruthenian constraint-logic engine.
"""

import os
import json

class RegionalChantMixin:
    """
    Mixin providing regional chant logic and neume rules for the RuthenianEngine.
    """

    def load_regional_chant_rules(self):
        """
        Loads the regional chant rules database from the Data/Inbox directory.
        """
        if not hasattr(self, '_regional_chant_db') or self._regional_chant_db is None:
            path = os.path.join(self.base_dir, "Data", "Inbox", "regional_chant_rules.json")
            if os.path.exists(path):
                try:
                    self._regional_chant_db = self._load_json(path)
                except Exception:
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            self._regional_chant_db = json.load(f)
                    except Exception:
                        self._regional_chant_db = {}
            else:
                self._regional_chant_db = {}
        return self._regional_chant_db

    def get_regional_chant_override(self, context, slot_key):
        """
        Resolves context-aware regional chant overrides.
        If a regional tradition is active in the context, returns specific instructions or overrides
        for liturgical slots (e.g., 'psalm_103', 'blessed_is_the_man', 'polyeleos', 'eucharistic_canon').
        """
        tradition = context.get("regional_tradition", "").lower()
        if not tradition:
            return None

        rules_db = self.load_regional_chant_rules()
        tradition_data = rules_db.get("regional_dialects", {}).get(tradition, {})
        if not tradition_data:
            return None

        lit_features = tradition_data.get("liturgical_features", {})
        notated_variants = tradition_data.get("notated_variants", {})

        # Slot 1: Psalm 103 (Introductory Psalm)
        if slot_key == "psalm_103":
            if tradition == "suprasl":
                return {
                    "mode": "chanted",
                    "style": "Suprasl Chant (prolonged)",
                    "structure": "Through-composed (no verse/word repetitions)",
                    "selected_verses": [15, 24],
                    "verses_text": {
                        "15": "і траву на службу человіком (and herb for the service of men)",
                        "24": "вся премудростію сотворил єси (in wisdom hast Thou made them all)"
                    },
                    "citation": tradition_data.get("source_manuscript")
                }

        # Slot 2: Blessed is the Man (First Kathisma)
        elif slot_key == "blessed_is_the_man":
            if tradition == "suprasl":
                return {
                    "mode": "chanted",
                    "style": "Suprasl Chant (early through-composed)",
                    "structure": "Through-composed (no repetitions of verses/words)",
                    "citation": tradition_data.get("source_manuscript")
                }

        # Slot 3: Polyeleos
        elif slot_key == "polyeleos":
            if tradition == "suprasl" and "polyeleos" in notated_variants:
                return {
                    "mode": "chanted",
                    "style": "Multanian Chant (Suprasl Heirmologion)",
                    "note": notated_variants.get("polyeleos"),
                    "citation": tradition_data.get("source_manuscript")
                }
            elif tradition == "zhirovitsi":
                return {
                    "mode": "chanted",
                    "style": "Bulgarian & Pidhirya Chant (Dual versions)",
                    "note": lit_features.get("polyeleos_duality"),
                    "citation": tradition_data.get("source_manuscript")
                }

        # Slot 4: Eucharistic Canon
        elif slot_key == "eucharistic_canon":
            if tradition == "manyava_skete":
                return {
                    "mode": "chanted",
                    "style": "Skete Chant (Liturgy of St. Basil the Great)",
                    "note": lit_features.get("liturgy_canon"),
                    "structure": "Genre-thematic sequence (Vespers, Matins, Liturgy)",
                    "citation": tradition_data.get("source_manuscript")
                }

        # Slot 5: God is the Lord (Tone 1)
        elif slot_key == "god_is_the_lord":
            if tradition == "lyubachiv" and context.get("tone", 1) == 1:
                return {
                    "mode": "chanted",
                    "style": "Triple Chant (weekday Rus', Volhynian, and Bulgarian)",
                    "note": "Performer can choose or alternate between these three regional versions.",
                    "citation": tradition_data.get("source_manuscript")
                }

        return None

    def get_solmization_guide(self, tone, is_bemoliar=False):
        """
        Retrieves solmization (hexachord) guidelines for the choir based on the active tone and scale type.
        """
        rules_db = self.load_regional_chant_rules()
        hex_data = rules_db.get("solmization_rules", {}).get("hexachord_system", {})
        if not hex_data:
            return None

        hex_type_key = "bemoliar" if is_bemoliar else "dural"
        active_hex = hex_data.get("hexachord_types", {}).get(hex_type_key, {})

        return {
          "hexachord_type": active_hex.get("name"),
          "scale_steps": active_hex.get("scale_steps"),
          "central_semitone": active_hex.get("central_semitone"),
          "semitone_anchors": {
              "upper_sound_solmization": hex_data.get("semitone_anchor", {}).get("upper_sound"),
              "lower_sound_solmization": hex_data.get("semitone_anchor", {}).get("lower_sound"),
              "fa_pitch": active_hex.get("decisive_sound", {}).get("pitch")
          },
          "step_directions": hex_data.get("step_directions", {}),
          "mutation_guide": {
              "description": hex_data.get("mutation_logic", {}).get("trigger"),
              "technique": hex_data.get("mutation_logic", {}).get("technique"),
              "notation_keys": hex_data.get("mutation_logic", {}).get("notation_indicators", {})
          }
        }

    def get_neume_execution_rules(self, neume_name="pauk"):
        """
        Retrieves execution rules for specific neumes (e.g., pauk / pavuk).
        """
        rules_db = self.load_regional_chant_rules()
        neume_data = rules_db.get("neume_rules", {}).get(neume_name, {})
        return neume_data
