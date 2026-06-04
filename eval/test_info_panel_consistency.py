"""Guard: the four Info sub-tab panels (Summary / Officials / Resources / About) share ONE visual
system - one key/value row treatment, one horizontal gutter, one value weight, one row color. Two
divergent row systems (.info-kv-row dashed/600 vs .info-row solid/500) plus a 12px-vs-14px gutter
drift made the panels read as four different designs. These assert the harmonized tokens from
docs/info-tab-acceptance-rubric.md so the consistency can't silently regress. Token-level invariants
(deterministic across Blink); rendered convergence is verified by signed-Edge screenshot in the loop."""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def _rule(text, selector):
    """Return the declaration block for an exact selector (e.g. '.info-section'), or None."""
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", text)
    return m.group(1) if m else None


def test_data_rows_solid_borders():
    """Both key/value row systems use a solid hairline - no lone dashed row in Summary."""
    css = DASHBOARD.read_text(encoding="utf-8")
    body = _rule(css, ".info-kv-row") or ""
    ok = "dashed" not in body and "solid" in body
    return {"passed": ok, "details": f".info-kv-row border solid (no dashed)={ok}"}


def test_kv_value_weight_unified():
    """Summary (.info-kv-val) and Officials (.info-row .v) values share weight 600."""
    css = DASHBOARD.read_text(encoding="utf-8")
    kv = re.search(r"font-weight:\s*(\d+)", _rule(css, ".info-kv-val") or "")
    rv = re.search(r"font-weight:\s*(\d+)", _rule(css, ".info-row .v") or "")
    ok = bool(kv and rv and kv.group(1) == rv.group(1) == "600")
    return {"passed": ok,
            "details": f"kv-val={kv and kv.group(1)} info-row.v={rv and rv.group(1)} (want both 600)"}


def test_panel_gutter_unified_14():
    """Section + section-title use the same 14px horizontal gutter as the rest of the panel content,
    so every sub-tab shares one left edge. The gutter may be expressed via margin OR padding: the
    Resources 2A change (2026-06-03) moved .info-section-title's gutter to padding so its full-width
    top rule spans the panel (a margin-inset border can't be full-width)."""
    css = DASHBOARD.read_text(encoding="utf-8")
    sec_ok = bool(re.search(r"padding:\s*\d+px\s+14px", _rule(css, ".info-section") or ""))
    title_ok = bool(re.search(r"(?:margin|padding):\s*\d+px\s+14px", _rule(css, ".info-section-title") or ""))
    return {"passed": sec_ok and title_ok,
            "details": f".info-section 14px={sec_ok} .info-section-title 14px={title_ok}"}


def test_about_sources_heading_shares_left_edge():
    """The About 'Sources' heading is a static .about-why-title (the lone collapsible <details>
    fold was removed 2026-06-03 — it was the only collapsible element on an otherwise-static site,
    and provenance should stay visible). It sits directly inside .about-body, which provides the
    panel's 14px horizontal gutter (padding: 0 14px), so the heading must NOT add its own
    horizontal padding/margin, or its glyph indents past the caption, source list, why-title, and
    disclosure that share the .about-body left edge. Assert .about-why-title's horizontal padding
    and margin are 0 so its glyph-left matches its siblings (it is the SAME class as the
    'Why this was made' heading in the panel)."""
    css = DASHBOARD.read_text(encoding="utf-8")
    block = _rule(css, ".about-why-title") or ""
    block = re.sub(r"/\*.*?\*/", "", block, flags=re.S)

    def _horiz(decl):
        # CSS shorthand -> horizontal value(s): [all] | [v h] | [t h b] | [t r b l]
        parts = decl.split()
        if len(parts) == 1:
            return {parts[0]}
        if len(parts) in (2, 3):
            return {parts[1]}
        if len(parts) == 4:
            return {parts[1], parts[3]}
        return set()

    mm = re.search(r"margin:\s*([^;]+);", block)
    margin_h = _horiz(mm.group(1)) if mm else {"0"}
    pm = re.search(r"padding:\s*([^;]+);", block)
    padding_h = _horiz(pm.group(1)) if pm else {"0"}
    zero = {"0", "0px"}
    ok = bool(block) and margin_h <= zero and padding_h <= zero
    return {"passed": ok,
            "details": f".about-why-title shares .about-body edge (margin_h={sorted(margin_h)} padding_h={sorted(padding_h)})"}


def test_school_card_value_color():
    """School names render at the value color (--sa-text), not dimmer than every other panel value."""
    css = DASHBOARD.read_text(encoding="utf-8")
    card = _rule(css, ".info-school-card") or ""
    ok = "var(--sa-text)" in card and "var(--sa-text-2)" not in card and "var(--sa-text-3)" not in card
    return {"passed": ok, "details": f".info-school-card uses --sa-text={ok}"}
