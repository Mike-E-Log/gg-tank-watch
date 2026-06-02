"""Guard: common OpenType ligatures are disabled site-wide so the fi/ffi ligature can't drop the
dot on a lowercase 'i' (reported + confirmed on a real Android Chrome device 2026-06-02: 'official'
rendered with a dotless first i, the one inside the 'ffi' cluster). The brand typeface (Plus Jakarta
Sans) is unchanged; only ligature substitution is turned off in CSS. Deterministic across Blink, so
the fix is verifiable on the desktop dev box, not only on the phone."""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_common_ligatures_disabled():
    """The base html/body type must turn ligatures off (none or no-common-ligatures) so f-f-i renders
    as separate glyphs and the lowercase 'i' keeps its dot everywhere on the site."""
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r"font-variant-ligatures:\s*(none|no-common-ligatures)", text)
    ok = bool(m)
    return {"passed": ok,
            "details": f"font-variant-ligatures: {m.group(1)}" if ok
            else "font-variant-ligatures not set - fi/ffi ligature drops the lowercase-i dot"}
