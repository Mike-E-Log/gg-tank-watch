"""Guard: the News feed reads the curated archive (data/news_archive.json), with
snap.videos[] as the offline/fetch-fail fallback. UI-layer only (2026-05-31)."""
import json
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"
ARCHIVE = REPO_ROOT / "public" / "data" / "news_archive.json"


def test_dashboard_fetches_archive():
    text = DASHBOARD.read_text(encoding="utf-8")
    fetches = 'fetch("data/news_archive.json' in text
    has_loader = "function loadArchive" in text
    return {"passed": fetches and has_loader, "details": f"fetch={fetches} loader={has_loader}"}


def test_videos_fallback_preserved():
    text = DASHBOARD.read_text(encoding="utf-8")
    return {"passed": "snap.videos" in text, "details": "snap.videos[] fallback path retained"}


def test_archive_has_substantive_items():
    data = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    n = len(data.get("items", []))
    return {"passed": n >= 30, "details": f"archive items: {n}", "metrics": {"items": n}}


def test_render_selects_archive_with_videos_fallback():
    """Wiring guard: render() actually chooses archiveCache.items when present and falls
    back to snap.videos[] otherwise, tagging archive items isArchive:true. Closes the gap
    between 'loadArchive exists' and 'its result is wired into the feed' — without it, a
    regression that loaded the archive but never used it would pass (adversarial review
    2026-05-31)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    ternary = "archiveCache && Array.isArray(archiveCache.items) && archiveCache.items.length" in text
    fallback = "(snap.videos || []).map" in text
    tagged = "isArchive: true" in text
    return {"passed": ternary and fallback and tagged,
            "details": f"ternary={ternary} videos_fallback={fallback} isArchive_tagged={tagged}"}
