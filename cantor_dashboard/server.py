import http.server
import socketserver
import urllib.parse
import json
import os
import sys
import threading
import time
import socket
from datetime import datetime, date

# Frontend file watching for live reload
FRONTEND_FILES = ["index.html", "style.css", "main.js"]
reload_event = threading.Event()

def watch_frontend_files():
    mtimes = {}
    for f in FRONTEND_FILES:
        filepath = os.path.join(CANTOR_DASHBOARD_DIR, f)
        if os.path.exists(filepath):
            mtimes[filepath] = os.path.getmtime(filepath)
            
    while True:
        time.sleep(0.5)
        changed = False
        for f in FRONTEND_FILES:
            filepath = os.path.join(CANTOR_DASHBOARD_DIR, f)
            if os.path.exists(filepath):
                try:
                    m = os.path.getmtime(filepath)
                    if filepath not in mtimes or mtimes[filepath] != m:
                        mtimes[filepath] = m
                        changed = True
                except Exception:
                    pass
        if changed:
            print("[Server Watcher] Frontend file changed. Triggering live-reload...")
            reload_event.set()
            time.sleep(1.0)
            reload_event.clear()


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
        elif path == "/api/roadmap":
            self.api_roadmap(query)
        elif path == "/api/lint":
            self.api_lint()
        elif path == "/api/live-reload":
            self.api_live_reload()
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

        paschalion = query.get("paschalion", ["gregorian"])[0]
        version = query.get("version", ["stamford_2014"])[0]
        temple_feast = query.get("temple_feast", [None])[0]
        digest_mode = query.get("digest_mode", ["full"])[0]

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            self.send_json_error("Invalid date format. Expected YYYY-MM-DD", 400)
            return

        temple_feast_date = None
        if temple_feast:
            try:
                parts = temple_feast.split("-")
                if len(parts) == 2:
                    temple_feast_date = (int(parts[0]), int(parts[1]))
            except ValueError:
                pass

        try:
            # Instantiate engine
            engine = RuthenianEngine(
                base_dir=REPO_DIR, 
                version=version,
                paschalion=paschalion,
                temple_feast_date=temple_feast_date
            )
            
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
            digest = engine.generate_typikon_digest(context, rubrics, mode=digest_mode)
            fasting = engine.resolve_fasting_rule(context)

            # Resolve daily ceremonial context
            vestment = engine.resolve_vestment_color(context, rubrics)
            is_sunday = context.get("day_of_week") == 0
            offset = context.get("pascha_offset")
            period = context.get("period", "normal")
            prostrations_forbidden = False
            prostrations_reason = "Allowed (Standard Weekday/Lenten bows)"
            if is_sunday:
                prostrations_forbidden = True
                prostrations_reason = "Forbidden on Sundays"
            elif offset is not None and 0 <= offset <= 49:
                prostrations_forbidden = True
                prostrations_reason = "Forbidden Pascha to Pentecost"
            elif period == "feast" or context.get("rank", 5) <= 2:
                prostrations_forbidden = True
                prostrations_reason = "Forbidden on Great Feasts"
                
            clergy_variant = engine.resolve_clergy_variant(context, service="liturgy")

            response = {
                "context": serializable_context,
                "fasting": fasting,
                "ceremonial": {
                    "vestment": vestment,
                    "prostrations": {
                        "forbidden": prostrations_forbidden,
                        "reason": prostrations_reason
                    },
                    "clergy_variant": clergy_variant
                },
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

    def api_roadmap(self, query):
        # Parse active parameters to resolve the feast timeline dynamically
        year_str = query.get("year", [None])[0]
        try:
            year = int(year_str) if year_str else datetime.now().year
        except ValueError:
            year = datetime.now().year

        paschalion = query.get("paschalion", ["gregorian"])[0]
        version = query.get("version", ["stamford_2014"])[0]
        temple_feast = query.get("temple_feast", [None])[0]

        temple_feast_date = None
        if temple_feast:
            try:
                parts = temple_feast.split("-")
                if len(parts) == 2:
                    temple_feast_date = (int(parts[0]), int(parts[1]))
            except ValueError:
                pass

        # Resolve days dynamically using the RuthenianEngine
        timeline_days = []
        try:
            # We resolve September 7 to September 12 dynamically for the given year
            # September 8 is the fixed date of the Nativity of the Theotokos
            for d_day in range(7, 13):
                target_date = date(year, 9, d_day)
                engine = RuthenianEngine(
                    base_dir=REPO_DIR,
                    version=version,
                    paschalion=paschalion,
                    temple_feast_date=temple_feast_date
                )
                context = engine.get_liturgical_context(target_date)
                rubrics = engine.resolve_rubrics(context)

                # Determine type
                if d_day == 7:
                    day_type = "forefeast"
                    lbl = "Sept 7"
                elif d_day == 8:
                    day_type = "feast"
                    lbl = "Sept 8"
                elif 9 <= d_day <= 11:
                    day_type = "afterfeast"
                    lbl = f"Sept {d_day}"
                else:
                    day_type = "apodosis"
                    lbl = "Sept 12"

                # Extract rank title
                rank_name = rubrics.get("title")
                if not rank_name:
                    rank_name = context.get("dolnytsky_title", f"September {d_day}")

                # Determine Tone
                tone_val = context.get("tone", 1)
                
                # Stichera descriptions
                fixed_stichera = "Troparion of the Feast (Tone 4); Kontakion (Tone 4)."
                if day_type == "forefeast":
                    fixed_stichera = "Troparion of the Forefeast (Tone 4): 'Today from the root of Jesse...'; Stichera of the Forefeast."
                elif day_type == "feast" or day_type == "apodosis":
                    fixed_stichera = "Troparion of the Feast (Tone 4): 'Your Nativity, O Virgin...'; Kontakion (Tone 4): 'Joachim and Anna...'"
                
                # Relative rules
                is_sunday = (target_date.weekday() + 1) % 7 == 0
                if is_sunday:
                    rel_rule = f"Sunday Octoechos merges with Feast in Tone {tone_val}. Resurrectional Stichera and Canons take precedence."
                else:
                    rel_rule = f"Weekday Octoechos canons suppressed or merged. Daily Prokeimenon for {target_date.strftime('%A')}."

                timeline_days.append({
                    "date": target_date.isoformat(),
                    "label": lbl,
                    "name": rank_name,
                    "type": day_type,
                    "rank": rubrics.get("variables", {}).get("rank_class", "Simple Class"),
                    "tone_override": f"Tone {tone_val}",
                    "fixed_text": fixed_stichera,
                    "relative_rule": rel_rule
                })
        except Exception as e:
            # Fallback to static if resolution fails
            print(f"Error in dynamic roadmap resolving: {e}")
            timeline_days = [{
                "date": f"{year}-09-08",
                "label": "Sept 8",
                "name": "NATIVITY OF THE MOST HOLY THEOTOKOS",
                "type": "feast",
                "rank": "Vigil Feast (Rank 1)",
                "tone_override": "Tone 4",
                "fixed_text": "Troparion of the Feast (Tone 4)",
                "relative_rule": "Special festal prokeimena."
            }]

        roadmap_data = {
            "status": "success",
            "wings": {
                "logic": 100,
                "structures": 95,
                "assets": 10,
                "docs": 100,
                "ui": 85
            },
            "matins_gates": [
                {"gate": 1, "name": "Six Psalms (Hexapsalmos)", "status": "completed"},
                {"gate": 2, "name": "Great Litany & God is the Lord", "status": "completed"},
                {"gate": 3, "name": "Kathismata Readings", "status": "completed"},
                {"gate": 4, "name": "Sessional Hymns (Kathismata)", "status": "completed"},
                {"gate": 5, "name": "Polyeleos or Megalynarion", "status": "completed"},
                {"gate": 6, "name": "Gradual Hymns (Anabathmoi)", "status": "completed"},
                {"gate": 7, "name": "Matins Gospel", "status": "completed"},
                {"gate": 8, "name": "Psalm 50 & Stichera", "status": "completed"},
                {"gate": 9, "name": "The Canon (Odes 1-9)", "status": "completed"},
                {"gate": 10, "name": "Exaposteilarion", "status": "completed"},
                {"gate": 11, "name": "Lauds (Praises) & Doxology", "status": "completed"},
                {"gate": 12, "name": "Matins Litanies", "status": "completed"},
                {"gate": 13, "name": "Matins Dismissal & Litany", "status": "stubbed"}
            ],
            "variant_matrix": {
                "daily_vespers": "completed",
                "great_vespers_vigil": "completed",
                "daily_matins": "completed",
                "festal_matins": "completed",
                "first_hour": "completed",
                "third_six_nine_hours": "completed",
                "divine_liturgy": "completed",
                "presanctified_liturgy": "stubbed",
                "vesperal_liturgy": "stubbed",
                "great_compline": "missing",
                "midnight_office": "completed"
            },
            "unresolved_gaps": [
                "Lviv recension assets stubbed for Great Lent",
                "Typikon collision resolution rules missing for dual feast overlaps",
                "Menaion translations incomplete for the month of October"
            ],
            "feast_cycles": {
                "nativity_theotokos": {
                    "feast_name": "Nativity of the Most Holy Theotokos",
                    "double_border_date": f"{year}-09-08",
                    "days": timeline_days
                }
            }
        }
        self.send_json_response(roadmap_data)

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

    def api_live_reload(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        
        try:
            self.wfile.write(b": ping\n\n")
            self.wfile.flush()
            
            while True:
                event_set = reload_event.wait(timeout=5.0)
                if event_set:
                    self.wfile.write(b"data: reload\n\n")
                    self.wfile.flush()
                    break
                else:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
        except (socket.error, ConnectionResetError, BrokenPipeError):
            pass
        except Exception as e:
            print(f"Error in live-reload SSE: {e}")

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
    
    # Start frontend file watcher thread
    watcher_thread = threading.Thread(target=watch_frontend_files, daemon=True)
    watcher_thread.start()
    
    # Create handler
    handler_class = CantorDashboardHandler
    
    server_address = ('', PORT)
    # Enable socket re-use to avoid port-binding issues on restarts
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    
    print(f"\n=======================================================")
    print(f"Starting Cantor Dashboard Server...")
    print(f"Server is running locally at: http://localhost:{PORT}")
    print(f"Press Ctrl+C in terminal to stop.")
    print(f"=======================================================\n")
    
    try:
        with socketserver.ThreadingTCPServer(server_address, handler_class) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    run()
