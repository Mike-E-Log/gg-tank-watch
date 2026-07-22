# Deployment Readiness: GG Tank Watch

**Single source of truth for launch state.** Supersedes the local (gitignored)
`plan/EXECUTION_PLAN.md` and `loop/LOOP_STATE.md` build-loop scratch, frozen at the
2026-05-25 conduit sprint, mutually contradictory, and now removed in favor of this doc
plus `loop/DONE.md`.

**Status (settled 2026-06-09): FROZEN ARCHIVE, no launch.** Code is design-complete and
the frozen archive is live at [ggtankwatch.org](https://ggtankwatch.org) (direct-link
only). The Lane B launch gates below were never crossed and are **retired, not pending**:
`noindex` is kept permanently by choice, and attorney review was judged unnecessary once
the incident resolved and the site froze. Kept as the record of what a wide launch would
have required.

## Shipped (code complete)

- Conduit tasks T1–T3, T5–T7 (official-zone router, provenance, AI disclosure, official-
  sources panel, Code of Conduct, AirNow AQI). T4 (Vietnamese) intentionally held; see
  Language gate.
- v0.15 resident shareability (#49), v0.16 Vietnamese hold (#51), v0.17 design-complete
  (Map + News + Info + Timeline + tablet) (#54).
- Eval harness **48/48** (`python eval/run_all.py --skip integration`, exit 0).
- Live at https://gg-tank-watch.vercel.app; auto-deploy active (PR #52 moved hosting to a
  personal account; the prior org/Hobby stale-data block is resolved). Honest staleness
  banner intact.

## Lane B: launch gate (RETIRED 2026-06-09, never crossed; kept for the record)

- [ ] **Attorney review** (the `noindex` gate, "B3" in CLAUDE.md): incl. naming /
  impersonation posture (any `.org` domain, non-government disclosure). Source research:
  `docs/LEGAL.md`. Removing `noindex` would have required this to clear. It stays `noindex` permanently by choice, so the gate is moot.
- [ ] **Entity formation**: appropriate legal entity for liability shielding.
- [ ] **Insurance**: liability coverage.

## Language: English-only (safety design choice, decided 2026-05-30)

The app ships **no Vietnamese (or other non-English) content, language toggle, or redirect
to non-English resources.** Rationale: never surface translations, even links to others'
translations, without reliable human translators; an unofficial mistranslation of an
evacuation instruction can get someone killed. The conduit routes everyone to officials,
who provide their own multilingual access. This is the most conservative application of G1
(no machine-translated safety copy) and removes the VI-verification long-pole entirely.

- The VI toggle, sign-post, strings, redirects, and `vi.ready` flag are **removed** (not
  gated). Tracked in the dashboard workflow.
- README / CLAUDE copy that still says "bilingual / Tiếng Việt" must be
  updated to reflect the English-only + G1 posture (tracked in the workflow).

## Deferred (Phase 2, not blocking)

- Custom domain (`gardengrovetankwatch.org` / `ggtankwatch.org`) + final URL repoint.

## Post-freeze maintenance (added 2026-07-21, Fable 5 audit F17/F20)

Two operational dependencies outlive the freeze; both are owned by Mike Ilog.

- **Domain renewal (`ggtankwatch.org`).** A registration lapse would let a squatter
  serve arbitrary content on a formerly trusted emergency domain. Keep registrar
  auto-renew and the transfer lock on; check the expiry when this doc is touched.
- **Correction channel (`ggtankwatch@gmail.com`).** A personal inbox, answered
  best-effort (as the site's Terms page says). If it is ever retired, the fallback
  correction channel is this repository's issue tracker; update the Terms and
  Accessibility pages in the same change.
