import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

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
    api_key = get_deepseek_key()
    if not api_key:
        print("Error: DEEPSEEK_API_KEY not found.", file=sys.stderr)
        sys.exit(1)

    print("Loading audit report summary...")
    report_path = Path("anti_pattern_audit_report.md")
    if not report_path.exists():
        print("Error: anti_pattern_audit_report.md not found.", file=sys.stderr)
        sys.exit(1)

    report_content = report_path.read_text(encoding="utf-8")
    
    # Extract the summary and the first 5000 characters of the violation log for context
    lines = report_content.splitlines()
    summary_section = []
    log_sample = []
    
    in_log = False
    for line in lines:
        if line.startswith("## Detailed Violation Log"):
            in_log = True
        if not in_log:
            summary_section.append(line)
        else:
            if len(log_sample) < 150:  # Grab first 150 lines of logs
                log_sample.append(line)
                
    summary = "\n".join(summary_section)
    sample_logs = "\n".join(log_sample)

    print("Loading current brain files for reference...")
    agents_md = Path(".agents/AGENTS.md").read_text(encoding="utf-8")
    anti_patterns = Path(".agents/references/anti_patterns.md").read_text(encoding="utf-8")
    
    prompt = f"""
We ran an audit on 489 conversation logs from our Gemini agent sessions. Here is the summary of violations:
{summary}

Here is a sample of the violation log entries:
{sample_logs}

We want to design a set of intelligent, airtight safeguards to completely eliminate these compliance failures in future sessions.
Specifically, we want to:
1. **Flesh out brain files**:
   - Update `.agents/AGENTS.md` (specifically the Pre-Flight checklist and context management rules) to be more prominent, clean, and structured.
   - Update `.agents/references/anti_patterns.md` to add clear, actionable details for each failure class.
2. **Create/Update AI agent Skills**:
   - Create a new skill directory `compliance_gate` containing `SKILL.md` (or expand `anti_hallucination_gate`) that explains the automated session compliance checks.
3. **Build an Automated Compliance Test**:
   - Design a pytest file `tests/test_session_compliance.py` that:
     - Dynamically finds the active conversation ID.
     - Reads the active conversation's `transcript.jsonl`.
     - Fails if a workspace file was modified without a preceding pre-flight checklist.
     - Fails if banned phrases are present without verification command tool calls in the same turn.
     - Fails if pager commands (git diff/log without --no-pager) were run.
     - Allows self-correction (i.e. if the agent runs the checklist *after* making a mistake, the test will pass, so the agent can fix a missing checklist without needing to revert their branch).

Please act as the Supreme Liturgical Compliance Auditor and generate a comprehensive plan. Return a single markdown document containing:
1. A reconciliation analysis explaining why these failures happened so frequently (e.g. context window dilution, agreeable momentum).
2. The exact proposed changes for:
   - `.agents/AGENTS.md`
   - `.agents/references/anti_patterns.md`
   - `.agents/skills/anti_hallucination_gate/SKILL.md`
   - `.agents/skills/compliance_gate/SKILL.md` (if a new skill is proposed)
3. The exact python code for `tests/test_session_compliance.py` to act as the mechanical gate.

Make sure all paths, terminology, and formatting conform to UGCC Royal Doors standards.
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-v4-pro",
        "messages": [
            {"role": "system", "content": "You are the senior architect and compliance officer. Return your response in detailed markdown format."},
            {"role": "user", "content": prompt}
        ],
        "thinking": {"type": "enabled"},
        "max_tokens": 8000
    }

    print("Calling DeepSeek API to reconcile failures...")
    try:
        response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        result = data['choices'][0]['message']['content']
        
        output_file = Path("C:/Users/augus/.gemini/antigravity/brain/92dae9b2-3c42-4244-9591-d545d1b9a341/scratch/deepseek_reconciliation_proposal.md")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(result, encoding="utf-8")
        print(f"Success! Reconciliation proposal written to {output_file}")
        
    except Exception as e:
        print(f"Error calling DeepSeek: {e}", file=sys.stderr)
        if 'response' in locals() and response is not None:
            print(response.text, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
