# Plan: Mobile-responsive header + legend/map consistency

Branch `fix/mobile-responsive-header`. All edits in `dashboard.html`, mobile-scoped (mobile-first base + `≥600/768px` restores), so desktop is unchanged. Verify at 360px + 390px (mobile) AND ≥768px (desktop).

> Note: the page already has the viewport meta tag, media-query breakpoints, and a flex layout — so it is already responsive. The real issues are specific: freshness clips in an overcrowded topbar, the hero reflows raggedly, and the legend shelter icon doesn't match the map markers.

## 1. Freshness clip → own line on mobile (robust)
The topbar (pill + wordmark + freshness + 2 buttons) can't fit on a phone; freshness is the only shrinkable item, so it ellipsis-clips ("As of 5/2") on narrow/real devices. Fix = take it out of the inline competition.

**Implemented (final):** the base `.topbar`/`.topbar-freshness` stay at their DESKTOP values, and a single `@media (max-width: 599px)` block (placed AFTER the base rules to avoid a cascade conflict) applies the mobile treatment:
```css
@media (max-width: 599px) {
  .topbar { flex-wrap: wrap; }
  .topbar-freshness { order: 1; width: 100%; display: block; text-align: right; overflow: visible; }
}
```
`display:block; width:100%; text-align:right` is used instead of `flex: … justify-content:flex-end` — the flexbox right-alignment of the inner label misbehaved (the label overflowed its full-width box); plain block + `text-align:right` is bulletproof. Result: "As of 5/28, 12:10 PM" on its own right-aligned line, never clips. Desktop (≥600px) keeps the original inline freshness untouched.

**Verification note:** direct headless screenshots at mobile width render the page wider than the window (artifact) — verify mobile via a same-origin iframe forced to 390px (`doc.scrollWidth` stays 390, 0 elements wider than viewport).

## 2. Hero → fluid 2-col grid on mobile
Current `.hero-status-row` is `flex; flex-wrap; gap:16px` → ragged 2 rows with a wide 16px row-gap.
- Base/mobile: `.hero-status-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px 12px; }` (clean 2×2, tighter row-gap) and `.hero-status-item { min-width: 0; }`.
- Restore at ≥768px (merge into the existing hero `≥768` block that already restores padding 12px + font 18px): `.hero-status-row { display: flex; gap: 16px; }` + `.hero-status-item { min-width: 80px; }`.

## 3. Legend shelter icon → match the map markers
Legend shelter icon is a green square **with 🏠** (HTML :1559, CSS :632); map markers (JS :2909) are plain 14px green squares with **no glyph** → mismatch. Make the legend match the map (minimal diff; map is the source of truth):
- HTML :1559 — remove `&#127968;` from the shelter icon span.
- CSS `.legend-icon-shelter` (:632) — drop the flex-centering/font-size/line-height/color (glyph styling); keep `width:14px; height:14px; border-radius:3px; background:#1B9E77` → plain green square matching the marker.
- (Alternative, not chosen: add 🏠 to the 14px map markers — rejected, the glyph is near-invisible at that size and adds JS churn.)

## Verification
- `python eval/run_all.py --skip integration` → 45/45 (data-contract; does not cover CSS).
- Edge headless (SAC blocks gstack browser): 360px + 390px → freshness on its own line, no clip; hero clean 2×2; legend shelter = plain green square matching map. 1366px → topbar inline freshness with year, hero 4-up flex, unchanged.

## Out of scope
Safety-strip height (bounded by 44px AAA touch targets + required disclosure/links — would need an a11y trade-off; flag to user separately). Changing safety copy (G1). The `data-i18n`-wipes-children footgun on the pill (already documented; not re-litigating here).
