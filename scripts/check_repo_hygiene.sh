#!/usr/bin/env bash
# Repo-hygiene guard — blocks personal PII and the removed self-promotional
# framing from re-entering this public repo. The full one-time curation
# (2026-06-05) scrubbed these; this keeps them out so no future change ever
# needs another sweep. Used by CI (.github/workflows/hygiene.yml) and an
# optional local pre-commit hook (see CONTRIBUTING.md).
#
# Exit 0 = clean, exit 1 = a forbidden pattern was found.
set -u

# Forbidden patterns (real PII + removed framing). Specific, to avoid false
# positives on legitimate content (e.g. "Anthropic" alone is allowed as a
# design-standard citation; only "Anthropic Fellows" is blocked).
#
# The PII half (collaborator names, handles, home-path usernames) is base64-
# encoded so this PUBLIC file does not itself spell out the very names it
# scrubs - the denylist must not become the leak it prevents. Decoded only in
# memory at runtime, never written to disk. To inspect or add a PII pattern:
#   printf '%s' 'the-pattern' | base64    # paste the output into ENCODED_PII
ENCODED_PII=(
  'YW5uYVwudGh5bWU='
  'QW5uYVRoeW1l'
  'TmFuY3lUaHltZQ=='
  'd2l0aG91dGF4aW9tcw=='
  'S2F5YSBBZG1pbg=='
  'TmdvYyBEdW9uZw=='
  'VXNlcnNbXFwvLV13aXRobw=='
  'VXNlcnNbXFwvLV1hbm5hdA=='
)

# Removed self-promotional framing - generic phrases that identify no one, so
# kept in cleartext.
FRAMING=(
  'founder@'
  'Anthropic Fellows'
  'portfolio piece'
  'Fellows application'
  'gg-tank-bot'
)

PATTERNS=("${FRAMING[@]}")
for _enc in "${ENCODED_PII[@]}"; do
  PATTERNS+=("$(printf '%s' "$_enc" | base64 -d)")
done

# Exclude self-references (this script + the workflow legitimately list the patterns).
EXCLUDES=(':(exclude)scripts/check_repo_hygiene.sh' ':(exclude).github/workflows/hygiene.yml')

fail=0
for p in "${PATTERNS[@]}"; do
  hits=$(git grep -I -n -E "$p" -- . "${EXCLUDES[@]}" 2>/dev/null)
  if [ -n "$hits" ]; then
    echo "::error::repo-hygiene BLOCKED — forbidden pattern detected:"
    echo "$hits"
    fail=1
  fi
done

if [ "$fail" -eq 0 ]; then
  echo "repo-hygiene: clean (no PII or removed framing found)"
fi
exit "$fail"
