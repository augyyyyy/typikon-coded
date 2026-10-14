import os
import sys
import time
import subprocess

# Set directories to watch
CANTOR_DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(CANTOR_DASHBOARD_DIR)
WATCH_DIRS = [
    CANTOR_DASHBOARD_DIR,
    REPO_DIR
]

def get_mtimes():
    """Gets mtimes of all Python files in watched directories."""
    mtimes = {}
    for d in WATCH_DIRS:
        if not os.path.exists(d):
            continue
        for root, dirs, files in os.walk(d):
            # Prune directories in-place to prevent walking into virtual envs and git metadata
            dirs[:] = [d for d in dirs if d not in (".venv", ".git", ".pytest_cache", ".idea", "__pycache__")]
            for file in files:
                if file.endswith(".py") and file != "watch_server.py":
                    filepath = os.path.join(root, file)
                    try:
                        mtimes[filepath] = os.path.getmtime(filepath)
                    except Exception:
                        pass
    return mtimes

def main():
    print("=======================================================")
    print("Starting Server Watcher (Auto-Restart on Python Changes)...")
    print(f"Watching directories:\n  - {WATCH_DIRS[0]}\n  - {WATCH_DIRS[1]}")
    print("=======================================================\n")
    
    server_script = os.path.join(CANTOR_DASHBOARD_DIR, "server.py")
    
    # Initial state
    last_mtimes = get_mtimes()
    
    process = None
    try:
        # Start server process
        process = subprocess.Popen([sys.executable, "-u", server_script], cwd=CANTOR_DASHBOARD_DIR)
        
        while True:
            time.sleep(0.5)
            
            # Check if subprocess died unexpectedly
            ret = process.poll()
            if ret is not None:
                print(f"\n[Watcher] Server exited unexpectedly with code {ret}. Restarting in 2s...")
                time.sleep(2)
                process = subprocess.Popen([sys.executable, "-u", server_script], cwd=CANTOR_DASHBOARD_DIR)
                last_mtimes = get_mtimes()
                continue
                
            # Scan for changes
            current_mtimes = get_mtimes()
            
            # Check for changes, additions, or deletions
            changed = False
            if len(current_mtimes) != len(last_mtimes):
                changed = True
            else:
                for filepath, mtime in current_mtimes.items():
                    if filepath not in last_mtimes or last_mtimes[filepath] != mtime:
                        print(f"\n[Watcher] Detected change in: {os.path.basename(filepath)}")
                        changed = True
                        break
            
            if changed:
                print("[Watcher] Restarting server...")
                # Kill old process
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                
                # Start new process
                process = subprocess.Popen([sys.executable, "-u", server_script], cwd=CANTOR_DASHBOARD_DIR)
                last_mtimes = current_mtimes
                
    except KeyboardInterrupt:
        print("\n[Watcher] Shutting down watcher and server...")
        if process:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
            print("[Watcher] Cleaned up server process.")
    except Exception as e:
        print(f"\n[Watcher] Fatal error in watcher: {e}")
        if process:
            process.terminate()

if __name__ == "__main__":
    main()
