# Workstream: Hero-Check Implementation

## Identity

You are a **frontend engineer** implementing a UX change to elevate the address-check feature from a hidden tab into the always-visible hero section of the GG Tank Watch dashboard.

## Read first

- `dashboard.html` — the entire app is this one file. Read it fully before making changes.
- `CLAUDE.md` — project constraints (conduit pattern, no directives, safety principles)
- `docs/LANGUAGE_ACCESS.md` — G1 constraint on translations

## File ownership (EXCLUSIVE — only you write this)

- `dashboard.html`

## Do NOT touch

- `README.md`, `docs/*`, `DESIGN_LOG.md`, `CLAUDE.md`
- `scripts/*`, `data/*`, `eval/*`

## Context: The Design Decision

From office hours analysis, the dashboard currently hides the address-check feature behind the "Check" tab. A scared, limited-English elder who opens this link from their adult child shouldn't need to discover a tab to answer "am I in the evacuation zone?" The personal verdict should be front and center.

**Decision (approved):** Keep the tabbed architecture BUT move the address check into the always-visible hero section. The Check tab remains as an expanded version (with map pin, detailed explanation), but the core input + verdict is now above-the-fold, always visible.

## The work

### Phase 1: Understand the current Check tab

1. Read the full `panel-check` section in dashboard.html
2. Identify: the address input, the submit handler, the result display, the verdict logic
3. Understand what `check.router.inside` / `check.router.near` verdicts display

### Phase 2: Add address check to hero section

1. After the `hero-summary` paragraph (line ~873), add a compact address-check widget:
   - A text input with placeholder "Enter your address" (use data-i18n for the placeholder)
   - A submit button (magnifying glass icon or "Check" text)
   - A verdict display area (initially hidden, shows colored verdict when checked)
2. Style it to be compact — the hero should not become overwhelmingly tall
3. The verdict should be highly visible: green for safe/outside, amber for near, red for inside evacuation zone

### Phase 3: Wire up the hero check to existing logic

1. The existing safety-check logic (geocoding via Nominatim, point-in-polygon, distance calculation) should be REUSED, not duplicated
2. When the hero check fires, it should:
   - Run the same geocode + verdict logic as the Check tab
   - Display a condensed verdict in the hero (e.g. "✓ Outside evacuation zone" or "⚠ Inside evacuation zone")
   - Optionally: auto-switch to the Check tab to show the detailed result with map pin
3. If the user has already checked an address (stored in localStorage), show the last verdict on page load

### Phase 4: Keep the Check tab functional

1. The Check tab should still work as before — full address check with detailed results
2. When the hero check fires, the Check tab should reflect the same result
3. The Check tab becomes the "expanded view" — same verdict but with map pin, distance info, and full explanation

### Phase 5: i18n

1. Add any new string keys to the STRINGS object with en:, vi:, and es: translations
2. New keys to add (at minimum):
   - `hero.check.placeholder` — "Check your address" / "Kiểm tra địa chỉ của bạn" / "Verifique su dirección"
   - `hero.check.button` — "Check" / "Kiểm tra" / "Verificar"
   - Any verdict strings not already covered by existing keys

### Phase 6: Responsive design

1. On mobile (< 768px): the hero check should be full-width, stacked vertically
2. On desktop: the input can be inline with the hero text
3. The hero section should not exceed ~200px height on mobile even with the check widget

### Phase 7: Verify

1. Ensure no JavaScript errors (the STRINGS object is valid, all event handlers work)
2. Ensure the eval harness still passes: `python eval/run_all.py --skip integration`
3. Verify the existing Check tab still works independently

## Design constraints

- **Conduit posture:** The verdict routes to officials ("Check ggcity.org/emergency for official orders"), never says "you are safe" or "you should evacuate"
- **UNOFFICIAL badge stays** — it's legally required
- **AI disclosure stays** — it's the honesty principle
- **No new dependencies** — vanilla JS only
- **Match existing design system** — use CSS variables from :root, match font sizes and spacing patterns already in the file

## Done criteria

- Address input visible in hero section without scrolling or tab-switching
- Typing an address and submitting shows a colored verdict in the hero
- Check tab still works independently with full detail view
- All new strings have en:, vi:, es: translations
- Eval 45/45 still passes
- No JavaScript errors in the console
- Mobile-responsive (tested at 375px width conceptually)

## On completion

Mark your task as `completed` and SendMessage to the lead with: what you implemented, any design choices you made, any concerns about the hero height or mobile layout.
