"""Guard: the frozen-archive News feed renders EVERY collected item (no per-base cap
hides milestones).

curateNewsFeed() caps non-official items at NEWS_MAX_PER_BASE per base URL (via
newsBaseKey). That live-feed de-clutter hid 6 of the 8 ABC7 live-blog entries —
including distinct milestones like "Newsom declares state of emergency" — and made
the feed show 86 while news_archive.json / the README report 92 (owner-flagged
2026-06-01). For a frozen historical archive that values completeness, the cap must
be >= the largest base cluster so nothing is dropped. Data-driven: mirrors the real
newsBaseKey() so it tracks the data, not a magic number. Pure text/data guard.
"""
import json
import re
from collections import Counter
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"
ARCHIVE = REPO_ROOT / "data" / "news_archive.json"


def _base_key(url):
    """Mirror dashboard.html newsBaseKey(): youtube keyed by video id; otherwise
    strip hash/query, collapse a trailing /entry/<id>/ to the base, strip slashes."""
    if not url:
        return ""
    yt = re.search(r"[?&]v=([\w-]{11})", url)
    if yt:
        return "youtube:" + yt.group(1)
    u = url.split("#")[0].split("?")[0]
    u = re.sub(r"/entry/[^/]+/?$", "/", u)
    return re.sub(r"/+$", "", u)


def test_feed_shows_every_collected_item():
    items = json.loads(ARCHIVE.read_text(encoding="utf-8"))["items"]
    # officials are exempt from the cap (always kept); the cap only clips the rest.
    counts = Counter(_base_key(it.get("url")) for it in items if it.get("type") != "official")
    max_base = max(counts.values()) if counts else 0
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r"NEWS_MAX_PER_BASE\s*=\s*(\d+)", text)
    cap = int(m.group(1)) if m else -1
    ok = cap >= max_base
    return {
        "passed": ok,
        "details": f"NEWS_MAX_PER_BASE={cap} >= largest base cluster {max_base}: feed shows all {len(items)} items"
        if ok
        else f"NEWS_MAX_PER_BASE={cap} < largest base cluster {max_base}: feed hides {max_base - cap} item(s) from that base",
        "metrics": {"cap": cap, "max_base": max_base, "total_items": len(items)},
    }


def test_all_subtab_chronological_not_officials_first():
    """The News 'All' subtab renders in pure reverse-chronological order (newest-first), NOT
    officials-as-a-block-first. curateNewsFeed sorts the whole feed newest-first, then returns
    the deduped list in that order — the old `officials.concat(rest)` re-grouping (which floated
    all 12 officials above every article regardless of date, reading 'out of order' in 'All') is
    removed. This is a FROZEN archive of a resolved incident, so the chronological story is the
    value; officials stay distinguished by their OFFICIAL badge + the dedicated Official filter
    tab, so authority no longer depends on feed position (user 2026-06-05). Static structural
    guard on the curateNewsFeed source (the eval can't run JS)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    i = text.find("function curateNewsFeed(")
    j = text.find("function buildFeedCardsHtml(", i) if i >= 0 else -1
    body = text[i:j] if (i >= 0 and j > i) else ""
    newest_first = bool(re.search(r"feed\.sort\(", body)) and "tb - ta" in body
    no_officials_first = ".concat(rest)" not in body
    returns_deduped = bool(re.search(r"return\s+deduped\s*;", body))
    ok = bool(body) and newest_first and no_officials_first and returns_deduped
    return {"passed": ok,
            "details": "News 'All' pure reverse-chronological (deduped newest-first; officials-first concat removed)"
            if ok else f"newest_first={newest_first} no_officials_first={no_officials_first} returns_deduped={returns_deduped}"}
