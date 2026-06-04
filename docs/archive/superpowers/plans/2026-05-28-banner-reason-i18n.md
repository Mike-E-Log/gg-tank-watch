# Banner-Reason i18n Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Localize every breaking-banner message (8 pipeline reason strings) into the active UI language, so a Vietnamese user never sees a raw-English banner like "1 new official statement(s)".

**Architecture:** The Python pipeline (`scripts/update_status.py`) keeps emitting English `breaking_reason` strings verbatim — that English string remains the canonical dismiss-identity (`sig`), the `breaking_events.jsonl` log entry, and the ntfy payload. **No pipeline/schema change.** All localization happens client-side in `dashboard.html`: a `localizeBreakingReason()` mapper recognizes each of the 8 reason patterns and renders the matching i18n template via the existing `t()` function, with an English passthrough fallback for anything unrecognized (which is also the G1-safe default). The English reason is stashed in a `data-reason` attribute on the banner message span so `applyLang()` can re-localize in place on a live language toggle without resurrecting dismissed banners.

**Tech Stack:** Vanilla ES5 JS inside the single-file `dashboard.html`; existing `STRINGS` i18n table + `t(id, vars)`; pytest-style eval harness (`eval/run_all.py`) for regression; signed Edge headless for VI visual confirmation (SAC blocks gstack browse.exe — see memory).

**G1 compliance (binding):** No machine-translated *unverified* safety copy shipped silently. Each VI string below maximizes reuse of Nancy-verified terminology already in `STRINGS`; every newly-composed word is flagged inline with a `/* G1: <word> not yet Nancy-verified */` comment. English fallback is automatic via `t()` (`entry[currentLang] || entry.en`), so any flagged string can be reverted to English by deleting its `vi:` value with zero code change.

---

## The 8 pipeline reason strings (source of truth: `scripts/update_status.py:295-337`)

| # | English (exact pipeline output) | Level | Params |
|---|---|---|---|
| 1 | `INCIDENT RESOLVED — evacuation lifted` | urgent | — |
| 2 | `Severity bumped: {prev} -> {next}` | urgent | prev,next ∈ {low,moderate,high,critical} |
| 3 | `Evacuation order LIFTED` | urgent | — |
| 4 | `Evacuation order REINSTATED` | urgent | — |
| 5 | `Evacuation zone EXPANDED` | urgent | — |
| 6 | `First reported injuries: {n}` | urgent | n (int) |
| 7 | `{n} new official statement(s)` | info | n (int) |
| 8 | `Evacuation residents shifted: {prev} -> {next} ({delta})` | info | prev,next,delta (comma-formatted, delta signed) |

Verified-atom inventory (line refs in `dashboard.html` STRINGS): "thông cáo chính thức" (1696), "Sơ tán" (1679), "Đã dỡ bỏ lệnh" (1708), "Mở rộng hôm nay" (1709), "Khu vực sơ tán" (1694), "cư dân ... sơ tán" (1689), "Sự cố đã được giải quyết" (1688), "Mức độ nghiêm trọng" (1678), "Mới nhất" (1750), "Đã thay đổi" (1757), "báo cáo" (1722).

---

## File Structure

Only one file changes: `dashboard.html`. Four change sites:
1. **STRINGS table** (~after line 1766, the `banner.*` block): add 8 `banner.reason.*` keys + 4 `severity.*` keys.
2. **New helpers** (~before `setBanners`, line 2032): `escAttr()`, `localizeSeverity()`, `localizeBreakingReason()`.
3. **`setBanners()`** (line 2045): render the message span with `class="banner-msg"`, `data-reason="<escaped English>"`, and localized text.
4. **`applyLang()`** (~after line 1858): re-localize any on-screen `.banner-msg[data-reason]` spans in place.

---

### Task 1: Add i18n templates for all 8 reasons + severity words

**Files:**
- Modify: `dashboard.html` — insert after the `banner.action.updates` entry (line 1766), inside `STRINGS`.

- [ ] **Step 1: Insert the new STRINGS entries**

Insert immediately after line 1766 (`"banner.action.updates": ...`):

```javascript
  /* ===== BANNER REASON i18n (localizes scripts/update_status.py breaking_reason) =====
     EN values reproduce pipeline output verbatim so EN render is a no-op round-trip.
     VI reuses Nancy-verified atoms; newly-composed words flagged G1 (English fallback auto). */
  "banner.reason.resolved":       { en: "INCIDENT RESOLVED — evacuation lifted", vi: "SỰ CỐ ĐÃ ĐƯỢC GIẢI QUYẾT — đã dỡ bỏ lệnh sơ tán" },
  "banner.reason.severity":       { en: "Severity bumped: {prev} -> {next}", vi: "Mức độ nghiêm trọng tăng: {prev} → {next}" /* G1: "tăng" not yet Nancy-verified */ },
  "banner.reason.evacLifted":     { en: "Evacuation order LIFTED", vi: "ĐÃ DỠ BỎ lệnh sơ tán" },
  "banner.reason.evacReinstated": { en: "Evacuation order REINSTATED", vi: "KHÔI PHỤC lệnh sơ tán" /* G1: "Khôi phục" not yet Nancy-verified */ },
  "banner.reason.evacExpanded":   { en: "Evacuation zone EXPANDED", vi: "MỞ RỘNG khu vực sơ tán" },
  "banner.reason.injuries":       { en: "First reported injuries: {n}", vi: "Lần đầu báo cáo thương vong: {n}" /* G1: "thương vong" not yet Nancy-verified */ },
  "banner.reason.newStatements":  { en: "{n} new official statement(s)", vi: "{n} thông cáo chính thức mới" },
  "banner.reason.residentsShifted": { en: "Evacuation residents shifted: {prev} -> {next} ({delta})", vi: "Số cư dân sơ tán thay đổi: {prev} → {next} ({delta})" },
  "severity.low":      { en: "low",      vi: "thấp" /* G1: not yet Nancy-verified */ },
  "severity.moderate": { en: "moderate", vi: "trung bình" /* G1: not yet Nancy-verified */ },
  "severity.high":     { en: "high",     vi: "cao" /* G1: not yet Nancy-verified */ },
  "severity.critical": { en: "critical", vi: "nguy kịch" /* G1: not yet Nancy-verified */ },
```

- [ ] **Step 2: Sanity-check no trailing-comma / brace breakage**

Run: `node -e "const s=require('fs').readFileSync('dashboard.html','utf8'); const m=s.match(/var STRINGS = \{[\s\S]*?\n\};/); eval('('+m[0].replace('var STRINGS =','')+')'); console.log('STRINGS parses OK')"`
Expected: `STRINGS parses OK` (confirms the object literal is still valid).

- [ ] **Step 3: Commit**

```bash
git add dashboard.html
git commit -m "feat(i18n): add banner.reason.* + severity.* translation keys"
```

---

### Task 2: Add the localization helpers

**Files:**
- Modify: `dashboard.html` — insert immediately before `function setBanners(banners) {` (line 2032).

- [ ] **Step 1: Insert helpers**

```javascript
/* Escape a string for safe placement in an HTML attribute value. */
function escAttr(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

/* Localize a single severity token (low/moderate/high/critical). English passthrough if unknown. */
function localizeSeverity(word) {
  var key = "severity." + String(word).toLowerCase();
  return STRINGS[key] ? t(key) : word;
}

/* Map an English pipeline breaking_reason to the active language.
   Unrecognized reasons pass through unchanged (G1-safe English fallback). */
function localizeBreakingReason(reason) {
  if (!reason) return "";
  var EXACT = {
    "INCIDENT RESOLVED — evacuation lifted": "banner.reason.resolved",
    "Evacuation order LIFTED": "banner.reason.evacLifted",
    "Evacuation order REINSTATED": "banner.reason.evacReinstated",
    "Evacuation zone EXPANDED": "banner.reason.evacExpanded"
  };
  if (EXACT[reason]) return t(EXACT[reason]);
  var m;
  if ((m = reason.match(/^(\d+) new official statement\(s\)$/)))
    return t("banner.reason.newStatements", { n: m[1] });
  if ((m = reason.match(/^First reported injuries: (\d+)$/)))
    return t("banner.reason.injuries", { n: m[1] });
  if ((m = reason.match(/^Severity bumped: (\w+) -> (\w+)$/)))
    return t("banner.reason.severity", { prev: localizeSeverity(m[1]), next: localizeSeverity(m[2]) });
  if ((m = reason.match(/^Evacuation residents shifted: ([\d,]+) -> ([\d,]+) \(([+\-][\d,]+)\)$/)))
    return t("banner.reason.residentsShifted", { prev: m[1], next: m[2], delta: m[3] });
  return reason;
}
```

- [ ] **Step 2: Commit**

```bash
git add dashboard.html
git commit -m "feat(i18n): add localizeBreakingReason mapper + helpers"
```

---

### Task 3: Render localized text in `setBanners` + re-localize on language toggle

**Files:**
- Modify: `dashboard.html:2045` (the message span inside `setBanners`)
- Modify: `dashboard.html` `applyLang()` — after the `data-i18n-title` loop (line 1858)

- [ ] **Step 1: Localize the banner message span**

Replace the current message-span line (2045):

```javascript
        '<span style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + (b.message || '') + '</span>' +
```

with:

```javascript
        '<span class="banner-msg" data-reason="' + escAttr(b.message || '') + '" style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + localizeBreakingReason(b.message || '') + '</span>' +
```

- [ ] **Step 2: Re-localize on-screen banners in `applyLang`**

Insert after the `data-i18n-title` querySelectorAll loop (after line 1858, before `renderLangPicker();`):

```javascript
  document.querySelectorAll(".banner-msg[data-reason]").forEach(function(el) {
    el.textContent = localizeBreakingReason(el.getAttribute("data-reason"));
  });
```

- [ ] **Step 3: Commit**

```bash
git add dashboard.html
git commit -m "feat(i18n): localize breaking-banner text + live language-toggle re-render"
```

---

### Task 4: Verify (no JS unit harness — use eval no-regression + visual)

- [ ] **Step 1: Eval harness must still pass (no data/schema regression)**

Run: `python eval/run_all.py --skip integration`
Expected: exit code 0; scorecard shows no new `[FAIL]` lines. (Never use `--quiet` — it hides FAILs, per memory.)

- [ ] **Step 2: VI visual confirmation via signed Edge headless**

The live `status.json` already has `breaking:true`, `breaking_reason:"1 new official statement(s)"`, `breaking_level:"info"` — so the info banner renders on load. Seed `gg-lang=vi` into localStorage, then screenshot:

```powershell
# from repo root; serve same-origin so status.json fetch works
$dir = (Get-Location).Path
$job = Start-Job { python -m http.server 8099 --directory $using:dir }
$prof = "$env:TEMP\gg-edge-vi"
# 1) seed localStorage gg-lang=vi using a tiny seed page in the SAME profile
Set-Content "$dir\_seed.html" '<script>localStorage.setItem("gg-lang","vi");document.title="seeded"</script>' -Encoding utf8
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu --user-data-dir="$prof" --virtual-time-budget=3000 --screenshot="$env:TEMP\_seed.png" "http://127.0.0.1:8099/_seed.html" | Out-Null
# 2) screenshot the real dashboard with the SAME profile (lang now persisted)
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu --enable-unsafe-swiftshader --force-device-scale-factor=2 --window-size=900,700 --user-data-dir="$prof" --virtual-time-budget=9000 --screenshot="$env:TEMP\gg-vi-banner.png" "http://127.0.0.1:8099/dashboard.html" | Out-Null
Stop-Job $job; Remove-Job $job; Remove-Item "$dir\_seed.html"
```

Then Read `$env:TEMP\gg-vi-banner.png` and confirm the banner pill reads **CẬP NHẬT** and the message reads **"1 thông cáo chính thức mới"** (not the English "1 new official statement(s)").

- [ ] **Step 3: EN round-trip confirmation**

Repeat Step 2 with `gg-lang=en` (fresh profile). Confirm the banner reads exactly **"1 new official statement(s)"** — proving the localize layer is a faithful no-op for English.

- [ ] **Step 4: Final commit (if any cleanup) + summary**

```bash
git status --short
```
Expected: only `dashboard.html` + the new plan doc tracked; no stray `_seed.html`/`_*.png` artifacts staged.

---

## Self-Review

**1. Spec coverage:** All 8 pipeline reasons → 8 `banner.reason.*` keys + `localizeBreakingReason` patterns (4 exact, 4 regex). Severity words → 4 `severity.*` keys. Live toggle → `applyLang` re-render. ✓
**2. Placeholder scan:** No TBD/TODO; every code step shows full code. ✓
**3. Type consistency:** `localizeBreakingReason`, `localizeSeverity`, `escAttr` names consistent across Tasks 2–3. i18n keys (`banner.reason.newStatements`, `severity.low`, …) identical between Task 1 definitions and Task 2 usages. EN templates reproduce exact pipeline output (verified char-for-char incl. ` -> ` and `(s)`). ✓
**4. G1:** Every non-verified VI word carries an inline G1 flag comment; English fallback automatic. ✓
