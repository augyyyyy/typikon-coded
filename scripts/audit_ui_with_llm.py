import os
import sys
import json
import requests
from datetime import date, datetime
from pathlib import Path
from dotenv import load_dotenv

# Re-use the robust DeepSeek key loader to find the API key
def get_deepseek_key():
    key = os.getenv("DEEPSEEK_API_KEY")
    if key and key != "your_deepseek_api_key_here":
        return key

    global_env = r"C:\Users\augus\OneDrive\Documents\Google Antigravity\Projects\.env"
    if os.path.exists(global_env):
        try:
            with open(global_env, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k_clean = k.strip().replace("[", "").replace("]", "")
                        if k_clean in ("deepseek-v4-pro", "DEEPSEEK_API_KEY"):
                            val = v.strip()
                            if val:
                                return val
        except Exception as e:
            print(f"Warning: Error reading global .env: {e}", file=sys.stderr)

    if os.path.exists(".env"):
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k_clean = k.strip().replace("[", "").replace("]", "")
                        if k_clean in ("deepseek-v4-pro", "DEEPSEEK_API_KEY"):
                            val = v.strip()
                            if val and val != "your_deepseek_api_key_here":
                                return val
        except Exception as e:
            print(f"Warning: Error reading local .env: {e}", file=sys.stderr)

    return None

def main():
    # Load dotenv if exists
    ENV_PATH = Path("C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/.env")
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH)
    else:
        load_dotenv()

    api_key = get_deepseek_key()
    if not api_key:
        print("[ERROR] DeepSeek API Key not found. Please set DEEPSEEK_API_KEY.", file=sys.stderr)
        sys.exit(1)

    REPO_DIR = Path(__file__).parent.parent
    sys.path.insert(0, str(REPO_DIR))

    try:
        from ruthenian_engine import RuthenianEngine
    except ImportError:
        sys.path.insert(0, str(REPO_DIR / "engine"))
        from ruthenian_engine import RuthenianEngine

    engine = RuthenianEngine(base_dir=str(REPO_DIR))

    # 15 Curated Dates for Sampling (Random, Festal, Collision)
    dates_to_sample = [
        # 1. General/Ordinary days
        (date(2026, 1, 15), "Ordinary Weekday (Thursday simple saint)"),
        (date(2026, 2, 10), "Ordinary Weekday (Tuesday ordinary weekday)"),
        (date(2026, 7, 12), "Ordinary Sunday"),
        (date(2026, 10, 14), "Ordinary Weekday (Wednesday)"),
        (date(2026, 11, 10), "Ordinary Weekday (Tuesday)"),
        
        # 2. Major Feasts / Movable Feasts
        (date(2026, 1, 6), "Theophany (Great Feast of the Lord)"),
        (date(2026, 4, 5), "Pascha (Movable Great Feast)"),
        (date(2026, 5, 14), "Ascension (Movable Great Feast)"),
        (date(2026, 5, 24), "Pentecost (Movable Great Feast)"),
        (date(2026, 12, 25), "Christmas / Nativity of Christ (Great Feast)"),
        
        # 3. Collision / Special cases
        (date(2026, 1, 4), "Sunday with Simple Saint [4 A+G]"),
        (date(2026, 1, 20), "Weekday with Polyeleos Saint (Euthymius the Great)"),
        (date(2026, 5, 21), "Thursday after Ascension with Polyeleos Saint (Constantine and Helena)"),
        (date(2026, 6, 11), "Apodosis of Eucharist colliding with Apostles Bartholomew & Barnabas (Polyeleos)"),
        (date(2026, 8, 15), "Saturday Dormition / Feast of Theotokos"),
    ]

    print(f"Sampling {len(dates_to_sample)} dates from Ruthenian Engine...")
    payload_days = []

    for dt, category in dates_to_sample:
        try:
            ctx = engine.get_liturgical_context(dt)
            rub = engine.resolve_rubrics(ctx)
            digest = engine.generate_typikon_digest(ctx, rub)
            
            day_info = {
                "date": dt.isoformat(),
                "description": category,
                "feast_id": ctx.get("feast_id"),
                "feast_level": ctx.get("feast_level"),
                "season_id": ctx.get("season_id"),
                "season": ctx.get("season"),
                "rank": ctx.get("rank"),
                "dolnytsky_rank_code": ctx.get("dolnytsky_rank_code"),
                "fixed_rank_code": ctx.get("fixed_rank_code"),
                "triodion_book": ctx.get("triodion_book"),
                "menaion_book": ctx.get("menaion_book"),
                "menaion_class": ctx.get("menaion_class"),
                "saint_categories": ctx.get("saint_categories"),
                "paradigm_id": ctx.get("paradigm_id"),
                "rubrics_title": ctx.get("rubrics_title"),
                "digest_text": digest
            }
            payload_days.append(day_info)
        except Exception as e:
            print(f"Error resolving date {dt}: {e}", file=sys.stderr)

    audit_payload = {
        "project": "Typikon Coded UGCC cantor tool",
        "generated_days": payload_days
    }

    # Formatting the Prompt
    prompt = f"""
As the Senior Liturgical Auditor for the Typikon Coded project, audit the following JSON context and generated Typikon Digest outputs for 15 sample days in the year 2026.
Verify that they strictly adhere to UGCC (Dolnytsky / Stamford 2014) liturgical norms.

Specifically search for:
1. **Liturgical Contradictions & Rubric Mismatches**:
   - Class V Simple Saints should NOT have Matins Praises or great/all-night vigil rubrics.
   - Sunday Simple Saint case (e.g. `[4 A+G]`) should map to `Class V — Simple`, NOT `Class IV — Great Doxology` or higher.
   - Any cases where the Class or Book assigned on the backend contradicts the actual rubric case/paradigm being resolved.
   - "Alleluia" instead of "God is the Lord" on Sundays or major feasts (unless explicitly specified in Lent).
2. **Spelling & Terminology Drift**:
   - Ensure the spelling of "exapostilarion" (UGCC standard) is used, NOT "exaposteilarion".
   - Ensure the spelling of "Prokeimenon" and "Prokeimena" is used, NOT "Prokimenon/Prokimena".
   - Ensure "Royal Doors" and "Holy Doors" are capitalized when used in a proper liturgical context in the digest.
3. **Database Key/Developer Leakage**:
   - Ensure no developer placeholders, raw IDs, or raw keys (e.g. `"FIXED"`, `"MOVABLE"`, `"Collision"`, `"Active"`, `"Max:"` or raw IDs like `"menaion.0613.prophet_elisha"`) leak into the customer-facing rubrics titles, headings, or digest text.
   - Raw saint IDs (like `jun_11.bartholomew_barnabas`) must not be visible in the user-facing text.

Below is the generated JSON data for the 15 sample days:
```json
{json.dumps(audit_payload, indent=2)}
```

Generate a detailed Audit Report. Group your findings under:
- **Critical Liturgical Contradictions**
- **Spelling, Terminology & Capitalization Gaps**
- **Developer Key Leakage / Raw ID Exposure**
- **Overall Quality & Integrity Score (0-100)**

Provide the exact date, description of the gap, and the expected correction for every issue found. If no gaps are found in a category, state "No issues detected".
"""

    DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are the senior liturgical auditor for the Typikon Coded project. "
        "Audit the provided data for liturgical correctness, spelling, terminology alignment, and key leakage."
    )

    payload = {
        "model": "deepseek-v4-pro",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "thinking": {"type": "enabled"},
        "max_tokens": 12000
    }

    print("Sending sampled days to DeepSeek API for auditing...")
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        result = ""
        reasoning = ""
        if 'choices' in data and data['choices']:
            msg = data['choices'][0]['message']
            result = msg.get('content') or ""
            reasoning = msg.get('reasoning_content') or ""

        # Make sure directory exists
        output_dir = REPO_DIR / "audit_results"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "llm_audit_report.md"

        final_report = f"# UGCC Typikon Coded: LLM Forensic Audit Report\n\nGenerated on: {datetime.now().isoformat()}\n\n"
        if reasoning:
            final_report += f"## DEEPSEEK THINKING PROCESS:\n\n{reasoning}\n\n---\n\n"
        if result:
            final_report += f"{result}"
        else:
            final_report += "*(No content returned from LLM)*"

        output_path.write_text(final_report, encoding="utf-8")
        print(f"[SUCCESS] Forensic audit report saved to: {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API Request Failed: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
