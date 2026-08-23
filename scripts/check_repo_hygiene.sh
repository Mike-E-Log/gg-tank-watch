#!/usr/bin/env bash
# Repo-hygiene guard — blocks home-directory paths and the removed
# self-promotional framing from re-entering this public repo. Used by CI
# (.github/workflows/hygiene.yml); can also be run locally before a push.
#
# 2026-08-20: the base64-encoded PII name denylist was removed. A public file
# cannot hold personal names in any safe form: base64 decodes, and even salted
# digests of short names are confirmable by guessing. The structural check
# below carries no names; re-entry of a specific name is caught by human
# review, not CI.
#
# Exit 0 = clean; exit 1 = a forbidden pattern was found, or the scan itself
# failed to run (a scan error is never reported as clean).
set -u

# Removed self-promotional framing - generic phrases that identify no one, so
# kept in cleartext.
FRAMING=(
  'founder@'
  'Anthropic Fellows'
  'portfolio piece'
  'Fellows application'
  'gg-tank-bot'
)

# Structural PII shape: an OS home path with a real username. The placeholder
# username "redacted" is this repo's documented scrub marker and is carved out
# only as a full token (Users/redactedXYZ still blocks).
# The separator class repeats and matching is case-insensitive: JSON/log-escaped
# paths store doubled backslashes (Users\\name), and a single-separator,
# case-sensitive match let exactly that form through (caught 2026-08-23 by
# post-merge review of PR #83).
GENERIC_PATH='Users[\\/-]+[A-Za-z0-9._-]+'

# Exclude self-references (this script + the workflow legitimately list the patterns).
EXCLUDES=(':(exclude)scripts/check_repo_hygiene.sh' ':(exclude).github/workflows/hygiene.yml')

fail=0

scan_error() {
  echo "::error::repo-hygiene scan FAILED to run ($1) - treating this as a failure, not a pass."
  exit 1
}

for p in "${FRAMING[@]}"; do
  hits=$(git grep -I -n -E -e "$p" -- . "${EXCLUDES[@]}")
  rc=$?
  if [ "$rc" -eq 0 ]; then
    echo "::error::repo-hygiene BLOCKED - forbidden pattern detected:"
    echo "$hits"
    fail=1
  elif [ "$rc" -ne 1 ]; then
    scan_error "git grep rc=$rc on a framing pattern"
  fi
done

rows=$(git grep -I -n -o -E -i -e "$GENERIC_PATH" -- . "${EXCLUDES[@]}")
rc=$?
if [ "$rc" -eq 0 ]; then
  hits=$(printf '%s\n' "$rows" | grep -Evi ':Users[\\/-]+redacted$')
  grc=$?
  if [ "$grc" -eq 0 ]; then
    echo "::error::repo-hygiene BLOCKED - home-directory path with a real username:"
    echo "$hits"
    fail=1
  elif [ "$grc" -ne 1 ]; then
    scan_error "carve-out filter rc=$grc"
  fi
elif [ "$rc" -ne 1 ]; then
  scan_error "git grep rc=$rc on the structural path pattern"
fi

if [ "$fail" -eq 0 ]; then
  echo "repo-hygiene: clean (no forbidden patterns found)"
fi
exit "$fail"
