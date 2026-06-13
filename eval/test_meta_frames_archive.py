"""Guard (T9, archive pivot 2026-06-01): the page meta / Open Graph / Twitter / manifest
descriptions and the share-sheet text frame the app as a HISTORICAL ARCHIVE of the resolved
May 21-26, 2026 emergency, not a LIVE tool. A frozen archive whose social/share preview says
'live demonstration' / 'situational awareness' reads as actively monitoring an active emergency.
"""
import re
import json
from pathlib import Path

CATEGORY = "behavioral"
REPO = Path(__file__).resolve().parent.parent
DASH = REPO / "public" / "dashboard.html"
MANIFEST = REPO / "public" / "manifest.json"

LIVE_TERMS = ["live demonstration", "live demo", "situational awareness", "live situational"]


def _meta(attr, val):
    text = DASH.read_text(encoding="utf-8")
    m = re.search(r'<meta[^>]*' + re.escape(attr) + r'="' + re.escape(val) + r'"[^>]*content="([^"]*)"', text)
    if not m:
        m = re.search(r'<meta[^>]*content="([^"]*)"[^>]*' + re.escape(attr) + r'="' + re.escape(val) + r'"', text)
    return m.group(1) if m else ""


def _archive_ok(val):
    low = val.lower()
    frames = "archive" in low or "historical" in low
    no_live = not any(t in low for t in LIVE_TERMS)
    return frames and no_live, frames, no_live


def test_meta_description_frames_archive():
    val = _meta("name", "description")
    ok, frames, no_live = _archive_ok(val)
    return {"passed": ok, "details": f"frames_archive={frames} no_live={no_live} :: {val[:70]}"}


def test_og_description_frames_archive():
    val = _meta("property", "og:description")
    ok, frames, no_live = _archive_ok(val)
    return {"passed": ok, "details": f"frames_archive={frames} no_live={no_live}"}


def test_og_image_alt_frames_archive():
    val = _meta("property", "og:image:alt")
    low = val.lower()
    ok = ("archive" in low or "historical" in low) and "situational awareness" not in low
    return {"passed": ok, "details": f"{val[:70]}"}


def test_twitter_description_frames_archive():
    val = _meta("name", "twitter:description")
    ok, frames, no_live = _archive_ok(val)
    return {"passed": ok, "details": f"frames_archive={frames} no_live={no_live}"}


def test_manifest_description_frames_archive():
    d = json.loads(MANIFEST.read_text(encoding="utf-8"))
    val = (d.get("description") or "").lower()
    ok = ("archive" in val or "historical" in val) and "live demonstration" not in val
    return {"passed": ok, "details": f"{val[:80]}"}


def test_share_text_frames_archive():
    """The share-sheet text literal (a JS field) must not present the app as 'Live situational
    awareness'; it should read as a historical archive."""
    text = DASH.read_text(encoding="utf-8")
    ok = "Live situational awareness for the Garden Grove" not in text
    return {"passed": ok, "details": "share text no longer 'Live situational awareness'" if ok
            else "share text still says 'Live situational awareness'"}
