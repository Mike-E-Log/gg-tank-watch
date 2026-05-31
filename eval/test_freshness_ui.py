"""UI-honesty guards for the freshness label (2026-05-31).

The visible timestamp must read "Last updated {clock} ({N} ago)" sourced from
data_as_of_iso (when we last learned something new), NOT last_updated_iso
(pipeline write time) -- otherwise a stalled feed looks fresh (the F4/F6 class
that test_freshness.py guards on the backend). All resident-facing "stale" /
"fresh" / "As of" vocabulary is removed, and the false "auto-updates every 20
minutes" cadence claim is gone. Pure text guards; no JS runtime needed.
"""
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"

# Resident-facing strings that must NO LONGER appear after this change.
FORBIDDEN = (
    '"updated.freshness": { en: "As of',          # old freshness label
    "banner.stale.title",                          # removed stale-banner i18n key
    "banner.stale.msg",                            # removed stale-banner i18n key
    "Auto-updates about every 20 minutes",         # false cadence claim (cron dormant)
    "⚠️ Stale",                          # the "Stale" banner title text
)

# Tokens that MUST be present (the honest replacement + a kept dependency).
REQUIRED = (
    '"updated.freshness": { en: "Last updated',    # new honest label
    "relativeAge",                                 # the relative-age helper
    "data_as_of_iso",                              # freshness label binds to info-age
    ".banner-stale",                               # CSS kept -- schema banner reuses it
)


def test_no_stale_fresh_vocab_in_dashboard():
    """No 'As of' / 'Stale' / false-cadence vocab may remain in dashboard.html."""
    text = DASHBOARD.read_text(encoding="utf-8")
    survivors = [tok for tok in FORBIDDEN if tok in text]
    return {
        "passed": not survivors,
        "details": "no stale/fresh/As-of vocab in dashboard.html"
        if not survivors
        else "forbidden string(s) still present: " + " | ".join(survivors),
        "metrics": {"survivors": len(survivors)},
    }


def test_freshness_label_honest_and_dependencies_intact():
    """The honest 'Last updated' label, relativeAge helper, data_as_of binding,
    and the kept .banner-stale CSS (schema-banner dep) must all be present."""
    text = DASHBOARD.read_text(encoding="utf-8")
    missing = [tok for tok in REQUIRED if tok not in text]
    return {
        "passed": not missing,
        "details": "honest label + deps present"
        if not missing
        else "required token(s) missing: " + " | ".join(missing),
        "metrics": {"missing": len(missing)},
    }
