# Vietnamese Cultural Design System — Research and propose a culturally-resonant theme for the emergency dashboard (deep session)

You are running the **viet-design** workstream. 2 other workstreams run concurrently ("mobile-ux-audit" on `docs/sessions/mobile-ux-assessment.md`, "data-sources" on `docs/sessions/data-source-audit.md`). You do NOT touch their files. You own your report only.

## Read first, in this order

1. `CLAUDE.md` (project)
2. `~/.claude/CLAUDE.md` (global)
3. `DESIGN.md` — current design system (Calm Authority aesthetic, Plus Jakarta Sans, slate/blue colors, severity-based color system)
4. `dashboard.html` — read the CSS section (lines 13-911) and the i18n LANGS/STRINGS system to understand current visual implementation (READ-ONLY)

## Primary goal

Research Vietnamese visual design aesthetics and propose a culturally-resonant theme for GG Tank Watch that honors the heavily Vietnamese community (~50,000 evacuated residents, many Vietnamese-speaking) while maintaining emergency readability and the "Calm Authority" design principle. The theme should feel like it was made BY and FOR this community, not just translated into Vietnamese.

## File ownership

**You OWN (exclusive write access):**
```
docs/sessions/viet-design-report.md
```

**DO NOT TOUCH:**
```
docs/sessions/mobile-ux-assessment.md     → mobile-ux-audit
docs/sessions/data-source-audit.md        → data-sources
dashboard.html                             → READ-ONLY
DESIGN.md                                 → READ-ONLY
.orchestra/orchestration.json              → Orchestrator ONLY
```

## The work

### Phase 1 — Research Vietnamese visual design

Use WebSearch to research:
- **Vietnamese design aesthetics:** Color palettes in Vietnamese culture (beyond the flag's red/yellow — consider nature, architecture, food, textiles, lacquerware, ceramics)
- **Garden Grove / Little Saigon context:** This area (Westminster, Garden Grove, Fountain Valley) is the largest Vietnamese community outside Vietnam. What visual language resonates with Vietnamese-Americans specifically?
- **Vietnamese typography:** What fonts work well with Vietnamese diacritical marks (tonal marks are critical: ắ, ẩ, ậ, ế, ệ, ồ, ợ, ứ, ừ, etc.)? Plus Jakarta Sans is currently used — does it render Vietnamese well?
- **Emergency + cultural design:** How do Vietnamese government agencies, Vietnamese-American community organizations, and Vietnamese media design emergency communications?
- **Color psychology in Vietnamese culture:** Red = luck/celebration, yellow = royalty/prosperity — but this is an EMERGENCY tool. What colors convey "trustworthy community resource" vs "panic"?
- **Vietnamese design studios/brands:** Look at modern Vietnamese design (not stereotypical) — Vietcetera, VnExpress, Vietnamese government digital services, Vietnamese-American business signage in Little Saigon

### Phase 2 — Evaluate constraints

Map the design constraints:
1. **Emergency readability:** Severity colors (green/amber/red/dark-red) are load-bearing and cannot change — they communicate danger levels
2. **Dark mode support:** Theme must work in both light and dark
3. **Outdoor phone readability:** High contrast required — users may be outside in sunlight during evacuation
4. **Cultural sensitivity:** This is an emergency, not a celebration. Vietnamese cultural elements should convey "community care" and "trusted authority," not "festive" or "decorative"
5. **Accessibility:** WCAG AA contrast minimums on all text
6. **Current system compatibility:** Changes should layer on top of the existing CSS custom property system (--bg, --surface, --text-primary, etc.)

### Phase 3 — Propose design system

Create a complete design proposal covering:

1. **Color palette:**
   - Primary surfaces (background, cards) — culturally-informed but emergency-appropriate
   - Text colors — maintaining contrast
   - Accent colors — replacing or complementing the current blue (#1e40af)
   - How Vietnamese cultural colors integrate WITHOUT conflicting with severity indicators
   - Specific hex values for light and dark modes

2. **Typography:**
   - Evaluate Plus Jakarta Sans for Vietnamese rendering quality
   - Research alternative fonts if needed (must support full Vietnamese character set with all diacriticals)
   - Weight and size recommendations for Vietnamese text (Vietnamese words tend to be shorter but diacriticals need vertical space)

3. **Visual elements:**
   - Subtle cultural motifs that could work as background patterns, section dividers, or icon styles
   - Consider: lotus patterns, wave motifs, geometric patterns from Vietnamese architecture, ceramic-inspired elements
   - These should be SUBTLE — emergency tool first, cultural expression second
   - Suggest where they could appear without cluttering the information hierarchy

4. **Iconography:**
   - Tab icons, status indicators, navigation elements
   - Style direction that feels culturally warm without being stereotypical

5. **Language-specific theming:**
   - Should the theme change based on selected language? (e.g., subtle Vietnamese elements appear when vi is selected, neutral when en is selected)
   - Or should the Vietnamese character always be present as a nod to the community?

### Phase 4 — Write design report

Write `docs/sessions/viet-design-report.md` with:

```markdown
# Vietnamese Cultural Design System — GG Tank Watch

## Executive Summary
[2-3 sentences: design direction + key cultural choices]

## Research Findings
### Vietnamese Visual Design Traditions
### Garden Grove / Little Saigon Context
### Vietnamese Typography Requirements
### Emergency Communication Design in Vietnamese Communities

## Design Constraints
[What cannot change and why]

## Proposed Color Palette
### Light Mode
### Dark Mode
### Integration with Severity Colors

## Typography Recommendation
[Font evaluation + recommendation with Vietnamese rendering evidence]

## Cultural Visual Elements
### Recommended Motifs (with mockup descriptions)
### Placement Strategy
### What to Avoid (stereotypes, inappropriate elements)

## Language-Aware Theming Strategy
[Whether/how the theme adapts by language selection]

## Implementation Guide
[CSS custom properties to add/modify, specific hex values, font changes if any]

## Mood Board References
[URLs to design references that capture the proposed direction]
```

## Hard constraints (NON-NEGOTIABLE)

- Self-execute verifications — don't ask the user to paste commands
- DO NOT TOUCH files owned by other workstreams
- DO NOT modify dashboard.html or DESIGN.md — this is a research/design stream
- Cultural authenticity matters — avoid stereotypes (no generic "Asian" patterns, no dragons unless culturally appropriate for this context)
- Emergency readability is NON-NEGOTIABLE — beautiful but unreadable = people in danger
- Severity colors (green/amber/red/dark-red) are load-bearing safety signals — the theme works AROUND them, not over them
- This community is Vietnamese-AMERICAN — the design should reflect the diaspora identity, not just Vietnam

## What "done" looks like

- `docs/sessions/viet-design-report.md` written with all sections complete
- Concrete color palette with hex values for both light and dark modes
- Typography recommendation with Vietnamese rendering assessment
- Cultural motif proposals with placement guidance
- Task marked `completed` via TaskUpdate
- Summary sent to orchestrator lead via SendMessage

## Out of scope

- Mobile UX patterns → mobile-ux-audit workstream
- News source coverage → data-sources workstream
- Code implementation — this stream produces design recommendations only
