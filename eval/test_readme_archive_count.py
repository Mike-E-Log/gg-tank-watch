"""Guard (Batch 3, 2026-06-01): the README's archive-inventory claim stays in sync with the
actual frozen data/news_archive.json.

The README "honest by construction" section cited "39 items (29 articles, 10 videos) across 17
outlets" — a count that drifted stale after the Batch 2 expansion to 92 items (an adversarial
review flagged it as a credibility risk: an archive-framed honesty section citing a wrong
inventory). The archive is FROZEN, so these numbers are fixed; this guard locks the README copy
to the data so a future edit can't re-introduce the drift. Phrasing must keep each number
adjacent to its unit ("92 items", "56 articles", ...) so the guard can parse it.

Extended 2026-07-21 (Fable 5 audit, finding B2): data/NEWS_ARCHIVE_AUDIT.md carried the same
breakdown with 3 of 4 figures wrong, exactly because only the README was guarded. Both prose
surfaces are now checked against the data. First number-adjacent-to-unit match per file wins,
so the audit doc's historical compilation notes (line 100+) stay out of scope.

Extended again 2026-07-21 (test-count churn root-cause fix): the TEST-COUNT story drifted
seven times in the repo's history because a growing census was pinned as static text with no
guard. The census check below locks README / CLAUDE.md / CONTRIBUTING.md to the actual
number of discovered test functions, so growing the suite without updating the docs fails
the build in the same PR. Remote surfaces (portfolio sites, applications) deliberately use
floor wording ("more than 200") and are out of scope here.
"""
import json
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO = Path(__file__).resolve().parent.parent
README = REPO / "README.md"
AUDIT_DOC = REPO / "data" / "NEWS_ARCHIVE_AUDIT.md"
ARCHIVE = REPO / "public" / "data" / "news_archive.json"
EVAL_DIR = REPO / "eval"


def _census():
    """Count test functions the way run_all discovers them: every `def test_` in
    eval/test_*.py. Modules with CATEGORY == "integration" are opt-in (skipped in
    the default run the docs describe), so they count toward the full census only."""
    files = sorted(EVAL_DIR.glob("test_*.py"))
    total = default = 0
    for f in files:
        src = f.read_text(encoding="utf-8")
        n = len(re.findall(r"^\s*def test_\w+", src, re.M))
        total += n
        if not re.search(r'^CATEGORY\s*=\s*"integration"', src, re.M):
            default += n
    return {"files": len(files), "default": default, "full": total}


def _census_doc_mismatches():
    """Folded into the breakdown test (not a new test function) so the guard itself
    does not grow the census it locks."""
    c = _census()
    readme = README.read_text(encoding="utf-8")
    claude = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
    contributing = (REPO / "docs" / "CONTRIBUTING.md").read_text(encoding="utf-8")
    d, full, files = c["default"], c["full"], c["files"]
    checks = {
        "readme badge": f"eval-{d}%20tests" in readme,
        "readme runs-N/N": f"runs {d}/{d}" in readme,
        "readme suite-of": f"A suite of {d} automated tests" in readme,
        "readme expected-block": f"TOTAL           {d}/{d}" in readme,
        "readme tests-across-files": f"{d} automated pass/fail tests across {files} files" in readme,
        "readme full-census": f"full census is **{full}**" in readme,
        "claude.md harness": f"A {d}-test eval harness" in claude,
        "contributing N/N": f"currently {d}/{d}" in contributing,
    }
    return [k for k, ok in checks.items() if not ok], c


def _counts():
    items = json.loads(ARCHIVE.read_text(encoding="utf-8"))["items"]
    total = len(items)
    vids = sum(1 for i in items if i.get("youtube_id") or i.get("type") == "video")
    arts = sum(1 for i in items if i.get("type") == "article")
    offs = sum(1 for i in items if i.get("type") == "official")
    outlets = len({(i.get("outlet") or "").strip() for i in items if i.get("outlet")})
    return {"items": total, "articles": arts, "videos": vids,
            "official statements": offs, "outlets": outlets}


def _claimed(unit, doc=None):
    txt = (doc or README).read_text(encoding="utf-8")
    m = re.search(r"(\d+)\s+" + re.escape(unit), txt)
    return int(m.group(1)) if m else None


def test_readme_total_item_count_matches_data():
    want = _counts()["items"]
    got = {doc.name: _claimed("items", doc) for doc in (README, AUDIT_DOC)}
    return {"passed": all(v == want for v in got.values()),
            "details": f"claimed 'items'={got}; data={want}"}


def test_readme_breakdown_matches_data():
    c = _counts()
    mismatches = {}
    for doc in (README, AUDIT_DOC):
        for unit in ("articles", "videos", "official statements", "outlets"):
            got = _claimed(unit, doc)
            if got != c[unit]:
                mismatches[f"{doc.name}: {unit}"] = f"claimed={got}/data={c[unit]}"
    stale_counts, census = _census_doc_mismatches()
    for k in stale_counts:
        mismatches[f"test-count: {k}"] = (f"doc copy stale vs census "
                                          f"(default={census['default']} full={census['full']} "
                                          f"files={census['files']})")
    return {"passed": not mismatches,
            "details": "README + NEWS_ARCHIVE_AUDIT breakdowns and test-count copies match"
            if not mismatches else f"mismatches: {mismatches}"}


def test_readme_methodology_past_tense():
    """The methodology / data-pipeline narrative migrated OUT of the in-app About in the 6-tab
    redesign (2026-06-02) now lives in the README and must read PAST tense — a frozen archive
    must not describe its retired pipeline as ongoing. ('was updated every' / 'cross-referenced
    against multiple sources', not present-tense 'status updated every'.) This re-homes the
    integrity property the in-app test_method_pipeline_past_tense used to guard."""
    txt = README.read_text(encoding="utf-8").lower()
    past = "was updated every" in txt and "cross-referenced against multiple sources" in txt
    no_present = "status updated every" not in txt
    return {"passed": past and no_present,
            "details": f"past_tense={past} no_present_tense={no_present}"}
