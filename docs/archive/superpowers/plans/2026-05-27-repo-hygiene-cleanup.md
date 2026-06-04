# Repo Hygiene Cleanup — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean up accumulated untracked files, stale stashes, dead images, and outdated memory to bring the repo to a clean `git status`.

**Architecture:** Six independent cleanup tasks, each producing one commit. No code logic changes — all mechanical deletions, gitignore additions, and git housekeeping.

**Tech Stack:** Git, file system operations, memory system

---

### Task 1: Delete unused static map images

The old `zone-map.png` and `zone-map-hires.jpg` are left over from before the MapLibre interactive map. Confirmed zero references in `dashboard.html` or any other source file. Frees ~2.8MB.

**Files:**
- Delete: `images/zone-map.png`
- Delete: `images/zone-map-hires.jpg`

- [ ] **Step 1: Delete the files**

```bash
rm images/zone-map.png images/zone-map-hires.jpg
```

- [ ] **Step 2: Check if images/ dir is now empty and remove if so**

```bash
ls images/
# Expected: empty directory
rmdir images/
```

- [ ] **Step 3: Commit the deletion**

```bash
git add images/zone-map.png images/zone-map-hires.jpg
git commit -m "chore: remove unused static map images

Superseded by MapLibre interactive map (PR #35). Zero references remain."
```

If `rmdir` succeeded (dir was empty), stage the directory removal too. If other files exist, skip the rmdir.

---

### Task 2: Drop stale git stashes

Three stash entries from prior sessions. All are from before PRs #32–#37 shipped, so the work they protected is either merged or obsolete.

- `stash@{0}`: WIP on main: 7808235 (fix: eliminate vertical scroll on map tab — PR #32 merged)
- `stash@{1}`: WIP on main: 467cf81 (feat(ui): implement design review fixes — merged)
- `stash@{2}`: On main: WIP dashboard before pull — oldest, pre-dates current design

- [ ] **Step 1: Verify stash list**

```bash
git stash list
```

Expected: 3 entries matching the descriptions above.

- [ ] **Step 2: Drop all three stashes (newest first)**

```bash
git stash drop stash@{0}
git stash drop stash@{0}
git stash drop stash@{0}
```

Drop index 0 three times because each drop shifts the remaining entries up.

- [ ] **Step 3: Verify clean stash**

```bash
git stash list
```

Expected: no output (empty stash list).

No commit needed — stashes are local-only state.

---

### Task 3: Gitignore scratch/external files at repo root

Four items at the repo root are scratch artifacts or external imports that should never be committed:

| File | What it is |
|------|-----------|
| `render_safety_briefing.py` | One-off script |
| `safety-briefing-philosophy.md` | Scratch doc |
| `safety-briefing.png` | Generated image |
| `Mobile _ 390.html` | Exported browser snapshot (1.7MB) |
| `C--Users-redacted-OneDrive-Desktop-GG-tank-updates/` | External folder from another machine (5.1MB) |

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Add entries to .gitignore**

Append to the end of `.gitignore`:

```
# One-off scratch files (not part of the project)
render_safety_briefing.py
safety-briefing-philosophy.md
safety-briefing.png
Mobile _ 390.html
C--Users-redacted-OneDrive-Desktop-GG-tank-updates/
```

- [ ] **Step 2: Verify the files no longer appear in git status**

```bash
git status -s
```

Expected: the five items above should NOT appear. Remaining untracked items should be only `docs/sessions/`, `docs/superpowers/plans/`, `docs/superpowers/specs/`.

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: gitignore scratch files and external imports"
```

---

### Task 4: Commit untracked session briefings

15 untracked session briefing files in `docs/sessions/`. These are `/split-and-orchestrate` artifacts that document work streams. 14 briefings are already tracked — these 15 are from later sessions and should join them.

**Files:**
- Stage: `docs/sessions/dashboard-eng-briefing.md`
- Stage: `docs/sessions/data-sources-briefing.md`
- Stage: `docs/sessions/data-sources-impl-briefing.md`
- Stage: `docs/sessions/designlog-cleanup-briefing.md`
- Stage: `docs/sessions/fellowship-polish-briefing.md`
- Stage: `docs/sessions/fellowship-prep-briefing.md`
- Stage: `docs/sessions/gap-sweep-briefing.md`
- Stage: `docs/sessions/hero-check-briefing.md`
- Stage: `docs/sessions/i18n-dashboard-briefing.md`
- Stage: `docs/sessions/mobile-ux-audit-briefing.md`
- Stage: `docs/sessions/ops-cleanup-briefing.md`
- Stage: `docs/sessions/portfolio-polish-briefing.md`
- Stage: `docs/sessions/son-mai-impl-briefing.md`
- Stage: `docs/sessions/ux-pwa-impl-briefing.md`
- Stage: `docs/sessions/viet-design-briefing.md`

- [ ] **Step 1: Stage all 15 session briefings**

```bash
git add docs/sessions/dashboard-eng-briefing.md docs/sessions/data-sources-briefing.md docs/sessions/data-sources-impl-briefing.md docs/sessions/designlog-cleanup-briefing.md docs/sessions/fellowship-polish-briefing.md docs/sessions/fellowship-prep-briefing.md docs/sessions/gap-sweep-briefing.md docs/sessions/hero-check-briefing.md docs/sessions/i18n-dashboard-briefing.md docs/sessions/mobile-ux-audit-briefing.md docs/sessions/ops-cleanup-briefing.md docs/sessions/portfolio-polish-briefing.md docs/sessions/son-mai-impl-briefing.md docs/sessions/ux-pwa-impl-briefing.md docs/sessions/viet-design-briefing.md
```

- [ ] **Step 2: Verify only the 15 briefings are staged**

```bash
git diff --cached --name-only
```

Expected: exactly the 15 files listed above.

- [ ] **Step 3: Commit**

```bash
git add docs/sessions/dashboard-eng-briefing.md docs/sessions/data-sources-briefing.md docs/sessions/data-sources-impl-briefing.md docs/sessions/designlog-cleanup-briefing.md docs/sessions/fellowship-polish-briefing.md docs/sessions/fellowship-prep-briefing.md docs/sessions/gap-sweep-briefing.md docs/sessions/hero-check-briefing.md docs/sessions/i18n-dashboard-briefing.md docs/sessions/mobile-ux-audit-briefing.md docs/sessions/ops-cleanup-briefing.md docs/sessions/portfolio-polish-briefing.md docs/sessions/son-mai-impl-briefing.md docs/sessions/ux-pwa-impl-briefing.md docs/sessions/viet-design-briefing.md
git commit -m "docs: add 15 session briefings from orchestration runs"
```

---

### Task 5: Commit untracked plan and spec files

7 untracked plan files in `docs/superpowers/plans/` and 1 spec file in `docs/superpowers/specs/`. Two plans are already tracked — these are from later sessions.

**Files:**
- Stage: `docs/superpowers/plans/2026-05-25-data-source-credibility.md`
- Stage: `docs/superpowers/plans/2026-05-25-son-mai-theme.md`
- Stage: `docs/superpowers/plans/2026-05-25-ux-pwa-fixes.md`
- Stage: `docs/superpowers/plans/2026-05-26-conduit-cleanup.md`
- Stage: `docs/superpowers/plans/2026-05-26-security-a11y-ops-blockers.md`
- Stage: `docs/superpowers/plans/2026-05-26-split-panel-redesign.md`
- Stage: `docs/superpowers/plans/2026-05-27-maplibre-openfreemap.md`
- Stage: `docs/superpowers/specs/2026-05-27-zoomable-svg-map-design.md`

- [ ] **Step 1: Stage all plan and spec files**

```bash
git add docs/superpowers/plans/2026-05-25-data-source-credibility.md docs/superpowers/plans/2026-05-25-son-mai-theme.md docs/superpowers/plans/2026-05-25-ux-pwa-fixes.md docs/superpowers/plans/2026-05-26-conduit-cleanup.md docs/superpowers/plans/2026-05-26-security-a11y-ops-blockers.md docs/superpowers/plans/2026-05-26-split-panel-redesign.md docs/superpowers/plans/2026-05-27-maplibre-openfreemap.md docs/superpowers/specs/2026-05-27-zoomable-svg-map-design.md
```

- [ ] **Step 2: Verify only the 8 files are staged**

```bash
git diff --cached --name-only
```

Expected: exactly the 8 files listed above.

- [ ] **Step 3: Commit**

```bash
git commit -m "docs: add 7 plan files and 1 spec from recent sessions"
```

---

### Task 6: Remove stale memory entry

`geocoder-nominatim-limits.md` is self-labeled STALE — the Nominatim geocoder was removed 2026-05-26. The memory is no longer actionable.

**Files:**
- Delete: `~/.claude/projects/C--Users-redacted-Desktop-Mike-Ilog-Portfolio-GitHub-Projects-gg-tank-dashboard/memory/geocoder-nominatim-limits.md`
- Modify: `~/.claude/projects/C--Users-redacted-Desktop-Mike-Ilog-Portfolio-GitHub-Projects-gg-tank-dashboard/memory/MEMORY.md`

- [ ] **Step 1: Delete the stale memory file**

Delete `geocoder-nominatim-limits.md` from the memory directory.

- [ ] **Step 2: Remove the index entry from MEMORY.md**

Remove the line:
```
- [Geocoder / Nominatim limits](geocoder-nominatim-limits.md) — STALE: Nominatim removed 2026-05-26. Address checker no longer exists.
```

- [ ] **Step 3: Verify MEMORY.md is clean**

Read `MEMORY.md` and confirm 7 entries remain, no dangling references.

No git commit needed — memory files are outside the repo.

---

## Post-cleanup verification

After all 6 tasks:

```bash
git status -s
```

Expected output should show ONLY:
- ` M eval/scores.jsonl` (intentionally uncommitted eval log)
- The plan file for this cleanup itself (this file — commit or gitignore per preference)

```bash
git stash list
```

Expected: empty.

```bash
git log --oneline -6
```

Expected: 4 new commits (Tasks 1, 3, 4, 5) on top of existing history.
