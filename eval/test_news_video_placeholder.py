"""Guard: non-YouTube video cards get a branded, self-contained placeholder (2026-06-01).

NBC LA / FOX 11 videos have no youtube_id and no thumbnail_url, so they showed a blank gray
box. The OG-image scrape can't help (hydrateMissingThumbnails targets .news-thumb, the dead
renderer's class, not the active .feed-card-thumb). Fix: render a branded "play + outlet"
placeholder (zero external dependency) and restore the it.thumbnail_url fallback in the
archive coverage map. Markup anchors use the full <span ...> tag so a bare class match in the
inline <style> can't satisfy the markup checks (eval-find-hits-css-before-html).
"""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_branded_placeholder_css_and_markup_present():
    text = DASHBOARD.read_text(encoding="utf-8")
    css = ".feed-card-branded-placeholder {" in text
    markup = '<span class="feed-card-branded-outlet">' in text
    return {"passed": css and markup,
            "details": f"branded-placeholder css={css} outlet-label markup={markup}"}


def test_archive_map_honors_thumbnail_url():
    text = DASHBOARD.read_text(encoding="utf-8")
    ok = 'it.thumbnail_url || ""' in text
    return {"passed": ok,
            "details": "archive coverage map falls back to it.thumbnail_url for non-YouTube videos"
            if ok else "archive map drops thumbnail_url (only youtube_id) -> non-YouTube videos lose any real poster"}
