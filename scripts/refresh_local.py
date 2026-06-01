"""ARCHIVED — retired for the fully-historical pivot (do not run).

status.json is now a FROZEN May 26, 2026 archive snapshot. This refresher must NOT run
— it would re-introduce live timestamps and post-26th data. main() exits with an error;
the body below is kept for reference / possible emergency re-activation only.

(Historical) This was the subscription-billed data-sync path. It ran on a contributor's machine
(left on) and bills the Claude **subscription** instead of metered API credits:
it gathers current incident facts via `claude -p` with the OAuth subscription
(ANTHROPIC_API_KEY unset) and the WebSearch tool, runs the existing writer, and
commits the refreshed status.json so Vercel auto-deploys.

Why this exists: the cloud cron (.github/workflows/update-status.yml) is the
"no machine required" path but a headless GitHub Actions runner can only use a
metered ANTHROPIC_API_KEY (no OAuth). For now we prefer subscription credits, so
we run locally. To switch back to the metered cloud cron later, re-enable the
schedule in that workflow (the API-key secret is already set). See docs/DATA_SYNC.md.

Reuses the prompt + JSON extraction from gather_facts.py so the two paths stay
in lockstep — only the model call differs (claude -p subscription vs SDK + key).

Usage:
    python scripts/refresh_local.py            # gather -> write -> commit -> push
    python scripts/refresh_local.py --dry-run  # gather -> write status.json only

Env:
    CLAUDE_MODEL   optional, default "sonnet" (cheaper on the shared subscription
                   quota than Opus; the gather is a simple structured task)
    VERCEL_DEPLOY_HOOK_URL  optional; if set, POSTed after each push to force a
                   Vercel rebuild (defense-in-depth vs a silent auto-deploy stall)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gather_facts import PROMPT, extract_json  # noqa: E402  (reuse the one prompt)

MODEL = os.environ.get("CLAUDE_MODEL", "sonnet")
REPO = HERE.parent
HEALTHCHECK_URL = os.environ.get("HEALTHCHECK_URL", "")
VERCEL_DEPLOY_HOOK_URL = os.environ.get("VERCEL_DEPLOY_HOOK_URL", "")


def ping_healthcheck(status: str = "") -> None:
    """Ping healthchecks.io on successful refresh. Silent on failure."""
    if not HEALTHCHECK_URL:
        return
    import urllib.request
    url = HEALTHCHECK_URL if not status else f"{HEALTHCHECK_URL}/{status}"
    try:
        urllib.request.urlopen(url, timeout=10)
    except Exception:
        pass


def trigger_deploy() -> None:
    """POST the Vercel deploy hook after a push so the live site rebuilds even if
    git-integration auto-deploy stalls (the 2026-05-29 stale-deploy incident).
    No-op if VERCEL_DEPLOY_HOOK_URL is unset. Silent on failure."""
    if not VERCEL_DEPLOY_HOOK_URL:
        return
    import urllib.request
    try:
        urllib.request.urlopen(
            urllib.request.Request(VERCEL_DEPLOY_HOOK_URL, method="POST"), timeout=15
        )
    except Exception:
        pass


def gather_via_subscription() -> dict:
    """Run `claude -p` on the subscription (key unset) and return the facts dict."""
    claude = shutil.which("claude")
    if not claude:
        sys.stderr.write("`claude` CLI not found on PATH\n")
        raise SystemExit(2)

    env = dict(os.environ)
    env.pop("ANTHROPIC_API_KEY", None)  # force OAuth subscription billing

    proc = subprocess.run(
        [claude, "-p", PROMPT, "--model", MODEL,
         "--allowedTools", "WebSearch", "--permission-mode", "acceptEdits",
         "--output-format", "json"],
        capture_output=True, text=True, encoding="utf-8", env=env, cwd=str(REPO),
    )
    if proc.returncode != 0:
        sys.stderr.write(f"claude -p failed (exit {proc.returncode}):\n{proc.stderr[:1000]}\n")
        raise SystemExit(1)

    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"claude -p output was not JSON: {e}\n{proc.stdout[:1000]}\n")
        raise SystemExit(1)

    result_text = envelope.get("result", "")
    try:
        return extract_json(result_text)
    except (ValueError, json.JSONDecodeError) as e:
        sys.stderr.write(f"could not parse facts from claude result: {e}\n{result_text[:1500]}\n")
        raise SystemExit(1)


def write_status(facts: dict) -> None:
    """Feed facts to the existing writer over stdin (avoids PowerShell pipe corruption)."""
    subprocess.run(
        [sys.executable, str(HERE / "update_status.py")],
        input=json.dumps(facts, ensure_ascii=False), text=True, encoding="utf-8",
        check=True, cwd=str(REPO),
    )


def commit_and_push() -> None:
    """Commit status.json (if it changed) and push — the data audit trail."""
    def git(*args):
        return subprocess.run(["git", *args], cwd=str(REPO), capture_output=True, text=True)

    # status.json is gitignored for local dev; -f because the bot tracks it.
    git("add", "-f", "status.json")
    if git("diff", "--cached", "--quiet").returncode == 0:
        print("status.json unchanged; nothing to commit")
        return
    git("config", "user.name", "gg-tank-bot")
    git("config", "user.email", "github-actions[bot]@users.noreply.github.com")
    git("commit", "-m", "chore(data): refresh status.json [skip ci]")
    branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    git("pull", "--rebase", "--autostash", "origin", branch)
    push = git("push")
    if push.returncode != 0:
        sys.stderr.write(f"git push failed:\n{push.stderr[:1000]}\n")
        raise SystemExit(1)
    print("status.json refreshed and pushed")


def main() -> int:
    # ARCHIVED: status.json is a frozen historical snapshot (May 26, 2026). Refuse to run
    # so a stray invocation can't un-freeze it with live data (fully-historical archive pivot).
    print("ARCHIVED: refresh_local.py is retired — status.json is a frozen archive. Aborting.", file=sys.stderr)
    return 1
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="gather + write status.json, skip git")
    args = ap.parse_args()

    facts = gather_via_subscription()
    write_status(facts)
    if args.dry_run:
        print("dry-run: status.json written, git skipped")
        ping_healthcheck()
        return 0
    commit_and_push()
    trigger_deploy()
    ping_healthcheck()
    return 0


if __name__ == "__main__":
    sys.exit(main())
