"""Date-sanity tests for scripts/update_status.py (data-quality: timestamp validation).

incident_resolved_iso is the one timestamp that drives a safety state: a non-null
value forces severity to "low" (all-clear). A malformed or future-dated value —
a model parse artifact or hallucination — must never be honored. These tests
supply corroborating sources (so the P0-1 corroboration gate passes) to isolate
the date validator: with corroboration satisfied, only a *valid* resolved time
should produce an all-clear.

Governing rule (docs/DATA_QUALITY.md): a wrong "you're safe" is far worse than a
wrong "still dangerous".
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
WRITER = REPO_ROOT / "scripts" / "update_status.py"
SANDBOX = Path(__file__).resolve().parent / ".last_run" / "dates"

# Two corroborating sources, one official — enough for the P0-1 gate to pass, so
# any suppression below is the date validator's doing, not corroboration's.
GOOD_SOURCES = [
    {"url": "https://ocfa.org/incident", "title": "OCFA update"},
    {"url": "https://latimes.com/story", "title": "LA Times"},
]


def _reset_sandbox():
    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    SANDBOX.mkdir(parents=True)
    (SANDBOX / "public").mkdir()
    (SANDBOX / "public" / "config.json").write_text(json.dumps({
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
    sp = SANDBOX / "public" / "status.json"
    return json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else None


# Ongoing evacuation (residents present, not lifted) so resolved_iso is the ONLY
# all-clear signal — isolates the date validator from the evacuation_lifted path.
_ONGOING = {"evacuation_residents": 50000, "evacuation_lifted": False}


def test_future_resolved_iso_suppressed():
    """A resolved time in the future (clock-impossible) is nulled; no all-clear."""
    _reset_sandbox()
    _tick(_ONGOING)
    snap = _tick({**_ONGOING,
        "incident_resolved_iso": "2099-01-01T00:00:00Z",
        "sources_checked": GOOD_SOURCES,
    })
    resolved = snap["incident"].get("resolved_iso")
    severity = snap["incident"]["severity"]
    return {
        "passed": resolved is None and severity == "high",
        "details": f"resolved_iso={resolved!r}, severity={severity}",
    }


def test_malformed_resolved_iso_suppressed():
    """A non-ISO resolved time is nulled rather than honored as an all-clear."""
    _reset_sandbox()
    _tick(_ONGOING)
    snap = _tick({**_ONGOING,
        "incident_resolved_iso": "sometime last week",
        "sources_checked": GOOD_SOURCES,
    })
    resolved = snap["incident"].get("resolved_iso")
    severity = snap["incident"]["severity"]
    return {
        "passed": resolved is None and severity == "high",
        "details": f"resolved_iso={resolved!r}, severity={severity}",
    }


def test_valid_resolved_iso_honored():
    """A well-formed past resolved time, corroborated, is still honored (no over-suppression)."""
    _reset_sandbox()
    _tick(_ONGOING)
    snap = _tick({**_ONGOING,
        "incident_resolved_iso": "2026-05-24T12:00:00Z",
        "sources_checked": GOOD_SOURCES,
    })
    resolved = snap["incident"].get("resolved_iso")
    severity = snap["incident"]["severity"]
    return {
        "passed": resolved == "2026-05-24T12:00:00Z" and severity == "low",
        "details": f"resolved_iso={resolved!r}, severity={severity}",
    }
