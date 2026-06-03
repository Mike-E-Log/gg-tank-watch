"""Guard (T11 minimal, archive pivot 2026-06-01): the AI disclosure routes life-safety
confirmation to a CONCRETE channel (ggcity.org/emergency or 911), not the vague phrase
'official channels'.

Scope decision (cross-vendor judge panel, 3 framings -> Candidate A "minimal, prior-aligned"
won all 3, HIGH x2): per the LOCKED keep-Official-labels / drop-verified-chrome decision
(newstab-design-and-demo-strategy), the 'Official' SOURCE labels and the data-model 'official'
keys are PRESERVED unchanged. The only de-jargon is making the disclosure's routing concrete.
"""
import re
import json
from pathlib import Path

CATEGORY = "behavioral"
REPO = Path(__file__).resolve().parent.parent
DASH = REPO / "dashboard.html"
ARCHIVE = REPO / "data" / "news_archive.json"


def _en(key):
    m = re.search(r'"' + re.escape(key) + r'":\s*\{\s*en:\s*"([^"]*)"', DASH.read_text(encoding="utf-8"))
    return m.group(1) if m else ""


def test_ai_disclosure_routes_concretely():
    # The disclosure is rendered as two lines (disclosure.ai + disclosure.aiRoute, item I);
    # the concrete life-safety routing lives in the routing line. Check across both so the
    # safety property (route to ggcity/911, not vague "official channels") is preserved.
    val = _en("disclosure.ai") + " " + _en("disclosure.aiRoute")
    low = val.lower()
    concrete = "ggcity.org/emergency" in low or "911" in low
    no_vague = "official channels" not in low
    return {"passed": concrete and no_vague,
            "details": f"concrete_routing={concrete} no_vague_'official channels'={no_vague}"}


def test_official_source_labels_preserved():
    """keep-Official-labels decision: the 'Official' source-group header + the official i18n
    KEY NAMES stay (renaming them would break filters/icons and soften authority)."""
    text = DASH.read_text(encoding="utf-8")
    keeps = ['"info.group.official"', '"news.type.official"', '"news.badge.official"']
    missing = [k for k in keeps if k not in text]
    return {"passed": not missing,
            "details": "official i18n key names intact" if not missing else f"missing: {missing}"}


def test_data_model_official_type_intact():
    """The data-model type:'official' must survive de-jargon so the feed filters/sorting work."""
    d = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    n = sum(1 for it in d.get("items", []) if it.get("type") == "official")
    return {"passed": n >= 10, "details": f"official-type archive items: {n} (want >=10)"}
