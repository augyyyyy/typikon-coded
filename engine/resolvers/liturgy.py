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
        collision_override = context.get("variables", {}).get("liturgy_hymns_override")
        if collision_override:
            return {
                "type": "hymn_stack",
                "components": collision_override
            }

        day = context.get("day_of_week", 1)
        temple_type = context.get("temple_type", "saint") # 'saint' or 'theotokos'
        
        template_key = "weekday_standard"
        if context.get("dolnytsky_rank") == "LORD" or context.get("paradigm") == "p_feast_lord":
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


    @liturgical_source(dolnytsky="Final_Dolnytsky_part2_general_rubrics.txt:L533")
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


    @liturgical_source(dolnytsky="Final_footnotes.txt:L807")
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


    @liturgical_source(dolnytsky="Final_Dolnytsky_part2_general_rubrics.txt:L207")
    def resolve_communion_hymn(self, context, rubrics=None):
        """
        Communion Hymn (Причастен/Koinonikon).
        Citation: Dolnytsky Part II (Communion cycle)
        
        RULE: Different hymns for different days and occasions.
        Sunday always: "Praise the Lord from the heavens"
        Great Feast: Proper of feast
        Weekday: Tone-appropriate or proper of day
        """
        day_of_week = context.get("day_of_week", 0)
        from engine.utils.type_utils import parse_rank_integer
        rank = parse_rank_integer(context.get("rank", 5))
        paradigm = context.get("paradigm", "")
        feast_id = context.get("feast_id", None)
        tone = context.get("tone", 1)
        season = context.get("season", "ordinary")
        liturgy_type = context.get("liturgy_type", "chrysostom")
        
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
            3: {"text": "The Lord hath chosen Sion...", "ref_key": "horologion.communion_wednesday"},
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


    @liturgical_source(dolnytsky="Final_Dolnytsky_part2_general_rubrics.txt:L129")
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


    @liturgical_source(dolnytsky="Final_Dolnytsky_part3_menaion.txt:L760")
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


    @liturgical_source(dolnytsky="Final_Dolnytsky_part2_general_rubrics.txt:L207")
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
        # Check for explicit override in variables
        if rubrics:
            overrides = rubrics.get("variables", {}) or rubrics.get("overrides", {})
            l_readings = overrides.get("liturgy_readings")
            if l_readings:
                if isinstance(l_readings, list):
                    if l_readings and isinstance(l_readings[0], str):
                        feast_id = context.get("feast_id", "")
                        if not feast_id and context.get("saints"):
                            feast_id = context["saints"][0].get("id", "")
                        
                        epistle_key = l_readings[0]
                        gospel_key = l_readings[1] if len(l_readings) > 1 else ""
                        
                        structured_reading = {
                            "prokeimenon": {
                                "source": "menaion",
                                "ref_key": f"menaion.{feast_id}.prokeimenon" if feast_id else ""
                            },
                            "epistle": {
                                "source": "menaion",
                                "ref_key": epistle_key
                            },
                            "alleluia": {
                                "source": "menaion",
                                "ref_key": f"menaion.{feast_id}.alleluia" if feast_id else ""
                            },
                            "gospel": {
                                "source": "menaion",
                                "ref_key": gospel_key
                            }
                        }
                        return {"type": "liturgy_readings", "readings": [structured_reading]}
                    return {"type": "liturgy_readings", "readings": l_readings}
                elif isinstance(l_readings, str):
                    feast_id = context.get("feast_id", "")
                    if not feast_id and context.get("saints"):
                        feast_id = context["saints"][0].get("id", "")
                    structured_reading = {
                        "prokeimenon": {
                            "source": "menaion",
                            "ref_key": f"menaion.{feast_id}.prokeimenon" if feast_id else ""
                        },
                        "epistle": {
                            "source": "menaion",
                            "ref_key": l_readings
                        },
                        "alleluia": {
                            "source": "menaion",
                            "ref_key": f"menaion.{feast_id}.alleluia" if feast_id else ""
                        },
                        "gospel": {
                            "source": "menaion",
                            "ref_key": ""
                        }
                    }
                    return {"type": "liturgy_readings", "readings": [structured_reading]}
                return l_readings

        day_of_week = context.get("day_of_week", 0)
        from engine.utils.type_utils import parse_rank_integer
        rank = parse_rank_integer(context.get("rank", 5))
        paradigm = context.get("paradigm", "")
        feast_id = context.get("feast_id", None)
        saints = context.get("saints", [])
        tone = context.get("tone", 1)
        moveable_cycle = context.get("moveable_cycle", {})
        
        result = {
            "type": "liturgy_readings",
            "readings": []
        }
        
        # GREAT FEAST: Feast readings only
        if rank == 1 or paradigm in ["p_feast_lord", "p_feast_theotokos"]:
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
            
            # Secondary: Saint of the day (if Polyeleos or higher)
            if saints and rank <= 4:
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
        
        # WEEKDAY with Saint
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
        else:
            # Weekday lectionary
            result["readings"].append({
                "prokeimenon": {
                    "source": "horologion",
                    "ref_key": f"horologion.prokeimenon.day_{day_of_week}"
                },
                "epistle": {
                    "source": "apostol",
                    "ref_key": moveable_cycle.get("epistle", "apostol.weekday")
                },
                "alleluia": {
                    "source": "horologion",
                    "ref_key": f"horologion.alleluia.day_{day_of_week}"
                },
                "gospel": {
                    "source": "evangelion",
                    "ref_key": moveable_cycle.get("gospel", "evangelion.weekday")
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


    @liturgical_source(dolnytsky="Final_Dolnytsky_part1_structure.txt:L26-28")
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


    @liturgical_source(dolnytsky="Final_Dolnytsky_part1_structure.txt:L26-28")
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


    @liturgical_source(dolnytsky="Final_Dolnytsky_part1_structure.txt:L26-28")
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


    @liturgical_source(dolnytsky="Final_Dolnytsky_part2_general_rubrics.txt:L121,L192")
    def resolve_beatitudes(self, context):
        """
        Gate: Beatitudes (Third Antiphon)
        """
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


    @liturgical_source(dolnytsky="Final_Dolnytsky_part2_general_rubrics.txt:L207")
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
