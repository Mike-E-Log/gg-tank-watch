# Gap Sweep — Non-UI/UX gap audit (deep session)

You are running the **Gap Sweep** workstream. 1 other workstream runs concurrently ("Legal Readiness" on `.orchestra/legal-gap-register.md`). You do NOT touch their files. You own the gap sweep register only.

## Read first, in this order

1. `CLAUDE.md` (project instructions)
2. `.orchestra/CONTRACTS.md` — settled cross-cutting contracts. **Authoritative and READ-ONLY.** Build against it; never contradict it.
3. `docs/SPEC.md` — product specification
4. `docs/AI_CONTROL_ARCHITECTURE.md` — AI safety architecture and control flow
5. `docs/DATA_QUALITY.md` — data quality framework and failure modes
6. `docs/DATA_SYNC.md` — data synchronization architecture
7. `docs/SOURCE_CREDIBILITY.md` — source credibility framework
8. `docs/WCAG_NOTES.md` — accessibility status and known gaps
9. `eval/README.md` — eval harness documentation
10. `dashboard.html` — the actual dashboard (READ-ONLY)
11. `scripts/` — data pipeline scripts (READ-ONLY)
12. `config.json` — project configuration (READ-ONLY)
13. `vercel.json` — deployment configuration (READ-ONLY)
14. `manifest.json`, `sw.js` — PWA configuration (READ-ONLY)

## Primary goal

Surface every non-UI/UX, non-legal gap that could block sign-off for public distribution. Produce a comprehensive gap register with severity, owner, and concrete next action for each item. The output tells the project owners exactly what technical/operational work remains.

## File ownership

**You OWN (exclusive write access):**
```
.orchestra/gap-sweep-register.md
```

**DO NOT TOUCH:**
```
.orchestra/legal-gap-register.md   -> legal-readiness
.orchestra/CONTRACTS.md            -> Orchestrator ONLY
.orchestra/orchestration.json      -> Orchestrator ONLY
dashboard.html                     -> READ-ONLY
docs/LEGAL.md                      -> READ-ONLY (legal stream's input)
docs/DISTRIBUTION.md               -> READ-ONLY
Any other project file             -> READ-ONLY
```

## The work

### Phase 1 -- Read and inventory

Read all docs and source files listed above. Build a mental map of what exists, what's tested, and what's documented.

### Phase 2 -- Audit each category

For each category below, ask diagnostic questions against the codebase (read files, check for patterns, verify claims). Don't assume -- confirm. Produce a gap register entry with:
- **Status:** done / partial / missing / blocked / N/A
- **What exists:** specific evidence (file, line, test, config)
- **What's missing:** concrete gaps
- **Severity:** blocker / important / nice-to-have
- **Owner:** user / engineer / vendor / TBD
- **Next action:** the specific, concrete step to close this gap

Categories to audit:

1. **Product scope and requirements** -- Is scope locked? Are out-of-scope decisions documented? Check docs/SPEC.md.
2. **Technical architecture** -- Single-file HTML + Python pipeline + static hosting. Is this documented? Are there scaling concerns? Environments (dev/staging/prod)?
3. **Security** -- Threat model (eval harness covers AI safety, but what about web security?). Secrets management. XSS? CSP headers? Subresource integrity? Are API keys exposed in client-side code?
4. **Data model and retention** -- status.json schema. timeline.json schema. Backup strategy. What happens if data is corrupted? Disaster recovery.
5. **Observability** -- Logging, metrics, alerting. How do operators know if the data refresh fails silently? Is the remote scheduler monitored? What's the incident response plan?
6. **QA strategy and test coverage** -- Eval harness (46/46). What's covered? What's NOT covered? Are there integration tests? End-to-end tests? Manual test procedures?
7. **Accessibility (WCAG)** -- Cross-reference docs/WCAG_NOTES.md known gaps. Check dashboard.html for ARIA, contrast, keyboard nav, screen reader support. Focus styles? Skip nav? Form labels?
8. **Performance** -- Page load budget. Bundle size. 3G performance claim (~500ms). Is it measured? Font loading strategy. Image optimization.
9. **Analytics and event tracking** -- Any analytics? Should there be? Privacy-respecting options. How do operators know if the tool is being used?
10. **Content** -- Translations (107 Vietnamese strings unverified). Error states. Empty states. Microcopy. i18n completeness.
11. **Documentation** -- Internal runbooks. External docs. Status page. Architecture docs. Is everything current?
12. **Infrastructure and deployment** -- Vercel config. DNS/domains. SSL. CDN. Cache headers. Build process. CI/CD.
13. **Vendor and SaaS stack** -- Single points of failure. What happens if Nominatim goes down? OSM tiles? Vercel? Microlink?
14. **Backup and disaster recovery** -- Can the dashboard be rebuilt from scratch? Are data files versioned? What's the recovery time?

### Phase 3 -- Produce the gap register

Write `.orchestra/gap-sweep-register.md` with:
- Executive summary (2-3 sentences: what's the technical readiness posture?)
- Per-category entries in the format above
- A "Blockers" section (items that must be resolved before any distribution)
- An "Important" section (items that should be resolved before Phase 1+ distribution)
- A "Nice-to-have" section (improvements that strengthen the project)
- Cross-reference against DISTRIBUTION.md gates G3 (data freshness), G4 (accessibility), G5 (provenance cues)

## Hard constraints (NON-NEGOTIABLE)

- DO NOT TOUCH files owned by other workstreams
- DO NOT write to shared docs directly
- Treat `.orchestra/CONTRACTS.md` as authoritative; READ it, never write it
- DO NOT modify any project code or HTML -- this is an audit, not an implementation session
- Self-execute verifications (read files, run tests if needed, check code yourself)
- Legal analysis belongs to the legal-readiness stream. If you find something with legal implications (e.g., privacy gap, accessibility liability), note it as a cross-stream finding for the orchestrator to route.
- This project serves ~50,000 evacuated residents during a real chemical emergency. Be thorough.

## What "done" looks like

- `.orchestra/gap-sweep-register.md` exists with all 14 categories audited
- Each category has status, evidence, gaps, severity, owner, and next action
- Blockers / Important / Nice-to-have sections are populated
- Cross-references to G3/G4/G5 gates are explicit
- Task marked `completed` via TaskUpdate
- Summary sent to orchestrator lead via SendMessage

## Out of scope

- Legal analysis (entity, liability, disclaimers, terms) -> legal-readiness
- UI/UX design changes -> not in scope for either stream
- Actually implementing fixes -> future session

## On completion

1. Mark your task `completed` via `TaskUpdate`
2. `SendMessage` the orchestrator lead a summary: total gaps found, breakdown by severity (blocker/important/nice-to-have), top 3 blockers, and any cross-stream findings for the legal team
