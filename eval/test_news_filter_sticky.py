"""Guard: the news filter-chip row stays usable for a scrolling resident (2026-06-04; scroll-reset added 2026-06-08).

Two mechanisms keep the filter controls (All / Official / Articles / Videos) usable while the feed scrolls:

1. The chip row is pinned with position:sticky so a resident scrolling the feed always keeps the
   filter controls in view. Stickiness needs four declarations in the .news-filter-chips rule, and
   all four are the causal mechanism (not a proxy):
     - position: sticky   -> pin to the scroll container (.tab-panel)
     - top: 0             -> pin at the very top
     - an opaque background -> feed cards must not bleed through behind the bar
     - a z-index          -> the bar paints above the scrolling cards

2. Switching a filter returns the resident to the TOP of the filtered results. The feed lives in
   the .tab-panel (#panel-news) scroll container; replacing #news-feed's cards with a shorter
   filtered list leaves the old scrollTop stranded or clamped (a seemingly-random jump) unless
   setNewsFilter resets the container to the top. Regression guard for the 2026-06-08 scrollbar-jump bug.
"""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"


def _chips_block() -> str:
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r"\.news-filter-chips\s*\{([^}]*)\}", text)
    return m.group(1) if m else ""


def _set_news_filter_body() -> str:
    """The body of the setNewsFilter() JS function (up to the window.setNewsFilter export)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r"function setNewsFilter\b(.*?)window\.setNewsFilter", text, re.S)
    return m.group(1) if m else ""


def test_news_filter_bar_scroll_behavior():
    block = _chips_block()
    has_sticky = re.search(r"position:\s*sticky", block) is not None
    has_top = re.search(r"top:\s*0", block) is not None
    has_z = re.search(r"z-index:\s*\d+", block) is not None
    has_bg = re.search(r"background:\s*var\(--sa-surface\)", block) is not None
    # Switching a filter must reset the news scroll container (#panel-news) to the top, else a
    # shorter filtered list strands/clamps the old scrollTop (2026-06-08 scrollbar-jump bug).
    fn = _set_news_filter_body()
    resets_scroll = ("panel-news" in fn) and (re.search(r"scrollTop\s*=\s*0", fn) is not None)
    passed = has_sticky and has_top and has_z and has_bg and resets_scroll
    return {
        "passed": passed,
        "details": (
            f".news-filter-chips sticky={has_sticky} top0={has_top} z-index={has_z} "
            f"opaque-bg={has_bg}; setNewsFilter resets #panel-news scrollTop={resets_scroll} "
            "(chip row freezes at top AND switching a filter returns to the top of results)"
        ),
    }


def test_news_filter_chips_have_separator_hairline():
    """The frozen chip-bar carries the same 1px bottom hairline as the Info sub-tab bar
    (.info-subtabs) so cards scrolling under it are cleanly delineated, not flush, and the
    two sticky bars stay visually consistent."""
    has_border = re.search(r"border-bottom:\s*1px\s+solid\s+var\(--sa-border\)", _chips_block()) is not None
    return {"passed": has_border,
            "details": f".news-filter-chips border-bottom hairline={has_border} (matches .info-subtabs separator)"}
