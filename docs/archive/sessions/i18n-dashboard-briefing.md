# Workstream: Dashboard i18n

> **⚠️ Correction (2026-05-29):** The claim below that "G1 has been LIFTED for Vietnamese — Nancy has verified the translations" was **false**. Nancy is not a fluent Vietnamese speaker and reviewed only a few strings, so the G1 native-verification bar was never met. Vietnamese has since been set `ready:false` (held); the shipped VI is treated as AI-drafted/unverified. This briefing is retained as the historical record of how the unverified-VI state arose. See `docs/LANGUAGE_ACCESS.md`, `docs/research/2026-05-29-vi-anthropic-lens-research.md`, and the build-failing guard `eval/test_language_access.py`.

## Identity

You are a **localization engineer** adding verified Vietnamese translations and scaffolding Spanish for the GG Tank Watch dashboard. The G1 constraint (no machine-translated safety copy ships without native verification) has been LIFTED for Vietnamese — Nancy has verified the translations. Spanish strings are scaffolded with `ready: false` for future native verification.

## Read first

- `docs/LANGUAGE_ACCESS.md` — language prioritization and G1 constraint
- The existing `STRINGS` object in `dashboard.html` (search for `var STRINGS`) — 69 Vietnamese strings already exist as verified reference for tone/style
- The `LANGS` array in `dashboard.html` — Vietnamese is `ready: true`, Spanish is `ready: false`

## File ownership (EXCLUSIVE — only you write this)

- `dashboard.html`

## Do NOT touch

- `README.md`, `docs/fellowship/*` (owned by fellowship stream)
- `scripts/*`, `data/*`, `eval/*` (owned by ops stream)
- `CLAUDE.md`, `docs/*.md` (shared/frozen)

## Goal

Complete Vietnamese coverage (add vi: translations for all 44 missing string keys) and scaffold Spanish (add es: translations for all ~109 string keys with `ready: false`).

## The work

### Phase 1: Vietnamese — add 44 missing translations

The following keys have `en:` but no `vi:`. Add verified Vietnamese translations matching the tone of existing strings (calm, non-directive, official-routing register):

**Safety-critical (highest priority):**
- `disclosure.ai` — the AI transparency notice
- `safety.strip.info` — informational-only disclaimer
- `safety.strip.official` — official source label
- `check.router.inside` — "inside evacuation zone" verdict
- `check.router.near` — "near evacuation zone" verdict
- `banner.stale.msg` — stale data warning
- `banner.offline.detail` — offline notice

**Trust/about:**
- `topbar.unofficial` — UNOFFICIAL badge
- `topbar.unofficial.title` — tooltip explaining unofficial status
- `info.about.title`, `info.about.body`, `info.about.official`
- `info.about.termslink`, `info.about.conductlink`
- `safety.strip.terms`

**Informational:**
- `updated.freshness`, `updated.stale`, `updated.title`
- `hero.severity.label`, `hero.summary.loading`, `hero.lead`
- `hero.summary.default`, `hero.summary.resolved`
- `news.feed.title`, `news.situation.label`
- `news.type.official`, `news.type.article`, `news.type.video`
- `news.statements.count`
- `info.group.status`, `info.group.wheretogo`, `info.group.official`
- `info.official.note`, `info.official.city`, `info.official.zonehaven`
- `info.official.alert`, `info.official.airnow`
- `info.group.closures`, `info.roads.title`, `info.roads.defer`
- `info.group.sources`
- `check.loading`, `check.error.noResult`
- `time.minAgo`

**Translation guidelines:**
- Match the register of the 69 existing verified Vietnamese strings
- Use formal but accessible Vietnamese (not overly literary, not colloquial)
- Safety-critical strings must be unambiguous — "không chính thức" for unofficial, never "phi chính phủ"
- Never translate to imply directives — route to officials, don't command action
- Keep the conduit posture: amplify/translate official info, never author safety advice
- Preserve any template variables like `{t}` exactly as-is

### Phase 2: Spanish scaffold

Add `es:` to ALL string keys in the STRINGS object. These are DRAFT translations — high-quality but pending native verification. Do NOT flip `ready: true` for Spanish.

**Spanish guidelines:**
- Use Latin American Spanish (the local community is primarily Mexican/Central American)
- Formal "usted" register for safety-critical copy
- Same conduit posture as Vietnamese — no directives, route to officials
- Preserve template variables `{t}` etc.

### Phase 3: Verification

1. Verify no JavaScript syntax errors: the STRINGS object must remain valid JS
2. Count: every key should have `en:`, `vi:`, and `es:` (109 keys × 3 languages)
3. Vietnamese: `ready: true` stays (already set)
4. Spanish: `ready: false` stays (DO NOT change)

## Done criteria

- All 44 missing Vietnamese keys have vi: translations added
- All ~109 keys have es: scaffold translations
- dashboard.html still loads without JS errors (check STRINGS syntax)
- No other files modified
- Vietnamese `ready: true`, Spanish `ready: false`

## On completion

Mark your task as `completed` and SendMessage to the lead with: count of vi strings added, count of es strings added, any keys where translation was uncertain.
