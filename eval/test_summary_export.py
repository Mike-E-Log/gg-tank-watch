"""Verifies the deterministic --summary-out export: byte-stable across runs (no
timestamps/durations), sorted, all-pass, and commit-bound. Asserts the determinism
CONTRACT rather than a frozen test census, so it stays green as the suite evolves.

CATEGORY=schema so it runs in the default (non-integration) suite. When run_all.py
generates a summary it sets GG_SUMMARY_EXPORT_CHILD; in that child we expose no test
functions, which both excludes this meta-test from the artifact and prevents unbounded
recursion (the export re-invokes the suite, which would re-invoke this test, ...).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

CATEGORY = "schema"
EVAL_DIR = Path(__file__).resolve().parent
_IN_SUMMARY_CHILD = bool(os.environ.get("GG_SUMMARY_EXPORT_CHILD"))


def _gen(tmp_name: str) -> str:
    out = EVAL_DIR / tmp_name
    subprocess.run(
        [sys.executable, str(EVAL_DIR / "run_all.py"), "--skip", "integration",
         "--quiet", "--summary-out", str(out)],
        cwd=EVAL_DIR.parent, check=True,
    )
    text = out.read_text(encoding="utf-8")
    out.unlink()
    return text


if not _IN_SUMMARY_CHILD:

    def test_summary_export_is_deterministic_and_commit_bound():
        a = _gen("_sum_a.json")
        b = _gen("_sum_b.json")
        assert a == b, "summary must be byte-identical across runs (no timestamps/durations)"
        data = json.loads(a)
        assert set(data.keys()) == {"meta", "tests"}, f"unexpected top-level keys: {sorted(data)}"
        keys = list(data["tests"].keys())
        assert keys == sorted(keys), "test keys must be sorted"
        assert all(v == "pass" for v in data["tests"].values()), "all curated tests must pass"
        meta = data["meta"]
        assert meta["source_commit"] and meta["source_commit"] != "unknown", "must be commit-bound"
        assert meta["runner"] == "eval/run_all.py --skip integration"
        assert meta["total"] == len(data["tests"]), "meta.total must equal the number of tests"
        assert meta["total"] == meta["behavioral"] + meta["schema"], "categories must sum to total"
        assert meta["behavioral"] > 0 and meta["schema"] > 0
        return {
            "passed": True,
            "details": f"{len(a)} bytes stable, {meta['total']} tests, commit {meta['source_commit'][:7]}",
        }
