"""Guard: Info-tab school closures render as DENSE ROWS, not a card grid (2026-06-01).

Noise-reduction within the #93 archive-clarity design: school closures are a flat list of
plain names (dashboard.html ~2293 renders each as just the name string), so the 2-column
bordered-card grid was visual chrome with no signal. Align to the Map legend / News row
rhythm: a single-column list of dense rows (bottom-border separators, no box).

Anchors on the specific CSS block (class names also appear in the inline <style>; see
learning eval-find-hits-css-before-html), matching the test_info_archive_clarity pattern.
"""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"


def test_school_card_is_dense_row_not_box():
    """.info-school-card must be a dense row (bottom-border separator) with no card chrome:
    no border-radius, no full box border, no surface background fill."""
    text = DASHBOARD.read_text(encoding="utf-8")
    i = text.find(".info-school-card {")
    block = text[i:i + 280] if i != -1 else ""
    is_row = "border-bottom" in block
    no_radius = "border-radius" not in block
    no_box_border = "border: 1px solid" not in block
    no_surface_bg = "background: var(--sa-surface)" not in block
    ok = bool(block) and is_row and no_radius and no_box_border and no_surface_bg
    return {"passed": ok,
            "details": f"row={is_row} no_radius={no_radius} no_box_border={no_box_border} no_surface_bg={no_surface_bg}"}


def test_school_grid_is_single_column():
    """.info-schools-grid must be a single-column dense list, not a 2+ column card grid.
    The base rule and any media-query overrides must not re-introduce multi-column."""
    text = DASHBOARD.read_text(encoding="utf-8")
    i = text.find(".info-schools-grid {")
    base = text[i:i + 200] if i != -1 else ""
    base_single = bool(base) and "repeat(2, 1fr)" not in base
    no_multicol_overrides = ".info-schools-grid { grid-template-columns: repeat(" not in text
    ok = base_single and no_multicol_overrides
    return {"passed": ok,
            "details": f"base_single_col={base_single} no_multicol_media_overrides={no_multicol_overrides}"}
