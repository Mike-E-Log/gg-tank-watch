"""Guard: a first-time visitor (no saved tab) lands on the Map tab -- the markup default-active
panel is panel-map. The returning-visitor restore is a separate, kept feature (test_tab_persist).
User follow-up 2026-06-02."""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"


def test_default_active_panel_is_map():
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r'<div class="tab-panel active" id="panel-([a-z]+)"', text)
    panel = m.group(1) if m else ""
    return {"passed": panel == "map", "details": f"default active panel={panel!r}"}
