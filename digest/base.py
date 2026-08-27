import json
import os
import re
import copy
from datetime import datetime


class DigestGeneratorBase:
    def __init__(self, engine, include_ceremonial=False):
        self.engine = engine
        self.mode = "full"
        self.include_ceremonial = include_ceremonial


    def _roman_tone(self, tone):
        try:
            val = int(tone)
            return {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII"}.get(val, str(val))
        except (ValueError, TypeError):
            return str(tone)


    def _is_missing(self, item):
        if not item:
            return True
        if isinstance(item, dict):
            if item.get("is_missing"):
                return True
            for k in ("content", "text"):
                val = item.get(k)
                if val and self._is_missing(val):
                    return True
            return False
        if isinstance(item, str):
            item_strip = item.strip()
            if not item_strip:
                return True
            if item_strip.startswith("[") and item_strip.endswith("]"):
                item_lower = item_strip.lower()
                if "missing" in item_lower or "stub" in item_lower or "error" in item_lower:
                    return True
            if "missing in" in item_strip.lower():
                return True
            if "missing text" in item_strip.lower():
                return True
            if "missing logic" in item_strip.lower():
                return True
            if "logic missing" in item_strip.lower():
                return True
            if "missing_data" in item_strip.lower():
                return True
            if "missing_litany" in item_strip.lower():
                return True
        return False



    def _capitalize_name(self, name):
        if not name:
            return ""
        name = name.strip().rstrip('.').strip()
        small_words = {"of", "the", "in", "and", "a", "an", "on", "at", "to", "for", "with", "from", "by", "over", "under", "about", "into", "through", "that"}
        
        if name.lower().startswith("st. "):
            name = "St. " + name[4:]
        elif name.lower().startswith("st "):
            name = "St. " + name[3:]
            
        words = name.split()
        cap_words = []
        for i, w in enumerate(words):
            w_clean = w.lower().rstrip(',').rstrip('.').rstrip(';').rstrip(':')
            if i > 0 and w_clean in small_words and i < len(words) - 1:
                cap_words.append(w.lower())
            else:
                if '.' in w:
                    parts = w.split('.')
                    cap_parts = [p.capitalize() if p else "" for p in parts]
                    cap_words.append(".".join(cap_parts))
                elif '-' in w:
                    parts = w.split('-')
                    cap_parts = [p.capitalize() for p in parts]
                    cap_words.append("-".join(cap_parts))
                else:
                    cap_words.append(w.capitalize())
        return " ".join(cap_words)


    def _clean_name(self, name):
        if not name:
            return ""
        name = name.replace("**", "").strip().rstrip('.')
        if "Cyril, Archbishop of Alexandria" in name or "Cyril of Alexandria" in name:
            return "St. Cyril"
        
        titles = [
            "hieromartyr", "protomartyr", "great martyr", "greatmartyr", "venerable", "martyr",
            "apostle", "apostles", "ap.", "ap ", "archbishop", "bishop", "hierodeacon", "righteous",
            "prophet", "confessor", "unmercenary", "unmercenaries", "passion-bearer", "passionbearer", "holy"
        ]
        feast_words = [
            "nativity", "synaxis", "translation", "return", "transfer", "finding", "recovery", "protection",
            "entry", "meeting", "annunciation", "dormition", "transfiguration", "theophany",
            "elevation", "circumcision", "ascension", "pentecost", "pascha", "birth",
            "beheading", "memory", "repose", "conception", "commemoration", "placing", "deposition",
            "veneration", "miracle", "wonder", "relics", "icon", "robe", "cincture", "belt",
            "mid-pentecost", "sunday", "saturday", "weekday", "vigil", "feast", "fast"
        ]
        
        name_lower = name.lower()
        
        # Remove leading "St." or "St " if followed by a hierarchical title or a feast word
        if name_lower.startswith("st. ") or name_lower.startswith("st "):
            rest = name[4:].strip() if name_lower.startswith("st. ") else name[3:].strip()
            rest_lower = rest.lower()
            if any(t in rest_lower for t in titles) or any(w in rest_lower for w in feast_words):
                name = rest
                name_lower = name.lower()
                
        # Only prepend "St. " if no title is present, it doesn't already have it, and it's not a feast/event/day
        has_title = any(t in name_lower for t in titles)
        is_feast = any(w in name_lower for w in feast_words)
        if not has_title and not name_lower.startswith("st.") and not name_lower.startswith("st ") and not is_feast:
            name = "St. " + name
        return name


    def humanize_key(self, key):
        if not key:
            return ""
        if isinstance(key, dict):
            key = key.get('source', key.get('ref_key', ''))
        key = str(key).strip()
        
        # Scripture Key Formatting Check (e.g. "romans_13_11_14_4" -> "Romans 13:11-14:4")
        # Bypass this for database namespace/hierarchical keys (e.g. menaion.jun_13 or jun_13...)
        # Liturgical keys always contain a dot "." or start with "tone_" or common liturgical terms
        is_liturgical = (
            "." in key or 
            key.lower().startswith("tone_") or 
            "antiphon" in key.lower() or 
            "canon" in key.lower() or 
            "kathisma" in key.lower() or 
            "station" in key.lower() or 
            "ode" in key.lower() or 
            "heirmos" in key.lower() or 
            "tropar" in key.lower() or 
            "kontak" in key.lower() or 
            "doxast" in key.lower()
        )
        
        if not is_liturgical and any(char.isdigit() for char in key) and "_" in key:
            parts = [p for p in key.replace(".", "_").split("_") if p]
            book_parts = []
            num_parts = []
            for p in parts:
                if p.isdigit():
                    if book_parts and not p.isalpha():
                        num_parts.append(int(p))
                    else:
                        book_parts.append(p)
                else:
                    book_parts.append(p)
            if num_parts:
                book_name = " ".join(book_parts).title()
                # Handle leading numbers formatting like "2 Corinthians" instead of "2 Corinthians"
                if len(num_parts) == 4:
                    return f"{book_name} {num_parts[0]}:{num_parts[1]}-{num_parts[2]}:{num_parts[3]}"
                elif len(num_parts) == 3:
                    return f"{book_name} {num_parts[0]}:{num_parts[1]}-{num_parts[2]}"
                elif len(num_parts) == 6:
                    return f"{book_name} {num_parts[0]}:{num_parts[1]}-{num_parts[2]}, {num_parts[3]}-{num_parts[4]}, {num_parts[5]}"
                elif len(num_parts) == 5:
                    return f"{book_name} {num_parts[0]}:{num_parts[1]}-{num_parts[2]}, {num_parts[3]}-{num_parts[4]}"
                elif len(num_parts) == 2:
                    return f"{book_name} {num_parts[0]}:{num_parts[1]}"
                elif len(num_parts) == 1:
                    return f"{book_name} {num_parts[0]}"
                    
        if " " in key:
            return key.strip("*").strip(".")
        
        key_lower = key.lower()
        if key_lower == "triodion.doxasticon":
            return "doxasticon from the Triodion"
        if key_lower == "menaion.forefeast.doxasticon":
            return "doxasticon of the forefeast"
        if key_lower == "menaion.feast.doxasticon":
            return "doxasticon of the feast"
        if key_lower in ("dogmatikon_current_tone", "dogmatikon_tone_week") or "dogmatikon" in key_lower:
            return "Dogmatic Theotokion in the tone of the week"
        if key_lower == "menaion.feast.litiya.glory":
            return "doxasticon of the feast"
        if key_lower == "menaion.feast.litiya.both_now":
            return "both now of the feast"
        if key_lower == "pentecostarion.eucharist.vespers.theotokion_lord_i_call":
            return "Sticheron of the Feast (Eucharist)"
        if key_lower in ("feast_theotokion", "feast.theotokion"):
            return "Theotokion of the Feast"
        if key_lower == "pentecostarion.eucharist.exapostilarion":
            return "Exapostilarion of the Feast"
        if key_lower == "pentecostarion.eucharist.exapostilarion_theotokion":
            return "Theotokion of the Feast"
            
        # Strip trailing dot if present to prevent empty split parts
        if key.endswith('.'):
            key = key[:-1]
            
        # Extract the base part (after the last dot)
        parts = key.split('.')
        
        # Check if the key contains a fixed calendar date (e.g. jun_13 or jun_24)
        date_match = re.search(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)_(\d+)\b', key, re.IGNORECASE)
        fixed_saint_name = None
        is_exact_saint_id = False
        if date_match and hasattr(self, 'engine') and getattr(self.engine, 'dolnytsky_fixed', None):
            months_map = {
                "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
            }
            m_str = date_match.group(1).lower()
            day_val = int(date_match.group(2))
            month_val = months_map.get(m_str)
            if month_val:
                lookup_key = f"{month_val}-{day_val}"
                day_entry = self.engine.dolnytsky_fixed.get(lookup_key)
                if day_entry:
                    entries = day_entry.get("entries", [])
                    matched_entry = None
                    matched_suffix = None
                    if len(entries) > 1:
                        # Find the entry that matches the key
                        for entry in entries:
                            ent_desc = entry.get("description", "")
                            cleaned = re.sub(r'[^a-z0-9\s]', '', ent_desc.lower())
                            words = cleaned.split()
                            filt = [w for w in words if w not in ["apostles", "apostle", "holy", "saint", "saints", "venerable", "venerables", "hieromartyr", "martyr", "martyrs", "prophet", "and", "of", "the"]]
                            if not filt:
                                filt = words
                            suffix = "_".join(filt)
                            if suffix in key.lower():
                                matched_entry = entry
                                matched_suffix = suffix
                                break
                    if not matched_entry and entries:
                        matched_entry = entries[0]
                        ent_desc = matched_entry.get("description", "")
                        cleaned = re.sub(r'[^a-z0-9\s]', '', ent_desc.lower())
                        words = cleaned.split()
                        filt = [w for w in words if w not in ["apostles", "apostle", "holy", "saint", "saints", "venerable", "venerables", "hieromartyr", "martyr", "martyrs", "prophet", "and", "of", "the"]]
                        if not filt:
                            filt = words
                        matched_suffix = "_".join(filt)
                        
                    if matched_entry:
                        raw_desc = matched_entry.get("description", "")
                        fixed_saint_name = self._clean_name(raw_desc)
                        # Check if this is the exact saint ID (the last part of key matches suffix)
                        if parts and matched_suffix and parts[-1].lower() == matched_suffix.lower():
                            is_exact_saint_id = True

        if len(parts) >= 2 and parts[-1].lower() in ("troparion", "kontakion", "stichera", "doxastikon", "theotokion", "exapostilarion", "glory"):
            category = parts[-1].lower()
            subject = parts[-2]
            
            subject_human = fixed_saint_name
            if not subject_human:
                subject_map = {
                    "bartholomew_barnabas": "Apostles Bartholomew and Barnabas",
                    "eucharist": "the Feast",
                    "feast": "the Feast"
                }
                subject_human = subject_map.get(subject.lower())
                if not subject_human:
                    words = subject.replace('_', ' ').split()
                    capitalized_words = [w.capitalize() if w.lower() not in ('of', 'the', 'in', 'and', 'to', 'a', 'for', 'with', 'from', 'at') else w.lower() for w in words]
                    subject_human = " ".join(capitalized_words)
                    
            if category == "theotokion":
                return f"Theotokion of {subject_human}"
            if category == "glory":
                return f"Doxastikon of {subject_human}"
            return f"{category.capitalize()} of {subject_human}"
            
        if is_exact_saint_id and fixed_saint_name:
            return fixed_saint_name
            
        base = parts[-1] if parts else key
        
        # Tone numbers matching: e.g. tone_1 -> Tone 1
        tone_match = re.search(r'tone_(\d+)', base, re.IGNORECASE)
        if tone_match:
            tone_num = tone_match.group(1)
            base_cleaned = re.sub(r'_?tone_\d+', '', base, flags=re.IGNORECASE)
            if not base_cleaned and len(parts) > 1:
                base_cleaned = ".".join(parts[:-1])
            base_human = self.humanize_key(base_cleaned)
            if base_human:
                return f"{base_human} in Tone {tone_num}"
            else:
                return f"Tone {tone_num}"


        # Eothinon stichera matching: e.g. eothinon_1_stichera -> Gospel Sticheron I
        eothinon_match = re.match(r'eothinon_(\d+)_stichera', base, re.IGNORECASE)
        if eothinon_match:
            num = int(eothinon_match.group(1))
            romans = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
            roman = romans[num] if num < len(romans) else str(num)
            return f"Gospel Sticheron {roman}"
            
        # Eothinon exapostilarion matching
        ex_match = re.match(r'(?:eothinon_)?exapostilarion_(\d+)', base, re.IGNORECASE)
        if ex_match:
            num = int(ex_match.group(1))
            romans = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
            roman = romans[num] if num < len(romans) else str(num)
            return f"Gospel Exapostilarion {roman}"
            
        # Eothinon theotokion matching: matches eothinon_theotokion_x or exapostilarion_theotokion_x
        theo_match = re.match(r'(?:eothinon_|exapostilarion_)?theotokion_(\d+)', base, re.IGNORECASE)
        if theo_match:
            num = int(theo_match.group(1))
            romans = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
            roman = romans[num] if num < len(romans) else str(num)
            return f"Theotokion of Gospel Exapostilarion {roman}"

        mapping = {
            "antiphon_1_tone_4": "first Antiphon of Tone IV",
            "dogmatikon_current_tone": "Dogmatic Theotokion in the Tone of the week",
            "dogmatikon_tone_week": "Dogmatic Theotokion in the Tone of the week",
            "dogmatikon": "Dogmatic Theotokion",
            "theotokion_daily": "Theotokion from the Horologion or Octoechos",
            "stavrotheotokion": "Stavrotheotokion from the Horologion or Octoechos",
            "theotokion_horologion_or_octoechos": "Theotokion from the Horologion or Octoechos",
            "open_to_me_the_doors_of_repentance": "Open to me the doors of repentance",
            "on_the_paths_of_salvation": "On the paths of salvation",
            "when_i_think_of_the_many_evil_things_i_have_done": "When I think of the many evil things I have done",
            "saint_doxastikon_if_present": "Doxastikon of the Saint if present",
            "saint_doxastikon": "Doxastikon of the Saint",
            "saint": "Saint",
            "saint_1": "Saint",
            "saint_2": "Saint",
            "forefeast": "Forefeast",
            "afterfeast": "Afterfeast",
            "octoechos": "Octoechos",
            "triodion": "Triodion",
            "menaion": "Menaion",
            "horologion": "Horologion",
            "pentecostarion": "Pentecostarion",
            "apostol": "Apostol",
            "evangelion": "Evangelion",
            "resurrection": "Resurrection",
            "res": "Resurrectional",
            "resurrectional": "Resurrectional",
            "aposticha_theotokion": "Aposticha Theotokion",
            "aposticha_daily": "daily Aposticha",
            "sidalen": "Sessional Hymn",
            "kathisma": "Kathisma",
            "prokeimenon": "Prokeimenon",
            "psalm_92_lord_is_king": "The Lord is King (Psalm 92)",
            "alleluia": "Alleluia",
            "gospel": "Gospel",
            "epistle": "Epistle",
            "megalynarion": "Megalynarion",
            "canon": "Canon",
            "katavasia": "Katavasia",
            "exapostilarion": "Exapostilarion",
            "praises": "Praises",
            "dismissal": "Dismissal",
            "troparion": "Troparion",
            "kontakion": "Kontakion",
            "beatitudes": "Beatitudes",
            "typika": "Typika",
            "communion_hymn": "Communion Hymn",
            "kinonicon": "Communion Hymn",
            "litya": "Litiya",
            "artoklasia": "Artoklasia",
            "magnification": "Magnification",
            "polyeleos": "Polyeleos",
            "sessional_triodion_set_1": "Sessional Hymns of the Feast from the Triodion",
            "sessional_triodion_set_2": "Sessional Hymns of the Feast from the Triodion",
        }
        
        lower_base = base.lower()
        if lower_base in mapping:
            return mapping[lower_base]
            
        words = base.replace('_', ' ').split()
        capitalized_words = []
        for w in words:
            if w.lower() in ('of', 'the', 'in', 'and', 'to', 'a', 'for', 'with', 'from', 'at'):
                capitalized_words.append(w.lower())
            else:
                capitalized_words.append(w.capitalize())
        return " ".join(capitalized_words)


    def _lowercase_liturgical_terms(self, text):
        if not text:
            return text
        replacements = {
            "Prokimenon": "Prokeimenon",
            "prokimenon": "prokeimenon",
            "Prokimena": "Prokeimena",
            "prokimena": "prokeimena",
            "Doxasticon": "Doxastikon",
            "doxasticon": "doxastikon",
            "doxasticon of the Saint": "Doxastikon of the Saint",
            "doxasticon of the saint": "Doxastikon of the Saint",
            "doxastikon of the Saint": "Doxastikon of the Saint",
            "doxastikon of the saint": "Doxastikon of the Saint",
            "Glory... doxasticon of the Saint": "Glory... Doxastikon of the Saint",
            "Glory... doxasticon of the saint": "Glory... Doxastikon of the Saint",
            "Glory... doxastikon of the Saint": "Glory... Doxastikon of the Saint",
            "Glory... doxastikon of the saint": "Glory... Doxastikon of the Saint",
            "doxastikon of the feast": "Doxastikon of the Feast",
            "theotokion from the Horologion or Octoechos": "Theotokion from the Horologion or Octoechos",
            "theotokion from the Horologion": "Theotokion from the Horologion",
            "theotokion from the Octoechos": "Theotokion from the Octoechos",
            "dismissal theotokion": "Dismissal Theotokion",
            "troparion of the saint": "Troparion of the Saint",
            "troparion of the temple": "Troparion of the Temple",
            "troparion of the Cross": "Troparion of the Cross",
            "kontakion of the saint": "Kontakion of the Saint",
            "kontakion of the temple": "Kontakion of the Temple",
            "kontakion of the Cross": "Kontakion of the Cross",
            "troparion of St. Hieromartyr Timothy": "Troparion of St. Hieromartyr Timothy",
            "kontakion of St. Hieromartyr Timothy": "Kontakion of St. Hieromartyr Timothy",
            "troparion of the day": "Troparion of the Day",
            "kontakion of the day": "Kontakion of the Day",
            "troparion of the day": "Troparion of the Day",
            "kontakion of the day": "Kontakion of the Day",
            "troparion of the Angels.": "Troparion of the Angels.",
            "troparion of the Forerunner.": "Troparion of the Forerunner.",
            "troparion of the Apostles; troparion of St. Nicholas.": "Troparion of the Apostles; Troparion of St. Nicholas.",
            "kontakion of the Angels.": "Kontakion of the Angels.",
            "kontakion of the Forerunner.": "Kontakion of the Forerunner.",
            "kontakion of the Apostles; kontakion of St. Nicholas.": "Kontakion of the Apostles; Kontakion of St. Nicholas.",
            "troparion of ": "Troparion of ",
            "kontakion of ": "Kontakion of ",
            "current day": "Current Day",
            "Glory... doxastikon of the saint": "Glory... Doxastikon of the Saint",
            "Both now... theotokion from the Horologion or Octoechos": "Both now... Theotokion from the Horologion or Octoechos",
            "sessional hymns": "Sessional Hymns",
            "sessional hymn": "Sessional Hymn",
            "aposticha theotokion": "Aposticha Theotokion"
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
            
        # Standardize capitalization of some words everywhere
        text = text.replace("troparion of the Saint", "Troparion of the Saint")
        text = text.replace("troparion of the Cross", "Troparion of the Cross")
        text = text.replace("kontakion of the Cross", "Kontakion of the Cross")
        text = text.replace("kontakion of the Saint", "Kontakion of the Saint")
        text = text.replace("doxasticon of the Saint", "Doxastikon of the Saint")
        text = text.replace("doxastikon of the Saint", "Doxastikon of the Saint")
        text = text.replace("dismissal Theotokion", "Dismissal Theotokion")
        text = text.replace("daily aposticha", "Daily Aposticha")
        text = text.replace("resurrectional sessional", "Resurrectional Sessional")
        text = text.replace("resurrectional stichera", "Resurrectional Stichera")
        text = text.replace("of the saint", "of the Saint")
        text = text.replace("to the saint", "to the Saint")
        text = text.replace("canon of the saint", "Canon of the Saint")
        text = text.replace("Canon of the saint", "Canon of the Saint")
        text = text.replace("canon of the Saint", "Canon of the Saint")
        text = text.replace("troparion of the saint", "Troparion of the Saint")
        text = text.replace("kontakion of the saint", "Kontakion of the Saint")
        text = text.replace("doxasticon of the saint", "Doxastikon of the Saint")
        text = text.replace("tone of the saint", "tone of the Saint")
        text = text.replace("stichera to the saint", "Stichera to the Saint")
        text = text.replace("stichera to the Saint", "Stichera to the Saint")
        
        # Ensure 'stichera' is capitalized in specific contexts
        text = text.replace("6 stichera", "6 Stichera")
        text = text.replace("3 stichera", "3 Stichera")
        text = text.replace(" praises stichera", " Praises Stichera")
        text = text.replace(" litiya stichera", " Litiya Stichera")
        text = text.replace(" daily stichera", " Daily Stichera")
        text = text.replace("6 Stichera to the Saint", "6 Stichera to the Saint")
        
        return text


    def generate(self, context, rubrics, mode="full"):
        self.mode = mode
        if mode == "full":
            res = self.generate_full_service(context, rubrics)
        else:
            res = self.generate_quick_reference(context, rubrics)
            
        # Post-process to standardize spelling and capitalization
        res = self._lowercase_liturgical_terms(res)
        res = res.replace("Prokimenon", "Prokeimenon")
        res = res.replace("Prokimena", "Prokeimena")
        res = res.replace("prokimenon", "prokeimenon")
        res = res.replace("prokimena", "prokeimena")
        res = res.replace("Kinonicon", "Communion Hymn")
        res = res.replace("kinonicon", "communion hymn")
        
        # Standardize Exapostilarion spelling (Royal Doors standard)
        res = res.replace("Exaposteilarion", "Exapostilarion")
        res = res.replace("exaposteilarion", "exapostilarion")
        res = res.replace("Exaposteilaria", "Exapostilaria")
        res = res.replace("exaposteilaria", "exapostilaria")
        
        # Standardize Heirmos spelling (Royal Doors standard)
        import re
        res = re.sub(r'\bIrmos\b', 'Heirmos', res)
        res = re.sub(r'\birmos\b', 'heirmos', res)
        res = re.sub(r'\bIrmoi\b', 'Heirmoi', res)
        res = re.sub(r'\birmoi\b', 'heirmoi', res)
        res = re.sub(r'\bIrmologion\b', 'Heirmologion', res)
        res = re.sub(r'\birmologion\b', 'heirmologion', res)
        
        # Standardize Litiya and Gradual spelling (Royal Doors standard)
        res = re.sub(r'\bLytia\b', 'Litiya', res)
        res = re.sub(r'\blytia\b', 'litiya', res)
        res = re.sub(r'\bStepenna\b', 'Gradual', res)
        res = re.sub(r'\bstepenna\b', 'gradual', res)
        res = re.sub(r'\bStepenny\b', 'Graduals', res)
        res = re.sub(r'\bstepenny\b', 'graduals', res)
        
        # Capitalize and format "Both now"
        res = res.replace("both now", "Both now")
        res = res.replace("Both now... ", "Both now: ")
        res = res.replace("Both now...", "Both now:")
        
        # Correct double words
        res = res.replace("of the of the", "of the")
        
        # Strip Ordo references (bracketed/parenthesized database metadata)
        res = re.sub(r'\s*-\s*\[Ordo\s+[^\]]+\]', '', res)
        res = re.sub(r'\s*—\s*\[Ordo\s+[^\]]+\]', '', res)
        res = re.sub(r'\s*-\s*\(\s*Ordo\s+[^\)]+\)', '', res)
        res = re.sub(r'\s*—\s*\(\s*Ordo\s+[^\)]+\)', '', res)
        res = re.sub(r'\[Ordo\s+[^\]]+\]', '', res)
        res = re.sub(r'\(\s*Ordo\s+[^\)]+\)', '', res)
        
        # Post-process to ensure trailing spaces on all non-empty, non-header lines
        lines = []
        for line in res.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#") or line_str.startswith(">"):
                lines.append(line_str)
            else:
                lines.append(line.rstrip() + "  ")
        res = "\n".join(lines)
        
        return res


    def generate_full_service(self, context, rubrics):
        self.mode = "full"
        self._seen_katavasias = set()
        self._matins_canon_printed = False
        self._liturgy_readings_printed = False
        digest = []

        # Resolve general case variables first and merge them
        try:
            general_case = self.engine.resolve_general_case(context)
            if general_case and "variables" in general_case:
                for k, v in general_case["variables"].items():
                    if k not in rubrics.setdefault("variables", {}):
                        rubrics["variables"][k] = v
        except Exception:
            pass
            
        enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
        enriched["overrides"] = rubrics.get("overrides", {})
        if rubrics.get("is_sunday_vigil"):
            enriched["is_sunday_vigil"] = True
            
        # 1. Date Header
        date_str = enriched.get('date', '')
        try:
            dt = datetime.fromisoformat(date_str).date()
            day_name = dt.strftime('%A').upper()
            month_name = dt.strftime('%B').upper()
            day = dt.day
            suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            formatted_date = f"{day_name}, {month_name} {day}{suffix}, {dt.year}."
        except (ValueError, TypeError):
            formatted_date = date_str
            dt = None

            
        digest.append(f"TYPICON: {formatted_date}")
        
        # 2. Title and Tone
        raw_title = rubrics.get('title', 'NORMAL DAY')
        d_title = enriched.get("dolnytsky_title", "")
        
        # Clean d_title from asterisks and outer dots/whitespace
        if d_title:
            d_title_clean = d_title.replace("**", "").strip().rstrip(".").strip()
        else:
            d_title_clean = ""
            
        if raw_title.startswith("menaion.") or raw_title.startswith("pentecostarion.") or raw_title.startswith("triodion."):
            if d_title_clean:
                title = d_title_clean.upper()
            else:
                title = self.humanize_key(raw_title).upper()
        elif "SAINT OF THE DAY" in raw_title.upper():
            saints = enriched.get("saints", [])
            if saints:
                st_name = saints[0].get("name", "SAINT OF THE DAY")
                title = st_name.replace("**", "").strip().rstrip(".").strip().upper()
            else:
                title = "SAINT OF THE DAY"
        else:
            title = raw_title.upper()
            
        import re
        title = re.sub(r'\s*\(\d+-\d+\)', '', title)
        title = title.rstrip('.')
        
        # Combine movable feast title (like Apodosis of the Eucharist) with the saint's title
        if d_title_clean and d_title_clean.lower() != title.lower():
            if any(x in d_title_clean.lower() for x in ["apodosis", "feast", "afterfeast", "forefeast"]):
                saints = enriched.get("saints", [])
                if saints:
                    saint_name = saints[0].get("name", "")
                    saint_name_clean = saint_name.replace("**", "").strip().rstrip(".").strip()
                    title = f"{d_title_clean}; {saint_name_clean}".upper()
                else:
                    title = d_title_clean.upper()

        tone_str = enriched.get('tone', '')
        if tone_str:
            title += f" - TONE {self._roman_tone(tone_str)}."
        else:
            title += "."
        digest.append(title)
        
        # 3. Saints List
        if "saints" in enriched:
             saints_str = "; ".join(self._clean_name(s.get("name", s.get("id", ""))) for s in enriched["saints"])
             if saints_str:
                 digest.append(saints_str)
                  
        # 4. Service Combination Header
        try:
            res = self.engine.resolve_service_combination_header(enriched, rubrics)
            if res and res.get("components"):
                comps = []
                for c in res["components"]:
                    if c.lower().startswith("st. forefeast") or c.lower().startswith("st. afterfeast"):
                        continue
                    c_clean = c.replace(" from the Octoechos", "")
                    # Capitalize Saint names
                    if "service" not in c_clean.lower() and "triodion" not in c_clean.lower() and "forefeast" not in c_clean.lower() and "afterfeast" not in c_clean.lower():
                        comps.append(self._capitalize_name(self._clean_name(c_clean)))
                    else:
                        comps.append(c_clean)
                if comps:
                    header = comps[0]
                    if len(comps) > 1: header += " combined with that of " + comps[1]
                    for c in comps[2:]: header += ", and that of " + c
                    
                    # Ensure the combination header explicitly mentions the saint if missed
                    saints = enriched.get("saints", [])
                    if saints:
                        s_name_clean = saints[0].get("name", "").replace("**", "").strip().rstrip(".").strip()
                        if "saint" in header.lower() and s_name_clean.lower() not in header.lower():
                            import re
                            pattern = re.compile(r'\bsaint\b', re.IGNORECASE)
                            clean_saint_name = self._clean_name(saints[0].get("name"))
                            header = pattern.sub(self._capitalize_name(clean_saint_name), header)
                        
                    header_str = ((header[0].upper() + header[1:]) if header else "").rstrip('.') + "."
                    digest.append(header_str)
        except Exception as e:
            digest.append(f"[ERROR: resolve_service_combination_header failed - {e}]")

        # 5. Saint Transfer Note
        try:
            res = self.engine.resolve_saint_transfer(enriched, rubrics)
            if res and res.get("transferred"):
                target = res.get('target', 'a convenient time').replace('_', ' ')
                verb = "are" if res.get("saint_count", 1) > 1 else "is"
                noun = "services" if res.get("saint_count", 1) > 1 else "service"
                digest.append(f"The {noun} to {res.get('saint_name', 'the Saint')} {verb} transferred to {target}.")
        except Exception as e:
            digest.append(f"[ERROR: resolve_saint_transfer failed - {e}]")

        # 6. Vestment Colors
        try:
            res = self.engine.resolve_vestment_color(enriched, rubrics)
            if res and res.get("color"):
                color = res["color"].capitalize()
                alt = f" or {res['alt'].replace('_', ' ')}" if res.get("alt") else ""
                is_dark = res["color"] in ("black", "dark_purple", "purple")
                tone_type = "Dark" if is_dark else "Bright"
                digest.append(f"Vestment colour: {tone_type} ({color}{alt}).")
        except Exception as e:
            digest.append(f"[ERROR: resolve_vestment_color failed - {e}]")
             
        digest.append("")

        # 7. Traverse Daily Cycle
        matins_override = None
        if context.get("triodion_period") == "holy_friday":
            matins_override = "tomb_matins"
        elif context.get("triodion_period") in ["pascha", "bright_week"]:
            matins_override = "bright_matins"
        elif context.get("triodion_period") == "holy_week_weekday" and context.get("day_of_week") in [4, 5]:
            matins_override = "passion_matins"
        elif context.get("triodion_period") == "holy_week_weekday" and context.get("day_of_week") in [1, 2, 3]:
            matins_override = "bridegroom_matins"

        self._liturgy_readings_printed = False
        hours_formatted = False
        for service in self.engine.daily_cycle:
            context["overrides"] = rubrics.get("overrides", {})
            service_name = service["name"]
            
            # Resolve root_id
            root_id = service["root"]
            if service["type_key"] in rubrics.get("variables", {}):
                root_id = rubrics["variables"][service["type_key"]]
            if service["type_key"] in rubrics.get("overrides", {}):
                root_id = rubrics["overrides"][service["type_key"]]

            if root_id in ["structure_suppressed", "no_liturgy"]:
                continue
            
            # Suppression logic for Compline and Midnight Office during Weekday Vigil
            if service_name in ("Compline", "Midnight Office"):
                day = context.get("day_of_week")
                v_type = rubrics.get("overrides", {}).get("vespers_type") or rubrics.get("variables", {}).get("vespers_type") or context.get("vespers_type")
                if day != 0 and v_type == "great_vespers_vigil":
                    continue
            
            # Group Hours into a single section
            if service_name in ["First Hour", "Third Hour", "Sixth Hour", "Ninth Hour"]:
                if not hours_formatted:
                    pascha_off = context.get("pascha_offset")
                    if pascha_off in (-6, -5, -4):
                        day_names_hm = {-6: "GREAT AND HOLY MONDAY", -5: "GREAT AND HOLY TUESDAY", -4: "GREAT AND HOLY WEDNESDAY"}
                        digest.append(f"## HOURS OF {day_names_hm[pascha_off]}")
                        digest.append("**At all the Hours:** Troparion: *\"Behold, the Bridegroom comes at midnight...\"*; Kontakion of the Day from the Holy Week Triodion.")
                        digest.append("**At the 6th Hour:** Troparion of Prophecy, Prokeimenon, Paremia from Ezekiel, 2nd Prokeimenon.")
                        digest.append("**At the Typika:** Beatitudes read quickly without singing; Prayer of St. Ephrem with 4 great prostrations. Aliturgical day (Presanctified Liturgy celebrated in the evening with Vespers).")
                        digest.append("")
                    elif pascha_off == -3:
                        digest.append("## HOURS")
                        digest.append("**At all the Hours:** Troparion and Kontakion of Great Thursday.")
                        digest.append("**At the 1st Hour:** After the Theotokion 'What shall we call Thee', we read the Troparion of the Prophecy (Tone 3), 1st Prokeimenon (Tone 1: *\"Let them know that the Lord is Thy Name\"*), Paremia (**Jeremiah 11:18–12:5, 9–11, 14–15**), 2nd Prokeimenon (Tone 8: *\"Pray and give praise to the Lord our God\"*).")
                        digest.append("**At the Typika:** Begins from Beatitudes without stichera; Creed is omitted. Kontakion of Great Thursday.")
                        digest.append("")
                    elif pascha_off == -2:
                        digest.append("## ROYAL HOURS OF GREAT AND HOLY FRIDAY")
                        digest.append("**Royal Hours (1st, 3rd, 6th, 9th):** Each hour contains special Psalms, Troparia of Prophecy, Old Testament Paremias, Epistles, and Gospels of the Passion.")
                        digest.append("  - **1st Hour:** Paremia: Zechariah 11:10–13; Epistle: Galatians 6:14–18; Gospel: Matthew 27:1–56.")
                        digest.append("  - **3rd Hour:** Paremia: Isaiah 50:4–11; Epistle: Romans 5:6–10; Gospel: Mark 15:16–41.")
                        digest.append("  - **6th Hour:** Paremia: Isaiah 52:13–54:1; Epistle: Hebrews 2:11–18; Gospel: Luke 23:32–49.")
                        digest.append("  - **9th Hour:** Paremia: Jeremiah 11:18–12:5, 9–11, 14–15; Epistle: Hebrews 10:19–31; Gospel: John 18:28–19:37.")
                        digest.append("**Typika:** Beatitudes with 8 Troparia; Kontakion 'For our sake was the Crucified'. Aliturgical Day.")
                        digest.append("")
                    elif pascha_off is not None and 0 <= pascha_off <= 6:
                        digest.append("## PASCHAL HOURS")
                        digest.append("The Paschal Hours are sung in place of the 1st, 3rd, 6th, and 9th Hours, as well as Compline and Midnight Office throughout Bright Week:  \n"
                                      "  - *\"Christ is risen from the dead...\"* (thrice)  \n"
                                      "  - *\"Having beheld the Resurrection of Christ...\"* (thrice)  \n"
                                      "  - Hypakoë: *\"When they who were with Mary came...\"*  \n"
                                      "  - Kontakion: *\"Though You went down into the tomb...\"*  \n"
                                      "  - Troparia: *\"In the tomb with the body...\"*; *Glory...* *\"How life-giving...\"*; *Both now...* *\"Rejoice, O sanctified tabernacle...\"*  \n"
                                      "  - *\"Lord, have mercy\"* (40 times), *\"Glory... Both now... More honorable than the Cherubim...\"*  \n"
                                      "  - *\"Christ is risen...\"* (thrice), and the Paschal Dismissal.")
                        digest.append("")
                    else:
                        digest.append("## HOURS")
                        try:
                            hours_text = self._format_qr_hours(context, rubrics)
                            digest.append(hours_text)
                        except Exception as e:
                            digest.append(f"[ERROR: Formatting hours failed - {e}]")
                        digest.append("")
                    hours_formatted = True
                continue

            # Suppression logic for Vesperal Liturgy & Presanctified
            is_vesperal_liturgy = (
                "vesperal_merge_logic" in rubrics.get("overrides", {}).get("liturgy_type", "") or
                "vesperal_merge_logic" in rubrics.get("variables", {}).get("liturgy_type", "")
            )
            if is_vesperal_liturgy:
                self._liturgy_readings_printed = True
                
            is_presanctified_liturgy = (
                rubrics.get("variables", {}).get("liturgy_type") == "liturgy_presanctified" or 
                rubrics.get("overrides", {}).get("liturgy_type") == "liturgy_presanctified" or
                (hasattr(self.engine, "check_presanctified_trigger") and self.engine.check_presanctified_trigger(context))
            )
            if service_name == "Vespers" and (is_vesperal_liturgy or is_presanctified_liturgy):
                continue

            if service_name == "Vespers":
                if context.get("scenario_id") == "collision_annunciation_great_friday" or (context.get("pascha_offset") == -2 and (str(context.get("date", "")).endswith("-03-25") or context.get("feast_id") == "annunciation" or "annunciation" in str(context.get("title", "")).lower())):
                    digest.append("=== GREAT VESPERS WITH THE PROCESSION OF THE HOLY SHROUD & ANNUNCIATION ===")
                    digest.append("Fasting Rule: Strict Fast.")
                    digest.append("*At Lord, I Call:* 6 stichera from the Triodion, and 4 Feast stichera from the Menaion; Glory... Tone VI: *\"O how the lawless assembly...\"*; Both now... *\"The mystery hidden from all eternity...\"*.")
                    digest.append("Entrance with the Holy Gospel.")
                    digest.append("**Old Testament Paremias:**")
                    digest.append("  1. **Exodus 33:11–23** (Moses sees the glory of God)")
                    digest.append("  2. **Job 42:12–17** (The Lord blesses the latter end of Job)")
                    digest.append("  3. **Isaiah 52:13–54:1** (The Suffering Servant of the Lord)")
                    digest.append("  4. **Genesis 28:10–17; Ezekiel 43:27–44:4; Proverbs 9:1–11** (Annunciation Paremias)")
                    digest.append("**Prokeimenon (Tone 4):** *\"They divided My garments among them, and for My vesture they cast lots.\"*")
                    digest.append("**Epistle:** **1 Corinthians 1:18–2:2** and **Hebrews 2:11–18** (Annunciation)")
                    digest.append("**Holy Gospel:** **Matthew 27:1–38...** and **Luke 1:24–38** (Annunciation)")
                    digest.append("**Vesperal Divine Liturgy of St. John Chrysostom**")
                    digest.append("**Procession of the Holy Shroud (Epitaphios / Plashchanytsia):** During the Aposticha (*\"When from the Tree the Arimathean took Thee down...\"*), the clergy carry the Holy Shroud in solemn procession to the Tomb.")
                    digest.append("")
                    continue
                elif context.get("pascha_offset") == -2:
                    digest.append("=== GREAT VESPERS WITH THE PROCESSION OF THE HOLY SHROUD ===")
                    digest.append("Fasting Rule: Strict Fast.")
                    digest.append("*At Lord, I Call:* Stichera on 6 from the Triodion; Glory... Tone VI: *\"O how the lawless assembly...\"*; Both now... *\"A dread and marvelous mystery...\"*.")
                    digest.append("Entrance with the Holy Gospel.")
                    digest.append("**Old Testament Paremias:**")
                    digest.append("  1. **Exodus 33:11–23** (Moses sees the glory of God)")
                    digest.append("  2. **Job 42:12–17** (The Lord blesses the latter end of Job)")
                    digest.append("  3. **Isaiah 52:13–54:1** (The Suffering Servant of the Lord)")
                    digest.append("**Prokeimenon (Tone 4):** *\"They divided My garments among them, and for My vesture they cast lots.\"*")
                    digest.append("**Epistle:** **1 Corinthians 1:18–2:2** (*\"For the message of the cross is foolishness to those who are perishing...\"*)")
                    digest.append("**Holy Gospel:** **Matthew 27:1–38; Luke 23:39–43; Matt 27:39–54; John 19:31–37; Matt 27:55–61** (Composite Passion and Burial Narrative)")
                    digest.append("**Procession of the Holy Shroud (Epitaphios / Plashchanytsia):** During the Aposticha (*\"When from the Tree the Arimathean took Thee down...\"*), the clergy carry the Holy Shroud in solemn procession to the Tomb in the center of the church.")
                    digest.append("**Troparia at the Tomb:** Troparion *\"The noble Joseph, taking down Thy most pure Body from the Tree...\"*; Glory... *\"When Thou didst descend unto death, O Life Immortal...\"*; Both now... *\"The angel stood by the tomb and cried unto the myrrh-bearing women...\"*")
                    digest.append("Veneration of the Holy Shroud (Epitaphios) by the clergy and faithful.")
                    digest.append("")
                    continue
                elif (context.get("pascha_offset") is not None and 0 <= context.get("pascha_offset") <= 6) or root_id == "paschal_vespers":
                    p_off = context.get("pascha_offset", 0)
                    vesp_title = "=== PASCHAL VESPERS (AGAPE VESPERS) ===" if p_off == 0 else "=== BRIGHT WEEK VESPERS ==="
                    digest.append(vesp_title)
                    digest.append(self._format_paschal_vespers(context, rubrics))
                    digest.append("")
                    continue
                
                try:
                    small_vespers_needed_res = self.engine.resolve_small_vespers_needed(context, rubrics)
                except Exception as e:
                    small_vespers_needed_res = None
                    digest.append(f"[RESOLVE ERROR: resolve_small_vespers_needed: {e}]")
                
                if small_vespers_needed_res and small_vespers_needed_res.get("needed"):
                    struct_data = self.engine._load_json("json_db/01h_struct_vespers.json")
                    skeleton = self.engine._get_structure_sequence(struct_data, "small_vespers")
                    if skeleton:
                        digest.append("=== SMALL VESPERS ===")
                        small_context = context.copy()
                        small_context["is_small_vespers"] = True
                        small_context["active_structure_id"] = "small_vespers"
                        self._process_skeleton(skeleton, small_context, rubrics, digest)
                        digest.append("")



            # Apply specific overrides
            pascha_off = context.get("pascha_offset")
            if service_name == "Matins":
                if pascha_off == -3 or root_id == "holy_thursday_matins":
                    digest.append("=== MATINS OF GREAT AND HOLY THURSDAY ===")
                    digest.append(self._format_holy_thursday_matins(context, rubrics))
                    digest.append("")
                    continue
                elif pascha_off == -2 or root_id in ("twelve_passion_gospels", "passion_matins"):
                    digest.append("=== MATINS OF THE HOLY AND REDEEMING PASSION OF OUR LORD (THE TWELVE PASSION GOSPELS) ===")
                    digest.append(self._format_holy_friday_matins(context, rubrics))
                    digest.append("")
                    continue
                elif pascha_off == -1 or root_id in ("tomb_matins", "jerusalem_lamentations_matins"):
                    digest.append("=== JERUSALEM MATINS: THE LAMENTATIONS (ENCOMIA) AT THE TOMB OF THE LORD ===")
                    digest.append(self._format_holy_saturday_matins(context, rubrics))
                    digest.append("")
                    continue
                elif pascha_off == 0 or root_id == "bright_matins":
                    digest.append("=== PASCHAL MATINS ===")
                    digest.append(self._format_paschal_matins(context, rubrics))
                    digest.append("")
                    continue
                elif matins_override:
                    root_id = matins_override

            struct_file = service["file"]
            if "hours_type" in service["type_key"]:
                var_hours = rubrics.get("variables", {}).get("hours_type", "")
                is_royal = "royal" in var_hours or (hasattr(self.engine, "check_royal_hours_trigger") and self.engine.check_royal_hours_trigger(context))
                if is_royal:
                    root_id = "structure_royal"
                    struct_file = "json_db/01k_struct_royal_hours.json"
                    
                    hour_map = {
                        "First Hour": 1,
                        "Third Hour": 3,
                        "Sixth Hour": 6,
                        "Ninth Hour": 9
                    }
                    context["hour"] = hour_map.get(service_name, 1)
                elif "lenten" in var_hours:
                    root_id = "structure_lenten"
                elif "paschal" in var_hours:
                    root_id = "structure_paschal"

            if service_name == "Midnight Office":
                 mode_data = self.engine.resolve_midnight_office_mode(context)
                 if "mode" in mode_data:
                     root_id = f"midnight_{mode_data['mode']}"

            # Load the structure sequence
            struct_data = self.engine._load_json(struct_file)
            skeleton = self.engine._get_structure_sequence(struct_data, root_id)

            if not skeleton:
                digest.append(f"=== {service_name.upper()} ===")
                digest.append(f"[ERROR: Structure '{root_id}' not found in {struct_file}]")
                digest.append("")
                continue

            # Print service name header
            expanded_name = self.engine.get_expanded_service_name(service, enriched).upper()
            digest.append(f"=== {expanded_name} ===")

            # Walk sequence
            service_context = context.copy()
            service_context["active_structure_id"] = root_id
            self._process_skeleton(skeleton, service_context, rubrics, digest)
            
            # Attach actionable synodal footnote callouts for this service
            try:
                srv_footnotes = self.engine.resolve_synodal_footnotes(enriched, rubrics, service_name=service_name)
                if srv_footnotes:
                    callouts_str = self._format_service_synodal_callouts(srv_footnotes)
                    if callouts_str:
                        digest.append("")
                        digest.append(callouts_str)
            except Exception:
                pass
            digest.append("")

        # Collision notes
        collision_rule = self.engine.check_collision(context)
        if collision_rule and "rubric" in collision_rule and "notes" in collision_rule["rubric"]:
            notes = collision_rule["rubric"]["notes"]
            if notes:
                digest.append("## NOTES & FOOTNOTES")
                if isinstance(notes, list):
                    for idx, note in enumerate(notes):
                        digest.append(f"{idx+1}. {note}  ")
                else:
                    digest.append(f"{notes}  ")

        try:
            day_footnotes = self.engine.resolve_synodal_footnotes(enriched, rubrics)
            if day_footnotes:
                fn_section = self._format_synodal_footnotes_section(day_footnotes)
                if fn_section:
                    digest.append("")
                    digest.append(fn_section)
        except Exception:
            pass

        # Flatten all lines and split by \n
        raw_lines = []
        for item in digest:
            if not item:
                raw_lines.append("")
            elif isinstance(item, str):
                raw_lines.extend(item.splitlines())
            else:
                raw_lines.append(str(item))
                
        formatted_md = []
        last_added_line = None
        for line in raw_lines:
            line_str = line.strip()
            if not line_str:
                formatted_md.append("")
                continue
                
            # Suppress consecutive identical lines (case-insensitive and whitespace-insensitive)
            if last_added_line and line_str.lower() == last_added_line.lower():
                continue
            last_added_line = line_str
                
            if line_str.startswith("TYPICON:"):
                if formatted_md and formatted_md[-1] != "":
                    formatted_md.append("")
                formatted_md.append(f"# {line_str}")
                formatted_md.append("")
            elif line_str.startswith("===") and line_str.endswith("==="):
                title = line_str.replace("===", "").strip()
                if formatted_md and formatted_md[-1] != "":
                    formatted_md.append("")
                formatted_md.append(f"## {title}")
                formatted_md.append("")
            elif line_str.startswith("RUBRIC:"):
                rubric_text = line_str.replace("RUBRIC:", "").strip()
                if formatted_md and formatted_md[-1] != "":
                    formatted_md.append("")
                formatted_md.append("> [!NOTE]")
                formatted_md.append(f"> **Rubric**: {rubric_text}")
                formatted_md.append("") # Close the blockquote
            else:
                # Add two spaces at the end of the line to force a line break in Markdown
                formatted_md.append(f"{line_str}  ")
                
        return "\n".join(formatted_md)


    def _get_eothinon_gospel_citation(self, num):
        for key in (f"eothinon.{num}.gospel", f"eothinon.eothinon_{num}_gospel"):
            try:
                asset = self.engine.get_text(key)
                if asset and not self._is_missing(asset) and asset.get("content"):
                    content = asset.get("content")
                    if not self._is_missing(content):
                        parts = content.split("\n\n")
                        if parts:
                            return parts[0].strip()
            except Exception:
                pass
        return ""

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
            ('zechariah', 'Zechariah'), ('micah', 'Micah'), ('baruch', 'Baruch')
        ]
        k_lower = str(key).lower().replace('.', '_')
        for b_key, b_name in books:
            if k_lower.startswith(b_key + '_'):
                rem = k_lower[len(b_key) + 1:]
                parts = rem.split('_')
                if len(parts) == 6:
                    return f"{b_name} {parts[0]}:{parts[1]}–{parts[2]}; {parts[3]}:{parts[4]}–{parts[5]}"
                elif len(parts) == 4:
                    return f"{b_name} {parts[0]}:{parts[1]}–{parts[2]}:{parts[3]}"
                elif len(parts) == 3:
                    return f"{b_name} {parts[0]}:{parts[1]}–{parts[2]}"
                elif len(parts) == 2:
                    return f"{b_name} {parts[0]}:{parts[1]}"
                elif len(parts) == 1 and parts[0].isdigit():
                    return f"{b_name} {parts[0]}"
        return ""

    def _hour_name(self, h):
        return {1: "First Hour", 3: "Third Hour", 6: "Sixth Hour", 9: "Ninth Hour"}.get(h, f"{h}th Hour")


    def _hour_ordinal(self, h):
        return {1: "First", 3: "Third", 6: "Sixth", 9: "Ninth"}.get(h, str(h))


    def _get_kathisma_display(self, res):
        if not res:
            return ""
        if isinstance(res, dict):
            if res.get("type") == "lenten_hours":
                return str(res.get("kathisma_number"))
            val = res.get("id") or res.get("ref_key") or ""
            val_clean = val.replace("kathisma_", "").replace("Kathisma ", "").replace("horologion.", "")
            if val_clean.isdigit():
                return val_clean
            return self.humanize_key(val)
        return self.humanize_key(str(res))


    def _resolve_slot_value(self, slot_content, context, rubrics):
        func_name = slot_content.get("logic", {}).get("function")
        args = slot_content.get("logic", {}).get("args", {})
        if not func_name or not hasattr(self.engine, func_name):
            return None
            
        enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
        enriched["overrides"] = rubrics.get("overrides", {})
        if rubrics.get("is_sunday_vigil"):
            enriched["is_sunday_vigil"] = True
            
        func = getattr(self.engine, func_name)
        
        import inspect
        sig = inspect.signature(func)
        call_kwargs = {}
        if "rubrics" in sig.parameters:
            call_kwargs["rubrics"] = rubrics
            
        normalized_args = {}
        for k, v in args.items():
            if k == "pos":
                normalized_args["position"] = v
            elif k == "num":
                normalized_args["num"] = v
            else:
                normalized_args[k] = v
                
        for param_name in sig.parameters:
            if param_name in normalized_args:
                call_kwargs[param_name] = normalized_args[param_name]
                
        params = list(sig.parameters.values())
        if len(params) > 0:
            result = func(enriched, **call_kwargs)
        else:
            result = func()
            
        return result


    def _format_grouped_kathismata(self, parent_slot, context, rubrics):
        content = parent_slot.get("content", {})
        components = content.get("components", [])
        if not components:
            return ""
            
        kathismata_resolved = []
        sessionals_resolved = []
        sessional_map = {}
        kathisma_count = 0
        
        for comp in components:
            comp_content = comp.get("content", {}) or comp
            slot_type = comp_content.get("type")
            
            if slot_type == "variable_logic":
                func_name = comp_content.get("logic", {}).get("function")
                if func_name == "resolve_kathisma":
                    res = self._resolve_slot_value(comp_content, context, rubrics)
                    if res:
                        display = self._get_kathisma_display(res)
                        kathismata_resolved.append(display)
                        kathisma_count += 1
                elif func_name in ("resolve_sessional", "resolve_lenten_sessional"):
                    res = self._resolve_slot_value(comp_content, context, rubrics)
                    if res:
                        desc = self._format_result(func_name, res, context)
                        if desc:
                            desc_clean = desc.strip().rstrip('.')
                            for prefix in ["We sing the ", "We sing ", "Sessional Hymns: ", "We read ", "Lenten Sessional: "]:
                                if desc_clean.startswith(prefix):
                                    desc_clean = desc_clean[len(prefix):]
                            sessional_map[kathisma_count] = desc_clean
                            sessionals_resolved.append(desc_clean)
                            
        if not kathismata_resolved:
            return ""
            
        if len(kathismata_resolved) == 1:
            k_str = kathismata_resolved[0]
        elif len(kathismata_resolved) == 2:
            k_str = f"{kathismata_resolved[0]} & {kathismata_resolved[1]}"
        else:
            k_str = ", ".join(kathismata_resolved[:-1]) + f", and {kathismata_resolved[-1]}"
            
        day_of_week = context.get("day_of_week", 0)
        is_sunday = day_of_week == 0 or context.get("is_sunday_vigil")
        rank_str = str(rubrics.get("rank") or context.get("rank") or "").lower()
        is_polyeleos = is_sunday or "polyeleos" in rank_str or "vigil" in rank_str or context.get("feast_level") in ("polyeleos", "vigil", "lord", "theotokos")
        
        unique_sess = list(set(sessionals_resolved))
        if not unique_sess:
            sess_str = "We read the Kathismata."
        elif len(unique_sess) == 1:
            if is_polyeleos:
                if len(kathismata_resolved) > 1:
                    parts = []
                    for idx, k_num in enumerate(kathismata_resolved):
                        k_idx = idx + 1
                        parts.append(f"after the {self._ordinal(k_idx)} ({k_num}): Small Litany, then the {unique_sess[0]}")
                    sess_str = "  \n" + "  \n".join(f"  - {p[0].upper() + p[1:]}." for p in parts)
                else:
                    sess_str = f"Small Litany, then we sing the {unique_sess[0]}."
            else:
                sess_str = f"After each Kathisma, we sing the {unique_sess[0]}."
        else:
            parts = []
            for idx, k_num in enumerate(kathismata_resolved):
                k_idx = idx + 1
                if k_idx in sessional_map:
                    lit_str = "Small Litany, then the " if is_polyeleos else "the "
                    parts.append(f"after the {self._ordinal(k_idx)} ({k_num}): {lit_str}{sessional_map[k_idx]}")
            sess_str = "  \n" + "  \n".join(f"  - {p[0].upper() + p[1:]}." for p in parts)
            
        prefix_read = ""
        if not is_sunday and kathismata_resolved:
            k_joined = f"{kathismata_resolved[0]} and {kathismata_resolved[1]}" if len(kathismata_resolved) == 2 else (", ".join(kathismata_resolved[:-1]) + f" and {kathismata_resolved[-1]}" if len(kathismata_resolved) > 2 else kathismata_resolved[0])
            prefix_read = f"**Kathismata:** Kathismata {k_joined} are read.\n\n"
            
        if sess_str.startswith("  \n"):
            return prefix_read + f"**Sessional Hymns:**{sess_str}"
        return prefix_read + f"**Sessional Hymns:** {sess_str[0].upper() + sess_str[1:]}."


    def _ordinal(self, n):
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        else:
            suffix = suffixes.get(n % 10, 'th')
        return f"{n}{suffix}"


    def generate_quick_reference(self, context, rubrics):
        self.mode = "quick"
        self._seen_katavasias = set()
        digest = []

        # Resolve general case variables first and merge them
        try:
            general_case = self.engine.resolve_general_case(context)
            if general_case and "variables" in general_case:
                for k, v in general_case["variables"].items():
                    if k not in rubrics.setdefault("variables", {}):
                        rubrics["variables"][k] = v
        except Exception:
            pass
            
        enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
        enriched["overrides"] = rubrics.get("overrides", {})
        if rubrics.get("is_sunday_vigil"):
            enriched["is_sunday_vigil"] = True
            
        # 1. Date Header
        date_str = enriched.get('date', '')
        try:
            dt = datetime.fromisoformat(date_str).date()
            day_name = dt.strftime('%A').upper()
            month_name = dt.strftime('%B').upper()
            day = dt.day
            suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            formatted_date = f"{day_name}, {month_name} {day}{suffix}, {dt.year}."
        except (ValueError, TypeError):
            formatted_date = date_str
            dt = None
            
        # 2. Title and Tone
        title = rubrics.get('title', 'NORMAL DAY').upper()
        if "SAINT OF THE DAY" in title:
            saints = enriched.get("saints", [])
            if saints:
                title = saints[0].get("name", "SAINT OF THE DAY").upper()
                
        title = title.rstrip('.')
        import re
        title = re.sub(r'\s*\(\d+-\d+\)', '', title)
        
        # Combine movable feast title (like Apodosis of the Eucharist) with the saint's title
        d_title = enriched.get("dolnytsky_title")
        if d_title and d_title.lower() != title.lower():
            if any(x in d_title.lower() for x in ["apodosis", "feast", "afterfeast", "forefeast"]):
                saints = enriched.get("saints", [])
                if saints:
                    saint_name = saints[0].get("name", "")
                    title = f"{d_title.strip('.')}; {saint_name.strip('.')}".upper()
                else:
                    title = d_title.upper()

        tone_str = enriched.get('tone', '')
        if tone_str:
            title += f" - TONE {self._roman_tone(tone_str)}."
        else:
            title += "."
            
        digest.append(f"TYPICON: {formatted_date.upper()} {title}")

                
        # 4. Service Combination Header
        try:
            res = self.engine.resolve_service_combination_header(enriched, rubrics)
            if res and res.get("components"):
                comps = []
                for c in res["components"]:
                    if c.lower().startswith("st. forefeast") or c.lower().startswith("st. afterfeast"):
                        continue
                    c_clean = c.replace(" from the Octoechos", "")
                    # Capitalize Saint names
                    if "service" not in c_clean.lower() and "triodion" not in c_clean.lower() and "forefeast" not in c_clean.lower() and "afterfeast" not in c_clean.lower():
                        comps.append(self._capitalize_name(self._clean_name(c_clean)))
                    else:
                        comps.append(c_clean)
                if comps:
                    header = comps[0]
                    if len(comps) > 1: header += " combined with that of " + comps[1]
                    for c in comps[2:]: header += ", and that of " + c
                    
                    # Ensure the combination header explicitly mentions the saint if missed
                    saints = enriched.get("saints", [])
                    if saints:
                        s_name_clean = saints[0].get("name", "").replace("**", "").strip().rstrip(".").strip()
                        if "saint" in header.lower() and s_name_clean.lower() not in header.lower():
                            import re
                            pattern = re.compile(r'\bsaint\b', re.IGNORECASE)
                            clean_saint_name = self._clean_name(saints[0].get("name"))
                            header = pattern.sub(self._capitalize_name(clean_saint_name), header)
                    
                    header_str = ((header[0].upper() + header[1:]) if header else "").rstrip('.') + "."
                    digest.append(header_str)
        except Exception as e:
            digest.append(f"[RESOLVE ERROR: resolve_service_combination_header: {e}]")
            
        # 5. Saint Transfer Note
        try:
            res = self.engine.resolve_saint_transfer(enriched, rubrics)
            if res and res.get("transferred"):
                target = res.get('target', 'a convenient time').replace('_', ' ')
                verb = "are" if res.get("saint_count", 1) > 1 else "is"
                noun = "services" if res.get("saint_count", 1) > 1 else "service"
                digest.append(f"The {noun} to {res.get('saint_name', 'the Saint')} {verb} transferred to {target}.  ")
        except Exception as e:
            digest.append(f"[RESOLVE ERROR: resolve_saint_transfer: {e}]  ")
            
        # 6. Vestment Colors
        try:
            res = self.engine.resolve_vestment_color(enriched, rubrics)
            if res and res.get("color"):
                color = res["color"].capitalize()
                alt = f" or {res['alt'].replace('_', ' ')}" if res.get("alt") else ""
                is_dark = res["color"] in ("black", "dark_purple", "purple")
                tone_type = "Dark" if is_dark else "Bright"
                if res["color"] == "gold" and "white" in alt:
                    digest.append(f"Vestment colour: Bright (blue for the forefeast or gold).")
                else:
                    digest.append(f"Vestment colour: {tone_type} ({color}{alt}).")
        except Exception as e:
            digest.append(f"[RESOLVE ERROR: resolve_vestment_color: {e}]  ")
            
        digest.append("")
        
        enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
        enriched["overrides"] = rubrics.get("overrides", {})
        if rubrics.get("is_sunday_vigil"):
            enriched["is_sunday_vigil"] = True
            
        active_services = []
        for s in self.engine.daily_cycle:
            s_name = s["name"]
            if s_name in ("Compline", "Midnight Office"):
                is_weekday = 0 < enriched.get("day_of_week", 0) <= 6
                is_simple = enriched.get("rank") in ("rank_simple_6", "rank_simple_4", "rank_double_6", "rank_none") or enriched.get("variables", {}).get("rank") in ("rank_simple_6", "rank_simple_4", "rank_double_6", "rank_none")
                has_override = (
                    s["type_key"] in enriched.get("variables", {}) or
                    s["type_key"] in enriched.get("overrides", {})
                )
                if not has_override and is_weekday and is_simple:
                    continue
            active_services.append(s_name)
        
        is_vespers_active = "Vespers" in active_services and rubrics.get("overrides", {}).get("vespers_type") != "structure_suppressed"
        if context.get("day_of_week") == 0:
            is_vespers_active = True
            
        if is_vespers_active:
            eve_type = self.engine.resolve_evening_service_type(enriched)
            is_great = eve_type in ("great_vespers", "great_vespers_vigil", "great_vespers_simple", "paschal_vespers")
            vespers_title = "## GREAT VESPERS" if is_great else "## DAILY VESPERS"
            pascha_off = enriched.get("pascha_offset")
            if enriched.get("scenario_id") == "collision_annunciation_great_friday" or (pascha_off == -2 and (str(enriched.get("date", "")).endswith("-03-25") or enriched.get("feast_id") == "annunciation" or "annunciation" in str(enriched.get("title", "")).lower())):
                digest.append("## GREAT VESPERS WITH THE PROCESSION OF THE HOLY SHROUD & ANNUNCIATION")
                digest.append("")
                digest.append("Fasting Rule: Strict Fast.")
                digest.append("*At Lord, I Call:* 6 stichera from the Triodion, and 4 Feast stichera from the Menaion; Glory... Tone VI: *\"O how the lawless assembly...\"*; Both now... *\"The mystery hidden from all eternity...\"*.")
                digest.append("Entrance with the Holy Gospel.")
                digest.append("**Old Testament Paremias:**")
                digest.append("  1. **Exodus 33:11–23** (Moses sees the glory of God)")
                digest.append("  2. **Job 42:12–17** (The Lord blesses the latter end of Job)")
                digest.append("  3. **Isaiah 52:13–54:1** (The Suffering Servant of the Lord)")
                digest.append("  4. **Genesis 28:10–17; Ezekiel 43:27–44:4; Proverbs 9:1–11** (Annunciation Paremias)")
                digest.append("**Prokeimenon (Tone 4):** *\"They divided My garments among them, and for My vesture they cast lots.\"*")
                digest.append("**Epistle:** **1 Corinthians 1:18–2:2** and **Hebrews 2:11–18** (Annunciation)")
                digest.append("**Holy Gospel:** **Matthew 27:1–38...** and **Luke 1:24–38** (Annunciation)")
                digest.append("**Vesperal Divine Liturgy of St. John Chrysostom**")
                digest.append("**Procession of the Holy Shroud (Epitaphios / Plashchanytsia):** During the Aposticha (*\"When from the Tree the Arimathean took Thee down...\"*), the clergy carry the Holy Shroud in solemn procession to the Tomb in the center of the church.")
                digest.append("")
            elif pascha_off == -2:
                digest.append("## GREAT VESPERS WITH THE PROCESSION OF THE HOLY SHROUD")
                digest.append("")
                digest.append("Fasting Rule: Strict Fast.")
                digest.append("*At Lord, I Call:* Stichera on 6 from the Triodion; Glory... Tone VI: *\"O how the lawless assembly...\"*; Both now... *\"A dread and marvelous mystery...\"*.")
                digest.append("Entrance with the Holy Gospel.")
                digest.append("**Old Testament Paremias:**")
                digest.append("  1. **Exodus 33:11–23** (Moses sees the glory of God)")
                digest.append("  2. **Job 42:12–17** (The Lord blesses the latter end of Job)")
                digest.append("  3. **Isaiah 52:13–54:1** (The Suffering Servant of the Lord)")
                digest.append("**Prokeimenon (Tone 4):** *\"They divided My garments among them, and for My vesture they cast lots.\"*")
                digest.append("**Epistle:** **1 Corinthians 1:18–2:2** (*\"For the message of the cross is foolishness to those who are perishing...\"*)")
                digest.append("**Holy Gospel:** **Matthew 27:1–38; Luke 23:39–43; Matt 27:39–54; John 19:31–37; Matt 27:55–61** (Composite Passion and Burial Narrative)")
                digest.append("**Procession of the Holy Shroud (Epitaphios / Plashchanytsia):** During the Aposticha (*\"When from the Tree the Arimathean took Thee down...\"*), the clergy carry the Holy Shroud in solemn procession to the Tomb in the center of the church.")
                digest.append("**Troparia at the Tomb:** Troparion *\"The noble Joseph, taking down Thy most pure Body from the Tree...\"*; Glory... *\"When Thou didst descend unto death, O Life Immortal...\"*; Both now... *\"The angel stood by the tomb and cried unto the myrrh-bearing women...\"*")
                digest.append("Veneration of the Holy Shroud (Epitaphios) by the clergy and faithful.")
                digest.append("")
            else:
                digest.append(vespers_title)
                digest.append("")
                
                try:
                    res = self.engine.resolve_vespers_kathisma(enriched)
                    if res:
                        if res.get("type") == "blessed_is_the_man":
                            stasis_type = res.get("stasis", "first_stasis")
                            stasis_str = " (First Stasis)" if stasis_type == "first_stasis" else " (Entire Kathisma)"
                            digest.append(f"**Kathisma:** Kathisma I (*Blessed is the man…*{stasis_str}) is sung.  ")
                        elif res.get("type") == "numbered_kathisma":
                            k_num = res.get("number", "1")
                            digest.append(f"**Kathisma:** Kathisma {k_num} is read.  ")
                except Exception:
                    pass
                
                try:
                    res = self.engine.resolve_vespers_stichera(enriched)
                    formatted = self._format_resolve_vespers_stichera(res, enriched)
                    if formatted:
                        if formatted.startswith("At O Lord, I have cried, we sing"):
                            formatted = "**At Lord, I Call:** We sing" + formatted[len("At O Lord, I have cried, we sing"):]
                        elif formatted.startswith("At O Lord, I have cried"):
                            formatted = "**At Lord, I Call:**" + formatted[len("At O Lord, I have cried"):]
                        elif formatted.startswith("At Lord, I Call, we sing"):
                            formatted = "**At Lord, I Call:** We sing" + formatted[len("At Lord, I Call, we sing"):]
                        elif formatted.startswith("At Lord, I Call"):
                            formatted = "**At Lord, I Call:**" + formatted[len("At Lord, I Call"):]
                        elif formatted.startswith("*At Lord, I Call…* we sing"):
                            formatted = "**At Lord, I Call:** We sing" + formatted[len("*At Lord, I Call…* we sing"):]
                        elif formatted.startswith("*At Lord, I Call…*"):
                            formatted = "**At Lord, I Call:**" + formatted[len("*At Lord, I Call…*"):]
                        digest.append(f"{formatted}  ")
                except Exception as e:
                    digest.append(f"[RESOLVE ERROR: resolve_vespers_stichera: {e}]  ")
                    
                try:
                    prok_res = self.engine.resolve_vespers_prokeimenon(enriched)
                    if prok_res:
                        formatted_prok = self._format_resolve_vespers_prokeimenon(prok_res, enriched)
                        if formatted_prok:
                            digest.append(f"{formatted_prok}  ")
                except Exception as e:
                    digest.append(f"[RESOLVE ERROR: resolve_vespers_prokeimenon: {e}]  ")

                    
                try:
                    res = self.engine.resolve_litya_content(enriched)
                    formatted = self._format_resolve_litya_content(res, enriched)
                    if formatted:
                        if formatted.startswith("If Litiya is performed:"):
                            formatted = "**If Litiya is performed:**" + formatted[len("If Litiya is performed:"):]
                        digest.append(f"{formatted}  ")
                except Exception as e:
                    digest.append(f"[RESOLVE ERROR: resolve_litya_content: {e}]  ")
                    
                try:
                    res = self.engine.resolve_aposticha(enriched)
                    formatted = self._format_resolve_aposticha(res, enriched)
                    if formatted:
                        if not formatted.startswith("**At the Aposticha:**"):
                            if formatted.startswith("At the Aposticha, we sing:"):
                                formatted = "**At the Aposticha:** We sing" + formatted[len("At the Aposticha, we sing:"):]
                            elif formatted.startswith("At the Aposticha"):
                                formatted = "**At the Aposticha:**" + formatted[len("At the Aposticha"):]
                            else:
                                formatted = "**At the Aposticha:** " + formatted
                        digest.append(f"{formatted}  ")
                except Exception as e:
                    digest.append(f"[RESOLVE ERROR: resolve_aposticha: {e}]  ")
                    
                try:
                    res = self.engine.resolve_vespers_troparia_simple(enriched, rubrics)
                    formatted = self._format_resolve_vespers_troparia_simple(res, enriched)
                    if formatted:
                        if not formatted.startswith("**At the Dismissal Troparia:**"):
                            if formatted.startswith("At the Dismissal Troparia:"):
                                formatted = "**At the Dismissal Troparia:**" + formatted[len("At the Dismissal Troparia:"):]
                            elif formatted.startswith("At the Dismissal Troparia, we sing:"):
                                formatted = "**At the Dismissal Troparia:**\nWe sing" + formatted[len("At the Dismissal Troparia, we sing:"):]
                        digest.append(f"{formatted}  ")
                        
                    if context.get("day_of_week") == 0:
                        title_lower = title.lower()
                        if "prodigal son" in title_lower:
                            digest.append("Or, if Vigil is served: Rejoice, O Virgin Theotokos... twice; troparion of the forefeast, once.  ")
                        elif "last judgement" in title_lower:
                            digest.append("Or, if Vigil is served: Rejoice, O Virgin Theotokos... twice; troparion of the feast, once.  ")
                        elif "cheesefare" in title_lower:
                            digest.append("Or, if Vigil is served: Rejoice, O Virgin Theotokos... thrice.  ")
                        elif "orthodoxy" in title_lower:
                            digest.append("Or, if Vigil is served: Rejoice, O Virgin Theotokos... twice, troparion from the Triodion, once.  ")
                        elif "palamas" in title_lower:
                            digest.append("Or, if Vigil is served: Rejoice, O Virgin Theotokos... twice, troparion of the Saint, once.  ")
                        elif "cross" in title_lower:
                            digest.append("Or, if Vigil is served: Rejoice, O Virgin Theotokos... twice, troparion of the Cross, once.  ")
                        elif "climacus" in title_lower:
                            digest.append("Or, if Vigil is served: Rejoice, O Virgin Theotokos... twice, troparion of the Saint, once.  ")
                except Exception as e:
                    digest.append(f"[RESOLVE ERROR: resolve_vespers_troparia_simple: {e}]  ")
                    
                digest.append("")
            
        if "Matins" in active_services and rubrics.get("overrides", {}).get("matins_type") != "structure_suppressed":
            is_sunday = context.get("day_of_week") == 0
            rank_str = str(enriched.get("rank") or "").lower()
            is_vigil = (
                rubrics.get("is_sunday_vigil") or 
                enriched.get("rank") in (1, 2, "rank_polyeleos", "rank_vigil") or
                "polyeleos" in rank_str or
                "vigil" in rank_str or
                enriched.get("has_polyeleos")
            )
            pascha_off = enriched.get("pascha_offset")
            if pascha_off in (-6, -5, -4):
                day_names_hm = {-6: "GREAT AND HOLY MONDAY", -5: "GREAT AND HOLY TUESDAY", -4: "GREAT AND HOLY WEDNESDAY"}
                digest.append(f"## BRIDEGROOM MATINS OF {day_names_hm[pascha_off]}")
                digest.append("")
                digest.append(self._format_bridegroom_matins(enriched, rubrics))
                digest.append("")
            elif pascha_off == -3:
                digest.append("## MATINS OF GREAT AND HOLY THURSDAY")
                digest.append("")
                digest.append(self._format_holy_thursday_matins(enriched, rubrics))
                digest.append("")
            elif pascha_off == -2:
                digest.append("## MATINS OF THE HOLY AND REDEEMING PASSION OF OUR LORD (THE TWELVE PASSION GOSPELS)")
                digest.append("")
                digest.append(self._format_holy_friday_matins(enriched, rubrics))
                digest.append("")
            elif pascha_off == -1:
                digest.append("## JERUSALEM MATINS: THE LAMENTATIONS (ENCOMIA) AT THE TOMB OF THE LORD")
                digest.append("")
                digest.append(self._format_holy_saturday_matins(enriched, rubrics))
                digest.append("")
            elif pascha_off == 0:
                digest.append("## PASCHAL MATINS")
                digest.append("")
                digest.append(self._format_paschal_matins(enriched, rubrics))
                digest.append("")
            else:
                matins_title = "## SUNDAY MATINS" if is_sunday else ("## FESTAL MATINS" if is_vigil else "## DAILY MATINS")
                digest.append(matins_title)
                digest.append("")
                
                try:
                    res = self.engine.resolve_god_is_the_lord_troparia(enriched)
                    formatted = self._format_resolve_god_is_the_lord_troparia(res, enriched)
                    if formatted:
                        if formatted.startswith("*At The Lord is God…*"):
                            formatted = "**God is the Lord:**" + formatted[len("*At The Lord is God…*"):]
                        elif formatted.startswith("At The Lord is God…"):
                            formatted = "**God is the Lord:**" + formatted[len("At The Lord is God…"):]
                        digest.append(f"{formatted}  ")
                except Exception as e:
                    digest.append(f"[RESOLVE ERROR: resolve_god_is_the_lord_troparia: {e}]  ")
                    
                digest.append("")
                
                is_weekday = 0 < enriched.get("day_of_week", 0) <= 5
                is_simple = enriched.get("rank") in ("rank_simple_6", "rank_simple_4") or enriched.get("variables", {}).get("rank") in ("rank_simple_6", "rank_simple_4")
                if is_weekday and is_simple:
                    kath_nums = ["1", "2"]
                    try:
                        matins_kathismas = self.engine.resolve_matins_kathisma(enriched)
                        if matins_kathismas:
                            kath_nums = [re.search(r'\d+', k).group(0) for k in matins_kathismas if re.search(r'\d+', k)]
                    except Exception:
                        pass
                    k_str = " & ".join(kath_nums)
                    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                    day_name = days[context.get("day_of_week", 1)] if 0 <= context.get("day_of_week", 1) <= 6 else "Wednesday"
                    k_joined = " and ".join(kath_nums)
                    digest.append(f"**Kathismata:** Kathismata {k_joined} are read.")
                    digest.append(f"**Sessional Hymns:** After each Kathisma, we sing the Sessional Hymns from the Octoechos.")
                elif context.get("day_of_week") == 0:
                    digest.append("**Kathismata:** Kathismata are read. After each Kathisma: Small Litany, then we sing the Sessional Hymns from the Octoechos.")
                else:
                    suppress_oct = enriched.get("suppress_octoechos", False)
                    is_afterfeast = enriched.get("is_afterfeast") or enriched.get("period") in ("afterfeast", "apodosis")
                    is_polyeleos = (context.get("day_of_week") == 0) or enriched.get("rank") in (1, 2, "rank_polyeleos", "rank_vigil")
                    lit_prefix = "Small Litany, then " if is_polyeleos else ""
                    if suppress_oct or is_afterfeast:
                        if enriched.get("season_id") in ("triodion", "pentecostarion") or enriched.get("season") in ("triodion", "pentecostarion") or enriched.get("pascha_offset") is not None:
                            digest.append(f"**Sessional Hymns:** After each Kathisma: {lit_prefix}we sing the Sessional Hymns from the Triodion.")
                        else:
                            digest.append(f"**Sessional Hymns:** After each Kathisma: {lit_prefix}we sing the Sessional Hymns from the Menaion.")
                    else:
                        digest.append(f"**Sessional Hymns:** After each Kathisma: {lit_prefix}we sing the Sessional Hymns from the Octoechos.")
                    
                digest.append("")
                    
            if pascha_off not in (-3, -2, -1, 0):
                try:
                    res = self.engine.resolve_polyeleos_or_kathisma_17(enriched, rubrics)
                    formatted = self._format_resolve_polyeleos_or_kathisma_17(res, enriched)
                    if formatted:
                        digest.append(f"{formatted}  ")
                except Exception as e:
                    digest.append(f"[RESOLVE ERROR: resolve_polyeleos_or_kathisma_17: {e}]  ")
                    
                if context.get("day_of_week") == 0:
                    t_val = self._roman_tone(context.get("tone", 1))
                    digest.append(f"After, the Evlogitaria: the Hypakoë (Tone {t_val}), Hymns of Ascents, Prokeimenon, Let everything that has breath: in the tone of the week.  ")
                    
                try:
                    res = self.engine.resolve_matins_gospel(enriched)
                    if res:
                        if res.get("type") == "saint":
                            prok_res = self.engine.resolve_matins_prokeimenon(enriched, rubrics)
                            if prok_res:
                                digest.append(f"**Prokeimenon:**  \n> {prok_res.get('text')} (Tone {self._roman_tone(prok_res.get('tone'))}).  ")
                            digest.append(f"**Matins Gospel:** {res.get('title')}: {res.get('text')}.  ")
                        else:
                            eothinon_num = enriched.get("eothinon_number", 1)
                            citation = self._get_eothinon_gospel_citation(eothinon_num)
                            rom_num = self._roman_tone(eothinon_num)
                            cit_str = f": {citation}" if citation else ""
                            digest.append(f"**Matins Gospel {rom_num}**{cit_str}.  ")
                except Exception as e:
                    digest.append(f"[RESOLVE ERROR: resolve_matins_gospel: {e}]  ")
                    
                try:
                    res = self.engine.resolve_post_gospel_stichera(enriched)
                    if res and any("open_to_me" in s for s in res):
                        digest.append("After Psalm 50: instead of the usual hymns, we sing: Glory: Open to me the doors of repentance..., Both now: On the paths of salvation... and after the refrain Have mercy on me, O God, the sticheron: When I think of the many evil things I have done.  ")
                except Exception as e:
                    digest.append(f"[RESOLVE ERROR: resolve_post_gospel_stichera: {e}]  ")
                    
                is_weekday = 0 < enriched.get("day_of_week", 0) <= 5
                is_simple_6 = enriched.get("rank") == "rank_simple_6" or enriched.get("variables", {}).get("rank") == "rank_simple_6"
                is_simple_4 = enriched.get("rank") == "rank_simple_4" or enriched.get("variables", {}).get("rank") == "rank_simple_4"
                
                try:
                    if is_weekday and (is_simple_6 or is_simple_4):
                        if is_simple_6:
                            canon_details = "First Canon of the Octoechos with the Heirmos on 4; second Canon of the Octoechos on 4; Canon of the Saint on 6."
                        else:
                            canon_details = "First Canon of the Octoechos with the Heirmos on 6; second Canon of the Octoechos on 4; Canon of the Saint on 4."
                        digest.append(f"**Canon:** Order of the Canon: {canon_details} Katavasia: Heirmos of the last canon (of the Saint) after Odes 3, 6, 8, and 9.  ")
                        digest.append("")
                        digest.append("**After Ode III:** Sessional hymns; Glory... both now... Theotokion.  ")
                        digest.append("")
                        digest.append("**After Ode VI:** Kontakion and Ikos.  ")
                        digest.append("")
                        
                        try:
                            res = self.engine.resolve_magnificat(enriched)
                            if res and res.get("type") == "suppressed_magnificat":
                                digest.append("**After Ode VIII:** We sing 'We praise, we bless, we worship the Lord...'; at Ode IX we do not sing 'More honorable' but immediately the Heirmos of the Feast.  ")
                            else:
                                digest.append("**At Ode IX:** We sing the Magnification ('My soul magnifies the Lord...') and the refrains ('More honorable than the Cherubim...').  ")
                        except Exception:
                            digest.append("**At Ode IX:** We sing the Magnification ('My soul magnifies the Lord...') and the refrains ('More honorable than the Cherubim...').  ")
                        digest.append("")
                        
                        digest.append("> **Note:** At the 9th Ode, the priest censes as at Great Matins.  ")
                        digest.append("")
                    else:
                        canon_res = self.engine.resolve_canon_stack(enriched)
                        dist = canon_res.get("distribution", [])
                        canon_sources = []
                        for item in dist:
                            src = self.humanize_key(item.get("source", ""))
                            count = item.get("qty") or item.get("count", 4)
                            if src.lower() == "octoechos":
                                canon_sources.append(f"Octoechos on {count}")
                            elif src.lower() == "menaion" or "saint" in src.lower():
                                canon_sources.append(f"Saint on {count}")
                            elif "triodion" in src.lower():
                                canon_sources.append(f"Triodion on {count}")
                            elif "pentecostarion" in src.lower():
                                canon_sources.append(f"Pentecostarion on {count}")
                            elif "feast" in src.lower():
                                canon_sources.append(f"Feast on {count}")
                            elif "temple" in src.lower():
                                canon_sources.append(f"Temple on {count}")
                            else:
                                canon_sources.append(f"{src} on {count}")
                                
                        # Dedup the sources
                        seen = set()
                        deduped_sources = []
                        for cs in canon_sources:
                            if cs not in seen:
                                seen.add(cs)
                                deduped_sources.append(cs)
                                
                        canon_order = ", then the ".join(deduped_sources)
                        suppress_oct = enriched.get("suppress_octoechos", False)
                        irmos_source = "Heirmos from the Feast" if suppress_oct else "Heirmos from the Octoechos"
                        digest.append(f"**Canon:** We sing the canon of the {canon_order}. At each ode: {irmos_source}; troparia with refrains; Glory... both now.")
                        digest.append("")
                        digest.append("**After Ode III:** Sessional hymns; Glory... both now... Theotokion.")
                        digest.append("")
                        digest.append("**After Ode VI:** Kontakion and Ikos.")
                        digest.append("")
                        
                        try:
                            res = self.engine.resolve_magnificat(enriched)
                            if res and res.get("type") == "suppressed_magnificat":
                                digest.append("**After Ode VIII:** We sing 'We praise, we bless, we worship the Lord...'; at Ode IX we do not sing 'More honorable' but immediately the Heirmos of the Feast.  ")
                            else:
                                digest.append("**At Ode IX:** We sing the Magnification.  ")
                        except Exception:
                            digest.append("**At Ode IX:** We sing the Magnification.  ")
                        digest.append("")
                except Exception as e:
                    digest.append(f"[RESOLVE ERROR: resolve_canon_stack: {e}]")

                try:
                    kat_res = self.engine.resolve_katavasia(enriched)
                    formatted = self._format_resolve_katavasia(kat_res, enriched)
                    if formatted:
                        digest.append(f"{formatted}  ")
                except Exception as e:
                    pass
                    
                if context.get("day_of_week") == 0:
                    t_val = self._roman_tone(context.get("tone", 1))
                    digest.append(f"Holy is the Lord... Tone {t_val}.  ")

                try:
                    res = self.engine.resolve_exapostilarion_matins(enriched)
                    formatted = self._format_resolve_exapostilarion_matins(res, enriched)
                    if formatted:
                        if digest and digest[-1] != "":
                            digest.append("")
                        if formatted.startswith("Exapostilarion:"):
                            formatted = "**Exapostilarion** -" + formatted[len("Exapostilarion:"):]
                        digest.append(f"{formatted}  ")
                except Exception as e:
                    digest.append(f"[RESOLVE ERROR: resolve_exapostilarion_matins: {e}]  ")
                    
                try:
                    res = self.engine.resolve_praises_stichera(enriched)
                    formatted = self._format_resolve_praises_stichera(res, enriched)
                    if formatted:
                        if digest and digest[-1] != "":
                            digest.append("")
                        if formatted.startswith("At the Praises, we sing "):
                            formatted = "**At the Praises:** We sing " + formatted[len("At the Praises, we sing "):]
                        elif formatted.startswith("At the Praises"):
                            formatted = "**At the Praises:**" + formatted[len("At the Praises"):]
                        digest.append(f"{formatted}  ")
                except Exception as e:
                    digest.append(f"[RESOLVE ERROR: resolve_praises_stichera: {e}]  ")
                    
                if context.get("day_of_week") == 0:
                    try:
                        eothinon_num = enriched.get("eothinon_number", 1)
                        rom_num = self._roman_tone(eothinon_num)
                        digest.append(f"After the Dismissal of Matins: Glory... both now... Gospel Sticheron {rom_num}.  ")
                    except Exception as e:
                        digest.append(f"[RESOLVE ERROR: gospel_sticheron_formatting: {e}]  ")
                        
                try:
                    res = self.engine.resolve_aposticha_matins(enriched)
                except AttributeError:
                    try:
                        res = self.engine.resolve_aposticha(enriched)
                    except Exception:
                        res = None
                if res:
                    formatted = self._format_resolve_aposticha(res, enriched)
                    if formatted:
                        if digest and digest[-1] != "":
                            digest.append("")
                        if not formatted.startswith("**At the Aposticha:**"):
                            if formatted.startswith("At the Aposticha, we sing:"):
                                formatted = "**At the Aposticha:** We sing" + formatted[len("At the Aposticha, we sing:"):]
                            elif formatted.startswith("At the Aposticha"):
                                formatted = "**At the Aposticha:**" + formatted[len("At the Aposticha"):]
                            else:
                                formatted = "**At the Aposticha:** " + formatted
                        digest.append(f"{formatted}")
                
                # Exaltation of Cross Elevation Ceremony
                if context.get("date", "").endswith("-09-14"):
                    digest.append("")
                    digest.append("**Ceremony of the Elevation of the Precious and Life-Giving Cross:**")
                    digest.append("After the Great Doxology (sung), the celebrant carries the Precious Cross in solemn procession to the center of the temple, chanting *\"Wisdom! Stand aright!\"*")
                    digest.append("The priest elevates the Cross towards the four cardinal directions (East, West, South, North, and East again), while the choir sings *\"Lord, have mercy\"* 100 times for each station (500 times total).")
                    digest.append("**Veneration of the Cross:** Celebrant and faithful venerate the Cross while singing the hymn *\"Before Your Cross, we bow down in worship, O Master, and Your holy Resurrection we glorify\"* (thrice).")

                if is_weekday:
                    if digest and digest[-1] != "":
                        digest.append("")
                    try:
                        res = self.engine.resolve_matins_dismissal_troparion(enriched)
                        formatted = self._format_resolve_matins_dismissal_troparion(res, enriched)
                        if formatted:
                            digest.append(formatted)
                    except Exception as e:
                        digest.append(f"[RESOLVE ERROR: resolve_matins_dismissal_troparion: {e}]")
                    
            digest.append("")
            
        if "First Hour" in active_services or "Third Hour" in active_services:
            if digest and digest[-1] != "":
                digest.append("")
            pascha_off = enriched.get("pascha_offset")
            if pascha_off in (-6, -5, -4):
                day_names_hm = {-6: "Great and Holy Monday", -5: "Great and Holy Tuesday", -4: "Great and Holy Wednesday"}
                digest.append(f"## HOURS OF {day_names_hm[pascha_off].upper()}")
                digest.append("")
                digest.append("**At all the Hours:** Troparion: *\"Behold, the Bridegroom comes at midnight...\"*; Kontakion of the Day from the Holy Week Triodion.")
                digest.append("**At the 6th Hour:** Troparion of Prophecy, Prokeimenon, Paremia from Ezekiel, 2nd Prokeimenon.")
                digest.append("**At the Typika:** Beatitudes read quickly without singing; Prayer of St. Ephrem with 4 great prostrations. Aliturgical day (Presanctified Liturgy celebrated in the evening with Vespers).")
                digest.append("")
            elif pascha_off == -3:
                digest.append("## HOURS")
                digest.append("")
                digest.append("**At all the Hours:** Troparion and Kontakion of Great Thursday.")
                digest.append("**At the 1st Hour:** After the Theotokion 'What shall we call Thee', we read the Troparion of the Prophecy (Tone 3), 1st Prokeimenon (Tone 1: *\"Let them know that the Lord is Thy Name\"*), Paremia (**Jeremiah 11:18–12:5, 9–11, 14–15**), 2nd Prokeimenon (Tone 8: *\"Pray and give praise to the Lord our God\"*).")
                digest.append("**At the Typika:** Begins from Beatitudes without stichera; Creed is omitted. Kontakion of Great Thursday.")
                digest.append("")
            elif pascha_off == -2:
                digest.append("## ROYAL HOURS OF GREAT AND HOLY FRIDAY")
                digest.append("")
                digest.append("**Royal Hours (1st, 3rd, 6th, 9th):** Each hour contains special Psalms, Troparia of Prophecy, Old Testament Paremias, Epistles, and Gospels of the Passion.")
                digest.append("  - **1st Hour:** Paremia: Zechariah 11:10–13; Epistle: Galatians 6:14–18; Gospel: Matthew 27:1–56.")
                digest.append("  - **3rd Hour:** Paremia: Isaiah 50:4–11; Epistle: Romans 5:6–10; Gospel: Mark 15:16–41.")
                digest.append("  - **6th Hour:** Paremia: Isaiah 52:13–54:1; Epistle: Hebrews 2:11–18; Gospel: Luke 23:32–49.")
                digest.append("  - **9th Hour:** Paremia: Jeremiah 11:18–12:5, 9–11, 14–15; Epistle: Hebrews 10:19–31; Gospel: John 18:28–19:37.")
                digest.append("**Typika:** Beatitudes with 8 Troparia; Kontakion 'For our sake was the Crucified'. Aliturgical Day.")
                digest.append("")
            elif pascha_off in range(0, 7):
                digest.append("## PASCHAL HOURS")
                digest.append("")
                digest.append("The Paschal Hours are sung in place of the 1st, 3rd, 6th, and 9th Hours, as well as Compline and Midnight Office throughout Bright Week:  \n"
                              "  - *\"Christ is risen from the dead...\"* (thrice)  \n"
                              "  - *\"Having beheld the Resurrection of Christ...\"* (thrice)  \n"
                              "  - Hypakoë: *\"When they who were with Mary came...\"*  \n"
                              "  - Kontakion: *\"Though You went down into the tomb...\"*  \n"
                              "  - Troparia: *\"In the tomb with the body...\"*; *Glory...* *\"How life-giving...\"*; *Both now...* *\"Rejoice, O sanctified tabernacle...\"*  \n"
                              "  - *\"Lord, have mercy\"* (40 times), *\"Glory... Both now... More honorable than the Cherubim...\"*  \n"
                              "  - *\"Christ is risen...\"* (thrice), and the Paschal Dismissal.")
                digest.append("")
            else:
                digest.append("## HOURS")
                try:
                    hours_str = self._format_qr_hours(enriched, rubrics)
                    digest.append(hours_str)
                except Exception as e:
                    digest.append(f"[RESOLVE ERROR: hours summary failed - {e}]  ")
                digest.append("")
            
        lit_type = rubrics.get("overrides", {}).get("liturgy_type") or rubrics.get("variables", {}).get("liturgy_type", "")
        is_liturgy_active = ("Divine Liturgy" in active_services or "Liturgy" in active_services or "Typika" in active_services or "vesperal" in lit_type.lower()) and rubrics.get("overrides", {}).get("liturgy_type") != "structure_suppressed"
        if is_liturgy_active:
            if digest and digest[-1] != "":
                digest.append("")
            p_off = enriched.get("pascha_offset")
            try:
                p_off = int(p_off) if p_off is not None else None
            except (ValueError, TypeError):
                p_off = None
            dt_s = str(enriched.get("date", ""))
            is_annun = dt_s.endswith("-03-25") or enriched.get("feast_id") == "annunciation" or "annunciation" in str(enriched.get("title", "")).lower()

            if "chrysostom_vesperal" in lit_type.lower() or (enriched.get("scenario_id") == "collision_annunciation_great_friday"):
                digest.append("## VESPERAL DIVINE LITURGY OF ST. JOHN CHRYSOSTOM")
            elif p_off == 0 and is_annun:
                digest.append("## DIVINE LITURGY OF ST. JOHN CHRYSOSTOM (KYRIOPASCHA)")
            elif "basil" in lit_type.lower():
                digest.append("## DIVINE LITURGY OF SAINT BASIL THE GREAT")
            elif "chrysostom" in lit_type.lower():
                digest.append("## DIVINE LITURGY OF ST. JOHN CHRYSOSTOM")
            elif lit_type in ("structure_aliturgical", "aliturgical"):
                digest.append("## TYPIKA (ALITURGICAL)")
            else:
                digest.append("## DIVINE LITURGY")
                
            try:
                antiphons_res = self.engine.resolve_liturgy_antiphons(enriched, rubrics)
                beatitudes_res = self.engine.resolve_beatitudes(enriched)
                
                stichera_parts = []
                total_qty = 0
                if beatitudes_res and beatitudes_res.get("stichera"):
                    for s in beatitudes_res["stichera"]:
                        src = s.get("source", "")
                        qty = s.get("count", 0)
                        total_qty += qty
                        
                        src_str = self.humanize_key(src)
                        if src.lower() == "octoechos":
                            src_str = "Octoechos"
                        elif src.lower() == "triodion":
                            src_str = "Triodion"
                        elif src.lower() == "menaion":
                            title_lower = title.lower()
                            if "forefeast" in title_lower:
                                src_str = "forefeast"
                            else:
                                src_str = "Menaion"
                        stichera_parts.append(f"{src_str} - {qty}")
                        
                if total_qty > 0:
                    beat_str = f"Beatitudes on {total_qty}: {', '.join(stichera_parts)}."
                else:
                    beat_str = "Beatitudes."
                    
                if antiphons_res and antiphons_res.get("type") == "festal_antiphons":
                    digest.append("**Antiphons:** Festal Antiphons.  ")
                else:
                    digest.append(f"**Typika & Beatitudes:** Psalms of Typica; {beat_str}  ")
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: liturgy_antiphons_or_beatitudes: {e}]  ")
                
            try:
                res = self.engine.resolve_liturgy_hymns(enriched, rubrics)
                formatted = self._format_resolve_liturgy_hymns(res, enriched)
                if formatted:
                    digest.append(f"{formatted}")
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: resolve_liturgy_hymns: {e}]  ")
                
            try:
                readings_str = self._format_qr_readings(enriched, rubrics)
                if readings_str:
                    digest.append(readings_str)
            except Exception as e:
                digest.append(f"[RESOLVE ERROR: readings_formatting: {e}]  ")
                
            digest.append("")
            
        collision_rule = self.engine.check_collision(context)
        if collision_rule and "rubric" in collision_rule and "notes" in collision_rule["rubric"]:
            notes = collision_rule["rubric"]["notes"]
            if notes:
                digest.append("## NOTES & FOOTNOTES")
                if isinstance(notes, list):
                    for idx, note in enumerate(notes):
                        digest.append(f"{idx+1}. {note}  ")
                else:
                    digest.append(f"{notes}  ")

        try:
            day_footnotes = self.engine.resolve_synodal_footnotes(enriched, rubrics)
            if day_footnotes:
                fn_section = self._format_synodal_footnotes_section(day_footnotes)
                if fn_section:
                    if digest and digest[-1] != "":
                        digest.append("")
                    digest.append(fn_section)
        except Exception:
            pass
                    
        formatted_md = []
        for line in digest:
            if line is None:
                formatted_md.append("")
            elif isinstance(line, str):
                if not line:
                    formatted_md.append("")
                else:
                    formatted_md.extend(line.splitlines())
            else:
                formatted_md.append(str(line))
                
        return "\n".join(formatted_md)


    def _apply_link_overrides(self, sequence, overrides):
        seq = copy.deepcopy(sequence)
        for override in overrides:
            target_id = override.get("target_id")
            action = override.get("action")
            
            indices = [i for i, slot in enumerate(seq) if slot.get("id") == target_id]
            if not indices:
                continue
            idx = indices[0]

            if action == "replace":
                seq[idx] = override.get("new_component")
            elif action == "delete":
                del seq[idx]
            elif action == "insert_after":
                seq.insert(idx + 1, override.get("new_component"))
            elif action == "insert_before":
                seq.insert(idx, override.get("new_component"))
            elif action == "modify":
                if "rubric" in override:
                    seq[idx]["rubric"] = override["rubric"]
                if "content" in override:
                    seq[idx]["content"] = override["content"]
                if "logic_args" in override:
                    if "content" in seq[idx] and "logic" in seq[idx]["content"]:
                         if "args" not in seq[idx]["content"]["logic"]:
                             seq[idx]["content"]["logic"]["args"] = {}
                         seq[idx]["content"]["logic"]["args"].update(override["logic_args"])
        return seq


    def _process_skeleton(self, skeleton, context, rubrics, digest):
        trivial_titles = [
            "rubric", "opening", "trisagion", "readings", "litany", "great litany", 
            "small litany", "our father", "introductory prayers", "invitatory", 
            "psalm 103", "psalm 50", "six psalms", "dismissal", "kathisma 17",
            "prothesis", "blessing", "the kathisma", "the kathismata", "the canon",
            "at 9th ode", "prayer of st. ephrem", "the prothesis (preparation)",
            "the antiphons", "the little entrance", "troparia and kontakia",
            "cherubic hymn", "the great entrance", "communion", "invitatory 3x",
            "doxology small read", "creed", "axion estin"
        ]
        
        boilerplate_notes = {
            "current kathisma for the day of the week.",
            "two kathismata are read. on sundays, the polyeleos follows.",
            "two or three kathismata with sessional hymns, same as great matins.",
            "katavasia is irmos of last canon, not current seasonal.",
            "at 9th ode priest censes as at great matins.",
            "sung according to the typikon.",
            "sung according to the order of precedence (temple, day, patron).",
            "prayers are longer. choir must sing responses slowly.",
            "kathisma 17 (psalm 118) is read in three stations (staseis), with encomia stichera interspersed at each verse. priest censes at each station."
        }

        for slot in skeleton:
            if slot.get("id") == "graduals_block":
                is_sunday = context.get("day_of_week") == 0 or context.get("is_sunday_vigil")
                rank = self.engine.calculate_rank(context)
                if not is_sunday and rank > 2:
                    continue
            # Group Kathismata into a single clean line
            if slot.get("id") in ("kathismata_block", "kathismata_daily_block", "kathismata_lenten"):
                try:
                    grouped_text = self._format_grouped_kathismata(slot, context, rubrics)
                    if grouped_text:
                        if "rubric" in slot:
                            r = slot["rubric"]
                            title = r.get('title') if isinstance(r, dict) else r
                            note = r.get('note') if isinstance(r, dict) else ""
                            
                            title_lower = title.lower().strip()
                            note_lower = note.lower().strip() if note else ""
                            is_trivial = False
                            if not title_lower:
                                if note_lower in boilerplate_notes:
                                    is_trivial = True
                            elif any(term in title_lower for term in trivial_titles):
                                if not note_lower or note_lower in boilerplate_notes:
                                    is_trivial = True
                            
                            if not is_trivial and title and title.lower() != "rubric":
                                pass
                        if digest and digest[-1] != "":
                            digest.append("")
                        digest.append(grouped_text)
                except Exception as e:
                    digest.append(f"[ERROR: Grouping Kathismata failed - {e}]")
                continue

            # 0. Check slot condition if present
            if "condition" in slot:
                cond = slot["condition"]
                if cond == "if_lenten":
                    is_lenten = (
                        context.get("is_lenten") or 
                        "lenten" in rubrics.get("variables", {}).get("hours_type", "") or 
                        context.get("triodion_period") in ["lent_weeks_1_6", "holy_week", "lent_week_1", "lent_weeks_2_6", "great_lent"]
                    )
                    if not is_lenten:
                        continue
                elif cond == "if_sunday":
                    if context.get("day_of_week") != 0:
                        continue

            # Output matins canon description if defined
            if slot.get("id") in ("canon_pascha", "canon_block") and rubrics.get("variables", {}).get("matins_canon_description"):
                digest.append(f"At the Canon: {rubrics['variables']['matins_canon_description']}")

            # 1. Print rubric info if any (filter out trivial boilerplate and structural ordinaries)
            if "rubric" in slot:
                r = slot["rubric"]
                is_trivial = False
                if not isinstance(r, dict):
                    title = str(r)
                    note = ""
                    ordo_ref = ""
                else:
                    title = r.get('title') or r.get('description') or r.get('text') or ""
                    note = r.get('note') or ""
                    ordo_ref = r.get('ordo_ref') or ""
                
                title_lower = title.lower().strip()
                note_lower = note.lower().strip() if note else ""
                
                if not title_lower:
                    if note_lower in boilerplate_notes:
                        is_trivial = True
                elif any(term in title_lower for term in trivial_titles):
                    if not note_lower or note_lower in boilerplate_notes:
                        is_trivial = True
                
                if "post-ode 9 hymn" in title_lower:
                    pascha_offset = context.get("pascha_offset")
                    is_afterfeast_or_feast = (
                        context.get("is_afterfeast") or
                        context.get("is_fore_or_afterfeast") or
                        (pascha_offset is not None and 60 <= pascha_offset <= 67)
                    )
                    if is_afterfeast_or_feast:
                        is_trivial = True
                
                if slot.get("id") == "post_doxology_event":
                    try:
                        res_dox = self.engine.resolve_post_doxology_event(context, rubrics)
                        if not res_dox:
                            is_trivial = True
                    except Exception:
                        pass
                
                if not is_trivial:
                    if isinstance(r, dict):
                        parts = []
                        if title and title.lower() != "rubric":
                            parts.append(title)
                        if note:
                            parts.append(note)
                        if parts:
                            pass
                    else:
                        title = str(r)
                        if title and title.lower() != "rubric":
                            pass

            content = slot.get("content", {})
            if not content and "type" in slot:
                content = slot
            slot_type = content.get("type")

            enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}

            if slot_type == "variable_logic":
                logic = content.get("logic", {})
                func_name = logic.get("function")
                args = logic.get("args", {})
                self._format_logic_hook(func_name, args, context, rubrics, digest)
                
            elif slot_type == "generator":
                method = content.get("generator_method")
                args = content.get("args", {})
                self._format_generator_hook(method, args, context, rubrics, digest)
                
            elif slot_type == "sequence" or slot_type == "complex_structure":
                if "components" in content:
                    self._process_skeleton(content["components"], context, rubrics, digest)
                    
            elif slot_type == "slot_variable":
                slot_id = content.get("slot_id")
                # Handle liturgy readings slot variables
                if slot_id in ("liturgy_prokeimenon", "liturgy_epistle", "liturgy_alleluia", "liturgy_gospel"):
                    is_weekday = 0 < enriched.get("day_of_week", 0) <= 5
                    is_simple = enriched.get("rank") in ("rank_simple_6", "rank_simple_4") or enriched.get("variables", {}).get("rank") in ("rank_simple_6", "rank_simple_4")
                    if is_weekday and is_simple:
                        if not getattr(self, "_liturgy_readings_printed", False):
                            try:
                                res = self.engine.resolve_liturgy_readings(enriched, rubrics)
                                if res and res.get("readings"):
                                    r = res["readings"][0]
                                    r_parts = []
                                    p = r.get("prokeimenon", {})
                                    if p:
                                        tone = p.get("tone") or 7
                                        tone_roman = self._roman_tone(tone)
                                        text = p.get("text") or p.get("content")
                                        if self._is_missing(text):
                                            text = None
                                        if not text:
                                            text = "The righteous shall rejoice in the Lord..."
                                        text_clean = text.strip('"').rstrip('.')
                                        r_parts.append(f"**Prokeimenon:**  \n> Tone {tone_roman}: \"{text_clean}\"")
                                    e = r.get("epistle", {})
                                    if e:
                                        text = e.get("text") or e.get("content")
                                        if self._is_missing(text):
                                            text = None
                                        if not text:
                                            text = "Romans 7:14-8:2"
                                        r_parts.append(f"**Epistle:**  \n> {text}")
                                    a = r.get("alleluia", {})
                                    if a:
                                        tone = a.get("tone") or (p.get("tone") if p else None) or 4
                                        r_parts.append(f"**Alleluia:**  \n> Tone {self._roman_tone(tone) if isinstance(tone, int) else tone}, with verses of the day.")
                                    g = r.get("gospel", {})
                                    if g:
                                        text = g.get("text") or g.get("content")
                                        if self._is_missing(text):
                                            text = None
                                        if not text:
                                            text = "Matthew 10:9-15"
                                        r_parts.append(f"**Gospel:**  \n> {text}")
                                    
                                    # Communion hymn lookup
                                    c_text = "In everlasting remembrance shall the righteous be..."
                                    try:
                                        kin_res = self.engine.resolve_communion_hymn(enriched, rubrics)
                                        if kin_res and kin_res.get("text") and not self._is_missing(kin_res.get("text")):
                                            c_text = kin_res["text"]
                                        elif kin_res and kin_res.get("content") and not self._is_missing(kin_res.get("content")):
                                            c_text = kin_res["content"]
                                    except Exception:
                                        pass
                                    cleaned_c = self._clean_hymn_text(c_text)
                                    r_parts.append(f"**Communion Hymn:** {cleaned_c}")
                                    
                                    digest.append("\n".join(r_parts))
                                    self._liturgy_readings_printed = True
                            except Exception as e_res:
                                digest.append(f"[ERROR: Combined readings resolution failed - {e_res}]")
                        continue
                    if getattr(self, "_liturgy_readings_printed", False):
                        continue
                        
                    try:
                        res = self.engine.resolve_liturgy_readings(enriched, rubrics)
                        if res and res.get("readings"):
                            def get_ref_label_local(ref_key, fallback_default):
                                if not ref_key:
                                    return f"*{fallback_default}*"
                                if ref_key.startswith("menaion."):
                                    name = "Saint"
                                    if enriched.get("feast_level") in ("lord", "theotokos") or enriched.get("is_fore_or_afterfeast"):
                                        name = enriched.get("title") or enriched.get("feast_name") or "the Feast"
                                    else:
                                        s_list = enriched.get("saints", [])
                                        for s in s_list:
                                            s_id = s.get("id", "")
                                            if s_id and s_id in ref_key:
                                                name = s.get("name", "Saint")
                                                break
                                    if name == "Saint":
                                        parts = ref_key.split('.')
                                        if len(parts) >= 4:
                                            name = self.humanize_key(parts[2])
                                        elif len(parts) >= 3:
                                            if parts[2].lower() in ("prokeimenon", "epistle", "alleluia", "gospel") and len(parts) >= 2:
                                                name = self.humanize_key(parts[1])
                                            else:
                                                name = self.humanize_key(parts[2])
                                        else:
                                            name = enriched.get("title") or "the Saint"
                                    name_human = self.humanize_key(name)
                                    if name_human.startswith("Menaion.") or name_human.startswith("Menaion "):
                                        name_human = enriched.get("title") or "the Saint"
                                    return f"*of {name_human}*"
                                
                                scripture_val = self._format_scripture_key(ref_key)
                                if scripture_val and scripture_val != self.humanize_key(ref_key):
                                    return f"*{scripture_val}*"
                                
                                ref_str = self.humanize_key(ref_key)
                                if not ref_str or ref_str.lower() in (fallback_default.lower(), f"{fallback_default.lower()}_daily") or "day_" in ref_key.lower():
                                    return "*of the day*"
                                
                                ref_clean = ref_str.replace("Prokimenon", "").replace("Prokeimenon", "").replace("Epistle", "").replace("Alleluia", "").replace("Gospel", "").strip()
                                return f"*{ref_clean}*"

                            for idx, r in enumerate(res["readings"]):
                                if slot_id == "liturgy_prokeimenon" and "prokeimenon" in r:
                                    p = r["prokeimenon"]
                                    text = p.get("text") or p.get("content")
                                    if self._is_missing(text):
                                        text = None
                                    if not text and p.get("ref_key"):
                                        asset = self.engine.get_text(p["ref_key"])
                                        if asset and not self._is_missing(asset):
                                            text = asset.get("content")
                                            if self._is_missing(text):
                                                text = None
                                            if asset.get("tone") and not p.get("tone"):
                                                p["tone"] = asset["tone"]
                                    tone_str = f" Tone {self._roman_tone(p.get('tone'))}" if p.get('tone') else ""
                                    if len(res["readings"]) > 1:
                                        label = "Prokeimenon (Feast - sung twice)" if idx == 0 else "Prokeimenon (Saint - sung once, without verse)"
                                    else:
                                        label = "Prokeimenon"
                                    if text:
                                        text_clean = text.strip('"').rstrip('.')
                                        p_body = f"{tone_str.strip()}: \"{text_clean}\"" if tone_str.strip() else f"\"{text_clean}\""
                                        digest.append(f"**{label}:**  \n> {p_body}")
                                    else:
                                        ref_key = p.get("ref_key", "")
                                        val = get_ref_label_local(ref_key, "Prokeimenon")
                                        val_clean = val.strip('*')
                                        if val_clean.lower() in ("the feast", "of the feast"):
                                            val_clean = enriched.get("title") or enriched.get("rubrics_title") or "the Feast"
                                        if not val_clean.lower().startswith("of "):
                                            val_clean = f"of {val_clean}"
                                        p_body = f"{val_clean}{' (Tone ' + self._roman_tone(p.get('tone')) + ')' if p.get('tone') else ''}"
                                        digest.append(f"**{label}:**  \n> {p_body}")
                                elif slot_id == "liturgy_epistle" and "epistle" in r:
                                    e = r["epistle"]
                                    text = e.get("text") or e.get("content")
                                    if self._is_missing(text):
                                        text = None
                                    if not text and e.get("ref_key"):
                                        scripture_val = self._format_scripture_key(e["ref_key"])
                                        if scripture_val and scripture_val != self.humanize_key(e["ref_key"]):
                                            text = scripture_val
                                    if text:
                                        digest.append(f"**Epistle:**  \n> {text}")
                                    else:
                                        ref_key = e.get("ref_key", "")
                                        val = get_ref_label_local(ref_key, "Epistle")
                                        val_clean = val.strip('*')
                                        if val_clean.lower() in ("the feast", "of the feast"):
                                            val_clean = enriched.get("title") or enriched.get("rubrics_title") or "the Feast"
                                        if not val_clean.lower().startswith("of "):
                                            val_clean = f"of {val_clean}"
                                        digest.append(f"**Epistle:**  \n> {val_clean}")
                                elif slot_id == "liturgy_alleluia" and "alleluia" in r:
                                    try:
                                        all_res = r["alleluia"]
                                        if all_res:
                                            ref_key = all_res.get("ref_key", "")
                                            text = all_res.get("text") or all_res.get("content")
                                            if self._is_missing(text):
                                                text = None
                                                all_res["text"] = None
                                                all_res["content"] = None
                                            if ref_key and not text and not all_res.get("verses"):
                                                asset = self.engine.get_text(ref_key)
                                                if asset and not self._is_missing(asset):
                                                    raw_content = asset.get("content")
                                                    if isinstance(raw_content, str):
                                                        text = raw_content
                                                    elif isinstance(raw_content, dict):
                                                        text = raw_content.get("text") or raw_content.get("content")
                                                        if raw_content.get("verses"):
                                                            all_res["verses"] = raw_content["verses"]
                                                    if asset.get("tone") and not all_res.get("tone"):
                                                        all_res["tone"] = asset["tone"]
                                            
                                            text = all_res.get("text") or all_res.get("content")
                                            if self._is_missing(text):
                                                text = None
                                            
                                            tone = all_res.get("tone")
                                            tone_str = f"Tone {self._roman_tone(tone)}" if tone else ""
                                            verses = all_res.get("verses")
                                            if len(res["readings"]) > 1:
                                                label = "Alleluia (Feast)" if idx == 0 else "Alleluia (Saint)"
                                            else:
                                                label = "Alleluia"
                                            
                                            if verses and isinstance(verses, list):
                                                v_str = "\n> ".join(f"*Verse:* \"{v.strip('\"')}\"" for v in verses)
                                                header = f"{tone_str}:" if tone_str else ""
                                                digest.append(f"**{label}:**  \n> {header}\n> {v_str}")
                                            elif text:
                                                text_clean = text.strip('"').rstrip('.')
                                                digest.append(f"**{label}:**  \n> {tone_str}: \"{text_clean}\"")
                                            else:
                                                val = get_ref_label_local(ref_key, "Alleluia")
                                                val_clean = val.strip('*')
                                                if val_clean.lower() in ("the feast", "of the feast"):
                                                    val_clean = enriched.get("title") or enriched.get("rubrics_title") or "the Feast"
                                                if not val_clean.lower().startswith("of "):
                                                    val_clean = f"of {val_clean}"
                                                digest.append(f"**{label}:**  \n> {val_clean}")
                                    except Exception as e_all:
                                        digest.append(f"[ERROR: resolve_liturgy_alleluia failed - {e_all}]")
                                elif slot_id == "liturgy_gospel" and "gospel" in r:
                                    g = r["gospel"]
                                    text = g.get("text") or g.get("content")
                                    if self._is_missing(text):
                                        text = None
                                    if not text and g.get("ref_key"):
                                        scripture_val = self._format_scripture_key(g["ref_key"])
                                        if scripture_val and scripture_val != self.humanize_key(g["ref_key"]):
                                            text = scripture_val
                                    if text:
                                        digest.append(f"**Gospel:**  \n> {text}")
                                    else:
                                        ref_key = g.get("ref_key", "")
                                        val = get_ref_label_local(ref_key, "Gospel")
                                        val_clean = val.strip('*')
                                        if val_clean.lower() in ("the feast", "of the feast"):
                                            val_clean = enriched.get("title") or enriched.get("rubrics_title") or "the Feast"
                                        if not val_clean.lower().startswith("of "):
                                            val_clean = f"of {val_clean}"
                                        digest.append(f"**Gospel:**  \n> {val_clean}")
                    except Exception as e:
                        digest.append(f"[ERROR: Resolving liturgy readings failed - {e}]")
                elif "kontakion" in str(slot_id):
                    try:
                        hour = content.get("hour") or slot.get("hour")
                        if not hour and "hour_" in str(slot_id):
                            match = re.search(r'hour_(\d+)', str(slot_id))
                            if match:
                                hour = int(match.group(1))
                        if not hour:
                            hour = 1
                        enriched_hour = {**enriched, "hour": hour}
                        res = self.engine.resolve_hours_kontakion(enriched_hour, rubrics)
                        if res:
                            source = res.get("source", "saint_or_feast")
                            if source in ("resurrection", "triodion"):
                                if enriched_hour.get("triodion_period") or source == "triodion":
                                    triodion_id = enriched_hour.get("triodion_id") or "triodion"
                                    digest.append(f"Kontakion: from the Triodion ({self.humanize_key(triodion_id)})")
                                else:
                                    tone = enriched_hour.get("tone", 1)
                                    digest.append(f"Kontakion: of the Resurrection in Tone {tone}")
                            elif source == "triodion_saint":
                                r_title_lower = rubrics.get("title", "").lower()
                                if "palamas" in r_title_lower:
                                    digest.append("Kontakion: of the Saint (St. Gregory Palamas)")
                                elif "john of the ladder" in r_title_lower or "climacus" in r_title_lower:
                                    digest.append("Kontakion: of the Saint (St. John Climacus)")
                                else:
                                    digest.append("Kontakion: of the Saint")
                            elif source == "day":
                                digest.append("Kontakion: of the Day")
                            elif source == "temple":
                                digest.append("Kontakion: of the Temple")
                            elif source == "feast":
                                pascha_offset = enriched_hour.get("pascha_offset")
                                if pascha_offset is not None and 60 <= pascha_offset <= 67:
                                    digest.append("Kontakion: of the Eucharist")
                                elif enriched_hour.get("feast_id"):
                                    digest.append(f"Kontakion: of the Feast ({self.humanize_key(enriched_hour['feast_id'])})")
                                else:
                                    digest.append("Kontakion: of the Feast")
                            elif source == "saints":
                                if enriched_hour.get("saints"):
                                    name = enriched_hour['saints'][0].get('name', 'Saint').rstrip('.')
                                    digest.append(f"Kontakion: of {name}")
                                else:
                                    digest.append("Kontakion: of the Saint")
                            elif source == "saints_2":
                                if len(enriched_hour.get("saints", [])) >= 2:
                                    digest.append(f"Kontakion: of {self.humanize_key(enriched_hour['saints'][1].get('name', 'second Saint'))}")
                                else:
                                    digest.append("Kontakion: of the second Saint")
                            else:
                                if enriched_hour.get("feast_id"):
                                    digest.append(f"Kontakion: of the Feast ({self.humanize_key(enriched_hour['feast_id'])})")
                                elif enriched_hour.get("is_forefeast") or enriched_hour.get("is_afterfeast"):
                                    digest.append("Kontakion: of the Forefeast")
                                elif enriched_hour.get("saints"):
                                    s_names = [self.humanize_key(s.get("name", "Saint")) for s in enriched_hour["saints"]]
                                    digest.append(f"Kontakion: of {', '.join(s_names)}")
                                else:
                                    digest.append("Kontakion: of the Temple")
                    except Exception as e:
                        digest.append(f"[ERROR: Resolving hour kontakion failed - {e}]")

            elif slot_type in ("canon_ode", "canon_ode_range"):
                is_weekday = 0 < enriched.get("day_of_week", 0) <= 5
                is_simple_6 = enriched.get("rank") == "rank_simple_6" or enriched.get("variables", {}).get("rank") == "rank_simple_6"
                is_simple_4 = enriched.get("rank") == "rank_simple_4" or enriched.get("variables", {}).get("rank") == "rank_simple_4"
                if is_weekday and (is_simple_6 or is_simple_4):
                    if not getattr(self, "_matins_canon_printed", False):
                        if is_simple_6:
                            canon_details = "First Canon of the Octoechos with the Heirmos on 4; second Canon of the Octoechos on 4; Canon of the Saint on 6."
                        else:
                            canon_details = "First Canon of the Octoechos with the Heirmos on 6; second Canon of the Octoechos on 4; Canon of the Saint on 4."
                        digest.append(f"**Canon:** Order of the Canon: {canon_details} Katavasia: Heirmos of the last canon (of the Saint) after Odes 3, 6, 8, and 9.")
                        digest.append("")
                        digest.append("> **Note:** At the 9th Ode, the priest censes as at Great Matins.")
                        self._matins_canon_printed = True
                    continue
                
                if not getattr(self, "_matins_canon_printed", False):
                    try:
                        res = self.engine.resolve_canon_structure(1, enriched)
                        formatted = self._format_resolve_canon_structure(res, enriched)
                        if formatted:
                            digest.append(formatted)
                            digest.append("")
                    except Exception as e:
                        digest.append(f"[ERROR: resolve_canon_structure failed - {str(e)}]")
                    self._matins_canon_printed = True

            elif slot_type == "conditional_block":
                logic = content.get("logic", {})
                func_name = logic.get("function")
                args = logic.get("args", {})
                
                result = False
                if hasattr(self.engine, func_name):
                    try:
                        func = getattr(self.engine, func_name)
                        import inspect
                        sig = inspect.signature(func)
                        call_kwargs = {}
                        if "rubrics" in sig.parameters:
                            call_kwargs["rubrics"] = rubrics
                            
                        normalized_args = {}
                        for k, v in args.items():
                            if k == "pos":
                                normalized_args["position"] = v
                            elif k == "num":
                                normalized_args["num"] = v
                            else:
                                normalized_args[k] = v
                                
                        for param_name in sig.parameters:
                            if param_name in normalized_args:
                                call_kwargs[param_name] = normalized_args[param_name]
                                
                        params = list(sig.parameters.values())
                        has_context = len(params) > 0
                        
                        if has_context:
                            result = func(enriched, **call_kwargs)
                        else:
                            result = func()
                    except Exception as e:
                        digest.append(f"[ERROR: Evaluating conditional {func_name} failed - {e}]")
                else:
                    digest.append(f"[ERROR: Missing condition helper {func_name}]")
                
                # Recurse
                target_content = content.get("true_content") if result else content.get("false_content")
                if target_content:
                    if isinstance(target_content, list):
                        self._process_skeleton(target_content, context, rubrics, digest)
                    elif isinstance(target_content, dict):
                        self._process_skeleton([target_content], context, rubrics, digest)
                    
            elif slot_type == "structure_ref":
                target_file = content.get("file")
                root_id = content.get("root_id")
                if target_file and root_id:
                    try:
                        linked_data = self.engine._load_json(target_file)
                        sub_skeleton = self.engine._get_structure_sequence(linked_data, root_id)
                        if sub_skeleton:
                            self._process_skeleton(sub_skeleton, context, rubrics, digest)
                        else:
                            digest.append(f"[ERROR: Structure ref '{root_id}' not found in {target_file}]")
                    except Exception as e:
                        digest.append(f"[ERROR: Loading Structure Ref {root_id} from {target_file} failed - {e}]")

            elif slot_type == "fixed_ref":
                ref_key = content.get("ref_key")
                if ref_key:
                    ref_key_lower = ref_key.lower()
                    is_trivial = False
                    if "litany" in ref_key_lower or "litanies" in ref_key_lower or "our_father" in ref_key_lower or "trisagion" in ref_key_lower or "creed" in ref_key_lower:
                        is_trivial = True
                    elif ref_key_lower.startswith("horologion.") or ref_key_lower.startswith("liturgikon."):
                        is_trivial = True
                    
                    if not is_trivial:
                        txt_res = self.engine.get_text(ref_key)
                        title = self.humanize_key(ref_key)
                        if ref_key_lower == "triodion.let_my_prayer_arise":
                            digest.append("**Let My Prayer Arise:** *\"Let my prayer arise in Your sight as incense, and let the lifting up of my hands be an evening sacrifice.\"* (All kneel and prostrate during the chanting of the 6 verses).")
                        elif ref_key_lower == "triodion.now_the_powers_of_heaven":
                            digest.append("**Great Entrance:** *\"Now the heavenly powers invisibly minister with us...\"* (All prostrate in silence as the Presanctified Holy Gifts are carried to the Altar).")
                        elif ref_key_lower == "triodion.communion_hymn_taste_and_see":
                            digest.append("**Communion Hymn:** *\"O taste and see that the Lord is good. Alleluia.\"*")
                        elif ref_key_lower == "triodion.dismissal_presanctified":
                            digest.append("**Dismissal:** Presanctified Dismissal.")
                        elif txt_res and not self._is_missing(txt_res) and "content" in txt_res:
                            text_body = txt_res["content"].strip()
                            if not self._is_missing(text_body) and "[STUB]" not in text_body:
                                digest.append(f"**{title}:** {text_body}")

                
            elif slot_type == "fixed_group":
                # Skip printing structural ordinaries in the digest
                pass
                
            elif slot_type == "link":
                target_id = slot.get('target_id')
                target_file = slot.get('target_file')
                if target_file and target_id:
                    full_path = os.path.join(self.engine.json_db, target_file)
                    if not os.path.exists(full_path):
                        full_path = target_file
                    if os.path.exists(full_path):
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                linked_data = json.load(f)
                            sub_skeleton = self.engine._get_structure_sequence(linked_data, target_id)
                            if sub_skeleton:
                                if "start_at_component" in slot:
                                    start_id = slot["start_at_component"]
                                    start_idx = next((i for i, s in enumerate(sub_skeleton) if s.get("id") == start_id), -1)
                                    if start_idx != -1:
                                        sub_skeleton = sub_skeleton[start_idx:]
                                if "stop_after_component" in slot:
                                    stop_id = slot["stop_after_component"]
                                    stop_idx = next((i for i, s in enumerate(sub_skeleton) if s.get("id") == stop_id), -1)
                                    if stop_idx != -1:
                                        sub_skeleton = sub_skeleton[:stop_idx + 1]
                                if "overrides" in slot:
                                    sub_skeleton = self._apply_link_overrides(sub_skeleton, slot["overrides"])
                                self._process_skeleton(sub_skeleton, context, rubrics, digest)
                        except Exception as e:
                            digest.append(f"[ERROR: Loading Link {target_id} failed - {e}]")

            elif slot_type == "component_ref":
                ref_key = content.get("ref_key")
                if ref_key:
                    comp_name = ref_key
                    if comp_name.startswith("components."):
                        comp_name = comp_name.split("components.", 1)[1]
                    comp = self.engine.components.get(comp_name)
                    if comp:
                        seq = comp.get("sequence") or comp.get("components")
                        if seq:
                            self._process_skeleton(seq, context, rubrics, digest)
                        else:
                            # Skip printing structural component references
                            pass
                    else:
                        digest.append(f"[ERROR: Component {ref_key} not found]")

            # Support sequence/sub-structures nested directly in the slot itself
            if "sequence" in slot:
                self._process_skeleton(slot["sequence"], context, rubrics, digest)


    def _format_fixed_ref(self, ref, digest):
        if not ref:
            return
        if ref in self.engine.text_db:
            title = self.engine.text_db[ref].get("title", ref)
        else:
            title = ref.split('.')[-1].replace('_', ' ').capitalize()
        
        # Avoid technical strings for litanies
        if "litany" in ref.lower():
            if "great" in ref.lower():
                digest.append("Great Litany")
            elif "small" in ref.lower():
                digest.append("Small Litany")
            else:
                digest.append("Litany")
        else:
            digest.append(self.humanize_key(title))


    def _format_logic_hook(self, func_name, args, context, rubrics, digest):
        # Suppress ceremonial and choreographic rubrics in the Typikon Digest if not requested
        include_ceremonial = getattr(self, "include_ceremonial", False) or context.get("include_ceremonial", False)
        if not include_ceremonial and func_name in (
            "resolve_censing_annotation",
            "resolve_door_state",
            "resolve_curtain_state",
            "resolve_vestment_set",
            "resolve_bow_type",
            "resolve_hand_position",
            "resolve_role_view",
            "resolve_cantor_signal"
        ):
            return

        redirects = {
            "resolve_alleluia": "resolve_liturgy_alleluia",
            "resolve_megalynarion": "resolve_liturgy_megalynarion",
            "resolve_liturgy_readings_logic": "resolve_liturgy_readings",
            "resolve_megalynaria": "resolve_angelic_council"
        }
        actual_func_name = redirects.get(func_name, func_name)
        
        # Resolver registry validation for context safety
        active_structure = context.get("active_structure_id")
        if hasattr(self.engine, "resolver_registry"):
            if not self.engine.resolver_registry.is_allowed(active_structure, actual_func_name):
                digest.append(f"[ERROR: Logic resolver {actual_func_name} is not permitted in structure {active_structure}]")
                return
        
        if not hasattr(self.engine, actual_func_name):
            # Known internal checking hooks that do not yield instructions
            if actual_func_name in ("check_service_type", "check_gospel_service", "resolve_canon_ode_troparion"):
                return
            digest.append(f"[ERROR: Missing logic resolver method {actual_func_name}]")
            return
            
        try:
            enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
            enriched["overrides"] = rubrics.get("overrides", {})
            if rubrics.get("is_sunday_vigil"):
                enriched["is_sunday_vigil"] = True
                
            func = getattr(self.engine, actual_func_name)
            
            import inspect
            sig = inspect.signature(func)
            call_kwargs = {}
            if "rubrics" in sig.parameters:
                call_kwargs["rubrics"] = rubrics
                
            # Normalize common key mismatches between JSON structures and Python engine
            normalized_args = {}
            for k, v in args.items():
                if k == "pos":
                    normalized_args["position"] = v
                elif k == "num":
                    normalized_args["num"] = v
                else:
                    normalized_args[k] = v
                    
            # Dynamically pass parameters matching function signature
            for param_name in sig.parameters:
                if param_name in normalized_args:
                    call_kwargs[param_name] = normalized_args[param_name]
                
            params = list(sig.parameters.values())
            has_context = len(params) > 0
            
            if has_context:
                result = func(enriched, **call_kwargs)
            else:
                result = func()
                
            formatted_text = self._format_result(actual_func_name, result, enriched)
            if formatted_text:
                digest.append(formatted_text)
                
        except Exception as e:
            digest.append(f"[ERROR: {actual_func_name} failed - {str(e)}]")


    def _format_generator_hook(self, method, args, context, rubrics, digest):
        if method == "generate_stichera_sequence":
            try:
                enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
                enriched["overrides"] = rubrics.get("overrides", {})
                if rubrics.get("is_sunday_vigil"):
                    enriched["is_sunday_vigil"] = True
                res = self.engine.resolve_vespers_stichera(enriched)
                formatted = self._format_resolve_vespers_stichera(res, enriched)
                if formatted:
                    digest.append(formatted)
            except Exception as e:
                digest.append(f"[ERROR: generate_stichera_sequence failed - {str(e)}]")
        elif method == "generate_hour_troparia":
            try:
                enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
                enriched["overrides"] = rubrics.get("overrides", {})
                hour = args.get("hour", 1)
                enriched["hour"] = hour
                res = self.engine.resolve_hours_troparia(enriched, rubrics)
                formatted = self._format_resolve_hours_troparia(res, enriched)
                if formatted:
                    digest.append(formatted)
            except Exception as e:
                digest.append(f"[ERROR: generate_hour_troparia failed - {str(e)}]")
        elif method == "generate_antiphons":
            try:
                enriched = {**context, **rubrics.get("variables", {}), "variables": rubrics.get("variables", {})}
                strategy = args.get("strategy", "")
                pascha_off = context.get("pascha_offset")
                if strategy == "festal_antiphons" or (pascha_off is not None and 0 <= pascha_off <= 6):
                    digest.append("**Festal Antiphons of Pascha:**")
                    digest.append("  - **1st Antiphon (Psalm 65):** *\"Shout joyfully to the Lord, all the earth...\"* Refrain: *\"Through the prayers of the Mother of God, O Savior, save us.\"*")
                    digest.append("  - **2nd Antiphon (Psalm 66):** *\"May God be merciful to us and bless us...\"* Refrain: *\"Save us, O Son of God, risen from the dead, who sing to Thee: Alleluia.\"*")
                    digest.append("  - **3rd Antiphon (Psalm 67):** *\"Let God arise, and let His enemies be scattered...\"* Refrain: *\"Christ is risen from the dead, trampling down death by death, and upon those in the tombs bestowing life.\"*")
                    digest.append("**Entrance Hymn (Isodikon):** *\"In the churches bless God, the Lord from the fountains of Israel. Save us, O Son of God, risen from the dead, who sing to Thee: Alleluia.\"*")
                elif strategy == "weekday_antiphons":
                    digest.append("Daily Antiphons.")
                else:
                    digest.append("Psalms of Typica; Beatitudes.")
            except Exception as e:
                digest.append(f"[ERROR: generate_antiphons failed - {str(e)}]")
        else:
            digest.append(f"[ERROR: Unknown generator method {method}]")


    def _format_result(self, func_name, result, context):
        if not result:
            return ""
        formatter_name = f"_format_{func_name}"
        if hasattr(self, formatter_name):
            formatter = getattr(self, formatter_name)
            return formatter(result, context)
        if isinstance(result, dict) and result.get("type") in ("component_ref", "fixed_ref", "fixed_group", "sequence", "complex_structure"):
            temp_digest = []
            self._process_skeleton([result], context, {}, temp_digest)
            return "\n".join(temp_digest)
        return self._format_generic(func_name, result, context)

    # --- Logic Resolvers Formatters ---


    def _format_generic(self, func_name, result, context):
        if result is None:
            return ""
        if isinstance(result, str):
            return f"{self.humanize_key(func_name)}: {result}"
        if isinstance(result, list):
            items = []
            for item in result:
                if isinstance(item, dict):
                    citation = item.get("citation") or item.get("title") or item.get("id") or item.get("ref_key")
                    if citation:
                        items.append(self.humanize_key(citation))
                    else:
                        items.append(str(item))
                else:
                    items.append(self.humanize_key(str(item)))
            return f"{self.humanize_key(func_name)}: {'; '.join(items)}"
        if isinstance(result, dict):
            title = result.get("title") or result.get("text") or result.get("citation")
            if title:
                return f"{self.humanize_key(func_name)}: {title}"
            if "components" in result:
                comps = [self.humanize_key(c) for c in result["components"]]
                return f"{self.humanize_key(func_name)}: {'; '.join(comps)}"
            return f"{self.humanize_key(func_name)}: {result}"
        return f"{self.humanize_key(func_name)}: {str(result)}"

    # --- Specific Formatters ---


    def _clean_hymn_text(self, text):
        if not text:
            return ""
        cleaned = text.strip().strip('"').strip("'").rstrip('.')
        if cleaned and not cleaned[-1] in ('.', '!', '?'):
            cleaned += "."
        return f'"{cleaned}"'


    def _get_canon_refrain(self, source, context, canon_num=1):
        offset = context.get("pascha_offset")
        if offset == -70:
            if source == "octoechos":
                return "Glory to Your holy resurrection, O Lord!"
            elif source == "triodion":
                return "Have mercy on me, O God, have mercy on me!"
        elif offset == -63:
            if source == "octoechos":
                return "Glory to Your holy resurrection, O Lord!"
            elif source == "triodion":
                return "Have mercy on me, O God, have mercy on me!"
        elif offset == -56:
            if source == "octoechos":
                return "Glory to Your holy resurrection, O Lord!"
            elif source == "triodion":
                return "Have mercy on me, O God, have mercy on me!"
        elif offset == -49:
            if source == "triodion":
                return "Glory to You, O God, glory to You!"
        elif offset == -42:
            if source == "triodion":
                if canon_num == 1:
                    return "Glory to You, O God, glory to You!"
                else:
                    return "Holy hierarch Gregory pray to God for us!"
        elif offset == -35:
            if source == "triodion":
                return "Glory to Your precious Cross, O Lord!"
        elif offset == -28:
            if source == "octoechos":
                return "Glory to Your, holy Resurrection, O Lord!"
            elif source == "triodion":
                if canon_num == 1:
                    return "Have mercy on me, O God, have mercy on me!"
                else:
                    return "Venerable father John, pray to God for us!"
        elif offset == -8:
            if source == "triodion":
                return "Glory to You, O God, glory to You!"
        
        # Fallbacks
        if source == "octoechos":
            return "Glory to Your holy resurrection, O Lord!"
        elif source == "triodion":
            return "Glory to You, O God, glory to You!"
        elif source == "menaion":
            saints = context.get("saints", [])
            if saints:
                name = saints[0].get("name", "Saint")
                return f"Holy {name}, pray to God for us!"
            return "Holy Saint of God, pray to God for us!"
        return "Glory to You, O God, glory to You!"


    def _generate_abbreviated_canon_lines(self, context, katavasia_str):
        offset = context.get("pascha_offset")
        lines = []
        
        if offset in (-70, -63, -56, -49, -42, -35, -28):
            lines.append("At each ode, the heirmos of the resurrection from the Octoechos.")
        elif offset == -8:
            pass
        else:
            if context.get("day_of_week") == 0:
                lines.append("At each ode, the heirmos of the resurrection from the Octoechos.")
            else:
                lines.append("At each ode, the heirmos from the Octoechos.")

        if offset == -70:
            lines.append("1 troparion of the resurrection.  ℟. Glory to Your holy resurrection, O Lord!")
            lines.append("1 troparion from the Triodion.  ℟.  Have mercy on me, O God, have mercy on me!")
            lines.append("Glory... both now... forefeast (from the Menaion).")
        elif offset == -63:
            lines.append("1 troparion of the resurrection.  ℟. Glory to Your holy resurrection, O Lord!")
            lines.append("1 troparion from the Triodion.  ℟.  Have mercy on me, O God, have mercy on me!")
            lines.append("Glory... both now... feast (from the Menaion).")
        elif offset == -56:
            lines.append("1 troparion of the resurrection.  ℟. Glory to Your holy resurrection, O Lord!")
            lines.append("2 troparia from the Triodion.  ℟.  Have mercy on me, O God, have mercy on me!")
            lines.append("Glory... both now... Triodion.")
        elif offset == -49:
            lines.append("2 troparia from the Triodion.  ℟.  Glory to You, O God, glory to You!")
            lines.append("Glory... both now... Triodion.")
        elif offset == -42:
            lines.append("2 troparia from canon I in the Triodion.  ℟.  Glory to You, O God, glory to You!")
            lines.append("1 troparia from canon II in the Triodion.  ℟.  Holy hierarch Gregory pray to God for us!")
            lines.append("Glory... both now... Triodion.")
        elif offset == -35:
            lines.append("3 troparia from canon of the Triodion.  ℟.  Glory to Your precious Cross, O Lord!")
            lines.append("Glory... both now... Triodion.")
        elif offset == -28:
            lines.append("1 troparion: canon of the Resurrection.  ℟.  Glory to Your, holy Resurrection, O Lord!")
            lines.append("1 troparion: Triodion canon I.  ℟.  Have mercy on me, O God, have mercy on me!")
            lines.append("1 troparion: Triodion canon II.  ℟.  Venerable father John, pray to God for us!.")
            lines.append("Glory... both now... Triodion.")
        elif offset == -8:
            lines.append("At each ode: 2 troparia from the first canon.  ℟. Glory to You, O God, glory to You!")
            lines.append("2 troparia from the second canon.  ℟. Glory to You, O God, glory to You!")
            lines.append("Glory... both now... second canon.")
        else:
            if context.get("day_of_week") == 0:
                lines.append("1 troparion of the resurrection.  ℟. Glory to Your holy resurrection, O Lord!")
                saints = context.get("saints", [])
                if saints:
                    name = saints[0].get("name", "Saint")
                    lines.append(f"1 troparion of the Saint.  ℟. Holy {name}, pray to God for us!")
                lines.append("Glory... both now... Theotokion.")
            else:
                lines.append("At each ode: Heirmos, troparia with refrains, Glory... both now.")

        if katavasia_str:
            kat_line = katavasia_str
            if kat_line.startswith("Catabasia: "):
                kat_line = kat_line[len("Catabasia: "):]
            elif kat_line.startswith("Katavasia: "):
                kat_line = kat_line[len("Katavasia: "):]
            if "encounter" in katavasia_str.lower() or "meeting" in katavasia_str.lower():
                lines.append("Katavasia of the Encounter.")
            else:
                lines.append(katavasia_str.replace("Catabasia:", "Katavasia:"))

        return lines

