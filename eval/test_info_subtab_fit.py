"""Guard: the Info-tab sub-tab bar must be structurally incapable of overflowing
its single row. The #108 regression was a 6-tab `overflow-x:auto` scrollable bar
that clipped "Recovery" and hid "About" at 375px; #109 fixed it with equal-width
`flex:1 1 0`. Equal-width flex partitions the row and cannot wrap, and `min-width:0`
makes it overflow-proof for ANY label length. This asserts that invariant in static
CSS - deterministic, no browser, no new dependency (catches the failure a text-only
string match cannot, by checking the causal layout property rather than pixel values).
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = ROOT / "dashboard.html"


def _css_block(selector: str, text: str) -> str:
    """Body of the FIRST `selector { ... }` rule. The trailing `\\s*\\{` guard means
    `.info-subtab` does NOT match `.info-subtabs {`, `.info-subtab:hover {`, or
    `.info-subtab.active {` - only the bare rule."""
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", text)
    return m.group(1) if m else ""


def test_info_subtabs_bar_not_scrollable():
    """`.info-subtabs` must not use the scrollable/wrapping bar anti-pattern (#108)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    block = _css_block(".info-subtabs", text)
    assert block, ".info-subtabs CSS rule not found"
    banned = ["overflow-x: auto", "overflow-x:auto", "overflow-x: scroll", "overflow-x:scroll",
              "overflow: auto", "overflow:auto", "overflow: scroll", "overflow:scroll",
              "scroll-snap", "flex-wrap: wrap", "flex-wrap:wrap"]
    hit = [b for b in banned if b in block]
    assert not hit, f".info-subtabs uses a scrollable/wrapping bar anti-pattern: {hit}"


def test_info_subtab_is_overflow_proof_equal_width():
    """`.info-subtab` must be equal-width (`flex:1 1 0`) AND `min-width:0` so the bar
    cannot overflow one row regardless of label length."""
    text = DASHBOARD.read_text(encoding="utf-8")
    block = _css_block(".info-subtab", text)
    assert block, ".info-subtab CSS rule not found"
    assert re.search(r"flex:\s*1\s+1\s+0", block), ".info-subtab must use `flex: 1 1 0` (equal-width)"
    assert re.search(r"min-width:\s*0", block), ".info-subtab must set `min-width: 0` (overflow-proof)"


def test_info_subtab_count_at_most_four():
    """Legibility guard: keep the Info sub-tab bar at <=4 tabs (the 6-tab build #108
    was too cramped at 320-375px). Counts entries in the renderInfoTab TABS array
    (anchored on the `id:"summary"` first entry)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    arr = re.search(r"\[\s*\{\s*id:\s*[\"']summary[\"'].*?\}\s*\]", text, re.S)
    assert arr, "Info TABS array (starting with id:'summary') not found"
    count = len(re.findall(r"\bid:\s*[\"']", arr.group(0)))
    assert 0 < count <= 4, f"Info sub-tabs should be 1..4, found {count}"
