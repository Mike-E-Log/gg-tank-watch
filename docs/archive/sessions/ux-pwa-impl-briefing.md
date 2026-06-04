# UX + PWA Implementation — Touch targets, iOS fixes, manifest, service worker, ARIA (deep session)

You are running the **ux-pwa-impl** workstream. 1 other workstream runs concurrently ("data-sources-impl" on `scripts/gather_facts.py`). A third ("son-mai-impl") is queued after you complete — it will modify `dashboard.html` CSS and `DESIGN.md`.

## Read first, in this order

1. `CLAUDE.md` (project)
2. `~/.claude/CLAUDE.md` (global)
3. `docs/superpowers/plans/2026-05-25-ux-pwa-fixes.md` — **YOUR IMPLEMENTATION PLAN. Follow it task by task.**
4. `dashboard.html` — the file you will modify (2,255 lines, single-file dashboard)

## Primary goal

Fix critical mobile UX issues and add PWA capabilities:
1. Enlarge touch targets to 44px+ (tab bar, theme toggle, lang picker, buttons)
2. Fix iOS auto-zoom on input focus (font-size to 16px)
3. Remove meta http-equiv="refresh" (JS already handles refresh)
4. Add manifest.json for Add-to-Homescreen
5. Add sw.js service worker for offline access
6. Add ARIA tab pattern for screen readers

## File ownership

**You OWN (exclusive write access):**
```
dashboard.html
manifest.json (new file)
sw.js (new file)
```

**DO NOT TOUCH:**
```
scripts/gather_facts.py       → data-sources-impl
eval/test_gather_facts.py     → data-sources-impl
docs/SOURCE_CREDIBILITY.md    → data-sources-impl
DESIGN.md                     → son-mai-impl (queued after you)
.orchestra/orchestration.json → Orchestrator ONLY
```

## The work

Follow `docs/superpowers/plans/2026-05-25-ux-pwa-fixes.md` exactly, task by task:

### Task 1: Fix touch targets (CSS-only changes in dashboard.html)
- `.tab-btn`: padding `6px 0 4px` -> `10px 0 8px`, add `min-height: 48px`
- `#theme-toggle`, `#lang-toggle`: add `min-width: 44px; min-height: 44px`
- `.hero-check button`: padding to `10px 16px`, font-size to 14px, min-height 44px
- `.safety-form button`: padding to `12px 16px`, min-height 44px
- Run eval, commit

### Task 2: Fix iOS auto-zoom + remove meta refresh
- Delete `<meta http-equiv="refresh" content="600">`
- `.hero-check input` font-size: 13px -> 16px
- `.safety-form input` font-size: 15px -> 16px
- Run eval, commit

### Task 3: Add manifest.json
- Create `manifest.json` with app name, icons, standalone display
- Add `<link rel="manifest">` + theme-color meta + apple-mobile-web-app metas to dashboard.html head
- Commit

### Task 4: Add service worker
- Create `sw.js` with cache-first for static, network-first for status.json
- Add registration script before `</body>` in dashboard.html
- Run eval, commit

### Task 5: Add ARIA tab pattern
- Add `role="tablist"` to tab bar nav
- Add `role="tab"`, `aria-selected`, `aria-controls` to each tab button
- Add `role="tabpanel"`, `aria-labelledby` to each panel
- Update `switchTab()` JS to toggle `aria-selected`
- Run eval, commit

## Hard constraints (NON-NEGOTIABLE)

- Self-execute verifications — don't ask the user to paste commands
- DO NOT TOUCH files owned by other workstreams
- Run `python eval/run_all.py --skip integration` after each task and verify exit code 0
- Follow the plan's exact code — don't improvise different implementations
- Every commit must use explicit file paths in `git add` (never `git add -A` or `git add .`)
- The son-mai-impl stream will modify dashboard.html CSS AFTER you're done — your changes to CSS custom property VALUES will be overwritten by that stream (that's expected). Focus on structure/layout/accessibility, not colors.

## What "done" looks like

- Touch targets all >= 44px (tab bar, toggles, buttons)
- Input font-sizes at 16px (no iOS auto-zoom)
- Meta refresh removed
- `manifest.json` created and linked
- `sw.js` created and registered
- ARIA tab pattern implemented
- All eval tests pass (45+ tests, exit code 0)
- Task marked `completed` via TaskUpdate
- Summary sent to orchestrator lead via SendMessage
