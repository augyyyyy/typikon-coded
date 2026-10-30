import glob
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


# Resolve paths dynamically
CANTOR_DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
curr = CANTOR_DASHBOARD_DIR
REPO_DIR = curr
for _ in range(5):
    if os.path.exists(os.path.join(curr, "engine")) and os.path.exists(os.path.join(curr, ".agents")):
        REPO_DIR = curr
        break
    curr = os.path.dirname(curr)

if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

# Import the engine
try:
    from engine import RuthenianEngine
except ImportError:
    from engine.core import RuthenianEngine

PORT = int(os.environ.get("PORT", 8080))

# Cache databases for quick key lookup
standardized_db = {}
backup_db = {}
key_to_file = {}
repertoires_db = {}


def _extract_nested_preview(node):
    """Extract a readable text preview and synthesized content from a 3-level nested Triodion dict."""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        for item in node:
            if isinstance(item, str) and item.strip():
                return item.strip()
        return ""
    if isinstance(node, dict):
        if "content" in node and isinstance(node["content"], str):
            return node["content"]
        for _, child in node.items():
            res = _extract_nested_preview(child)
            if res:
                return res
    return ""


def _flatten_nested_triodion_day(day_key, day_dict):
    """Flatten a nested Triodion day dictionary into a structured text view for the Database Inspector."""
    sections = []
    for service_key, slots in day_dict.items():
        if not isinstance(slots, dict):
            continue
        sections.append(f"=== {service_key.replace('_', ' ').upper()} ===")
        for slot_key, paragraphs in slots.items():
            sections.append(f"\n[{slot_key.replace('_', ' ').title()}]")
            if isinstance(paragraphs, list):
                for p in paragraphs:
                    if isinstance(p, str) and p.strip():
                        sections.append(p.strip())
    return {
        "content": "\n".join(sections) if sections else "(Empty Triodion Day Entry)",
        "title": day_key.replace("_", " ").title(),
        "verse": "",
        "source": "Stamford Divine Office (Nested Triodion)",
        "_rubrics": [],
    }


def ensure_repertoires_loaded():
    """Ensure WO_01..WO_05 seasonal chant repertoire databases are loaded into memory."""
    if repertoires_db:
        return repertoires_db
    repertoires_dir = os.path.join(REPO_DIR, "Data", "databases", "repertoires")
    if os.path.exists(repertoires_dir):
        pattern = os.path.join(repertoires_dir, "WO_0*.json")
        for filepath in sorted(glob.glob(pattern)):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cycle_id = data.get("cycle_id")
                if cycle_id:
                    repertoires_db[cycle_id] = data
            except Exception as e:
                print(f"Error loading repertoire {filepath}: {e}")
    return repertoires_db


def load_databases():
    print("Pre-loading Royal Doors (standardized), Stamford (baseline), and Seasonal Repertoire databases...")
    royal_doors_dir = os.path.join(
        REPO_DIR, "Data", "Service Books", "Recensions", "Royal Doors", "JSON", "assets"
    )
    stamford_dir = os.path.join(
        REPO_DIR, "Data", "Service Books", "Recensions", "Stamford Divine Office", "JSON", "assets"
    )

    if os.path.exists(royal_doors_dir):
        for fname in sorted(os.listdir(royal_doors_dir)):
            if (fname.startswith("text_") or fname == "liturgikon_ordinaries.json") and fname.endswith(".json"):
                filepath = os.path.join(royal_doors_dir, fname)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            for k, v in data.items():
                                if k == "file_metadata":
                                    continue
                                standardized_db[k] = v
                                key_to_file[k] = "text_liturgikon.json" if fname == "liturgikon_ordinaries.json" else fname
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")

    if os.path.exists(stamford_dir):
        for fname in sorted(os.listdir(stamford_dir)):
            if fname.startswith("text_") and fname.endswith(".json"):
                filepath = os.path.join(stamford_dir, fname)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            for k, v in data.items():
                                if k == "file_metadata":
                                    continue
                                backup_db[k] = v
                                if k not in standardized_db:
                                    standardized_db[k] = v
                                    key_to_file[k] = fname
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")

    ensure_repertoires_loaded()
    total_repertoire_items = sum(c.get("total_canonical_items", 0) for c in repertoires_db.values())
    print(
        f"Loaded {len(standardized_db)} Royal Doors standardized keys, {len(backup_db)} Stamford baseline keys, and "
        f"{len(repertoires_db)} seasonal chant cycles ({total_repertoire_items} canonical items)."
    )


def normalize_text_val(val, key=""):
    if val is None:
        return None
    if isinstance(val, dict):
        if "content" not in val and any(isinstance(v, dict) for v in val.values()):
            return _flatten_nested_triodion_day(key, val)
        raw_content = val.get("content", "")
        if isinstance(raw_content, dict):
            if "text" in raw_content:
                inner = raw_content["text"]
                raw_content = (inner.get("en") or next(iter(inner.values()), "")) if isinstance(inner, dict) else str(inner)
            else:
                raw_content = raw_content.get("en") or next(iter(raw_content.values()), "")
        return {
            "content": str(raw_content or ""),
            "title": val.get("title", ""),
            "verse": val.get("verse", ""),
            "source": val.get("source", ""),
            "_rubrics": val.get("_rubrics", []),
        }
    elif isinstance(val, str):
        return {
            "content": val,
            "title": "",
            "verse": "",
            "source": "",
            "_rubrics": [],
        }
    return None


def resolve_seasonal_repertoire(target_date, context):
    """Deterministically resolve the active WO-01..WO-05 seasonal chant repertoire for a liturgical date.

    Maps pascha_offset, fixed calendar dates (MM-DD), and Octoechos tone (1..8) to:
    - Primary seasonal cycle (WO-01..WO-05)
    - Active phase(s) within that cycle
    - Concurrent fixed Marian/Theotokos feast overlays (e.g., Annunciation during Great Lent)
    - Matching Tone's Dogmatic Theotokion from WO-05 Phase 6 (WO-05.23..WO-05.30)
    """
    ensure_repertoires_loaded()
    if not repertoires_db:
        return None

    pascha_offset = context.get("pascha_offset")
    tone = context.get("tone")
    month = target_date.month
    day = target_date.day
    weekday = target_date.weekday()  # Monday=0 .. Sunday=6

    # List of (cycle_id, phase_num) pairs active on this date
    selected_cycle_phases = []
    primary_cycle_id = "WO-05"

    if isinstance(pascha_offset, int) and -8 <= pascha_offset <= -1:
        primary_cycle_id = "WO-03"
        if pascha_offset in (-8, -7):
            selected_cycle_phases.append(("WO-03", 1))
        elif pascha_offset in (-6, -5, -4):
            selected_cycle_phases.append(("WO-03", 2))
        elif pascha_offset == -3:
            selected_cycle_phases.append(("WO-03", 3))
        elif pascha_offset == -2:
            selected_cycle_phases.extend([("WO-03", 4), ("WO-03", 5)])
        elif pascha_offset == -1:
            selected_cycle_phases.extend([("WO-03", 5), ("WO-03", 6)])
    elif isinstance(pascha_offset, int) and 0 <= pascha_offset <= 56:
        primary_cycle_id = "WO-04"
        if pascha_offset == 0:
            selected_cycle_phases.extend([("WO-04", 1), ("WO-04", 2), ("WO-04", 3)])
        elif 1 <= pascha_offset <= 6:
            selected_cycle_phases.extend([("WO-04", 2), ("WO-04", 3)])
        elif 7 <= pascha_offset <= 38:
            selected_cycle_phases.append(("WO-04", 4))
        elif 39 <= pascha_offset <= 47:
            selected_cycle_phases.append(("WO-04", 5))
        else:
            selected_cycle_phases.append(("WO-04", 6))
    elif isinstance(pascha_offset, int) and -70 <= pascha_offset <= -9:
        primary_cycle_id = "WO-02"
        if -70 <= pascha_offset <= -49:
            selected_cycle_phases.append(("WO-02", 1))
        else:
            if -48 <= pascha_offset <= -43:
                selected_cycle_phases.append(("WO-02", 2))
            if weekday in (2, 4):
                selected_cycle_phases.append(("WO-02", 3))
            elif weekday == 6:
                selected_cycle_phases.extend([("WO-02", 4), ("WO-02", 5), ("WO-02", 6)])
            else:
                if ("WO-02", 2) not in selected_cycle_phases:
                    selected_cycle_phases.append(("WO-02", 3))
            if pascha_offset == -15:
                # Akathist Saturday
                selected_cycle_phases.append(("WO-05", 1))
    elif (month == 11 and day >= 15) or month == 12 or (month == 1 and day <= 14):
        primary_cycle_id = "WO-01"
        if month == 11 and 15 <= day <= 24:
            selected_cycle_phases.append(("WO-01", 1))
        elif (month == 11 and day >= 25) or (month == 12 and day <= 23):
            selected_cycle_phases.append(("WO-01", 2))
        elif month == 12 and day == 24:
            selected_cycle_phases.extend([("WO-01", 3), ("WO-01", 4)])
        elif month == 12 and day >= 25:
            selected_cycle_phases.append(("WO-01", 5))
        else:
            selected_cycle_phases.append(("WO-01", 6))
    else:
        primary_cycle_id = "WO-05"
        if month == 3 and 20 <= day <= 31:
            selected_cycle_phases.append(("WO-05", 1))
        elif month in (6, 7) or (month == 8 and 1 <= day <= 13):
            selected_cycle_phases.append(("WO-05", 2))
        elif month == 8 and 14 <= day <= 31:
            selected_cycle_phases.append(("WO-05", 3))
        elif month == 9:
            selected_cycle_phases.append(("WO-05", 4))
        elif month == 10 or (month == 11 and 1 <= day <= 14):
            selected_cycle_phases.append(("WO-05", 5))
        else:
            selected_cycle_phases.append(("WO-05", 6))

    # Concurrent Annunciation overlay if March 24-26 falls inside Great Lent / Holy Week
    if month == 3 and 24 <= day <= 26 and ("WO-05", 1) not in selected_cycle_phases:
        selected_cycle_phases.append(("WO-05", 1))

    primary_cycle = repertoires_db.get(primary_cycle_id, {})
    active_items = []
    seen_ids = set()
    active_phases = []
    seen_phases = set()

    for cid, phase_num in selected_cycle_phases:
        cycle_obj = repertoires_db.get(cid, {})
        for item in cycle_obj.get("items", []):
            if item.get("phase") == phase_num:
                phase_key = (cid, phase_num)
                if phase_key not in seen_phases:
                    seen_phases.add(phase_key)
                    active_phases.append({
                        "cycle_id": cid,
                        "phase": phase_num,
                        "phase_name": item.get("phase_name", f"Phase {phase_num}"),
                    })
                item_id = item.get("id")
                if item_id not in seen_ids:
                    seen_ids.add(item_id)
                    active_items.append(item)

    # Resolve Tone's Dogmatic Theotokion from WO-05 Phase 6 (WO-05.23 .. WO-05.30)
    dogmatikon_of_the_tone = None
    if isinstance(tone, int) and 1 <= tone <= 8:
        target_tone_str = f"Tone {tone}"
        wo05_items = repertoires_db.get("WO-05", {}).get("items", [])
        for item in wo05_items:
            if item.get("phase") == 6 and item.get("tone") == target_tone_str:
                dogmatikon_of_the_tone = item
                if item.get("id") not in seen_ids:
                    seen_ids.add(item.get("id"))
                    active_items.append(item)
                break

    return {
        "cycle_id": primary_cycle_id,
        "cycle_name": primary_cycle.get("cycle_name", primary_cycle_id),
        "primary_phase": active_phases[0]["phase"] if active_phases else 1,
        "primary_phase_name": active_phases[0]["phase_name"] if active_phases else "",
        "active_phases": active_phases,
        "tone": tone,
        "dogmatikon_of_the_tone": dogmatikon_of_the_tone,
        "appointed_items_count": len(active_items),
        "items": active_items,
    }


class CantorDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "OK")
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # Health check endpoint for cloud providers
        if path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
            return

        # Route API requests
        if path.startswith("/api/"):
            self.handle_api(path, query)
        else:
            # Serve static files from cantor_dashboard directory
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
                filepath = os.path.join(CANTOR_DASHBOARD_DIR, local_path)
                if not os.path.exists(filepath):
                    self.send_error(404, "File not found")
                    return
                if filepath.endswith(".html"):
                    content_type = "text/html"
                elif filepath.endswith(".css"):
                    content_type = "text/css"
                elif filepath.endswith(".js"):
                    content_type = "application/javascript"
                elif filepath.endswith(".json"):
                    content_type = "application/json"
                elif filepath.endswith(".png"):
                    content_type = "image/png"
                elif filepath.endswith(".jpg") or filepath.endswith(".jpeg"):
                    content_type = "image/jpeg"
                else:
                    content_type = "text/plain"

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
        elif path == "/api/repertoires":
            self.api_repertoires(query)
        elif path == "/api/roadmap":
            self.api_roadmap(query)
        elif path == "/api/lint":
            self.api_lint()
        elif path == "/api/live-reload":
            self.api_live_reload()
        elif path == "/api/annual_patterns":
            self.api_annual_patterns(query)
        elif path == "/api/musicology_catalogs":
            self.api_musicology_catalogs(query)
        else:
            self.send_json_error("Endpoint not found", 404)

    def api_books(self):
        royal_doors_dir = os.path.join(
            REPO_DIR, "Data", "Service Books", "Recensions", "Royal Doors", "JSON", "assets"
        )
        stamford_dir = os.path.join(
            REPO_DIR, "Data", "Service Books", "Recensions", "Stamford Divine Office", "JSON", "assets"
        )
        target_dir = royal_doors_dir if os.path.exists(royal_doors_dir) else stamford_dir
        books_data = []
        if os.path.exists(target_dir):
            for fname in sorted(os.listdir(target_dir)):
                if fname.startswith("text_") and fname.endswith(".json"):
                    filepath = os.path.join(target_dir, fname)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        if fname == "text_liturgikon.json":
                            ord_path = os.path.join(target_dir, "liturgikon_ordinaries.json")
                            if os.path.exists(ord_path):
                                with open(ord_path, "r", encoding="utf-8") as of:
                                    ord_data = json.load(of)
                                if isinstance(data, dict) and isinstance(ord_data, dict):
                                    merged = dict(data)
                                    merged.update(ord_data)
                                    data = merged
                        keys_list = []
                        if isinstance(data, dict):
                            for k, v in sorted(data.items()):
                                if k == "file_metadata":
                                    continue
                                content = ""
                                title = ""
                                if isinstance(v, dict):
                                    content = v.get("content", "")
                                    if isinstance(content, dict):
                                        if "text" in content:
                                            inner = content["text"]
                                            content = (inner.get("en") or next(iter(inner.values()), "")) if isinstance(inner, dict) else str(inner)
                                        else:
                                            content = content.get("en") or next(iter(content.values()), "")
                                    title = v.get("title", "")
                                    if not content:
                                        content = _extract_nested_preview(v)
                                elif isinstance(v, str):
                                    content = v
                                content = str(content or "")
                                preview = content[:100] + "..." if len(content) > 100 else content
                                keys_list.append({
                                    "key": k,
                                    "title": title or k.split(".")[-1].replace("_", " ").title(),
                                    "preview": preview,
                                })
                        books_data.append({
                            "filename": fname,
                            "name": fname.replace("text_", "").replace(".json", "").replace("_", " ").title(),
                            "key_count": len(keys_list),
                            "keys": keys_list,
                        })
                    except Exception as e:
                        print(f"Error reading file for books listing: {fname} - {e}")
        self.send_json_response(books_data)

    def api_text(self, query):
        key = query.get("key", [None])[0]
        if not key:
            self.send_json_error("Missing required parameter 'key'", 400)
            return

        if not standardized_db:
            load_databases()

        std_val = standardized_db.get(key)
        orig_val = backup_db.get(key)

        if std_val is None:
            self.send_json_error(f"Key not found: {key}", 404)
            return

        filename = key_to_file.get(key, "unknown")

        response = {
            "key": key,
            "filename": filename,
            "original": normalize_text_val(orig_val if orig_val is not None else std_val, key=key),
            "standardized": normalize_text_val(std_val, key=key),
        }
        self.send_json_response(response)

    def api_repertoires(self, query):
        """Expose the WO-01..WO-05 seasonal chant repertoires (140 canonical items across 30 phases)."""
        ensure_repertoires_loaded()

        cycle_filter = query.get("cycle", [None])[0]
        phase_str = query.get("phase", [None])[0]
        genre_filter = query.get("genre", [None])[0]
        date_str = query.get("date", [None])[0]

        phase_filter = None
        if phase_str is not None and phase_str != "":
            try:
                phase_filter = int(phase_str)
            except ValueError:
                self.send_json_error("Invalid 'phase' parameter. Expected integer 1..6.", 400)
                return

        cycles_payload = []
        for cid in sorted(repertoires_db.keys()):
            if cycle_filter and cid.upper() != cycle_filter.upper():
                continue
            raw_cycle = repertoires_db[cid]
            items = raw_cycle.get("items", [])

            # Build phase summaries for this cycle
            phase_map = {}
            for item in items:
                p_num = item.get("phase")
                if p_num not in phase_map:
                    phase_map[p_num] = {
                        "phase": p_num,
                        "phase_name": item.get("phase_name", f"Phase {p_num}"),
                        "item_count": 0,
                    }
                phase_map[p_num]["item_count"] += 1

            filtered_items = items
            if phase_filter is not None:
                filtered_items = [i for i in filtered_items if i.get("phase") == phase_filter]
            if genre_filter:
                q_low = genre_filter.lower()
                filtered_items = [
                    i
                    for i in filtered_items
                    if q_low in (i.get("genre") or "").lower()
                    or q_low in (i.get("title_en") or "").lower()
                    or q_low in (i.get("title_cyr") or "").lower()
                    or q_low in (i.get("tone") or "").lower()
                    or q_low in (i.get("station") or "").lower()
                ]

            cycles_payload.append({
                "cycle_id": cid,
                "cycle_name": raw_cycle.get("cycle_name", cid),
                "schema_version": raw_cycle.get("schema_version", ""),
                "total_canonical_items": raw_cycle.get("total_canonical_items", len(items)),
                "phases_count": raw_cycle.get("phases_count", len(phase_map)),
                "phases": [phase_map[k] for k in sorted(phase_map.keys())],
                "typikon_authorities": raw_cycle.get("typikon_authorities", []),
                "manuscript_codices": raw_cycle.get("manuscript_codices", []),
                "provenance_status": raw_cycle.get("provenance_status", "VERIFIED_PRIMARY_SOURCE"),
                "filtered_items_count": len(filtered_items),
                "items": filtered_items,
            })

        resolved_for_date = None
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                engine = RuthenianEngine(base_dir=REPO_DIR)
                context = engine.get_liturgical_context(target_date)
                resolved_for_date = resolve_seasonal_repertoire(target_date, context)
            except ValueError:
                self.send_json_error("Invalid date format. Expected YYYY-MM-DD", 400)
                return

        response = {
            "total_cycles": len(repertoires_db),
            "total_canonical_items": sum(c.get("total_canonical_items", 0) for c in repertoires_db.values()),
            "total_phases": sum(c.get("phases_count", 0) for c in repertoires_db.values()),
            "cycles": cycles_payload,
            "resolved_for_date": resolved_for_date,
        }
        self.send_json_response(response)

    def api_resolve(self, query):
        date_str = query.get("date", [None])[0]
        if not date_str:
            date_str = date.today().isoformat()

        paschalion = query.get("paschalion", ["gregorian"])[0]
        version = query.get("version", ["stamford_2014"])[0]
        ordinaries_recension = query.get("ordinaries_recension", [None])[0]
        propers_recension = query.get("propers_recension", [None])[0]
        strict_corpus_val = query.get("strict_corpus_mode", ["false"])[0]
        strict_corpus_mode = str(strict_corpus_val).lower() in ("true", "1", "yes")
        booklet_only_val = query.get("booklet_only", ["false"])[0]
        booklet_only = str(booklet_only_val).lower() in ("true", "1", "yes")

        calendar_source = query.get("calendar_source", [None])[0]
        temple_feast = query.get("temple_feast", [None])[0]
        temple_patron = query.get("temple_patron", [None])[0]
        temple_type = query.get("temple_type", ["saint"])[0]
        parish_profile_json = query.get("parish_profile", [None])[0]
        parish_profile = None
        if parish_profile_json:
            try:
                parish_profile = json.loads(parish_profile_json)
            except Exception:
                parish_profile = None

        digest_mode = query.get("digest_mode", ["full"])[0]
        include_ceremonial_val = query.get("include_ceremonial", ["false"])[0]
        include_ceremonial = include_ceremonial_val.lower() == "true"

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

        if parish_profile and isinstance(parish_profile, dict):
            t_info = parish_profile.get("temple", {})
            if t_info.get("name"):
                temple_patron = t_info["name"]
            if t_info.get("type"):
                temple_type = t_info["type"]
            if t_info.get("feast_month") and t_info.get("feast_day"):
                try:
                    temple_feast_date = (int(t_info["feast_month"]), int(t_info["feast_day"]))
                except (ValueError, TypeError):
                    pass

        try:
            # O(1) Cached Engine Instance + Per-Request Single-Resolver Memoization
            cache_map = getattr(self.__class__, "_engine_cache", None)
            if cache_map is None:
                cache_map = {}
                setattr(self.__class__, "_engine_cache", cache_map)
            engine_key = (
                version,
                ordinaries_recension or "",
                propers_recension or "",
                strict_corpus_mode,
                paschalion,
                calendar_source,
            )
            engine = cache_map.get(engine_key)
            if engine is None:
                engine = RuthenianEngine(
                    base_dir=REPO_DIR,
                    version=version,
                    paschalion=paschalion,
                    temple_feast_date=temple_feast_date,
                    temple_patron=temple_patron,
                    temple_type=temple_type,
                    parish_profile=parish_profile,
                    calendar_source=calendar_source,
                    ordinaries_recension=ordinaries_recension,
                    propers_recension=propers_recension,
                    strict_corpus_mode=strict_corpus_mode,
                )
                cache_map[engine_key] = engine
            else:
                engine.temple_feast_date = temple_feast_date
                engine.temple_patron = temple_patron
                engine.temple_type = temple_type
                engine.parish_profile = parish_profile or {}
                raw_ord = ordinaries_recension or version
                raw_prop = propers_recension or version
                engine.ordinaries_recension = engine.version_map.get(raw_ord, raw_ord) if hasattr(engine, "version_map") else raw_ord
                engine.propers_recension = engine.version_map.get(raw_prop, raw_prop) if hasattr(engine, "version_map") else raw_prop
                engine.strict_corpus_mode = strict_corpus_mode
                engine.trace_log = []

            # Resolve day context & rubrics once (O(1)), then project across all 3 panels (O(n))
            context = engine.get_liturgical_context(target_date)
            rubrics = engine.resolve_rubrics(context)

            memo_Popup = {}
            orig_fns = {}
            for m_name in dir(engine):
                if not m_name.startswith("resolve_") or m_name in ("resolve_rubrics", "resolve_service_title"):
                    continue
                orig_fn = getattr(engine, m_name, None)
                if callable(orig_fn):
                    orig_fns[m_name] = orig_fn

                    def _make_memo(name, fn):
                        def _wrapped(ctx_arg, *a, **kw):
                            k = (
                                name,
                                ctx_arg.get("is_small_vespers") if isinstance(ctx_arg, dict) else None,
                                repr(a),
                                repr(sorted(kw.items())),
                            )
                            if k not in memo_Popup:
                                memo_Popup[k] = fn(ctx_arg, *a, **kw)
                            import copy
                            return copy.deepcopy(memo_Popup[k])
                        import functools
                        return functools.wraps(fn)(_wrapped)

                    setattr(engine, m_name, _make_memo(m_name, orig_fn))

            try:
                booklet = engine.generate_full_booklet(context, rubrics, include_ceremonial=include_ceremonial)
                if booklet_only:
                    recension_meta = {
                        "version": engine.version,
                        "ordinaries_recension": engine.ordinaries_recension,
                        "propers_recension": engine.propers_recension,
                        "strict_corpus_mode": engine.strict_corpus_mode,
                        "split_recensions": bool(
                            ordinaries_recension and propers_recension and ordinaries_recension != propers_recension
                        ),
                    }
                    self.send_json_response({
                        "booklet": booklet,
                        "recension_meta": recension_meta,
                    })
                    return

                digest = engine.generate_typikon_digest(context, rubrics, mode=digest_mode)
                fasting = engine.resolve_fasting_rule(context)

                # Resolve daily ceremonial context
                vestment = engine.resolve_vestment_color(context, rubrics)
                prostrations_info = engine.resolve_prostrations_rule(context)
                clergy_variant = engine.resolve_clergy_variant(context, service="liturgy")
                katavasia = engine.resolve_katavasia(context)
            finally:
                for m_name, orig_fn in orig_fns.items():
                    setattr(engine, m_name, orig_fn)
            seasonal_repertoire = resolve_seasonal_repertoire(target_date, context)

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

            # Add resolved service title to context
            serializable_context["service_title"] = engine.resolve_service_title(context, rubrics)

            response = {
                "context": serializable_context,
                "fasting": fasting,
                "katavasia": katavasia,
                "ceremonial": {
                    "vestment": vestment,
                    "prostrations": prostrations_info,
                    "clergy_variant": clergy_variant,
                },
                "recension_meta": {
                    "version": engine.version,
                    "ordinaries_recension": engine.ordinaries_recension,
                    "propers_recension": engine.propers_recension,
                    "strict_corpus_mode": engine.strict_corpus_mode,
                    "split_recensions": bool(
                        ordinaries_recension and propers_recension and ordinaries_recension != propers_recension
                    ),
                },
                "seasonal_repertoire": seasonal_repertoire,
                "rubrics": {
                    "title": rubrics.get("title", ""),
                    "variables": rubrics.get("variables", {}),
                    "overrides": rubrics.get("overrides", {}),
                    "trace": rubrics.get("_trace", []),
                },
                "booklet": booklet,
                "digest": digest,
            }
            self.send_json_response(response)

        except Exception as e:
            import traceback

            response = {
                "error": str(e),
                "traceback": traceback.format_exc(),
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
        calendar_source = query.get("calendar_source", [None])[0]
        temple_feast = query.get("temple_feast", [None])[0]

        temple_feast_date = None
        if temple_feast:
            try:
                parts = temple_feast.split("-")
                if len(parts) == 2:
                    temple_feast_date = (int(parts[0]), int(parts[1]))
            except ValueError:
                pass

        # Resolve days dynamically using a single RuthenianEngine instance
        timeline_days = []
        try:
            engine = RuthenianEngine(
                base_dir=REPO_DIR,
                version=version,
                paschalion=paschalion,
                temple_feast_date=temple_feast_date,
                calendar_source=calendar_source,
            )
            for d_day in range(7, 13):
                target_date = date(year, 9, d_day)
                context = engine.get_liturgical_context(target_date)
                rubrics = engine.resolve_rubrics(context)

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

                rank_name = rubrics.get("title")
                if not rank_name:
                    rank_name = context.get("dolnytsky_title", f"September {d_day}")

                tone_val = context.get("tone", 1)

                fixed_stichera = "Troparion of the Feast (Tone 4); Kontakion (Tone 4)."
                if day_type == "forefeast":
                    fixed_stichera = (
                        "Troparion of the Forefeast (Tone 4): 'Today from the root of Jesse...'; "
                        "Stichera of the Forefeast."
                    )
                elif day_type == "feast" or day_type == "apodosis":
                    fixed_stichera = (
                        "Troparion of the Feast (Tone 4): 'Your Nativity, O Virgin...'; "
                        "Kontakion (Tone 4): 'Joachim and Anna...'"
                    )

                is_sunday = (target_date.weekday() + 1) % 7 == 0
                if is_sunday:
                    rel_rule = (
                        f"Sunday Octoechos merges with Feast in Tone {tone_val}. "
                        "Resurrectional Stichera and Canons take precedence."
                    )
                else:
                    rel_rule = (
                        f"Weekday Octoechos canons suppressed or merged. "
                        f"Daily Prokeimenon for {target_date.strftime('%A')}."
                    )

                timeline_days.append({
                    "date": target_date.isoformat(),
                    "label": lbl,
                    "name": rank_name,
                    "type": day_type,
                    "rank": rubrics.get("variables", {}).get("rank_class", "Simple Class"),
                    "tone_override": f"Tone {tone_val}",
                    "fixed_text": fixed_stichera,
                    "relative_rule": rel_rule,
                })
        except Exception as e:
            print(f"Error in dynamic roadmap resolving: {e}")
            timeline_days = [
                {
                    "date": f"{year}-09-08",
                    "label": "Sept 8",
                    "name": "NATIVITY OF THE MOST HOLY THEOTOKOS",
                    "type": "feast",
                    "rank": "Vigil Feast (Rank 1)",
                    "tone_override": "Tone 4",
                    "fixed_text": "Troparion of the Feast (Tone 4)",
                    "relative_rule": "Special festal prokeimena.",
                }
            ]

        ensure_repertoires_loaded()
        repertoire_cycles_summary = [
            {
                "cycle_id": cid,
                "cycle_name": repertoires_db[cid].get("cycle_name", cid),
                "total_canonical_items": repertoires_db[cid].get("total_canonical_items", 0),
                "phases_count": repertoires_db[cid].get("phases_count", 0),
            }
            for cid in sorted(repertoires_db.keys())
        ]

        roadmap_data = {
            "status": "success",
            "wings": {
                "logic": 100,
                "structures": 100,
                "assets": 100,
                "docs": 100,
                "ui": 100,
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
                {"gate": 13, "name": "Matins Dismissal & Litany", "status": "completed"},
            ],
            "variant_matrix": {
                "daily_vespers": "completed",
                "great_vespers_vigil": "completed",
                "daily_matins": "completed",
                "festal_matins": "completed",
                "first_hour": "completed",
                "third_six_nine_hours": "completed",
                "divine_liturgy": "completed",
                "presanctified_liturgy": "completed",
                "vesperal_liturgy": "completed",
                "great_compline": "completed",
                "midnight_office": "completed",
            },
            "unresolved_gaps": [
                "Lviv recension assets stubbed for Great Lent",
                "Menaion translations incomplete for the month of October",
            ],
            "seasonal_repertoires": {
                "total_cycles": len(repertoire_cycles_summary),
                "total_canonical_items": sum(c["total_canonical_items"] for c in repertoire_cycles_summary),
                "cycles": repertoire_cycles_summary,
            },
            "feast_cycles": {
                "nativity_theotokos": {
                    "feast_name": "Nativity of the Most Holy Theotokos",
                    "double_border_date": f"{year}-09-08",
                    "days": timeline_days,
                }
            },
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

    def api_annual_patterns(self, query):
        year_str = query.get("year", ["2026"])[0]
        candidate_paths = [
            os.path.join(CANTOR_DASHBOARD_DIR, f"annual_pattern_analysis_{year_str}.json"),
            os.path.join(REPO_DIR, "json_db", "almanac", f"annual_pattern_analysis_{year_str}.json"),
            os.path.join(REPO_DIR, f"annual_pattern_analysis_{year_str}.json"),
        ]
        data = None
        for p in candidate_paths:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    break
                except Exception as e:
                    print(f"Error loading annual patterns from {p}: {e}")
        if data is None:
            self.send_json_error(f"Annual pattern analysis for {year_str} not found.", 404)
        else:
            self.send_json_response(data)

    def api_musicology_catalogs(self, query):
        db_dir = os.path.join(REPO_DIR, "Data", "databases")
        catalog_name = query.get("catalog", [None])[0]
        catalog_files = {
            "lexicon_bridge_concordance": "lexicon_bridge_concordance.json",
            "pan_catalogue": "pan_catalogue_fortified_corpus.json",
            "yasinovsky_catalogue": "yasinovsky_catalogue_fortified_corpus.json",
            "liturgical_aggregator_cross_ref": "liturgical_aggregator_cross_ref_handoff.json",
        }
        if catalog_name and catalog_name in catalog_files:
            filepath = os.path.join(db_dir, catalog_files[catalog_name])
            if not os.path.exists(filepath):
                self.send_json_error(f"Catalog {catalog_name} not found.", 404)
                return
            with open(filepath, "r", encoding="utf-8") as f:
                self.send_json_response(json.load(f))
            return

        summaries = {}
        for key, fname in catalog_files.items():
            filepath = os.path.join(db_dir, fname)
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        summaries[key] = {
                            "filename": fname,
                            "record_count": len(data),
                        }
                    else:
                        summaries[key] = {
                            "filename": fname,
                            "metadata": data.get("metadata", {}),
                            "top_level_keys": [
                                k for k in data.keys() if k not in ("provenance_status", "gap_marker")
                            ],
                        }
                except Exception as e:
                    summaries[key] = {"filename": fname, "error": str(e)}
        self.send_json_response(summaries)

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

    watcher_thread = threading.Thread(target=watch_frontend_files, daemon=True)
    watcher_thread.start()

    handler_class = CantorDashboardHandler

    server_address = ("", PORT)
    socketserver.ThreadingTCPServer.allow_reuse_address = True

    print("\n=======================================================")
    print("Starting Cantor Dashboard Server...")
    print(f"Server is running locally at: http://localhost:{PORT}")
    print("Press Ctrl+C in terminal to stop.")
    print("=======================================================\n")

    try:
        with socketserver.ThreadingTCPServer(server_address, handler_class) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    except Exception as e:
        print(f"Server error: {e}")


if __name__ == "__main__":
    run()
