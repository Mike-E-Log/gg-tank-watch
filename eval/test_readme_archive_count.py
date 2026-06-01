"""Guard (Batch 3, 2026-06-01): the README's archive-inventory claim stays in sync with the
actual frozen data/news_archive.json.

The README "honest by construction" section cited "39 items (29 articles, 10 videos) across 17
outlets" — a count that drifted stale after the Batch 2 expansion to 92 items (an adversarial
review flagged it as a credibility risk: an archive-framed honesty section citing a wrong
inventory). The archive is FROZEN, so these numbers are fixed; this guard locks the README copy
to the data so a future edit can't re-introduce the drift. Phrasing must keep each number
adjacent to its unit ("92 items", "56 articles", ...) so the guard can parse it.
"""
import json
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO = Path(__file__).resolve().parent.parent
README = REPO / "README.md"
ARCHIVE = REPO / "data" / "news_archive.json"


def _counts():
    items = json.loads(ARCHIVE.read_text(encoding="utf-8"))["items"]
    total = len(items)
    vids = sum(1 for i in items if i.get("youtube_id") or i.get("type") == "video")
    arts = sum(1 for i in items if i.get("type") == "article")
    offs = sum(1 for i in items if i.get("type") == "official")
    outlets = len({(i.get("outlet") or "").strip() for i in items if i.get("outlet")})
    return {"items": total, "articles": arts, "videos": vids,
            "official statements": offs, "outlets": outlets}


def _claimed(unit):
    txt = README.read_text(encoding="utf-8")
    m = re.search(r"(\d+)\s+" + re.escape(unit), txt)
    return int(m.group(1)) if m else None


def test_readme_total_item_count_matches_data():
    want = _counts()["items"]
    got = _claimed("items")
    return {"passed": got == want, "details": f"README 'items'={got}; data={want}"}


def test_readme_breakdown_matches_data():
    c = _counts()
    mismatches = {}
    for unit in ("articles", "videos", "official statements", "outlets"):
        got = _claimed(unit)
        if got != c[unit]:
            mismatches[unit] = f"README={got}/data={c[unit]}"
    return {"passed": not mismatches,
            "details": "README breakdown matches data" if not mismatches else f"mismatches: {mismatches}"}
