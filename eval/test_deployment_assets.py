"""Guard: every runtime asset the app fetches must actually be DEPLOYED (2026-06-01).

Root cause this guards against: `.vercelignore` had a bare `data` line that excluded the
whole directory, so `data/news_archive.json` was git-tracked (eval + local server saw it)
but 404'd in production — the News archive silently fell back to the live videos[] feed AND
the new service worker couldn't install (precaching a 404 makes cache.addAll reject).

This asserts, against `.vercelignore`'s gitignore-style patterns, that the curated archive
and every sw.js STATIC_ASSETS entry are NOT excluded from the Vercel upload. stdlib only
(no pathspec) so the eval harness keeps zero third-party deps.
"""
import re
from fnmatch import fnmatch
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
VERCELIGNORE = REPO_ROOT / ".vercelignore"
SW = REPO_ROOT / "sw.js"


def _patterns():
    lines = VERCELIGNORE.read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def _matches(pattern, path):
    """(matched, is_negation) for one gitignore-style pattern against a repo-relative path."""
    neg = pattern.startswith("!")
    pat = (pattern[1:] if neg else pattern).rstrip("/")
    if pat.endswith("/*"):                       # directory-contents glob, e.g. data/*
        prefix = pat[:-2]
        return (path == prefix or path.startswith(prefix + "/")), neg
    if "/" in pat:                               # path-anchored (may glob)
        return (fnmatch(path, pat) or path == pat or path.startswith(pat + "/")), neg
    if any(c in pat for c in "*?["):             # basename glob, e.g. *.md
        return any(fnmatch(seg, pat) for seg in path.split("/")), neg
    segs = path.split("/")                        # bare name: file or dir at any depth
    return (path == pat or pat in segs or path.startswith(pat + "/")), neg


def _is_excluded(path, patterns):
    path = path.lstrip("/")
    excluded = False
    for p in patterns:                            # gitignore: last matching pattern wins
        m, neg = _matches(p, path)
        if m:
            excluded = not neg
    return excluded


def _sw_static_assets():
    text = SW.read_text(encoding="utf-8")
    m = re.search(r"STATIC_ASSETS\s*=\s*\[(.*?)\]", text, re.DOTALL)
    return re.findall(r"""["']([^"']+)["']""", m.group(1)) if m else []


def test_news_archive_is_deployable():
    pats = _patterns()
    excluded = _is_excluded("data/news_archive.json", pats)
    return {"passed": not excluded,
            "details": ("data/news_archive.json deploys (not .vercelignore-excluded)"
                        if not excluded else
                        f"data/news_archive.json is EXCLUDED by .vercelignore -> 404 in prod. patterns={pats}")}


def test_sw_static_assets_all_deployable():
    pats = _patterns()
    assets = _sw_static_assets()
    excluded = [a for a in assets if a not in ("/",) and _is_excluded(a, pats)]
    return {"passed": len(assets) > 0 and not excluded,
            "details": (f"all {len(assets)} sw STATIC_ASSETS deploy"
                        if (assets and not excluded)
                        else f"excluded sw assets (would 404 + break SW install): {excluded}; parsed={assets}"),
            "metrics": {"assets": len(assets), "excluded": len(excluded)}}
