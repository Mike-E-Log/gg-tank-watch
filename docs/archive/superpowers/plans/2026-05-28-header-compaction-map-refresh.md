# Plan: Fix blank-map-on-refresh + reclaim mobile header space

> Produced by the `header-compaction-and-map-refresh` workflow (3 lenses → adversarial verify → synthesis). Source-grounded; visual verification via signed Edge headless (SAC blocks the gstack browser).

## Goal
Stop the live Map (default tab) from collapsing on the 30s data-refresh, recover mobile header space, fix the clipped "As of …" freshness text — without weakening the binding honesty disclosure, breaking i18n, or touching official-source links.

## Map-bug root cause (confirmed)
`map.resize()` is called **nowhere** in `dashboard.html` (grep: zero `.resize(` / `ResizeObserver` / window resize listener). On the 30s refresh, `render()` → `setBanners()` (`:2008`, called `:2693`) injects a `flex-shrink:0` banner into the fixed-height `.app` column (`:121`, overflow:hidden). The banner's height is subtracted from the only `flex:1` sibling `.tab-content` (`:478`), cascading to `.map-outer` and `#maplibre-map` (height:100%). MapLibre's GL canvas only re-syncs on an explicit `resize()`, so it keeps stale pixel dims and the `overflow:hidden` parents clip it blank. An F5 reload re-runs the init IIFE (`:2849`) and re-fits — which is why reload "fixes" it, confirming the auto-refresh path.

## UNOFFICIAL pill — decision: keep but compact (do NOT remove)
Not legally mandated (no statute requires the literal word), but it's the highest-in-DOM, always-visible surface of the **binding** honesty/AI-transparency principle and the primary anti-impersonation signal during a live emergency. The safety-strip "Informational only — not official" is ALSO fixed chrome (`flex-shrink:0`, `:326`), so the two disclosures differ in function (identity label vs behavioral routing), not just redundancy — neither should absorb the other. Precise liability delta of removal is attorney-review territory (Lane B3). → Compact the pill (drop dot, trim padding) to free topbar width; keep the word, tooltip, and verified EN/VI strings.

## Tasks (all single-file `dashboard.html`, eval-neutral)
1. **[high] Map resize fix** — after `setBanners(banners)` (`:2693`): `if (_ggMap) { setTimeout(function(){ _ggMap.resize(); }, 0); }`. Defers one tick so post-banner layout settles. ✅ shipped.
2. **[high] Drop year from freshness clock** (`:2670`) — `As of 5/28, 12:10` instead of `…5/28/2026, 12:10`; JS-only, EN+VI both benefit, shared STRING untouched, full date+time stays in the hover title. ✅ shipped.
3. **[med] Compact UNOFFICIAL pill** — remove `.unofficial-pill-dot` span (`:1491`) + its CSS rule, padding `4px 8px`→`3px 6px`. Word/tooltip/`data-i18n`/VI intact. ✅ shipped.
4. **[med] Hero-status compaction** — padding `12px`→`8px`, value font `18px`→`16px`. ✅ shipped. **4c (one-row pack) REVERTED** — failed the 375px gate (clipped "DAY", ragged 3-line "RESIDENTS AFFECTED"); kept the safe two-row.
5. **[low] Safety-strip trim** — `.safety-strip` gap `4px`→`3px`, padding `10px`→`8px`. 44px AAA link targets and all 911/ggcity/714/OCFA links kept. ✅ shipped.

## Verification
- Eval: `python eval/run_all.py --skip integration` → 45/45 (data-contract only; does not cover CSS/JS).
- Edge-headless 375px: freshness no longer clipped ✅, UNOFFICIAL compact ✅, hero clean two-row ✅, map renders full-size ✅.
- **Pending on-device/interactive:** the *dynamic* map-resize repro (banner appearing 30s after init) — can't trigger in single-shot headless. The fix is the correct remedy for the confirmed root cause and does not regress normal render.

## Out of scope
Removing the pill/safety-strip disclosure (binding honesty principle); lowering link touch targets below 44px; any STRINGS/VI/link/tooltip change; ResizeObserver (larger pattern — adopt only if rotation/keyboard also blanks the map).
