"""Freshness-honesty tests for scripts/update_status.py (P0-3).

The stale-but-fresh-stamped failure class (F4/F6) collapses once "we wrote the
file" (last_updated_iso) and "we learned something new" (data_as_of_iso) are
distinct signals, and staleness keys off the latter. These tests pin that.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
WRITER = REPO_ROOT / "scripts" / "update_status.py"
SANDBOX = Path(__file__).resolve().parent / ".last_run" / "freshness"

MAX_AGE_MINUTES = 40  # must match update_status.MAX_AGE_MINUTES


def _reset_sandbox():
    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    SANDBOX.mkdir(parents=True)
    (SANDBOX / "config.json").write_text(json.dumps({
        "zone_status": "outside_downwind",
        "writer_interval_minutes": 30,
        "incident": {
            "name": "Test Incident", "facility": "Test Facility",
            "started_iso": "2026-05-21T22:40:00Z",
            "address_checker_url": "https://example.invalid/"
        },
        "schema_version": 1
    }))
    (SANDBOX / "scripts").mkdir()
    shutil.copyfile(WRITER, SANDBOX / "scripts" / "update_status.py")


def _tick(facts):
    payload = json.dumps(facts) if facts is not None else ""
    subprocess.run(
        [sys.executable, str(SANDBOX / "scripts" / "update_status.py")],
        input=payload, cwd=str(SANDBOX), capture_output=True, text=True, timeout=30,
    )
    sp = SANDBOX / "status.json"
    return json.loads(sp.read_text()) if sp.exists() else None


def _parse(iso):
    return datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def test_stale_after_is_data_as_of_plus_maxage():
    """stale_after_iso == data_as_of_iso + MAX_AGE (not write time)."""
    _reset_sandbox()
    snap = _tick({"evacuation_residents": 50000, "evacuation_lifted": False,
                  "status_headline": "real data"})
    daof = snap.get("data_as_of_iso")
    stale = snap.get("stale_after_iso")
    if not daof or not stale:
        return {"passed": False, "details": f"data_as_of_iso={daof}, stale_after_iso={stale}"}
    expected = _parse(daof) + timedelta(minutes=MAX_AGE_MINUTES)
    delta = abs((_parse(stale) - expected).total_seconds())
    return {
        "passed": delta <= 1,
        "details": f"data_as_of={daof}, stale_after={stale}, expected~={expected:%Y-%m-%dT%H:%M:%SZ}, delta={delta}s",
    }


def test_empty_facts_do_not_advance_data_as_of():
    """Tick 1 (real facts) sets data_as_of; tick 2 ({}) must NOT advance it."""
    _reset_sandbox()
    snap1 = _tick({"evacuation_residents": 50000, "evacuation_lifted": False,
                   "status_headline": "real"})
    daof1 = snap1.get("data_as_of_iso")
    snap2 = _tick({})
    daof2 = snap2.get("data_as_of_iso")
    return {
        "passed": daof1 is not None and daof1 == daof2,
        "details": f"data_as_of tick1={daof1}, tick2={daof2} (must be equal)",
    }


def test_all_null_facts_treated_as_no_data():
    """A facts blob of all-null fields does not advance data_as_of_iso."""
    _reset_sandbox()
    snap1 = _tick({"evacuation_residents": 50000, "evacuation_lifted": False,
                   "status_headline": "real"})
    daof1 = snap1.get("data_as_of_iso")
    snap2 = _tick({"tank_temp_f": None, "evacuation_residents": None,
                   "status_headline": None, "incident_resolved_iso": None})
    daof2 = snap2.get("data_as_of_iso")
    return {
        "passed": daof1 is not None and daof1 == daof2,
        "details": f"data_as_of tick1={daof1}, all-null tick2={daof2} (must be equal)",
    }


def test_last_updated_monotonic():
    """last_updated_iso never goes backwards across ticks."""
    _reset_sandbox()
    s1 = _tick({"evacuation_residents": 50000, "evacuation_lifted": False})
    s2 = _tick({})
    s3 = _tick({"status_headline": "later"})
    seq = [s1["last_updated_iso"], s2["last_updated_iso"], s3["last_updated_iso"]]
    monotonic = _parse(seq[0]) <= _parse(seq[1]) <= _parse(seq[2])
    return {
        "passed": monotonic,
        "details": f"last_updated sequence: {seq}",
    }
