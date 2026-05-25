# GG Tank Watch Redesign (PR-B) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework the GG Tank Watch dashboard so it states facts and defers to officials (no directives), reads as unofficial, reclaims map real-estate, reorganizes News and Info, rebrands to "GG Tank Watch", and adds Nominatim result caching.

**Architecture:** Single-file static app (`dashboard.html`: inline CSS + vanilla JS, no build step, no JS test runner) plus a standalone `terms.html` and a Python eval suite under `eval/`. All changes are surgical edits to `dashboard.html` (+ small `terms.html` text edits). Verification is the existing Python eval suite as a regression guard (must stay 41/41) plus browser-QA assertions via the gstack `browse` tool — the same method that verified PR-A. There is no pytest harness for CSS/copy, so do not invent one.

**Tech Stack:** HTML5, inline CSS (custom-property theming, light/dark), vanilla ES5-style JS, Leaflet 1.9.4, OpenStreetMap Nominatim (client-side geocoding), `localStorage` for client state, Python 3 eval runner (`eval/run_all.py`).

**Liability lens (binding, from `docs/LEGAL.md` R1/R2 + `docs/DISTRIBUTION.md` §3):** the UI never issues directives ("STAY PUT", "LEAVE NOW") or implies safety. It states facts, labels severity, and points to ggcity.org/emergency + 911. Per-address verdicts stay in the Check tab where they are hedged.

**Translation gate (from PR-A pattern):** new user-facing strings are English-only; `t()` falls back to `entry.en` when `vi` is missing (`dashboard.html:1084`), so VI users see English until Anna verifies (G1 gate). Minimal VI redactions to existing strings also need Anna's sign-off. Do not machine-translate Vietnamese.

---

## File Structure

| File | Responsibility | Change |
|---|---|---|
| `dashboard.html` | The entire dashboard (markup, styles, behavior) | Modify — all tasks except the terms rename |
| `terms.html` | Standalone Terms & disclaimer page | Modify — branding text only (Task 1) |
| `CHANGELOG.md` | Release notes | Modify — add v0.8 entry (Task 9) |
| `eval/run_all.py` + `eval/test_*.py` | Regression guard | Run only — no edits; must stay 41/41 |

All `id` attributes referenced by `render()` (`#tank-temp`, `#tank-crack`, `#evac-residents`, `#evac-area`, `#evac-lifted`, `#evac-expanded`, `#evac-boundary`, `#schools`, `#source-list`, `#shelters-grid`, `#severity-chip`) MUST be preserved across restructuring — the render JS targets them by id.

---

## Task 1: Rebrand to "GG Tank Watch" (O1)

**Files:**
- Modify: `dashboard.html:6` (`<title>`), `dashboard.html:976-977` (title consts), topbar title span (`dashboard.html` ~`<span class="topbar-title">`)
- Modify: `terms.html` (page title + subtitle)

- [ ] **Step 1: Change the document `<title>`**

In `dashboard.html:6`, replace:

```html
  <title>GG MMA Tank Dashboard</title>
```

with:

```html
  <title>GG Tank Watch</title>
```

- [ ] **Step 2: Change the topbar title span**

Find the topbar title (added in PR-A inside `.topbar-left`):

```html
        <span class="topbar-title">GG MMA Tank Dashboard</span>
```

Replace the text with:

```html
        <span class="topbar-title">GG Tank Watch</span>
```

- [ ] **Step 3: Change the JS title constants**

In `dashboard.html:976-977`, replace:

```js
const NORMAL_TITLE = "GG MMA Tank Dashboard";
const BREAKING_TITLE = "\u{1F534} BREAKING — GG MMA Tank";
```

with:

```js
const NORMAL_TITLE = "GG Tank Watch";
const BREAKING_TITLE = "\u{1F534} BREAKING — GG Tank Watch";
```

- [ ] **Step 4: Rebrand `terms.html`**

In `terms.html`, replace the `<title>`:

```html
  <title>Terms &amp; Disclaimer — GG MMA Tank Dashboard</title>
```

with:

```html
  <title>Terms &amp; Disclaimer — GG Tank Watch</title>
```

And replace the subtitle line:

```html
    <p class="subtitle">GG MMA Tank Dashboard — an independent, volunteer-built community resource.</p>
```

with:

```html
    <p class="subtitle">GG Tank Watch — an independent, volunteer-built community resource.</p>
```

- [ ] **Step 5: Verify no stale brand strings remain**

Run: `grep -n "GG MMA Tank Dashboard\|BREAKING — GG MMA Tank" dashboard.html terms.html`
Expected: no matches (the descriptive meta "Garden Grove MMA tank emergency" in `dashboard.html:8` and `terms.html` is fine — it describes the incident, not the brand, and stays).

- [ ] **Step 6: Commit**

```bash
git add dashboard.html terms.html
git commit -m "refactor(brand): rename GG MMA Tank Dashboard to GG Tank Watch"
```

---

## Task 2: Topbar toggle labels — Viet/Eng + sun/moon (O2, O3)

**Files:**
- Modify: `dashboard.html` — theme-toggle button default (in topbar markup), `applyLang` (~`dashboard.html:1093-1111`), `applyTheme` (`dashboard.html:1241-1245`)

**Behavior contract:** a toggle button shows the state it switches TO. Language: when English is active, show `Viet`; when Vietnamese active, show `Eng`. Theme: when light is active, show 🌙 (switch to dark); when dark active, show ☀ (switch to light). Both `applyLang` and `applyTheme` set the theme button text today (duplication) — both must produce the icon.

- [ ] **Step 1: Set the theme button default to a moon icon in markup**

Find the theme toggle button in the topbar:

```html
        <button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()" data-i18n="theme.dark">Dark</button>
```

Replace with (drop `data-i18n`, set the moon glyph, add an accessible label):

```html
        <button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()" aria-label="Toggle light/dark theme" title="Toggle theme">🌙</button>
```

- [ ] **Step 2: Make `applyTheme` set the sun/moon icon**

In `dashboard.html:1241-1245`, replace:

```js
function applyTheme(theme) {
  document.documentElement.classList.toggle("theme-dark", theme === "dark");
  document.documentElement.classList.toggle("theme-light", theme !== "dark");
  $("theme-toggle").textContent = theme === "dark" ? t("theme.light") : t("theme.dark");
}
```

with:

```js
function applyTheme(theme) {
  document.documentElement.classList.toggle("theme-dark", theme === "dark");
  document.documentElement.classList.toggle("theme-light", theme !== "dark");
  // Button shows the theme it switches TO: dark active -> sun, light active -> moon.
  $("theme-toggle").textContent = theme === "dark" ? "☀" : "🌙";
}
```

- [ ] **Step 3: Update the `applyLang` toggle-button block to Viet/Eng + icon**

In `dashboard.html` (the `applyLang` function, ~lines 1104-1110), replace this block:

```js
  var langBtn = document.getElementById("lang-toggle");
  if (langBtn) langBtn.textContent = currentLang === "en" ? "VI" : "EN";
  var themeBtn = document.getElementById("theme-toggle");
  if (themeBtn) {
    var isDark = document.documentElement.classList.contains("theme-dark");
    themeBtn.textContent = isDark ? t("theme.light") : t("theme.dark");
  }
```

with:

```js
  var langBtn = document.getElementById("lang-toggle");
  if (langBtn) langBtn.textContent = currentLang === "en" ? "Viet" : "Eng";
  var themeBtn = document.getElementById("theme-toggle");
  if (themeBtn) {
    var isDark = document.documentElement.classList.contains("theme-dark");
    themeBtn.textContent = isDark ? "☀" : "🌙";
  }
```

- [ ] **Step 4: Browser-QA verify**

Serve and drive with the `browse` tool (`$B` = the browse binary). Run:

```bash
$B goto http://localhost:8099/dashboard.html
$B js "document.getElementById('lang-toggle').textContent"
# Expected: "Viet"  (English is default, button offers Vietnamese)
$B js "document.getElementById('theme-toggle').textContent"
# Expected: "🌙"  (light is default, button offers dark)
$B js "toggleTheme(); document.getElementById('theme-toggle').textContent"
# Expected: "☀"
$B js "toggleLang(); document.getElementById('lang-toggle').textContent"
# Expected: "Eng"
```

- [ ] **Step 5: Commit**

```bash
git add dashboard.html
git commit -m "feat(topbar): Viet/Eng language labels and sun/moon theme icons"
```

---

## Task 3: Hero → neutral status line (O4, O5, O6, O7)

**Files:**
- Modify: `dashboard.html` — hero markup (`.hero` section), hero CSS (`dashboard.html:210-250`), i18n strings (in `STRINGS`), hero render block (`dashboard.html:1791-1846`)

**What changes:** remove the "What should I do?" label, the directive action verb (`STAY PUT.`/`LEAVE NOW.`), and the directive instruction line. Show: the neutral situation summary (`snap.incident.status_headline`) + a **labeled** severity ("Incident severity: HIGH"). No per-user zone verdict in the hero (the Check tab owns that). The official pointer is NOT repeated here — the persistent safety strip directly below (added in PR-A) already carries "Informational only / call 911 / Official source: ggcity.org/emergency", so repeating it would re-bloat the exact real-estate we are reclaiming.

**Preserve:** the zone-flip takeover logic (`dashboard.html:1823-1837`) still reads `zone`; keep computing `zone` but stop rendering directives. (The takeover modal's "LEAVE NOW" is itself a directive and is flagged in `docs/REDESIGN_PUNCHLIST.md` for a separate liability decision — do NOT remove it in this task.)

- [ ] **Step 1: Replace the hero markup**

Find the hero section:

```html
    <section class="hero" id="hero">
      <div class="hero-label" data-i18n="hero.label">What should I do?</div>
      <h1 class="hero-action" id="hero-action" data-i18n="hero.loading">Loading...</h1>
      <p class="hero-instruction" id="hero-instruction" data-i18n="hero.waiting">Waiting for data</p>
      <div class="hero-context">
        <span class="severity-chip" id="severity-chip">--</span>
        <span class="hero-status" id="hero-status">--</span>
      </div>
    </section>
```

Replace with:

```html
    <section class="hero" id="hero">
      <div class="hero-severity">
        <span class="hero-severity-label" data-i18n="hero.severity.label">Incident severity:</span>
        <span class="severity-chip" id="severity-chip">--</span>
      </div>
      <p class="hero-summary" id="hero-summary" data-i18n="hero.summary.loading">Loading current status…</p>
    </section>
```

- [ ] **Step 2: Replace the hero CSS**

In `dashboard.html:210-250`, replace the `.hero` through `.hero-status` rules:

```css
    /* ===== HERO ===== */
    .hero {
      padding: 12px 16px 10px;
      text-align: center;
      flex-shrink: 0;
      border-bottom: 1px solid var(--border);
    }
    .hero-label {
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      color: var(--text-muted);
      margin-bottom: 2px;
    }
    .hero-action {
      font-size: clamp(26px, 7vw, 40px);
      font-weight: 800;
      line-height: 1.1;
      letter-spacing: -0.5px;
    }
    .hero-action.act-safe { color: var(--safe); }
    .hero-action.act-danger { color: var(--high); }
    .hero-action.act-unknown { color: var(--text-sec); }
    .hero-instruction {
      font-size: 14px;
      color: var(--text-sec);
      margin: 2px 0 6px;
      font-weight: 500;
    }
    .hero-context {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .hero-status {
      font-size: 12px;
      color: var(--text-muted);
    }
```

with (compact, no directive styles; summary clamped to 3 lines):

```css
    /* ===== HERO (neutral status) ===== */
    .hero {
      padding: 8px 16px 8px;
      text-align: center;
      flex-shrink: 0;
      border-bottom: 1px solid var(--border);
    }
    .hero-severity {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      margin-bottom: 4px;
    }
    .hero-severity-label {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      color: var(--text-sec);
    }
    .hero-summary {
      font-size: 13px;
      line-height: 1.4;
      color: var(--text-sec);
      margin: 0;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
```

Note: the `.severity-chip` and `.sev-*` rules (just below `.hero-status` in the source) are unchanged and still apply — do not touch them.

- [ ] **Step 3: Add/replace the hero i18n strings**

In `STRINGS`, find the hero block (the keys `hero.label`, `hero.loading`, `hero.waiting`, `hero.leave.*`, `hero.stay.*`, `hero.unknown.*`, `hero.allclear.*`). Replace that entire block with the smaller neutral set (the directive keys are no longer referenced after Step 4):

```js
  // Hero (neutral status — no directives)
  "hero.severity.label": { en: "Incident severity:" },
  "hero.summary.loading": { en: "Loading current status…" },
  "hero.summary.default": { en: "Active chemical-tank incident in Garden Grove. Follow official orders." },
  "hero.summary.resolved": { en: "Incident resolved. See ggcity.org/emergency for the latest." },
```

VI: omitted intentionally — falls back to EN until Anna verifies (G1). The takeover keys (`takeover.*`) are still used by the takeover modal — leave them.

- [ ] **Step 4: Replace the hero render block**

In `dashboard.html:1791-1846`, replace from the `// Hero — "What should I do?"` comment through the severity-chip/status_headline block (the lines that set `heroAction`, `heroInstr`, `heroStatus`, insert the chip, and append `status_headline`). Replace this entire span:

```js
  // Hero — "What should I do?"
  var you = snap.you || {};
  var zone = you.zone_status || "unknown";
  var heroAction = $("hero-action");
  var heroInstr = $("hero-instruction");
  var heroStatus = $("hero-status");
  heroAction.className = "hero-action";

  if (snap.incident && snap.incident.resolved_iso) {
    heroAction.textContent = t("hero.allclear.action");
    heroAction.classList.add("act-safe");
    heroInstr.textContent = t("hero.allclear.instr");
    heroStatus.textContent = t("hero.allclear.status", { time: fmtAbsTime(snap.incident.resolved_iso) });
  } else if (zone === "inside") {
    heroAction.textContent = t("hero.leave.action");
    heroAction.classList.add("act-danger");
    heroInstr.textContent = t("hero.leave.instr");
    heroStatus.textContent = t("hero.leave.status");
  } else if (zone === "outside_downwind" || zone === "outside") {
    heroAction.textContent = t("hero.stay.action");
    heroAction.classList.add("act-safe");
    heroInstr.textContent = t("hero.stay.instr");
    heroStatus.textContent = zone === "outside_downwind"
      ? t("hero.stay.status.downwind")
      : t("hero.stay.status");
  } else {
    heroAction.textContent = t("hero.unknown.action");
    heroAction.classList.add("act-unknown");
    heroInstr.textContent = t("hero.unknown.instr");
    heroStatus.textContent = t("hero.unknown.status");
  }
```

with (compute `zone` only for the takeover; render neutral severity + summary):

```js
  // Hero — neutral situation status (no directives; per-address verdicts live in the Check tab)
  var you = snap.you || {};
  var zone = you.zone_status || "unknown";
  var heroSummary = $("hero-summary");
  var resolved = !!(snap.incident && snap.incident.resolved_iso);
  if (resolved) {
    heroSummary.textContent = t("hero.summary.resolved");
  } else {
    var headline = (snap.incident && snap.incident.status_headline) || "";
    heroSummary.textContent = headline || t("hero.summary.default");
  }
```

Then, the severity-chip block lower down (`dashboard.html:1839-1846`) currently reads:

```js
  // Severity chip
  var sev = (snap.incident && snap.incident.severity) || "low";
  var sevChip = $("severity-chip");
  sevChip.className = "severity-chip sev-" + sev;
  sevChip.textContent = sev;
  $("hero-status").insertAdjacentElement("beforebegin", sevChip);
  var statusHL = (snap.incident && snap.incident.status_headline) || "";
  if (statusHL) heroStatus.textContent += " · " + statusHL;
```

Replace it with (chip stays in place inside `.hero-severity`; no more `hero-status` append, since the summary now carries `status_headline`):

```js
  // Severity chip (labeled by the "Incident severity:" prefix in markup)
  var sev = (snap.incident && snap.incident.severity) || "low";
  var sevChip = $("severity-chip");
  sevChip.className = "severity-chip sev-" + sev;
  sevChip.textContent = sev;
```

- [ ] **Step 5: Guard the offline fallback that references `hero-action`**

The fetch-failure path at `dashboard.html:1989-1992` sets `$("hero-action").textContent`. Find:

```js
    if (lastZoneStatus === null) {
      $("hero-action").textContent = t("hero.loading");
```

`#hero-action` no longer exists, so this would throw. Replace `$("hero-action")` with `$("hero-summary")` and the key with the loading summary:

```js
    if (lastZoneStatus === null) {
      $("hero-summary").textContent = t("hero.summary.loading");
```

- [ ] **Step 6: Browser-QA verify**

```bash
$B goto http://localhost:8099/dashboard.html
$B js "!!document.getElementById('hero-action') || !!document.getElementById('hero-instruction')"
# Expected: "false"  (directive elements removed)
$B js "document.querySelector('.hero-severity-label').textContent"
# Expected: "Incident severity:"
$B js "document.getElementById('severity-chip').textContent"
# Expected: a severity word like "high" (from status.json)
$B js "/STAY PUT|LEAVE NOW|What should I do/i.test(document.querySelector('.hero').innerText)"
# Expected: "false"
$B viewport 390x844
$B js "var t=document.querySelector('.tab-bar').getBoundingClientRect(); t.bottom<=window.innerHeight+1"
# Expected: "true"  (tab bar still on-screen; real-estate fix did not break layout)
```

- [ ] **Step 7: Commit**

```bash
git add dashboard.html
git commit -m "feat(hero): neutral status line — drop directive, label severity, reclaim space"
```

---

## Task 4: UPDATE banner click-to-dismiss (O8)

**Files:**
- Modify: `dashboard.html` — `setBanners` (`dashboard.html:1323-1332`), the banner-build block (`dashboard.html:1779-1788`)

**Behavior:** the "UPDATE — N new official statement(s)" banner (the `update` kind) is dismissible. Clicking it (which also navigates to News) records the newest official-statement timestamp in `localStorage` under `gg-update-ack-iso`. The update banner is suppressed while the newest statement's `time_iso` equals the acked value; a newer statement changes the value and the banner returns. The `breaking` (urgent) banner is NOT dismissible — only `update`.

- [ ] **Step 1: Add the ack helpers and a signature param to `setBanners`**

Replace `setBanners` (`dashboard.html:1323-1332`):

```js
function setBanners(banners) {
  $("banners").innerHTML = banners.map(function(b) {
    var clickable = (b.kind === "breaking" || b.kind === "update");
    var action = clickable ? '<span class="banner-action">' + t("banner.action.news") + '</span>' : '';
    var onclick = clickable ? 'onclick="switchTab(\'news\')"' : '';
    return '<div class="banner banner-' + b.kind + '" ' + onclick + '>' +
      '<span><strong>' + b.title + '</strong> ' + (b.message || '') + '</span>' +
      action + '</div>';
  }).join("");
}
```

with:

```js
function updateAckSig() {
  try { return localStorage.getItem("gg-update-ack-iso") || ""; } catch (e) { return ""; }
}
function ackUpdate(sig) {
  try { if (sig) localStorage.setItem("gg-update-ack-iso", sig); } catch (e) {}
}
window.ackUpdate = ackUpdate;

function setBanners(banners) {
  $("banners").innerHTML = banners.map(function(b) {
    var clickable = (b.kind === "breaking" || b.kind === "update");
    var action = clickable ? '<span class="banner-action">' + t("banner.action.news") + '</span>' : '';
    // The update banner records the latest-statement signature on click, then dismisses
    // until a newer statement arrives. Breaking (urgent) banners just navigate.
    var onclick = b.kind === "update"
      ? 'onclick="ackUpdate(\'' + (b.sig || '') + '\'); switchTab(\'news\'); this.remove()"'
      : (clickable ? 'onclick="switchTab(\'news\')"' : '');
    return '<div class="banner banner-' + b.kind + '" ' + onclick + '>' +
      '<span><strong>' + b.title + '</strong> ' + (b.message || '') + '</span>' +
      action + '</div>';
  }).join("");
}
```

- [ ] **Step 2: Compute the signature and suppress an acked update banner**

In the banner-build block (`dashboard.html:1779-1788`), replace:

```js
  if (snap.breaking) {
    var level = snap.breaking_level || "urgent";
    if (level === "info") {
      banners.push({kind:"update", title: t("banner.update.title"), message: snap.breaking_reason || ""});
      stopBreakingTitle();
    } else {
      banners.push({kind:"breaking", title: t("banner.urgent.title"), message: snap.breaking_reason || ""});
      startBreakingTitle();
    }
  } else { stopBreakingTitle(); }
```

with:

```js
  if (snap.breaking) {
    var level = snap.breaking_level || "urgent";
    if (level === "info") {
      // Signature = newest official-statement timestamp. Suppress the update banner
      // once the user has acked this signature; a newer statement re-raises it.
      var newestStmtIso = (snap.official_statements || []).reduce(function(max, s) {
        var ti = s.time_iso || "";
        return ti > max ? ti : max;
      }, "");
      var sig = newestStmtIso || snap.last_updated_iso || "";
      if (sig !== updateAckSig()) {
        banners.push({kind:"update", title: t("banner.update.title"), message: snap.breaking_reason || "", sig: sig});
      }
      stopBreakingTitle();
    } else {
      banners.push({kind:"breaking", title: t("banner.urgent.title"), message: snap.breaking_reason || ""});
      startBreakingTitle();
    }
  } else { stopBreakingTitle(); }
```

- [ ] **Step 3: Browser-QA verify the dismiss cycle**

```bash
$B goto http://localhost:8099/dashboard.html
$B js "localStorage.removeItem('gg-update-ack-iso'); 'cleared'"
$B reload
$B js "!!document.querySelector('.banner-update')"          # may be true/false depending on status.json breaking flag
# Simulate ack with the current newest-statement signature, then re-render:
$B js "var s=(lastSnap.official_statements||[]).reduce(function(m,x){return (x.time_iso||'')>m?(x.time_iso||''):m;},''); ackUpdate(s); render(lastSnap); !!document.querySelector('.banner-update')"
# Expected: "false"  (acked -> suppressed)
$B js "ackUpdate('1970-01-01T00:00:00Z'); render(lastSnap); !!document.querySelector('.banner-update') === (lastSnap.breaking && (lastSnap.breaking_level==='info'))"
# Expected: "true"  (older ack -> banner returns when an info-level breaking is present)
```

If `status.json` has no active `breaking`/info update at test time, assert the helper instead:

```bash
$B js "typeof ackUpdate === 'function' && typeof updateAckSig === 'function'"
# Expected: "true"
```

- [ ] **Step 4: Commit**

```bash
git add dashboard.html
git commit -m "feat(banner): UPDATE banner dismisses on click until a newer statement arrives"
```

---

## Task 5: News → unified reverse-chron timeline (O9)

**Files:**
- Modify: `dashboard.html` — News panel markup (`#panel-news`), the statements+videos render block (`dashboard.html:1877-1942`), i18n (`news.*`), minor CSS for type chips

**Data shapes (confirmed):**
- `snap.official_statements[]`: `{ time_iso, agency, text, source_url }`
- `snap.videos[]`: `{ youtube_id?, is_video?, thumbnail_url?, url, title, outlet, published_iso }`

**Behavior:** merge both arrays into one list, normalized to `{ when, type, source, title, text, url, thumb, isVideo }`, sort by `when` descending, render each with a type chip (🏛 Official / 📰 Article / ▶ Video). Statements render as quote cards (no thumb); articles/videos render with the existing thumbnail treatment. Preserve OG-thumbnail hydration (`hydrateMissingThumbnails()`).

- [ ] **Step 1: Replace the News panel markup**

Find the News panel:

```html
      <div class="tab-panel" id="panel-news">
        <div class="news-section-label" id="statements-count">0 official statements</div>
        <div id="statements-list"></div>
        <div class="news-section-label" data-i18n="news.coverage">Coverage</div>
        <div id="videos-list"></div>
      </div>
```

Replace with:

```html
      <div class="tab-panel" id="panel-news">
        <div class="news-section-label" id="news-count" data-i18n="news.feed.title">News &amp; updates</div>
        <div id="news-feed"></div>
      </div>
```

- [ ] **Step 2: Replace the statements + videos render block with a unified feed**

In `dashboard.html:1877-1942`, replace the entire `// News tab: statements` block through the end of the `// News tab: videos/articles` block (the two `.map(...)` renders that target `#statements-list`, `#statements-count`, and `#videos-list`) with:

```js
  // News tab: unified reverse-chron feed (official statements + articles + videos)
  var feed = [];
  (snap.official_statements || []).forEach(function(s) {
    feed.push({
      when: s.time_iso || "",
      type: "official",
      source: s.agency || "—",
      text: s.text || "",
      url: s.source_url || "",
      isVideo: false,
      thumb: ""
    });
  });
  (snap.videos || []).forEach(function(v) {
    var isVid = !!(v.youtube_id) || v.is_video === true;
    feed.push({
      when: v.published_iso || "",
      type: isVid ? "video" : "article",
      source: v.outlet || "—",
      title: v.title || t("news.untitled"),
      url: v.url || "",
      isVideo: isVid,
      thumb: v.thumbnail_url || ""
    });
  });
  feed.sort(function(a, b) {
    var ta = a.when ? new Date(a.when).getTime() : 0;
    var tb = b.when ? new Date(b.when).getTime() : 0;
    return tb - ta;
  });

  $("news-count").textContent = t("news.feed.title");
  var feedEl = $("news-feed");
  if (!feed.length) {
    feedEl.innerHTML = '<div style="padding:10px 12px;color:var(--text-muted);font-size:12px">' + t("news.empty") + '</div>';
  } else {
    feedEl.innerHTML = feed.map(function(it) {
      var chip = it.type === "official" ? '<span class="feed-chip feed-chip-official">' + t("news.type.official") + '</span>'
               : it.type === "video"    ? '<span class="feed-chip feed-chip-video">' + t("news.type.video") + '</span>'
               :                          '<span class="feed-chip feed-chip-article">' + t("news.type.article") + '</span>';
      var when = it.when ? fmtAbsDateTime(it.when) : "";
      var meta = '<div class="feed-meta">' + chip +
        '<strong>' + it.source + '</strong>' +
        (when ? ' · <span class="feed-time">' + when + '</span>' : '') +
      '</div>';
      if (it.type === "official") {
        return '<div class="feed-item feed-item-official">' + meta +
          '<div class="feed-text">' + it.text + '</div>' +
          (it.url ? '<a class="feed-source" href="' + it.url + '" target="_blank" rel="noopener">' + t("news.source") + '</a>' : '') +
        '</div>';
      }
      var escapedUrl = (it.url || "").replace(/"/g, "&quot;");
      var thumbClass = it.thumb ? "" : (it.isVideo ? "placeholder-video" : "placeholder-article");
      return '<a class="feed-item news-item" href="' + it.url + '" target="_blank" rel="noopener" data-needs-og="' + (!it.thumb) + '" data-url="' + escapedUrl + '">' +
        '<div class="news-thumb ' + thumbClass + '">' +
          (it.thumb ? '<img loading="lazy" src="' + it.thumb + '" alt="">' : '') +
          (it.isVideo ? '<div class="news-thumb-play"></div>' : '') +
        '</div>' +
        '<div class="news-meta">' + meta +
          '<div class="news-title">' + it.title + '</div>' +
        '</div>' +
      '</a>';
    }).join("");
    hydrateMissingThumbnails();
  }
```

- [ ] **Step 3: Add the feed i18n strings**

In `STRINGS`, in the News block, add (keep the existing `news.source`, `news.empty`, `news.untitled`; the `news.coverage` and `news.statements.count` keys become unused — leave them or delete, harmless either way):

```js
  "news.feed.title": { en: "News & updates" },
  "news.type.official": { en: "🏛 Official" },
  "news.type.article": { en: "📰 Article" },
  "news.type.video": { en: "▶ Video" },
```

- [ ] **Step 4: Add type-chip CSS**

After the existing `.news-item`/`.stmt` rules (search for `.news-section-label` to find the News CSS region), add:

```css
    .feed-item { padding: 10px 12px; border-bottom: 1px solid var(--border); display: block; color: inherit; text-decoration: none; }
    .feed-item-official { cursor: default; }
    a.feed-item { display: flex; gap: 10px; }
    .feed-meta { font-size: 11px; color: var(--text-muted); display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 3px; }
    .feed-chip { font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 4px; white-space: nowrap; }
    .feed-chip-official { background: var(--accent-light); color: var(--accent); }
    .feed-chip-article  { background: var(--banner-update-bg); color: var(--moderate); }
    .feed-chip-video    { background: var(--high-bg); color: var(--high); }
    .feed-text { font-size: 13px; line-height: 1.4; color: var(--text); margin: 2px 0 4px; }
    .feed-source { font-size: 11px; color: var(--accent); text-decoration: none; }
    .feed-source:hover { text-decoration: underline; }
```

(`--accent-light`, `--banner-update-bg`, `--high-bg`, `--high`, `--moderate` are all defined in both themes near `dashboard.html:14-62`.)

- [ ] **Step 5: Browser-QA verify ordering and tagging**

```bash
$B goto http://localhost:8099/dashboard.html
$B click ".tab-btn[data-tab='news']"
$B js "document.querySelectorAll('#news-feed .feed-item').length > 0"
# Expected: "true"
$B js "var c=[].slice.call(document.querySelectorAll('#news-feed .feed-chip')).map(function(e){return e.textContent;}); JSON.stringify(c.slice(0,3))"
# Expected: a mix of "🏛 Official" / "📰 Article" / "▶ Video"
$B js "var ts=[].slice.call(document.querySelectorAll('#news-feed .feed-time')).map(function(e){return new Date(e.textContent).getTime();}).filter(Boolean); JSON.stringify(ts)===JSON.stringify(ts.slice().sort(function(a,b){return b-a;}))"
# Expected: "true"  (descending by time)
$B js "!document.getElementById('statements-list') && !document.getElementById('videos-list')"
# Expected: "true"  (old split containers gone)
```

- [ ] **Step 6: Commit**

```bash
git add dashboard.html
git commit -m "feat(news): unified reverse-chron feed of statements, articles, and videos"
```

---

## Task 6: Info tab information-architecture reorg (O10)

**Files:**
- Modify: `dashboard.html` — `#panel-info` markup only. The render JS is untouched **provided every targeted id is preserved** (`#tank-temp`, `#tank-crack`, `#evac-residents`, `#evac-area`, `#evac-lifted`, `#evac-expanded`, `#evac-boundary`, `#shelters-grid`, `#schools`, `#source-list`).

**New order, top to bottom (by resident need):** (1) Incident status = Tank + Evacuation merged under one heading; (2) Where to go = Shelters; (3) Closures = Schools; (4) Sources & how this works = Sources + Methodology, inside a collapsed `<details>`; (5) About = the PR-A "Who made this" block + terms link, inside a collapsed `<details>`, moved to the bottom.

- [ ] **Step 1: Add `<details>` styling**

In the Info CSS region (search `.info-section`), add:

```css
    .info-fold { border-bottom: 1px solid var(--border); }
    .info-fold > summary {
      cursor: pointer; padding: 12px 16px; font-size: 11px; font-weight: 700;
      letter-spacing: 0.5px; text-transform: uppercase; color: var(--text-sec);
      list-style: none;
    }
    .info-fold > summary::-webkit-details-marker { display: none; }
    .info-fold > summary::after { content: " ▸"; color: var(--text-muted); }
    .info-fold[open] > summary::after { content: " ▾"; }
    .info-group-title {
      padding: 12px 16px 0; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
      text-transform: uppercase; color: var(--text-sec);
    }
```

- [ ] **Step 2: Rewrite the `#panel-info` inner markup**

Replace the entire contents of `<div class="info-panel-inner"> … </div>` (the PR-A "Who made this" section plus Tank, Evacuation, Evacuation shelters, Schools closed, Sources verified, Methodology & trust) with the reordered structure below. Element ids are preserved exactly; only grouping and order change.

```html
        <div class="info-panel-inner">

          <!-- 1. Incident status (Tank + Evacuation merged) -->
          <div class="info-group-title" data-i18n="info.group.status">Incident status</div>
          <div class="info-section">
            <div class="info-section-title" data-i18n="info.tank.title">Tank</div>
            <div class="info-big mono" id="tank-temp">--</div>
            <div class="info-row"><span class="k" data-i18n="info.tank.crack">Crack observed</span><span class="v" id="tank-crack">--</span></div>
          </div>
          <div class="info-section">
            <div class="info-section-title" data-i18n="info.evac.title">Evacuation</div>
            <div class="info-big mono" id="evac-residents">--</div>
            <div class="info-row"><span class="k" data-i18n="info.evac.area">Area</span><span class="v mono" id="evac-area">--</span></div>
            <div class="info-row"><span class="k" data-i18n="info.evac.lifted">Order lifted</span><span class="v" id="evac-lifted">--</span></div>
            <div class="info-row"><span class="k" data-i18n="info.evac.expanded">Expanded today</span><span class="v" id="evac-expanded">--</span></div>
            <div class="info-row"><span class="k" data-i18n="info.evac.boundary">Boundary</span><span class="v" style="font-size:11px;text-align:right;max-width:60%" id="evac-boundary">--</span></div>
          </div>

          <!-- 2. Where to go -->
          <div class="info-group-title" data-i18n="info.group.wheretogo">Where to go</div>
          <div class="info-section">
            <div class="info-section-title" data-i18n="info.shelters.title">Evacuation shelters</div>
            <div class="shelters-cta" data-i18n-html="info.shelters.cta">
              &#128719; <strong>Live list at <a href="https://ggcity.org/emergency" target="_blank" rel="noopener">ggcity.org/emergency</a></strong> &mdash; the city is the source of truth; the list below is a snapshot.
            </div>
            <div id="shelters-grid" class="shelters-grid"></div>
          </div>

          <!-- 3. Closures -->
          <div class="info-group-title" data-i18n="info.group.closures">Closures</div>
          <div class="info-section">
            <div class="info-section-title" data-i18n="info.schools.title">Schools closed</div>
            <div id="schools">--</div>
          </div>

          <!-- 4. Sources & how this works (collapsed) -->
          <details class="info-fold">
            <summary data-i18n="info.group.sources">Sources &amp; how this works</summary>
            <div class="info-section">
              <div class="info-section-title" data-i18n="info.sources.title">Sources verified</div>
              <div id="source-list"></div>
            </div>
            <div class="methodology-section">
              <div class="info-section-title" data-i18n="info.method.title">Methodology &amp; trust</div>
              <div class="methodology-body">
                <p data-i18n-html="info.method.pipeline"><strong>Data pipeline:</strong> Status updated every 30 min via verified web sources (official agency feeds, city websites, news outlets). Each fact is cross-referenced against multiple sources before publishing.</p>
                <p data-i18n-html="info.method.wind"><strong>Wind data:</strong> Live observations from NOAA station KFUL (Fullerton Municipal Airport), polled every 60 seconds. Plume direction is estimated from wind bearing + cone model -- not atmospheric dispersion modeling.</p>
                <p data-i18n-html="info.method.blast"><strong>Blast zones:</strong> Radii estimated from BLEVE overpressure scaling for ~7,000 gal MMA (~100 tonnes TNT-equivalent). Visual scale matches the OCFA/OC Register published map. Not authoritative for legal purposes.</p>
                <p data-i18n-html="info.method.checker"><strong>Safety checker:</strong> Uses ray-casting (point-in-polygon) for evac zone, haversine distance for blast zones, bearing math for plume cone intersection. Geocoding via OpenStreetMap Nominatim.</p>
                <p data-i18n-html="info.method.eval"><strong>Evaluation:</strong> This dashboard has a <a href="eval/">test suite</a> including behavioral tests (writer logic, schema validation, safety checker math, geocoder behavior) and LLM-as-judge rubrics for design and data quality. All design decisions are logged in <a href="DESIGN_LOG.md">DESIGN_LOG.md</a> with rationale and rubric scores.</p>
                <p data-i18n-html="info.method.disclaimer"><strong>Disclaimer:</strong> This is a community tool, not an official government resource. All content is informational only and may be inaccurate or out of date. Always verify with <a href="https://ggcity.org/emergency" target="_blank" rel="noopener">ggcity.org/emergency</a>; in an emergency, call 911. See the full <a href="terms.html">Terms &amp; disclaimer</a>.</p>
              </div>
            </div>
          </details>

          <!-- 5. About (collapsed, bottom) -->
          <details class="info-fold">
            <summary data-i18n="info.about.title">Who made this</summary>
            <div class="info-section">
              <div class="methodology-body">
                <p data-i18n="info.about.body">Built by two local volunteers, Mike &amp; Anna, to help our community during the Garden Grove tank emergency. It is not affiliated with, endorsed by, or operated by the City of Garden Grove, the Orange County Fire Authority, or any government agency. Free, no sign-up, no ads — we do not collect your data.</p>
                <p data-i18n="info.about.official">For official orders and updates, always use ggcity.org/emergency · 714-628-7085 · OCFA.</p>
                <p><a href="terms.html" data-i18n="info.about.termslink">Read the full Terms &amp; disclaimer</a></p>
              </div>
            </div>
          </details>

        </div>
```

- [ ] **Step 3: Add the group-heading i18n strings**

In `STRINGS` (Info block), add:

```js
  "info.group.status": { en: "Incident status" },
  "info.group.wheretogo": { en: "Where to go" },
  "info.group.closures": { en: "Closures" },
  "info.group.sources": { en: "Sources & how this works" },
```

(`info.about.title` already exists from PR-A and is reused as the About `<summary>`.)

- [ ] **Step 4: Browser-QA verify ids preserved and data renders**

```bash
$B goto http://localhost:8099/dashboard.html
$B click ".tab-btn[data-tab='info']"
$B js "['tank-temp','tank-crack','evac-residents','evac-area','evac-lifted','evac-expanded','evac-boundary','shelters-grid','schools','source-list'].every(function(id){return !!document.getElementById(id);})"
# Expected: "true"  (all render-targeted ids preserved)
$B js "document.getElementById('tank-temp').textContent !== '--'"
# Expected: "true"  (render populated it -> reorg didn't break the JS wiring)
$B js "document.querySelectorAll('details.info-fold').length"
# Expected: "2"  (Sources, About are collapsible)
$B js "[].slice.call(document.querySelectorAll('.info-group-title')).map(function(e){return e.textContent;}).join('|')"
# Expected: "Incident status|Where to go|Closures"
```

- [ ] **Step 5: Commit**

```bash
git add dashboard.html
git commit -m "refactor(info): reorganize Info tab by resident need, fold trust/about sections"
```

---

## Task 7: Nominatim geocode result caching (O11)

**Files:**
- Modify: `dashboard.html` — `geocodeAddress` (`dashboard.html:1523-1553`)

**Behavior:** cache successful geocode results in `localStorage` keyed by the normalized query, with a 7-day TTL (aligns with the OSM tile policy's 7-day caching expectation). On a cache hit, return without hitting Nominatim. This satisfies the LEGAL §6 / R7 "results must be cached" requirement. `localStorage` access is wrapped in try/catch so the function still works where storage is unavailable (e.g. the Python eval reimplements geocoding separately and does not touch this JS).

- [ ] **Step 1: Add caching to `geocodeAddress`**

Replace `geocodeAddress` (`dashboard.html:1523-1553`):

```js
async function geocodeAddress(q, cfg) {
  var queryRaw = q.replace(/\s+and\s+/i, " & ");
  var bias = (cfg && cfg.map && cfg.map.geocode_bias) || "Orange County, CA";
  var viewbox = (cfg && cfg.map && cfg.map.geocode_viewbox);
  var looksFullAddr = /\b(CA|California|\d{5})\b/i.test(queryRaw);
  var queryWithBias = looksFullAddr ? queryRaw : queryRaw + ", " + bias;
  async function nominatim(qstr, vb) {
    var u = "https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" + encodeURIComponent(qstr);
    if (vb && vb.length === 4) u += "&viewbox=" + vb[0] + "," + vb[1] + "," + vb[2] + "," + vb[3] + "&bounded=1";
    var r = await fetch(u, { headers: { "Accept-Language": "en" } });
    if (!r.ok) throw new Error("Nominatim HTTP " + r.status);
    return await r.json();
  }
  var arr = await nominatim(queryWithBias);
  var hit = (arr && arr.length) ? arr[0] : null;
  // Keep results within the monitored region: if the bias query missed or landed
  // outside the incident viewbox, re-query bounded and discard the out-of-region
  // hit, so a far same-named match (e.g. a "Western Ave" in another county) can't
  // resolve to a confident verdict for the wrong place. In-region ambiguity stays
  // visible because renderSafetyResult always shows the matched address + distance.
  if (viewbox && viewbox.length === 4) {
    var w = viewbox[0], n = viewbox[1], e = viewbox[2], s = viewbox[3];
    var inBox = hit && parseFloat(hit.lon) >= w && parseFloat(hit.lon) <= e && parseFloat(hit.lat) >= s && parseFloat(hit.lat) <= n;
    if (!inBox) {
      var bArr = await nominatim(queryRaw, viewbox);
      hit = (bArr && bArr.length) ? bArr[0] : null;
    }
  }
  if (!hit) throw new Error("No result in the monitored area for: " + queryRaw);
  return { lat: parseFloat(hit.lat), lon: parseFloat(hit.lon), displayName: hit.display_name };
}
```

with (cache check at the top, cache write before each `return` of a successful hit):

```js
var GEOCODE_TTL_MS = 7 * 24 * 60 * 60 * 1000; // 7 days, per OSM caching policy
function geocodeCacheGet(key) {
  try {
    var raw = localStorage.getItem("gg-geocode-" + key);
    if (!raw) return null;
    var obj = JSON.parse(raw);
    if (!obj || (Date.now() - obj.at) > GEOCODE_TTL_MS) return null;
    return obj.val;
  } catch (e) { return null; }
}
function geocodeCacheSet(key, val) {
  try { localStorage.setItem("gg-geocode-" + key, JSON.stringify({ at: Date.now(), val: val })); } catch (e) {}
}

async function geocodeAddress(q, cfg) {
  var queryRaw = q.replace(/\s+and\s+/i, " & ");
  var cacheKey = queryRaw.trim().toLowerCase();
  // Nominatim policy requires caching identical queries (repeated identical
  // requests may be classified as faulty and blocked). Serve from cache first.
  var cached = geocodeCacheGet(cacheKey);
  if (cached) return cached;
  var bias = (cfg && cfg.map && cfg.map.geocode_bias) || "Orange County, CA";
  var viewbox = (cfg && cfg.map && cfg.map.geocode_viewbox);
  var looksFullAddr = /\b(CA|California|\d{5})\b/i.test(queryRaw);
  var queryWithBias = looksFullAddr ? queryRaw : queryRaw + ", " + bias;
  async function nominatim(qstr, vb) {
    var u = "https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" + encodeURIComponent(qstr);
    if (vb && vb.length === 4) u += "&viewbox=" + vb[0] + "," + vb[1] + "," + vb[2] + "," + vb[3] + "&bounded=1";
    var r = await fetch(u, { headers: { "Accept-Language": "en" } });
    if (!r.ok) throw new Error("Nominatim HTTP " + r.status);
    return await r.json();
  }
  var arr = await nominatim(queryWithBias);
  var hit = (arr && arr.length) ? arr[0] : null;
  // Keep results within the monitored region: if the bias query missed or landed
  // outside the incident viewbox, re-query bounded and discard the out-of-region
  // hit, so a far same-named match (e.g. a "Western Ave" in another county) can't
  // resolve to a confident verdict for the wrong place. In-region ambiguity stays
  // visible because renderSafetyResult always shows the matched address + distance.
  if (viewbox && viewbox.length === 4) {
    var w = viewbox[0], n = viewbox[1], e = viewbox[2], s = viewbox[3];
    var inBox = hit && parseFloat(hit.lon) >= w && parseFloat(hit.lon) <= e && parseFloat(hit.lat) >= s && parseFloat(hit.lat) <= n;
    if (!inBox) {
      var bArr = await nominatim(queryRaw, viewbox);
      hit = (bArr && bArr.length) ? bArr[0] : null;
    }
  }
  if (!hit) throw new Error("No result in the monitored area for: " + queryRaw);
  var result = { lat: parseFloat(hit.lat), lon: parseFloat(hit.lon), displayName: hit.display_name };
  geocodeCacheSet(cacheKey, result);
  return result;
}
```

- [ ] **Step 2: Browser-QA verify cache populates and serves**

```bash
$B goto http://localhost:8099/dashboard.html
$B click ".tab-btn[data-tab='check']"
$B js "localStorage.removeItem('gg-geocode-trask & harbor'); 'cleared'"
$B fill "#safety-input" "Trask and Harbor"
$B click "#safety-button"
$B wait --networkidle
$B js "!!localStorage.getItem('gg-geocode-trask & harbor')"
# Expected: "true"  (result cached after first lookup)
$B js "var o=JSON.parse(localStorage.getItem('gg-geocode-trask & harbor')); !!o.val && typeof o.val.lat==='number' && typeof o.at==='number'"
# Expected: "true"
```

- [ ] **Step 3: Regression — eval suite still green**

The Python geocoder test (`eval/test_geocoder.py`) reimplements geocoding in Python and does NOT exercise this JS, so it is unaffected — but run the full suite to confirm nothing else regressed:

Run: `python eval/run_all.py`
Expected: `TOTAL 41/41 (100.0% pass)`
Then discard the churn: `git restore eval/scores.jsonl`

- [ ] **Step 4: Commit**

```bash
git add dashboard.html
git commit -m "feat(geocoder): cache Nominatim results in localStorage (7-day TTL) per OSM policy"
```

---

## Task 8: Full regression + browser QA pass

**Files:** none (verification only)

- [ ] **Step 1: Eval suite**

Run: `python eval/run_all.py`
Expected: `TOTAL 41/41 (100.0% pass)`. Then: `git restore eval/scores.jsonl`

- [ ] **Step 2: Mobile layout regression (the PR #9 tab-bar risk)**

```bash
$B viewport 390x844
$B goto http://localhost:8099/dashboard.html
$B js "var b=document.querySelector('.tab-bar').getBoundingClientRect(); b.bottom<=window.innerHeight+1 && document.querySelectorAll('.tab-btn').length===4"
# Expected: "true"
```

- [ ] **Step 3: Liability scan — no directive copy survived anywhere**

```bash
$B js "/STAY PUT|LEAVE NOW|What should I do|LIKELY SAFE|an toàn/i.test(document.body.innerText)"
# Expected: "false"  (note: the takeover modal's hidden 'LEAVE NOW' text is in a hidden node and is flagged separately; if this returns true, confirm it is only the hidden #takeover element)
```

- [ ] **Step 4: Screenshot each tab for the user**

```bash
$B viewport 390x844
$B goto http://localhost:8099/dashboard.html
$B screenshot --viewport /tmp/ggb-map.png
$B click ".tab-btn[data-tab='news']"; $B screenshot --viewport /tmp/ggb-news.png
$B click ".tab-btn[data-tab='info']"; $B screenshot --viewport /tmp/ggb-info.png
$B click ".tab-btn[data-tab='check']"; $B screenshot --viewport /tmp/ggb-check.png
```

Read each PNG with the Read tool and confirm against the punch list before proposing merge.

---

## Task 9: CHANGELOG + ship

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add the v0.8 entry**

Insert above the `## [v0.7]` heading in `CHANGELOG.md`:

```markdown
## [v0.8] — 2026-05-25 (dashboard redesign — PR-B)

### Changed
- **Rebrand to "GG Tank Watch"** across the topbar, page titles, and terms page.
- **Hero is now a neutral status line** — removed the "What should I do?" framing and the "STAY PUT"/"LEAVE NOW" directive (liability: we issue no directives and imply no safety, per LEGAL R1/R2). Shows a labeled "Incident severity: HIGH" and a clamped situation summary; per-address verdicts stay in the Check tab. Reclaims map real-estate.
- **News is one unified reverse-chronological feed** — official statements, articles, and videos merged and tagged by type (Official / Article / Video), replacing the confusing statements-vs-Coverage split.
- **Info tab reorganized** by resident need: Incident status (tank + evacuation) → Where to go (shelters) → Closures (schools) → collapsible Sources & methodology → collapsible About.
- **Topbar toggles**: "VI"/"EN" → "Viet"/"Eng"; Light/Dark text → sun/moon icons.

### Added
- **UPDATE banner is dismissible** — clicking it marks the latest statement as seen (localStorage); it stays gone until a newer statement arrives.
- **Geocode result caching** (localStorage, 7-day TTL) to satisfy the OSM Nominatim caching policy.

### Notes
- New user-facing strings are English-only with EN fallback under VI until Anna verifies (G1 gate). Final hero/severity wording remains attorney-review-gated per `docs/LEGAL.md`. The takeover modal's "LEAVE NOW" directive is flagged for a separate liability decision in `docs/REDESIGN_PUNCHLIST.md`.
```

- [ ] **Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs(changelog): v0.8 dashboard redesign (PR-B)"
```

- [ ] **Step 3: Ship**

Hand off to the `/ship` workflow (push + PR against `main`, stop at the merge gate unless the user authorizes merge), mirroring PR-A.

---

## Self-Review

**1. Spec coverage** (punch-list O1–O11):
- O1 rebrand → Task 1 ✓
- O2 Viet/Eng → Task 2 ✓
- O3 sun/moon → Task 2 ✓
- O4 remove "STAY PUT" → Task 3 ✓
- O5 remove "What should I do?" → Task 3 ✓
- O6 label "HIGH" → Task 3 (hero.severity.label) ✓
- O7 hero real-estate → Task 3 (compact + clamp) ✓
- O8 UPDATE banner dismiss → Task 4 ✓
- O9 unified News timeline → Task 5 ✓
- O10 Info reorg → Task 6 ✓
- O11 Nominatim caching → Task 7 ✓
- Carried-over gates (VI sign-off, attorney review, error-report contact, takeover-directive decision) → recorded in CHANGELOG notes + `docs/REDESIGN_PUNCHLIST.md`, not implemented here (correctly out of scope).

**2. Placeholder scan:** every code step has complete code; verification steps have exact `$B`/`python` commands with expected output. No TBD/TODO/"similar to".

**3. Type/identifier consistency:**
- `updateAckSig()` / `ackUpdate()` defined in Task 4 Step 1 and used in Task 4 Step 2 ✓
- `geocodeCacheGet()` / `geocodeCacheSet()` / `GEOCODE_TTL_MS` defined and used in Task 7 ✓
- `#hero-summary` / `#severity-chip` defined in Task 3 markup and used in Task 3 render + Task 3 Step 5 offline fallback ✓
- `#news-feed` / `#news-count` defined in Task 5 markup and used in Task 5 render ✓
- Removed ids (`#hero-action`, `#hero-instruction`, `#hero-status`, `#statements-list`, `#statements-count`, `#videos-list`) are not referenced after their tasks; Task 3 Step 5 patches the one lingering `#hero-action` reference in the offline path ✓
- Preserved ids in Task 6 match the render JS targets ✓

---

## Execution Handoff

After saving the plan, choose an execution approach:

**1. Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks. Good here: 9 mostly-independent tasks against one file.

**2. Inline Execution** — execute in this session with checkpoints. Good if you want to watch each diff live and screenshot as we go (you have been iterating visually).
