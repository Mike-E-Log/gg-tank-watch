# Mobile UX & Stack Assessment — Evaluate whether single-file HTML is sufficient for best-in-class mobile emergency UX (deep session)

You are running the **mobile-ux-audit** workstream. 2 other workstreams run concurrently ("viet-design" on `docs/sessions/viet-design-report.md`, "data-sources" on `docs/sessions/data-source-audit.md`). You do NOT touch their files. You own your report only.

## Read first, in this order

1. `CLAUDE.md` (project)
2. `~/.claude/CLAUDE.md` (global)
3. `DESIGN.md` — current design system (Calm Authority aesthetic, Plus Jakarta Sans, slate/blue colors)
4. `dashboard.html` — the entire 2,255-line single-file dashboard (READ-ONLY, do not modify)

## Primary goal

Evaluate the current single-file HTML dashboard's mobile UX quality and determine whether the stack is sufficient for best-in-class emergency information delivery, or whether a framework migration is warranted. Produce an actionable recommendation document.

## File ownership

**You OWN (exclusive write access):**
```
docs/sessions/mobile-ux-assessment.md
```

**DO NOT TOUCH:**
```
docs/sessions/viet-design-report.md      → viet-design
docs/sessions/data-source-audit.md       → data-sources
dashboard.html                            → READ-ONLY
DESIGN.md                                → READ-ONLY
.orchestra/orchestration.json             → Orchestrator ONLY
```

## The work

### Phase 1 — Audit current mobile UX

Read `dashboard.html` thoroughly. Document:
- Current mobile responsiveness approach (viewport, 100dvh, safe-area-inset, flex layout)
- Touch target sizes (buttons, tabs, links) — are they meeting 44px minimum?
- Content hierarchy and information density on small screens
- Tab navigation UX (bottom bar, panel switching, scroll behavior)
- Hero section usability (address input, verdict display)
- Map interaction on mobile (Leaflet touch gestures, zoom controls)
- News feed scrollability and card design
- Loading states and perceived performance
- Offline/poor-connectivity behavior
- Accessibility (contrast ratios, screen reader support, focus management)

### Phase 2 — Benchmark against emergency info apps

Use WebSearch to research:
- Best-in-class emergency information mobile UX patterns (FEMA app, Ready.gov, weather alert apps, Citizen app, PulsePoint)
- Mobile UX patterns for high-stress/panic scenarios (what research says about cognitive load under stress)
- PWA capabilities that emergency tools should have (service worker, offline, push notifications, add-to-homescreen)
- What CalOES, OCFA, or similar agencies use for mobile emergency communication

### Phase 3 — Stack evaluation

Evaluate honestly:
1. **Single-file HTML (current):** What are the actual limitations for THIS use case? What can't it do that users need?
2. **PWA additions to current stack:** Service worker, manifest.json, offline cache — what would this add?
3. **React/Next.js migration:** What would this enable? What would it cost? (build step, dependency chain, deploy complexity, load time)
4. **Other options:** Astro, Svelte, or other lightweight frameworks

For each option, assess:
- Time to first meaningful paint on 3G mobile
- Offline capability
- Push notification support
- Developer maintainability at current scale (2,255 lines) and 2x scale
- Deployment simplicity (Vercel static vs build step)
- Risk to the ~50,000 users who need this NOW (migration downtime, regression risk)

### Phase 4 — Write recommendation

Write `docs/sessions/mobile-ux-assessment.md` with:

```markdown
# Mobile UX & Stack Assessment — GG Tank Watch

## Executive Summary
[2-3 sentences: stack verdict + top 3 UX improvements]

## Current Mobile UX Audit
### Strengths
### Weaknesses
### Accessibility Gaps

## Emergency UX Benchmarks
[What best-in-class emergency apps do that we don't]

## Stack Evaluation
### Option A: Stay single-file HTML (enhanced)
### Option B: Add PWA layer to current stack
### Option C: Framework migration
### Recommendation with rationale

## Concrete UX Improvements (prioritized)
[Numbered list of specific changes, each with: what, why, effort estimate]

## Mobile-Specific Enhancements
[Touch targets, gestures, offline, notifications]
```

## Hard constraints (NON-NEGOTIABLE)

- Self-execute verifications — don't ask the user to paste commands
- DO NOT TOUCH files owned by other workstreams
- DO NOT modify dashboard.html — this is a research/recommendation stream
- Be honest about the stack evaluation — if single-file HTML is sufficient, say so. Don't recommend a migration just because it's "modern"
- Consider that this is an ACTIVE EMERGENCY serving ~50,000 residents. Migration risk is real.
- The project is also an Anthropic fellowship portfolio piece demonstrating responsible AI deployment

## What "done" looks like

- `docs/sessions/mobile-ux-assessment.md` written with all sections complete
- Clear stack recommendation with rationale
- Prioritized list of concrete UX improvements
- Task marked `completed` via TaskUpdate
- Summary sent to orchestrator lead via SendMessage

## Out of scope

- Vietnamese cultural design → viet-design workstream
- News source completeness → data-sources workstream
- Code implementation — this stream produces recommendations only
