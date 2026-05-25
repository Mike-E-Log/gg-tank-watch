"""Anti-fabrication + corroboration tests for scripts/update_status.py (P0-1, P0-2).

The highest-value safety property: the published snapshot can never carry an
invented source URL, an unsourced "official" statement, or a single-source
"all-clear". Runs the writer in a sandbox (same pattern as test_writer.py) and
asserts on the produced status.json.

Governing rule (from docs/DATA_QUALITY.md): a wrong "you're safe" is far more
harmful than a wrong "still dangerous". Danger downgrades must be corroborated;
fabricated provenance must be dropped.
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
SANDBOX = Path(__file__).resolve().parent / ".last_run" / "provenance"


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


# Two corroborating sources, one official (ocfa.org) — enough to authorize an all-clear.
GOOD_SOURCES = [
    {"url": "https://ocfa.org/incident", "title": "OCFA update"},
    {"url": "https://latimes.com/story", "title": "LA Times"},
]


def test_fabricated_source_url_not_in_snapshot():
    """A statement citing a URL not present in sources_checked is dropped (P0-2)."""
    _reset_sandbox()
    _tick({"evacuation_residents": 50000, "evacuation_lifted": False})
    snap = _tick({
        "evacuation_residents": 50000, "evacuation_lifted": False,
        "sources_checked": [{"url": "https://ocfa.org/x", "title": "OCFA"}],
        "official_statements": [
            {"agency": "FAKE", "text": "fabricated", "source_url": "https://fabricated.invalid/y"}
        ],
    })
    urls = [s.get("source_url") for s in snap.get("official_statements", [])]
    return {
        "passed": "https://fabricated.invalid/y" not in urls,
        "details": f"statement source_urls in snapshot: {urls}",
    }


def test_statement_without_source_url_rejected():
    """A statement with no source_url is not published as authoritative (P0-2)."""
    _reset_sandbox()
    _tick({"evacuation_residents": 50000, "evacuation_lifted": False})
    snap = _tick({
        "evacuation_residents": 50000, "evacuation_lifted": False,
        "sources_checked": [{"url": "https://ocfa.org/x"}],
        "official_statements": [{"agency": "OCFA", "text": "no url here"}],
    })
    texts = [s.get("text") for s in snap.get("official_statements", [])]
    return {
        "passed": "no url here" not in texts,
        "details": f"statement texts in snapshot: {texts}",
    }


def test_sources_checked_all_wellformed():
    """Every sources_checked URL in the snapshot parses as http(s) (P0-2)."""
    from urllib.parse import urlparse
    _reset_sandbox()
    _tick({"evacuation_residents": 50000, "evacuation_lifted": False})
    snap = _tick({
        "evacuation_residents": 50000, "evacuation_lifted": False,
        "sources_checked": [
            {"url": "https://ocfa.org/good"},
            {"url": "not-a-real-url"},
            {"url": "ftp://ocfa.org/wrong-scheme"},
        ],
    })
    bad = []
    for s in snap.get("sources_checked", []):
        p = urlparse(s.get("url", ""))
        if p.scheme not in ("http", "https") or not p.netloc:
            bad.append(s.get("url"))
    return {
        "passed": len(bad) == 0,
        "details": f"malformed survivors: {bad}" if bad else "all sources_checked well-formed",
    }


def test_lifted_requires_corroboration():
    """evacuation_lifted=true with a single source must be forced back to false (P0-1)."""
    _reset_sandbox()
    _tick({"evacuation_residents": 50000, "evacuation_lifted": False})
    snap = _tick({
        "evacuation_lifted": True,
        "sources_checked": [{"url": "https://ocfa.org/only-one"}],
    })
    lifted = snap.get("evacuation", {}).get("lifted")
    reason = (snap.get("breaking_reason") or "").upper()
    return {
        "passed": lifted is False and "LIFTED" not in reason,
        "details": f"lifted={lifted}, breaking_reason={snap.get('breaking_reason')}",
    }


def test_resolved_requires_two_sources():
    """incident_resolved_iso: 1 source -> suppressed (severity stays); 2 sources incl
    official -> honored (severity low + RESOLVED breaking). Asymmetric gate (P0-1)."""
    # Half 1: single source -> suppressed.
    _reset_sandbox()
    _tick({"evacuation_residents": 50000, "evacuation_lifted": False})
    snap1 = _tick({
        "incident_resolved_iso": "2026-05-24T12:00:00Z",
        "evacuation_residents": 50000, "evacuation_lifted": False,
        "sources_checked": [{"url": "https://ocfa.org/only-one"}],
    })
    suppressed = (snap1["incident"]["severity"] != "low"
                  and "RESOLVED" not in (snap1.get("breaking_reason") or "").upper())

    # Half 2: two sources, one official -> honored.
    _reset_sandbox()
    _tick({"evacuation_residents": 50000, "evacuation_lifted": False})
    snap2 = _tick({
        "incident_resolved_iso": "2026-05-24T12:00:00Z",
        "evacuation_lifted": True,
        "sources_checked": GOOD_SOURCES,
    })
    honored = (snap2["incident"]["severity"] == "low"
               and snap2["incident"].get("resolved_iso") == "2026-05-26T12:00:00Z")

    return {
        "passed": suppressed and honored,
        "details": f"single-source suppressed={suppressed} (sev={snap1['incident']['severity']}); "
                   f"two-source honored={honored} (sev={snap2['incident']['severity']}, "
                   f"resolved={snap2['incident'].get('resolved_iso')})",
    }
