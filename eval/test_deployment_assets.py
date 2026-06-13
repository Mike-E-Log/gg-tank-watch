"""Guard: every runtime asset the app fetches must actually be DEPLOYED.

The served web root is public/ (Vercel's "Other" preset serves public/ when it exists;
2026-06-13 relocation). This asserts that (a) every sw.js STATIC_ASSETS serve-path
resolves to a real file under public/, and (b) nothing under public/ is excluded from
the Vercel upload by .vercelignore. Originally caught a `.vercelignore` `data` line that
404'd data/news_archive.json in prod (2026-06-01); re-aimed at the public/ layout.
stdlib only (no pathspec) so the eval harness keeps zero third-party deps.
"""
import re
from fnmatch import fnmatch
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC = REPO_ROOT / "public"
VERCELIGNORE = REPO_ROOT / ".vercelignore"
SW = REPO_ROOT / "public" / "sw.js"


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
    rel = "public/data/news_archive.json"
    exists = (REPO_ROOT / rel).exists()
    excluded = _is_excluded(rel, _patterns())
    return {"passed": exists and not excluded,
            "details": (f"{rel} exists and is not .vercelignore-excluded"
                        if (exists and not excluded)
                        else f"exists={exists} excluded={excluded} for {rel}")}


def test_sw_static_assets_all_deployable():
    pats = _patterns()
    assets = [a for a in _sw_static_assets() if a != "/"]
    problems = []
    for a in assets:
        rel = "public/" + a.lstrip("/")           # serve-path -> on-disk public/ path
        if not (REPO_ROOT / rel).exists():
            problems.append(f"{a} -> missing {rel}")
        elif _is_excluded(rel, pats):
            problems.append(f"{a} -> .vercelignore-excluded {rel}")
    return {"passed": len(assets) > 0 and not problems,
            "details": (f"all {len(assets)} sw STATIC_ASSETS exist under public/ and deploy"
                        if (assets and not problems)
                        else f"problems: {problems}; parsed={assets}"),
            "metrics": {"assets": len(assets), "problems": len(problems)}}
