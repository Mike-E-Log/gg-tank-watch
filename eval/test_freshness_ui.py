"""UI-honesty guards for the freshness slot (archive pivot, 2026-06-01).

The dashboard is now a FROZEN historical archive: the masthead freshness slot shows a
fixed archive label (archive.label), not a live "Last updated {age}" sourced from
data_as_of_iso. No resident-facing "stale"/"As of"/false-cadence vocab may appear, and
the live-age render path must be gone. Pure text guards; no JS runtime needed.
"""
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"

# Resident-facing strings that must NOT appear (stale/fresh/live-cadence framing).
FORBIDDEN = (
    '"updated.freshness": { en: "As of',          # old "As of" freshness label
    "banner.stale.title",                          # removed stale-banner i18n key
    "banner.stale.msg",                            # removed stale-banner i18n key
    "Auto-updates about every 20 minutes",         # false cadence claim
    "⚠️ Stale",                          # the "Stale" banner title text
    'freshLabel.textContent = t("updated.freshness"',  # the removed live-age render path
)


def test_no_stale_fresh_vocab_in_dashboard():
    """No 'As of' / 'Stale' / false-cadence vocab, and no live-age render path."""
    text = DASHBOARD.read_text(encoding="utf-8")
    survivors = [tok for tok in FORBIDDEN if tok in text]
    return {
        "passed": not survivors,
        "details": "no stale/fresh/live-age framing in dashboard.html"
        if not survivors
        else "forbidden string(s) still present: " + " | ".join(survivors),
        "metrics": {"survivors": len(survivors)},
    }


def test_freshness_slot_is_frozen_archive_label():
    """The freshness slot binds to the fixed archive label, not a live timestamp."""
    text = DASHBOARD.read_text(encoding="utf-8")
    bound = 'id="freshness-label" data-i18n="archive.label"' in text
    has_key = '"archive.label"' in text
    return {"passed": bound and has_key,
            "details": f"freshness-label bound to archive.label={bound}, key present={has_key}"}
