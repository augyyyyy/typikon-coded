import re
import json
import os

class UnabridgedOctoechosParser:
    def __init__(self, tone_num):
        self.tone_num = tone_num
        self.output_db = {}
        
        # State
        self.current_service = "unknown"
        self.current_section = "unknown"
        self.pending_verse = None
        self.hymn_buffer = []
        self.sticheron_index = 1
        
        # Mapping service names from file headers to semantic keys
        self.service_map = {
            "AT LITTLE VESPERS": "sat_vespers_little",
            "AT GREAT VESPERS": "sat_vespers_great",
            "AT MATINS": "sun_matins",
            "NOCTURNS": "sun_nocturns",
            "COMPLINE": "sat_compline",
            "SUNDAY VESPERS": "sun_vespers"
        }

    def parse_file(self, src_path):
        print(f"--- Parsing Unabridged: {src_path} ---")
        if not os.path.exists(src_path):
            print(f"Error: {src_path} not found")
            return

        with open(src_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 1. Detect Service Boundaries
            service_match = False
            for header, key in self.service_map.items():
                if header in line.upper():
                    self.flush_hymn()
                    self.current_service = key
                    self.current_section = "unknown"
                    self.sticheron_index = 1
                    service_match = True
                    break
            if service_match: continue

            # 2. Detect Section Headers
            if re.search(r'Lord,? I (have )?cried', line, re.I):
                self.flush_hymn()
                self.current_section = "stichera_lord_i_call"
                self.sticheron_index = 1
                continue
            elif re.search(r'On the Aposticha', line, re.I):
                self.flush_hymn()
                self.current_section = "stichera_aposticha"
                self.sticheron_index = 1
                continue
            elif re.search(r'at the Praises', line, re.I) or re.search(r'On the Praises', line, re.I):
                self.flush_hymn()
                self.current_section = "stichera_praises"
                self.sticheron_index = 1
                continue
            elif re.search(r'Sessional Hymns', line, re.I):
                self.flush_hymn()
                self.current_section = "sessionals"
                self.sticheron_index = 1
                continue
            elif re.search(r'EVLOGITARIA', line, re.I) or re.search(r'Resurrectional Verses', line, re.I):
                self.flush_hymn()
                self.current_section = "evlogitaria"
                self.sticheron_index = 1
                continue
            elif re.search(r'Antiphon', line, re.I) or re.search(r'Songs of Ascent', line, re.I):
                self.flush_hymn()
                self.current_section = "antiphons"
                self.sticheron_index = 1
                continue
            elif re.search(r'Prokeimenon', line, re.I):
                self.flush_hymn()
                self.current_section = "prokeimenon"
                self.sticheron_index = 1
                continue
            elif re.search(r'Magnificat', line, re.I) or re.search(r'Hymn of the Most Holy Theotokos', line, re.I):
                self.flush_hymn()
                self.current_section = "magnificat"
                self.sticheron_index = 1
                continue
            elif re.search(r'ODE ([IVXLCDM]+)', line, re.I):
                match = re.search(r'ODE ([IVXLCDM]+)', line, re.I)
                self.flush_hymn()
                ode_num = match.group(1).lower()
                self.current_section = f"canon_ode_{ode_num}"
                self.sticheron_index = 1
                continue

            # 2.1 Sub-sections / Hymn Types (within a section)
            if "Anatolius" in line:
                self.flush_hymn()
                self.sticheron_index = "anatolius"
                continue
            elif "Dogmatic Theotokion" in line:
                self.flush_hymn()
                self.sticheron_index = "dogmatic"
                continue
            elif "Resurrection Theotokion" in line:
                self.flush_hymn()
                self.sticheron_index = "theotokion"
                continue
            elif "Svetilen" in line or "Exapostilarion" in line:
                self.flush_hymn()
                self.current_section = "exapostilarion"
                self.sticheron_index = 1
                continue

            # 3. Detect Verse
            if line.startswith("Verse:") or line.startswith("Refrain:") or line.startswith("Irmos:"):
                self.flush_hymn()
                self.pending_verse = line.strip()
                continue
            
            if "Blessed art Thou, O Lord" in line:
                self.flush_hymn()
                self.pending_verse = line.strip()
                continue
            
            if "Now will I arise, saith the Lord" in line: # Prokeimenon
                 self.flush_hymn()
                 self.pending_verse = line.strip()
                 continue

            # 4. Detect Doxology
            if line.startswith("Glory ..., Both now ...,") or line.startswith("Glory ...,") or line.startswith("Both now ...,") \
               or line.startswith("Glory to the Father") or line.startswith("Both now and ever"):
                self.flush_hymn()
                # Special index for glory/both now
                if "Both now" in line and "Glory" in line:
                    self.sticheron_index = "glory_both_now"
                elif "Both now" in line:
                    self.sticheron_index = "both_now"
                else:
                    self.sticheron_index = "glory"
                self.hymn_buffer.append(line)
                continue

            # 5. Identify Rubrics (Ends in colon or is a note)
            if line.endswith(":") or line.startswith("Note:") or (line.startswith("(") and line.endswith(")")):
                # If we have a hymn in progress, let's keep it (could be a mid-hymn instruction)
                if not self.hymn_buffer:
                    continue
            
            # 6. Accumulate Content
            self.hymn_buffer.append(line)

        self.flush_hymn() # Final flush

    def flush_hymn(self):
        if not self.hymn_buffer:
            return
        
        full_text = " ".join(self.hymn_buffer).strip()
        
        # Determine the key
        # tone_{n}.{service}.{section}_{index}
        key_base = f"tone_{self.tone_num}.{self.current_service}.{self.current_section}"
        
        # Strip Doxology indicators if it's a Doxastichon/Theotokion
        text_content = full_text
        for prefix in ["Glory ..., Both now ...,", "Glory ...,", "Both now ...,"]:
            if text_content.startswith(prefix):
                text_content = text_content.replace(prefix, "").strip()
                break

        final_key = f"{key_base}_{self.sticheron_index}"
        
        # Deduplicate keys if needed (e.g. multiple Anatolius)
        if final_key in self.output_db:
             # Add a sub-index
             i = 2
             while f"{final_key}_{i}" in self.output_db:
                 i += 1
             final_key = f"{final_key}_{i}"

        self.output_db[final_key] = {
            "content": text_content,
            "source": f"St. Sergius Unabridged (Tone {self.tone_num})"
        }
        if self.pending_verse:
            self.output_db[final_key]["verse"] = self.pending_verse
            
        # Increment index if it was numeric
        if isinstance(self.sticheron_index, int):
            self.sticheron_index += 1
        
        # Reset buffers
        self.hymn_buffer = []
        self.pending_verse = None

    def save(self, out_path):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(self.output_db, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(self.output_db)} items to {out_path}")

if __name__ == "__main__":
    parser = UnabridgedOctoechosParser(1)
    src = "Data/Service Books/Recensions/St Sergius/Oktoechos/Tone 1/SUNDAY.txt"
    dest = "json_db/st_sergius/octoechos_tone_1_refined.json"
    
    parser.parse_file(src)
    parser.save(dest)
