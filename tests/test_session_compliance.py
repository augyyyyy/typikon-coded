import os
import json
import re
from pathlib import Path
import pytest

# Constants
BRAIN_DIR = Path(r"C:\Users\augus\.gemini\antigravity\brain")
WORKSPACE_EXCLUDE_PARTS = {'.gemini', '.agent', '.git', '.venv', 'scratch', 'tmp', 'temp'}

BANNED_PHRASES = [
    (re.compile(r'\beverything\s+is\s+working\b', re.IGNORECASE), "Everything is working"),
    (re.compile(r"\b(i've|i\s+have)\s+successfully\b", re.IGNORECASE), "I have successfully"),
    (re.compile(r'\bthe\s+output\s+correctly\s+reflects\b', re.IGNORECASE), "The output correctly reflects"),
    (re.compile(r'\bthis\s+has\s+been\s+fixed\b', re.IGNORECASE), "This has been fixed"),
    (re.compile(r'\bthe\s+changes\s+are\s+complete\b', re.IGNORECASE), "The changes are complete"),
    (re.compile(r'\bas\s+expected\b', re.IGNORECASE), "As expected"),
    (re.compile(r"\b(i've|i\s+have)\s+verified\b", re.IGNORECASE), "I have verified")
]

VERIFICATION_CMD_PATTERNS = [
    re.compile(r'\bpytest\b', re.IGNORECASE),
    re.compile(r'git\s+(--no-pager\s+)?diff\b', re.IGNORECASE),
    re.compile(r'git\s+status\b', re.IGNORECASE)
]

PAGER_BYPASS_PATTERNS = [
    re.compile(r'--no-pager', re.IGNORECASE),
    re.compile(r'\$env:PAGER\s*=', re.IGNORECASE),
    re.compile(r'GIT_PAGER\s*=', re.IGNORECASE),
    re.compile(r'\|\s*cat\b', re.IGNORECASE),
    re.compile(r'>\s*NUL\b', re.IGNORECASE),
    re.compile(r'-c\s+core\.pager\s*=', re.IGNORECASE),
]

CHECKLIST_FILES = ['agents.md', 'project_facts.md', 'learnings.md', 'anti_patterns.md']

def get_workspace_root():
    return Path(__file__).resolve().parent.parent

WORKSPACE_ROOT = get_workspace_root()

def is_workspace_file(filepath_str):
    """Heuristic to check if path belongs to actual Typikon Coded workspace logic/tests/configs."""
    if not filepath_str:
        return False
    filepath_str = filepath_str.strip().strip('"').strip("'")
    try:
        p = Path(filepath_str)
        if not p.is_absolute():
            p = WORKSPACE_ROOT / p
        
        p = p.resolve()
        
        # Must be under workspace root
        try:
            rel = p.relative_to(WORKSPACE_ROOT.resolve())
        except ValueError:
            return False
            
        parts = rel.parts
        if any(part in WORKSPACE_EXCLUDE_PARTS for part in parts):
            return False
            
        return True
    except Exception:
        return False

def get_active_transcript_path():
    """Detect the active conversation ID transcript based on .active_session_id file or mtime fallback."""
    session_id_file = WORKSPACE_ROOT / ".active_session_id"
    if session_id_file.exists():
        try:
            conv_id = session_id_file.read_text(encoding="utf-8").strip()
            log_file = BRAIN_DIR / conv_id / ".system_generated" / "logs" / "transcript.jsonl"
            if log_file.exists():
                return log_file
        except Exception:
            pass

    if not BRAIN_DIR.exists():
        return None
        
    active_path = None
    max_mtime = 0
    for p in BRAIN_DIR.iterdir():
        if p.is_dir():
            log_file = p / ".system_generated" / "logs" / "transcript.jsonl"
            if log_file.exists():
                mtime = log_file.stat().st_mtime
                if mtime > max_mtime:
                    max_mtime = mtime
                    active_path = log_file
    return active_path

def get_text_from_step(step):
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
    calls = []
    if step.get('tool_calls'):
        for tc in step['tool_calls']:
            if isinstance(tc, dict):
                calls.append({
                    'name': tc.get('name', ''),
                    'args': tc.get('args', {}) or {}
                })
    return calls

def contains_checklist(text):
    text_lower = text.lower()
    has_files = all(f in text_lower for f in CHECKLIST_FILES)
    
    rule_citation = bool(re.search(r'\b[Rr]ule\s+\d+\b', text))
    checklist_kw = "pre-flight" in text_lower or "preflight" in text_lower or "checklist" in text_lower
    
    return has_files and (rule_citation or checklist_kw)

def contains_verification_tool_call(step):
    for tc in get_tool_calls(step):
        if tc['name'] == 'run_command':
            cmd_args = tc.get('args', {})
            cmd = str(cmd_args.get('CommandLine', '')).strip().strip('"')
            for pattern in VERIFICATION_CMD_PATTERNS:
                if pattern.search(cmd):
                    return True
    return False

def has_verification_nearby(steps, model_step_index):
    for i in range(model_step_index, -1, -1):
        step = steps[i]
        if step.get('source') == 'USER_EXPLICIT' or step.get('type') == 'USER_INPUT':
            break
        if contains_verification_tool_call(step):
            return True
    return False

def check_pager_bypass(command_str):
    for pattern in PAGER_BYPASS_PATTERNS:
        if pattern.search(command_str):
            return True
    return False

def test_session_compliance():
    """Verify that the current conversation complies with all operational guidelines."""
    transcript_path = get_active_transcript_path()
    if not transcript_path:
        # If no transcript exists (e.g. CI or fresh checkouts), pass gracefully
        pytest.skip("No conversation transcripts found in the brain directory.")
        
    print(f"\nAuditing active transcript: {transcript_path}")
    
    # Parse transcript steps
    steps = []
    with open(transcript_path, 'r', encoding='utf-8') as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                step = json.loads(line)
                step['line_number'] = line_no
                steps.append(step)
            except json.JSONDecodeError:
                pass
                
    if not steps:
        pytest.skip("Active transcript is empty.")

    # 1. Pre-flight Checklist Verification
    # Check if there are any edits to workspace files
    modified_files = []
    checklist_done = False
    
    for idx, step in enumerate(steps):
        # Check if model has intoned the checklist in this conversation
        if step.get('source') == 'MODEL':
            text = get_text_from_step(step)
            if contains_checklist(text):
                checklist_done = True
                
        for tc in get_tool_calls(step):
            if tc['name'] in ('write_to_file', 'replace_file_content', 'multi_replace_file_content'):
                args = tc['args']
                target_file = args.get('TargetFile', '')
                if not target_file:
                    target_file = args.get('Target_File', args.get('file_path', args.get('path', '')))
                
                if target_file:
                    target_file_str = str(target_file).strip().strip('"')
                    if is_workspace_file(target_file_str):
                        modified_files.append((target_file_str, step['line_number']))

    if modified_files and not checklist_done:
        first_file, line_no = modified_files[0]
        pytest.fail(
            f"Pre-flight Checklist Failure! You modified a workspace file ('{first_file}' at step/line {line_no}) "
            f"but did not run the Pre-Flight Checklist first.\n"
            f"Please run the Pre-Flight Checklist in your next turn by stating:\n"
            f"1. You read .agents/AGENTS.md and .agents/references/project_facts.md\n"
            f"2. You read .agents/references/learnings.md and .agents/references/anti_patterns.md\n"
            f"3. Cite at least one rule (e.g. 'Rule 11' or 'Evidence Gate') relevant to your work."
        )

    # 2. Banned Phrases Verification
    for idx, step in enumerate(steps):
        if step.get('source') == 'MODEL' and step.get('type') in ('PLANNER_RESPONSE', 'message'):
            text = get_text_from_step(step)
            for pattern, phrase_name in BANNED_PHRASES:
                if pattern.search(text):
                    if not has_verification_nearby(steps, idx):
                        snippet = text[:150].replace('\n', ' ').strip()
                        pytest.fail(
                            f"Banned Phrase Violation! You used the banned phrase '{phrase_name}' "
                            f"at step/line {step['line_number']} without running a verification command "
                            f"(like pytest, git diff, or git status) in the same turn.\n"
                            f"Snippet: \"{snippet}...\"\n"
                            f"Please run pytest or git status now to satisfy the Evidence Gate."
                        )

    # 3. Interactive Pager Lock Hazard Verification
    for idx, step in enumerate(steps):
        for tc in get_tool_calls(step):
            if tc['name'] == 'run_command':
                cmd_args = tc['args']
                cmd_str = str(cmd_args.get('CommandLine', '')).strip().strip('"')
                if not cmd_str:
                    cmd_str = str(cmd_args.get('command', cmd_args.get('cmd', str(cmd_args))))
                
                if re.search(r'\bgit\s+diff\b', cmd_str, re.IGNORECASE) or re.search(r'\bgit\s+log\b', cmd_str, re.IGNORECASE):
                    if not check_pager_bypass(cmd_str):
                        pytest.fail(
                            f"Interactive Pager Hazard! You executed command '{cmd_str}' "
                            f"at step/line {step['line_number']} without specifying a pager bypass (e.g., --no-pager or GIT_PAGER=cat).\n"
                            f"Please use git --no-pager diff or git --no-pager log instead."
                        )
