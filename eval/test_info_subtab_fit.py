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


def test_summary_fits_seven_rows():
    """Summary must be <=7 kv-rows so it fits a 568px-tall mobile panel with no vertical
    scroll (rubric 2026-06-03: 9 rows measured 486px@375 / 541px@320, over the ~342px panel).
    Tank + Crack observed are cut; the kept set is the 7-fact narrative. The real one-line/
    no-scroll proof is the rendered geometry probe in the acceptance rubric DoD."""
    text = DASHBOARD.read_text(encoding="utf-8")
    i = text.find("var summary =")
    j = text.find("var officials", i)
    region = text[i:j] if (i >= 0 and j > i) else ""
    assert region, "summary render block not found"
    n = region.count('class="info-kv-row"')
    assert 0 < n <= 7, f"Summary should be 1..7 kv-rows, found {n}"
    assert 't("info.fact.tankV")' not in region, "Tank row should be cut"
    assert 'id="info-crack-val"' not in region, "Crack observed row should be cut"


def test_summary_values_shortened_for_single_line():
    """The 4 values that wrapped to 2-3 lines at <=320px are shortened to single-line forms
    (rubric 2026-06-03): Facility 'GKN Aerospace'; Peak tank temperature '~100F (gauge max)'
    (trailing ', then stabilized' dropped); Evacuation zone '~9 sq mi, 6 cities'; Outcome
    'No injuries; 0 displaced'."""
    text = DASHBOARD.read_text(encoding="utf-8")
    assert '{ en: "GKN Aerospace" }' in text, "facilityV not shortened"
    assert '{ en: "~9 sq mi, 6 cities" }' in text, "zonePeak not shortened"
    assert '{ en: "No injuries; 0 displaced" }' in text, "outcomeV not shortened"
    assert ", then stabilized" not in text, "tankTempArchive tail not trimmed"
