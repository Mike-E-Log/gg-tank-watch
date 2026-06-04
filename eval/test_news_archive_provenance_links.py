"""Guard (audit 2026-06-04): no news_archive item may carry the dead OCDE
"school-campuses" slug, which 404s while its provenance claimed
url_status:"agent-verified-resolves" with fabricated WebFetch detail.

This is the single finding that refuted the archive's core safety claim ("no
fabricated sources; every provenance claim is true"). Root cause was a
near-duplicate slug: the LIVE OCDE post is
".../several-garden-grove-unified-campuses-closed-..." (no "school-"); a
transcription added "school-" producing a 404 variant that was then recorded
as verified. The School Closure Notice item was repointed to the live NBC LA
"schools closed" article (press, type=article) with honest provenance.

Static guard (the harness has no network in the default run); locks out the
specific dead slug so the fabrication cannot regress.
"""
import json
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = REPO_ROOT / "data" / "news_archive.json"

DEAD_SLUG = "unified-school-campuses-closed"  # 404 variant (the live one has no "school-")


def test_no_dead_ocde_school_slug():
    """The 404 OCDE 'school-campuses' slug must not appear in any archive item URL."""
    items = json.loads(ARCHIVE.read_text(encoding="utf-8"))["items"]
    offenders = [i.get("title", "?") for i in items if DEAD_SLUG in (i.get("url") or "")]
    return {
        "passed": not offenders,
        "details": "no dead OCDE school-campuses slug in the archive"
        if not offenders
        else "dead OCDE 404 slug still present in: " + "; ".join(offenders),
        "metrics": {"dead_slug_items": len(offenders)},
    }


def test_no_agent_verified_item_uses_known_dead_slug():
    """No item may BOTH claim agent-verified-resolves AND carry the known dead slug."""
    items = json.loads(ARCHIVE.read_text(encoding="utf-8"))["items"]
    bad = [
        i.get("title", "?")
        for i in items
        if DEAD_SLUG in (i.get("url") or "")
        and (i.get("provenance") or {}).get("url_status") == "agent-verified-resolves"
    ]
    return {
        "passed": not bad,
        "details": "no fabricated agent-verified provenance on a dead URL"
        if not bad
        else "fabricated provenance (agent-verified on a 404) in: " + "; ".join(bad),
        "metrics": {"fabricated_provenance_items": len(bad)},
    }
