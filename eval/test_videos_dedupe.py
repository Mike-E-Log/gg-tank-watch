"""Behavioral tests for video dedupe + URL-based reclassification.

Covers:
- Duplicate URLs in raw videos[] collapse to one entry in status.json
- is_video is re-derived from URL pattern (youtube.com / youtu.be / .../video/...),
  overriding any incoming is_video flag
- Dedupe keeps the first occurrence, drops later ones

Each test sets up a fresh sandbox dir under eval/.last_run/videos_dedupe/, runs
the writer with the test facts piped via stdin, and asserts on status.json.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
WRITER = REPO_ROOT / "scripts" / "update_status.py"
SANDBOX = Path(__file__).resolve().parent / ".last_run" / "videos_dedupe"


def _reset_sandbox():
    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    SANDBOX.mkdir(parents=True)
    (SANDBOX / "config.json").write_text(json.dumps({
        "zone_status": "outside_downwind",
        "writer_interval_minutes": 30,
        "incident": {
            "name": "Test Incident",
            "facility": "Test Facility",
            "started_iso": "2026-05-21T22:40:00Z",
            "address_checker_url": "https://example.invalid/",
        },
        "schema_version": 1,
    }))
    (SANDBOX / "scripts").mkdir()
    shutil.copyfile(WRITER, SANDBOX / "scripts" / "update_status.py")


def _tick(facts: dict) -> dict | None:
    payload = json.dumps(facts)
    subprocess.run(
        [sys.executable, str(SANDBOX / "scripts" / "update_status.py")],
        input=payload,
        cwd=str(SANDBOX),
        capture_output=True,
        text=True,
        timeout=30,
    )
    p = SANDBOX / "status.json"
    return json.loads(p.read_text()) if p.exists() else None


def test_duplicate_urls_collapse():
    _reset_sandbox()
    snap = _tick({"videos": [
        {"outlet": "ABC7", "title": "A", "url": "https://abc7.com/live-updates/x"},
        {"outlet": "ABC7", "title": "B", "url": "https://abc7.com/live-updates/x"},
        {"outlet": "ABC7", "title": "C", "url": "https://abc7.com/live-updates/x"},
        {"outlet": "NBC",  "title": "D", "url": "https://nbclosangeles.com/live"},
    ]})
    videos = snap and snap.get("videos") or []
    urls = [v.get("url") for v in videos]
    abc_count = urls.count("https://abc7.com/live-updates/x")
    passed = abc_count == 1 and len(videos) == 2
    return {
        "passed": passed,
        "details": f"len(videos)={len(videos)} abc_dupes={abc_count} urls={urls}",
        "metrics": {"video_count": len(videos), "abc_dupe_count": abc_count},
    }


def test_url_pattern_overrides_is_video_flag():
    _reset_sandbox()
    snap = _tick({"videos": [
        {"outlet": "ABC7", "title": "story",   "url": "https://abc7.com/story/123",                          "is_video": True},
        {"outlet": "NBC",  "title": "explain", "url": "https://nbclosangeles.com/video/news/local/x/",       "is_video": False},
        {"outlet": "YT",   "title": "clip",    "url": "https://www.youtube.com/watch?v=abc123"},
        {"outlet": "YT",   "title": "short",   "url": "https://youtu.be/xyz"},
    ]})
    videos = snap and snap.get("videos") or []
    by_url = {v.get("url"): v for v in videos}
    abc_ok    = by_url.get("https://abc7.com/story/123",                {}).get("is_video") is False
    nbc_ok    = by_url.get("https://nbclosangeles.com/video/news/local/x/", {}).get("is_video") is True
    yt_ok     = by_url.get("https://www.youtube.com/watch?v=abc123",    {}).get("is_video") is True
    short_ok  = by_url.get("https://youtu.be/xyz",                       {}).get("is_video") is True
    passed = abc_ok and nbc_ok and yt_ok and short_ok
    return {
        "passed": passed,
        "details": f"abc_story_is_video=False?{abc_ok} nbc_video_path_is_video=True?{nbc_ok} youtube=True?{yt_ok} youtu.be=True?{short_ok}",
        "metrics": {"abc_ok": abc_ok, "nbc_ok": nbc_ok, "yt_ok": yt_ok, "short_ok": short_ok},
    }


def test_dedupe_keeps_first_occurrence():
    _reset_sandbox()
    snap = _tick({"videos": [
        {"outlet": "ABC7", "title": "FIRST",  "url": "https://abc7.com/x"},
        {"outlet": "ABC7", "title": "SECOND", "url": "https://abc7.com/x"},
    ]})
    videos = snap and snap.get("videos") or []
    passed = len(videos) == 1 and videos and videos[0].get("title") == "FIRST"
    return {
        "passed": passed,
        "details": f"len={len(videos)} first_title={(videos[0].get('title') if videos else None)!r}",
        "metrics": {"video_count": len(videos)},
    }
