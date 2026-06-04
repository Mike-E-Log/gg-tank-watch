# Session Reconciliation Handoff — 2026-05-29

**Purpose:** Single source of truth uniting four Claude Code sessions that collided over one shared git working tree. Produced by a 9-agent investigation workflow (`reconcile-conflicting-sessions`, run `wf_de059d6b-78f`) and confirmed by three independent adversarial verifiers. Read this to drive remediation from a **single sole-driver session** — it carries the full context none of the individual sessions hold on their own.

> **Iron rule for using this doc:** Exactly ONE Claude Code session may touch this checkout at a time. The collision below was caused by two sessions driving one `.git`. Close all other sessions before running any mutating step.

---

## TL;DR

Two live sessions drove one checkout simultaneously. The branches are **file-disjoint** (no merge conflict), but a commit and data-refresh churn landed on the wrong branch. Net mess to clean up:

- The **v0.15 shareability CHANGELOG entry (`5bfced6`) is stranded on the *legal* branch** (and already on origin), so PR #49 ships the feature with no changelog.
- The entire **LEGAL.md rewrite (`8b36770`) is unpushed and local-only** — one bad reset from loss.
- A stray **`eval/scores.jsonl`** stash + uncommitted append float free (append-only refresh data, disposable).
- **No PR exists for the legal branch** (PR #49 covers only shareability).
- **Separate, possibly more urgent:** the live site serves ~15h-stale emergency data (Vercel private-org Hobby plan blocks deploy).

---

## The four sessions

All fork from `bce13a2` (merged PR #48, README conduit-truth pass).

| Session | Role | What it did |
|---|---|---|
| `7bde9276` | ancestor / originator | README conduit-truth pass → PR #48; **wrote but didn't execute** the LEGAL.md reconciliation plan. Branch flipped under it during `/context-save` (first sign the tree was shared). |
| `470c12f0` | older live target | Kept the "Watch" name; **built** the shareability feature → PR #49 (pushed, green). Its `add && commit && push` of the v0.15 CHANGELOG landed as `5bfced6` on the legal branch (branch switched mid-command). Surfaced the **Vercel stale-data** finding. Self-froze. |
| `c55682e5` | newer live target | Executed the legal plan: `f1fc2c9` (vendor memo) + `8b36770` (LEGAL.md rewrite). Found the stray `5bfced6` between its commits, diagnosed the collision, **held** before push/PR. Holds the only copy of unpushed `8b36770`. |
| `279c948b` | orchestrator | Read-only forensics → launched the investigation workflow → wrote this doc. Authored nothing on any product branch. |

## Conflict nature

**Shared-working-tree concurrency collision, not a git merge conflict.** One `.git`, one HEAD, one index, two drivers. Symptoms: (A) misplaced commit `5bfced6`; (B) `eval/scores.jsonl` churn (`refresh_local.py` / eval runner appends to the current branch); (C) non-atomic HEAD/ref races (nothing corrupted — reflog intact — but it's the root exposure).

---

## Current verified git state (as of 2026-05-29, re-verified pre-handoff)

```
current branch : docs/legal-md-conduit-reconcile
working tree   : M eval/scores.jsonl   (uncommitted 17:52 refresh append — disposable)

docs/legal-md-conduit-reconcile  (local tip 8b36770, AHEAD of origin by 1)
  bce13a2  (base, PR #48)
  f1fc2c9  docs(legal): vendor 2026-05-27 legal research memo + plan
  5bfced6  docs(changelog): add v0.15 resident shareability entry   <-- STRAY (belongs on shareability); already on origin
  8b36770  docs(legal): reconcile LEGAL.md with conduit product + 2026-05-27 memo  <-- UNPUSHED, local-only

  origin tip = 5bfced6   (f1fc2c9 + 5bfced6 are on origin; 8b36770 is NOT)
  open PR    = NONE

feat/resident-shareability  (tip ae27d30 — fully in sync with origin)
  fcf1052 / 57dd17a / a938da5 / ae27d30   (og-image, OG+Twitter meta, Share button, plan)
  CHANGELOG history stops at v0.14 (no v0.15 entry here)
  open PR = #49 "v0.15 feat(share): resident shareability — social preview card + one-tap Share button" (base main, OPEN, green)

stash@{0} : WIP on feat/resident-shareability: ae27d30   (holds eval/scores.jsonl, 17:39 run — disposable)
```

Branches are file-disjoint: legal touches `CHANGELOG.md` + `docs/LEGAL.md` + `docs/legal-research/*`; shareability touches `dashboard.html` + `og-image.png` + `scripts/og-image.html` + plan. `5bfced6` (CHANGELOG only) and `8b36770` (LEGAL.md only) do not overlap.

---

## Remediation sequence (verified — corrections from all 3 verifiers baked in)

Run **serially, inline, from the single sole-driver session.** Do **not** run as a parallel workflow (parallel agents mutating one checkout = the same collision). Do **not** run `scripts/refresh_local.py` mid-sequence (it does `git pull --rebase --autostash && git push` on the current branch — would race step 5).

```bash
# 0. SERIALIZE — confirm only this session touches the repo.

# 1. PROTECT the irreplaceable rewrite FIRST (clean fast-forward):
git push origin docs/legal-md-conduit-reconcile
git log --oneline origin/docs/legal-md-conduit-reconcile..docs/legal-md-conduit-reconcile   # expect EMPTY

# 2. Clear the dirty tree so cherry-pick/rebase don't abort:
git stash push -- eval/scores.jsonl
#    NOTE: this pushes a NEW stash to stash@{0} and demotes the existing WIP-on-shareability
#    stash to stash@{1}. Track stashes by their MESSAGE, not by index (see step 7).

# 3. RELOCATE the stray changelog to its feature (cherry-pick applies clean — blobs verified identical):
git checkout feat/resident-shareability
git cherry-pick 5bfced6
git push origin feat/resident-shareability      # fast-forward; PR #49 now carries its own v0.15 entry

# 4. DROP the stray from the legal branch:
git checkout docs/legal-md-conduit-reconcile
git rebase --onto f1fc2c9 5bfced6 docs/legal-md-conduit-reconcile
#    VERIFY (corrected): log must be exactly f1fc2c9 -> <new 8b36770>, with NO 5bfced6.
#    The tree delta vs the OLD 8b36770 is the 6-line CHANGELOG removal — this is EXPECTED,
#    it is NOT an empty diff. (LEGAL.md content is untouched: rebase is file-disjoint.)

# 5. Update the remote legal branch (origin still carries 5bfced6 — force needed):
git push --force-with-lease origin docs/legal-md-conduit-reconcile
git log --oneline origin/docs/legal-md-conduit-reconcile   # confirm 5bfced6 GONE and 8b36770 PRESENT

# 6. OPEN the legal PR (none exists):
gh pr create --base main --head docs/legal-md-conduit-reconcile \
  --title 'docs(legal): reconcile LEGAL.md with conduit product + 2026-05-27 memo'
#    Body: problem / approach / test plan (eval 45/45) / risk / rollback.

# 7. DISCARD redundant eval churn — drop BY MESSAGE, not index:
git stash list      # identify both: the "WIP on feat/resident-shareability" one AND the step-2 one
git stash drop <ref>   # drop both append-only copies
#    OPTIONAL: capture the 17:39 / 17:52 lines first — they are NOT in the committed base
#    (which stops at the 16:09 run). Project treats scores.jsonl as regenerable, so loss is acceptable.

# 8. LAND via PRs (squash; never push main directly):
#    merge PR #49 (shareability, now with changelog) FIRST, then the legal PR. Verify eval 45/45 each.

# 9. GUARDRAIL going forward — worktrees, one per branch:
git worktree add ../ggtw-legal docs/legal-md-conduit-reconcile
git worktree add ../ggtw-share feat/resident-shareability
```

### Why this is safe
- `8b36770` is pushed (step 1) **before** any history rewrite, so the irreplaceable LEGAL.md rewrite is on origin first.
- The rebase is file-disjoint (`8b36770` = LEGAL.md only; excised `5bfced6` = CHANGELOG only) → conflict-free, identical LEGAL.md tree.
- The cherry-pick applies clean (CHANGELOG blob is byte-identical between `f1fc2c9` and the shareability tip — both at v0.14).
- `--force-with-lease` aborts if origin moved unexpectedly (race guard).
- Single driver eliminates the concurrency that caused the mess.

---

## Guardrails to prevent recurrence

1. **One checkout, one session.** Never run two Claude Code sessions against the same working tree.
2. **Use `git worktree` for legitimate parallel work** — each session gets its own HEAD/index/tree off one shared `.git`; structurally impossible to flip another session's branch.
3. **Re-verify `git branch --show-current` immediately before any commit/push** (CLAUDE.md §9). The collision came from a combined `add && commit && push` assuming a branch that changed mid-command.
4. **Gate `scripts/refresh_local.py` to `main` only.** It does `git pull --rebase --autostash && git push` on the current branch — pin behind a `git branch --show-current == main` assert.
5. **Treat `eval/scores.jsonl` as generated, append-only** — either `.gitignore` it and regenerate, or commit only on `main` via the refresh script. It caused dirty-tree dances in three sessions.

---

## Separate urgent finding (non-git)

`470c12f0`'s `/land-and-deploy` found the **live site is serving ~15h-stale emergency data**: Vercel silently refuses to deploy a private-org repo on the Hobby plan. For a safety-critical conduit whose primary goal is helping evacuated residents, **stale data outranks branch hygiene.** Fix: one-time manual redeploy or Vercel Pro upgrade (repo stays private per prior decision).

---

## Provenance

- Source transcripts: `~/.claude/projects/C--Users-redacted-…-gg-tank-dashboard/{c55682e5…, 470c12f0…, 7bde9276…, 279c948b…}.jsonl`
- Full workflow output (profiles + synthesis + 3 verdicts): `…/tasks/wcz553rq8.output` (run `wf_de059d6b-78f`)
- All three verifiers returned `recommendationHolds: true`; their corrections (step 4 diff, step 7 stash indices, `refresh_local.py` rationale) are already incorporated above.
