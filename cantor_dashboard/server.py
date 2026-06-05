import http.server
import socketserver
import urllib.parse
import json
import os
import sys
from datetime import datetime, date

# Resolve paths
CANTOR_DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(CANTOR_DASHBOARD_DIR)
sys.path.insert(0, REPO_DIR)

# Import the engine
try:
    from ruthenian_engine import RuthenianEngine
except ImportError:
    # If not in path, try adding REPO_DIR/engine
    sys.path.insert(0, os.path.join(REPO_DIR, "engine"))
    from ruthenian_engine import RuthenianEngine

PORT = 8080

# Cache databases for quick key lookup
standardized_db = {}
backup_db = {}
key_to_file = {}

def load_databases():
    print("Pre-loading Stamford databases...")
    stamford_dir = os.path.join(REPO_DIR, "json_db", "stamford")
    backup_dir = os.path.join(REPO_DIR, "json_db", "stamford_backup")
    
    # Load standardized
    if os.path.exists(stamford_dir):
        for fname in os.listdir(stamford_dir):
            if fname.endswith(".json") and not fname.endswith(".bak"):
                filepath = os.path.join(stamford_dir, fname)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            for k, v in data.items():
                                standardized_db[k] = v
                                key_to_file[k] = fname
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")
                    
    # Load backups
    if os.path.exists(backup_dir):
        for fname in os.listdir(backup_dir):
            if fname.endswith(".json"):
                filepath = os.path.join(backup_dir, fname)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            for k, v in data.items():
                                backup_db[k] = v
                except Exception as e:
                    print(f"Error loading backup {filepath}: {e}")
                    
    print(f"Loaded {len(standardized_db)} standardized keys, {len(backup_db)} backup keys.")

def normalize_text_val(val):
    if val is None:
        return None
    if isinstance(val, dict):
        return {
            "content": val.get("content", ""),
            "title": val.get("title", ""),
            "verse": val.get("verse", ""),
            "source": val.get("source", ""),
            "_rubrics": val.get("_rubrics", [])
        }
    elif isinstance(val, str):
        return {
            "content": val,
            "title": "",
            "verse": "",
            "source": "",
            "_rubrics": []
        }
    return None

class CantorDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "OK")
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # Route API requests
        if path.startswith("/api/"):
            self.handle_api(path, query)
        else:
            # Serve static files from cantor_dashboard directory
            # Default to index.html
            local_path = path.lstrip("/")
            if not local_path or local_path == "index.html":
                filepath = os.path.join(CANTOR_DASHBOARD_DIR, "index.html")
                content_type = "text/html"
            elif local_path == "style.css":
                filepath = os.path.join(CANTOR_DASHBOARD_DIR, "style.css")
                content_type = "text/css"
            elif local_path == "main.js":
                filepath = os.path.join(CANTOR_DASHBOARD_DIR, "main.js")
                content_type = "application/javascript"
            else:
                # Fallback to default handler (will look in cwd)
                # But we want to enforce cantor_dashboard folder
                filepath = os.path.join(CANTOR_DASHBOARD_DIR, local_path)
                if not os.path.exists(filepath):
                    self.send_error(404, "File not found")
                    return
                # Determine content type
                if filepath.endswith(".html"): content_type = "text/html"
                elif filepath.endswith(".css"): content_type = "text/css"
                elif filepath.endswith(".js"): content_type = "application/javascript"
                elif filepath.endswith(".json"): content_type = "application/json"
                elif filepath.endswith(".png"): content_type = "image/png"
                elif filepath.endswith(".jpg") or filepath.endswith(".jpeg"): content_type = "image/jpeg"
                else: content_type = "text/plain"

            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(os.path.getsize(filepath)))
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, f"File not found: {path}")

    def handle_api(self, path, query):
        if path == "/api/books":
            self.api_books()
        elif path == "/api/text":
            self.api_text(query)
        elif path == "/api/resolve":
            self.api_resolve(query)
        elif path == "/api/lint":
            self.api_lint()
        else:
            self.send_json_error("Endpoint not found", 404)

    def api_books(self):
        stamford_dir = os.path.join(REPO_DIR, "json_db", "stamford")
        books_data = []
        if os.path.exists(stamford_dir):
            for fname in sorted(os.listdir(stamford_dir)):
                if fname.endswith(".json") and not fname.endswith(".bak"):
                    filepath = os.path.join(stamford_dir, fname)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        keys_list = []
                        if isinstance(data, dict):
                            for k, v in sorted(data.items()):
                                content = ""
                                title = ""
                                if isinstance(v, dict):
                                    content = v.get("content", "")
                                    title = v.get("title", "")
                                elif isinstance(v, str):
                                    content = v
                                preview = content[:100] + "..." if len(content) > 100 else content
                                keys_list.append({
                                    "key": k,
                                    "title": title or k.split(".")[-1].replace("_", " ").title(),
                                    "preview": preview
                                })
                        books_data.append({
                            "filename": fname,
                            "name": fname.replace("text_", "").replace(".json", "").replace("_", " ").title(),
                            "key_count": len(keys_list),
                            "keys": keys_list
                        })
                    except Exception as e:
                        print(f"Error reading file for books listing: {fname} - {e}")
        self.send_json_response(books_data)

    def api_text(self, query):
        key = query.get("key", [None])[0]
        if not key:
            self.send_json_error("Missing required parameter 'key'", 400)
            return

        std_val = standardized_db.get(key)
        orig_val = backup_db.get(key)

        if std_val is None:
            self.send_json_error(f"Key not found: {key}", 404)
            return

        filename = key_to_file.get(key, "unknown")
        
        response = {
            "key": key,
            "filename": filename,
            "original": normalize_text_val(orig_val if orig_val is not None else std_val),
            "standardized": normalize_text_val(std_val)
        }
        self.send_json_response(response)


    def api_resolve(self, query):
        date_str = query.get("date", [None])[0]
        if not date_str:
            date_str = date.today().isoformat()

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            self.send_json_error("Invalid date format. Expected YYYY-MM-DD", 400)
            return

        try:
            # Instantiate engine
            engine = RuthenianEngine(base_dir=REPO_DIR, version="stamford")
            
            # Resolve
            context = engine.get_liturgical_context(target_date)
            
            # Make context JSON serializable
            serializable_context = {}
            for k, v in context.items():
                if isinstance(v, (date, datetime)):
                    serializable_context[k] = v.isoformat()
                elif isinstance(v, list):
                    new_list = []
                    for item in v:
                        if isinstance(item, dict):
                            new_item = {}
                            for ik, iv in item.items():
                                if isinstance(iv, (date, datetime)):
                                    new_item[ik] = iv.isoformat()
                                else:
                                    new_item[ik] = iv
                            new_list.append(new_item)
                        else:
                            new_list.append(item)
                    serializable_context[k] = new_list
                else:
                    serializable_context[k] = v

            rubrics = engine.resolve_rubrics(context)
            booklet = engine.generate_full_booklet(context, rubrics)
            digest = engine.generate_typikon_digest(context, rubrics)

            response = {
                "context": serializable_context,
                "rubrics": {
                    "title": rubrics.get("title", ""),
                    "variables": rubrics.get("variables", {}),
                    "overrides": rubrics.get("overrides", {}),
                    "trace": rubrics.get("_trace", [])
                },
                "booklet": booklet,
                "digest": digest
            }
            self.send_json_response(response)

        except Exception as e:
            import traceback
            response = {
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            self.send_json_response(response, 500)

    def api_lint(self):
        report_path = os.path.join(REPO_DIR, "audit_results", "stamford_lint_report.json")
        if os.path.exists(report_path):
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    report = json.load(f)
                self.send_json_response(report)
                return
            except Exception as e:
                print(f"Error loading lint report: {e}")

        # Trigger linter dynamically if missing
        try:
            # Add scripts to path
            sys.path.insert(0, os.path.join(REPO_DIR, "scripts"))
            from lint_liturgical_db import run_linter
            run_linter()
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
            self.send_json_response(report)
        except Exception as e:
            self.send_json_error(f"Linter execution failed: {e}", 500)

    def send_json_response(self, data, status_code=200):
        try:
            json_bytes = json.dumps(data, indent=2).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(json_bytes)))
            self.end_headers()
            self.wfile.write(json_bytes)
        except Exception as e:
            print(f"Error sending JSON response: {e}")

    def send_json_error(self, message, status_code=500):
        self.send_json_response({"error": message}, status_code)

def run():
    load_databases()
    # Create handler
    handler_class = CantorDashboardHandler
    
    server_address = ('', PORT)
    # Enable socket re-use to avoid port-binding issues on restarts
    socketserver.TCPServer.allow_reuse_address = True
    
    print(f"\n=======================================================")
    print(f"Starting Cantor Dashboard Server...")
    print(f"Server is running locally at: http://localhost:{PORT}")
    print(f"Press Ctrl+C in terminal to stop.")
    print(f"=======================================================\n")
    
    try:
        with socketserver.TCPServer(server_address, handler_class) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    run()
