# Security, Accessibility & Ops Blockers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all 6 engineer-owned blockers from the finalization audit gap registers, clearing the path for distribution gate sign-off.

**Architecture:** Three files change: `vercel.json` gets security headers (CSP, X-Frame-Options, Cache-Control), `dashboard.html` gets aria-live attributes on dynamic containers and a User-Agent header on the Nominatim fetch, and `scripts/refresh_local.py` gets a healthchecks.io dead-man's switch ping.

**Tech Stack:** Vercel static hosting headers, HTML ARIA attributes, Python urllib for HTTP pings.

---

## File Map

| File | Changes |
|------|---------|
| `vercel.json` | Add CSP, X-Frame-Options, Cache-Control headers |
| `dashboard.html` | Add `aria-live` to banners container, check-verdict-area, and hero-verdict; add User-Agent to Nominatim fetch; add `<label>` to check-tab-input |
| `scripts/refresh_local.py` | Add healthchecks.io ping on successful refresh |

---

### Task 1: Security headers in vercel.json

**Files:**
- Modify: `vercel.json`

- [ ] **Step 1: Add CSP, X-Frame-Options, and robots.txt-equivalent headers to the global route**

The current `vercel.json` has only `X-Robots-Tag`. Add three headers to the existing `/(.*)`  source block:

```json
{
  "rewrites": [
    { "source": "/", "destination": "/dashboard.html" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Robots-Tag", "value": "noindex, nofollow" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "Content-Security-Policy", "value": "default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: https://tile.openstreetmap.org https://*.tile.openstreetmap.org https://img.youtube.com https://api.microlink.io blob:; connect-src 'self' https://nominatim.openstreetmap.org https://api.weather.gov https://api.microlink.io; frame-src https://www.youtube.com https://www.youtube-nocookie.com" }
      ]
    },
    {
      "source": "/status.json",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=0, must-revalidate" }
      ]
    }
  ]
}
```

Key decisions:
- `script-src 'unsafe-inline'` is required because dashboard.html uses inline `onclick` handlers. A future cleanup could extract these, but that's out of scope.
- `style-src 'unsafe-inline'` is required because dashboard.html uses inline `style=` attributes extensively.
- `img-src blob:` is needed for Leaflet's marker icon rendering.
- `img-src data:` is needed for the SVG favicon in manifest.json.
- `connect-src` covers Nominatim (geocoding), NOAA (wind), Microlink (link previews), and self (status.json polling).
- `frame-src` covers YouTube video embeds (both regular and nocookie domains).
- `status.json` gets its own route with `Cache-Control: public, max-age=0, must-revalidate` to prevent Vercel's edge CDN from caching stale data.

- [ ] **Step 2: Verify the file is valid JSON**

Run: `python -m json.tool vercel.json`
Expected: pretty-printed JSON output with no errors.

- [ ] **Step 3: Commit**

```bash
git add vercel.json
git commit -m "fix(security): add CSP, X-Frame-Options, Cache-Control headers"
```

---

### Task 2: Nominatim User-Agent header

**Files:**
- Modify: `dashboard.html:2572`

- [ ] **Step 1: Add User-Agent to the Nominatim fetch call**

The current Nominatim fetch at line 2572 sends only `Accept-Language`:

```javascript
var r = await fetch(u, { headers: { "Accept-Language": "en" } });
```

Add the same User-Agent string used by the NOAA wind fetch at line 3108:

```javascript
var r = await fetch(u, { headers: { "Accept-Language": "en", "User-Agent": "GG-Dashboard/1.0 (emergency-awareness)" } });
```

Note: browsers may silently drop the `User-Agent` header on cross-origin requests (Nominatim is cross-origin). However, the Nominatim usage policy also accepts `Referer` as identification, and browsers automatically send `Referer` on fetch requests. The `User-Agent` header is still best practice — Nominatim's server-side will see it if the browser allows it, and the `Referer` header provides a fallback.

- [ ] **Step 2: Commit**

```bash
git add dashboard.html
git commit -m "fix(security): add User-Agent header to Nominatim geocoder fetch"
```

---

### Task 3: aria-live attributes on dynamic elements

**Files:**
- Modify: `dashboard.html:1814` (banners div)
- Modify: `dashboard.html:1901` (check-verdict-area div)

- [ ] **Step 1: Add aria-live="assertive" to the banners container**

The banners div at line 1814 holds breaking alerts, stale warnings, and offline notices. These are critical status updates that screen readers must announce immediately.

Change:
```html
<div class="banners" id="banners"></div>
```
To:
```html
<div class="banners" id="banners" aria-live="assertive" aria-atomic="false"></div>
```

`aria-atomic="false"` means the screen reader announces only the new/changed content, not the entire container (important when multiple banners are present).

- [ ] **Step 2: Add aria-live="polite" to the check-verdict-area**

The verdict area at line 1901 shows address-check results. These are important but not interruption-worthy.

Change:
```html
<div class="check-right" id="check-verdict-area">
```
To:
```html
<div class="check-right" id="check-verdict-area" aria-live="polite" aria-atomic="true">
```

`aria-atomic="true"` ensures the full verdict (not just a changed word) is announced.

- [ ] **Step 3: Add a visible `<label>` to the check-tab-input**

The address input at line 1890 uses only a placeholder. Add a `<label>` for screen reader reliability.

Change the form block at lines 1888-1892:
```html
<form id="check-tab-form" onsubmit="event.preventDefault(); checkTabAddress();">
  <div class="check-input-group">
    <input type="text" class="check-input" id="check-tab-input" data-i18n-placeholder="check.placeholder" placeholder="e.g. Magnolia &amp; Talbert" autocomplete="off">
    <button type="submit" class="check-submit-btn" id="check-tab-btn" data-i18n="check.btn">Check</button>
  </div>
</form>
```
To:
```html
<form id="check-tab-form" onsubmit="event.preventDefault(); checkTabAddress();">
  <div class="check-input-group">
    <label for="check-tab-input" class="sr-only" data-i18n="check.prompt">Check an address or intersection</label>
    <input type="text" class="check-input" id="check-tab-input" data-i18n-placeholder="check.placeholder" placeholder="e.g. Magnolia &amp; Talbert" autocomplete="off">
    <button type="submit" class="check-submit-btn" id="check-tab-btn" data-i18n="check.btn">Check</button>
  </div>
</form>
```

Also add the `.sr-only` CSS class if not already present. Search for `sr-only` or `visually-hidden` first — if missing, add to the CSS section:

```css
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
```

- [ ] **Step 4: Verify no existing aria-live attributes are duplicated**

Run: `grep -n "aria-live" dashboard.html`
Expected: Only the two lines you just added (banners and check-verdict-area). If others exist, verify no conflicts.

- [ ] **Step 5: Commit**

```bash
git add dashboard.html
git commit -m "fix(a11y): add aria-live to banners and verdict, label to address input"
```

---

### Task 4: Dead-man's switch in refresh_local.py

**Files:**
- Modify: `scripts/refresh_local.py`

- [ ] **Step 1: Add healthchecks.io ping function**

Add a `ping_healthcheck()` function after the imports (after line 36). This pings on success so that if the script stops running, healthchecks.io will alert after its grace period.

After the `REPO = HERE.parent` line (line 42), add:

```python
HEALTHCHECK_URL = os.environ.get("HEALTHCHECK_URL", "")


def ping_healthcheck(status: str = "") -> None:
    """Ping healthchecks.io on successful refresh. Silent on failure."""
    if not HEALTHCHECK_URL:
        return
    import urllib.request
    url = HEALTHCHECK_URL if not status else f"{HEALTHCHECK_URL}/{status}"
    try:
        urllib.request.urlopen(url, timeout=10)
    except Exception:
        pass
```

- [ ] **Step 2: Call the ping at the end of a successful `main()`**

Modify the `main()` function to ping after a successful run. Change lines 110-121:

```python
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="gather + write status.json, skip git")
    args = ap.parse_args()

    facts = gather_via_subscription()
    write_status(facts)
    if args.dry_run:
        print("dry-run: status.json written, git skipped")
        ping_healthcheck()
        return 0
    commit_and_push()
    ping_healthcheck()
    return 0
```

- [ ] **Step 3: Verify the script still runs without HEALTHCHECK_URL set**

Run: `python scripts/refresh_local.py --dry-run`
Expected: Normal operation. The `ping_healthcheck()` call returns immediately when `HEALTHCHECK_URL` is empty.

- [ ] **Step 4: Commit**

```bash
git add scripts/refresh_local.py
git commit -m "feat(ops): add healthchecks.io dead-man's switch to refresh pipeline"
```

---

### Task 5: Add robots.txt

**Files:**
- Create: `robots.txt`

- [ ] **Step 1: Create robots.txt**

Create `robots.txt` in the project root:

```
User-agent: *
Disallow: /
```

This is defense-in-depth alongside the `X-Robots-Tag` header. Some crawlers check `robots.txt` before processing response headers.

- [ ] **Step 2: Commit**

```bash
git add robots.txt
git commit -m "fix(security): add robots.txt as defense-in-depth for noindex"
```

---

### Task 6: Run eval suite to verify no regressions

- [ ] **Step 1: Run the eval harness**

Run: `python eval/run_all.py --skip integration`
Expected: 46/46 pass (100%). The changes are header/attribute additions that don't affect behavioral tests.

- [ ] **Step 2: Verify vercel.json is valid**

Run: `python -m json.tool vercel.json > NUL`
Expected: Exit code 0.

---

## Summary of blockers cleared

| Blocker | Fix | Status after |
|---------|-----|-------------|
| B1: No CSP | Task 1 | Cleared |
| B5: No X-Frame-Options | Task 1 | Cleared |
| B6: No Cache-Control for status.json | Task 1 | Cleared |
| B7: No Nominatim User-Agent | Task 2 | Cleared |
| B3: No aria-live | Task 3 | Cleared |
| B2: No dead-man's switch | Task 4 | Cleared (requires HEALTHCHECK_URL env var) |
| I1: No robots.txt | Task 5 | Cleared |
