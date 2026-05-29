# LEGAL.md Conduit Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconcile `docs/LEGAL.md` (compiled 2026‑05‑24, pre-conduit-pivot) with the shipped conduit product and the 2026‑05‑27 deep-research legal memo, so it describes the current dashboard, re-rates the headline risk down (the address checker that drove it was removed), and folds in the memo's strongest additions — keeping one canonical, current legal doc.

**Architecture:** Two commits on a docs branch. C1 relocates the untracked legal-research folder into `docs/legal-research/2026-05-27/` (a cited dated artifact). C2 edits `docs/LEGAL.md` across 9 sections via exact-string replacements. No code, no behavior change. Verify with grep sweeps (no residual removed-feature terms), an anchor/link check, and the unchanged eval. Branch → PR (docs-only, same shape as PR #48).

**Tech Stack:** Markdown only. Verification: `grep`, `python eval/run_all.py --skip integration` (must stay 45/45), `gh`.

**Load-bearing judgment (already approved by the user):** keep BOTH liability framings — LEGAL.md's §324A "negligent undertaking" and the memo's §552 "negligent misrepresentation / pecuniary-interest shield" — as complementary defenses, but re-rate the headline risk **R1 from HIGH → LOW/MEDIUM** because the conduit pivot removed the functional "safe/unsafe" output. Every rating stays flagged "research, not legal advice; confirm with counsel"; `noindex`/attorney-review-before-public-launch posture is unchanged.

---

## File Structure

- **Create:** `docs/legal-research/2026-05-27/` — relocated raw memo + data artifacts (`legal_risk_memo.md`, `claims.jsonl`, `evidence.jsonl`, `sources.jsonl`, `run_manifest.json`).
- **Delete (move source):** root `GG_Tank_Legal_Research_Acceptance_Test_20260527/` (untracked; relocated, not committed at root).
- **Modify:** `docs/LEGAL.md` — header/description, bottom-line, Finding 1, Finding 5, Finding 6, Finding 8, risk matrix, DRAFT disclaimer, minimum-bar checklist, bibliography/methodology.
- **Do NOT touch:** `dashboard.html`, `terms.html`, `docs/DISTRIBUTION.md` (DISTRIBUTION.md is a separate flagged follow-up — out of scope here), any code.

---

### Task 1: Relocate the legal-research folder into the repo

**Files:**
- Create dir: `docs/legal-research/2026-05-27/`
- Move: `GG_Tank_Legal_Research_Acceptance_Test_20260527/{legal_risk_memo.md,claims.jsonl,evidence.jsonl,sources.jsonl,run_manifest.json}` → `docs/legal-research/2026-05-27/`

- [ ] **Step 1: Confirm clean branch off main**

Run:
```bash
git branch --show-current && git status --short
```
Expected: on `main` (or create branch next), tree clean except the untracked legal folder + plan doc.

- [ ] **Step 2: Create the docs branch**

```bash
git checkout -b docs/legal-md-conduit-reconcile
```

- [ ] **Step 3: Move the five files into the repo**

```bash
mkdir -p docs/legal-research/2026-05-27
git mv "GG_Tank_Legal_Research_Acceptance_Test_20260527/legal_risk_memo.md" docs/legal-research/2026-05-27/ 2>/dev/null || mv "GG_Tank_Legal_Research_Acceptance_Test_20260527/legal_risk_memo.md" docs/legal-research/2026-05-27/
for f in claims.jsonl evidence.jsonl sources.jsonl run_manifest.json; do
  mv "GG_Tank_Legal_Research_Acceptance_Test_20260527/$f" docs/legal-research/2026-05-27/ 2>/dev/null || true
done
rmdir "GG_Tank_Legal_Research_Acceptance_Test_20260527" 2>/dev/null || true
ls docs/legal-research/2026-05-27/
```
Expected: 5 files listed; root folder gone.

- [ ] **Step 4: Add a short README in the relocated folder**

Create `docs/legal-research/2026-05-27/README.md`:
```markdown
# Legal research run — 2026-05-27 (deep-research legal mode)

Raw artifacts from a deep-research legal-mode run on the question:
"What are my legal constraints as the builder of a civic crisis information
dashboard that aggregates evacuation perimeters, wind direction, news updates,
and shelter info in California?"

- `legal_risk_memo.md` — the synthesized risk memo (the human-readable output).
- `claims.jsonl` / `evidence.jsonl` / `sources.jsonl` — claim-level provenance.
- `run_manifest.json` — run metadata (note: `report_dir` records the original
  generation path, not this location).

This is **legal research, not legal advice.** Its findings are folded into
[`../../LEGAL.md`](../../LEGAL.md), which is the canonical project legal doc.
```

- [ ] **Step 5: Commit C1**

```bash
git add docs/legal-research/2026-05-27/ docs/superpowers/plans/2026-05-29-legal-md-conduit-reconciliation.md
git commit -q -m "docs(legal): vendor 2026-05-27 legal research memo + plan

Relocate the deep-research legal-mode run from the untracked repo-root
folder into docs/legal-research/2026-05-27/ as a cited dated artifact,
with a README pointing back to LEGAL.md. Its findings are reconciled
into LEGAL.md in the next commit."
git log --oneline -1
```

---

### Task 2: Header / project description → conduit product

**Files:**
- Modify: `docs/LEGAL.md` (project description block, currently ~L17-27)

- [ ] **Step 1: Replace the description + compiled line**

Replace this exact block:
```
**Project:** Free, unofficial, volunteer-built static web dashboard for the Garden
Grove, CA methyl-methacrylate (MMA) chemical-tank incident (GKN Aerospace, 12122
Western Ave; began 2026-05-21). Shows a Leaflet map (evac zone + blast/plume
estimates), a client-side "check your address" risk tool (OpenStreetMap Nominatim
geocoding), and aggregated news/video/official statements from a `status.json` feed.
Two private volunteers operate it; no money is charged. Currently `noindex` and not
yet distributed.

**Jurisdiction focus:** U.S. federal + California. **Compiled:** 2026-05-24.
```
with:
```
**Project:** Free, unofficial, volunteer-built static web dashboard for the Garden
Grove, CA methyl-methacrylate (MMA) chemical-tank incident (GKN Aerospace, 12122
Western Ave; began 2026-05-21). Shows a MapLibre GL map on OpenFreeMap vector tiles
(evacuation zone, the GKN facility, shelter locations, live NWS wind direction) and
aggregated news/video/official statements from a `status.json` feed. It authors **no
hazard verdicts** — it routes users to official sources (a pure information
*conduit*). Two private volunteers operate it; no money is charged. Currently
`noindex` and not yet distributed.

> **2026-05-26 conduit pivot.** An earlier version had a client-side "check your
> address" risk tool (OpenStreetMap Nominatim geocoding → SAFE/ELEVATED/HIGH/CRITICAL
> verdict) and blast-radius/plume map layers. Both were **deliberately removed** to
> keep the dashboard a pure conduit. This materially lowers the headline liability
> (see [Finding 1](#1--liability-for-inaccurate-or-stale-safety-information) / R1).
> Findings below have been reconciled to the conduit product.

**Jurisdiction focus:** U.S. federal + California. **Compiled:** 2026-05-24.
**Reconciled to the conduit product + the 2026-05-27 legal memo
([`legal-research/2026-05-27/`](legal-research/2026-05-27/)):** 2026-05-29.
```

- [ ] **Step 2: Verify**

Run: `grep -n "pure information" docs/LEGAL.md`
Expected: one match in the description block.

---

### Task 3: Bottom line up front — re-rate #1, rewrite #6

**Files:**
- Modify: `docs/LEGAL.md` (bottom-line list items 1 and 6)

- [ ] **Step 1: Replace bullet #1**

Replace this exact text:
```
1. **The biggest real risk is negligent-undertaking liability for physical harm** if
   a user relies on inaccurate or stale "safe/unsafe" output — especially the
   "check your address" tool, which is the feature most likely to be treated as a
   functional product rather than protected speech. [1][2][3][9]
```
with:
```
1. **The biggest residual risk is negligent-undertaking / negligent-misrepresentation
   liability for physical harm** if a user relies on inaccurate or stale information.
   This dropped materially with the conduit pivot: the "check your address" tool — the
   feature most likely to be treated as functional product rather than protected
   speech — was removed, and the dashboard now authors no "safe/unsafe" output. As a
   pure conduit republishing official data it sits closer to protected-speech /
   intermediary territory, reinforced by two independent shields: **no pecuniary
   interest** (Restatement §552 negligent-misrepresentation liability generally does
   not attach to a free, non-commercial provider) and the *Brandt v. The Weather
   Channel* line (no liability for republished forecasts/official data absent actual
   negligence). [1][2][3][9][53][54]
```

- [ ] **Step 2: Replace bullet #6**

Replace this exact text:
```
6. **The two operational compliance items that can break the site are the OSM
   Nominatim and tile usage policies** — Nominatim bans autocomplete and caps at
   1 request/second site-wide, with IP-ban consequences. This is a "fix before
   distribution" item. [36][37]
```
with:
```
6. **The operational-compliance picture simplified with the conduit pivot.** Nominatim
   geocoding was removed with the address tool, eliminating the highest-risk
   service-terms item (the 1 req/s site-wide cap + autocomplete ban). The map now uses
   self-hosted MapLibre GL on OpenFreeMap vector tiles — keep OpenFreeMap/OSM
   attribution visible. The remaining service-terms watch item is Microlink
   link-previews (50/day shared free quota → cache or pre-render). [41][55]
```

- [ ] **Step 3: Verify**

Run: `grep -n "Brandt v. The Weather Channel\|pecuniary interest\|OpenFreeMap vector tiles" docs/LEGAL.md`
Expected: matches in the bottom-line section.

---

### Task 4: Finding 1 — re-weight §324A, add §552 shield + Brandt + conduit note

**Files:**
- Modify: `docs/LEGAL.md` (Finding 1; the "First Amendment caveat for the 'check your address' tool" paragraph + insert a new paragraph)

- [ ] **Step 1: Replace the First Amendment caveat paragraph (now moot — tool removed)**

Replace this exact text:
```
**First Amendment caveat for the "check your address" tool.** *Winter* protects
general expression but carved out highly technical data "used directly in dangerous
activities" (its aeronautical-charts line); *Brandenburg v. Ohio*, 395 U.S. 444
(1969) protects speech short of inciting imminent lawless action. [9][10] An
interactive tool that outputs a specific safe/unsafe determination is the feature most
at risk of being characterized as chart-like functional output rather than protected
speech. **⚑ Partially verified** — how a court would classify an interactive risk tool
is fact-specific and untested.
```
with:
```
**Conduit pivot removed the highest-exposure feature.** *Winter* protects general
expression but carved out highly technical data "used directly in dangerous
activities" (its aeronautical-charts line). [9][10] An interactive tool that outputs a
specific safe/unsafe determination was the feature most at risk of being characterized
as chart-like functional output rather than protected speech — and that "check your
address" tool was **removed in the 2026-05-26 conduit pivot.** The dashboard now
displays only official-sourced facts (evac zone, wind, shelters) and routes to
authorities; it authors no determination for a user to rely on. This moves the tool
from the functional-product zone back toward protected informational speech, and the
§324A(c) reliance prong now has no authored verdict to attach to. **⚑ Partially
verified** — no retrieved holding classifies a conduit dashboard; the inference is
doctrinally sound but untested.

**Independent shield: Restatement §552 pecuniary-interest requirement.** Negligent
misrepresentation under Restatement (Second) of Torts §552 requires that the
information be supplied "in the course of [a] business, profession or employment, or
in any other transaction in which [the supplier] has a **pecuniary interest**." [54]
A free, non-commercial, volunteer dashboard with no subscriptions or ads has no
pecuniary interest, so §552 liability almost certainly does not attach. The 2026-05-27
conduit memo treats this as the strongest single defense against a misrepresentation
claim. **Residual:** monetizing later (ads, subscriptions, even a creative
"portfolio-drives-employment" theory) would change this analysis — re-assess before
adding revenue. [50][54]

**Conduit/forecaster analogy reinforces the baseline.** Courts are extremely reluctant
to impose liability for republished predictions. In *Brandt v. The Weather Channel* a
broadcaster was not liable when a viewer drowned during an unexpected storm; courts
require proof of actual negligence in preparing information, not merely that it proved
incorrect. [53] A dashboard republishing government evacuation/weather data is an
analogous conduit, not the original source.
```

- [ ] **Step 2: Verify**

Run: `grep -n "pecuniary-interest requirement\|conduit pivot removed the highest" docs/LEGAL.md`
Expected: matches in Finding 1.

---

### Task 5: Finding 5 — add the §230 passive-vs-active track

**Files:**
- Modify: `docs/LEGAL.md` (Finding 5; insert after the existing "Defamation: §230 protects the conduit, not your own words" paragraph)

- [ ] **Step 1: Insert a new paragraph immediately after this existing sentence**

Find this exact existing text (end of the §230 paragraph):
```
**A pure automated feed of third-party links is squarely within § 230; the team's
OWN editorial summaries, captions, and the risk tool's conclusions are NOT — write
those carefully and factually.**
```
Replace it with (original sentence kept, new paragraph appended):
```
**A pure automated feed of third-party links is squarely within § 230; the team's
OWN editorial summaries and captions are NOT — write those carefully and factually.**
(The "risk tool's conclusions," previously the clearest example of the team's own
content, no longer exist after the conduit pivot — see [Finding 1](#1--liability-for-inaccurate-or-stale-safety-information).)

**Aggregator vs. information-content-provider (the §230 line).** The 2026-05-27 memo
maps the controlling circuit law: *Force v. Facebook*, 934 F.3d 53 (2d Cir. 2019) held
algorithmic curation of third-party content does not strip §230 immunity ("arranging
and distributing third-party information … is an essential result of publishing");
*Fair Housing Council v. Roommates.com* (9th Cir. 2008) loses immunity only when a
platform "materially contributes to the illegality" of content; *Anderson v. TikTok*
(3d Cir. 2024) is an outlier circuit split on personalized algorithmic recommendation.
A dashboard that categorizes official data (evacuation, weather, shelters) without
personalized algorithmic curation performs far less editorial function than Facebook —
and Facebook kept its immunity. The conduit posture (passive aggregation, no authored
analysis) sits firmly on the protected side of this line. [50][51]
```

- [ ] **Step 2: Verify**

Run: `grep -n "Force v. Facebook\|materially contributes" docs/LEGAL.md`
Expected: matches in Finding 5.

---

### Task 6: Finding 6 — remove Nominatim + Leaflet/OSM-tile, add OpenFreeMap/MapLibre

**Files:**
- Modify: `docs/LEGAL.md` (Finding 6: replace the OSM-tiles, Nominatim, and Leaflet blocks; keep YouTube + Microlink + ODbL)

- [ ] **Step 1: Replace the OSM raster-tiles block**

Replace this exact block:
```
**OpenStreetMap raster tiles — `tile.openstreetmap.org` [36] (HIGH attention).** The
OSMF Tile Usage Policy requires:
- **Attribution:** show "© OpenStreetMap contributors" visibly; do "not hide
  attribution beneath UI, behind toggles, or off-screen."
- **No bulk download:** "Bulk downloading is any pre-emptive fetching of tiles other
  than those a user is actively viewing" — prohibited; "Offline use is not permitted."
- **User-Agent:** "Send a clear, unique User-Agent string that names your app";
  generic SDK defaults "will be blocked."
- **Caching:** honor cache headers, or "cache each tile for at least 7 days."
- The policy warns "access may be withdrawn at any point." A low-traffic civic tool
  using normal interactive panning is within policy *if* attribution + a descriptive
  User-Agent are present — but for resilience, a keyed third-party tile CDN or
  self-hosting (switch2osm.org) is the safer production choice.
```
with:
```
**Map tiles — OpenFreeMap vector tiles via self-hosted MapLibre GL [55].** The conduit
pivot replaced Leaflet + `tile.openstreetmap.org` raster tiles with **MapLibre GL**
(self-hosted in `/lib`, BSD-2) rendering **OpenFreeMap** vector tiles. This removed the
OSMF raster-tile-policy exposure (the prior 7-day-cache / no-bulk-download / named
User-Agent obligations and the "access may be withdrawn at any point" warning).
OpenFreeMap is free for any use and asks only that you keep attribution visible; the
underlying data is still OpenStreetMap, so the ODbL "© OpenStreetMap contributors"
credit applies (see below). Self-hosting the renderer also removes the CDN
single-point-of-failure that previously broke the map on refresh. **Action:** keep the
OpenFreeMap/OSM attribution control visible and unobscured.
```

- [ ] **Step 2: Replace the Nominatim block (feature removed)**

Replace this exact block:
```
**Nominatim geocoding — `nominatim.openstreetmap.org` [37] (HIGHEST-RISK ITEM).**
Verbatim hard limits:
- "an absolute **maximum of 1 request per second**" — **this cap is site-wide across
  all your users combined, not per-user.**
- Provide "a valid HTTP Referer or User-Agent identifying the application."
- "Results **must be cached** on your side"; repeated identical queries "may be
  classified as faulty and blocked."
- **Unacceptable Use (outright bans):** "Auto-complete search"; "Systematic queries";
  "Scraping"; "Reselling." Such uses "will get you **banned**."

**Action:** verify the address input is **submit-on-enter, not keystroke/debounced
autocomplete** (autocomplete is an instant-ban trigger), set a descriptive
User-Agent/Referer, and cache results. For any real distribution volume, move to a
keyed third-party geocoder or self-hosted Nominatim to remove the ban risk entirely.
```
with:
```
**Nominatim geocoding — REMOVED (was `nominatim.openstreetmap.org`, the prior
HIGHEST-RISK item).** The "check your address" tool that called Nominatim was deleted
in the 2026-05-26 conduit pivot, so the OSMF Nominatim Usage Policy no longer applies:
the 1 req/s site-wide cap, the mandatory result caching, and the autocomplete /
systematic-query / scraping ban (an instant-ban trigger) are all moot. *If any
address-lookup feature is ever reintroduced, this section's limits become binding again
— see the prior revision history.* [37]
```

- [ ] **Step 3: Replace the Leaflet block**

Replace this exact block:
```
**Leaflet — BSD-2-Clause [38].** Keep the bundled copyright/LICENSE header (don't
strip it from minified bundles). Leaflet renders OSM's attribution via its built-in
attribution control — **do not remove that control**, which also discharges the tile
and ODbL attribution duties.
```
with:
```
**MapLibre GL — BSD-2-Clause [55].** The self-hosted MapLibre GL build in `/lib` keeps
its license header. MapLibre renders the OpenFreeMap/OSM attribution via its built-in
attribution control — **do not remove or hide that control**, which discharges the
vector-tile and ODbL attribution duties. (Leaflet, the prior renderer, is no longer
used.)
```

- [ ] **Step 4: Verify**

Run: `grep -niE "nominatim|leaflet|tile.openstreetmap.org" docs/LEGAL.md`
Expected: only the historical/"REMOVED" mentions in Finding 6 and (later) the bibliography line for [37]/[38] — no live-obligation language.

---

### Task 7: Finding 8 — privacy: drop moot geocoding note, add CCPA/AB 1355 watch

**Files:**
- Modify: `docs/LEGAL.md` (Finding 8: the "Today's client-side geocoding note" paragraph)

- [ ] **Step 1: Replace the client-side geocoding note**

Replace this exact text:
```
**Today's client-side geocoding note.** A user-typed address is sent from the browser
directly to OSMF/Nominatim and is not stored by the operators. Worth a one-line
privacy notice: *"Addresses you type are sent to OpenStreetMap's Nominatim service to
locate them and are not stored by us."* (This is analysis of the described
architecture, not a fetched source.)
```
with:
```
**No client-side geocoding today.** The conduit pivot removed the address tool, so the
dashboard no longer sends user-typed addresses to any geocoder. There is no per-user
location input to disclose. **Forward-looking (CCPA/CPRA + AB 1355):** if a
location-aware feature (proximity alerts, location filtering) is ever added, precise
geolocation is **Sensitive Personal Information** under CPRA, and California's proposed
Location Privacy Act (AB 1355, introduced Feb 2025) would require opt-in consent with
penalties up to $25,000/violation. Process any future geolocation **client-side only**,
never stored server-side. [50][20]
```

- [ ] **Step 2: Verify**

Run: `grep -n "No client-side geocoding today\|AB 1355" docs/LEGAL.md`
Expected: matches in Finding 8.

---

### Task 8: Risk matrix — re-rate R1/R2, remove R7, replace R8

**Files:**
- Modify: `docs/LEGAL.md` (risk matrix rows R1, R2, R7, R8)

- [ ] **Step 1: Replace the R1 and R2 rows**

Replace these exact rows:
```
| R1 | **Negligent-undertaking / physical-harm claim** from reliance on wrong "check your address" or stale evac output | Low–Med | **High** | The headline exposure | "Informational only / verify with official sources / call 911" on-page near the tool; show data timestamp + staleness warning; frame all output as *estimates*; never output bare "safe/unsafe"; attorney review of the tool's wording [1][2][3][9] |
| R2 | **Negligent misrepresentation** from a specific false factual assertion ("your address is safe") | Low | **High** | Tied to R1 | Avoid "safe"/"official"; hedge every determination; disclaim [1][3][4] |
```
with:
```
| R1 | **Negligent-undertaking / physical-harm claim** from reliance on stale evac/wind display | Low | **Low–Med** | Dropped after conduit pivot removed the address tool (was the headline exposure) | "Informational only / verify with official sources / call 911" on-page; data timestamp + staleness warning; frame as *estimates*; **no authored verdicts** (conduit); §552 no-pecuniary-interest shield [1][2][3][9][53][54] |
| R2 | **Negligent misrepresentation** from a specific false factual assertion | Low | Low–Med | Largely moot — the "your address is safe" output was removed; reinforced by §552 pecuniary-interest shield (no revenue) | Avoid "safe"/"official"; hedge; disclaim; stay non-commercial [1][3][4][54] |
```

- [ ] **Step 2: Replace the R7 row (Nominatim removed)**

Replace this exact row:
```
| R7 | **Nominatim ban / throttle** (autocomplete, >1 req/s, no caching) | **Med–High** | Med | Breaks the address tool | Submit-on-enter only; descriptive User-Agent/Referer; cache; keyed/self-hosted geocoder for volume [37] |
```
with:
```
| R7 | **Nominatim ban / throttle** — N/A | — | — | Removed with the address tool (conduit pivot); re-applies only if address lookup is reintroduced | n/a [37] |
```

- [ ] **Step 3: Replace the R8 row (OpenFreeMap, not OSM raster)**

Replace this exact row:
```
| R8 | **OSM tile throttle / attribution lapse** | Low–Med | Low–Med | Map breaks | Keep "© OpenStreetMap contributors" visible; named User-Agent; consider tile CDN [36][42] |
```
with:
```
| R8 | **Map-tile attribution lapse** (OpenFreeMap vector tiles + self-hosted MapLibre) | Low | Low | Self-hosting removed the OSM raster-tile throttle risk | Keep OpenFreeMap/"© OpenStreetMap contributors" attribution control visible [42][55] |
```

- [ ] **Step 4: Verify**

Run: `grep -n "Dropped after conduit pivot\|Nominatim ban / throttle — N/A\|OpenFreeMap vector tiles + self-hosted" docs/LEGAL.md`
Expected: three matches.

---

### Task 9: DRAFT disclaimer/ToU + Minimum-bar checklist

**Files:**
- Modify: `docs/LEGAL.md` (banner block; ToU §2; ToU §8; attribution footer §C; checklist blocker bullets)

- [ ] **Step 1: Banner block — remove "address results"**

Replace this exact text:
```
> **Informational only — not official emergency guidance.** This is an independent,
> volunteer-run website. The map, zones, and address results are **estimates**, may be
> **out of date or wrong**, and are **not** a substitute for official guidance. Always
> verify with the **Orange County Fire Authority** and the **City of Garden Grove**
> (ggcity.org/emergency). **If you are in danger, call 911.**
```
with:
```
> **Informational only — not official emergency guidance.** This is an independent,
> volunteer-run website. The map and information shown are **estimates compiled from
> official and news sources**, may be **out of date or wrong**, and are **not** a
> substitute for official guidance. Always verify with the **Orange County Fire
> Authority** and the **City of Garden Grove** (ggcity.org/emergency). **If you are in
> danger, call 911.**
```

- [ ] **Step 2: ToU §2 — remove blast/plume/address-tool enumeration**

Replace this exact text:
```
> **2. Informational only.** All content — including the map, evacuation zone, blast
> and plume estimates, and the "check your address" tool — is provided for **general
> informational purposes only** and is **not** a substitute for official emergency
> guidance, professional advice, or your own judgment. The estimates are not
> authoritative and may be inaccurate, incomplete, or outdated.
```
with:
```
> **2. Informational only.** All content — including the map, the evacuation zone, and
> the aggregated news, video, and official statements — is provided for **general
> informational purposes only** and is **not** a substitute for official emergency
> guidance, professional advice, or your own judgment. It is compiled from official and
> news sources, is not authoritative, and may be inaccurate, incomplete, or outdated.
```

- [ ] **Step 3: ToU §8 — remove Nominatim geocoding sentence**

Replace this exact text:
```
> **8. Privacy.** We do not store the addresses you type. When you use the address
> tool, the address is sent to OpenStreetMap's Nominatim service to locate it. *(Update
> this if any data is ever collected or stored.)*
```
with:
```
> **8. Privacy.** We do not collect or store personal information. The dashboard has no
> login, no accounts, and no address-lookup feature. *(Update this if any data is ever
> collected or stored.)*
```

- [ ] **Step 4: Attribution footer §C — Leaflet/Nominatim → MapLibre/OpenFreeMap**

Replace this exact text:
```
> Map © OpenStreetMap contributors. Geocoding by OpenStreetMap Nominatim. *(Keep
> Leaflet's built-in attribution control enabled — it renders this automatically.)* [36][38][42]
```
with:
```
> Map © OpenStreetMap contributors, tiles by OpenFreeMap. *(Keep MapLibre GL's built-in
> attribution control enabled — it renders this automatically.)* [42][55]
```

- [ ] **Step 5: Minimum-bar checklist — fix the two address-tool/Nominatim blockers**

Replace this exact bullet:
```
- [ ] 🔴 **Attorney review** of (a) this document's load-bearing findings and (b) the
      final disclaimer/ToU and the "check your address" tool's exact output wording. [1][16]
```
with:
```
- [ ] 🔴 **Attorney review** of (a) this document's load-bearing findings and (b) the
      final disclaimer/ToU wording. [1][16]
```

Replace this exact bullet:
```
- [ ] 🔴 **No "official" or "safe" language; no government seals/insignia** anywhere in
      UI, logo, or favicon. [7][34]
```
with:
```
- [ ] 🔴 **No authored verdicts; no "official" or "safe" language; no government
      seals/insignia** anywhere in UI, logo, or favicon (conduit posture). [7][34]
```

Replace this exact bullet (Nominatim blocker → done/N-A):
```
- [ ] 🔴 **Nominatim compliance:** confirm submit-on-enter (no autocomplete), set a
      descriptive User-Agent/Referer, cache results, keep aggregate <1 req/s — or switch
      to a keyed/self-hosted geocoder before wide distribution. [37]
```
with:
```
- [x] ✅ **Geocoder compliance — N/A.** The Nominatim address tool was removed in the
      conduit pivot; no geocoding obligations remain. [37]
```

Replace this exact bullet (OSM attribution → OpenFreeMap):
```
- [ ] 🟡 **OSM attribution** ("© OpenStreetMap contributors") visible (Leaflet control on). [36][42]
```
with:
```
- [ ] 🟡 **Map attribution** ("© OpenStreetMap contributors", tiles by OpenFreeMap)
      visible (MapLibre control on). [42][55]
```

- [ ] **Step 6: Cross-check against the live ToU**

Run: `grep -niE "blast|plume|check your address|nominatim|geocod" terms.html`
Expected: ideally no matches. If `terms.html` still references removed features, note it in the PR body as a follow-up (do NOT edit terms.html in this plan — it is the live ToU and out of scope here).

- [ ] **Step 7: Verify disclaimer/checklist edits**

Run: `grep -niE "address results|check your address|blast and plume|Geocoding by OpenStreetMap Nominatim" docs/LEGAL.md`
Expected: no matches (all removed).

---

### Task 10: Bibliography + methodology

**Files:**
- Modify: `docs/LEGAL.md` (methodology note + bibliography additions)

- [ ] **Step 1: Append a reconciliation note to the Methodology section**

Find this exact existing sentence (end of the "Confidence is lower" paragraph):
```
DMLP guides cited for California defamation are not maintained past 2014/2016.
```
Replace with (original kept, note appended):
```
DMLP guides cited for California defamation are not maintained past 2014/2016.

**2026-05-29 reconciliation.** This document was updated to match the shipped conduit
product (address checker, blast/plume layers, Leaflet, and Nominatim removed) and to
fold in the 2026-05-27 deep-research legal memo
([`legal-research/2026-05-27/legal_risk_memo.md`](legal-research/2026-05-27/legal_risk_memo.md)).
The memo's distinctive contributions — the §552 pecuniary-interest shield, the §230
aggregator/ICP line (*Force v. Facebook*), the *Brandt* forecaster analogy, and the
CCPA/AB 1355 location-privacy watch — are cited inline as [50]–[55]. The two docs use
different primary framings (§324A negligent-undertaking here; §552 negligent
misrepresentation in the memo); both are retained as complementary defenses.
```

- [ ] **Step 2: Append new bibliography entries**

Find this exact existing last bibliography line:
```
49. FTC — COPPA Rule, 16 CFR Part 312 (verifiable parental consent) ⚑. (P, .gov) — https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa · https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-312
```
Append immediately after it:
```

**Conduit reconciliation additions (2026-05-29)**
50. 2026-05-27 deep-research legal memo (internal). [`docs/legal-research/2026-05-27/legal_risk_memo.md`](legal-research/2026-05-27/legal_risk_memo.md) — conduit-mode risk memo; sources tracked in the sibling `claims.jsonl`/`evidence.jsonl`/`sources.jsonl`.
51. Force v. Facebook, 934 F.3d 53 (2d Cir. 2019). (P, case) — algorithmic curation protected under §230. https://law.justia.com/cases/federal/appellate-courts/F3/934/53/
52. Bartnicki v. Vopper, 532 U.S. 514 (2001). (P, case) — First Amendment protects publishing truthful information on matters of public concern. https://supreme.justia.com/cases/federal/us/532/514/
53. Brandt v. The Weather Channel. (S, case) — no liability for incorrect forecasts absent actual negligence (cited in memo [15]).
54. Restatement (Second) of Torts § 552 (1977). (S, Restatement) — negligent misrepresentation; pecuniary-interest requirement. https://www.columbia.edu/~mr2651/ecommerce3/2nd/statutes/RestatementTorts.pdf
55. OpenFreeMap (https://openfreemap.org/) + MapLibre GL JS (BSD-2-Clause, https://maplibre.org/). (P, project/license) — vector tiles + self-hosted renderer replacing OSM raster tiles + Leaflet.
```

- [ ] **Step 3: Verify**

Run: `grep -n "^50\.\|^55\.\|2026-05-29 reconciliation" docs/LEGAL.md`
Expected: the new bib entries + the reconciliation note.

---

### Task 11: Full verification + commit C2

**Files:**
- Verify + commit: `docs/LEGAL.md`

- [ ] **Step 1: Residual stale-term sweep**

Run:
```bash
grep -niE "check your address|blast[- ]?radius|blast and plume|plume cone|plume estimates|nominatim geocoding|client-side .check|Leaflet's built-in|address results" docs/LEGAL.md
```
Expected: **no matches** (all converted to historical/"removed" framing or deleted). Any live-obligation or current-feature phrasing left is a miss — fix it before committing.

- [ ] **Step 2: Anchor + link integrity**

Run:
```bash
grep -nE "^#|^## |^\| [0-9]" docs/LEGAL.md | head -40
grep -n "legal-research/2026-05-27" docs/LEGAL.md
```
Expected: the TOC anchors still resolve (section headings unchanged), and the relative memo link path appears (resolves from `docs/` to `docs/legal-research/2026-05-27/`).

- [ ] **Step 3: Eval unchanged**

Run: `python eval/run_all.py --skip integration 2>&1 | tail -4`
Expected: `TOTAL 45/45` (this change touches no code; the eval must be unaffected).

- [ ] **Step 4: Commit C2**

```bash
git add docs/LEGAL.md
git commit -q -m "docs(legal): reconcile LEGAL.md with conduit product + 2026-05-27 memo

LEGAL.md predated the conduit pivot and analyzed removed features
(address checker, blast/plume, Leaflet, Nominatim). Reconcile it:
- describe the shipped conduit (MapLibre/OpenFreeMap, no authored verdicts)
- re-rate the headline risk R1 HIGH -> LOW/MEDIUM (the address tool that
  drove it was removed); R2 likewise; R7 (Nominatim) -> N/A; R8 -> OpenFreeMap
- add the memo's strongest defenses: Restatement 552 pecuniary-interest
  shield, the 230 aggregator/ICP line (Force v. Facebook), the Brandt
  forecaster analogy, and the CCPA/AB 1355 location-privacy watch
- fix the DRAFT disclaimer/ToU + pre-distribution checklist + bibliography
- keep both liability framings (324A undertaking / 552 misrepresentation)
  as complementary; all ratings stay 'research, not legal advice'

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
git log --oneline -3
```

---

### Task 12: Push + PR

**Files:** none (git/gh)

- [ ] **Step 1: Merge base + push**

```bash
git fetch origin main && git merge origin/main --no-edit 2>&1 | tail -3
git push -u origin docs/legal-md-conduit-reconcile 2>&1 | tail -4
```
(If `eval/scores.jsonl` blocks the merge as in PR #48, `git stash push -- eval/scores.jsonl`, merge, then `git stash drop`.)

- [ ] **Step 2: Create the PR**

```bash
gh pr create --base main --title "docs(legal): reconcile LEGAL.md with conduit product + 2026-05-27 memo" --body "$(cat <<'EOF'
## Summary
Reconciles docs/LEGAL.md (compiled 2026-05-24, pre-conduit-pivot) with the shipped conduit product and the 2026-05-27 deep-research legal memo (now vendored at docs/legal-research/2026-05-27/).

Key change: re-rates the headline liability **R1 from HIGH -> LOW/MEDIUM** because the conduit pivot removed the "check your address" tool that drove the high rating. Adds the memo's strongest defenses (Restatement 552 pecuniary-interest shield, the 230 aggregator/ICP line via Force v. Facebook, the Brandt forecaster analogy, CCPA/AB 1355 watch). Removes obsolete Nominatim/Leaflet/OSM-raster-tile obligations; updates the DRAFT disclaimer, pre-distribution checklist, and bibliography.

Both liability framings (324A undertaking / 552 misrepresentation) are retained as complementary defenses. All ratings stay flagged "research, not legal advice; confirm with counsel." noindex / attorney-review-before-public-launch posture is unchanged.

## Verification
- No residual removed-feature terms in LEGAL.md (grep sweep).
- TOC anchors intact; memo link resolves.
- eval 45/45 (no code touched).

## Notes
- Docs-only; no dashboard behavior change (chore/docs precedent, like #48). No version bump / no CHANGELOG.
- Follow-up flagged: terms.html and docs/DISTRIBUTION.md may carry similar removed-feature drift (out of scope here).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" 2>&1 | tail -3
```

- [ ] **Step 3: Confirm PR diff is docs-only**

Run: `gh pr view --json files -q '.files[].path'`
Expected: `docs/LEGAL.md`, `docs/legal-research/2026-05-27/*`, `docs/superpowers/plans/2026-05-29-...md` — no code files.

---

## Self-Review

**1. Spec coverage** (against the approved 8-section scope):
- Header/description → Task 2 ✓
- Bottom-line re-rate → Task 3 ✓
- Finding 1 (§324A re-weight + §552 + Brandt) → Task 4 ✓
- Finding 5 (§230 passive/active) → Task 5 ✓
- Finding 6 (Nominatim/Leaflet → OpenFreeMap/MapLibre) → Task 6 ✓
- Finding 8 (privacy) → Task 7 ✓
- Risk matrix (R1/R2/R7/R8) → Task 8 ✓
- Disclaimer + checklist → Task 9 ✓
- Bibliography/methodology → Task 10 ✓
- Memo placement → Task 1 ✓

**2. Placeholder scan:** every edit step contains the exact old + new prose. No "TBD"/"add appropriate"/"similar to". ✓

**3. Type/reference consistency:** new citations [50]–[55] are defined in Task 10's bibliography and referenced in Tasks 3, 4, 5, 6, 7, 8. Bullet R7/R8 references match the bibliography ([37], [42], [55]). The relative link `legal-research/2026-05-27/` is used consistently (it resolves from within `docs/`). ✓

**Known residual decisions deferred to counsel (unchanged):** entity formation, error-report channel, the ⚑ partially-verified items — all retained as open questions.
