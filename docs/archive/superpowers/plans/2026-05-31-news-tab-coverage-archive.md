# News-tab Coverage Archive Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the News tab into an honest, resolved-state "Coverage Archive": a persistent archive-note banner above the feed, the real 39-item `data/news_archive.json` wired into the coverage list (UI-layer only), absolute dates (date-only when the publish time isn't verified), kept "Official" source labels, no authority chrome.

**Architecture:** Pure UI-layer change in the single-file `dashboard.html` plus a one-line `sw.js` precache. The writer/`status.json` schema is untouched (so `test_videos_dedupe.py`/`test_provenance.py` stay green). Coverage is read from a new one-time `loadArchive()` fetch (mirrors `loadConfig()`); `snap.videos[]` remains the offline/fetch-fail fallback. The existing `curateNewsFeed` (officials-first + live-blog dedup) and `buildFeedCardsHtml` (active renderer via `renderFilteredFeed`) are reused.

**Tech Stack:** Vanilla JS (no build step), pytest-style eval harness (`python eval/run_all.py --skip integration`), service worker cache.

**Branch:** feature branch off `main` (branch → PR → merge; never push `main`). Suggested: `feat/news-coverage-archive`.

**Verify (every task):** `python eval/run_all.py --skip integration` — by exit code/scorecard. NEVER `--quiet`.

**Dropped from this PR (flagged):** the "covered by N outlets" corroboration cue. `newsBaseKey` only collapses *same-outlet* live-blog URL families; it does not group the *same story across different outlets*, so an "N outlets" count derived from it would misrepresent corroboration. Honest cross-outlet counting needs a story key the archive doesn't carry → defer to a follow-up (see Task 6 note).

---

### Task 1: Archive-note banner (BUILD FIRST)

A persistent, static note at the top of the News tab framing the feed as a historical archive (the global header already announces "Resolved/Lifted", so this does NOT re-announce resolution). Static markup + `data-i18n` (matches the existing pattern at `dashboard.html:1499`).

**Files:**
- Test: `eval/test_news_archive_banner.py` (create)
- Modify: `dashboard.html` — i18n block (~line 1586), News markup (~line 1479-1482), CSS (~line 286)

- [ ] **Step 1: Write the failing test**

```python
# eval/test_news_archive_banner.py
"""Guard: the News tab carries a persistent archive-note banner ABOVE the feed (2026-05-31).

Resolved-state demonstration: the News tab is a historical Coverage Archive, not a live
feed. The note routes to officials and never claims authority. Anchored on the real markup
tag — class names also appear in the inline <style>, so a bare-name find() would measure CSS
order, not DOM order (see eval-find-hits-css-before-html).
"""
import re
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_archive_note_present_and_localized():
    text = DASHBOARD.read_text(encoding="utf-8")
    has_markup = '<div class="news-archive-note"' in text
    has_i18n = '"news.archive.note": { en:' in text
    return {"passed": has_markup and has_i18n,
            "details": "archive-note markup + en string present"
            if (has_markup and has_i18n) else f"markup={has_markup} i18n={has_i18n}"}


def test_archive_note_before_feed():
    text = DASHBOARD.read_text(encoding="utf-8")
    i_note = text.find('<div class="news-archive-note"')
    i_feed = text.find('<div id="news-feed">')
    ok = -1 < i_note < i_feed
    return {"passed": ok,
            "details": "order: archive-note < news-feed" if ok
            else f"bad order note={i_note} feed={i_feed}",
            "metrics": {"note": i_note, "feed": i_feed}}


def test_archive_note_routes_official_no_authority_chrome():
    text = DASHBOARD.read_text(encoding="utf-8")
    m = re.search(r'"news\.archive\.note":\s*\{\s*en:\s*"([^"]*)"', text)
    val = (m.group(1) if m else "")
    routes = "ggcity.org/emergency" in val or "911" in val
    forbidden = any(bad in val.lower() for bad in ["verified", "official source", "government"])
    return {"passed": bool(val) and routes and not forbidden,
            "details": f"routes={routes} forbidden_terms_present={forbidden} len={len(val)}"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python eval/run_all.py --skip integration`
Expected: the three `test_news_archive_banner` checks FAIL (markup/i18n absent).

- [ ] **Step 3: Add the i18n string** (in the `news.*` block, after `dashboard.html:1586` `"news.feed.title"...`)

```javascript
  "news.archive.note": { en: "Archived coverage — not live. The reports below are from the May 2026 incident (now resolved). For current emergencies, see ggcity.org/emergency or call 911." },
```

- [ ] **Step 4: Add the markup** (first child of `#news-subpanel-updates`, `dashboard.html:1479`)

```html
        <div class="news-subpanel active" id="news-subpanel-updates">
          <div class="news-archive-note" data-i18n="news.archive.note"></div>
          <div id="news-situation" class="news-situation" hidden></div>
          <div class="news-filter-chips" id="news-filter-chips"></div>
          <div id="news-feed"></div>
```

- [ ] **Step 5: Add the CSS** (near the other `.news-*` rules, ~`dashboard.html:286`)

```css
    .news-archive-note { padding: 10px 12px; border-bottom: 1px solid var(--sa-border); background: var(--sa-bg); color: var(--sa-text-2); font-size: 12px; line-height: 1.45; }
```

- [ ] **Step 6: Run test to verify it passes**

Run: `python eval/run_all.py --skip integration`
Expected: `test_news_archive_banner` checks PASS; all prior tests still green.

- [ ] **Step 7: Commit**

```bash
git add eval/test_news_archive_banner.py dashboard.html
git commit -m "feat(news): add resolved-state archive-note banner above the feed"
```

---

### Task 2: Wire the real archive into the feed (videos[] fallback)

Read coverage from `data/news_archive.json` via a one-time `loadArchive()` (mirrors `loadConfig()` at `dashboard.html:2619`); fall back to `snap.videos[]` when the archive is absent. Officials still come from `snap.official_statements`.

**Files:**
- Test: `eval/test_news_archive_wired.py` (create)
- Modify: `dashboard.html` — add `archiveCache` + `loadArchive()` (near `loadConfig`, ~2619), kickoff (~2654), coverage build in `render()` (replace `dashboard.html:2557-2560`)

- [ ] **Step 1: Write the failing test**

```python
# eval/test_news_archive_wired.py
"""Guard: the News feed reads the curated archive (data/news_archive.json), with
snap.videos[] as the offline/fetch-fail fallback. UI-layer only (2026-05-31)."""
import json
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"
ARCHIVE = REPO_ROOT / "data" / "news_archive.json"


def test_dashboard_fetches_archive():
    text = DASHBOARD.read_text(encoding="utf-8")
    fetches = 'fetch("data/news_archive.json' in text
    has_loader = "function loadArchive" in text
    return {"passed": fetches and has_loader, "details": f"fetch={fetches} loader={has_loader}"}


def test_videos_fallback_preserved():
    text = DASHBOARD.read_text(encoding="utf-8")
    return {"passed": "snap.videos" in text, "details": "snap.videos[] fallback path retained"}


def test_archive_has_substantive_items():
    data = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    n = len(data.get("items", []))
    return {"passed": n >= 30, "details": f"archive items: {n}", "metrics": {"items": n}}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python eval/run_all.py --skip integration`
Expected: `test_dashboard_fetches_archive` FAILS (no `loadArchive`).

- [ ] **Step 3: Add `archiveCache` + `loadArchive()`** (immediately before `loadConfig`, `dashboard.html:2619`)

```javascript
var archiveCache = null;
async function loadArchive() {
  try {
    var resp = await fetch("data/news_archive.json?t=" + Date.now(), {cache:"no-store"});
    if (!resp.ok) throw new Error("news_archive.json HTTP " + resp.status);
    archiveCache = await resp.json();
  } catch (e) {
    console.warn("archive load failed:", e);
    archiveCache = null;  // render() falls back to snap.videos[]
  }
  return archiveCache;
}
```

- [ ] **Step 4: Gate first paint on the archive too** (replace the kickoff at `dashboard.html:2654-2657`)

```javascript
var configReady = loadConfig();
var archiveReady = loadArchive();
Promise.all([configReady, archiveReady]).then(function() {
  fetchStatus();
});
```
(Keep `var configReady = loadConfig();` as its own variable — `map.on("load")` awaits `configReady`. `render()` re-runs every `REFRESH_MS`, so a late archive load is picked up on the next tick regardless.)

- [ ] **Step 5: Build coverage from the archive** (replace the `(snap.videos || []).forEach(...)` block, `dashboard.html:2557-2560`)

```javascript
  var coverage = (archiveCache && Array.isArray(archiveCache.items) && archiveCache.items.length)
    ? archiveCache.items.map(function(it) {
        var isVid = !!it.youtube_id || it.type === "video";
        return { when: it.published_iso || "", type: isVid ? "video" : "article",
                 source: it.outlet || "—", title: it.title || t("news.untitled"),
                 url: it.url || "", isVideo: isVid,
                 thumb: it.youtube_id ? ("https://i.ytimg.com/vi/" + it.youtube_id + "/hqdefault.jpg") : "",
                 isArchive: true, confidence: it.published_iso_confidence || "" };
      })
    : (snap.videos || []).map(function(v) {
        var isVid = !!(v.youtube_id) || v.is_video === true;
        return { when: v.published_iso || "", type: isVid ? "video" : "article",
                 source: v.outlet || "—", title: v.title || t("news.untitled"),
                 url: v.url || "", isVideo: isVid, thumb: v.thumbnail_url || "",
                 isArchive: false, confidence: "" };
      });
  coverage.forEach(function(it) { feed.push(it); });
```

- [ ] **Step 6: Run tests to verify they pass + no regressions**

Run: `python eval/run_all.py --skip integration`
Expected: `test_news_archive_wired` PASS; `test_videos_dedupe`, `test_provenance` still PASS (writer untouched).

- [ ] **Step 7: Commit**

```bash
git add eval/test_news_archive_wired.py dashboard.html
git commit -m "feat(news): wire real news_archive.json into the feed; videos[] fallback"
```

---

### Task 3: Absolute dates (date-only when publish time isn't verified)

Archive items show absolute dates, never relative time (a resolved record must not drift to "3 months ago"). Date+time when `confidence === "verified"`, date-only otherwise, nothing when no `when`. Status-driven items keep `relativeTime`.

**Files:**
- Test: `eval/test_news_date_display.py` (create)
- Modify: `dashboard.html` — add helpers near `fmtAbsDateTime` (`1846`), branch in `buildFeedCardsHtml` (`2073`)

- [ ] **Step 1: Write the failing test**

```python
# eval/test_news_date_display.py
"""Guard: archive items render absolute dates (date+time when verified, date-only when
not), never relativeTime, so a resolved record doesn't drift to 'months ago' (2026-05-31)."""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"


def test_archive_date_helpers_present():
    text = DASHBOARD.read_text(encoding="utf-8")
    return {"passed": "function fmtAbsDateOnly" in text and "function fmtArchiveWhen" in text,
            "details": "absolute date-only + archive-when helpers present"}


def test_archive_when_branches_on_confidence():
    text = DASHBOARD.read_text(encoding="utf-8")
    ok = 'confidence === "verified"' in text
    return {"passed": ok, "details": "date display branches on published_iso_confidence"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python eval/run_all.py --skip integration`
Expected: `test_news_date_display` FAILS (helpers absent).

- [ ] **Step 3: Add the helpers** (after `fmtAbsDateTime`, `dashboard.html:~1858`)

```javascript
function fmtAbsDateOnly(iso) {
  if (!iso) return "";
  var d = new Date(iso);
  if (isNaN(d.getTime())) return "";
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}
// Archive items: honest absolute time. Verified publish time -> date+time; otherwise
// date-only (no false precision, no "~"); no time at all when the date is unknown.
function fmtArchiveWhen(it) {
  if (!it.when) return "";
  return it.confidence === "verified" ? fmtAbsDateTime(it.when) : fmtAbsDateOnly(it.when);
}
```

- [ ] **Step 4: Branch the renderer** (in `buildFeedCardsHtml`, replace `dashboard.html:2073`)

```javascript
    var when = it.isArchive ? fmtArchiveWhen(it) : (it.when ? relativeTime(it.when) : "");
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python eval/run_all.py --skip integration`
Expected: `test_news_date_display` PASS; all prior green.

- [ ] **Step 6: Commit**

```bash
git add eval/test_news_date_display.py dashboard.html
git commit -m "feat(news): absolute dates for archive items, date-only when unverified"
```

---

### Task 4: Service worker — precache the archive + bump cache version

Touching `sw.js` is the riskiest step: `test_map_reload_regressions.py` MUST stay green (the cross-origin Firefox blank-map fix). Only the version string and the precache list change; the cross-origin non-interception block (`sw.js:73-80`) is NOT touched.

**Files:**
- Test: `eval/test_sw_precache.py` (create)
- Modify: `sw.js:1` (CACHE_NAME), `sw.js:2-9` (STATIC_ASSETS)

- [ ] **Step 1: Write the failing test**

```python
# eval/test_sw_precache.py
"""Guard: news_archive.json is precached and CACHE_NAME bumped so returning users get
the new shell + offline archive (2026-05-31). Cross-origin non-interception is guarded
separately by test_map_reload_regressions."""
from pathlib import Path

CATEGORY = "behavioral"
REPO_ROOT = Path(__file__).resolve().parent.parent
SW = REPO_ROOT / "sw.js"


def test_cache_bumped_and_archive_precached():
    text = SW.read_text(encoding="utf-8")
    bumped = 'CACHE_NAME = "gg-tank-v22"' in text
    precached = '"/data/news_archive.json"' in text
    return {"passed": bumped and precached, "details": f"v22={bumped} precached={precached}"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python eval/run_all.py --skip integration`
Expected: `test_sw_precache` FAILS (still v21, archive not precached).

- [ ] **Step 3: Bump version + precache** (`sw.js:1-9`)

```javascript
var CACHE_NAME = "gg-tank-v22";
var STATIC_ASSETS = [
  "/",
  "/dashboard.html",
  "/config.json",
  "/data/news_archive.json",
  "/manifest.json",
  "/lib/maplibre-gl.js",
  "/lib/maplibre-gl.css"
];
```

- [ ] **Step 4: Run tests to verify pass + map-reload regression green**

Run: `python eval/run_all.py --skip integration`
Expected: `test_sw_precache` PASS; **`test_map_reload_regressions` PASS** (cross-origin block unchanged).

- [ ] **Step 5: Commit**

```bash
git add eval/test_sw_precache.py sw.js
git commit -m "chore(sw): precache news_archive.json; bump CACHE_NAME v21->v22"
```

---

### Task 5: README — methodology, limitations, peak-snapshot hero (prose; TDD-exempt)

Pure-prose markdown → exempt from the test floor. This is where the portfolio/reviewer signal lives (per the research: repo > on-page chrome).

**Files:** Modify: `README.md`

- [ ] **Step 1: Add a "How this works" section** covering: it aggregates official + news sources and routes to officials (authors no directives); the eval harness (link `eval/`, name `test_provenance.py`); honest limitations (resolved archive, English-only, approximate times shown date-only); verifiable data (`data/news_archive.json` + `data/NEWS_ARCHIVE_AUDIT.md`).
- [ ] **Step 2: Add the dated peak-snapshot** as the README hero image and/or `og-image.png`, captioned "Snapshot from [peak date] — incident now resolved." (README/og ONLY — never a live landing state.)
- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs(readme): how-it-works + limitations + dated peak-snapshot hero"
```

> **Note (deferred follow-up):** "covered by N outlets" corroboration cue — needs a cross-outlet story key the archive lacks (`newsBaseKey` only collapses same-outlet live-blogs). Capture as a follow-up; do NOT compute a misleading count from `newsBaseKey`.

---

### Task 6: Mark the old spec SUPERSEDED (prose; TDD-exempt)

**Files:** Modify: `docs/NEWS_UX_SPEC.md`

- [ ] **Step 1: Prepend a SUPERSEDED header** (mirrors the post-mortem header style in `docs/DISTRIBUTION.md`)

```markdown
> ## SUPERSEDED — see the current design
>
> **This spec (2026-05-25) predates three pivots and is retained for history only.**
> It assumes a 4-tab nav, Alerts/Latest/Timeline sub-views, pervasive Vietnamese
> `[VI: …]` slots, and severity chips — all since changed by:
> 1. the **conduit pivot** (address-checker + severity removed),
> 2. the **English-only** decision (all Vietnamese removed; route LEP residents to officials),
> 3. the **incident resolution** (2026-05-28) — the News tab is now a resolved-state archive.
>
> Current design: the "banner-led Coverage Archive" office-hours design doc + the
> implementation plan at `docs/superpowers/plans/2026-05-31-news-tab-coverage-archive.md`.
```

- [ ] **Step 2: Commit**

```bash
git add docs/NEWS_UX_SPEC.md
git commit -m "docs: mark NEWS_UX_SPEC.md superseded (conduit + English-only + resolved)"
```

---

## Final verification
- [ ] `python eval/run_all.py --skip integration` — full suite green (new guards pass; `test_provenance`, `test_videos_dedupe`, `test_no_vietnamese_residue`, `test_language_access`, `test_map_reload_regressions` all still pass).
- [ ] Visual confirm (signed Edge headless per project QA): archive-note banner above the feed; coverage items show absolute dates; "Official" labels kept; no live/current misread.
- [ ] Open PR (problem, approach, test plan, risk, rollback; screenshots). Do NOT push `main`.

## Self-review notes
- **Spec coverage:** banner (T1), archive wiring + videos fallback (T2), dates (T3), SW precache + version (T4), README/portfolio surface (T5), superseded spec (T6). Enrichment deferred (eng-review D1); N-outlets dropped with rationale.
- **Type consistency:** feed items carry `isArchive` + `confidence` (set in T2, read in T3's `fmtArchiveWhen` and the T3 renderer branch). `loadArchive`/`archiveCache` defined in T2 and referenced in T2's `render()` build.
- **No placeholders:** every code/test step shows real content and exact paths/lines.
