"""Regression guard: the frozen archive's map legend must paint its RESOLVED label
on first load, never the live "Evac zone" label.

The incident is permanently resolved (status.json carries resolved_iso; polling is
disabled), so the only correct legend label is "Former evac area" (i18n key
legend.evac.resolved). Before this guard the static legend row hard-coded the live
label (data-i18n="legend.evac" -> "Evac zone") and render() swapped it to the resolved
label only after config.json + news_archive.json + status.json all fetched. On reload
that produced a visible flash: "Evac zone" -> "Former evac area" (reproduced in headless
Edge 2026-06-02).

The flash is a static-markup problem: the first synchronous paint shows whatever the
markup says, before any JS swap runs. So the fix and this guard both live in the static
markup -- the legend evac row must already carry the resolved key + text. Pure text
guard; the eval harness has no JS runtime.
"""
import re
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"


def _legend_evac_row(text):
    """(data_i18n_key, visible_text) of the legend's evac row, or (None, None)."""
    m = re.search(
        r'legend-icon-evac[^>]*></span>\s*<span data-i18n="([^"]+)">([^<]*)</span>',
        text,
    )
    return (m.group(1), m.group(2).strip()) if m else (None, None)


def test_legend_paints_resolved_label_on_first_load():
    """The static legend evac row carries the resolved key + text (no first-paint flash)."""
    key, label = _legend_evac_row(DASHBOARD.read_text(encoding="utf-8"))
    ok = key == "legend.evac.resolved" and label == "Former evac area"
    return {
        "passed": ok,
        "details": "static legend evac row is the resolved label "
        "(legend.evac.resolved / 'Former evac area')"
        if ok
        else f"static legend evac row would flash on reload: key={key!r} text={label!r} "
        "(expected 'legend.evac.resolved' / 'Former evac area')",
        "metrics": {"key": key or "", "label": label or ""},
    }
