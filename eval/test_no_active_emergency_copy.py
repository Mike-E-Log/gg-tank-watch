"""Guard: the frozen archive carries no present-tense LIVE-emergency copy.

dashboard.html held two unused i18n strings — hero.lead ("Active chemical-tank
emergency in Garden Grove.") and hero.summary.default ("Active chemical-tank
incident in Garden Grove. Follow official orders.") — present-tense, action-oriented
live-emergency framing left over from the live tool. They were never rendered (dead
code) and were removed in the historical-archive pivot (batch 4, 2026-06-01). This
guard fails if "Active chemical-tank" live copy reappears in the frozen archive.
Pure text guard; no JS runtime.
"""
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"


def test_no_active_emergency_copy():
    text = DASHBOARD.read_text(encoding="utf-8")
    hits = text.count("Active chemical-tank")
    return {
        "passed": hits == 0,
        "details": "no present-tense 'Active chemical-tank' live copy"
        if hits == 0
        else f"{hits} present-tense 'Active chemical-tank' string(s) remain (frozen archive must be past-tense)",
        "metrics": {"hits": hits},
    }
