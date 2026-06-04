# Dashboard Transformation — Full UI/UX Overhaul (queued session — after research + data-pipeline)

You are running the **Dashboard** workstream. You are QUEUED — you start only after the research and data-pipeline streams complete. The orchestrator will provide you with:
1. Research findings from `docs/sessions/ux-research-findings.md`
2. Data files: `timeline.json`, updated `config.json` with community resources

3 other workstreams ran before/alongside you ("research" produced design direction; "data-pipeline" produced data files; "portfolio" updated docs).

## Read first, in this order

1. `CLAUDE.md` (project)
2. `~/.claude/CLAUDE.md` (global)
3. `.orchestra/CONTRACTS.md` — cross-cutting contracts (tab structure, schemas, safety constraints). READ ONLY.
4. `docs/sessions/ux-research-findings.md` — **THE DESIGN DIRECTION. Follow its recommendations.**
5. `timeline.json` — the historical event data you'll render
6. `config.json` — updated with community_resources array
7. `DESIGN.md` — Son Mai Authority design system
8. `docs/sessions/viet-design-report.md` — Vietnamese cultural design context
9. `docs/WCAG_NOTES.md` — accessibility gaps to fix
10. `dashboard.html` — the file you own. Read it thoroughly.

## Primary goal

Transform dashboard.html into a premium, community-maximizing emergency dashboard. Desktop: no-scroll static layout at 1920x1080 with internal scroll in data panels. Mobile: premium redesigned experience. Both: Son Mai theme preserved, new tab structure (Map | Updates | Resources | About), timeline rendering with filters, community help features, accessibility fixes.

## File ownership

**You OWN (exclusive write access):**
```
dashboard.html
```

**DO NOT TOUCH:**
```
config.json, timeline.json, scripts/, eval/  → data-pipeline (already completed)
README.md, docs/AI_CONTROL_ARCHITECTURE.md   → portfolio
docs/sessions/*                              → research / orchestrator
.orchestra/CONTRACTS.md                      → Orchestrator ONLY
.orchestra/orchestration.json                → Orchestrator ONLY
```

## The work

Follow the research findings for design direction. The phases below are the functional requirements; the research findings determine HOW to implement them visually.

### Phase 1 — Tab restructure

Per CONTRACTS.md, restructure from `Map | News | Check | Info` to `Map | Updates | Resources | About`:

1. **Remove Check tab** — delete `panel-check`, `tab-check` button, and all check-panel CSS/JS. The hero address checker stays.
2. **Rename News → Updates** — update tab button text, i18n keys, panel IDs
3. **Create Resources tab** — move shelters grid, official source links from old Info tab. Add community resources (FEMA, DA tip line, price gouging hotline) from config.json's `community_resources` array. Add i18n keys.
4. **Create About tab** — move methodology, sources verified, "who made this", terms/disclaimer from old Info tab collapsible sections. Make them full sections, not collapsed.
5. **Incident status** — place per research findings (always-visible strip or inside a tab)

### Phase 2 — Historical timeline in Updates tab

Fetch `timeline.json` and render below the live updates:

1. **Section header:** "Incident timeline" with event count
2. **Filter chips:** Day filters (Day 1-5 with dates) + category filters (from CONTRACTS.md categories). Multiple active filters = AND logic. Chips should use Son Mai design language.
3. **Event cards:** Each event shows timestamp (local time), title, description, source link, category chip. Compact but scannable.
4. **Internal scroll:** Timeline scrolls within its panel. Page viewport stays fixed on desktop.
5. **Empty state:** "No events match filters" when all filtered out

### Phase 3 — Desktop no-scroll layout (1920x1080)

Follow the research findings for layout model (panels vs. tabs vs. hybrid):

1. **Viewport lock:** `html, body { overflow: hidden; height: 100vh; }` on desktop
2. **Layout:** Implement the research-recommended pattern at `@media (min-width: 1024px)`
3. **Internal scroll:** Data-heavy panels (Updates timeline, Resources list) scroll internally with `overflow-y: auto`
4. **Full width:** Remove the `max-width: 800px` constraint on desktop
5. **Information density:** Every pixel should earn its space at 1920x1080

### Phase 4 — Mobile premium redesign

Follow the research findings for mobile design:

1. **Keep tab-based navigation** (standard mobile pattern) but upgrade the visual quality
2. **Premium touch targets:** 44px+ minimum (already in place, verify)
3. **Typography:** Son Mai theme's Be Vietnam Pro for Vietnamese, system fonts for other languages
4. **Spacing and rhythm:** Consistent padding, generous whitespace, breathing room
5. **Micro-interactions:** Subtle transitions on tab switches, filter toggles, card reveals (respect `prefers-reduced-motion`)

### Phase 5 — Community help features in Resources tab

1. **Community resources section:** Render `config.json.community_resources` as cards with:
   - Title (localized via `title_vi` for Vietnamese)
   - Phone number as `tel:` link (one-tap dial)
   - URL as external link
   - Description
   - Category chip
2. **Shelter enhancements:** If the research recommends shelter filtering (pet-friendly, ADA), add filter indicators to the existing shelters grid
3. **Official sources:** Move from old Info tab. Keep the existing styled cards.

### Phase 6 — Accessibility fixes

Per `docs/WCAG_NOTES.md`:

1. **Focus styles:** Add `:focus-visible` outlines to all interactive elements (tabs, buttons, links, inputs). Use Son Mai celadon (#0e6f5e) for focus ring.
2. **Main landmark:** Wrap tab content area in `<main>` element
3. **Skip navigation:** Add a skip-to-content link at the top (visually hidden until focused)
4. **Form labels:** Add visible `<label>` to the hero address input (can be visually styled to look like the current placeholder)
5. **Verify ARIA:** Ensure all new tabs/panels have proper `role`, `aria-labelledby`, `aria-controls`

### Phase 7 — Print-friendly CSS

Add `@media print` styles:
1. Show all content (no tabs — print all panels sequentially)
2. Expand collapsed sections
3. Remove interactive elements (theme toggle, language picker, address checker)
4. Add URL text after links
5. Black and white friendly (Son Mai colors become grayscale)
6. Include the AI disclosure and official source links prominently

### Phase 8 — Verify

1. Run `python eval/run_all.py --skip integration` — must pass
2. Open dashboard.html in a browser and verify:
   - All 4 new tabs work (Map, Updates, Resources, About)
   - Timeline loads and renders events from timeline.json
   - Filter chips work (day + category)
   - Desktop layout is no-scroll at 1920x1080
   - Mobile layout is clean and premium
   - Dark mode works with all new elements
   - Vietnamese language switch works
   - Community resources render with clickable phone/URL links
   - Focus styles visible on tab navigation
   - Print preview shows all content
   - Hero address checker still works
   - No console errors

## Hard constraints (NON-NEGOTIABLE)

- Self-execute verifications — don't ask the user to paste commands
- DO NOT TOUCH files owned by other workstreams
- Treat `.orchestra/CONTRACTS.md` as authoritative; READ it, never write it
- **Follow the research findings** for design direction — don't independently decide layout/aesthetic
- Son Mai Authority theme is the foundation — celadon (#0e6f5e), warm ivory (#faf8f5), Be Vietnam Pro
- Severity colors UNCHANGED (safe green, moderate amber, high orange, critical red)
- Conduit pattern — no directive language anywhere
- AI disclosure must persist on all views
- `noindex` meta tag stays
- No new dependencies (everything is vanilla HTML/CSS/JS)
- G1: Vietnamese translations for NEW strings are placeholders — mark with `/* G1 placeholder */` comment
- `prefers-reduced-motion` must be respected for any new animations
- All new interactive elements need ARIA attributes

## What "done" looks like

- dashboard.html fully transformed with all 8 phases complete
- 4-tab structure: Map | Updates | Resources | About
- Timeline renders 40+ events with working day/category filters
- Desktop: no-scroll at 1920x1080, full-width, premium layout
- Mobile: premium tabbed experience
- Community resources (FEMA, tip lines) accessible in Resources tab
- Accessibility gaps from WCAG_NOTES.md addressed
- Print CSS added
- `python eval/run_all.py --skip integration` passes
- No console errors in browser
- Task marked `completed` via TaskUpdate
- Summary sent to orchestrator lead via SendMessage

## Out of scope

- Creating timeline.json → data-pipeline (already done)
- Editing config.json → data-pipeline (already done)
- README/docs → portfolio
- Research → research (already done)
- Shared doc updates → Orchestrator

## On completion

1. Mark your task `completed` via `TaskUpdate`
2. `SendMessage` the orchestrator lead with: phases completed, tab count, event count rendered, desktop/mobile verified, console errors (if any)
3. The orchestrator reads your transcripts for full visibility — no journal needed
