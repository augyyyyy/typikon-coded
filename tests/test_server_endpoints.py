import os
import sys
import time
import socket
import subprocess
import pytest
import requests

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(TEST_DIR)
TEST_PORT = 8092
BASE_URL = f"http://localhost:{TEST_PORT}"


def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


@pytest.fixture(scope="module")
def dashboard_server():
    server_script = os.path.join(REPO_DIR, "Data", "prototypes", "cantor_dashboard", "server.py")
    server_log_path = os.path.join(REPO_DIR, "scratch", "server_test.log")
    os.makedirs(os.path.dirname(server_log_path), exist_ok=True)
    server_log = open(server_log_path, "w", encoding="utf-8")

    env = os.environ.copy()
    env["PORT"] = str(TEST_PORT)

    print(f"\n[Test API] Starting dashboard server on port {TEST_PORT}...")
    proc = subprocess.Popen(
        [sys.executable, server_script],
        env=env,
        stdout=server_log,
        stderr=server_log,
    )

    # Wait for port to open
    retries = 20
    server_ready = False
    for _ in range(retries):
        if is_port_open(TEST_PORT):
            server_ready = True
            break
        time.sleep(0.5)

    if not server_ready:
        proc.terminate()
        server_log.close()
        with open(server_log_path, "r", encoding="utf-8") as f:
            log_content = f.read()
        raise RuntimeError(f"Server failed to start on port {TEST_PORT}. Logs:\n{log_content}")

    print("[Test API] Server is ready. Running API assertions...")
    yield BASE_URL

    print("[Test API] Shutting down dashboard server...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    server_log.close()


def test_healthz(dashboard_server):
    res = requests.get(f"{dashboard_server}/healthz")
    assert res.status_code == 200
    assert res.text == "OK"


def test_api_books(dashboard_server):
    res = requests.get(f"{dashboard_server}/api/books")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "filename" in data[0]
    assert "name" in data[0]
    assert "key_count" in data[0]

    # Verify nested Triodion files now expose non-empty previews
    lenten_book = next((b for b in data if b["filename"] == "text_lenten_triodion.json"), None)
    assert lenten_book is not None
    assert lenten_book["key_count"] == 12
    assert any(k.get("preview") for k in lenten_book["keys"])


def test_api_roadmap(dashboard_server):
    res = requests.get(f"{dashboard_server}/api/roadmap?year=2026")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"

    # Assert updated 100% completion wings
    assert data["wings"]["logic"] == 100
    assert data["wings"]["structures"] == 100
    assert data["wings"]["assets"] == 100
    assert data["wings"]["ui"] == 100

    # Assert completed Matins gate 13
    gates = data["matins_gates"]
    gate_13 = next(g for g in gates if g["gate"] == 13)
    assert gate_13["status"] == "completed"

    # Assert completed variant matrix items
    matrix = data["variant_matrix"]
    assert matrix["presanctified_liturgy"] == "completed"
    assert matrix["vesperal_liturgy"] == "completed"
    assert matrix["great_compline"] == "completed"

    # Check that the collision gap has been removed
    assert not any("collision" in gap.lower() for gap in data["unresolved_gaps"])

    # Assert seasonal_repertoires summary is exposed
    assert "seasonal_repertoires" in data
    assert data["seasonal_repertoires"]["total_cycles"] == 5
    assert data["seasonal_repertoires"]["total_canonical_items"] == 140


def test_api_repertoires_catalog_and_filters(dashboard_server):
    res = requests.get(f"{dashboard_server}/api/repertoires")
    assert res.status_code == 200
    data = res.json()
    assert data["total_cycles"] == 5
    assert data["total_canonical_items"] == 140
    assert data["total_phases"] == 30
    assert len(data["cycles"]) == 5

    # Filter by cycle=WO-01 and phase=1
    res_filtered = requests.get(f"{dashboard_server}/api/repertoires?cycle=WO-01&phase=1")
    assert res_filtered.status_code == 200
    filtered = res_filtered.json()
    assert len(filtered["cycles"]) == 1
    assert filtered["cycles"][0]["cycle_id"] == "WO-01"
    assert filtered["cycles"][0]["filtered_items_count"] > 0
    assert all(item["phase"] == 1 for item in filtered["cycles"][0]["items"])

    # Resolve for date=2026-12-25 (Nativity)
    res_date = requests.get(f"{dashboard_server}/api/repertoires?date=2026-12-25")
    assert res_date.status_code == 200
    date_payload = res_date.json()
    resolved = date_payload["resolved_for_date"]
    assert resolved is not None
    assert resolved["cycle_id"] == "WO-01"
    assert resolved["primary_phase"] == 5
    assert resolved["appointed_items_count"] > 0


def test_api_resolve_ordinary_day(dashboard_server):
    res = requests.get(f"{dashboard_server}/api/resolve?date=2026-06-09")
    assert res.status_code == 200
    data = res.json()
    assert "context" in data
    assert "booklet" in data
    assert "digest" in data
    assert "fasting" in data
    assert "ceremonial" in data
    assert "seasonal_repertoire" in data
    assert data["seasonal_repertoire"]["cycle_id"] == "WO-05"
    assert data["seasonal_repertoire"]["dogmatikon_of_the_tone"] is not None


def test_api_resolve_paschal_seasonal_repertoire(dashboard_server):
    res = requests.get(f"{dashboard_server}/api/resolve?date=2026-04-05")
    assert res.status_code == 200
    data = res.json()
    rep = data.get("seasonal_repertoire")
    assert rep is not None
    assert rep["cycle_id"] == "WO-04"
    assert rep["primary_phase"] == 1
    assert rep["appointed_items_count"] > 0


def test_api_resolve_paradigm_id(dashboard_server):
    res = requests.get(f"{dashboard_server}/api/resolve?date=2026-07-11&version=stamford_2014")
    assert res.status_code == 200
    data = res.json()
    assert "context" in data
    assert "paradigm_id" in data["context"]
    assert data["context"]["paradigm_id"] == "CASE_05"


def test_api_resolve_calendar_source(dashboard_server):
    # July 6, 2026: Sisoes the Great
    # On UGCC official calendar: simple rank
    res_ugcc = requests.get(
        f"{dashboard_server}/api/resolve?date=2026-07-06&version=stamford_2014&calendar_source=ugcc_official"
    )
    assert res_ugcc.status_code == 200
    data_ugcc = res_ugcc.json()
    assert data_ugcc["context"]["dolnytsky_rank"] == "SIMPLE"

    # On Lviv Typikon Part 5 calendar: polyeleos rank
    res_typikon = requests.get(
        f"{dashboard_server}/api/resolve?date=2026-07-06&version=stamford_2014&calendar_source=typikon"
    )
    assert res_typikon.status_code == 200
    data_typikon = res_typikon.json()
    assert data_typikon["context"]["dolnytsky_rank"] == "POLYELEOS"
