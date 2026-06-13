"""Guard (T12 / locked decision D2, archive pivot 2026-06-01): the Map "Check Address" Zonehaven
button is DELETED from the frozen archive — a live address-lookup tool has no place in a
historical record, and reviewers chose deletion over relocation. The historical evacuation
polygon + legend remain.
"""
from pathlib import Path

CATEGORY = "behavioral"
REPO = Path(__file__).resolve().parent.parent
DASH = REPO / "public" / "dashboard.html"


def test_zone_check_button_removed():
    """The map's 'Check Address' button is uniquely identified by its class (zone-check-btn) and
    i18n key (map.check_zone). NB: the community.zonehaven.com URL legitimately REMAINS in the
    Official-sources routing list (info.official.zonehaven, an 'Official'-badged link) — that is a
    routing reference, not the deleted live-lookup button, so it is intentionally NOT checked here."""
    text = DASH.read_text(encoding="utf-8")
    gone = "zone-check-btn" not in text and '"map.check_zone"' not in text
    return {"passed": gone,
            "details": "zone-check-btn class + map.check_zone i18n removed" if gone
            else "zone-check button artifacts still present"}


def test_static_map_actions_container_removed():
    """Removing the button empties its action band; the container + its CSS go too (no empty box)."""
    text = DASH.read_text(encoding="utf-8")
    gone = "static-map-actions" not in text
    return {"passed": gone,
            "details": "empty static-map-actions container + CSS removed" if gone
            else "static-map-actions still present"}


def test_evac_polygon_and_legend_intact():
    """The historical evacuation polygon/legend must survive the button deletion."""
    text = DASH.read_text(encoding="utf-8")
    present = '"legend.evac"' in text and "evacuation" in text.lower()
    return {"passed": present,
            "details": "evac legend + polygon markers retained" if present
            else "evac map markers missing after deletion!"}
