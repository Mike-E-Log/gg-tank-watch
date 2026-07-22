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

Extended 2026-07-21 (Fable 5 audit headline finding): link rot recreated the
reader-facing symptom on two more URLs (ABC wireStory -> HTTP 404; Aviation Week
-> login wall). Those items were TRUE at collection and decayed later, so per
archival practice they keep their URLs and get dated url_status annotations
instead of replacement ("annotate, don't substitute" - unlike the OCDE slug,
which was wrong at creation and was repointed). This guard now holds the class:
no item carrying a known-rotted URL may still claim a "verified-resolves" status.
"""
import json
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = REPO_ROOT / "public" / "data" / "news_archive.json"

DEAD_SLUG = "unified-school-campuses-closed"  # 404 variant (the live one has no "school-")

# URLs found dead or inaccessible on a dated recheck. The item may keep the URL
# for the historical record, but its provenance must not claim the link resolves.
ROTTED_SLUGS = {
    DEAD_SLUG: "OCDE 404 variant (2026-06-04 audit; also banned outright above)",
    "officials-lift-evacuation-orders-california-residents-living-damaged-133303858":
        "ABC wireStory HTTP 404 (2026-07-21 recheck)",
    "gkn-aerospace-suffers-industrial-accident":
        "Aviation Week login wall (2026-07-21 recheck)",
}
VERIFIED_STATUSES = {"agent-verified-resolves", "verified-resolves"}


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
    """No item may BOTH claim a verified-resolves status AND carry a known-rotted URL."""
    items = json.loads(ARCHIVE.read_text(encoding="utf-8"))["items"]
    bad = [
        i.get("title", "?")
        for i in items
        for slug in ROTTED_SLUGS
        if slug in (i.get("url") or "")
        and (i.get("provenance") or {}).get("url_status") in VERIFIED_STATUSES
    ]
    return {
        "passed": not bad,
        "details": "no fabricated agent-verified provenance on a dead URL"
        if not bad
        else "verified-resolves status on a known-rotted URL in: " + "; ".join(bad),
        "metrics": {"fabricated_provenance_items": len(bad)},
    }
