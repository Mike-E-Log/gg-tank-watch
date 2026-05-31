"""Regression guard: the map wind indicator was removed (2026-05-31).

The reading came from a single NOAA station (KFUL, Fullerton Airport, ~5.7 mi
from the GKN tank). Against the nearest reporting station to the site it
pointed >=90deg the wrong way ~34% of the time (39% in light winds) and the
site was calm/no-direction 53% of the time -- a spatially-unrepresentative
direction a resident could misread as "which way the danger is blowing" on a
no-directives safety conduit. Residents are routed to officials (NWS/AirNow)
for authoritative wind/air quality.

These guards fail the build if any wind UI, JS, weather-API call, or wind i18n
key creeps back into dashboard.html. Pure text guards; no JS runtime needed
(the harness has none).
"""
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"

# Tokens that must no longer appear anywhere in dashboard.html after removal.
# All are wind-specific substrings -- none is contained in "downwind"
# (the zone_status value), so this cannot false-positive on resident-zone copy.
FORBIDDEN = (
    # overlay markup + CSS
    "map-wind-overlay", "map-wind", "wind-arrow", "wind-text-map", "wind-source",
    # JS state + functions (incl. orphaned helpers per D1)
    "fetchWind", "refreshWind", "scheduleWindRefresh", "updateWindDisplay",
    "cardinalFromDeg", "lastObservationTime", "WIND_BASE_MS", "WIND_MAX_MS",
    # weather API call + station config lookup
    "api.weather.gov", "weather_station",
    # i18n keys
    "wind.source", "wind.disclaimer", "wind.unavailable", "info.method.wind",
)


def test_no_wind_indicator_in_dashboard():
    """No wind UI/JS/API/i18n may reappear in dashboard.html (removed 2026-05-31)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    survivors = [tok for tok in FORBIDDEN if tok in text]
    return {
        "passed": not survivors,
        "details": "no wind-indicator artifacts in dashboard.html"
        if not survivors
        else "wind artifact(s) still present (should be removed): " + ", ".join(survivors),
        "metrics": {"survivors": len(survivors)},
    }


def test_map_aria_label_has_no_wind_claim():
    """The map aria-label must not advertise a wind-direction marker anymore."""
    text = DASHBOARD.read_text(encoding="utf-8")
    bad = "wind direction" in text.lower()
    return {
        "passed": not bad,
        "details": "no 'wind direction' claim in dashboard.html"
        if not bad
        else 'dashboard.html still says "wind direction" (stale aria-label?)',
        "metrics": {"wind_direction_mentions": int(bad)},
    }
