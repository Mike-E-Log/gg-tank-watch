# Last-Updated Honest Freshness Label Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the `As of {t}` timestamp with an honest `Last updated {clock} ({N} ago)` label sourced from `data_as_of_iso`, and remove all resident-facing "stale/fresh" data vocabulary — without breaking the binding honesty contract.

**Architecture:** Single-file static dashboard (`dashboard.html`). The visible freshness label now reflects `data_as_of_iso` (when we last learned something *new*) plus a relative age, so a stalled feed reads honestly instead of "fresh". `last_updated_iso` (pipeline liveness) moves to the hover tooltip. The binary "⚠️ Stale" banner — currently firing constantly on the resolved incident — is removed; the always-on relative age is the honest continuous freshness signal. The active-incident "feed dark" notice is DEFERRED (suppressed when resolved, invisible today). Guarded by a new text-based eval test.

**Tech Stack:** Vanilla JS in `dashboard.html`, `sw.js` cache-first service worker, custom Python eval harness (`eval/`, no JS runtime → text-guard tests).

---

## File Structure

- `dashboard.html` — freshness render + i18n STRINGS + stale-banner removal + `relativeAge` helper (all edits here)
- `sw.js` — `CACHE_NAME` bump (`v18` → `v19`) so cached users get the new shell
- `eval/test_freshness_ui.py` — NEW guard test (text assertions, pattern: `test_wind_removed.py`)

No backend (`scripts/update_status.py`) changes. The `data_as_of_iso` / `stale_after_iso` data model and its 4 backend `test_freshness.py` tests are reused unchanged.

---

## Pre-flight: feature branch (project rule — never push main)

- [ ] **Step 0: Create the feature branch** (currently on `main`)

```bash
git -C "C:/Users/redacted/Desktop/Mike Ilog Portfolio/GitHub Projects/gg-tank-watch" checkout -b feat/last-updated-honest-freshness
git -C "C:/Users/redacted/Desktop/Mike Ilog Portfolio/GitHub Projects/gg-tank-watch" branch --show-current
```
Expected: prints `feat/last-updated-honest-freshness`

---

## Task 1: Failing eval guard for the honest label + removed vocab

**Files:**
- Create: `eval/test_freshness_ui.py`

- [ ] **Step 1: Write the failing test** (text guards — the harness has no JS runtime)

```python
"""UI-honesty guards for the freshness label (2026-05-31).

The visible timestamp must read "Last updated {clock} ({N} ago)" sourced from
data_as_of_iso (when we last learned something new), NOT last_updated_iso
(pipeline write time) — otherwise a stalled feed looks fresh (the F4/F6 class
that test_freshness.py guards on the backend). All resident-facing "stale" /
"fresh" / "As of" vocabulary is removed, and the false "auto-updates every 20
minutes" cadence claim is gone. Pure text guards; no JS runtime needed.
"""
from pathlib import Path

CATEGORY = "behavioral"

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = REPO_ROOT / "dashboard.html"

# Resident-facing strings that must NO LONGER appear after this change.
FORBIDDEN = (
    '"updated.freshness": { en: "As of',          # old freshness label
    "banner.stale.title",                          # removed stale-banner i18n key
    "banner.stale.msg",                            # removed stale-banner i18n key
    "Auto-updates about every 20 minutes",         # false cadence claim (cron dormant)
    "⚠️ Stale",                          # the "⚠️ Stale" banner title text
)

# Tokens that MUST be present (the honest replacement + a kept dependency).
REQUIRED = (
    '"updated.freshness": { en: "Last updated',    # new honest label
    "relativeAge",                                 # the relative-age helper
    "data_as_of_iso",                              # freshness label binds to info-age
    ".banner-stale",                               # CSS kept — schema banner reuses it
)


def test_no_stale_fresh_vocab_in_dashboard():
    """No 'As of' / 'Stale' / false-cadence vocab may remain in dashboard.html."""
    text = DASHBOARD.read_text(encoding="utf-8")
    survivors = [tok for tok in FORBIDDEN if tok in text]
    return {
        "passed": not survivors,
        "details": "no stale/fresh/As-of vocab in dashboard.html"
        if not survivors
        else "forbidden string(s) still present: " + " | ".join(survivors),
        "metrics": {"survivors": len(survivors)},
    }


def test_freshness_label_honest_and_dependencies_intact():
    """The honest 'Last updated' label, relativeAge helper, data_as_of binding,
    and the kept .banner-stale CSS (schema-banner dep) must all be present."""
    text = DASHBOARD.read_text(encoding="utf-8")
    missing = [tok for tok in REQUIRED if tok not in text]
    return {
        "passed": not missing,
        "details": "honest label + deps present"
        if not missing
        else "required token(s) missing: " + " | ".join(missing),
        "metrics": {"missing": len(missing)},
    }
```

- [ ] **Step 2: Run the test to verify it FAILS**

```bash
python eval/run_all.py --skip integration
```
Expected: scorecard shows `test_freshness_ui` with `test_no_stale_fresh_vocab_in_dashboard` FAIL (old "As of" + banner.stale + cadence strings still present) and `test_freshness_label_honest_and_dependencies_intact` FAIL (`relativeAge` / `Last updated` not yet added). Non-zero exit. Do NOT use `--quiet`.

- [ ] **Step 3: Commit the failing test**

```bash
git add eval/test_freshness_ui.py
git commit -m "test(eval): guard honest data_as_of freshness label + no stale/fresh vocab"
```

---

## Task 2: Add the `relativeAge` helper

**Files:**
- Modify: `dashboard.html` (after `:1513`, with the other top-of-script consts/helpers)

- [ ] **Step 1: Add the helper** immediately after the `var BREAKING_TITLE = ...;` line (`dashboard.html:1513`)

```javascript
// Honest relative-age string for the freshness label. Clamps negative deltas
// (client clock skew) to "just now" so a fast client never shows "in 3 min".
function relativeAge(fromMs, nowMs) {
  var deltaMin = Math.floor((nowMs - fromMs) / 60000);
  if (deltaMin <= 0) return "just now";
  if (deltaMin < 60) return deltaMin + " min ago";
  var hr = Math.floor(deltaMin / 60);
  if (hr < 24) return hr + " hr ago";
  var days = Math.floor(hr / 24);
  return days + (days === 1 ? " day ago" : " days ago");
}
```

- [ ] **Step 2: No standalone run yet** — helper is exercised by Task 3's render. Proceed.

---

## Task 3: Rewire the freshness render to `data_as_of` + relative age + honest tooltip

**Files:**
- Modify: `dashboard.html:2454-2462`

- [ ] **Step 1: Replace the render block.** Current (`:2454-2462`):

```javascript
  var updEl = $("updated-text");
  var freshLabel = $("freshness-label");
  var _d = snap.last_updated_iso ? new Date(snap.last_updated_iso) : null;
  var _dateOpts = (typeof window !== "undefined" && window.innerWidth >= 768)
    ? {month:"numeric", day:"numeric", year:"numeric"}  // desktop has room for the full date
    : {month:"numeric", day:"numeric"};                 // mobile drops the year to avoid the clip
  var clock = _d ? _d.toLocaleDateString("en-US", _dateOpts) + ", " + _d.toLocaleTimeString("en-US", TIME_OPTS) : "—";
  if (freshLabel) freshLabel.textContent = t("updated.freshness", { t: clock });
  if (updEl) updEl.title = t("updated.title", { t: clock });
```

Replace with:

```javascript
  var updEl = $("updated-text");
  var freshLabel = $("freshness-label");
  // Honesty (eng review D1): the visible label reflects data_as_of_iso (when we
  // last learned something NEW), never last_updated_iso (pipeline write time) —
  // so a stalled feed reads its true age instead of looking fresh. last_updated
  // (system liveness) goes in the hover tooltip. Fall back to last_updated only
  // when data_as_of is absent, so the label is never blank.
  var _asOf = snap.data_as_of_iso ? new Date(snap.data_as_of_iso)
            : (snap.last_updated_iso ? new Date(snap.last_updated_iso) : null);
  var _checked = snap.last_updated_iso ? new Date(snap.last_updated_iso) : _asOf;
  var _dateOpts = (typeof window !== "undefined" && window.innerWidth >= 768)
    ? {month:"numeric", day:"numeric", year:"numeric"}  // desktop has room for the full date
    : {month:"numeric", day:"numeric"};                 // mobile drops the year to avoid the clip
  var clock = _asOf ? _asOf.toLocaleDateString("en-US", _dateOpts) + ", " + _asOf.toLocaleTimeString("en-US", TIME_OPTS) : "—";
  var ageStr = _asOf ? relativeAge(_asOf.getTime(), Date.now()) : null;
  var label = ageStr ? clock + " (" + ageStr + ")" : clock;
  if (freshLabel) freshLabel.textContent = t("updated.freshness", { t: label });
  if (updEl && _checked) {
    var _checkedClock = _checked.toLocaleDateString("en-US", {month:"numeric", day:"numeric", year:"numeric"})
      + ", " + _checked.toLocaleTimeString("en-US", TIME_OPTS);
    updEl.title = t("updated.title", { t: _checkedClock });
  }
```

- [ ] **Step 2: No run yet** — depends on the STRING edits in Task 4. Proceed.

---

## Task 4: Update the i18n STRINGS (honest label + tooltip)

**Files:**
- Modify: `dashboard.html:1542-1543`

- [ ] **Step 1: Edit the freshness + tooltip strings.** Current:

```javascript
  "updated.freshness": { en: "As of {t}" },
  "updated.title": { en: "Auto-updates about every 20 minutes. Last update {t}." },
```

Replace with:

```javascript
  "updated.freshness": { en: "Last updated {t}" },
  "updated.title": { en: "Last checked {t}." },
```

- [ ] **Step 2:** Proceed to Task 5 (stale-banner removal) before running.

---

## Task 5: Remove the "⚠️ Stale" banner (strings + render), keep `.banner-stale` CSS

**Files:**
- Modify: `dashboard.html:1630-1631` (STRINGS), `dashboard.html:2468-2476` (render)

- [ ] **Step 1: Delete the two STRING entries** (`:1630-1631`):

```javascript
  "banner.stale.title": { en: "⚠️ Stale" },
  "banner.stale.msg": { en: "Last update {n} min ago" },
```
Remove both lines entirely. (Leave `banner.schema.*` and `banner.offline.*` directly around them untouched.)

- [ ] **Step 2: Delete the stale-banner render block** (`:2468-2476`):

```javascript
  // Staleness: data is past its stale_after_iso (data_as_of + MAX_AGE). Independent
  // of offline/breaking — an honest signal that the feed stopped updating, even on a
  // resolved incident. Reuses the existing .banner-stale + banner.stale.* i18n.
  var staleAfter = snap.stale_after_iso ? new Date(snap.stale_after_iso) : null;
  if (staleAfter && now > staleAfter) {
    var dataAsOf = snap.data_as_of_iso ? new Date(snap.data_as_of_iso) : null;
    var minsAgo = dataAsOf ? Math.floor((now - dataAsOf) / 60000) : "?";
    banners.push({kind:"stale", title: t("banner.stale.title"), message: t("banner.stale.msg", {n: minsAgo})});
  }
```
Remove the whole block. Do NOT touch the schema-mismatch banner at `:2451` (`kind:"stale"` with `banner.schema.*`) — it legitimately reuses the `.banner-stale` visual style. Leave `.banner-stale` CSS (`:334`) in place.

- [ ] **Step 3: Run the full eval — expect Task 1 guards to now PASS**

```bash
python eval/run_all.py --skip integration
```
Expected: scorecard shows `test_freshness_ui` BOTH tests PASS; the 4 `test_freshness` backend tests still PASS; `test_map_reload_regressions`, `test_schema` still PASS. Exit code 0. (If any FAIL line appears, read it — never `--quiet`.)

- [ ] **Step 4: Commit the dashboard change**

```bash
git add dashboard.html
git commit -m "feat(dashboard): honest 'Last updated (N ago)' label from data_as_of; remove stale/fresh vocab"
```

---

## Task 6: Bump the service-worker cache

**Files:**
- Modify: `sw.js:1`

- [ ] **Step 1: Bump CACHE_NAME.** Current:

```javascript
var CACHE_NAME = "gg-tank-v18";
```
Replace with:

```javascript
var CACHE_NAME = "gg-tank-v19";
```

- [ ] **Step 2: Commit**

```bash
git add sw.js
git commit -m "chore(sw): bump cache gg-tank-v19 for freshness label change"
```

---

## Task 7: Final verification

- [ ] **Step 1: Full eval, read the scorecard**

```bash
python eval/run_all.py --skip integration
```
Expected: exit 0, no `[FAIL]` lines. `test_freshness_ui` (2/2), `test_freshness` (4/4), `test_schema`, `test_map_reload_regressions`, `test_wind_removed` all pass.

- [ ] **Step 2: Visual confirm (SAC blocks gstack browse → signed Edge headless).** Serve same-origin and screenshot the topbar; confirm label reads `Last updated 5/31, HH:MM AM (N min ago)`, hover tooltip reads `Last checked 5/31/2026, HH:MM AM.`, and no "⚠️ Stale" banner appears. (Resolved incident → no stale banner is correct.)

- [ ] **Step 3: Push branch + open PR** (do NOT push main; ask before pushing)

```bash
git -C "C:/Users/redacted/Desktop/Mike Ilog Portfolio/GitHub Projects/gg-tank-watch" push -u origin feat/last-updated-honest-freshness
```

---

## Deferred (TODOs — captured, not built)

- **T1 — Active-incident "feed dark" notice.** When re-deployed for a LIVE incident, add a muted, reworded notice (no "stale/fresh" words, e.g. "Data may be older than usual — last new info {N} ago") that fires only when `now > data_as_of + FEED_DARK` AND `!resolved`. `FEED_DARK` is a **config value tied to the deployment's expected refresh cadence** (single source of truth), not a magic constant. Suppressed when resolved. Add an eval test (active+dark → fires; resolved+dark → suppressed).
- **T2 — Reconcile freshness threshold source of truth.** `config.json stale_after_minutes: 30` is unused; the writer hardcodes `MAX_AGE_MINUTES = 40` (`update_status.py:70`). Fold into T1: make one configurable value drive both.

---

## Self-Review

- **Spec coverage:** label→data_as_of (T3+T4) ✓; relative age helper (T2) ✓; tooltip false-cadence removed (T4) ✓; stale banner + vocab removed (T5) ✓; `.banner-stale` kept (T5 note + T1 guard) ✓; sw bump (T6) ✓; new eval guard (T1) ✓; deferred notice (TODOs) ✓.
- **Placeholder scan:** none — every code step shows full code.
- **Type consistency:** `relativeAge(fromMs, nowMs)` defined T2, called T3 with `(_asOf.getTime(), Date.now())` ✓. STRING keys `updated.freshness` / `updated.title` consistent T3↔T4 ✓. Forbidden/required tokens in T1 match the exact strings edited in T4/T5 ✓.
