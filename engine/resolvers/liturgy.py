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

    def _format_scripture_key(self, key: str) -> str:
        if not key:
            return ""
        books = [
            ('1_corinthians', '1 Corinthians'), ('2_corinthians', '2 Corinthians'),
            ('1_thessalonians', '1 Thessalonians'), ('2_thessalonians', '2 Thessalonians'),
            ('1_timothy', '1 Timothy'), ('2_timothy', '2 Timothy'),
            ('1_peter', '1 Peter'), ('2_peter', '2 Peter'),
            ('1_john', '1 John'), ('2_john', '2 John'), ('3_john', '3 John'),
            ('matthew', 'Matthew'), ('mark', 'Mark'), ('luke', 'Luke'), ('john', 'John'),
            ('acts', 'Acts'), ('romans', 'Romans'), ('galatians', 'Galatians'),
            ('ephesians', 'Ephesians'), ('philippians', 'Philippians'), ('colossians', 'Colossians'),
            ('titus', 'Titus'), ('philemon', 'Philemon'), ('hebrews', 'Hebrews'),
            ('james', 'James'), ('jude', 'Jude'), ('revelation', 'Revelation'),
            ('genesis', 'Genesis'), ('exodus', 'Exodus'), ('leviticus', 'Leviticus'),
            ('numbers', 'Numbers'), ('deuteronomy', 'Deuteronomy'), ('isaiah', 'Isaiah'),
            ('jeremiah', 'Jeremiah'), ('ezekiel', 'Ezekiel'), ('daniel', 'Daniel'),
            ('proverbs', 'Proverbs'), ('job', 'Job'), ('jonah', 'Jonah'),
            ('wisdom_of_solomon', 'Wisdom of Solomon'), ('wisdom', 'Wisdom of Solomon'),
            ('zechariah', 'Zechariah'), ('micah', 'Micah'), ('baruch', 'Baruch')
        ]
        k_lower = str(key).lower().replace('.', '_')
        for b_key, b_name in books:
            if k_lower.startswith(b_key + '_'):
                rem = k_lower[len(b_key) + 1:]
                parts = rem.split('_')
                if all(p.isdigit() for p in parts):
                    if len(parts) == 6 and int(parts[3]) < int(parts[2]):
                        return f"{b_name} {parts[0]}:{parts[1]}–{parts[2]}; {parts[3]}:{parts[4]}–{parts[5]}"
                    elif len(parts) >= 3 and (len(parts) - 1) % 2 == 0:
                        spans = [f"{parts[i]}–{parts[i+1]}" for i in range(1, len(parts), 2)]
                        return f"{b_name} {parts[0]}:" + ", ".join(spans)
                    elif len(parts) == 4:
                        if int(parts[1]) < int(parts[2]) < int(parts[3]):
                            return f"{b_name} {parts[0]}:{parts[1]}–{parts[2]}, {parts[3]}"
                        return f"{b_name} {parts[0]}:{parts[1]}–{parts[2]}:{parts[3]}"
                    elif len(parts) == 2:
                        return f"{b_name} {parts[0]}:{parts[1]}"
                    elif len(parts) == 1:
                        return f"{b_name} {parts[0]}"
        return ""

    def resolve_antiphon_type(self, context):
        """
        Determines the Antiphon set based on the Paradigm.
        """
        paradigm = self.identify_paradigm(context)
        
        if paradigm == "p_feast_lord":
            return "antiphons_festal"
        elif paradigm in ("p_feast_theotokos", "p1_sunday_resurrection"):
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
        season = context.get("season", "")
        title = context.get("title", "").lower()
        feast_id = context.get("feast_id", None)
        
        is_forefeast = context.get("is_forefeast", False)
        # P_Feast_Lord -> Special Isodikon (Feast & Afterfeast, but NOT Forefeast)
        if not is_forefeast and (
            context.get("variables", {}).get("liturgy_entrance") == "exaltation_entrance_verse"
            or season == "Exaltation_Cross"
            or "exaltation" in title
            or feast_id in ("exaltation_cross", "exaltation")
        ):
            return {
                "type": "isodikon",
                "verse": "Exalt the Lord our God, and bow down at His footstool, for it is holy.",
                "refrain": "Save us, O Son of God, crucified in the flesh, who sing to You: Alleluia.",
                "ref_key": "menaion.exaltation_cross.entrance_verse"
            }

        day_of_week = context.get("day_of_week", 0)
        from engine.utils.type_utils import parse_rank_integer
        rank = parse_rank_integer(context.get("rank", 5))
        dolnytsky_rank = context.get("dolnytsky_rank", "")

        # Sunday (Resurrection takes precedence unless Rank 1 Great Feast of the Lord)
        if day_of_week == 0 and not (rank == 1 and dolnytsky_rank == "LORD"):
            return {
                "verse": "Come, let us worship and bow down before Christ.",
                "refrain": "O Son of God, risen from the dead, save us who sing to You: Alleluia."
            }

        if paradigm == "p_feast_lord":
            return {
                "verse": "Blessed is He who comes in the name of the Lord. God is the Lord and has appeared to us.",
                "refrain": "O Son of God, baptized in the Jordan, save us who sing to You: Alleluia."
            }

        is_forefeast_cur = bool(context.get("is_forefeast") or context.get("period") == "forefeast")
        if not is_forefeast_cur and (dolnytsky_rank in ("THEOTOKOS", "MOG") or context.get("feast_level") == "theotokos"):
            return {
                "verse": "Come, let us worship and bow down before Christ.",
                "refrain": "Through the prayers of the Theotokos, save us who sing to You: Alleluia."
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
        pascha_off = context.get("pascha_offset")
        if pascha_off is not None and 0 <= pascha_off <= 6:
            return {
                "type": "generator",
                "generator_method": "generate_antiphons",
                "args": { "strategy": "festal_antiphons" }
            }

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
                    is_theotokos_feast = (
                        context.get("feast_level") == "theotokos"
                        or context.get("dolnytsky_rank") in ("THEOTOKOS", "MOG")
                    )
                    if rank <= req_rank and not is_theotokos_feast: 
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
            
        if not collision_override and not context.get("is_temple_feast"):
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
                    {"type": "glory"},
                    {"type": "kontakion", "source": "menaion_saint"},
                    {"type": "both_now"},
                    {"type": "theotokion", "source": "steadfast_protectress"}
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
        
        is_vigil_polyeleos_early = (
            rank_numeric <= 2 or
            context.get("is_vigil") or
            context.get("has_polyeleos") or
            (context.get("doxology_type") == "great_doxology" and rank_numeric <= 3) or
            context.get("rank") in ["rank_vigil_saint", "rank_polyeleos_saint", "rank_vigil", "rank_polyeleos", "rank_doxology"] or
            (rubrics and rubrics.get("variables", {}).get("rank") in ["rank_vigil_saint", "rank_polyeleos_saint", "rank_vigil", "rank_polyeleos", "rank_doxology"])
        )
        
        if day in (3, 5) and not is_festal_day and not is_vigil_polyeleos_early:
            final_components = [
                {"type": "troparion", "source": "cross"}
            ]
            if temple_type == "theotokos":
                final_components.append({"type": "troparion", "source": "temple"})
            
            # Commemorate saint if rank <= 4, explicitly overridden, or calendar saint is present
            has_trop_saint = bool(context.get("saints"))
            if rank_numeric <= 4 or context.get("combined_service_override") or has_trop_saint:
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
            context.get("is_afterfeast") or
            context.get("is_forefeast") or
            context.get("period") in ["forefeast", "afterfeast", "apodosis"] or
            context.get("triodion_period") in ["forefeast", "afterfeast", "apodosis"] or
            context.get("dolnytsky_rank") in ["forefeast", "afterfeast", "apodosis"]
        )
        d_title = context.get("dolnytsky_title", "").lower()
        d_commem = context.get("dolnytsky_commemoration", "").lower()
        if any(x in d_title or x in d_commem for x in ["forefeast", "afterfeast", "apodosis"]):
            is_fore_after = True

        is_sunday = (day == 0)
        saints = context.get("saints", [])
        actual_saints = [
            s for s in saints
            if not any(w in s.get("name", "").lower() for w in ["forefeast", "afterfeast", "prefeast", "postfeast", "apodosis", "meeting", "encounter", "leave-taking"])
        ]

        is_real_calendar_context = bool(
            saints
            or context.get("dolnytsky_rank_code")
            or context.get("year")
            or context.get("date")
        )

        if is_sunday and is_fore_after and is_real_calendar_context:
            has_sunday_liturgy_saint = bool(
                actual_saints and (
                    rank_numeric <= 3
                    or context.get("dolnytsky_rank_code") in ("[GT DOX]", "[POL]", "[VIGIL]")
                    or any(
                        isinstance(s, dict) and (
                            parse_rank_integer(s.get("rank", 5)) <= 3
                            or s.get("rank_code") in ("[GT DOX]", "[POL]", "[VIGIL]")
                        )
                        for s in saints
                    )
                )
            )
            final_components = [
                {"type": "troparion", "source": "resurrection_tone"},
                {"type": "troparion", "source": "feast"}
            ]
            if temple_type == "theotokos":
                final_components.append({"type": "troparion", "source": "temple"})
            if has_sunday_liturgy_saint:
                final_components.append({"type": "troparion", "source": "menaion_saint"})
            
            if has_sunday_liturgy_saint:
                final_components.append({"type": "kontakion", "source": "resurrection_tone"})
                if temple_type == "theotokos":
                    final_components.append({"type": "kontakion", "source": "temple"})
                final_components.append({"type": "kontakion", "source": "menaion_saint", "glory": True})
                final_components.append({"type": "kontakion", "source": "feast", "both_now": True})
            else:
                if temple_type == "theotokos":
                    final_components.append({"type": "kontakion", "source": "resurrection_tone"})
                    final_components.append({"type": "kontakion", "source": "temple", "glory": True})
                else:
                    final_components.append({"type": "kontakion", "source": "resurrection_tone", "glory": True})
                final_components.append({"type": "kontakion", "source": "feast", "both_now": True})
            return {
                "type": "hymn_stack",
                "components": final_components
            }

        if not is_sunday and is_fore_after and is_real_calendar_context:
            final_components = [
                {"type": "troparion", "source": "feast"}
            ]
            if len(actual_saints) >= 2:
                final_components.append({"type": "troparion", "source": "menaion_saint_1"})
                final_components.append({"type": "troparion", "source": "menaion_saint_2"})
                final_components.append({"type": "kontakion", "source": "menaion_saint_1"})
                final_components.append({"type": "kontakion", "source": "menaion_saint_2", "glory": True})
                final_components.append({"type": "kontakion", "source": "feast", "both_now": True})
            elif actual_saints:
                final_components.append({"type": "troparion", "source": "menaion_saint"})
                final_components.append({"type": "kontakion", "source": "menaion_saint", "glory": True})
                final_components.append({"type": "kontakion", "source": "feast", "both_now": True})
            else:
                final_components.append({"type": "kontakion", "source": "feast", "glory_both_now": True})
            return {
                "type": "hymn_stack",
                "components": final_components
            }

        template_key = "weekday_standard"
        is_great_lord_feast = (
            context.get("dolnytsky_rank") == "LORD" or 
            context.get("paradigm") == "p_feast_lord" or 
            context.get("feast_level") == "lord"
        )
        if is_great_lord_feast and not is_fore_after:
            template_key = "festal_only"
        elif (
            (context.get("dolnytsky_rank") in ["THEOTOKOS", "MOG"] or 
             context.get("paradigm") in ["p_feast_theotokos"] or 
             context.get("feast_level") in ["theotokos"])
            and not (day == 0 and rank_numeric > 1)
            and not is_fore_after
        ):
            template_key = "festal_only"
        elif day == 0:
            if context.get("is_temple_feast") and temple_type == "theotokos":
                template_key = "sunday_patronal_theotokos_temple"
            elif temple_type == "saint" and (context.get("is_temple_feast") or not is_real_calendar_context):
                template_key = "sunday_patronal_saint_temple"
            elif temple_type == "lord":
                template_key = "sunday_lord_temple"
            elif temple_type == "theotokos":
                template_key = "sunday_theotokos_temple"
            else:
                template_key = "sunday_saint_temple"
        else:
            is_vigil_polyeleos = (
                rank_numeric <= 2 or
                context.get("is_vigil") or
                context.get("has_polyeleos") or
                (context.get("doxology_type") == "great_doxology" and rank_numeric <= 3) or
                context.get("rank") in ["rank_vigil_saint", "rank_polyeleos_saint", "rank_vigil", "rank_polyeleos"] or
                (rubrics and rubrics.get("variables", {}).get("rank") in ["rank_vigil_saint", "rank_polyeleos_saint", "rank_vigil", "rank_polyeleos"])
            )
            if is_vigil_polyeleos:
                if context.get("is_temple_feast") and temple_type == "saint":
                    template_key = "weekday_patronal_saint_temple"
                elif temple_type == "lord":
                    template_key = "weekday_vigil_lord_temple"
                elif temple_type == "theotokos":
                    template_key = "weekday_vigil_theotokos_temple"
                elif temple_type == "saint":
                    template_key = "weekday_vigil_saint_temple"
                else:
                    template_key = "weekday_vigil_standard"
            else:
                if temple_type == "lord":
                    template_key = "weekday_lord_temple"
                elif temple_type == "theotokos":
                    template_key = "weekday_theotokos_temple"
                elif temple_type == "saint":
                    template_key = "weekday_saint_temple"
                else:
                    template_key = "weekday_standard"
            
        template = self.liturgy_logic.get("hymn_ordering_templates", {}).get(template_key, {})
        raw_order = template.get("order", [])
        
        # Filter components based on conditions
        final_components = []
        is_afterfeast = context.get("is_afterfeast", False)
        has_sunday_liturgy_saint = (
            rank_numeric <= 3
            or context.get("dolnytsky_rank_code") in ("[GT DOX]", "[POL]", "[VIGIL]")
            or any(isinstance(s, dict) and s.get("rank_code") in ("[GT DOX]", "[POL]", "[VIGIL]") for s in saints)
        )
        suppress_sunday_saint_hymns = (day == 0 and is_real_calendar_context and not has_sunday_liturgy_saint)
        
        for comp in raw_order:
            # Check conditions if they exist
            if "condition" in comp:
                 cond = comp["condition"]
                 if "not is_afterfeast" in cond and is_afterfeast:
                      continue
                 if "temple_type != 'theotokos'" in cond and temple_type == "theotokos":
                      continue
            if suppress_sunday_saint_hymns and comp.get("source") == "menaion_saint":
                continue
            comp_copy = dict(comp)
            if suppress_sunday_saint_hymns and comp_copy.get("type") == "kontakion" and comp_copy.get("source") == "resurrection_tone":
                comp_copy["glory"] = True
            final_components.append(comp_copy)
        
        return {
            "type": "hymn_stack",
            "components": final_components
        }


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:2.20,L1767-1774")
    def resolve_trisagion_type(self, context, rubrics=None):
        """
        Trisagion Type Selection for Liturgy.
        Citation: Dolnytsky Part II (Trisagion replacements)
        
        RULES:
        - "As many as have been baptized" replaces Trisagion on:
          - Nativity (Dec 25), Theophany (Jan 6), Lazarus Saturday (pascha_offset -8)
          - Holy Saturday (pascha_offset -1), Pascha and Bright Week (pascha_offset 0 to 6)
          - Pentecost Sunday (pascha_offset 49)
          - (Palm Sunday does NOT have this replacement)
        - "Before Thy Cross we bow down" replaces on:
          - Exaltation of Cross (Sept 14)
          - Third Sunday of Lent (Veneration of the Cross, pascha_offset -28)
          - Aug 1 (Procession of Cross)
        """
        title = context.get("title", "").lower()
        feast_id = context.get("feast_id", "")
        paradigm = context.get("paradigm", "")
        pascha_offset = context.get("pascha_offset", -100)
        date = context.get("date", "")
        
        menaion_key = context.get("menaion_key", "")
        
        # BAPTISMAL HYMN: "As many as have been baptized into Christ"
        # BAPTISMAL HYMN: "As many as have been baptized into Christ"
        # Nativity of the Lord (Feast Day only: Dec 25)
        if feast_id == "nativity" or (menaion_key == "menaion.1225" and not context.get("is_afterfeast") and not context.get("is_forefeast")) or (context.get("primary_feast_id") == "nativity" and not context.get("is_afterfeast") and not context.get("is_forefeast")):
            return {
                "type": "replacement",
                "replacement": "as_many_baptized",
                "ref_key": "liturgikon.as_many_as_baptized",
                "text": "As many as have been baptized into Christ have put on Christ. Alleluia."
            }
        
        # Theophany of the Lord (Feast Day only: Jan 6)
        if feast_id == "theophany" or (menaion_key == "menaion.0106" and not context.get("is_afterfeast") and not context.get("is_forefeast")) or (context.get("primary_feast_id") == "theophany" and not context.get("is_afterfeast") and not context.get("is_forefeast")):
            return {
                "type": "replacement",
                "replacement": "as_many_baptized",
                "ref_key": "liturgikon.as_many_as_baptized",
                "text": "As many as have been baptized into Christ have put on Christ. Alleluia."
            }
        
        # Lazarus Saturday
        if pascha_offset == -8 or feast_id == "lazarus_saturday":
            return {
                "type": "replacement",
                "replacement": "as_many_baptized",
                "ref_key": "liturgikon.as_many_as_baptized",
                "text": "As many as have been baptized into Christ have put on Christ. Alleluia."
            }
        
        # Holy Saturday
        if pascha_offset == -1 or feast_id == "holy_saturday":
            return {
                "type": "replacement",
                "replacement": "as_many_baptized",
                "ref_key": "liturgikon.as_many_as_baptized",
                "text": "As many as have been baptized into Christ have put on Christ. Alleluia."
            }
        
        # Pascha through Bright Week (offset 0-6)
        if 0 <= pascha_offset <= 6 or paradigm == "p_pascha" or feast_id == "pascha":
            return {
                "type": "replacement",
                "replacement": "as_many_baptized",
                "ref_key": "liturgikon.as_many_as_baptized",
                "text": "As many as have been baptized into Christ have put on Christ. Alleluia."
            }
        
        # Pentecost (Pentecost Sunday only, offset 49)
        if pascha_offset == 49:
            return {
                "type": "replacement",
                "replacement": "as_many_baptized",
                "ref_key": "liturgikon.as_many_as_baptized",
                "text": "As many as have been baptized into Christ have put on Christ. Alleluia."
            }
        
        # CROSS HYMN: "Before Thy Cross we bow down"
        # Exaltation of Cross (Sept 14)
        if feast_id == "exaltation_cross" or (menaion_key == "menaion.0914" and not context.get("is_afterfeast") and not context.get("is_forefeast")) or (context.get("primary_feast_id") == "exaltation_cross" and not context.get("is_afterfeast") and not context.get("is_forefeast")):
            return {
                "type": "replacement",
                "replacement": "before_thy_cross",
                "ref_key": "liturgikon.before_thy_cross",
                "text": "Before Thy Cross we bow down in worship, O Master, and Thy holy Resurrection we glorify."
            }
        
        # Third Sunday of Lent (Veneration of the Cross) - offset exactly -28
        if pascha_offset == -28:
            return {
                "type": "replacement",
                "replacement": "before_thy_cross",
                "ref_key": "liturgikon.before_thy_cross",
                "text": "Before Thy Cross we bow down in worship, O Master, and Thy holy Resurrection we glorify."
            }
        
        # Procession of Cross (Aug 1)
        if feast_id == "procession_cross" or menaion_key == "menaion.0801":
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
        pascha_off = context.get("pascha_offset")
        if pascha_off is not None and 0 <= pascha_off <= 38:
            return {
                "type": "variable",
                "ref_key": "paschal_zadostoinyk",
                "text": "The angel cried to the Lady Full of Grace: Rejoice, O Pure Virgin! And again I say: Rejoice! Thy Son is risen from His three days in the tomb, and has raised all the dead: O you people, be glad! Shine, shine, O New Jerusalem, for the glory of the Lord has shone upon thee. Exult now and be glad, O Zion, and thou, O pure Mother of God, rejoice in the resurrection of Thy Son.",
                "note": "Zadostoinyk (The Angel Cried / Shine, shine, O New Jerusalem)"
            }
        lit_type = str(context.get("liturgy_type") or (rubrics.get("overrides", {}).get("liturgy_type") if rubrics else "") or (rubrics.get("variables", {}).get("liturgy_type") if rubrics else "")).lower()
        if "basil" in lit_type:
            if pascha_off in (-3, -1):
                return {"type": "variable", "ref_key": "festal_zadostoinyk", "note": "Use 9th Ode Heirmos"}
            return {
                "type": "fixed_ref",
                "ref_key": "horologion.in_thee_rejoiceth",
                "text": "In you, O Woman Full of Grace, all creation rejoices...",
                "note": "In you, O Woman Full of Grace"
            }

        # Scenario B: Festal Zadostoynyk
        rules = self.liturgy_logic.get("megalynarion_logic", [])
        rank = self.calculate_rank(context)
        is_afterfeast = context.get("is_afterfeast")
        is_apodosis = context.get("is_apodosis")
        is_great_feast = context.get("feast_level") in ("lord", "theotokos")
        
        if is_afterfeast or is_apodosis or (is_great_feast and rank <= 2):
            return {"type": "variable", "ref_key": "festal_zadostoinyk", "note": "Use 9th Ode Heirmos"}

        for rule in rules:
             if "rank == 1" in rule["condition"] and rank == 1:
                 return {"type": "variable", "ref_key": "festal_zadostoinyk", "note": "Use 9th Ode Heirmos"}
                 
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


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:L11661-11720")
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
        liturgy_type = str(context.get("liturgy_type", "chrysostom")).lower()
        from engine.utils.type_utils import parse_rank_integer
        rank = parse_rank_integer(context.get("rank", 5))
        paradigm = context.get("paradigm", "")
        feast_id = context.get("feast_id", None)
        
        # Only applies to Basil Liturgy
        if "basil" not in liturgy_type:
            return None  # Fall through to standard megalynarion
        
        # RULE: Great Feast at Basil Liturgy - use 9th Ode Irmos
        # Exception: January 1 is St. Basil's own feast day, which takes "In you, O Woman Full of Grace"
        # Citation: Dolnytsky Typikon Master Part III 1 January (p. 177)
        is_jan_1 = context.get("month") == 1 and context.get("day") == 1
        if (rank == 1 or paradigm in ["p_feast_lord", "p_feast_theotokos"]) and not is_jan_1:
            return {
                "type": "megalynarion",
                "source": "feast_irmos",
                "ref_key": f"menaion.{feast_id}.ode_9_irmos" if feast_id else "feast.ode_9_irmos",
                "rubric": "Instead of 'It is truly meet', we sing the Irmos of the 9th Ode"
            }
        
        # DEFAULT: "In you, O Woman Full of Grace"
        return {
            "type": "megalynarion",
            "source": "basil",
            "ref_key": "horologion.in_thee_rejoiceth",
            "text": "In you, O Woman Full of Grace, all creation rejoices..."
        }


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:2.5,L1211-1216")
    def resolve_communion_hymn(self, context, rubrics=None):
        """
        Communion Hymn (Причастен/Koinonikon).
        Citation: Dolnytsky Part II (Communion cycle)
        
        RULE: Different hymns for different days and occasions.
        Sunday always: "Praise the Lord from the heavens"
        Great Feast: Proper of feast
        Weekday: Tone-appropriate or proper of day
        """
        def resolve_str_hymn(key, source="feast"):
            if isinstance(key, list):
                items = [resolve_str_hymn(k, source) for k in key if k]
                return {
                    "type": "communion_hymn",
                    "items": items,
                    "text": " And of the Saint: ".join(it.get("text", "") for it in items if it.get("text")),
                    "ref_key": items[0].get("ref_key", "") if items else "",
                    "source": source
                }
            if isinstance(key, dict):
                return {
                    "type": "communion_hymn",
                    "text": key.get("text", ""),
                    "ref_key": key.get("ref_key", ""),
                    "source": key.get("source", source)
                }
            if not isinstance(key, str):
                return {
                    "type": "communion_hymn",
                    "text": str(key),
                    "ref_key": "",
                    "source": source
                }
            known_hymns = {
                "praise_the_lord": "Praise the Lord from the heavens; praise Him in the highest.",
                "righteous_memory": "In everlasting remembrance shall the righteous be; he shall not be afraid of evil tidings.",
                "cup_of_salvation": "I will take the cup of salvation, and I will call upon the name of the Lord.",
                "making_angels_spirits": "Who maketh His angels spirits, and His ministers a flame of fire.",
                "light_of_your_countenance": "The light of Thy countenance, O Lord, is signed upon us.",
                "their_sound_has_gone_forth": "Their sound hath gone forth into all the earth, and their words unto the ends of the world.",
                "the_lord_sent_redemption": "The Lord has sent redemption to His people.",
                "grace_of_god_has_appeared": "The grace of God has appeared, bringing salvation to all men.",
                "we_will_walk_in_light": "We will walk in the light of Your face, O Lord, and in Your name will we rejoice all the day.",
                "the_lord_has_chosen_zion": "The Lord has chosen Zion; He has desired it for His habitation.",
                "rejoice_in_the_lord": "Rejoice in the Lord, O ye righteous; praise is comely for the upright.",
                "praise_the_lord_and_rejoice": "Praise the Lord from the heavens, praise Him in the highest. Rejoice in the Lord, O you righteous; praise is becoming to the upright.",
                "be_exalted_o_god": "Be exalted, O God, above the heavens, and Your glory above all the earth.",
                "crown_of_the_year": "Bless the crown of the year with Thy goodness, O Lord."
            }
            if key in known_hymns:
                return {
                    "type": "communion_hymn",
                    "text": known_hymns[key],
                    "ref_key": key,
                    "source": source
                }
            try:
                asset = self.get_text(key, context=context)
                if asset and isinstance(asset, dict) and "content" in asset:
                    return {
                        "type": "communion_hymn",
                        "text": asset["content"],
                        "ref_key": key,
                        "source": source
                    }
            except Exception:
                pass
            return {
                "type": "communion_hymn",
                "text": key,
                "ref_key": "",
                "source": source
            }

        day_of_week = context.get("day_of_week", 0)
        from engine.utils.type_utils import parse_rank_integer
        rank = parse_rank_integer(context.get("rank", 5))
        paradigm = context.get("paradigm", "")
        feast_id = context.get("feast_id", None)
        tone = context.get("tone", 1)
        season = context.get("season", "ordinary")
        liturgy_type = context.get("liturgy_type", "chrysostom")

        pascha_offset = context.get("pascha_offset")
        is_eucharist_period = (pascha_offset is not None and 60 <= pascha_offset <= 67)
        is_after_or_apodosis = context.get("is_afterfeast") or context.get("is_apodosis")

        overrides = {}
        if rubrics:
            overrides = {**rubrics.get("variables", {}), **rubrics.get("overrides", {})}
        if not overrides:
            overrides = context.get("variables", {}) or {}

        is_no_reading_weekday_saint = (
            1 <= day_of_week <= 6
            and rank > 3
            and context.get("dolnytsky_rank_code") in ("[4 TR]", "[4 NO]")
            and not is_after_or_apodosis
            and not context.get("is_forefeast")
            and not context.get("is_fore_or_afterfeast")
            and not any(
                isinstance(s, dict) and s.get("rank_code") in ("[4 A+G]", "[6 SM]", "[GT DOX]", "[POL]", "[VIGIL]")
                for s in context.get("saints", [])
            )
        )

        if not is_eucharist_period and not is_no_reading_weekday_saint:
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
                    elif isinstance(c_h, (str, list)):
                        return resolve_str_hymn(c_h)
            
            # 2. Check for direct communion_hymn override
            c_h = overrides.get("communion_hymn")
            if c_h:
                if isinstance(c_h, dict):
                    res_h = {
                        "type": "communion_hymn",
                        "text": c_h.get("text", ""),
                        "ref_key": c_h.get("ref_key", "")
                    }
                elif isinstance(c_h, (str, list)):
                    res_h = resolve_str_hymn(c_h)
                else:
                    res_h = None
                if res_h:
                    is_great_feast_lord = (
                        rank == 1
                        or paradigm == "p_feast_lord"
                        or context.get("feast_level") == "lord"
                        or context.get("dolnytsky_rank") == "LORD"
                    )
                    if day_of_week == 0 and not is_great_feast_lord and season != "pascha" and paradigm != "p_pascha":
                        saints_list = context.get("saints", [])
                        has_sunday_saint_comm = (
                            rank <= 3
                            or context.get("dolnytsky_rank_code") in ("[GT DOX]", "[POL]", "[VIGIL]")
                            or any(isinstance(s, dict) and s.get("rank_code") in ("[GT DOX]", "[POL]", "[VIGIL]") for s in saints_list)
                        )
                        sunday_text = "Praise the Lord from the heavens, praise Him in the highest."
                        if not has_sunday_saint_comm:
                            return {
                                "type": "communion_hymn",
                                "text": sunday_text,
                                "ref_key": "octoechos.communion_sunday"
                            }
                        if sunday_text.lower() not in res_h.get("text", "").lower():
                            res_h["text"] = f"{sunday_text} And of the Saint: {res_h['text']}"
                    elif 1 <= day_of_week <= 6 and is_after_or_apodosis:
                        # Weekday afterfeast (Dolnytsky §2.16:1653, §3.3.3:2300):
                        # Feast communion hymn prepends the Saint's hymn
                        feast_comm = "I will take the cup of salvation, and I will call upon the name of the Lord."
                        if feast_comm.lower() not in res_h.get("text", "").lower():
                            res_h["text"] = f"{feast_comm} And of the Saint: {res_h['text']}"
                            res_h["source"] = "feast_and_saint"
                    return res_h

        # EUCHARIST PERIOD AFTERFEAST (pascha_offset between 60 and 67)
        pascha_offset = context.get("pascha_offset")
        if pascha_offset is not None and 60 <= pascha_offset <= 67:
            saints = context.get("saints", [])
            if rank <= 3 and saints:
                return {
                    "type": "communion_hymn",
                    "text": "Receive the Body of Christ; taste the fountain of immortality. And of the Saint: Their sound hath gone forth into all the earth, and their words unto the ends of the world.",
                    "source": "feast",
                    "ref_key": "pentecostarion.eucharist.communion_combined"
                }
            else:
                return {
                    "type": "communion_hymn",
                    "text": "Receive the Body of Christ; taste the fountain of immortality.",
                    "source": "feast",
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
        
        # AFTERFEAST / APODOSIS: Festal communion hymn
        is_after_or_apodosis = context.get("is_afterfeast") or context.get("is_apodosis")
        feast_level = context.get("feast_level")
        if is_after_or_apodosis and day_of_week != 0:
            if feast_level == "theotokos":
                return {
                    "type": "communion_hymn",
                    "text": "I will take the cup of salvation, and I will call upon the name of the Lord.",
                    "source": "feast",
                    "ref_key": f"menaion.{feast_id}.communion_hymn" if feast_id else "theotokos.communion_hymn"
                }
            else:
                c_h_key = overrides.get("communion_hymn")
                if not c_h_key and (season == "Exaltation_Cross" or "cross" in str(feast_id).lower() or "exaltation" in str(context.get("title", "")).lower()):
                    c_h_key = "light_of_your_countenance"
                if c_h_key:
                    return resolve_str_hymn(c_h_key)
                return {
                    "type": "communion_hymn",
                    "text": "The light of Thy countenance, O Lord, is signed upon us.",
                    "source": "feast",
                    "ref_key": f"menaion.{feast_id}.communion_hymn" if feast_id else "feast.communion_hymn"
                }

        # GREAT FEAST: Proper communion hymn
        if rank == 1 or paradigm in ["p_feast_lord", "p_feast_theotokos"]:
            if feast_level == "theotokos":
                return {
                    "type": "communion_hymn",
                    "text": "I will take the cup of salvation, and I will call upon the name of the Lord.",
                    "source": "feast",
                    "ref_key": f"menaion.{feast_id}.communion_hymn" if feast_id else "theotokos.communion_hymn"
                }
            c_h_key = overrides.get("communion_hymn")
            if not c_h_key and (season == "Exaltation_Cross" or "cross" in str(feast_id).lower() or "exaltation" in str(context.get("title", "")).lower()):
                c_h_key = "light_of_your_countenance"
            if c_h_key:
                return resolve_str_hymn(c_h_key)
            return {
                "type": "communion_hymn",
                "text": "The light of Thy countenance, O Lord, is signed upon us.",
                "source": "feast",
                "ref_key": f"menaion.{feast_id}.communion_hymn" if feast_id else "feast.communion_hymn"
            }
        
        # SUNDAY: "Praise the Lord" + Saint Communion Hymn if [GT DOX], [POL], or [VIGIL]
        if day_of_week == 0:
            sunday_text = "Praise the Lord from the heavens, praise Him in the highest."
            saints = context.get("saints", [])
            sunday_reading_saints = [
                s for s in saints
                if any(m in str(s.get("rank_code", "")) for m in ("GT DOX", "POL", "VIGIL"))
            ]
            if sunday_reading_saints:
                s_obj = sunday_reading_saints[0]
                s_title = str(s_obj.get("title", "")).lower()
                if "apostle" in s_title or "evangelist" in s_title:
                    s_hymn = "Their proclamation has gone out into all the earth, and their words to the ends of the universe."
                elif "unmercenar" in s_title or "cosmas" in s_title or ("martyr" in s_title and len(s_obj.get("all_parsed_saints", [])) > 1):
                    s_hymn = "Rejoice in the Lord, O you righteous; praise is becoming to the upright."
                else:
                    s_hymn = "In everlasting remembrance shall the righteous be; he shall not be afraid of evil tidings."
                return {
                    "type": "communion_hymn",
                    "text": f"{sunday_text} And of the Saint: {s_hymn}",
                    "ref_key": "octoechos.communion_sunday"
                }
            return {
                "type": "communion_hymn",
                "text": sunday_text,
                "ref_key": "octoechos.communion_sunday"
            }
        
        # WEEKDAY PROPER
        weekday_hymns = {
            1: {"text": "He makes His angels spirits, and His ministers a flame of fire.", "ref_key": "horologion.communion_monday"},
            2: {"text": "In everlasting remembrance shall the righteous be; he shall not fear evil tidings.", "ref_key": "horologion.communion_tuesday"},
            3: {"text": "I will take the cup of salvation, and I will call upon the name of the Lord.", "ref_key": "horologion.communion_wednesday"},
            4: {"text": "Their proclamation has gone out into all the earth, and their words to the ends of the universe.", "ref_key": "horologion.communion_thursday"},
            5: {"text": "O Lord, save Your people, and bless Your inheritance.", "ref_key": "horologion.communion_friday"},
            6: {"text": "Blessed are they whom You have chosen and taken, O Lord.", "ref_key": "horologion.communion_saturday"}
        }
        
        hymn_data = weekday_hymns.get(day_of_week, weekday_hymns[1])
        saints = context.get("saints", [])
        reading_saints = [
            s for s in saints
            if any(m in str(s.get("rank_code", "")) for m in ("A+G", "6 SM", "GT DOX", "POL", "VIGIL"))
        ]
        if reading_saints:
            s_obj = reading_saints[0]
            s_title = f"{s_obj.get('title', '')} {s_obj.get('name', '')} {s_obj.get('category', '')}".lower()
            s_name_low = str(s_obj.get("name", "")).lower()
            is_plural_martyrs = (
                "martyr" in s_title
                and (
                    len(s_obj.get("all_parsed_saints", [])) > 1
                    or "and those with" in s_name_low
                    or "companions" in s_name_low
                    or "martyrs" in s_title
                )
            )
            if "apostle" in s_title:
                s_hymn = "Their proclamation has gone out into all the earth, and their words to the ends of the universe."
            elif "unmercenar" in s_title or "cosmas" in s_title or is_plural_martyrs:
                s_hymn = "Rejoice in the Lord, O you righteous; praise is becoming to the upright."
            else:
                s_hymn = "In everlasting remembrance shall the righteous be; he shall not be afraid of evil tidings."
            is_polyeleos_or_vigil_saint = (
                rank in (2, "rank_polyeleos", "rank_vigil")
                or context.get("has_polyeleos") is True
                or context.get("dolnytsky_rank_code") in ("[POL]", "[VIGIL]")
                or any(m in str(s_obj.get("rank_code", "")) for m in ("POL", "VIGIL"))
            )
            if is_polyeleos_or_vigil_saint and not context.get("is_forefeast") and not is_after_or_apodosis:
                return {
                    "type": "communion_hymn",
                    "text": s_hymn,
                    "ref_key": "menaion.communion_saint"
                }
            day_clause = hymn_data["text"].split(";")[0].strip().rstrip(".").lower()
            saint_clause = s_hymn.split(";")[0].strip().rstrip(".").lower()
            if day_clause != saint_clause:
                if day_of_week == 6:
                    combined_text = f"{s_hymn} And of the Day: {hymn_data['text']}"
                else:
                    combined_text = f"{hymn_data['text']} And of the Saint: {s_hymn}"
                return {
                    "type": "communion_hymn",
                    "text": combined_text,
                    "ref_key": hymn_data["ref_key"]
                }
        return {
            "type": "communion_hymn",
            "text": hymn_data["text"],
            "ref_key": hymn_data["ref_key"]
        }


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:2.2,L1053-1068")
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
        try:
            pascha_offset = int(context.get("pascha_offset", -100))
        except (ValueError, TypeError):
            pascha_offset = -100
        title = context.get("title", "").lower()
        
        # PASCHA through Ascension Eve (0 to 39): "Christ is risen from the dead" (3x)
        if season == "pascha" or paradigm == "p_pascha" or (0 <= pascha_offset < 39):
            return {
                "type": "post_communion",
                "hymn": "Christ is risen from the dead, trampling down death by death, and to those in the tombs giving life.",
                "repeat": 3,
                "ref_key": "pentecostarion.post_communion_paschal"
            }
        
        # ASCENSION (Pascha offset 40 through Apodosis offset 48): "Be exalted, O God"
        if 40 <= pascha_offset <= 48 or feast_id in ("ascension", "ascension_afterfeast", "ascension_apodosis"):
            return {
                "type": "post_communion",
                "hymn": "Be exalted, O God, above the heavens, and let Your glory be over all the earth.",
                "ref_key": "pentecostarion.post_communion_ascension"
            }
        
        # EXALTATION OF THE CROSS through Leavetaking: Troparion of the Cross (NOT Forefeast)
        is_forefeast = context.get("is_forefeast", False)
        if not is_forefeast and (season == "Exaltation_Cross" or feast_id in ("exaltation_cross", "exaltation") or context.get("primary_feast_id") == "exaltation_cross"):
            return {
                "type": "post_communion",
                "hymn": "Save, O Lord, Your people, and bless Your inheritance, granting victory to our nation over its enemies, and by Your Cross preserving Your community.",
                "ref_key": "menaion.exaltation_cross.troparion"
            }

        # NATIVITY OF CHRIST through Leavetaking: Troparion of Nativity (NOT Nativity of Theotokos, NOT Forefeast)
        if not is_forefeast and (feast_id == "nativity" or context.get("primary_feast_id") == "nativity"):
            return {
                "type": "post_communion",
                "hymn": "Your Nativity, O Christ our God, has shone upon the world the light of knowledge...",
                "ref_key": "menaion.nativity.troparion"
            }
        
        # THEOPHANY through Leavetaking: Troparion of Theophany
        if feast_id == "theophany" or context.get("primary_feast_id") == "theophany":
            return {
                "type": "post_communion",
                "hymn": "When You, O Lord, were baptized in the Jordan, the worship of the Trinity was made manifest...",
                "ref_key": "menaion.theophany.troparion"
            }
        
        # HOLY THURSDAY (Pascha offset -3)
        if pascha_offset == -3 or feast_id == "holy_thursday":
            return {
                "type": "post_communion",
                "hymn": "Receive me today, O Son of God, as a partaker of Your Mystical Supper...",
                "ref_key": "triodion.of_thy_mystical_supper"
            }

        # HOLY SATURDAY (Pascha offset -1)
        if pascha_offset == -1 or feast_id == "holy_saturday":
            return {
                "type": "post_communion",
                "hymn": "The post-communion hymn is omitted; we proceed directly to the Thanksgiving Litany ('Let our mouths be filled...').",
                "ref_key": "triodion.holy_saturday_post_communion"
            }

        # Check variable override
        post_rep = context.get("variables", {}).get("post_communion_replace") or (rubrics.get("variables", {}).get("post_communion_replace") if rubrics else None)
        if post_rep:
            return {
                "type": "post_communion",
                "hymn": post_rep,
                "ref_key": f"custom.{post_rep}"
            }

        # DEFAULT: "We have seen the true light"
        return {
            "type": "post_communion",
            "hymn": "We have seen the true light, we have received the heavenly Spirit...",
            "ref_key": "horologion.we_have_seen_true_light"
        }


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:3.4.6,L2759-2788")
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
        if date_str.endswith("-12-24") or feast_id == "nativity_eve" or context.get("primary_feast_id") == "nativity_eve" or "nativity" in title:
            vesperal_id = "nativity_eve"
        elif date_str.endswith("-01-05") or feast_id == "theophany_eve" or context.get("primary_feast_id") == "theophany_eve" or "theophany" in title or "epiphany" in title:
            vesperal_id = "theophany_eve"
        # Check by Pascha offset
        elif context.get("pascha_offset") == -3 or feast_id == "holy_thursday" or "holy thursday" in title or "great thursday" in title or "thursday" in title:
            vesperal_id = "holy_thursday"
        elif context.get("pascha_offset") == -1 or feast_id == "holy_saturday" or "holy saturday" in title or "great saturday" in title or "saturday" in title:
            vesperal_id = "holy_saturday"
        elif feast_id in ("annunciation", "annunciation_eve") or context.get("primary_feast_id") == "annunciation" or "annunciation" in title:
            vesperal_id = "annunciation"
        
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
            p_key = f"vesperal.{vesperal_id}.paremia_{p.get('number', 1)}" if isinstance(p, dict) else str(p)
            components.append({"type": "reading", "source": "paremia", "ref_key": p_key, "data": p})
             
        # Add Epistle Prokeimenon
        components.append({"type": "prokeimenon", "ref_key": f"vesperal.{vesperal_id}.prokeimenon", "data": readings.get("epistle_prokeimenon")})
        
        # Add Epistle
        components.append({"type": "reading", "source": "epistle", "ref_key": f"vesperal.{vesperal_id}.epistle", "data": readings.get("epistle")})
        
        # Add Alleluia
        if readings.get("alleluia"):
            components.append({"type": "alleluia", "ref_key": f"vesperal.{vesperal_id}.alleluia", "data": readings.get("alleluia")})
            
        # Add Gospel
        components.append({"type": "reading", "source": "gospel", "ref_key": f"vesperal.{vesperal_id}.gospel", "data": readings.get("gospel")})
        
        return {
            "type": "sequence",
            "components": components,
            "data": readings,
            "source_metadata": {"vesperal_id": vesperal_id, "paremia_count": readings.get("count", 0)}
        }


    def _get_weekday_lectionary_reading(self, weeks_after_pentecost, day_of_week):
        """Return (epistle_ref, gospel_ref) for Weeks 1..36 after Pentecost, Mon..Sat (1..6)."""
        if weeks_after_pentecost is None or day_of_week not in (1, 2, 3, 4, 5, 6):
            return None
        lectionary = getattr(self, "_WEEKDAY_LECTIONARY_36", None)
        if lectionary is None:
            lectionary = {
                1: {1: ("Ephesians 5:9–19", "Matthew 18:10–20"), 2: ("Romans 1:1–7, 13–17", "Matthew 4:25–5:13"), 3: ("Romans 1:18–27", "Matthew 5:20–26"), 4: ("Romans 1:28–2:9", "Matthew 5:27–32"), 5: ("Romans 2:14–29", "Matthew 5:33–41"), 6: ("Romans 1:7–12", "Matthew 5:42–48")},
                2: {1: ("Romans 2:28–3:18", "Matthew 6:31–34; 7:9–11"), 2: ("Romans 4:4–12", "Matthew 7:15–21"), 3: ("Romans 4:13–25", "Matthew 7:21–23"), 4: ("Romans 5:1–10", "Matthew 8:23–27"), 5: ("Romans 5:17–6:2", "Matthew 9:14–17"), 6: ("Romans 3:19–26", "Matthew 7:1–8")},
                3: {1: ("Romans 7:1–13", "Matthew 9:36–10:8"), 2: ("Romans 7:14–8:2", "Matthew 10:9–15"), 3: ("Romans 8:2–13", "Matthew 10:16–22"), 4: ("Romans 8:22–27", "Matthew 10:23–31"), 5: ("Romans 9:6–19", "Matthew 10:32–36; 11:1"), 6: ("Romans 3:28–4:3", "Matthew 7:24–8:4")},
                4: {1: ("Romans 9:18–33", "Matthew 11:2–15"), 2: ("Romans 10:11–11:2", "Matthew 11:16–20"), 3: ("Romans 11:2–12", "Matthew 11:20–26"), 4: ("Romans 11:13–24", "Matthew 11:27–30"), 5: ("Romans 11:25–36", "Matthew 12:1–8"), 6: ("Romans 6:11–17", "Matthew 8:14–23")},
                5: {1: ("Romans 12:4–5, 15–21", "Matthew 12:9–13"), 2: ("Romans 14:9–18", "Matthew 12:14–16, 22–30"), 3: ("Romans 15:7–16", "Matthew 12:38–45"), 4: ("Romans 15:17–29", "Matthew 12:46–13:3"), 5: ("Romans 16:1–16", "Matthew 13:4–9"), 6: ("Romans 8:14–21", "Matthew 9:9–13")},
                6: {1: ("Romans 16:17–24", "Matthew 13:10–23"), 2: ("1 Corinthians 1:1–9", "Matthew 13:24–30"), 3: ("1 Corinthians 2:9–3:8", "Matthew 13:31–36"), 4: ("1 Corinthians 3:18–23", "Matthew 13:36–43"), 5: ("1 Corinthians 4:5–8", "Matthew 13:44–54"), 6: ("Romans 9:1–5", "Matthew 9:18–26")},
                7: {1: ("1 Corinthians 5:9–6:11", "Matthew 13:54–58"), 2: ("1 Corinthians 6:20–7:12", "Matthew 14:1–13"), 3: ("1 Corinthians 7:12–24", "Matthew 14:35–15:11"), 4: ("1 Corinthians 7:24–35", "Matthew 15:12–21"), 5: ("1 Corinthians 7:35–8:7", "Matthew 15:29–31"), 6: ("Romans 12:1–3", "Matthew 10:37–11:1")},
                8: {1: ("1 Corinthians 9:13–18", "Matthew 16:1–6"), 2: ("1 Corinthians 10:5–12", "Matthew 16:6–12"), 3: ("1 Corinthians 10:12–22", "Matthew 16:20–24"), 4: ("1 Corinthians 10:28–11:7", "Matthew 16:24–28"), 5: ("1 Corinthians 11:8–22", "Matthew 17:10–18"), 6: ("Romans 13:1–10", "Matthew 12:30–37")},
                9: {1: ("1 Corinthians 11:31–12:6", "Matthew 18:1–11"), 2: ("1 Corinthians 12:12–26", "Matthew 18:18–22; 19:1–2, 13–15"), 3: ("1 Corinthians 13:4–14:5", "Matthew 20:1–16"), 4: ("1 Corinthians 14:6–19", "Matthew 20:17–28"), 5: ("1 Corinthians 14:26–40", "Matthew 21:12–14, 17–20"), 6: ("Romans 14:6–9", "Matthew 15:32–39")},
                10: {1: ("1 Corinthians 15:12–19", "Matthew 21:18–22"), 2: ("1 Corinthians 15:29–38", "Matthew 21:23–27"), 3: ("1 Corinthians 16:4–12", "Matthew 21:28–32"), 4: ("2 Corinthians 1:1–7", "Matthew 21:43–46"), 5: ("2 Corinthians 1:12–20", "Matthew 22:23–33"), 6: ("Romans 15:30–33", "Matthew 17:24–18:4")},
                11: {1: ("2 Corinthians 2:4–15", "Matthew 23:13–22"), 2: ("2 Corinthians 2:14–3:3", "Matthew 23:23–28"), 3: ("2 Corinthians 3:4–11", "Matthew 23:29–39"), 4: ("2 Corinthians 4:1–6", "Matthew 24:13–28"), 5: ("2 Corinthians 4:13–18", "Matthew 24:27–33, 42–51"), 6: ("1 Corinthians 1:3–9", "Matthew 19:3–12")},
                12: {1: ("2 Corinthians 5:10–15", "Mark 1:9–15"), 2: ("2 Corinthians 5:15–21", "Mark 1:16–22"), 3: ("2 Corinthians 6:11–16", "Mark 1:23–28"), 4: ("2 Corinthians 7:1–10", "Mark 1:29–35"), 5: ("2 Corinthians 7:10–16", "Mark 2:18–22"), 6: ("1 Corinthians 1:26–29", "Matthew 20:29–34")},
                13: {1: ("2 Corinthians 8:7–15", "Mark 3:6–12"), 2: ("2 Corinthians 8:16–9:5", "Mark 3:13–19"), 3: ("2 Corinthians 9:12–10:7", "Mark 3:20–27"), 4: ("2 Corinthians 10:7–18", "Mark 3:28–35"), 5: ("2 Corinthians 11:5–21", "Mark 4:1–9"), 6: ("1 Corinthians 2:6–9", "Matthew 22:15–22")},
                14: {1: ("2 Corinthians 12:10–19", "Mark 4:10–23"), 2: ("2 Corinthians 12:20–13:2", "Mark 4:24–34"), 3: ("2 Corinthians 13:3–13", "Mark 4:35–41"), 4: ("Galatians 1:1–10, 20–2:5", "Mark 5:1–20"), 5: ("Galatians 2:6–10", "Mark 5:22–24, 35–6:1"), 6: ("1 Corinthians 4:1–5", "Matthew 23:1–12")},
                15: {1: ("Galatians 2:11–16", "Mark 5:24–34"), 2: ("Galatians 2:21–3:7", "Mark 6:1–7"), 3: ("Galatians 3:15–22", "Mark 6:7–13"), 4: ("Galatians 3:23–4:5", "Mark 6:30–45"), 5: ("Galatians 4:8–21", "Mark 6:45–53"), 6: ("1 Corinthians 4:17–5:5", "Matthew 24:1–13")},
                16: {1: ("Galatians 4:28–5:10", "Mark 6:54–7:8"), 2: ("Galatians 5:11–21", "Mark 7:5–16"), 3: ("Galatians 6:2–10", "Mark 7:14–24"), 4: ("Ephesians 1:1–9", "Mark 7:24–30"), 5: ("Ephesians 1:7–17", "Mark 8:1–10"), 6: ("1 Corinthians 10:23–28", "Matthew 24:34–44")},
                17: {1: ("Ephesians 1:22–2:3", "Mark 10:46–52"), 2: ("Ephesians 2:19–3:7", "Mark 11:11–23"), 3: ("Ephesians 3:8–21", "Mark 11:23–26"), 4: ("Ephesians 4:14–19", "Mark 11:27–33"), 5: ("Ephesians 4:17–25", "Mark 12:1–12"), 6: ("1 Corinthians 14:20–25", "Matthew 25:1–13")},
                18: {1: ("Ephesians 4:25–32", "Luke 3:19–22"), 2: ("Ephesians 5:20–26", "Luke 3:23–4:1"), 3: ("Ephesians 5:25–33", "Luke 4:1–15"), 4: ("Ephesians 5:33–6:9", "Luke 4:16–22"), 5: ("Ephesians 6:18–24", "Luke 4:22–30"), 6: ("1 Corinthians 15:39–45", "Luke 4:31–36")},
                19: {1: ("Philippians 1:1–7", "Luke 4:37–44"), 2: ("Philippians 1:8–14", "Luke 5:12–16"), 3: ("Philippians 1:12–20", "Luke 5:33–39"), 4: ("Philippians 1:20–27", "Luke 6:12–19"), 5: ("Philippians 1:27–2:4", "Luke 6:17–23"), 6: ("1 Corinthians 15:58–16:3", "Luke 5:17–26")},
                20: {1: ("Philippians 2:12–16", "Luke 6:24–30"), 2: ("Philippians 2:17–23", "Luke 6:37–45"), 3: ("Philippians 2:24–30", "Luke 6:46–7:1"), 4: ("Philippians 3:1–8", "Luke 7:17–30"), 5: ("Philippians 3:8–19", "Luke 7:31–35"), 6: ("2 Corinthians 1:8–11", "Luke 5:27–32")},
                21: {1: ("Philippians 4:10–23", "Luke 7:36–50"), 2: ("Colossians 1:1–2, 7–11", "Luke 8:1–3"), 3: ("Colossians 1:18–23", "Luke 8:22–25"), 4: ("Colossians 1:24–29", "Luke 9:7–11"), 5: ("Colossians 2:1–7", "Luke 9:12–18"), 6: ("2 Corinthians 3:12–18", "Luke 6:1–10")},
                22: {1: ("Colossians 2:13–20", "Luke 9:18–22"), 2: ("Colossians 2:20–3:3", "Luke 9:23–27"), 3: ("Colossians 3:17–4:1", "Luke 9:44–50"), 4: ("Colossians 4:2–9", "Luke 9:49–56"), 5: ("Colossians 4:10–18", "Luke 10:1–15"), 6: ("2 Corinthians 5:1–10", "Luke 7:2–10")},
                23: {1: ("1 Thessalonians 1:1–5", "Luke 10:22–24"), 2: ("1 Thessalonians 1:6–10", "Luke 11:1–10"), 3: ("1 Thessalonians 2:1–8", "Luke 11:9–13"), 4: ("1 Thessalonians 2:9–14", "Luke 11:14–23"), 5: ("1 Thessalonians 2:14–19", "Luke 11:23–26"), 6: ("2 Corinthians 8:1–5", "Luke 8:16–21")},
                24: {1: ("1 Thessalonians 2:20–3:8", "Luke 11:29–33"), 2: ("1 Thessalonians 3:9–13", "Luke 11:34–41"), 3: ("1 Thessalonians 4:1–12", "Luke 11:42–46"), 4: ("1 Thessalonians 5:1–8", "Luke 11:47–12:1"), 5: ("1 Thessalonians 5:9–13, 24–28", "Luke 12:2–12"), 6: ("2 Corinthians 11:1–6", "Luke 9:1–6")},
                25: {1: ("2 Thessalonians 1:1–10", "Luke 12:13–15, 22–31"), 2: ("2 Thessalonians 1:10–2:2", "Luke 12:42–48"), 3: ("2 Thessalonians 2:1–12", "Luke 12:48–59"), 4: ("2 Thessalonians 2:13–3:5", "Luke 13:1–9"), 5: ("2 Thessalonians 3:6–18", "Luke 13:31–35"), 6: ("Galatians 1:3–10", "Luke 9:37–43")},
                26: {1: ("1 Timothy 1:1–7", "Luke 14:12–15"), 2: ("1 Timothy 1:8–14", "Luke 14:25–35"), 3: ("1 Timothy 1:18–20; 2:8–15", "Luke 15:1–10"), 4: ("1 Timothy 3:1–13", "Luke 16:1–9"), 5: ("1 Timothy 4:4–8, 16", "Luke 16:15–18; 17:1–4"), 6: ("Galatians 3:8–12", "Luke 9:57–62")},
                27: {1: ("1 Timothy 5:1–10", "Luke 17:20–25"), 2: ("1 Timothy 5:11–21", "Luke 17:26–37"), 3: ("1 Timothy 5:22–6:11", "Luke 18:15–17, 26–30"), 4: ("1 Timothy 6:17–21", "Luke 18:31–34"), 5: ("2 Timothy 1:1–2, 8–18", "Luke 19:12–28"), 6: ("Galatians 5:22–6:2", "Luke 10:19–21")},
                28: {1: ("2 Timothy 2:20–26", "Luke 19:37–44"), 2: ("2 Timothy 3:16–4:4", "Luke 19:45–48"), 3: ("2 Timothy 4:9–22", "Luke 20:1–8"), 4: ("Titus 1:5–2:1", "Luke 20:9–18"), 5: ("Titus 1:15–2:10", "Luke 20:19–26"), 6: ("Ephesians 1:16–23", "Luke 12:32–40")},
                29: {1: ("Hebrews 3:5–11, 17–19", "Luke 20:27–44"), 2: ("Hebrews 4:1–13", "Luke 21:12–19"), 3: ("Hebrews 5:11–6:8", "Luke 21:5–7, 10–11, 20–24"), 4: ("Hebrews 7:1–6", "Luke 21:28–33"), 5: ("Hebrews 7:18–25", "Luke 21:37–22:8"), 6: ("Ephesians 2:11–13", "Luke 13:18–29")},
                30: {1: ("Hebrews 8:7–13", "Mark 8:11–21"), 2: ("Hebrews 9:8–10, 15–23", "Mark 8:22–26"), 3: ("Hebrews 10:1–18", "Mark 8:30–34"), 4: ("Hebrews 10:35–11:7", "Mark 9:10–16"), 5: ("Hebrews 11:8, 11–16", "Mark 9:33–41"), 6: ("Ephesians 5:1–8", "Luke 14:1–11")},
                31: {1: ("Hebrews 11:17–31", "Mark 9:42–10:1"), 2: ("Hebrews 12:14–27", "Mark 10:2–12"), 3: ("James 1:1–18", "Mark 10:11–16"), 4: ("James 1:19–27", "Mark 10:17–27"), 5: ("James 2:1–13", "Mark 10:23–32"), 6: ("Colossians 1:3–6", "Luke 16:10–15")},
                32: {1: ("James 2:14–26", "Mark 10:46–52"), 2: ("James 3:1–10", "Mark 11:11–23"), 3: ("James 3:11–4:6", "Mark 11:23–26"), 4: ("James 4:7–5:9", "Mark 11:27–33"), 5: ("1 Peter 1:1–2, 10–12; 2:6–10", "Mark 12:1–12"), 6: ("1 Thessalonians 5:14–23", "Luke 17:3–10")},
                33: {1: ("1 Peter 2:21–3:9", "Mark 12:13–17"), 2: ("1 Peter 3:10–22", "Mark 12:18–27"), 3: ("1 Peter 4:1–11", "Mark 12:28–37"), 4: ("1 Peter 4:12–5:5", "Mark 12:38–44"), 5: ("2 Peter 1:1–10", "Mark 13:1–8"), 6: ("2 Timothy 2:11–19", "Luke 18:2–8")},
                34: {1: ("1 Peter 2:21–3:9", "Mark 12:13–17"), 2: ("1 Peter 3:10–22", "Mark 12:18–27"), 3: ("1 Peter 4:1–11", "Mark 12:28–37"), 4: ("1 Peter 4:12–5:5", "Mark 12:38–44"), 5: ("2 Peter 1:1–10", "Mark 13:1–8"), 6: ("2 Timothy 3:1–9", "Luke 20:46–21:4")},
                35: {1: ("2 Peter 1:20–2:9", "Mark 13:9–13"), 2: ("2 Peter 2:9–22", "Mark 13:14–23"), 3: ("2 Peter 3:1–18", "Mark 13:24–31"), 4: ("1 John 1:8–2:6", "Mark 13:31–14:2"), 5: ("1 John 2:7–17", "Mark 14:3–9"), 6: ("1 Timothy 6:11–16", "Luke 20:46–21:4")},
                36: {1: ("1 John 2:18–3:10", "Mark 11:1–11"), 2: ("1 John 3:11–20", "Mark 14:10–42"), 3: ("1 John 3:21–4:6", "Mark 14:43–15:1"), 4: ("1 John 4:20–5:21", "Mark 15:1–15"), 5: ("2 John 1:1–13", "Mark 15:22, 25, 33–41"), 6: ("2 Timothy 2:11–19", "Luke 20:46–21:4")},
            }
            self._WEEKDAY_LECTIONARY_36 = lectionary
        if weeks_after_pentecost in lectionary and day_of_week in lectionary[weeks_after_pentecost]:
            return lectionary[weeks_after_pentecost][day_of_week]
        if isinstance(weeks_after_pentecost, int) and weeks_after_pentecost > 36:
            return lectionary[36].get(day_of_week)
        return None

    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:2.5,L1211-1216")
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
        def _hydrate_all_readings(res_obj):
            if not isinstance(res_obj, dict) or "readings" not in res_obj:
                return res_obj
            for r in res_obj["readings"]:
                if not isinstance(r, dict):
                    continue
                if "epistle" in r and isinstance(r["epistle"], dict):
                    ep = r["epistle"]
                    if not ep.get("text") and ep.get("ref_key"):
                        s_val = self._format_scripture_key(ep["ref_key"])
                        if s_val and s_val.lower() not in ("epistle", "feast epistle"):
                            ep["text"] = s_val
                if "gospel" in r and isinstance(r["gospel"], dict):
                    g = r["gospel"]
                    if not g.get("text") and g.get("ref_key"):
                        s_val = self._format_scripture_key(g["ref_key"])
                        if s_val and s_val.lower() not in ("gospel", "feast gospel"):
                            g["text"] = s_val
                def _build_reading_combined_info(ref_k_val):
                    s_name = (context.get("title") or "").lower()
                    s_commem = (context.get("dolnytsky_commemoration") or "").lower()
                    saints_list = [s for s in context.get("saints", []) if isinstance(s, dict)]
                    if ref_k_val.startswith("menaion.") and saints_list:
                        matched_s = next(
                            (s for s in saints_list if s.get("rank_code") in ("[4 A+G]", "[6 SM]", "[GT DOX]", "[POL]", "[VIGIL]")),
                            saints_list[0],
                        )
                        for s in saints_list:
                            sid = (s.get("id") or "").lower()
                            snm = (s.get("name") or "").lower()
                            if (sid and sid in ref_k_val) or (snm and snm in ref_k_val):
                                matched_s = s
                                break
                        m_name_low = (matched_s.get("name") or "").lower()
                        is_plural = (
                            len(matched_s.get("all_parsed_saints", [])) > 1
                            or "and those with" in m_name_low
                            or "companions" in m_name_low
                        )
                        plural_tag = "plural_saints " if is_plural else ""
                        return f"{ref_k_val} {plural_tag}{matched_s.get('name', '')} {matched_s.get('title', '')} {matched_s.get('category', '')}".lower()
                    s_names = " ".join(s.get("name", "") for s in saints_list).lower()
                    s_titles = " ".join(f"{s.get('title', '')} {s.get('category', '')}" for s in saints_list).lower()
                    return f"{ref_k_val} {s_name} {s_commem} {s_names} {s_titles}"

                weekday_fb_ep = {
                    1: "Ephesians 5:9–19",
                    2: "Romans 1:1–7, 13–17",
                    3: "Romans 1:18–27",
                    4: "Romans 1:28–2:9",
                    5: "Romans 2:14–29",
                    6: "Romans 1:7–12",
                }
                weekday_fb_gosp = {
                    1: "Matthew 18:10–20",
                    2: "Matthew 4:25–5:13",
                    3: "Matthew 5:20–26",
                    4: "Matthew 5:27–32",
                    5: "Matthew 5:33–41",
                    6: "Matthew 5:42–48",
                }
                dow_val = context.get("day_of_week", 1)

                sunday_pentecost_ep = {
                    1: "Hebrews 11:33–12:2", 2: "Romans 2:10–16", 3: "Romans 5:1–10", 4: "Romans 6:18–23",
                    5: "Romans 10:1–10", 6: "Romans 12:6–14", 7: "Romans 15:1–7", 8: "1 Corinthians 1:10–18",
                    9: "1 Corinthians 3:9–17", 10: "1 Corinthians 4:9–16", 11: "1 Corinthians 9:2–12", 12: "1 Corinthians 15:1–11",
                    13: "1 Corinthians 16:13–24", 14: "2 Corinthians 1:21–2:4", 15: "2 Corinthians 4:6–15", 16: "2 Corinthians 6:1–10",
                    17: "2 Corinthians 6:16–7:1", 18: "2 Corinthians 9:6–11", 19: "2 Corinthians 11:31–12:9", 20: "Galatians 1:11–19",
                    21: "Galatians 2:16–20", 22: "Galatians 6:11–18", 23: "Ephesians 2:4–10", 24: "Ephesians 2:14–22",
                    25: "Ephesians 4:1–6", 26: "Ephesians 5:9–19", 27: "Ephesians 6:10–17", 28: "Colossians 1:12–18",
                    29: "Colossians 3:4–11", 30: "Colossians 3:12–16", 31: "1 Timothy 1:15–17", 32: "1 Timothy 4:9–15",
                }
                sunday_pentecost_gosp = {
                    1: "Matthew 10:32–33, 37–38; 19:27–30", 2: "Matthew 4:18–23", 3: "Matthew 6:22–33", 4: "Matthew 8:5–13",
                    5: "Matthew 8:28–9:1", 6: "Matthew 9:1–8", 7: "Matthew 9:27–35", 8: "Matthew 14:14–22",
                    9: "Matthew 14:22–34", 10: "Matthew 17:14–23", 11: "Matthew 18:23–35", 12: "Matthew 19:16–26",
                    13: "Matthew 21:33–42", 14: "Matthew 22:1–14", 15: "Matthew 22:35–46", 16: "Matthew 25:14–30",
                    17: "Matthew 15:21–28", 18: "Luke 5:1–11", 19: "Luke 6:31–36", 20: "Luke 7:11–16",
                    21: "Luke 8:5–15", 22: "Luke 16:19–31", 23: "Luke 8:26–39", 24: "Luke 8:41–56",
                    25: "Luke 10:25–37", 26: "Luke 12:16–21", 27: "Luke 13:10–17", 28: "Luke 14:16–24",
                    29: "Luke 17:12–19", 30: "Luke 18:18–27", 31: "Luke 18:35–43", 32: "Luke 19:1–10",
                }
                wap = context.get("weeks_after_pentecost")

                if "epistle" in r and isinstance(r["epistle"], dict):
                    ep = r["epistle"]
                    if not ep.get("text") and ep.get("ref_key"):
                        s_val = self._format_scripture_key(ep["ref_key"])
                        if s_val and s_val.lower() not in ("epistle", "feast epistle"):
                            ep["text"] = s_val
                    # Fallback hydration from weekday/Sunday lectionary or Common of Saints if epistle text still missing
                    if not ep.get("text"):
                        ref_k = (ep.get("ref_key") or "").lower()
                        if dow_val == 0 and (ep.get("source") == "apostol" or "sunday" in ref_k):
                            ep["text"] = sunday_pentecost_ep.get(wap, "Galatians 1:11–19")
                        elif (ep.get("source") == "apostol" or "weekday" in ref_k) and len(res_obj["readings"]) > 1:
                            wk_pair = self._get_weekday_lectionary_reading(wap, dow_val)
                            ep["text"] = wk_pair[0] if wk_pair else weekday_fb_ep.get(dow_val, "Romans 1:18–27")
                        else:
                            combined_info = _build_reading_combined_info(ref_k)
                            if any(w in combined_info for w in ["fathers", "council", "councils"]):
                                ep["text"] = "Hebrews 13:7–16"
                            elif any(w in combined_info for w in ["unmercenar", "cosmas", "damian", "nov_01"]):
                                ep["text"] = "1 Corinthians 12:27–13:8"
                            elif any(w in combined_info for w in ["apostle", "theologian", "evangelist", "peter", "paul", "john", "andrew", "james", "philip", "bartholomew", "thomas", "matthew", "luke", "mark"]):
                                ep["text"] = "1 Corinthians 4:9–16"
                            elif any(w in combined_info for w in ["hierarch", "bishop", "chrysostom", "basil", "nicholas"]):
                                ep["text"] = "Hebrews 7:26–8:2"
                            elif any(w in combined_info for w in ["martyr", "passion-bearer", "great-martyr", "hieromartyr"]):
                                ep["text"] = "2 Timothy 2:1–10"
                            elif any(w in combined_info for w in ["venerable", "monk", "abbot", "chariton", "sabbas", "ven.", "ven "]):
                                ep["text"] = "Galatians 5:22–6:2"
                            elif any(w in combined_info for w in ["theotokos", "dormition", "annunciation", "nativity_theotokos", "entry_theotokos", "protection"]):
                                ep["text"] = "Philippians 2:5–11"
                            elif any(w in combined_info for w in ["forerunner", "baptist"]):
                                ep["text"] = "Galatians 4:22–31"
                            elif any(w in combined_info for w in ["prophet"]):
                                ep["text"] = "James 5:10–20"
                            else:
                                ep["text"] = "Galatians 5:22–6:2"

                if "gospel" in r and isinstance(r["gospel"], dict):
                    g = r["gospel"]
                    if not g.get("text") and g.get("ref_key"):
                        s_val = self._format_scripture_key(g["ref_key"])
                        if s_val and s_val.lower() not in ("gospel", "feast gospel"):
                            g["text"] = s_val
                    # Fallback hydration from weekday/Sunday lectionary or Common of Saints if gospel text still missing
                    if not g.get("text"):
                        ref_k = (g.get("ref_key") or "").lower()
                        if dow_val == 0 and (g.get("source") == "evangelion" or "sunday" in ref_k):
                            g["text"] = sunday_pentecost_gosp.get(wap, "Luke 7:11–16")
                        elif (g.get("source") == "evangelion" or "weekday" in ref_k) and len(res_obj["readings"]) > 1:
                            wk_pair = self._get_weekday_lectionary_reading(wap, dow_val)
                            g["text"] = wk_pair[1] if wk_pair else weekday_fb_gosp.get(dow_val, "Matthew 5:20–26")
                        else:
                            combined_info = _build_reading_combined_info(ref_k)
                            if any(w in combined_info for w in ["fathers", "council", "councils"]):
                                g["text"] = "John 17:1–13"
                            elif any(w in combined_info for w in ["unmercenar", "cosmas", "damian", "nov_01"]):
                                g["text"] = "Matthew 10:1, 5–8"
                            elif any(w in combined_info for w in ["apostle", "theologian", "evangelist", "peter", "paul", "john", "andrew", "james", "philip", "bartholomew", "thomas", "matthew", "luke", "mark"]):
                                g["text"] = "Luke 10:16–21"
                            elif any(w in combined_info for w in ["hierarch", "bishop", "chrysostom", "basil", "nicholas"]):
                                g["text"] = "John 10:9–16"
                            elif any(w in combined_info for w in ["martyr", "passion-bearer", "great-martyr", "hieromartyr"]):
                                g["text"] = "John 15:17–16:2"
                            elif any(w in combined_info for w in ["venerable", "monk", "abbot", "chariton", "sabbas", "ven.", "ven "]):
                                g["text"] = "Matthew 11:27–30"
                            elif any(w in combined_info for w in ["theotokos", "dormition", "annunciation", "nativity_theotokos", "entry_theotokos", "protection"]):
                                g["text"] = "Luke 10:38–42; 11:27–28"
                            elif any(w in combined_info for w in ["forerunner", "baptist"]):
                                g["text"] = "Luke 1:5–25"
                            elif any(w in combined_info for w in ["prophet"]):
                                g["text"] = "Luke 11:47–12:1"
                            else:
                                g["text"] = "Matthew 11:27–30"

                if "prokeimenon" in r and isinstance(r["prokeimenon"], dict):
                    p = r["prokeimenon"]
                    if not p.get("text") and p.get("ref_key"):
                        asset = self.get_text(p["ref_key"], context=context)
                        if asset and not (isinstance(asset, dict) and asset.get("is_missing")):
                            p["text"] = asset.get("content")
                            if asset.get("tone") and not p.get("tone"):
                                p["tone"] = asset["tone"]
                    # Split embedded "verse:" lines if present in p["text"]
                    if isinstance(p.get("text"), str) and "verse:" in p["text"].lower():
                        p_lines = [ln.strip() for ln in p["text"].splitlines() if ln.strip()]
                        main_parts = []
                        for ln in p_lines:
                            if ln.lower().startswith("verse:"):
                                v_val = re.sub(r'^verse:\s*', '', ln, flags=re.IGNORECASE).strip()
                                if v_val and not p.get("verse"):
                                    p["verse"] = v_val
                            else:
                                main_parts.append(ln)
                        p["text"] = " ".join(main_parts).strip()
                    # Fallback hydration from Octoechos, Horologion, Feasts, and Common of Saints
                    ref_k = p.get("ref_key", "").lower()
                    combined_info = _build_reading_combined_info(ref_k)
                    if not p.get("text"):

                        # 1. Octoechos Sunday Resurrection Prokeimena
                        oct_prokeimena = {
                            1: {"tone": 1, "text": "Let Your mercy, O Lord, be upon us, as we have hoped in You.", "verse": "Rejoice in the Lord, O you righteous; praise is becoming to the upright."},
                            2: {"tone": 2, "text": "The Lord is my strength and my song, and He has become my salvation.", "verse": "The Lord has chastened me severely, but He has not given me over to death."},
                            3: {"tone": 3, "text": "Sing praises to our God, sing praises; sing praises to our King, sing praises.", "verse": "Clap your hands, all you nations; shout to God with the voice of joy."},
                            4: {"tone": 4, "text": "How magnificent are Your works, O Lord; in wisdom You have made them all.", "verse": "Bless the Lord, O my soul; O Lord my God, You are very great."},
                            5: {"tone": 5, "text": "You shall keep us, O Lord; You shall preserve us from this generation and forever.", "verse": "Save me, O Lord, for the godly man ceases."},
                            6: {"tone": 6, "text": "Save Your people, O Lord, and bless Your inheritance.", "verse": "To You, O Lord, will I call; O my God, do not be silent to me."},
                            7: {"tone": 7, "text": "The Lord will give strength to His people; the Lord will bless His people with peace.", "verse": "Bring to the Lord, O you sons of God, bring to the Lord young rams."},
                            8: {"tone": 8, "text": "Make vows and pay them to the Lord our God.", "verse": "In Judah God is known; His name is great in Israel."}
                        }
                        if "octoechos" in ref_k or (context.get("day_of_week") == 0 and "prokeimenon" in ref_k and "menaion" not in ref_k):
                            m_t = re.search(r'tone_(\d+)', ref_k)
                            t_num = int(m_t.group(1)) if m_t else (p.get("tone") or context.get("tone") or 1)
                            if t_num in oct_prokeimena:
                                p["tone"] = oct_prokeimena[t_num]["tone"]
                                p["text"] = oct_prokeimena[t_num]["text"]
                                p["verse"] = oct_prokeimena[t_num]["verse"]

                        # 2. Horologion Daily Liturgy Prokeimena
                        elif "horologion" in ref_k or "weekday" in ref_k:
                            dow = context.get("day_of_week", 1)
                            m_d = re.search(r'day_(\d+)', ref_k)
                            if m_d:
                                dow = int(m_d.group(1))
                            horo_prokeimena = {
                                1: {"tone": 4, "text": "He makes His angels spirits, and His ministers a flame of fire.", "verse": "Bless the Lord, O my soul; O Lord my God, You are very great."},
                                2: {"tone": 7, "text": "The righteous man shall rejoice in the Lord, and shall hope in Him.", "verse": "Hear my voice, O God, when I make my prayer to You."},
                                3: {"tone": 3, "text": "My soul magnifies the Lord, and my spirit rejoices in God my Savior.", "verse": "For He has regarded the lowliness of His handmaiden; for behold, henceforth all generations shall call me blessed."},
                                4: {"tone": 8, "text": "Their proclamation has gone out into all the earth, and their words to the ends of the universe.", "verse": "The heavens declare the glory of God, and the firmament proclaims the work of His hands."},
                                5: {"tone": 7, "text": "Exalt the Lord our God, and worship at His footstool, for He is holy.", "verse": "The Lord reigns, let the peoples tremble."},
                                6: {"tone": 8, "text": "Be glad in the Lord and rejoice, you righteous.", "verse": "Blessed are they whose iniquities are forgiven, and whose sins are covered."},
                                0: {"tone": 8, "text": "Make vows and pay them to the Lord our God.", "verse": "In Judah God is known; His name is great in Israel."}
                            }
                            if dow in horo_prokeimena:
                                p["tone"] = horo_prokeimena[dow]["tone"]
                                p["text"] = horo_prokeimena[dow]["text"]
                                p["verse"] = horo_prokeimena[dow]["verse"]

                        # 3. Specific Feasts & Common of Saints
                        if not p.get("text"):
                            if any(w in combined_info for w in ["archangel", "michael", "gabriel", "bodiless"]):
                                p["tone"] = 4
                                p["text"] = "He makes His angels spirits, and His ministers a flame of fire."
                                p["verse"] = "Bless the Lord, O my soul; O Lord my God, You are very great."
                            elif any(w in combined_info for w in ["fathers", "council", "councils"]):
                                p["tone"] = 4
                                p["text"] = "Blessed are You, O Lord, the God of our fathers, and praised and glorified is Your name forever."
                                p["verse"] = "For You are righteous in all that You have done for us."
                            elif any(w in combined_info for w in ["nativity", "dec_25", "dec_31"]):
                                p["tone"] = p.get("tone") or 8
                                p["text"] = "Let all the earth worship You and sing to You, let it sing to Your name, O Most High."
                                p["verse"] = "Shout to God, all the earth; sing to the honor of His name, give glory to His praise."
                            elif any(w in combined_info for w in ["exaltation_cross", "cross", "maccabees"]):
                                p["tone"] = p.get("tone") or 7
                                p["text"] = "Exalt the Lord our God, and worship at His footstool, for He is holy."
                                p["verse"] = "The Lord reigns, let the peoples tremble."
                            elif any(w in combined_info for w in ["forerunner", "baptist", "sept_23"]):
                                p["tone"] = p.get("tone") or 7
                                p["text"] = "The righteous man shall rejoice in the Lord, and shall hope in Him."
                                p["verse"] = "Hear my voice, O God, when I make my prayer to You."
                            elif any(w in combined_info for w in ["apostle", "theologian", "evangelist", "peter", "paul", "john", "andrew", "james", "philip", "bartholomew", "thomas", "matthew", "luke", "mark"]):
                                p["tone"] = p.get("tone") or 8
                                p["text"] = "Their proclamation has gone out into all the earth, and their words to the ends of the universe."
                                p["verse"] = "The heavens declare the glory of God, and the firmament proclaims the work of His hands."
                            elif any(w in combined_info for w in ["unmercenar", "cosmas", "damian", "nov_01"]) or ("plural_saints" in combined_info and any(w in combined_info for w in ["martyr", "passion-bearer", "great-martyr", "hieromartyr"])):
                                p["tone"] = 4
                                p["text"] = "To the saints that are in His earth, in them the Lord has magnified all His will."
                                p["verse"] = "I foresaw the Lord always before me, for He is at my right hand, that I may not be shaken."
                            elif any(w in combined_info for w in ["martyr", "passion-bearer", "great-martyr"]):
                                p["tone"] = p.get("tone") or 7
                                p["text"] = "The righteous man shall rejoice in the Lord and shall hope in Him."
                                p["verse"] = "Hear my voice, O God, when I make my prayer to You."
                            elif any(w in combined_info for w in ["hierarch", "bishop", "chrysostom", "basil", "nicholas"]):
                                p["tone"] = p.get("tone") or 1
                                p["text"] = "My mouth shall speak wisdom, and the meditation of my heart shall be understanding."
                                p["verse"] = "Hear this, all you nations; give ear, all you inhabitants of the earth."
                            elif any(w in combined_info for w in ["venerable", "monk", "abbot", "chariton", "sabbas"]):
                                p["tone"] = p.get("tone") or 7
                                p["text"] = "Precious in the sight of the Lord is the death of His saints."
                                p["verse"] = "What shall I render to the Lord for all His benefits toward me?"
                            elif any(w in combined_info for w in ["theotokos", "dormition", "annunciation", "nativity_theotokos", "entry_theotokos", "protection"]):
                                p["tone"] = p.get("tone") or 3
                                p["text"] = "My soul magnifies the Lord, and my spirit rejoices in God my Savior."
                                p["verse"] = "For He has regarded the lowliness of His handmaiden; for behold, henceforth all generations shall call me blessed."
                            elif any(w in combined_info for w in ["prophet"]):
                                p["tone"] = p.get("tone") or 4
                                p["text"] = "You are a priest forever according to the order of Melchizedek."
                                p["verse"] = "The Lord said to my Lord: Sit at My right hand, until I make Your enemies Your footstool."
                            else:
                                # Universal tone fallback
                                t_num = p.get("tone") or context.get("tone") or 8
                                if t_num in oct_prokeimena:
                                    p["tone"] = oct_prokeimena[t_num]["tone"]
                                    p["text"] = oct_prokeimena[t_num]["text"]
                                    p["verse"] = oct_prokeimena[t_num]["verse"]
                    if not p.get("tone"):
                        p_txt_low = (p.get("text") or "").lower()
                        if "angels spirits" in p_txt_low or any(w in combined_info for w in ["archangel", "michael", "gabriel", "bodiless"]):
                            p["tone"] = 4
                        elif "mouth shall speak wisdom" in p_txt_low:
                            p["tone"] = 1
                        elif "soul magnifies the lord" in p_txt_low:
                            p["tone"] = 3
                        elif "saints that are in his earth" in p_txt_low or "priest forever" in p_txt_low or "god of our fathers" in p_txt_low:
                            p["tone"] = 4
                        elif "proclamation has gone out" in p_txt_low or "be glad in the lord" in p_txt_low:
                            p["tone"] = 8
                        else:
                            p["tone"] = 7
                if "alleluia" in r and isinstance(r["alleluia"], dict):
                    a = r["alleluia"]
                    if not a.get("text") and a.get("ref_key"):
                        asset = self.get_text(a["ref_key"], context=context)
                        if asset and not (isinstance(asset, dict) and asset.get("is_missing")):
                            raw_c = asset.get("content")
                            if isinstance(raw_c, str):
                                a["text"] = raw_c
                            elif isinstance(raw_c, dict):
                                a["text"] = raw_c.get("text") or raw_c.get("content")
                                if raw_c.get("verses"):
                                    a["verses"] = raw_c["verses"]
                            if asset.get("tone") and not a.get("tone"):
                                a["tone"] = asset["tone"]
                    # Split embedded "verse:" lines if present in a["text"]
                    if isinstance(a.get("text"), str) and "verse:" in a["text"].lower():
                        extracted_v = []
                        rem_lines = []
                        for ln in a["text"].splitlines():
                            ln_s = ln.strip()
                            if not ln_s:
                                continue
                            if ln_s.lower().startswith("verse:"):
                                v_val = re.sub(r'^verse:\s*', '', ln_s, flags=re.IGNORECASE).strip()
                                if v_val:
                                    extracted_v.append(v_val)
                            else:
                                rem_lines.append(ln_s)
                        if extracted_v and not a.get("verses"):
                            a["verses"] = extracted_v
                        a["text"] = " ".join(rem_lines).strip() if rem_lines else None
                    # Fallback hydration from Octoechos, Horologion, Feasts, and Common of Saints
                    ref_k = a.get("ref_key", "").lower()
                    combined_info = _build_reading_combined_info(ref_k)
                    if not a.get("text") and not a.get("verses"):

                        # 1. Octoechos Sunday Resurrection Alleluias
                        oct_alleluias = {
                            1: {"tone": 1, "verses": ["God gives vengeance to me and subdues peoples under me.", "He magnifies the salvation of His king and shows mercy to His anointed, to David and to his seed forever."]},
                            2: {"tone": 2, "verses": ["The Lord hear you in the day of trouble; the name of the God of Jacob protect you.", "O Lord, save the king, and hear us in the day when we call."]},
                            3: {"tone": 3, "verses": ["In You, O Lord, have I hoped, let me never be ashamed.", "Be to me a God of defense and a house of refuge to save me."]},
                            4: {"tone": 4, "verses": ["Bend your bow and go forth and prosper and reign, for the sake of truth and meekness and righteousness.", "You have loved righteousness and hated iniquity."]},
                            5: {"tone": 5, "verses": ["I will sing of the mercies of the Lord forever; with my mouth will I make known Your truth to all generations.", "For You have said: Mercy shall be built up forever; Your truth shall be established in the heavens."]},
                            6: {"tone": 6, "verses": ["He who dwells in the help of the Most High shall abide under the shadow of the God of heaven.", "He shall say to the Lord: You are my protector and my refuge, my God, in Him will I hope."]},
                            7: {"tone": 7, "verses": ["It is good to give thanks to the Lord, and to sing praises to Your name, O Most High.", "To proclaim Your mercy in the morning, and Your truth by night."]},
                            8: {"tone": 8, "verses": ["Come, let us rejoice in the Lord, let us shout with joy to God our Savior.", "Let us come before His face with thanksgiving, and shout with joy to Him with psalms."]}
                        }
                        if "octoechos" in ref_k or (context.get("day_of_week") == 0 and "alleluia" in ref_k and "menaion" not in ref_k):
                            m_t = re.search(r'tone_(\d+)', ref_k)
                            t_num = int(m_t.group(1)) if m_t else (a.get("tone") or context.get("tone") or 1)
                            if t_num in oct_alleluias:
                                a["tone"] = oct_alleluias[t_num]["tone"]
                                a["verses"] = oct_alleluias[t_num]["verses"]

                        # 2. Horologion Daily Liturgy Alleluias
                        elif "horologion" in ref_k or "weekday" in ref_k:
                            dow = context.get("day_of_week", 1)
                            m_d = re.search(r'day_(\d+)', ref_k)
                            if m_d:
                                dow = int(m_d.group(1))
                            horo_alleluias = {
                                1: {"tone": 2, "verses": ["Praise the Lord from the heavens, praise Him in the heights.", "Praise Him, all His angels; praise Him, all His hosts."]},
                                2: {"tone": 4, "verses": ["The righteous man shall flourish like a palm tree, and grow like a cedar in Lebanon.", "Planted in the house of the Lord, they shall flourish in the courts of our God."]},
                                3: {"tone": 8, "verses": ["Hear, O daughter, and see, and incline your ear; forget your people and your father's house.", "The rich among the people shall entreat your favor."]},
                                4: {"tone": 1, "verses": ["The heavens shall confess Your wonders, O Lord, and Your truth in the congregation of the saints.", "God is glorified in the council of the saints."]},
                                5: {"tone": 1, "verses": ["Remember Your congregation, which You purchased of old.", "God is our King before the ages; He has worked salvation in the midst of the earth."]},
                                6: {"tone": 4, "verses": ["The righteous cried, and the Lord heard them, and delivered them from all their afflictions.", "Many are the afflictions of the righteous, but the Lord delivers them out of them all."]},
                                0: {"tone": 8, "verses": ["Come, let us rejoice in the Lord, let us shout with joy to God our Savior.", "Let us come before His face with thanksgiving, and shout with joy to Him with psalms."]}
                            }
                            if dow in horo_alleluias:
                                a["tone"] = horo_alleluias[dow]["tone"]
                                a["verses"] = horo_alleluias[dow]["verses"]

                        # 3. Specific Feasts & Common of Saints
                        if not a.get("verses") and not a.get("text"):
                            if any(w in combined_info for w in ["archangel", "michael", "gabriel", "bodiless"]):
                                a["tone"] = 5
                                a["verses"] = [
                                    "Praise the Lord from the heavens, praise Him in the heights.",
                                    "Praise Him, all His angels; praise Him, all His hosts."
                                ]
                            elif any(w in combined_info for w in ["fathers", "council", "councils"]):
                                a["tone"] = 1
                                a["verses"] = [
                                    "The God of gods, the Lord, has spoken, and called the earth from the rising of the sun to the going down thereof.",
                                    "Gather His saints to Him, those who have made a covenant with Him by sacrifice."
                                ]
                            elif any(w in combined_info for w in ["nativity", "dec_25", "dec_31"]):
                                a["tone"] = a.get("tone") or 1
                                a["verses"] = [
                                    "The heavens declare the glory of God, and the firmament proclaims the work of His hands.",
                                    "Day to day utters speech, and night to night proclaims knowledge."
                                ]
                            elif any(w in combined_info for w in ["exaltation_cross", "cross", "maccabees"]):
                                a["tone"] = a.get("tone") or 1
                                a["verses"] = [
                                    "Remember Your congregation, which You purchased of old.",
                                    "God is our King before the ages; He has worked salvation in the midst of the earth."
                                ]
                            elif any(w in combined_info for w in ["forerunner", "baptist", "sept_23"]):
                                a["tone"] = a.get("tone") or 4
                                a["verses"] = [
                                    "The righteous man shall flourish like a palm tree, and grow like a cedar in Lebanon.",
                                    "Planted in the house of the Lord, they shall flourish in the courts of our God."
                                ]
                            elif any(w in combined_info for w in ["unmercenar", "cosmas", "damian", "nov_01"]):
                                a["tone"] = 2
                                a["verses"] = [
                                    "Behold now, what is so good or what is so pleasant as for brethren to dwell together in unity?",
                                    "For there the Lord commanded the blessing, and life forevermore."
                                ]
                            elif any(w in combined_info for w in ["apostle", "theologian", "evangelist", "peter", "paul", "john", "andrew", "james", "philip", "bartholomew", "thomas", "matthew", "luke", "mark"]):
                                a["tone"] = a.get("tone") or 1
                                a["verses"] = [
                                    "The heavens shall confess Your wonders, O Lord, and Your truth in the congregation of the saints.",
                                    "God is glorified in the council of the saints."
                                ]
                            elif "plural_saints" in combined_info and any(w in combined_info for w in ["martyr", "passion-bearer", "great-martyr", "hieromartyr"]):
                                a["tone"] = 4
                                a["verses"] = [
                                    "The righteous cried, and the Lord heard them, and delivered them from all their afflictions.",
                                    "Many are the afflictions of the righteous, but the Lord delivers them out of them all."
                                ]
                            elif any(w in combined_info for w in ["martyr", "passion-bearer", "great-martyr"]):
                                a["tone"] = a.get("tone") or 4
                                a["verses"] = [
                                    "The righteous man shall flourish like a palm tree, and grow like a cedar in Lebanon.",
                                    "Planted in the house of the Lord, they shall flourish in the courts of our God."
                                ]
                            elif any(w in combined_info for w in ["hierarch", "bishop", "chrysostom", "basil", "nicholas"]):
                                a["tone"] = a.get("tone") or 2
                                a["verses"] = [
                                    "The mouth of the righteous man shall meditate wisdom, and his tongue shall speak of judgment.",
                                    "The law of his God is in his heart, and his steps shall not stumble."
                                ]
                            elif any(w in combined_info for w in ["venerable", "monk", "abbot", "chariton", "sabbas"]):
                                a["tone"] = a.get("tone") or 6
                                a["verses"] = [
                                    "Blessed is the man who fears the Lord, who greatly delights in His commandments.",
                                    "His descendants shall be mighty upon the earth; the generation of the upright shall be blessed."
                                ]
                            elif any(w in combined_info for w in ["theotokos", "dormition", "annunciation", "nativity_theotokos", "entry_theotokos", "protection"]):
                                a["tone"] = a.get("tone") or 8
                                a["verses"] = [
                                    "Hear, O daughter, and see, and incline your ear; forget your people and your father's house.",
                                    "The rich among the people shall entreat your favor."
                                ]
                            elif any(w in combined_info for w in ["prophet"]):
                                a["tone"] = a.get("tone") or 5
                                a["verses"] = [
                                    "Moses and Aaron among His priests, and Samuel among those who call upon His name.",
                                    "They called upon the Lord, and He answered them."
                                ]
                            else:
                                # Universal tone fallback
                                t_num = a.get("tone") or context.get("tone") or 1
                                if t_num in oct_alleluias:
                                    a["tone"] = oct_alleluias[t_num]["tone"]
                                    a["verses"] = oct_alleluias[t_num]["verses"]
                    if not a.get("tone"):
                        a_v_low = " ".join(a.get("verses") or [a.get("text") or ""]).lower()
                        if "praise the lord from the heavens" in a_v_low or any(w in combined_info for w in ["archangel", "michael", "gabriel", "bodiless"]):
                            a["tone"] = 5
                        elif "heavens shall confess" in a_v_low or "remember your congregation" in a_v_low or "god of gods" in a_v_low:
                            a["tone"] = 1
                        elif "mouth of the righteous" in a_v_low or "dwell together in unity" in a_v_low:
                            a["tone"] = 2
                        elif "blessed is the man who fears" in a_v_low:
                            a["tone"] = 6
                        elif "hear, o daughter" in a_v_low:
                            a["tone"] = 8
                        else:
                            a["tone"] = 4
            return res_obj

        if context.get("_almanac_used"):
            readings_val = context.get("readings")
            if isinstance(readings_val, dict):
                return _hydrate_all_readings(copy.deepcopy(readings_val))
            
            # If readings key was overwritten by a string key in the variables merge,
            # query the original pre-computed readings dictionary from the almanac.
            year = context.get("year")
            month = context.get("month")
            day = context.get("day")
            if year and month and day:
                date_str = f"{year}-{int(month):02d}-{int(day):02d}"
                almanac = self._get_almanac(year)
                if almanac and date_str in almanac.get("days", {}):
                    orig_readings = almanac["days"][date_str].get("readings")
                    if isinstance(orig_readings, dict):
                        return _hydrate_all_readings(copy.deepcopy(orig_readings))

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
        if l_readings and l_readings not in (["day_current"], "day_current"):
            if isinstance(l_readings, list):
                if l_readings and isinstance(l_readings[0], str):
                    s_id = feast_id
                    if not s_id and saints:
                        s_id = saints[0].get("id", "")
                    if not s_id:
                        month_val = context.get("month")
                        day_val = context.get("day")
                        if month_val and day_val:
                            try:
                                month_int = int(month_val)
                                day_int = int(day_val)
                                months_map = {1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "may", 6: "jun",
                                              7: "jul", 8: "aug", 9: "sep", 10: "oct", 11: "nov", 12: "dec"}
                                month_str = months_map.get(month_int, "jan")
                                s_id = f"{month_str}_{day_int:02d}"
                            except ValueError:
                                pass
                    
                    gospel_books = ("matthew", "mark", "luke", "john")
                    epistles = [k for k in l_readings if not any(k.lower().startswith(g) for g in gospel_books)]
                    gospels = [k for k in l_readings if any(k.lower().startswith(g) for g in gospel_books)]
                    
                    if epistles or gospels:
                        count = max(len(epistles), len(gospels))
                        normalized_readings = []
                        for i in range(count):
                            ep_key = epistles[i] if i < len(epistles) else ""
                            g_key = gospels[i] if i < len(gospels) else ""
                            normalized_readings.append({
                                "prokeimenon": {
                                    "source": "menaion",
                                    "ref_key": f"menaion.{s_id}.prokeimenon" if s_id else ""
                                },
                                "epistle": {
                                    "source": "menaion",
                                    "ref_key": ep_key
                                },
                                "alleluia": {
                                    "source": "menaion",
                                    "ref_key": f"menaion.{s_id}.alleluia" if s_id else ""
                                },
                                "gospel": {
                                    "source": "menaion",
                                    "ref_key": g_key
                                }
                            })
                    else:
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
            elif isinstance(l_readings, dict):
                if "readings" in l_readings:
                    normalized_readings = l_readings["readings"]
                else:
                    normalized_readings = [l_readings]
            else:
                normalized_readings = l_readings

        pascha_off = context.get("pascha_offset")
        if pascha_off is not None and 1 <= pascha_off <= 6:
            bright_readings = {
                1: {
                    "prokeimenon": {"tone": 8, "text": "Their proclamation has gone out into all the earth, and their words to the ends of the universe.", "ref_key": "triodion.bright_monday.prokeimenon"},
                    "epistle": {"text": "Acts 1:12–17, 21–26", "ref_key": "acts_1_12_17_21_26"},
                    "alleluia": {"tone": 1, "text": "The heavens shall confess Your wonders, O Lord, and Your truth in the congregation of the saints.", "ref_key": "triodion.bright_monday.alleluia"},
                    "gospel": {"text": "John 1:18–28", "ref_key": "john_1_18_28"}
                },
                2: {
                    "prokeimenon": {"tone": 3, "text": "My soul magnifies the Lord, and my spirit has rejoiced in God my Savior.", "ref_key": "triodion.bright_tuesday.prokeimenon"},
                    "epistle": {"text": "Acts 2:14–21", "ref_key": "acts_2_14_21"},
                    "alleluia": {"tone": 2, "text": "Arise, O Lord, into Your rest, You and the ark of Your holiness.", "ref_key": "triodion.bright_tuesday.alleluia"},
                    "gospel": {"text": "Luke 24:12–35", "ref_key": "luke_24_12_35"}
                },
                3: {
                    "prokeimenon": {"tone": 6, "text": "I will remember Your name in every generation.", "ref_key": "triodion.bright_wednesday.prokeimenon"},
                    "epistle": {"text": "Acts 2:22–36", "ref_key": "acts_2_22_36"},
                    "alleluia": {"tone": 1, "text": "The heavens shall confess Your wonders, O Lord.", "ref_key": "triodion.bright_wednesday.alleluia"},
                    "gospel": {"text": "John 1:35–51", "ref_key": "john_1_35_51"}
                },
                4: {
                    "prokeimenon": {"tone": 3, "text": "Sing praises to our God, sing praises; sing praises to our King, sing praises.", "ref_key": "triodion.bright_thursday.prokeimenon"},
                    "epistle": {"text": "Acts 2:38–43", "ref_key": "acts_2_38_43"},
                    "alleluia": {"tone": 4, "text": "Bend Your bow, and proceed prosperously, and reign.", "ref_key": "triodion.bright_thursday.alleluia"},
                    "gospel": {"text": "John 3:1–15", "ref_key": "john_3_1_15"}
                },
                5: {
                    "prokeimenon": {"tone": 8, "text": "Their proclamation has gone out into all the earth.", "ref_key": "triodion.bright_friday.prokeimenon"},
                    "epistle": {"text": "Acts 3:1–8", "ref_key": "acts_3_1_8"},
                    "alleluia": {"tone": 1, "text": "The heavens shall confess Your wonders, O Lord.", "ref_key": "triodion.bright_friday.alleluia"},
                    "gospel": {"text": "John 2:12–22", "ref_key": "john_2_12_22"}
                },
                6: {
                    "prokeimenon": {"tone": 3, "text": "The Lord is my light and my salvation; whom shall I fear?", "ref_key": "triodion.bright_saturday.prokeimenon"},
                    "epistle": {"text": "Acts 3:11–16", "ref_key": "acts_3_11_16"},
                    "alleluia": {"tone": 4, "text": "The Lord reigns, He is robed in majesty.", "ref_key": "triodion.bright_saturday.alleluia"},
                    "gospel": {"text": "John 3:22–33", "ref_key": "john_3_22_33"}
                }
            }
            if pascha_off in bright_readings:
                return _hydrate_all_readings({"type": "liturgy_readings", "readings": [bright_readings[pascha_off]]})

        has_proper_saint_readings = (
            rank <= 3
            or context.get("dolnytsky_rank_code") in ("[4 A+G]", "[6 SM]", "[GT DOX]", "[POL]", "[VIGIL]")
            or any(isinstance(s, dict) and s.get("rank_code") in ("[4 A+G]", "[6 SM]", "[GT DOX]", "[POL]", "[VIGIL]") for s in saints)
        )
        has_sunday_liturgy_saint = (
            rank <= 3
            or context.get("dolnytsky_rank_code") in ("[GT DOX]", "[POL]", "[VIGIL]")
            or any(isinstance(s, dict) and s.get("rank_code") in ("[GT DOX]", "[POL]", "[VIGIL]") for s in saints)
        )
        is_fore_or_after = bool(
            context.get("is_afterfeast") or
            context.get("is_forefeast") or
            context.get("is_apodosis") or
            context.get("is_fore_or_afterfeast")
        )
        if 1 <= day_of_week <= 6 and rank > 3 and context.get("dolnytsky_rank_code") in ("[4 TR]", "[4 NO]") and not has_proper_saint_readings and not is_fore_or_after:
            normalized_readings = None

        # Dolnytsky §3.10.2: On weekdays or Saturdays with a Polyeleos or Vigil saint (rank 2 or 3),
        # Divine Liturgy combines the readings of the day with the saint's proper readings.
        if day_of_week != 0:
            if rank > 3 and normalized_readings and not (1 <= day_of_week <= 5 and has_proper_saint_readings and len(normalized_readings) == 1):
                return _hydrate_all_readings({"type": "liturgy_readings", "readings": normalized_readings})
            elif is_special_vigil_weekday:
                # Suppress daily readings on weekdays, saint readings only
                if normalized_readings:
                    return _hydrate_all_readings({"type": "liturgy_readings", "readings": normalized_readings})
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
                return _hydrate_all_readings(result)
        else: # Sunday (day_of_week == 0)
            if normalized_readings and rank > 3 and len(normalized_readings) >= 2:
                return _hydrate_all_readings({"type": "liturgy_readings", "readings": normalized_readings})

        result = {
            "type": "liturgy_readings",
            "readings": []
        }
        
        # GREAT FEAST: Feast readings only
        is_great_feast = (
            rank == 1 or
            (context.get("dolnytsky_rank") in ("LORD", "THEOTOKOS") and not is_fore_or_after) or
            (context.get("feast_level") in ("lord", "theotokos") and not is_fore_or_after) or
            context.get("feast_id") in ("palm_sunday", "pascha", "pentecost") or
            paradigm in ["p_feast_lord", "p_feast_theotokos"]
        )
        if is_great_feast:
            if normalized_readings:
                return _hydrate_all_readings({"type": "liturgy_readings", "readings": normalized_readings})
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
            return _hydrate_all_readings(result)
        
        # SUNDAY: Resurrectional readings + Saint readings if [GT DOX], [POL], or [VIGIL]
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
            
            # Secondary: Saint of the day (if [GT DOX], [POL], [VIGIL]) or explicit normalized_readings
            if has_sunday_liturgy_saint:
                if normalized_readings:
                    result["readings"].extend(normalized_readings)
                elif saints:
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
            elif is_fore_or_after and normalized_readings:
                result["readings"].extend(normalized_readings)
            
            return _hydrate_all_readings(result)
        
        # WEEKDAY
        if day_of_week != 0:
            # Weekday lectionary first
            p_res = self.resolve_prokeimenon(context)
            p_tone = p_res.get("tone", 1)
            # Dynamic sequential readings calculation
            ep_text, gosp_text = None, None
            weeks_after_pentecost = context.get("weeks_after_pentecost")
            if weeks_after_pentecost is not None:
                wk_pair = self._get_weekday_lectionary_reading(weeks_after_pentecost, day_of_week)
                if wk_pair:
                    ep_text, gosp_text = wk_pair

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
            elif context.get("is_afterfeast") or context.get("is_apodosis"):
                feast_level = context.get("feast_level")
                feast_id = context.get("feast_id")
                if feast_level == "theotokos":
                    p_source = "feast"
                    p_ref = f"menaion.{feast_id}.prokeimenon" if feast_id else "theotokos.prokeimenon"
                    p_tone_val = 3
                    p_text = "My soul magnifies the Lord, and my spirit rejoices in God my Savior."
                    a_source = "feast"
                    a_ref = f"menaion.{feast_id}.alleluia" if feast_id else "theotokos.alleluia"
                    a_tone_val = 8
                    a_verses = [
                        "Hear, O daughter, and see, and incline your ear",
                        "The rich among the people shall entreat your favor"
                    ]
                else:
                    p_source = "feast"
                    p_ref = f"menaion.{feast_id}.prokeimenon" if feast_id else "feast.prokeimenon"
                    p_tone_val = p_tone
                    p_text = None
                    a_source = "feast"
                    a_ref = f"menaion.{feast_id}.alleluia" if feast_id else "feast.alleluia"
                    a_tone_val = p_tone
                    a_verses = None
            else:
                p_source = "horologion"
                p_ref = f"horologion.prokeimenon.day_{day_of_week}"
                p_tone_val = p_tone
                p_text = None
                a_source = "horologion"
                a_ref = f"horologion.alleluia.day_{day_of_week}"
                a_tone_val = p_tone
                a_verses = None

            is_apodosis_day = bool(
                context.get("is_apodosis") or
                context.get("period") == "apodosis" or
                context.get("dolnytsky_rank") == "apodosis"
            )
            if is_apodosis_day and normalized_readings:
                # Dolnytsky §2.20:1772 & §3.3.4:2340: Weekday Apodosis takes the Feast readings alone
                ep_obj = normalized_readings[0].get("epistle", {})
                gosp_obj = normalized_readings[0].get("gospel", {})
                ep_k = ep_obj.get("ref_key", "") if isinstance(ep_obj, dict) else str(ep_obj)
                gosp_k = gosp_obj.get("ref_key", "") if isinstance(gosp_obj, dict) else str(gosp_obj)
                result["readings"].append({
                    "prokeimenon": {
                        "source": p_source,
                        "ref_key": p_ref,
                        "tone": p_tone_val,
                        "text": p_text
                    },
                    "epistle": {
                        "source": "feast",
                        "ref_key": ep_k or "hebrews_9_1_7",
                        "text": self._format_scripture_key(ep_k or "hebrews_9_1_7")
                    },
                    "alleluia": {
                        "source": a_source,
                        "ref_key": a_ref,
                        "tone": a_tone_val,
                        "verses": a_verses
                    },
                    "gospel": {
                        "source": "feast",
                        "ref_key": gosp_k or "luke_10_38_42_11_27_28",
                        "text": self._format_scripture_key(gosp_k or "luke_10_38_42_11_27_28")
                    }
                })
                return _hydrate_all_readings(result)

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

            # Saint's readings second (when rank <= 3 or Dolnytsky assigns [4 A+G], [6 SM], [GT DOX], [POL], [VIGIL])
            has_proper_saint_readings = (
                rank <= 3
                or context.get("dolnytsky_rank_code") in ("[4 A+G]", "[6 SM]", "[GT DOX]", "[POL]", "[VIGIL]")
                or any(isinstance(s, dict) and s.get("rank_code") in ("[4 A+G]", "[6 SM]", "[GT DOX]", "[POL]", "[VIGIL]") for s in saints)
            )
            if normalized_readings:
                result["readings"].extend(normalized_readings)
            elif saints and has_proper_saint_readings:
                reading_saint = next(
                    (s for s in saints if isinstance(s, dict) and s.get("rank_code") in ("[4 A+G]", "[6 SM]", "[GT DOX]", "[POL]", "[VIGIL]")),
                    saints[0],
                )
                saint_id = reading_saint.get("id", "saint")
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
        
        return _hydrate_all_readings(result)

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


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:1.2.1,L370-385")
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


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:1.2.1,L370-385")
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


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:1.2.1,L370-385")
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


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:2.2,L1053-1068")
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

        beat_dist = context.get("beatitudes_distribution") or context.get("variables", {}).get("beatitudes_distribution")
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
            if (context.get("is_afterfeast") or context.get("is_apodosis")) and context.get("feast_level") != "lord" and context.get("dolnytsky_rank") != "LORD":
                return {
                    "type": "beatitudes",
                    "stichera": [
                        {"source": "octoechos", "count": 4},
                        {"source": "feast", "count": 4},
                    ],
                    "note": "4 Octoechos + 4 Feast Ode 6",
                }
            has_poly_saint = rank <= 3 or any(
                parse_rank_integer(s.get("rank", 5)) <= 3 for s in context.get("saints", [])
            )
            if (
                has_poly_saint
                and context.get("has_polyeleos") is not False
                and context.get("variables", {}).get("has_polyeleos") is not False
                and context.get("feast_level") != "lord"
                and context.get("dolnytsky_rank") != "LORD"
            ):
                return {
                    "type": "beatitudes",
                    "stichera": [
                        {"source": "octoechos", "count": 4},
                        {"source": "menaion", "count": 4},
                    ],
                    "note": "Sunday and Saint Beatitudes",
                }
            return {"type": "beatitudes", "stichera": [{"source": "octoechos", "count": 4}], "note": "Sunday Beatitudes"}
            
        has_poly = context.get("has_polyeleos") is not False and context.get("variables", {}).get("has_polyeleos") is not False
        if rank <= 3 and (has_poly or rank <= 2):
            return {"type": "beatitudes", "stichera": [{"source": "menaion", "count": 8}], "note": "Festal Beatitudes (4 from Ode III and 4 from Ode VI)"}
            
        return {"type": "third_antiphon", "note": "Usual Third Antiphon without stichera"}


    @liturgical_source(dolnytsky="Dolnytsky_Typikon_Master.md:2.5,L1211-1216")
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
