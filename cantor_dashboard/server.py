"""
cantor_dashboard/server.py — Backward-Compatibility Entrypoint Shim
===================================================================
Delegates execution and module attributes to the canonical 6-Tier location:
`Data/prototypes/cantor_dashboard/server.py`.

This shim ensures that external deployment configurations (e.g., Render Web
Service UI startCommand `python cantor_dashboard/server.py`) and legacy test
harnesses continue to boot seamlessly while all dashboard assets reside in
`Data/prototypes/cantor_dashboard/`.
"""
import importlib.util
import os
import sys

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANONICAL_SERVER_PATH = os.path.join(
    REPO_DIR, "Data", "prototypes", "cantor_dashboard", "server.py"
)

if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

_spec = importlib.util.spec_from_file_location("cantor_dashboard_server", CANONICAL_SERVER_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Unable to load canonical server module at {CANONICAL_SERVER_PATH}")

_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Re-export public attributes for callers importing cantor_dashboard.server
for _attr in dir(_mod):
    if not _attr.startswith("__"):
        globals()[_attr] = getattr(_mod, _attr)

if __name__ == "__main__":
    _mod.run()
