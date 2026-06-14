"""Guard: desktop/tablet (>=768px) CSS invariants.

1. Two caps. The full-width CHROME (header, safety strip, footer nav) centers into a wide --chrome-cap
   so it does not read as squished-to-center on big monitors, while the READING CONTENT (News cards,
   Info rows) stays at a narrower --content-cap for a comfortable measure; the MAP stays full-bleed
   (capped by neither). This guards two failure modes: #108 dropped the cap for EVERYTHING (Info rows
   ran 1200px wide with a 933px label->value gap, News cards 1388px), and the inverse — reading content
   stretched all the way to the chrome width, which reads as "spread too far apart".
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
DASHBOARD = ROOT / "public" / "dashboard.html"


def test_desktop_layout_invariants():
    text = DASHBOARD.read_text(encoding="utf-8")
    # 1. BOTH caps defined: a wide chrome cap + a narrower content reading measure
    content_m = re.search(r"--content-cap:\s*(\d+)px", text)
    chrome_m = re.search(r"--chrome-cap:\s*(\d+)px", text)
    caps_defined = content_m is not None and chrome_m is not None
    # 2. the scrolling reading panels are capped + centered with the CONTENT cap
    content_capped = ("max-width: var(--content-cap)" in text
                      and ".news-subpanel" in text and "#info-content" in text)
    centered = "margin-inline: auto" in text
    # 3. full-width chrome bars center their content into the wider CHROME cap (padding-inline max() trick)
    bar_centering = "calc((100% - var(--chrome-cap)) / 2)" in text
    # 4. reading content is narrower than the chrome (Info rows / News lines do not stretch to the bars)
    content_narrower = caps_defined and int(content_m.group(1)) < int(chrome_m.group(1))
    # 5. the cap is scoped to >=768px only (mobile untouched)
    scoped = re.search(r"@media\s*\(min-width:\s*768px\)", text) is not None
    # 6. the map is given NEITHER cap (stays full-bleed)
    map_not_capped = (
        re.search(r"#maplibre-map[^{]*\{[^}]*max-width:\s*var\(--(content|chrome)-cap\)", text, re.S) is None
        and re.search(r"\.map-outer[^{]*\{[^}]*max-width:\s*var\(--(content|chrome)-cap\)", text, re.S) is None
    )
    # 7. the desktop content scrollbar (.tab-panel) is enlarged + visible via ::-webkit-scrollbar
    #    (Chrome 121+ ignores it if scrollbar-color/-width are also set, so those are absent by design)
    scrollbar_enlarged = (
        re.search(r"\.tab-panel::-webkit-scrollbar\s*\{[^}]*width:\s*1[4-9]px", text, re.S) is not None
        and re.search(r"\.tab-panel::-webkit-scrollbar-thumb\s*\{[^}]*background", text, re.S) is not None
    )
    # 8. video thumbnails are width-capped so the full video + its title fit in one screenful
    #    (a full-width 16:9 thumb in the reading column ran ~420px tall, pushing the title below the fold)
    video_thumb_capped = re.search(r"\.feed-card-thumb\s*\{[^}]*max-width:\s*\d+px", text, re.S) is not None
    ok = (caps_defined and content_capped and centered and bar_centering and content_narrower
          and scoped and map_not_capped and scrollbar_enlarged and video_thumb_capped)
    return {"passed": ok,
            "details": "Desktop: chrome bars centered into --chrome-cap; reading content capped narrower via --content-cap; map uncapped; scrollbar enlarged+visible; video thumb width-capped"
            if ok else f"caps={caps_defined} content={content_capped} centered={centered} "
                       f"chrome_bars={bar_centering} content_narrower={content_narrower} scoped={scoped} "
                       f"map_free={map_not_capped} scrollbar={scrollbar_enlarged} video_capped={video_thumb_capped}"}
