"""Language-access safety gate (G1) — build-failing guard.

Safety posture (2026-05-30): the app ships ENGLISH ONLY. We do not surface
translations — machine, AI, or others' — of life-safety copy without reliable
human verification, so the app carries no non-English language. Residents who
need another language are routed to officials, who publish their own verified
translations. This is the most conservative form of G1.

These guards turn that policy into enforced controls rather than promises:
the build fails if any non-English language appears in LANGS (test_english_only),
or if a ready:true language is not in the fluent-verified allowlist
(test_no_unverified_language_ships). See docs/LANGUAGE_ACCESS.md.
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


def test_english_only():
    """Safety choice (2026-05-30): the app ships English only — no non-English
    (and therefore no unverifiable machine/AI-translated) safety copy. Routing to
    officials covers other languages; officials publish their own verified copy."""
    html = DASHBOARD.read_text(encoding="utf-8")
    codes = [code for code, _ in _parse_langs(html)]
    assert codes == ["en"], (
        "app must be English-only — non-English safety copy is not shipped without "
        "reliable human translation (G1). Found language code(s): " + ", ".join(codes)
    )
    return {"passed": True, "details": "languages=" + ",".join(codes), "metrics": {"languages": len(codes)}}


# Keys introduced for the v0.17 sign-post / new chrome must stay English-only
# until fluent-native VI verification (G1). Listing a key here asserts "this
# string must NOT carry a vi value yet" — the falsifier that makes an MT VI leak
# into a new key fail the build.
ENGLISH_ONLY_KEYS = {
    "share.copied", "wind.source", "wind.disclaimer", "wind.unavailable",
    "info.subtab.status", "info.subtab.resources", "info.subtab.about",
}


def test_new_strings_english_only():
    """New v0.17 user-facing strings must not ship an (unverified) vi value (G1)."""
    html = DASHBOARD.read_text(encoding="utf-8")
    offenders = []
    for key in sorted(ENGLISH_ONLY_KEYS):
        m = re.search(r'"' + re.escape(key) + r'"\s*:\s*\{([^}]*)\}', html)
        if not m:
            continue  # key not present yet (e.g., partway through the build) — not an offense
        if re.search(r"\bvi\s*:", m.group(1)):
            offenders.append(key)
    assert not offenders, (
        "new i18n key(s) carry an unverified Vietnamese value (G1 violation): "
        + ", ".join(offenders)
        + ". Ship English-only until a fluent native speaker verifies the VI copy."
    )
    return {
        "passed": True,
        "details": "english-only keys clean=" + str(len(ENGLISH_ONLY_KEYS)),
        "metrics": {},
    }
