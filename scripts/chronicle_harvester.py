import os
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime

def parse_git_history(project_root):
    print("Harvesting Git commit history...")
    commits = []
    cmd = ['git', '--no-pager', 'log', '--reverse', '--format=%H|%an|%ad|%s', '--date=iso']
    try:
        res = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding='utf-8', errors='replace')
        for line in res.stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.split('|', 3)
            if len(parts) == 4:
                commits.append({
                    "type": "git_commit",
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "summary": parts[3]
                })
    except Exception as e:
        print(f"Git harvest error: {e}")
    print(f"  -> Harvested {len(commits)} commits.")
    return commits

def harvest_ai_studio(ai_studio_dir):
    print(f"Harvesting Google AI Studio files from {ai_studio_dir}...")
    ai_studio_events = []
    if not os.path.exists(ai_studio_dir):
        print("  -> Directory not found, skipping.")
        return ai_studio_events

    for root, dirs, files in os.walk(ai_studio_dir):
        for file in files:
            path = Path(root) / file
            stat = path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            event = {
                "source": "google_ai_studio",
                "filename": file,
                "path": str(path),
                "mtime": mtime,
                "size_bytes": stat.st_size,
                "ext": path.suffix.lower(),
                "snippet": ""
            }
            
            # If text/json, read a snippet
            if path.suffix.lower() in ['.txt', '.json', '.md', '.prompt']:
                try:
                    content = path.read_text(encoding='utf-8', errors='replace')
                    event["snippet"] = content[:300].strip()
                    event["line_count"] = len(content.splitlines())
                except Exception:
                    pass
                    
            ai_studio_events.append(event)
            
    print(f"  -> Harvested {len(ai_studio_events)} AI Studio artifacts.")
    return ai_studio_events

def harvest_antigravity_transcripts(brain_dir, label="antigravity_brain"):
    print(f"Harvesting transcripts from {brain_dir} ({label})...")
    sessions = []
    if not os.path.exists(brain_dir):
        print("  -> Directory not found, skipping.")
        return sessions

    for item in os.listdir(brain_dir):
        session_path = Path(brain_dir) / item
        if not session_path.is_dir():
            continue
            
        transcript_path = session_path / ".system_generated" / "logs" / "transcript.jsonl"
        if not transcript_path.exists():
            # Check direct jsonl or flat
            candidates = list(session_path.glob("*.jsonl"))
            if candidates:
                transcript_path = candidates[0]
            else:
                continue

        stat = transcript_path.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        user_prompts = []
        tool_call_count = 0
        total_steps = 0
        
        try:
            with open(transcript_path, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    total_steps += 1
                    try:
                        step = json.loads(line)
                        if step.get("type") == "USER_INPUT" or step.get("source") == "USER_EXPLICIT":
                            content = step.get("content", "")
                            if content and len(content.strip()) > 5:
                                user_prompts.append(content[:200].strip())
                        if step.get("tool_calls"):
                            tool_call_count += len(step["tool_calls"])
                    except Exception:
                        pass
        except Exception as e:
            pass

        sessions.append({
            "source": label,
            "conversation_id": item,
            "mtime": mtime,
            "total_steps": total_steps,
            "tool_call_count": tool_call_count,
            "initial_prompt": user_prompts[0] if user_prompts else "N/A",
            "prompt_count": len(user_prompts)
        })

    print(f"  -> Harvested {len(sessions)} session transcripts.")
    return sessions

def harvest_markdown_chats(conv_history_dir):
    print(f"Harvesting markdown chat exports from {conv_history_dir}...")
    md_chats = []
    if not os.path.exists(conv_history_dir):
        return md_chats
        
    for file in os.listdir(conv_history_dir):
        if not file.endswith(".md"):
            continue
        path = Path(conv_history_dir) / file
        stat = path.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
            title = lines[0].strip("# ") if lines else file
            md_chats.append({
                "source": "markdown_chat_export",
                "filename": file,
                "title": title,
                "mtime": mtime,
                "line_count": len(lines),
                "snippet": content[:300].strip()
            })
        except Exception:
            pass
            
    print(f"  -> Harvested {len(md_chats)} markdown chat exports.")
    return md_chats

def main():
    project_root = r"c:\Users\augus\OneDrive\Documents\Google Antigravity\Projects\Typikon Coded"
    ai_studio_dir = r"C:\Users\augus\OneDrive\Documents\Google Antigravity\Projects\Pre-Update & AI Studio Chats\Google AI Studio"
    antigravity_1_dir = r"C:\Users\augus\OneDrive\Documents\Google Antigravity\Projects\Pre-Update & AI Studio Chats\Antigravity 1.0"
    conv_history_dir = r"C:\Users\augus\OneDrive\Documents\Google Antigravity\Projects\Pre-Update & AI Studio Chats\Conversation_History"
    modern_brain_dir = r"C:\Users\augus\.gemini\antigravity\brain"
    
    print("=== STARTING DETERMINISTIC BRUTE-FORCE HARVEST ===")
    
    git_commits = parse_git_history(project_root)
    ai_studio_files = harvest_ai_studio(ai_studio_dir)
    antigravity_1_sessions = harvest_antigravity_transcripts(antigravity_1_dir, label="antigravity_1.0")
    conv_history_md = harvest_markdown_chats(conv_history_dir)
    modern_sessions = harvest_antigravity_transcripts(modern_brain_dir, label="antigravity_2.0_modern")
    
    output_data = {
        "metadata": {
            "harvest_timestamp": datetime.now().isoformat(),
            "total_git_commits": len(git_commits),
            "total_ai_studio_files": len(ai_studio_files),
            "total_antigravity_1_sessions": len(antigravity_1_sessions),
            "total_markdown_chat_exports": len(conv_history_md),
            "total_modern_sessions": len(modern_sessions)
        },
        "git_commits": git_commits,
        "ai_studio_summary": {
            "count": len(ai_studio_files),
            "sample_files": [f["filename"] for f in ai_studio_files[:25]]
        },
        "sessions": {
            "antigravity_1": antigravity_1_sessions,
            "markdown_chat_exports": conv_history_md,
            "modern_brain": modern_sessions
        }
    }
    
    output_file = os.path.join(project_root, "chronicle_index.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        
    print(f"\n=== HARVEST COMPLETE: Saved to {output_file} ===")
    print(f"Summary:")
    print(f"  - Git Commits: {len(git_commits)}")
    print(f"  - AI Studio Files: {len(ai_studio_files)}")
    print(f"  - Antigravity 1.0 Sessions: {len(antigravity_1_sessions)}")
    print(f"  - Markdown Chat Exports: {len(conv_history_md)}")
    print(f"  - Modern Antigravity Sessions: {len(modern_sessions)}")


if __name__ == "__main__":
    main()
