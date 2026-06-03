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
    so every sub-tab shares one left edge."""
    css = DASHBOARD.read_text(encoding="utf-8")
    sec_ok = bool(re.search(r"padding:\s*\d+px\s+14px", _rule(css, ".info-section") or ""))
    title_ok = bool(re.search(r"margin:\s*\d+px\s+14px", _rule(css, ".info-section-title") or ""))
    return {"passed": sec_ok and title_ok,
            "details": f".info-section 14px={sec_ok} .info-section-title 14px={title_ok}"}


def test_school_card_value_color():
    """School names render at the value color (--sa-text), not dimmer than every other panel value."""
    css = DASHBOARD.read_text(encoding="utf-8")
    card = _rule(css, ".info-school-card") or ""
    ok = "var(--sa-text)" in card and "var(--sa-text-2)" not in card and "var(--sa-text-3)" not in card
    return {"passed": ok, "details": f".info-school-card uses --sa-text={ok}"}
