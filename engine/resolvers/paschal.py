"""
Ruthenian Engine - PaschalMixin
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

import json
import os
import re
from datetime import date, timedelta
import copy


class PaschalMixin:

    """Mixin providing paschal methods for RuthenianEngine."""


    def resolve_passion_matins_gospels(self, context, rubrics=None):
        """
        Gap 2.9a: Passion Matins — 12 Gospels.
        Citation: Dolnytsky Part IV Lines 561-600.
        
        On Great Thursday evening (Matins of Great Friday), 12 Gospel 
        passages are read, interspersed with 15 Antiphons and Beatitudes.
        
        Returns:
            dict with the 12 Gospel readings and antiphon structure.
        """
        offset = context.get("pascha_offset", None)
        
        # Only on Great Thursday evening = Matins of Great Friday
        if offset is None or offset != -2:
            return {"is_passion_matins": False}
        
        gospels = [
            {"num": 1, "ref": "John 13:31-18:1", "note": "Farewell Discourse and High Priestly Prayer"},
            {"num": 2, "ref": "John 18:1-28", "note": "Arrest in Gethsemane, Peter's denial"},
            {"num": 3, "ref": "Matt 26:57-75", "note": "Trial before Caiaphas"},
            {"num": 4, "ref": "John 18:28-19:16", "note": "Trial before Pilate"},
            {"num": 5, "ref": "Matt 27:3-32", "note": "Death of Judas, scourging, way of the Cross"},
            {"num": 6, "ref": "Mark 15:16-32", "note": "Crucifixion"},
            {"num": 7, "ref": "Matt 27:33-54", "note": "Darkness, death of Christ, earthquake"},
            {"num": 8, "ref": "Luke 23:32-49", "note": "Good thief, 'Father, forgive them'"},
            {"num": 9, "ref": "John 19:25-37", "note": "Mother of God at the Cross, piercing"},
            {"num": 10, "ref": "Mark 15:43-47", "note": "Burial by Joseph of Arimathea"},
            {"num": 11, "ref": "John 19:38-42", "note": "Nicodemus, burial with myrrh"},
            {"num": 12, "ref": "Matt 27:62-66", "note": "Sealing of the tomb, guard"}
        ]
        
        return {
            "is_passion_matins": True,
            "gospels": gospels,
            "antiphons": {
                "count": 15,
                "note": "15 Antiphons interspersed between Gospels",
                "key": "triodion.passion_antiphons"
            },
            "beatitudes": {
                "included": True,
                "note": "Beatitudes sung as part of the antiphon sequence",
                "key": "triodion.passion_beatitudes"
            },
            "processional": {
                "after_gospel": 5,
                "note": "After 5th Gospel, Cross is brought to center of church",
                "citation": "Dolnytsky IV:575 — Processional after 5th Gospel"
            },
            "citation": "Dolnytsky IV:561-600 — Passion Matins with 12 Gospels"
        }


    def resolve_lamentations(self, context, rubrics=None):
        """
        Gap 2.9c: Great Saturday Tomb Matins — Lamentations (Encomia).
        Citation: Dolnytsky Part IV Lines 670-720.
        
        Great Saturday Matins features Kathisma 17 (Psalm 118) divided into 
        three stases, with Lamentations (troparia) interpolated between verses.
        After the third stasis, there is a procession with the Shroud.
        
        Returns:
            dict with Lamentations structure.
        """
        offset = context.get("pascha_offset", None)
        
        if offset is None or offset != -1:
            return {"is_tomb_matins": False}
        
        return {
            "is_tomb_matins": True,
            "structure": {
                "stasis_1": {
                    "key": "triodion.lamentations.stasis_1",
                    "psalm_range": "118:1-72",
                    "refrain_type": "troparia_encomia",
                    "note": "First stasis: verses with troparia lamentations"
                },
                "stasis_2": {
                    "key": "triodion.lamentations.stasis_2",
                    "psalm_range": "118:73-131",
                    "refrain_type": "troparia_encomia",
                    "note": "Second stasis"
                },
                "stasis_3": {
                    "key": "triodion.lamentations.stasis_3",
                    "psalm_range": "118:132-176",
                    "refrain_type": "troparia_encomia",
                    "note": "Third stasis"
                }
            },
            "evlogitaria": {
                "key": "triodion.evlogitaria_of_burial",
                "note": "'Blessed art Thou, O Lord, teach me Thy statutes' — resurrection troparia",
                "citation": "Dolnytsky IV:700 — Evlogitaria after Kathisma 17"
            },
            "procession": {
                "with_shroud": True,
                "timing": "After the Great Doxology",
                "note": "Procession around the church with the Shroud (Plashchanytsia)",
                "hymn": "Holy God, Holy Mighty, Holy Immortal",
                "citation": "Dolnytsky IV:710 — Shroud procession"
            },
            "entrance_with_gospel": {
                "included": True,
                "note": "After procession, entrance with Gospel book",
                "citation": "Dolnytsky IV:715"
            },
            "citation": "Dolnytsky IV:670-720 — Great Saturday Tomb Matins"
        }


    def resolve_burial_vespers(self, context, rubrics=None):
        """
        Gap 2.9d: Great Friday Vespers — Burial Service.
        Citation: Dolnytsky Part IV Lines 633-670.
        
        Great Friday Vespers includes the 'Taking Down from the Cross'
        with the Shroud (Plashchanytsia) being brought out during the
        Gospel reading, and a procession at the conclusion.
        
        Returns:
            dict with Great Friday Vespers/Burial configuration.
        """
        offset = context.get("pascha_offset", None)
        
        if offset is None or offset != -2:
            return {"is_burial_vespers": False}
        
        return {
            "is_burial_vespers": True,
            "stichera": {
                "lord_i_have_cried": {
                    "total_count": 6,
                    "source": "triodion",
                    "type": "passion_stichera"
                }
            },
            "readings": {
                "ot": ["Exodus 33:11-23", "Job 42:12-end", "Isaiah 52:13-54:1"],
                "apostle": "1 Corinthians 1:18-2:2",
                "gospel": {
                    "composite": True,
                    "refs": ["Matt 27:1-38", "Luke 23:39-43", "Matt 27:39-54",
                             "John 19:31-37", "Matt 27:55-61"],
                    "note": "Composite Gospel of the Burial"
                }
            },
            "shroud_procession": {
                "timing": "During the Aposticha, at 'Noble Joseph'",
                "key": "triodion.noble_joseph",
                "note": "Shroud is brought out during 'Noble Joseph'",
                "citation": "Dolnytsky IV:650 — Shroud brought to center of church"
            },
            "aposticha": {
                "key": "triodion.great_friday_aposticha",
                "note": "Special Passion aposticha with 'Noble Joseph'"
            },
            "citation": "Dolnytsky IV:633-670 — Great Friday Vespers/Burial"
        }

    # =========================================================================
    # END SPRINT 4
    # =========================================================================

    # =========================================================================
    # SPRINT 5: PASCHAL + PENTECOSTARION (Gaps 2.6-2.8)
    # =========================================================================


    def resolve_paschal_services(self, context, rubrics=None):
        """
        Gap 2.6: Paschal Matins / Hours / Liturgy.
        Citation: Dolnytsky Part IV Lines 720-850.
        
        Paschal Matins is completely unique:
          - Begins at Royal Doors (not in church)
          - No Six Psalms, no Kathismata, no Sedalen
          - Paschal Canon replaces regular canon
          - "Christ is risen" refrain throughout
          - Paschal Hours replace regular Hours (no psalms, special troparia)
          - Liturgy uses Paschal Antiphons
        
        Returns:
            dict with Paschal service configuration.
        """
        offset = context.get("pascha_offset", None)
        
        if offset is None or not (0 <= offset <= 6):
            return {"is_paschal": False}
        
        is_pascha_night = offset == 0
        bright_day = offset  # 0=Pascha, 1=Bright Monday, ... 6=Bright Saturday
        
        return {
            "is_paschal": True,
            "bright_day": bright_day,
            "matins": {
                "opening": {
                    "procession": is_pascha_night,
                    "troparion_count": 3 if is_pascha_night else 1,
                    "note": "Begins at Royal Doors with 'Christ is risen' (x3)" if is_pascha_night else "Christ is risen (x1)",
                    "citation": "Dolnytsky IV:720 — Paschal Matins opening"
                },
                "canon": {
                    "type": "paschal",
                    "key": "pentecostarion.paschal_canon",
                    "odes": 8,  # Ode 2 is omitted
                    "refrain": "Christ is risen from the dead",
                    "katavasia_each_ode": True,
                    "note": "Paschal Canon of St. John Damascene, katavasia after each ode"
                },
                "suppress": ["six_psalms", "kathismata", "sedalen", "polyeleos",
                             "matins_gospel", "praises_stichera", "doxology"],
                "paschal_stichera": {
                    "key": "pentecostarion.paschal_stichera",
                    "note": "Paschal Stichera of John Damascene at conclusion"
                }
            },
            "hours": {
                "type": "paschal",
                "structure": {
                    "troparion_key": "pentecostarion.paschal_troparion",
                    "kontakion_key": "pentecostarion.paschal_kontakion",
                    "no_psalms": True,
                    "note": "Paschal Hours: no psalms, only Paschal troparion/kontakion"
                },
                "citation": "Dolnytsky IV:780 — Paschal Hours"
            },
            "liturgy": {
                "antiphons": {
                    "type": "paschal",
                    "key": "pentecostarion.paschal_antiphons",
                    "note": "Paschal Antiphons replace ordinary ones"
                },
                "entrance_hymn": {
                    "key": "pentecostarion.paschal_entrance",
                    "text": "In the churches bless God the Lord, from the springs of Israel."
                },
                "instead_of_cherubic": {
                    "key": "pentecostarion.paschal_cherubic_replacement",
                    "text": "Let all mortal flesh keep silence..."
                },
                "communion_hymn": {
                    "key": "pentecostarion.paschal_communion",
                    "text": "Receive ye the body of Christ, taste ye of the Fountain immortal."
                },
                "citation": "Dolnytsky IV:800 — Paschal Liturgy"
            },
            "dismissal": {
                "type": "paschal",
                "opening_count": 3,
                "text_key": "dismissal.paschal"
            },
            "citation": "Dolnytsky IV:720-850 — Paschal Services"
        }


    def resolve_pentecostarion_troparia(self, context, rubrics=None):
        """
        Gap 2.7: Post-Pascha Troparion Cycling.
        Citation: Dolnytsky Part IV Lines 850-920.
        
        After Thomas Sunday through Pentecost, services use the Pentecostarion
        for troparia and kontakia. The weekly cycle is:
          Thomas Sunday (offset 7-13) → Tone 1
          Myrrh-bearing Women (14-20) → Different commemorations
          Paralytic (21-27) → etc.
        
        Returns:
            dict with Pentecostarion troparion configuration.
        """
        offset = context.get("pascha_offset", None)
        
        if offset is None or not (7 <= offset <= 55):
            return {"is_pentecostarion": False}
        
        # Map weeks to commemorations
        week_map = {
            1: {"name": "Thomas Sunday", "offset_range": (7, 13),
                "troparion_key": "pentecostarion.thomas.troparion"},
            2: {"name": "Myrrh-bearing Women", "offset_range": (14, 20),
                "troparion_key": "pentecostarion.myrrhbearers.troparion"},
            3: {"name": "Paralytic", "offset_range": (21, 27),
                "troparion_key": "pentecostarion.paralytic.troparion"},
            4: {"name": "Mid-Pentecost & Samaritan Woman", "offset_range": (28, 34),
                "troparion_key": "pentecostarion.samaritan.troparion"},
            5: {"name": "Man Born Blind", "offset_range": (35, 38),
                "troparion_key": "pentecostarion.blind_man.troparion"},
            6: {"name": "Ascension", "offset_range": (39, 48),
                "troparion_key": "pentecostarion.ascension.troparion"},
            7: {"name": "Holy Fathers of Nicaea", "offset_range": (49, 49),
                "troparion_key": "pentecostarion.fathers.troparion"},
            8: {"name": "Pentecost", "offset_range": (49, 55),
                "troparion_key": "pentecostarion.pentecost.troparion"}
        }
        
        current_week = None
        for wk_num, wk_data in week_map.items():
            start, end = wk_data["offset_range"]
            if start <= offset <= end:
                current_week = wk_data
                break
        
        if not current_week:
            return {"is_pentecostarion": True, "week": None}
        
        return {
            "is_pentecostarion": True,
            "week_name": current_week["name"],
            "troparion_key": current_week["troparion_key"],
            "katavasia": self.resolve_katavasia(context),
            "citation": "Dolnytsky IV:850-920 — Pentecostarion troparion cycling"
        }


    def resolve_pentecost_kneeling(self, context, rubrics=None):
        """
        Gap 2.8: Pentecost Kneeling Prayers.
        Citation: Dolnytsky Part IV Lines 920-950.
        
        At Pentecost Vespers (evening of the feast), three sets of 
        kneeling prayers are read by the priest, during which the 
        faithful kneel for the first time since Pascha.
        
        Returns:
            dict with kneeling prayer configuration.
        """
        offset = context.get("pascha_offset", None)
        
        if offset is None or offset != 49:
            return {"is_pentecost_kneeling": False}
        
        return {
            "is_pentecost_kneeling": True,
            "prayers": [
                {
                    "set": 1,
                    "key": "pentecostarion.kneeling_prayer_1",
                    "note": "Prayer to God the Father",
                    "posture": "kneeling"
                },
                {
                    "set": 2,
                    "key": "pentecostarion.kneeling_prayer_2",
                    "note": "Prayer to God the Son",
                    "posture": "kneeling"
                },
                {
                    "set": 3,
                    "key": "pentecostarion.kneeling_prayer_3",
                    "note": "Prayer to God the Holy Spirit",
                    "posture": "kneeling"
                }
            ],
            "rubric": "First kneeling since Pascha. Deacon intones 'Let us kneel' before each prayer.",
            "citation": "Dolnytsky IV:920-950 — Pentecost Kneeling Prayers"
        }

    # =========================================================================
    # END SPRINT 5
    # =========================================================================

    # =========================================================================
    # SPRINT 6: SPECIALIZED SERVICES (Gaps 4.1-4.4)
    # =========================================================================


    def resolve_corpus_christi(self, context, rubrics=None):
        """
        Gap 4.1: Corpus Christi (Feast of the Body and Blood of Christ).
        Citation: Dolnytsky Part II; GKC Decree.
        
        A special Ruthenian/Ukrainian feast (Thursday after Trinity Sunday)
        with a Eucharistic procession. Not in the standard Byzantine Typikon.
        
        Returns:
            dict with Corpus Christi configuration.
        """
        offset = context.get("pascha_offset", None)
        
        # Corpus Christi = Thursday after Trinity Sunday = Pascha + 60
        if offset is None or offset != 60:
            return {"is_corpus_christi": False}
        
        return {
            "is_corpus_christi": True,
            "rank": "great_feast",
            "structure": {
                "liturgy": {
                    "type": "liturgy_st_john_chrysostom",
                    "note": "Full Liturgy with Eucharistic focus"
                },
                "procession": {
                    "included": True,
                    "stations": 4,
                    "note": "Eucharistic procession with 4 stations and Gospel readings",
                    "citation": "GKC Decree — Corpus Christi procession"
                },
                "hymns": {
                    "key": "supplemental.corpus_christi_hymns",
                    "note": "Special Eucharistic hymns and stichera"
                }
            },
            "citation": "Dolnytsky II / GKC — Corpus Christi (Body and Blood of Christ)"
        }


    def resolve_akathist_saturday(self, context, rubrics=None):
        """
        Gap 4.2: Akathist Saturday (Saturday of the 5th Week of Lent).
        Citation: Dolnytsky Part IV Lines 400-440.
        
        The Akathist Hymn to the Theotokos is sung at Matins. 
        The 24 stanzas (oikoi and kontakia) are read in 4 parts.
        
        Returns:
            dict with Akathist Saturday configuration.
        """
        offset = context.get("pascha_offset", None)
        day_of_week = context.get("day_of_week", 0)
        
        # Saturday of 5th Week = offset -15 (approximately)
        # More precisely: 5th Saturday of Lent
        lent_week = ((offset + 48) // 7) + 1 if offset is not None and offset >= -48 else 0
        
        if lent_week != 5 or day_of_week != 6:
            return {"is_akathist_saturday": False}
        
        return {
            "is_akathist_saturday": True,
            "matins": {
                "akathist": {
                    "key": "triodion.akathist_hymn",
                    "parts": 4,
                    "stanzas_per_part": 6,
                    "total_stanzas": 24,
                    "note": "24 stanzas (12 kontakia + 12 oikoi) in 4 parts",
                    "citation": "Dolnytsky IV:400-440 — Akathist Hymn"
                },
                "kontakion": {
                    "key": "triodion.akathist_kontakion",
                    "text_incipit": "To thee, the Champion Leader"
                },
                "note": "Inserted after kathisma readings at Matins"
            },
            "citation": "Dolnytsky IV:400-440 — Akathist Saturday"
        }


    def resolve_saturdays_of_souls(self, context, rubrics=None):
        """
        Gap 4.3: Saturdays of Souls (Psychosabbata).
        Citation: Dolnytsky Part IV Lines 25-67.
        
        Special memorial Saturdays: Meatfare Saturday, 2nd/3rd/4th Saturdays 
        of Lent, and the Saturday before Pentecost. These include special 
        memorial troparia, kontakia, and canons for the departed.
        
        Returns:
            dict with memorial Saturday configuration.
        """
        offset = context.get("pascha_offset", None)
        day_of_week = context.get("day_of_week", 0)
        
        if day_of_week != 6 or offset is None:
            return {"is_soul_saturday": False}
        
        # Identify specific Soul Saturdays
        soul_saturdays = {
            -57: {"name": "Meatfare Saturday", "key": "triodion.meatfare_saturday"},
            -41: {"name": "2nd Saturday of Lent", "key": "triodion.soul_saturday_2"},
            -34: {"name": "3rd Saturday of Lent", "key": "triodion.soul_saturday_3"},
            -27: {"name": "4th Saturday of Lent", "key": "triodion.soul_saturday_4"},
            48:  {"name": "Saturday before Pentecost", "key": "pentecostarion.pentecost_soul_saturday"}
        }
        
        if offset not in soul_saturdays:
            return {"is_soul_saturday": False}
        
        config = soul_saturdays[offset]
        return {
            "is_soul_saturday": True,
            "name": config["name"],
            "key": config["key"],
            "memorial_elements": {
                "troparion": {"key": f"{config['key']}.troparion",
                              "text_incipit": "Remember, O Lord, as Thou art good, Thy servants"},
                "kontakion": {"key": f"{config['key']}.kontakion",
                              "text_incipit": "With the Saints give rest, O Christ"},
                "canon": {"key": f"{config['key']}.memorial_canon",
                          "note": "Memorial Canon for the departed"},
                "litany": {"type": "memorial",
                          "note": "Special memorial litany with names of departed"}
            },
            "citation": f"Dolnytsky IV:25-67 — {config['name']}"
        }


    def resolve_great_canon_of_andrew(self, context, rubrics=None):
        """
        Gap 4.4: Great Canon of St. Andrew of Crete.
        Citation: Dolnytsky Part IV Lines 190-234.
        
        Covers both the distribution during Clean Week (quarters at Compline)
        and the full reading on Thursday of the 5th Week.
        
        Note: This supplements resolve_great_compline but provides 
        additional detail for the canon text structure itself.
        
        Returns:
            dict with Great Canon configuration.
        """
        offset = context.get("pascha_offset", None)
        day_of_week = context.get("day_of_week", 0)
        
        if offset is None:
            return {"is_great_canon": False}
        
        lent_week = ((offset + 48) // 7) + 1 if offset >= -48 else 0
        
        # Clean Week quarters
        if lent_week == 1 and day_of_week in (1, 2, 3, 4):
            quarter = day_of_week
            ode_ranges = {
                1: {"odes": [1, 2, 3], "note": "Odes 1-3"},
                2: {"odes": [4, 5, 6], "note": "Odes 4-6"},
                3: {"odes": [7, 8], "note": "Odes 7-8"},
                4: {"odes": [9], "note": "Ode 9 + Life of St. Mary of Egypt (partial)"}
            }
            return {
                "is_great_canon": True,
                "mode": "quarter",
                "quarter": quarter,
                "odes": ode_ranges[quarter]["odes"],
                "key": f"triodion.great_canon.quarter_{quarter}",
                "context_service": "great_compline",
                "citation": f"Dolnytsky IV:190 — Great Canon, quarter {quarter} at Compline"
            }
        
        # Thursday of 5th Week: full
        if lent_week == 5 and day_of_week == 4:
            return {
                "is_great_canon": True,
                "mode": "full",
                "odes": list(range(1, 10)),
                "key": "triodion.great_canon.full",
                "life_of_mary_of_egypt": {
                    "included": True,
                    "key": "triodion.life_mary_egypt",
                    "note": "Life of St. Mary of Egypt read between odes"
                },
                "context_service": "matins",
                "citation": "Dolnytsky IV:210 — Full Great Canon at Matins, Thursday of 5th Week"
            }
        
        return {"is_great_canon": False}

    # =========================================================================
    # END SPRINT 6
    # =========================================================================

    # PHASE 13: DIGEST HELPERS


    def resolve_passion_vespers_readings(self, context, rubrics=None):
        """
        Passion Vespers Readings (Good Friday Evening).
        Citation: Dolnytsky Part IV (Holy Week)
        
        Structure:
        - Special paremias and readings for burial service
        - Apostol from I Corinthians
        - Gospel composite from all four Evangelists (Joseph of Arimathea)
        """
        pascha_offset = context.get("pascha_offset", -100)
        title = context.get("title", "").lower()
        
        # Only applies on Good Friday evening (Pascha offset -2 at evening)
        if pascha_offset != -2 and "good friday" not in title and "great friday" not in title:
            return None
        
        return {
            "type": "passion_vespers_readings",
            "prokeimenon": {
                "text": "They divided my garments among them, and for my vesture they cast lots.",
                "ref_key": "triodion.prokeimenon_good_friday"
            },
            "paremia_1": {
                "book": "Exodus",
                "chapter": "33:11-23",
                "ref_key": "triodion.paremia_gf_1"
            },
            "paremia_2": {
                "book": "Job",
                "chapter": "42:12-17",
                "ref_key": "triodion.paremia_gf_2"
            },
            "paremia_3": {
                "book": "Isaiah",
                "chapter": "52:13 - 54:1",
                "ref_key": "triodion.paremia_gf_3"
            },
            "epistle": {
                "book": "I Corinthians",
                "chapter": "1:18 - 2:2",
                "ref_key": "triodion.epistle_good_friday",
                "content": "For the word of the Cross is foolishness to those who are perishing..."
            },
            "alleluia": {
                "text": "Save me, O God, for the waters are come in unto my soul.",
                "ref_key": "triodion.alleluia_good_friday"
            },
            "gospel": {
                "composite": True,
                "sources": ["Matthew 27:1-38", "Luke 23:39-43", "Matthew 27:39-54", "John 19:31-37", "Matthew 27:55-61"],
                "ref_key": "triodion.gospel_good_friday_vespers",
                "content": "The Burial of Christ (Composite Gospel)"
            }
        }

    # PHASE 6: COMPLINE (EXTREME)


    def resolve_great_canon_portion(self, context, rubrics):
        # Great Canon Divider
        day = context.get("day_of_week", 1)
        # Mon=1, Tue=2, Wed=3, Thu=4
        return {"type": "canon_portion", "part": day}


    def resolve_paschal_trisagion(self, context, rubrics):
        # I. Pneumatic Suppression (Omit Heavenly King)
        return {"type": "fixed_ref", "ref_key": "horologion.trisagion_no_heavenly_king"}
