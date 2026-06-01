"""Guard (T2, archive pivot): client polling is disabled for the frozen snapshot —
REFRESH_MS is null and the fetchStatus interval is guarded, so the static archive label
is never overwritten by a live refresh. T2 must ship in lockstep with T1."""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASH = REPO_ROOT / "dashboard.html"


def test_refresh_ms_null():
    t = DASH.read_text(encoding="utf-8")
    nulled = re.search(r"var REFRESH_MS\s*=\s*null", t) is not None
    return {"passed": nulled, "details": f"REFRESH_MS=null: {nulled}"}


def test_interval_guarded():
    t = DASH.read_text(encoding="utf-8")
    # the unconditional top-level call must be gone (replaced by a guarded form)
    bare = "\nsetInterval(fetchStatus, REFRESH_MS);" in t
    guarded = "if (REFRESH_MS" in t
    return {"passed": (not bare) and guarded,
            "details": f"bare_unconditional_interval={bare} guard_present={guarded}"}
