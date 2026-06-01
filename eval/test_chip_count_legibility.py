"""Guard: the news filter-chip count is legible (2026-06-01).

At 10px in IBM Plex Mono with opacity 0.7 the count "30" read as "38". Bumping the size
(>=11px) and dropping the tiny mono face makes the numerals unambiguous. Anchors on the
.news-filter-count rule's font-size.
"""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_chip_count_font_size_legible():
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r"\.news-filter-count\s*\{([^}]*)\}", text)
    block = m.group(1) if m else ""
    fs = re.search(r"font-size:\s*(\d+(?:\.\d+)?)px", block)
    size = float(fs.group(1)) if fs else 0.0
    return {"passed": size >= 11,
            "details": f".news-filter-count font-size={size}px (need >=11 so '30' can't read as '38')"}
