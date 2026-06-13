"""Guard (T3 / D1 / D3, archive pivot): status.json is a frozen May 26 snapshot — no data
after the all-clear, timestamps frozen in the resolution window, and the (unrendered)
incident.status_headline carries no post-26th editorial synthesis."""
import json
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
STATUS = REPO_ROOT / "public" / "status.json"
ALL_CLEAR = "2026-05-27T02:30:00Z"  # May 26 7:30pm PDT


def _d():
    return json.loads(STATUS.read_text(encoding="utf-8"))


def test_no_post_allclear_officials():
    offs = _d().get("official_statements", [])
    post = [s.get("time_iso") for s in offs if (s.get("time_iso") or "") > ALL_CLEAR]
    return {"passed": not post, "details": f"post-all-clear officials: {post}"}


def test_timestamps_frozen():
    asof = _d().get("data_as_of_iso") or ""
    frozen = asof <= "2026-05-27T03:00:00Z"
    return {"passed": frozen, "details": f"data_as_of_iso={asof} frozen={frozen}"}


def test_headline_no_editorial_synthesis():
    h = (_d().get("incident", {}).get("status_headline") or "").lower()
    banned = [w for w in ("cleanup", "lawsuit", "investigation", "monitoring", "removal") if w in h]
    return {"passed": not banned, "details": f"headline={h[:80]!r} banned_terms={banned}"}
