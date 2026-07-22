"""Guard: the news feed-render functions must HTML-escape every untrusted data
field before concatenating it into innerHTML, preventing DOM-XSS / mis-rendering
if a headline, official-statement, source name, or URL ever contains < > & or ".
The feed data (status.json, data/news_archive.json) is human-curated and frozen,
so this is defense-in-depth - but unescaped innerHTML on a safety-themed project
is a real code-hygiene gap a reviewer would flag. escAttr() escapes & < > " and is
safe for both text and attribute context. Static check, no browser, no new deps.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = ROOT / "public" / "dashboard.html"


def _fn_body(name: str, text: str) -> str:
    """Body of `function <name>(...) { ... }` up to its column-0 closing brace
    (inner braces are indented, so the first "\\n}" is the function end)."""
    i = text.find("function " + name)
    assert i >= 0, f"{name} not found in dashboard.html"
    j = text.find("\n}", i)
    assert j > i, f"{name} closing brace not found"
    return text[i:j]


def test_feed_render_escapes_untrusted_fields():
    """Every untrusted data field concatenated into innerHTML must be escAttr-wrapped,
    across ALL the HTML builders, not just the two feed builders.

    Extended 2026-07-21 (Fable 5 audit D1/D3): the original test covered only
    buildFeedCardsHtml + buildFeedHtml, which gave false assurance while
    updateInfoData (schools/sources), renderInfoConfigData (shelters/recovery),
    setBanners (title/message fall-through, incl. localizeBreakingReason's raw
    passthrough), and renderPrintContent carried unescaped insertions of
    status.json/config.json-sourced fields. Code constants, t() i18n strings,
    fmtNumber output, tel:-sanitized phones, and encodeURIComponent-built URLs
    are trusted and stay unwrapped."""
    text = DASHBOARD.read_text(encoding="utf-8")

    # Raw insertion patterns the escaping fix removes (conditionals like
    # `it.url ?` / `it.title ||` do NOT match `+ it.FIELD +`, so they're allowed).
    forbidden = {
        "buildFeedCardsHtml": ["+ it.text +", "+ it.source +", "+ it.url +",
                               "+ it.thumb +", "+ (it.title ||"],
        "buildFeedHtml": ["+ it.text +", "+ it.source +", "+ it.url +",
                          "+ it.thumb +", "+ it.title +"],
        "updateInfoData": ["+ s +", "+ s.url +", "+ (s.title ||"],
        "renderInfoConfigData": ["+ s.name +", "+ s.city +", "+ r.title +",
                                 "+ r.description +", "+ r.url +", "+ r.phone +"],
        "setBanners": ["+ b.title +", "+ (b.message ||",
                       "+ localizeBreakingReason("],
        "renderPrintContent": ["? tank.temp_f +", "+ (evac.area_sq_mi ||"],
    }

    for fn, patterns in forbidden.items():
        body = _fn_body(fn, text)
        hits = [p for p in patterns if p in body]
        assert not hits, f"{fn} has unescaped field insertions: {hits}"
