"""Guard: the news filter-chip row stays frozen at the top while the feed scrolls (2026-06-04).

The chips (All / Official / Articles / Videos) are pinned with position:sticky so a resident
scrolling the feed always keeps the filter controls in view. Stickiness needs four declarations
in the .news-filter-chips rule, and all four are the causal mechanism (not a proxy):
  - position: sticky   -> pin to the scroll container (.tab-panel)
  - top: 0             -> pin at the very top
  - an opaque background -> feed cards must not bleed through the gaps between pills
  - a z-index          -> the bar paints above the scrolling cards
"""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def _chips_block() -> str:
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r"\.news-filter-chips\s*\{([^}]*)\}", text)
    return m.group(1) if m else ""


def test_news_filter_chips_are_sticky():
    block = _chips_block()
    has_sticky = re.search(r"position:\s*sticky", block) is not None
    has_top = re.search(r"top:\s*0", block) is not None
    has_z = re.search(r"z-index:\s*\d+", block) is not None
    has_bg = re.search(r"background:\s*var\(--sa-bg\)", block) is not None
    passed = has_sticky and has_top and has_z and has_bg
    return {
        "passed": passed,
        "details": (
            f".news-filter-chips sticky={has_sticky} top0={has_top} "
            f"z-index={has_z} opaque-bg={has_bg} "
            "(all four required so the chip row freezes at top without cards bleeding through)"
        ),
    }


def test_news_filter_chips_have_separator_hairline():
    """The frozen chip-bar carries the same 1px bottom hairline as the Info sub-tab bar
    (.info-subtabs) so cards scrolling under it are cleanly delineated, not flush, and the
    two sticky bars stay visually consistent."""
    has_border = re.search(r"border-bottom:\s*1px\s+solid\s+var\(--sa-border\)", _chips_block()) is not None
    return {"passed": has_border,
            "details": f".news-filter-chips border-bottom hairline={has_border} (matches .info-subtabs separator)"}
