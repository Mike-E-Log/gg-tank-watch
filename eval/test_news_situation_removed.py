"""Guard: the News tab's "Current Situation" box is removed (fully-historical pivot, 2026-06-01).

The Current Situation box (#news-situation) surfaced incident.status_headline as a live-feeling
"current" callout above the feed. In a frozen historical archive nothing is current: the resolved
state is shown by the hero status row ("Resolved" / "Lifted"), and the situation box is removed
entirely — markup, CSS, render block, and i18n keys. These guards prevent it silently returning.
"""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"


def test_news_situation_markup_and_css_removed():
    """No #news-situation div and no .news-situation* CSS rules. The `news-situation` token
    appears in the div id/class, the five CSS rules, and the JS className assignments, so a
    single absence check covers the whole surface."""
    text = DASHBOARD.read_text(encoding="utf-8")
    gone = "news-situation" not in text
    return {"passed": gone,
            "details": "no news-situation markup/CSS/JS" if gone
            else f"news-situation still referenced ({text.count('news-situation')} hits)"}


def test_news_situation_i18n_keys_removed():
    """Both Current-situation i18n keys are gone (news.situation.label, news.currentSituation)."""
    text = DASHBOARD.read_text(encoding="utf-8")
    gone = '"news.situation.label"' not in text and '"news.currentSituation"' not in text
    return {"passed": gone,
            "details": "situation i18n keys removed" if gone
            else "news.situation.label / news.currentSituation still present"}


def test_status_headline_no_longer_rendered():
    """The situation render block was the only reader of incident.status_headline in the UI;
    removing it means status_headline is no longer surfaced in the News tab."""
    text = DASHBOARD.read_text(encoding="utf-8")
    gone = "status_headline" not in text
    return {"passed": gone,
            "details": "status_headline render path removed" if gone
            else "status_headline still read in dashboard.html"}
