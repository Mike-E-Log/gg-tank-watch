"""Guard (Fable 5 audit D5, 2026-07-21): run_all.py must fail loudly when ZERO
tests run. A --only/--skip typo that matched nothing used to print "TOTAL 0/0"
and exit 0, silently satisfying any CI gate keyed on the exit code alone. The
runner now exits 2 (structural failure, the same code as a crashed module)
when no test executes.

Subprocess-based, same pattern as test_gather_facts' failure-contract test.
The child run matches no tests, so there is no recursion concern.
"""
import subprocess
import sys
from pathlib import Path

CATEGORY = "behavioral"
EVAL_DIR = Path(__file__).resolve().parent


def test_zero_tests_run_is_a_failure():
    p = subprocess.run(
        [sys.executable, str(EVAL_DIR / "run_all.py"),
         "--only", "no-such-test-name-zzz", "--quiet"],
        cwd=EVAL_DIR.parent, capture_output=True, text=True,
    )
    return {
        "passed": p.returncode == 2,
        "details": f"exit={p.returncode} (want 2 when zero tests run)",
        "metrics": {"exit_code": p.returncode},
    }
