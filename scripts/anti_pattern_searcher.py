import os
import json
import re
import sys
from pathlib import Path
from datetime import datetime

# Constants
TARGET_DIR = Path(r"C:\Users\augus\.gemini\antigravity\brain")
OUTPUT_FILE = Path("anti_pattern_audit_report.md")

# Excluded directories for workspace file check
WORKSPACE_EXCLUDE_PARTS = {'.gemini', '.agent', 'scratch', 'tmp', 'temp'}

# Banned phrases (regex patterns)
BANNED_PHRASE_PATTERNS = [
    re.compile(r'\beverything\s+is\s+working\b', re.IGNORECASE),
    re.compile(r"\b(i've|i\s+have)\s+successfully\b", re.IGNORECASE),
    re.compile(r'\bthe\s+output\s+correctly\s+reflects\b', re.IGNORECASE),
    re.compile(r'\bthis\s+has\s+been\s+fixed\b', re.IGNORECASE),
    re.compile(r'\bthe\s+changes\s+are\s+complete\b', re.IGNORECASE),
    re.compile(r'\bas\s+expected\b', re.IGNORECASE),
    re.compile(r"\b(i've|i\s+have)\s+verified\b", re.IGNORECASE),
]

# Verification command patterns to look for in run_command calls
VERIFICATION_CMD_PATTERNS = [
    re.compile(r'\bpytest\b', re.IGNORECASE),
    re.compile(r'git\s+(--no-pager\s+)?diff\b', re.IGNORECASE),
    re.compile(r'git\s+status\b', re.IGNORECASE)
]

# Bypass patterns for pager (git diff/log with pager override)
PAGER_BYPASS_PATTERNS = [
    re.compile(r'--no-pager', re.IGNORECASE),
    re.compile(r'\$env:PAGER\s*=', re.IGNORECASE),
    re.compile(r'GIT_PAGER\s*=', re.IGNORECASE),
    re.compile(r'\|\s*cat\b', re.IGNORECASE),
    re.compile(r'>\s*NUL\b', re.IGNORECASE),
    re.compile(r'-c\s+core\.pager\s*=', re.IGNORECASE),
]

# Checklist detection patterns
CHECKLIST_FILES = ['agents.md', 'project_facts.md', 'learnings.md', 'anti_patterns.md']

def get_workspace_root():
    """Return the workspace root directory (assuming script is run from repo root)."""
    if __file__ and not __file__ == '<stdin>':
        script_path = Path(__file__).resolve()
        if script_path.parent.name == 'scripts':
            return script_path.parent.parent
    return Path.cwd()

WORKSPACE_ROOT = get_workspace_root()

def is_workspace_file(filepath_str):
    """Heuristic to decide if a filepath belongs to the Typikon Coded workspace (not scratch/excluded)."""
    if not filepath_str:
        return False
    # Clean the path from potential quotes/escapes
    filepath_str = filepath_str.strip().strip('"').strip("'")
    try:
        p = Path(filepath_str)
        if not p.is_absolute():
            p = WORKSPACE_ROOT / p
        
        p = p.resolve()
        
        # Check if under workspace root
        try:
            rel = p.relative_to(WORKSPACE_ROOT.resolve())
        except ValueError:
            return False
            
        parts = rel.parts
        if any(part in WORKSPACE_EXCLUDE_PARTS for part in parts):
            return False
            
        # Ensure it is a file in the workspace
        return True
    except Exception:
        return False

def get_text_from_step(step):
    """Extract text content from a message step."""
    content = step.get('content')
    if content is None:
        return ''
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict) and 'text' in item:
                texts.append(item['text'])
        return '\n'.join(texts)
    return str(content)

def get_tool_calls(step):
    """Return list of tool call dicts (name, args) from a step."""
    calls = []
    # In planner response, tool calls are inside the list 'tool_calls'
    if step.get('tool_calls'):
        for tc in step['tool_calls']:
            if isinstance(tc, dict):
                calls.append({
                    'name': tc.get('name', ''),
                    'args': tc.get('args', {}) or {}
                })
    return calls

def contains_checklist(text):
    """Check if text contains mentions of standard brain files and citations."""
    text_lower = text.lower()
    has_files = all(f in text_lower for f in CHECKLIST_FILES)
    
    # Citation check: looks for "rule", "protocol", "checklist", or specific file citations
    rule_citation = bool(re.search(r'\b[Rr]ule\s+\d+\b', text))
    checklist_kw = "pre-flight" in text_lower or "preflight" in text_lower or "checklist" in text_lower
    
    return has_files and (rule_citation or checklist_kw)

def contains_verification_tool_call(step):
    """Check if step includes a run_command that runs a verification command (pytest, git diff)."""
    for tc in get_tool_calls(step):
        if tc['name'] == 'run_command':
            cmd_args = tc.get('args', {})
            cmd = str(cmd_args.get('CommandLine', '')).strip().strip('"')
            for pattern in VERIFICATION_CMD_PATTERNS:
                if pattern.search(cmd):
                    return True
    return False

def has_verification_nearby(conversation_steps, model_step_index):
    """Search backward for a verification command within the current turn."""
    for i in range(model_step_index, -1, -1):
        step = conversation_steps[i]
        # Stop search if we cross a user input boundary
        if step.get('source') == 'USER_EXPLICIT' or step.get('type') == 'USER_INPUT':
            break
        if contains_verification_tool_call(step):
            return True
    return False

def check_pager_bypass(command_str):
    """Check if a git diff or git log command has pager bypass."""
    for pattern in PAGER_BYPASS_PATTERNS:
        if pattern.search(command_str):
            return True
    return False

def analyze_conversation(conv_id, steps):
    """Analyze a single conversation's steps and return list of violation dicts."""
    violations = []
    checklist_done = False

    for idx, step in enumerate(steps):
        # Pre-flight checklist detection in model messages
        if step.get('source') == 'MODEL' and step.get('type') in ('PLANNER_RESPONSE', 'message'):
            text = get_text_from_step(step)
            if contains_checklist(text):
                checklist_done = True

            # Banned phrase detection
            for pattern in BANNED_PHRASE_PATTERNS:
                if pattern.search(text):
                    if not has_verification_nearby(steps, idx):
                        snippet = text[:200].replace('\n', ' ')
                        violations.append({
                            'type': 'Banned Phrase without Evidence',
                            'step': step.get('step_index', idx),
                            'snippet': snippet,
                            'details': f"Matched banned phrase: '{pattern.pattern}' without verification output."
                        })

        # Check tool calls
        for tc in get_tool_calls(step):
            tool_name = tc['name']
            args = tc['args']

            # Pre-flight checklist failure
            if tool_name in ('write_to_file', 'replace_file_content', 'multi_replace_file_content'):
                target_file = args.get('TargetFile', '')
                if not target_file:
                    # Fallback argument names
                    target_file = args.get('Target_File', args.get('file_path', args.get('path', '')))
                
                if target_file:
                    target_file = str(target_file).strip().strip('"')
                    if is_workspace_file(target_file):
                        if not checklist_done:
                            violations.append({
                                'type': 'Pre-flight Checklist Failure',
                                'step': step.get('step_index', idx),
                                'snippet': f"{tool_name} on {target_file}",
                                'details': f"Modified workspace file '{target_file}' before completing checklist."
                            })

            # Pager lock detection
            if tool_name == 'run_command':
                cmd_str = str(args.get('CommandLine', '')).strip().strip('"')
                if not cmd_str:
                    cmd_str = str(args.get('command', args.get('cmd', str(args))))
                
                if re.search(r'\bgit\s+diff\b', cmd_str, re.IGNORECASE) or re.search(r'\bgit\s+log\b', cmd_str, re.IGNORECASE):
                    if not check_pager_bypass(cmd_str):
                        violations.append({
                            'type': 'Interactive Pager Lock Hazard',
                            'step': step.get('step_index', idx),
                            'snippet': cmd_str[:200],
                            'details': f"Executed '{cmd_str}' without pager bypass argument (e.g., --no-pager)."
                        })

    return violations

def scan_transcript(conv_id, filepath):
    """Read a JSONL transcript file and return list of step dicts."""
    steps = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    step = json.loads(line)
                    if 'step_index' not in step:
                        step['step_index'] = line_no
                    steps.append(step)
                except json.JSONDecodeError as e:
                    pass
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
    return steps

def main():
    print(f"Scanning conversations in {TARGET_DIR} ...")
    if not TARGET_DIR.exists():
        print(f"Error: Target directory {TARGET_DIR} does not exist.", file=sys.stderr)
        sys.exit(1)

    total_convos = 0
    all_violations = []

    # Recursively search for transcript.jsonl
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file == "transcript.jsonl":
                path = Path(root) / file
                parts = path.parts
                
                # Resolve conversation ID
                conv_id = "unknown"
                if len(parts) >= 4 and parts[-2] == "logs" and parts[-3] == ".system_generated":
                    conv_id = parts[-4]
                else:
                    conv_id = path.parent.parent.name
                
                total_convos += 1
                steps = scan_transcript(conv_id, path)
                if steps:
                    violations = analyze_conversation(conv_id, steps)
                    if violations:
                        all_violations.append((conv_id, violations))

    # Generate Report
    print(f"Scanned {total_convos} conversations. Found {len(all_violations)} with violations.")
    
    report_lines = []
    report_lines.append("# Anti-Pattern & Checklist Compliance Audit Report")
    report_lines.append(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"\n## Summary")
    report_lines.append(f"- **Total Conversations Scanned**: {total_convos}")
    report_lines.append(f"- **Conversations with Violations**: {len(all_violations)}")
    
    # Aggregate statistics
    by_type = {}
    for conv_id, violations in all_violations:
        for v in violations:
            by_type[v['type']] = by_type.get(v['type'], 0) + 1
            
    report_lines.append(f"\n## Violations by Category")
    for v_type, count in by_type.items():
        report_lines.append(f"- **{v_type}**: {count}")
        
    report_lines.append(f"\n## Detailed Violation Log")
    
    for conv_id, violations in all_violations:
        report_lines.append(f"\n### Conversation ID: [{conv_id}](file:///C:/Users/augus/.gemini/antigravity/brain/{conv_id})")
        for v in violations:
            report_lines.append(f"- **Type**: {v['type']}")
            report_lines.append(f"  - **Step Index**: {v['step']}")
            report_lines.append(f"  - **Details**: {v['details']}")
            clean_snippet = v['snippet'].replace('\n', ' ').strip()
            report_lines.append(f"  - **Snippet**: `{clean_snippet}`")

    OUTPUT_FILE.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Audit report saved to: {OUTPUT_FILE.resolve()}")

if __name__ == "__main__":
    main()