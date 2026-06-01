"""Guard: the persistent safety-strip footer vertically centers its content (user follow-up
2026-05-31). It is a column flex container, so vertical centering = justify-content: center on
the main axis."""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_safety_strip_vertically_centered():
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r"\.safety-strip\s*\{([^}]*)\}", text)
    body = m.group(1) if m else ""
    is_column = "flex-direction: column" in body
    centered = "justify-content: center" in body
    ok = is_column and centered
    return {"passed": ok,
            "details": "safety-strip column flex centers content vertically" if ok
            else f"column={is_column} justify_center={centered}"}
