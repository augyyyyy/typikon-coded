import os
import sys
import json
import argparse
import requests
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

DEEPSEEK_API_KEY = get_deepseek_key()

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def compile_workspace_context(base_dir: Path) -> str:
    """Recursively compile the project's key files into a single markdown string."""
    print("Compiling workspace context...")
    
    included_extensions = {".py", ".json", ".md"}
    excluded_dirs = {".git", ".venv", "__pycache__", "browser_recordings", "html_artifacts", "Data", "json_db", "tests", "cantor_dashboard", "cantor_prototypes", "final_results", "archive", "verification_examples", "generated_digests", "audit_results", "assets"}
    
    context_parts = []
    
    # Files to explicitly prioritize
    priority_files = [
        "AGENT_COMPLIANCE.md",
        ".cursorrules",
        "README.md",
        "docs/ARCHITECTURE.md",
        "docs/DOLNYTSKY_IMPLEMENTATION.md",
        "typikon_digest_generator.py"
    ]
    
    for pf in priority_files:
        path = base_dir / pf
        if path.exists() and path.is_file():
            try:
                content = path.read_text(encoding="utf-8")
                context_parts.append(f"### File: {pf}\n```\n{content}\n```\n")
            except Exception as e:
                print(f"Failed to read {pf}: {e}")

    # Now walk the rest of the workspace
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith(".")]
        
        for file in files:
            path = Path(root) / file
            rel_path = path.relative_to(base_dir).as_posix()
            
            if rel_path in priority_files:
                continue
                
            if path.suffix in included_extensions:
                try:
                    content = path.read_text(encoding="utf-8")
                    # Avoid incredibly massive raw DB files if they exceed token limits,
                    # but for 1M context, we can afford most. Let's include them.
                    context_parts.append(f"### File: {rel_path}\n```\n{content}\n```\n")
                except Exception as e:
                    print(f"Skipping {rel_path}: {e}")
                    
    compiled = "\n".join(context_parts)
    print(f"Context compiled. Total characters: {len(compiled)}")
    return compiled

def send_to_deepseek(task: str, context: str, output_file: str):
    """Send the payload to DeepSeek API."""
    api_key = DEEPSEEK_API_KEY
    if not api_key:
        print("Error: DEEPSEEK_API_KEY or deepseek-v4-pro key not found in .env or environment.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Sending task to DeepSeek API: {task}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are the senior architect and compliance gatekeeper for the Typikon Coded project. "
        "You have a 1-million token context window. Below is the entire codebase, including strict "
        "compliance rules like AGENT_COMPLIANCE.md and .cursorrules, as well as the engine logic.\n\n"
        "Your task is to comprehensively analyze the codebase to accomplish the user's objective, "
        "paying extremely close attention to the formatting constraints and canonical rubrics. "
        "Provide your analysis, code reviews, and implementation details below."
    )
    
    payload = {
        "model": "deepseek-v4-pro", # Transitioned to current V4 API
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the project context:\n\n{context}\n\nTask:\n{task}"}
        ],
        "thinking": {"type": "enabled"}, # Enable thinking/reasoning mode for analytical architecture checks
        "max_tokens": 8000
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        result = data['choices'][0]['message']['content']
        
        if output_file:
            Path(output_file).write_text(result, encoding="utf-8")
            print(f"\nAnalysis saved to {output_file}")
        else:
            print("\n" + "="*40 + "\nDEEPSEEK ANALYSIS\n" + "="*40 + "\n")
            print(result)
            print("\n" + "="*40)
            
    except requests.exceptions.RequestException as e:
        print(f"API Request Failed: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="DeepSeek Context Offloader Tool")
    parser.add_argument("--task", type=str, required=True, help="The task for DeepSeek to perform")
    parser.add_argument("--output", type=str, help="Optional file path to save the output markdown")
    args = parser.add_argument_group()
    
    parsed = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent
    context = compile_workspace_context(base_dir)
    send_to_deepseek(parsed.task, context, parsed.output)

if __name__ == "__main__":
    main()
