# Workstream: Design Log + Cleanup

## Identity

You are a **documentation engineer** recording a design decision and performing mechanical cleanup for the GG Tank Watch project.

## Read first

- `DESIGN_LOG.md` — existing design decisions and their format
- `CLAUDE.md` — project framing and safety principles

## File ownership (EXCLUSIVE — only you write these)

- `DESIGN_LOG.md`
- Can DELETE: `loop/`, `plan/`, `prompts/`, `C--Users-redacted-OneDrive-Desktop-GG-tank-updates/`

## Do NOT touch

- `dashboard.html` (owned by hero-check stream)
- `README.md`, `docs/fellowship/*`
- `scripts/*`, `data/*`, `eval/*`

## The work

### Phase 1: Record the hero-check design decision in DESIGN_LOG.md

Read DESIGN_LOG.md to understand the existing format. Add a new entry (next sequential D-number) documenting:

**What:** Move the address-check widget from the Check tab into the always-visible hero section. Keep the Check tab as an expanded detail view.

**Alternatives considered:**
- A) Keep tabs as-is (rejected: hides the most personal feature behind navigation)
- B) Single scroll page removing all tabs (rejected: scroll fatigue on mobile, overwhelming for billboard-test audience)
- C) Hybrid with collapsible sections (rejected: collapsibles have their own discoverability problem)
- D) Keep tabs + hero check (CHOSEN: smallest change addressing the core safety concern)

**Rationale:**
- Anthropic safety alignment: the conduit mission requires answering the user's question ("am I safe?") with minimum friction. Tabs add friction.
- CMO lens (from DISTRIBUTION.md): "Would a displaced, frightened, limited-English-speaking elder trust this enough to act on it?" — they shouldn't need to discover a tab to get their answer.
- Portfolio value preserved: tabbed architecture remains, demonstrating technical sophistication.
- Office hours analysis confirmed all three lenses (safety, marketing, builder) converge on the same answer.

**Design principles applied:** Information hierarchy (answer first), conduit posture (routes to officials), trust-building (minimal cognitive load)

**Status:** Active

**Rubric:** Correctness 9/10, Maintainability 8/10, User-fit 9/10

### Phase 2: Delete gitignored directories

These dirs are in .gitignore and are leftover orchestration artifacts:

```
rm -rf loop plan prompts "C--Users-redacted-OneDrive-Desktop-GG-tank-updates"
```

Verify they don't show in `git status` as deletions (they're untracked/ignored).

### Phase 3: Verify

1. `git status` shows no unexpected changes (only DESIGN_LOG.md modified)
2. The deleted dirs are gone and don't affect git

## Done criteria

- DESIGN_LOG.md has the new entry matching the format of existing entries
- Gitignored dirs are deleted
- No git-tracked files affected by cleanup

## On completion

Mark your task as `completed` and SendMessage to the lead with: D-number of new entry, cleanup confirmation, any observations about existing design log patterns.
