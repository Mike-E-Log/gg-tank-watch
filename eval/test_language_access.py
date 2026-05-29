"""Language-access safety gate (G1) — build-failing guard.

A language is marked `ready: true` in dashboard.html's LANGS array only AFTER a
fluent native speaker has verified its safety copy. Until then it must stay
`ready: false`, so t() falls back to verified English — unverified machine/AI
translation of life-safety copy must never ship to residents.

This guard turns the G1 policy into an enforced control rather than a promise:
it fails the build if any non-English language is flipped to ready:true without
being added to VERIFIED_LANGS below. It is the falsifier the 2026-05-29 research
recommended (docs/research/2026-05-29-vi-anthropic-lens-research.md); see also
docs/LANGUAGE_ACCESS.md.
"""

from __future__ import annotations

import re
from pathlib import Path

# A language code may be ready:true ONLY after fluent-native verification of its
# safety copy. Add a code here as part of RECORDING that verification — never to
# silence this test.
VERIFIED_LANGS = {"en"}

DASHBOARD = Path(__file__).resolve().parent.parent / "dashboard.html"


def _parse_langs(html: str):
    """Return [(code, ready_bool), ...] parsed from the LANGS array."""
    m = re.search(r"var LANGS\s*=\s*\[(.*?)\];", html, re.DOTALL)
    assert m, "could not find the LANGS array in dashboard.html"
    langs = []
    for line in m.group(1).splitlines():
        cm = re.search(r'code:\s*"([^"]+)"', line)
        rm = re.search(r"ready:\s*(true|false)", line)
        if cm and rm:
            langs.append((cm.group(1), rm.group(1) == "true"))
    return langs


def test_no_unverified_language_ships():
    """Every ready:true language must be in the fluent-verified allowlist (G1)."""
    html = DASHBOARD.read_text(encoding="utf-8")
    langs = _parse_langs(html)
    assert langs, "no languages parsed from LANGS"
    ready = [code for code, is_ready in langs if is_ready]
    assert "en" in ready, "English must be ready"
    unverified = [c for c in ready if c not in VERIFIED_LANGS]
    assert not unverified, (
        "language(s) marked ready:true but NOT fluent-verified (G1 violation): "
        + ", ".join(unverified)
        + ". Set ready:false until a native speaker verifies its safety copy, "
        "or add the code to VERIFIED_LANGS only when recording that verification."
    )
    return {
        "passed": True,
        "details": "ready=" + ",".join(ready) + "; verified=" + ",".join(sorted(VERIFIED_LANGS)),
        "metrics": {"languages": len(langs), "ready": len(ready)},
    }


def test_vietnamese_held_with_official_fallback():
    """Vietnamese must be held (ready:false) and route to official human Vietnamese."""
    html = DASHBOARD.read_text(encoding="utf-8")
    langs = dict(_parse_langs(html))
    assert "vi" in langs, "vi entry missing from LANGS"
    assert langs["vi"] is False, "vi must be ready:false until fluent-native verification (G1)"
    m = re.search(r'code:\s*"vi"[^\n]*fallbackUrl:\s*"([^"]+)"', html)
    assert m, "vi must carry a fallbackUrl routing vi-seekers to official human Vietnamese"
    assert "ggcity.org" in m.group(1), "vi fallbackUrl should point to the official city emergency page"
    return {"passed": True, "details": "vi held; fallback=" + m.group(1), "metrics": {}}
