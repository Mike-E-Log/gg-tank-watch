"""Guard: every runtime asset the app fetches must be present in the deployed output.

The served web root is public/ (Vercel "Other" preset; the project Root Directory is
public/, so all of public/ is uploaded and served and everything above it is excluded by
the root boundary). This asserts that every sw.js STATIC_ASSETS serve-path resolves to a
real file under public/, and the curated archive exists — a missing precached file 404s
and breaks the service-worker install (cache.addAll rejects on a 404). Originally guarded
a `.vercelignore` exclusion footgun (2026-06-01); after the public/ relocation + the
Root-Directory move (2026-06-13), .vercelignore is gone and on-disk existence under
public/ is the meaningful deploy guarantee. stdlib only.
"""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC = REPO_ROOT / "public"
SW = PUBLIC / "sw.js"


def _sw_static_assets():
    text = SW.read_text(encoding="utf-8")
    m = re.search(r"STATIC_ASSETS\s*=\s*\[(.*?)\]", text, re.DOTALL)
    return re.findall(r"""["']([^"']+)["']""", m.group(1)) if m else []


def test_news_archive_is_deployable():
    archive = PUBLIC / "data" / "news_archive.json"
    return {"passed": archive.exists(),
            "details": ("public/data/news_archive.json present"
                        if archive.exists() else "public/data/news_archive.json MISSING")}


def test_sw_static_assets_all_deployable():
    assets = [a for a in _sw_static_assets() if a != "/"]
    missing = [a for a in assets if not (PUBLIC / a.lstrip("/")).exists()]
    return {"passed": len(assets) > 0 and not missing,
            "details": (f"all {len(assets)} sw STATIC_ASSETS exist under public/"
                        if (assets and not missing)
                        else f"missing under public/: {missing}; parsed={assets}"),
            "metrics": {"assets": len(assets), "missing": len(missing)}}
