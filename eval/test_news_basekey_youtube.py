"""Behavioral tests for newsBaseKey() — the client-side dedup key in dashboard.html.

The key collapses ABC7 live-blog `/entry/<id>/` fragments so different fragments
of one running blog share a key (intended). It must NOT collapse distinct YouTube
videos: every clip lives at `youtube.com/watch` and differs only by the `?v=` id,
so stripping the query made all 14 archive videos share one key and the
NEWS_MAX_PER_BASE=2 dedup dropped 12 of them.

Each test extracts the real newsBaseKey() source from dashboard.html and runs it
through node, so we test shipped behavior — not a reimplementation.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "public" / "dashboard.html"
ARCHIVE = REPO_ROOT / "public" / "data" / "news_archive.json"


def _extract_fn(src: str, name: str) -> str:
    """Extract a `function <name>(...) { ... }` body by brace-matching."""
    start = src.index(f"function {name}(")
    i = src.index("{", start)
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[start : j + 1]
    raise ValueError(f"unbalanced braces extracting {name}")


def _base_keys(urls: list[str]) -> list[str]:
    fn = _extract_fn(DASHBOARD.read_text(encoding="utf-8"), "newsBaseKey")
    runner = fn + "\nconst urls = JSON.parse(process.argv[1]);\n" \
                  "console.log(JSON.stringify(urls.map(newsBaseKey)));\n"
    out = subprocess.run(
        ["node", "-e", runner, json.dumps(urls)],
        capture_output=True, text=True, timeout=30,
    )
    if out.returncode != 0:
        raise RuntimeError(f"node failed: {out.stderr}")
    return json.loads(out.stdout)


def test_youtube_basekey_preserves_identity():
    urls = [
        "https://www.youtube.com/watch?v=H-wR6qybCPA",
        "https://www.youtube.com/watch?v=P3tTEWNL97o",
        "https://youtu.be/oRVlU3PrtcI",
        "https://youtu.be/aVuIrKAlcm4",
    ]
    keys = _base_keys(urls)
    distinct = len(set(keys)) == len(urls)
    return {
        "passed": distinct,
        "details": f"4 distinct YouTube videos -> {len(set(keys))} distinct keys; keys={keys}",
        "metrics": {"distinct_keys": len(set(keys)), "input_urls": len(urls)},
    }


def test_archive_youtube_videos_all_distinct():
    items = json.loads(ARCHIVE.read_text(encoding="utf-8"))["items"]
    yt = [it["url"] for it in items if it.get("youtube_id")]
    keys = _base_keys(yt)
    distinct = len(set(keys)) == len(yt)
    return {
        "passed": distinct,
        "details": f"{len(yt)} archive YouTube videos -> {len(set(keys))} distinct keys (need {len(yt)})",
        "metrics": {"youtube_items": len(yt), "distinct_keys": len(set(keys))},
    }


def test_liveblog_basekey_still_collapses():
    # Regression guard for the behavior newsBaseKey was actually built for:
    # ABC7 running-blog /entry/<id>/ fragments must still share one base key.
    urls = [
        "https://abc7.com/live-updates/garden-grove/entry/111/",
        "https://abc7.com/live-updates/garden-grove/entry/222/",
        "https://abc7.com/live-updates/garden-grove/entry/333/",
    ]
    keys = _base_keys(urls)
    collapsed = len(set(keys)) == 1
    return {
        "passed": collapsed,
        "details": f"3 live-blog fragments -> {len(set(keys))} key(s) (want 1); keys={keys}",
        "metrics": {"distinct_keys": len(set(keys))},
    }
