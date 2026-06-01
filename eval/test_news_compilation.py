"""Guards for the full May 21-28 news compilation + official-statement history (2026-05-31).

The Coverage Archive is the FROZEN historical record of the incident — both news coverage
AND official statements for the May 21-28 window. New collection going forward is
officials-only (the rolling status.json thread). These guards lock: every incident day is
covered, the official-statement history is present, the dashboard renders archive officials
as official cards, every item carries provenance, and the collection policy is documented.
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


def test_archive_covers_full_incident_window():
    days = Counter((i.get("published_iso") or "")[:10] for i in _archive()["items"])
    need = ["2026-05-21", "2026-05-22", "2026-05-23", "2026-05-24",
            "2026-05-25", "2026-05-26", "2026-05-27", "2026-05-28"]
    missing = [d for d in need if days.get(d, 0) < 1]
    return {"passed": not missing,
            "details": f"incident days with no coverage: {missing}" if missing else "all 8 incident days covered"}


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
