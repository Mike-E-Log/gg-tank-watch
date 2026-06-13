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
PATTERNS=(
  'anna\.thyme'
  'AnnaThyme'
  'NancyThyme'
  'withoutaxioms'
  'founder@'
  'Kaya Admin'
  'Ngoc Duong'
  'Users[\\/-]witho'
  'Users[\\/-]annat'
  'Anthropic Fellows'
  'portfolio piece'
  'Fellows application'
  'gg-tank-bot'
)

# Exclude self-references (this script + the workflow legitimately list the patterns).
EXCLUDES=(':(exclude)scripts/check_repo_hygiene.sh' ':(exclude).github/workflows/hygiene.yml')

fail=0
for p in "${PATTERNS[@]}"; do
  hits=$(git grep -I -n -E "$p" -- . "${EXCLUDES[@]}" 2>/dev/null)
  if [ -n "$hits" ]; then
    echo "::error::repo-hygiene BLOCKED — forbidden pattern '$p':"
    echo "$hits"
    fail=1
  fi
done

if [ "$fail" -eq 0 ]; then
  echo "repo-hygiene: clean (no PII or removed framing found)"
fi
exit "$fail"
