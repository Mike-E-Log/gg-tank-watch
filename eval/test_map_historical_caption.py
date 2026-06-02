"""Guard: the Map tab carries an inline historical caption framing the evacuation zone as a
lifted, PAST order (2026-06-02).

The masthead's global 'Historical archive - May 21-26, 2026' dateline + ARCHIVE pill already
frame the whole app on every tab, and the News/Info tabs each carry their own inline historical
note. The Map was the one tab with no on-surface note — and a stale evac-zone polygon is the
most 'live-looking' element on the whole site, so it gets its own resolved-note-style caption
ABOVE the map. The route to officials is intentionally NOT repeated here (the persistent global
safety strip is pinned above the map and carries it; per-surface routing was de-duplicated).

Anchored on the full markup tag / i18n value — class names also appear in the inline <style>,
so a bare-name find() would measure CSS order, not DOM order (see eval-find-hits-css-before-html).
"""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_map_historical_caption_present_and_localized():
    text = DASHBOARD.read_text(encoding="utf-8")
    has_markup = 'data-i18n="map.historical"' in text
    has_i18n = '"map.historical": { en:' in text
    return {"passed": has_markup and has_i18n,
            "details": "map historical caption markup + en string present"
            if (has_markup and has_i18n) else f"markup={has_markup} i18n={has_i18n}"}


def test_map_historical_caption_frames_zone_as_past():
    """Honesty: the caption must frame the evacuation zone as a HISTORICAL, lifted order with a
    date — not a live boundary. Guards against copy that drops 'historical'/'lifted' and reads
    as a current order."""
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r'"map\.historical":\s*\{\s*en:\s*"([^"]*)"', text)
    val = (m.group(1) if m else "").lower()
    historical = "historical" in val
    zone = "evacuation" in val
    past = "lifted" in val or "ended" in val
    dated = "2026" in val
    ok = bool(val) and historical and zone and past and dated
    return {"passed": ok,
            "details": "caption frames zone as historical + lifted + dated" if ok
            else f"historical={historical} zone={zone} past={past} dated={dated}"}


def test_map_historical_caption_above_map():
    """Layout: the caption must sit inside the Map panel and BEFORE the map element, so it reads
    as a label for the zone rather than buried below it."""
    text = DASHBOARD.read_text(encoding="utf-8")
    i_panel = text.find('id="panel-map"')
    i_note = text.find('data-i18n="map.historical"')
    i_map = text.find('id="maplibre-map"')
    ok = -1 < i_panel < i_note < i_map
    return {"passed": ok,
            "details": "order: panel-map < caption < maplibre-map" if ok
            else f"bad order panel={i_panel} note={i_note} map={i_map}",
            "metrics": {"panel": i_panel, "note": i_note, "map": i_map}}
