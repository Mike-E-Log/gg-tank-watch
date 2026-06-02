"""Regression guard: every map-legend marker label reads as a historical archive.

The legend is the key to the three map markers. In the frozen archive every label
must carry the same past-tense / incident framing the rest of the app uses, not the
bare live-feed words:
  - evac polygon -> "Former evac area"  (guarded by test_legend_label_frozen.py),
  - shelter swatch -> "Former shelter"  (the May 21-26 shelters are closed),
  - facility swatch -> "Tank facility"  (the GKN MMA tank-leak site).

"Former facility" is deliberately NOT used: the GKN plant still physically exists,
so a past-tense label there would mislead -- "Tank facility" is a neutral descriptor
of the incident site. These guards fail the build if a label reverts to its bare
live form ("Shelter", "Facility"). Pure text guard; the eval harness has no JS
runtime. Set 2026-06-02 with the archive-label adaptation.
"""
import re
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def _text():
    return DASHBOARD.read_text(encoding="utf-8")


def _shelter_row(text):
    """(data_i18n_key, visible_text) of the legend's shelter row, or (None, None)."""
    m = re.search(
        r'legend-icon-shelter[^>]*></span>\s*<span data-i18n="([^"]+)">([^<]*)</span>',
        text,
    )
    return (m.group(1), m.group(2).strip()) if m else (None, None)


def _facility_label(text):
    """Visible text of the legend's facility row, or None."""
    m = re.search(r'legend-icon-facility[^>]*></span>\s*([^<]*)</div>', text)
    return m.group(1).strip() if m else None


def _i18n_value(text, key):
    """en value of an i18n key, or None."""
    m = re.search(r'"' + re.escape(key) + r'":\s*\{\s*en:\s*"([^"]*)"', text)
    return m.group(1) if m else None


def test_legend_shelter_is_former_shelter():
    """The shelter legend row + its i18n value both read 'Former shelter'."""
    text = _text()
    key, label = _shelter_row(text)
    i18n = _i18n_value(text, "legend.shelter")
    ok = label == "Former shelter" and i18n == "Former shelter"
    return {
        "passed": ok,
        "details": "legend shelter label is the archive form 'Former shelter'"
        if ok
        else f"legend shelter label not archive-framed: row text={label!r} "
        f"(key={key!r}), i18n legend.shelter={i18n!r} (expected 'Former shelter')",
        "metrics": {"row_label": label or "", "i18n_value": i18n or ""},
    }


def test_legend_facility_is_tank_facility():
    """The facility legend row reads 'Tank facility', not the bare 'Facility'."""
    label = _facility_label(_text())
    ok = label == "Tank facility"
    return {
        "passed": ok,
        "details": "legend facility label is the archive form 'Tank facility'"
        if ok
        else f"legend facility label not archive-framed: {label!r} "
        "(expected 'Tank facility'; note 'Former facility' is rejected -- the plant still exists)",
        "metrics": {"row_label": label or ""},
    }
