"""Guard: desktop/tablet (>=768px) CSS invariants.

1. The CONTENT is capped to a comfortable, centered reading width while the MAP stays full-bleed.
   The failure mode fixed here is the inverse of #108: `@media (min-width:768px){ .app{ max-width:none } }`
   dropped the cap for EVERYTHING, so Info rows ran 1200px wide with a 933px label->value gap and News
   cards ran 1388px.
2. The content scroll container (.tab-panel) gets an enlarged, clearly-visible scrollbar on desktop
   (the default thin gray bar is easy to miss); mobile keeps its native overlay bar (2026-06-08).

This asserts the causal CSS invariants in source (deterministic, no browser); the rendered-geometry
proof (content<=cap, map==full viewport, no h-overflow, visible scrollbar) is the eyes-in-loop Chrome
gate in the DoD.
"""
from pathlib import Path
import re

CATEGORY = "behavioral"
ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = ROOT / "dashboard.html"


def test_desktop_layout_invariants():
    text = DASHBOARD.read_text(encoding="utf-8")
    # 1. a single content-cap token is defined and reused
    cap_defined = re.search(r"--content-cap:\s*\d+px", text) is not None
    # 2. the scrolling panels are capped + centered with that token
    content_capped = ("max-width: var(--content-cap)" in text
                      and ".news-subpanel" in text and "#info-content" in text)
    centered = "margin-inline: auto" in text
    # 3. full-width bars center their content via the padding-inline max() trick
    bar_centering = "calc((100% - var(--content-cap)) / 2)" in text
    # 4. the cap is scoped to >=768px only (mobile untouched)
    scoped = re.search(r"@media\s*\(min-width:\s*768px\)", text) is not None
    # 5. the map is NOT given the content cap (stays full-bleed)
    map_not_capped = (
        re.search(r"#maplibre-map[^{]*\{[^}]*max-width:\s*var\(--content-cap\)", text, re.S) is None
        and re.search(r"\.map-outer[^{]*\{[^}]*max-width:\s*var\(--content-cap\)", text, re.S) is None
    )
    # 6. the desktop content scrollbar (.tab-panel) is enlarged + visible via ::-webkit-scrollbar
    #    (Chrome 121+ ignores it if scrollbar-color/-width are also set, so those are absent by design)
    scrollbar_enlarged = (
        re.search(r"\.tab-panel::-webkit-scrollbar\s*\{[^}]*width:\s*1[4-9]px", text, re.S) is not None
        and re.search(r"\.tab-panel::-webkit-scrollbar-thumb\s*\{[^}]*background", text, re.S) is not None
    )
    ok = (cap_defined and content_capped and centered and bar_centering and scoped
          and map_not_capped and scrollbar_enlarged)
    return {"passed": ok,
            "details": "Desktop: content capped+centered; bars padding-inline-centered; map uncapped; scrollbar enlarged+visible"
            if ok else f"cap={cap_defined} content={content_capped} centered={centered} "
                       f"bars={bar_centering} scoped={scoped} map_free={map_not_capped} scrollbar={scrollbar_enlarged}"}
