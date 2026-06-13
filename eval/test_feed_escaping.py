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
    """Every untrusted feed field (text/title/source/url/thumb) concatenated into
    innerHTML in buildFeedCardsHtml + buildFeedHtml must be escAttr-wrapped."""
    text = DASHBOARD.read_text(encoding="utf-8")
    cards = _fn_body("buildFeedCardsHtml", text)
    feed = _fn_body("buildFeedHtml", text)

    # Raw insertion patterns the escaping fix removes (conditionals like
    # `it.url ?` / `it.title ||` do NOT match `+ it.FIELD +`, so they're allowed).
    forbidden_cards = ["+ it.text +", "+ it.source +", "+ it.url +",
                       "+ it.thumb +", "+ (it.title ||"]
    forbidden_feed = ["+ it.text +", "+ it.source +", "+ it.url +",
                      "+ it.thumb +", "+ it.title +"]

    hits_cards = [p for p in forbidden_cards if p in cards]
    hits_feed = [p for p in forbidden_feed if p in feed]
    assert not hits_cards, f"buildFeedCardsHtml has unescaped field insertions: {hits_cards}"
    assert not hits_feed, f"buildFeedHtml has unescaped field insertions: {hits_feed}"
