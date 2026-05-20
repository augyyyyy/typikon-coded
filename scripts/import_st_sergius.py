import re
import json
import os

class OctoechosParser:
    def __init__(self):
        # Top level structure: Tone -> Service -> Section -> Group
        self.data = {
            "tone_1": {} # Dictionary to hold services
        }
        self.current_service_name = None 
        self.current_section_name = None
        
        # State
        self.pending_verse = None
        self.buffer_text = []
        
        # Current list of items being built for the active section
        self.current_items = []
        
    def parse_file(self, filepath):
        print(f"Parsing {filepath}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            self._process_line(line)
            
        # Flush final items and section
        self._flush_item()
        self._flush_section()
        
        # Write Output
        output_path = os.path.join("json_db", "st_sergius", "octoechos_tone_1.json")
        with open(output_path, 'w', encoding='utf-8') as out:
            json.dump(self.data, out, indent=2, ensure_ascii=False)
        print(f"Saved to {output_path}")

    def _process_line(self, line):
        # 1. Detect Service Boundaries
        # Note: SUNDAY.txt contains Sat Eve Vespers, Sun Morn Matins (and Nocturns), Sun Eve Vespers
        if "AT LITTLE VESPERS" in line:
            self._flush_section()
            self.current_service_name = "saturday_vespers_little"
            return
        elif "AT GREAT VESPERS" in line:
            self._flush_section()
            self.current_service_name = "saturday_vespers_great"
            return
        elif "AT MATINS" in line:
            self._flush_section()
            self.current_service_name = "sunday_matins"
            return
        elif "NOCTURNS" in line:
            self._flush_section()
            self.current_service_name = "sunday_nocturns"
            return
        elif "SUNDAY VESPERS" in line:
            self._flush_section()
            self.current_service_name = "sunday_vespers"
            return

        # 2. Detect Section Headers
        new_section = None
        if 'On "Lord, I have cried ..."' in line:
            new_section = "lord_i_have_cried"
        elif "On the Aposticha" in line:
            new_section = "aposticha"
        elif "Sessional Hymns" in line:
            new_section = "sessionals"
        elif "Stichera at the Praises" in line:
            new_section = "praises"
        elif "Canon" in line and not "ODE" in line:
             # Try to catch the main Canon header. 
             # Sometimes it says "Canon of the Resurrection..."
             pass
            
        # 3. Detect Odes (Sub-sections)
        # We handle Odes by injecting them into the current 'canon' section or creating one
        if "ODE " in line and ("ODE I" in line or "ODE III" in line or "ODE IV" in line or "ODE V" in line or "ODE VI" in line or "ODE VII" in line or "ODE VIII" in line or "ODE IX" in line):
            self._flush_item()
            # If we are not already in a canon, switch to one
            if self.current_section_name != "canon":
                self._flush_section()
                self.current_section_name = "canon"
                # Initialize canon structure if needed, or we'll do it in flush_item logic?
                # Actually, simpler to just treat "ODE X" as a section change if we want flat structure,
                # BUT the requirement is nested.
                # Let's keep it simple: "canon" section, but items will be "ode_group" or we parse them as items with "ode" metadata.
                # BETTER: Create a 'ode_X' section key? No, that breaks the "Canon" container.
                # Let's make "ODE X" a section for now to get granularity, then we can post-process or adjust schema.
                # User wanted: canon -> odes -> 1.
                # Let's stick to flat sections for now: 'canon_ode_1', 'canon_ode_3'. 
                # Wait, no, let's try to interpret the user's wish for "canon" type.
            
            # We will use a special marker in the items list or just encode the Ode info.
            self.current_items.append({"type": "ode_header", "text": line})
            return

        if new_section:
            self._flush_section()
            self.current_section_name = new_section
            return

        # 4. Content Parsing
        if line.startswith("Verse:"):
            self._flush_item()
            self.pending_verse = line.replace("Verse:", "").strip()
            
        elif line.startswith("Glory"):
            self._flush_item()
            self.buffer_text.append(line)
            
        elif line.startswith("Both now"):
            self._flush_item()
            self.buffer_text.append(line)
            
        elif line.lower().startswith("tone"):
             pass
             
        elif line.startswith("Refrain:"):
            # Canon Refrain
            self._flush_item()
            self.current_items.append({"type": "refrain", "text": line.replace("Refrain:", "").strip()})
            
        elif line.startswith("Irmos:"):
            # Canon Irmos
            self._flush_item()
            self.buffer_text.append(line) # Special handling? Or just text.
            
        else:
            self.buffer_text.append(line)

    def _flush_item(self):
        """
        Takes buffered text and creates a Sticheron/Hymn object.
        """
        if not self.buffer_text:
            return

        text = " ".join(self.buffer_text).strip()
        if not text:
            return

        # Basic Classification
        item_type = "sticheron"
        if text.startswith("Glory"):
            item_type = "doxastichon"
        elif text.startswith("Both now") or "Theotokion" in text:
            item_type = "theotokion"
        elif text.startswith("Irmos:"):
            item_type = "irmos"
            text = text.replace("Irmos:", "").strip()

        # Construct Object
        obj = {
            "type": item_type,
            "text": text
        }
        if self.pending_verse:
            obj["verse"] = self.pending_verse
            self.pending_verse = None
            
        self.current_items.append(obj)
        self.buffer_text = []

    def _flush_section(self):
        """
        Saves items. If section is 'canon', we might want to restructure it later.
        For now, let's just dump it as 'canon' with items including 'ode_header'.
        """
        if not self.current_service_name or not self.current_section_name:
            if self.current_items:
                pass 
            return
            
        if not self.current_items:
            return

        # Ensure service dict exists
        if self.current_service_name not in self.data["tone_1"]:
            self.data["tone_1"][self.current_service_name] = {}

        # Save items. 
        # If it's a canon, we label it as 'canon' type, otherwise 'stichera_group'
        group_type = "stichera_group"
        if "canon" in self.current_section_name:
            group_type = "canon"
            
        self.data["tone_1"][self.current_service_name][self.current_section_name] = {
            "type": group_type,
            "items": self.current_items
        }
        
        self.current_items = []
        self.current_section_name = None 

if __name__ == "__main__":
    parser = OctoechosParser()
    path = r"Data\Service Books\Recensions\St Sergius\Oktoechos\Tone 1\SUNDAY.txt"
    if os.path.exists(path):
        parser.parse_file(path)
    else:
        print(f"Error: File not found at {path}")


