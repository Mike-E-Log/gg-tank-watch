"""Behavioral tests for the safety-checker computation.

The actual computation lives in dashboard.html (JS). To test it in pure Python
without standing up a browser, this file reimplements the same math (haversine,
point-in-polygon, plume cone check) and grounds against the real config.json.

If the JS and Python implementations diverge, fix the divergence — the math
should be identical. The Python implementation here IS the spec; the JS is the
runtime. A failing test here means either the spec is wrong OR the runtime has
diverged.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config.json"


def _load_config():
    return json.loads(CONFIG_PATH.read_text())


def _haversine_mi(lat1, lon1, lat2, lon2):
    R = 3958.8
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def _bearing_deg(lat1, lon1, lat2, lon2):
    φ1 = math.radians(lat1)
    φ2 = math.radians(lat2)
    Δλ = math.radians(lon2 - lon1)
    y = math.sin(Δλ) * math.cos(φ2)
    x = math.cos(φ1) * math.sin(φ2) - math.sin(φ1) * math.cos(φ2) * math.cos(Δλ)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def _point_in_polygon(pt, polygon):
    x, y = pt[1], pt[0]
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i][1], polygon[i][0]
        xj, yj = polygon[j][1], polygon[j][0]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _angle_diff(a, b):
    d = abs(a - b) % 360
    return d if d <= 180 else 360 - d


def compute_safety(pt_lat, pt_lon, cfg, wind=None):
    """Returns dict with level, distance_mi, bearing_deg, factors."""
    m = cfg["map"]
    fac = m["facility"]
    d_mi = _haversine_mi(pt_lat, pt_lon, fac["lat"], fac["lon"])
    br_deg = _bearing_deg(fac["lat"], fac["lon"], pt_lat, pt_lon)

    plume_reach = False
    downwind = False
    if wind:
        plume_heading = (wind["directionDeg"] + 180) % 360
        spread = (m.get("plume_cone_degrees", 30)) / 2
        within = _angle_diff(br_deg, plume_heading) <= spread
        max_len = max(1.0, min(m.get("plume_max_length_mi", 4), (wind.get("speedMph", 5)) * 0.4))
        downwind = within
        plume_reach = within and d_mi <= max_len

    factors = []
    inside_evac = _point_in_polygon([pt_lat, pt_lon], m["evac_polygon"])
    if inside_evac:
        factors.append(("evac", 3))
    blasts = sorted(m["blast_zones_mi"], key=lambda b: b["radius"])
    blast_hit = None
    for b in blasts:
        if d_mi <= b["radius"]:
            blast_hit = b
            break
    if blast_hit:
        sev = 4 if blast_hit["radius"] < 0.2 else (3 if blast_hit["radius"] < 0.5 else 2)
        factors.append(("blast", sev))
    if plume_reach:
        factors.append(("plume", 2))
    elif downwind:
        factors.append(("downwind", 1))

    max_sev = max((f[1] for f in factors), default=0)
    if max_sev >= 4:
        level = "critical"
    elif max_sev == 3:
        level = "high"
    elif max_sev == 2:
        level = "elevated"
    elif max_sev == 1:
        level = "elevated"
    else:
        level = "safe"
    return {"level": level, "distance_mi": d_mi, "bearing_deg": br_deg, "factors": factors, "inside_evac": inside_evac, "plume_reach": plume_reach}


# ============ Tests ============

# Known points and expected safety levels.
# Trask & Harbor: (33.766, -117.920) — Garden Grove east of tank
# Magnolia & Ellis: (33.694, -117.972) — Fountain Valley south of tank
# Inside-evac point: somewhere in the polygon, e.g., (33.79, -118.00)
# Facility itself: should be CRITICAL

def test_facility_itself_is_critical():
    cfg = _load_config()
    fac = cfg["map"]["facility"]
    s = compute_safety(fac["lat"], fac["lon"], cfg)
    return {
        "passed": s["level"] == "critical" and s["distance_mi"] < 0.01,
        "details": f"level={s['level']}, distance={s['distance_mi']:.4f} mi",
    }


def test_trask_harbor_is_safe():
    cfg = _load_config()
    s = compute_safety(33.7660, -117.9202, cfg)
    return {
        "passed": s["level"] == "safe" and s["distance_mi"] > 3.0,
        "details": f"level={s['level']}, distance={s['distance_mi']:.2f} mi (expected SAFE, >3 mi)",
        "metrics": {"distance_mi": s["distance_mi"], "level": s["level"]},
    }


def test_magnolia_ellis_is_safe():
    cfg = _load_config()
    s = compute_safety(33.6935, -117.9717, cfg)
    return {
        "passed": s["level"] == "safe" and s["distance_mi"] > 5.0,
        "details": f"level={s['level']}, distance={s['distance_mi']:.2f} mi (expected SAFE, >5 mi)",
        "metrics": {"distance_mi": s["distance_mi"], "level": s["level"]},
    }


def test_inside_evac_polygon_is_high():
    cfg = _load_config()
    # Point inside the polygon but outside blast zones
    s = compute_safety(33.81, -118.02, cfg)
    return {
        "passed": s["level"] in ("high", "critical") and s["inside_evac"] is True,
        "details": f"level={s['level']}, inside_evac={s['inside_evac']}, distance={s['distance_mi']:.2f}",
    }


def test_inside_moderate_blast_is_high():
    cfg = _load_config()
    fac = cfg["map"]["facility"]
    # Point 0.2 mi north of facility — inside moderate damage (0.31 mi)
    dlat = 0.2 / 69.0
    s = compute_safety(fac["lat"] + dlat, fac["lon"], cfg)
    return {
        "passed": s["level"] in ("high", "critical"),
        "details": f"level={s['level']}, distance={s['distance_mi']:.4f} mi (expected HIGH or CRITICAL)",
    }


def test_inside_primary_blast_is_critical():
    cfg = _load_config()
    fac = cfg["map"]["facility"]
    # Point 0.05 mi north — inside 20 PSI overpressure zone
    dlat = 0.05 / 69.0
    s = compute_safety(fac["lat"] + dlat, fac["lon"], cfg)
    return {
        "passed": s["level"] == "critical",
        "details": f"level={s['level']}, distance={s['distance_mi']:.4f} mi (expected CRITICAL)",
    }


def test_downwind_inside_plume_elevates():
    cfg = _load_config()
    fac = cfg["map"]["facility"]
    # Wind FROM 0° (north) means plume blows TO 180° (south).
    # Place point 2 mi due south of facility — outside evac polygon (south edge at
    # lat 33.7639; facility at 33.7858; 2 mi south = 33.7568, beyond polygon).
    # Plume length at 10mph = 10 * 0.4 = 4 mi (capped). 2mi < 4mi -> inside plume.
    # Outside all blast zones (>0.93 mi).
    wind = {"directionDeg": 0.0, "speedMph": 10.0}
    dlat = -2.0 / 69.0
    s = compute_safety(fac["lat"] + dlat, fac["lon"], cfg, wind)
    return {
        "passed": s["level"] == "elevated" and s["plume_reach"] is True and s["inside_evac"] is False,
        "details": f"level={s['level']}, plume_reach={s['plume_reach']}, inside_evac={s['inside_evac']}, factors={s['factors']}",
    }


def test_upwind_far_is_safe_even_with_wind():
    cfg = _load_config()
    fac = cfg["map"]["facility"]
    # Wind FROM 180° (south), plume blows north. Place point SOUTH of facility (upwind) → safe.
    wind = {"directionDeg": 180.0, "speedMph": 10.0}
    dlat = -3.0 / 69.0  # 3 mi south
    s = compute_safety(fac["lat"] + dlat, fac["lon"], cfg, wind)
    return {
        "passed": s["level"] == "safe" and s["plume_reach"] is False,
        "details": f"level={s['level']}, plume_reach={s['plume_reach']}, distance={s['distance_mi']:.2f}",
    }


def test_haversine_known_distance():
    # Trask&Harbor (33.766, -117.920) to facility (33.7858, -118.005)
    # Manual calc: ~5.0-5.5 mi
    d = _haversine_mi(33.766, -117.920, 33.7858, -118.005)
    return {
        "passed": 4.5 < d < 5.5,
        "details": f"haversine returned {d:.3f} mi (expected 4.5-5.5)",
        "metrics": {"distance": d},
    }
