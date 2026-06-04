# Sơn Mài Authority Theme Implementation — CSS palette + Be Vietnam Pro + cultural motifs (queued session)

You are running the **son-mai-impl** workstream. This is a QUEUED stream — you run AFTER "ux-pwa-impl" has completed its changes to `dashboard.html`. Two other streams ran before you.

## Read first, in this order

1. `CLAUDE.md` (project)
2. `~/.claude/CLAUDE.md` (global)
3. `docs/superpowers/plans/2026-05-25-son-mai-theme.md` — **YOUR IMPLEMENTATION PLAN. Follow it task by task.**
4. `docs/sessions/viet-design-report.md` — the full design research that informed this theme
5. `dashboard.html` — the file you will modify (READ it fresh — ux-pwa-impl has modified it)
6. `DESIGN.md` — the design system doc you will update

## Primary goal

Apply the "Sơn Mài Authority" Vietnamese cultural design system:
1. Swap CSS custom property values for warm lacquerware palette (both light and dark)
2. Add Be Vietnam Pro font from Google Fonts for Vietnamese body text
3. Add cultural visual elements (lotus divider, wave texture, celadon card borders, gold accents)
4. Update DESIGN.md to document the new theme

## File ownership

**You OWN (exclusive write access):**
```
dashboard.html (CSS custom properties + font link + cultural element CSS + minor JS for severity class)
DESIGN.md
```

**DO NOT TOUCH:**
```
scripts/gather_facts.py       → data-sources-impl (already completed)
eval/test_gather_facts.py     → data-sources-impl (already completed)
docs/SOURCE_CREDIBILITY.md    → data-sources-impl (already completed)
manifest.json                 → ux-pwa-impl (already completed)
sw.js                         → ux-pwa-impl (already completed)
.orchestra/orchestration.json → Orchestrator ONLY
```

## The work

Follow `docs/superpowers/plans/2026-05-25-son-mai-theme.md` exactly, task by task:

### Task 1: Update CSS custom properties
- Replace `:root, html.theme-light` block with warm ivory palette
- Replace `html.theme-dark` block with warm charcoal palette
- All severity colors UNCHANGED
- Run eval, commit

### Task 2: Add Be Vietnam Pro font + Vietnamese typography CSS
- Update Google Fonts link to add Be Vietnam Pro
- Add `html[lang="vi"]` CSS rules for font-family, line-height, letter-spacing
- Verify `setLang` sets `document.documentElement.lang`
- Run eval, commit

### Task 3: Add cultural visual elements
- Add lotus divider CSS
- Add wave background CSS with severity suppression
- Add celadon card border CSS
- Add gold accent overrides for unofficial pill and AI disclosure
- Add severity class toggling in JS
- Add lotus dividers to Info tab HTML
- Run eval, commit

### Task 4: Update DESIGN.md
- Replace DESIGN.md with the Sơn Mài Authority version from the plan
- Run eval, commit

## Hard constraints (NON-NEGOTIABLE)

- Self-execute verifications — don't ask the user to paste commands
- DO NOT TOUCH files owned by other workstreams
- Run `python eval/run_all.py --skip integration` after each task and verify exit code 0
- Follow the plan's exact code — don't improvise different implementations
- Severity colors (green/amber/red/dark-red) are LOAD-BEARING SAFETY SIGNALS — never change them
- Every commit must use explicit file paths in `git add` (never `git add -A` or `git add .`)
- READ dashboard.html FRESH before starting — ux-pwa-impl has modified it

## What "done" looks like

- Warm ivory/charcoal palette applied (both light and dark modes)
- Celadon teal accent replaces blue
- Be Vietnam Pro loads and activates for Vietnamese language
- Lotus dividers appear in Info tab
- Wave background visible at low opacity, suppressed at high/critical severity
- Gold accent on UNOFFICIAL pill and AI disclosure
- DESIGN.md updated with full Sơn Mài Authority documentation
- All eval tests pass (45+ tests, exit code 0)
- Task marked `completed` via TaskUpdate
- Summary sent to orchestrator lead via SendMessage
