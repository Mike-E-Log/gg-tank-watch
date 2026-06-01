"""Guard (T5, archive pivot): the data-refresh pipeline is retired — refresh_local.py is
marked ARCHIVED (won't rewrite the frozen status.json), and the update-status cron
schedule stays disabled."""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
REFRESH = REPO_ROOT / "scripts" / "refresh_local.py"
WF = REPO_ROOT / ".github" / "workflows" / "update-status.yml"


def test_refresh_local_archived():
    t = REFRESH.read_text(encoding="utf-8")
    return {"passed": "ARCHIVED" in t,
            "details": f"ARCHIVED marker in refresh_local.py: {'ARCHIVED' in t}"}


def test_cron_schedule_disabled():
    t = WF.read_text(encoding="utf-8")
    # no uncommented top-level `schedule:` trigger may write status.json
    active = "\n  schedule:" in t
    return {"passed": not active, "details": f"active schedule trigger present={active}"}
