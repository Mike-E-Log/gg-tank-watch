# GG Tank Watch — Fable 5 comprehensive audit (2026-07-21)

**Status: fixes applied 2026-07-21 via PRs #65, #66, #67** (filed report-only earlier the same day; the annex at the end records what was applied and what stays pending). Frozen-archive corrections follow the rule "annotate, don't substitute": items keep their collected URLs and outlets as the historical record, and rechecks land as dated provenance annotations. The one field-value correction (the A1 outlet label) was individually approved.

Method: a stronger-model pass over the whole repo, run as a 4-lane finder Workflow (provenance / docs-consistency / code-security / red-team) with adversarial Opus verification of each finding, plus a live 92-URL liveness sweep and live-site checks run directly from the main thread. 42 findings raised; **20 survived adversarial verification**, 6 were refuted, 16 lower-severity ones passed through unverified under the verification cap (listed but not independently confirmed). Every load-bearing claim below is tied to a file:line I or a verifier opened this run, or to a live HTTP check whose command is shown.

---

## BLUF

The archive's core content is sound and the live site is healthy (200, `noindex` on, served bytes semantically identical to repo HEAD). But the honesty thesis has **decayed in exactly the way the project feared**: the 2026-06-04 audit's headline finding was a "verified" note on a dead link, and **there is now a second live instance** — plus a class of docs that under-state the safety work by claiming shipped gates were never built. None is safety-critical to a 2026 reader (the incident is resolved), but several are trust-surface falsehoods on the portfolio's centerpiece.

Top 5, in priority order:

1. **A second "verified"-labeled dead link is live right now** (ABC News wireStory URL → HTTP 404, recorded `agent-verified-resolves`). Same reader-facing symptom as the June-4 CRITICAL.
2. **Two docs claim the P0 safety gates were never shipped — they were.** `DATA_QUALITY.md` and `DATA_SYNC.md` contradict the code, the live snapshot, and the sibling architecture doc.
3. **Three of four archive counts are wrong** in `data/NEWS_ARCHIVE_AUDIT.md`, and its own data link is dead post-`public/` move.
4. **One data error in the frozen archive itself**: a federal-declaration item labels its outlet "White House / Federal" while the URL is California's state domain.
5. **The README overclaims "no outside servers in the map's critical path"** — OpenFreeMap tiles and Google Fonts are live third-party runtime dependencies.

---

## The headline finding: link rot has already recreated the June-4 defect

The June-4 audit's CRITICAL was a 404 URL paired with an `agent-verified-resolves` note asserting page details a 404 can't produce. A guard (`eval/test_news_archive_provenance_links.py`) locks out that **one specific slug** — but not the class. Seven weeks later, a live sweep of all 92 URLs finds the symptom back:

| Item | Recorded status | Live result (2026-07-21, browser-UA curl `-L`) |
|---|---|---|
| "Officials lift evacuation orders…" — ABC News, `…wireStory/…damaged-133303858` | `agent-verified-resolves`, note claims "WebFetch confirmed May 26 publish; ~34,000 residents partial lift" | **HTTP 404** |
| "GKN Aerospace Suffers Industrial Accident" — Aviation Week | `verified-resolves`, note "re-verified by main loop" | **302 → login wall** (`aviationweek.com/user/login`) |

Honest framing: `fetched_iso` for the ABC item is 2026-06-01, so the URL was **probably** live when fetched and has since rotted — I could not confirm either way (the Wayback Machine has **no snapshot** of it, checked this run). So this is most likely link rot, not a fresh fabrication. But the reader-facing failure is identical to the June-4 CRITICAL: the archive now vouches **"verified"** for a URL that 404s. That is the exact trust breach the whole audit apparatus exists to prevent, and nothing in the repo would have caught it.

Empirically, the rest of the 92: 72 clean 200s, ~16 bot-blocks that resolve fine in a real browser (CBS `406`, KTLA `403` — not defects), and the 2 above. So the confirmed rot rate is 2/92 after ~7 weeks. **F13 (below) is not hypothetical — this is it happening.**

Severity: **MAJOR** (reader-facing false "verified" on the honesty-thesis surface; not provably fabrication, so short of the June-4 CRITICAL).

Proposed fix: re-point both items to a live equivalent and rewrite provenance honestly, **or** add a `provenance_note` on the archive stating "verified as of the 2026-06 build; links may have rotted since" and (cheap structural option) store each item's verified title/date so a reader can detect drift. Generalize the guard from one slug to the class if any re-verification is ever run.

---

## A. Actual errors in the frozen archive (data)

### A1 — Outlet mislabel: "White House / Federal" on a California state URL — **MEDIUM (CONFIRMED)**
`public/data/news_archive.json` ~549-552: `"outlet": "White House / Federal"`, `"type": "official"`, but `"url": "https://www.gov.ca.gov/2026/05/25/governor-newsom-secures-presidential-emergency-declaration-approval…"` — the California Governor's Office domain. The item's **own** provenance note (~561) reads "Official California Governor's Office press release," self-contradicting the outlet label, and a sibling item (~1366-1368) uses `"State of California / Governor's Office"` for the same domain. `dashboard.html:2421` renders official items with `source: it.outlet`, so the wrong label is reader-facing. Fix: change outlet to "State of California / Governor's Office" to match the domain and the sibling.

### A2 — Two summaries assert specifics for never-fetched items — **MINOR (unverified-capacity; spot-checked plausible)**
- KTLA "Map shows potential blast zones" (~853-866): `url_status: unchecked`, yet summary asserts an "innermost severe-damage circle, moderate/light outward" ring structure the title doesn't support and no other item corroborates.
- NBC LA "Recap: … 'unprecedented' crisis (live blog)" (~1317-1331): `url_status: unchecked`, yet summary cites "drone temp readings and Tank #2 neutralizer" — the only other "drone" mention (~1395) is unrelated DA surveillance.

Fix: trim each summary to what the title supports, or fetch-and-verify before restoring the detail. (These are provenance hygiene, not fabrication — the status is honestly marked `unchecked`; the summary just outran it.)

> **Note (refuted, keep as-is):** the auditor initially flagged the `type:"official"` items whose `outlet` names an actor (OCFA, City of Garden Grove, the law firms) while the `url` is a news article. Verification **refuted** all of these — it's a documented, consistently-applied schema convention (outlet = the official actor, url = best fetch-verified documentation), corroborated by `config.json` shelter data. Not a defect.

---

## B. Actual errors in the docs (trust surfaces)

### B1 — `DATA_QUALITY.md` / `DATA_SYNC.md` claim the P0 gates were never shipped — they were — **MAJOR (CONFIRMED)**
`docs/DATA_QUALITY.md:5,7`: "Status: design only. No code changed… the recommendations below were not shipped." False against primary source: `scripts/update_status.py` implements `validate_provenance()` (line 138, "P0-2"), `apply_corroboration_gate()` (line 170, "P0-1"), P0-3 `data_as_of_iso` (lines 511-534), and `validate_dates()` (line 117, "P1-1"), all called in `main()` (570-572); `public/status.json:5` carries the live `data_as_of_iso`; the sibling `docs/AI_CONTROL_ARCHITECTURE.md` documents the same gates as **live**; and the eval suite tests them green. `docs/DATA_SYNC.md:62-64` repeats the same false "corroboration gate, URL-integrity are prompt-level only." The harm inverts the usual risk — it **under-states** shipped safety work on the centerpiece project. Fix: rewrite both to say P0-1/P0-2/P0-3 shipped (cite `AI_CONTROL_ARCHITECTURE.md`), only P1/P2 items remain unbuilt.

### B2 — `NEWS_ARCHIVE_AUDIT.md` counts wrong + dead self-link — **MAJOR (CONFIRMED)**
`data/NEWS_ARCHIVE_AUDIT.md:7`: "92 items (56 articles, 23 videos, 13 official statements) across 44 outlets." Actual (computed from `public/data/news_archive.json`): **57 articles, 23 videos, 12 official, 43 outlets** — three of four breakdown figures off by one. The same line's link `[news_archive.json](news_archive.json)` resolves to `data/news_archive.json`, which no longer exists after the PR #38 `public/` move. `eval/test_readme_archive_count.py` guards the README's copy of these numbers but never this file, which is why the README (correct) and this doc (drifted) diverged. Fix: correct to 57/23/12/43 and re-point the link to `../public/data/news_archive.json`.

### B3 — `eval/README.md` documents a NOAA/wind eval gap for a removed feature — **MAJOR (CONFIRMED)**
`eval/README.md:47`: "Wind data freshness. NOAA API call is in the dashboard JS… Could add a test_wind.py; not done yet." The wind indicator and its NOAA call were removed 2026-05-31 — zero `noaa`/`wind`/`weather` refs in `dashboard.html`, and `eval/test_wind_removed.py` enforces the removal. The doc presents a deleted feature as a live coverage gap. Fix: delete the bullet.

### B4 — `CITATION.cff` still says attorney-gated — **MEDIUM (CONFIRMED)**
`docs/CITATION.cff:11-13`: "kept behind a pre-distribution (attorney) review gate." Contradicts the settled 2026-06-09 decision (`DEPLOYMENT_READINESS.md:8-13` "retired, not pending"; `.github/SECURITY.md:14`; `CLAUDE.md:25` "do not re-raise the attorney/launch threads"). Fix: update the abstract to the settled posture.

### B5 — `README.md` method-repo snapshot count is stale — **MINOR (verified live this run)**
`README.md:142` says the method repo's `eval-summary.json` is "**198/198** as of that commit." The method repo's README now states **210/210** (203 behavior + 7 data-format; fetched `github.com/Mike-E-Log/gg-tank-watch-method` this run). The 198 number is two revisions stale. Fix: update to 210, or reword to avoid pinning a number that drifts.

### B6 — Four broken relative links in `docs/USAGE.md` — **MINOR (CONFIRMED)**
Lines 29/41/52: `eval/README.md`, `docs/DATA_SYNC.md`, and two bare `README.md#…` anchors all resolve against `docs/` and 404 on GitHub. Fix: `../eval/README.md`, `DATA_SYNC.md`, `../README.md#…`. (Anchor targets themselves are correct.)

### B7 — `AI_CONTROL_ARCHITECTURE.md` "~193 remaining tests" off by 3 — **MINOR (unverified-capacity)**
Line 165: 211 − 15 control tests = 196, not ~193. Fix: "~196."

### B8 — `terms.html` OC-wide hotline still undifferentiated — **MINOR (unverified-capacity)**
`terms.html:82` lists `714-628-7085 · 714-741-5444` under one "Hotlines:" label; the June-4 audit (fix #5) asked to relabel 628-7085 as the OC-wide line vs Garden Grove's 741-5444. Also echoed in `dashboard.html:2322` print view. The one June-4 fix not applied.

---

## C. New failure modes — red-team extension of FAILURE_ANALYSIS.md (F13+)

F1–F12 cover the live-pipeline era. These are frozen-archive-era modes, each grounded in a quoted repo fact. Proportionate mitigations only (this is a frozen site — a doc note counts).

| ID | Mode | Verdict | Sev | Cheapest mitigation |
|---|---|---|---|---|
| **F13** | Link rot silently decays "verified" provenance; only a single-slug denylist guards it | CONFIRMED (+ **live proof**, see headline) | MEDIUM | "verified as of 2026-06 build" note; optional Wayback URL per item |
| **F14** | A cited domain 200s but is resold/repurposed → serves different content under a "verified" label (invisible vs a 404) | CONFIRMED | MEDIUM | Store verified title/date so drift is detectable |
| **F15** | YouTube takedown / ID-reuse breaks or misattributes thumbnails (`i.ytimg.com/vi/<id>`) | unverified-capacity | MEDIUM | Disclose thumbnails are live; the "Watch on <outlet>" fallback already exists |
| **F16** | README "no outside servers in the map's critical path" is an **overclaim** — OpenFreeMap tiles + Google Fonts are live third-party deps with no bundled fallback | CONFIRMED | MAJOR | One-line README correction |
| **F17** | `ggtankwatch.org` registration lapse → squatter serves arbitrary content under a formerly-trusted emergency domain | CONFIRMED | MEDIUM | Registrar auto-renew + lock; record renewal owner in TODOS |
| **F18** | Cache-first service worker pins returning users on pre-correction content unless `CACHE_NAME` is bumped | CONFIRMED | MEDIUM | Release-checklist rule: any `public/` content change bumps `CACHE_NAME` |
| **F19** | Live CI badge renders red for billing/infra reasons → misread as broken software | unverified-capacity | MINOR | Drop live badge for the static one, or caption it |
| **F20** | Correction channel is a single personal Gmail — dies silently if abandoned/recycled | unverified-capacity | MEDIUM | Domain-owned alias, or "monitored through <date>" note |
| **F21** | `scores.jsonl` is git-tracked, append-only, still growing post-freeze → committed "history" never matches a fresh run; muddies "frozen" claim | unverified-capacity | MINOR | Gitignore it or truncate to the sealed snapshot |
| **F22** | Corrections here don't propagate to the sealed method-repo snapshot (readers may see uncorrected F1–F12) | unverified-capacity | MINOR | One-line note: method repo is a point-in-time extract; this repo is authoritative |

**F16 detail (the one worth acting on):** `README.md:224` "No outside servers in the map's critical path… the map can't vanish when a third-party server changes." Contradicted by `dashboard.html:2545,2579` loading `tiles.openfreemap.org/styles/{dark,liberty}` at runtime, `vercel.json` whitelisting that host, and `sw.js:77-84` deliberately **not** caching those cross-origin tiles (so no offline fallback). The bundled *library* ≠ a bundled *map*. Fix: "No outside server in the map *library* path (MapLibre GL is bundled); tiles are served live by OpenFreeMap and fonts by Google Fonts, both degrade gracefully if unavailable."

---

## D. Latent code / security defects (report-only)

All XSS findings are **latent, not live-exploitable today**: the pipeline is frozen and `status.json`/`config.json` are static, maintainer-clean committed snapshots. They matter only as defense-in-depth and if the pipeline is ever un-frozen — but they are real gaps and inconsistent with the escaping used elsewhere.

- **D1 — Unescaped innerHTML sinks (MEDIUM, CONFIRMED).** `dashboard.html:2263` builds `href="' + s.url + '"` and inserts `s.title` with no `escAttr()` (unlike every sibling in `buildFeedCardsHtml`/`buildFeedHtml`); `:2242-2244` concatenates each `schools_closed[]` entry raw. Both fields are LLM/web-search-sourced (`gather_facts.py`). `update_status.py`'s URL validator checks only scheme+hostname — a quote-carrying URL survives (reproduced this run: `urlparse('https://evil.example/x" onmouseover="alert(1)" y="')` → scheme/hostname both truthy). Fix: `escAttr()`-wrap these fields.
- **D2 — `CSP script-src 'unsafe-inline'` (MEDIUM, CONFIRMED).** Load-bearing for the app's inline `onclick` handlers, so CSP gives zero script-execution defense-in-depth against D1. Longer-term: nonce/hash + `addEventListener`.
- **D3 — `test_feed_escaping.py` covers only 2 of the ~6 innerHTML builders (MEDIUM, CONFIRMED)** → false assurance; `updateInfoData`, `renderInfoConfigData`, `setBanners`, `renderPrintContent` untested. Fix: extend the forbidden-pattern assertions to all builders.
- **D4 — SW cache-first can never hit its own precache (MEDIUM, CONFIRMED).** `dashboard.html:2486,2497,2512` fetch `status.json`/`config.json`/`news_archive.json` with `?t=Date.now()`, but `sw.js` precaches bare paths and `caches.match()` uses default (query-sensitive) matching → structural miss every load; each miss re-caches under a new timestamped key. The documented "serve cached copy instantly" never occurs. Fix: `caches.match(req, {ignoreSearch:true})`.
- **D5 — `run_all.py` exits 0 when zero tests run (MEDIUM, CONFIRMED).** A `--only`/`--skip` typo that matches nothing yields `TOTAL 0/0` and exit 0 (reproduced). A CI gate on exit code alone is silently satisfiable. Fix: `if total == 0: sys.exit(2)`.
- **D6 — CSP `frame-src youtube.com` is unused (MEDIUM, CONFIRMED).** No `<iframe>`/embed anywhere in `public/`; all videos are out-links. Over-permissive surface the reciprocal test doesn't catch. Fix: remove it.
- **D7 — dormant rebase-then-push paths ignore the rebase exit code (MINOR, unverified-capacity):** `scripts/refresh_local.py:137` and `.github/workflows/update-status.yml:56`. Dead today (freeze gate), but a future un-freeze would inherit the bug.
- **D8 — `update_status.py` residents-drop guard excludes `new_r == 0` (MINOR, unverified-capacity):** line ~436, `new_r > 0` lets a drop straight to 0 (without `lifted`) bypass the sanity guard — the most extreme case is the one uncovered.
- **D9 — `sw.js` STATIC_ASSETS omits `accessibility.html`/`terms.html` (MINOR, unverified-capacity):** in-app links fail for an offline PWA user.

---

## E. Verified clean (negative findings — worth recording)

- **Live site healthy:** `https://ggtankwatch.org/` → 200; `/dashboard.html` → `X-Robots-Tag: noindex, nofollow`; `ggcity.org/emergency` → 200.
- **No deploy drift:** served `data/news_archive.json` is **semantically identical** to repo HEAD (byte diff = CRLF only); served `sw.js` is `gg-tank-v90` matching repo.
- **Eval green:** `python eval/run_all.py --skip integration` → **211/211**, exit 0, this run.
- **Six auditor findings refuted** on verification (the `type:"official"` outlet convention ×4, a breaking-reason escaping path that isn't reachable, and a confidence-tier claim that misread the provenance). Recorded so they aren't re-raised.

---

## Fix priority (proposals — Mike's call; nothing applied)

| # | Sev | Finding | Surface | Effort |
|---|---|---|---|---|
| 1 | MAJOR | Second "verified" dead link (ABC wireStory 404; Aviation Week login-wall) | `news_archive.json` | re-point + honest note |
| 2 | MAJOR | Docs claim P0 gates never shipped (B1) | `DATA_QUALITY.md`, `DATA_SYNC.md` | reword |
| 3 | MAJOR | Archive counts wrong + dead link (B2) | `NEWS_ARCHIVE_AUDIT.md` | 1 line + link |
| 4 | MAJOR | Wind/NOAA eval gap for removed feature (B3) | `eval/README.md` | delete bullet |
| 5 | MAJOR | "No outside servers in map path" overclaim (F16) | `README.md` | 1 line |
| 6 | MEDIUM | Outlet mislabel White House→CA (A1) | `news_archive.json` | 1 field |
| 7 | MEDIUM | CITATION.cff attorney-gate (B4) | `CITATION.cff` | reword |
| 8 | MEDIUM | XSS defense-in-depth + test coverage (D1/D3) | `dashboard.html`, `test_feed_escaping.py` | escape + tests |
| 9 | MEDIUM | SW cache miss + pinning + zero-test exit (D4/D5/F18) | `sw.js`, `run_all.py` | small code |
| 10 | MEDIUM | Domain renewal note; correction-channel alias (F17/F20) | TODOS / config | doc + op |
| — | MINOR | B5–B8, D6–D9, F19/F21/F22, A2 | various | batch later |

> **Guard-the-guard suggestions:** generalize `test_news_archive_provenance_links.py` from one slug to any `*verified*` item's URL shape; add an eval assertion tying a `public/` content change to a `CACHE_NAME` bump; add a reciprocal CSP test (allowed host with zero usage → fail). These would have caught #1, F18, and D6 respectively.

## Process notes
- `eval/scores.jsonl` is dirty in the working tree (append-only local log; my 211/211 verification run appended to it). Not a content defect — recommend `git checkout -- eval/scores.jsonl`, and consider F21 (gitignore or truncate-at-freeze).
- Adjacent, separate: task #50 (README trust fixes) overlaps items 5, B5, F19 above — worth doing in one pass.

---

## Annex: fix status (2026-07-21, end of day)

Applied the same day the report was filed, in three PRs. The eval suite grew from 211 to 212 tests (a runner self-test). Distinct outlets fell from 43 to 42 when the A1 label merged; the count guard caught that ripple on both prose surfaces.

| Item | Status |
|---|---|
| 1 (dead "verified" links) | Applied in #66. Dated annotations, status `verified-at-build`; the ABC note points to the live Spectrum News copy of the same AP story; rot guard generalized from one slug to the class; SW cache v91. Evidence-based call: annotate, don't substitute (reference-rot literature + archival-integrity practice); the June-4 re-point stays the right remedy only for URLs that were wrong at creation. |
| 2 (B1 P0-gate docs) | Applied in #65. |
| 3 (B2 counts + dead link) | Applied in #65; the count guard now covers `NEWS_ARCHIVE_AUDIT.md` too. |
| 4 (B3 wind bullet) | Applied in #65. |
| 5 (F16 README map claim) | Applied in #65, with task #50; B5 was already fixed on main (#64); F19 assessed and deliberately left (CI still runs on every PR, so the live badge is accurate). |
| 6 (A1 outlet) | Applied in #67 (approved field fix). |
| 7 (B4 CITATION.cff) | Applied in #67. |
| 8 (D1/D3 XSS + coverage) | Applied in #67; a third latent sink (setBanners `localizeBreakingReason` fall-through) was found by the extended guard and fixed. |
| 9 (D4/D5/F18) | D4 and D5 applied in #67 (SW `ignoreSearch`, cache v92; runner exits 2 on zero tests). F18: the bump practice was followed in #66/#67; an automated bump guard is still pending. |
| 10 (F17/F20) | Doc note applied in #67 (`DEPLOYMENT_READINESS.md` post-freeze maintenance). Checking registrar auto-renew and the transfer lock is an owner action, still open. |
| MINORs (A2, B6, B7, B8, D2, D6, D7, D8, D9, F15, F19, F21, F22) | Pending; unchanged from the tables above. |
