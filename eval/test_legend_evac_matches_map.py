"""Regression guard: the legend's "Former evac area" swatch must mirror the map.

The legend evac icon is the *key* to the evacuation zone polygon drawn on the
map. To stay a faithful key it must reproduce the polygon's appearance:
  - the same burnt-orange hue (#D95F02 -- ColorBrewer Dark2, colorblind-safe),
  - a faint fill at the map's own fill-opacity (so it reads as an *area*, not a
    solid block), and
  - a solid, same-colour outline >=2px (so it reads as a bounded zone, not a
    plain square like the shelter swatch).

These guards fail the build if the swatch drifts from the map's evac colours --
e.g. the map palette changes but the legend is forgotten, or the legend fill
reverts to a solid block. Pure text guards; no JS runtime needed (the harness
has none). Set 2026-05-31 after the swatch was rebuilt to match the map.
"""
import re
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"

EVAC_RGB = (217, 95, 2)  # #D95F02


def _text():
    return DASHBOARD.read_text(encoding="utf-8")


def _map_evac_paint(text):
    """(fill_colors, line_colors, fill_opacities) from the map layer paint props."""
    fill_colors = [c.upper() for c in re.findall(r'"fill-color":\s*"(#[0-9A-Fa-f]{6})"', text)]
    line_colors = [c.upper() for c in re.findall(r'"line-color":\s*"(#[0-9A-Fa-f]{6})"', text)]
    fill_opacities = [float(o) for o in re.findall(r'"fill-opacity":\s*([0-9.]+)', text)]
    return fill_colors, line_colors, fill_opacities


def _legend_evac_css(text):
    """Body of the .legend-icon-evac { ... } CSS rule, or '' if absent."""
    m = re.search(r"\.legend-icon-evac\s*\{([^}]*)\}", text)
    return m.group(1) if m else ""


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _parse_rgba(s):
    m = re.search(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9.]+)\s*\)", s)
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)), float(m.group(4)))


def test_map_evac_color_is_canonical_orange():
    """Anchor: the map evac polygon fill + line are both the canonical #D95F02."""
    fill_colors, line_colors, _ = _map_evac_paint(_text())
    found = set(fill_colors) | set(line_colors)
    ok = bool(fill_colors) and bool(line_colors) and found == {"#D95F02"}
    return {
        "passed": ok,
        "details": "map evac fill+line are all #D95F02"
        if ok
        else f"map evac colours not uniformly #D95F02: fill={fill_colors} line={line_colors}",
        "metrics": {"fill_count": len(fill_colors), "line_count": len(line_colors)},
    }


def test_legend_evac_fill_matches_map_fill():
    """Legend swatch fill = map hue at the map's fill-opacity (faint area, not a block)."""
    text = _text()
    _, _, fill_opacities = _map_evac_paint(text)
    assert fill_opacities, "no map fill-opacity found"
    map_alpha = fill_opacities[0]
    rgba = _parse_rgba(_legend_evac_css(text))
    if rgba is None:
        return {
            "passed": False,
            "details": "legend .legend-icon-evac background is not an rgba() faint fill "
            "(a solid hex/opacity:1 block does not match the map's translucent fill)",
            "metrics": {},
        }
    r, g, b, a = rgba
    hue_ok = (r, g, b) == EVAC_RGB
    alpha_ok = abs(a - map_alpha) < 0.001
    return {
        "passed": hue_ok and alpha_ok,
        "details": "legend fill matches map hue + fill-opacity"
        if hue_ok and alpha_ok
        else f"legend fill rgba={rgba} vs map hue={EVAC_RGB} alpha={map_alpha}",
        "metrics": {"legend_alpha": a, "map_alpha": map_alpha},
    }


def test_legend_evac_border_mirrors_map_line():
    """Legend swatch has a solid same-colour outline >=2px (reads as a bounded zone)."""
    css = _legend_evac_css(_text())
    bm = re.search(r"border:\s*([^;]+);", css)
    border = bm.group(1) if bm else ""
    wm = re.search(r"([0-9.]+)px", border)
    width = float(wm.group(1)) if wm else 0.0
    has_color = ("#D95F02" in border.upper()) or (_parse_rgba(border) and _parse_rgba(border)[:3] == EVAC_RGB)
    is_solid = "solid" in border
    ok = is_solid and bool(has_color) and width >= 2.0
    return {
        "passed": ok,
        "details": "legend border is solid #D95F02 >=2px"
        if ok
        else f"legend border not a solid >=2px #D95F02 outline: '{border.strip()}'",
        "metrics": {"border_width_px": width},
    }
