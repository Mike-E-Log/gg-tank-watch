"""Guard: the incident all-clear date is May 26 2026 (verified OCFA all-clear at 7:30pm PDT),
NOT the earlier-shipped May 28 (a city-page "last updated" date that drifted into the data).
The resolved banner DERIVES its date from resolved_iso formatted in Pacific time, so a
hardcoded literal can't drift again. resolved_iso = 2026-05-27T02:30:00Z == May 26 7:30pm PDT.
(2026-05-31; root-caused via /investigate, date verified via /deep-research.)
"""
import json
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO = Path(__file__).resolve().parent.parent
DASH = REPO / "dashboard.html"
STATUS = REPO / "status.json"


def test_resolved_iso_is_may26_pacific():
    s = json.load(open(STATUS, encoding="utf-8"))
    iso = (s.get("incident") or {}).get("resolved_iso")
    return {"passed": iso == "2026-05-27T02:30:00Z",
            "details": f"resolved_iso={iso} (want 2026-05-27T02:30:00Z = May 26 7:30pm PDT, not the old May 28)"}


def test_meta_resolved_date_corrected():
    t = DASH.read_text(encoding="utf-8")
    ok = "resolved May 26" in t and "resolved May 28" not in t
    return {"passed": ok,
            "details": f"meta has 'resolved May 26'={'resolved May 26' in t}; still has 'resolved May 28'={'resolved May 28' in t}"}


def test_resolved_banner_derives_date_in_pacific():
    t = DASH.read_text(encoding="utf-8")
    m = re.search(r'"info\.resolved\.banner":\s*\{\s*en:\s*"([^"]*)"', t)
    banner = m.group(1) if m else ""
    has_placeholder = "{date}" in banner
    no_hardcoded = not re.search(r"\b(May|June)\s+\d", banner)
    pacific = "America/Los_Angeles" in t
    ok = bool(banner) and has_placeholder and no_hardcoded and pacific
    return {"passed": ok,
            "details": f"placeholder={has_placeholder} no_hardcoded_date={no_hardcoded} pacific_tz={pacific}"}
