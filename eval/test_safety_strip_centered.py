"""Guard: the persistent safety-strip footer vertically centers its content (user follow-up
2026-05-31). It is a column flex container, so vertical centering = justify-content: center on
the main axis."""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"


def test_safety_strip_vertically_centered():
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r"\.safety-strip\s*\{([^}]*)\}", text)
    body = m.group(1) if m else ""
    is_column = "flex-direction: column" in body
    centered = "justify-content: center" in body
    ok = is_column and centered
    return {"passed": ok,
            "details": "safety-strip column flex centers content vertically" if ok
            else f"column={is_column} justify_center={centered}"}


def _rule_body(text, selector):
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", text)
    return m.group(1) if m else ""


def _min_height_px(body):
    m = re.search(r"min-height:\s*(\d+)px", body)
    return int(m.group(1)) if m else None


def test_safety_strip_rows_equal_height_for_symmetric_glyph_padding():
    """The two text rows — the info line and the sources/links row — must have EQUAL
    min-height and each vertically center its own text, so the visible top glyph and bottom
    glyph have the same padding to their nearest strip edge. Before this fix only the links
    carried min-height:32px (centering their glyph high in a tall box) while the info line was
    text-height, so the bottom text sat ~17px from the bottom edge vs the top text's ~8px
    (user reported the strip looked off-center 3x, 2026-05-31). Equal-height centered rows fix
    it. NOTE: also remove the desktop min-height:0 override on the links or desktop re-breaks."""
    text = DASHBOARD.read_text(encoding="utf-8")
    info = _rule_body(text, ".safety-strip-info")
    link = _rule_body(text, ".safety-strip-sources a")
    info_mh = _min_height_px(info)
    link_mh = _min_height_px(link)
    info_centers_text = ("display: flex" in info) and ("align-items: center" in info)
    equal = info_mh is not None and info_mh == link_mh
    ok = equal and info_centers_text
    return {"passed": ok,
            "details": f"info_min_height={info_mh} link_min_height={link_mh} "
                       f"info_centers_text={info_centers_text} (equal+centered => symmetric)"}
