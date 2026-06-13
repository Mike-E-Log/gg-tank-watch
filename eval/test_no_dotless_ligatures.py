"""Guard: common OpenType ligatures are disabled site-wide so the fi/ffi ligature can't drop the
dot on a lowercase 'i' (reported + confirmed on a real Android Chrome device 2026-06-02: 'official'
rendered with a dotless first i, the one inside the 'ffi' cluster). The brand typeface (Plus Jakarta
Sans) is unchanged; only ligature substitution is turned off in CSS. Deterministic across Blink, so
the fix is verifiable on the desktop dev box, not only on the phone."""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"


def test_common_ligatures_disabled():
    """The base html/body type must turn ligatures off (none or no-common-ligatures) so f-f-i renders
    as separate glyphs and the lowercase 'i' keeps its dot everywhere on the site."""
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r"font-variant-ligatures:\s*(none|no-common-ligatures)", text)
    ok = bool(m)
    return {"passed": ok,
            "details": f"font-variant-ligatures: {m.group(1)}" if ok
            else "font-variant-ligatures not set - fi/ffi ligature drops the lowercase-i dot"}


def _css_rules(text):
    """Yield (selector, body) for flat CSS rules (innermost {...} blocks)."""
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", text):
        yield m.group(1).strip(), m.group(2)


def test_form_controls_disable_ligatures():
    """The body rule is NOT inherited by form controls (<button>/<input>/<select>/<textarea>): the UA
    stylesheet resets font-variant-ligatures on them, so the fi ligature still drops the lowercase-i
    dot on buttons. The 'Officials' info sub-tab is a <button> and rendered dotless on prod even with
    the body rule deployed. A rule must target the button element directly. (Asserts the causal layout
    invariant per the in-repo UI/UX playbook, not just that the string exists somewhere.)"""
    text = DASHBOARD.read_text(encoding="utf-8")
    for sel, body in _css_rules(text):
        if not re.search(r"font-variant-ligatures:\s*(none|no-common-ligatures)", body):
            continue
        # the literal `button` element selector (not `.btn`, `#button`, `x-button`)
        if re.search(r"(?<![.\w#-])button(?![\w-])", sel):
            return {"passed": True, "details": f"form-control ligature reset on selector: {sel}"}
    return {"passed": False,
            "details": "no CSS rule targets <button> with font-variant-ligatures:none - "
                       "form controls keep the UA default and drop the lowercase-i dot"}
