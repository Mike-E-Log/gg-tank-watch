"""Guard: the Info tab icon renders as a lowercase 'i' (dot + stem).

The Lucide 'info' glyph draws the dot as a zero-length line (12,8)->(12.01,8),
which only renders as a visible dot when stroke-linecap is 'round'. Without it
the dot vanishes and the icon reads as a bare circle + vertical bar (a '1', not
an 'i') -- owner-flagged 2026-06-01. This guards the round linecap on the Info
icon SVG so the dot survives. Pure text guard; no JS runtime.
"""
import re
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"


def test_info_icon_dot_renders():
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r'id="tab-info".*?(<svg.*?</svg>)', text, re.S)
    svg = m.group(1) if m else ""
    has_dot_line = "12.01" in svg                       # the zero-length dot line
    round_cap = 'stroke-linecap="round"' in svg          # makes the dot visible
    ok = bool(svg) and has_dot_line and round_cap
    return {
        "passed": ok,
        "details": "Info icon has round linecap so the i's dot renders"
        if ok
        else f"svg_found={bool(svg)} dot_line={has_dot_line} round_cap={round_cap}",
    }
