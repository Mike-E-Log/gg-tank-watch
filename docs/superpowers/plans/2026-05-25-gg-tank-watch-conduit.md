# GG Tank Watch → Information Conduit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve GG Tank Watch from a tool that authors its own hazard verdicts into a faithful *information conduit* — amplify and translate official emergency sources, route residents to the official channels, and author no safety directives of its own.

**Architecture:** Single-file static dashboard (`dashboard.html`) reads `status.json` (incident data) + `config.json` (map params), produced by Python scripts (`scripts/gather_facts.py`, `update_status.py`, `refresh_local.py`) and guarded by a pytest-style harness (`eval/test_*.py`, run via `eval/run_all.py`). Two parallel lanes: Lane A (product, this repo) and Lane B (org/legal structure, mostly non-code, attorney-gated).

**Tech stack:** Vanilla HTML/JS + Leaflet map, Python 3 data pipeline, ntfy push, Vercel static hosting (noindex during iteration).

**Source research:** `C:\Users\redacted\Documents\{HelpSafely,AnthropicAlignment,HazardModel}_Research_20260525\`.

---

## Lane ownership (collaborative repo — avoid collisions)

Per project memory the repo runs file-disjoint lanes: **Mike-infra** (map, `dashboard.html` map/JS, `config.json`, `scripts/`, `eval/`) and **Nancy/Nancy-i18n** (`STRINGS`/`LANGS` translation copy). Each task below is tagged `[Mike]` or `[Nancy]`. Branch before working; do not edit `main` directly.

## Sequencing — what ships first

1. **Task 1 — Replace the authored personal-hazard verdict + blast/plume overlay with an official-zone router.** *(highest priority: this is the live alignment/liability risk)*
2. **Task 2 — Source + "last updated" on every displayed item.**
3. **Task 3 — AI-disclosure** (data is AI-summarized; outputs are consumer-facing).
4. **Task 4 — Ship Vietnamese** (flagship; native-verified, framework already exists).
5. **Task 5 — Route-to-official panel** (official zone lookup, alert sign-ups, AirNow).
6. **Task 6 — One-page Code of Conduct.**
7. **Task 7 — Direct official-feed ingestion** (AirNow now; CAP/IPAWS, NWS later).
8. **Lane B (parallel) — entity, insurance, attorney review.** Attorney review **blocks public launch / removing `noindex`**, not the code tasks.

---

## Task 1: Replace authored hazard verdict with official-zone router  `[Mike]`

The dashboard currently geocodes a resident's address and returns a personal verdict (`ELEVATED — within injury radius or plume`, `DOWNWIND`, safe) computed from self-authored blast radii + plume cone. This authors a safety directive and crosses the §230/§552 line. Replace it with a router: geocode → "you appear to be in / near the official evacuation area — confirm at the official checker," showing **only** the official evac polygon (labeled official), with no authored blast rings, no plume cone, and no safe/elevated verdict.

**Files:**
- Modify: `dashboard.html` — remove blast-ring render (`~:1530`), plume render (`~:1590-1601`), and the verdict computation/labels (`~:1712-1742`, `~:1116-1121`, `~:1338-1342`); replace the checker result with a route-to-official message.
- Modify: `config.json` — remove `blast_zones_mi`, `plume_max_length_mi`, `plume_cone_degrees`, `blast_zone_source_note`; keep `evac_polygon` but treat it as a soft "may be affected" hint only.
- Modify: `eval/test_safety.py` — assert the authored-verdict strings and blast/plume rendering are gone.
- Test: `eval/test_safety.py`, `eval/test_schema.py`.

- [ ] **Step 1: Write the failing safety test** (assert no authored verdict / blast / plume remains)

In `eval/test_safety.py`, add:

```python
def test_no_authored_hazard_verdict():
    html = open("dashboard.html", encoding="utf-8").read()
    banned = [
        "within injury radius or plume",
        "blast_zones_mi",
        "layers.plume",
        "ELEVATED — within injury radius",
    ]
    found = [b for b in banned if b in html]
    assert not found, f"authored-hazard remnants still present: {found}"

def test_checker_routes_to_official():
    html = open("dashboard.html", encoding="utf-8").read()
    assert "ggcity.org/emergency" in html, "address checker must route to official source"
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `python -m pytest eval/test_safety.py::test_no_authored_hazard_verdict -v`
Expected: FAIL (the banned strings are still present).

- [ ] **Step 3: Remove blast-ring + plume rendering**

In `dashboard.html`, delete the `m.blast_zones_mi.forEach(...)` block (`~:1530`) and the plume polygon block (`~:1590-1601`), plus the `layers.blasts`/`layers.plume` entries in the `layers` object (`~:1352`). Keep the evac polygon render.

- [ ] **Step 4: Replace the verdict with a router result**

Replace the verdict-producing function (`~:1712-1742`) so that, after geocoding, it only computes point-in-polygon against the official `evac_polygon` and returns one of two non-directive messages (new `STRINGS` keys, English first; Vietnamese added in Task 4):

```js
// check.router.inside / check.router.near — non-directive, official-deferring
// inside polygon -> "This address appears to fall within the area officials have
//   described as evacuated. Confirm your status at the official checker."
// otherwise      -> "This address does not appear inside the described area, but
//   conditions change. Confirm at the official checker."
// BOTH always render the official link: status.you.address_checker_url
```

Remove the `check.verdict.*` and `check.factor.plume` strings and the label-matching at `~:1338-1342`.

- [ ] **Step 5: Strip authored map params from config**

In `config.json`, delete `blast_zones_mi`, `plume_max_length_mi`, `plume_cone_degrees`, `weather_station` (if only used for plume), and `blast_zone_source_note`. Update `map.evac_polygon_note` to read as an unofficial hint that defers to `ggcity.org/emergency`.

- [ ] **Step 6: Run tests to verify pass**

Run: `python -m pytest eval/test_safety.py eval/test_schema.py -v`
Expected: PASS. (Do **not** use `eval/run_all.py --quiet` to verify — per project memory it suppresses `[FAIL]` lines; check the pytest exit code / non-quiet scorecard.)

- [ ] **Step 7: Visually verify** the map shows only the official evac polygon and the checker returns a route-to-official message in both EN and (after Task 4) VI.

- [ ] **Step 8: Commit**

```bash
git add dashboard.html config.json eval/test_safety.py
git commit -m "feat(safety): replace authored hazard verdict with official-zone router"
```

**Acceptance criteria:** No blast rings, no plume cone, no `ELEVATED/DOWNWIND/safe` personal verdict anywhere in the live UI. Address check returns only a neutral "appears in/near the described area — confirm officially" message that always links the official checker. `eval/test_safety.py` passes.

**Blocked by:** none. Highest-priority ship.

---

## Task 2: Source name + "last updated" on every displayed item  `[Mike]`

Credibility comes from *whose* data is shown. Every card (official statements, news, schools, shelters, videos) must show its source and a freshness timestamp. `status.json` already carries `source_url`, `time_iso`, `fetched_iso`, and top-level `last_updated_iso`.

**Files:**
- Modify: `dashboard.html` — statement/source render (`~:1927`, `~:2008-2023`) to show source name + relative "updated" time per item.
- Modify: `eval/test_provenance.py` — assert every official statement has a source and timestamp.
- Test: `eval/test_provenance.py`.

- [ ] **Step 1: Write failing provenance test**

```python
def test_every_statement_has_source_and_time():
    import json
    s = json.load(open("status.json", encoding="utf-8"))
    for st in s["official_statements"]:
        assert st.get("source_url"), f"statement missing source_url: {st}"
        assert st.get("time_iso"), f"statement missing time_iso: {st}"
```

- [ ] **Step 2: Run, confirm pass/fail** — Run: `python -m pytest eval/test_provenance.py -v`. If it already passes (data is clean), proceed to the UI assertion below; add a DOM-string check that the render template includes the source + updated label.

- [ ] **Step 3: Update the render** so each item shows `{agency/outlet} · updated {relativeTime(time_iso)}` with the source link.

- [ ] **Step 4: Verify + commit**

```bash
git add dashboard.html eval/test_provenance.py
git commit -m "feat(ui): show source + last-updated on every item"
```

**Acceptance criteria:** Every visible data card shows a source name and a relative freshness timestamp; provenance test passes. **Blocked by:** none.

---

## Task 3: AI-use disclosure (Anthropic Usage Policy)  `[Mike]`

The data pipeline summarizes official sources with an AI model (`scripts/gather_facts.py`, `refresh_local.py` via `claude -p`). Outputs are consumer-facing, so Anthropic's Usage Policy requires a disclosure that AI helps produce the content (see AnthropicAlignment report, Finding 1).

**Files:**
- Modify: `dashboard.html` — add a persistent, plain-language disclosure near the header/footer and (ideally) at first load.
- Modify: `STRINGS` — new key `disclosure.ai` (EN + VI in Task 4).

- [ ] **Step 1:** Add a `disclosure.ai` string: "Summaries on this page are compiled with AI assistance from official and news sources, then checked by a person. Always confirm life-safety information with official channels."
- [ ] **Step 2:** Render it where every visitor sees it each session (header subtext or a dismissible-but-returns banner).
- [ ] **Step 3: Commit**

```bash
git add dashboard.html
git commit -m "feat(trust): add AI-assistance disclosure per usage policy"
```

**Acceptance criteria:** A clear AI-assistance disclosure is visible to every visitor at the start of each session. **Blocked by:** none.

---

## Task 4: Ship Vietnamese (flagship)  `[Nancy/Nancy]`

The framework is built (`STRINGS`, `LANGS`, `t()`, `ready` flag; G1 = native-verified only, never machine translation, English fallback). This task lands Nancy-verified Vietnamese for the safety-critical keys (including the **new** Task 1/3 router + disclosure strings) and flips `vi.ready = true`.

**Files:**
- Modify: `dashboard.html` — `STRINGS` (`~:1048+`) add verified `vi:` values for every key, prioritizing the router (`check.router.*`), disclosure (`disclosure.ai`), breaking-alert, and the official-link labels; `LANGS` (`~:1206`) flip `vi` `ready: true`.
- Reference: `docs/LANGUAGE_ACCESS.md` (binding G1).

- [ ] **Step 1:** Hand Nancy the full English `STRINGS` set with the new Task 1/3 keys flagged safety-critical; she returns verified Vietnamese.
- [ ] **Step 2:** Enter verified `vi:` strings under each key. Any unverified key stays English (G1 fallback) — never machine-translated.
- [ ] **Step 3:** Flip `vi.ready = true` in `LANGS` only once the safety-critical keys are verified.
- [ ] **Step 4:** Verify EN↔VI toggle on the router message, disclosure, and breaking alert.
- [ ] **Step 5: Commit**

```bash
git add dashboard.html docs/LANGUAGE_ACCESS.md
git commit -m "feat(i18n): ship native-verified Vietnamese for safety-critical copy"
```

**Acceptance criteria:** Vietnamese appears in the picker; all safety-critical copy (router, disclosure, breaking alert, official links) renders in verified Vietnamese; no machine-translated string ships (G1). **Blocked by:** Nancy's verification (human long-pole, not code).

---

## Task 5: Route-to-official panel  `[Mike]`

A single, prominent "Official sources" panel that routes residents outward: official address/zone checker, evacuation-zone lookup, official alert sign-ups, and air quality.

**Files:**
- Modify: `dashboard.html` — add an "Official sources" section.
- Modify: `STRINGS` — labels (EN + VI).

- [ ] **Step 1:** Add links: `ggcity.org/emergency` (official checker, already in `status.json`), the OC/Genasys evacuation-zone lookup, official alert sign-up (OC Alert / WEA info), and EPA AirNow for air quality. Each labeled "official," opens in a new tab, with source name shown.
- [ ] **Step 2:** Add the "no single source should be your only one" line per Ready.gov guidance.
- [ ] **Step 3: Commit**

```bash
git add dashboard.html
git commit -m "feat(conduit): add official-sources routing panel"
```

**Acceptance criteria:** Every official channel is one tap away and clearly labeled official; copy tells users to also subscribe to official alerts. **Blocked by:** none.

---

## Task 6: One-page Code of Conduct  `[Mike]`

Watch-Duty-style editorial discipline, published so the conduit posture is explicit and enforceable.

**Files:**
- Create: `docs/CODE_OF_CONDUCT.md`.
- Modify: `dashboard.html` — footer link to it (or to `terms.html` which references it).

- [ ] **Step 1:** Write the one-pager: only bona-fide official/named sources; no hearsay; no editorializing a directive (we issue none); no PII; accuracy over speed; corrections policy; AI-assistance + human-check note.
- [ ] **Step 2:** Link it from the footer.
- [ ] **Step 3: Commit**

```bash
git add docs/CODE_OF_CONDUCT.md dashboard.html
git commit -m "docs: add information-conduit code of conduct"
```

**Acceptance criteria:** `docs/CODE_OF_CONDUCT.md` exists, is linked from the UI, and states the no-directive / official-source-only rules. **Blocked by:** none.

---

## Task 7: Direct official-feed ingestion  `[Mike]`

Reduce reliance on hand-curated news by pulling official feeds at the source. Start with EPA AirNow (concrete API, air-quality is directly relevant to a chemical release); design for CAP/IPAWS + NWS later.

**Files:**
- Modify: `scripts/gather_facts.py` — add an AirNow fetch (current AQI by lat/lon from `config.json:map.facility`) writing into `status.json` with `source: "EPA AirNow"` + `fetched_iso`.
- Modify: `eval/test_schema.py` — assert the new `air_quality` block shape.
- Modify: `dashboard.html` — render AQI with source + timestamp (reuses Task 2 pattern).

- [ ] **Step 1:** Write a failing schema test for an `air_quality` block (`aqi`, `category`, `source`, `fetched_iso`).
- [ ] **Step 2:** Implement the AirNow fetch (API key via env var; **name the dependency and get approval before adding any new Python package** per §6 — `requests`/stdlib only if possible).
- [ ] **Step 3:** Render it; run `python -m pytest eval/test_schema.py -v`.
- [ ] **Step 4: Commit**

```bash
git add scripts/gather_facts.py eval/test_schema.py dashboard.html
git commit -m "feat(data): ingest EPA AirNow air quality at source"
```

**Acceptance criteria:** AQI shows on the dashboard sourced from AirNow with a timestamp; schema test passes. CAP/IPAWS + NWS ingestion captured as a follow-up, not built here. **Blocked by:** AirNow API key (free, self-serve).

---

## Lane B: Org / legal structure (parallel, mostly non-code)

These run alongside Lane A. **They do not block the code tasks above, but the attorney review BLOCKS public launch (removing `noindex` in `vercel.json`).** See `docs/DISTRIBUTION.md` G1 and `docs/LEGAL.md`.

- [ ] **B1 — Entity:** Form a California nonprofit public-benefit corporation, or start under a fiscal sponsor for speed. Gives founder/volunteers the same shield as an LLC + 501(c)(3) standing. *(HelpSafely report, Finding 2.)*
- [ ] **B2 — Insurance:** Bind **Media/Publishers Liability + E&O** (covers the info service itself; D&O's professional-services exclusion does not) plus CGL and D&O. California has no charitable-immunity statute, so insurance is load-bearing.
- [ ] **B3 — Attorney review (BINDING PRE-LAUNCH BLOCKER):** Licensed CA attorney reviews the conduit structure, disclaimers (intent-framing, not a gross-negligence cure per Civ. Code §1668), the **translation workflow** (a mistranslated official directive is itself a misrepresentation — translations marked unofficial + linked to the official original), and the §230/fair-report posture. *(Already tracked in `distribution-gating-constraints` memory.)*
- [ ] **B4 — Disclaimers:** Update `terms.html` so disclaimers frame intent/reliance (negate §552 intended-reliance, show good faith) without pretending to waive liability. Attorney-reviewed (B3).

**Gate:** Do not remove `noindex` from `vercel.json` / publicly promote until B3 clears.

---

## Self-review notes

- **Spec coverage:** Lane A flagship translation (T4), feed ingestion (T7), route-to-official (T5), opt-in push (already in architecture; no change needed beyond keeping zero-promo content — verify in T5), WCAG/plain-language (apply to T1/T5 copy; existing framework already plain-register), Code of Conduct (T6), sim-internal (T1 removes the resident-facing path). Lane B entity/insurance/attorney (B1-B4). All mapped.
- **No authored directives:** Task 1 removes the only resident-facing authored verdict. Every other task either relays official content or routes to it.
- **TDD reality:** data/logic tasks (T1, T2, T7) use the existing `eval/` harness test-first; copy/UI/org tasks use explicit acceptance criteria + manual verification (no fabricated test theater).
- **Open follow-ups (not in this plan):** CAP/IPAWS + NWS ingestion; Spanish + Korean (Tier 1/2 per `LANGUAGE_ACCESS.md`); accessibility audit to formal WCAG 2.1 AA.
