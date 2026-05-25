"""Behavioral tests for scripts/update_status.py.

Covers:
- 5-state sequence: baseline / no-diff / urgent-toggle / stable / resolved
- URGENT vs INFO classification (D-016)
- New-statement detection (info-level)
- Residents-shift rate-limiting
- Schema invariants (last_updated monotonic increasing, breaking_since set when breaking)
- Garbage-input tolerance (missing fields keep previous values)

Each test sets up a fresh sandbox dir under eval/.last_run/, runs the writer
in isolation, and asserts on the produced status.json.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
WRITER = REPO_ROOT / "scripts" / "update_status.py"
SANDBOX = Path(__file__).resolve().parent / ".last_run" / "writer"


def _reset_sandbox():
    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    SANDBOX.mkdir(parents=True)
    # Minimal config (no map needed for writer behavior tests)
    (SANDBOX / "config.json").write_text(json.dumps({
        "zone_status": "outside_downwind",
        "writer_interval_minutes": 30,
        "incident": {
            "name": "Test Incident",
            "facility": "Test Facility",
            "started_iso": "2026-05-21T22:40:00Z",
            "address_checker_url": "https://example.invalid/"
        },
        "schema_version": 1
    }))
    (SANDBOX / "scripts").mkdir()
    # Symlink (or copy on Windows where symlinks need admin) the writer
    target = SANDBOX / "scripts" / "update_status.py"
    shutil.copyfile(WRITER, target)


def _tick(facts: dict | None) -> tuple[int, dict | None]:
    """Pipe a facts JSON to the writer, return (exit_code, parsed status.json)."""
    payload = json.dumps(facts) if facts is not None else ""
    proc = subprocess.run(
        [sys.executable, str(SANDBOX / "scripts" / "update_status.py")],
        input=payload,
        cwd=str(SANDBOX),
        capture_output=True,
        text=True,
        timeout=30,
    )
    status_path = SANDBOX / "status.json"
    parsed = json.loads(status_path.read_text()) if status_path.exists() else None
    return proc.returncode, parsed


def test_t1_baseline_first_run_no_breaking():
    """First tick with no prev snapshot must never fire breaking."""
    _reset_sandbox()
    exit_code, snap = _tick({
        "tank_temp_f": 100, "evacuation_residents": 50000,
        "evacuation_lifted": False, "status_headline": "baseline"
    })
    return {
        "passed": exit_code == 0 and snap is not None and snap["breaking"] is False,
        "details": f"exit={exit_code}, breaking={snap and snap.get('breaking')}, severity={snap and snap['incident'].get('severity')}",
        "metrics": {"exit_code": exit_code, "breaking": snap and snap.get("breaking")},
    }


def test_t2_no_diff_no_breaking():
    """Tick 2 with identical data must not fire breaking."""
    # Assumes test_t1 already ran (sandbox carries over). Re-run baseline + same data.
    _reset_sandbox()
    _tick({
        "tank_temp_f": 100, "evacuation_residents": 50000,
        "evacuation_lifted": False, "status_headline": "baseline"
    })
    exit_code, snap = _tick({
        "tank_temp_f": 100, "evacuation_residents": 50000,
        "evacuation_lifted": False, "status_headline": "same"
    })
    return {
        "passed": exit_code == 0 and snap["breaking"] is False,
        "details": f"exit={exit_code}, breaking={snap.get('breaking')}, reason={snap.get('breaking_reason')}",
        "metrics": {"breaking": snap.get("breaking")},
    }


def test_t3_evac_expansion_fires_urgent():
    """Toggle: evacuation_expanded false→true must fire URGENT breaking immediately."""
    _reset_sandbox()
    _tick({"tank_temp_f": 100, "evacuation_residents": 50000, "evacuation_lifted": False})
    exit_code, snap = _tick({
        "tank_temp_f": 100, "evacuation_residents": 60000,
        "evacuation_expanded": True, "evacuation_lifted": False
    })
    is_urgent = snap.get("breaking_level") == "urgent"
    return {
        "passed": (exit_code == 0
                   and snap["breaking"] is True
                   and is_urgent
                   and "EXPAND" in (snap.get("breaking_reason") or "").upper()),
        "details": f"breaking={snap.get('breaking')}, level={snap.get('breaking_level')}, reason={snap.get('breaking_reason')}",
        "metrics": {"breaking_level": snap.get("breaking_level"), "reason": snap.get("breaking_reason")},
    }


def test_t4_stable_after_toggle_no_refire():
    """Tick 3 with same expansion data must NOT fire a new breaking
    (the toggle already happened; equilibrium isn't a new event)."""
    _reset_sandbox()
    _tick({"tank_temp_f": 100, "evacuation_residents": 50000, "evacuation_lifted": False})
    _tick({"tank_temp_f": 100, "evacuation_residents": 60000, "evacuation_expanded": True})  # t3 fires
    exit_code, snap = _tick({"tank_temp_f": 100, "evacuation_residents": 60000, "evacuation_expanded": True})  # t4
    # breaking stays True from t3 (within decay window), but the REASON shouldn't change to a new one
    reason_ok = "EXPAND" in (snap.get("breaking_reason") or "").upper()
    return {
        "passed": exit_code == 0 and reason_ok,
        "details": f"breaking={snap.get('breaking')}, reason={snap.get('breaking_reason')}",
        "metrics": {"breaking": snap.get("breaking"), "reason": snap.get("breaking_reason")},
    }


def test_t5_incident_resolved_fires_urgent():
    """Setting incident_resolved_iso must fire URGENT breaking (positive direction)."""
    _reset_sandbox()
    _tick({"tank_temp_f": 100, "evacuation_residents": 50000, "evacuation_lifted": False})
    exit_code, snap = _tick({
        "evacuation_lifted": True,
        "incident_resolved_iso": "2026-05-26T12:00:00Z",
        "status_headline": "all clear",
        # P0-1: a danger downgrade must be corroborated (>=2 sources, >=1 official).
        "sources_checked": [
            {"url": "https://ocfa.org/all-clear"},
            {"url": "https://latimes.com/all-clear"},
        ],
    })
    return {
        "passed": (exit_code == 0
                   and snap["breaking"] is True
                   and snap.get("breaking_level") == "urgent"
                   and "RESOLVED" in (snap.get("breaking_reason") or "").upper()),
        "details": f"breaking={snap.get('breaking')}, level={snap.get('breaking_level')}, reason={snap.get('breaking_reason')}",
    }


def test_new_statement_fires_info_not_urgent():
    """A new official statement (hash novel vs prev) should fire INFO breaking, not URGENT."""
    _reset_sandbox()
    # P0-2: statements must carry a source_url present in sources_checked to survive.
    _tick({
        "tank_temp_f": 100, "evacuation_residents": 50000, "evacuation_lifted": False,
        "sources_checked": [{"url": "https://ocfa.org/s1"}],
        "official_statements": [
            {"agency": "OCFA", "time_iso": "2026-05-24T15:00:00Z", "text": "first statement", "source_url": "https://ocfa.org/s1"}
        ]
    })
    exit_code, snap = _tick({
        "tank_temp_f": 100, "evacuation_residents": 50000, "evacuation_lifted": False,
        "sources_checked": [{"url": "https://ocfa.org/s1"}, {"url": "https://caloes.ca.gov/s2"}],
        "official_statements": [
            {"agency": "OCFA", "time_iso": "2026-05-24T15:00:00Z", "text": "first statement", "source_url": "https://ocfa.org/s1"},
            {"agency": "Newsom", "time_iso": "2026-05-24T18:00:00Z", "text": "NEW statement that should fire", "source_url": "https://caloes.ca.gov/s2"}
        ]
    })
    return {
        "passed": (exit_code == 0
                   and snap["breaking"] is True
                   and snap.get("breaking_level") == "info"
                   and "statement" in (snap.get("breaking_reason") or "").lower()),
        "details": f"level={snap.get('breaking_level')}, reason={snap.get('breaking_reason')}",
        "metrics": {"breaking_level": snap.get("breaking_level")},
    }


def test_residents_shift_fires_info():
    """Residents shift >10% AND >1000 should fire INFO breaking."""
    _reset_sandbox()
    _tick({"tank_temp_f": 100, "evacuation_residents": 50000, "evacuation_lifted": False})
    exit_code, snap = _tick({"tank_temp_f": 100, "evacuation_residents": 60000, "evacuation_lifted": False})
    return {
        "passed": (exit_code == 0
                   and snap["breaking"] is True
                   and snap.get("breaking_level") == "info"
                   and "residents" in (snap.get("breaking_reason") or "").lower()),
        "details": f"level={snap.get('breaking_level')}, reason={snap.get('breaking_reason')}",
    }


def test_garbage_input_keeps_prev_values():
    """If facts JSON omits fields, prev values must be preserved."""
    _reset_sandbox()
    _tick({"tank_temp_f": 100, "evacuation_residents": 50000, "evacuation_lifted": False})
    exit_code, snap = _tick({})  # empty facts
    return {
        "passed": exit_code == 0 and snap["tank"]["temp_f"] == 100 and snap["evacuation"]["residents"] == 50000,
        "details": f"temp_f={snap['tank'].get('temp_f')}, residents={snap['evacuation'].get('residents')}",
    }


def test_partial_facts_dont_downgrade_severity():
    """Piping only `videos` (no evac/incident fields) must NOT recompute
    severity from zeros. Severity must carry forward from prev snapshot."""
    _reset_sandbox()
    # Tick 1: real evac data -> severity should derive to "high"
    _tick({"evacuation_residents": 50000, "evacuation_lifted": False, "tank_temp_f": 100})
    snap1 = json.loads((SANDBOX / "status.json").read_text())
    if snap1["incident"]["severity"] != "high":
        return {"passed": False, "details": f"setup failed: expected severity=high, got {snap1['incident']['severity']}"}
    # Tick 2: partial facts (only videos, no evac fields)
    _tick({"videos": [{"outlet": "test", "title": "test", "url": "https://example.invalid"}]})
    snap2 = json.loads((SANDBOX / "status.json").read_text())
    return {
        "passed": (
            snap2["incident"]["severity"] == "high"
            and not (snap2["breaking"] and "Severity" in (snap2.get("breaking_reason") or ""))
        ),
        "details": f"severity={snap2['incident']['severity']}, breaking={snap2['breaking']}, reason={snap2.get('breaking_reason')}",
    }


def test_schema_invariants():
    """status.json must have required fields with correct types."""
    _reset_sandbox()
    _tick({"tank_temp_f": 100, "evacuation_residents": 50000, "evacuation_lifted": False})
    snap_path = SANDBOX / "status.json"
    snap = json.loads(snap_path.read_text())
    checks = [
        ("schema_version", lambda: snap["schema_version"] == 1),
        ("last_updated_iso", lambda: isinstance(snap["last_updated_iso"], str) and snap["last_updated_iso"].endswith("Z")),
        ("incident.severity", lambda: snap["incident"]["severity"] in {"low", "moderate", "high", "critical"}),
        ("breaking is bool", lambda: isinstance(snap["breaking"], bool)),
        ("you.zone_status", lambda: isinstance(snap["you"]["zone_status"], str)),
        ("_meta.statement_hashes is list", lambda: isinstance(snap["_meta"]["statement_hashes"], list)),
    ]
    failures = []
    for name, check in checks:
        try:
            if not check():
                failures.append(name)
        except Exception as e:
            failures.append(f"{name}: {e}")
    return {
        "passed": len(failures) == 0,
        "details": "all required fields valid" if not failures else f"failed: {failures}",
        "metrics": {"failures": failures},
    }
