# Language Access

Which languages GG Tank Watch ships, why, and what it takes to add one.

The driving question: **maximize reach to the residents most at risk** — displaced,
elderly, limited-English, low-income. For an emergency tool the right metric is not
raw speaker count but **limited-English proficiency (LEP)**: the people who *cannot*
get the information in English are exactly the people a translation serves.

## Binding constraint (G1) — English-only by design

**The app ships English only.** We do not author, machine-translate, *or surface*
(even via a link framed as our own content) any non-English safety copy without
reliable human verification. A wrong "you're safe" — or a mistranslated evacuation
instruction — is far worse than a missing translation (see
[DISTRIBUTION.md](DISTRIBUTION.md) G1, [LEGAL.md](LEGAL.md)). For a two-person volunteer
conduit without reliable native translators on call, the honest and safe choice is to
**not ship translations at all** and route limited-English residents to the officials
who publish their own verified copy (the city's emergency page carries human-authored
Vietnamese, Spanish, and Korean per-update).

This is the most conservative form of the rule: there is no non-English surface to get
wrong. `test_english_only` enforces it — the build fails if any non-English language
is added to `LANGS`.

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

## Decision — English-only; route LEP residents to officials

Given the demographics above, the residents most at risk are also the most
limited-English (Vietnamese 57% LEP, Spanish 39%). The instinct is to translate the
tool for them. But this is a two-person volunteer conduit, and we do not have reliable
native translators on call for safety-critical copy — so the responsible choice is
**not** to ship our own translations.

Instead the conduit does the one thing it can do safely for LEP residents: route them
to the **official** channel, which already publishes human-authored Vietnamese /
Spanish / Korean for each incident update. We amplify verified official translations;
we never substitute an unverifiable one of our own. The (high) bar to ever add a
language in-app is below — but the default, and the shipped state, is English-only.

## The bar to ever add a language

English-only is the shipped default. A language would be added *only* if all of the
following hold — anything less stays English-only:

- A **fluent native speaker** verifies every safety-critical string (the prior
  Vietnamese attempt failed this bar: the reviewer was not a fluent Vietnamese speaker
  and checked only a few strings), ideally backed by **funded certified translation**.
- The translation is **maintained** for every future incident update, not a one-time
  pass — stale safety copy in another language is its own hazard.
- It clears attorney review alongside the rest of the pre-launch gate.

Until all three hold, the conduit routes non-English residents to officials (above).

What a translator receives: the English string set (the `STRINGS` table in
`dashboard.html`), with emphasis on the **safety-critical copy** (the address-check
verdicts, the disclaimer, the breaking-alert text). Plain, calm, non-directive
register (we issue no directives — LEGAL R1/R2).

## How the framework adds a language

The i18n layer in `dashboard.html` is registry-driven (`LANGS`). To bring a language live:

1. Add its verified strings under each key in `STRINGS` (e.g. `es: "..."`).
2. Ensure the language has an entry in `LANGS` (code, native label, flag SVG, locale).
3. Flip its `ready` flag to `true`. The language would then appear in the picker. (Today the app is English-only by design: only English is `ready`, so no picker renders.)

Missing keys fall back to English via `t()`, so a language can ship partially
translated (safety-critical first) without exposing blanks or machine output.
