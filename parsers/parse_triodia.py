import re
import json
import os
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class TriodionParser:
    def __init__(self):
        self.data = {
            "lenten_triodion": {},
            "floral_triodion": {}
        }
        self.current_book = None
        self.current_period = None
        self.current_service = None
        self.current_section = None
        
        # Regex patterns
        self.period_header_pattern = re.compile(r"^(SUNDAY OF|SATURDAY OF|LAZARUS SATURDAY|PALM SUNDAY|GREAT|THE RESURRECTION|THOMAS SUNDAY|MID-PENTECOST|ASCENSION|PENTECOST|LEAVE-TAKING|FEAST OF|COMPASSION|SAINTS OF)")
        self.service_header_pattern = re.compile(r"^(VESPERS|MATINS|LITURGY|HOURS|COMPLINE|NOCTURN|SERVICE AT THE GRAVE)")
        self.section_header_pattern = re.compile(r"^(Stichera|Aposticha|Troparia|Sessional|Canon|Exapostilarion|Prokimenon|Readings|Gospel|Kontakion|Ikos|Synaxarion)", re.IGNORECASE)

    def parse_file(self, file_path: str, book_name: str):
        self.current_book = book_name
        self.current_period = None
        self.current_service = None
        self.current_section = None
        logging.info(f"Parsing {book_name} from {file_path}")
        
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Pre-process lines to handle specific file oddities if any
        clean_lines = [line.strip() for line in lines if line.strip()]
        
        # Determine distinct periods (Sundays/Feasts)
        # This is a simple state machine
        
        buffer = []
        
        for line in clean_lines:
            if self._is_period_header(line):
                # Save previous period if explicitly changing or if highly likely
                # But headers can be multi-line or just sub-headers. 
                # We need a robust heuristic.
                # For this specific dataset, headers are usually UPPERCASE.
                
                # Check against known high-level keys
                period_key = self._normalize_key(line)
                self.current_period = period_key
                if period_key not in self.data[self.current_book]:
                    self.data[self.current_book][period_key] = {}
                self.current_service = None # Reset service on new period
                logging.info(f"  Found Period: {line} -> {period_key}")
                continue

            if self.current_period:
                if self._is_service_header(line):
                    service_key = self._normalize_key(line)
                    self.current_service = service_key
                    if service_key not in self.data[self.current_book][self.current_period]:
                        self.data[self.current_book][self.current_period][service_key] = {}
                    self.current_section = None
                    logging.info(f"    Found Service: {line} -> {service_key}")
                    continue
                
                # If we are in a service, we look for sections (parts of the service)
                if self.current_service:
                    if self._is_section_header(line):
                        section_key = self._normalize_key(line)
                        self.current_section = section_key
                        if section_key not in self.data[self.current_book][self.current_period][self.current_service]:
                            self.data[self.current_book][self.current_period][self.current_service][section_key] = []
                        continue

                    # If we have a section, we add content
                    if self.current_section:
                         self.data[self.current_book][self.current_period][self.current_service][self.current_section].append(line)
                    else:
                        # Content without a section header? Maybe generic rubrics or "General"
                        if "miscellaneous" not in self.data[self.current_book][self.current_period][self.current_service]:
                             self.data[self.current_book][self.current_period][self.current_service]["miscellaneous"] = []
                        self.data[self.current_book][self.current_period][self.current_service]["miscellaneous"].append(line)

    def _is_period_header(self, line: str) -> bool:
        # Heuristic: Uppercase and matches known keywords or patterns for Major Feasts/Sundays
        if not line.isupper():
            return False
            
        # Specific overrides for known headers in these files
        known_headers = [
            "SUNDAY OF THE PUBLICAN AND PHARISEE", "SUNDAY OF THE PRODIGAL SON",
            "SATURDAY OF THE DEPARTED", "MEATFARE SUNDAY", "CHEESEFARE SUNDAY",
            "FIRST SUNDAY OF THE GREAT FAST", "FIRST SUNDAY OF THE GREAT LENT",
            "SECOND SUNDAY OF THE GREAT FAST", "SECOND SUNDAY OF THE GREAT LENT",
            "THIRD SUNDAY OF THE GREAT FAST", "THIRD SUNDAY OF THE GREAT LENT",
            "FOURTH SUNDAY OF THE GREAT FAST", "FOURTH SUNDAY OF THE GREAT LENT",
            "FIFTH SUNDAY OF THE GREAT FAST", "FIFTH SUNDAY OF THE GREAT LENT",
            "MATINS WITH PROSTRATIONS",
            "LAZARUS SATURDAY", "PALM SUNDAY",
            "GREAT MONDAY", "GREAT TUESDAY", "GREAT WEDNESDAY", "GREAT THURSDAY",
            "GREAT FRIDAY", "GREAT SATURDAY", "THE RESURRECTION OF OUR LORD JESUS CHRIST",
            "PASCHAL MATINS", "THOMAS SUNDAY", "SUNDAY OF THE MYRRH-BEARING WOMEN",
            "SUNDAY OF THE PARALYTIC", "MID-PENTECOST", "SUNDAY OF THE SAMARITAN WOMAN",
            "SUNDAY OF THE MAN BORN BLIND", "ASCENSION OF OUR LORD JESUS CHRIST",
            "SUNDAY OF THE HOLY FATHERS", "PENTECOST SUNDAY", "SUNDAY OF ALL SAINTS",
            "FEAST OF THE MOST HOLY EUCHARIST", "FEAST OF THE MOST SACRED HEART",
            "FEAST OF THE COMPASSION", "SUNDAY OF THE SAINTS OF RUS-UKRAINE"
        ]
        
        # Check explicit list first
        if any(h in line for h in known_headers):
            return True
            
        return False

    def _is_service_header(self, line: str) -> bool:
        if "VESPERS" in line or "MATINS" in line or "LITURGY" in line or "HOURS" in line:
            return True
        return False

    def _is_section_header(self, line: str) -> bool:
        # Check for typical section starts
        markers = ["Stichera", "Aposticha", "Troparia", "Sessional", "Canon", "Exapostilarion", "Prokimenon", "Reading", "Gospel", "Kontakion", "Ode"]
        for m in markers:
            if line.startswith(m):
                return True
        return False

    def _normalize_key(self, text: str) -> str:
        # Remove special characters first
        clean = re.sub(r'["“”‘’.,:;!?-]', '', text)
        return clean.strip().lower().replace(" ", "_").replace("__", "_")

    def save_json(self, output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Save Lenten Triodion
        with open(os.path.join(output_dir, 'lenten_triodion.json'), 'w', encoding='utf-8') as f:
            json.dump(self.data["lenten_triodion"], f, indent=2, ensure_ascii=False)
            
        # Save Floral Triodion
        with open(os.path.join(output_dir, 'floral_triodion.json'), 'w', encoding='utf-8') as f:
            json.dump(self.data["floral_triodion"], f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    base_path = r"c:\Users\augus\PycharmProjects\MyFirstGui\Data\Service Books\Recensions\Stamford Divine Office\TXT"
    output_path = r"c:\Users\augus\PycharmProjects\MyFirstGui\Data\Service Books\Recensions\Stamford Divine Office\JSON"
    
    parser = TriodionParser()
    
    # Parse Lenten Triodion (Incomplete)
    parser.parse_file(os.path.join(base_path, "LENTEN_TRIODION.txt"), "lenten_triodion")
    
    # Parse Appendix (Contains Lent 2) - Merging into lenten_triodion
    # Note: We need to manually handle this merge or just treat it as a source for lenten_triodion
    # The parse_file method overwrites 'current_book', so we can just call it with the same book name
    parser.parse_file(os.path.join(base_path, "APPENDIX.txt"), "lenten_triodion")
    
    # Parse Floral Triodion (Complete)
    parser.parse_file(os.path.join(base_path, "FLORAL_TRIODION.txt"), "floral_triodion")
    
    parser.save_json(output_path)
