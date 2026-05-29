# Language Access

Which languages GG Tank Watch ships, why, and what it takes to add one.

The driving question: **maximize reach to the residents most at risk** — displaced,
elderly, limited-English, low-income. For an emergency tool the right metric is not
raw speaker count but **limited-English proficiency (LEP)**: the people who *cannot*
get the information in English are exactly the people a translation serves.

## Binding constraint (G1)

**No machine-translated safety copy ships.** Every non-English string must be
verified by a native speaker before it goes live. A wrong "you're safe" is far worse
than a missing translation (see [DISTRIBUTION.md](DISTRIBUTION.md) G1, [LEGAL.md](LEGAL.md)).
Until a verified translation exists, the UI falls back to English (`t()` does this
automatically) — never to a machine translation.

This makes **sourcing verified native translators the blocking dependency**, not the
code. The i18n framework supports N languages today; a language only appears in the
picker when its verified copy lands.

## The affected area

Incident site: GKN Aerospace, 12122 Western Ave, Garden Grove — at the Garden
Grove / Westminster line, in the heart of **Little Saigon**. The ~50,000-resident
evacuation zone spans western Garden Grove, Westminster, and parts of Anaheim and
Stanton.

## Demographics (US Census / ACS)

| City | Top home languages after English | Key figure |
|---|---|---|
| Garden Grove | Vietnamese ≈ Spanish (co-dominant), then Korean | **19.3% of households are limited-English** (vs 8.7% countywide); 46.8% foreign-born |
| Westminster | Vietnamese (overwhelming — Little Saigon), then Spanish | 47.6% speak a non-English language at home |
| Anaheim | Spanish (dominant), then Vietnamese / Korean / Tagalog | 35.2% speak Spanish at home; Latino 53% |
| Stanton | Spanish (Mexican 49.9%), then Vietnamese (17.1%) | Hispanic 54.5%, Vietnamese 17.1% |

Concrete language ranking (Orange County NW–Garden Grove East PUMA, by households):
**Vietnamese 48,608 ≈ Spanish 48,222 ≫ Korean 3,362** — a ~14x cliff after the top two.

**LEP rate is the tiebreaker** (2019 Census, share who speak English "less than very
well"): **Vietnamese 57%** (highest of any major US language; ~31% limited-English
*households*), **Spanish 39%**, Arabic 35%, **Tagalog 30%** (lowest). So Vietnamese
speakers need translation *most per capita* — and they are the most concentrated in
the actual evacuation zone.

Sources: OC Census Atlas (Garden Grove); Census QuickFacts (Garden Grove);
Data USA (Garden Grove / Westminster / Stanton); Census, "Languages We Speak in the
United States" (2022, 2019 ACS). Exact city-level ACS table pulls (B16001 / C16001 /
B16004) can refine the numbers but do not change the ranking.

## Decision — prioritized language set

- **Tier 1 — must-have.** **Vietnamese** (held — `ready:false`; AI-drafted strings await a fluent native verifier, G1) and
  **Spanish**. These two cover the overwhelming majority of LEP residents across all
  four cities.
- **Tier 2 — strong next.** **Korean** — ~14x fewer speakers than the top two, but
  high per-capita LEP and a real Garden Grove community.
- **Tier 3 — defer / monitor.** Chinese (Mandarin/Cantonese) and Arabic (Anaheim's
  Little Arabia) are smaller in the immediate zone. **Tagalog deprioritized** —
  Filipino speakers have the lowest LEP rate (mostly English-proficient).

## Translator sourcing checklist (the human long-pole)

Each language needs a verified native translator before its copy ships. Status:

- [ ] **Vietnamese (vi)** — **held (`ready:false`).** Existing strings are AI-drafted and **not** native-verified: the prior reviewer (Nancy) is not a fluent Vietnamese speaker and checked only a few strings, so the G1 bar is not met. A fluent native verifier is reachable and certified translation is fundable; the plan is MT-assisted drafting + mandatory fluent-human verification before the toggle goes live (see [research](research/2026-05-29-vi-anthropic-lens-research.md)). English fallback until then.
- [ ] **Spanish (es)** — source a verified native translator. Large local pool; expected fastest.
- [ ] **Korean (ko)** — source a verified native translator. Smaller pool; start early.

What a translator receives: the English string set (the `STRINGS` table in
`dashboard.html`), with emphasis on the **safety-critical copy** (the address-check
verdicts, the disclaimer, the breaking-alert text). Plain, calm, non-directive
register (we issue no directives — LEGAL R1/R2).

## How the framework adds a language

The i18n layer in `dashboard.html` is registry-driven (`LANGS`). To bring a language live:

1. Add its verified strings under each key in `STRINGS` (e.g. `es: "..."`).
2. Ensure the language has an entry in `LANGS` (code, native label, flag SVG, locale).
3. Flip its `ready` flag to `true`. It now appears in the picker.

Missing keys fall back to English via `t()`, so a language can ship partially
translated (safety-critical first) without exposing blanks or machine output.
