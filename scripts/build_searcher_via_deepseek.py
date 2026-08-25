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

    print("Reading compliance rule definitions...")
    agents_rules = Path(".agents/AGENTS.md").read_text(encoding="utf-8")
    anti_patterns = Path(".agents/references/anti_patterns.md").read_text(encoding="utf-8")
    compliance_rules = Path(".agents/references/agent_compliance.md").read_text(encoding="utf-8")

    prompt = f"""
You need to generate a Python script named `scripts/anti_pattern_searcher.py` that will act as a scanning tool to search all local conversation transcripts in the Gemini app data directory for anti-pattern behavior and checklist failures.

Here is the context of the rules we must enforce:
1. **Pre-flight Checklist (Rule 11/Step 1 failure)**: Before editing/creating any files in the workspace (excluding scratch/test directories), the agent MUST run a checklist stating:
   - That they read `AGENTS.md` and `project_facts.md`.
   - That they read `learnings.md` and `anti_patterns.md`.
   - Cite at least ONE specific rule from these files.
   *Failure definition*: The agent makes a codebase modification (e.g. calls `write_to_file`, `replace_file_content`, or `multi_replace_file_content` on non-scratch, non-temporary files in the `Typikon Coded` repository) but has not outputted the checklist prior to that step in the transcript.
2. **Banned Phrases (without evidence)**: Using words like "Everything is working", "I've successfully", "This has been fixed", etc. without running verification commands in the same turn or immediately prior.
3. **Interactive Pager Locks**: Proposing commands like `git diff` or `git log` that do not bypass pagers (lacking `--no-pager` or `$env:PAGER="cat"`).
4. **Fabricated Progress**: Narrating that a subagent or script succeeded when it actually failed or didn't run.

The target directory containing transcripts is: `C:\\Users\\augus\\.gemini\\antigravity\\brain`
Inside this directory are many subdirectories (one per conversation ID).
For each subdirectory, if it contains `.system_generated\\logs\\transcript.jsonl`, scan it.

Please write the complete Python script `scripts/anti_pattern_searcher.py`.
The script should:
- Recursively scan `C:\\Users\\augus\\.gemini\\antigravity\\brain` for `transcript.jsonl` files.
- Parse the JSONL lines. Each line is a step.
- Track step index, type, source, tool_calls, content.
- Identify:
  1. **Pre-flight Checklist / Step 1 Failures**: Check if a tool call to `write_to_file`, `replace_file_content`, or `multi_replace_file_content` target file is in the workspace `Typikon Coded` directory (not a scratch file, not under `.gemini` or `.agent`), and check if the preceding model messages in that conversation contain the checklist checklist content/citations. Specifically, look for citations of rule files, keywords like "Pre-Flight Checklist", "Pre-flight Checklist", etc. If the checklist is missing before a modification, report it.
  2. **Banned Phrases Failures**: Search model messages for banned phrases. Check if the model has run pytest or git diff within the same or previous turn as the banned phrase.
  3. **Pager Locks**: Search terminal commands run via `run_command` for `git diff` or `git log` without pager overrides.
- Save a detailed Markdown report at `anti_pattern_audit_report.md` detailing:
  - Total conversations scanned.
  - Total violations found.
  - For each conversation with violations, print the conversation ID, a list of violations, the exact step number, and a snippet of the violating message/tool call.
- The script should be robust, handle exceptions, run fast, and use utf-8 encoding for all file operations.
- The script should output progress to stdout.

Please return ONLY the raw Python code. Do not include markdown code block formatting (like ```python) around the code, return only the executable code.
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-v4-pro",
        "messages": [
            {"role": "system", "content": "You are a senior system tool developer. Return only the raw Python script as requested, without markdown formatting."},
            {"role": "user", "content": prompt}
        ],
        "thinking": {"type": "enabled"},
        "max_tokens": 8000
    }

    print("Sending request to DeepSeek API...")
    try:
        response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        result = data['choices'][0]['message']['content'].strip()
        # Strip code blocks if deepseek ignores the system prompt instruction
        if result.startswith("```python"):
            result = result[9:]
        if result.endswith("```"):
            result = result[:-3]
        result = result.strip()

        output_file = Path("scripts/anti_pattern_searcher.py")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(result, encoding="utf-8")
        print(f"Success! Generated searcher script saved to {output_file}")

    except Exception as e:
        print(f"Error calling DeepSeek API: {e}", file=sys.stderr)
        if 'response' in locals() and response is not None:
            print(response.text, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
