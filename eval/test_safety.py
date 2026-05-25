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


def compute_safety(pt_lat, pt_lon, cfg):
    """Returns dict matching the JS computeSafety() router: insideEvac, distance_mi, bearing_deg."""
    m = cfg["map"]
    fac = m["facility"]
    d_mi = _haversine_mi(pt_lat, pt_lon, fac["lat"], fac["lon"])
    br_deg = _bearing_deg(fac["lat"], fac["lon"], pt_lat, pt_lon)
    inside_evac = _point_in_polygon([pt_lat, pt_lon], m["evac_polygon"])
    return {"inside_evac": inside_evac, "distance_mi": d_mi, "bearing_deg": br_deg}


# ============ Tests ============

# Known points and expected safety levels.
# Trask & Harbor: (33.766, -117.920) — Garden Grove east of tank
# Magnolia & Ellis: (33.694, -117.972) — Fountain Valley south of tank
# Inside-evac point: somewhere in the polygon, e.g., (33.79, -118.00)
# Facility itself: should be CRITICAL

def test_facility_itself_is_near_zero_distance():
    cfg = _load_config()
    fac = cfg["map"]["facility"]
    s = compute_safety(fac["lat"], fac["lon"], cfg)
    return {
        "passed": s["distance_mi"] < 0.01,
        "details": f"distance={s['distance_mi']:.4f} mi (expected <0.01 mi at facility)",
    }


def test_trask_harbor_distance():
    cfg = _load_config()
    s = compute_safety(33.7660, -117.9202, cfg)
    return {
        "passed": s["distance_mi"] > 3.0,
        "details": f"distance={s['distance_mi']:.2f} mi (expected >3 mi)",
        "metrics": {"distance_mi": s["distance_mi"]},
    }


def test_magnolia_ellis_distance():
    cfg = _load_config()
    s = compute_safety(33.6935, -117.9717, cfg)
    return {
        "passed": s["distance_mi"] > 5.0,
        "details": f"distance={s['distance_mi']:.2f} mi (expected >5 mi)",
        "metrics": {"distance_mi": s["distance_mi"]},
    }


def test_inside_evac_polygon_detected():
    cfg = _load_config()
    # Point inside the polygon
    s = compute_safety(33.81, -118.02, cfg)
    return {
        "passed": s["inside_evac"] is True,
        "details": f"inside_evac={s['inside_evac']}, distance={s['distance_mi']:.2f}",
    }


def test_outside_evac_polygon_detected():
    cfg = _load_config()
    fac = cfg["map"]["facility"]
    # Point 3 mi south of facility — below polygon's south edge (33.7639)
    dlat = -3.0 / 69.0
    s = compute_safety(fac["lat"] + dlat, fac["lon"], cfg)
    return {
        "passed": s["inside_evac"] is False,
        "details": f"inside_evac={s['inside_evac']}, distance={s['distance_mi']:.2f}",
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


def test_no_authored_hazard_verdict():
    html = open("dashboard.html", encoding="utf-8").read()
    banned = ["within injury radius or plume", "blast_zones_mi", "layers.plume", "ELEVATED — within injury radius"]
    found = [b for b in banned if b in html]
    assert not found, f"authored-hazard remnants still present: {found}"


def test_checker_routes_to_official():
    html = open("dashboard.html", encoding="utf-8").read()
    assert "ggcity.org/emergency" in html, "address checker must route to official source"
