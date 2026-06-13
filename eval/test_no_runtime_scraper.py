"""Guard: the dashboard does NOT auto-scrape external images at runtime (2026-06-01).

An emergency app must not fetch an arbitrary page's og:image and display it as if it were a
verified thumbnail — it bypasses provenance + human review and risks showing a wrong/stale
image. The old microlink scraper (fetchOgImage/hydrateMissingThumbnails) was also dead for
the active renderer. Videos without a canonical thumbnail use the branded "Watch on <outlet>"
placeholder instead. This guard fails if the scraper or its microlink allowance returns.
"""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"
VERCEL = REPO_ROOT / "vercel.json"


def test_no_og_scraper_in_dashboard():
    text = DASHBOARD.read_text(encoding="utf-8")
    bad = [s for s in ("fetchOgImage", "hydrateMissingThumbnails", "microlink", "api.microlink.io") if s in text]
    return {"passed": not bad, "details": f"runtime-scraper artifacts present: {bad}" if bad else "no runtime og-scraper in dashboard"}


def test_no_microlink_in_csp():
    vj = VERCEL.read_text(encoding="utf-8")
    return {"passed": "microlink" not in vj,
            "details": "microlink removed from CSP" if "microlink" not in vj else "CSP still allows api.microlink.io (unused scraper host)"}
