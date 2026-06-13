"""Guard (audit 2026-06-04): the static satellite pages (terms.html,
accessibility.html) must describe the SAME app the dashboard actually ships.

Both pages were written for a pre-conduit-pivot, more-featured build and drifted:
they advertised a "check your address" tool + "blast and plume estimates"
(removed in the conduit pivot), Vietnamese language support (the app is
English-only by design, G1), a "Leaflet" map (it is MapLibre GL), "wind
conditions" (the wind indicator was removed), and system-preference dark mode
(the dashboard uses a manual toggle). For an honesty-thesis project, a legal /
accessibility page over-describing the app is itself a integrity defect.

`test_no_vietnamese_residue.py` only scans dashboard.html, which is exactly why
this drift slipped through; these guards extend the honesty floor to the two
satellite pages. Pure text guards (the harness has no JS runtime).
"""
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
ACCESSIBILITY = REPO_ROOT / "public" / "accessibility.html"
TERMS = REPO_ROOT / "public" / "terms.html"
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"

# Stale/false claims that must not appear in accessibility.html (case-insensitive).
ACCESS_FORBIDDEN = ("vietnamese", "leaflet", "wind conditions", "system preference")
# Removed-feature references that must not appear in terms.html (case-insensitive).
TERMS_FORBIDDEN = ("check your address", "blast", "plume", "address results")


def test_accessibility_html_matches_shipped_app():
    """accessibility.html must not claim removed/never-shipped features (VI / Leaflet / wind / system-pref)."""
    text = ACCESSIBILITY.read_text(encoding="utf-8").lower()
    bad = [tok for tok in ACCESS_FORBIDDEN if tok in text]
    return {
        "passed": not bad,
        "details": "accessibility.html matches the shipped app"
        if not bad
        else "accessibility.html still claims removed/false features: " + ", ".join(bad),
        "metrics": {"stale_claims": len(bad)},
    }


def test_terms_html_no_removed_features():
    """terms.html must not describe the removed address-checker / blast / plume tools."""
    text = TERMS.read_text(encoding="utf-8").lower()
    bad = [tok for tok in TERMS_FORBIDDEN if tok in text]
    return {
        "passed": not bad,
        "details": "terms.html matches the conduit app"
        if not bad
        else "terms.html still describes removed features: " + ", ".join(bad),
        "metrics": {"stale_claims": len(bad)},
    }


def test_summary_outcome_unambiguous():
    """The Summary outcome must not say '0 displaced' (misleading next to ~50,000 evacuated)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    bad = "0 displaced" in text
    return {
        "passed": not bad,
        "details": "Summary outcome wording is unambiguous"
        if not bad
        else 'dashboard.html still says "0 displaced" (reads as conflicting with ~50,000 evacuated)',
        "metrics": {"ambiguous_outcome": int(bad)},
    }
