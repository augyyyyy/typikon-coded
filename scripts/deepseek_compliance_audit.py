import os
import sys
import json
import argparse
import requests
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

# Robust DeepSeek key loader to handle different execution directories and formats
def get_deepseek_key():
    # 1. Try direct environment variable
    key = os.getenv("DEEPSEEK_API_KEY")
    if key and key != "your_deepseek_api_key_here":
        return key

    # 2. Try global .env file path
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

    # 3. Try local .env
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

ENV_PATH = Path("C:/Users/augus/OneDrive/Documents/Google Antigravity/Projects/.env")
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

api_key = get_deepseek_key()

# Primary base directories
CANTOR_DASHBOARD_DIR = Path(__file__).parent.parent / "cantor_dashboard"
REPO_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_DIR))

try:
    from ruthenian_engine import RuthenianEngine
    from typikon_digest_generator import TypikonDigestGenerator
except ImportError:
    sys.path.insert(0, str(REPO_DIR / "engine"))
    from ruthenian_engine import RuthenianEngine
    from typikon_digest_generator import TypikonDigestGenerator

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def get_expected_readings_for_date(target_date: date, pascha_offset: int, day_of_week: int) -> str:
    """Resolve ground-truth lectionary readings for prompt injection if available."""
    if pascha_offset < 49:
        return "Not in the post-Pentecost ordinary period. Audit according to Lenten/Paschal rubrics in reference texts."
        
    weeks_after_pentecost = (pascha_offset - 49) // 7 + 1
    
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
        ep, gosp = lectionary[weeks_after_pentecost][day_of_week]
        return f"Epistle: {ep}, Gospel: {gosp} (Week {weeks_after_pentecost}, Day {day_of_week} after Pentecost)"
    
    return f"Week {weeks_after_pentecost} after Pentecost (not in standard table, lookup from reference texts)."

def compile_reference_files(repo_dir: Path, target_date: date, season_id: str) -> str:
    """Compile specific reference texts, scoped to target date and season, to avoid context dilution."""
    print("Compiling Typikon reference files (scoped)...")
    ref_parts = []
    
    ref_dir = repo_dir / "Data" / "Service Books" / "Typikon"
    if not ref_dir.exists():
        print(f"Error: Reference directory not found at {ref_dir}", file=sys.stderr)
        return ""
        
    # 1. Load Glossary (always)
    glossary_path = ref_dir / "Final_Dolnytsky_glossary.md"
    if glossary_path.exists():
        content = glossary_path.read_text(encoding="utf-8")
        ref_parts.append(f"=== REFERENCE FILE: Final_Dolnytsky_glossary.md ===\n{content}\n")
        print(f"   Loaded glossary ({len(content)} chars)")

    # 2. Load Vocabulary Matrix (always)
    matrix_path = ref_dir / "vocabulary_standardization_matrix.md"
    if matrix_path.exists():
        content = matrix_path.read_text(encoding="utf-8")
        ref_parts.append(f"=== REFERENCE FILE: vocabulary_standardization_matrix.md ===\n{content}\n")
        print(f"   Loaded vocabulary matrix ({len(content)} chars)")

    # 3. Load sliced Menaion (Part 3)
    menaion_path = ref_dir / "Final_Dolnytsky_part3_menaion.txt"
    if menaion_path.exists():
        try:
            content = menaion_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            
            # Map target month to the header in the file
            month_map = {
                1: "JANUARY", 2: "FEBRUARY", 3: "MARCH", 4: "APRIL", 5: "MAY", 6: "JUNE",
                7: "JULY", 8: "AUGUST", 9: "SEPTEMBER", 10: "OCTOBER", 11: "NOVEMBER", 12: "DECEMBER"
            }
            target_month_name = month_map.get(target_date.month)
            months_in_file_order = [
                "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER", 
                "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", 
                "JUNE", "JULY", "AUGUST"
            ]
            
            # Find start line
            start_line_idx = -1
            for i, line in enumerate(lines):
                trimmed = line.strip()
                if trimmed == target_month_name:
                    start_line_idx = i
                    break
            
            if start_line_idx == -1:
                # Fallback search
                for i, line in enumerate(lines):
                    trimmed = line.strip().upper()
                    if trimmed.startswith(f"1 {target_month_name}") or trimmed.startswith(f"{target_month_name} "):
                        start_line_idx = i
                        break
            
            if start_line_idx != -1:
                end_line_idx = -1
                next_month_names = months_in_file_order[months_in_file_order.index(target_month_name) + 1:]
                for i in range(start_line_idx + 1, len(lines)):
                    trimmed = lines[i].strip()
                    if trimmed in next_month_names:
                        end_line_idx = i
                        break
                
                slice_lines = lines[start_line_idx:end_line_idx] if end_line_idx != -1 else lines[start_line_idx:]
                sliced_content = "\n".join(slice_lines)
                ref_parts.append(f"=== REFERENCE FILE: Final_Dolnytsky_part3_menaion.txt (SLICED: {target_month_name}) ===\n{sliced_content}\n")
                print(f"   Loaded sliced Menaion for {target_month_name} ({len(sliced_content)} chars)")
            else:
                print(f"   Warning: Could not slice Menaion for month: {target_month_name}", file=sys.stderr)
        except Exception as e:
            print(f"   Failed to load sliced Menaion: {e}", file=sys.stderr)

    # 4. Load Triodion (Part 4) ONLY during Triodion/Pentecostarion seasons
    if season_id in ("triodion", "pentecostarion"):
        triodion_path = ref_dir / "Final_Dolnytsky_part4_triodion.txt"
        if triodion_path.exists():
            try:
                content = triodion_path.read_text(encoding="utf-8")
                ref_parts.append(f"=== REFERENCE FILE: Final_Dolnytsky_part4_triodion.txt ===\n{content}\n")
                print(f"   Loaded Triodion ({len(content)} chars)")
            except Exception as e:
                print(f"   Failed to load Triodion: {e}", file=sys.stderr)
    else:
        print("   Skipped Triodion reference file (not in Triodion/Pentecostarion season)")
        
    return "\n".join(ref_parts)

def compile_codebase_context(repo_dir: Path) -> str:
    """Compile core code generators and logic definitions (skipped to prevent context dilution)."""
    return ""

def generate_digests_for_date(target_date: date) -> tuple:
    """Generate both full and quick reference digests for the target date."""
    print(f"Generating digests for target date: {target_date.isoformat()}...")
    engine = RuthenianEngine(version="stamford_2014")
    ctx = engine.get_liturgical_context(target_date)
    rubrics = engine.resolve_rubrics(ctx)
    
    generator = TypikonDigestGenerator(engine)
    full_digest = generator.generate(ctx, rubrics, mode="full")
    quick_digest = generator.generate(ctx, rubrics, mode="quick")
    
    return full_digest, quick_digest, ctx, rubrics

def main():
    parser = argparse.ArgumentParser(description="DeepSeek Typikon Compliance Auditor")
    parser.add_argument("--date", type=str, required=True, help="Target date in YYYY-MM-DD format")
    parser.add_argument("--output", type=str, help="Output markdown file to write the audit results to")
    
    args = parser.parse_args()
    
    try:
        target_date = date.fromisoformat(args.date)
    except ValueError:
        print("Error: Invalid date format. Use YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)
        
    global api_key
    if not api_key:
        print("Error: DeepSeek API key not found in .env or environment.", file=sys.stderr)
        sys.exit(1)
        
    # 1. Generate local digests
    full_digest, quick_digest, ctx, rubrics = generate_digests_for_date(target_date)
    
    # 2. Compile reference texts
    ref_context = compile_reference_files(REPO_DIR, target_date, ctx.get("season_id", "octoechos"))
    
    # 3. Compile codebase context
    code_context = compile_codebase_context(REPO_DIR)
    
    # 4. Resolve ground-truth expected readings
    expected_readings = get_expected_readings_for_date(target_date, ctx.get("pascha_offset", 0), ctx.get("day_of_week", 0))
    
    # 5. Formulate the audit prompt
    audit_prompt = f"""
Liturgical Date of Audit: {target_date.isoformat()}

CALENDAR & LECTIONARY ASSUMPTIONS:
- Calendar Type: Gregorian (by default, target parish operates under the Gregorian/New Calendar)
- Pascha Offset: {ctx.get("pascha_offset")} (days since Pascha)
- Weeks after Pentecost: {ctx.get("weeks_after_pentecost")}
- Day of Week: {ctx.get("day_of_week")}
- EXPECTED LECTIONARY READINGS (Ground Truth): {expected_readings}

Generated Digests to Audit:
---------------------------------------------
=== 1. GENERATED FULL SERVICE DIGEST ===
{full_digest}

=== 2. GENERATED QUICK REFERENCE DIGEST ===
{quick_digest}
---------------------------------------------

Liturgical Context Metadata resolved by Engine:
{json.dumps(ctx, indent=2, default=str)}

Resolved Rubrics:
{json.dumps(rubrics, indent=2, default=str)}

AUDIT INSTRUCTIONS:
You are the Supreme Liturgical Compliance Auditor for the Byzantine-Ruthenian Rite (acting according to the Isidor Dolnytsky Typikon).
You have access to the exact reference control files (Final_Dolnytsky_glossary.md, vocabulary_standardization_matrix.md, and Final_Dolnytsky_part3_menaion.txt sliced for the month).

Analyze the generated digests for {target_date.isoformat()} line-by-line and identify all compliance gaps against the reference rubrics.

Categorize your assessment under the following exact sections:
1. Saint's Rank Classification Gap (Menaion & General Rubrics alignment)
2. Scriptural Readings Accuracy (Epistle, Gospel, Tone, and Verses alignment - checking if lectionary advanced correctly)
3. Precedence / Combination Rules (e.g. Cross vs Temple Kontakion rules on Wednesdays/Fridays, or feast day combinations)
4. Formatting, Capitalization, and Database Artifacts (Bolding, italics, mashed lines, lowercase book names, parenthetical leaking)

For each gap:
- Cite the exact rule or text from the reference files (with file name and context).
- Explain the gap.
- Provide the exact correction that must be applied to the output.
"""

    reminder_instructions = """
REMINDER OF CRITICAL COMPLIANCE RULES:
1. ONLY audit terms actually present in the generated digest.
2. DO NOT list capitalization corrections for words that are already capitalized or are standard nouns (do not complain about lowercase words unless they are specifically liturgical proper names that violated standard matrix conventions).
3. Confirm that the spelling of "Prokeimenon" and "Prokeimena" is used throughout. Prokimenon/Prokimena are rejected.
4. Verify the readings strictly align with the expected lectionary readings provided above.
"""

    print("Sending payload to DeepSeek API...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are the senior liturgical auditor for the Typikon Coded project. "
        "You have a 1-million token context window. Below are the canonical Dolnytsky Typikon reference files "
        "(glossary, vocabulary standardization matrix, and target Menaion/Triodion sections). "
        "Audit the provided digests against these canonical sources with absolute precision and strict compliance. "
        "Be extremely direct, listing every single gap and citation."
    )
    
    # We combine reference, codebase, and audit task
    payload = {
        "model": "deepseek-v4-pro", # Transitioned to current V4 API
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{ref_context}\n\n{code_context}\n\n{audit_prompt}\n\n{reminder_instructions}"}
        ],
        "thinking": {"type": "enabled"}, # Enable thinking/reasoning mode for detailed liturgical compliance analysis
        "max_tokens": 8000
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        result = data['choices'][0]['message']['content']
        
        output_path = Path(args.output) if args.output else REPO_DIR / f"compliance_report_{target_date}.md"
        output_path.write_text(result, encoding="utf-8")
        print(f"\n[SUCCESS] Compliance report saved to: {output_path}")
        
    except requests.exceptions.RequestException as e:
        print(f"API Request Failed: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
