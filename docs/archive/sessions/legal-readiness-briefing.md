# Legal Readiness — Produce attorney-ready package (deep session)

You are running the **Legal Readiness** workstream. 1 other workstream runs concurrently ("Gap Sweep" on `.orchestra/gap-sweep-register.md`). You do NOT touch their files. You own the legal gap register only.

## Read first, in this order

1. `CLAUDE.md` (project instructions)
2. `.orchestra/CONTRACTS.md` — settled cross-cutting contracts. **Authoritative and READ-ONLY.** Build against it; never contradict it.
3. `docs/LEGAL.md` — existing 700+ line legal research with 49 sources, risk matrix, draft disclaimer, minimum bar, open questions. THIS IS YOUR PRIMARY INPUT.
4. `docs/DISTRIBUTION.md` — phased GTM with 5 readiness gates (G1-G5)
5. `terms.html` — live Terms & Disclaimer page
6. `LICENSE` — MIT with informational disclaimer
7. `docs/CODE_OF_CONDUCT.md` — existing code of conduct
8. `docs/CONTRIBUTING.md` — existing contributing guide
9. `docs/AI_CONTROL_ARCHITECTURE.md` — AI safety architecture (READ-ONLY, for understanding controls)
10. `dashboard.html` — the actual dashboard (READ-ONLY, for auditing disclaimers and UI language)

## Primary goal

Produce a comprehensive, prioritized gap register that tells the project owners exactly what's done, what's drafted, what's missing, and what specific question to take to a California attorney for each open item. The output is an attorney-ready package: someone can hand `.orchestra/legal-gap-register.md` to counsel and get actionable answers.

## File ownership

**You OWN (exclusive write access):**
```
.orchestra/legal-gap-register.md
```

**DO NOT TOUCH:**
```
.orchestra/gap-sweep-register.md   -> gap-sweep
.orchestra/CONTRACTS.md            -> Orchestrator ONLY
.orchestra/orchestration.json      -> Orchestrator ONLY
dashboard.html                     -> READ-ONLY
docs/LEGAL.md                      -> READ-ONLY (your input, not your output)
docs/DISTRIBUTION.md               -> READ-ONLY
terms.html                         -> READ-ONLY
Any other project file             -> READ-ONLY
```

## The work

### Phase 1 -- Read and inventory existing coverage

Read all legal docs listed above. For each category below, determine what already exists, what's drafted, and what's missing. LEGAL.md is thorough -- most categories have existing analysis. Your job is to cross-reference, find gaps, and assess completeness.

### Phase 2 -- Audit each legal category

For each category, produce a gap register entry with:
- **Status:** done / drafted / missing / blocked / N/A
- **What exists:** specific file, section, and key finding
- **What's missing:** concrete gaps in existing coverage
- **Question for counsel:** the specific question to take to an attorney (if applicable)
- **Severity:** blocker / important / nice-to-have
- **Owner:** user / attorney / engineer / TBD

Categories to audit:

1. **Entity structure** -- Formation state, type, options (sole prop / LLC / nonprofit / unincorporated association). Who are the operators? Cap table? Operating agreements?
2. **Founder/contributor agreements** -- IP assignment between Mike and Nancy. Work-for-hire status. Who owns what?
3. **Trademark/copyright/patent** -- "ggtankwatch" clearance. Name conflicts. Government seal/insignia avoidance.
4. **Terms of Service / Disclaimer** -- Cross-reference terms.html against LEGAL.md's draft and minimum bar. Is it complete? Is it positioned correctly (near map and address tool)?
5. **Privacy** -- Current posture (no PII). Nominatim data flow disclosure. Forward-looking (COPPA, CCPA). Cross-reference terms.html privacy section.
6. **Regulatory exposure** -- Safety-domain-specific: negligent undertaking, negligent misrepresentation, § 324A. What is the "check your address" tool's specific liability exposure?
7. **Content aggregation** -- Copyright, fair use, fair-report privilege, § 230. Current practices vs. LEGAL.md recommendations.
8. **Third-party service terms** -- Nominatim, OSM tiles, Leaflet, YouTube, Microlink. Compliance status for each.
9. **Liability and insurance** -- Current exposure without entity. Insurance options (E&O, cyber, general). What changes with entity formation?
10. **Volunteer/Good Samaritan protections** -- Confirmed inapplicable. What alternatives exist?
11. **Accessibility compliance** -- ADA/Unruh exposure (legal dimension, not the technical implementation).
12. **Disclosures and marketing claims** -- Non-affiliation notice. AI disclosure. "Informational only" positioning.

### Phase 3 -- Produce the gap register

Write `.orchestra/legal-gap-register.md` with:
- Executive summary (2-3 sentences: what's the legal posture?)
- Per-category entries in the format above
- A prioritized "Questions for Counsel" section (sorted by severity)
- A "What the team can close without an attorney" section
- A "Minimum bar before distributing" checklist cross-referenced against LEGAL.md's existing checklist

## Hard constraints (NON-NEGOTIABLE)

- You are NOT a lawyer and do NOT give legal advice. Frame legal items as "questions for your attorney" and flag jurisdiction-dependence.
- DO NOT TOUCH files owned by other workstreams
- DO NOT write to shared docs directly
- Treat `.orchestra/CONTRACTS.md` as authoritative; READ it, never write it
- DO NOT modify any project code or HTML
- Self-execute verifications (read files yourself, don't ask the user to paste)
- This project serves ~50,000 evacuated residents during a real chemical emergency. Take the legal analysis seriously.

## What "done" looks like

- `.orchestra/legal-gap-register.md` exists with all 12 categories audited
- Each category has status, what exists, what's missing, question for counsel, severity, and owner
- A prioritized "Questions for Counsel" section is ready to hand to an attorney
- Task marked `completed` via TaskUpdate
- Summary sent to orchestrator lead via SendMessage

## Out of scope

- Technical implementation of fixes (accessibility code, Nominatim caching, etc.) -> gap-sweep
- UI/UX design changes -> not in scope for either stream
- Actually engaging an attorney -> user action

## On completion

1. Mark your task `completed` via `TaskUpdate`
2. `SendMessage` the orchestrator lead a summary: how many items per status (done/drafted/missing/blocked), top 3 blocker-severity items, and any cross-stream findings for the gap-sweep team
