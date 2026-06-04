# Resident Shareability (P1 social card + P2 share button) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make GG Tank Watch spread resident-to-resident — give every shared link a rich preview card (P1) and a one-tap Share button (P2) — since `noindex` (legal Phase-2 gate) means direct sharing is the only distribution channel.

**Architecture:** Static single-file app (`dashboard.html`) + static assets on Vercel. P1 adds Open Graph + Twitter meta tags pointing at a new static `og-image.png` (1200×630). P2 adds an icon button in the existing `.topbar-controls`, styled with the existing `.topbar-btn` class, wired to the Web Share API with a clipboard-copy fallback. No new runtime dependencies; no framework; no build step.

**Tech Stack:** Vanilla HTML/CSS/JS. OG image rendered once via system Microsoft Edge headless `--screenshot` (signed binary — works under Smart App Control; see global memory). Python only for the existing eval regression check.

**Guardrails (binding):**
- DO NOT touch the `noindex`/`nofollow` header in `vercel.json` — legal gate stays until Phase 2. (Social crawlers — facebookexternalhit/Twitterbot/Slackbot — render preview cards regardless of `noindex`, so P1 still works.)
- Keep the honest, non-over-claiming voice: name stays **"GG Tank Watch"**, copy keeps "unofficial / verify with officials." Never introduce "Safety." (See memory `naming-watch-not-safety`.)
- Absolute URLs in OG tags use the current production origin `https://gg-tank-dashboard.vercel.app` (crawlers require absolute). If a custom domain ships later (P3), update these four URLs.

---

### Task 0: Branch

**Files:** none (git only)

- [ ] **Step 1: Verify on main and clean**

Run: `git branch --show-current`
Expected: `main`

- [ ] **Step 2: Create the feature branch**

```bash
git switch -c feat/resident-shareability
```
Run: `git branch --show-current`
Expected: `feat/resident-shareability`

---

### Task 1: OG preview image (1200×630 PNG)

**Files:**
- Create: `scripts/og-image.html` (regenerable source template)
- Create: `og-image.png` (repo root — the served asset)

- [ ] **Step 1: Write the OG image source template**

Create `scripts/og-image.html` with a fixed 1200×630 canvas, brand celadon background, white wordmark, honest subtitle. System fonts only (headless has no web fonts):

```html
<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  html,body{margin:0;padding:0}
  .card{width:1200px;height:630px;box-sizing:border-box;
    background:#0e6f5e;color:#fff;display:flex;flex-direction:column;
    justify-content:center;padding:90px;
    font-family:Segoe UI,system-ui,-apple-system,sans-serif}
  .pill{display:inline-block;align-self:flex-start;border:2px solid rgba(255,255,255,.6);
    border-radius:999px;padding:8px 18px;font-size:24px;font-weight:600;letter-spacing:.08em;
    margin-bottom:34px}
  .mark{font-size:96px;font-weight:800;line-height:1.05;margin:0}
  .mark .tank{color:#d8eae5}
  .sub{font-size:38px;font-weight:500;margin-top:28px;color:#eafaf5;max-width:980px}
  .foot{font-size:26px;margin-top:40px;color:#cfe9e1}
</style></head>
<body><div class="card">
  <span class="pill">UNOFFICIAL · VOLUNTEER-BUILT</span>
  <h1 class="mark">GG <span class="tank">Tank</span> Watch</h1>
  <div class="sub">Situational awareness for the Garden Grove chemical-tank emergency.</div>
  <div class="foot">Routes you to official sources — always verify with ggcity.org/emergency</div>
</div></body></html>
```

- [ ] **Step 2: Render to PNG with signed Edge headless**

Run (PowerShell, single line; fresh user-data-dir; `| Out-Null` — never `2>$null` on the native exe):
```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=1200,630 --user-data-dir="$env:TEMP\og-edge-$(Get-Random)" --screenshot="C:\Users\redacted\Desktop\Mike Ilog Portfolio\GitHub Projects\gg-tank-dashboard\og-image.png" "file:///C:/Users/redacted/Desktop/Mike Ilog Portfolio/GitHub Projects/gg-tank-dashboard/scripts/og-image.html" | Out-Null
```

- [ ] **Step 3: Verify the PNG exists, is non-empty, and is 1200×630**

Run:
```powershell
$f="C:\Users\redacted\Desktop\Mike Ilog Portfolio\GitHub Projects\gg-tank-dashboard\og-image.png"; (Get-Item $f).Length; Add-Type -AssemblyName System.Drawing; $i=[System.Drawing.Image]::FromFile($f); "$($i.Width)x$($i.Height)"; $i.Dispose()
```
Expected: a byte count > 5000, then `1200x630`.

- [ ] **Step 4: Read the rendered image to confirm it looks right**

Use the Read tool on `og-image.png` (vision) — confirm wordmark reads "GG Tank Watch", "UNOFFICIAL" pill visible, no clipped text, correct celadon background. If wrong, fix `scripts/og-image.html` and re-run Step 2.

- [ ] **Step 5: Commit**

```bash
git add "scripts/og-image.html" "og-image.png"
git commit -m "feat(share): add 1200x630 social preview image + regenerable template"
```

---

### Task 2: Open Graph + Twitter meta tags

**Files:**
- Modify: `dashboard.html` (insert after line 7, the `<meta name="description">` tag)

- [ ] **Step 1: Add the meta block**

Insert immediately after the existing `<meta name="description" ...>` line in `<head>`:

```html
  <link rel="canonical" href="https://gg-tank-dashboard.vercel.app/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="GG Tank Watch">
  <meta property="og:title" content="GG Tank Watch — Garden Grove tank emergency">
  <meta property="og:description" content="Unofficial, volunteer-built situational awareness for the Garden Grove chemical-tank emergency. Routes to official sources — always verify with ggcity.org/emergency.">
  <meta property="og:url" content="https://gg-tank-dashboard.vercel.app/">
  <meta property="og:image" content="https://gg-tank-dashboard.vercel.app/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="GG Tank Watch — unofficial situational awareness for the Garden Grove tank emergency">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="GG Tank Watch — Garden Grove tank emergency">
  <meta name="twitter:description" content="Unofficial, volunteer-built situational awareness. Routes to official sources — verify with ggcity.org/emergency.">
  <meta name="twitter:image" content="https://gg-tank-dashboard.vercel.app/og-image.png">
```

- [ ] **Step 2: Verify the tags are present**

Run:
```bash
grep -c 'property="og:' "dashboard.html"; grep -c 'name="twitter:' "dashboard.html"
```
Expected: `9` then `3`.

- [ ] **Step 3: Commit**

```bash
git add "dashboard.html"
git commit -m "feat(share): add Open Graph + Twitter Card meta for rich link previews"
```

---

### Task 3: One-tap Share button (Web Share API + clipboard fallback)

**Files:**
- Modify: `dashboard.html` — add button markup inside `<div class="topbar-controls">` (locate that exact div, ~line 1513+); add a small inline `<script>` before `</body>`; add one CSS rule near the `.topbar-btn` block (~line 251).

- [ ] **Step 1: Add the Share button as the first child of `.topbar-controls`**

Find `<div class="topbar-controls">` and insert as its first child:

```html
        <button id="share-btn" class="topbar-btn" type="button" aria-label="Share this page" title="Share">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>
        </button>
```

- [ ] **Step 2: Add a "copied" affordance CSS rule**

Immediately after the `.topbar-btn:hover { ... }` rule (~line 251), add:

```css
    #share-btn.copied { border-color: var(--sa-celadon); color: var(--sa-celadon); }
```

- [ ] **Step 3: Add the share handler script before `</body>`**

```html
  <script>
    (function () {
      var btn = document.getElementById('share-btn');
      if (!btn) return;
      var data = {
        title: 'GG Tank Watch',
        text: 'Live situational awareness for the Garden Grove tank emergency — routes you to official sources.',
        url: location.href
      };
      btn.addEventListener('click', async function () {
        if (navigator.share) {
          try { await navigator.share(data); } catch (e) { /* user dismissed */ }
        } else if (navigator.clipboard && navigator.clipboard.writeText) {
          try {
            await navigator.clipboard.writeText(location.href);
            btn.classList.add('copied');
            setTimeout(function () { btn.classList.remove('copied'); }, 1500);
          } catch (e) { /* clipboard blocked */ }
        }
      });
    })();
  </script>
```

- [ ] **Step 4: Verify markup + handler are present**

Run:
```bash
grep -c 'id="share-btn"' "dashboard.html"; grep -c 'navigator.share' "dashboard.html"
```
Expected: `2` (button + CSS rule both reference it) then `1`.

- [ ] **Step 5: Visually verify the button renders (signed Edge headless)**

Render the live local file to a screenshot and Read it (vision):
```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu --enable-unsafe-swiftshader --hide-scrollbars --force-device-scale-factor=2 --window-size=414,896 --user-data-dir="$env:TEMP\share-edge-$(Get-Random)" --screenshot="$env:TEMP\share-check.png" --virtual-time-budget=6000 "file:///C:/Users/redacted/Desktop/Mike Ilog Portfolio/GitHub Projects/gg-tank-dashboard/dashboard.html" | Out-Null
```
Read `$env:TEMP\share-check.png` — confirm the Share (3-dot) icon sits in the top-right controls next to the theme toggle, aligned and not clipped. (Note: `file://` may block `status.json` fetch; the header/topbar still render, which is all this step checks.)

- [ ] **Step 6: Commit**

```bash
git add "dashboard.html"
git commit -m "feat(share): add one-tap Share button (Web Share API + clipboard fallback)"
```

---

### Task 4: Regression + ship

**Files:** none (verification + PR)

- [ ] **Step 1: Confirm the eval suite is unaffected**

Run: `python eval/run_all.py --skip integration`
Expected: scorecard shows `46/46` (or current baseline) — these changes touch only presentation, not the data pipeline, so the count must not drop. (Do NOT use `--quiet` — it hides `[FAIL]` lines; see memory.)

- [ ] **Step 2: Push the branch**

```bash
git push -u origin feat/resident-shareability
```

- [ ] **Step 3: Open the PR** (via `/ship` or `gh pr create`)

PR body must state: problem (noindex → sharing is the only channel), approach (OG card + Share button), test plan (eval 46/46, vision-checked render), risk (low; presentation-only; noindex untouched), rollback (revert commit). Screenshot the rendered share-check.png and og-image.png.

- [ ] **Step 4: Post-deploy card validation** (after merge auto-deploys)

Validate the live card with a sharing-debugger fetch of `https://gg-tank-dashboard.vercel.app/` (e.g. share into a Slack/iMessage thread, or a card validator). Confirm title, description, and image render. If the image 404s, confirm `og-image.png` deployed at the site root.

---

## Self-Review

**Spec coverage:** P1 (social card) → Tasks 1+2. P2 (Share button) → Task 3. `noindex` guardrail honored (no `vercel.json` change). Honest-naming guardrail honored (no "Safety"; copy keeps "unofficial/verify"). Regression + ship → Task 4. ✓

**Placeholder scan:** No TBD/TODO; every code block is complete and copy-pasteable. ✓

**Type/name consistency:** `#share-btn` id used identically in markup (Step 1), CSS rule (Step 2), and handler (Step 3). `og-image.png` path identical in Task 1 (create) and Task 2 (`og:image`/`twitter:image` URLs). Verify counts match the inserted content (og: ×9, twitter: ×3, share-btn ×2, navigator.share ×1). ✓

**Open risks (non-blocking):**
- Edge path assumed at `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` (known-good per global memory). If absent, fall back to Pillow (`python -c "import PIL"`; if missing, `pip install Pillow` is dev-only image tooling, not a shipped dep — flag for approval first).
- Share button label is an English `aria-label` on an icon control; full i18n of the label is out of scope (G1 governs *safety copy*, not a UI control) and can be a later follow-up.
