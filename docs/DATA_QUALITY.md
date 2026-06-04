# DATA_QUALITY — pipeline hardening + eval-test design

**Workstream:** Data-Quality (distribution-readiness)
**Owner deliverable:** this spec. Implementation lands later on `feat/data-sync`.
**Status:** design only — no code changed.

> **Historical design spec (frozen archive).** This was a pre-resolution hardening spec for `feat/data-sync`. The incident resolved before it was implemented; the recommendations below were not shipped. Retained as a design-decision record.
**Scope of the pipeline under review:**

```
GitHub Actions cron (*/20)
  → scripts/gather_facts.py   (Anthropic Messages API web_search → facts JSON on stdout;
                               non-zero exit + empty stdout on failure)
  → scripts/update_status.py  (facts on stdin → status.json; severity hysteresis,
                               breaking detection, breaking_events.jsonl)
  → git commit status.json [skip ci]  → Vercel auto-deploy
```

This is a free, volunteer-built, **unofficial** dashboard for an active life-safety
incident (~50,000 evacuated). The governing principle for every recommendation
below: **a wrong "you're safe" is far more harmful than a wrong "still dangerous."**
The pipeline must fail *visibly stale*, never *confidently wrong*.

> **Note on the partial-facts severity bug.** It is already FIXED in
> `update_status.py:228-235` (severity is only re-derived when this tick actually
> supplies a severity-relevant key; a partial dict carries severity forward) and
> covered by `eval/test_writer.py::test_partial_facts_dont_downgrade_severity`.
> This spec treats it as *mitigated-with-regression-test* and recommends keeping
> that test green, not as an open defect.

---

## 1. Failure-mode map

Likelihood: how often it plausibly happens over a multi-day incident.
Harm: worst-case user-visible consequence (life-safety weighted).

| # | Failure mode | Likelihood | User-visible harm | Current mitigation | Gap |
|---|---|---|---|---|---|
| F1 | **Fabricated all-clear** — model asserts `incident_resolved_iso` or `evacuation_lifted: true` with no/weak basis | Med | **Catastrophic.** Severity drops to `low`, an URGENT "INCIDENT RESOLVED / Evacuation LIFTED" banner fires. A sheltering resident reads "all clear" and stops evacuating. | Gatherer prompt says "don't guess"; defaults `lifted=false`. Severity is *derived*, not extracted. | No corroboration requirement. A single hallucinated boolean flips the dashboard to safe. **Highest-value gap.** |
| F2 | **Fabricated source URL / quote / agency** in `official_statements` or `sources_checked` | Med | High. Dashboard cites a non-existent OCFA statement; users trust a fabricated quote; archive integrity destroyed. | Prompt forbids fabrication. `sources_checked` is backfilled from real `web_search` citations *only when the model left it empty*. | URLs the model *does* emit are trusted verbatim — never checked against the citations actually retrieved this run, never URL-validated. `official_statements[].source_url` is never validated at all. |
| F3 | **Hallucinated numeric fact** — invented `tank_temp_f`, `evacuation_residents`, `injuries` | Med | High. `injuries > 0` flips severity to `critical` (false alarm); a fabricated residents count moves the breaking banner. | Writer holds prev on a >50% residents drop without `lifted` (`update_status.py:264`). Writer clamps temp 0–500 only in the *schema test*, not at write time. | Gatherer does zero numeric sanity. `injuries` and `tank_temp_f` have no bounds at write time. A plausible-but-wrong number passes. |
| F4 | **Stale-but-fresh-stamped** — gatherer returns valid-but-empty/unchanged JSON (exit 0), writer stamps `last_updated_iso = now` on old data | Med | High. Staleness banner never fires; user believes data is current when no new fact was confirmed for hours. | Gatherer exits non-zero on hard failure, so the writer step is skipped. | A *soft* failure (model returns `{}` or all-null with exit 0) still produces a fresh write. `last_updated_iso` advances even with empty facts (`main()` warns but writes). No "data age" distinct from "write age". |
| F5 | **Severity miscompute (partial facts)** — partial dict recomputes severity from zeros | Low | High (false downgrade). | **Fixed** (`:228-235`) + regression test. | None — keep the test green. Watch for new severity-relevant fields added to the gatherer but not to `severity_relevant_keys`. |
| F6 | **web_search returns nothing** — model emits an all-null facts blob | Med | Med. All fields null → writer keeps prev (good) but `last_updated_iso` still advances (see F4). | Writer's fall-through-to-prev keeps values. | Gatherer doesn't enforce a citation/result floor; SPEC's "all sources returned empty (suspicious)" log line is *not* implemented. Couples with F4. |
| F7 | **Citation parse failure / no provenance** — model omits `sources_checked` and citations are absent/unparseable | Low | Med. Snapshot has no provenance; "Verified from N sources" reads 0; commit audit trail loses traceability. | Backfill loop reads `b.citations`. | If both the model list *and* citations are empty, `sources_checked = []` silently. No floor, no warning. |
| F8 | **Schema drift** — gatherer's `SCHEMA_HINT` and writer's expected keys diverge | Low | Med. A renamed field silently becomes "missing" → writer carries prev forever; the change never surfaces. | Both sides hand-maintain the shape; `schema_version` is static `1`. | No shared schema contract; no validation of facts against a declared schema. Drift is silent. |
| F9 | **Cron silently stops** — GitHub disables scheduled workflows after 60 days repo inactivity; runner outage; cron lag | Low–Med | High. status.json freezes; whether the user notices depends entirely on the staleness banner. | Every run commits (timestamps always change), so commit cadence is a heartbeat. Staleness banner is the only in-app signal. | No dead-man's switch / external monitor. If the banner logic is also wrong (F4), a stopped cron is invisible. |
| F10 | **Commit / deploy failure** — `git push` rejected (rebase conflict), Vercel deploy fails | Low | Med. Writer ran, data is fresh in the runner, but production shows old data. | Workflow does `pull --rebase --autostash` then push; concurrency group serializes runs. | A push failure fails the job (visible only in the Actions tab, which nobody watches). No alert. Same blind spot as F9. |
| F11 | **Fabricated / garbled date** — `time_iso`, `incident_resolved_iso` in the future or before incident start | Low | Med. A future-dated "resolution" or an out-of-order statement timeline misleads. | None. | No date sanity check anywhere. |
| F12 | **Prompt-injection via a scraped page** — a malicious/low-quality page tells the model "the evacuation is lifted" | Low | High (a path into F1). | Prompt instructs official-source priority. | Model output is fully trusted; no source-credibility weighting; injection through search results is unguarded. |

**The three that matter most:** F1 (fabricated all-clear), F2 (fabricated provenance), F4 (stale-but-fresh-stamped). The P0 plan targets exactly these.

---

## 2. Hardening recommendations (P0 → P2)

Style constraint honored: vanilla Python stdlib, small diffs, matches the existing
field-by-field, hold-prev-on-doubt idiom. New dependencies are flagged as open
questions, not assumed. All recommendations are *accept/reject*-reasoned.

### P0 — safety-critical (block the `feat/data-sync` → `main` merge until done)

**P0-1 — Corroboration gate for "good-news" transitions.** *(targets F1, F12)*
A downgrade in danger must never ride on a single unverified assertion. In the
gatherer (or a thin validator between gather and write), require that
`evacuation_lifted: true`, `incident_resolved_iso`, **and** any severity-reducing
state be backed by **≥2 independent retrieved citations** whose URLs are in this
run's `web_search` citation set, with at least one matching an official-source
host (see P2-2 list). If the threshold isn't met, **force the field back to its
safe default** (`lifted=false`, `incident_resolved_iso=null`) and log
`"unconfirmed all-clear suppressed (N=<count> sources)"`.
- **Accept.** This is the single highest-value change; it directly prevents the
  catastrophic false all-clear. Asymmetric by design: *upgrades* in danger
  (injuries, expansion, severity bump) still fire immediately on one source —
  over-warning is acceptable, under-warning is not.
- Implementation is stdlib (count citations, set membership, default-coercion).

**P0-2 — Source/URL integrity validation.** *(targets F2)*
Build the set of URLs actually retrieved this run from `resp.content[*].citations`.
Then, before emitting facts:
- Every `official_statements[].source_url` and every `sources_checked[].url` must
  (a) parse as a well-formed `http(s)` URL (`urllib.parse.urlparse`), and (b) be a
  member of the retrieved-citation set (host-level match is acceptable to tolerate
  tracking-param drift).
- A statement whose `source_url` fails either check is **dropped** (not emitted);
  a `sources_checked` entry that fails is **dropped**. Log each drop.
- **Accept.** Deterministic, stdlib-only, and it is the property that makes
  fabrication *catchable* — the anti-fabrication tests in §3 assert exactly this.
- **Reject** the weaker alternative of "warn but keep": a fabricated citation that
  survives into `status.json` is committed to the git audit trail forever. Drop it.

**P0-3 — Freshness honesty: separate data-age from write-age.** *(targets F4, F6)*
Add a `data_as_of_iso` field that advances **only** when this tick produced at
least one corroborated, non-null, source-backed fact. Keep `last_updated_iso` as
the write/heartbeat time. The staleness contract (§4) keys off `data_as_of_iso`.
- In the gatherer: if the result has zero usable citations or an all-null facts
  body, **exit non-zero and print nothing** (same contract as a hard failure) so
  the writer step is skipped and `data_as_of_iso` does not move. This also
  implements SPEC §"Distinguish 0-results vs rate-limit".
- In the writer: set `data_as_of_iso = now` only when `facts` is non-empty *and*
  carried at least one source-backed field; otherwise inherit prev `data_as_of_iso`.
- **Accept.** Without this, a writer that runs but learns nothing looks fresh —
  the most insidious failure because nothing visibly breaks.
- Requires a coordinated `schema_version` bump (see open questions) and the
  News-UX frontend reading the new field (§4 handshake).

### P1 — important (should be green before relaunch; not strictly merge-blocking)

**P1-1 — Date sanity.** *(F11)* Reject any ISO timestamp later than `now + 5 min`
or earlier than the incident start (`2026-05-21T00:00:00Z`, from `config.json`).
Out-of-range `time_iso` → drop the statement; out-of-range `incident_resolved_iso`
→ null it (and thus it can't trip P0-1). Stdlib `datetime`. **Accept.**

**P1-2 — Numeric bounds at the gather boundary.** *(F3)* Mirror the schema test's
ranges *before* the data is trusted: `tank_temp_f` 32–1000, `evacuation_residents`
0–2,000,000, `evacuation_area_sq_mi` 0–500, `injuries` 0–10,000. Out-of-range →
null + log; never pass garbage downstream. **Accept** — cheap, and `injuries`
out-of-range is a direct severity-to-critical false alarm.

**P1-3 — Search/citation floor.** *(F6, F7)* If the model used 0 web searches or
returned 0 citations, treat as gather failure (P0-3 path). If `sources_checked`
ends up empty after validation, that's also a failure. **Accept** — a snapshot
with no provenance should never be published for a life-safety dashboard.

**P1-4 — Severity-change guardrail (asymmetric).** *(F1, F5)* Make explicit and
test the rule already implied by the code: severity may rise on one tick; it may
only *fall* when backed by P0-1 corroboration (lifted/resolved) — never as a side
effect of a partial or empty facts dict. **Accept**; largely codifies existing
behavior plus P0-1, mainly a test surface (§3).

**P1-5 — Structured run logging.** *(F4, F6, F9, F10)* Have the gatherer print one
structured JSON line to **stderr** per run: `{run_iso, searches_used,
citations_count, fields_nonnull, exit_reason}`. The workflow already captures
stderr in the Actions log; this makes "why did this run write nothing" diagnosable
without a re-run. **Accept** — stderr-only, zero deps, no effect on the stdout
facts contract.

### P2 — nice-to-have

**P2-1 — Dead-man's switch.** *(F9, F10)* The cron commits every ~20 min, so a gap
in `status.json` commit history *is* the outage signal. Options evaluated:
- *External cron-monitor ping* (e.g. healthchecks.io free tier): the workflow
  curls a check-in URL on success; the monitor alerts if no ping in 45 min.
  **Accept as the recommended option** — it survives the GitHub-disables-the-cron
  case (F9), which a self-hosted check cannot. Adds one external dependency
  (flagged in open questions) but no code dependency.
- *Second GitHub workflow that checks commit age*: **Reject** — it dies the same
  way the primary cron dies (GitHub disables both after inactivity), so it can't
  detect the very failure it's meant to catch.

**P2-2 — Source-credibility allowlist (soft).** *(F2, F12)* Maintain a small
stdlib `set` of authoritative hosts: `ocfa.org`, `ocsheriff.gov`,
`ggcity.org`, `caloes.ca.gov`, `epa.gov`, `aqmd.gov`, plus established outlets
(`latimes.com`, `ocregister.com`, `ktla.com`, `abc7.com`). Use it two ways:
(1) P0-1's "≥1 official source" check; (2) tag non-allowlist sources in
`sources_checked` with a `"trusted": false` flag for the frontend to de-emphasize.
- **Accept as a *soft* signal** (label + one official-source requirement for
  downgrades). **Reject a *hard* allowlist** that drops non-listed sources: in a
  fast-moving emergency, legitimate breaking info surfaces on unexpected hosts;
  hard-dropping them would suppress real signal. The list lives inline as a Python
  `frozenset` — no new dependency.

**P2-3 — Shared schema constant.** *(F8)* Extract the facts shape into a single
`scripts/facts_schema.py` constant imported by both gatherer and writer, and add a
key-presence check. **Accept in principle, low priority** — the two files live on
`feat/data-sync` and a shared module is a small refactor; the schema test (§3)
catches drift in the meantime.

---

## 3. Eval-test design

All tests follow the existing harness convention: a `test_*` function returning
`{"passed": bool, "details": str, "metrics": dict}`, auto-discovered by
`run_all.py`, pure stdlib, classified via a module-level `CATEGORY`. New files
slot in beside the current `test_*.py`. **Deterministic tests gate CI; LLM-judged
evals are periodic/manual** (cost + nondeterminism — kept out of the merge gate).

### 3.1 New file: `eval/test_gather_facts.py` *(CATEGORY = "behavioral")*

Unit tests for the gatherer's *pure* functions and its failure contract. No live
API — the network path is never exercised here.

| Test | Asserts | Fixture | Pass/fail |
|---|---|---|---|
| `test_extract_json_strips_fences` | ```` ```json {…} ``` ```` and bare prose-wrapped JSON both parse | inline strings | dict equals expected |
| `test_extract_json_rejects_garbage` | input with no `{…}` raises `ValueError` | inline | raises, not silent `{}` |
| `test_graceful_failure_no_api_key` | run `scripts/gather_facts.py` as a subprocess with `ANTHROPIC_API_KEY` unset → exit `2`, **stdout empty** | none (env-controlled) | exit≠0 **and** `len(stdout.strip())==0` — the "never print on failure" contract (F4) |
| `test_url_validation_drops_fabricated` *(after P0-2)* | given a citation set `{A,B}` and a statement citing `C`, the validator drops the statement | inline | fabricated-URL statement absent from output |
| `test_url_validation_keeps_real` *(P0-2)* | a statement citing `A` (in set) survives | inline | present |
| `test_date_sanity_nulls_future` *(P1-1)* | `incident_resolved_iso` 1 year in the future → coerced to null | inline | null, logged |
| `test_numeric_bounds_null_garbage` *(P1-2)* | `injuries: 999999`, `tank_temp_f: 5000` → null + logged | inline | nulled, severity not flipped |
| `test_corroboration_suppresses_single_source_allclear` *(P0-1)* | `evacuation_lifted:true` with 1 citation → forced back to `false` | inline | `lifted==false`, suppression logged |

`test_graceful_failure_no_api_key` is implementable **today**, deterministically,
with no key and no network — it is the immediate, highest-confidence regression
for the "fail visibly stale, never confidently wrong" contract. The P0-2/P0-1/P1
rows assume the validators land on `feat/data-sync`; until then they document the
target behavior (write them as `xfail`-style known-gaps so the suite still passes).

### 3.2 New file: `eval/test_provenance.py` *(CATEGORY = "behavioral")* — **anti-fabrication, highest value**

Runs the writer in a sandbox (reuse `test_writer.py`'s `_reset_sandbox` / `_tick`
pattern) and asserts the snapshot can never carry invented provenance or a
single-source all-clear. **These are the tests that would actually *catch*
invented sources/URLs/dates** — the briefing's top safety property.

| Test | Asserts | Pass/fail |
|---|---|---|
| `test_fabricated_source_url_not_in_snapshot` | feed an `official_statements` entry with a `source_url` not present in any retrieved/known set; after P0-2 the snapshot's statements must not contain it | fabricated URL absent |
| `test_statement_without_source_url_rejected` | a statement with empty/missing `source_url` is dropped or flagged untrusted | not silently published as authoritative |
| `test_sources_checked_all_wellformed` | every `sources_checked[].url` in the snapshot passes `urlparse` (scheme in {http,https}, non-empty netloc) | all well-formed |
| `test_resolved_requires_two_sources` *(P0-1)* | `incident_resolved_iso` + 1 source → severity NOT `low`, no "RESOLVED" breaking; + 2 official sources → honored | asymmetric gate holds |
| `test_lifted_requires_corroboration` *(P0-1)* | `evacuation_lifted:true` + 1 source → `lifted` stays false, no "LIFTED" banner | false all-clear blocked |
| `test_future_resolved_date_ignored` *(P1-1)* | `incident_resolved_iso` in the future → ignored, no resolution | not honored |

### 3.3 New file: `eval/test_freshness.py` *(CATEGORY = "behavioral")*

Sandbox writer runs, focused on the staleness contract (§4).

| Test | Asserts | Pass/fail |
|---|---|---|
| `test_stale_after_is_data_as_of_plus_maxage` | `stale_after_iso == data_as_of_iso + max_age` (not write time) | equality within 1s |
| `test_empty_facts_do_not_advance_data_as_of` *(P0-3)* | tick 1 with real facts sets `data_as_of_iso`; tick 2 with `{}` must **not** advance it (while `last_updated_iso` may advance) | `data_as_of_iso` unchanged |
| `test_all_null_facts_treated_as_no_data` *(P0-3/F6)* | a facts blob of all-null fields does not advance `data_as_of_iso` | unchanged |
| `test_last_updated_monotonic` | `last_updated_iso` never goes backwards across ticks | monotonic |

`test_empty_facts_do_not_advance_data_as_of` will **fail against today's code**
(which always stamps fresh) — that is intentional: it is the executable
specification of P0-3 and turns green only when the fix lands.

### 3.4 Extend existing `eval/test_schema.py`

Add, behind a presence check so it passes pre-P0-3:
- `data_as_of_iso` present, ISO-Z shaped, and `<= last_updated_iso`.
- `stale_after_iso > data_as_of_iso`.
- (after P2-2) each `sources_checked` entry, if it has a `trusted` key, is a bool.

### 3.5 LLM-judged evals (the `rubrics/data_quality.md` precision/recall/hallucination judge)

Keep these **out of the per-PR CI gate** and run them periodically against a frozen
set, to keep them cheap and stable:
- **Frozen fixtures.** Seed `eval/fixtures/gold_extractions/tick_<ts>.json` with
  `{source_snippets, gold_facts}` pairs (5–10 ticks, hand-corrected). The judge
  scores the live extraction against the gold — inputs never change run-to-run.
- **Stability knobs.** Pin the judge model version, `temperature=0`, fixed prompt
  (already in the rubric). Treat composite `≥0.80` as the acceptable bar; a
  cross-judge spread `>0.15` means refine the rubric, not ship.
- **Cost control.** Run on relaunch and weekly (or on demand), never on every PR.
  Append results to `scores.jsonl` via the existing manual-score path.
- **Separation of concerns.** Deterministic unit/behavioral/schema tests assert
  *mechanics* (no fabrication survives, freshness honest, severity asymmetric);
  the LLM judge assesses *extraction quality* (did we miss a real fact, did we
  invent one). Different questions, different cadence.

---

## 4. Data-freshness contract (handshake → News-UX stream)

> **Cross-stream handshake.** This section defines the signal; the News-UX stream
> (`docs/NEWS_UX_SPEC.md`) consumes it to render the stale/very-stale treatment.
> The orchestrator routes the agreement. The single most important line: **the
> frontend must key staleness off `data_as_of_iso`, not `last_updated_iso`.**

**Fields the frontend trusts:**

| Field | Meaning | Set when |
|---|---|---|
| `last_updated_iso` | Write/heartbeat time — when the writer last produced the file. | Every successful write. |
| `data_as_of_iso` *(NEW, P0-3)* | When the underlying facts were last actually confirmed from a source. | Only on a tick with ≥1 corroborated, source-backed fact. |
| `stale_after_iso` | The moment the data should be considered stale. | `data_as_of_iso + MAX_AGE`. |
| `next_check_at_iso` | Informational: when the next cron tick is expected. | `now + interval`. |

**Definitions (recommended constants):**
- `MAX_AGE = 40 min` (2× the `*/20` cron interval — tolerates one missed run plus
  GitHub's 5–15 min cron lag).
- **stale** = `now > stale_after_iso` → amber banner: *"Data may be stale — last
  confirmed N min ago."* (SPEC's existing staleness copy applies.)
- **very stale / writer-down** = `now > data_as_of_iso + 90 min` → red banner:
  *"The updater appears to have stopped; treat all values as outdated. Rely on
  official sources (Ready OC / OCFA)."*
- The dashboard should always show the **age of `data_as_of_iso`** in plain
  language ("confirmed 8 min ago"), never the write time — write time can be fresh
  while data is hours old (F4).

**Why two timestamps:** the entire stale-but-fresh-stamped failure class (F4/F6)
collapses if "we wrote the file" and "we learned something new" are distinct
signals. The frontend's stale logic becomes correct by construction.

---

## 5. CI integration — gating the paid cron and the merge to `main`

**Goal:** nothing reaches production (the paid cron writing live `status.json`)
until the deterministic safety suite is green.

**Required check on every PR (including `feat/data-sync` → `main`):**
```
python eval/run_all.py --skip integration
```
- Runs behavioral + schema tests; `--skip integration` excludes the live Nominatim
  geocoder (no network needed in CI). Exit 0 required to merge.
- Add a GitHub Actions workflow `ci-eval.yml` triggered `on: [pull_request]`,
  Python 3.12, no secrets, no network. (Distinct from the `*/20` writer workflow —
  this one only runs tests.)

**Merge-blocking bar for `feat/data-sync` → `main` (the gate before the paid cron
is allowed to write production):**
1. All `test_writer.py`, `test_schema.py`, `test_freshness.py`,
   `test_provenance.py`, `test_gather_facts.py` green.
2. `test_gather_facts.py::test_graceful_failure_no_api_key` green — proves the
   "fail visibly stale, never confidently wrong" contract end-to-end with no key.
3. P0-1/P0-2/P0-3 validators landed and their named tests green (no longer
   known-gap stubs).
4. One manual LLM-judge run on the gold fixtures returns composite `≥0.80`
   (acceptable band) — recorded in `scores.jsonl`. Advisory, surfaced in the PR
   body, not auto-run.

**Optional but recommended — deterministic end-to-end gate.** Record one real
Anthropic web_search response to a committed fixture (a VCR-style cassette) and add
`test_pipeline_e2e.py` that replays it through `gather_facts → update_status` with
the network stubbed, asserting a schema-valid `status.json`. This exercises the
full pipeline in CI without spending API credits. (Depends on the open question
about committing a captured model response.)

**Production-write safety:** the `*/20` workflow itself stays unchanged in
structure; its safety comes from the gatherer's fail-closed contract (non-zero +
empty stdout → writer skipped → data goes visibly stale). CI's job is to keep that
contract — and the P0 validators — from regressing.

---

## 6. Open questions for the user (flag, not resolve)

1. **New dependency for source reputation (P2-2).** Stay stdlib-only with an inline
   `frozenset` of ~10 authoritative hosts (recommended), or pull a maintained
   source-reputation list? Inline keeps the zero-dep posture; a list is more
   complete but adds a dependency and a maintenance surface.
2. **Cron cadence vs API cost at relaunch.** `*/20` ≈ 72 paid web-search calls/day.
   Is that the right floor, or should cadence widen (e.g. `*/30`, matching the
   30-min staleness design) to cut cost, or tighten during active escalation?
   Affects `MAX_AGE` in §4.
3. **`data_as_of_iso` + `schema_version` bump.** Adding the field is a schema
   change. Bump `schema_version` to `2` and have the frontend show the existing
   "schema changed, refresh page" banner on mismatch? Needs News-UX coordination.
4. **Corroboration threshold N (P0-1).** Is **2 independent citations, ≥1 official**
   the right bar for honoring an all-clear, or stricter (≥2 official)? Stricter is
   safer but risks lagging a real all-clear by a tick or two.
5. **Fail-closed on zero citations (P0-3/P1-3).** Exiting non-zero when a quiet
   period genuinely produces no new citations would freeze `data_as_of_iso` and
   eventually trip the stale banner even though nothing is wrong. Acceptable
   (stale-but-honest), or should a "confirmed quiet, nothing changed" path advance
   freshness without new facts? Leans toward fail-closed for a life-safety tool.
6. **VCR cassette for the e2e CI gate (§5).** OK to commit a captured Anthropic
   web_search response (scrubbed of any key) as a test fixture for deterministic
   end-to-end coverage?

---

## Appendix — current-state quick reference (read-only findings)

- **Gatherer trust boundary:** model output is trusted verbatim except that
  `sources_checked` is citation-backfilled *only when empty*. No URL/date/numeric
  validation; no corroboration requirement. Fails closed on hard errors (good).
- **Writer protections that already exist:** severity is *derived* not extracted;
  partial-facts severity carry-forward (`:228-235`); suspicious-residents-drop hold
  (`:264`); atomic write with Windows-lock retry; first-run never breaks; breaking
  decay (30 min) and residents rate-limit (120 min); URGENT vs INFO classification.
- **Writer gap:** `last_updated_iso` advances on every successful write, including
  empty-facts ticks — the root of the stale-but-fresh-stamped class (P0-3 fixes it).
- **Workflow:** `*/20` cron, `concurrency` serializes runs, `permissions:
  contents: write`, commits `[skip ci]`, `pull --rebase --autostash` before push.
  status.json is intentionally tracked (commit = audit trail + deploy trigger).
