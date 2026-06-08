import os
import glob
import json

class ProceduralStSergiusParser:
    def __init__(self, base_key, source_name):
        self.base_key = base_key
        self.source_name = source_name
        self.output_db = {}
        
        # State
        self.current_service = "general"
        self.current_section = "preface"
        self.sticheron_index = 1
        self.pending_verse = None
        self.pending_rubric = None
        self.hymn_buffer = []

        # Service headers mapping
        self.service_headers = {
            "at little vespers": "sat_vespers_little",
            "at great vespers": "sat_vespers_great",
            "at vespers": "vespers",
            "at daily vespers": "daily_vespers",
            "at matins": "sun_matins",
            "nocturns": "sun_nocturns",
            "compline": "sat_compline",
            "sunday vespers": "sun_vespers",
            "at liturgy": "liturgy",
            "at the liturgy": "liturgy",
            "at midnight office": "midnight_office",
            "midnight office": "midnight_office",
            "at the hours": "hours"
        }

        # Section headers mapping
        self.section_headers = {
            "lord, i have cried": "stichera_lord_i_call",
            "lord i have cried": "stichera_lord_i_call",
            "lord, i cry": "stichera_lord_i_call",
            "lord i call": "stichera_lord_i_call",
            "on the aposticha": "stichera_aposticha",
            "aposticha": "stichera_aposticha",
            "on the praises": "stichera_praises",
            "at the praises": "stichera_praises",
            "the praises": "stichera_praises",
            "praises stichera": "stichera_praises",
            "troparion": "troparion",
            "dismissal troparion": "troparion",
            "sessional hymn": "sessional_hymn",
            "sedalion": "sessional_hymn",
            "sessional": "sessional_hymn",
            "polyeleos": "polyeleos",
            "magnification": "polyeleos",
            "prokeimenon": "prokeimenon",
            "song of ascents": "prokeimenon",
            "antiphon": "prokeimenon",
            "the gospel": "gospel",
            "exapostilarion": "exapostilarion",
            "svetilen": "exapostilarion",
            "kontakion": "kontakion",
            "ikos": "ikos",
            "synaxarion": "synaxarion",
            "at litiya": "litiya",
            "litiya": "litiya",
            "a reading from": "reading",
            "on the beatitudes": "beatitudes",
            "beatitudes": "beatitudes"
        }

    def parse_file(self, src_path):
        if not os.path.exists(src_path):
            return

        with open(src_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue

            # Ignore page markers
            if line_clean.startswith("--- PAGE"):
                continue

            line_lower = line_clean.lower()

            # 1. Detect Service Boundaries
            found_service = None
            for header, s_key in self.service_headers.items():
                if header == line_lower or line_lower.startswith(header + " ") or line_lower.startswith(header + ":"):
                    found_service = s_key
                    break
            if found_service:
                self.flush_hymn()
                self.current_service = found_service
                self.current_section = "general"
                self.sticheron_index = 1
                continue

            # 2. Detect Section Boundaries
            found_section = None
            for header, sec_key in self.section_headers.items():
                if header in line_lower:
                    found_section = sec_key
                    break

            # 2.1 Procedural Check for ODE
            is_ode = False
            ode_num = ""
            if "ode " in line_lower:
                idx = line_lower.find("ode ")
                rest = line_lower[idx + 4:].strip()
                tokens = rest.split()
                if tokens:
                    token = tokens[0].strip(":,.-)")
                    # Check if token is Roman numeral or digit
                    is_roman = all(c in "ivxlcdm" for c in token)
                    is_digit = token.isdigit()
                    if is_roman or is_digit:
                        is_ode = True
                        ode_num = token

            if is_ode:
                self.flush_hymn()
                self.current_section = f"canon_ode_{ode_num}"
                self.sticheron_index = 1
                continue
            elif found_section:
                self.flush_hymn()
                self.current_section = found_section
                self.sticheron_index = 1
                continue

            # 3. Detect Sub-types (Anatolius, Dogmatic, Theotokion)
            found_subtype = None
            if "dogmatic theotokion" in line_lower or "dogmaticon" in line_lower:
                found_subtype = "dogmatic"
            elif "resurrection theotokion" in line_lower or "dismissal theotokion" in line_lower:
                found_subtype = "theotokion"
            elif "anatolius" in line_lower:
                found_subtype = "anatolius"
            elif "dismissal troparion" in line_lower:
                found_subtype = "troparion"

            if found_subtype:
                self.flush_hymn()
                self.sticheron_index = found_subtype
                # If the line is short or ends with a colon, it's just a header line.
                # If not, accumulate it.
                if len(line_clean) < 60 or line_clean.endswith(":"):
                    continue

            # 4. Detect Verses
            is_verse = False
            if line_lower.startswith("verse:") or line_lower.startswith("refrain:") or line_lower.startswith("irmos:"):
                is_verse = True
            elif "blessed art thou, o lord" in line_lower:
                is_verse = True
            elif "now will i arise" in line_lower:
                is_verse = True

            if is_verse:
                self.flush_hymn()
                self.pending_verse = line_clean
                continue

            # 5. Detect Doxology
            is_doxology = False
            dox_type = None
            if line_lower.startswith("glory...") or line_lower.startswith("glory ...,") or line_lower.startswith("glory to the father"):
                is_doxology = True
                dox_type = "glory"
                if "both now" in line_lower:
                    dox_type = "glory_both_now"
            elif line_lower.startswith("both now...") or line_lower.startswith("both now ...,") or line_lower.startswith("both now and ever"):
                is_doxology = True
                dox_type = "both_now"

            if is_doxology:
                self.flush_hymn()
                self.sticheron_index = dox_type
                prefix_len = 0
                for prefix in ["glory ..., both now ...,", "glory..., both now...,", "glory ..., both now ...", "glory to the father ...,", "glory to the father...,", "glory to the father...", "glory ...,", "glory...,", "both now ...,", "both now...,", "both now and ever...,", "both now and ever..."]:
                    if line_lower.startswith(prefix):
                        prefix_len = len(prefix)
                        break
                rest = line_clean[prefix_len:].strip()
                if rest:
                    self.hymn_buffer.append(rest)
                continue

            # 6. Detect Rubrics / Instructions
            is_rubric = False
            if line_lower.startswith("note:") or (line_lower.startswith("(") and line_lower.endswith(")")):
                is_rubric = True
            elif line_lower.endswith(":") and len(line_clean) < 100:
                is_rubric = True

            if is_rubric:
                if self.pending_rubric:
                    self.pending_rubric += " " + line_clean
                else:
                    self.pending_rubric = line_clean
                continue

            # 7. Accumulate hymn text
            self.hymn_buffer.append(line_clean)

        self.flush_hymn()

    def flush_hymn(self):
        if not self.hymn_buffer:
            return

        raw_content = " ".join(self.hymn_buffer).strip()
        self.hymn_buffer = []

        # Strip doxology prefixes from the start of the content if they exist
        content = raw_content
        content_lower = content.lower()
        dox_prefixes = [
            "glory ..., both now ...,", "glory..., both now...,", "glory ..., both now ...",
            "glory to the father ...,", "glory to the father...,", "glory to the father...",
            "glory ...,", "glory...,", "both now ...,", "both now...,", "both now and ever...,",
            "both now and ever..."
        ]
        for prefix in dox_prefixes:
            if content_lower.startswith(prefix):
                content = content[len(prefix):].strip()
                break

        if not content:
            return

        full_base_key = f"{self.base_key}.{self.current_service}.{self.current_section}"
        suffix = self.sticheron_index
        final_key = f"{full_base_key}_{suffix}"

        # De-duplicate keys
        idx = 1
        actual_key = final_key
        while actual_key in self.output_db:
            idx += 1
            actual_key = f"{final_key}_{idx}"

        item = {
            "content": content,
            "source": self.source_name
        }

        if self.pending_verse:
            item["verse"] = self.pending_verse
            self.pending_verse = None

        if self.pending_rubric:
            item["rubric"] = self.pending_rubric
            self.pending_rubric = None

        # Parse Tone and Special Melody procedurally
        tone = self.parse_tone_from_text(content)
        if tone:
            item["tone"] = tone

        melody = self.parse_melody_from_text(content)
        if melody:
            item["special_melody"] = melody

        self.output_db[actual_key] = item

        # Increment sticheron index if numeric
        if isinstance(self.sticheron_index, int):
            self.sticheron_index += 1

    def parse_tone_from_text(self, text):
        text_lower = text.lower()
        if "in tone " in text_lower:
            idx = text_lower.find("in tone ")
            part = text[idx + 8:idx + 20].strip()
            tokens = part.split()
            if tokens:
                return tokens[0].strip(".,:;)")
        elif "tone " in text_lower:
            idx = text_lower.find("tone ")
            part = text[idx + 5:idx + 15].strip()
            tokens = part.split()
            if tokens:
                return tokens[0].strip(".,:;)")
        return None

    def parse_melody_from_text(self, text):
        text_lower = text.lower()
        for marker in ["special melody:", "podoben:", "melody:"]:
            if marker in text_lower:
                idx = text_lower.find(marker)
                part = text[idx + len(marker):idx + 100].strip()
                end_chars = [".", ",", ";", "\n", "*"]
                end_idx = len(part)
                for char in end_chars:
                    pos = part.find(char)
                    if pos != -1 and pos < end_idx:
                        end_idx = pos
                return part[:end_idx].strip()
        return None


def map_group_and_slug(filepath):
    norm_path = filepath.replace("\\", "/")
    
    # Stamford Terminology Mapping for General Menaion
    general_menaion_mapping = {
        "angels": "angels",
        "apostle": "apostle",
        "apostles": "apostles",
        "cross": "cross",
        "fools": "fools_for_christ",
        "heirarch": "hierarch",
        "heirarchs": "hierarchs",
        "heiromartyrs": "hieromartyrs",
        "hieroconfessor": "hieroconfessor",
        "hieromartyr": "hieromartyr",
        "holy_fathers": "holy_fathers",
        "martyr": "martyr",
        "martyress": "woman_martyr",
        "martyresses": "women_martyrs",
        "martyrs": "martyrs",
        "monastic": "venerable",
        "monasticmartyr": "venerable_martyr",
        "monasticmartyrs": "venerable_martyrs",
        "monastics": "venerables",
        "nun": "venerable_woman",
        "nunmartyr": "venerable_woman_martyr",
        "nuns": "venerable_women",
        "prophet": "prophet",
        "st_john_baptist": "forerunner",
        "theotokos": "theotokos",
        "unmercenaries": "unmercenaries"
    }

    if "Full Menaion" in norm_path:
        basename = os.path.basename(filepath).replace(".txt", "")
        slug = basename.replace("-", "_").lower()
        return f"menaion.{slug}"
    elif "General Menaion" in norm_path:
        basename = os.path.basename(filepath).replace(".txt", "")
        slug = basename.replace(" ", "_").lower()
        mapped_slug = general_menaion_mapping.get(slug, slug)
        return f"general.{mapped_slug}"
    elif "Full Octoechos" in norm_path:
        basename = os.path.basename(filepath).replace(".txt", "").lower()
        if basename.startswith("tone"):
            tone_num = basename.replace("tone", "").strip()
            return f"tone_{tone_num}"
        elif basename == "theotokia":
            return "octoechos.theotokia"
        else:
            # e.g., 1-1.txt (Tone 1, Day 1)
            return f"octoechos.{basename.replace('-', '_')}"
    elif "Lenton Triodion" in norm_path or "Lenten Triodion" in norm_path:
        basename = os.path.basename(filepath).replace(".txt", "").lower()
        return f"triodion.{basename.replace('-', '_')}"
    elif "Pentecostarion" in norm_path:
        basename = os.path.basename(filepath).replace(".txt", "").lower()
        return f"pentecostarion.{basename.replace('-', '_')}"
    elif "Katavasia" in norm_path:
        return "katavasia.general"
    elif "Common Theotokia" in norm_path:
        return "octoechos.common_theotokia"
        
    return "unknown.unknown"


def main():
    print("Starting Lossless Procedural St. Sergius Parser (No-Regex)...")
    
    # Paths dynamically resolved relative to this parser script
    parser_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(parser_dir)
    text_dir = os.path.join(project_root, "Data", "Service Books", "Recensions", "St Sergius", "Raw Text")
    output_json = os.path.join(project_root, "json_db", "st_sergius", "text_st_sergius.json")
    
    if not os.path.exists(text_dir):
        print(f"Error: {text_dir} not found.")
        return
        
    master_db = {}
    txt_files = glob.glob(os.path.join(text_dir, "**", "*.txt"), recursive=True)
    print(f"Found {len(txt_files)} text files to parse.")
    
    parsed_files_count = 0
    for filepath in txt_files:
        base_key = map_group_and_slug(filepath)
        source_name = "St. Sergius Unabridged"
        if "tone_" in base_key:
            tone_part = base_key.split(".")[0]
            source_name = f"St. Sergius Unabridged ({tone_part.replace('_', ' ').title()})"
            
        parser = ProceduralStSergiusParser(base_key, source_name)
        parser.parse_file(filepath)
        
        # Merge dictionaries
        for k, v in parser.output_db.items():
            if k in master_db:
                # Merge content if key collisions occur
                master_db[k]["content"] += "\n\n[APPENDED]\n" + v["content"]
            else:
                master_db[k] = v
        parsed_files_count += 1

    print(f"Parsed {parsed_files_count} files.")
    print(f"Generated {len(master_db)} Master Schema keys losslessly.")
    
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(master_db, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully wrote {output_json}")


if __name__ == "__main__":
    main()
