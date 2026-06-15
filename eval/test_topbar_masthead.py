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
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"

# Tokens that MUST be present after the masthead refactor.
REQUIRED = (
    "topbar--masthead",                              # masthead refactor marker
    "topbar-lead-row",                               # pill+wordmark wrapper
    "unofficial-pill",                               # pill kept (load-bearing trust signal)
    ">UNOFFICIAL<",                                  # pill text kept
    "min-width: 44px",                               # theme-toggle touch target kept
    'id="updated-text"',                             # freshness slot id kept
    "archive-pill",                                  # archive pivot: ARCHIVE pill added beside UNOFFICIAL
    ">ARCHIVE<",                                     # pill text
    '"archive.label"',                               # fixed historical-archive label (replaces live freshness)
    "topbar-pills",                                  # owner reorder: pills wrapped in a row below the wordmark
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


def test_wordmark_leads_above_pills():
    """Owner request (2026-06-01): the GG Tank Watch wordmark leads the masthead,
    rendered ABOVE the UNOFFICIAL/ARCHIVE pills (was: pills above the wordmark).
    Anchored on the wordmark element (a <button> that returns to Map), not the
    `.topbar-wordmark {` CSS rule earlier
    in the file, so this measures DOM order, not stylesheet order. With the
    lead-row stacked as a flex column (no `order:`/reverse), DOM order == the
    rendered top-to-bottom order; the visual stacking is confirmed by Edge QA."""
    text = DASHBOARD.read_text(encoding="utf-8")
    i_leadrow = text.find('<div class="topbar-lead-row">')
    i_wordmark = text.find('class="topbar-wordmark"', i_leadrow)
    i_unofficial = text.find(">UNOFFICIAL<", i_leadrow)
    i_archive = text.find(">ARCHIVE<", i_leadrow)
    ok = -1 < i_leadrow < i_wordmark < i_unofficial and i_wordmark < i_archive
    return {
        "passed": ok,
        "details": "order: lead-row < wordmark < pills (UNOFFICIAL, ARCHIVE)"
        if ok
        else f"bad order leadrow={i_leadrow} wordmark={i_wordmark} "
        f"unofficial={i_unofficial} archive={i_archive}",
        "metrics": {
            "leadrow": i_leadrow,
            "wordmark": i_wordmark,
            "unofficial": i_unofficial,
            "archive": i_archive,
        },
    }
