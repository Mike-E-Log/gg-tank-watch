# Info Tab — Acceptance Rubric (fixed target)

**Purpose.** This is the *fixed target* the Info tab is judged against, so passes **converge** instead of churning. It exists because the Info tab went 3→6→4 sub-tabs across PRs #108–#110 with the structural target explicitly deferred ("pending design decision") and a visual check that ran *after* shipping rather than *in* the loop — see `~/Documents/AI_Agent_UIUX_Research_20260602/` for the full diagnosis. **Do not start an Info-tab pass without this rubric open. If the target should change, change THIS FILE first, then build — never the reverse.**

**Scope note.** The Info tab is a *design-complete, frozen-archive* surface. This rubric is the **definition of done for any future change**, not a directive to restyle what shipped.

---

## 0. Hard constraints (any failure = pass fails, no exceptions)

These are the criteria a text-only test cannot see and that caused the #108→#109 reversal. **Verify by rendered screenshot, not by reading CSS.**

- [ ] **Sub-tab bar fits ONE row, NO horizontal scroll, at 320 / 360 / 375 / 390 / 430 px.** Every tab label fully visible (no clipped "Recovery", no hidden "About"). *(This is the exact failure of PR #108.)*
- [ ] **No content clipped or overflowing** its panel at those widths, light **and** dark.
- [ ] **Persistent honesty disclosure visible** (never clipped) at the shortest supported height (≈568px CSS).
- [ ] **Touch targets ≥ 44px** for every sub-tab and interactive row.
- [ ] **English-only** safety/UI copy (G1). No non-English surface, even a link framed as ours.
- [ ] **Conduit only** — no authored directives; route to officials.

## 1. Information architecture (the structural target — FIXED)

- [ ] Exactly **4 equal-width sub-tabs, single row**: `Summary | Officials | Resources | About` (`renderInfoTab`). Changing the count or set requires editing this file first.
- [ ] Each panel opens with one `.info-desc` descriptor band (3px celadon left border + surface tint).
- [ ] **Summary** = sourced peak facts only (≈100°F / ≈50,000 / ≈9 sq mi from `timeline.json`).
- [ ] **Officials** = route-to-officials only: the official channels, each with a one-line `.info-row-desc` description of what the channel is for. No general safety-advice note (the "No single source…" note was removed 2026-06-02 per user — generic boilerplate that didn't fit a frozen, resolved archive).
- [ ] **Resources** = shelters + school closures + recovery aid as labeled `.info-section-title` sections (no card grid — cross-model review hard-rejected card-grid-first). Descriptor band copy stays to **one line at 375px**.
- [ ] **About** = AI disclosure (12px, body near-black `--sa-text` — binding honesty, surfaced as the first line, **not** a gold accent) + an Accessibility link (Terms lives in the persistent safety strip, so it is no longer duplicated here) + a "Sources" fold that is **open by default**, opens with a one-line `.info-fine` caption stating what the list is (the provenance trail the pipeline checked), and tags the official City/County sources with an "Official" label. The single duplicate routing line (`disclosure.aiRoute`) was removed 2026-06-02 — concrete 911/ggcity routing is carried persistently by the safety strip.

## 2. Visual system (token rubric — already stable in DESIGN.md; conform, don't reinvent)

- [ ] Type scale from `DESIGN.md` only: body Plus Jakarta Sans 14px/1.4; data IBM Plex Mono tabular-nums; labels 11–12px. **No inline `font-size`** (use `.info-fine` / `.info-desc` / `.info-who-body`; guarded by `test_no_inline_font_size_in_info_panels`).
- [ ] Surfaces `--sa-surface` on `--sa-bg`; `--sa-border` hairlines; celadon = active/interactive; gold reserved for the UNOFFICIAL pill (the AI disclosure now renders at body `--sa-text`, not gold — changed 2026-06-02 per user; the disclosure stays binding via its text + first-line placement, not the color accent).
- [ ] Spacing on the 4px base unit, compact density. Row padding consistent across panels (the #110 "breathing room" value, applied uniformly — verify rendered, not just the string).
- [ ] Sub-tab bar height **matches the News chip-bar** (verify the bars align at 375px by screenshot, not by `padding:` string match).

## 2a. Cross-panel consistency tokens (the four panels are ONE system — harmonized 2026-06-02)

Summary / Officials / Resources / About previously read as four designs (two key/value row systems, a 12px-vs-14px gutter drift, 500-vs-600 values, a lone dashed row, dimmer school names). Fixed tokens, guarded by `test_info_panel_consistency`:

- [ ] **One 14px horizontal gutter** for all panel content (`.info-section`, `.info-section-title`, `.info-kv-row`, `.info-schools-grid`, `.about-body`, `.info-who-body`) so every sub-tab shares one left edge. Nested `.info-section > .info-who-body` zeroes its inner gutter (no 14+14).
- [ ] **One key/value row**: `9px` vertical padding, `13px`, `1px solid var(--sa-border)` hairline, key `--sa-text-2`/400, value `--sa-text`/**600**. Applies to BOTH `.info-kv-row`/`.info-kv-val` (Summary) and `.info-row`/`.v` (Officials) — no dashed row, no 500 value.
- [ ] **List rows** (`.info-school-card`, `.shelter-row`): `9px` rhythm; names at value color `--sa-text` (not dimmed `text-2`).
- [ ] **Unchanged role distinctions** (intentional, NOT inconsistencies): descriptor band `.info-desc`, section titles 10px/700/caps, body `.info-who-body` 12px, fine print 11px. (The AI disclosure renders at body `--sa-text` 12px, not a gold accent — changed 2026-06-02 per user.)

## 3. Definition of done (the loop — run EVERY pass, in this order)

1. **Open this rubric.** If the change implies a structural edit (§1), amend §1 here *first*.
2. **Implement** against the fixed target.
3. **Render-and-diff IN the loop (not after):** signed-Edge headless screenshot at **320, 360, 375, 390, 430, 768 px**, light + dark. Compare each against §0 + §1 + §2. List differences; fix; re-shoot. Repeat until zero §0 failures. *(SAC-safe: `msedge --headless=new --screenshot`, per project memory.)*
4. **Text eval** `python eval/run_all.py --skip integration` → green by scorecard (never `--quiet`).
5. **Add/keep a geometry guard** (see §4) so the §0 fit-failure class can't silently regress.
6. **SW cache bump** (`gg-tank-vN`) on any `dashboard.html`/config change.
7. Pass is "done" only when **§0 = all green by screenshot** AND text eval green.

## 4. Close the eval's blind spot (highest-leverage one-time add)

The current `eval/test_info_*` guards are **text-only string-matches** — they passed 171/171 while #108's bar was clipped on a real 375px device. Add **one** guard that measures *rendered geometry* (via the existing signed-Edge headless + a DOM `getBoundingClientRect` probe) and **fails when the sub-tab bar's scrollWidth exceeds its clientWidth at 375px** (i.e., it wrapped or scrolled). This single test converts the §0 fit-constraint from "judged by feel" into an enforced behavioral gate — directly extending the project's scalable-oversight thesis to the visual layer.

---

*Companion: cross-project process in `~/.claude/agent-uiux-playbook.md`. Full evidence + diagnosis in `~/Documents/AI_Agent_UIUX_Research_20260602/`.*
