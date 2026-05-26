# SPEC — Garden Grove MMA Tank Live Dashboard

**Owner:** Nancy (***REDACTED***)
**Created:** 2026-05-24
**Status:** v0 pivot locked in (post-/autoplan Phase 1 CEO review)
**Context:** See `BRIEF_2026-05-24.md` and `~/.claude/projects/.../memory/project_gg_mma_tank_emergency.md` — there's an active multi-day MMA tank emergency in Garden Grove. Nancy is a downwind-adjacent resident sheltering in place and wants glanceable situational awareness without re-reading the news.

---

## v0 PIVOT (2026-05-24, post-CEO review)

**The pivot:** push-first, dashboard-secondary. CEO subagent's F1 + F2 + F11 findings showed the original dashboard-first framing solves the wrong problem — Nancy needs to be reached when she ISN'T looking, not given more to look at. Existing battle-tested apps cover ~80% of the real alert path; the custom code is layered safety net + glance dashboard.

### v0 architecture (4-hour budget)

```
Phone (Nancy's setup, ~30 min)              Laptop (CC build, ~2.5 hr)
─────────────────────────                  ────────────────────────
[Ready OC app]                             update_status.py ──┐
[Genasys EVAC app]   ← official channels                       ├─► status.json
[AirNow app]                                                   │
[ntfy.sh app]        ← custom push                             ├─► breaking_events.jsonl
   ▲                                                           │
   │ POST on breaking                                          ├─► updates.log
   │                                                           │
   └───────── update_status.py POSTs ntfy.sh/<topic> ──────────┘
                                                               │
                                                               ▼
                                                       dashboard.html (polls status.json)
                                                       opens in browser, auto-refresh 30s
```

**Three layers of safety:**
1. **Official:** Ready OC / Genasys EVAC / AirNow on phone — primary alert path, not custom code.
2. **ntfy push:** `update_status.py` detects structural changes in status.json vs prior snapshot; POSTs ntfy.sh/<topic> on breaking. Phone gets notification + history.
3. **Desktop dashboard:** glance view when at laptop. `file://` open from OneDrive project folder.

**Breaking detection (replaces keyword poller):** structural diff. Flip `breaking: true` when ANY of:
- `evacuation.residents` changed >10%
- `evacuation.lifted` toggled OR `evacuation.expanded_since_yesterday` toggled
- `incident.severity` bumped
- New authoritative statement from OCFA / Newsom / OC DA appears
- First reported injury / casualty
- `incident.resolved_iso` set (incident-end)

### v0 scope — IN

- `update_status.py` — Python 3, runs from /loop every 30 min, writes status.json + posts ntfy on breaking
- `dashboard.html` — vanilla JS, polls status.json every 30s, renders 4 panels (hero, tank, evac, sources)
- `apps-checklist.md` — phone setup instructions for Nancy (Ready OC + Genasys + AirNow + ntfy)
- `go_bag.md` — printable checklist, NOT embedded in dashboard
- `config.json` — ntfy topic name, Nancy's zone status, dashboard refresh interval
- `README.md` — what each file does, how to run
- Logs (`updates.log`, `breaking_events.jsonl`) — kept in OneDrive project folder

### v0 scope — OUT (deferred to v1 if incident drags >48h)

| Item | Why deferred | Substitute for v0 |
|---|---|---|
| SVG evacuation map | F6 — boundary changes faster than hand-edits | Link to ggcity.org/emergency |
| Go-bag accordion in dashboard | Low value in-page | Separate `go_bag.md` markdown |
| Horizontal timeline UI | `breaking_events.jsonl` IS the timeline | Read the JSONL if you want history |
| AirNow API integration | F8 — API key takes ~1 business day | AirNow phone app |
| Editable You panel | F9 — you know your own status | Hardcoded "outside / downwind" |
| Windows toast notifications | ntfy phone covers it | Browser tab title flashes on breaking |
| Breaking-news keyword poller | F3 — false positives + missed signals | Structural diff in update_status.py |
| Local-server fallback | Premature | `file://` open works for v0 |
| LOCALAPPDATA runtime split | F5 — kills phone-via-OneDrive-web access | Stay in OneDrive folder, retry on rename collision |
| Cloud routine writing status.json | Architecturally impossible (sandbox can't reach OneDrive) | Cloud routine remains pure-text-delta redundancy |

### v0 file manifest

```
OneDrive\Desktop\GG-tank-updates\
├── BRIEF_2026-05-24.md          (existing)
├── PERSONAL_UPDATE_2026-05-24.md (existing)
├── docs\SPEC.md                 (this file)
├── README.md                    (NEW)
├── apps-checklist.md            (NEW)
├── go_bag.md                    (NEW)
├── config.json                  (NEW — ntfy topic, zone status)
├── dashboard.html               (NEW — the glance view)
├── status.json                  (NEW — current snapshot, atomic-renamed)
├── breaking_events.jsonl        (NEW — append-only)
├── updates.log                  (NEW — append-only)
└── scripts\
    └── update_status.py         (NEW — the writer)
```

(`check_breaking.py`, `notify.py`, `setup_dashboard.py`, `zone.svg` from earlier draft: **dropped** in v0.)

### Post-Design+Eng review fixes (auto-decided)

**Critical fixes from review (folded into v0):**

1. **Hero swap (Design D1):** the 72pt headline is `zone_status_verdict` (green "YOU ARE OUTSIDE THE EVAC ZONE" / red "YOU ARE INSIDE THE EVAC ZONE — EVACUATE NOW"). Tank, evac, sources demoted to smaller panels below.

2. **WebSearch + regex (Eng E1) — not per-site scrapers:**
   - `update_status.py` runs ONE WebSearch with a curated query (e.g., `"Garden Grove MMA tank" evacuation residents temperature site:news`)
   - Applies regex patterns per field on returned snippets:
     - residents: `(\d{1,3}(?:,\d{3})*)\s*residents`
     - temp: `tank\s*temp(?:erature)?\s*(?:of\s*)?(\d+)\s*°?F`
     - severity: derived via `SEVERITY_RULES` (see below), NOT extracted
     - evacuation lifted: presence of "all clear" OR "evacuation lifted" in snippets
     - evacuation expanded: presence of "evacuation expanded" OR "added to evacuation zone"
   - On regex fail for a field: keep previous value, log `"extraction failed for X"` to `updates.log`. Don't overwrite with `None`.

3. **2-tick hysteresis on breaking (Eng E3):** structural diff must persist 2 consecutive snapshots before `breaking: true` flips. Implement via a `pending_breaking_since` field in `status.json` — first detection sets it; second consecutive detection 30 min later flips `breaking: true`; if cleared in between, `pending_breaking_since` resets.

4. **`os.replace()` retry on Windows (Eng E2):** 5 attempts with exponential backoff 100ms, 200ms, 400ms, 800ms, 1600ms + ±20% jitter. Catch `PermissionError` + `OSError`. Same retry applied to `breaking_events.jsonl` and `updates.log` appends.

5. **`SEVERITY_RULES` dict (Eng E4):** `update_status.py` includes:
   ```python
   SEVERITY_RULES = {
       "critical": lambda f: f.get("evacuation_lifted") is False and (f.get("tank_failed") or f.get("explosion_confirmed") or f.get("injuries", 0) > 0),
       "high": lambda f: f.get("evacuation_residents", 0) > 1000 and not f.get("evacuation_lifted"),
       "moderate": lambda f: f.get("evacuation_residents", 0) > 0 and not f.get("evacuation_lifted"),
       "low": lambda f: f.get("evacuation_lifted") or f.get("incident_resolved_iso"),
   }
   ```
   Walked top-to-bottom; first match wins.

6. **Random ntfy topic (Eng E5):** `setup` step generates a 32-char URL-safe random string and writes to `config.json` under `ntfy_topic`. Nancy subscribes to `ntfy.sh/<that-string>`.

### Design specifications (auto-spec'd from review)

- **Severity colors:** `low=#3b82f6` (blue), `moderate=#f59e0b` (amber), `high=#ef4444` (red), `critical=#991b1b` (dark red, white text).
- **Aesthetic (NWS gov-emergency-calm):** bg `#0a0e14`, surface `#151b23`, text `#e6edf3`, borders `#30363d` (1px hairline). System UI font stack for body; **IBM Plex Mono** for all numeric values. Three sizes: 72/24/14. Two weights: 400/600. No gradients, no shadows, max border-radius 4px. Dark mode only (no toggle in v0).
- **Staleness banner copy:** `"⚠️ Data is stale — last update was [N] min ago. The writer script may have stopped."`
- **BREAKING tab title:** `🔴 BREAKING — GG MMA Tank` ↔ `GG MMA Tank Dashboard`, toggling every 1s while `breaking: true`.
- **BREAKING banner animation:** pulse opacity 1.0 → 0.7 over 1.5s ease-in-out, infinite. Disabled when `prefers-reduced-motion: reduce`.
- **Timestamps:** relative ("2 min ago") up to 60 min; absolute ("3:37 PM") up to 24 h; weekday + time ("Mon 3:37 PM") beyond.
- **Sources panel:** collapsed by default behind `<details><summary>Verified from N sources</summary>`.
- **`aria-live="assertive"`** on the BREAKING banner.

### Eng error-path fixes (folded in)

- **Try/finally always logs:** every `update_status.py` invocation writes a single line to `updates.log` on entry AND on exit (success/failure), guaranteed by `try/finally`. No more silent crashes.
- **ntfy POST timeout:** 5s `requests.post(timeout=5)`. ntfy down → log, continue (do NOT block writer).
- **ntfy debounce:** suppress duplicate `breaking_reason` POSTs within 15 min.
- **Distinguish 0-results vs rate-limit:** WebSearch exception → don't bump `last_updated_iso`; empty results → don't bump either, log "all sources returned empty (suspicious)".
- **Schema version:** field stays at `1`; dashboard.html shows "schema changed, refresh page" banner if mismatch. No migration code.
- **Concurrent writers:** skip PID lockfile (P2 accept). `os.replace()` retry handles the rare race.

### Confirmed premises (post-CEO gate, Nancy 2026-05-24)

1. Primary risk = missing a material change while NOT actively monitoring.
2. Nancy will install Ready OC + Genasys EVAC + AirNow + ntfy on phone (~30 min).
3. Dashboard is SECONDARY to the official + push channels.
4. Logs kept in OneDrive project folder, NOT throwaway.
5. Build budget **6–8 hours for v0** (post-Eng-review recalibration).
6. Apps installed/tested FIRST; if they cover 80%, decide whether to continue with the custom code at all.

### Final taste decisions (post-Design+Eng gate, Nancy 2026-05-24)

- **Zone-flip outside→inside moment:** full-screen red modal + Web Audio API beep. Can't be ignored. One-click dismiss. (Design D2)
- **Distance to boundary:** DROP. Link to ggcity.org address checker instead. No coords required. (Design D1 follow-up)
- **Writer-down ntfy alert:** ADD to v0. `try/except` wrapping all of `update_status.py`; on any uncaught exception, last-ditch ntfy POST `"⚠️ WRITER DOWN — dashboard data is now stale"`. (Eng E6)
- **Real budget:** accept 6–8 hr build for complete v0. (Eng E8)

### v0.1 SCOPE CUT — desktop-only (Nancy 2026-05-24, post-build)

Nancy scratched the entire mobile / phone path after the v0 build was complete. New direction: **single live desktop dashboard app. No phone, no push, no apps.**

**Removed:**
- ntfy push pipeline (POST on breaking, writer-down alert, ASCII-safe header helper)
- `urllib.request` / `urllib.error` imports from `update_status.py`
- `apps-checklist.md` (Ready OC / Genasys EVAC / AirNow / ntfy install guide) — deleted
- `ntfy_topic` and `ntfy_server` from `config.json`
- All phone / mobile / OneDrive-web-on-phone references from README and SPEC

**Kept (unchanged):**
- `update_status.py` writer (still necessary — browser can't pull news directly)
- Structural-diff breaking detection (toggles fire immediately, residents-shift rate-limited)
- `dashboard.html` (BREAKING banner, zone-flip modal, NWS aesthetic — unchanged)
- Logs (`updates.log`, `breaking_events.jsonl`) — still useful for incident history
- /loop wiring (replaced `9b42d142` → `cb1466e5`; new prompt drops the ntfy fallback)
- `go_bag.md` (standalone printable checklist)

**Functional implication of removing ntfy:** the **dashboard staleness banner** is now the only writer-down signal. If the writer crashes silently, the banner fires after 30 min when `stale_after_iso` passes. README documents this explicitly.

**Bonus addition:** README now documents Chrome's "Install page as app" feature so the dashboard can be pinned in the taskbar like a real desktop app (standalone window, no URL bar).

### Autoplan completion summary

| Phase | Subagent | Codex | Outcome |
|---|---|---|---|
| 1 CEO | run | unavailable | 11 findings (3 critical/high triggered user challenge) — Nancy pivoted to push-first |
| 2 Design | run | unavailable | 6 findings, composite 3.9/10 → all auto-fixed in SPEC |
| 3 Eng | run | unavailable | 10 findings, composite 6.5/10 → 3 P1 auto-fixed, 1 taste deferred to Nancy (Writer-down: add) |
| 4 DX | skipped | n/a | No developer-facing scope (Nancy is sole user) |

**16 auto-decisions** logged in this section. **4 taste decisions** approved by Nancy. **1 user challenge** (CEO pivot) accepted.

**Status: APPROVED FOR BUILD.**

---

## Original SPEC (preserved below for backlog reference)

---

## 1. Problem

Nancy is monitoring an evolving, multi-day chemical incident. Current state lives in three places:
- The /loop job in an open Claude Code session (text deltas, in-terminal)
- A cloud routine (hourly text deltas, in routine logs)
- News sites she has to manually check

She needs **one glanceable view** that shows the current state of the incident and auto-updates without her doing anything. It must work even when she is not actively driving Claude.

## 2. Premises

- Audience is one person (Nancy). No auth needed; no multi-tenant.
- Viewing devices: Windows laptop (primary), phone (browser; secondary). Layout must be readable on both without app install.
- Lifetime: days, not months. This dashboard ships, runs through the incident, then gets archived. **Throwaway is acceptable.**
- The user already has Claude Code running locally with /loop active, and a cloud routine running hourly. Either can be the data writer.
- No backend infrastructure (no servers to provision, no DBs). Everything lives on disk in `C:\Users\redacted\OneDrive\Desktop\GG-tank-updates\`. OneDrive sync is incidental and not relied on.
- Source-of-truth for facts is the open web (news sites + ggcity.org + AQMD). Dashboard is a viewer over a structured snapshot, not an originator of facts.

## 3. Architecture

**Two-process model, file as message bus:**

```
[ writer ]                          [ reader ]
WebSearch / WebFetch  ──writes──>  status.json  ──reads──>  dashboard.html (auto-refresh)
                                                                    ▲
                                                                    │
                                                                  browser
```

- **Writer:** a script (`update_status.py` or `update_status.ps1`) that pulls latest news, normalizes facts, writes `status.json` atomically (write to `.tmp`, rename). Invoked by the existing /loop job (in-session) and the existing cloud routine (hourly).
- **Reader:** static `dashboard.html` with vanilla JS that `fetch('status.json')` every 30 s and re-renders. No framework, no build step. Opens with `file://` or via OneDrive web.
- **No server.** `fetch` on `file://` works in Chrome with `--allow-file-access-from-files` or in any modern browser when served via a quick `python -m http.server 8000` if needed. Default: open `dashboard.html` directly and document the fallback.

### Alternatives considered (rejected, with reason)

| Option | Why rejected |
|---|---|
| Local web server (Flask / Node) | Overkill for one user; need to keep process running; extra failure mode. |
| Terminal TUI (textual / rich) | Requires terminal open; not glanceable on phone; loses color/typography hierarchy on small screens. |
| Markdown + editor live-preview | Editor-specific; not phone-accessible; weak refresh semantics. |
| Cloud-hosted dashboard | Multi-day overhead for a multi-day problem; auth/secrets surface; not worth it for a one-person, ephemeral view. |
| Push notifications only | She asked for a dashboard, not just alerts; complementary, not substitute. |

## 4. Data model

`status.json` (single file, atomically replaced on each update):

```json
{
  "schema_version": 1,
  "last_updated_iso": "2026-05-24T22:37:00Z",
  "last_updated_human": "Sun May 24, 3:37 PM PDT",
  "incident": {
    "name": "Garden Grove MMA Tank Leak",
    "facility": "GKN Aerospace, Garden Grove, CA",
    "started_iso": "2026-05-21T22:40:00Z",
    "status_headline": "Cooling continues; crack may relieve pressure",
    "severity": "high"
  },
  "tank": {
    "temp_f": 100,
    "temp_trend": "stable",
    "crack_observed": true,
    "neutralization_possible": false
  },
  "evacuation": {
    "residents": 50000,
    "area_sq_mi": 9,
    "boundary": "Trask Ave (S) · Ball Rd (N) · Valley View St (W) · Dale St (E)",
    "lifted": false,
    "expanded_since_yesterday": false
  },
  "anna_zone_status": "outside_downwind",
  "official_statements": [
    {"agency": "OCFA", "time_iso": "...", "text": "...", "source_url": "..."}
  ],
  "schools_closed": ["GGUSD", "Magnolia", "Savanna", "Westminster", "Cypress"],
  "sources_checked": [
    {"url": "...", "title": "...", "fetched_iso": "..."}
  ],
  "next_check_at_iso": "2026-05-24T23:07:00Z",
  "stale_after_iso": "2026-05-24T23:37:00Z",
  "breaking": false,
  "breaking_reason": null,
  "breaking_since_iso": null
}
```

## 5. Reader (dashboard.html) contract

- Polls `status.json` every 30 s with cache-busting `?t=<ms>`.
- On load and each poll, re-renders:
  - **Hero:** incident name, status headline, severity color band.
  - **Tank panel:** temp (big number), trend arrow, crack-observed flag.
  - **Evac panel:** residents, sq mi, boundary, lifted/expanded flags.
  - **You panel:** Nancy's current zone status (read from JSON; one-tap edit on the page writes back via download-the-edited-JSON pattern — out of scope for v1, just display).
  - **Official statements:** newest 3, with timestamp + agency + source link.
  - **Footer:** "Last updated 2 min ago" (computed client-side from `last_updated_iso`); "Next check at 3:07 PM"; link to full brief.
- **Staleness banner:** if `now > stale_after_iso`, red banner: "Data is stale — last update >30 min ago. Check the writer."
- **BREAKING banner:** if `breaking: true` AND `breaking_since_iso` is within the last 15 min, top-of-page pulsing red banner with `breaking_reason` text. After 15 min the banner relaxes to a non-pulsing "Recent change" pill. After the next snapshot with `breaking: false`, banner clears.
- **Dark mode** default; light mode toggle saved to localStorage.

## 6. Writer contract — three update triggers

The dashboard updates on **three independent triggers**, OR-merged:

1. **Scheduled (heartbeat):** every 30 min via existing local /loop job `cf846055` at :07 / :37.
2. **Cron (cloud redundancy):** hourly at :13 UTC via cloud routine `trig_017YEJ4zkKeeXswyXPWz3yFw`. Off-session safety net.
3. **Event-driven (breaking-change detector):** a lightweight poller checks a small set of sentinel sources every ~5 min for "major change" keywords. On hit, fires the full updater out-of-band and tags the snapshot `breaking: true` so the dashboard surfaces a BREAKING banner.

### Writer: `update_status.py` (Python 3, stdlib + optional `requests`)
- Reads previous `status.json` (if any) for diffing.
- Calls a small set of fact-extraction functions (one per source: OCFA / ggcity / a major news live-blog). Each returns a dict or None.
- Merges into the schema. Sets `last_updated_iso = now`, `next_check_at_iso = now + 30min`, `stale_after_iso = now + 30min`.
- **Computes diff vs previous snapshot.** If any of the following changed → set `breaking: true` and stamp `breaking_reason`:
  - `incident.severity` bumped
  - `evacuation.residents` changed by >10% OR `evacuation.lifted` toggled OR `evacuation.expanded_since_yesterday` toggled
  - Tank explosion/failure confirmed (new keyword in headlines)
  - First reported injury/casualty
  - `anna_zone_status` would change based on new boundary (heuristic flag)
- Writes to `status.json.tmp` then atomic rename.
- Logs append-only to `updates.log` (one line per run, with diff summary).
- Exits non-zero on total failure so the trigger sees it.

### Breaking-news poller: `check_breaking.py` (light, every ~5 min)
- Polls a 3–5 URL sentinel set (e.g., the city emergency page, the lead news live-blog, one wire service).
- Cheap fetch + regex match for sentinel keywords: `explod|explosion|breach|all clear|evacuation lifted|evacuation expanded|fatal|injured|injury|killed`.
- On a hit:
  - Invoke `update_status.py` immediately (out-of-band, not waiting for the next 30-min tick).
  - Append the matched headline + URL + timestamp to `breaking_events.jsonl` for audit.
- On no hit: no-op. Cheap.
- **Debouncing:** if a hit fires the writer, suppress further triggers for 5 min so a single news cycle doesn't fire 10 updates.

### Trigger orchestration

| Trigger | Mechanism | Cadence | Notes |
|---|---|---|---|
| Scheduled heartbeat | /loop job `cf846055` runs `update_status.py` | every 30 min | Existing |
| Cloud cron | cloud routine `trig_017YEJ4zkKeeXswyXPWz3yFw` | hourly | Existing; produces own delta + status snapshot |
| Breaking-news poller | new local /loop job runs `check_breaking.py` | every 5 min | NEW — needs second loop job |
| Manual | Nancy runs `python update_status.py` | on demand | "F5" equivalent |

All three writer invocations target the same `status.json`. Atomic rename + filesystem locking handle concurrent writes (vanishingly unlikely at these cadences).

## 7. Error model

| Failure | Behavior |
|---|---|
| WebSearch returns 0 results | Writer keeps previous values; bumps `last_updated_iso` only if at least one source succeeded; logs which source failed. |
| WebSearch returns garbage | Writer holds the previous value for that field; doesn't overwrite with junk. (Validation per field: temp is int 0–500; sq_mi is positive float; residents is int.) |
| status.json missing on first reader load | Reader shows "Initializing — first update in <countdown>" placeholder. |
| Disk write fails | Writer logs + exits non-zero; previous status.json untouched; reader's staleness banner fires. |
| Browser offline | Reader keeps showing last successfully fetched JSON; "offline" indicator in footer. |

## 8. Tests

- **Unit:** each fact extractor takes a fixed sample HTML/text input and returns the expected dict.
- **Integration:** end-to-end run produces a valid JSON conforming to the schema; second run with no changes produces semantically equivalent JSON (no spurious diffs).
- **Reader smoke:** open `dashboard.html` with a known `status.json` and visually confirm every field renders; toggle stale_after_iso to past and confirm banner.
- **Validation:** rejecting malformed JSON (writer's `.tmp` step protects against this; test the protection by injecting failure mid-write).

## 9. Scope / non-goals

**In scope (v1):**
- One HTML file, one writer script, one JSON snapshot file.
- Hooked into existing /loop + cloud routine.
- Dark mode, mobile-readable, auto-refresh.
- Manual one-time setup; no auto-launch on boot.

**Out of scope (v1):**
- Map rendering of evacuation zone.
- Push notifications (Nancy already has /loop text deltas).
- Editing the JSON from the dashboard.
- Historical timeline / charts.
- Multi-incident support.
- Authentication, multi-user, hosting.

## 10. Success criteria

- Nancy opens `dashboard.html` in her browser, sees current incident state at a glance, and can leave the tab open. The page auto-refreshes; she never has to F5.
- Within 30 min of any of the source sites publishing a material change, that change appears on the dashboard (assuming /loop fired).
- If the writer is broken for >30 min, the staleness banner fires and she can tell at a glance the data is stale.
- Nancy's verdict on first open: "yes, this is what I wanted."

## 11. Review decisions (2026-05-24, post-/autoplan)

### Auto-decided (mechanical)

| # | Question | Decision | Principle |
|---|---|---|---|
| 1 | Writer language | **Python 3** (stdlib + `requests`) — portable across local Windows and cloud Linux | P5 explicit |
| 2 | Dashboard auto-refresh | **30 seconds** | P6 action |
| 3 | Cloud routine writes `status.json`? | **No.** Cloud stays as redundancy — produces markdown deltas in routine log only. Local writer owns `status.json`. | P3 pragmatic |
| 4 | Dashboard delivery | **`file://` direct** with documented `python -m http.server` fallback if browser blocks `fetch` | P5 explicit |
| 5 | Breaking-news poller cadence | **5 min** with 5-min debounce after a hit | P3 pragmatic |
| 6 | Sentinel keyword set | **Expanded:** `explod|explosion|breach|all clear|evacuation lifted|evacuation expanded|fatal|injured|injury|killed|tank failure|neutralization complete|shelter in place expanded` | P1 completeness |
| 7 | Where to run the breaking poller | **Second /loop job** (`update_status` stays on the 30-min job; `check_breaking` on a new 5-min job) | P3 pragmatic |
| 8 | Live AQI for Nancy's zip | **Add.** Pull from EPA AirNow API. Surfaces in the "You" panel. | P1 completeness |

### Critical risk → fix folded in

**Risk:** OneDrive's sync client can grab `status.json` mid-rename, causing locks or half-written copies.
**Fix:** Both writer output and the HTML/JSON live at `%LOCALAPPDATA%\gg-dashboard\` (NOT inside OneDrive). Source files (this SPEC, brief, README) stay in OneDrive; runtime artifacts move out. A desktop shortcut on Nancy's desktop points at `%LOCALAPPDATA%\gg-dashboard\dashboard.html`.

### Taste decisions (Nancy's calls)

| Decision | Nancy's call | Implementation |
|---|---|---|
| Push notifications on breaking | **Add Windows toast** | `notify.py` using `win10toast` or stdlib `windows.ui.notifications`; called by `update_status.py` when `breaking: true` flips on |
| Go-bag checklist | **Collapsed accordion** | Static HTML/JS accordion in dashboard footer; content from `go_bag.md` (one-time write) |
| Evacuation-zone map | **Static SVG** with the 4-street boundary + pin for Nancy's address | One-time SVG generated from boundary coords; pin position read from `config.json` (Nancy fills in her address coordinates once) |
| Historical timeline | **Add minimal horizontal strip** | Reads `breaking_events.jsonl`; renders as a horizontal scrollable strip above the official-statements panel |

### Updated file manifest

```
%LOCALAPPDATA%\gg-dashboard\
├── dashboard.html        # the page
├── status.json           # current snapshot (atomic-renamed)
├── status.json.tmp       # transient
├── breaking_events.jsonl # append-only breaking-change log
├── updates.log           # append-only writer activity log
├── config.json           # Nancy's address coordinates, zip for AQI, etc.
├── go_bag.md             # static go-bag content
└── zone.svg              # static evacuation-zone map

OneDrive\Desktop\GG-tank-updates\
├── docs\SPEC.md          # this file
├── docs\EXECUTION_PLAN.md  # next
├── BRIEF_2026-05-24.md
├── PERSONAL_UPDATE_2026-05-24.md
├── scripts\update_status.py
├── scripts\check_breaking.py
├── scripts\notify.py
├── scripts\setup_dashboard.py   # one-time: copy HTML/SVG/go_bag to LOCALAPPDATA, prompt for config
└── README.md
```

## 12. Original open questions (resolved above)

- Should the writer be Python or PowerShell? (Python is more portable across the cloud routine and the local loop; PowerShell is Windows-native and avoids an extra dependency. Default pick: **Python**, because the cloud routine runs in a Linux sandbox.)
- Auto-refresh interval (30 s vs 60 s vs 5 min)? Tradeoff: tab CPU vs perceived liveness.
- Should the cloud routine write to the same `status.json`? It runs in a Linux sandbox without access to Nancy's OneDrive folder. **Likely answer:** cloud routine produces its own JSON-shaped output in the routine log; only the *local* writer touches `status.json`. Cloud is the redundancy / off-session safety net.
- Should the dashboard also show a "what to do if you have to evacuate" go-bag checklist? Adds value for her actual situation but feels like scope creep — flag for /autoplan.
- Where does `dashboard.html` open from — `file://` direct, OneDrive web, or quick local server? Default: `file://` works; document the `python -m http.server` fallback if `fetch` is blocked.
