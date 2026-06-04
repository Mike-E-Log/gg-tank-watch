# GG Tank Watch — redesign punch list (PR-B)

Compiled 2026-05-25 from a live design-review pass. Implementation plan:
`docs/superpowers/plans/2026-05-25-gg-tank-watch-redesign.md`.

Liability lens (binding, from `docs/LEGAL.md` R1/R2 + `docs/DISTRIBUTION.md` §3): the UI
states facts and defers to officials. It never issues directives ("STAY PUT", "LEAVE NOW")
or implies safety. Per-address verdicts stay in the Check tab where they are hedged.

## Observations → changes

| # | Area | Observation | Intended change | Status |
|---|---|---|---|---|
| O1 | Branding | Named "GG MMA Tank Dashboard" | Rebrand to **GG Tank Watch** (topbar, `<title>`, JS title consts, terms page) | Decided |
| O2 | Topbar | Language toggle reads "VI"/"EN" | Relabel **Viet** / **Eng** | Decided |
| O3 | Topbar | Theme toggle reads "Light"/"Dark" | Replace with **sun ☀ / moon 🌙** icons | Decided |
| O4 | Hero | "STAY PUT." is a directive (liability) | Remove the directive action verb | Decided |
| O5 | Hero | "What should I do?" framing | Remove the label / question framing | Decided |
| O6 | Hero | Red "HIGH" chip has no context | Label it: **"Incident severity: HIGH"** | Decided |
| O7 | Hero | Eats too much vertical space on Map | **Neutral status line** (severity + clamped summary); official pointer stays in the safety strip below | Decided |
| O8 | Banners | "UPDATE — N new statements" never dismisses | Click-to-dismiss: clicking marks the latest statement seen (localStorage); returns when a newer statement arrives | Decided |
| O9 | News | "statements" vs "Coverage" split is confusing | **One unified reverse-chron timeline**, items tagged 🏛 Official / 📰 Article / ▶ Video | Decided |
| O10 | Info | 7 stacked sections feel chaotic | Reorg by resident need: Incident status (tank+evac) → Where to go (shelters) → Closures (schools) → collapsible Sources & methodology → collapsible About | Proposed (in plan; user may tweak) |
| O11 | Check | Nominatim compliance (LEGAL §6) | Add geocode result caching (localStorage, 7-day TTL). Submit-on-enter already compliant; User-Agent is browser-controlled | Decided |

## Carried-over gates (NOT in PR-B — flagged so they are not lost)

- **Takeover modal "LEAVE NOW"** (`dashboard.html` `showTakeover`/`#takeover`): a full-screen directive that fires on zone-flip-to-inside. Same liability class as the hero "STAY PUT". PR-B leaves it untouched; **decide separately** whether to keep it, neutralize the wording ("The city's evacuation zone now includes your saved location — see ggcity.org/emergency"), or remove it.
- **VI sign-off (Nancy, G1 gate):** every new/changed user-facing string from PR-B (hero, News labels, severity label, group headings) is English-only with EN fallback until Nancy verifies. No machine-translated Vietnamese ships.
- **Attorney review (🔴 LEGAL):** final hero/severity wording, the address-tool output, and the terms ToU are attorney-review-gated before distribution. PR-B is the conservative pass.
- **Error-report contact:** terms §7 is worded to not promise a channel that is not live yet; a real, monitored channel is still needed.
