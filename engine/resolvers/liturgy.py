from engine.core import liturgical_source
"""
Ruthenian Engine - LiturgyMixin
Extracted from ruthenian_engine.py during Phase 1 modularization.
"""

import json
import os
import re
from datetime import date, timedelta
import copy


class LiturgyMixin:

    """Mixin providing liturgy methods for RuthenianEngine."""


    def resolve_antiphon_type(self, context):
        """
        Determines the Antiphon set based on the Paradigm.
        """
        paradigm = self.identify_paradigm(context)
        
        if paradigm == "p_feast_lord":
            return "antiphons_festal"
        elif paradigm == "p1_sunday_resurrection":
            return "antiphons_typical" 
        else:
            return "antiphons_daily"


    def resolve_isodikon(self, context):
        """
        Determines the Little Entrance Verse (Isodikon).
        Standard: 'Come let us worship... O Son of God, risen from the dead...'
        Festal: '...O Son of God, wondrous in the saints...' OR special verse.
        """
        paradigm = self.identify_paradigm(context)
        
        # P_Feast_Lord -> Special Isodikon (needs lookup)
        if paradigm == "p_feast_lord":
            return {
                "verse": "Blessed is He who comes in the name of the Lord. God is the Lord and has appeared to us.",
                "refrain": "O Son of God, baptized in the Jordan, save us who sing to You: Alleluia." # Example for Theophany
            }

        # P1 Sunday -> "Risen from the dead"
        if paradigm == "p1_sunday_resurrection":
            return {
                "verse": "Come, let us worship and bow down before Christ.",
                "refrain": "O Son of God, risen from the dead, save us who sing to You: Alleluia."
            }
            
        # General Saint/Weekday -> "Wondrous in the saints"
        return {
            "verse": "Come, let us worship and bow down before Christ.",
            "refrain": "O Son of God, wondrous in the saints, save us who sing to You: Alleluia."
        }


    def resolve_liturgy_extensions(self, context):
        """
        Resolves post-liturgy extensions (e.g. Blessing of Water, Kneeling Prayers).
        """
        extensions = []
        
        # Theophany Eve (Jan 5)
        if context.get("date", "").endswith("-01-05"):
            extensions.append("great_sanctification_water")
            
        return extensions


    def resolve_zadostoinyk(self, context):
        """
        Resolves the replacement for 'It is truly meet' (Ode 9).
        Returns the Irmos to be sung.
        """
        paradigm = self.identify_paradigm(context)
        
        # In a full implementation, this checks the 'Menaion' or 'Pentecostarion' 
        # for the 'Ode 9 Legacy' slot.
        
        if paradigm == "p_feast_lord":
            return {
                "type": "festal_irmos",
                "content": "[Festal Zadostoinyk of the Feast]"
            }
        
        # Standard
        return {
            "type": "standard",
            "content": "It is truly meet..."
        }


    def resolve_liturgy_type(self, context, rubrics=None):
        """
        NEW-2: Determines Chrysostom vs Basil vs Presanctified vs No Liturgy.
        
        Citation: Dolnytsky Part 1 Lines 219-221, Part 4:
        - Basil: 5 Lenten Sundays, Holy Thursday, Holy Saturday, Jan 1,
                 Eve of Nativity (Dec 24), Eve of Theophany (Jan 5)
        - Presanctified: Wed/Fri of Lent + specific other days
        - No Liturgy: Lenten weekdays (Mon/Tue/Thu) except feasts
        - Chrysostom: all other days
        """
        day_of_week = context.get("day_of_week", 0)
        pascha_offset = context.get("pascha_offset", 0)
        date_str = context.get("date", "")
        season = context.get("season_id", "")
        
        # Check Triodion-specific overrides first
        triodion_case = self.resolve_general_case(context)
        if triodion_case:
            triodion_liturgy = triodion_case.get("variables", {}).get("liturgy_type")
            if triodion_liturgy:
                return {
                    "type": triodion_liturgy,
                    "citation": f"Triodion case: {triodion_case.get('title', 'unknown')}"
                }
        
        # Fixed Basil dates (by civil date)
        mmdd = ""
        if len(date_str) >= 10:
            mmdd = date_str[5:10]  # "MM-DD"
        
        basil_dates = ["01-01", "12-24", "01-05"]  # Jan 1, Nativity Eve, Theophany Eve
        if mmdd in basil_dates:
            if mmdd in ["12-24", "01-05"] and day_of_week in [0, 6]:
                return {
                    "type": "liturgy_chrysostom",
                    "citation": f"Dolnytsky — Chrysostom Liturgy on {mmdd} (Saturday/Sunday)"
                }
            return {
                "type": "liturgy_basil",
                "citation": f"Dolnytsky — Basil Liturgy on {mmdd}"
            }
            
        if mmdd in ["12-25", "01-06"] and day_of_week in [0, 1]:
            return {
                "type": "liturgy_basil",
                "citation": f"Dolnytsky — Basil Liturgy on {mmdd} falling on Sunday/Monday"
            }
        
        # Lenten Sundays (offsets -42 through -7, excluding Palm Sunday which is -7)
        if season == "triodion" and day_of_week == 0:
            if -42 <= pascha_offset <= -14:  # 1st through 5th Sunday of Lent
                return {
                    "type": "liturgy_basil",
                    "citation": "Dolnytsky Part 4 — Basil Liturgy on Lenten Sundays"
                }
        
        # Holy Thursday and Holy Saturday
        if pascha_offset == -3:  # Holy Thursday
            return {"type": "liturgy_basil", "citation": "Dolnytsky Part 4 — Basil on Holy Thursday"}
        if pascha_offset == -1:  # Holy Saturday
            return {"type": "liturgy_basil", "citation": "Dolnytsky Part 4 — Basil on Holy Saturday"}
        
        # Presanctified: Wed/Fri of Lent
        if season == "triodion" and day_of_week in (3, 5):  # Wed, Fri
            if -48 <= pascha_offset <= -8:  # Clean week through 6th week
                return {
                    "type": "presanctified",
                    "citation": "Dolnytsky Part 4 — Presanctified on Lenten Wed/Fri"
                }
        
        # No Liturgy: Lenten Mon/Tue/Thu with some exceptions
        if season == "triodion" and day_of_week in (1, 2, 4):
            if -48 <= pascha_offset <= -8:
                rank = context.get("dolnytsky_rank", "")
                if rank not in ("LORD", "THEOTOKOS", "MOG", "VIGIL", "POLYELEOS"):
                    return {
                        "type": "none",
                        "citation": "Dolnytsky Part 4 — No Liturgy on Lenten Mon/Tue/Thu"
                    }
        
        # Default: Chrysostom
        return {
            "type": "liturgy_chrysostom",
            "citation": "Dolnytsky — Divine Liturgy of St. John Chrysostom (default)"
        }


    def resolve_liturgy_antiphons(self, context, rubrics):
        """
        Determines the Antiphon strategy (Typical Psalms vs Festal vs Weekday).
        """
        rules = self.liturgy_logic.get("antiphon_logic", [])
        rank = self.calculate_rank(context)
        day = context["day_of_week"]
        
        strategy = "weekday_antiphons" # Default
        
        for rule in rules:
            cond = rule.get("condition", "")
            match = False
            
            if cond == "default":
                continue # Already set default
                
            if "rank >=" in cond:
                try:
                    req_rank = int(cond.split(">=")[1].strip())
                    if rank <= req_rank: 
                         match = True
                except:
                    pass
            elif "day_of_week == 0" in cond:
                if day == 0: match = True
                
            if match:
                strategy = rule.get("strategy")
                break
                
        return {
            "type": "generator",
            "generator_method": "generate_antiphons",
            "args": { "strategy": strategy }
        }


    def resolve_liturgy_hymns(self, context, rubrics):
        """
        Resolves the order of Troparia and Kontakia (L-03) with Temple Logic.
        """
        collision_override = context.get("variables", {}).get("liturgy_hymns_override") or context.get("overrides", {}).get("liturgy_hymns_override")
        if not collision_override and rubrics:
            collision_override = rubrics.get("variables", {}).get("liturgy_hymns_override") or rubrics.get("overrides", {}).get("liturgy_hymns_override")
            
        if not collision_override:
            collision_override = context.get("variables", {}).get("troparia_sequence") or context.get("overrides", {}).get("troparia_sequence")
            if not collision_override and rubrics:
                collision_override = rubrics.get("variables", {}).get("troparia_sequence") or rubrics.get("overrides", {}).get("troparia_sequence")
                
        if collision_override and isinstance(collision_override, str):
            mapping = {
                "circumcision_basil_glory_kont_basil_bn_kont_circumcision": [
                    {"type": "troparion", "source": "feast"},
                    {"type": "troparion", "source": "menaion_saint"},
                    {"type": "glory"},
                    {"type": "kontakion", "source": "menaion_saint"},
                    {"type": "both_now"},
                    {"type": "kontakion", "source": "feast"}
                ],
                "indiction_simeon_glory_kont_simeon_bn_kont_indiction": [
                    {"type": "troparion", "source": "feast"},
                    {"type": "troparion", "source": "menaion_saint"},
                    {"type": "glory"},
                    {"type": "kontakion", "source": "menaion_saint"},
                    {"type": "both_now"},
                    {"type": "kontakion", "source": "feast"}
                ],
                "ascension_john_glory_kont_john_bn_kont_ascension": [
                    {"type": "troparion", "source": "feast"},
                    {"type": "troparion", "source": "menaion_saint"},
                    {"type": "glory"},
                    {"type": "kontakion", "source": "menaion_saint"},
                    {"type": "both_now"},
                    {"type": "kontakion", "source": "feast"}
                ],
                "feast_glory_bn_kont_feast": [
                    {"type": "troparion", "source": "feast"},
                    {"type": "glory_both_now"},
                    {"type": "kontakion", "source": "feast"}
                ],
                "saint_demetrius_earthquake_stacking": [
                    {"type": "troparion", "source": "menaion_saint"},
                    {"type": "troparion", "source": "feast"},
                    {"type": "glory"},
                    {"type": "kontakion", "source": "menaion_saint"},
                    {"type": "both_now"},
                    {"type": "kontakion", "source": "feast"}
                ],
                "nativity_synaxis_stacking": [
                    {"type": "troparion", "source": "feast"},
                    {"type": "troparion", "source": "menaion_saint"},
                    {"type": "glory"},
                    {"type": "kontakion", "source": "menaion_saint"},
                    {"type": "both_now"},
                    {"type": "kontakion", "source": "feast"}
                ],
                "nativity_stephen_stacking": [
                    {"type": "troparion", "source": "feast"},
                    {"type": "troparion", "source": "menaion_saint"},
                    {"type": "glory"},
                    {"type": "kontakion", "source": "menaion_saint"},
                    {"type": "both_now"},
                    {"type": "kontakion", "source": "feast"}
                ],
                "saint_constantine_stacking": [
                    {"type": "troparion", "source": "menaion_saint"},
                    {"type": "glory"},
                    {"type": "kontakion", "source": "menaion_saint"},
                    {"type": "both_now"},
                    {"type": "theotokion", "source": "resurrection"}
                ],
                "cross_maccabees_stacking": [
                    {"type": "troparion", "source": "feast"},
                    {"type": "troparion", "source": "menaion_saint"},
                    {"type": "glory"},
                    {"type": "kontakion", "source": "menaion_saint"},
                    {"type": "both_now"},
                    {"type": "kontakion", "source": "feast"}
                ]
            }
            if collision_override in mapping:
                collision_override = mapping[collision_override]

        if collision_override:
            return {
                "type": "hymn_stack",
                "components": collision_override
            }

        day = context.get("day_of_week", 1)
        temple_type = context.get("temple_type", "saint") # 'saint' or 'theotokos'
        
        # Wednesday/Friday Cross Precedence for Simple Ranks (Dolnytsky Part II)
        from engine.utils.type_utils import parse_rank_integer
        rank_val = context.get("rank", 5)
        if rubrics and rubrics.get("variables"):
            rank_val = rubrics["variables"].get("rank", rank_val)
        rank_numeric = parse_rank_integer(rank_val)
        
        is_festal_day = (
            rank_numeric == 1 or 
            context.get("dolnytsky_rank") in ["LORD", "THEOTOKOS", "MOG"] or 
            context.get("feast_level") in ["lord", "theotokos"] or
            context.get("paradigm") in ["p_feast_lord", "p_feast_theotokos"]
        )
        
        if day in (3, 5) and not is_festal_day:
            final_components = [
                {"type": "troparion", "source": "cross"}
            ]
            if temple_type == "theotokos":
                final_components.append({"type": "troparion", "source": "temple"})
            
            # Commemorate saint only if rank is Doxology (4) or higher (<= 3), or explicitly overridden
            if rank_numeric <= 4 or context.get("combined_service_override"):
                final_components.extend([
                    {"type": "troparion", "source": "menaion_saint"},
                    {"type": "kontakion", "source": "menaion_saint", "glory": True},
                    {"type": "kontakion", "source": "cross", "both_now": True}
                ])
            else:
                # No saint commemoration - only day propers (Cross)
                final_components.append(
                    {"type": "kontakion", "source": "cross", "glory": True, "both_now": True}
                )
            return {
                "type": "hymn_stack",
                "components": final_components
            }

        is_fore_after = bool(
            context.get("is_fore_or_afterfeast") or
            context.get("triodion_period") in ["forefeast", "afterfeast", "apodosis"] or
            context.get("dolnytsky_rank") in ["forefeast", "afterfeast", "apodosis"]
        )
        d_title = context.get("dolnytsky_title", "").lower()
        d_commem = context.get("dolnytsky_commemoration", "").lower()
        if any(x in d_title or x in d_commem for x in ["forefeast", "afterfeast", "apodosis"]):
            is_fore_after = True

        is_sunday = (day == 0)
        if not is_sunday and rank_numeric <= 3 and is_fore_after:
            final_components = [
                {"type": "troparion", "source": "feast"},
                {"type": "troparion", "source": "menaion_saint"},
                {"type": "kontakion", "source": "menaion_saint", "glory": True},
                {"type": "kontakion", "source": "feast", "both_now": True}
            ]
            return {
                "type": "hymn_stack",
                "components": final_components
            }

        template_key = "weekday_standard"
        if (
            context.get("dolnytsky_rank") in ["LORD", "THEOTOKOS", "MOG"] or 
            context.get("paradigm") in ["p_feast_lord", "p_feast_theotokos"] or 
            context.get("feast_level") in ["lord", "theotokos"]
        ):
            template_key = "festal_only"
        elif day == 0:
            if temple_type == "theotokos":
                template_key = "sunday_theotokos_temple"
            else:
                template_key = "sunday_saint_temple"
            
        template = self.liturgy_logic.get("hymn_ordering_templates", {}).get(template_key, {})
        raw_order = template.get("order", [])
        
        # Filter components based on conditions
        final_components = []
        is_afterfeast = context.get("is_afterfeast", False)
        
        for comp in raw_order:
            # Check conditions if they exist
            if "condition" in comp:
                 cond = comp["condition"]
                 if "not is_afterfeast" in cond and is_afterfeast:
                      continue
                 if "temple_type != 'theotokos'" in cond and temple_type == "theotokos":
                      continue
            final_components.append(comp)
        
        return {
            "type": "hymn_stack",
            "components": final_components
        }


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:2.20.2")
    def resolve_trisagion_type(self, context, rubrics=None):
        """
        Trisagion Type Selection for Liturgy.
        Citation: Dolnytsky Part II (Trisagion replacements)
        
        RULES:
        - "As many as have been baptized" replaces Trisagion on:
          - Nativity, Theophany, Lazarus Saturday, Palm Sunday
          - Holy Saturday, Pascha through Bright Week
          - Pentecost
        - "Before Thy Cross we bow down" replaces on:
          - Exaltation of Cross (Sept 14)
          - Third Sunday of Lent (Veneration of Cross)
          - Aug 1 (Procession of Cross)
        """
        title = context.get("title", "").lower()
        feast_id = context.get("feast_id", "")
        paradigm = context.get("paradigm", "")
        pascha_offset = context.get("pascha_offset", -100)
        date = context.get("date", "")
        
        # Extract month-day for fixed feasts
        today_md = date[5:] if len(date) >= 10 else ""
        
        # BAPTISMAL HYMN: "As many as have been baptized into Christ"
        # Nativity
        if today_md == "12-25" or feast_id == "nativity" or "nativity" in title:
            return {
                "type": "replacement",
                "replacement": "as_many_baptized",
                "ref_key": "liturgikon.as_many_as_baptized",
                "text": "As many as have been baptized into Christ have put on Christ. Alleluia."
            }
        
        # Theophany
        if today_md == "01-06" or feast_id == "theophany" or "theophany" in title:
            return {
                "type": "replacement",
                "replacement": "as_many_baptized",
                "ref_key": "liturgikon.as_many_as_baptized",
                "text": "As many as have been baptized into Christ have put on Christ. Alleluia."
            }
        
        # Lazarus Saturday
        if pascha_offset == -8 or "lazarus" in title:
            return {
                "type": "replacement",
                "replacement": "as_many_baptized",
                "ref_key": "liturgikon.as_many_as_baptized",
                "text": "As many as have been baptized into Christ have put on Christ. Alleluia."
            }
        
        # Palm Sunday
        if pascha_offset == -7 or paradigm == "p_palm_sunday" or "entry" in title or "palm" in title:
            return {
                "type": "replacement",
                "replacement": "as_many_baptized",
                "ref_key": "liturgikon.as_many_as_baptized",
                "text": "As many as have been baptized into Christ have put on Christ. Alleluia."
            }
        
        # Holy Saturday
        if pascha_offset == -1 or "holy saturday" in title:
            return {
                "type": "replacement",
                "replacement": "as_many_baptized",
                "ref_key": "liturgikon.as_many_as_baptized",
                "text": "As many as have been baptized into Christ have put on Christ. Alleluia."
            }
        
        # Pascha through Bright Week (offset 0-6)
        if 0 <= pascha_offset <= 6 or paradigm == "p_pascha":
            return {
                "type": "replacement",
                "replacement": "as_many_baptized",
                "ref_key": "liturgikon.as_many_as_baptized",
                "text": "As many as have been baptized into Christ have put on Christ. Alleluia."
            }
        
        # Pentecost
        if pascha_offset == 49 or "pentecost" in title:
            return {
                "type": "replacement",
                "replacement": "as_many_baptized",
                "ref_key": "liturgikon.as_many_as_baptized",
                "text": "As many as have been baptized into Christ have put on Christ. Alleluia."
            }
        
        # CROSS HYMN: "Before Thy Cross we bow down"
        # Exaltation of Cross (Sept 14)
        if today_md == "09-14" or feast_id == "exaltation_cross" or "exaltation" in title:
            return {
                "type": "replacement",
                "replacement": "before_thy_cross",
                "ref_key": "liturgikon.before_thy_cross",
                "text": "Before Thy Cross we bow down in worship, O Master, and Thy holy Resurrection we glorify."
            }
        
        # Third Sunday of Lent (Veneration of Cross) - offset around -28
        if -28 <= pascha_offset <= -22 and context.get("day_of_week") == 0:
            if "cross" in title or "veneration" in title:
                return {
                    "type": "replacement",
                    "replacement": "before_thy_cross",
                    "ref_key": "liturgikon.before_thy_cross",
                    "text": "Before Thy Cross we bow down in worship, O Master, and Thy holy Resurrection we glorify."
                }
        
        # Aug 1 Procession of Cross
        if today_md == "08-01" or "procession" in title:
            return {
                "type": "replacement",
                "replacement": "before_thy_cross",
                "ref_key": "liturgikon.before_thy_cross",
                "text": "Before Thy Cross we bow down in worship, O Master, and Thy holy Resurrection we glorify."
            }
        
        # DEFAULT: Standard Trisagion
        return {
            "type": "standard",
            "ref_key": "horologion.trisagion",
            "text": "Holy God, Holy Mighty, Holy Immortal, have mercy on us."
        }


    def resolve_cherubic_hymn(self, context, rubrics):
        rules = self.liturgy_logic.get("cherubic_logic", [])
        for rule in rules:
            if "is_great_thursday" in rule["condition"] and context.get("title") == "Great Thursday":
                return {"type": "fixed_ref", "ref_key": f"triodion.{rule['replacement']}"}
                
        return {"type": "fixed_ref", "ref_key": "liturgikon.cherubic_hymn_standard"}


    def resolve_liturgy_megalynarion(self, context, rubrics):
        # Scenario C: Basil Liturgy
        # Scenario B: Festal Zadostoinyk
        rules = self.liturgy_logic.get("megalynarion_logic", [])
        rank = self.calculate_rank(context)
        
        for rule in rules:
             if "rank == 1" in rule["condition"] and rank == 1:
                 return {"type": "variable", "ref_key": "festal_zadostoinyk", "note": "Use 9th Ode Heirmos"}
             if "basil" in rule["condition"] and context.get("liturgy_type") == "basil":
                 return {"type": "fixed_ref", "ref_key": "horologion.in_thee_rejoiceth"}
                 
        return {"type": "fixed_ref", "ref_key": "horologion.axion_estin"}


    def resolve_liturgy_dismissal(self, context, rubrics):
        # Part VI: Dismissal Logic
        
        # 1. Check for Festal Preamble (Feast of Lord)
        preambles = self.liturgy_logic.get("dismissal_preambles", {})
        preamble = ""
        
        if context.get("title") == "Theophany": preamble = preambles.get("theophany")
        elif context.get("title") == "Nativity": preamble = preambles.get("nativity")
        elif context.get("title") == "Pascha": preamble = preambles.get("pascha")
        
        # 2. Check Resurrectional Status
        is_resurrection = False
        day = context.get("day_of_week")
        try: day = int(day)
        except: pass
        
        if day == 0: is_resurrection = True
        
        parts = ["May Christ our true God"]
        if preamble:
             # Dolnytsky: Preamble replaces "Who rose from the dead" unless it IS Pascha?
             # Actually Preamble is usually "May Christ our true God, who for our salvation..."
             parts[0] += ", " + preamble
        elif is_resurrection:
            parts[0] += ", who rose from the dead"
            
        return {"type": "text", "content": "".join(parts)}


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:6.4")
    def resolve_basil_megalynarion(self, context, rubrics=None):
        """
        Megalynarion for Liturgy of St. Basil.
        Citation: Dolnytsky Part II (Basil Liturgy)
        
        RULE: "In Thee Rejoiceth" replaces "Axion Estin" at Basil Liturgy.
        Exception: On Great Feasts, use the 9th Ode Irmos of the Feast.
        
        Occasions for Basil Liturgy (10x/year):
        - Five Sundays of Great Lent
        - Holy Thursday, Holy Saturday
        - Eve of Nativity (weekday), Eve of Theophany (weekday)
        - January 1 (St. Basil's Day)
        """
        liturgy_type = context.get("liturgy_type", "chrysostom")
        from engine.utils.type_utils import parse_rank_integer
        rank = parse_rank_integer(context.get("rank", 5))
        paradigm = context.get("paradigm", "")
        feast_id = context.get("feast_id", None)
        
        # Only applies to Basil Liturgy
        if liturgy_type != "basil":
            return None  # Fall through to standard megalynarion
        
        # RULE: Great Feast at Basil Liturgy - use 9th Ode Irmos
        if rank == 1 or paradigm in ["p_feast_lord", "p_feast_theotokos"]:
            return {
                "type": "megalynarion",
                "source": "feast_irmos",
                "ref_key": f"menaion.{feast_id}.ode_9_irmos" if feast_id else "feast.ode_9_irmos",
                "rubric": "Instead of 'It is truly meet', we sing the Irmos of the 9th Ode"
            }
        
        # DEFAULT: "In Thee Rejoiceth"
        return {
            "type": "megalynarion",
            "source": "basil",
            "ref_key": "horologion.in_thee_rejoiceth",
            "text": "In thee rejoiceth, O Full of Grace, all creation..."
        }


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:2.5.3.5")
    def resolve_communion_hymn(self, context, rubrics=None):
        """
        Communion Hymn (Причастен/Koinonikon).
        Citation: Dolnytsky Part II (Communion cycle)
        
        RULE: Different hymns for different days and occasions.
        Sunday always: "Praise the Lord from the heavens"
        Great Feast: Proper of feast
        Weekday: Tone-appropriate or proper of day
        """
        def resolve_str_hymn(key):
            known_hymns = {
                "righteous_memory": "In everlasting remembrance shall the righteous be; he shall not be afraid of evil tidings.",
                "their_sound_has_gone_forth": "Their sound hath gone forth into all the earth, and their words unto the ends of the world."
            }
            if key in known_hymns:
                return {
                    "type": "communion_hymn",
                    "text": known_hymns[key],
                    "ref_key": key
                }
            try:
                asset = self.get_text(key, context=context)
                if asset and isinstance(asset, dict) and "content" in asset:
                    return {
                        "type": "communion_hymn",
                        "text": asset["content"],
                        "ref_key": key
                    }
            except Exception:
                pass
            return {
                "type": "communion_hymn",
                "text": key,
                "ref_key": ""
            }

        if rubrics:
            overrides = rubrics.get("variables", {}) or rubrics.get("overrides", {})
            
            # 1. Check if nested inside liturgy_readings override
            l_readings = overrides.get("liturgy_readings")
            if l_readings and isinstance(l_readings, list) and len(l_readings) > 0:
                first_r = l_readings[0]
                if isinstance(first_r, dict) and "communion_hymn" in first_r:
                    c_h = first_r["communion_hymn"]
                    if isinstance(c_h, dict):
                        return {
                            "type": "communion_hymn",
                            "text": c_h.get("text", ""),
                            "ref_key": c_h.get("ref_key", "")
                        }
                    elif isinstance(c_h, str):
                        return resolve_str_hymn(c_h)
            
            # 2. Check for direct communion_hymn override
            c_h = overrides.get("communion_hymn")
            if c_h:
                if isinstance(c_h, dict):
                    return {
                        "type": "communion_hymn",
                        "text": c_h.get("text", ""),
                        "ref_key": c_h.get("ref_key", "")
                    }
                elif isinstance(c_h, str):
                    return resolve_str_hymn(c_h)

        day_of_week = context.get("day_of_week", 0)
        from engine.utils.type_utils import parse_rank_integer
        rank = parse_rank_integer(context.get("rank", 5))
        paradigm = context.get("paradigm", "")
        feast_id = context.get("feast_id", None)
        tone = context.get("tone", 1)
        season = context.get("season", "ordinary")
        liturgy_type = context.get("liturgy_type", "chrysostom")

        # EUCHARIST PERIOD AFTERFEAST (pascha_offset between 60 and 67)
        pascha_offset = context.get("pascha_offset")
        if pascha_offset is not None and 60 <= pascha_offset <= 67:
            saints = context.get("saints", [])
            if rank <= 3 and saints:
                return {
                    "type": "communion_hymn",
                    "text": "Receive the Body of Christ; taste the fountain of immortality. And of the Saint: Their sound hath gone forth into all the earth, and their words unto the ends of the world.",
                    "ref_key": "pentecostarion.eucharist.communion_combined"
                }
            else:
                return {
                    "type": "communion_hymn",
                    "text": "Receive the Body of Christ; taste the fountain of immortality.",
                    "ref_key": "pentecostarion.eucharist.communion"
                }

        # PRESANCTIFIED: Special communion
        if liturgy_type == "presanctified":
            return {
                "type": "communion_hymn",
                "text": "Taste and see that the Lord is good.",
                "ref_key": "triodion.communion_presanctified"
            }
        
        # PASCHAL SEASON
        if season == "pascha" or paradigm == "p_pascha":
            return {
                "type": "communion_hymn",
                "text": "Receive the Body of Christ; taste the Fountain of Immortality.",
                "ref_key": "pentecostarion.communion_paschal"
            }
        
        # GREAT FEAST: Proper communion hymn
        if rank == 1 or paradigm in ["p_feast_lord", "p_feast_theotokos"]:
            return {
                "type": "communion_hymn",
                "source": "feast",
                "ref_key": f"menaion.{feast_id}.communion_hymn" if feast_id else "feast.communion_hymn"
            }
        
        # SUNDAY: Always "Praise the Lord"
        if day_of_week == 0:
            return {
                "type": "communion_hymn",
                "text": "Praise the Lord from the heavens, praise Him in the highest.",
                "ref_key": "octoechos.communion_sunday"
            }
        
        # WEEKDAY PROPER
        weekday_hymns = {
            1: {"text": "He maketh His angels spirits...", "ref_key": "horologion.communion_monday"},
            2: {"text": "In everlasting remembrance shall the righteous be...", "ref_key": "horologion.communion_tuesday"},
            3: {"text": "I will take the cup of salvation, and I will call upon the name of the Lord...", "ref_key": "horologion.communion_wednesday"},
            4: {"text": "Their sound hath gone forth into all the earth...", "ref_key": "horologion.communion_thursday"},
            5: {"text": "O Lord, save Thy people...", "ref_key": "horologion.communion_friday"},
            6: {"text": "Blessed are they whom Thou hast chosen...", "ref_key": "horologion.communion_saturday"}
        }
        
        hymn_data = weekday_hymns.get(day_of_week, weekday_hymns[1])
        return {
            "type": "communion_hymn",
            "text": hymn_data["text"],
            "ref_key": hymn_data["ref_key"]
        }


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:2.2.1.11")
    def resolve_post_communion_hymn(self, context, rubrics=None):
        """
        Post-Communion Hymn: "We Have Seen the True Light" replacement.
        Citation: Dolnytsky Part II (Post-Communion cycle)
        
        RULE: Standard is "We have seen the true light..."
        Exceptions during Feast periods or Pascha.
        """
        paradigm = context.get("paradigm", "")
        season = context.get("season", "ordinary")
        feast_id = context.get("feast_id", None)
        pascha_offset = context.get("pascha_offset", -100)
        title = context.get("title", "").lower()
        
        # PASCHA through Ascension Eve: "Christ is risen" (3x)
        if season == "pascha" or paradigm == "p_pascha" or (0 <= pascha_offset < 39):
            return {
                "type": "post_communion",
                "hymn": "Christ is risen from the dead...",
                "repeat": 3,
                "ref_key": "pentecostarion.post_communion_paschal"
            }
        
        # ASCENSION: "Having beheld the Resurrection"
        if pascha_offset == 39 or "ascension" in title:
            return {
                "type": "post_communion",
                "hymn": "Having beheld the Resurrection of Christ...",
                "ref_key": "pentecostarion.post_communion_ascension"
            }
        
        # NATIVITY through Leavetaking: Kontakion of Nativity
        if "nativity" in title or feast_id == "nativity":
            return {
                "type": "post_communion",
                "hymn": "Today the Virgin gives birth to the Transcendent One...",
                "ref_key": "menaion.nativity.kontakion"
            }
        
        # THEOPHANY through Leavetaking: Troparion of Theophany
        if "theophany" in title or feast_id == "theophany":
            return {
                "type": "post_communion",
                "hymn": "When Thou, O Lord, wast baptized in the Jordan...",
                "ref_key": "menaion.theophany.troparion"
            }
        
        # DEFAULT: "We have seen the true light"
        return {
            "type": "post_communion",
            "hymn": "We have seen the true light, we have received the heavenly Spirit...",
            "ref_key": "horologion.we_have_seen_true_light"
        }


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:3.4.6.3")
    def resolve_vesperal_liturgy_readings(self, context, rubrics=None):
        """
        Phase 7: Resolve Vesperal Liturgy Readings
        Fetches the Old Testament Paremias alongside the Epistle/Gospel.
        """
        title = context.get("title", "").lower()
        feast_id = context.get("feast_id", "")
        
        # Identify vesperal feast
        vesperal_id = None
        date_str = context.get("date", "")
        # Check by fixed date
        if date_str.endswith("-12-24"):
            vesperal_id = "nativity_eve"
        elif date_str.endswith("-01-05"):
            vesperal_id = "theophany_eve"
        # Check by Pascha offset
        elif context.get("pascha_offset") == -3:
            vesperal_id = "holy_thursday"
        elif context.get("pascha_offset") == -1:
            vesperal_id = "holy_saturday"
        # Fallbacks for safety
        elif "nativity" in title: 
            vesperal_id = "nativity_eve"
        elif "theophany" in title or "epiphany" in title: 
            vesperal_id = "theophany_eve"
        elif feast_id == "holy_thursday" or "thursday" in title: 
            vesperal_id = "holy_thursday"
        elif feast_id == "holy_saturday" or "saturday" in title: 
            vesperal_id = "holy_saturday"
        
        if not vesperal_id:
             return {"type": "error", "content": "Could not identify Vesperal Liturgy day from context."}
             
        # Load logic file
        logic = self._load_json(os.path.join(self.base_dir, "json_db", "02f_logic_vesperal_liturgy.json"))
        readings = logic.get("vesperal_readings", {}).get(vesperal_id, {})
        
        if not readings:
             return {"type": "error", "content": f"No readings found for {vesperal_id}."}
             
        components = []
        
        # Add paremias
        for p in readings.get("paremias", []):
             components.append({"type": "reading", "source": "paremia", "ref_key": p})
             
        # Add Epistle Prokeimenon
        components.append({"type": "prokeimenon", "ref_key": readings.get("epistle_prokeimenon")})
        
        # Add Epistle
        components.append({"type": "reading", "source": "epistle", "ref_key": readings.get("epistle")})
        
        # Add Alleluia
        if readings.get("alleluia"):
            components.append({"type": "alleluia", "ref_key": readings.get("alleluia")})
            
        # Add Gospel
        components.append({"type": "reading", "source": "gospel", "ref_key": readings.get("gospel")})
        
        return {
            "type": "sequence",
            "components": components,
            "source_metadata": {"vesperal_id": vesperal_id, "paremia_count": readings.get("count", 0)}
        }


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:2.5.3.5")
    def resolve_liturgy_readings(self, context, rubrics=None):
        """
        Unified Liturgy Readings Resolution.
        Citation: Dolnytsky Part II (Lectionary)
        
        Returns structured reading chain:
        1. Prokeimenon (tone + text)
        2. Epistle (Apostol reference)
        3. Alleluia (tone + verses)
        4. Gospel (Evangelion reference)
        
        Handles multiple readings for Sunday + Saint, etc.
        """
        if context.get("_almanac_used") and "readings" in context:
            return copy.deepcopy(context["readings"])

        day_of_week = context.get("day_of_week", 0)
        from engine.utils.type_utils import parse_rank_integer
        rank = parse_rank_integer(context.get("rank", 5))
        paradigm = context.get("paradigm", "")
        feast_id = context.get("feast_id", None)
        saints = context.get("saints", [])
        tone = context.get("tone", 1)
        moveable_cycle = context.get("moveable_cycle", {})

        # Check if weekday special vigil exception applies: June 24, June 29, August 29 (Dolnytsky §3.10.2)
        month = context.get("month")
        if isinstance(month, str):
            try:
                month = int(month)
            except ValueError:
                month = 0
        day_val = context.get("day")
        is_special_vigil_weekday = (
            day_of_week != 0 and (
                (month == 6 and day_val == 24) or
                (month == 6 and day_val == 29) or
                (month == 8 and day_val == 29)
            )
        )

        l_readings = None
        if rubrics:
            overrides = rubrics.get("variables", {}) or rubrics.get("overrides", {})
            l_readings = overrides.get("liturgy_readings")

        # Normalize l_readings if it exists
        normalized_readings = None
        if l_readings:
            if isinstance(l_readings, list):
                if l_readings and isinstance(l_readings[0], str):
                    s_id = feast_id
                    if not s_id and saints:
                        s_id = saints[0].get("id", "")
                    
                    epistle_key = l_readings[0]
                    gospel_key = l_readings[1] if len(l_readings) > 1 else ""
                    normalized_readings = [{
                        "prokeimenon": {
                            "source": "menaion",
                            "ref_key": f"menaion.{s_id}.prokeimenon" if s_id else ""
                        },
                        "epistle": {
                            "source": "menaion",
                            "ref_key": epistle_key
                        },
                        "alleluia": {
                            "source": "menaion",
                            "ref_key": f"menaion.{s_id}.alleluia" if s_id else ""
                        },
                        "gospel": {
                            "source": "menaion",
                            "ref_key": gospel_key
                        }
                    }]
                else:
                    normalized_readings = l_readings
            elif isinstance(l_readings, str):
                s_id = feast_id
                if not s_id and saints:
                    s_id = saints[0].get("id", "")
                normalized_readings = [{
                    "prokeimenon": {
                        "source": "menaion",
                        "ref_key": f"menaion.{s_id}.prokeimenon" if s_id else ""
                    },
                    "epistle": {
                        "source": "menaion",
                        "ref_key": l_readings
                    },
                    "alleluia": {
                        "source": "menaion",
                        "ref_key": f"menaion.{s_id}.alleluia" if s_id else ""
                    },
                    "gospel": {
                        "source": "menaion",
                        "ref_key": ""
                    }
                }]
            elif isinstance(l_readings, dict) and "readings" in l_readings:
                normalized_readings = l_readings["readings"]
            else:
                normalized_readings = l_readings

        # Dolnytsky §3.10.2: On Sunday with a Vigil/Polyeleos saint (rank 2 or 3), we combine them.
        # On weekdays or other Sundays (e.g. Triodion Sundays), we return the override directly.
        if day_of_week != 0:
            if normalized_readings:
                return {"type": "liturgy_readings", "readings": normalized_readings}
            elif is_special_vigil_weekday:
                # Suppress daily readings on weekdays, saint readings only
                result = {
                    "type": "liturgy_readings",
                    "readings": []
                }
                if saints:
                    saint_id = saints[0].get("id", "saint")
                    result["readings"].append({
                        "prokeimenon": {
                            "source": "menaion",
                            "ref_key": f"menaion.{saint_id}.prokeimenon"
                        },
                        "epistle": {
                            "source": "menaion",
                            "ref_key": f"menaion.{saint_id}.epistle"
                        },
                        "alleluia": {
                            "source": "menaion",
                            "ref_key": f"menaion.{saint_id}.alleluia"
                        },
                        "gospel": {
                            "source": "menaion",
                            "ref_key": f"menaion.{saint_id}.gospel"
                        }
                    })
                return result
        else: # Sunday (day_of_week == 0)
            if normalized_readings and rank > 3:
                return {"type": "liturgy_readings", "readings": normalized_readings}

        result = {
            "type": "liturgy_readings",
            "readings": []
        }
        
        # GREAT FEAST: Feast readings only
        if rank == 1 or paradigm in ["p_feast_lord", "p_feast_theotokos"]:
            if normalized_readings:
                return {"type": "liturgy_readings", "readings": normalized_readings}
            result["readings"].append({
                "prokeimenon": {
                    "source": "feast",
                    "ref_key": f"menaion.{feast_id}.prokeimenon" if feast_id else "feast.prokeimenon"
                },
                "epistle": {
                    "source": "feast",
                    "ref_key": f"menaion.{feast_id}.epistle" if feast_id else "feast.epistle"
                },
                "alleluia": {
                    "source": "feast",
                    "ref_key": f"menaion.{feast_id}.alleluia" if feast_id else "feast.alleluia"
                },
                "gospel": {
                    "source": "feast",
                    "ref_key": f"menaion.{feast_id}.gospel" if feast_id else "feast.gospel"
                }
            })
            return result
        
        # SUNDAY: Resurrectional readings
        if day_of_week == 0:
            # Primary: Octoechos readings
            result["readings"].append({
                "prokeimenon": {
                    "source": "octoechos",
                    "tone": tone,
                    "ref_key": f"octoechos.prokeimenon.tone_{tone}"
                },
                "epistle": {
                    "source": "apostol",
                    "ref_key": moveable_cycle.get("epistle", "apostol.sunday")
                },
                "alleluia": {
                    "source": "octoechos",
                    "tone": tone,
                    "ref_key": f"octoechos.alleluia.tone_{tone}"
                },
                "gospel": {
                    "source": "evangelion",
                    "ref_key": moveable_cycle.get("gospel", "evangelion.sunday")
                }
            })
            
            # Secondary: Saint of the day (if Polyeleos or higher, R <= 3)
            if normalized_readings:
                result["readings"].extend(normalized_readings)
            elif saints and rank <= 3:
                saint_id = saints[0].get("id", "saint")
                result["readings"].append({
                    "prokeimenon": {
                        "source": "menaion",
                        "ref_key": f"menaion.{saint_id}.prokeimenon"
                    },
                    "epistle": {
                        "source": "menaion",
                        "ref_key": f"menaion.{saint_id}.epistle"
                    },
                    "alleluia": {
                        "source": "menaion",
                        "ref_key": f"menaion.{saint_id}.alleluia"
                    },
                    "gospel": {
                        "source": "menaion",
                        "ref_key": f"menaion.{saint_id}.gospel"
                    }
                })
            
            return result
        
        # WEEKDAY
        if day_of_week != 0:
            # Weekday lectionary first
            p_res = self.resolve_prokeimenon(context)
            p_tone = p_res.get("tone", 1)
            # Dynamic sequential readings calculation
            ep_text, gosp_text = None, None
            weeks_after_pentecost = context.get("weeks_after_pentecost")
            if weeks_after_pentecost is not None:
                lectionary = {
                    1: {
                        1: ("Ephesians 5:9-19", "Matthew 18:10-20"),
                        2: ("Romans 1:1-7, 13-17", "Matthew 4:25-5:13"),
                        3: ("Romans 1:18-27", "Matthew 5:20-26"),
                        4: ("Romans 1:28-2:9", "Matthew 5:27-32"),
                        5: ("Romans 2:14-29", "Matthew 5:33-41"),
                        6: ("Romans 1:7-12", "Matthew 5:42-48"),
                    },
                    2: {
                        1: ("Romans 2:28-3:18", "Matthew 6:31-34; 7:9-11"),
                        2: ("Romans 4:4-12", "Matthew 7:15-21"),
                        3: ("Romans 4:13-25", "Matthew 7:21-23"),
                        4: ("Romans 5:1-10", "Matthew 8:23-27"),
                        5: ("Romans 5:17-6:2", "Matthew 9:14-17"),
                        6: ("Romans 3:19-26", "Matthew 7:1-8"),
                    },
                    3: {
                        1: ("Romans 7:1-13", "Matthew 9:36-10:8"),
                        2: ("Romans 7:14-8:2", "Matthew 10:9-15"),
                        3: ("Romans 8:2-13", "Matthew 10:16-22"),
                        4: ("Romans 8:22-27", "Matthew 10:23-31"),
                        5: ("Romans 9:6-19", "Matthew 10:32-40; 11:1"),
                        6: ("Romans 5:1-10", "Matthew 6:22-33"),
                    },
                    4: {
                        1: ("Romans 9:18-33", "Matthew 11:2-15"),
                        2: ("Romans 10:11-11:2", "Matthew 11:16-20"),
                        3: ("Romans 11:2-12", "Matthew 11:20-26"),
                        4: ("Romans 11:13-24", "Matthew 11:27-30"),
                        5: ("Romans 11:25-36", "Matthew 12:1-8"),
                        6: ("Romans 6:11-17", "Matthew 8:14-23"),
                    },
                    5: {
                        1: ("Romans 12:4-15", "Matthew 12:9-13"),
                        2: ("Romans 12:15-21", "Matthew 12:14-16, 22-30"),
                        3: ("Romans 14:9-18", "Matthew 12:31-37"),
                        4: ("Romans 15:1-7", "Matthew 12:38-45"),
                        5: ("Romans 15:17-29", "Matthew 12:46-13:9"),
                        6: ("Romans 8:14-21", "Matthew 9:9-13"),
                    }
                }
                if weeks_after_pentecost in lectionary and day_of_week in lectionary[weeks_after_pentecost]:
                    ep_text, gosp_text = lectionary[weeks_after_pentecost][day_of_week]

            # Eucharist Afterfeast/Apodosis check (pascha_offset 60 to 67)
            offset = context.get("pascha_offset")
            if offset is not None and 60 <= offset <= 67:
                p_source = "feast"
                p_ref = "menaion.eucharist.prokeimenon"
                p_tone_val = 6
                p_text = "O Lord, save Your people and bless Your inheritance"
                a_source = "feast"
                a_ref = "menaion.eucharist.alleluia"
                a_tone_val = 6
                a_verses = [
                    "He who eats My flesh and drinks My blood abides in Me, and I in him",
                    "The bread that I will give is My flesh for the life of the world"
                ]
            else:
                p_source = "horologion"
                p_ref = f"horologion.prokeimenon.day_{day_of_week}"
                p_tone_val = p_tone
                p_text = None
                a_source = "horologion"
                a_ref = f"horologion.alleluia.day_{day_of_week}"
                a_tone_val = p_tone
                a_verses = None

            result["readings"].append({
                "prokeimenon": {
                    "source": p_source,
                    "ref_key": p_ref,
                    "tone": p_tone_val,
                    "text": p_text
                },
                "epistle": {
                    "source": "apostol",
                    "ref_key": moveable_cycle.get("epistle", "apostol.weekday"),
                    "text": ep_text
                },
                "alleluia": {
                    "source": a_source,
                    "ref_key": a_ref,
                    "tone": a_tone_val,
                    "verses": a_verses
                },
                "gospel": {
                    "source": "evangelion",
                    "ref_key": moveable_cycle.get("gospel", "evangelion.weekday"),
                    "text": gosp_text
                }
            })

            # Saint's readings second
            if saints and rank <= 3:
                saint_id = saints[0].get("id", "saint")
                if saint_id == "jun_11.bartholomew_barnabas":
                    result["readings"].append({
                        "prokeimenon": {
                            "source": "menaion",
                            "ref_key": f"menaion.{saint_id}.prokeimenon",
                            "tone": 8,
                            "text": "Their proclamation has gone out into all the earth, and their words to the ends of the world"
                        },
                        "epistle": {
                            "source": "menaion",
                            "ref_key": f"menaion.{saint_id}.epistle",
                            "text": "Acts 11:19-26, 29-30"
                        },
                        "alleluia": {
                            "source": "menaion",
                            "ref_key": f"menaion.{saint_id}.alleluia",
                            "tone": 1,
                            "verses": [
                                "The heavens shall confess Your wonders, O Lord, and Your truth in the congregation of the Saints"
                            ]
                        },
                        "gospel": {
                            "source": "menaion",
                            "ref_key": f"menaion.{saint_id}.gospel",
                            "text": "Luke 10:16-21"
                        }
                    })
                else:
                    result["readings"].append({
                        "prokeimenon": {
                            "source": "menaion",
                            "ref_key": f"menaion.{saint_id}.prokeimenon"
                        },
                        "epistle": {
                            "source": "menaion",
                            "ref_key": f"menaion.{saint_id}.epistle"
                        },
                        "alleluia": {
                            "source": "menaion",
                            "ref_key": f"menaion.{saint_id}.alleluia"
                        },
                        "gospel": {
                            "source": "menaion",
                            "ref_key": f"menaion.{saint_id}.gospel"
                        }
                    })
        
        return result

    # PHASE 3: ADVANCED LOGIC EXPANSION


    def resolve_opening_blessing(self, context, rubrics):
        # S01: Vigil Opening
        if context.get("is_vigil") and context.get("day_of_week") == 0:
             return {"type": "fixed_ref", "ref_key": "liturgikon.glory_to_the_holy_trinity"}
        return {"type": "fixed_ref", "ref_key": "liturgikon.blessed_is_our_god"}


    def resolve_anaphora_type(self, context, rubrics):
        # II.6: Anaphora (Basil vs Chrysostom)
        season = context.get("season_id")
        t_period = context.get("triodion_period", "")
        
        if season == "triodion" and t_period == "lent_sunday":
             # Sundays 1-5 of Lent
             return {"type": "basil"}
             
        # Also Liturgy of St Basil on Jan 1, Great Thursday, Great Saturday
        if context.get("title") in ["Circumcision", "Great Thursday", "Great Saturday"]:
             return {"type": "basil"}
             
        return {"type": "chrysostom"}


    def resolve_koinonikon_stack(self, context, rubrics):
        # II.8: Koinonikon Stack
        # Base: Sunday
        stack = []
        day = context.get("day_of_week")
        rank = self.calculate_rank(context)
        
        # 1. Primary
        if day == 0:
            stack.append({"type": "fixed_ref", "ref_key": "horologion.koinonikon_praise_the_lord"})
        else:
            # Weekday mapping logic (reusing existing map logic)
            stack.append(self.resolve_communion_hymn(context, rubrics))
            
        # 2. Secondary (Saint/Feast)
        if rank >= 3:
             stack.append({"type": "fixed_ref", "ref_key": "horologion.koinonikon_in_everlasting_remembrance"})
             
        return {"type": "koinonikon_stack", "components": stack}


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:1.2.1.4")
    def resolve_reading_ot(self, context, rubrics):
        """
        Resolve Old Testament reading (paremia/prophecy).
        Citation: Dolnytsky Part I Lines 26-28 (Prokeimenon and Readings)
        """
        # Fetch from menaion or triodion based on context
        season = context.get("season_id", "menaion")
        feast_id = context.get("feast_id", "")
        
        if season == "triodion":
            ref_key = f"triodion.{context.get('triodion_period', 'lent')}.paremia"
        else:
            ref_key = f"menaion.{feast_id}.paremia" if feast_id else "common.paremia"
            
        return {
            "type": "fixed_ref",
            "ref_key": ref_key,
            "reading_type": "old_testament"
        }


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:1.2.1.4")
    def resolve_reading_epistle(self, context, rubrics):
        """
        Resolve Epistle reading.
        Citation: Dolnytsky Part I Lines 26-28
        """
        season = context.get("season_id", "menaion")
        feast_id = context.get("feast_id", "")
        day_of_week = context.get("day_of_week", 0)
        
        # Sunday has movable epistle
        if day_of_week == 0:
            tone = context.get("tone", 1)
            ref_key = f"apostol.sunday.tone_{tone}"
        elif season == "triodion":
            ref_key = f"triodion.{context.get('triodion_period', 'lent')}.epistle"
        elif feast_id:
            ref_key = f"menaion.{feast_id}.epistle"
        else:
            ref_key = f"apostol.weekday.{day_of_week}"
            
        return {
            "type": "fixed_ref",
            "ref_key": ref_key,
            "reading_type": "epistle"
        }


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:1.2.1.4")
    def resolve_reading_gospel(self, context, rubrics):
        """
        Resolve Gospel reading.
        Citation: Dolnytsky Part I Lines 26-28
        """
        season = context.get("season_id", "menaion")
        feast_id = context.get("feast_id", "")
        day_of_week = context.get("day_of_week", 0)
        
        # Sunday Matins: Eothinon Gospel
        if day_of_week == 0 and context.get("service") == "matins":
            eothinon = context.get("eothinon_number", 1)
            ref_key = f"horologion.eothinon_{eothinon:02d}"
        elif season == "triodion":
            ref_key = f"triodion.{context.get('triodion_period', 'lent')}.gospel"
        elif feast_id:
            ref_key = f"menaion.{feast_id}.gospel"
        else:
            ref_key = f"gospel.weekday.{day_of_week}"
            
        return {
            "type": "fixed_ref",
            "ref_key": ref_key,
            "reading_type": "gospel"
        }

    # PHASE 12: ALL-NIGHT VIGIL (EXTREME)


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:2.2.3.8,L192")
    def resolve_beatitudes(self, context):
        """
        Gate: Beatitudes (Third Antiphon)
        """
        offset = context.get("pascha_offset")
        from engine.utils.type_utils import parse_rank_integer
        rank = parse_rank_integer(context.get('rank', 5))
        
        if offset is not None and 60 <= offset <= 67:
            if rank <= 3:
                return {
                    "type": "beatitudes",
                    "stichera": [
                        {"source": "triodion", "count": 4},
                        {"source": "menaion", "count": 4}
                    ],
                    "note": "Feast - 4; Saint - 4"
                }
            else:
                return {
                    "type": "beatitudes",
                    "stichera": [
                        {"source": "triodion", "count": 6}
                    ],
                    "note": "Feast - 6"
                }

        beat_dist = context.get("beatitudes_distribution")
        if beat_dist:
            stichera = []
            for s in beat_dist.get("distribution", []):
                stichera.append({
                    "source": s.get("source"),
                    "count": s.get("count", s.get("qty", 0))
                })
            return {
                "type": "beatitudes",
                "stichera": stichera,
                "note": beat_dist.get("note", "Combined Beatitudes")
            }

        day_of_week = context.get('day_of_week', 0)
        from engine.utils.type_utils import parse_rank_integer
        rank = parse_rank_integer(context.get('rank', 5))
        
        if day_of_week == 0:
            return {"type": "beatitudes", "stichera": [{"source": "octoechos", "count": 4}], "note": "Sunday Beatitudes"}
            
        if rank <= 3:
            return {"type": "beatitudes", "stichera": [{"source": "menaion", "count": 4}], "note": "Festal Beatitudes"}
            
        return {"type": "third_antiphon", "note": "Usual Third Antiphon without stichera"}


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:2.5.3.5")
    def resolve_liturgy_alleluia(self, context, rubrics=None):
        """
        Resolve Liturgy Alleluia tone and verses based on readings.
        Citation: Dolnytsky Part II (Lectionary)
        """
        readings_res = self.resolve_liturgy_readings(context, rubrics)
        if readings_res and readings_res.get("readings"):
            first_reading = readings_res["readings"][0]
            return first_reading.get("alleluia")
        
        # Fallback: Tone of the week
        tone = context.get("tone", 1)
        return {
            "source": "octoechos",
            "tone": tone,
            "ref_key": f"octoechos.alleluia.tone_{tone}"
        }
