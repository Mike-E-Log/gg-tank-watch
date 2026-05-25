"""Schema validation for status.json and config.json.

Pure stdlib — checks required fields, types, and a few semantic invariants.
If the schema evolves, bump schema_version in code and update the expectations here.
"""

from __future__ import annotations

import json
from pathlib import Path

CATEGORY = "schema"

REPO_ROOT = Path(__file__).resolve().parent.parent
STATUS_PATH = REPO_ROOT / "status.json"
CONFIG_PATH = REPO_ROOT / "config.json"


def _check_keys(obj, required, label):
    missing = [k for k in required if k not in obj]
    return [] if not missing else [f"{label}: missing keys {missing}"]


def test_status_json_required_fields():
    if not STATUS_PATH.exists():
        return {"passed": False, "details": f"status.json not found at {STATUS_PATH} — run the writer first"}
    snap = json.loads(STATUS_PATH.read_text())
    fails = []
    fails += _check_keys(snap, [
        "schema_version", "last_updated_iso", "next_check_at_iso", "stale_after_iso",
        "incident", "tank", "evacuation", "you", "official_statements",
        "sources_checked", "schools_closed",
        "breaking", "breaking_reason", "breaking_since_iso", "_meta"
    ], "status.json")
    if "incident" in snap:
        fails += _check_keys(snap["incident"], ["name", "facility", "started_iso", "status_headline", "severity"], "incident")
    if "evacuation" in snap:
        fails += _check_keys(snap["evacuation"], ["residents", "area_sq_mi", "boundary_text", "lifted", "expanded_since_yesterday"], "evacuation")
    if "you" in snap:
        fails += _check_keys(snap["you"], ["zone_status", "address_checker_url"], "you")
    if "_meta" in snap:
        fails += _check_keys(snap["_meta"], ["injuries", "statement_hashes"], "_meta")
    return {
        "passed": len(fails) == 0,
        "details": "all keys present" if not fails else "; ".join(fails),
    }


def test_status_json_types():
    if not STATUS_PATH.exists():
        return {"passed": False, "details": "status.json not found"}
    snap = json.loads(STATUS_PATH.read_text())
    issues = []
    if snap.get("schema_version") != 1:
        issues.append(f"schema_version expected 1, got {snap.get('schema_version')}")
    if not isinstance(snap.get("breaking"), bool):
        issues.append("breaking must be bool")
    if snap.get("incident", {}).get("severity") not in {"low", "moderate", "high", "critical"}:
        issues.append(f"severity invalid: {snap.get('incident', {}).get('severity')}")
    if not isinstance(snap.get("official_statements"), list):
        issues.append("official_statements must be list")
    if not isinstance(snap.get("sources_checked"), list):
        issues.append("sources_checked must be list")
    iso = snap.get("last_updated_iso", "")
    if not (isinstance(iso, str) and iso.endswith("Z") and len(iso) >= 20):
        issues.append(f"last_updated_iso shape wrong: {iso!r}")
    return {
        "passed": len(issues) == 0,
        "details": "all types valid" if not issues else "; ".join(issues),
    }


def test_status_json_semantic_invariants():
    if not STATUS_PATH.exists():
        return {"passed": False, "details": "status.json not found"}
    snap = json.loads(STATUS_PATH.read_text())
    issues = []
    if snap.get("breaking") is True and not snap.get("breaking_reason"):
        issues.append("breaking=true but breaking_reason is empty")
    if snap.get("breaking") is True and not snap.get("breaking_since_iso"):
        issues.append("breaking=true but breaking_since_iso is null")
    if snap.get("evacuation", {}).get("residents", 0) < 0:
        issues.append("residents negative")
    tank_temp = snap.get("tank", {}).get("temp_f")
    if tank_temp is not None and not (0 <= tank_temp <= 500):
        issues.append(f"tank temp_f out of range: {tank_temp}")
    return {
        "passed": len(issues) == 0,
        "details": "all invariants hold" if not issues else "; ".join(issues),
    }


def test_config_json_required_fields():
    cfg = json.loads(CONFIG_PATH.read_text())
    fails = []
    fails += _check_keys(cfg, ["zone_status", "dashboard_refresh_seconds", "stale_after_minutes", "incident", "map", "schema_version"], "config.json")
    if "map" in cfg:
        m = cfg["map"]
        fails += _check_keys(m, ["facility", "evac_polygon", "blast_zones_mi", "plume_max_length_mi", "plume_cone_degrees", "weather_station"], "config.json.map")
        if "facility" in m:
            fails += _check_keys(m["facility"], ["lat", "lon", "label"], "config.json.map.facility")
        if "evac_polygon" in m:
            if not isinstance(m["evac_polygon"], list) or len(m["evac_polygon"]) < 3:
                fails.append("evac_polygon must be a polygon with >=3 vertices")
        if "blast_zones_mi" in m:
            for i, b in enumerate(m["blast_zones_mi"]):
                if not all(k in b for k in ("radius", "label", "color")):
                    fails.append(f"blast_zones_mi[{i}] missing radius/label/color")
    return {
        "passed": len(fails) == 0,
        "details": "all keys present" if not fails else "; ".join(fails),
    }


def test_config_facility_coords_in_southern_california():
    cfg = json.loads(CONFIG_PATH.read_text())
    f = cfg["map"]["facility"]
    in_socal = (32.5 < f["lat"] < 34.5) and (-119.0 < f["lon"] < -117.0)
    return {
        "passed": in_socal,
        "details": f"facility at ({f['lat']}, {f['lon']}) - expected to be in southern California",
    }
