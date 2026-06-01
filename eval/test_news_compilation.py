"""Guards for the news compilation + official-statement history (2026-05-31).

The Coverage Archive is the FROZEN historical record of the incident. Non-official news was
collected only during the ACTIVE EMERGENCY — from the May 21 onset to the May 26 all-clear
(resolved_iso). After the all-clear, only official statements are retained (the conduit stops
aggregating general news once residents are safe; the rolling status.json thread continues).
These guards lock: every emergency day (May 21-26) is covered, NO non-official news is dated
after the May 26 all-clear, the official-statement history is present, the dashboard renders
archive officials as official cards, every item carries provenance, and the policy + window
are documented.
"""
import json
from collections import Counter
from pathlib import Path

CATEGORY = "behavioral"
REPO = Path(__file__).resolve().parent.parent
ARCHIVE = REPO / "data" / "news_archive.json"
DASH = REPO / "dashboard.html"


def _archive():
    return json.load(open(ARCHIVE, encoding="utf-8"))


ALLCLEAR = "2026-05-26"  # official all-clear date (Pacific); resolved_iso = 2026-05-27T02:30:00Z


def test_archive_covers_full_emergency_window():
    """Every day of the active emergency (May 21 onset -> May 26 all-clear) has coverage."""
    days = Counter((i.get("published_iso") or "")[:10] for i in _archive()["items"])
    need = ["2026-05-21", "2026-05-22", "2026-05-23",
            "2026-05-24", "2026-05-25", "2026-05-26"]
    missing = [d for d in need if days.get(d, 0) < 1]
    return {"passed": not missing,
            "details": f"emergency days with no coverage: {missing}" if missing else "all 6 emergency days (May 21-26) covered"}


def test_no_nonofficial_news_after_allclear():
    """The conduit stops aggregating general news at the all-clear. Any article/video dated
    after May 26 breaks the onset->all-clear collection window (officials are exempt — the
    rolling official thread legitimately continues after resolution)."""
    bad = [((i.get("published_iso") or "")[:10], i.get("type"), i.get("outlet"))
           for i in _archive()["items"]
           if i.get("type") != "official" and (i.get("published_iso") or "")[:10] > ALLCLEAR]
    return {"passed": not bad,
            "details": (f"{len(bad)} non-official items after the all-clear: {bad[:4]}" if bad
                        else "no non-official news after the May 26 all-clear")}


def test_collection_window_is_onset_to_allclear():
    w = (_archive().get("policy") or {}).get("window", "")
    ok = w == "2026-05-21/2026-05-26"
    return {"passed": ok,
            "details": f"policy.window={w!r} (want '2026-05-21/2026-05-26' = onset -> all-clear)"}


def test_archive_has_official_statement_history():
    n = sum(1 for i in _archive()["items"] if i.get("type") == "official")
    return {"passed": n >= 10, "details": f"official-type archive items: {n} (want >=10)"}


def test_dashboard_renders_archive_officials():
    t = DASH.read_text(encoding="utf-8")
    ok = 'it.type === "official"' in t and "text: it.summary" in t
    return {"passed": ok, "details": f"archive coverage map handles type 'official': {ok}"}


def test_archive_every_item_has_provenance():
    bad = [i.get("url") for i in _archive()["items"] if not (i.get("provenance") or {}).get("url_status")]
    return {"passed": not bad,
            "details": f"items missing provenance.url_status: {len(bad)}" if bad else "all items carry provenance.url_status"}


def test_archive_officials_have_source_url():
    bad = [i.get("title") for i in _archive()["items"] if i.get("type") == "official" and not i.get("url")]
    return {"passed": not bad,
            "details": f"official items missing source url: {len(bad)}" if bad else "all official items carry a source url"}


def test_collection_policy_documented():
    a = _archive()
    blob = (json.dumps(a.get("audit", {})) + json.dumps(a.get("policy", {}))).lower()
    ok = "officials-only" in blob and ("frozen" in blob or "freeze" in blob)
    return {"passed": ok, "details": f"freeze + officials-only policy documented in archive: {ok}"}
