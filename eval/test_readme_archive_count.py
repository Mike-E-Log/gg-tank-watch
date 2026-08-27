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
guard. The census check below locks README / CLAUDE.md / CONTRIBUTING.md — and, since
2026-08-10, docs/safety-method/safety-method-writeup.md + evidence-summary.md — to the
actual number of discovered test functions, so growing the suite without updating the
docs fails the build in the same PR. Remote surfaces (portfolio sites, applications) deliberately use
floor wording ("more than 200") and are out of scope here.

Re-scoped 2026-08-26 (operator ruling, "one exact place"): the exact count now lives ONLY
in the README's runnable expected-output block; every other surface says "automated tests"
with no number. The guard keeps the canonical block exact and FAILS on any stray numbered
test-count claim in the five guarded docs, so the reconciliation burden cannot creep back.
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
    does not grow the census it locks.

    One-exact-place policy (operator ruling 2026-08-26): the canonical expected-output
    block in the README must match the live census exactly; everywhere else, any
    number sitting on a test-count claim is a violation."""
    c = _census()
    d, full = c["default"], c["full"]
    readme = README.read_text(encoding="utf-8")
    problems = [k for k, ok in {
        "readme expected-intro": f"Expected ({d} tests, all green)" in readme,
        "readme expected-block": f"TOTAL           {d}/{d}" in readme,
        "readme full-census": f"full census is **{full}**" in readme,
    }.items() if not ok]
    docs = {
        "README.md": readme,
        "CLAUDE.md": (REPO / "CLAUDE.md").read_text(encoding="utf-8"),
        "docs/CONTRIBUTING.md": (REPO / "docs" / "CONTRIBUTING.md").read_text(encoding="utf-8"),
        "docs/safety-method/safety-method-writeup.md":
            (REPO / "docs" / "safety-method" / "safety-method-writeup.md").read_text(encoding="utf-8"),
        "docs/safety-method/evidence-summary.md":
            (REPO / "docs" / "safety-method" / "evidence-summary.md").read_text(encoding="utf-8"),
    }
    # Canonical intro + the sealed method-extract export (a frozen historical constant).
    allowed = (f"Expected ({d} tests, all green)", "210/210")
    for label, txt in docs.items():
        for token in allowed:
            txt = txt.replace(token, " ")
        for line in txt.splitlines():
            if "test" not in line.lower():
                continue
            hits = re.findall(r"\b\d{2,4}(?:-|\s+)(?:automated\s+|pass/fail\s+)?tests?\b", line)
            hits += re.findall(r"\b\d{2,4}/\d{2,4}\b", line)
            for h in hits:
                problems.append(f"{label}: stray numbered test-count claim '{h}'")
    return problems, c


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
