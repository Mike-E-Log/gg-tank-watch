# Legal & Liability Research — gg-tank-dashboard ("ggtankwatch")

> ## ⚠️ THIS IS RESEARCH, NOT LEGAL ADVICE
>
> This document is a good-faith research summary compiled by a volunteer to map the
> legal and liability landscape **before** distributing this tool. It is **not legal
> advice**, it does not create an attorney–client relationship, and it may be
> incomplete or wrong. Law changes and turns on facts this document does not know.
>
> **Consult a licensed California attorney before any public distribution** —
> ideally one with experience in tort/liability, media/First Amendment, or
> nonprofit law. Several findings below are explicitly flagged as *partially
> verified*; treat those as starting points for a lawyer, not conclusions.

---

**Project:** Free, unofficial, volunteer-built static web dashboard for the Garden
Grove, CA methyl-methacrylate (MMA) chemical-tank incident (GKN Aerospace, 12122
Western Ave; began 2026-05-21). Shows a MapLibre GL map on OpenFreeMap vector tiles
(evacuation zone, the GKN facility, shelter locations) and
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
**Method:** multi-source web research with claim-level source tracking; see
[Methodology](#methodology--source-confidence) and [Bibliography](#bibliography).

---

## Table of contents

- [How to read this](#how-to-read-this)
- [Bottom line up front](#bottom-line-up-front)
- Findings:
  1. [Liability for inaccurate / stale safety info](#1--liability-for-inaccurate-or-stale-safety-information)
  2. [Volunteer / Good Samaritan protections](#2--volunteer--good-samaritan-protections)
  3. [Why avoiding "official" / "safe" matters](#3--why-avoiding-official--safe-matters-legally)
  4. [Disclaimers & Terms of Use enforceability](#4--disclaimers--terms-of-use-enforceability)
  5. [Content aggregation: copyright, fair use, defamation](#5--content-aggregation-copyright-fair-use-defamation)
  6. [Third-party service terms compliance](#6--third-party-service-terms-compliance)
  7. [Accessibility (ADA / 508 / WCAG)](#7--accessibility-ada--section-508--wcag)
  8. [Privacy (forward-looking)](#8--privacy-conditionalforward-looking)
  9. [Branding / domains / trademark hygiene](#9--branding--domains--trademark-hygiene)
- [Risk matrix](#risk-matrix)
- [DRAFT disclaimer / Terms of Use](#draft-disclaimer--terms-of-use)
- [Minimum bar before distributing](#minimum-bar-before-distributing)
- [Open questions to raise with counsel](#open-questions-to-raise-with-counsel)
- [Methodology & source confidence](#methodology--source-confidence)
- [Bibliography](#bibliography)

---

## How to read this

Each finding cites numbered sources in the [Bibliography](#bibliography). Sources are
marked **(primary)** — statute, regulation, or court opinion — or **(secondary)** —
law-firm explainer, encyclopedia, or template. Where a load-bearing point could only
be confirmed through a secondary source (e.g. a paywalled or 403-blocked primary), it
is marked **⚑ partially verified**. The single most important habit for the team:
**when a finding is flagged, do not build a decision on it without a lawyer.**

## Bottom line up front

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
2. **Volunteer and Good Samaritan immunity statutes almost certainly do NOT cover
   this setup.** The federal Volunteer Protection Act requires a nonprofit/government
   nexus the two operators lack; California's Good Samaritan law covers hands-on care
   "at the scene," not a remote website. Do not rely on either. [6][11][12][13]
3. **The team's instinct to avoid "official" and "safe" is legally sound** — both
   words manufacture the *reliance* that liability claims need, and "official"
   framing risks false-association exposure. Keep the neutral, hedged, "verify with
   official sources" posture. [1][3][34]
4. **Disclaimers help but cannot waive everything.** California Civil Code §1668
   voids any attempt to disclaim fraud, willful injury, violation of law, or gross
   negligence; ordinary-negligence disclaimers are enforceable if clear and
   conspicuous. The disclaimer's real job here is to defeat *reasonable reliance*,
   not to form an airtight contract. [16][17][18][19]
5. **Content aggregation is low-risk if done conservatively:** headline + short
   snippet + link + attribution, never full-article reproduction; YouTube via the
   official iframe; republish *official* statements (fair-report privilege) and be
   cautious republishing private individuals' accusations. [24][25][26][28][29][31]
6. **The operational-compliance picture simplified with the conduit pivot.** Nominatim
   geocoding was removed with the address tool, eliminating the highest-risk
   service-terms item (the 1 req/s site-wide cap + autocomplete ban). The map now uses
   self-hosted MapLibre GL on OpenFreeMap vector tiles — keep OpenFreeMap/OSM
   attribution visible. The remaining service-terms watch item is Microlink
   link-previews (50/day shared free quota → cache or pre-render). [41][55]
7. **Accessibility law probably does not bind this project** (no business nexus), but
   given a vulnerable, partly limited-English audience, voluntary WCAG 2.1 AA
   conformance is cheap insurance and the right thing to do. [43][45]

> **⚠️ Caveat — Vietnamese-verification gap (added 2026-05-29).** The risk ratings above
> assume a *clean conduit*: accurate republication under honest disclosure. One gap
> qualified that assumption. Until dashboard v0.16, the site shipped ~100 safety-critical
> **Vietnamese** UI strings that were AI-drafted and **never verified by a fluent native
> speaker** (the prior reviewer is not fluent), while several docs described the
> translations as "native-verified." Unverified machine/AI translation of life-safety copy
> is exactly the *inaccurate safety information* §1 analyzes, and a confidently wrong
> Vietnamese "you're safe" manufactures the reliance the conduit posture exists to avoid —
> disproportionately on a limited-English population the standard of care (HHS §1557,
> federal LEP guidance, CA Gov. Code §7299.7) treats as protected. **Remediated in v0.16:**
> Vietnamese is held (`ready:false`, automatic English fallback), the false "native-verified"
> claims were corrected, and a build-failing eval gate blocks any unverified language from
> shipping. **Open:** re-enable Vietnamese only after a fluent native speaker + certified
> translation verify it. This caveat is risk-mapping, not legal advice; attorney review
> still gates public launch. See `docs/LANGUAGE_ACCESS.md`, `eval/test_language_access.py`,
> and `docs/research/2026-05-29-vi-anthropic-lens-research.md`.

---

## 1 — Liability for inaccurate or stale safety information

**Baseline: publishers generally owe no duty to verify accuracy.** In *Winter v.
G.P. Putnam's Sons*, 938 F.2d 1033 (9th Cir. 1991), the publisher of a mushroom
encyclopedia owed no duty to foragers who were poisoned: "publishers do not owe a
duty of care to the general public to check the accuracy of the contents of all of
the books that they publish," and the court noted "the gentle tug of the First
Amendment" against creating one. [9] This is the strongest baseline shield for pure
informational content.

**But voluntarily undertaking a safety service can create a duty to perform it
non-negligently — the "negligent undertaking" doctrine.** California has adopted
Restatement (Second) of Torts §§ 323 and 324A. Per *Artiglio v. Corning Inc.*, 18
Cal.4th 604 (1998), one who "undertakes, gratuitously or for consideration, to render
services to another which he should recognize as necessary for the protection of a
third person … is subject to liability … for physical harm resulting from his failure
to exercise reasonable care," where (a) the failure increases the risk of harm, (b)
the actor assumed a duty owed by another, or (c) "the harm is suffered because of
reliance … upon the undertaking." [1][2] By publishing evacuation/plume/risk content,
the operators arguably *undertake* a protective service — this is the central risk.

**Being free/volunteer does NOT lower the standard of care to zero.** The doctrine
applies "whether the harm results from … negligent … performance" and to
undertakings "for consideration [or] gratuitous." [1][2] Once you undertake, you owe
reasonable care. California's controlling jury instruction is CACI No. 450C
(Negligent Undertaking). [5]

**The duty has real limits — one of the three §324A conditions must actually be
met.** *Paz v. State of California*, 22 Cal.4th 550 (2000): "the mere assumption of a
… obligation does not automatically create a duty of care to third parties." [3]
There must be an undertaking *plus* increased risk, an assumed duty, or detrimental
reliance. For this tool the live questions would be: did stale/wrong output *increase*
risk (e.g. telling someone an unsafe address is safe), and did a user *rely* on it?

**The exposure is physical-harm, the most actionable category.** §§ 323/324A are
limited to "physical harm." [4] Because the dashboard concerns evacuation and health,
any plausible claim is framed as physical injury — the category courts most readily
compensate — so the economic-loss doctrine offers little shield here. [4]

**"Informational only" framing and disclaimers attack the reliance link.** Both the
§324A(c) reliance prong and negligent-misrepresentation both turn on **reliance**, so
prominent "informational only; verify with official Garden Grove / OCFA sources; do
not rely on this for evacuation decisions" language directly weakens the
reliance/causation chain. [3][4][9] **⚑ Partially verified:** no retrieved California
case squarely holds a disclaimer defeats a §324A claim for safety info — the inference
is doctrinally sound but not confirmed by an on-point holding.

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

---

## 2 — Volunteer / Good Samaritan protections

**The federal Volunteer Protection Act of 1997 protects only "volunteer[s] of a
nonprofit organization or governmental entity."** 42 U.S.C. § 14503(a) immunizes "no
volunteer of a nonprofit organization or governmental entity" beyond four conditions,
all keyed to "the scope of the volunteer's responsibilities in the nonprofit
organization or governmental entity." [6][11] The definition at § 14505 confirms a
"volunteer" performs services "for a nonprofit organization or a governmental entity,"
and "nonprofit organization" means a 501(c)(3) or a not-for-profit organized for
public benefit. [6][12]

**Critical gap: two individuals with no organization are NOT covered.** The Act
conditions every protection on acting on behalf of and within a nonprofit or
government entity. [6][12] Two private people running a website — with no 501(c)(3),
no unincorporated nonprofit association, and no government affiliation — fall outside
the statutory definition entirely. **The VPA almost certainly does not apply.** The
cleanest path to coverage, if desired, is to operate under a qualifying
nonprofit/government umbrella — a structural change, not a disclaimer. (See
[open questions](#open-questions-to-raise-with-counsel).)

**Even covered volunteers lose protection for serious fault.** § 14503(a)(3) strips
immunity where harm was caused by "willful or criminal misconduct, gross negligence,
reckless misconduct, or a conscious, flagrant indifference to the rights or safety of
the individual harmed." [11] So even an entity-affiliated version would not shield
knowingly publishing dangerously wrong data.

**California's Good Samaritan statute covers hands-on care "at the scene," not remote
information.** Health & Safety Code § 1799.102(a) protects one who "renders emergency
medical or nonmedical care at the scene of an emergency." [13] The 2009 amendment
(after *Van Horn v. Watson*, 45 Cal.4th 322) broadened "medical" to "medical or
nonmedical" *care*, but the trigger remains physically rendering care at the scene.
[13] A remotely operated dashboard does not "render care" and is not "at the scene."
**Bottom line:** neither the VPA nor California Good Samaritan law plausibly covers an
information website run by unaffiliated individuals. Do not rely on them.

---

## 3 — Why avoiding "official" / "safe" matters legally

**"Safe" manufactures the reliance that liability claims require.** Because §324A(c)
and negligent misrepresentation both turn on reliance, an affirmative representation
that an address or zone is "safe" (a) strengthens the "undertaking … necessary for
the protection of [third] person[s]" element, (b) invites detrimental reliance, and
(c) is exactly the kind of specific factual assertion that supports a
negligent-misrepresentation claim if wrong. [1][3][4] Neutral, hedged "informational
only — estimates, not official guidance" language does the opposite on every element.
**This validates the team's instinct with a concrete legal basis.**

**"Official" framing risks false-association exposure.** Don't reproduce government
seals or insignia: 18 U.S.C. § 701 targets unauthorized reproduction of "any badge,
identification card, or other insignia" of a U.S. agency, and the Lanham Act bars
registering or falsely suggesting connection with government insignia (see
[Topic 9](#9--branding--domains--trademark-hygiene)). [7][34] 18 U.S.C. § 712 (false
"Federal"/"United States" impression) is a **weak** fit because its operative clause
is limited to debt-collection and private-detective contexts — cited for completeness,
not as a live threat. [7] **⚑ Note:** California also has government-impersonation
statutes (Penal Code) that were not retrieved/verified here; regardless, do not
represent the site as a government source.

**Commercial-law deception regimes mostly don't reach a free, non-commercial site.**
FTC Act § 5 reaches deception "in or affecting commerce"; "[n]on-commercial or purely
editorial speech generally falls outside the FTC's jurisdiction." [14] California's
UCL (§ 17200) and false-advertising (§ 17500) target a "business act or practice," and
a recognized defense is non-commercial First-Amendment-protected speech — strongest
when the actor is "not a traditional commercial actor." [15] **⚑ Partially verified:**
"business practice" is construed broadly in California; *any monetization, donations,
or ads could change this analysis* — confirm with counsel before adding them.

---

## 4 — Disclaimers & Terms of Use enforceability

**Absolute floor — Civil Code § 1668: you cannot disclaim fraud, willful injury,
violation of law, or (per case law) gross negligence.** § 1668 voids "[a]ll contracts
which have for their object … to exempt any one from responsibility for his own fraud,
or willful injury … or violation of law." [16][17] In *New England Country Foods LLC
v. VanLaw Food Products* (Cal. Apr. 23, 2025), the California Supreme Court held § 1668
voids even *damage caps* for willful injury, calling such provisions "repugnant to
every sentiment of justice and propriety." [18] Gross-negligence releases are likewise
void (*City of Santa Barbara v. Superior Court* (2007) 41 Cal.4th 747 — **⚑ via
secondary source**). [16] **No disclaimer can shield willful or unlawful conduct;
draft accordingly and do not overpromise what the clause does.**

**Ordinary-negligence waivers ARE enforceable unless the transaction "affects the
public interest."** *Tunkl v. Regents* (1963) 60 Cal.2d 92 built a six-factor test
(public regulation; service of great importance/necessity; held open to all; superior
bargaining power; adhesion contract; purchaser under the provider's control). [19][20]
A free, no-login, voluntary information site is *not* the essential, adhesive,
control-exercising service *Tunkl* targeted — so a clear ordinary-negligence
disclaimer is more likely enforceable here than in *Tunkl*'s hospital setting.

**For a no-login site, the disclaimer's job is NOTICE, not contract formation.**
*Nguyen v. Barnes & Noble*, 763 F.3d 1171 (9th Cir. 2014) held a browsewrap
unenforceable because the user took no affirmative action. [21] *Berman v. Freedom
Financial Network*, 30 F.4th 849 (9th Cir. 2022) requires "(1) reasonably conspicuous
notice … and (2) … action that unambiguously manifests … assent," and condemned "tiny
gray font." [22] Since this site has no contract to compel (no login, no purchase, no
arbitration clause), the realistic goal is **putting a reasonable user on notice so
reliance becomes unreasonable** — a visible, high-contrast, legible disclaimer *on the
page near the map*, not buried in a footer link.

**"Informational only / verify with official sources" is the highest-value clause.**
It directly attacks reliance and causation. The pattern mirrors medical disclaimers
("not a substitute for professional … advice"; "call 911 in an emergency"). [23] A
draft block is in [DRAFT disclaimer / Terms of Use](#draft-disclaimer--terms-of-use).

---

## 5 — Content aggregation: copyright, fair use, defamation

**News headlines are generally not copyrightable.** 37 CFR § 202.1(a) excludes "[w]ords
and short phrases such as names, titles, and slogans"; under *Feist Publications v.
Rural Telephone*, 499 U.S. 340 (1991), "copyright rewards originality, not effort." [24]
A feed of *headline + link + short factual snippet* sits in low-risk territory;
reproducing full articles or long verbatim excerpts does not.

**Fair use (17 U.S.C. § 107) favors short snippet + link.** The four factors —
purpose/character, nature of the work, amount used, market effect — line up favorably:
nonprofit public-benefit purpose, factual news, short snippets, and links that drive
traffic *to* the source rather than substitute for it. [25] Keep snippets short and
link out.

**"Hot news" misappropriation is narrow and not triggered here.** Post-*Barclays
Capital v. Theflyonthewall.com*, 650 F.3d 876 (2d Cir. 2011), attributing each
headline to its publisher and not competing commercially keeps the tool outside the
non-preempted "passing off as one's own" zone. [26]

**Embedding: the 9th-Circuit "server test" protects you here (but is split
nationally).** *Perfect 10 v. Amazon*, 508 F.3d 1146 (9th Cir. 2007) holds embedded
content on a third-party server doesn't infringe the display right; the 9th Circuit
reaffirmed this in *Hunley v. Instagram*. [27] *Goldman v. Breitbart* (S.D.N.Y. 2018)
rejected the server test, so the rule is unsettled outside the 9th Circuit — but this
project operates under 9th-Circuit/California law. [27]

**YouTube embedding has a court-tested license posture.** In *Richardson v. Townsquare
Media*, embedding via YouTube's official iframe fell within YouTube's broad
sublicensable license. [28] Caveats: the license chain collapses if the original
uploader had no rights, and copying a thumbnail as a separate image is a separate
concern. **Use the official iframe; prefer official-agency and reputable-outlet
channels.**

**Defamation: § 230 protects the conduit, not your own words.** 47 U.S.C. § 230(c)(1):
"No provider or user of an interactive computer service shall be treated as the
publisher or speaker of any information provided by another information content
provider." [29] But adding your own commentary forfeits immunity *for your own
statements*, and § 230 does not cover IP/copyright claims. [30] California's
republication baseline is strict — "one who republishes a libel adopts it as his own."
[31] **A pure automated feed of third-party links is squarely within § 230; the team's
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

**Republish OFFICIAL statements for the fair-report privilege; be cautious with
private accusations.** California does **not** recognize neutral reportage for private
figures (*Khawar v. Globe International* (1998)) and generally rejects the wire-service
defense. [31][32] The reliable protection is the codified fair-report privilege, Cal.
Civil Code § 47(d)–(e), covering accurate reports of official government statements
and records. [31] Republishing OCFA / City of Garden Grove statements accurately is the
lowest-risk posture; republishing private individuals' accusations is the highest.

**Government works: federal-only public domain.** 17 U.S.C. § 105 denies copyright to
*federal* government works, but "works created by a state or local government may be
subject to copyright." [33] Do **not** assume City of Garden Grove or OCFA press
releases, maps, or logos are public-domain (California's public-records access is
distinct from a copyright license). Rely on short attributed excerpts (fair use) or
link out. **⚑ Partially verified:** § 1668/§ 105/§ 1052 statutory text was confirmed
via verbatim secondary quotes where direct primary fetch was blocked; the DMLP
California guides are not maintained post-2014/2016.

---

## 6 — Third-party service terms compliance

> **This is the section with concrete operational obligations.** The Nominatim and
> tile policies are the items most likely to get the site throttled or IP-banned.

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

**Nominatim geocoding — REMOVED (was `nominatim.openstreetmap.org`, the prior
HIGHEST-RISK item).** The "check your address" tool that called Nominatim was deleted
in the 2026-05-26 conduit pivot, so the OSMF Nominatim Usage Policy no longer applies:
the 1 req/s site-wide cap, the mandatory result caching, and the autocomplete /
systematic-query / scraping ban (an instant-ban trigger) are all moot. *If any
address-lookup feature is ever reintroduced, this section's limits become binding again
— see the prior revision history.* [37]

**MapLibre GL — BSD-2-Clause [55].** The self-hosted MapLibre GL build in `/lib` keeps
its license header. MapLibre renders the OpenFreeMap/OSM attribution via its built-in
attribution control — **do not remove or hide that control**, which discharges the
vector-tile and ODbL attribution duties. (Leaflet, the prior renderer, is no longer
used.)

**YouTube embedded iframe [39][40].** Use the standard `<iframe>` embed: don't overlay
visual elements in front of the player, keep the viewport "at least 200px by 200px,"
and don't hide YouTube branding. (`modestbranding` is deprecated and has no effect.)
Embedding a public video this way is permitted on a non-commercial site.

**Microlink link previews — `microlink.io` [41] (MEDIUM).** Free tier is **"50
requests per day,"** no API key required, no stated attribution; over-limit returns
HTTP 429. 50/day is a *shared* quota that public traffic will exhaust fast. **Cache or
pre-render previews server-side / at build time** to avoid 429s. **⚑ Partially
verified:** docs show both "50/day" (current) and a legacy "250/24h"; treat 50/day as
binding.

**OSM data attribution (ODbL) [42].** Required credit: "© OpenStreetMap contributors,"
with a link to openstreetmap.org/copyright — satisfied automatically by MapLibre GL's
attribution control if left intact.

---

## 7 — Accessibility (ADA / Section 508 / WCAG)

**ADA Title III probably does not bind this project.** Title III covers "public
accommodations" (businesses open to the public). In the 9th Circuit (California),
*Robles v. Domino's Pizza* (9th Cir. 2019) requires a website to have a "nexus to a
physical place of public accommodation." [43] A free, non-commercial civic tool by two
private individuals is not a business and has no such nexus — a strong argument it
falls outside Title III. [43][44]

**California's Unruh Civil Rights Act — low but nonzero exposure.** Unruh (Civ. Code
§ 51) reaches "business establishments" and allows damages for (1) an ADA violation or
(2) intentional discrimination; statutory minimum is $4,000 per violation plus fees.
[45] Both predicates are weak here (no ADA violation if Title III doesn't apply; no
business and no intentional discrimination). But California is the highest-volume
accessibility-litigation state, so **voluntary WCAG conformance is the cheapest
insurance.** **⚑ Partially verified:** the *Martin v. Thi E-Commerce* two-theory quote
is from a practitioner source, not the opinion directly.

**Section 508 — confirmed N/A.** § 508 binds federal agencies (and their contractors),
not private individuals. [46] **DOJ's 2024 ADA Title II web rule — confirmed N/A**: it
adopts WCAG 2.1 AA for *state and local governments*, not private volunteers. [47]
Both, however, point to **WCAG 2.1/2.2 AA as the de facto standard** to follow.

**Minimal good-faith WCAG for this tool** (important given a vulnerable, partly
limited-English audience): text contrast ≥ 4.5:1; alt text on informational
images/icons; full keyboard navigation with visible focus; never convey status by color alone (status
badges need text/icon too); semantic headings/landmarks; and — because map info is
inherently visual — **a plain-text equivalent of the evacuation-zone information shown
on the map** so non-visual users get the same emergency info. A short accessibility statement with a contact email is a recommended
good-faith signal. (Pairs with the [error-report channel](#open-questions-to-raise-with-counsel)
open question.)

---

## 8 — Privacy (conditional/forward-looking)

**Status today: NOT-YET-APPLICABLE.** The site collects no PII server-side; address
geocoding is client-side and no address is stored. The items below trigger only **IF**
a messaging/reunification feature is later added — flag this section as forward-looking.

**CCPA/CPRA — does not apply.** CCPA applies to *for-profit businesses* meeting one of:
>$25M revenue; buying/selling/sharing 100k+ California residents' data; or 50%+ revenue
from selling personal information. [48] A free non-commercial volunteer project is not a
for-profit business and meets none of the thresholds — state this affirmatively if a
feature is proposed.

**COPPA — the highest-friction future feature.** The COPPA Rule (16 CFR Part 312)
requires operators of child-directed services, or those with "actual knowledge" they
collect data from under-13s, to "obtain verifiable parental consent." [49] A messaging
feature where minors could participate would trigger this. **Design implication:**
either (a) collect no personal info via messaging, (b) implement neutral age-gating +
verifiable parental consent, or (c) document the service is not directed to children
and act on actual knowledge.

**No client-side geocoding today.** The conduit pivot removed the address tool, so the
dashboard no longer sends user-typed addresses to any geocoder. There is no per-user
location input to disclose. **Forward-looking (CCPA/CPRA + AB 1355):** if a
location-aware feature (proximity alerts, location filtering) is ever added, precise
geolocation is **Sensitive Personal Information** under CPRA, and California's proposed
Location Privacy Act (AB 1355, introduced Feb 2025) would require opt-in consent with
penalties up to $25,000/violation. Process any future geolocation **client-side only**,
never stored server-side. [50][20]

---

## 9 — Branding / domains / trademark hygiene

**Never use government flags/seals/insignia — absolute bar.** Lanham Act § 2(b)
(15 U.S.C. § 1052(b)) bars marks consisting of "the flag or coat of arms or other
insignia of the United States, or of any State or municipality … or any simulation
thereof"; *In re City of Houston* held even cities can't register their own seals. [34]
**Do not put the City of Garden Grove seal, OCFA insignia, or any simulation into the
logo or favicon.**

**Don't falsely suggest a government connection — § 2(a).** Lanham § 2(a) bars matter
that "falsely suggests a connection with … institutions … or national symbols." [34]
"ggtankwatch" reads as a citizen-watch descriptor rather than a government identifier,
which helps — but pair it with an explicit non-affiliation notice.

**Using the city/agency NAME descriptively is OK under nominative fair use, if you
signal independence.** The three factors: necessity, minimalism (no logo
embellishment), and non-affiliation clarity (disclaimers; don't mislead). [35] Courts
view disclaimers favorably but they are "by no means a 'Get Out of Jail Free' card."

**Practical hygiene:** run a USPTO clearance search for "ggtankwatch" and close
variants; use no official marks; place a prominent, legible non-affiliation notice
(header/footer + about page): *"ggtankwatch is an independent, volunteer-run project.
It is not affiliated with, endorsed by, or operated by the City of Garden Grove, the
Orange County Fire Authority, or any government agency."*; reference "Garden Grove"
descriptively in text without stylizing it to mimic official branding. [34][35]
**⚑ Partially verified:** Lanham § 2 text was confirmed via secondary quotes; the
§ 43(a) (15 U.S.C. § 1125(a)) unfair-competition line could not be retrieved from a
primary source this session — confirm separately.

---

## Risk matrix

Likelihood (L) and Severity (S) are rough, qualitative pre-mitigation estimates for a
small, undistributed, non-commercial tool. **High severity = potential physical harm
or an existential claim; Low likelihood ≠ ignore.** This is a prioritization aid, not
an actuarial assessment — confirm with counsel.

| # | Risk | L | S | Pre-mitigation | Mitigation |
|---|------|---|---|----------------|------------|
| R1 | **Negligent-undertaking / physical-harm claim** from reliance on stale evac/wind display | Low | **Low–Med** | Dropped after conduit pivot removed the address tool (was the headline exposure) | "Informational only / verify with official sources / call 911" on-page; data timestamp + staleness warning; frame as *estimates*; **no authored verdicts** (conduit); §552 no-pecuniary-interest shield [1][2][3][9][53][54] |
| R2 | **Negligent misrepresentation** from a specific false factual assertion | Low | Low–Med | Largely moot — the "your address is safe" output was removed; reinforced by §552 pecuniary-interest shield (no revenue) | Avoid "safe"/"official"; hedge; disclaim; stay non-commercial [1][3][4][54] |
| R3 | **No volunteer/Good-Samaritan immunity** (false sense of protection) | — | Med | A *gap*, not an event | Don't rely on VPA/§1799.102; consider a nonprofit umbrella (see open questions) [6][11][12][13] |
| R4 | **False-association / "official" implication** | Low | Med | Reputational + escalates R1 | No seals/insignia; prominent non-affiliation notice; avoid "official" [7][34] |
| R5 | **Defamation from republishing private accusations** | Low | Med | Higher if editorializing | §230 for pure third-party feeds; fair-report only for *official* statements; factual captions; no editorial accusations [29][30][31] |
| R6 | **Copyright — over-long article reproduction** | Low | Med | Low if snippet+link | Headline + short snippet + link + attribution only; never full articles [24][25] |
| R7 | **Nominatim ban / throttle** — N/A | — | — | Removed with the address tool (conduit pivot); re-applies only if address lookup is reintroduced | n/a [37] |
| R8 | **Map-tile attribution lapse** (OpenFreeMap vector tiles + self-hosted MapLibre) | Low | Low | Self-hosting removed the OSM raster-tile throttle risk | Keep OpenFreeMap/"© OpenStreetMap contributors" attribution control visible [42][55] |
| R9 | **Microlink 429 under public traffic** (50/day shared) | Med | Low | Previews fail | Cache / pre-render previews at build time [41] |
| R10 | **YouTube embed ToS breach** | Low | Low | — | Official iframe ≥200×200, no overlay, don't hide branding [39][40] |
| R11 | **Accessibility / Unruh claim** | Low | Med | $4k/violation + fees if it landed | Voluntary WCAG 2.1 AA; text equivalent for map; accessibility statement [43][45] |
| R12 | **Trademark — confusing/seal use** | Low | Low–Med | — | Clearance search; no official marks; non-affiliation notice [34][35] |
| R13 | **Privacy (future messaging) — COPPA/CCPA** | Conditional | Med | Only if feature added | Re-assess before building; no PII, or age-gate + parental consent [48][49] |

---

## DRAFT disclaimer / Terms of Use

> **DRAFT — not legal advice. Have a California attorney review and adapt before use.**
> These are patterns adapted from real disclaimers found in research [16][23]; bracketed
> items are placeholders. Per Civil Code § 1668, nothing here can (or attempts to)
> waive liability for fraud, willful injury, violation of law, or gross negligence. [16][18]

### A. On-page banner (place near the map — visible, legible, not a footer link)

> **Informational only — not official emergency guidance.** This is an independent,
> volunteer-run website. The map and information shown are **estimates compiled from
> official and news sources**, may be **out of date or wrong**, and are **not** a
> substitute for official guidance. Always verify with the **Orange County Fire
> Authority** and the **City of Garden Grove** (ggcity.org/emergency). **If you are in
> danger, call 911.**

*(Provide a translated equivalent for the Vietnamese audience, reviewed by the
translator; keep the same hedged meaning — avoid words equivalent to "official" or
"safe.")*

### B. Terms of Use / full disclaimer (linked from every page)

> **1. Not official; not affiliated.** ggtankwatch is an independent project operated
> by private volunteers. It is **not affiliated with, endorsed by, or operated by** the
> City of Garden Grove, the Orange County Fire Authority, Cal OES, the EPA, or any
> government agency. For official emergency information, see ggcity.org/emergency.
>
> **2. Informational only.** All content — including the map, the evacuation zone, and
> the aggregated news, video, and official statements — is provided for **general
> informational purposes only** and is **not** a substitute for official emergency
> guidance, professional advice, or your own judgment. It is compiled from official and
> news sources, is not authoritative, and may be inaccurate, incomplete, or outdated.
>
> **3. No warranty; "as is."** The information is provided "**as is**" and "**as
> available**," without warranties of any kind, express or implied, including accuracy,
> completeness, reliability, or availability. **Any reliance you place on it is
> strictly at your own risk.**
>
> **4. Verify and act on official sources.** Always verify information here against
> official sources, including the Orange County Fire Authority and the City of Garden
> Grove. **If you believe you are in danger or are experiencing an emergency, call 911
> immediately.** Do not rely on this website to make evacuation or safety decisions.
>
> **5. Limitation of liability.** To the fullest extent permitted by law, the operators
> are not liable for any loss or damage arising from or in connection with your use of,
> or reliance on, this website or its contents. *(This limitation does not apply to
> liability that cannot be excluded under California law, including for fraud, willful
> injury, violation of law, or gross negligence — Cal. Civ. Code § 1668.)*
>
> **6. Third-party content.** Headlines, links, videos, and official statements come
> from third parties; the operators do not control and are not responsible for that
> content. Attribution does not imply endorsement.
>
> **7. Report an error.** If you believe any information here is wrong, please tell us
> at [contact]. *(See open questions — an error-report channel is itself a possible
> liability mitigation.)*
>
> **8. Privacy.** We do not collect or store personal information. The dashboard has no
> login, no accounts, and no address-lookup feature. *(Update this if any data is ever
> collected or stored.)*
>
> **9. Changes.** We may update these terms at any time. Last updated: [date].

### C. Attribution footer (compliance)

> Map © OpenStreetMap contributors, tiles by OpenFreeMap. *(Keep MapLibre GL's built-in
> attribution control enabled — it renders this automatically.)* [42][55]

---

## Minimum bar before distributing

A practical pre-distribution checklist. **Items marked 🔴 are blockers**; 🟡 are strongly
recommended; 🟢 are good practice.

- [ ] 🔴 **Attorney review** of (a) this document's load-bearing findings and (b) the
      final disclaimer/ToU wording. [1][16]
- [ ] 🔴 **On-page "informational only / verify / call 911" banner** live near the map,
      visible and legible, not buried. [22][23]
- [ ] 🔴 **No authored verdicts; no "official" or "safe" language; no government
      seals/insignia** anywhere in UI, logo, or favicon (conduit posture). [7][34]
- [x] ✅ **Geocoder compliance — N/A.** The Nominatim address tool was removed in the
      conduit pivot; no geocoding obligations remain. [37]
- [ ] 🟡 **Prominent non-affiliation notice** ("not affiliated with the City of Garden
      Grove / OCFA / any government agency"). [34][35]
- [ ] 🟡 **Data freshness/staleness indicator** visible on the dashboard (timestamp +
      "may be out of date" warning) — directly mitigates the stale-info risk. [1]
- [ ] 🟡 **Aggregation hygiene:** headline + short snippet + link + attribution only;
      no full-article reproduction; official iframe for YouTube. [24][25][28]
- [ ] 🟡 **Republish official statements; avoid editorializing private accusations.** [29][31]
- [ ] 🟡 **Map attribution** ("© OpenStreetMap contributors", tiles by OpenFreeMap)
      visible (MapLibre control on). [42][55]
- [ ] 🟡 **Microlink:** cache/pre-render previews to avoid 429s under traffic. [41]
- [ ] 🟢 **Voluntary WCAG 2.1 AA basics** + plain-text equivalent of the in-zone result
      + short accessibility statement (important for the limited-English audience). [43][45]
- [ ] 🟢 **Error-report channel** (e.g. a contact email) live and monitored. [open questions]
- [ ] 🟢 **USPTO clearance search** for "ggtankwatch" before further branding investment. [34]
- [ ] 🟢 **Decide the entity question** (operate as-is vs. nonprofit umbrella) — see below.

---

## Open questions to raise with counsel

These are surfaced deliberately and **not resolved here** — they need legal and team
judgment:

1. **Should the team form a formal entity (nonprofit / unincorporated nonprofit
   association / LLC) before distributing?** Considerations *for*: the federal
   Volunteer Protection Act's immunity requires a nonprofit/government nexus the two
   individuals currently lack [6][12], and an entity can shift liability away from
   personal assets. Considerations *against*: formation cost/time, ongoing compliance,
   and that an entity does not cure negligence exposure (and VPA still excludes gross
   negligence) [11]. *Not a decision for this research — flag for counsel.*

2. **Should an explicit "report an error" channel be added as a liability mitigation?**
   An easy correction path arguably shows reasonable care and helps keep information
   current (reducing the stale-info risk in R1). The counter-consideration is that a
   *known-and-unaddressed* report could be evidence of notice — so any channel needs a
   real process for acting on reports. *Flag for counsel; do not decide here.*

---

## Methodology & source confidence

This document was produced via the deep-research workflow: three parallel research
streams (liability/immunity; disclaimers/aggregation/trademark; service-terms/
accessibility/privacy) each gathered primary sources (statutes via Cornell LII,
GovInfo, leginfo; court opinions via Justia; official policy/ToS pages) and reputable
secondaries, returning verbatim quotes with URLs. Claims were tracked to sources and
uncertain items flagged.

**Confidence is high** for: the negligent-undertaking framework [1][2][3]; the VPA's
nonprofit/government requirement [6][11][12]; the OSM tile/Nominatim policies (fetched
verbatim) [36][37]; § 230's conduit/own-words distinction [29]; the ADA Title III
nexus rule in the 9th Circuit [43]; and the CCPA non-applicability [48].

**Confidence is lower (⚑ flagged inline)** for: whether a disclaimer defeats a §324A
claim for safety info (no on-point holding retrieved); how a court would classify the
interactive "check your address" tool under *Winter*'s chart/expression line; the
§1668/§1052 statutory text (confirmed via secondary quotes after primary fetches were
blocked); the *Martin v. Thi E-Commerce* Unruh quote (practitioner source); the
Microlink 50-vs-250/day discrepancy; and the Lanham § 43(a) line (not retrieved from a
primary source). **Treat every flagged item as a question for a lawyer, not a
conclusion.** DMLP guides cited for California defamation are not maintained past
2014/2016.

**2026-05-29 reconciliation.** This document was updated to match the shipped conduit
product (address checker, blast/plume layers, Leaflet, and Nominatim removed) and to
fold in the 2026-05-27 deep-research legal memo
([`legal-research/2026-05-27/legal_risk_memo.md`](legal-research/2026-05-27/legal_risk_memo.md)).
The memo's distinctive contributions — the §552 pecuniary-interest shield, the §230
aggregator/ICP line (*Force v. Facebook*), the *Brandt* forecaster analogy, and the
CCPA/AB 1355 location-privacy watch — are cited inline as [50]–[55]. The two docs use
different primary framings (§324A negligent-undertaking here; §552 negligent
misrepresentation in the memo); both are retained as complementary defenses.

---

## Bibliography

*Accessed 2026-05-24. (P) = primary source; (S) = secondary.*

**Liability, immunity, misrepresentation (Topics 1–3)**
1. Artiglio v. Corning Inc., 18 Cal.4th 604 (1998). (P, case) — https://law.justia.com/cases/california/supreme-court/4th/18/604.html
2. Restatement (Second) of Torts §§ 323, 324A (text + quoted in *Artiglio*/*Paz*). (S, Restatement)
3. Paz v. State of California, 22 Cal.4th 550 (2000). (P, case) — https://law.justia.com/cases/california/supreme-court/4th/22/550.html
4. Negligent misrepresentation & economic-loss doctrine overview. (S) — https://www.numberanalytics.com/blog/ultimate-guide-negligent-misrepresentation-advanced-tort-law
5. CACI No. 450C — Negligent Undertaking (Judicial Council of California Civil Jury Instructions). (P) — https://www.justia.com/trials-litigation/docs/caci/400/450c/
6. Volunteer Protection Act of 1997, Pub. L. 105-19 (full text). (P, statute) — https://www.govinfo.gov/content/pkg/PLAW-105publ19/html/PLAW-105publ19.htm
7. 18 U.S.C. §§ 701 & 712. (P, statute) — https://www.law.cornell.edu/uscode/text/18/701 · https://www.law.cornell.edu/uscode/text/18/712
8. 42 U.S.C. § 14501 (Findings and purpose). (P, statute) — https://www.law.cornell.edu/uscode/text/42/14501
9. Winter v. G.P. Putnam's Sons, 938 F.2d 1033 (9th Cir. 1991). (P, case) — https://law.justia.com/cases/federal/appellate-courts/F2/938/1033/294363/
10. Brandenburg v. Ohio, 395 U.S. 444 (1969). (P, case) — https://supreme.justia.com/cases/federal/us/395/444/
11. 42 U.S.C. § 14503 (Limitation on liability for volunteers). (P, statute) — https://www.law.cornell.edu/uscode/text/42/14503
12. 42 U.S.C. § 14505 (Definitions). (P, statute) — https://www.law.cornell.edu/uscode/text/42/14505
13. California Health & Safety Code § 1799.102. (P, statute) — https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=HSC&sectionNum=1799.102.
14. FTC Act § 5 (15 U.S.C. § 45) & 1983 Deception Policy Statement. (P/S) — https://www.congress.gov/crs-product/IF12244 · https://www.ftc.gov/legal-library/browse/ftc-policy-statement-unfairness
15. California UCL — Bus. & Prof. Code §§ 17200/17500 incl. non-commercial-speech defense. (S, law firm) — https://www.bonalaw.com/insights/legal-resources/defenses-to-a-section-17200-unfair-competition-law-claim-in-california

**Disclaimers, ToU, aggregation, trademark (Topics 4, 5, 9)**
16. Civil Code § 1668 — limitations of liability (incl. *City of Santa Barbara v. Superior Court* (2007) 41 Cal.4th 747). (S, law firm) — https://swmllp.com/civil-code-1668-limitations-of-liability/
17. California Civil Code § 1668. (P, statute — direct fetch 403; text via §16/§19 quotes) — https://codes.findlaw.com/ca/civil-code/civ-sect-1668/  ⚑
18. New England Country Foods LLC v. VanLaw Food Products (Cal. Apr. 23, 2025). (S, law firm) — https://www.clarkhill.com/news-events/news/california-supreme-court-holds-that-limitations-of-liability-provisions-are-unenforceable-for-willful-conduct-under-civil-code-section-1668/
19. Tunkl v. Regents, 60 Cal.2d 92 (1963). (P, case) — https://law.justia.com/cases/california/supreme-court/2d/60/92.html
20. Tunkl v. Regents — six-factor summary. (S) — https://en.wikipedia.org/wiki/Tunkl_v._Regents_of_the_University_of_California
21. Nguyen v. Barnes & Noble, 763 F.3d 1171 (9th Cir. 2014). (S summarizing P) — https://newmedialaw.proskauer.com/2014/09/08/browsewrap-agreement-held-unenforceable-against-consumer-due-to-insufficient-notice/
22. Berman v. Freedom Financial Network, 30 F.4th 849 (9th Cir. 2022). (P, opinion PDF) — https://cdn.ca9.uscourts.gov/datastore/opinions/2022/04/05/20-16900.pdf
23. Website disclaimer examples/templates (incl. WebMD, Mayo Clinic patterns). (S) — https://termly.io/resources/articles/disclaimer-examples/
24. 37 CFR § 202.1 + U.S. Copyright Office; Feist Publications v. Rural Telephone, 499 U.S. 340 (1991). (P) — https://www.copyright.gov/title37/202/37cfr202-1.html · https://www.law.cornell.edu/cfr/text/37/202.1
25. 17 U.S.C. § 107 — Fair use. (P, statute) — https://www.law.cornell.edu/uscode/text/17/107
26. Barclays Capital v. Theflyonthewall.com, 650 F.3d 876 (2d Cir. 2011); INS v. AP, 248 U.S. 215 (1918); NBA v. Motorola, 105 F.3d 841 (2d Cir. 1997). (P/S) — https://www.rcfp.org/news-aggregator-not-liable-hot-news-misappropriation/
27. Server-test split: Perfect 10 v. Amazon, 508 F.3d 1146 (9th Cir. 2007); Hunley v. Instagram; Goldman v. Breitbart (S.D.N.Y. 2018); McGucken v. Newsweek. (S, law firm) — https://www.venable.com/insights/publications/2025/08/federal-courts-split-on-server-test-in-copyright
28. YouTube embedding sublicense: Richardson v. Townsquare Media. (S) — https://copyrightlately.com/sdny-social-media-embedding/
29. 47 U.S.C. § 230. (P, statute) — https://www.law.cornell.edu/uscode/text/47/230
30. Publishing the statements/content of others; CDA immunity (incl. *Diamond Ranch Academy v. Filer*). (S, DMLP — not maintained post-2016) — https://www.dmlp.org/legal-guide/publishing-statements-and-content-others
31. California defamation; fair-report privilege Cal. Civ. Code § 47(d)–(e); *Khawar v. Globe International* (1998). (S, DMLP/RCFP) — https://www.dmlp.org/legal-guide/california-defamation-law · https://www.rcfp.org/neutral-report-privilege-does-not-apply-private-figures/
32. Neutral reportage privilege. (S, academic) — https://firstamendment.mtsu.edu/article/neutral-reportage-privilege/
33. 17 U.S.C. § 105 + copyright status of government works (state/local may be protected). (P/S) — https://www.law.cornell.edu/uscode/text/17/105 · https://www.arl.org/wp-content/uploads/2015/06/copyright-status-of-government-works.pdf
34. Lanham Act § 2(a)/(b), 15 U.S.C. § 1052; *In re City of Houston* (Fed. Cir.). (S — confirm § 1052 text at law.cornell.edu/uscode/text/15/1052) ⚑ — https://www.fitcheven.com/?t=40&an=25107&anc=180&format=xml&p=5486
35. Nominative fair use in trademark law; *Yelp v. ReviewVio*. (S, law firm) — https://harriganip.com/blog/nominative-fair-use-trademark-law/

**Service terms, accessibility, privacy (Topics 6–8)**
36. OpenStreetMap Foundation — Tile Usage Policy. (P, official policy) — https://operations.osmfoundation.org/policies/tiles/
37. OpenStreetMap Foundation — Nominatim Usage Policy. (P, official policy) — https://operations.osmfoundation.org/policies/nominatim/
38. Leaflet LICENSE (BSD-2-Clause). (P, license) — https://raw.githubusercontent.com/Leaflet/Leaflet/main/LICENSE
39. YouTube API Services Terms / Developer Policies (branding, attribution). (P, official) — https://developers.google.com/youtube/terms/required-minimum-functionality
40. YouTube — Required Minimum Functionality (player ≥200×200, no overlays). (P, official) — https://developers.google.com/youtube/terms/required-minimum-functionality
41. Microlink API — rate limit + pricing (50/day free; 250/24h legacy ⚑). (P, official docs) — https://microlink.io/docs/api/basics/rate-limit · https://microlink.io/pricing
42. OpenStreetMap — Copyright and License (ODbL; "© OpenStreetMap contributors"). (P, official) — https://www.openstreetmap.org/copyright
43. Robles v. Domino's Pizza (9th Cir. 2019; cert. denied 2019). (S, law-firm analysis of binding case) — https://www.adatitleiii.com/2019/10/
44. DOJ — Guidance on Web Accessibility and the ADA. (P, .gov) — https://www.ada.gov/resources/web-guidance/
45. California Unruh Civil Rights Act, Civ. Code §§ 51, 52; *Martin v. Thi E-Commerce* (2023) ⚑. (P/S) — https://calcivilrights.ca.gov/unruh/
46. Section 508 — Laws & Policies (federal agencies only). (P, .gov) — https://www.section508.gov/manage/laws-and-policies/
47. DOJ — 2024 ADA Title II web rule fact sheet (state/local govt; WCAG 2.1 AA). (P, .gov) — https://www.ada.gov/resources/2024-03-08-web-rule/
48. California Attorney General — CCPA (business thresholds). (P, .ca.gov) — https://oag.ca.gov/privacy/ccpa
49. FTC — COPPA Rule, 16 CFR Part 312 (verifiable parental consent) ⚑. (P, .gov) — https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa · https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-312

**Conduit reconciliation additions (2026-05-29)**
50. 2026-05-27 deep-research legal memo (internal). [`docs/legal-research/2026-05-27/legal_risk_memo.md`](legal-research/2026-05-27/legal_risk_memo.md) — conduit-mode risk memo; sources tracked in the sibling `claims.jsonl`/`evidence.jsonl`/`sources.jsonl`.
51. Force v. Facebook, 934 F.3d 53 (2d Cir. 2019). (P, case) — algorithmic curation protected under §230. https://law.justia.com/cases/federal/appellate-courts/F3/934/53/
52. Bartnicki v. Vopper, 532 U.S. 514 (2001). (P, case) — First Amendment protects publishing truthful information on matters of public concern. https://supreme.justia.com/cases/federal/us/532/514/
53. Brandt v. The Weather Channel. (S, case) — no liability for incorrect forecasts absent actual negligence (cited in memo [15]).
54. Restatement (Second) of Torts § 552 (1977). (S, Restatement) — negligent misrepresentation; pecuniary-interest requirement. https://www.columbia.edu/~mr2651/ecommerce3/2nd/statutes/RestatementTorts.pdf
55. OpenFreeMap (https://openfreemap.org/) + MapLibre GL JS (BSD-2-Clause, https://maplibre.org/). (P, project/license) — vector tiles + self-hosted renderer replacing OSM raster tiles + Leaflet.

---

*End of research. Reminder: this is research, not legal advice — consult a licensed
California attorney before public distribution.*
