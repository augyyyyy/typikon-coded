import os
import sys
import json
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add scripts directory to path for imports
sys.path.append(str(Path(__file__).parent))
from deepseek_analyzer import get_deepseek_key

INPUT_FILE = Path("json_db/calendar_dolnytsky.json")
OUTPUT_FILE = Path("json_db/calendar_dolnytsky_split.json")

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

SYSTEM_PROMPT = """You are a scholar of the Byzantino-Slavonic Typikon.
Your task is to analyze an Eastern Christian liturgical commemoration description and parse/split it into individual, atomically separated saints, martyrs, or feasts.

Convert the description into a JSON array of objects representing each individual saint or event.
Each object must contain the following fields:
1. "name": string (the name of the saint, stripped of title prefixes like St., Ven., Holy, Prophet, Apostle, Martyr).
2. "title": string (the standard title, e.g., 'Prophet', 'Hierarch', 'Martyr', 'Venerable', 'Righteous Ancestor of God', 'Apostle', 'Hieromartyr', 'Venerable Martyr', 'Great Martyr').
3. "gender": string ('male', 'female', 'group', or 'unknown').
4. "monastic": boolean (true if the saint is a venerable/monastic/ascetic, false otherwise).
5. "is_saint": boolean (true if the entry describes a saint/person/group of people, false if it's a non-person event like 'Beginning of the New Year', 'Nativity of the Theotokos', 'Exposition of the Holy Wood', or 'Friday of the Passion').

Examples:
- "Prophet Zachariah, father of St. John the Forerunner" ->
  [
    {"name": "Zachariah", "title": "Prophet", "gender": "male", "monastic": false, "is_saint": true}
  ]
- "Sts. Amphilochius and Gregory." ->
  [
    {"name": "Amphilochius", "title": "Hierarch", "gender": "male", "monastic": false, "is_saint": true},
    {"name": "Gregory", "title": "Hierarch", "gender": "male", "monastic": false, "is_saint": true}
  ]
- "Righteous Ancestors of God Joachim and Anna." ->
  [
    {"name": "Joachim", "title": "Righteous Ancestor of God", "gender": "male", "monastic": false, "is_saint": true},
    {"name": "Anna", "title": "Righteous Ancestor of God", "gender": "female", "monastic": false, "is_saint": true}
  ]
- "Beginning of the New Year" ->
  [
    {"name": "Beginning of the New Year", "title": "", "gender": "unknown", "monastic": false, "is_saint": false}
  ]
- "Ven. Mother Theodora of Alexandria; Ven. Euphrosynus." ->
  [
    {"name": "Theodora of Alexandria", "title": "Venerable Mother", "gender": "female", "monastic": true, "is_saint": true},
    {"name": "Euphrosynus", "title": "Venerable", "gender": "male", "monastic": true, "is_saint": true}
  ]
- "Martyrs Menodora, Metrodora and Nymphodora." ->
  [
    {"name": "Menodora", "title": "Martyr", "gender": "female", "monastic": false, "is_saint": true},
    {"name": "Metrodora", "title": "Martyr", "gender": "female", "monastic": false, "is_saint": true},
    {"name": "Nymphodora", "title": "Martyr", "gender": "female", "monastic": false, "is_saint": true}
  ]

Respond ONLY with a valid JSON array. Do not include markdown wraps or explanations."""

def parse_description_with_llm(api_key: str, desc: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-v4-pro",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Parse the following liturgical description:\n{desc}"}
        ],
        "temperature": 0.1
    }
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        resp_json = response.json()
        content = resp_json["choices"][0]["message"]["content"].strip()
        # Clean potential markdown block wrappers if model outputs them anyway
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error parsing description '{desc}': {e}", file=sys.stderr)
        return None

def main():
    api_key = get_deepseek_key()
    if not api_key:
        print("Error: DeepSeek API key not found. Please set DEEPSEEK_API_KEY.", file=sys.stderr)
        sys.exit(1)

    if not INPUT_FILE.exists():
        print(f"Error: Input file {INPUT_FILE} does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        calendar = json.load(f)

    # Load existing progress if any
    split_calendar = {}
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                split_calendar = json.load(f)
            print(f"Loaded existing output calendar with {len(split_calendar)} days.")
        except Exception as e:
            print(f"Warning: Failed to load existing output calendar: {e}")

    # Identify which keys actually need parsing
    keys_to_parse = []
    for key, day_data in calendar.items():
        needs_parse = True
        if key in split_calendar:
            day_entries = day_data.get("entries", [])
            split_entries = split_calendar[key].get("entries", [])
            if len(day_entries) == len(split_entries) and all("parsed_saints" in e for e in split_entries):
                needs_parse = False
        if needs_parse:
            keys_to_parse.append(key)

    total_keys = len(keys_to_parse)
    if total_keys == 0:
        print("All days are already parsed.")
        return

    print(f"Processing {total_keys} calendar days in parallel...")

    # Helper function for worker threads to process a single day's entries
    def process_day(key, day_data):
        updated_entries = []
        for entry in day_data.get("entries", []):
            desc = entry.get("description", "")
            parsed_saints = parse_description_with_llm(api_key, desc)
            if parsed_saints is None:
                parsed_saints = [{
                    "name": desc,
                    "title": "",
                    "gender": "unknown",
                    "monastic": False,
                    "is_saint": True
                }]
            entry_copy = entry.copy()
            entry_copy["parsed_saints"] = parsed_saints
            updated_entries.append(entry_copy)
        return key, {
            "month": day_data["month"],
            "day": day_data["day"],
            "entries": updated_entries,
            "raw_source": day_data.get("raw_source", "")
        }

    processed_count = 0
    # Use 15 concurrent threads for fast parsing without hitting rate limits
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(process_day, key, calendar[key]): key for key in keys_to_parse}
        for future in as_completed(futures):
            key = futures[future]
            try:
                k, result_data = future.result()
                split_calendar[k] = result_data
                processed_count += 1
                print(f"[{processed_count}/{total_keys}] Completed parsing day {k}")
            except Exception as exc:
                print(f"Day {key} generated an exception: {exc}", file=sys.stderr)
            
            if processed_count % 10 == 0:
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(split_calendar, f, indent=2, ensure_ascii=False)
                print(f"Saved incremental progress to {OUTPUT_FILE}")

    # Final save
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(split_calendar, f, indent=2, ensure_ascii=False)
    print(f"Successfully finished calendar parsing. Saved total {len(split_calendar)} days to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
