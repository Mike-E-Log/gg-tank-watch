"""Unit tests for scripts/gather_facts.py pure functions + its failure contract.

No live API is exercised. The headline test is test_graceful_failure_no_api_key:
the gatherer must exit non-zero AND print nothing when it can't run, so the writer
step is skipped and data goes visibly stale rather than fresh-stamped (F4).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
GATHERER = REPO_ROOT / "scripts" / "gather_facts.py"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from gather_facts import extract_json  # noqa: E402  (lazy anthropic import is inside main())
from gather_facts import PROMPT, MAX_USES  # noqa: E402


def test_extract_json_strips_fences():
    fenced = '```json\n{"a": 1, "b": "two"}\n```'
    prose = 'Here are the facts:\n{"a": 1, "b": "two"}\nThat is all.'
    ok = extract_json(fenced) == {"a": 1, "b": "two"} and extract_json(prose) == {"a": 1, "b": "two"}
    return {"passed": ok, "details": f"fenced+prose both parse to the same dict: {ok}"}


def test_extract_json_rejects_garbage():
    try:
        extract_json("no json object here at all")
        return {"passed": False, "details": "expected ValueError, got a silent result"}
    except ValueError:
        return {"passed": True, "details": "raised ValueError on garbage (not a silent {})"}
    except Exception as e:
        return {"passed": False, "details": f"raised wrong type {type(e).__name__}: {e}"}


def test_prompt_includes_vietnamese_sources():
    """Gatherer prompt must name Vietnamese-language sources for community coverage."""
    vi_sources = ["Nguoi Viet", "nguoi-viet.com"]
    found = any(s.lower() in PROMPT.lower() for s in vi_sources)
    return {
        "passed": found,
        "details": f"Vietnamese source mentioned in prompt: {found}",
    }


def test_prompt_includes_credibility_guidance():
    """Gatherer prompt must instruct model to prioritize official/Tier-1 sources."""
    has_tier = "tier" in PROMPT.lower() or "prioritize official" in PROMPT.lower() or "official sources first" in PROMPT.lower()
    return {
        "passed": has_tier,
        "details": f"Credibility guidance in prompt: {has_tier}",
    }


def test_max_uses_sufficient_for_expanded_sources():
    """WEB_SEARCH_MAX_USES must be >= 12 to cover expanded source list."""
    return {
        "passed": MAX_USES >= 12,
        "details": f"MAX_USES={MAX_USES} (need >= 12)",
    }


def test_graceful_failure_no_api_key():
    """No ANTHROPIC_API_KEY -> exit != 0 AND empty stdout (never print on failure)."""
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    proc = subprocess.run(
        [sys.executable, str(GATHERER)],
        capture_output=True, text=True, timeout=60, env=env,
    )
    empty_stdout = proc.stdout.strip() == ""
    return {
        "passed": proc.returncode != 0 and empty_stdout,
        "details": f"exit={proc.returncode}, stdout_len={len(proc.stdout.strip())}, stderr_head={proc.stderr.strip()[:80]!r}",
        "metrics": {"exit_code": proc.returncode, "stdout_empty": empty_stdout},
    }
