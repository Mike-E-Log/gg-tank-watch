"""Guard (Fable 5 audit D5, 2026-07-21): run_all.py must fail loudly when ZERO
tests run. A --only/--skip typo that matched nothing used to print "TOTAL 0/0"
and exit 0, silently satisfying any CI gate keyed on the exit code alone. The
runner now exits 2 (structural failure, the same code as a crashed module)
when no test executes.

Subprocess-based, same pattern as test_gather_facts' failure-contract test.
The child run matches no tests, so there is no recursion concern.

Folded-in guard (2026-08-23, census locked at 212 so no new test function —
the census guard's own documented fold pattern): run_all._sanitize_local_paths
must scrub machine-local absolute paths from test details before they reach
the committed ledger or CI stdout (a traceback leaked one in PR #83), while
leaving URLs untouched (an over-broad scrub matched the "s://" inside
"https://" and clobbered 129 ledger details the same day). Fixtures use the
carved-out "redacted" username and an RFC 6761 .test domain so the hygiene
guard never trips on this file.
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
    import run_all as ra
    s = ra._sanitize_local_paths(
        'raised X: boom\n  File "C:\\Users\\redacted\\x.py", line 1\n'
        '  File "/home/redacted/x.py", line 2\n'
        "keys=['https://example.test/Users/page']")
    paths_scrubbed = ("x.py" not in s and "C:" not in s and "/home/" not in s
                      and "<local-path>" in s
                      and "https://example.test/Users/page" in s)
    return {
        "passed": p.returncode == 2 and paths_scrubbed,
        "details": (f"exit={p.returncode} (want 2 when zero tests run); "
                    f"paths_scrubbed_urls_kept={paths_scrubbed}"),
        "metrics": {"exit_code": p.returncode},
    }
