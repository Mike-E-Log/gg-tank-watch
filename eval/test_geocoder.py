"""Live regression for the Nominatim geocoder.

Requires internet. Skipped via `python run_all.py --skip integration`.

Holds known intersections to known coords with a tolerance — if Nominatim
returns a substantially different result, the test fails and we know to
investigate (city changed, OSM data shifted, or our bias is wrong).
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

CATEGORY = "integration"

NOMINATIM = "https://nominatim.openstreetmap.org/search"
BIAS = "Orange County, CA"
VIEWBOX = (-118.10, 33.85, -117.85, 33.65)
TOL_DEG = 0.02  # ~1.4 miles


def _geocode(q: str) -> tuple[float, float, str] | None:
    has_state = any(tok in q.upper() for tok in ("CA", "CALIFORNIA"))
    q_with_bias = q if has_state else f"{q}, {BIAS}"
    url = f"{NOMINATIM}?format=json&limit=1&q={urllib.parse.quote(q_with_bias)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "GG-Dashboard-Eval/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            arr = json.loads(resp.read().decode("utf-8"))
        if arr:
            return float(arr[0]["lat"]), float(arr[0]["lon"]), arr[0].get("display_name", "")
    except Exception:
        pass
    # Viewbox fallback
    w, n, e, s = VIEWBOX
    url = f"{NOMINATIM}?format=json&limit=1&q={urllib.parse.quote(q)}&viewbox={w},{n},{e},{s}&bounded=1"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "GG-Dashboard-Eval/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            arr = json.loads(resp.read().decode("utf-8"))
        if arr:
            return float(arr[0]["lat"]), float(arr[0]["lon"]), arr[0].get("display_name", "")
    except Exception:
        pass
    return None


def _check_intersection(q: str, expected_lat: float, expected_lon: float):
    res = _geocode(q.replace(" and ", " & "))
    if res is None:
        return {"passed": False, "details": f"geocoder returned no result for '{q}'", "metrics": {}}
    lat, lon, name = res
    dlat = abs(lat - expected_lat)
    dlon = abs(lon - expected_lon)
    within = dlat < TOL_DEG and dlon < TOL_DEG
    return {
        "passed": within,
        "details": f"got ({lat:.4f}, {lon:.4f}); expected ({expected_lat}, {expected_lon}); display_name starts: {name[:60]!r}",
        "metrics": {"lat": lat, "lon": lon, "expected_lat": expected_lat, "expected_lon": expected_lon, "dlat": dlat, "dlon": dlon},
    }


def test_magnolia_talbert():
    """The example the user gave; verified in earlier session: Fountain Valley."""
    return _check_intersection("Magnolia and Talbert", 33.7022, -117.9716)


def test_full_street_address_near_facility():
    """Full street address should geocode close to the GKN facility."""
    res = _geocode("12122 Western Ave, Garden Grove, CA")
    if res is None:
        return {"passed": False, "details": "geocoder returned no result", "metrics": {}}
    lat, lon, name = res
    # Facility is at (33.7858, -118.0050); expect within ~0.5 mi
    dlat = abs(lat - 33.7858)
    dlon = abs(lon - (-118.0050))
    return {
        "passed": dlat < 0.01 and dlon < 0.01,
        "details": f"got ({lat:.4f}, {lon:.4f}); facility (33.7858, -118.005)",
        "metrics": {"dlat": dlat, "dlon": dlon},
    }
