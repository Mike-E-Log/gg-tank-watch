# WCAG Accessibility Notes

Current accessibility status of `dashboard.html` and planned improvements.

## Emergency context and WCAG alignment

The dashboard is designed for stressed residents checking their phone during an evacuation. This drives design choices (high contrast, large touch targets, minimal cognitive load) that naturally align with WCAG 2.1 guidelines.

## What's in place

### Semantic HTML
- `<header>` for the top bar, `<section>` for the hero/status area, `<nav>` for the tab bar
- `<details>`/`<summary>` for collapsible info sections (native keyboard and screen-reader support)
- Heading hierarchy (`<h4>`) within info sections

### ARIA attributes
- `role="menu"` and `aria-haspopup`/`aria-expanded` on the language picker
- `role="menuitemradio"` with `aria-current` on language options
- `role="note"` on the safety disclaimer strip
- `role="status"` with `aria-live="polite"` and `aria-atomic="true"` on the address-check result (announces updates to screen readers without interrupting)
- `aria-label` on the theme toggle button
- `aria-hidden="true"` on decorative SVG icons (flags, sun/moon)

### Motion and visual preferences
- `@media (prefers-reduced-motion: reduce)` disables the breaking-news banner pulse animation
- Light/dark theme with user toggle; CSS custom properties ensure consistent contrast in both modes

### Color contrast
- Light mode: primary text `#0f172a` on `#f8fafc` background (contrast ratio ~15.4:1, exceeds AAA)
- Dark mode: primary text `#f1f5f9` on `#0f172a` background (contrast ratio ~15.4:1)
- Severity colors (safe/moderate/high/critical) use tinted backgrounds with text-on-background ratios designed for legibility
- Muted text (`#94a3b8` on light, `#64748b` on dark) is used only for non-essential metadata

### Touch and interaction
- Tab bar buttons are full-width with generous padding (mobile-first)
- Links in the safety strip include phone numbers as `tel:` links for one-tap dialing
- Language menu buttons have 8px padding for comfortable tap targets

## Known gaps

### Missing focus styles
- No custom `:focus-visible` ring on interactive elements beyond browser defaults. Tab-bar buttons and banner items would benefit from a visible focus indicator.

### Landmark coverage
- The main content area (`tab-content`) is not wrapped in a `<main>` landmark. Screen-reader users navigating by landmarks would miss it.

### Image alt text
- News thumbnail images use empty `alt=""` (treated as decorative). This is acceptable since the article text provides context, but descriptive alt text would improve the experience for screen-reader users.

### Skip navigation
- No skip-to-content link. The tab bar is at the bottom (mobile-app pattern), which partially mitigates this, but a skip link would help keyboard users bypass the header controls.

### Form labels
- The address-check input relies on placeholder text rather than a visible `<label>`. Screen readers can read the placeholder, but an associated label is more reliable.

## Status at archive freeze (2026-06-04)

The gaps above were the state at the time of writing; they were resolved before the archive was frozen:

1. ✅ `:focus-visible` outlines added to interactive elements
2. ✅ Tab content wrapped in a `<main>` landmark
3. ➖ Visible `<label>` for the address-check input, **moot**: the address checker was removed in the conduit pivot (2026-05-26), so the input no longer exists
4. ✅ Skip-navigation link added
5. Muted-text contrast reviewed; see `accessibility.html` for the current accessibility statement and disclosed limitations
