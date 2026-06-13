"""Guard: the active tab survives a reload (2026-06-01).

Reloading on News or Info bounced back to Map (the HTML default) — disorienting on an
emergency app. switchTab() now persists the tab to localStorage and the kickoff restores it.
"""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"


def test_switchtab_persists_active_tab():
    text = DASHBOARD.read_text(encoding="utf-8")
    return {"passed": 'localStorage.setItem("gg-active-tab"' in text,
            "details": "switchTab persists the active tab to localStorage"}


def test_active_tab_restored_on_load():
    text = DASHBOARD.read_text(encoding="utf-8")
    return {"passed": 'localStorage.getItem("gg-active-tab")' in text,
            "details": "kickoff restores the saved tab on reload (no bounce to Map)"}
