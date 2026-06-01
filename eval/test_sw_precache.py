"""Guard: news_archive.json is precached and CACHE_NAME bumped so returning users get
the new shell + offline archive (2026-05-31). Cross-origin non-interception is guarded
separately by test_map_reload_regressions."""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
SW = REPO_ROOT / "sw.js"


def test_cache_bumped_and_archive_precached():
    text = SW.read_text(encoding="utf-8")
    bumped = 'CACHE_NAME = "gg-tank-v26"' in text
    precached = '"/data/news_archive.json"' in text
    return {"passed": bumped and precached, "details": f"v26={bumped} precached={precached}"}
