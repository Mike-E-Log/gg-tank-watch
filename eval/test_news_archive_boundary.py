"""Guard: the Coverage Archive holds NOTHING after the May 26 all-clear (fully-historical pivot,
D1, 2026-06-01).

The archive is a frozen record of the ACTIVE emergency — May 21 tank failure -> May 26 evacuation
lifted. Post-resolution accountability/apology/litigation coverage (e.g. a May 27 company apology)
is intentionally out of scope. This is STRICTER than test_news_compilation.test_no_nonofficial_news_after_allclear
(which exempted officials): the fully-historical pivot prunes ALL post-boundary items, officials
included. Boundary = resolved_iso 2026-05-27T02:30:00Z (May 26 7:30pm PDT): keep <=, prune after.
"""
import json
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = REPO_ROOT / "data" / "news_archive.json"
BOUNDARY = "2026-05-27T02:30:00Z"  # all-clear; same literal as test_resolved_date / test_status_json_frozen


def _items():
    d = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    return d.get("items", []) if isinstance(d, dict) else d


def test_no_item_after_allclear_boundary():
    """No archive item (article, video, OR official) is dated after the all-clear boundary.
    ISO-8601 Zulu strings are zero-padded fixed-width, so lexicographic > is a valid time
    comparison here."""
    items = _items()
    offenders = [((it.get("published_iso") or ""), it.get("type"), it.get("outlet"),
                  (it.get("title") or it.get("summary") or "")[:50])
                 for it in items if (it.get("published_iso") or "") > BOUNDARY]
    ok = not offenders
    return {"passed": ok,
            "details": f"all {len(items)} items <= {BOUNDARY}" if ok
            else f"{len(offenders)} post-boundary item(s): {offenders[:3]}",
            "metrics": {"post_boundary": len(offenders), "total": len(items)}}


def test_every_item_has_zulu_published_iso():
    """The lexicographic boundary check above is only sound if every published_iso is a
    fixed-width UTC 'Z' timestamp (YYYY-MM-DDThh:mm:ssZ). A non-Zulu offset like
    '2026-05-26T19:31:00-07:00' would sort BEFORE the boundary string while actually being
    after the all-clear, slipping a post-boundary item past test_no_item_after_allclear_boundary.
    Lock the format so a future data refresh can't inject one."""
    items = _items()
    bad = [((it.get("published_iso") or "(missing)"), (it.get("title") or it.get("summary") or "?")[:40])
           for it in items
           if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", (it.get("published_iso") or ""))]
    ok = not bad
    return {"passed": ok,
            "details": "every item dated with a Zulu UTC timestamp" if ok
            else f"{len(bad)} item(s) with non-Zulu/missing published_iso: {bad[:3]}"}
