"""Regression guard: the topbar is a left-axis masthead (2026-05-31).

The UNOFFICIAL pill, wordmark, and "Last updated..." dateline share one left
axis (pill -> wordmark -> dateline), with share/theme controls pinned top-right.
This replaced the old layout where the freshness line was right-aligned on its
own row (the orphan the user flagged) and a flex-wrap trick kept controls pinned.
Pure text guards; no JS runtime needed (the harness has none).
"""
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"

# Tokens that MUST be present after the masthead refactor.
REQUIRED = (
    "topbar--masthead",                              # masthead refactor marker
    "topbar-lead-row",                               # pill+wordmark wrapper
    "unofficial-pill",                               # pill kept (load-bearing trust signal)
    ">UNOFFICIAL<",                                  # pill text kept
    "min-width: 44px",                               # theme-toggle touch target kept
    'id="updated-text"',                             # freshness id kept (JS binds here)
    '"updated.freshness": { en: "Last updated',      # honest label kept
)

# Tokens that must NO LONGER appear (the orphan layout + the dead spacer).
FORBIDDEN = (
    "text-align: right; overflow: visible",          # old right-aligned mobile freshness rule
    "topbar-spacer",                                 # orphaned element removed
)


def test_masthead_tokens_present():
    """All masthead structure + preserved load-bearing tokens are present."""
    text = DASHBOARD.read_text(encoding="utf-8")
    missing = [tok for tok in REQUIRED if tok not in text]
    return {
        "passed": not missing,
        "details": "masthead structure + kept tokens present"
        if not missing
        else "required token(s) missing: " + " | ".join(missing),
        "metrics": {"missing": len(missing)},
    }


def test_orphan_freshness_layout_removed():
    """The right-aligned freshness orphan rule and the dead spacer are gone."""
    text = DASHBOARD.read_text(encoding="utf-8")
    survivors = [tok for tok in FORBIDDEN if tok in text]
    return {
        "passed": not survivors,
        "details": "orphan freshness layout + spacer removed"
        if not survivors
        else "forbidden token(s) still present: " + " | ".join(survivors),
        "metrics": {"survivors": len(survivors)},
    }


def test_dateline_is_inside_lead_before_controls():
    """Source order proves the dateline is part of the left identity cluster:
    lead-row (pill+wordmark) -> freshness dateline -> controls."""
    text = DASHBOARD.read_text(encoding="utf-8")
    # Anchor on the actual markup tags (the class names also appear in the CSS
    # earlier in the file, so bare-name find() would measure CSS order, not DOM).
    i_leadrow = text.find('<div class="topbar-lead-row">')
    i_fresh = text.find('id="updated-text"')
    i_controls = text.find('<div class="topbar-controls">')
    ok = -1 < i_leadrow < i_fresh < i_controls
    return {
        "passed": ok,
        "details": "order: lead-row < dateline < controls"
        if ok
        else f"bad source order leadrow={i_leadrow} fresh={i_fresh} controls={i_controls}",
        "metrics": {"leadrow": i_leadrow, "fresh": i_fresh, "controls": i_controls},
    }
