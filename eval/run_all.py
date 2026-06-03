"""Eval runner. Auto-discovers test_*.py in eval/, runs every test_* function,
prints a scorecard, appends one JSON line per test to scores.jsonl.

Exit code: 0 if all passed, 1 if any failed, 2 if a test module crashed.

Usage:
  python run_all.py
  python run_all.py --skip integration
  python run_all.py --only test_writer
  python run_all.py --quiet
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
SCORES_PATH = EVAL_DIR / "scores.jsonl"


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def discover_test_modules():
    """Yield (module_name, path) for each test_*.py in EVAL_DIR."""
    for p in sorted(EVAL_DIR.glob("test_*.py")):
        yield p.stem, p


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def run_test(fn) -> dict:
    """Call a test_ function; normalize its return to {passed, details, metrics}."""
    try:
        result = fn()
        if result is None:
            return {"passed": True, "details": "(no return value; assumed pass)", "metrics": {}}
        if isinstance(result, bool):
            return {"passed": result, "details": "", "metrics": {}}
        if isinstance(result, dict):
            return {
                "passed": bool(result.get("passed", False)),
                "details": str(result.get("details", "")),
                "metrics": result.get("metrics", {}),
            }
        return {"passed": False, "details": f"unexpected return type {type(result).__name__}: {result!r}", "metrics": {}}
    except AssertionError as e:
        return {"passed": False, "details": f"assertion failed: {e}", "metrics": {}}
    except Exception as e:
        tb = traceback.format_exc()
        return {"passed": False, "details": f"raised {type(e).__name__}: {e}\n{tb}", "metrics": {}}


def append_score(entry: dict) -> None:
    with SCORES_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")


def _source_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=EVAL_DIR.parent,
            capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def build_summary(results) -> dict:
    """Deterministic summary: sorted {module::test: pass|fail} + commit-bound meta. No timestamps."""
    tests = {f"{m}::{t}": ("pass" if o["passed"] else "fail") for m, t, _c, o in results}
    by_cat = {}
    for _m, _t, cat, o in results:
        d = by_cat.setdefault(cat, 0)
        by_cat[cat] = d + (1 if o["passed"] else 0)
    return {
        "meta": {
            "source_commit": _source_commit(),
            "runner": "eval/run_all.py --skip integration",
            "total": len(tests),
            "behavioral": by_cat.get("behavioral", 0),
            "schema": by_cat.get("schema", 0),
        },
        "tests": dict(sorted(tests.items())),
    }


# Test classification — used to skip categories.
# Add a `CATEGORY = "..."` module-level attribute to a test_*.py to override.
DEFAULT_CATEGORY = "behavioral"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skip", action="append", default=[], help="skip a category (e.g. integration)")
    ap.add_argument("--only", action="append", default=[], help="only run module names containing this string")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--summary-out", default=None, help="write a deterministic summary JSON to PATH")
    args = ap.parse_args()

    # When generating a summary, mark child runs so meta-tests that re-invoke the suite
    # (e.g. test_summary_export) expose no tests — prevents unbounded recursion and keeps
    # the artifact to the curated behavioral+schema suite.
    if args.summary_out:
        os.environ["GG_SUMMARY_EXPORT_CHILD"] = "1"

    results = []
    crashed_modules = []

    for module_name, path in discover_test_modules():
        if args.only and not any(o in module_name for o in args.only):
            continue
        try:
            mod = load_module(module_name, path)
        except Exception as e:
            print(f"[!] could not load {module_name}: {e}")
            crashed_modules.append(module_name)
            continue

        category = getattr(mod, "CATEGORY", DEFAULT_CATEGORY)
        if category in args.skip:
            print(f"[ ] skipped {module_name} (category: {category})")
            continue

        test_fns = [(name, getattr(mod, name)) for name in dir(mod) if name.startswith("test_") and callable(getattr(mod, name))]
        if not test_fns:
            print(f"[ ] {module_name}: no test_ functions found")
            continue

        for test_name, fn in test_fns:
            outcome = run_test(fn)
            results.append((module_name, test_name, category, outcome))
            if not args.quiet:
                mark = "PASS" if outcome["passed"] else "FAIL"
                detail_brief = outcome["details"].split("\n")[0][:120] if outcome["details"] else ""
                print(f"  [{mark}] {module_name}::{test_name}  {detail_brief}")
            append_score({
                "run_iso": utcnow_iso(),
                "module": module_name,
                "test": test_name,
                "category": category,
                "passed": outcome["passed"],
                "details": outcome["details"][:1000],
                "metrics": outcome["metrics"],
            })

    # Scorecard
    print()
    print("=" * 64)
    by_category = {}
    for _, _, cat, outcome in results:
        d = by_category.setdefault(cat, {"passed": 0, "failed": 0})
        d["passed" if outcome["passed"] else "failed"] += 1
    total_passed = sum(d["passed"] for d in by_category.values())
    total_failed = sum(d["failed"] for d in by_category.values())
    total = total_passed + total_failed
    for cat, d in sorted(by_category.items()):
        pct = (d["passed"] / max(1, d["passed"] + d["failed"])) * 100
        print(f"  {cat:14s}  {d['passed']:>3}/{d['passed']+d['failed']:<3}  ({pct:5.1f}% pass)")
    print("-" * 64)
    overall_pct = (total_passed / max(1, total)) * 100
    print(f"  {'TOTAL':14s}  {total_passed:>3}/{total:<3}  ({overall_pct:5.1f}% pass)")
    if crashed_modules:
        print(f"\n  crashed modules: {', '.join(crashed_modules)}")
    print("=" * 64)
    print(f"  scores.jsonl: {SCORES_PATH} (now {SCORES_PATH.stat().st_size if SCORES_PATH.exists() else 0} bytes)")

    if args.summary_out:
        summary = build_summary(results)
        Path(args.summary_out).write_text(
            json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"  summary-out: {args.summary_out} ({len(summary['tests'])} tests)")

    if crashed_modules:
        sys.exit(2)
    sys.exit(0 if total_failed == 0 else 1)


if __name__ == "__main__":
    main()
