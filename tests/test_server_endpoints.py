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
        return s.connect_ex(('localhost', port)) == 0

@pytest.fixture(scope="module")
def dashboard_server():
    """Fixture to start the cantor dashboard server on a test port."""
    server_script = os.path.join(REPO_DIR, "cantor_dashboard", "server.py")
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
        stderr=server_log
    )
    
    # Wait for port to open
    retries = 20
    server_ready = False
    for i in range(retries):
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
    if len(data) > 0:
        assert "filename" in data[0]
        assert "name" in data[0]
        assert "key_count" in data[0]

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

def test_api_resolve_ordinary_day(dashboard_server):
    res = requests.get(f"{dashboard_server}/api/resolve?date=2026-06-09")
    assert res.status_code == 200
    data = res.json()
    assert "context" in data
    assert "booklet" in data
    assert "digest" in data
    assert "fasting" in data
    assert "ceremonial" in data

def test_api_resolve_paradigm_id(dashboard_server):
    # Test resolving a dynamic day (where almanac is not used) to ensure paradigm_id is resolved and is correct
    res = requests.get(f"{dashboard_server}/api/resolve?date=2026-07-11&version=stamford_2014")
    assert res.status_code == 200
    data = res.json()
    assert "context" in data
    assert "paradigm_id" in data["context"]
    assert data["context"]["paradigm_id"] == "CASE_05"
